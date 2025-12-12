from flask import Flask, request
from pyngrok import ngrok

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        data = request.json
        print("Data received:", data)
        return {"status": "success", "received": data}
    return "<h3>Hello Testing MCA - RIT </h3>"

if __name__ == "__main__":
    public_url = ngrok.connect(5000)
    print("Public URL:", public_url)
    app.run(port=5000)
