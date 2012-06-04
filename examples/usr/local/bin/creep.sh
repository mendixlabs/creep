#!/bin/sh
curl -s -S -m 2 --data @- -H "Content-Type:text/plain" -H "Creep-Authentication:base64string==" https://creep.example.com
