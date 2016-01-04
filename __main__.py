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

    yamlfile = ('/usr/local/etc/creep.yaml'
                if os.path.isfile('/usr/local/etc/creep.yaml') else
                'creep.yaml')
    config = yaml.load(open(yamlfile))

    creep = Creep(config)

    def handle_ctrl_c(signal, frame):
        creep.shutdown()

    signal.signal(signal.SIGINT, handle_ctrl_c)
    # wait for a signal, so the main thread does not vanish (which means it
    # would not be there anymore to react on ctrl-c)
    creep.run()
    signal.pause()
