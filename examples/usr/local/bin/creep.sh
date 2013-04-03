#!/bin/sh

configs="/etc/creep.cfg /usr/local/etc/creep.cfg creep.cfg"

url="http://localhost:8000"
secret="YmxhYXQK" # matches 'blaat', default secret from creep.yaml.example

for i in $configs; do
    [ -f "$i" ] && config="$i"
done

[ -f "$config" ] && source "$config"

curl -s -S -m 2 --data @- -H "Content-Type:text/plain" -H "Creep-Authentication:$secret" $url
