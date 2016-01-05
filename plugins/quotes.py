import sys
reload(sys)
sys.setdefaultencoding('utf8')
from plugin import Plugin
import boto3
import random
import time
import os
import json
try:
    import pylibmc
except ImportError:
    pass

'''we use boto3 s3, configuration via environment variables'''


class Quotes(Plugin):

    provides = ['aq', 'iq', 'q', 'sq', 'lq', 'dq']

    def __init__(self, creep):
        self.admins = []
        self.bucket = boto3.resource('s3').Bucket(os.environ['S3_BUCKET_NAME'])
        self.cache = {}
        try:
            credentials = json.loads(
                os.environ['VCAP_SERVICES']
            )['memcachier'][0]['credentials']
            self.memcached = pylibmc.Client(
                credentials['servers'].split(','),
                binary=True,
                username=credentials['username'],
                password=credentials['password'],
                behaviors={
                    "tcp_nodelay": True,
                    "ketama": True,
                    "no_block": True,
                }
            )
        except:
            self.memcached = None

    def _get_quote(self, identifier):
        try:
            if identifier in self.cache:
                return self.cache[identifier]
            if self.memcached is not None:
                x = self.memcached.get(identifier)
                if x:
                    self.cache[identifier] = x
                    return x
        except:
            pass
        quote = self.bucket.Object(
            str(int(identifier))
        ).get()['Body'].read()
        if self.memcached:
            self.memcached.set(identifier, quote)
        self.cache[identifier] = quote
        return quote

    def _print_quote(self, identifier):
        return '%s - %s' % (identifier, self._get_quote(identifier))

    def aq(self, message=None, origin=None):
        '''Add a quote. For example: "aq this is my quote"'''
        ID = str(int(time.time()*100))
        self.bucket.put_object(Key=ID, Body=message)
        return 'inserted quote \'%s\'' % ID

    def iq(self, message=None, origin=None):
        '''Query for a quote. For example: "iq 123"'''
        try:
            return self._print_quote(message)
        except:
            return 'quote not found or error: \'%s\'' % message

    def q(self, message=None, origin=None):
        '''Retrieve a random quote. For example: "q"'''
        key = random.choice(list(self.bucket.objects.all()))
        return self._print_quote(key.key)

    def lq(self, message=None, origin=None):
        '''List the last 10 quotes, optionally from offset'''
        quotes = sorted(
            list(self.bucket.objects.all()),
            key=lambda obj: int(obj.key)
        )
        if message is not None and len(message) > 0:
            quotes = filter(lambda q: int(q.key) < int(message), quotes)
        quotes = quotes[-10:]
        return '\n'.join(
            self._print_quote(key.key)
            for key in quotes
        )

    def sq(self, message=None, origin=None):
        '''Search for a quote. For example: "sq name"'''
        results = []
        limit = 3
        if message.startswith('unlimited '):
            message = message.replace('unlimited ', '')
            limit = 99999
        for key in self.bucket.objects.all():
            text = self._get_quote(key.key)
            if str(message).lower() in text.lower():
                results.append(self._print_quote(key.key))
        if results:
            random.shuffle(results)
            return '\n'.join(results[:limit])
        else:
            return 'no results'

    def dq(self, message=None, origin=None):
        '''Delete a quote. Only available for admins'''
        return 'not yet implemented, bug jouke plz'

    def shutdown(self):
        pass

    def __str__(self):
        return 'quotes'
