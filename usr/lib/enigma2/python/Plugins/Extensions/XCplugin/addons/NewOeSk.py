#!/usr/bin/python
# -*- coding: utf-8 -*-

# ======================================================================
# LinuxsatPanel Plugin
# Coded by masterG - oktus - pcd
#
# rewritten by Lululla at 20240720
#
# ATTENTION PLEASE...
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2, or (at your option) any later
# version.
# You must not remove the credits at
# all and you must make the modified
# code open to everyone. by Lululla
# ======================================================================
from __future__ import absolute_import
from __future__ import print_function
from os.path import isfile

__author__ = "Lululla"
__email__ = "ekekaz@gmail.com"
__copyright__ = 'Copyright (c) 2024 Lululla'
__license__ = "GPL-v2"
__version__ = "1.0.0"


def newOE():
    '''
    coded by s3n0
    return True ---- for commercial versions of Enigma2 core (OE 2.2+) - DreamElite, DreamOS, Merlin, ... etc.
    return False --- for open-source versions of Enigma2 core (OE 2.0 or OE-Alliance 4.x) - OpenATV, OpenPLi, VTi, ... etc.
    '''
    # return os.path.exists('/etc/dpkg')
    boo = False
    try:
        from enigma import PACKAGE_VERSION
        major, minor, patch = [int(n) for n in PACKAGE_VERSION.split('.')]
        if major > 4 or (major == 4 and minor >= 2):  # if major > 4 or major == 4 and minor >= 2:
            boo = True  # new enigma core (DreamElite, DreamOS, Merlin, ...) ===== e2 core: OE 2.2+ ====================== (c)Dreambox core
    except Exception:
        pass
    try:
        from Components.SystemInfo import SystemInfo
        if 'MachineBrand' in SystemInfo.keys and 'TeamBlue' in SystemInfo['MachineBrand']:
            boo = False
    except Exception:
        pass
    try:
        from boxbranding import getOEVersion
        if getOEVersion().find('OE-Alliance') >= 0:
            boo = False
    except Exception:
        pass
    return boo


def ctrlSkin(pank, skin):
    # coded by @Lululla 20240720
    from re import sub, findall
    print('ctrlSkin panel=%s' % pank)
    # Keywords to identify when to remove "font" and "scrollbarWidth"
    scrollbar_keywords = ['list', 'text', 'menu', 'config', 'tasklist', 'menulist']  # , 'menu_list', 'filelist', 'file_list', 'entries', 'Listbox', 'list_left', 'list_right', 'streamlist', 'tablist', 'HelpScrollLabel']
    # Check if it is a Dreambox system with NewOE
    if newOE() or isfile('/etc/opkg/nn2-feed.conf') or isfile("/usr/bin/apt-get"):
        # Remove "scrollbarWidth" if present
        if 'scrollbarWidth' in skin:
            skin = sub(r'scrollbarWidth="[^"]*"', '', skin)

        # Find all widgets defined in the skin file
        widgets = findall(r'<widget[^>]*>', skin)
        for widget in widgets:
            # Search for the widget name
            widget_name_match = findall(r'name="([^"]+)"', widget)
            widget_name = widget_name_match[0] if widget_name_match else None

            # Removes font only for scrollbar_keywords key on NewOE systems
            # if widget_name == 'config':
            if widget_name and widget_name in scrollbar_keywords:
                # Remove font if present
                mod_widget = sub(r'font="[^"]*"', '', widget)
                skin = skin.replace(widget, mod_widget)
            # Change for other widgets with scrollbarMode
            else:
                for key in scrollbar_keywords:
                    if 'scrollbarMode="%s"' % key in widget:
                        mod_widget = sub(r'font="[^"]*"', '', widget)
                        skin = skin.replace(widget, mod_widget)
                        break
        # print('Skin mod:\n%s' % skin)
    else:
        print('No changes to the content of `skin.')
    return skin
