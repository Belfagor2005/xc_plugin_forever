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
from os import stat
from os.path import exists as file_exists, isdir, join
from re import DOTALL, findall

# Enigma2 imports
from Components.ActionMap import HelpableActionMap
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.config import (
	ConfigClock,
	ConfigDirectory,
	ConfigEnableDisable,
	ConfigPassword,
	ConfigSelection,
	ConfigSelectionNumber,
	ConfigSubsection,
	ConfigText,
	ConfigYesNo,
	config,
	configfile,
	getConfigListEntry,
	NoSave,
)
from Screens.LocationBox import LocationBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools import Directories

# Local package imports
from . import _, version
from .addons.NewOeSk import ctrlSkin
from .addons.modul import globalsxp
from .xcHelp import xc_help
from .xcSkin import skin_path


xc_list = "/tmp/xc.txt"
iptvsh = "/etc/enigma2/iptv.sh"
modelive = [("1", "Dvb(1)"), ("4097", "IPTV(4097)")]
modemovie = [("4097", "IPTV(4097)")]

if file_exists("/usr/bin/gstplayer"):
	modelive.append(("5001", "Gstreamer(5001)"))
	modemovie.append(("5001", "Gstreamer(5001)"))
if file_exists("/usr/bin/exteplayer3"):
	modelive.append(("5002", "Exteplayer3(5002)"))
	modemovie.append(("5002", "Exteplayer3(5002)"))
if file_exists('/var/lib/dpkg/info'):
	modelive.append(("8193", "eServiceUri(8193)"))
	modemovie.append(("8193", "eServiceUri(8193)"))


"""
# def get_help():
	# from .xcHelp import xc_help  # Import locale
	# return xc_help
"""


print('Xc Version :', version)
config.plugins.XCplugin = ConfigSubsection()
cfg = config.plugins.XCplugin
cfg.LivePlayer = ConfigEnableDisable(default=False)
cfg.autobouquetupdate = ConfigEnableDisable(default=False)
cfg.badcar = ConfigEnableDisable(default=False)
cfg.bouquettop = ConfigSelection(default="Bottom", choices=["Bottom", "Top"])
cfg.data = ConfigYesNo(default=False)
cfg.fixedtime = ConfigClock(default=0)
cfg.infoexp = ConfigYesNo(default=False)
cfg.stoplayer = ConfigYesNo(default=True)
cfg.infoname = NoSave(ConfigText(default="myBouquet"))
cfg.last_update = ConfigText(default="Never")
cfg.live = ConfigSelection(default='1', choices=modelive)
cfg.hostaddress = ConfigText(default="exampleserver.com")
cfg.user = ConfigText(default="Enter_Username", visible_width=50, fixed_size=False)
cfg.passw = ConfigPassword(default="******", visible_width=50, fixed_size=False, censor="*")
cfg.uptimezone = ConfigSelectionNumber(default=0, min=-20, max=80, stepwidth=1)
cfg.pdownmovie = ConfigSelection(default="JobManager", choices=["JobManager", "Direct", "Requests"])
cfg.picons = ConfigEnableDisable(default=False)
cfg.port = ConfigText(default="80", fixed_size=False)
cfg.pthmovie = ConfigDirectory(default=config.movielist.last_videodir.value)
cfg.pthpicon = ConfigDirectory(default="/usr/share/enigma2/picon/")
cfg.pthxmlfile = ConfigDirectory(default="/etc/enigma2/xc")
cfg.screenxl = ConfigEnableDisable(default=True)
cfg.services = ConfigSelection(default='4097', choices=modemovie)
cfg.strtmain = ConfigEnableDisable(default=True)
cfg.timeout = ConfigSelectionNumber(default=10, min=5, max=80, stepwidth=5)
cfg.timetype = ConfigSelection(default="interval", choices=[("interval", _("interval")), ("fixed time", _("fixed time"))])
cfg.typelist = ConfigSelection(default="Multi Live & VOD", choices=["Multi Live & VOD", "Multi Live/Single VOD", "Combined Live/VOD"])
cfg.typem3utv = ConfigSelection(default="MPEGTS to TV", choices=["M3U to TV", "MPEGTS to TV"])
cfg.updateinterval = ConfigSelectionNumber(default=24, min=1, max=48, stepwidth=1)
Path_XML = str(cfg.pthxmlfile.value) + "/"


# Ensure movie path
def defaultMoviePath():
	result = config.usage.default_path.value
	if not result.endswith("/"):
		result += "/"
	if not isdir(result):
		return Directories.defaultRecordingLocation(config.usage.default_path.value)
	return result


if not isdir(config.movielist.last_videodir.value):
	try:
		config.movielist.last_videodir.value = defaultMoviePath()
		config.movielist.last_videodir.save()
	except Exception as e:
		print("Error saving movie path:", e)


def defaultPiconPath():
	# get the configured picon directory
	result = cfg.pthpicon.value
	if not result.endswith("/"):
		result += "/"
	# if it does not exist, try Enigma2 default location
	if not isdir(result):
		default_path = Directories.defaultRecordingLocation(result)
		if default_path and isdir(default_path):
			return default_path
		else:
			return "/usr/share/enigma2/picon/"
	return result


# ensure the directory exists and save back into the plugin config
if not isdir(cfg.pthpicon.value):
	try:
		new_path = defaultPiconPath()
		cfg.pthpicon.value = new_path
		cfg.pthpicon.save()
	except Exception as e:
		print("Error setting picon directory:", e)
		cfg.pthpicon.value = "/usr/share/enigma2/picon/"
		cfg.pthpicon.save()


def update_globals_dynamic():
	for var_name in globalsxp.__dict__.keys():  # Itera su tutte le chiavi di globalsxp
		if hasattr(cfg, var_name):  # Verifica se esiste una configurazione con lo stesso nome
			config_value = getattr(cfg, var_name).value  # Ottieni il valore dalla configurazione
			current_value = getattr(globalsxp, var_name)
			if current_value != config_value:
				setattr(globalsxp, var_name, config_value)  # Aggiorna la variabile globale
				print("Updated global: %s to %s" % (var_name, config_value))


cfg.save()
update_globals_dynamic()


class xc_config(Screen, ConfigListScreen):
	def __init__(self, session):
		Screen.__init__(self, session)

		skin = join(skin_path, 'xc_config.xml')
		with codecs.open(skin, "r", encoding="utf-8") as f:
			skin = f.read()
		self.skin = ctrlSkin('xc_config', skin)
		try:
			Screen.setTitle(self, _('%s') % 'CONFIG MENU')
		except:
			try:
				self.setTitle(_('%s') % 'CONFIG MENU')
			except:
				pass

		self.list = []
		self.onChangedEntry = []

		self["playlist"] = Label("Xstream Code Setup")
		self["version"] = Label(version)
		self['statusbar'] = Label()
		self["description"] = Label("")
		self["key_red"] = Label(_("Back"))
		self["key_green"] = Label(_("Save"))
		self["key_blue"] = Label(_("Import") + " txt")
		self["key_yellow"] = Label(_("Import") + " sh")
		self["actions"] = HelpableActionMap(
			self,
			"XCpluginActions",
			{
				"home": self.extnok,
				"cancel": self.extnok,
				"left": self.keyLeft,
				"right": self.keyRight,
				"up": self.keyUp,
				"down": self.keyDown,
				"help": self.xc_Help,
				"yellow": self.iptv_sh,
				"green": self.cfgok,
				"blue": self.ImportInfosServer,
				"showVirtualKeyboard": self.KeyText,
				"ok": self.ok
			},
			-1
		)
		self.update_status()
		ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)
		self.createSetup()
		self.showhide()
		self.onLayoutFinish.append(self.layoutFinished)

	def iptv_sh(self, answer=None):
		try:
			if answer is None:
				self.session.openWithCallback(
					self.iptv_sh,
					MessageBox,
					_("Import Server from /etc/enigma2/iptv.sh?")
				)
			elif answer:
				if file_exists(iptvsh) and stat(iptvsh).st_size > 0:
					try:
						with open(iptvsh, 'r') as f:
							fpage = f.read()
							print('fpage=', fpage)

						regexcat = r'USERNAME="(.*?)";.*?PASSWORD="(.*?)";.*?url="http://([^:]+):(\d+)/get.php'
						matches = findall(regexcat, fpage, DOTALL)

						if matches:
							for match in matches:
								username, password, host, port = match
								print("USERNAME:", username)
								print("PASSWORD:", password)
								print("URL Host:", host)
								print("Port:", port)

								cfg.hostaddress.setValue(host)
								cfg.port.setValue(port)
								cfg.user.setValue(username)
								cfg.passw.setValue(password)

							self.xml_plugin()
							self.createSetup()

						else:
							print("No match found.")
							self.session.open(
								MessageBox,
								_("Invalid format in %s. Could not extract server details." % iptvsh),
								MessageBox.TYPE_ERROR,
								timeout=5
							)

					except Exception as e:
						self.session.open(
							MessageBox,
							_("Error reading or processing %s: %s" % (iptvsh, str(e))),
							MessageBox.TYPE_ERROR,
							timeout=5
						)
				else:
					self.session.open(
						MessageBox,
						_("Missing or empty file: %s" % iptvsh),
						MessageBox.TYPE_INFO,
						timeout=4
					)
			else:
				return
		except Exception as e:
			print("Error in iptv_sh:", str(e))

	def ImportInfosServer(self, answer=None):
		try:
			if answer is None:
				self.session.openWithCallback(
					self.ImportInfosServer,
					MessageBox,
					_("Import Server from /tmp/xc.tx?")
				)
			elif answer:
				if file_exists(xc_list) and stat(xc_list).st_size > 0:
					try:
						with codecs.open(xc_list, "r", encoding="utf-8") as f:
							lines = f.readlines()

						# Check if the file has enough lines and that they are not empty
						if len(lines) < 4 or any(not line.strip() for line in lines):
							self.session.open(
								MessageBox,
								_("Invalid file format: not enough or empty lines in %s" % xc_list),
								MessageBox.TYPE_ERROR,
								timeout=5
							)
							return

						# Extract values from the file
						url = lines[0].strip()
						port = lines[1].strip().replace(":", "_")
						user = lines[2].strip().replace(":", "_")
						pswrd = lines[3].strip()

						# Set the configuration values
						cfg.hostaddress.setValue(url)
						cfg.port.setValue(port)
						cfg.user.setValue(user)
						cfg.passw.setValue(pswrd)

						# Call additional setup methods
						self.xml_plugin()
						self.createSetup()

					except Exception as e:
						self.session.open(
							MessageBox,
							_("Error reading or processing the file: %s" % str(e)),
							MessageBox.TYPE_ERROR,
							timeout=5
						)
				else:
					self.session.open(
						MessageBox,
						_("File not found or empty: %s" % xc_list),
						MessageBox.TYPE_INFO,
						timeout=5
					)
			else:
				return
		except Exception as e:
			print("Error in ImportInfosServer:", str(e))

	def update_status(self):
		if cfg.autobouquetupdate:
			self['statusbar'].setText(_("Last channel update: %s") % cfg.last_update.value)

	def layoutFinished(self):
		pass

	def xc_Help(self):
		# self.session.open(xc_help)
		self.session.openWithCallback(self.layoutFinished, xc_help)

	def createSetup(self):
		self.editListEntry = None
		self.list = []
		indent = "- "

		self.list.append(getConfigListEntry(_("Data Server Configuration:"), cfg.data, (_("Your Server Login and data input"))))
		if cfg.data.getValue():
			self.list.append(getConfigListEntry(indent + (_("Server URL")), cfg.hostaddress, (_("Enter Server Url without 'http://' your_domine"))))
			self.list.append(getConfigListEntry(indent + (_("Server PORT")), cfg.port, (_("Enter Server Port Eg.:'8080'"))))
			self.list.append(getConfigListEntry(indent + (_("Server Username")), cfg.user, (_("Enter Username"))))
			self.list.append(getConfigListEntry(indent + (_("Server Password")), cfg.passw, (_("Enter Password"))))
		self.list.append(getConfigListEntry(_("Server Timeout"), cfg.timeout, (_("Timeout Server (sec)"))))
		self.list.append(getConfigListEntry(_("Adjust Timezone"), cfg.uptimezone, (_("Adjust Timezone (hour)"))))

		self.list.append(getConfigListEntry(_("Folder user file .xml"), cfg.pthxmlfile, (_("Configure folder containing .xml files\nPress 'OK' to change location."))))
		self.list.append(getConfigListEntry(_("Media Folder "), cfg.pthmovie, (_("Configure folder containing movie/media files\nPress 'OK' to change location."))))

		self.list.append(getConfigListEntry(_("Main Screen XL"), cfg.screenxl, (_("Active Main Screen Large"))))
		self.list.append(getConfigListEntry(_("LivePlayer Active "), cfg.LivePlayer, (_("Live Player for Stream .ts: set No for Record Live"))))
		if cfg.LivePlayer.value is True:
			self.list.append(getConfigListEntry(indent + (_("Live Services Type")), cfg.live, (_("Configure service Reference Dvb-Iptv-Gstreamer-Exteplayer3"))))

		self.list.append(getConfigListEntry(_("Download Type "), cfg.pdownmovie, (_("Configure type of download movie: JobManager/Direct."))))

		self.list.append(getConfigListEntry(_("Filter Bad Tag"), cfg.badcar, (_("Filter Bad Tag"))))

		self.list.append(getConfigListEntry(_("Bouquet style "), cfg.typelist, (_("Configure the type of conversion in the favorite list"))))
		if cfg.typelist.value == "Combined Live/VOD":
			self.list.append(getConfigListEntry(indent + (_("Conversion type Output ")), cfg.typem3utv, (_("Configure type of stream to be downloaded by conversion"))))

		self.list.append(getConfigListEntry(_("Vod Services Type"), cfg.services, (_("Configure service Reference Iptv-Gstreamer-Exteplayer3"))))

		self.list.append(getConfigListEntry(_("Stop Player on Exit"), cfg.stoplayer, (_("If player active STOP player riproduction on exit"))))

		self.list.append(getConfigListEntry(_("Name Bouquet Configuration:"), cfg.infoexp, (_("Set Name for MakerBouquet"))))
		if cfg.infoexp.getValue():
			self.list.append(getConfigListEntry(indent + (_("Name Bouquet Export")), cfg.infoname, (_("Configure name of exported bouquet. Default is myBouquet"))))

		self.list.append(getConfigListEntry(_("Place IPTV bouquets at "), cfg.bouquettop, (_("Configure to place the bouquets of the converted lists"))))

		self.list.append(getConfigListEntry(_("Automatic bouquet update (schedule):"), cfg.autobouquetupdate, (_("Active Automatic Bouquet Update"))))
		if cfg.autobouquetupdate.value is True:
			self.list.append(getConfigListEntry(indent + (_("Schedule type:")), cfg.timetype, (_("At an interval of hours or at a fixed time"))))
			if cfg.timetype.value == "interval":
				self.list.append(getConfigListEntry(2 * indent + (_("Update interval (hours):")), cfg.updateinterval, (_("Configure every interval of hours from now"))))
			if cfg.timetype.value == "fixed time":
				self.list.append(getConfigListEntry(2 * indent + (_("Time to start update:")), cfg.fixedtime, (_("Configure at a fixed time"))))
		self.list.append(getConfigListEntry(_("Picons IPTV "), cfg.picons, (_("Download Picons ?"))))
		if cfg.picons.value:
			self.list.append(getConfigListEntry(indent + (_("Picons IPTV bouquets to ")), cfg.pthpicon, (_("Configure folder containing picons files\nPress 'OK' to change location."))))
		self.list.append(getConfigListEntry(_("Link in Main Menu "), cfg.strtmain, (_("Display XCplugin in Main Menu"))))

		self["config"].list = self.list
		self["config"].l.setList(self.list)
		self.setInfo()

	def setInfo(self):
		try:
			sel = self['config'].getCurrent()[2]
			if sel:
				self['description'].setText(str(sel))
			else:
				self['description'].setText(_('SELECT YOUR CHOICE'))
			return
		except Exception as e:
			print("Error ", e)

	def changedEntry(self):
		for x in self.onChangedEntry:
			x()

	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]

	def showhide(self):
		pass

	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())

	def createSummary(self):
		from Screens.Setup import SetupSummary
		return SetupSummary

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.createSetup()
		self.showhide()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.createSetup()
		self.showhide()

	def keyDown(self):
		self['config'].instance.moveSelection(self['config'].instance.moveDown)
		self.createSetup()
		self.showhide()

	def keyUp(self):
		self['config'].instance.moveSelection(self['config'].instance.moveUp)
		self.createSetup()
		self.showhide()

	def ok(self):
		sel = self["config"].getCurrent()[1]
		if sel:
			if sel == cfg.pthmovie:
				self.setting = "pthmovie"
				self.openDirectoryBrowser(cfg.pthmovie.value, self.setting)
			elif sel == cfg.pthxmlfile:
				self.setting = "pthxmlfile"
				self.openDirectoryBrowser(Path_XML, self.setting)
			elif sel == cfg.pthpicon:
				self.setting = "pthpicon"
				self.openDirectoryBrowser(cfg.pthpicon.value, self.setting)
			else:
				print("Unknown selection:", sel)

	def openDirectoryBrowser(self, path, itemcfg):
		try:
			callback_map = {
				"pthmovie": self.openDirectoryBrowserCB(cfg.pthmovie),
				"pthxmlfile": self.openDirectoryBrowserCB(cfg.pthxmlfile),
				"pthpicon": self.openDirectoryBrowserCB(cfg.pthpicon)
			}
			if itemcfg in callback_map:
				self.session.openWithCallback(
					callback_map[itemcfg],
					LocationBox,
					windowTitle=_("Choose Directory:"),
					text=_("Choose directory"),
					currDir=str(path),
					bookmarks=config.movielist.videodirs,
					autoAdd=True,
					editDir=True,
					inhibitDirs=["/bin", "/boot", "/dev", "/home", "/lib", "/proc", "/run", "/sbin", "/sys", "/usr", "/var"]
				)
		except Exception as e:
			print(e)

	def openDirectoryBrowserCB(self, config_entry):
		def callback(path):
			if path is not None:
				config_entry.setValue(path)
		return callback

	def cfgok(self):
		if cfg.picons.value:
			if not file_exists(cfg.picons.value):
				self.session.open(
					MessageBox,
					_("%s NOT DETECTED!" % cfg.picons.value),
					MessageBox.TYPE_INFO,
					timeout=4
				)
				return

		if cfg.pthxmlfile.value:
			if not file_exists(cfg.pthxmlfile.value):
				self.session.open(
					MessageBox,
					_("%s NOT DETECTED!" % cfg.pthxmlfile.value),
					MessageBox.TYPE_INFO,
					timeout=4
				)
				return

		if cfg.pthmovie.value:
			if not file_exists(cfg.pthmovie.value):
				self.session.open(
					MessageBox,
					_("%s NOT DETECTED!" % cfg.pthmovie.value),
					MessageBox.TYPE_INFO,
					timeout=4
				)
				return

		self.save()

	def save(self):
		if self["config"].isChanged():
			for x in self["config"].list:
				x[1].save()
			cfg.hostaddress.save()
			cfg.port.save()
			cfg.user.save()
			cfg.passw.save()
			configfile.save()
			self.xml_plugin()
			update_globals_dynamic()
			self.session.open(MessageBox, _("Settings saved successfully !"), MessageBox.TYPE_INFO, timeout=5)
		self.close()

	def xml_plugin(self):
		try:
			if str(cfg.hostaddress.value) != 'exampleserver.com':
				if file_exists(Path_XML + '/xclink.txt'):
					linecode = 'http://' + str(cfg.hostaddress.value) + ':' + str(cfg.port.value) + '/get.php?username=' + str(cfg.user.value) + '&password=' + str(cfg.passw.value) + '&type=m3u_plus'
					line_exists = False
					with codecs.open(Path_XML + '/xclink.txt', "r+", encoding="utf-8") as f:
						lines = f.readlines()
						for line in lines:
							if line.strip() == linecode:
								line_exists = True
								break

						if not line_exists:
							f.write('\n' + linecode + '\n')
							self.session.open(MessageBox, _("Line appended to playlist"), type=MessageBox.TYPE_INFO, timeout=5)
						else:
							self.session.open(MessageBox, _("Line already exists in playlist"), type=MessageBox.TYPE_INFO, timeout=5)
		except Exception as e:
			print("xcConfig xml_plugin failed: ", e)

	def KeyText(self):
		sel = self["config"].getCurrent()
		if sel:
			self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=self["config"].getCurrent()[0], text=self["config"].getCurrent()[1].value)

	def VirtualKeyBoardCallback(self, callback=None):
		if callback is not None and len(callback):
			self["config"].getCurrent()[1].value = callback
			self["config"].invalidate(self["config"].getCurrent())
		return

	def extnok(self, answer=None):
		if answer is None:
			self.session.openWithCallback(self.extnok, MessageBox, _("Really close without saving settings?"))
		elif answer:
			for x in self["config"].list:
				x[1].cancel()
			self.close()
		else:
			return

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
