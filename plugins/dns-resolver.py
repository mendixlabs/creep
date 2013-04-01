import sys
import re
from dns import resolver
from dns.resolver import NoAnswer
from plugin import Plugin

host_regex = ("^(([a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*"
              "([A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$")


class DNSResolver(Plugin):

    provides = ['dns']

    def __init__(self, xmpp, config=None):
        pass

    def dns(self, message=None, origin=None):
        if re.match(host_regex, message) is None:
            return "'%s' doesn't seem to be a valid host" % message
        a_records = _resolve(message)
        aaaa_records = _resolve(message, record_type='AAAA')
        if len(a_records) == 0 and len(aaaa_records) == 0:
            return 'Host not found'

        return '\n'.join(a_records + aaaa_records)

    def __str__(self):
        return 'dns-resolver'


def _resolve(hostname, record_type='A'):
    try:
        resolver_instance = resolver.Resolver()
        print dir(resolver_instance)
        resolver_instance.lifetime = 20
        answers = resolver_instance.query(hostname, record_type)
        return ['%s resolves to %s' % (hostname, answer) for answer in answers]
    except NoAnswer:
        return []
    except Exception as e:
        trace = sys.exc_info()[2]
        raise Exception("Could not resolve host '%s'" % hostname), None, trace
