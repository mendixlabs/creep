from flask import Flask, request, make_response, render_template, redirect
from base64 import decodestring
from plugin import Plugin
from threading import Thread

app = Flask(__name__)

class HttpJson(Plugin):

    def __init__(self, xmpp, config=None):
        kwargs = {'host' : config['http']['host'], 'port' : config['http']['port']}
        HttpJson.config = config
        HttpJson.xmpp = xmpp
        self.thread = Thread(target=app.run, kwargs=kwargs)
        self.thread.start()
        print "initialized http-json"

    @app.route("/", methods=['POST',])
    def index():
        if 'secret' in HttpJson.config['http']:
            if 'Creep-Authentication' in request.headers:
                provided_secret = decodestring(request.headers['Creep-Authentication']).rstrip()
                if isinstance(HttpJson.config['http']['secret'], list):
                    if not provided_secret in HttpJson.config['http']['secret']:
                        return make_response("forbidden", 403)
                elif provided_secret != HttpJson.config['http']['secret']:
                    return make_response("forbidden", 403)
            else:
                return make_response("forbidden", 403)

        if request.content_type == 'application/json':
            msg = request.json['message']
            room = request.json['room']
        else:
            msg = request.data
            room = HttpJson.config['xmpp']['default_room']
        HttpJson.xmpp.send_message(mto=room, mbody="%s" % msg, mtype='groupchat')
        return ""
