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
from . import _
from .addons import html_conv
from .addons import Utils
from .addons.modul import copy_poster, globalsxp
from .addons.NewOeSk import ctrlSkin
from .xcShared import skin_path

from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from os.path import exists as file_exists
from Screens.Screen import Screen
from Tools.Directories import (SCOPE_PLUGINS, resolveFilename)

import codecs
import os
import re

global _session


class xc_Epg(Screen):
	def __init__(self, session, text_clear, png=None):
		Screen.__init__(self, session)
		global _session
		_session = session
		skin = os.path.join(skin_path, 'xc_epg.xml')
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
	if os.path.exists(TMDB):
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

	if os.path.exists(tmdbx):
		try:
			from Plugins.Extensions.tmdb.plugin import tmdb
			session.open(tmdb.tmdbScreen, text, 0)
		except Exception as e:
			print("[XCF] Tmdb: ", str(e))
		return True

	if os.path.exists(IMDb):
		try:
			from Plugins.Extensions.IMDb.plugin import main as imdb
			imdb(session, text)
		except Exception as e:
			print("[XCF] imdb: ", str(e))
		return True

	return False


def show_more_infos(name, index, session):
	text_clear = re.sub(r'\b\d{4}\b.*', '', name).strip()  # name
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
