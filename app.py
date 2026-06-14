"""
Text-to-Voice PRO — Flask Web Backend
Generates speech via gTTS and serves audio to the browser.
"""

from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
import hashlib, os, tempfile

app = Flask(__name__)
CACHE_DIR = os.path.join(tempfile.gettempdir(), "tts_web_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

LANGUAGES = [
    {
        "name": "🇮🇳 Hindi",
        "id": "hi-in",
        "female": "hi-IN-SwaraNeural",
        "male": "hi-IN-MadhurNeural"
    },
    {
        "name": "🇮🇳 English – India",
        "id": "en-in",
        "female": "en-IN-NeerjaExpressiveNeural",
        "male": "en-IN-PrabhatNeural"
    },
    {
        "name": "🇬🇧 English – British",
        "id": "en-gb",
        "female": "en-GB-LibbyNeural",
        "male": "en-GB-RyanNeural"
    },
    {
        "name": "🇺🇸 English – American",
        "id": "en-us",
        "female": "en-US-AvaNeural",
        "male": "en-US-AndrewNeural"
    },
    {
        "name": "🇦🇺 English – Australia",
        "id": "en-au",
        "female": "en-AU-NatashaNeural",
        "male": "en-AU-WilliamMultilingualNeural"
    },
    {
        "name": "🇨🇦 English – Canada",
        "id": "en-ca",
        "female": "en-CA-ClaraNeural",
        "male": "en-CA-LiamNeural"
    },
    {
        "name": "🇵🇰 Urdu",
        "id": "ur-pk",
        "female": "ur-PK-UzmaNeural",
        "male": "ur-PK-AsadNeural"
    },
    {
        "name": "🇸🇦 Arabic",
        "id": "ar-sa",
        "female": "ar-SA-ZariyahNeural",
        "male": "ar-SA-HamedNeural"
    },
    {
        "name": "🇫🇷 French",
        "id": "fr-fr",
        "female": "fr-FR-VivienneMultilingualNeural",
        "male": "fr-FR-RemyMultilingualNeural"
    },
    {
        "name": "🇪🇸 Spanish",
        "id": "es-es",
        "female": "es-ES-XimenaNeural",
        "male": "es-ES-AlvaroNeural"
    },
    {
        "name": "🇩🇪 German",
        "id": "de-de",
        "female": "de-DE-SeraphinaMultilingualNeural",
        "male": "de-DE-FlorianMultilingualNeural"
    },
    {
        "name": "🇨🇳 Chinese (Mandarin)",
        "id": "zh-cn",
        "female": "zh-CN-XiaoxiaoNeural",
        "male": "zh-CN-YunjianNeural"
    },
    {
        "name": "🇯🇵 Japanese",
        "id": "ja-jp",
        "female": "ja-JP-NanamiNeural",
        "male": "ja-JP-KeitaNeural"
    },
    {
        "name": "🇰🇷 Korean",
        "id": "ko-kr",
        "female": "ko-KR-SunHiNeural",
        "male": "ko-KR-HyunsuMultilingualNeural"
    },
    {
        "name": "🇧🇷 Portuguese – BR",
        "id": "pt-br",
        "female": "pt-BR-ThalitaMultilingualNeural",
        "male": "pt-BR-AntonioNeural"
    },
    {
        "name": "🇵🇹 Portuguese – PT",
        "id": "pt-pt",
        "female": "pt-PT-RaquelNeural",
        "male": "pt-PT-DuarteNeural"
    },
    {
        "name": "🇮🇹 Italian",
        "id": "it-it",
        "female": "it-IT-ElsaNeural",
        "male": "it-IT-GiuseppeMultilingualNeural"
    },
    {
        "name": "🇷🇺 Russian",
        "id": "ru-ru",
        "female": "ru-RU-SvetlanaNeural",
        "male": "ru-RU-DmitryNeural"
    },
    {
        "name": "🇳🇱 Dutch",
        "id": "nl-nl",
        "female": "nl-NL-ColetteNeural",
        "male": "nl-NL-MaartenNeural"
    },
    {
        "name": "🇸🇪 Swedish",
        "id": "sv-se",
        "female": "sv-SE-SofieNeural",
        "male": "sv-SE-MattiasNeural"
    },
    {
        "name": "🇩🇰 Danish",
        "id": "da-dk",
        "female": "da-DK-ChristelNeural",
        "male": "da-DK-JeppeNeural"
    },
    {
        "name": "🇫🇮 Finnish",
        "id": "fi-fi",
        "female": "fi-FI-NooraNeural",
        "male": "fi-FI-HarriNeural"
    },
    {
        "name": "🇵🇱 Polish",
        "id": "pl-pl",
        "female": "pl-PL-ZofiaNeural",
        "male": "pl-PL-MarekNeural"
    },
    {
        "name": "🇨🇿 Czech",
        "id": "cs-cz",
        "female": "cs-CZ-VlastaNeural",
        "male": "cs-CZ-AntoninNeural"
    },
    {
        "name": "🇷🇴 Romanian",
        "id": "ro-ro",
        "female": "ro-RO-AlinaNeural",
        "male": "ro-RO-EmilNeural"
    },
    {
        "name": "🇭🇺 Hungarian",
        "id": "hu-hu",
        "female": "hu-HU-NoemiNeural",
        "male": "hu-HU-TamasNeural"
    },
    {
        "name": "🇬🇷 Greek",
        "id": "el-gr",
        "female": "el-GR-AthinaNeural",
        "male": "el-GR-NestorasNeural"
    },
    {
        "name": "🇹🇷 Turkish",
        "id": "tr-tr",
        "female": "tr-TR-EmelNeural",
        "male": "tr-TR-AhmetNeural"
    },
    {
        "name": "🇻🇳 Vietnamese",
        "id": "vi-vn",
        "female": "vi-VN-HoaiMyNeural",
        "male": "vi-VN-NamMinhNeural"
    },
    {
        "name": "🇹🇭 Thai",
        "id": "th-th",
        "female": "th-TH-PremwadeeNeural",
        "male": "th-TH-NiwatNeural"
    },
    {
        "name": "🇮🇩 Indonesian",
        "id": "id-id",
        "female": "id-ID-GadisNeural",
        "male": "id-ID-ArdiNeural"
    },
    {
        "name": "🇲🇾 Malay",
        "id": "ms-my",
        "female": "ms-MY-YasminNeural",
        "male": "ms-MY-OsmanNeural"
    },
    {
        "name": "🇮🇳 Tamil",
        "id": "ta-in",
        "female": "ta-IN-PallaviNeural",
        "male": "ta-IN-ValluvarNeural"
    },
    {
        "name": "🇮🇳 Telugu",
        "id": "te-in",
        "female": "te-IN-ShrutiNeural",
        "male": "te-IN-MohanNeural"
    },
    {
        "name": "🇮🇳 Kannada",
        "id": "kn-in",
        "female": "kn-IN-SapnaNeural",
        "male": "kn-IN-GaganNeural"
    },
    {
        "name": "🇮🇳 Malayalam",
        "id": "ml-in",
        "female": "ml-IN-SobhanaNeural",
        "male": "ml-IN-MidhunNeural"
    },
    {
        "name": "🇮🇳 Bengali",
        "id": "bn-in",
        "female": "bn-IN-TanishaaNeural",
        "male": "bn-IN-BashkarNeural"
    },
    {
        "name": "🇮🇳 Gujarati",
        "id": "gu-in",
        "female": "gu-IN-DhwaniNeural",
        "male": "gu-IN-NiranjanNeural"
    },
    {
        "name": "🇮🇳 Marathi",
        "id": "mr-in",
        "female": "mr-IN-AarohiNeural",
        "male": "mr-IN-ManoharNeural"
    },
    {
        "name": "🇮🇱 Hebrew",
        "id": "he-il",
        "female": "he-IL-HilaNeural",
        "male": "he-IL-AvriNeural"
    },
    {
        "name": "🇺🇦 Ukrainian",
        "id": "uk-ua",
        "female": "uk-UA-PolinaNeural",
        "male": "uk-UA-OstapNeural"
    },
    {
        "name": "🇪🇬 Arabic – Egypt",
        "id": "ar-eg",
        "female": "ar-EG-SalmaNeural",
        "male": "ar-EG-ShakirNeural"
    },
    {
        "name": "🇿🇦 English – S.Africa",
        "id": "en-za",
        "female": "en-ZA-LeahNeural",
        "male": "en-ZA-LukeNeural"
    },
    {
        "name": "🇳🇬 English – Nigeria",
        "id": "en-ng",
        "female": "en-NG-EzinneNeural",
        "male": "en-NG-AbeoNeural"
    },
    {
        "name": "🇮🇪 English – Ireland",
        "id": "en-ie",
        "female": "en-IE-EmilyNeural",
        "male": "en-IE-ConnorNeural"
    },
    {
        "name": "🇳🇿 English – N.Zealand",
        "id": "en-nz",
        "female": "en-NZ-MollyNeural",
        "male": "en-NZ-MitchellNeural"
    },
    {
        "name": "🇲🇽 Spanish – Mexico",
        "id": "es-mx",
        "female": "es-MX-DaliaNeural",
        "male": "es-MX-JorgeNeural"
    },
    {
        "name": "🇦🇷 Spanish – Argentina",
        "id": "es-ar",
        "female": "es-AR-ElenaNeural",
        "male": "es-AR-TomasNeural"
    },
    {
        "name": "🇨🇴 Spanish – Colombia",
        "id": "es-co",
        "female": "es-CO-SalomeNeural",
        "male": "es-CO-GonzaloNeural"
    }
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
    import edge_tts
    import asyncio
    data = request.get_json() or {}
    text = (data.get("text") or "").strip()
    voice = data.get("voice", "en-US-JennyNeural")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    cache_key = hashlib.md5(f"{voice}_{text}".encode("utf-8")).hexdigest()
    cache_path = os.path.join(CACHE_DIR, f"{cache_key}.mp3")

    if not os.path.exists(cache_path):
        try:
            communicate = edge_tts.Communicate(text, voice)
            asyncio.run(communicate.save(cache_path))
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
    safe_filename = secure_filename(filename)
    if not safe_filename:
        safe_filename = "speech.mp3"
        
    return send_file(path, mimetype="audio/mpeg",
                     as_attachment=True, download_name=safe_filename)


@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

if __name__ == "__main__":
    print("Text-to-Voice PRO web server running at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
