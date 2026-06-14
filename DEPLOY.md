# Deploying Text-to-Voice PRO to Vercel

This guide walks you through deploying your app so it works publicly, anytime, for free.

---

## Prerequisites

- A free account at [vercel.com](https://vercel.com)
- A free account at [github.com](https://github.com)
- Git installed on your machine

---

## Step 1 — Push your project to GitHub

```bash
cd C:\Users\gurba\Downloads\text_to_voice_PRO

git init
git add .
git commit -m "Initial commit — Text-to-Voice PRO"
```

Create a **new repository** on GitHub (e.g. `text-to-voice-pro`), then:

```bash
git remote add origin https://github.com/YOUR_USERNAME/text-to-voice-pro.git
git branch -M main
git push -u origin main
```

---

## Step 2 — Import to Vercel

1. Go to [vercel.com/new](https://vercel.com/new)
2. Click **"Import Git Repository"**
3. Select your `text-to-voice-pro` repo
4. Leave all settings as default — Vercel auto-detects `vercel.json`
5. Click **Deploy**

Vercel installs packages from `requirements.txt` automatically.

> Your app will be live at `https://text-to-voice-pro.vercel.app`

---

## Step 3 — Verify the deployment

Open your Vercel URL and test:
- Language selector sidebar loads
- Typing text and pressing **Speak** returns audio
- **Save MP3** downloads correctly
- Light/Dark theme toggle works

---

## Project file structure

```
text_to_voice_PRO/
├── app.py                  ← Flask backend (entry point)
├── vercel.json             ← Vercel routing config
├── requirements.txt        ← Python dependencies
├── templates/
│   └── index.html          ← Main UI
└── static/
    ├── css/style.css
    └── js/app.js
```

---

## Important Vercel notes

| Topic | Detail |
|-------|--------|
| **Audio caching** | `/tmp` exists per invocation but is not shared across servers. Same text may re-generate on different requests. |
| **Execution timeout** | Hobby plan = **10 s** per request. Very long texts may time out. Upgrade to Pro for 60 s limit. |
| **gTTS internet** | gTTS calls Google's servers. Vercel functions have outbound internet access, so this works fine. |
| **Cold starts** | First request after inactivity takes 2–4 s to warm up. |

---

## Updating your deployment

Any `git push` to `main` triggers an automatic Vercel re-deploy (~30 s):

```bash
git add .
git commit -m "My changes"
git push
```

---

## Running locally

```bash
cd C:\Users\gurba\Downloads\text_to_voice_PRO
python app.py
```

Open **http://127.0.0.1:5000**
