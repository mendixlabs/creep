from flask import Flask, request, render_template, redirect
from ConfigParser import ConfigParser
import sleekxmpp
import logging

logging.basicConfig(level=logging.DEBUG)

config = ConfigParser()
config.read(['creep.cfg', '/usr/local/etc/creep.cfg'])
app = Flask(__name__)

if __name__ == "__main__":
    jid = config.get('xmpp', 'username')
    password = config.get('xmpp', 'password')
    to = config.get('xmpp', 'recipient')
    server = config.get('xmpp', 'server')
    host = config.get('http', 'host')
    port = int(config.get('http', 'port'))

    conn = sleekxmpp.ClientXMPP('%s/collector' % jid, password)

    @app.route("/", methods=['POST',])
    def index():
        if request.content_type == 'application/json':
            msg = request.json['message']
        else:
            msg = request.data
        conn.send_message(mto=to, mbody="%s" % msg)
        return "message sent"

    print("Connecting %s to xmppserver %s" % (jid, server))
    conn.connect((server, 5222))
    print("Connected")

    conn.process(threaded=True)
    app.run(host=host, port=port)
