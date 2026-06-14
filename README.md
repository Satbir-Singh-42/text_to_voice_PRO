# 🎙️ Text to Voice PRO

> Free, open-source multi-language text-to-speech web app powered by Google TTS.  
> Supports **50+ languages and accents** — Hindi, English, Arabic, Spanish, Japanese, and more.

![VoicePRO](static/icons/icon-512.png)

---

## ✨ Features

| Feature | Detail |
|---------|--------|
| 🌍 **50+ Languages** | Hindi, Punjabi, English (7 accents), Arabic, Spanish, Japanese, Korean, and many more |
| 🎚️ **Speed Control** | Draggable slider — Slow / Normal / Fast |
| 🎵 **In-browser Playback** | Scrubable audio progress bar with waveform animation |
| 💾 **Save as MP3** | Download the generated audio file directly |
| 🌙 **Light / Dark Theme** | Toggle with preference saved in localStorage |
| 🔍 **Language Search** | Instant filter in the sidebar |
| ⌨️ **Keyboard Shortcut** | `Ctrl + Enter` to speak |
| ♾️ **No Character Limit** | Paste as much text as you want |
| 📱 **Responsive** | Works on desktop, tablet, and mobile |
| 🚀 **Vercel Ready** | One-click deployment via `vercel.json` |

---

## 🖥️ Screenshots

> Run locally and open `http://127.0.0.1:5000` to see the app.

---

## 🗂️ Project Structure

```
text_to_voice_PRO/
│
├── app.py                    # Flask backend (TTS API + routes)
├── requirements.txt          # Python dependencies
├── vercel.json               # Vercel deployment config
├── DEPLOY.md                 # Step-by-step Vercel deployment guide
├── gen_icons.py              # One-time favicon generation script
│
├── templates/
│   └── index.html            # Main single-page UI (Jinja2 template)
│
└── static/
    ├── css/
    │   └── style.css         # Premium dark/light theme CSS
    ├── js/
    │   └── app.js            # Frontend logic (audio, slider, theme)
    ├── icons/
    │   ├── favicon.svg       # SVG favicon (scalable)
    │   ├── favicon-16x16.png
    │   ├── favicon-32x32.png
    │   ├── apple-touch-icon.png
    │   ├── icon-192.png
    │   └── icon-512.png
    └── site.webmanifest      # PWA web app manifest
```

---

## ⚡ Quick Start (Local)

### 1. Prerequisites
- Python 3.9+ installed
- Internet connection (gTTS calls Google's servers)

### 2. Install dependencies

```bash
cd text_to_voice_PRO
pip install flask gtts
```

### 3. Run the server

```bash
python app.py
```

### 4. Open in browser

```
http://127.0.0.1:5000
```

---

## 🚀 Deploy to Vercel

See the full guide in [DEPLOY.md](DEPLOY.md).

**Quick summary:**

```bash
# 1. Push to GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/text-to-voice-pro.git
git push -u origin main

# 2. Import at vercel.com/new → select repo → Deploy
```

Every `git push` after that triggers an automatic re-deploy.

> **Note:** Vercel Hobby plan has a **10-second function timeout**. Very long texts may time out. Upgrade to Pro for a 60-second limit.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python · Flask |
| TTS Engine | [gTTS](https://github.com/pndurette/gTTS) (Google Text-to-Speech) |
| Frontend | Vanilla HTML · CSS · JavaScript |
| Icons | Custom inline SVGs |
| Fonts | Inter (Google Fonts) |
| Deployment | Vercel (serverless Python) |

---

## 🌐 API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/` | Main UI |
| `POST` | `/synthesize` | Generate TTS audio, returns `audio_key` |
| `GET` | `/audio/<key>` | Stream audio for playback |
| `GET` | `/download/<key>` | Download MP3 file |
| `GET` | `/robots.txt` | SEO crawler rules |
| `GET` | `/sitemap.xml` | SEO sitemap |
| `GET` | `/favicon.ico` | App favicon |

### `/synthesize` request body

```json
{
  "text": "Hello world",
  "lang": "en",
  "tld": "co.in",
  "slow": false
}
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + Enter` | Speak the current text |

---

## 🌍 Supported Languages (50+)

Hindi · Punjabi · English (India, British, American, Australia, Canada, Ireland, N.Zealand, S.Africa, Nigeria) · Urdu · Arabic (Standard + Egypt) · French · Spanish (Spain, Mexico, Argentina, Colombia) · German · Chinese (Mandarin) · Japanese · Korean · Portuguese (BR + PT) · Italian · Russian · Dutch · Swedish · Norwegian · Danish · Finnish · Polish · Czech · Romanian · Hungarian · Greek · Turkish · Vietnamese · Thai · Indonesian · Filipino · Malay · Tamil · Telugu · Kannada · Malayalam · Bengali · Gujarati · Marathi · Hebrew · Ukrainian

---

## 📋 Requirements

```
flask>=3.0.0
gtts>=2.5.0
```

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🙏 Credits

- **gTTS** by [Pierre Nicolas Durette](https://github.com/pndurette/gTTS)
- **Inter font** by Rasmus Andersson
- **Icons** — Custom SVG (Lucide-inspired)
