from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

# Store click logs in memory (you can later save to a file or database)
click_logs = []

@app.route('/')
def show_time():
    # Get current server time
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Get client IP address
    user_ip = request.remote_addr

    # Log the access
    click_logs.append((now, user_ip))
    print(f"Clicked at {now} from {user_ip}")

    return f"""
    <h1>Ramaiah Institute of Technology (RIT)</h1>
    <h1>Current Time: {now}</h1>
    <p>Your IP: {user_ip}</p>
    <p>This access has been logged.</p>
    """

@app.route('/logs')
def show_logs():
    return '<br>'.join([f"Clicked at {time} from {ip}" for time, ip in click_logs])

if __name__ == '__main__':
    app.run(port=5001)
