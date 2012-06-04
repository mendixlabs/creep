#!/usr/bin/python

import sys,os

installed = set()
removed = set()

installed_libs = set()
removed_libs = set()

for line in iter(sys.stdin.readline, ""):
    # +debconf-i18n 1.5.43
    line = line.split()[0]
    # +debconf-i18n
    if line[0] == '+':
        if line[1:].startswith('lib'):
            installed_libs.add(line[1:])
        else:
            installed.add(line[1:])
    elif line[0] == '-':
        if line[1:].startswith('lib'):
            removed_libs.add(line[1:])
        else:
            removed.add(line[1:])
    else:
        print("cannot parse line: %s" % line)

output = []

changed = installed & removed
installed = installed - changed
removed = removed - changed

if installed:
    output.append("installed: [%s]" % ' '.join(installed))
if removed:
    output.append("removed: [%s]" % ' '.join(removed))
if changed:
    output.append("changed: [%s]" % ' '.join(changed))

changed_libs = installed_libs & removed_libs
installed_libs = installed_libs - changed_libs
removed_libs = removed_libs - changed_libs

output_libs = []
if installed_libs:
    output_libs.append("+%d" % len(installed_libs))
if removed_libs:
    output_libs.append("-%d" % len(removed_libs))
if changed_libs:
    output_libs.append("~%d" % len(changed_libs))
   
if output_libs:
    output.append("libs: %s" % ''.join(output_libs))

if output:
    print("apt: %s" % ', '.join(output))
