from flask import Flask, redirect, url_for, send_from_directory
app = Flask(__name__)

@app.route('/')
def send_index():
    return redirect(url_for('send_static', path='html/index.html'))

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('myapp/static', path)