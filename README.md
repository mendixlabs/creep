creep
=====

XMPP-based chatbot that's easy to extend. Originally inspired by <a href="https://pypi.python.org/pypi/gozerbot">gozerbot</a>. Easy & minimal plugin structure, couple of useful plugins out-of-the-box:
 - http-json: provides HTTP interface that lets you POST messages to a XMPP conference rooms
 - quotes: add & ask about quotes
 - dns-resolver: resolve domains from within the bot. Useful for situations where your bot is running behind your firewall but you want to quickly resolve a host on that local network


requirements
----
see requirements.txt
 - pyyaml
 - sleekxmpp
 - dnspython (optional, for dns plugin)

installation
----
Recommended way of installing is via virtualenv:

    virtualenv venv
    venv/bin/pip install -r requirements.txt

running
----
See example config: creep.yaml.example
At the very least, jid, password & default room configured (you can use your gmail/gchat account if you want to mess around and test)

Running:

    venv/bin/python app.py

To test you can edit & run:

    echo "test" | ./examples/usr/local/bin/creep.sh

Be sure to base64 encode your secret (if you changed it) before pasting it in examples/usr/local/bin/creep.sh
