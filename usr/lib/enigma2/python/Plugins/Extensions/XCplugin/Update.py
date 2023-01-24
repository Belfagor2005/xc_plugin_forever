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
