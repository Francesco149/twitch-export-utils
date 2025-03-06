twitch is deleting old highlights for people who have >100h of videos, so I cobbled together this
big mess of terrible ai generated scripts to export all my twitch vods to youtube.

use at your own risk

for vods that are <12h, you can use the twitch export feature without having to download and reupload.

the workflow is (see usage below to set everything up and generate the spreadsheet):
* select first 2 columns in the spreadsheet (timestamp + title)
* ctrl+c
* ctrl + click the clickable twitch link
* dismiss 100h quota warning
* click on export
* paste the title
* wait a second or two and press ctrl+w (or leave the tab open just in case the request doesn't process)

for >12h vods, the scripts will download them, split them with no re-encoding and re-upload them

# usage

install the nix package manager (untested on windows, just use WSL or linux)

https://nix.dev/install-nix.html

```sh
nix-shell -p git --run 'git clone https://github.com/Francesco149/twitch-export-utils'
cd twitch-export-utils
nix develop # or nix-shell

python3 ./twitch-export.py

# open the spreadsheet, click links and export to yt making sure to include the timestamp in title

python3 ./download-vods.py

# this will download all vods longer than 12h to ./vods

# NOTE!!!! anything past this part is UNTESTED because I'm still downloading my own vods!!!
# USE AT YOUR OWN RISK

python3 ./upload-long-vods.py

# this will split the long vods to 11hr 58min parts and upload them as private videos
# full title will be included in the video description

# wait a day or two for vids to process

python3 ./yt-checker.py
cat output.csv | cut -d, -f2- | tail -n +2 | xclip -sel cli

# paste in a column in your spreadsheet and you will get your youtube urls
# check for any blank youtube urls and manually verify and fix

# TODO: generate playlist with all videos and set them as unlisted
```

# setting up the youtube auth (ai generated)

---

### Step 1: Create a New Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. If you already have a project, click the project dropdown in the top bar (next to the Google Cloud logo) and select **New Project**.
3. Give your project a name (e.g., "YouTube Timestamp Search").
4. Click **Create**.

---

### Step 2: Enable the YouTube Data API v3
1. In the Google Cloud Console, navigate to **APIs & Services** > **Library**.
2. In the search bar, type **YouTube Data API v3** and select it.
3. Click **Enable** to enable the API for your project.

---

### Step 3: Set Up the OAuth Consent Screen
1. In the Google Cloud Console, go to **APIs & Services** > **OAuth consent screen**.
2. Select **External** as the user type (unless you’re part of a Google Workspace organization).
3. Click **Create**.
4. Fill in the required fields:
   - **App name**: Enter a name for your app (e.g., "YouTube Timestamp Search").
   - **User support email**: Select your email address from the dropdown.
   - **Developer contact information**: Enter your email address.
5. Click **Save and Continue**.

---

### Step 4: Add Test Users
1. Under **Test users**, click **Add Users**.
2. Enter your email address (and any other emails you want to grant access to).
3. Click **Save and Continue**.

---

### Step 5: Create OAuth 2.0 Credentials
1. In the Google Cloud Console, go to **APIs & Services** > **Credentials**.
2. Click **Create Credentials** and select **OAuth client ID**.
3. Configure the OAuth client:
   - **Application type**: Select **Desktop app**.
   - **Name**: Give your OAuth client a name (e.g., "YouTube Timestamp Search Client").
4. Click **Create**.

---

### Step 6: Download the `credentials.json` File
1. After creating the OAuth client ID, you’ll see a popup with your **Client ID** and **Client Secret**.
2. Click the **Download JSON** button (it looks like a download icon) to download the `credentials.json` file.
3. Save the `credentials.json` file in the same directory as your Python script.
