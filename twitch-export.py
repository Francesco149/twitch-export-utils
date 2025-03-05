import requests
from openpyxl import Workbook
from http.server import BaseHTTPRequestHandler, HTTPServer
import webbrowser
import urllib.parse
from config import *

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

# Automatically obtain OAuth token
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

# Get user ID from username
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

# Fetch all highlights for the user with pagination
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

# Generate spreadsheet
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

        # Generate spreadsheet
        generate_spreadsheet(highlights)
    except Exception as e:
        print(f"An error occurred: {e}")
