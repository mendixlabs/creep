from plugin import Plugin
from sleekxmpp.xmlstream import ET


class EggDrop(Plugin):

    provides = ['kick']

    def __init__(self, creep, config=None):
        creep.xmpp.registerPlugin('xep_0045')
        self.muc = creep.xmpp.plugin['xep_0045']
        self.xmpp = creep.xmpp
        if config is not None and 'admins' in config:
            self.admins = config['admins']
        else:
            self.admins = []

    def kick(self, message=None, origin=None):
        '''Kick users
        Usage: kick <nick> <reason>
        reason is optional '''
        if len(message.split()) > 1:
            (nick, reason) = message.split()
        else:
            nick = message
            reason = 'Connection reset by peer'

        (room, requester_nick) = str(origin).split('/')
        if nick not in self.muc.getRoster(room):
            return "%s is not in this room" % nick

        requester = self.muc.getJidProperty(room, str(requester_nick), 'jid')
        origin_bare = str(requester).split('/')[0]
        if origin_bare not in self.admins:
            return "You're not an admin"
 
        self._send_kick_iq(nick, reason, room)
        return "kicked %s" % nick

    def _send_kick_iq(self, nick, reason, room):
        query = ET.Element('{http://jabber.org/protocol/muc#admin}query')
        item = ET.Element('item', {'role':'none', 'nick':nick})    
        reason_element = ET.Element('reason')    
        reason_element.text = reason
        item.append(reason_element)
        iq = self.xmpp.makeIqSet(query)
        query.append(item)
        iq['to'] = room
        result = iq.send()

    def __str__(self):
        return 'eggdrop'
