from flask import Flask, request, render_template, redirect
from ConfigParser import ConfigParser
import sleekxmpp
import logging

logging.basicConfig(level=logging.INFO)

config = ConfigParser()
config.read(['creep.cfg', '/usr/local/etc/creep.cfg'])
app = Flask(__name__)

jid = config.get('xmpp', 'username')
password = config.get('xmpp', 'password')
room = config.get('xmpp', 'room')
server = config.get('xmpp', 'server')
resource = config.get('xmpp', 'resource')
host = config.get('http', 'host')
port = int(config.get('http', 'port'))

conn = sleekxmpp.ClientXMPP('%s/%s' % (jid, resource), password)
conn.register_plugin('xep_0045')

@app.route("/", methods=['POST',])
def index():
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
