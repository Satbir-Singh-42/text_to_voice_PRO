"""
Text-to-Voice PRO — Flask Web Backend
Generates speech via gTTS and serves audio to the browser.
"""

from flask import Flask, request, jsonify, send_file, render_template
import hashlib, os, tempfile

app = Flask(__name__)
CACHE_DIR = os.path.join(tempfile.gettempdir(), "tts_web_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

LANGUAGES = [
    {"name": "🇮🇳 Hindi",               "lang": "hi",    "tld": "co.in",   "id": "hi"},
    {"name": "🇮🇳 Punjabi",             "lang": "pa",    "tld": "co.in",   "id": "pa"},
    {"name": "🇮🇳 English – India",     "lang": "en",    "tld": "co.in",   "id": "en-in"},
    {"name": "🇬🇧 English – British",   "lang": "en",    "tld": "co.uk",   "id": "en-uk"},
    {"name": "🇺🇸 English – American",  "lang": "en",    "tld": "com",     "id": "en-us"},
    {"name": "🇦🇺 English – Australia", "lang": "en",    "tld": "com.au",  "id": "en-au"},
    {"name": "🇨🇦 English – Canada",    "lang": "en",    "tld": "ca",      "id": "en-ca"},
    {"name": "🇵🇰 Urdu",                "lang": "ur",    "tld": "com.pk",  "id": "ur"},
    {"name": "🇸🇦 Arabic",              "lang": "ar",    "tld": "com",     "id": "ar"},
    {"name": "🇫🇷 French",              "lang": "fr",    "tld": "fr",      "id": "fr"},
    {"name": "🇪🇸 Spanish",             "lang": "es",    "tld": "es",      "id": "es"},
    {"name": "🇩🇪 German",              "lang": "de",    "tld": "de",      "id": "de"},
    {"name": "🇨🇳 Chinese (Mandarin)",  "lang": "zh-CN", "tld": "com",     "id": "zh"},
    {"name": "🇯🇵 Japanese",            "lang": "ja",    "tld": "co.jp",   "id": "ja"},
    {"name": "🇰🇷 Korean",              "lang": "ko",    "tld": "com",     "id": "ko"},
    {"name": "🇧🇷 Portuguese – BR",     "lang": "pt",    "tld": "com.br",  "id": "pt-br"},
    {"name": "🇵🇹 Portuguese – PT",     "lang": "pt",    "tld": "pt",      "id": "pt-pt"},
    {"name": "🇮🇹 Italian",             "lang": "it",    "tld": "it",      "id": "it"},
    {"name": "🇷🇺 Russian",             "lang": "ru",    "tld": "com",     "id": "ru"},
    {"name": "🇳🇱 Dutch",               "lang": "nl",    "tld": "nl",      "id": "nl"},
    {"name": "🇸🇪 Swedish",             "lang": "sv",    "tld": "se",      "id": "sv"},
    {"name": "🇳🇴 Norwegian",           "lang": "no",    "tld": "com",     "id": "no"},
    {"name": "🇩🇰 Danish",              "lang": "da",    "tld": "dk",      "id": "da"},
    {"name": "🇫🇮 Finnish",             "lang": "fi",    "tld": "fi",      "id": "fi"},
    {"name": "🇵🇱 Polish",              "lang": "pl",    "tld": "pl",      "id": "pl"},
    {"name": "🇨🇿 Czech",               "lang": "cs",    "tld": "cz",      "id": "cs"},
    {"name": "🇷🇴 Romanian",            "lang": "ro",    "tld": "ro",      "id": "ro"},
    {"name": "🇭🇺 Hungarian",           "lang": "hu",    "tld": "com",     "id": "hu"},
    {"name": "🇬🇷 Greek",               "lang": "el",    "tld": "gr",      "id": "el"},
    {"name": "🇹🇷 Turkish",             "lang": "tr",    "tld": "com.tr",  "id": "tr"},
    {"name": "🇻🇳 Vietnamese",          "lang": "vi",    "tld": "com",     "id": "vi"},
    {"name": "🇹🇭 Thai",                "lang": "th",    "tld": "co.th",   "id": "th"},
    {"name": "🇮🇩 Indonesian",          "lang": "id",    "tld": "co.id",   "id": "id"},
    {"name": "🇵🇭 Filipino",            "lang": "tl",    "tld": "com.ph",  "id": "tl"},
    {"name": "🇲🇾 Malay",               "lang": "ms",    "tld": "com.my",  "id": "ms"},
    {"name": "🇮🇳 Tamil",               "lang": "ta",    "tld": "co.in",   "id": "ta"},
    {"name": "🇮🇳 Telugu",              "lang": "te",    "tld": "co.in",   "id": "te"},
    {"name": "🇮🇳 Kannada",             "lang": "kn",    "tld": "co.in",   "id": "kn"},
    {"name": "🇮🇳 Malayalam",           "lang": "ml",    "tld": "co.in",   "id": "ml"},
    {"name": "🇮🇳 Bengali",             "lang": "bn",    "tld": "co.in",   "id": "bn"},
    {"name": "🇮🇳 Gujarati",            "lang": "gu",    "tld": "co.in",   "id": "gu"},
    {"name": "🇮🇳 Marathi",             "lang": "mr",    "tld": "co.in",   "id": "mr"},
    {"name": "🇮🇱 Hebrew",              "lang": "iw",    "tld": "co.il",   "id": "he"},
    {"name": "🇺🇦 Ukrainian",           "lang": "uk",    "tld": "com",     "id": "uk"},
    {"name": "🇪🇬 Arabic – Egypt",      "lang": "ar",    "tld": "com.eg",  "id": "ar-eg"},
    {"name": "🇿🇦 English – S.Africa",  "lang": "en",    "tld": "co.za",   "id": "en-za"},
    {"name": "🇳🇬 English – Nigeria",   "lang": "en",    "tld": "com.ng",  "id": "en-ng"},
    {"name": "🇮🇪 English – Ireland",   "lang": "en",    "tld": "ie",      "id": "en-ie"},
    {"name": "🇳🇿 English – N.Zealand", "lang": "en",    "tld": "co.nz",   "id": "en-nz"},
    {"name": "🇲🇽 Spanish – Mexico",    "lang": "es",    "tld": "com.mx",  "id": "es-mx"},
    {"name": "🇦🇷 Spanish – Argentina", "lang": "es",    "tld": "com.ar",  "id": "es-ar"},
    {"name": "🇨🇴 Spanish – Colombia",  "lang": "es",    "tld": "co",      "id": "es-co"},
]


@app.route("/")
def index():
    return render_template("index.html", languages=LANGUAGES)


@app.route("/favicon.ico")
def favicon():
    return send_file(
        os.path.join(app.root_path, "static", "icons", "favicon-32x32.png"),
        mimetype="image/png"
    )


@app.route("/robots.txt")
def robots():
    from flask import Response
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /audio/\n"
        "Disallow: /download/\n"
        "Sitemap: https://voicepro.vercel.app/sitemap.xml\n"
    )
    return Response(content, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    from flask import Response
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        '  <url>\n'
        '    <loc>https://voicepro.vercel.app/</loc>\n'
        '    <changefreq>monthly</changefreq>\n'
        '    <priority>1.0</priority>\n'
        '  </url>\n'
        '</urlset>'
    )
    return Response(xml, mimetype="application/xml")



@app.route("/synthesize", methods=["POST"])
def synthesize():
    from gtts import gTTS
    data = request.get_json()
    text = (data.get("text") or "").strip()
    lang = data.get("lang", "en")
    tld  = data.get("tld", "com")
    slow = bool(data.get("slow", False))

    if not text:
        return jsonify({"error": "No text provided"}), 400

    cache_key = hashlib.md5(f"{lang}_{tld}_{slow}_{text}".encode("utf-8")).hexdigest()
    cache_path = os.path.join(CACHE_DIR, f"{cache_key}.mp3")

    if not os.path.exists(cache_path):
        try:
            tts = gTTS(text=text, lang=lang, tld=tld, slow=slow)
            tts.save(cache_path)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"audio_key": cache_key})


@app.route("/audio/<key>")
def audio(key):
    # Sanitize key — only hex chars allowed
    if not all(c in "0123456789abcdef" for c in key):
        return "Invalid key", 400
    path = os.path.join(CACHE_DIR, f"{key}.mp3")
    if not os.path.exists(path):
        return "Not found", 404
    return send_file(path, mimetype="audio/mpeg")


@app.route("/download/<key>")
def download(key):
    if not all(c in "0123456789abcdef" for c in key):
        return "Invalid key", 400
    path = os.path.join(CACHE_DIR, f"{key}.mp3")
    if not os.path.exists(path):
        return "Not found", 404
    filename = request.args.get("name", "speech.mp3")
    return send_file(path, mimetype="audio/mpeg",
                     as_attachment=True, download_name=filename)


if __name__ == "__main__":
    print("Text-to-Voice PRO web server running at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
