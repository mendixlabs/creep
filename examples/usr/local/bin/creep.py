#!/usr/bin/python
import sys
import json

text = "\n".join(iter(sys.stdin.readline, ""))
body = {"message": text, "room": "room@conference.example.com"}

print json.dumps(body)
