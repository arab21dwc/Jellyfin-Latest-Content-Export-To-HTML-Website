# Jellyfin-Latest-Content-Export-To-HTML-Website
![image](https://github.com/user-attachments/assets/81d78080-b4f2-423a-a7af-88958b708fb1)
![image](https://github.com/user-attachments/assets/535e9a46-d7c4-4860-a8b9-0a8880f10081)

This script connects to a Jellyfin server, retrieves the latest added **movies** and **TV episodes**, and generates a mobile-friendly, auto-refreshing HTML page displaying media posters, titles, genres, season info, and descriptions.

---

## 📌 Features

- ✅ Pulls latest 50 movies and episodes from a Jellyfin server.
- 📄 Displays:
  - Poster image
  - Title (with episode/season labels)
  - Genres
  - Season name
  - Production year
  - Description/overview
- 📱 Mobile-friendly layout with responsive design
- 🔁 HTML auto-refresh interval (user-defined)
- 🔄 Script update interval (user-defined)

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

---

## ▶️ How to Run

```bash
python main.py
```

When started, you will be prompted:

```text
Enter how often to update the HTML for Library changes (in minutes): 
Enter HTML auto-refresh interval (in seconds): 
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
