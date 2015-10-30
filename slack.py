import time
import json
import logging
import errno
from ssl import SSLError
from slackclient import SlackClient
from threading import Thread
from random import random

class Slack():

    def __init__(self, creep, config, loglevel=logging.INFO):
        logging.basicConfig(level=loglevel)
        self.creep = creep
        self.token = config["slack"]["token"]
        self.client = SlackClient(self.token)
        self.channel = None
        self.user_id = None
        self.connected = False
        self.connect(config)
            
    def shutdown(self, shutup=False):
        logging.debug("Going back to sleep, ZzzzZzzzz...")
        self.keep_running = False
        if not shutup: 
            self.send_message("Catch you on the flip side!")
    
    def start(self):
        self.keep_running = True
        self.thread = Thread(target=self._run)
        self.thread.start()
        logging.debug("Started slack service integration")
    
    def _run(self):
        while self.keep_running:
            message = self.client.rtm_read()
            if message:
                self.read_message(message)
           
    def _set_channel(self, config):
        if self.connected:
            channel_info = json.loads(self.client.api_call("channels.list"))
            channel = filter(lambda c: c["name"] == config["slack"]["channel"], channel_info["channels"])
            if channel:
                self.channel = channel[0]["id"]
                logging.debug("Channel id set to '%s'" % self.user_id)
                return True
            else:
                logging.exception("Channel '" + config["slack"]["channel"] + "' does not exists yet or you are not a member!")
        else:
            logging.info("Not connected.")
        return False
    
    def _set_user_id(self):
        if self.connected:
            user = json.loads(self.client.api_call("auth.test", token=self.token))
            if user:
                self.user_id = user["user_id"]
                logging.debug("User id set to '%s'" % self.user_id)
                return True
            else:
                logging.exception("Unable to locate user: " + config["slack"]["email"])
        else:
            logging.info("Not connected.")
        return False
    
    def connect(self, config):
        if self.client.rtm_connect():
            self.connected = True
            if self._set_channel(config) and self._set_user_id() and self.channel:
                self.client.rtm_send_message(self.channel, lines[int(random()*len(lines))])
                return True
        else:
            self.connected = False
            logging.exception("Connection Failed, invalid token: " + config["slack"]["token"])
        return False
    
    def send_message(self, message, channel=None):  
        if not channel:
            channel = self.channel
        
        sc = SlackClient(self.token)
        sc.rtm_connect()
        sc.rtm_send_message(channel, message)
        logging.debug("%s| %s" % (channel, message))
    
    def _get_user_by_id(self, user_id=None):
        result = json.loads(self.client.api_call("users.list", token=self.token))
        if 'members' in result.keys() and result["members"]:
            user = filter(lambda u: 'id' in u.keys() and u["id"] == user_id, result["members"])
            if user and user[0] and 'profile' in user[0].keys() and 'email' in user[0]["profile"].keys():
                return user[0]["profile"]["email"]
        return None
    
    def read_message(self, message):
        m = message[0]
        if set(["type", "text", "user"])<=m.keys() and m["type"]=="message" and m["user"] != self.user_id:
            if m["text"].startswith("<@" +self.user_id + ">"):
                self.send_message(self._highlight())
            elif m["channel"][0]=="D": # direct message
                channel = m["channel"]
                response = self.creep.handle_message(m["text"], self, self._get_user_by_id(m["user"]))
                self.send_message(response, channel)
        else:
            logging.debug("message ignored: %s" % message)
    
    def delete_message(self, quote_id):
        message = self._search_message(quote_id)
        if not message:
            logging.info("Could not find message %d" % quote_id)
            return False
        
        if not 'ts' in message.keys():
            logging.info("invalid message format: %s" % str(message))
            return False
        
        result = json.loads(self.client.api_call("chat.delete", token=self.token, channel=self.channel, ts=message["ts"]))
        result_status = result and 'ok' in result.keys() and result["ok"]
        logging.info("Message %d delete status: %s" % (quote_id, result_status))
    
    def _search_message(self, quote_id=None):
        response = json.loads(self.client.api_call("channels.history", token=self.token, channel=self.channel))
        if 'messages' in response.keys():
            message = filter(lambda m: 'type' in m.keys() and m["type"] == "message" and 'text' in m.keys() and m["text"].split(" ", 1)[0]==str("%d" % quote_id), response["messages"])
            if message:
                return message[0]
        return None
    
    def _highlight(self):
        return "Want to use my awesome quoting functionality? DM me!"
    
    def __str__(self):
        return 'slack'
        
lines = [
    "Back in the house!", 
    "Respect for the man with the ice cream van!",
    "It's nice to be important, but it's more important to be nice!"
]