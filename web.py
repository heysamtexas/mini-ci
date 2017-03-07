from flask import Flask
import zmq
import time

import settings
import importlib

app = Flask(__name__)


def push_message(project):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect('tcp://runner:4444')
    time.sleep(1)
    socket.send_pyobj(project)


@app.route("/webhook/<project>", methods=['POST'])
def webhook(project):

    importlib.reload(settings)

    # validate that project exists
    if project in settings.settings:
        push_message(settings.settings[project])
        return "Success"
    else:
        # todo: return 400
        return "Project does not exist"


if __name__ == "__main__":
    app.run(host='0.0.0.0')
