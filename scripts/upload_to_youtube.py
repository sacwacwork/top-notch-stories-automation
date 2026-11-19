import os
import sys
import json
import glob
import argparse
from datetime import datetime
import pytz

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]

def get_ist_now():
    """Returns current datetime in Indian Standard Time (IST)."""
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist)

def get_authenticated_service():
    """Builds YouTube service using OAuth Refresh Token from Environment Variables or local youtube_credentials.json."""
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        # Check local credentials file
        for cred_file in ["youtube_credentials.json", os.path.join(os.path.dirname(__file__), "..", "youtube_credentials.json")]:
            if os.path.exists(cred_file):
                try:
                    with open(cred_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        client_id = client_id or data.get("client_id")
                        client_secret = client_secret or data.get("client_secret")
                        refresh_token = refresh_token or data.get("refresh_token")
                except Exception:
                    pass

    if not all([client_id, client_secret, refresh_token]):
        raise ValueError(
            "Missing credentials! Please set YOUTUBE_CLIENT_ID, "
            "YOUTUBE_CLIENT_SECRET, and YOUTUBE_REFRESH_TOKEN in GitHub Secrets or youtube_credentials.json."
        )

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES
    )
    return build("youtube", "v3", credentials=creds)

def find_target_folder(slot=None):
    """Finds today's folder matching current date and slot in content/."""
    now_ist = get_ist_now()
    date_str = now_ist.strftime("%d-%m-%Y") # e.g. 19-11-2026

    if not slot:
        # Auto-detect slot based on IST hour
        # Morning slot: before 2:00 PM IST (14:00)
        # Evening slot: 2:00 PM IST and onwards
        slot = "morning" if now_ist.hour < 14 else "evening"

    target_name = f"{date_str}_{slot}"
    target_path = os.path.join("content", target_name)

    print(f"[SEARCH] Looking for target folder: {target_path} (IST Time: {now_ist.strftime('%Y-%m-%d %H:%M:%S')})")

    if os.path.exists(target_path):
        return target_path

    # Fallback: Check if there's any pending unuploaded folder in content/
    print("[INFO] Exact date folder not found. Checking for any unuploaded pending folders in content/...")
    all_folders = sorted(glob.glob(os.path.join("content", "*")))
    for folder in all_folders:
        if os.path.isdir(folder):
            flag_path = os.path.join(folder, "uploaded.flag")
            video_path = os.path.join(folder, "video.mp4")
            meta_path = os.path.join(folder, "metadata.json")
            if not os.path.exists(flag_path) and os.path.exists(video_path) and os.path.exists(meta_path):
                print(f"[FOUND PENDING] Found pending folder: {folder}")
                return folder

    return None

def upload_video(folder_path):
    video_path = os.path.join(folder_path, "video.mp4")
    meta_path = os.path.join(folder_path, "metadata.json")
    flag_path = os.path.join(folder_path, "uploaded.flag")

    if os.path.exists(flag_path):
        print(f"[SKIP] Folder {folder_path} is already uploaded. uploaded.flag exists.")
        return

    if not os.path.exists(video_path) or not os.path.exists(meta_path):
        print(f"[ERROR] Required files (video.mp4 or metadata.json) missing in {folder_path}")
        return

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    # Ensure title and description include #Shorts
    title = meta.get("title", "Magical Story #Shorts")
    if "#Shorts" not in title and "#shorts" not in title:
        title = f"{title} #Shorts"

    description = meta.get("description", "A magical cartoon story. Subscribe for daily shorts! #Shorts #Cartoon")
    if "#Shorts" not in description and "#shorts" not in description:
        description = f"{description}\n\n#Shorts #AnimatedStories"

    tags = meta.get("tags", ["shorts", "cartoon", "animation", "hindi stories", "moral stories"])
    category_id = str(meta.get("category_id", "1")) # 1 = Film & Animation
    privacy_status = meta.get("privacy_status", "public") # public, unlisted, private

    print(f"\n[STARTING UPLOAD]")
    print(f"Folder: {folder_path}")
    print(f"Title: {title}")
    print(f"Privacy: {privacy_status}")

    youtube = get_authenticated_service()

    body = {
        "snippet": {
            "title": title[:100], # Max 100 chars
            "description": description[:5000],
            "tags": tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": meta.get("made_for_kids", False)
        }
    }

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024*1024*5 # 5MB chunks
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploading progress: {int(status.progress() * 100)}%")

    video_id = response.get("id")
    video_url = f"https://youtube.com/shorts/{video_id}"

    print("\n" + "="*60)
    print("SUCCESS! Video uploaded to YouTube Shorts successfully!")
    print(f"Video ID: {video_id}")
    print(f"Video URL: {video_url}")
    print("="*60 + "\n")

    # Mark as uploaded
    with open(flag_path, "w", encoding="utf-8") as f:
        json.dump({
            "uploaded_at": datetime.utcnow().isoformat(),
            "video_id": video_id,
            "video_url": video_url,
            "title": title
        }, f, indent=2)

    print(f"[FLAG] Created {flag_path} to prevent duplicate uploads.")

def main():
    parser = argparse.ArgumentParser(description="Upload YouTube Short from content folder")
    parser.add_argument("--slot", choices=["morning", "evening", "auto"], default="auto", help="Release slot")
    parser.add_argument("--folder", help="Specific folder path in content/")
    args = parser.parse_args()

    if args.folder:
        target = args.folder
    else:
        slot = None if args.slot == "auto" else args.slot
        target = find_target_folder(slot)

    if not target:
        print("[EXIT] No scheduled folder found to upload at this time. Exiting cleanly.")
        sys.exit(0)

    try:
        upload_video(target)
    except Exception as e:
        print(f"[FATAL ERROR] Upload failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
