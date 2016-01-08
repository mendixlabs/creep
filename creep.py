import logging
import inspect
from slackbot.bot import Bot
from plugins import Plugin
from threading import Timer
import os

'''
TODO
 - reload plugins on-the-fly
 - README
'''


class Creep():

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.muted_rooms = set()

        self.handlers = {}
        self.plugins = []
        if 'PLUGINS' in os.environ:
            self._load_plugins(map(
                str.strip,
                os.environ['PLUGINS'].split(',')
            ))
        self.bot = Bot()
#        for k, v in self.bot._client.channels.iteritems():
#            if 'name' in v and v['name'] == 'creep':
#                self.bot._client.send_message(
#                    k, 'Creep reporting for duty!'
#                )

    def mute(self, room_id, timeout=10):
        def unmute_room():
            self.unmute(room_id)

        self.muted_rooms.add(room_id)
        Timer(timeout, unmute_room).start()

    def unmute(self, room_id):  # TODO
        if room_id in self.muted_rooms:
            self.muted_rooms.remove(room_id)
            self.bot._client.send_message(
                room_id, "I'm back baby!"
            )

    def run(self):
        self.bot.run()

    def handle_message(self, message):
        body = message.body['text']
        command = body.split(' ')[0] if ' ' in body else body
        params = body[body.find(" ")+1:] if ' ' in body else None
        if command in self.handlers:
            handler = self.handlers[command]
            try:
                try:
                    chan = message.channel
                except KeyError:
                    chan = None
                result = handler(message=params, origin=chan)
                message.reply(result)
            except Exception:
                logging.exception("Couldn't handle command '%s': " % command)
                message.reply("Sorry, I got into trouble")
        else:
            message.reply(
                "Unknown command: '%s'. "
                'Run "help" for more info on available commands.' % body
            )

    def shutdown(self):
        for plugin in self.plugins:
            plugin.shutdown()

    def _load_plugins(self, names):
        for name in names:
            try:
                self._load_plugin(name)
            except Exception:
                logging.exception("Couldn't load plugin '%s':" % name)

    def _load_plugin(self, name):
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
                plugin_instance = item(self)
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
