from flask import Flask, request, render_template_string

app = Flask(__name__)
messages = []

@app.route('/', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form.get('name')
        msg = request.form.get('msg')
        messages.append((name, msg))
    return render_template_string('''
    <h1>💬 Live Feedback Board</h1>
    <form method="POST">
        Name: <input name="name"><br>
        Message: <input name="msg"><br>
        <button type="submit">Send</button>
    </form>
    <hr>
    {% for n,m in messages %}
        <p><b>{{n}}:</b> {{m}}</p>
    {% endfor %}
    ''', messages=messages)

if __name__ == '__main__':
    app.run(port=5002)
