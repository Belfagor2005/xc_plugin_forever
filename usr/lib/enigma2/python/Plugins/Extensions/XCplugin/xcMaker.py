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
from . import _, version, plugin_path
from .addons import Utils
from .addons.Console import Console as xcConsole
from .addons.modul import globalsxp
from .addons.NewOeSk import ctrlSkin
from .xcConfig import cfg
from .xcSkin import skin_path
from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen

from os import listdir, remove, system
from os.path import isdir
from os.path import exists as file_exists

import codecs
import os

global _session


# def get_config():
	# from .xcConfig import xc_config  # Import locale
	# return xc_config


# def get_cfg():
	# from .xcConfig import cfg  # Import locale
	# return cfg


Path_Picons = str(cfg.pthpicon.value) + "/"
enigma_path = '/etc/enigma2/'
epgimport_path = '/etc/epgimport/'


class xc_maker(Screen):

	def __init__(self, session):
		Screen.__init__(self, session)
		global _session
		_session = self.session
		skin = os.path.join(skin_path, 'xc_maker.xml')
		with codecs.open(skin, "r", encoding="utf-8") as f:
			skin = f.read()
		self.skin = ctrlSkin('xc_maker', skin)
		try:
			Screen.setTitle(self, _('%s') % 'MAKER MENU')
		except:
			try:
				self.setTitle(_('%s') % 'MAKER MENU')
			except:
				pass

		self.list = []
		self["Text"] = Label("")
		self["version"] = Label(version)
		self["description"] = Label('')
		self["key_red"] = Label(_("Back"))
		self["key_green"] = Label(_("Make"))
		self["key_yellow"] = Label(_("Remove"))
		self["actions"] = HelpableActionMap(self, "XCpluginActions", {
			"cancel": self.exitY,
			"back": self.exitY,
			"home": self.exitY,
			"menu": self.configc,
			"help": self.xc_Help,
			"green": self.maker,
			"yellow": self.remove}, -1)
		self.onLayoutFinish.append(self.updateMenuList)

	def configc(self):
		from .xcConfig import xc_config
		self.session.open(xc_config)

	def exitY(self):
		self.close()

	def xc_Help(self):
		from .xcHelp import xc_help
		self.session.openWithCallback(self.updateMenuList, xc_help)

	def updateMenuList(self):
		if cfg.infoexp.getValue():
			globalsxp.infoname = str(cfg.infoname.value)
		self["description"].setText(self.getabout())
		self["Text"].setText(globalsxp.infoname)

	def maker(self):
		if str(cfg.typelist.value) == "Multi Live & VOD":
			dom = "Multi Live & VOD"
			self.session.openWithCallback(self.createCfgxml, MessageBox, _("Convert Playlist to: %s ?") % dom, MessageBox.TYPE_YESNO, timeout=10)  # default=False)
		elif str(cfg.typelist.value) == "Multi Live/Single VOD":
			dom = "Multi Live/Single VOD"
			self.session.openWithCallback(self.createCfgxml, MessageBox, _("Convert Playlist to: %s ?") % dom, MessageBox.TYPE_YESNO, timeout=10)  # default=False)
		elif str(cfg.typelist.value) == "Combined Live/VOD":
			dom = "Combined Live/VOD"
			self.session.openWithCallback(self.save_tv, MessageBox, _("Convert Playlist to: %s ?") % dom, MessageBox.TYPE_YESNO, timeout=10)  # default=False)
		else:
			pass

	def save_tv(self, result):
		if result:
			save_old()
			self.session.open(MessageBox, _("Reload Playlists in progress...") + "\n\n\n" + _("wait please..."), MessageBox.TYPE_INFO, timeout=8)
			return

	def createCfgxml(self, result):
		if result:
			if "exampleserver.com" not in globalsxp.STREAMS.xtream_e2portal_url:
				make_bouquet(_session)
				self.session.open(MessageBox, _("Reload Playlists in progress...") + "\n\n\n" + _("wait please..."), MessageBox.TYPE_INFO, timeout=8)
				return
			else:
				message = (_("First Select the list or enter it in Config"))
				self.session.open(MessageBox, message, MessageBox.TYPE_INFO, timeout=6)

	def remove(self, answer=None):
		if answer is None:
			self.session.openWithCallback(self.remove, MessageBox, _("Remove Playlist from Bouquets?"))
		elif answer:
			uninstaller()
			self.session.open(MessageBox, _("Reload Playlists in progress...") + "\n\n\n" + _("wait please..."), MessageBox.TYPE_INFO, timeout=8)
		else:
			pass

	def getabout(self):
		conthelp = _("GREEN BUTTON:\n ")
		conthelp += _("    Create XC Live/VOD Bouquets\n")
		conthelp += _("    You need to configure the type of output\n")
		conthelp += _("    in the config menu\n\n")
		conthelp += _("YELLOW BUTTON:\n")
		conthelp += _("    Removes all the bouquets that have been\n")
		conthelp += _("    created with XCplugin\n\n")
		conthelp += _("HELP BUTTON:\n")
		conthelp += _("    Go to Help info plugin\n\n")
		conthelp += "        ___________________________________\n"
		conthelp += "Config Folder file xml %s\n" % cfg.pthxmlfile.value
		conthelp += "Config Media Folder %s/\n" % cfg.pthmovie.value
		conthelp += "LivePlayer Active %s\n" % cfg.LivePlayer.value
		conthelp += "Current Service Type: %s\n" % cfg.services.value
		conthelp += _("Current configuration for creating the bouquet\n%s Conversion %s\n\n") % (cfg.typem3utv.getValue(), cfg.typelist.getValue())
		conthelp += "        ___________________________________\n"
		conthelp += "Time is what we want most,\n"
		conthelp += "    but what we use worst.(William Penn)"
		return conthelp


def uninstaller():
	"""Routine di pulizia per rimuovere eventuali modifiche precedenti"""
	try:
		configfilexml = ("/etc/enigma2/e2m3u2bouquet/config.xml")
		try:
			remove(configfilexml)
			print("% s removed successfully" % configfilexml)
		except OSError as error:
			print("File path can not be removed. Error is:", error)

		for fname in listdir(enigma_path):
			file_path = os.path.join(enigma_path, fname)
			if 'userbouquet.xc_' in fname or 'bouquets.tv.bak' in fname:
				remove(file_path)

		if isdir(epgimport_path):
			for fname in listdir(epgimport_path):
				if 'xc_' in fname:
					remove(os.path.join(epgimport_path, fname))
		os.rename(os.path.join(enigma_path, 'bouquets.tv'), os.path.join(enigma_path, 'bouquets.tv.bak'))
		with open(os.path.join(enigma_path, 'bouquets.tv'), 'w+') as tvfile, open(os.path.join(enigma_path, 'bouquets.tv.bak'), 'r+') as bakfile:
			for line in bakfile:
				if '.xc_' not in line:
					tvfile.write(line)
	except Exception as e:
		print("Errore durante il processo di disinstallazione: ", e)
		raise


def save_old():
	fldbouquet = "/etc/enigma2/bouquets.tv"
	namebouquet = globalsxp.STREAMS.playlistname.lower()
	tag = "xc_"
	xc12 = globalsxp.urlinfo.replace("enigma2.php", "get.php") + '&type=dreambox&output=mpegts'
	xc13 = globalsxp.urlinfo.replace("enigma2.php", "get.php") + '&type=m3u_plus&output=ts'
	in_bouquets = False
	desk_tmp = xcname = ''
	try:
		if cfg.typem3utv.value == 'MPEGTS to TV':
			file_path = os.path.join(enigma_path, 'userbouquet.%s%s_.tv' % (tag, namebouquet))
			if file_exists(file_path):
				remove(file_path)
			try:
				localFile = os.path.join(enigma_path, 'userbouquet.%s%s_.tv' % (tag, namebouquet))
				r = Utils.getUrl(xc12)
				with open(localFile, 'w') as f:
					f.write(r)
			except Exception as e:
				print('Error downloading or writing TV file: ', e)
			xcname = 'userbouquet.%s%s_.tv' % (tag, namebouquet)
		else:
			if file_exists(os.path.join(globalsxp.Path_Movies, namebouquet + ".m3u")):
				remove(os.path.join(globalsxp.Path_Movies, namebouquet + ".m3u"))
			try:
				localFile = os.path.join(globalsxp.Path_Movies, '%s.m3u' % namebouquet)
				r = Utils.getUrl(xc13)
				with open(localFile, 'w') as f:
					f.write(r)
			except Exception as e:
				print('Error downloading or writing TV file: ', e)
			name = namebouquet.replace('.m3u', '')
			xcname = 'userbouquet.%s%s_.tv' % (tag, name)
			if file_exists('/etc/enigma2/%s' % xcname):
				remove('/etc/enigma2/%s' % xcname)
			try:
				with open('/etc/enigma2/%s' % xcname, 'w') as outfile:
					outfile.write('#NAME %s\r\n' % name.capitalize())
					desk_tmp = ""
					with open(os.path.join(globalsxp.Path_Movies, '%s.m3u' % name)) as infile:
						for line in infile:
							if line.startswith('http://') or line.startswith('https://'):
								outfile.write('#SERVICE 4097:0:1:0:0:0:0:0:0:0:%s\r\n' % line.strip().replace(':', '%3a'))
								outfile.write('#DESCRIPTION %s\r\n' % desk_tmp)
							elif line.startswith('#EXTINF'):
								desk_tmp = '%s' % line.split(',')[-1].strip()
							elif '<stream_url><![CDATA' in line:
								outfile.write('#SERVICE 4097:0:1:0:0:0:0:0:0:0:%s\r\n' % line.split('[')[-1].split(']')[0].strip().replace(':', '%3a'))
								outfile.write('#DESCRIPTION %s\r\n' % desk_tmp)
							elif '<title>' in line:
								if '<![CDATA[' in line:
									desk_tmp = '%s' % line.split('[')[-1].split(']')[0].strip()
								else:
									desk_tmp = '%s' % line.split('<')[1].split('>')[1].strip()
			except Exception as e:
				print('Error creating bouquet: ', e)

		for line in open(fldbouquet):
			if xcname in line:
				in_bouquets = True
		if in_bouquets is False:
			try:
				with open("/etc/enigma2/new_bouquets.tv", "w") as new_bouquet:
					with open(fldbouquet, "r") as f:
						file_read = f.readlines()

					if cfg.bouquettop.value == "Top":
						new_bouquet.write('#NAME User - bouquets (TV)\n')
						new_bouquet.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "{}" ORDER BY bouquet\r\n'.format(xcname))
						new_bouquet.writelines(line for line in file_read if not line.startswith("#NAME"))
					else:
						new_bouquet.writelines(file_read)
						new_bouquet.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "{}" ORDER BY bouquet\r\n'.format(xcname))
			except IOError as e:
				print("An error occurred while accessing the file: {}".format(e))
			system('cp -rf /etc/enigma2/bouquets.tv /etc/enigma2/backup_bouquets.tv')
			system('mv -f /etc/enigma2/new_bouquets.tv /etc/enigma2/bouquets.tv')
	except Exception as e:
		print(e)


def make_bouquet(session):
	if "exampleserver.com" not in globalsxp.STREAMS.xtream_e2portal_url:
		e2m3u2bouquet = plugin_path + '/bouquet/e2m3u2bouquetpy3.py'
		if not file_exists("/etc/enigma2/e2m3u2bouquet"):
			system("mkdir /etc/enigma2/e2m3u2bouquet")
		configfilexml = ("/etc/enigma2/e2m3u2bouquet/config.xml")
		try:
			remove(configfilexml)
			print("% s removed successfully" % configfilexml)
		except OSError as error:
			print("File path can not be removed. Error is:", error)
		all_bouquet = "0"
		iptv_types = "0"
		multi_vod = "0"
		if cfg.typelist.value == "Multi Live & VOD":
			multi_vod = "1"
		bouquet_top = "0"
		if cfg.bouquettop.value and cfg.bouquettop.value == "Top":
			bouquet_top = "1"
		picons = "0"
		if cfg.picons.value:
			picons = "1"
		username = str(cfg.user.value)
		password = str(cfg.passw.value)
		streamtype_tv = str(cfg.live.value)
		streamtype_vod = str(cfg.services.value)
		m3u_url = globalsxp.urlinfo.replace("enigma2.php", "get.php")
		epg_url = globalsxp.urlinfo.replace("enigma2.php", "xmltv.php")
		if cfg.infoexp.getValue():
			globalsxp.infoname = str(cfg.infoname.value)

		with open(configfilexml, 'w') as f:
			configtext = '<config>\r\n'
			configtext += '\t<supplier>\r\n'
			configtext += '\t\t<name>' + globalsxp.infoname + '</name>\r\n'
			configtext += '\t\t<enabled>1</enabled>\r\n'
			configtext += '\t\t<m3uurl><![CDATA[' + m3u_url + '&type=m3u_plus&output=ts' + ']]></m3uurl>\r\n'
			configtext += '\t\t<epgurl><![CDATA[' + epg_url + ']]></epgurl>\r\n'
			configtext += '\t\t<username><![CDATA[' + username + ']]></username>\r\n'
			configtext += '\t\t<password><![CDATA[' + password + ']]></password>\r\n'
			configtext += '\t\t<iptvtypes>' + iptv_types + '</iptvtypes>\r\n'
			configtext += '\t\t<streamtypetv>' + streamtype_tv + '</streamtypetv>\r\n'
			configtext += '\t\t<streamtypevod>' + streamtype_vod + '</streamtypevod>\r\n'
			configtext += '\t\t<multivod>' + multi_vod + '</multivod>\r\n'
			configtext += '\t\t<allbouquet>' + all_bouquet + '</allbouquet>\r\n'
			configtext += '\t\t<picons>' + picons + '</picons>\r\n'
			configtext += '\t\t<iconpath>' + Path_Picons + '</iconpath>\r\n'
			configtext += '\t\t<xcludesref>0</xcludesref>\r\n'
			configtext += '\t\t<bouqueturl><![CDATA[]]></bouqueturl>\r\n'
			configtext += '\t\t<bouquetdownload>0</bouquetdownload>\r\n'
			configtext += '\t\t<bouquettop>' + bouquet_top + '</bouquettop>\r\n'
			configtext += '\t</supplier>\r\n'
			configtext += '</config>\r\n'
			f.write(configtext)
		dom = str(globalsxp.STREAMS.playlistname)
		com = ("python %s") % e2m3u2bouquet
		session.open(xcConsole, _("Conversion %s in progress: ") % dom, ["%s" % com], closeOnSuccess=True)


"""
for convertion bouquet credits
Thanks to @author: Dave Sully, Doug Mackay
for use e2m3u2bouquet.e2m3u2bouquet -- Enigma2 IPTV m3u to bouquet parser
@copyright:  2017 All rights reserved.
@license:    GNU GENERAL PUBLIC LICENSE version 3
@deffield
CONVERT TEAM TO ALL FAVORITES LIST MULTIVOD + EPG
Open the epgimporter plugin via extension's menu.
Press the blue button to select the sources.
Select the entry xcBouquet and press the OK button
Save it with the green button
Run a manual import using the yellow button manual.
Save the input with the green button.
After a while should you the events imported.
It takes a while so be patient.
"""

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