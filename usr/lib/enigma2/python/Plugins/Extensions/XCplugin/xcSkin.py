#!/usr/bin/python
# -*- coding: utf-8 -*-

# ======================================================================
# XCForever Plugin
#
# Original code by Dave Sully, Doug Mackay\
# rewritten by Lululla
#
#***************************************
#        coded by Lululla              *
#             skin by MMark            *
#  update     29/12/2024               *
#       Skin by MMark                  *
#***************************************
# ATTENTION PLEASE...
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2, or (at your option) any later
# version.
# You must not remove the credits at
# all and you must make the modified
# code open to everyone. by Lululla
# ======================================================================

from __future__ import print_function
from . import plugin_path
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
import os

global skin_path


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


MENU_ITEMS = [
	"home",
	"playlist",
	"maker bouquet",
	"downloader",
	"m3u loader",
	"config",
	"about & help",
]


def xcm3ulistEntry(name):
	if 'active' in name.lower() or name.lower() in [item.lower() for item in MENU_ITEMS]:
		png0 = os.path.join(plugin_path, 'skin/pic/xcon.png')
		if screenwidth.width() == 2560:
			png0 = os.path.join(plugin_path, 'skin/pic/xcselh.png')
	else:
		png0 = os.path.join(plugin_path, 'skin/pic/xcoff.png')
		if screenwidth.width() == 2560:
			png0 = os.path.join(plugin_path, 'skin/pic/xc1.png')
	res = [name]
	white = 16777215
	if screenwidth.width() == 2560:
		icon0_pos = (5, 4)
		icon0_size = (86, 54)
		text_pos = (140, 0)
		text_size = (1800, 60)
		font_size = 0
	elif screenwidth.width() == 1920:
		icon0_pos = (5, 5)
		icon0_size = (64, 40)
		text_pos = (80, 0)
		text_size = (1000, 50)
		font_size = 0
	else:
		icon0_pos = (5, 5)
		icon0_size = (66, 40)
		text_pos = (80, 0)
		text_size = (500, 50)
		font_size = 0
	res.append(MultiContentEntryPixmapAlphaTest(pos=icon0_pos, size=icon0_size, png=loadPNG(png0)))
	res.append(MultiContentEntryText(pos=text_pos, size=text_size, font=font_size, text=name, color=white, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
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

# ===================Time is what we want most, but what we use worst===================
#
# Time is the best author. It always writes the perfect ending (Charlie Chaplin)
#
# by Lululla & MMark -thanks my friend PCD and aime_jeux and other friends
# thank's to Linux-Sat-support forum - MasterG
# thanks again to KiddaC for all the tricks we exchanged, and not just the tricks ;)
# -------------------------------------------------------------------------------------
# ===================Skin by Mmark Edition for Xc Plugin Infinity please don't copy o remove this
# send credits to autor Lululla  ;)
