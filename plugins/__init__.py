import os, sys, inspect
import logging
from plugin import Plugin
logging.basicConfig(level=logging.INFO)

handlers = {}
activated_plugins = ['quotes',]
for activated_plugin in activated_plugins:
    plugin = __import__('plugins.%s' % activated_plugin, fromlist=['plugins',])
    for i in dir(plugin):
        item = getattr(plugin, i)
        if inspect.isclass(item) and issubclass(item, Plugin) and not item == Plugin:
            plugin_instance = item()
            for p in plugin_instance.provides:
                if p in handlers:
                    raise Exception("Handler already defined for command '%s'" % p)
                if not hasattr(plugin_instance, p):
                    raise Exception("Plugin '%s' doesn't provide '%s'" 
                            % (plugin_instance, p))
                handlers[p] = getattr(plugin_instance, p)
                logging.info("registered '%s' as a handler for '%s'" % 
                        (plugin_instance, p))
