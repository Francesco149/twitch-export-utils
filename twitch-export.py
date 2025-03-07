import requests
from openpyxl import Workbook
from http.server import BaseHTTPRequestHandler, HTTPServer
import webbrowser
import urllib.parse
import pickle
from config import *
from common import *

# Twitch API credentials
#CLIENT_ID = 'xxx'
#CLIENT_SECRET = 'xxx'
#REDIRECT_URI = "http://localhost:3000"  # Local redirect URI
#USERNAME = "xxx"  # Replace with your Twitch username

# Twitch API endpoints
AUTH_URL = "https://id.twitch.tv/oauth2/authorize"
TOKEN_URL = "https://id.twitch.tv/oauth2/token"

USER_ENDPOINT = "https://api.twitch.tv/helix/users"
HIGHLIGHTS_ENDPOINT = "https://api.twitch.tv/helix/videos"

# Global variable to store the OAuth token
OAUTH_TOKEN = None

# HTTP server to handle the OAuth redirect
class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global OAUTH_TOKEN
        # Extract the authorization code from the query parameters
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        code = params.get("code", [None])[0]

        if code:
            # Exchange the authorization code for an OAuth token
            token_data = {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": REDIRECT_URI
            }
            response = requests.post(TOKEN_URL, data=token_data)
            if response.status_code == 200:
                OAUTH_TOKEN = response.json()["access_token"]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"OAuth token received! You can close this window.")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Failed to obtain OAuth token.")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"No authorization code found.")

# Start a local HTTP server to handle the OAuth redirect
def start_local_server():
    server = HTTPServer(("localhost", 3000), OAuthHandler)
    print("Starting local server to handle OAuth redirect...")
    server.handle_request()  # Handle one request and then stop

@cached
def get_oauth_token():
    # Open the Twitch authorization page in the default browser
    auth_params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "user:read:broadcast"  # Required scope for accessing highlights
    }
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(auth_params)}"
    webbrowser.open(auth_url)

    # Start the local server to handle the redirect
    start_local_server()

    if OAUTH_TOKEN:
        return OAUTH_TOKEN
    else:
        raise Exception("Failed to obtain OAuth token.")

@cached
def get_user_id(username):
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {OAUTH_TOKEN}"
    }
    params = {"login": username}
    response = requests.get(USER_ENDPOINT, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["data"]:
            return data["data"][0]["id"]
    raise Exception(f"Failed to fetch user ID for {username}")

@cached
def fetch_all_highlights(user_id):
    highlights = []
    cursor = None
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {OAUTH_TOKEN}"
    }

    while True:
        params = {
            "user_id": user_id,
            "type": "highlight",  # Only fetch highlights
            "first": 100,  # Maximum number of highlights per request
            "after": cursor  # Pagination cursor
        }
        response = requests.get(HIGHLIGHTS_ENDPOINT, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            highlights.extend(data["data"])
            cursor = data.get("pagination", {}).get("cursor")
            if not cursor:
                break  # No more pages
        else:
            raise Exception("Failed to fetch highlights")

    return highlights

# stupid me decided to use timestamps so now I have to deal
# with a few identical ones.
# why didn't I use video id's? why?
def handle_duplicate_ts(date_time, seen_ts):
    i = 0
    new_dt = date_time
    while new_dt in seen_ts:
        new_dt = f"{date_time}.{i}"
        i += 1
    seen_ts.append(new_dt)
    return (new_dt, seen_ts)

def adjust_ts(highlights):
    seen_ts = []
    for highlight in highlights:
        date_time, seen_ts = handle_duplicate_ts(highlight["created_at"], seen_ts)
        highlight["created_at"] = date_time

def generate_spreadsheet(highlights):
    wb = Workbook()
    ws = wb.active
    ws.title = "Twitch Highlights"

    # Add headers
    ws.append(["Date and Time", "Title", "Twitch Link", "YouTube Link"])

    # Add highlight data
    for highlight in highlights:
        date_time = highlight["created_at"]
        title = highlight["title"]
        twitch_link = f"https://dashboard.twitch.tv/u/{USERNAME}/content/video-producer/edit/{highlight['id']}"
        ws.append([date_time, title, twitch_link, ""])

    # Save the spreadsheet
    wb.save(SPREADSHEET)
    print("Spreadsheet generated: " + SPREADSHEET)

# Parse duration in the format "XhYmZs" and return total duration in hours
def parse_duration(duration_str):
    hours = 0
    minutes = 0
    seconds = 0

    # Extract hours
    if "h" in duration_str:
        hours = int(duration_str.split("h")[0])
        duration_str = duration_str.split("h")[1]

    # Extract minutes
    if "m" in duration_str:
        minutes = int(duration_str.split("m")[0])
        duration_str = duration_str.split("m")[1]

    # Extract seconds
    if "s" in duration_str:
        seconds = int(duration_str.split("s")[0])

    # Convert everything to hours
    total_hours = hours + (minutes / 60) + (seconds / 3600)
    return total_hours

# Generate pickle file with VOD URLs and metadata
def generate_vod_pickle_file(highlights):
    vod_data = []
    for highlight in highlights:
        duration_str = highlight["duration"]
        total_duration = parse_duration(duration_str)
        if total_duration >= 12:
            vod_url = f"https://www.twitch.tv/videos/{highlight['id']}"
            timestamp = highlight["created_at"]
            title = highlight["title"]
            vod_data.append((vod_url, f"{timestamp} {title}"))

    # Save the list of pairs to a pickle file
    with open("long_vods.pkl", "wb") as file:
        pickle.dump(vod_data, file)
    print("Pickle file with long VOD URLs and metadata generated: long_vods.pkl")

# Main script
if __name__ == "__main__":
    try:
        # Automatically obtain OAuth token
        OAUTH_TOKEN = get_oauth_token()
        print("OAuth token obtained successfully.")

        # Fetch user ID and highlights
        user_id = get_user_id(USERNAME)
        highlights = fetch_all_highlights(user_id)
        print(f"Fetched {len(highlights)} highlights.")

        # fix duplicate timestamps
        adjust_ts(highlights)

        # Generate spreadsheet
        generate_spreadsheet(highlights)

        # Generate pickle file with VOD URLs and metadata
        generate_vod_pickle_file(highlights)
    except Exception as e:
        print(f"An error occurred: {e}")
