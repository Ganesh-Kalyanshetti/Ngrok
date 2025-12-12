from flask import Flask
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def show_time():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return f"<h1>Current Time: {now}</h1>"

if __name__ == '__main__':
    app.run(port=5000)
