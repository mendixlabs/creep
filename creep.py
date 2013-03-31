import sleekxmpp
import logging
from plugins import load_plugins 

class Creep():

    def __init__(self, config):
        logging.basicConfig(level=logging.INFO)
        self.config = config
        self.xmpp = sleekxmpp.ClientXMPP(
            '%s/%s' % (config['xmpp']['jid'], config['xmpp']['resource']),
            config['xmpp']['password']
        )

        self.xmpp.register_plugin('xep_0045')

        logging.info("Connecting %s" % config['xmpp']['jid'])
        if 'server' in config['xmpp'] and 'port' in config['xmpp']:
            self.xmpp.connect((config['xmpp']['server'], config['xmpp']['port']))
        else:
            self.xmpp.connect()
        logging.info("Connected")

        self.xmpp.process()

        self.xmpp.add_event_handler("session_start", self.handle_connected)
        self.xmpp.add_event_handler('message', self.handle_message)

        activated_plugins = ['quotes', 'http-json']
        (plugins, handlers) = load_plugins(activated_plugins, self.xmpp, config)
        self.plugins = plugins


    def handle_connected(self, flap):
        self.xmpp.send_presence()
        logging.info("Started processing")
        for room in self.config['xmpp'].get('autojoin',[]):
            self.xmpp.plugin['xep_0045'].joinMUC(room,
                'creep',
                wait=True)
            logging.info("Connected to chat room '%s'" % room)

    def handle_message(self, message):
        body = message['body']
        if not self.from_us(message):
            if not message.get_mucroom():
                reply = __handle_message(body, message.get_from())
                message.reply(reply).send()
            elif message.get_mucroom() and body.startswith('!'):
                reply = __handle_message(body[1:], message.get_from())
                message.reply(reply).send()

        logging.debug('Handled request "%s"' % body)
        
    def __handle_message(self, body, origin):
        command = body.split(' ')[0] if ' ' in body else body
        params = body[body.find(" ")+1:] if ' ' in body else None
        if command in handlers:
            handler = handlers[command]
            result = handler(message=params, origin=origin)
            return result
        else:
            return 'Unknown command: \n%s' % body

    def from_us(self,message):
        if message.get_mucroom():
            message_from = str(message.get_from())
            if '/' in message_from:
                (location, resource) = message_from.split('/')
                return (resource == self.xmpp.plugin['xep_0045'].ourNicks[location])
        return False


    def shutdown(self):
        for plugin in self.plugins:
            plugin.shutdown()

        self.xmpp.disconnect(wait=True)
