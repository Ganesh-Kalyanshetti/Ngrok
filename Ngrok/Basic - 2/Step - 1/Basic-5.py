from flask import Flask, request, render_template_string

app = Flask(__name__)
votes = {"Python": 0, "AI": 0, "IoT": 0, "ML": 0}

@app.route('/', methods=['GET', 'POST'])
def vote():
    if request.method == 'POST':
        choice = request.form.get('option')
        if choice in votes:
            votes[choice] += 1

    return render_template_string('''
    <html>
    <head>
        <title>️ Live Voting App</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; background-color: #f0f0f0; }
            h2 { font-size: 50px; color: #333; }
            form { margin-top: 40px; font-size: 28px; }
            select, button { font-size: 28px; padding: 10px 20px; margin: 10px; border-radius: 10px; }
            hr { margin: 40px; }
            h3 { font-size: 36px; color: #222; }
            p { font-size: 28px; color: #444; }
        </style>
    </head>
    <body>
        <h2>️Ramaiah Institute of Technology (RIT) </h2>
        <h2> Live Voting App</h2>
        <form method="POST">
            <label for="option">Select Your Favorite Tech:</label><br>
            <select name="option" id="option">
                {% for opt in votes %}
                    <option value="{{opt}}">{{opt}}</option>
                {% endfor %}
            </select>
            <button type="submit">Vote</button>
        </form>
        <hr>
        <h3>📊 Live Results</h3>
        {% for opt, count in votes.items() %}
            <p><b>{{opt}}:</b> {{count}} votes</p>
        {% endfor %}
    </body>
    </html>
    ''', votes=votes)

if __name__ == '__main__':
    app.run(port=5004)
