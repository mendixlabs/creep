#!/usr/bin/python
import sys
import json

if len(sys.argv) > 1:
    room = sys.argv[1]
else:
    sys.stderr.write("Usage: echo fooo | %s room@conference.example.com" % sys.argv[0])
    exit(1)

text = "".join(iter(sys.stdin.readline, ""))
body = {"message": text, "room": room}

print json.dumps(body)
