import pickle
import os
import json
import subprocess
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

PICKLE_FILE = "long_vods.pkl"
STATUS_FILE = "upload_status.json"
CLIENT_SECRETS_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
TOKEN_FILE = "token-upload.json"

def load_pickle_file():
    with open(PICKLE_FILE, "rb") as file:
        return pickle.load(file)

def load_upload_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as file:
            return json.load(file)
    return {"uploaded": [], "pending": []}

def save_upload_status(status):
    with open(STATUS_FILE, "w") as file:
        json.dump(status, file)

def authenticate_youtube():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=creds)

def download_vod(vod_url, output_file):
    print(f"Downloading VOD from {vod_url} to {output_file}")
    command = ["yt-dlp", "--downloader=aria2c", "--embed-chapters", "-o", output_file, vod_url]
    subprocess.run(command, check=True)

def split_video(input_file, part1_file, part2_file):
    print(f"Splitting {input_file} into {part1_file} and {part2_file}")

    # Split the first 11 hours and 58 minutes into part1
    command1 = ["ffmpeg", "-y", "-i", input_file, "-ss", "00:00:00", "-t", "11:58:00", "-c", "copy", part1_file]
    # Split the remaining into part2
    command2 = ["ffmpeg", "-y", "-i", input_file, "-ss", "11:58:00", "-c", "copy", part2_file]
    subprocess.run(command1, check=True)
    subprocess.run(command2, check=True)

def upload_video(youtube, file, title, description="", category="22", tags=None):
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category,
        },
        "status": {
            "privacyStatus": "private",  # Set to "public" if you want it public
        },
    }
    media = MediaFileUpload(file, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if "id" in response:
            print(f"Uploaded video ID: {response['id']}")
        else:
            print(f"The upload failed with an unexpected response: {response}")
    return response["id"]

def main():
    vod_data = load_pickle_file()
    status = load_upload_status()

    youtube = authenticate_youtube()

    for vod_url, vod_metadata in vod_data:
        if vod_url in status["uploaded"]:
            print(f"Skipping already uploaded VOD: {vod_url}")
            continue

        output_file = f"vod_{vod_data.index((vod_url, vod_metadata))}.mp4"
        download_vod(vod_url, output_file)

        part1_file = output_file.replace(".mp4", "_part1.mp4")
        part2_file = output_file.replace(".mp4", "_part2.mp4")
        split_video(output_file, part1_file, part2_file)

        part1_title = f"(Part 1/2) {vod_metadata}"
        upload_video(youtube, part1_file, part1_title)
        status["uploaded"].append(vod_url)

        part2_title = f"(Part 2/2) {vod_metadata}"
        upload_video(youtube, part2_file, part2_title)
        status["uploaded"].append(vod_url)

        save_upload_status(status)

        os.remove(output_file)
        os.remove(part1_file)
        os.remove(part2_file)

if __name__ == "__main__":
    main()
