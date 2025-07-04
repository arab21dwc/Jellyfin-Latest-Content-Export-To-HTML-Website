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

HEADERS = {
    "X-Emby-Token": API_KEY
}

PARAMS = {
    "SortBy": "DateCreated",
    "SortOrder": "Descending",
    "IncludeItemTypes": "Movie,Series,Episode",
    "Limit": 50,
    "Recursive": "true",
    "Fields": "PrimaryImageAspectRatio,SeriesName,SeasonNumber,IndexNumber,Genres,ProductionYear,SeasonName,Overview,CommunityRating"
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

def fetch_latest_items():
    url = f"{API_URL}/Users/{USER_ID}/Items"
    try:
        response = requests.get(url, headers=HEADERS, params=PARAMS, verify=False)
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

def build_poster_url(item_id):
    return f"{API_URL}/Items/{item_id}/Images/Primary?api_key={API_KEY}"

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
    return '<div class="genres">' + ', '.join(genres[:3]) + '</div>'

def format_year_season(item):
    year = item.get("ProductionYear")
    season = item.get("SeasonNumber") if item.get("Type") in ["Episode", "Series"] else None

    details = []
    if year:
        details.append(f"Year: {year}")
    if season is not None:
        details.append(f"Season: {season}")
    return f'<div class="details">{" | ".join(details)}</div>' if details else ""

def format_season_name(item):
    season_name = item.get("SeasonName")
    if not season_name:
        return ""
    return f'<div class="season-name">{season_name}</div>'

def format_description(item):
    desc = item.get("Overview", "")
    if not desc:
        return ""
    return f'<div class="description">{desc}</div>'

def format_rating(item):
    rating = item.get("CommunityRating")
    if not rating:
        return ""
    return f'<div class="rating">⭐ {rating:.1f}</div>'

def generate_html(movies, episodes, series, html_refresh_interval):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    html = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\">
  <meta http-equiv=\"refresh\" content=\"{html_refresh_interval}\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>Jellyfin Latest Media</title>
  <style>
    body {{
      margin: 0;
      padding: 20px;
      background: #111;
      color: #fff;
      font-family: system-ui, sans-serif;
    }}
    h1 {{ text-align: center; font-size: 2em; margin-bottom: 10px; }}
    .timestamp {{ text-align: center; font-size: 0.9em; color: #aaa; margin-bottom: 30px; }}
    h2 {{
      font-size: 1.5em;
      margin-top: 40px;
      margin-bottom: 20px;
      border-bottom: 1px solid #333;
      padding-bottom: 5px;
    }}
    .grid {{
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 20px;
    }}
    .card {{
      background: #1f1f1f;
      border-radius: 12px;
      overflow: hidden;
      width: 180px;
      max-width: 100%;
      display: flex;
      flex-direction: column;
      box-shadow: 0 4px 10px rgba(0,0,0,0.5);
      transition: transform 0.2s ease;
    }}
    .card:hover {{ transform: scale(1.05); }}
    .card img {{ width: 100%; height: auto; display: block; }}
    .card h3 {{
      padding: 10px 10px 0;
      font-size: 15px;
      color: #eee;
      text-align: center;
      word-wrap: break-word;
      line-height: 1.4;
    }}
    .genres, .details {{
      padding: 4px 10px;
      font-size: 12px;
      color: #aaa;
      text-align: center;
      font-style: italic;
    }}
    .season-name {{
      padding: 2px 10px;
      font-size: 12px;
      color: #ffc107;
      text-align: center;
      font-weight: bold;
    }}
    .description {{
      padding: 6px 10px;
      font-size: 13px;
      color: #ccc;
      text-align: center;
      line-height: 1.4;
      white-space: normal;
    }}
    .rating {{
      padding: 4px 10px;
      font-size: 13px;
      color: #f39c12;
      text-align: center;
    }}
    @media (max-width: 600px) {{ .card {{ width: 100%; }} }}
  </style>
</head>
<body>
  <h1>Latest Added Media</h1>
  <div class="timestamp">Last Updated: {timestamp}</div>
"""
    def add_cards(title, items, name_fn):
        nonlocal html
        html += f"<h2>{title}</h2>\n<div class='grid'>\n"
        for item in items:
            name = name_fn(item)
            genres = format_genres(item.get("Genres", []))
            details = format_year_season(item)
            poster_url = build_poster_url(item.get("Id"))
            season_name = format_season_name(item)
            description = format_description(item)
            rating = format_rating(item)
            html += f"""
    <div class=\"card\">
      <img src=\"{poster_url}\" alt=\"{name}\">
      <h3>{name}</h3>
      {season_name}
      {description}
      {genres}
      {details}
      {rating}
    </div>
"""
        html += "</div>\n"

    add_cards("Movies", movies, lambda x: x.get("Name", "Unknown"))
    add_cards("Series", series, lambda x: x.get("Name", "Unknown"))
    add_cards("Episodes", episodes, format_episode_title)

    html += "</body>\n</html>"
    return html

def main(refresh_interval):
    items = fetch_latest_items()
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

    try:
        while True:
            print("[⏳] Checking for new Jellyfin items...")
            main(html_refresh)
            print(f"[⏱] Waiting {script_interval} minutes before next check...")
            time.sleep(script_interval * 60)
    except KeyboardInterrupt:
        print("\n[👋] Stopped Jellyfin auto-updater.")
