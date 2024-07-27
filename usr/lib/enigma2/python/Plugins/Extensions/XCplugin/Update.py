#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os
PY3 = sys.version_info.major >= 3
print("Update.py")


def upd_done():
    from os import popen, system
    installUrl = 'https://raw.githubusercontent.com/Belfagor2005/xc_plugin_forever/main/installer.sh'
    cmd00 = 'wget -q "--no-check-certificate" ' + installUrl + ' -O - | /bin/sh'

    # cmd01 = "wget http://patbuweb.com/xcplugin/xcforever.tar -O /tmp/xcforever.tar --post-data='action=purge';tar -xvf /tmp/xcforever.tar -C /"
    # cmd02 = "wget --no-check-certificate -U 'Enigma2 - xcforever Plugin' -c 'http://patbuweb.com/xcplugin/xcforever.tar' -O '/tmp/xcforever.tar' --post-data='action=purge';tar -xvf /tmp/xcforever.tar -C /"
    # cmd22 = 'find /usr/bin -name "wget"'
    # res = popen(cmd22).read()
    # if 'wget' not in res.lower():
        # if os.path.exists('/etc/opkg'):
            # cmd23 = 'opkg update && opkg install wget'
        # else:
            # cmd23 = 'apt-get update && apt-get install wget'
        # popen(cmd23)
    # try:
        # popen(cmd02)
    # except:
        # popen(cmd01)
    popen(cmd00)
    # system('rm -rf /tmp/xcforever.tar')
    return
