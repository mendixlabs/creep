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
    self.channel = config["slack"]["channel"]
    self.client = SlackClient(self.token)
    self.connected = False
    self.connect(config)
    self.user_id = self.get_user_id(config)    
      
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
  
  def get_channel_id(self):
    if self.connected:
      channel_info = json.loads(self.client.api_call("channels.list"))
      channel = filter(lambda channel: channel["name"] == self.channel, channel_info["channels"])
      if channel:
        return channel[0]["id"]
      else:
        logging.exception("Channel '" + self.channel + "' does not exists yet!")
    else:
      logging.info("Not connected.")
    return None
  
  def get_user_id(self, config):
     if self.connected:
       user_list = json.loads(self.client.api_call("users.list"))
       user = filter(lambda u: u["profile"]["email"] == config["slack"]["email"], user_list["members"])
       if user:
         return user[0]["id"]
       else:
         logging.exception("Unable to locate user: " + config["slack"]["email"])
      else:
        logging.info("Not connected.")
    return None
  
  def connect(self, config):
    if self.client.rtm_connect():
      self.connected = True
      self.get_channel_id()
      self.client.rtm_send_message(self.channel, lines[int(random()*len(lines))])
    else:
      logging.exception("Connection Failed, invalid token: " + config["slack"]["token"])
      self.connected = False
    return None
  
  def send_message(self, message, channel=None):
    if self.connected:
      if not channel:
        channel = self.channel
      self.client.rtm_send_message(channel, message)
      logging.debug("%s| %s" % channel, message)
    else:  
      logging.info("Not connected")
    return None
    
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
      logging.debug("message ignored:| %s" % message)
    return None
  
  def _highlight(self):
    return "Want to use my awesome quoting functionality? DM me!"
  
  def __str__(self):
    return 'slack'
    
lines = [
  "Back in the house!", 
  "Boo!"
]