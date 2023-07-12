#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
PY3 = sys.version_info.major >= 3
print("Update.py")


def upd_done():
    from os import popen, system
    cmd01 = "wget http://patbuweb.com/xcplugin/xcforever.tar -O /tmp/xcforever.tar ; tar -xvf /tmp/xcforever.tar -C /"
    cmd02 = "wget --no-check-certificate -U 'Enigma2 - xcforever Plugin' -c 'http://patbuweb.com/xcplugin/xcforever.tar' -O '/tmp/xcforever.tar'; tar -xvf /tmp/xcforever.tar -C /"
    cmd22 = 'find /usr/bin -name "wget"'
    res = popen(cmd22).read()
    if 'wget' not in res.lower():
        cmd23 = 'apt-get update && apt-get install wget'
        popen(cmd23)
    try:
        popen(cmd02)
    except:
        popen(cmd01)
    system('rm -rf /tmp/xcforever.tar')
    return

'''


# 01.09.2022
import os
import sys
from twisted.web.client import downloadPage


PY3 = sys.version_info.major >= 3
a = "/tmp/xcforever.tar"
print("Update.py")


def upd_done():
    print("In upd_done")
    if os.path.isfile("/tmp/xcforever.tar"):
        os.remove("/tmp/xcforever.tar")
        return
    xfile = 'http://patbuweb.com/xcplugin/xcforever.tar'
    if PY3:
        xfile = b"http://patbuweb.com/xcplugin/xcforever.tar"
        print("Update.py in PY3")
    import requests
    response = requests.head(xfile)
    if response.status_code == 200:
        # if PY3:
            # res = response.read().decode('utf-8')
        # else:
            # res = response.read()
    
        fdest = "/tmp/xcforever.tar"
        # print("upd_done xfile =", xfile)
        downloadPage(xfile, fdest).addCallback(upd_last)
    elif response.status_code == 404:
        print("Error 404")
    else:
        return


def upd_last(fplug):
    import time
    time.sleep(3)
    if os.path.isfile("/tmp/xcforever.tar") and os.stat("/tmp/xcforever.tar").st_size > 100:
        cmd = "tar -xvf /tmp/xcforever.tar -C /"
        print("cmd A =", cmd)
        os.system(cmd)
    return
'''