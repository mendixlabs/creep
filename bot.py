from flask import Flask, request, make_response, render_template, redirect
from ConfigParser import ConfigParser
import sleekxmpp
import logging
import signal
from base64 import decodestring

logging.basicConfig(level=logging.INFO)

config = ConfigParser()
config.read(['/usr/local/etc/creep.cfg', 'creep.cfg'])
app = Flask(__name__)

jid = config.get('xmpp', 'username')
password = config.get('xmpp', 'password')
room = config.get('xmpp', 'room')
server = config.get('xmpp', 'server')
resource = config.get('xmpp', 'resource')
host = config.get('http', 'host')
port = int(config.get('http', 'port'))
secret_key = config.get('http', 'secret')

conn = sleekxmpp.ClientXMPP('%s/%s' % (jid, resource), password)
conn.register_plugin('xep_0045')

@app.route("/", methods=['POST',])
def index():
    if request.headers['Authorization']:
        (auth_type, credentials) = request.headers['Authorization'].split(" ")
        secret = decodestring(credentials).rstrip()
        if auth_type != 'Basic':
            return make_response("basic http auth supported only", 401)
        if secret != secret_key:
            return make_response("forbidden", 403)
    else:
        return make_response("forbidden", 403)

    if request.content_type == 'application/json':
        msg = request.json['message']
    else:
        msg = request.data
    conn.send_message(mto=room, mbody="%s" % msg, mtype='groupchat')
    return "message sent\n"

logging.info("Connecting %s to xmppserver %s" % (jid, server))
conn.connect((server, 5222))
logging.info("Connected")

conn.process(threaded=True)
def handle_connected(self):
    logging.info("Started processing")
    conn.plugin['xep_0045'].joinMUC(room,
        'creep',
        wait=True)
    logging.info("Connected to chat room '%s'" % room)
    app.run(host=host, port=port)

conn.add_event_handler("session_start", handle_connected)

def handle_ctrl_c(signal, frame):
    conn.disconnect(wait=True)

signal.signal(signal.SIGINT, handle_ctrl_c)

# wait for a signal, so the main thread does not vanish (which means it would not be
# there anymore to react on ctrl-c)
signal.pause()
