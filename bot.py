from flask import Flask, request, make_response, render_template, redirect
from ConfigParser import ConfigParser
import sleekxmpp
import logging
import signal
import os
import yaml
from base64 import decodestring

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
        if request.headers['Authorization']:
            (auth_type, credentials) = request.headers['Authorization'].split(" ")
            secret = decodestring(credentials).rstrip()
            if auth_type != 'Basic':
                return make_response("basic http auth supported only", 401)
            if secret != config['http']['secret']:
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
    return "message sent\n"

logging.info("Connecting %s" % config['xmpp']['jid'])
if 'server' in config['xmpp'] and 'port' in config['xmpp']:
    conn.connect((config['xmpp']['server'], config['xmpp']['port']))
else:
    conn.connect()
logging.info("Connected")

conn.process()
def handle_connected(self):
    logging.info("Started processing")
    for room in config['xmpp'].get('autojoin',[]):
        conn.plugin['xep_0045'].joinMUC(room,
            'creep',
            wait=True)
        logging.info("Connected to chat room '%s'" % room)
    app.run(host=config['http']['host'], port=config['http']['port'])

conn.add_event_handler("session_start", handle_connected)

def handle_ctrl_c(signal, frame):
    conn.disconnect(wait=True)

signal.signal(signal.SIGINT, handle_ctrl_c)

# wait for a signal, so the main thread does not vanish (which means it would not be
# there anymore to react on ctrl-c)
signal.pause()
