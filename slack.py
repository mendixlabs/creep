import time
import json
from slackclient import SlackClient
from threading import Thread
from random import random

class Slack():

  def __init__(self, creep, config, debug=True):
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
        raise Exception("Channel '" + self.channel + "' does not exists yet!")
    self._debug("Not connected.")
    return None
  
  def get_user_id(self, config):
    return config["slack"]["userid"]
  
  def connect(self, config):
    if self.client.rtm_connect():
      self.connected = True
      self.get_channel_id()
      self.client.rtm_send_message(self.channel, lines[int(random()*len(lines))])
    else:
      print "Connection Failed, invalid token?"
      self.connected = False
    return None
  
  def send_message(self, message, channel=None):
    if self.connected:
      if not channel:
        channel = self.channel
      self.client.rtm_send_message(channel, message)
    return None
    
  def _debug(self, message=None):
    if self.debug:
      print message
    return None
    
  def message_read(self, message):
    m = message[0]
    
    if 'type' in m.keys() and m["type"] == "message" and 'text' in m.keys() and m["text"]:
      if m["text"].startswith("<@" +self.user_id + ">"):
        self.send_message(self._highlight())
      if m["channel"][0]=="D": # direct message
        channel = m["channel"]
          
        response = self.creep.handle_message(m["text"], self)
        self.send_message(response, channel)
    return None
  
  def _highlight(self):
    return "Want to use my awesome quoting functionality? DM me!"
  
  def __str__(self):
    return 'slack'
    
lines = [
  "Back in the house!", 
  "Boo!"
]