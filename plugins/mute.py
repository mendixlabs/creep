from plugin import Plugin


class Mute(Plugin):

    provides = ['mute', 'unmute', 'shutup']

    def __init__(self, creep):
        self.creep = creep
        self.shutup = self.mute

    def mute(self, message=None, origin=None):
        '''Mute me in this room for a while'''
        timeout = 60
        if message is not None:
            try:
                timeout = int(message)
            except:
                pass

        if 'id' in origin._body:
            self.creep.mute(origin._body['id'], timeout=timeout)
            return "I'm going to be quiet for %s seconds now" % timeout
        else:
            return ('Sorry, could not find the '
                    'channel from which you posted this'
                    )

    def unmute(self, message=None, origin=None):
        '''Unmute me'''
        if 'id' in origin._body:
            self.creep.unmute(origin._body['id'])
            return None
        else:
            return ('Sorry, could not find the '
                    'channel from which you posted this'
                    )

    def __str__(self):
        return 'mute'
