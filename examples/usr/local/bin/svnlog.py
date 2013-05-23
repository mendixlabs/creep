#!/usr/bin/python
#
#
# Example usage in svn post-commit hook:
#
# REPOS="$1"
# REV="$2"
# /usr/local/bin/svnlog.py --repos "$REPOS" --rev "$REV"

# config
url = 'https://creep.example.com'
changeset_view_url = 'https://trac/%s/changeset/%s'
headers = {
    'Content-Type': 'application/json',
    'Creep-Authentication': 'base64something==',
}
lookcmnd = '/usr/bin/svnlook'
# end config

import socket
import sys
import getopt
import commands
import httplib2
import json

try:
    repo, rev = getopt.gnu_getopt(sys.argv[1:], "", ['repos', 'rev'])[1]
    if repo[-1] == '/':
        repo = repo[:-1]
    repname = repo.split('/')[-1]

    author = commands.getoutput('%s author %s -r %s' % (lookcmnd, repo, rev))
    msg = commands.getoutput('%s log %s -r %s' % (lookcmnd, repo, rev))
    dirs = commands.getoutput('%s dirs-changed %s -r %s'
                              % (lookcmnd, repo, rev)).split("\n")

    loc = {'room1': set(), 'room2': set()}
    # ok, let's see what we have...
    # the following code focuses on most occuring dirs in a svn commit,
    # and does not correctly handle all possible cases
    if repname == 'foo':
        for dir in dirs:
            l = dir.split('/')
            # trunk/blah/
            # (branches|tags)/blah/<ver>/
            if l[0] in ['branches', 'tags']:
                loc['room1'].add(l[2])
            elif l[0] == 'trunk':
                loc['room1'].add('trunk')
            else:
                loc['room1'].add('?')
    elif repname in ['bar']:
        for dir in dirs:
            l = dir.split('/')
            loc['room2'].add('/'.join([l[0], l[1]]))
    elif repname in ['baz']:
        for dir in dirs:
            l = dir.split('/')
            # trunk/
            # (branches|tags)/<ver>
            if l[0] in ['branches', 'tags']:
                loc['room2'].add(l[1])
            else:
                loc['room2'].add(l[0])

    for channel in loc:
        if len(loc[channel]) > 0:
            locations = ','.join(loc[channel])
            changeset_url = changeset_view_url % (repname, rev)
            text = '%s - %s/%s [%s] by %s: %s' % (changeset_url, repname,
                                                  locations, rev, author, msg)
            body = {"message": text,
                    "room": "%s@conference.example.com" % channel}
            socket.setdefaulttimeout(2)
            h = httplib2.Http()
            # fire and forget!
            h.request(url, "POST", json.dumps(body), headers=headers)

except Exception, ex:
    try:
        text = ('svnlog.py: Exception while parsing repo:%s rev:%s %s'
                % (repname, rev, ex))
        body = {"message": text, "room": "room1@conference.example.com"}
        h = httplib2.Http()
        h.request(url, "POST", json.dumps(body), headers=headers)

    except Exception, v:
        print v

# vim:sw=4:ts=4:expandtab
