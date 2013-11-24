from plugin import Plugin


class Mute(Plugin):

    provides = ['mute', 'unmute', 'shutup']

    def __init__(self, creep, config=None):
        self.creep = creep
        self.shutup = self.mute

    def mute(self, message=None, origin=None):
        '''Mute me in this room for a while'''
        timeout = 60
        if message != None:
            try:
                timeout = int(message)
            except:
                pass

        room, _ = str(origin).split('/')
        self.creep.mute(room, timeout=timeout)
        return "I'm going to be quiet for %s seconds now" % timeout

    def unmute(self, message=None, origin=None):
        '''Unmute me'''
        room, _ = str(origin).split('/')
        self.creep.unmute(room)
        return None

    def __str__(self):
        return 'mute'
