#!/bin/bash
# Never edit this file!

# priority: low to high
configs="/etc/creep.cfg /usr/local/etc/creep.cfg creep.cfg"

# override the following variables in .cfg file
url="https://creep.example.com"
secret="floep"

for i in $configs; do
    [ -f "$i" ] && config="$i"
done

# load config if found
[ -f "$config" ] && source "$config"

curl -s -S -m 2 --data @- -H "Content-Type:application/json" -H "Creep-Authentication:$secret" $url

