#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
****************************************
*        coded by Lululla              *
*             skin by MMark            *
*  update     16/12/2024               *
*       Skin by MMark                  *
****************************************
'''

from __future__ import print_function
from .addons.modul import globalsxp

from Components.MenuList import MenuList
from Components.MultiContent import (MultiContentEntryText, MultiContentEntryPixmapAlphaTest)
from enigma import (
    getDesktop,
    loadPNG,
    RT_HALIGN_LEFT,
    RT_VALIGN_CENTER,
    RT_HALIGN_CENTER,
    gFont,
    eListboxPythonMultiContent,
)
from Tools.Directories import (SCOPE_PLUGINS, resolveFilename)
import os


plugin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('XCplugin'))
globalsxp.piclogo = os.path.join(plugin_path, 'skin/fhd/iptvlogo.jpg'),
screenwidth = getDesktop(0).size()
skin_path = None
if screenwidth.width() == 2560:
    CHANNEL_NUMBER = [3, 4, 120, 60, 0]
    CHANNEL_NAME = [130, 4, 1800, 60, 1]
    FONT_0 = ("Regular", 52)
    FONT_1 = ("Regular", 52)
    BLOCK_H = 80
    skin_path = os.path.join(plugin_path, 'skin/uhd')
    globalsxp.piclogo = os.path.join(plugin_path, 'skin/uhd/iptvlogo.jpg')

elif screenwidth.width() == 1920:
    CHANNEL_NUMBER = [3, 0, 100, 50, 0]
    CHANNEL_NAME = [110, 0, 1200, 50, 1]
    FONT_0 = ("Regular", 32)
    FONT_1 = ("Regular", 32)
    BLOCK_H = 50
    skin_path = os.path.join(plugin_path, 'skin/fhd')
    globalsxp.piclogo = os.path.join(plugin_path, 'skin/fhd/iptvlogo.jpg')

else:
    CHANNEL_NUMBER = [3, 0, 50, 40, 0]
    CHANNEL_NAME = [75, 0, 900, 40, 1]
    FONT_0 = ("Regular", 24)
    FONT_1 = ("Regular", 24)
    BLOCK_H = 40
    skin_path = os.path.join(plugin_path, 'skin/hd')
    globalsxp.piclogo = os.path.join(plugin_path, 'skin/hd/iptvlogo.jpg')


def channelEntryIPTVplaylist(entry):
    menu_entry = [
        entry,
        (eListboxPythonMultiContent.TYPE_TEXT, CHANNEL_NUMBER[0], CHANNEL_NUMBER[1], CHANNEL_NUMBER[2], CHANNEL_NUMBER[3], CHANNEL_NUMBER[4], RT_HALIGN_CENTER | RT_VALIGN_CENTER, "%s" % entry[0]),
        (eListboxPythonMultiContent.TYPE_TEXT, CHANNEL_NAME[0], CHANNEL_NAME[1], CHANNEL_NAME[2], CHANNEL_NAME[3], CHANNEL_NAME[4], RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[1])]
    return menu_entry


def xcm3ulistEntry(name):
    png0 = os.path.join(plugin_path, 'skin/pic/xcselh.png')
    pngl = os.path.join(plugin_path, 'skin/pic/xcon.png')
    res = [name]
    white = 16777215

    if screenwidth.width() == 2560:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 4), size=(86, 54), png=loadPNG(png0)))
        res.append(MultiContentEntryText(pos=(140, 0), size=(1800, 60), font=0, text=name, color=white, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    elif screenwidth.width() == 1920:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(64, 40), png=loadPNG(pngl)))
        res.append(MultiContentEntryText(pos=(80, 0), size=(1000, 50), font=0, text=name, color=white, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(66, 40), png=loadPNG(pngl)))
        res.append(MultiContentEntryText(pos=(80, 0), size=(500, 50), font=0, text=name, color=white, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    return res


def m3ulistxc(data, list):
    icount = 0
    mlist = []
    for line in data:
        name = data[icount]
        mlist.append(xcm3ulistEntry(name))
        icount += 1
    list.setList(mlist)


class xcM3UList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        if screenwidth.width() == 2560:
            self.l.setItemHeight(70)
            self.l.setFont(0, gFont("Regular", 54))
        elif screenwidth.width() == 1920:
            self.l.setItemHeight(50)
            self.l.setFont(0, gFont("Regular", 32))
        else:
            self.l.setItemHeight(50)
            self.l.setFont(0, gFont("Regular", 24))
