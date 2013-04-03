from threading import Thread
import urllib2
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import cgi
from base64 import decodestring
from plugin import Plugin
import json


'''
TODO
 - move config to instance variable (static bad)
'''
class HttpJson(Plugin):

    def __init__(self, creep, config=None):
        kwargs = {'host' : config['http']['host'], 'port' : config['http']['port']}
        self.host = config['http']['host']
        self.port = config['http']['port']
        HttpJson.config = config
        HttpJson.xmpp = creep.xmpp
        server_address = ('', 8000)
        self.httpd = HTTPServer(server_address, Handler)

        self.thread = Thread(target=self._run)
        self.thread.start()

    def _run(self):
        self.keep_running = True
        while self.keep_running:
            self.httpd.handle_request()

    def shutdown(self):
        self.keep_running = False
        self._fire_dummy_request()

    def _fire_dummy_request(self):
        try:
            url = 'http://%s:%s' % (self.host, self.port)
            urllib2.urlopen(url, data='bubye now', timeout=5)
        except:
            # we might already have shutdown due to other request
            pass

    def __str__(self):
        return 'http-json'


class Handler(BaseHTTPRequestHandler):

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

        if 'secret' in HttpJson.config['http']:
            if 'Creep-Authentication' in self.headers:
                provided_secret = decodestring(self.headers['Creep-Authentication']).rstrip()
                if isinstance(HttpJson.config['http']['secret'], list):
                    if not provided_secret in HttpJson.config['http']['secret']:
                        self.return_forbidden()
                        return
                elif provided_secret != HttpJson.config['http']['secret']:
                    self.return_forbidden()
                    return
            else:
                self.return_forbidden()
                return

        length = int(self.headers['content-length'])
        request_content = self.rfile.read(length)

        if ctype == 'application/json':
            json_request = json.loads(request_content)
            msg = json_request['message']
            room = json_request['room']
        else:
            msg = request_content
            room = HttpJson.config['xmpp']['default_room']

        HttpJson.xmpp.send_message(mto=room, mbody="%s" % msg, mtype='groupchat')
        self.send_response(200)
        self.end_headers()
        self.wfile.write('ok')
        self.wfile.close()

    def return_forbidden(self):
        self.send_response(403)
        self.end_headers()
        self.wfile.write('forbidden')
        self.wfile.close()

