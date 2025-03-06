import pickle
import os
import subprocess

PICKLE_FILE = "long_vods.pkl"  # Same as the original script
VODS_DIR = "./vods"

def ensure_vods_dir():
    """Ensure the VODs directory exists."""
    if not os.path.exists(VODS_DIR):
        os.makedirs(VODS_DIR)

def load_pickle_file():
    """Load the list of VODs and metadata from the pickle file."""
    with open(PICKLE_FILE, "rb") as file:
        return pickle.load(file)

def download_vod(vod_url, output_file):
    """Download a VOD using yt-dlp."""
    print(f"Downloading VOD from {vod_url} to {output_file}")
    command = ["yt-dlp", "--downloader=aria2c", "--embed-chapters", "-o", output_file, vod_url]
    subprocess.run(command, check=True)

def main():
    """Main function to download and store VODs."""
    ensure_vods_dir()
    vod_data = load_pickle_file()  # Load VODs and metadata from the pickle file

    for i, (vod_url, vod_metadata) in enumerate(vod_data):
        output_file = os.path.join(VODS_DIR, f"vod_{i}.mp4")
        if os.path.exists(output_file):
            print(f"Skipping already downloaded VOD: {vod_url}")
            continue

        print(f"Downloading VOD {i+1}/{len(vod_data)}: {vod_metadata}")
        download_vod(vod_url, output_file)

if __name__ == "__main__":
    main()
