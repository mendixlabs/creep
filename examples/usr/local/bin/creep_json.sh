#!/bin/bash
curl -s -S -m 2 --data @- -H "Content-Type:application/json" -H "Creep-Authentication:base64string==" https://creep.example.com
