from threading import Thread
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import cgi
from base64 import decodestring
from plugin import Plugin
import json
import os


class HttpJson(Plugin):

    def __init__(self, creep):
        self.port = (int(os.environ['PORT']))
        self.default_room = 'creep'
        self.creep = creep
        server_address = ('', self.port)
        secret = os.environ.get('HTTP_SECRET')
        if secret is not None:
            print('Enabled http listener with secret authentication')

        def get_handler(request, client_address, httpserver):
            return Handler(request, client_address, httpserver, secret=secret,
                           creep_plugin=self)

        self.httpd = HTTPServer(server_address, get_handler)

        self.thread = Thread(target=self._run)
        self.thread.start()

    def _run(self):
        self.keep_running = True
        while self.keep_running:
            self.httpd.handle_request()

    def shutdown(self):
        self.keep_running = False

    def broadcast_message(self, content, content_type):
        if content_type == 'application/json':
            json_request = json.loads(content)
            msg = json_request['message']
            room = json_request['room']
        else:
            msg = content
            room = self.default_room
        if '@' in room:
            room = room.split('@')[0]
        room_id = None
        channels = self.creep.bot._client.channels
        for slack_room_id, room_details in channels.iteritems():
            if 'name' in room_details and room_details['name'] == room:
                room_id = slack_room_id

        if room_id and room_id not in self.creep.muted_rooms:
            self.creep.bot._client.send_message(room_id, msg)

    def __str__(self):
        return 'http-json'


class Handler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, httpserver, secret,
                 creep_plugin):
        self.secret = secret
        self.creep_plugin = creep_plugin
        BaseHTTPRequestHandler.__init__(self, request, client_address,
                                        httpserver)

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

        authenticated = False
        if self.secret:
            if 'Creep-Authentication' in self.headers:
                auth_token = self.headers['Creep-Authentication']
                provided_secret = decodestring(auth_token).rstrip()

                if isinstance(self.secret, list):
                    authenticated = provided_secret in self.secret
                elif provided_secret == self.secret:
                    authenticated = True

        if authenticated:
            length = int(self.headers['content-length'])
            request_content = self.rfile.read(length)

            self.creep_plugin.broadcast_message(request_content, ctype)

            self.send_response(200)
            self.end_headers()
            self.wfile.close()
        else:
            self.return_forbidden()

    def return_forbidden(self):
        self.send_response(403)
        self.end_headers()
        self.wfile.write('forbidden')
        self.wfile.close()
