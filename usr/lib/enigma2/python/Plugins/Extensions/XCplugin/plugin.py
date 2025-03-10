#!/usr/bin/python
# -*- coding: utf-8 -*-

# ======================================================================
# XCForever Plugin
#
# Original code by Dave Sully, Doug Mackay\
# rewritten by Lululla
#
# ***************************************
#        coded by Lululla              *
#             skin by MMark            *
#  update     29/12/2024               *
#       Skin by MMark                  *
# ***************************************
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
from . import (
	_,
	b64decoder,
	version,
	make_request,
	check_port,
	plugin_path,
)
from .addons import Utils
from .addons import html_conv
from .addons.Console import Console as xcConsole
from .addons.modul import (
	globalsxp,
	Panel_list,
)
from .addons.NewOeSk import ctrlSkin
from .xcConfig import cfg, xc_config
from .xcHelp import xc_help
from .xcMain import xc_Main
from .xcMaker import xc_maker
from .xcPlaylist import xc_Playlist
from .xcPlayerUri import xc_Play, aspect_manager
from .xcShared import autostart
from .xcTask import xc_StreamTasks
from .xcSkin import skin_path, xcm3ulistEntry, xcM3UList
from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from enigma import getDesktop
from Plugins.Plugin import PluginDescriptor
from Screens.MovieSelection import MovieSelection
from Screens.Screen import Screen
from six import text_type
try:
	from xml.etree.ElementTree import fromstring, tostring
except ImportError:
	from xml.etree.cElementTree import fromstring, tostring


import codecs
import os
import re
import six
import socket
import sys


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


class xc_home(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
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
		self["key_blue"] = Label(_("M3u Loader"))
		self["actions"] = HelpableActionMap(
			self,
			"XCpluginActions",
			{
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
				"info": self.xc_Help
			},
			-1
		)
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
		self.session.openWithCallback(self.ConfigTextx, xc_config)

	def ConfigTextx(self):
		globalsxp.STREAMS.read_config()
		globalsxp.STREAMS.get_list(globalsxp.STREAMS.xtream_e2portal_url)

	def button_ok(self):
		self.keyNumberGlobalCB(self['menu'].getSelectedIndex())

	def exitY(self):
		Utils.ReloadBouquets()
		aspect_manager.restore_aspect()
		self.close()

	def Team(self):
		# self.session.openWithCallback(self.OpenList, xc_Playlist(globalsxp.STREAMS))
		self.session.openWithCallback(self.OpenList, xc_Playlist, globalsxp.STREAMS)

	def xc_Help(self):
		self.session.openWithCallback(self.xcClean, xc_help)

	def taskManager(self):
		self.session.openWithCallback(self.xcClean, xc_StreamTasks)

	def xcPlay(self):
		self.session.open(xc_Play)

	def showMovies(self):
		self.session.open(MovieSelection)

	def OpenList(self, callback=None):
		globalsxp.STREAMS = iptv_streamse()
		globalsxp.STREAMS.read_config()
		if "exampleserver" not in globalsxp.STREAMS.xtream_e2portal_url:
			globalsxp.STREAMS.get_list(globalsxp.STREAMS.xtream_e2portal_url)
			self.session.openWithCallback(check_configuring, xc_Main)
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
			self.OpenList()
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


class iptv_streamse():
	def __init__(self):
		self.plugin_version = ""
		self.playlistname = ""
		self.playlistname_tmp = ""
		self.next_page_url = ""
		self.next_page_text = ""
		self.prev_page_url = ""
		self.prev_page_text = ""
		self.trial = ""
		self.iptv_list = []
		self.iptv_list_tmp = []
		self.list_index_tmp = 0
		self.list_index = 0
		self.ar_id_player = 0
		self.video_status = False
		self.img_loader = False
		self.cont_play = False
		self.host = str(cfg.hostaddress.value)
		self.port = str(cfg.port.value)
		self.username = str(cfg.user.value)
		self.password = str(cfg.passw.value)
		self.xtream_e2portal_url = "http://" + self.host + ':' + self.port

	def MoviesFolde(self):
		return globalsxp.Path_Movies

	def getValue(self, definitions, default):
		Len = len(definitions)
		return Len > 0 and definitions[Len - 1].text or default

	def read_config(self):
		try:
			print("\n-----------CONFIG START----------")
			host = str(cfg.hostaddress.value)
			self.port = str(cfg.port.value)
			username = str(cfg.user.value)
			password = str(cfg.passw.value)
			if host and host != 'exampleserver.com':
				self.host = host
			if username and username != "" and 'Enter' not in username:
				self.username = username
			if password and password != "" and 'Enter' not in password:
				self.password = password
			self.xtream_e2portal_url = "http://" + self.host + ':' + self.port

			print('Host: %s\nUsername: %s\nPassword:%s' % (self.xtream_e2portal_url, self.username, self.password))
			print("-----------CONFIG END----------\n")
			return self.username, self.password
		except Exception as e:
			print("++++++++++ERROR READ CONFIG+++++++++++++ ", e)
			return None, None

	def get_list(self, url=None):
		globalsxp.stream_live = False
		self.url = check_port(url)
		self.list_index = 0
		globalsxp.iptv_list_tmp = []
		root = None
		globalsxp.btnsearch = 0
		globalsxp.next_request = 0
		globalsxp.isStream = False
		name = ''
		description = ''
		category_id = ''
		playlist_url = None
		desc_image = ''
		globalsxp.stream_url = ''
		piconname = ''
		nameepg = ''
		description2 = ''
		description3 = ''
		chan_counter = 0
		try:
			# print("!!!!!!!!-------------------- URL %s" % self.url)
			if '&type' in self.url:
				globalsxp.next_request = 1
			elif "_get" in self.url:
				globalsxp.next_request = 2  # don't use it

			root = self._request(self.url)

			if root:
				self.playlistname = ""
				self.category_title = ""
				self.category_id = ""
				self.next_page_url = ""
				self.next_page_text = ""
				self.prev_page_url = ""
				self.prev_page_text = ""
				self.prev_page_text_element = ""
				self.next_page_text_element = ""

				playlistname_exists = root.findtext('playlist_name')
				if playlistname_exists:
					self.playlistname = playlistname_exists
					globalsxp.infoname = str(self.playlistname)

				next_page_url = root.find("next_page_url")
				if next_page_url is not None:
					self.next_page_url = next_page_url.attrib.get("text")

				prev_page_url = root.find("prev_page_url")
				if prev_page_url is not None:
					self.prev_page_url = prev_page_url.attrib.get("text")

				for channel in root.findall('.//channel'):
					chan_counter += 1

					# Category name
					title_element = channel.find('title')
					if title_element is not None and title_element.text is not None:
						name = b64decoder(title_element.text)  # Passiamo il testo decodificato
						# print('channels: Title:', type(name), name)

						name = html_conv.html_unescape(name)

					# Category description
					description_element = channel.find('description')
					if description_element is not None and description_element.text is not None:
						description = b64decoder(description_element.text)  # Passiamo il testo decodificato
						# print('channels: Description:', type(description), description)

					# Category desc_image
					desc_image_id_element = channel.find('desc_image')
					if desc_image_id_element is not None and desc_image_id_element.text is not None:
						desc_image = desc_image_id_element.text.strip()
						if desc_image != "n/A" and desc_image != "":
							if desc_image.startswith("https"):
								desc_image = desc_image.replace("https", "http")
							# print('channels:desc_image:', type(desc_image), desc_image)

					# Category ID
					category_id_element = channel.find('category_id')
					if category_id_element is not None and category_id_element.text is not None:
						category_id = category_id_element.text.strip()
						# print('channels: Category ID:', type(category_id), category_id)

					# Category stream_url list channel
					stream_url_id_element = channel.find('stream_url')
					if stream_url_id_element is not None and stream_url_id_element.text is not None:
						globalsxp.stream_url = stream_url_id_element.text.strip()
					else:
						print('channels: Stream URL not found or is empty.')

					# Playlist URL
					playlist_url_element = channel.find('playlist_url')
					if playlist_url_element is not None and playlist_url_element.text is not None:
						playlist_url = playlist_url_element.text

					# Category piconname
					piconname_id_element = channel.find('logo')
					if piconname_id_element is not None and piconname_id_element.text is not None:
						piconname = piconname_id_element.text
					if globalsxp.stream_url:
						globalsxp.isStream = True
					else:
						globalsxp.isStream = False

					if "/live/" in globalsxp.stream_url:
						globalsxp.stream_live = True
						epgnowtime = ''
						epgnowdescription = ''
						epgnexttitle = ''
						epgnexttime = ''
						epgnextdescription = ''

						if description != '':
							# Trova orari [hh:mm]
							timematch = re.findall(r'\[(\d{2}:\d{2})\]', description)

							# Trova titoli dopo gli orari
							titlematch = re.findall(r'\[\d{2}:\d{2}\]\s*(.*?)\n', description)

							# Trova descrizioni tra parentesi tonde multilinea
							descriptionmatch = re.findall(r'\((.*?)\)', description, re.DOTALL)

							# Ora attuale ed episodio successivo
							epgnowtime = timematch[0].strip() if len(timematch) > 0 else ''
							epgnexttime = timematch[1].strip() if len(timematch) > 1 else ''

							# Titoli
							nameepg = titlematch[0].strip() if len(titlematch) > 0 else ''
							epgnexttitle = titlematch[1].strip() if len(titlematch) > 1 else ''

							# Descrizioni
							epgnowdescription = descriptionmatch[0].strip() if len(descriptionmatch) > 0 else ''
							epgnextdescription = descriptionmatch[1].strip() if len(descriptionmatch) > 1 else ''

							# Stampa per debug
							"""
							print("Ora attuale:", epgnowtime)
							print("Prossimo orario:", epgnexttime)
							print("Titolo attuale:", nameepg)
							print("Titolo successivo:", epgnexttitle)
							print("Descrizione attuale:", epgnowdescription)
							print("Descrizione successiva:", epgnextdescription)
							"""
							# Compose the description
							description = epgnowtime + ' ' + nameepg + '\n\n' + epgnowdescription
							description = html_conv.html_unescape(description) + '\n\n'
							description2 = epgnexttime + ' ' + epgnexttitle + '\n\n' + epgnextdescription
							description2 = html_conv.html_unescape(description2) + '\n\n'

					elif ("/movie/" in globalsxp.stream_url) or ("/series/" in globalsxp.stream_url) or ("vod_streams" in globalsxp.stream_url):
						# print('movie globalsxp.stream_url==================================', globalsxp.stream_url)
						globalsxp.stream_live = False

						"""
						TMDB_URL:
						TMDB_ID:
						NAME: Never Let Go - A un passo dal male
						O_NAME: Never Let Go - A un passo dal male
						COVER_BIG:
						RELEASEDATE:
						EPISODE_RUN_TIME:
						YOUTUBE_TRAILER:
						DIRECTOR:
						ACTORS:
						CAST:
						DESCRIPTION:
						PLOT:
						AGE:
						MPAA_RATING:
						RATING_COUNT_KINOPOISK: 0
						COUNTRY:
						GENRE:
						DURATION_SECS: 5929
						DURATION: 01:38:49
						VIDEO: Array
						AUDIO: Array
						BITRATE: 1569
						RATING:
						"""

						NAME = channel.find("title").text if channel.find("title") is not None else ""
						O_NAME = channel.find("O_NAME").text if channel.find("O_NAME") is not None else ""
						COVER_BIG = channel.find("desc_image").text if channel.find("desc_image") is not None else ""
						DESCRIPTION = channel.find("description").text if channel.find("description") is not None else ""
						PLOT = channel.find("PLOT").text if channel.find("PLOT") is not None else ""
						DURATION = channel.find("DURATION").text if channel.find("DURATION") is not None else ""
						GENRE = channel.find("GENRE").text if channel.find("GENRE") is not None else ""
						RELEASEDATE = channel.find("RELEASEDATE").text if channel.find("RELEASEDATE") is not None else ""
						RATING = channel.find("RATING").text if channel.find("RATING") is not None else ""

						if NAME:
							vodTitle = b64decoder(NAME)  # Decodifica Base64 per NAME
						elif O_NAME:
							vodTitle = b64decoder(O_NAME)  # Decodifica Base64 per O_NAME
						else:
							vodTitle = name  # Valore predefinito se entrambi sono assenti

						piconname = COVER_BIG if COVER_BIG else ""

						if DESCRIPTION:
							vodDescription = b64decoder(DESCRIPTION)  # Decodifica Base64 per DESCRIPTION
						elif PLOT:
							vodDescription = b64decoder(PLOT)  # Decodifica Base64 per PLOT
						else:
							vodDescription = "DESCRIPTION: -- --"  # Valore predefinito

						vodDuration = DURATION if DURATION else "DURATION: -- --"  # Valore predefinito
						vodGenre = GENRE if GENRE else "GENRE: -- --"  # Valore predefinito
						vodRelease = RELEASEDATE if RELEASEDATE else "RELEASEDATE: -- --"  # Valore predefinito
						vodRating = RATING if RATING else "RATING: -- --"  # Valore predefinito

						"""
						vodItems = {}
						vodLines = description.splitlines()
						for line in vodLines:
							key, _, value = line.partition(": ")
						if "NAME" in vodItems:
							vodTitle = Utils.checkStr(vodItems["NAME"]).strip()
						elif "O_NAME" in vodItems:
							vodTitle = Utils.checkStr(vodItems["O_NAME"]).strip()
						else:
							vodTitle = name
						# print('vodTitle: ', vodTitle)
						if "COVER_BIG" in vodItems and vodItems["COVER_BIG"] and vodItems["COVER_BIG"] != "null":
							piconname = vodItems["COVER_BIG"].strip()
							# print('piconname: ', piconname)
						if "DESCRIPTION" in vodItems:
							vodDescription = str(vodItems["DESCRIPTION"]).strip()
						elif "PLOT" in vodItems:
							vodDescription = str(vodItems["PLOT"]).strip()
						else:
							vodDescription = str('DESCRIPTION: -- --')
						if "RELEASEDATE" in vodItems:
							vodRelease = str(vodItems["RELEASEDATE"]).strip()
						else:
							vodRelease = str('RELEASEDATE: -- --')
						if "DURATION" in vodItems:
							vodDuration = str(vodItems["DURATION"]).strip()
						else:
							vodDuration = str('DURATION: -- --')
						# print('vodDuration: ', vodDuration)
						if "GENRE" in vodItems:
							vodGenre = str(vodItems["GENRE"]).strip()
						else:
							vodGenre = str('GENRE: -- --')
						print('vodGenre: ', vodGenre)
						"""
						description3 = (
							str(vodTitle) + '\n' +
							str(vodDescription) + '\n' +
							str(vodGenre) + '\n' +
							'Duration: ' + str(vodDuration) + '\n' +
							'Release: ' + str(vodRelease) + '\n' +
							'Rating: ' + str(vodRating) + '\n'
						)

						description = html_conv.html_unescape(description3)
						# print('vodDescription: ', vodDescription)
						# print('channels name: ', name)
						# print('channels description:', description)

					chan_tulpe = (
						str(chan_counter),
						str(name),
						description,
						str(piconname),
						globalsxp.stream_url,
						playlist_url,
						category_id,
						str(desc_image),
						str(description2),
						str(nameepg)
					)
					globalsxp.iptv_list_tmp.append(chan_tulpe)
					globalsxp.btnsearch = globalsxp.next_request

		except Exception as e:
			print('----- get_list failed: ', e)

		if len(globalsxp.iptv_list_tmp):
			self.iptv_list = globalsxp.iptv_list_tmp
			globalsxp.iptv_list = self.iptv_list
		return

	def _request(self, url):
		if "exampleserver" not in str(cfg.hostaddress.value):
			TYPE_PLAYER = '/enigma2.php'
			# TYPE_PLAYER = '/player_api.php'
			url = url.strip(" \t\n\r")
			if globalsxp.next_request == 1:
				url = check_port(url)
				if not url.find(":"):
					self.port = str(cfg.port.value)
					full_url = self.xtream_e2portal_url + ':' + self.port
					url = url.replace(self.xtream_e2portal_url, full_url)
			else:
				url = url + TYPE_PLAYER + "?" + "username=" + self.username + "&password=" + self.password
			globalsxp.urlinfo = url
			try:
				# Effettua la richiesta HTTP
				res = make_request(globalsxp.urlinfo)
				if res is not None:
					try:
						res_xml = fromstring(res)
						if res_xml is not None:
							res_string = tostring(res_xml, encoding='utf-8', method='xml').decode('utf-8')
							file_path = os.path.join('/tmp', 'canali_temp.xml')
							with open(file_path, 'w') as temp_file:
								temp_file.write(res_string)
								temp_file.flush()
								globalsxp.temp_prev_list = res_string
							return res_xml
					except Exception as e:
						print("Error during XML parsing: " + str(e))
						return None
				else:
					print("Request failed or no content received.")
					return None
			except Exception as e:
				print("Error during request or XML processing: " + str(e))
				return None


def menu(menuid, **kwargs):
	if menuid == "mainmenu":
		return [("XCplugin", main, "XCplugin", 4)]
	else:
		return []


def main(session, **kwargs):
	globalsxp.STREAMS = iptv_streamse()
	if "exampleserver.com" not in globalsxp.STREAMS.xtream_e2portal_url:
		globalsxp.STREAMS.read_config()
		globalsxp.STREAMS.get_list(globalsxp.STREAMS.xtream_e2portal_url)
		session.openWithCallback(check_configuring, xc_home)
	else:
		session.open(xc_home)


def check_configuring():
	if cfg.autobouquetupdate.value is True:
		"""Check for new config values for auto start"""
		if globalsxp.autoStartTimer is not None:
			globalsxp.autoStartTimer.update()
		return


def get_next_wakeup():
	return -1


mainDescriptor = PluginDescriptor(name="XCplugin Forever", description=version, where=PluginDescriptor.WHERE_MENU, fnc=menu)


def Plugins(**kwargs):
	result = [
		PluginDescriptor(
			name="XCplugin Forever",
			description=version,
			where=[
				PluginDescriptor.WHERE_AUTOSTART,
				PluginDescriptor.WHERE_SESSIONSTART
			],
			fnc=autostart,
			wakeupfnc=get_next_wakeup
		),
		PluginDescriptor(
			name="XCplugin",
			description=version,
			where=PluginDescriptor.WHERE_PLUGINMENU,
			icon=iconpic,
			fnc=main
		)
	]
	if cfg.strtmain.value:
		result.append(mainDescriptor)
	return result


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
