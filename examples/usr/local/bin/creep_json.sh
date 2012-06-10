#!/bin/bash
if [ -f "/usr/local/etc/creep.cfg" ]
then
    source /usr/local/etc/creep.cfg
    curl -s -S -m 2 --data @- -H "Content-Type:application/json" -H "Creep-Authentication:$secret" https://creep.example.com
elif [ -f "creep.cfg" ]
then
    source creep.cfg
    curl -s -S -m 2 --data @- -H "Content-Type:application/json" -H "Creep-Authentication:$secret" https://creep.example.com
else
    curl -s -S -m 2 --data @- -H "Content-Type:application/json"  https://creep.example.com
fi

