import sleekxmpp
import logging
import inspect
from plugins import Plugin
from threading import Timer

'''
TODO
 - reload plugins on-the-fly
 - README
'''


class Creep():

    def __init__(self, config):
        logging.basicConfig(level=logging.INFO)
        self.config = config
        self.muted_rooms = set()
        self.xmpp = sleekxmpp.ClientXMPP(
            '%s/%s' % (config['xmpp']['jid'], config['xmpp']['resource']),
            config['xmpp']['password']
        )

        self.xmpp.register_plugin('xep_0045')

        logging.info("Connecting %s" % config['xmpp']['jid'])
        if 'server' in config['xmpp'] and 'port' in config['xmpp']:
            self.xmpp.connect((config['xmpp']['server'],
                               config['xmpp']['port']))
        else:
            self.xmpp.connect()
        logging.info("Connected")

        self.xmpp.process()

        self.xmpp.add_event_handler("session_start", self.handle_connected)
        self.xmpp.add_event_handler('message', self.handle_message)

        self.handlers = {}
        self.plugins = []
        if 'plugins' in config:
            self._load_plugins(config['plugins'], config)

    def handle_connected(self, flap):
        self.xmpp.send_presence()
        logging.info("Started processing")
        for room in self.config['xmpp'].get('autojoin', []):
            self.xmpp.plugin['xep_0045'].joinMUC(room,
                                                 'creep',
                                                 wait=True)
            logging.info("Connected to chat room '%s'" % room)

    def handle_message(self, message):
        body = message['body']
        if not self.from_us(message):
            if not message.get_mucroom():
                reply = self.__handle_message(body, message.get_from())
                message.reply(reply).send()
            elif message.get_mucroom() and body.startswith('!'):
                reply = self.__handle_message(body[1:], message.get_from())
                message.reply(reply).send()

        logging.debug('Handled request "%s"' % body)

    def mute(self, room, timeout=10):
        def unmute_room():
            self.unmute(room)

        self.muted_rooms.add(room)
        Timer(timeout, unmute_room).start()

    def unmute(self, room):
        if room in self.muted_rooms:
            self.muted_rooms.remove(room)
            self.xmpp.send_message(mto=room,
                                   mbody="I'm back baby!",
                                   mtype='groupchat')

    def __handle_message(self, body, origin):
        command = body.split(' ')[0] if ' ' in body else body
        params = body[body.find(" ")+1:] if ' ' in body else None
        if command in self.handlers:
            handler = self.handlers[command]
            try:
                result = handler(message=params, origin=origin)
                return result
            except Exception:
                logging.exception("Couldn't handle command '%s': " % command)
                return "Sorry, I got into trouble"
        else:
            return ("Unknown command: '%s'. "
                    'Run "help" for more info on available commands.' % body)

    def from_us(self, message):
        if message.get_mucroom():
            message_from = str(message.get_from())
            if '/' in message_from:
                (location, resource) = message_from.split('/')
                return (resource ==
                        self.xmpp.plugin['xep_0045'].ourNicks[location])
        return False

    def shutdown(self):
        for plugin in self.plugins:
            plugin.shutdown()

        self.xmpp.disconnect(wait=True)

    def _load_plugins(self, names, config):
        for name in names:
            try:
                self._load_plugin(name, config)
            except Exception:
                logging.exception("Couldn't load plugin '%s':" % name)

    def _load_plugin(self, name, config):
        '''
        assumes there's only one class per plugin
        '''
        plugin = __import__('plugins.%s' % name, fromlist=['plugins', ])
        plugin_instance = None
        for attribute in dir(plugin):
            item = getattr(plugin, attribute)
            if (inspect.isclass(item) and
                    issubclass(item, Plugin) and
                    not item == Plugin):
                plugin_instance = item(self, config=config)
                for handler_name in item.provides:
                    if handler_name in self.handlers.keys():
                        raise Exception("Can't load '%s': handler already "
                                        "registered for '%s'" % (name,
                                                                 handler_name))

                    self.handlers[handler_name] = _get_handler(handler_name,
                                                               plugin_instance)

                self.plugins.append(plugin_instance)
                logging.info("Finished loading '%s' plugin" % plugin_instance)


def _get_handler(handler_name, plugin_instance):
    if not hasattr(plugin_instance, handler_name):
        raise Exception("Plugin '%s' doesn't provide '%s'"
                        % (plugin_instance, handler_name))
    logging.info("Registered '%s' as a handler for '%s'" %
                 (plugin_instance, handler_name))
    return getattr(plugin_instance, handler_name)
