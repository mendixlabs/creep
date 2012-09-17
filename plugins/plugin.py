import os, sys, inspect
import logging
import yaml

class Plugin():
    provides = []
    pass

def load_plugins(names, xmpp, config):
    handlers = {}
    for name in names:
        load_plugin(name, handlers, xmpp, config)
    return handlers

def load_plugin(name, handlers, xmpp, config):
    plugin = __import__('plugins.%s' % name, fromlist=['plugins',])
    for attribute in dir(plugin):
        item = getattr(plugin, attribute)
        if inspect.isclass(item) and issubclass(item, Plugin) and not item == Plugin:
            plugin_instance = item(xmpp, config=config)
            for handler_name in plugin_instance.provides:
                register_handler(handler_name, plugin_instance, handlers)

def register_handler(handler_name, plugin_instance, handlers):
    if handler_name in handlers:
        raise Exception("Handler already defined for command '%s'" % p)
    if not hasattr(plugin_instance, handler_name):
        raise Exception("Plugin '%s' doesn't provide '%s'" 
                % (plugin_instance, handler_name))
    handlers[handler_name] = getattr(plugin_instance, handler_name)
    logging.info("Registered '%s' as a handler for '%s'" % 
            (plugin_instance, handler_name))

