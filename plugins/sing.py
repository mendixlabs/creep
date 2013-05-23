from plugin import Plugin
from random import random


class Sing(Plugin):

    provides = ['sing']

    def __init__(self, creep, config=None):
        pass

    def sing(self, message=None, origin=None):
        '''I'm a creep'''
        return lines[int(random()*len(lines))]

    def __str__(self):
        return 'sing'

lines = ["When you were here before",
         "Couldn't look you in the eye",
         "You're just like an angel",
         "Your skin makes me cry",
         "You float like a feather",
         "In a beautiful world",
         "I wish I was special",
         "You're so fucking special",
         "But I'm a creep",
         "I'm a weirdo",
         "What the hell am I doing here?",
         "I don't belong here",
         "I don't care if it hurts",
         "I want to have control",
         "I want a perfect body",
         "I want a perfect soul",
         "I want you to notice when I'm not around",
         "You're so fucking special",
         "I wish I was special",
         "But I'm a creep",
         "I'm a weirdo",
         "What the hell I'm doing here?",
         "I don't belong here",
         "She's running out the door",
         "She's running out",
         "She runs runs runs",
         "Whatever makes you happy",
         "Whatever you want",
         "You're so fucking special",
         "I wish I was special",
         "But I'm a creep",
         "I'm a weirdo",
         "What the hell am I doing here?",
         "I don't belong here",
         "I don't belong here"]
