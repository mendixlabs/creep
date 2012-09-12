import sleekxmpp
import logging
import signal
import os
import yaml
from plugins import load_plugins 

logging.basicConfig(level=logging.INFO)

yamlfile = '/usr/local/etc/creep.yaml' if os.path.isfile('/usr/local/etc/creep.yaml') else 'creep.yaml'
config = yaml.load(open(yamlfile))

conn = sleekxmpp.ClientXMPP(
    '%s/%s' % (config['xmpp']['jid'], config['xmpp']['resource']),
    config['xmpp']['password']
)

conn.register_plugin('xep_0045')

logging.info("Connecting %s" % config['xmpp']['jid'])
if 'server' in config['xmpp'] and 'port' in config['xmpp']:
    conn.connect((config['xmpp']['server'], config['xmpp']['port']))
else:
    conn.connect()
logging.info("Connected")

conn.process()
def handle_connected(self):
    conn.send_presence()
    logging.info("Started processing")
    for room in config['xmpp'].get('autojoin',[]):
        conn.plugin['xep_0045'].joinMUC(room,
            'creep',
            wait=True)
        logging.info("Connected to chat room '%s'" % room)

def handle_message(message):
    body = message['body']
    if not from_us(message):
        command = body.split(' ')[0] if ' ' in body else body
        params = body[body.find(" ")+1:] if ' ' in body else None
        if command in handlers:
            handler = handlers[command]
            result = handler(message=params, origin=message.get_from())
            message.reply(result).send()
        else:
            reply = 'Unknown command: \n%s' % body
            message.reply(reply).send()

    logging.debug('Handled request "%s"' % body)
    
def from_us(message):
    if message.get_mucroom():
        message_from = str(message.get_from())
        (location, resource) = message_from.split('/')
        return (resource == conn.plugin['xep_0045'].ourNicks[location])
    return False

conn.add_event_handler("session_start", handle_connected)
conn.add_event_handler('message', handle_message)

activated_plugins = ['quotes', 'http-json']
handlers = load_plugins(activated_plugins, conn, config)
def handle_ctrl_c(signal, frame):
    conn.disconnect(wait=True)

signal.signal(signal.SIGINT, handle_ctrl_c)

