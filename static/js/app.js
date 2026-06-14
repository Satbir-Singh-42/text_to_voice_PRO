/* ────────────────────────────────────────────────────────────
   Text-to-Voice PRO  ·  Frontend Logic
   ──────────────────────────────────────────────────────────── */

(function () {
  "use strict";

  /* ── Speed config ───────────────────────────────────────────
     gTTS only natively supports slow=True/False.
     For "Fast" we apply AudioContext playbackRate = 1.35×      */
  const SPEED_MAP = [
    { label: "1X",    slow: false, rate: 1.0  },
    { label: "1.2X",  slow: false, rate: 1.2  },
    { label: "1.5X",  slow: false, rate: 1.5  },
    { label: "1.75X", slow: false, rate: 1.75 },
    { label: "2X",    slow: false, rate: 2.0  },
  ];

  /* ── State ──────────────────────────────────────────────── */
  let currentLang     = window.LANGUAGES[0];
  let currentSpeedIdx = 0;
  let isDragging      = false;
  let isDark          = true;

  let textChunks      = [];
  let currentChunkIdx = -1;
  let isSpeaking      = false;
  let stopRequested   = false;

  /* ── DOM helpers ────────────────────────────────────────── */
  const $ = id => document.getElementById(id);

  const langSearch     = $("langSearch");
  const langList       = $("langList");
  const langItems      = Array.from(langList.querySelectorAll(".lang-item"));
  const selectedBadge  = $("selectedLangBadge");
  const textInput      = $("textInput");
  const charCount      = $("charCount");
  const speedSlider    = $("speedSlider");
  const speedLabels    = Array.from(document.querySelectorAll(".speed-label-item"));
  const speakBtn       = $("speakBtn");
  const stopBtn        = $("stopBtn");
  const downloadBtn    = $("downloadBtn");
  const uploadBtn      = $("uploadBtn");
  const fileInput      = $("fileInput");
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
  
  const donateBtn      = $("donateBtn");
  const donateModal    = $("donateModal");
  const donateClose    = $("donateClose");

  const genderFemale    = $("genderFemale");
  const genderMale      = $("genderMale");
  const genderFemaleLbl = document.querySelector('label[for="genderFemale"]');
  const genderMaleLbl   = document.querySelector('label[for="genderMale"]');

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

  /* ── Donate Modal ───────────────────────────────────────── */
  if (donateBtn && donateModal) {
    donateBtn.addEventListener("click", () => donateModal.classList.add("visible"));
    donateClose.addEventListener("click", () => donateModal.classList.remove("visible"));
    donateModal.addEventListener("click", (e) => {
      if (e.target === donateModal) donateModal.classList.remove("visible");
    });
  }

  /* ── Language selection ─────────────────────────────────── */
  function selectLang(item) {
    langItems.forEach(i => i.classList.remove("active"));
    item.classList.add("active");
    currentLang = {
      name: item.dataset.name,
      id:   item.dataset.id,
      slug: item.dataset.slug,
      male: item.dataset.male,
      female: item.dataset.female
    };
    // Strip flag emoji from badge for cleaner look
    selectedBadge.textContent  = currentLang.name.replace(/\p{Emoji_Presentation}\s*/gu, "").trim();

    selectedBadge.style.transform = "scale(1.08)";
    setTimeout(() => (selectedBadge.style.transform = ""), 180);

    // Disable unavailable genders
    if (!currentLang.female || currentLang.female === "None") {
      genderFemale.disabled = true;
      genderFemaleLbl.style.opacity = "0.4";
      genderFemaleLbl.style.cursor = "not-allowed";
      if (genderFemale.checked) genderMale.checked = true;
    } else {
      genderFemale.disabled = false;
      genderFemaleLbl.style.opacity = "1";
      genderFemaleLbl.style.cursor = "pointer";
    }

    if (!currentLang.male || currentLang.male === "None") {
      genderMale.disabled = true;
      genderMaleLbl.style.opacity = "0.4";
      genderMaleLbl.style.cursor = "not-allowed";
      if (genderMale.checked) genderFemale.checked = true;
    } else {
      genderMale.disabled = false;
      genderMaleLbl.style.opacity = "1";
      genderMaleLbl.style.cursor = "pointer";
    }

    if (window.innerWidth <= 720) sidebar.classList.remove("open");
  }

  langItems.forEach(item => item.addEventListener("click", () => selectLang(item)));

  /* ── Auto-Detect Language ───────────────────────────────── */
  function detectLanguage(text) {
    if (!text) return null;
    const scripts = [
      { id: 'hi-in', regex: /[\u0900-\u097F]/g }, // Hindi
      { id: 'pa-in', regex: /[\u0A00-\u0A7F]/g }, // Punjabi
      { id: 'bn-in', regex: /[\u0980-\u09FF]/g }, // Bengali
      { id: 'gu-in', regex: /[\u0A80-\u0AFF]/g }, // Gujarati
      { id: 'ta-in', regex: /[\u0B80-\u0BFF]/g }, // Tamil
      { id: 'te-in', regex: /[\u0C00-\u0C7F]/g }, // Telugu
      { id: 'kn-in', regex: /[\u0C80-\u0CFF]/g }, // Kannada
      { id: 'ml-in', regex: /[\u0D00-\u0D7F]/g }, // Malayalam
      { id: 'ja-jp', regex: /[\u3040-\u309F\u30A0-\u30FF]/g }, // Japanese
      { id: 'ko-kr', regex: /[\uAC00-\uD7A3]/g }, // Korean
      { id: 'zh-cn', regex: /[\u4E00-\u9FAF]/g }, // Chinese
      { id: 'ru-ru', regex: /[\u0400-\u04FF]/g }, // Russian
      { id: 'ar-sa', regex: /[\u0600-\u06FF]/g }, // Arabic
      { id: 'th-th', regex: /[\u0E00-\u0E7F]/g }, // Thai
      { id: 'he-il', regex: /[\u0590-\u05FF]/g }, // Hebrew
      { id: 'el-gr', regex: /[\u0370-\u03FF]/g }, // Greek
    ];

    let bestMatch = null;
    let maxCount = 5; // Require at least 5 chars to auto-switch

    for (const script of scripts) {
      const matches = text.match(script.regex);
      if (matches && matches.length > maxCount) {
        maxCount = matches.length;
        bestMatch = script.id;
      }
    }

    if (!bestMatch) {
      // If no distinct script found, check if it's mostly Latin but current lang is non-Latin
      const latinMatches = text.match(/[a-zA-Z]/g);
      if (latinMatches && latinMatches.length > 5) {
        const isCurrentlyLatin = !scripts.some(s => s.id === currentLang.id);
        if (!isCurrentlyLatin) {
          // Switch back to English (India) as a safe default for Latin text
          return 'en-in'; 
        }
      }
    }
    return bestMatch;
  }

  /* ── Language search ────────────────────────────────────── */
  langSearch.addEventListener("input", () => {
    const q = langSearch.value.toLowerCase().trim();
    langItems.forEach(item => {
      item.classList.toggle("hidden", !item.dataset.name.toLowerCase().includes(q));
    });
  });

  /* ── Speed slider ───────────────────────────────────────── */
  function setSpeed(idx) {
    currentSpeedIdx = Math.max(0, Math.min(SPEED_MAP.length - 1, idx));
    speedSlider.value = currentSpeedIdx;
    speedLabels.forEach((el, i) => el.classList.toggle("active", i === currentSpeedIdx));
    if (audioEl.src) audioEl.playbackRate = SPEED_MAP[currentSpeedIdx].rate;
  }

  speedSlider.addEventListener("input", () => setSpeed(Number(speedSlider.value)));
  speedLabels.forEach((el, i) => el.addEventListener("click", () => setSpeed(i)));

  /* ── Char counter & Auto-Detect ─────────────────────────── */
  let detectTimeout;
  textInput.addEventListener("input", () => {
    const len = textInput.value.length;
    charCount.textContent = `${len.toLocaleString()} chars`;

    clearTimeout(detectTimeout);
    detectTimeout = setTimeout(() => {
      const detectedId = detectLanguage(textInput.value);
      if (detectedId && detectedId !== currentLang.id) {
        const item = langItems.find(i => i.dataset.id === detectedId);
        if (item) {
          selectLang(item);
          setStatus("ready", `Auto-detected language: ${item.dataset.name}`);
        }
      }
    }, 500); // 500ms debounce
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
    if (!stopRequested && isSpeaking) {
      currentChunkIdx++;
      playCurrentChunk();
    } else {
      waveform.classList.remove("playing");
      setStatus("done", "Done — audio finished");
      speakBtn.disabled = false;
      stopBtn.disabled  = true;
    }
  });

  /* ── Scrub bar ──────────────────────────────────────────── */
  function scrubTo(e) {
    const rect = audioTrack.getBoundingClientRect();
    const pct  = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    if (audioEl.duration && isFinite(audioEl.duration)) {
      audioEl.currentTime   = pct * audioEl.duration;
      audioFill.style.width = `${pct * 100}%`;
      audioThumb.style.left = `${pct * 100}%`;
    }
  }
  audioTrack.addEventListener("mousedown", e => { isDragging = true; scrubTo(e); });
  document.addEventListener("mousemove",   e => { if (isDragging) scrubTo(e); });
  document.addEventListener("mouseup",     ()  => { isDragging = false; });

  /* ── Chunking & Pre-fetching Logic ─────────────────────── */
  function chunkText(text) {
    const chunks = [];
    let start = 0;
    for (let i = 0; i < text.length; i++) {
      const char = text[i];
      const isPunc = (char === '.' || char === '?' || char === '!' || char === '\n');
      if (isPunc || i === text.length - 1) {
        while (i + 1 < text.length && (text[i + 1] === '.' || text[i + 1] === '?' || text[i + 1] === '!' || text[i + 1] === '\n')) {
          i++;
        }
        const chunkStr = text.substring(start, i + 1);
        if (chunkStr.trim().length > 0) {
          chunks.push({ text: chunkStr.trim(), start: start, end: i + 1, audioKey: null, status: 'pending' });
        }
        start = i + 1;
      }
    }
    return chunks;
  }

  async function prefetchChunks(startIdx = 0) {
    const gender = document.querySelector('input[name="voiceGender"]:checked').value;
    const voiceId = currentLang[gender];

    for (let i = startIdx; i < textChunks.length; i++) {
      if (stopRequested) return;
      const chunk = textChunks[i];
      if (chunk.status === 'pending') {
        chunk.status = 'fetching';
        try {
          const res = await fetch("/synthesize", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: chunk.text, voice: voiceId })
          });
          const data = await res.json();
          if (data.error) throw new Error(data.error);
          
          chunk.audioKey = data.audio_key;
          
          // Pre-fetch the actual audio file into local memory for instant zero-latency playback
          const audioRes = await fetch(`/audio/${chunk.audioKey}`);
          if (!audioRes.ok) throw new Error("Failed to fetch audio file");
          const blob = await audioRes.blob();
          chunk.blobUrl = URL.createObjectURL(blob);
          
          chunk.status = 'ready';
          
          if (isSpeaking && currentChunkIdx === i && audioEl.paused) {
            playCurrentChunk();
          }
        } catch (err) {
          chunk.status = 'error';
          setStatus("error", "Error loading chunk");
        }
      }
    }
  }

  async function playCurrentChunk() {
    if (stopRequested) return;
    if (currentChunkIdx >= textChunks.length) {
      handleStop();
      return;
    }
    
    const chunk = textChunks[currentChunkIdx];
    if (chunk.status === 'ready') {
      textInput.setSelectionRange(chunk.start, chunk.end);
      textInput.focus();
      hideLoader();
      
      // Setup Media Session for background playback
      if ('mediaSession' in navigator) {
        navigator.mediaSession.metadata = new MediaMetadata({
          title: chunk.text.length > 40 ? chunk.text.substring(0, 40) + '...' : chunk.text,
          artist: 'Text to Voice PRO - ' + selectedBadge.textContent,
        });
        navigator.mediaSession.setActionHandler('play', () => audioEl.play());
        navigator.mediaSession.setActionHandler('pause', () => audioEl.pause());
        navigator.mediaSession.setActionHandler('stop', () => handleStop());
        navigator.mediaSession.setActionHandler('nexttrack', () => {
          if (currentChunkIdx + 1 < textChunks.length) {
            currentChunkIdx++;
            playCurrentChunk();
          }
        });
        navigator.mediaSession.setActionHandler('previoustrack', () => {
          if (currentChunkIdx - 1 >= 0) {
            currentChunkIdx--;
            playCurrentChunk();
          }
        });
      }

      audioEl.src = chunk.blobUrl;
      audioEl.load();
      await audioEl.play();
      audioEl.playbackRate = SPEED_MAP[currentSpeedIdx].rate;
    } else if (chunk.status === 'error') {
      currentChunkIdx++;
      playCurrentChunk();
    } else {
      showLoader("Buffering next part...");
      setStatus("loading", "Buffering...");
    }
  }

  function handleStop() {
    stopRequested = true;
    isSpeaking = false;
    audioEl.pause();
    audioEl.currentTime = 0;
    waveform.classList.remove("playing");
    setStatus("ready", "Stopped");
    speakBtn.disabled = false;
    stopBtn.disabled = true;
    hideLoader();
    textInput.setSelectionRange(0, 0);
  }

  /* ── Speak ──────────────────────────────────────────────── */
  speakBtn.addEventListener("click", async () => {
    const text = textInput.value.trim();
    if (!text) {
      shake(textInput);
      setStatus("error", "Please enter some text first");
      return;
    }

    stopRequested = false;
    isSpeaking = true;
    
    // Cleanup previous blobs to prevent memory leaks
    if (textChunks && textChunks.length > 0) {
      textChunks.forEach(c => {
        if (c.blobUrl) URL.revokeObjectURL(c.blobUrl);
      });
    }

    textChunks = chunkText(textInput.value);

    // Only start from the middle if the user has explicitly highlighted text
    currentChunkIdx = 0;
    if (textInput.selectionStart !== textInput.selectionEnd) {
      const cursor = textInput.selectionStart;
      currentChunkIdx = textChunks.findIndex(c => cursor >= c.start && cursor <= c.end);
      if (currentChunkIdx === -1) currentChunkIdx = 0;
    }

    audioEl.pause();
    audioEl.currentTime = 0;
    waveform.classList.remove("playing");
    speakBtn.disabled = true;
    stopBtn.disabled = false;
    downloadBtn.disabled = false;
    progressWrap.classList.remove("visible");

    showLoader(`Preparing speech…`);
    setStatus("loading", `Preparing speech…`);

    prefetchChunks(currentChunkIdx);
  });

  /* ── Stop ───────────────────────────────────────────────── */
  stopBtn.addEventListener("click", () => {
    handleStop();
    audioFill.style.width   = "0%";
    audioThumb.style.left   = "0%";
    timeCurrent.textContent = "0:00";
  });

  /* ── Download (Full MP3) ────────────────────────────────── */
  downloadBtn.addEventListener("click", async () => {
    const text = textInput.value.trim();
    if (!text) return;

    const langSlug = (currentLang.slug || currentLang.id || "speech")
      .replace(/[^a-z0-9_-]/gi, "_")
      .slice(0, 30);
    const filename = `speech_${langSlug}.mp3`;

    setStatus("loading", `Generating full MP3…`);
    downloadBtn.disabled = true;
    showLoader("Generating full MP3 for download...");

    const gender = document.querySelector('input[name="voiceGender"]:checked').value;
    const voiceId = currentLang[gender];

    try {
      const res = await fetch("/synthesize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, voice: voiceId })
      });
      const data = await res.json();
      if (!res.ok || data.error) throw new Error(data.error || "Server error");

      const audioRes = await fetch(`/audio/${data.audio_key}`);
      if (!audioRes.ok) throw new Error(`Server returned ${audioRes.status}`);
      const blob = await audioRes.blob();
      const url = URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);

      setTimeout(() => URL.revokeObjectURL(url), 10000);
      setStatus("done", `Downloaded ${filename}`);
    } catch (err) {
      setStatus("error", `Download failed: ${err.message}`);
    } finally {
      downloadBtn.disabled = false;
      hideLoader();
    }
  });

  /* ── Clear ──────────────────────────────────────────────── */
  clearBtn.addEventListener("click", () => {
    // Cleanup previous blobs
    if (textChunks && textChunks.length > 0) {
      textChunks.forEach(c => {
        if (c.blobUrl) URL.revokeObjectURL(c.blobUrl);
      });
    }

    textInput.value = "";
    charCount.textContent = "0 chars";
    handleStop();
    audioEl.src = "";
    progressWrap.classList.remove("visible");
    audioFill.style.width = "0%";
    timeCurrent.textContent = "0:00";
    timeDuration.textContent = "0:00";
    downloadBtn.disabled = true;
    setStatus("ready", "Ready — select a language and press Speak");
    textInput.focus();
  });

  /* ── Upload Document ────────────────────────────────────── */
  uploadBtn.addEventListener("click", () => {
    fileInput.click();
  });

  fileInput.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const ext = file.name.split('.').pop().toLowerCase();
    
    // Quick handle for text files directly in browser
    if (ext === "txt") {
      const reader = new FileReader();
      reader.onload = (evt) => {
        textInput.value = evt.target.result;
        textInput.dispatchEvent(new Event("input")); // trigger char count and auto-detect
        setStatus("done", `Loaded ${file.name}`);
      };
      reader.readAsText(file);
      fileInput.value = ""; // reset
      return;
    }

    // For PDF and DOCX, send to backend
    if (ext === "pdf" || ext === "docx") {
      showLoader(`Extracting text from ${file.name}…`);
      setStatus("loading", `Extracting text…`);
      
      const formData = new FormData();
      formData.append("file", file);

      try {
        const res = await fetch("/extract-text", {
          method: "POST",
          body: formData
        });
        const data = await res.json();
        if (!res.ok || data.error) throw new Error(data.error || "Failed to extract text");
        
        textInput.value = data.text;
        textInput.dispatchEvent(new Event("input")); // trigger char count and auto-detect
        setStatus("done", `Extracted text from ${file.name}`);
      } catch (err) {
        setStatus("error", err.message);
      } finally {
        hideLoader();
        fileInput.value = ""; // reset
      }
    } else {
      setStatus("error", "Unsupported file type. Please upload .txt, .pdf, or .docx");
      fileInput.value = ""; // reset
    }
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
  setSpeed(0);
  setStatus("ready", "Ready — select a language and press Speak");
  textInput.focus();

})();
