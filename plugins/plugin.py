import os, sys, inspect
import logging
import yaml

class Plugin():
    provides = []
    pass

    def shutdown(self):
        pass

def load_plugins(names, xmpp, config):
    handlers = {}
    plugins = []
    for name in names:
        plugin = load_plugin(name, handlers, xmpp, config)
        if plugin is not None:
            plugins.append(plugin)
    return (set(plugins), handlers)

def load_plugin(name, handlers, xmpp, config):
    '''
    assumes there's only one class per plugin
    '''
    plugin = __import__('plugins.%s' % name, fromlist=['plugins',])
    plugin_instance = None
    for attribute in dir(plugin):
        item = getattr(plugin, attribute)
        if inspect.isclass(item) and issubclass(item, Plugin) and not item == Plugin:
            plugin_instance = item(xmpp, config=config)
            for handler_name in plugin_instance.provides:
                register_handler(handler_name, plugin_instance, handlers)
    return plugin_instance

def register_handler(handler_name, plugin_instance, handlers):
    if handler_name in handlers:
        raise Exception("Handler already defined for command '%s'" % p)
    if not hasattr(plugin_instance, handler_name):
        raise Exception("Plugin '%s' doesn't provide '%s'" 
                % (plugin_instance, handler_name))
    handlers[handler_name] = getattr(plugin_instance, handler_name)
    logging.info("Registered '%s' as a handler for '%s'" % 
            (plugin_instance, handler_name))

