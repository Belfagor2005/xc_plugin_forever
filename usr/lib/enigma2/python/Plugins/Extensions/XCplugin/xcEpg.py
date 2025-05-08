#!/usr/bin/python
# -*- coding: utf-8 -*-

# ======================================================================
# XCForever Plugin
#
# Original code by Dave Sully, Doug Mackay
# Rewritten by Lululla
# Skin by MMark
#
# ***************************************
#        Coded by Lululla              *
#             Skin by MMark            *
#  Latest Update: 08/05/2025           *
#       Skin by MMark                  *
# ***************************************
# ATTENTION PLEASE...
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2, or (at your option) any later
# version.
#
# You must not remove the credits at all and you must make the modified
# code open to everyone. by Lululla
# ======================================================================

from __future__ import print_function

# Built-in imports
import codecs
from os.path import exists, exists as file_exists, join
from re import sub

# Enigma2 imports
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from Screens.Screen import Screen
from Tools.Directories import SCOPE_PLUGINS, resolveFilename

# Local imports
from . import _
from .addons import Utils, html_conv
from .addons.NewOeSk import ctrlSkin
from .addons.modul import copy_poster, globalsxp
from .xcSkin import skin_path

global _session


class xc_Epg(Screen):
	def __init__(self, session, text_clear, png=None):
		Screen.__init__(self, session)
		global _session
		_session = session

		skin = join(skin_path, 'xc_epg.xml')
		with codecs.open(skin, "r", encoding="utf-8") as f:
			skin = f.read()
		self.skin = ctrlSkin('xc_Epg', skin)
		try:
			Screen.setTitle(self, _('%s') % 'EPG MENU')
		except:
			try:
				self.setTitle(_('%s') % 'EPG MENU')
			except:
				pass

		if png is not None:
			self.pngx = png
		else:
			self.pngx = '/tmp/poster.jpg'

		self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {
			"red": self.closex,
			"cancel": self.closex,
			"ok": self.closex}, -1)
		text = text_clear
		self["poster"] = Pixmap()
		self["key_red"] = Label(_("Back"))
		self["text_clear"] = StaticText()
		self["text_clear"].setText(text)
		self.onLayoutFinish.append(self.setCoverArt)

	def setCoverArt(self, pixmap=None):
		if not self.pngx or not file_exists(self.pngx):
			self.pngx = '/tmp/poster.jpg'
		self["poster"].instance.setPixmapFromFile(self.pngx)

	def closex(self):
		copy_poster()
		self.close()


def returnIMDB(text_clear, session):
	TMDB = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('TMDB'))
	tmdbx = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('tmdb'))
	IMDb = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('IMDb'))
	text = html_conv.html_unescape(text_clear)
	if exists(TMDB):
		try:
			from Plugins.Extensions.TMBD.plugin import TMBD
			print("[XCF] TMDB")
			session.open(TMBD.tmdbScreen, text, 0)
		except Exception as e:
			print("[XCF] TMDB: ", str(e))
		return True

		try:
			from Plugins.Extensions.TMBD.plugin import TMBD
			print("[XCF] tmdb")
			session.open(TMBD, text, 0)
		except Exception as e:
			print("[XCF] tmdb: ", str(e))
		return True

	if exists(tmdbx):
		try:
			from Plugins.Extensions.tmdb.plugin import tmdb
			session.open(tmdb.tmdbScreen, text, 0)
		except Exception as e:
			print("[XCF] Tmdb: ", str(e))
		return True

	if exists(IMDb):
		try:
			from Plugins.Extensions.IMDb.plugin import main as imdb
			imdb(session, text)
		except Exception as e:
			print("[XCF] imdb: ", str(e))
		return True

	return False


def show_more_infos(name, index, session):
	text_clear = sub(r'\b\d{4}\b.*', '', name).strip()  # name
	if "exampleserver.com" not in globalsxp.STREAMS.xtream_e2portal_url:
		selected_channel = globalsxp.iptv_list_tmp[index]
		if selected_channel:
			if globalsxp.stream_live is True:
				text_clear = selected_channel[9]

		if returnIMDB(text_clear, session):
			print('show imdb/tmdb')
		else:
			text2 = selected_channel[2]
			text3 = selected_channel[8]
			text4 = selected_channel[9]
			pixim = selected_channel[7]
			text_clear += (str(text2) + '\n\n' + str(text3) + '\n\n' + str(text4))
			session.open(xc_Epg, text_clear, pixim)
	else:
		message = (_("Please enter correct server parameters in Config\nNo valid list!"))
		Utils.web_info(message)

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
