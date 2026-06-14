/* ────────────────────────────────────────────────────────────
   Text-to-Voice PRO  ·  Frontend Logic
   ──────────────────────────────────────────────────────────── */

(function () {
  "use strict";

  /* ── Speed config ───────────────────────────────────────────
     gTTS only natively supports slow=True/False.
     For "Fast" we apply AudioContext playbackRate = 1.35×      */
  const SPEED_MAP = [
    { label: "Slow",   slow: true,  rate: 0.85 },
    { label: "Normal", slow: false, rate: 1.0  },
    { label: "Fast",   slow: false, rate: 1.35 },
  ];

  /* ── State ──────────────────────────────────────────────── */
  let currentLang     = window.LANGUAGES[0];
  let currentSpeedIdx = 1;
  let currentAudioKey = null;
  let isDragging      = false;
  let isDark          = true;

  /* ── DOM helpers ────────────────────────────────────────── */
  const $ = id => document.getElementById(id);

  const langSearch     = $("langSearch");
  const langList       = $("langList");
  const langItems      = Array.from(langList.querySelectorAll(".lang-item"));
  const selectedBadge  = $("selectedLangBadge");
  const accentLangCode = $("accentLangCode");
  const accentTld      = $("accentTld");
  const textInput      = $("textInput");
  const charCount      = $("charCount");
  const speedSlider    = $("speedSlider");
  const speedLabels    = Array.from(document.querySelectorAll(".speed-label-item"));
  const speakBtn       = $("speakBtn");
  const stopBtn        = $("stopBtn");
  const downloadBtn    = $("downloadBtn");
  const clearBtn       = $("clearBtn");
  const audioEl        = $("audioPlayer");
  const waveform       = $("waveform");
  const progressWrap   = $("progressWrap");
  const audioTrack     = $("audioTrack");
  const audioFill      = $("audioFill");
  const audioThumb     = $("audioThumb");
  const timeCurrent    = $("timeCurrent");
  const timeDuration   = $("timeDuration");
  const statusDot      = $("statusDot");
  const statusText     = $("statusText");
  const loaderOverlay  = $("loaderOverlay");
  const loaderText     = $("loaderText");
  const sidebarToggle  = $("sidebarToggle");
  const sidebar        = $("sidebar");
  const themeToggle    = $("themeToggle");
  const iconMoon       = $("iconMoon");
  const iconSun        = $("iconSun");

  /* ── Theme ──────────────────────────────────────────────── */
  function applyTheme(dark) {
    isDark = dark;
    document.body.classList.toggle("light", !dark);
    // Swap moon ↔ sun icon
    iconMoon.style.display = dark  ? "" : "none";
    iconSun.style.display  = !dark ? "" : "none";
    localStorage.setItem("tts-theme", dark ? "dark" : "light");
  }

  themeToggle.addEventListener("click", () => applyTheme(!isDark));

  // Restore saved preference
  if (localStorage.getItem("tts-theme") === "light") applyTheme(false);

  /* ── Language selection ─────────────────────────────────── */
  function selectLang(item) {
    langItems.forEach(i => i.classList.remove("active"));
    item.classList.add("active");
    currentLang = {
      name: item.dataset.name,
      lang: item.dataset.lang,
      tld:  item.dataset.tld,
      id:   item.dataset.id,
      slug: item.dataset.slug,
    };
    // Strip flag emoji from badge for cleaner look
    selectedBadge.textContent  = currentLang.name.replace(/\p{Emoji_Presentation}\s*/gu, "").trim();
    accentLangCode.textContent = currentLang.lang;
    accentTld.textContent      = currentLang.tld;

    selectedBadge.style.transform = "scale(1.08)";
    setTimeout(() => (selectedBadge.style.transform = ""), 180);

    if (window.innerWidth <= 720) sidebar.classList.remove("open");
  }

  langItems.forEach(item => item.addEventListener("click", () => selectLang(item)));

  /* ── Language search ────────────────────────────────────── */
  langSearch.addEventListener("input", () => {
    const q = langSearch.value.toLowerCase().trim();
    langItems.forEach(item => {
      item.classList.toggle("hidden", !item.dataset.name.toLowerCase().includes(q));
    });
  });

  /* ── Speed slider ───────────────────────────────────────── */
  function setSpeed(idx) {
    currentSpeedIdx = Math.max(0, Math.min(2, idx));
    speedSlider.value = currentSpeedIdx;
    speedLabels.forEach((el, i) => el.classList.toggle("active", i === currentSpeedIdx));
    if (audioEl.src) audioEl.playbackRate = SPEED_MAP[currentSpeedIdx].rate;
  }

  speedSlider.addEventListener("input", () => setSpeed(Number(speedSlider.value)));
  speedLabels.forEach((el, i) => el.addEventListener("click", () => setSpeed(i)));

  /* ── Char counter ───────────────────────────────────────── */
  textInput.addEventListener("input", () => {
    const len = textInput.value.length;
    charCount.textContent = `${len.toLocaleString()} chars`;
  });

  /* ── Status ─────────────────────────────────────────────── */
  function setStatus(state, msg) {
    statusDot.className = `status-dot ${state}`;
    statusText.textContent = msg;
  }
  function showLoader(msg) {
    loaderText.textContent = msg;
    loaderOverlay.classList.add("visible");
  }
  function hideLoader() { loaderOverlay.classList.remove("visible"); }

  /* ── Time format ────────────────────────────────────────── */
  function fmtTime(sec) {
    if (!isFinite(sec) || isNaN(sec)) return "0:00";
    return `${Math.floor(sec / 60)}:${String(Math.floor(sec % 60)).padStart(2, "0")}`;
  }

  /* ── Audio progress ─────────────────────────────────────── */
  function updateProgress() {
    if (!audioEl.duration || isDragging) return;
    const pct = (audioEl.currentTime / audioEl.duration) * 100;
    audioFill.style.width   = `${pct}%`;
    audioThumb.style.left   = `${pct}%`;
    timeCurrent.textContent = fmtTime(audioEl.currentTime);
  }

  audioEl.addEventListener("timeupdate", updateProgress);
  audioEl.addEventListener("loadedmetadata", () => {
    timeDuration.textContent = fmtTime(audioEl.duration);
    progressWrap.classList.add("visible");
  });
  audioEl.addEventListener("play", () => {
    waveform.classList.add("playing");
    setStatus("playing", `Speaking — ${selectedBadge.textContent}`);
    speakBtn.disabled = true;
    stopBtn.disabled  = false;
  });
  audioEl.addEventListener("pause", () => waveform.classList.remove("playing"));
  audioEl.addEventListener("ended", () => {
    waveform.classList.remove("playing");
    setStatus("done", "Done — audio finished");
    speakBtn.disabled = false;
    stopBtn.disabled  = true;
  });

  /* ── Scrub bar ──────────────────────────────────────────── */
  function scrubTo(e) {
    const rect = audioTrack.getBoundingClientRect();
    const pct  = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    if (audioEl.duration) {
      audioEl.currentTime   = pct * audioEl.duration;
      audioFill.style.width = `${pct * 100}%`;
      audioThumb.style.left = `${pct * 100}%`;
    }
  }
  audioTrack.addEventListener("mousedown", e => { isDragging = true; scrubTo(e); });
  document.addEventListener("mousemove",   e => { if (isDragging) scrubTo(e); });
  document.addEventListener("mouseup",     ()  => { isDragging = false; });

  /* ── Speak ──────────────────────────────────────────────── */
  speakBtn.addEventListener("click", async () => {
    const text = textInput.value.trim();
    if (!text) {
      shake(textInput);
      setStatus("error", "Please enter some text first");
      return;
    }

    // Reset player
    audioEl.pause();
    audioEl.currentTime = 0;
    waveform.classList.remove("playing");
    speakBtn.disabled    = true;
    stopBtn.disabled     = false;
    downloadBtn.disabled = true;
    progressWrap.classList.remove("visible");

    const speed = SPEED_MAP[currentSpeedIdx];
    showLoader(`Generating speech…`);
    setStatus("loading", `Generating speech…`);

    try {
      const res = await fetch("/synthesize", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({
          text,
          lang: currentLang.lang,
          tld:  currentLang.tld,
          slow: speed.slow,
        }),
      });

      const data = await res.json();
      if (!res.ok || data.error) throw new Error(data.error || "Server error");

      currentAudioKey = data.audio_key;
      hideLoader();

      audioEl.src          = `/audio/${currentAudioKey}`;
      audioEl.playbackRate = speed.rate;
      audioEl.load();
      await audioEl.play();
      downloadBtn.disabled = false;

    } catch (err) {
      hideLoader();
      setStatus("error", `Error: ${err.message}`);
      speakBtn.disabled = false;
      stopBtn.disabled  = true;
    }
  });

  /* ── Stop ───────────────────────────────────────────────── */
  stopBtn.addEventListener("click", () => {
    audioEl.pause();
    audioEl.currentTime = 0;
    waveform.classList.remove("playing");
    setStatus("ready", "Stopped");
    speakBtn.disabled = false;
    stopBtn.disabled  = true;
    audioFill.style.width   = "0%";
    audioThumb.style.left   = "0%";
    timeCurrent.textContent = "0:00";
  });

  /* ── Download (fixed) ───────────────────────────────────── */
  downloadBtn.addEventListener("click", async () => {
    if (!currentAudioKey) return;

    // Build a safe ASCII filename from the language name
    const langSlug = (currentLang.slug || currentLang.id || "speech")
      .replace(/[^a-z0-9_-]/gi, "_")
      .slice(0, 30);
    const filename = `speech_${langSlug}.mp3`;

    setStatus("loading", `Preparing download…`);
    downloadBtn.disabled = true;

    try {
      // Fetch the audio blob directly — most reliable cross-browser download method
      const res = await fetch(`/audio/${currentAudioKey}`);
      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      const blob = await res.blob();
      const url  = URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href     = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);

      // Revoke object URL after a short delay
      setTimeout(() => URL.revokeObjectURL(url), 10000);

      setStatus("done", `Downloaded ${filename}`);
    } catch (err) {
      setStatus("error", `Download failed: ${err.message}`);
    } finally {
      downloadBtn.disabled = false;
    }
  });

  /* ── Clear ──────────────────────────────────────────────── */
  clearBtn.addEventListener("click", () => {
    textInput.value        = "";
    charCount.textContent  = "0 chars";
    audioEl.pause();
    audioEl.src = "";
    waveform.classList.remove("playing");
    progressWrap.classList.remove("visible");
    audioFill.style.width    = "0%";
    timeCurrent.textContent  = "0:00";
    timeDuration.textContent = "0:00";
    speakBtn.disabled    = false;
    stopBtn.disabled     = true;
    downloadBtn.disabled = true;
    currentAudioKey      = null;
    setStatus("ready", "Ready — select a language and press Speak");
    textInput.focus();
  });

  /* ── Sidebar (mobile) ───────────────────────────────────── */
  sidebarToggle.addEventListener("click", () => sidebar.classList.toggle("open"));
  document.addEventListener("click", e => {
    if (window.innerWidth <= 720 &&
        !sidebar.contains(e.target) &&
        !sidebarToggle.contains(e.target)) {
      sidebar.classList.remove("open");
    }
  });

  /* ── Shake helper ───────────────────────────────────────── */
  function shake(el) {
    el.style.animation = "none";
    void el.offsetHeight; // reflow
    el.style.animation = "shakeInput 0.4s ease";
    el.addEventListener("animationend", () => (el.style.animation = ""), { once: true });
  }
  const shakeStyle = document.createElement("style");
  shakeStyle.textContent = `
    @keyframes shakeInput {
      0%,100%{transform:translateX(0)} 20%{transform:translateX(-6px)}
      40%{transform:translateX(6px)}   60%{transform:translateX(-4px)}
      80%{transform:translateX(4px)}
    }`;
  document.head.appendChild(shakeStyle);

  /* ── Keyboard: Ctrl/Cmd+Enter → Speak ──────────────────── */
  document.addEventListener("keydown", e => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      if (!speakBtn.disabled) speakBtn.click();
    }
  });

  /* ── Init ───────────────────────────────────────────────── */
  selectLang(langItems[0]);
  setSpeed(1);
  setStatus("ready", "Ready — select a language and press Speak");
  textInput.focus();

})();
