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

python3 ./upload-long-vods.py

# this will split the long vods to 11hr 58min parts and upload them as private videos
# full title will be included in the video description

# wait a day or two for vids to process

python3 ./yt-check.py
cat output.csv | cut -d, -f2- | tail -n +2 | xclip -sel cli

# paste in a column in your spreadsheet and you will get your youtube urls
# check for any blank youtube urls and manually verify and fix

# TODO: generate playlist with all videos and set them as unlisted
```

# setting up the youtube auth (ai generated)

Absolutely! Here’s a **step-by-step guide** to setting up a new project in the Google Cloud Console, enabling the YouTube Data API v3, and generating the `credentials.json` file for your script:

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

---

### Step 7: Set Up Your Python Script
1. Install the required Python libraries if you haven’t already:
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pandas openpyxl
   ```
2. Place the `credentials.json` file in the same directory as your script.
3. Run your script. The first time you run it, it will open a browser window and ask you to log in to your Google account and grant permissions.
4. After authentication, a `token.json` file will be created, which stores your access and refresh tokens for future use.

---

### Step 8: Monitor Quota Usage
1. In the Google Cloud Console, go to **APIs & Services** > **Dashboard**.
2. Select the **YouTube Data API v3**.
3. Click on the **Quotas** tab to monitor your quota usage.
4. If you need more quota, click **Edit Quotas** and submit a quota increase request.

---

### Example Directory Structure
Your project directory should look like this:
```
project-folder/
│
├── credentials.json       # Downloaded from Google Cloud Console
├── token.json             # Generated after first run
├── twitch_highlights.xlsx # Your input Excel file
├── output.csv             # Generated by the script
└── youtube_search.py      # Your Python script
```

---

### Troubleshooting
- **Error: Redirect URI mismatch**: Ensure the `redirect_uris` in `credentials.json` match the redirect URI used in the script (usually `http://localhost`).
- **Error: Quota exceeded**: Request a quota increase or wait for the quota to reset at midnight PT.
- **Error: Invalid credentials**: Double-check that the `credentials.json` file is correct and hasn’t been modified.

---

By following these steps, you’ll have a fully set up Google Cloud project with the YouTube Data API enabled and the necessary credentials to run your script. Let me know if you need further assistance!
