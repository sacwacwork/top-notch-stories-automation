import os
import json
import subprocess
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]

CLIENT_SECRETS_FILE = "client_secrets.json"

def main():
    if not os.path.exists(CLIENT_SECRETS_FILE):
        print(f"\n[ERROR] {CLIENT_SECRETS_FILE} nahi mili!")
        return

    print("\n" + "="*60)
    print("Google OAuth Flow shuru ho raha hai...")
    print("Aapke browser me Google login page open hoga.")
    print("Apna YouTube account select karke 'Continue / Allow' karein.")
    print("="*60 + "\n")

    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES
    )

    credentials = flow.run_local_server(
        port=8080,
        prompt="consent",
        access_type="offline"
    )

    with open(CLIENT_SECRETS_FILE, "r") as f:
        data = json.load(f)
        client_info = data.get("installed") or data.get("web")

    client_id = client_info.get("client_id")
    client_secret = client_info.get("client_secret")
    refresh_token = credentials.refresh_token

    # Save to local gitignored file
    creds_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token
    }
    with open("youtube_credentials.json", "w") as f:
        json.dump(creds_data, f, indent=2)

    print("\n" + "="*60)
    print("SUCCESS! Refresh Token successfully praapt ho gaya!")
    print("="*60)

    # Set GitHub Secrets automatically using GitHub CLI (gh)
    print("\nSetting GitHub Repository Secrets automatically via gh CLI...")
    try:
        subprocess.run(["gh", "secret", "set", "YOUTUBE_CLIENT_ID", "--body", client_id], check=True)
        subprocess.run(["gh", "secret", "set", "YOUTUBE_CLIENT_SECRET", "--body", client_secret], check=True)
        subprocess.run(["gh", "secret", "set", "YOUTUBE_REFRESH_TOKEN", "--body", refresh_token], check=True)
        print("ALL 3 SECRETS SUCCESSFULLY ADDED TO YOUR GITHUB REPO!")
    except Exception as e:
        print(f"gh secret set warning: {e}")
        print("\nAap manually bhi add kar sakte hain:")
        print(f"YOUTUBE_CLIENT_ID = {client_id}")
        print(f"YOUTUBE_CLIENT_SECRET = {client_secret}")
        print(f"YOUTUBE_REFRESH_TOKEN = {refresh_token}")

    print("\n" + "="*60)
    print("SETUP COMPLETE! Ab GitHub Actions roz automatically videos upload kar sakega!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
