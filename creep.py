import logging
import inspect
import slack  # todo
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
        self.slack.connect  # TODO

        self.handlers = {}
        self.plugins = []
        if 'plugins' in config:
            self._load_plugins(config['plugins'], config)

    def handle_connected(self, flap):
        for room in self.config['xmpp'].get('autojoin', []):
            pass  # TODO auto join rooms

    def mute(self, room, timeout=10):  # TODO
        def unmute_room():
            self.unmute(room)

        self.muted_rooms.add(room)
        Timer(timeout, unmute_room).start()

    def unmute(self, room):  # TODO
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

    def shutdown(self):
        for plugin in self.plugins:
            plugin.shutdown()

        self.slack.disconnect(wait=True)  # TODO

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
