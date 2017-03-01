from flask import Flask
import zmq
import time

from settings import settings

app = Flask(__name__)


def push_message(project):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect('tcp://runner:4444')
    time.sleep(1)
    socket.send_pyobj(project)


@app.route("/webhook/<project>", methods=['POST'])
def webhook(project):

    # validate that project exists
    if project in settings:
        push_message(settings[project])
        return "Success"
    else:
        # todo: return 400
        return "Project does not exist"


if __name__ == "__main__":
    app.run(host='0.0.0.0')
