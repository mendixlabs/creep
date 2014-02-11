from threading import Thread
import urllib2
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from plugin import Plugin
import os
import cgi


class QuotesWebInterface(Plugin):

    def __init__(self, creep, config=None):
        self.host = config['http']['host']
        self.port = 13000
        self.creep = creep
        server_address = ('', self.port)

        def get_handler(request, client_address, httpserver):
            return Handler(request, client_address, httpserver,
                           creep=self.creep)

        self.httpd = HTTPServer(server_address, get_handler)

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
        return 'quotes-web'


class Handler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, httpserver,  creep):
        self.creep = creep
        BaseHTTPRequestHandler.__init__(self, request, client_address,
                                        httpserver)

    def do_POST(self):
        self.return_forbidden()

    def do_GET(self):
        mime_types = {
            '.css': 'text/css',
            '.js': 'text/javascript',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
        }
        if self.path == '/random':
            self.send_response(200)
            self.send_header("Content-type", "text")
            self.send_header('Cache-Control',
                             'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()
            for plugin in self.creep.plugins:
                if str(plugin) == 'quotes':
                    random_quote = plugin.q()
            self.wfile.write(random_quote)
        elif self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            for plugin in self.creep.plugins:
                if str(plugin) == 'quotes':
                    random_quote = plugin.q()
            self.wfile.write(
                open(
                    'src/templates/random_quote.html', 'r'
                ).read().format(text=cgi.escape(random_quote))
            )
        else:
            try:
                filename = os.path.join('src', self.path[1:])
                with open(filename, 'rb') as file_being_served:
                    self.send_response(200)
                    for ext, mime in mime_types.items():
                        if self.path.lower().endswith(ext):
                            self.send_header('Content-type', mime)
                            break
                    self.end_headers()
                    self.wfile.write(file_being_served.read())
            except IOError:
                pass

    def return_forbidden(self):
        self.send_response(403)
        self.end_headers()
        self.wfile.write('forbidden')
        self.wfile.close()
