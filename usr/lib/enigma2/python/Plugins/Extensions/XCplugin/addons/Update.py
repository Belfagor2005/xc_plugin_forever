#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
PY3 = sys.version_info.major >= 3
print("Update.py")


def upd_done():
    from os import popen
    installUrl = 'https://raw.githubusercontent.com/Belfagor2005/xc_plugin_forever/main/installer.sh'
    cmd00 = 'wget -q "--no-check-certificate" ' + installUrl + ' -O - | /bin/sh'
    popen(cmd00)
    return
