from plugin import Plugin
from sleekxmpp.xmlstream import ET


class EggDrop(Plugin):

    provides = ['kick']

    def __init__(self, creep, config=None):
        creep.xmpp.registerPlugin('xep_0045')
        self.muc = creep.xmpp.plugin['xep_0045']
        self.xmpp = creep.xmpp

    def kick(self, message=None, origin=None):
        '''Kick users
        Usage: kick <nick> <reason>
        reason is optional '''
        if len(message.split()) > 1:
            (nick, reason) = message.split()
        else:
            nick = message
            reason = 'Connection reset by peer'

        room = str(origin).split('/')[0]
        if nick not in self.muc.getRoster(room):
            return "%s is not in this room" % nick

        query = ET.Element('{http://jabber.org/protocol/muc#admin}query')
        item = ET.Element('item', {'role':'none', 'nick':nick})    
        reason_element = ET.Element('reason')    
        reason_element.text = reason
        item.append(reason_element)
        iq = self.xmpp.makeIqSet(query)
        query.append(item)
        iq['to'] = room
        result = iq.send()
        return "kicked %s" % nick

    def __str__(self):
        return 'eggdrop'
