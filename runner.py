import logging
import sys
import time
import zmq
from subprocess import Popen, PIPE


class Builder:

    def __init__(self, repo):
        """just a simple unix epoc timestamp

        this guarantees that we will have unique workspace folders
        """
        self.TIMESTAMP = int(time.time())

        """
        the subfolder where the git repo is checked out. Build assets
        and artifacts live here was well
        """
        self.WORKSPACE = 'workspace/{}'.format(self.TIMESTAMP)

        """git repo, the full url

        example: git@github.com:3cosystem/website.git
                 https://github.com/3cosystem/website.git
        """
        self.REPO = repo

    def procrun(self, command, directory=None, logmessage=None):
        """run a shell command. this is the method used to run the
        various commands that will build, test, and deploy."""

        if directory is None:
            directory = self.WORKSPACE

        if logmessage is not None:
            logging.info(logmessage)

        out = ''

        # change to the subfolder and then execute the command
        c = 'cd {} && {}'.format(directory, command)

        with Popen(c, stdout=PIPE, bufsize=1, universal_newlines=True,
                   shell=True) as p:

            for line in p.stdout:
                out += line
                logging.info(line.strip())

            out2, err = p.communicate()

            if p.returncode != 0:
                raise Exception(err)

        return out

    def create_workspace(self):
        """create the workspace folder"""
        self.procrun('mkdir -p {}'.format(self.WORKSPACE),
                     directory='.',
                     logmessage="Creating workspace...")

    def clone_repo(self):
        """clone the repo into the workspace folder"""
        self.procrun("git clone {} {}".format(self.REPO, self.WORKSPACE),
                     directory='.',
                     logmessage="Cloning repo...")

    def check_has_changes(self):
        """check that the most recent git tags commit hash does not match
        with the most recent commit hash."""

        # most recent tag (eg 0.0.12)
        latest_tag = self.procrun("git describe --abbrev=0 --tags").strip()

        # hash for most recent tag
        tag_hash = self.procrun("git show-ref --tags |"
                                " grep {} | awk '{{print $1}}'"
                                .format(latest_tag)).strip()

        head_hash = self.procrun("git rev-parse HEAD").strip()

        if tag_hash == head_hash:
            msg = ("Repo as not changed. Stopping.\n"
                   "Latest tag: {0}\n"
                   "Tag hash  : {1}\n"
                   "Head hash : {2}")

            self.procrun('rm -rf {}'.format(self.WORKSPACE))

            raise Exception(msg.format(latest_tag, tag_hash, head_hash))

        logging.info("Code has changed since last push. Continuing...")

    def run_commands(self):
        """run a series of shell commands in the order as they appear.

        TODO: maybe make this configurable as an array of strings which
        get run"""

        # this is a hack for when timezones are funny. not too sure...
        self.procrun('touch Makefile')
        self.procrun('make ci-deploy')

    def run_build(self):
        msg = ("Repository     : {}\n"
               "Working folder : {}\n"
               "Timestamp      : {}")
        logging.info(msg.format(self.REPO, self.WORKSPACE, self.TIMESTAMP))

        self.create_workspace()
        self.clone_repo()
        self.check_has_changes()
        self.run_commands()


class Runner:

    def __init__(self):
        pass

    def start(self):

        logging.info('Starting subscriber listening on socket')
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.bind('tcp://*:4444')
        socket.setsockopt(zmq.SUBSCRIBE, b'')

        while True:
            logging.debug('inside while')
            message = socket.recv_pyobj()
            if message:
                logging.debug('received message')
                self.run_build(message)
                time.sleep(3)

    def run_build_tmp(self, message):
        logging.debug(message)

    def run_build(self, message):
        repo = message["repo"]
        builder = Builder(repo)

        try:
            builder.run_build()

        except Exception as e:
            msg = ("Step FAILED!\n"
                   "*********** BEGIN ERROR MESSAGE ***********\n"
                   "{}\n"
                   "************ END ERROR MESSAGE ***********")
            logging.error(msg.format(e))


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s:%(message)s',
                        stream=sys.stdout, level=logging.DEBUG)

    runner = Runner()
    runner.start()
