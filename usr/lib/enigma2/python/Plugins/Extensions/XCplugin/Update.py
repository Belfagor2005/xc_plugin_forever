#!/usr/bin/python
# -*- coding: utf-8 -*-

# 01.09.2022
import os
import sys
from twisted.web.client import downloadPage

PY3 = sys.version_info.major >= 3
a = "/tmp/xcforever.tar"
print("Update.py")


def upd_done():
    print("In upd_done")
    if os.path.isfile(a):
        os.remove(a)
        return
    xfile = 'http://patbuweb.com/xcplugin/xcforever.tar'
    if PY3:
        xfile = b"http://patbuweb.com/xcplugin/xcforever.tar"
        print("Update.py not in PY3")
    import requests
    response = requests.head(xfile)
    if response.status_code == 200:
        fdest = a
        print("upd_done xfile =", xfile)
        downloadPage(xfile, fdest).addCallback(upd_last)
    elif response.status_code == 404:
        print("Error 404")
    else:
        return


def upd_last(fplug):
    import time
    time.sleep(5)
    if os.path.isfile(a) and os.stat(a).st_size > 1000:
        cmd = "tar -xvf /tmp/xcforever.tar -C /"
        print("cmd A =", cmd)
        os.system(cmd)
    return
