import requests
import time
import urllib3
import hashlib
import json
from datetime import datetime

# === Configuration ===
API_URL = "https://your-jellyfin-url:port"
USER_ID = "your-jellyfin-user-id"
API_KEY = "your-jellyfin-api-key"
OUTPUT_FILE = "jellyfin_latest.html"
CHECKSUM_FILE = "jellyfin_last_hash.txt"

HEADERS = {
    "X-Emby-Token": API_KEY
}

def get_interval(prompt, default):
    try:
        user_input = input(prompt).strip()
        if not user_input:
            return default
        value = int(user_input)
        if value <= 0:
            raise ValueError
        return value
    except ValueError:
        print(f"Invalid input. Using default value: {default}")
        return default

def get_limit():
    MAX_LIMIT = 100
    try:
        user_input = input(f"Enter how many latest items to fetch (default 50, max {MAX_LIMIT}): ").strip()
        if not user_input:
            return 50
        value = int(user_input)
        if value <= 0 or value > MAX_LIMIT:
            raise ValueError
        return value
    except ValueError:
        print(f"Invalid input. Using default value: 50")
        return 50

def fetch_latest_items(limit):
    url = f"{API_URL}/Users/{USER_ID}/Items"
    params = {
        "SortBy": "DateCreated",
        "SortOrder": "Descending",
        "IncludeItemTypes": "Movie,Series,Episode",
        "Limit": limit,
        "Recursive": "true",
        "Fields": "PrimaryImageAspectRatio,SeriesName,SeasonNumber,IndexNumber,Genres,ProductionYear,SeasonName,Overview,CommunityRating,RunTimeTicks,ProviderIds"
    }
    try:
        response = requests.get(url, headers=HEADERS, params=params, verify=False)
        response.raise_for_status()
        return response.json().get("Items", [])
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch items: {e}")
        return []

def compute_items_hash(items):
    serialized = json.dumps(items, sort_keys=True)
    return hashlib.md5(serialized.encode("utf-8")).hexdigest()

def load_last_hash():
    try:
        with open(CHECKSUM_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

def save_current_hash(hash_val):
    with open(CHECKSUM_FILE, "w") as f:
        f.write(hash_val)

def build_poster_url(item):
    # Check if the item is of type "Episode" or "Series" to fetch series poster
    if item.get("Type") == "Episode":
        # For episode, get the parent series' poster
        series_id = item.get("SeriesId")
        if series_id:
            return f"{API_URL}/Items/{series_id}/Images/Primary?api_key={API_KEY}"
    # For movies and other types, use the item itself to get the image
    return f"{API_URL}/Items/{item.get('Id')}/Images/Primary?api_key={API_KEY}"

def format_episode_title(item):
    series_name = item.get("SeriesName", "")
    season = item.get("SeasonNumber")
    episode = item.get("IndexNumber")
    name = item.get("Name", "Unknown")

    title_parts = []
    if series_name:
        title_parts.append(series_name)
    if season is not None and episode is not None:
        title_parts.append(f"S{int(season):02}E{int(episode):02}")
    elif season is not None:
        title_parts.append(f"Season {int(season)}")
    elif episode is not None:
        title_parts.append(f"Episode {int(episode)}")
    if name and name not in title_parts:
        title_parts.append(name)

    return " - ".join(title_parts)

def format_genres(genres):
    if not genres:
        return ""
    badges = ' '.join(f'<span class="genre-badge">{g}</span>' for g in genres[:3])
    return f'<div class="genres">{badges}</div>'

def format_year_season(item):
    year = item.get("ProductionYear")
    season = item.get("SeasonNumber") if item.get("Type") in ["Episode", "Series"] else None

    details = []
    if year:
        details.append(f"<i class='fas fa-calendar-alt'></i> {year}")
    if season is not None:
        details.append(f"Season {season}")
    return f'<div class="details">{" | ".join(details)}</div>' if details else ""

def format_season_name(item):
    season_name = item.get("SeasonName")
    if not season_name:
        return ""
    return f'<div class="season-name">{season_name}</div>'

def format_description(item):
    desc = item.get("Overview", "")
    if not desc:
        imdb_link = ""
        tmdb_link = ""
        ids = item.get("ProviderIds", {})
        
        imdb_id = ids.get("Imdb")
        tmdb_id = ids.get("Tmdb")
        
        # Generate IMDb and TMDb links if available
        if imdb_id:
            imdb_link = f"<a href='https://www.imdb.com/title/{imdb_id}' target='_blank'><i class='fab fa-imdb'></i> IMDb</a>"
        if tmdb_id:
            tmdb_link = f"<a href='https://www.themoviedb.org/movie/{tmdb_id}' target='_blank'><i class='fas fa-film'></i> TMDb</a>"

        # If neither IMDb nor TMDb is available, display only the message
        fallback_message = f"""
        <div class="description">
          <span class="desc-short" id="short-{item.get('Id')}">No Description Available For This Title. Kindly Open IMDb or TMDb Link Below:</span>
          <div class="links">{imdb_link} {tmdb_link}</div>
        </div>
        """
        return fallback_message
    
    # Short description
    short = desc[:200] + ("..." if len(desc) > 200 else "")
    
    # Full description
    full = desc.replace('"', '&quot;').replace("'", "&#39;")
    
    item_id = item.get("Id", "")
    
    # HTML for description with 'Read more' / 'Show less'
    return f"""
    <div class="description">
      <span class="desc-short" id="short-{item_id}">{short}</span>
      <span class="desc-full" id="full-{item_id}" style="display:none;">{full}</span>
      <a href="javascript:void(0);" class="toggle-desc" onclick="toggleDescription('{item_id}')">Read more</a>
    </div>
    <script>
      function toggleDescription(itemId) {{
        var fullDesc = document.getElementById('full-' + itemId);
        var shortDesc = document.getElementById('short-' + itemId);
        var toggleLink = document.querySelector('[onclick=\"toggleDescription(\\'' + itemId + '\\')\"]');

        if (fullDesc.style.display === 'none') {{
          fullDesc.style.display = 'block';
          shortDesc.style.display = 'none';
          toggleLink.innerText = 'Show less';
        }} else {{
          fullDesc.style.display = 'none';
          shortDesc.style.display = 'block';
          toggleLink.innerText = 'Read more';
        }}
      }}
    </script>
    """
    
def format_rating(item):
    rating = item.get("CommunityRating")
    if not rating:
        return ""
    return f'<div class="rating"><i class="fas fa-star"></i> {rating:.1f}</div>'

def format_runtime(item):
    ticks = item.get("RunTimeTicks")
    if not ticks:
        return ""
    seconds = ticks // 10_000_000
    minutes = seconds // 60
    hours = minutes // 60
    minutes = minutes % 60
    text = f"{hours}h {minutes}m" if hours else f"{minutes}m"
    return f'<div class="runtime"><i class="fas fa-clock"></i> {text}</div>'

def format_links(item):
    ids = item.get("ProviderIds", {})
    links = []
    imdb_id = ids.get("Imdb")
    tmdb_id = ids.get("Tmdb")

    if imdb_id:
        links.append(f"<a href='https://www.imdb.com/title/{imdb_id}' target='_blank'><i class='fab fa-imdb'></i> IMDb</a>")
    if tmdb_id:
        links.append(f"<a href='https://www.themoviedb.org/movie/{tmdb_id}' target='_blank'><i class='fas fa-film'></i> TMDb</a>")

    if not links:
        return ""
    return f"<div class='links'>{' | '.join(links)}</div>"

def generate_html(movies, episodes, series, html_refresh_interval):
    # Get system time for "Last Updated"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="{html_refresh_interval}">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Jellyfin Latest Media</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
  <style>
    body {{
      background: linear-gradient(to right, #141e30, #243b55);
      color: #fff;
      font-family: 'Segoe UI', sans-serif;
      padding: 20px;
    }}
    body.light {{
      background: #f5f5f5;
      color: #111;
    }}
    h1 {{
      text-align: center;
      font-size: 2.5em;
      transition: color 0.3s ease;
    }}
    h1:hover {{
      color: #00e5ff; /* Change color on hover */
    }}
    .timestamp {{
      text-align: center;
      font-size: 0.95em;
      color: #ccc;
      margin-bottom: 5px;
    }}
    h2 {{
      font-size: 1.6em;
      border-bottom: 2px solid #00acc1;
      margin-top: 40px;
      color: #00e5ff;
      text-align: center;  /* Center align category titles */
      transition: color 0.3s ease;
    }}
    h3 {{
      margin: 10px;
      font-size: 1em;
      text-align: center;  /* Center align item titles */
      transition: color 0.3s ease;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 20px;
    }}
    .card {{
      background: #1e1e2f;
      border-radius: 12px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
      height: 100%;
      transition: transform 0.3s ease, box-shadow 0.3s ease, background-color 0.3s ease;
    }}
    .card:hover {{
      transform: scale(1.05); /* Slightly scale up the card */
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
      background-color: #2c3e50; /* Change background on hover */
    }}
    .card img {{
      width: 100%;
      height: 270px;
      object-fit: cover;
    }}
    .card h3 {{
      margin: 10px;
      font-size: 1em;
      text-align: center;  /* Center align item titles */
      transition: color 0.3s ease;
    }}
    .card h3:hover {{
      color: #00e5ff; /* Change title color on hover */
    }}
    .genres {{
      font-size: 0.85em;
      text-align: center;
      margin: 6px;
    }}
    .genre-badge {{
      display: inline-block;
      background: #00acc1;
      padding: 2px 8px;
      border-radius: 12px;
      margin: 2px;
      color: #fff;
      font-size: 0.75em;
      transition: transform 0.2s ease, background-color 0.3s ease;
    }}
    .genre-badge:hover {{
      transform: scale(1.1); /* Slightly enlarge the genre badge on hover */
      background-color: #008b91; /* Darker shade of the badge background */
    }}
    .details, .rating, .runtime {{
      font-size: 0.85em;
      text-align: center;
      margin: 2px 10px;
    }}
    .season-name {{
      color: #ffd54f;
      font-size: 0.85em;
      text-align: center;
      font-weight: bold;
    }}
    .description {{
      font-size: 0.9em;
      color: #ccc;
      margin: 6px 10px;
      text-align: center;
    }}
    .toggle-desc {{
      display: inline-block;
      color: #00e5ff;
      cursor: pointer;
      margin-left: 6px;
      font-size: 0.85em;
      text-decoration: underline;
      transition: color 0.3s ease;
    }}
    .toggle-desc:hover {{
      color: #ff4081; /* Change text color on hover */
      opacity: 0.8;
    }}
    .links {{
      text-align: center;
      margin: 6px 0;
      font-size: 0.85em;
    }}
    .links a {{
      color: #00e5ff;
      text-decoration: none;
      margin: 0 6px;
      transition: color 0.3s ease;
    }}
    .links a:hover {{
      color: #ff4081; /* Change link color on hover */
      text-decoration: underline;
    }}
  </style>
</head>
<body>
  <h1>Latest Media</h1>
  <div class="timestamp">Last Updated: {timestamp}</div>
"""

    def add_cards(title, items, name_fn):
        nonlocal html
        html += f"<h2>{title}</h2>\n<div class='grid'>\n"
        for item in items:
            name = name_fn(item)
            genres = format_genres(item.get("Genres", []))
            details = format_year_season(item)
            poster_url = build_poster_url(item)
            season_name = format_season_name(item)
            description = format_description(item)
            rating = format_rating(item)
            runtime = format_runtime(item)
            links = format_links(item)
            html += f"""
    <div class="card">
      <img src="{poster_url}" alt="{name}">
      <h3>{name}</h3>
      {season_name}
      {description}
      {genres}
      {details}
      {rating}
      {runtime}
      {links}
    </div>
"""
        html += "</div>\n"

    add_cards("Movies", movies, lambda x: x.get("Name", "Unknown"))
    add_cards("Series", series, lambda x: x.get("Name", "Unknown"))
    add_cards("Episodes", episodes, format_episode_title)

    html += "</body>\n</html>"
    return html

def main(refresh_interval, limit):
    items = fetch_latest_items(limit)
    if not items:
        print("No media found.")
        return

    current_hash = compute_items_hash(items)
    last_hash = load_last_hash()

    if current_hash == last_hash:
        print("[✔] No new items. HTML not updated.")
        return

    movies = [item for item in items if item.get("Type") == "Movie"]
    episodes = [item for item in items if item.get("Type") == "Episode"]
    series = [item for item in items if item.get("Type") == "Series"]

    html_content = generate_html(movies, episodes, series, refresh_interval)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    save_current_hash(current_hash)
    print(f"[✔] New items found. HTML page updated: {OUTPUT_FILE}")

if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    script_interval = get_interval("Enter how often to update the HTML for Library changes (in minutes): ", 2)
    html_refresh = get_interval("Enter HTML auto-refresh interval (in seconds): ", 60)
    limit = get_limit()

    try:
        while True:
            print("[⏳] Checking for new Jellyfin items...")
            main(html_refresh, limit)
            print(f"[⏱] Waiting {script_interval} minutes before next check...\n")
            time.sleep(script_interval * 60)
    except KeyboardInterrupt:
        print("\n[👋] Stopped Jellyfin auto-updater.")
