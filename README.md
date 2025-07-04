# Jellyfin-Latest-Content-Export-To-HTML-Website

Desktop View
![image](https://github.com/user-attachments/assets/7a359777-1efb-478a-9a7c-7928873ef0e7)
![image](https://github.com/user-attachments/assets/08949e19-5503-40f1-b740-c58fb18d86e7)

Mobile View
![image](https://github.com/user-attachments/assets/6d3606ef-cc46-4924-b0a9-53c4a2e7a068)
![image](https://github.com/user-attachments/assets/7d75ac50-f5cf-4e58-9f07-d89b042d533b)
![image](https://github.com/user-attachments/assets/5ce4d279-8f02-4e9a-af57-af29231796e6)


This script connects to a Jellyfin server, retrieves the latest added **Movies** and **Series** **Episodes**, and generates a mobile-friendly, auto-refreshing HTML page displaying media posters, titles, genres, season info, and descriptions.

---

## 📌 Features

- ✅ Pulls latest 50 movies, seasons and episodes from a Jellyfin server.
- 🎬 Displays:
  - Poster image
  - Title (with episode/season labels)
  - Genres
  - Season/Episode Info
  - Production Year
  - Description/Overview
  - Rating
  - Runtime
  - Added TMDB/IMDB Links to cards
- 📱 Mobile-friendly layout with responsive design
- 🔁 HTML auto-refresh interval (user-defined)
- 🔄 Script update interval (user-defined)
- ⚠️ Suppresses SSL warnings for self-hosted instances
- ✅ Advanced Logic
  - Computes an **MD5 hash** of the latest library response
  - Stores the last hash in `jellyfin_last_hash.txt`
  - Skips HTML generation if the library has not changed

---

## ⚙️ Configuration

Inside the script:

```python
API_URL = "https://your-jellyfin-url:port"
USER_ID = "your-jellyfin-user-id"
API_KEY = "your-jellyfin-api-key"
OUTPUT_FILE = "jellyfin_latest.html"
```

You must replace these with valid Jellyfin server credentials:

- **API_URL**: Your Jellyfin server URL.
- **USER_ID**: ID of the Jellyfin user account.
- **API_KEY**: API token for the user (generate via Jellyfin web UI).
- **OUTPUT_FILE**: The name of the HTML file to generate.
- **CHECKSUM_FILE**: "jellyfin_last_hash.txt"
---

## ▶️ How to Run

```bash
python main.py
```
When started, you will be prompted:

```text
Enter how often to update the HTML for Library changes (in minutes): 
Enter HTML auto-refresh interval (in seconds):
Enter how many latest items to fetch (default 50, max 100) 
```

The script will then:

1. Connect to Jellyfin and retrieve the latest media.
2. Build and save an HTML page to `jellyfin_latest.html`.
3. Wait for the configured update interval and repeat.

Press `Ctrl + C` to stop it.

## 🔒 HTTPS & Insecure Warning

Since some users run Jellyfin with self-signed certificates, the script disables SSL verification warnings using:

```python
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

You may change `verify=False` in `requests.get(...)` to `True` to enforce SSL.

---

## 🔧 Advanced Customization

You can modify:

- **Fields to fetch** in `PARAMS` (add `CommunityRating`, `RunTimeTicks`, etc.)
- **Layout/styling** in the `<style>` section
- **Update schedule** logic in the `while True` loop

---

## 📤 Deployment (Optional)

To view the HTML output on other devices, you can:

- Upload it to a web server
- Use `python -m http.server` to serve it locally
- Share it on your local network

---

## 🧪 Troubleshooting

| Issue | Fix |
|------|-----|
| `[ERROR] Failed to fetch items` | Check your Jellyfin API URL, user ID, and token. |
| HTML not updating | Confirm the script is running and not blocked by firewall. |
| Images not loading | Make sure Jellyfin server allows access to poster URLs (check port and HTTPS). |

---

## ✅ Requirements

- Python 3.6+
- `requests` library (included in most Python installs)

Install if needed:

```bash
pip install requests
```
