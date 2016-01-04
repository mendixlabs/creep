import sys
reload(sys)
sys.setdefaultencoding('utf8')
from plugin import Plugin
import boto3
import random
import time


class Quotes(Plugin):

    provides = ['aq', 'iq', 'q', 'sq', 'lq', 'dq']

    def __init__(self, creep):
        self.admins = []
        self.bucket = boto3.resource('s3').Bucket('creep-quotes')
        self.cache = {}

    def _get_quote(self, identifier):
        if identifier in self.cache:
            return self.cache[identifier]
        else:
            quote = self.bucket.Object(
                str(int(identifier))
            ).get()['Body'].read()
            self.cache[identifier] = quote
            return quote

    def _print_quote(self, identifier, text):
        return '%s - %s' % (identifier, text)

    def aq(self, message=None, origin=None):
        '''Add a quote. For example: "aq this is my quote"'''
        ID = str(int(time.time()*100))
        self.bucket.put_object(Key=ID, Body=message)
        return 'inserted quote \'%s\'' % ID

    def iq(self, message=None, origin=None):
        '''Query for a quote. For example: "iq 123"'''
        try:
            return self._print_quote(message, self._get_quote(message))
        except:
            return 'quote not found or error: \'%s\'' % message

    def q(self, message=None, origin=None):
        '''Retrieve a random quote. For example: "q"'''
        l = []
        all = list(self.bucket.objects.all())
        for _ in range(3):
            all.append(random.choice(all))
        return '\n'.join(
            self._print_quote(key.key, self._get_quote(key.key)) for key in l
        )

    def lq(self, message=None, origin=None):
        '''List the last 10 quotes, optionally from offset'''
        quotes = []
        for key in sorted(
            list(self.bucket.objects.all()),
            key=lambda obj: int(obj.key)
        )[-10:]:
            quotes.append(self._print_quote(key.key, self._get_quote(key.key)))
        return '\n'.join(quotes)

    def sq(self, message=None, origin=None):
        '''Search for a quote. For example: "sq name"'''
        results = []
        for key in self.bucket.objects.all():
            text = self._get_quote(key.key)
            if str(message).lower() in text.lower():
                results.append(self._print_quote(key.key, text))
        if results:
            return '\n'.join(results)
        else:
            return 'no results'

    def dq(self, message=None, origin=None):
        '''Delete a quote. Only available for admins'''
        return 'not yet implemented, bug jouke plz'

    def shutdown(self):
        pass

    def __str__(self):
        return 'quotes'
