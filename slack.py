import time
import json
import logging
from slackclient import SlackClient
from threading import Thread
from random import random

class Slack():

  def __init__(self, creep, config):
    logging.basicConfig(level=logging.INFO)
    self.debug = debug
    self.creep = creep
    self.token = config["slack"]["token"]
    self.client = SlackClient(self.token)
    
    self.channel = None
    self.user_id = None
    self.connected = False
    self.connect(config)
      
  def shutdown(self):
    self.keep_running = False
    self.send_message("Catch you on the flip side!")
  
  def start(self):  
    self.thread = Thread(target=self._run)
    self.thread.start()
    logging.debug("Started slack service integration")
  
  def _run(self):
    self.keep_running = True
    while self.keep_running:
      message = self.client.rtm_read()
      if message:
        self.message_read(message)
  
  def _set_channel(self, config):
    if self.connected:
      channel_info = json.loads(self.client.api_call("channels.list"))
      channel = filter(lambda channel: channel["name"] == config["slack"]["channel"], channel_info["channels"])
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
        self.user_id = user["user_id"])
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
      if self._set_channel(config) and self._set_user_id(config) and self.channel:
        self.client.rtm_send_message(self.channel, lines[int(random()*len(lines))])
        return True
    else:
      self.connected = False
      logging.exception("Connection Failed, invalid token: " + config["slack"]["token"])
    return False
  
  def send_message(self, message, channel=None):
    if self.connected:
      if not channel:
        channel = self.channel
      self.client.rtm_send_message(channel, message)
      logging.debug("%s| %s" % channel, message)
      return True
    else:  
      logging.info("Not connected")
    return False
    
  def message_read(self, message):
    m = message[0]
    if 'type' in m.keys() and m["type"] == "message" and 'text' in m.keys() and m["text"]:
      if m["text"].startswith("<@" +self.user_id + ">"):
        self.send_message(self._highlight())
      elif m["channel"][0]=="D": # direct message
        channel = m["channel"]
        response = self.creep.handle_message(m["text"], self)
        self.send_message(response, channel)
    else:
      logging.debug("message ignored: %s" % message)
  
  def _highlight(self):
    return "Want to use my awesome quoting functionality? DM me!"
  
  def __str__(self):
    return 'slack'
    
lines = [
  "Back in the house!", 
  "Boo!",
  "Respect for the man with the icecream van!",
  "It's nice to be important, but it's more important to be nice!"
]