from plugin import Plugin

class Hello(Plugin):

    # replace this with decorators:
    provides = ['hello',]
    def __init__(self):
        pass

    def hello(self):
        return "Hello there!"

    def __str__(self):
        return "Simple test plugin that says hello"
