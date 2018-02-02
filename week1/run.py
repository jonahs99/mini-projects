import sys
sys.path.append("./myapp")

import eventlet
eventlet.monkey_patch()

from flask import Flask, send_from_directory, redirect, url_for, render_template
from flask_socketio import SocketIO, emit

from myapp import simulation
from myapp.timer import call_repeatedly, call_once

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

started = False

@socketio.on('connect')
def test_connect():
    global started
    if not started:
        started = True
        start()

def start():
    world = simulation.Simulation()

    def tick():
        world.update()
        socketio.emit('update', world.get_packet())
        tick()

    call_repeatedly(0.05, tick)