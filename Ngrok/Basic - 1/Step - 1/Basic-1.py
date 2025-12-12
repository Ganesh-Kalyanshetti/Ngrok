### sudo apt update
### pip install flask pyngrok



from flask import Flask
from pyngrok import ngrok
print("▗▖  ▗▖ ▗▄▄▖ ▗▄▖         ▗▄▄▖ ▗▄▄▄▖▗▄▄▄▖")
print("▐▛▚▞▜▌▐▌   ▐▌ ▐▌        ▐▌ ▐▌  █    █  ")
print("▐▌  ▐▌▐▌   ▐▛▀▜▌        ▐▛▀▚▖  █    █  ")
print("▐▌  ▐▌▝▚▄▄▖▐▌ ▐▌        ▐▌ ▐▌▗▄█▄▖  █  ")
print("                                       ")


app = Flask(__name__)

@app.route('/')
def home():
    return "<h2>Hello from Flask using Ngrok! </h2>"

if __name__ == "__main__":
    # Start ngrok tunnel on port 5000
    public_url = ngrok.connect(5000)
    print("🌐 Public URL:", public_url)
    
    # Run Flask app
    app.run(port=5000)

