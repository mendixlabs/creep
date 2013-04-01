from plugin import Plugin

class Hello(Plugin):

    provides = ['hello', 'hi']

    def __init__(self, creep, config=None):
        pass

    def hello(self, message=None, origin=None):
        '''
        Hello world
        '''
        return self._greet('Hello', origin)
        
    def hi(self, message=None, origin=None):
        '''
        Hi world
        '''
        return self._greet('Hi', origin)

    def _greet(self, greeting, origin=None):
        if origin is not None and '@' in str(origin):
            jid = str(origin)[:str(origin).find('@')]
            if '.' in jid:
                name = jid[:jid.find('.')]
            else:
                name = jid

            return ("%s %s, I'm creep. "
                    "I like to sing and enjoy long walks on the beach"
                    "If you want to know more about me, just say 'help'"
                    % (greeting, name))

        return ("%s there! I'm creep. "
                "I like to sing and enjoy long walks on the beach" 
                "If you want to know more about me, just say 'help'" % greeting)
                

    def __str__(self):
        return 'hello'

