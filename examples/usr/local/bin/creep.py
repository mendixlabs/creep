#!/usr/bin/python
import sys
import json
import yaml
import os

yamlfile = '/usr/local/etc/creep.yaml' if os.path.isfile('/usr/local/etc/creep.yaml') else 'creep.yaml'
config = yaml.load(open(yamlfile))

text = "\n".join(iter(sys.stdin.readline, ""))
body = {"message": text, "room": config['xmpp']['default_room']}

print json.dumps(body)
