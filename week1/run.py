import sys
sys.path.append("./myapp")

from flask import Flask, send_from_directory, redirect, url_for, render_template
from flask_socketio import SocketIO, emit

from myapp import simulation

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

if __name__ == '__main__':
    socketio.run(app)

@app.route('/')
def send_index():
    return redirect(url_for('send_static', path='html/index.html'))

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('myapp/static', path)

world = simulation.Simulation()

@socketio.on('connect')
def test_connect():
    print('connection! sending a response...')
    for i in range(1000):
        world.update()
        update_client()

def update_client():
    emit('update', world.get_packet())