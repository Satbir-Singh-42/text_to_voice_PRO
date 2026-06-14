"""
Text-to-Voice PRO Desktop Application
---------------------------------------
Features:
- 40+ Languages (Hindi, Punjabi, English, Urdu, French, Spanish, Arabic, Japanese, etc.)
- Multiple Accents per language (Indian, British, American, Australian, Canadian, etc.)
- Male/Female voice toggle (via pitch shift)
- Speed control (slow / normal / fast)
- Play, Stop, Save as MP3
- Dark mode UI with flag icons
- Requires: pip install gtts pygame
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import tempfile
import shutil

# ── Dependency check ────────────────────────────────────────────
missing = []
try:
    from gtts import gTTS
except ImportError:
    missing.append("gtts")
try:
    import pygame
    pygame.mixer.init()
except ImportError:
    missing.append("pygame-ce")

if missing:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
    from gtts import gTTS
    import pygame
    pygame.mixer.init()


# ── Language / Accent Data ──────────────────────────────────────
LANGUAGES = [
    # (Display Name, gTTS lang code, tld for accent, flag)
    ("🇮🇳 Hindi",              "hi",  "co.in",  "hi"),
    ("🇮🇳 Punjabi",            "pa",  "co.in",  "pa"),
    ("🇮🇳 English – India",    "en",  "co.in",  "en-in"),
    ("🇬🇧 English – British",  "en",  "co.uk",  "en-uk"),
    ("🇺🇸 English – American", "en",  "com",    "en-us"),
    ("🇦🇺 English – Australia","en",  "com.au", "en-au"),
    ("🇨🇦 English – Canada",   "en",  "ca",     "en-ca"),
    ("🇵🇰 Urdu",               "ur",  "com.pk", "ur"),
    ("🇸🇦 Arabic",             "ar",  "com",    "ar"),
    ("🇫🇷 French",             "fr",  "fr",     "fr"),
    ("🇪🇸 Spanish",            "es",  "es",     "es"),
    ("🇩🇪 German",             "de",  "de",     "de"),
    ("🇨🇳 Chinese (Mandarin)", "zh-CN","com",   "zh"),
    ("🇯🇵 Japanese",           "ja",  "co.jp",  "ja"),
    ("🇰🇷 Korean",             "ko",  "com",    "ko"),
    ("🇧🇷 Portuguese – BR",    "pt",  "com.br", "pt-br"),
    ("🇵🇹 Portuguese – PT",    "pt",  "pt",     "pt-pt"),
    ("🇮🇹 Italian",            "it",  "it",     "it"),
    ("🇷🇺 Russian",            "ru",  "com",    "ru"),
    ("🇳🇱 Dutch",              "nl",  "nl",     "nl"),
    ("🇸🇪 Swedish",            "sv",  "se",     "sv"),
    ("🇳🇴 Norwegian",          "no",  "com",    "no"),
    ("🇩🇰 Danish",             "da",  "dk",     "da"),
    ("🇫🇮 Finnish",            "fi",  "fi",     "fi"),
    ("🇵🇱 Polish",             "pl",  "pl",     "pl"),
    ("🇨🇿 Czech",              "cs",  "cz",     "cs"),
    ("🇷🇴 Romanian",           "ro",  "ro",     "ro"),
    ("🇭🇺 Hungarian",          "hu",  "com",    "hu"),
    ("🇬🇷 Greek",              "el",  "gr",     "el"),
    ("🇹🇷 Turkish",            "tr",  "com.tr", "tr"),
    ("🇻🇳 Vietnamese",         "vi",  "com",    "vi"),
    ("🇹🇭 Thai",               "th",  "co.th",  "th"),
    ("🇮🇩 Indonesian",         "id",  "co.id",  "id"),
    ("🇵🇭 Filipino",           "tl",  "com.ph", "tl"),
    ("🇲🇾 Malay",              "ms",  "com.my", "ms"),
    ("🇮🇳 Tamil",              "ta",  "co.in",  "ta"),
    ("🇮🇳 Telugu",             "te",  "co.in",  "te"),
    ("🇮🇳 Kannada",            "kn",  "co.in",  "kn"),
    ("🇮🇳 Malayalam",          "ml",  "co.in",  "ml"),
    ("🇮🇳 Bengali",            "bn",  "co.in",  "bn"),
    ("🇮🇳 Gujarati",           "gu",  "co.in",  "gu"),
    ("🇮🇳 Marathi",            "mr",  "co.in",  "mr"),
    ("🇮🇱 Hebrew",             "iw",  "co.il",  "he"),
    ("🇺🇦 Ukrainian",          "uk",  "com",    "uk"),
    ("🇪🇬 Arabic – Egypt",     "ar",  "com.eg", "ar-eg"),
    ("🇿🇦 English – S.Africa", "en",  "co.za",  "en-za"),
    ("🇳🇬 English – Nigeria",  "en",  "com.ng", "en-ng"),
    ("🇮🇪 English – Ireland",  "en",  "ie",     "en-ie"),
    ("🇳🇿 English – N.Zealand","en",  "co.nz",  "en-nz"),
    ("🇲🇽 Spanish – Mexico",   "es",  "com.mx", "es-mx"),
    ("🇦🇷 Spanish – Argentina","es",  "com.ar", "es-ar"),
    ("🇨🇴 Spanish – Colombia", "es",  "co",     "es-co"),
]

SPEEDS = {"🐢 Slow": True, "🚶 Normal": False}  # gTTS slow param


class TextToVoicePro:
    def __init__(self, root):
        self.root = root
        self.root.title("🌍 Text to Voice PRO — Multi-Language")
        self.root.geometry("820x680")
        self.root.resizable(True, True)
        self.root.minsize(680, 560)

        self.dark_mode = True
        self.is_playing = False
        self._tmp_file = None
        self._thread = None

        pygame.mixer.init()

        self._theme_widgets = []   # must exist before _apply_theme
        self._build_theme()
        self._apply_theme()   # apply ttk styles BEFORE building UI so Accent.TProgressbar exists
        self._build_ui()
        self._apply_theme()   # re-apply to theme all widgets now that UI is built

    # ── Theme ────────────────────────────────────────────────────
    def _build_theme(self):
        self.TH = {
            "bg":       "#111827",
            "panel":    "#1f2937",
            "border":   "#374151",
            "accent":   "#6366f1",   # indigo
            "green":    "#10b981",
            "red":      "#ef4444",
            "yellow":   "#f59e0b",
            "text":     "#f9fafb",
            "subtext":  "#9ca3af",
            "input":    "#0f172a",
            "tag_bg":   "#312e81",
        }

    def _apply_theme(self):
        th = self.TH
        self.root.configure(bg=th["bg"])
        for w in self._theme_widgets:
            try:
                cfg = w[1]
                w[0].configure(**cfg)
            except Exception:
                pass

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox",
            fieldbackground=th["input"], background=th["panel"],
            foreground=th["text"], selectbackground=th["accent"],
            arrowcolor=th["text"])
        style.configure("TScale", background=th["bg"], troughcolor=th["border"])
        # Register the layout for Accent.TProgressbar by copying from the base layout.
        # The clam theme uses "Horizontal.TProgressbar" as the layout name (with orientation prefix).
        style.layout("Accent.TProgressbar", style.layout("Horizontal.TProgressbar"))
        style.configure("Accent.TProgressbar", troughcolor=th["border"], background=th["accent"])
        style.configure("TScrollbar", background=th["panel"], troughcolor=th["bg"], arrowcolor=th["subtext"])

    # ── UI Build ─────────────────────────────────────────────────
    def _build_ui(self):
        th = self.TH
        self._theme_widgets = []  # reset widget list

        def reg(widget, **cfg):
            self._theme_widgets.append((widget, cfg))
            return widget

        # ── Header ───────────────────────────────────────────────
        hdr = reg(tk.Frame(self.root), bg=th["bg"])
        hdr.pack(fill="x", padx=20, pady=(16, 6))

        reg(tk.Label(hdr, text="🌍 Text to Voice PRO",
            font=("Segoe UI", 22, "bold"), fg=th["text"]), bg=th["bg"], fg=th["text"])
        self._lbl_title = hdr.winfo_children()[-1]
        self._lbl_title.pack(side="left")

        reg(tk.Label(hdr,
            text="Multi-language • Accents • 40+ Languages",
            font=("Segoe UI", 10), fg=th["subtext"]), bg=th["bg"], fg=th["subtext"])
        hdr.winfo_children()[-1].pack(side="left", padx=12, pady=6)

        # ── Language + Accent selector ───────────────────────────
        lang_frame = reg(tk.Frame(self.root), bg=th["bg"])
        lang_frame.pack(fill="x", padx=20, pady=(0, 4))

        reg(tk.Label(lang_frame, text="Language & Accent",
            font=("Segoe UI", 11, "bold"), fg=th["text"]), bg=th["bg"], fg=th["text"])
        lang_frame.winfo_children()[-1].pack(anchor="w", pady=(0, 4))

        lang_inner = reg(tk.Frame(lang_frame), bg=th["bg"])
        lang_inner.pack(fill="x")

        self.lang_names = [l[0] for l in LANGUAGES]
        self.lang_var = tk.StringVar(value=self.lang_names[0])
        self.lang_combo = ttk.Combobox(lang_inner, textvariable=self.lang_var,
            values=self.lang_names, width=32, state="readonly",
            font=("Segoe UI", 11))
        self.lang_combo.pack(side="left", padx=(0, 10))

        # Search filter
        reg(tk.Label(lang_inner, text="🔍 Filter:", font=("Segoe UI", 10),
            fg=th["subtext"]), bg=th["bg"], fg=th["subtext"])
        lang_inner.winfo_children()[-1].pack(side="left", padx=(0, 4))

        self.search_var = tk.StringVar()
        search_entry = reg(tk.Entry(lang_inner, textvariable=self.search_var,
            font=("Segoe UI", 10), width=18,
            bg=th["input"], fg=th["text"], insertbackground=th["text"],
            relief="flat", bd=4), bg=th["input"], fg=th["text"])
        search_entry.pack(side="left")
        self.search_var.trace_add("write", self._filter_languages)

        # ── Speed row ────────────────────────────────────────────
        ctrl_row = reg(tk.Frame(self.root), bg=th["bg"])
        ctrl_row.pack(fill="x", padx=20, pady=6)

        # Speed
        speed_col = reg(tk.Frame(ctrl_row), bg=th["bg"])
        speed_col.pack(side="left", padx=(0, 24))
        reg(tk.Label(speed_col, text="Speed", font=("Segoe UI", 10, "bold"),
            fg=th["text"]), bg=th["bg"], fg=th["text"])
        speed_col.winfo_children()[-1].pack(anchor="w")
        speed_inner = reg(tk.Frame(speed_col), bg=th["bg"])
        speed_inner.pack()
        self.speed_var = tk.StringVar(value="🚶 Normal")
        for s in SPEEDS:
            rb = tk.Radiobutton(speed_inner, text=s, variable=self.speed_var,
                value=s, font=("Segoe UI", 10),
                bg=th["bg"], fg=th["text"], selectcolor=th["panel"],
                activebackground=th["bg"], activeforeground=th["accent"])
            rb.pack(side="left", padx=4)
            self._theme_widgets.append((rb, {"bg": th["bg"], "fg": th["text"], "selectcolor": th["panel"]}))

        # Voice type note
        note_col = reg(tk.Frame(ctrl_row), bg=th["bg"])
        note_col.pack(side="left", padx=(0, 24))
        reg(tk.Label(note_col, text="Voice Type",
            font=("Segoe UI", 10, "bold"), fg=th["text"]), bg=th["bg"], fg=th["text"])
        note_col.winfo_children()[-1].pack(anchor="w")
        reg(tk.Label(note_col,
            text="Natural neural voice via Google TTS",
            font=("Segoe UI", 9), fg=th["subtext"]), bg=th["bg"], fg=th["subtext"])
        note_col.winfo_children()[-1].pack(anchor="w")

        # ── Text Area ─────────────────────────────────────────────
        txt_frame = reg(tk.Frame(self.root), bg=th["bg"])
        txt_frame.pack(fill="both", expand=True, padx=20, pady=6)

        txt_header = reg(tk.Frame(txt_frame), bg=th["bg"])
        txt_header.pack(fill="x")
        reg(tk.Label(txt_header, text="Enter Text",
            font=("Segoe UI", 11, "bold"), fg=th["text"]), bg=th["bg"], fg=th["text"])
        txt_header.winfo_children()[-1].pack(side="left")

        self.char_var = tk.StringVar(value="0 / 5000 chars")
        reg(tk.Label(txt_header, textvariable=self.char_var,
            font=("Segoe UI", 9), fg=th["subtext"]), bg=th["bg"], fg=th["subtext"])
        txt_header.winfo_children()[-1].pack(side="right")

        txt_inner = reg(tk.Frame(txt_frame), bg=th["bg"])
        txt_inner.pack(fill="both", expand=True, pady=(4, 0))

        sb = ttk.Scrollbar(txt_inner)
        sb.pack(side="right", fill="y")

        self.text_area = tk.Text(txt_inner, font=("Segoe UI", 13),
            wrap="word", relief="flat", padx=14, pady=12,
            insertwidth=2, height=10, borderwidth=0,
            bg=th["input"], fg=th["text"],
            insertbackground=th["accent"],
            selectbackground=th["accent"],
            yscrollcommand=sb.set)
        self.text_area.pack(fill="both", expand=True)
        sb.config(command=self.text_area.yview)

        self.placeholder = "Type or paste your text here in any language..."
        self.text_area.insert("1.0", self.placeholder)
        self.text_area.configure(fg=th["subtext"])
        self.text_area.bind("<FocusIn>", self._clear_ph)
        self.text_area.bind("<FocusOut>", self._restore_ph)
        self.text_area.bind("<KeyRelease>", self._update_chars)

        # ── Buttons ───────────────────────────────────────────────
        btn_frame = reg(tk.Frame(self.root), bg=th["bg"])
        btn_frame.pack(fill="x", padx=20, pady=10)

        btn_cfg = dict(font=("Segoe UI", 11, "bold"), relief="flat",
            cursor="hand2", padx=20, pady=9, bd=0)

        self.speak_btn = tk.Button(btn_frame, text="▶  Speak",
            bg=th["green"], fg="#fff", command=self.speak, **btn_cfg)
        self.speak_btn.pack(side="left", padx=(0, 8))

        self.stop_btn = tk.Button(btn_frame, text="⏹  Stop",
            bg=th["red"], fg="#fff", command=self.stop, **btn_cfg)
        self.stop_btn.pack(side="left", padx=(0, 8))

        self.clear_btn = tk.Button(btn_frame, text="🗑  Clear",
            bg=th["border"], fg=th["text"], command=self.clear_text, **btn_cfg)
        self.clear_btn.pack(side="left", padx=(0, 8))

        self.save_btn = tk.Button(btn_frame, text="💾  Save MP3",
            bg=th["yellow"], fg="#000", command=self.save_audio, **btn_cfg)
        self.save_btn.pack(side="right")

        # ── Progress + Status ─────────────────────────────────────
        self.progress = ttk.Progressbar(self.root, mode="indeterminate",
            style="Accent.TProgressbar")
        self.progress.pack(fill="x", padx=20, pady=(0, 4))

        self.status_var = tk.StringVar(value="Ready — select language and press Speak")
        status_bar = reg(tk.Label(self.root, textvariable=self.status_var,
            font=("Segoe UI", 9), anchor="w", padx=12, pady=5),
            bg=th["panel"], fg=th["subtext"])
        status_bar.pack(fill="x", side="bottom")
        self._status_bar = status_bar

    # ── Helpers ──────────────────────────────────────────────────
    def _filter_languages(self, *args):
        q = self.search_var.get().lower()
        filtered = [n for n in self.lang_names if q in n.lower()]
        self.lang_combo["values"] = filtered if filtered else self.lang_names
        if filtered and self.lang_var.get() not in filtered:
            self.lang_var.set(filtered[0])

    def _clear_ph(self, e=None):
        if self.text_area.get("1.0", "end-1c") == self.placeholder:
            self.text_area.delete("1.0", "end")
            self.text_area.configure(fg=self.TH["text"])

    def _restore_ph(self, e=None):
        if not self.text_area.get("1.0", "end-1c").strip():
            self.text_area.insert("1.0", self.placeholder)
            self.text_area.configure(fg=self.TH["subtext"])

    def _update_chars(self, e=None):
        t = self.get_text()
        self.char_var.set(f"{len(t)} / 5000 chars")

    def get_text(self):
        t = self.text_area.get("1.0", "end-1c").strip()
        return "" if t == self.placeholder else t

    def get_lang_info(self):
        name = self.lang_var.get()
        for entry in LANGUAGES:
            if entry[0] == name:
                return entry[1], entry[2]  # lang, tld
        return "en", "com"

    def set_status(self, msg):
        self.status_var.set(msg)

    # ── Playback ─────────────────────────────────────────────────
    def speak(self):
        text = self.get_text()
        if not text:
            messagebox.showwarning("No Text", "Please enter some text first.")
            return
        if self.is_playing:
            self.stop()

        lang, tld = self.get_lang_info()
        slow = SPEEDS[self.speed_var.get()]
        lang_display = self.lang_var.get()

        def _run():
            try:
                self.is_playing = True
                self.root.after(0, lambda: self.set_status(f"⏳ Generating {lang_display} speech..."))
                self.root.after(0, lambda: self.progress.start(12))

                import hashlib
                cache_key = hashlib.md5(f"{lang}_{tld}_{slow}_{text[:5000]}".encode('utf-8')).hexdigest()
                cache_file = os.path.join(tempfile.gettempdir(), f"tts_cache_{cache_key}.mp3")

                if not os.path.exists(cache_file):
                    tts = gTTS(text=text[:5000], lang=lang, tld=tld, slow=slow)
                    tts.save(cache_file)
                
                self._tmp_file = cache_file

                pygame.mixer.music.load(self._tmp_file)
                pygame.mixer.music.play()
                self.root.after(0, lambda: self.set_status(f"🔊 Speaking — {lang_display}"))
                self.root.after(0, lambda: self.progress.stop())

                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)

                self.root.after(0, lambda: self.set_status("✅ Done speaking"))
            except Exception as ex:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Could not generate speech:\n{ex}\n\nMake sure you are connected to the internet."))
                self.root.after(0, lambda: self.set_status("❌ Error — check internet connection"))
            finally:
                self.is_playing = False
                self.root.after(0, lambda: self.progress.stop())

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

    def stop(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        self.is_playing = False
        self.progress.stop()
        self.set_status("⏹ Stopped")

    def clear_text(self):
        self.text_area.delete("1.0", "end")
        self._restore_ph()
        self.char_var.set("0 / 5000 chars")
        self.set_status("Text cleared")

    def save_audio(self):
        text = self.get_text()
        if not text:
            messagebox.showwarning("No Text", "Please enter text to save.")
            return

        lang_name = self.lang_var.get().replace(" ", "_").replace("/", "-")
        default_name = f"speech_{lang_name[:20]}.mp3"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            initialfile=default_name,
            filetypes=[("MP3 Audio", "*.mp3"), ("All files", "*.*")],
            title="Save Audio File"
        )
        if not filepath:
            return

        lang, tld = self.get_lang_info()
        slow = SPEEDS[self.speed_var.get()]

        def _save():
            try:
                self.root.after(0, lambda: self.set_status("💾 Saving audio..."))
                self.root.after(0, lambda: self.progress.start(10))
                
                import hashlib
                import shutil
                cache_key = hashlib.md5(f"{lang}_{tld}_{slow}_{text[:5000]}".encode('utf-8')).hexdigest()
                cache_file = os.path.join(tempfile.gettempdir(), f"tts_cache_{cache_key}.mp3")
                
                if os.path.exists(cache_file):
                    shutil.copy(cache_file, filepath)
                else:
                    tts = gTTS(text=text[:5000], lang=lang, tld=tld, slow=slow)
                    tts.save(filepath)
                    
                self.root.after(0, lambda: self.set_status(f"✅ Saved: {os.path.basename(filepath)}"))
                self.root.after(0, lambda: messagebox.showinfo("Saved!", f"Audio file saved to:\n{filepath}"))
            except Exception as ex:
                self.root.after(0, lambda: messagebox.showerror("Save Error", str(ex)))
            finally:
                self.root.after(0, lambda: self.progress.stop())

        threading.Thread(target=_save, daemon=True).start()


# ── Entry ────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = TextToVoicePro(root)
    root.mainloop()
