from plugin import Plugin

class Help(Plugin):

    provides = ['help']

    def __init__(self, creep, config=None):
        self.creep = creep

    def help(self, message=None, origin=None):
        '''
        Returns help on creep & plugin usage
        example: "help aq"
        '''
        if message is None:
            return self._get_available_commands()
        else:
            return self._get_command_doc(message)

    def _get_available_commands(self):
        return ("Welcome to creep! Type 'help cmd' for more info\n"
                "Available commands: [%s] " % 
                ', '.join(self.creep.handlers.keys()))

    def _get_command_doc(self, name):
        if name not in self.creep.handlers:
            return "I don't know that command"
        else:
            handler = self.creep.handlers[name]
            return handler.__doc__

    def __str__(self):
        return 'help'
