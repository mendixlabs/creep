import signal
from creep import Creep
import logging
import os
import yaml
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

    signal.signal(signal.SIGINT, handle_ctrl_c)
    # wait for a signal, so the main thread does not vanish (which means it
    # would not be there anymore to react on ctrl-c)
    creep.run()
    signal.pause()
