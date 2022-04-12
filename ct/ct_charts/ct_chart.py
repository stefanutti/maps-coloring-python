import argparse
import time
import json

from flask import Flask, render_template
from flask_socketio import SocketIO

application = Flask(__name__)
socket_io = SocketIO(application, logger=False, engineio_logger=False)


@application.route('/')
def main():
    return render_template('index.html')


@socket_io.on('speed_event')
def speed_event(message):
    global animation_speed
    animation_speed = message["speed"]
    # print("Debug (speed_event) - animation_speed:", animation_speed)


def stream():
    while True:
        for line in open(args.input, 'r'):
            json_data_line = line
            json_data = json.loads(json_data_line)
            # print("Debug (stream) - json_data:", json_data)

            # Send data
            socket_io.emit('readings', json_data)
            # print("Debug (stream) - animation_speed:", animation_speed)
            time.sleep(animation_speed)
        time.sleep(5)


if __name__ == "__main__":

    global animation_speed
    global args

    # It will be se by the slider (html)
    animation_speed = 0.5

    # Read options
    parser = argparse.ArgumentParser(description='args')
    parser.add_argument("-i", "--input", help="Load a file to playback (F# distribution over time)", required=True)
    args = parser.parse_args()

    # Start
    socket_io.start_background_task(stream)
    application.run(debug=False, port=1234, host='0.0.0.0', threaded=True)
