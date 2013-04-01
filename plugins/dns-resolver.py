import dns
from dns.resolver import NoAnswer
from dns.resolver import NXDOMAIN
from plugin import Plugin


class DNSResolver(Plugin):

    provides = ['dns']

    def __init__(self, xmpp, config=None):
        pass

    def dns(self, message=None, origin=None):
        a_records = _resolve(message)
        aaaa_records = _resolve(message, record_type='AAAA')
        if len(a_records) == 0 and len(aaaa_records) == 0:
            return 'Host not found'

        return '\n'.join(a_records + aaaa_records)

    def __str__(self):
        return 'dns-resolver'


def _resolve(hostname, record_type='A'):
    try:
        resolver = dns.resolver.Resolver()
        resolver.lifetime = 20
        answers = resolver.query(hostname, record_type)
        return ['%s resolves to %s' % (hostname, answer) for answer in answers]
    except NXDOMAIN:
        return []
    except Exception as e:
        raise Exception("Could not resolve host '%s'" % hostname)
