# 🎬 YouTube Shorts Automation Setup Guide

Yeh complete system aapke banaye hue shorts ko **GitHub Actions** ke through **roz subah aur shaam automatically YouTube par upload** kar dega.

---

## 📁 Project Structure

```text
├── content/
│   └── 19-11-2026_evening/         <-- Har slot ka ek alag folder
│       ├── video.mp4               <-- Master short video
│       └── metadata.json           <-- Title, description, tags
│
├── scripts/
│   ├── upload_to_youtube.py        <-- GitHub Actions dwara run hone wali uploader script
│   └── get_oauth_token.py          <-- One-time token nikaalne ki script
│
└── .github/
    └── workflows/
        └── auto_upload.yml         <-- Roz 9:00 AM aur 6:00 PM IST par auto-run
```

---

## ⚙️ Step 1: Google Cloud Console se Credentials lena (One-Time: 3 Minutes)

1. [Google Cloud Console](https://console.cloud.google.com/) par jayein.
2. Ek naya project banayein (jaise: `YouTube-Automator`).
3. Search bar me **"YouTube Data API v3"** search karein aur use **ENABLE** kar dein.
4. Left side menu se **"OAuth consent screen"** par jayein:
   * User Type: **External** chunein aur Create par click karein.
   * App name: `MyUploader` aur apna email daal kar Save kar dein.
   * **Test Users** section me jaakar **apna wahi Gmail ID add karein** jispar aapka YouTube channel hai.
5. Left menu se **"Credentials"** par jayein:
   * **+ CREATE CREDENTIALS** > **OAuth client ID** par click karein.
   * Application type: **Desktop app** chunein.
   * Name: `YouTube Bot` likhkar Create dabayein.
6. Banane ke baad **"DOWNLOAD JSON"** button se file download karein.
7. Us downloaded file ko rename karke **`client_secrets.json`** naam se is project folder me save kar dein.

---

## 🔑 Step 2: One-Time Token generate karna (Sirf 1 baar)

Terminal me yeh command run karein:
```bash
python scripts/get_oauth_token.py
```
* Browser me login screen open hogi.
* Apna YouTube channel wala Google account select karein aur Allow/Continue karein.
* Terminal par aapko **3 Secrets** milenge:
  1. `YOUTUBE_CLIENT_ID`
  2. `YOUTUBE_CLIENT_SECRET`
  3. `YOUTUBE_REFRESH_TOKEN`

---

## 🔒 Step 3: GitHub Repository Secrets me Save karna

1. Apni GitHub Repository par jayein.
2. **Settings** > **Secrets and variables** > **Actions** par click karein.
3. **"New repository secret"** button dabakar teeno secrets add karein:
   * Name: `YOUTUBE_CLIENT_ID` | Value: (Jo step 2 me mila)
   * Name: `YOUTUBE_CLIENT_SECRET` | Value: (Jo step 2 me mila)
   * Name: `YOUTUBE_REFRESH_TOKEN` | Value: (Jo step 2 me mila)

---

## 🚀 Step 4: System Kaise Kaam Karega?

1. **Shorts Banana:** Hum chat me short banayenge aur usko date-slot folder me save karenge (jaise `content/20-11-2026_morning/`).
2. **Push to GitHub:** Code ko GitHub par push kar denge:
   ```bash
   git add content/
   git commit -m "add new shorts for tomorrow"
   git push
   ```
3. **Automatic Release:**
   * **Morning Slot:** Roz subah **9:00 AM IST** par GitHub Action chalegi aur morning folder ki video live publish kar degi.
   * **Evening Slot:** Roz shaam **6:00 PM IST** par evening folder ki video live publish ho jayegi!
   * Aur video publish hote hi GitHub Actions folder ke andar `uploaded.flag` create karke push kar dega taaki koi video dobara upload na ho!
