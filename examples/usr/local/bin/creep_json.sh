#!/bin/bash

configs="/etc/creep.cfg /usr/local/etc/creep.cfg creep.cfg"

url="https://creep.example.com"
secret="floep"

for i in $configs; do
    [ -f "$i" ] && config="$i"
done

[ -f "$config" ] && source "$config"

curl -s -S -m 2 --data @- -H "Content-Type:application/json" -H "Creep-Authentication:$secret" $url

