from flask import Flask, request, make_response, render_template, redirect
import sleekxmpp
import logging
import signal
import os
import yaml
from base64 import decodestring
from plugins import handlers #magic happens here :S

logging.basicConfig(level=logging.INFO)

yamlfile = '/usr/local/etc/creep.yaml' if os.path.isfile('/usr/local/etc/creep.yaml') else 'creep.yaml'
config = yaml.load(open(yamlfile))
app = Flask(__name__)

conn = sleekxmpp.ClientXMPP(
    '%s/%s' % (config['xmpp']['jid'], config['xmpp']['resource']),
    config['xmpp']['password']
)

conn.register_plugin('xep_0045')

@app.route("/", methods=['POST',])
def index():
    if 'secret' in config['http']:
        if 'Creep-Authentication' in request.headers:
            provided_secret = decodestring(request.headers['Creep-Authentication']).rstrip()
            if isinstance(config['http']['secret'], list):
                if not provided_secret in config['http']['secret']:
                    return make_response("forbidden", 403)
            elif provided_secret != config['http']['secret']:
                return make_response("forbidden", 403)
        else:
            return make_response("forbidden", 403)

    if request.content_type == 'application/json':
        msg = request.json['message']
        room = request.json['room']
    else:
        msg = request.data
        room = config['xmpp']['default_room']
    conn.send_message(mto=room, mbody="%s" % msg, mtype='groupchat')
    return ""

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
    print "FAK"
    body = message['body']
    if ":" in body:
        command = body.split(':')[0]
        if command in handlers:
            handler = handlers[command]
            result = handler()
            message.reply(result).send()
        else:
            reply = 'Unknown command: \n%s' % body
            message.reply(reply).send()
    else:
        reply = 'Sorry, I didn\'t understand \n%s' % body
        message.reply(reply).send()

    logging.debug('Handled request "%s"' % body)
    
conn.add_event_handler("session_start", handle_connected)
conn.add_event_handler('message', handle_message)

def handle_ctrl_c(signal, frame):
    conn.disconnect(wait=True)

signal.signal(signal.SIGINT, handle_ctrl_c)

app.run(host=config['http']['host'], port=config['http']['port'])
