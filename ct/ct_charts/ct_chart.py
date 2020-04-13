import argparse
import time

from flask import Flask, Response, render_template

application = Flask(__name__)


@application.route('/')
def main():
    return render_template('index.html')


@application.route('/stream')
def stream():

    def generate_chart_data():
        for line in open(args.input, 'r'):
            json_data = line

            # 2 \n\n are needed or the message won't get the other side (to the html)
            # I don't even want to know why is does like this
            # It is not even recognized by all versions of Python. Grrrrrr
            yield f"data:{json_data}\n\n"
            time.sleep(args.speed / 1000)

    return Response(generate_chart_data(), mimetype='text/event-stream')


if __name__ == "__main__":

    ###############
    # Read options:
    ###############
    parser = argparse.ArgumentParser(description='args')
    parser.add_argument("-i", "--input", help="Load a file to playback (F# distribution over time)", required=True)
    parser.add_argument("-s", "--speed", help="Speed of the animation (in millisec)", type=int, default=0.2, required=True)
    args = parser.parse_args()

    application.run(debug=False, port=1234, host='0.0.0.0', threaded=True)
