import signal
from creep import Creep
import logging
import sys
from slackbot.bot import respond_to

creep = None


@respond_to('.*')
def handle_message(message):
    if creep:
        creep.handle_message(message)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    creep = Creep()

    def handle_ctrl_c(signal, frame):
        creep.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_ctrl_c)
    creep.run()
