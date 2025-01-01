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
from . import _, version
from .addons import Utils
from .addons.Console import Console as xcConsole
from .addons.modul import (
	globalsxp,
	Panel_list,
)
from .addons.NewOeSk import ctrlSkin
from .xcConfig import xc_config, cfg
from .xcHelp import xc_help
from .xcMaker import xc_maker
from .xcPlaylist import xc_Playlist
from .xcPlayerUri import xc_Play
from .xcShared import skin_path, xcm3ulistEntry, xcM3UList
from .xcTask import xc_StreamTasks

from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from enigma import (
	getDesktop,
)

from Screens.MovieSelection import MovieSelection
from Screens.Screen import Screen
from Tools.Directories import (SCOPE_PLUGINS, resolveFilename)
from six import text_type

import codecs
import os
import six
import socket
import sys

plugin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('XCplugin'))

# global fixed
_session = None
globalsxp.eserv = int(cfg.services.value)
globalsxp.infoname = str(cfg.infoname.value)
globalsxp.Path_Movies = str(cfg.pthmovie.value)  # + "/"
globalsxp.Path_Movies2 = globalsxp.Path_Movies
globalsxp.piclogo = os.path.join(plugin_path, 'skin/fhd/iptvlogo.jpg'),
globalsxp.pictmp = "/tmp/poster.jpg"
enigma_path = '/etc/enigma2/'
epgimport_path = '/etc/epgimport/'
iconpic = os.path.join(plugin_path, 'plugin.png')
input_file = '/tmp/mydata.json'
iptvsh = "/etc/enigma2/iptv.sh"
ntimeout = float(cfg.timeout.value)
output_file = '/tmp/mydata2.json'
Path_Picons = str(cfg.pthpicon.value) + "/"
Path_XML = str(cfg.pthxmlfile.value) + "/"
xc_list = "/tmp/xc.txt"
socket.setdefaulttimeout(5)
screenwidth = getDesktop(0).size()


if six.PY3:
	unicode = text_type


def check_configuring(session):
	from .plugin import xc_Main
	if cfg.autobouquetupdate.value is True:
		if globalsxp.autoStartTimer is not None:
			globalsxp.autoStartTimer.update()
	session.open(xc_Main)


class xc_home(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		global _session
		_session = session
		skin = os.path.join(skin_path, 'xc_home.xml')
		with codecs.open(skin, "r", encoding="utf-8") as f:
			skin = f.read()
		self.skin = ctrlSkin('xc_home', skin)
		try:
			Screen.setTitle(self, _('%s') % 'MAIN MENU')
		except:
			try:
				self.setTitle(_('%s') % 'MAIN MENU')
			except:
				pass
		self.list = []
		self["Text"] = Label("")
		self["version"] = Label(version)
		self['menu'] = xcM3UList([])
		self["key_red"] = Label(_("Exit"))
		self["key_green"] = Label(_("Select"))
		self["key_yellow"] = Label(_("Movie"))
		self["key_blue"] = Label(_("Loader M3U"))
		self["actions"] = HelpableActionMap(self, "XCpluginActions", {
			"ok": self.button_ok,
			"home": self.exitY,
			"cancel": self.exitY,
			"back": self.exitY,
			"green": self.Team,
			"yellow": self.taskManager,
			"blue": self.xcPlay,
			"red": self.exitY,
			"help": self.xc_Help,
			"menu": self.config,
			"movielist": self.taskManager,
			"2": self.showMovies,
			"pvr": self.showMovies,
			"showMediaPlayer": self.showMovies,
			"info": self.xc_Help}, -1)
		self.onFirstExecBegin.append(self.check_dependencies)
		self.onLayoutFinish.append(self.updateMenuList)

	def check_dependencies(self):
		dependencies = True
		try:
			pythonFull = float(str(sys.version_info.major) + "." + str(sys.version_info.minor))
			if pythonFull < 3.9:
				print("*** checking python version ***", pythonFull)
		except Exception as e:
			print("**** missing dependencies ***", e)
			dependencies = False

		if dependencies is False:
			os.chmod(os.path.join(plugin_path, 'dependencies.sh', 0o0755))
			cmd1 = ". /usr/lib/enigma2/python/Plugins/Extensions/XCplugin/dependencies.sh"
			self.session.openWithCallback(self.xcClean, xcConsole, title="Checking Dependencies", cmdlist=[cmd1], closeOnSuccess=True)
		else:
			self.xcClean()

	def xcClean(self):
		Utils.OnclearMem()

	def config(self):
		self.session.openWithCallback(self.loadlist, xc_config)

	def button_ok(self):
		self.keyNumberGlobalCB(self['menu'].getSelectedIndex())

	def exitY(self):
		Utils.ReloadBouquets()
		self.close()

	def Team(self):
		# self.session.open(xc_Playlist)
		self.session.openWithCallback(self.loadlist, xc_Playlist)

	def xc_Help(self):
		self.session.openWithCallback(self.xcClean, xc_help)

	def taskManager(self):
		self.session.openWithCallback(self.xcClean, xc_StreamTasks)

	def xcPlay(self):
		self.session.open(xc_Play)

	def showMovies(self):
		self.session.open(MovieSelection)

	def loadlist(self):
		from Plugins.Extensions.XCplugin.plugin import iptv_streamse
		"""
		# print("-----------CONFIG START----------")
		# host = str(cfg.hostaddress.value)
		# if host and host != 'exampleserver.com':
			# self.host = host
			# self.port = str(cfg.port.value)
			# username = str(cfg.user.value)
			# if username and username != "" and 'Enter' not in username:
				# self.username = username
			# password = str(cfg.passw.value)
			# if password and password != "" and 'Enter' not in password:
				# self.password = password
			# self.xtream_e2portal_url = "http://" + self.host + ':' + self.port
		"""
		globalsxp.STREAMS = iptv_streamse()
		if "exampleserver.com" not in globalsxp.STREAMS.xtream_e2portal_url:
			globalsxp.STREAMS.read_config()
			globalsxp.STREAMS.get_list(globalsxp.STREAMS.xtream_e2portal_url)
			return True
		return False

	def xc_StartMain(self):
		if self.loadlist:
			check_configuring(_session)
		else:
			message = (_("First Select the list or enter it in Config"))
			Utils.web_info(message)

	def updateMenuList(self):
		self.menu_list = []
		for x in self.menu_list:
			del self.menu_list[0]
		list = []
		for x in Panel_list:
			list.append(xcm3ulistEntry(x))
			self.menu_list.append(x)
		self['menu'].setList(list)
		globalsxp.infoname = str(globalsxp.STREAMS.playlistname)
		if cfg.infoexp.getValue:
			if str(cfg.infoname.value) != 'myBouquet':
				globalsxp.infoname = str(cfg.infoname.value)
		self["Text"].setText(globalsxp.infoname)

	def keyNumberGlobalCB(self, idx):
		sel = self.menu_list[idx]
		if sel == ('HOME'):
			self.xc_StartMain()
		elif sel == ('PLAYLIST'):
			self.Team()
		elif sel == ('MAKER BOUQUET'):
			self.session.open(xc_maker)
		elif sel == ('DOWNLOADER'):
			self.taskManager()
		elif sel == ('M3U LOADER'):
			self.session.open(xc_Play)
		elif sel == ('CONFIG'):
			self.config()
		elif sel == ('ABOUT & HELP'):
			self.xc_Help()
