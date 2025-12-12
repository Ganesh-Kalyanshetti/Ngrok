# app_mic.py
from flask import Flask, request, render_template_string
from datetime import datetime
import os

# Optional Telegram send (set env vars if you want it)
BOT_TOKEN = os.getenv("Add Your Token Here", "").strip()
CHAT_ID   = os.getenv("12345", "").strip()
bot = None
if BOT_TOKEN and CHAT_ID:
    try:
        import telepot
        bot = telepot.Bot(token=BOT_TOKEN)
        print("[OK] Telegram bot initialized for audio sends.")
    except Exception as e:
        print("[WARN] Telegram init failed:", e)

app = Flask(__name__)

INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>️ MCA - MSRIT: Educational Demo</title>
  <title>️ Microphone Recorder (Secure Context)</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: Arial, sans-serif; padding: 24px; background: #f6f7fb; text-align: center; }
    h1 { font-size: 44px; margin: 0 0 6px; color: #222; }
    .note { color: #555; font-size: 18px; max-width: 760px; margin: 8px auto 18px; }
    #controls { margin: 20px 0; }
    button { font-size: 20px; padding: 12px 18px; border-radius: 10px; margin: 0 8px; cursor: pointer; border: 1px solid #ccc; }
    #status { margin-top: 14px; font-weight: 700; color: #333; font-size: 18px; }
    audio { margin-top: 18px; width: 360px; max-width: 90vw; }
    .warn { color: #A33; font-weight: 700; }
    .ok { color: #2A7; font-weight: 700; }
  </style>
</head>
<body>
  <h1>Microphone Recorder</h1>
  <p class="note">
    <b>Privacy notice:</b> This page will request microphone access to record a short clip for
    educational/testing purposes. Continue only if you consent.<br>
    <b>Important:</b> Use <span class="ok">HTTPS</span> (e.g., ngrok) or <span class="ok">localhost</span>.
    On plain HTTP, many browsers disable <code>getUserMedia</code>.
  </p>

  <div id="controls">
    <button id="startBtn">Start Recording</button>
    <button id="stopBtn" disabled>Stop & Upload</button>
  </div>

  <div id="status" class="warn">Idle…</div>
  <audio id="playback" controls style="display:none;"></audio>

  <script>
    // ---- Legacy/compat getUserMedia wrapper ----
    function compatGetUserMedia(constraints) {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        return navigator.mediaDevices.getUserMedia(constraints);
      }
      const legacy = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia;
      if (!legacy) {
        return Promise.reject(new Error("getUserMedia not supported in this context. Use HTTPS or localhost, and allow microphone permissions."));
      }
      return new Promise((res, rej) => legacy.call(navigator, constraints, res, rej));
    }

    // Pick a good MIME type for MediaRecorder
    function pickMime() {
      const candidates = [
        "audio/webm;codecs=opus",
        "audio/webm",
        "audio/ogg;codecs=opus",
        "audio/ogg"
      ];
      for (const c of candidates) {
        if (window.MediaRecorder && MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported(c)) {
          return c;
        }
      }
      return ""; // let browser choose
    }

    let mediaRecorder;
    let chunks = [];
    let streamRef;

    const statusEl = document.getElementById('status');
    const startBtn = document.getElementById('startBtn');
    const stopBtn  = document.getElementById('stopBtn');
    const playback = document.getElementById('playback');

    startBtn.onclick = async () => {
      startBtn.disabled = true;
      stopBtn.disabled  = false;
      chunks = [];
      statusEl.textContent = "Requesting microphone permission…";
      statusEl.className = "";

      try {
        const stream = await compatGetUserMedia({ audio: true, video: false });
        streamRef = stream;
        const mime = pickMime();
        mediaRecorder = new MediaRecorder(stream, mime ? { mimeType: mime } : undefined);

        mediaRecorder.onstart = () => {
          statusEl.textContent = "Recording… Speak now.";
        };
        mediaRecorder.ondataavailable = (e) => {
          if (e.data && e.data.size > 0) chunks.push(e.data);
        };
        mediaRecorder.onstop = async () => {
          try {
            statusEl.textContent = "Preparing upload…";
            const blob = new Blob(chunks, { type: mediaRecorder.mimeType || "audio/webm" });
            playback.src = URL.createObjectURL(blob);
            playback.style.display = "inline-block";

            const fd = new FormData();
            fd.append("audio", blob, "mic_clip.webm");

            const res = await fetch("/upload_audio", {
              method: "POST",
              body: fd,
              credentials: "same-origin"
            });
            if (res.ok) {
              statusEl.textContent = "Upload success ✅";
              statusEl.className = "ok";
            } else {
              const t = await res.text();
              statusEl.textContent = "Upload failed: " + t;
              statusEl.className = "warn";
            }
          } catch (e) {
            statusEl.textContent = "Upload error: " + e.message;
            statusEl.className = "warn";
          } finally {
            // stop audio tracks
            if (streamRef) streamRef.getTracks().forEach(t => t.stop());
            startBtn.disabled = false;
            stopBtn.disabled  = true;
          }
        };

        mediaRecorder.start();
      } catch (err) {
        statusEl.textContent = "Microphone access denied or unavailable: " + err.message;
        statusEl.className = "warn";
        startBtn.disabled = false;
        stopBtn.disabled  = true;
      }
    };

    stopBtn.onclick = () => {
      if (mediaRecorder && mediaRecorder.state === "recording") {
        statusEl.textContent = "Stopping…";
        mediaRecorder.stop();
      }
    };
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(INDEX_HTML)

@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    if "audio" not in request.files:
        return "No audio file received", 400

    audio_file = request.files["audio"]

    os.makedirs("captures_audio", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"captures_audio/mic_{ts}.webm"
    audio_file.save(filename)
    print(f"[INFO] Saved audio: {filename}")

    # Optional Telegram forward
    if bot and CHAT_ID:
        try:
            with open(filename, "rb") as f:
                bot.sendAudio(CHAT_ID, f, caption=f"Mic clip at {ts}")
        except Exception as e:
            print("[WARN] Telegram send error:", e)

    return "OK", 200

if __name__ == "__main__":
    # Use 0.0.0.0 so it works via LAN and tunnels; use HTTPS (ngrok) for remote mic access.
    app.run(host="0.0.0.0", port=5006, debug=True)
