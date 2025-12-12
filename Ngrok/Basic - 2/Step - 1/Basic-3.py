from flask import Flask, request
from datetime import datetime
import socket
import uuid
import requests

app = Flask(__name__)

click_logs = []

def get_local_ip():
    # Get the local IP of the machine running Flask
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unknown"

def get_public_ip():
    # Get the public IP of the machine (requires internet)
    try:
        return requests.get('https://api.ipify.org').text
    except:
        return "Unknown"

def get_mac_address():
    # Get the MAC address of the machine
    mac = uuid.getnode()
    mac_str = ':'.join(['{:02x}'.format((mac >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])
    return mac_str

@app.route('/')
def show_time():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_ip = request.remote_addr
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    mac_addr = get_mac_address()

    click_logs.append((now, user_ip, local_ip, public_ip, mac_addr))
    print(f"[{now}] Visitor: {user_ip}, Local IP: {local_ip}, Public IP: {public_ip}, MAC: {mac_addr}")

    return f"""
    <h1>Ramaiah Institute of Technology (RIT)</h1>
    <h1>Current Time: {now}</h1>
    <p><b>Your IP:</b> {user_ip}</p>
    <p><b>Server Local IP:</b> {local_ip}</p>
    <p><b>Server Public IP:</b> {public_ip}</p>
    <p><b>Server MAC Address:</b> {mac_addr}</p>
    <p>This access has been logged.</p>
    """

@app.route('/logs')
def show_logs():
    html = ""
    for time, ip, local_ip, public_ip, mac in click_logs:
        html += f"Clicked at {time} from {ip} | Local: {local_ip} | Public: {public_ip} | MAC: {mac}<br>"
    return html

if __name__ == '__main__':
    app.run(port=5001)
