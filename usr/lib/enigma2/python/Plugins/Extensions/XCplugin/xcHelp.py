#!/usr/bin/python
# -*- coding: utf-8 -*-

# ======================================================================
# XCForever Plugin
#
# Original code by Dave Sully, Doug Mackay\
# rewritten by Lululla
#
# ***************************************
#        coded by Lululla               *
#             skin by MMark             *
#  update     06/02/2025                *
#       Skin by MMark                   *
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
	currversion,
	developer_url,
	installer_url,
	paypal,
	version,
)
from .addons import Utils
from .addons.Console import Console as xcConsole
from .addons.NewOeSk import ctrlSkin
from .xcSkin import skin_path
from Components.ActionMap import ActionMap
from Components.Label import Label
from datetime import datetime
from enigma import eTimer
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from six import text_type
import codecs
from os.path import join, exists
from json import loads
from six import PY3, PY2
from time import strptime

if PY3:
	unicode = text_type
	from urllib.request import (urlopen, Request)
elif PY2:
	from urllib2 import (urlopen, Request)


class xc_help(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		skin = join(skin_path, 'xc_help.xml')
		with codecs.open(skin, "r", encoding="utf-8") as f:
			skin = f.read()
		self.skin = ctrlSkin('xc_help', skin)
		try:
			Screen.setTitle(self, _('%s') % 'HELP MENU')
		except:
			try:
				self.setTitle(_('%s') % 'HELP MENU')
			except:
				pass
		self.Update = False
		self["version"] = Label(version)
		self["key_red"] = Label(_("Back"))
		self["key_green"] = Label(_("Config"))
		self["key_yellow"] = Label(_("Main"))
		self["key_blue"] = Label(_("Player"))
		self["helpdesc"] = Label()
		self["helpdesc2"] = Label()
		self["paypal"] = Label()
		self["actions"] = ActionMap(
			[
				"OkCancelActions",
				"DirectionActions",
				"HotkeyActions",
				"InfobarEPGActions",
				"ColorActions",
				"ChannelSelectBaseActions"
			],
			{
				'ok': self.exitx,
				'back': self.exitx,
				'cancel': self.exitx,
				'yellow': self.yellow,
				'green': self.green,
				'blue': self.blue,
				'menu': self.update_dev,
				'yellow_long': self.update_dev,
				'info': self.update_dev,
				'infolong': self.update_dev,
				'showEventInfoPlugin': self.update_dev,
				'red': self.exitx
			},
			-1
		)
		self.timer = eTimer()
		if exists('/usr/bin/apt-get'):
			self.timer_conn = self.timer.timeout.connect(self.check_vers)
		else:
			self.timer.callback.append(self.check_vers)
		self.timer.start(500, 1)
		self.onLayoutFinish.append(self.finishLayout)

	# def check_vers(self):
		# remote_version = '0.0'
		# remote_changelog = ''

		# try:
			# req = Request(Utils.b64decoder(installer_url), headers={'User-Agent': 'Mozilla/5.0'})
			# page = urlopen(req).read().decode("utf-8")  # Decodifica diretta
		# except Exception as e:
			# print("[ERROR] Unable to fetch version info:", str(e))
			# return

		# if page:
			# for line in page.split("\n"):
				# line = line.strip()
				# if line.startswith("version"):
					# remote_version = line.split("=")[-1].strip().strip("'").strip('"')
				# elif line.startswith("changelog"):
					# remote_changelog = line.split("=")[-1].strip().strip("'").strip('"')
					# break

		# self.new_version = remote_version
		# self.new_changelog = remote_changelog
		# if not isinstance(self.new_changelog, str):
			# self.new_changelog = str(self.new_changelog)
		# if not isinstance(self.new_version, str):
			# self.new_version = str(self.new_version)

		# # if float(currversion) < float(remote_version):
		# if currversion < remote_version:
			# self.Update = True
			# self['key_yellow'].show()
			# self['key_green'].show()
			# self.session.open(MessageBox, _('New version %s is available\n\nChangelog: %s\n\nPress info_long or yellow_long button to start force updating.') % (self.new_version, self.new_changelog), MessageBox.TYPE_INFO, timeout=5)

	# def update_me(self):
		# if self.Update is True:
			# self.session.openWithCallback(self.install_update, MessageBox, _("New version %s is available.\n\nChangelog: %s \n\nDo you want to install it now?") % (self.new_version, self.new_changelog), MessageBox.TYPE_YESNO)
		# else:
			# self.session.open(MessageBox, _("Congrats! You already have the latest version..."),  MessageBox.TYPE_INFO, timeout=4)

	# def update_dev(self):
		# try:
			# req = Request(Utils.b64decoder(developer_url), headers={'User-Agent': 'Mozilla/5.0'})
			# page = urlopen(req).read()
			# data = loads(page)

			# if 'pushed_at' not in data:
				# print("[ERROR] 'pushed_at' key not found in JSON response")
				# return

			# remote_date = data['pushed_at']
			# strp_remote_date = strptime(remote_date, '%Y-%m-%dT%H:%M:%SZ')
			# formatted_date = strp_remote_date.strftime('%Y-%m-%d')

			# self.session.openWithCallback(
				# self.install_update,
				# MessageBox,
				# _("Do you want to install update ( %s ) now?") % formatted_date,
				# MessageBox.TYPE_YESNO
			# )

		# except Exception as e:
			# print("[ERROR] Failed to fetch update info:", str(e))

	# def install_update(self, answer=False):
		# if answer:
			# self.session.open(xcConsole, title='Upgrading...', cmdlist=('wget -q "--no-check-certificate" ' + Utils.b64decoder(installer_url) + ' -O - | /bin/sh'), finishedCallback=self.myCallback, closeOnSuccess=False, showStartStopText=True, skin=None)
		# else:
			# self.session.open(MessageBox, _("Update Aborted!"),  MessageBox.TYPE_INFO, timeout=3)

	# def myCallback(self, result=None):
		# print('result:', result)
		# return

	def check_vers(self):
		remote_version = '0.0'
		remote_changelog = ''
		page = ''

		try:
			req = Request(Utils.b64decoder(installer_url), headers={'User-Agent': 'Mozilla/5.0'})
			page = urlopen(req).read().decode("utf-8")
		except Exception as e:
			print("[ERROR] Unable to fetch version info:", str(e))
			return

		if page:
			for line in page.split("\n"):
				line = line.strip()
				if line.startswith("version"):
					remote_version = line.split("=")[-1].strip().strip("'").strip('"')
				elif line.startswith("changelog"):
					remote_changelog = line.split("=")[-1].strip().strip("'").strip('"')
					break

		self.new_version = remote_version
		self.new_changelog = remote_changelog
		if not isinstance(self.new_changelog, str):
			self.new_changelog = str(self.new_changelog)
		if not isinstance(self.new_version, str):
			self.new_version = str(self.new_version)
		# if float(currversion) < float(remote_version):
		if currversion < remote_version:
			self.Update = True
			self.show_update_message()

	def show_update_message(self):
		"""Mostra un MessageBox con le informazioni sull'aggiornamento"""
		if self.session.current_dialog and getattr(self.session.current_dialog, "isModal", lambda: False)():
			self.session.open(
				MessageBox,
				_("New version %s available\n\nChangelog: %s\n\nPress the green button to start the update.") % (
					self.new_version, self.new_changelog
				),
				MessageBox.TYPE_INFO,
				timeout=10  # Aumenta il timeout per dare più tempo all'utente
			)
		else:
			self.session.open(
				MessageBox,
				_("New version %s available\n\nChangelog: %s") % (
					self.new_version, self.new_changelog
				),
				MessageBox.TYPE_INFO,
				timeout=10
			)
			print("Cannot open modal MessageBox. The current screen is not modal.")

			# self["key_green"].setText(_("Update"))
			self['key_yellow'].show()
			self['key_green'].show()

	def update_me(self):
		if self.Update:
			message = _("New version %s is available.\n\nChangelog: %s\n\nDo you want to install it now?") % (
				self.new_version,
				self.new_changelog
			)
			self.session.openWithCallback(
				self.install_update,
				MessageBox,
				message,
				MessageBox.TYPE_YESNO
			)
		else:
			self.session.open(
				MessageBox,
				_("Congrats! You already have the latest version..."),
				MessageBox.TYPE_INFO,
				timeout=10
			)

	def update_dev(self):
		try:
			from six.moves.urllib.error import URLError
			AgentRequest = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.3'
			url = Utils.b64decoder(developer_url)
			req = Request(url, headers={"User-Agent": AgentRequest})
			try:
				response = urlopen(req)
				page = response.read()
			except URLError as e:
				print("Error fetching data from GitHub:", e)
				self.session.open(MessageBox, _("Failed to fetch update information. Please check your internet connection."), MessageBox.TYPE_ERROR)
				return

			try:
				data = loads(page)
			except ValueError as e:
				print("Error parsing JSON data:", e)
				self.session.open(MessageBox, _("Failed to parse update information. Please try again later."), MessageBox.TYPE_ERROR)
				return

			remote_date = data.get("pushed_at")
			if not remote_date:
				print("No 'pushed_at' field found in the response.")
				self.session.open(MessageBox, _("No update information available."), MessageBox.TYPE_INFO)
				return

			try:
				# from datetime import datetime
				strp_remote_date = datetime.strptime(remote_date, "%Y-%m-%dT%H:%M:%SZ")
				# strp_remote_date = strptime(remote_date, "%Y-%m-%dT%H:%M:%SZ")
				formatted_date = strp_remote_date.strftime("%Y-%m-%d")
			except ValueError as e:
				print("Error parsing date:", e)
				self.session.open(MessageBox, _("Invalid date format in update information."), MessageBox.TYPE_ERROR)
				return

			self.session.openWithCallback(
				self.install_update,
				MessageBox,
				_("Do you want to install update (%s) now?") % formatted_date,
				MessageBox.TYPE_YESNO
			)

		except Exception as e:
			print("Unexpected error in update_dev:", e)
			self.session.open(MessageBox, _("An unexpected error occurred. Please try again later."), MessageBox.TYPE_ERROR)

	def install_update(self, answer=False):
		if answer:
			self.session.open(xcConsole, "Upgrading...", cmdlist=["wget -q --no-check-certificate " + Utils.b64decoder(installer_url) + " -O - | /bin/sh"], finishedCallback=self.myCallback, closeOnSuccess=False)
		else:
			self.session.open(MessageBox, _("Update Aborted!"), MessageBox.TYPE_INFO, timeout=3)

	def myCallback(self, result=None):
		print("result:", result)
		return

	def finishLayout(self):
		helpdesc = self.homecontext()
		helpdesc2 = self.homecontext2()
		pay = paypal()
		self["paypal"].setText(pay)
		self["helpdesc"].setText(helpdesc)
		self["helpdesc2"].setText(helpdesc2)

	def homecontext(self):
		conthelp = "%s\n\n" % version
		conthelp += "Original code by Dave Sully, Doug Mackay\n\n"
		conthelp += "Modded by Lululla\n\n"
		conthelp += "Skin By: Mmark - Info e2skin.blogspot.it\n\n"
		conthelp += ("        ___________________________________\n")
		conthelp += "Please reports bug or info to forums:\n\n"
		conthelp += "Corvoboys - linuxsat-support\n\n"
		conthelp += ("        ___________________________________\n")
		conthelp += "Special thanks to:\n"
		conthelp += "MMark, Pcd, KiddaC\n\n"
		conthelp += "*FOR UPDATE PLUGIN PRESS INFO_LONG BUTTON\n"
		return conthelp

	def homecontext2(self):
		conthelp = "@Lululla enjoy"
		# conthelp = "Config Folder file xml %s\n" % cfg.pthxmlfile.value
		# conthelp += "Config Media Folder %s/\n" % cfg.pthmovie.value
		# conthelp += "LivePlayer Active %s\n" % cfg.LivePlayer.value
		# conthelp = "Current Service Type: %s\n" % cfg.services.value
		# conthelp += _("Current configuration for creating the bouquet\n    > %s Conversion %s\n\n") % (cfg.typem3utv.getValue(), cfg.typelist.getValue())
		return conthelp

	def yellow(self):
		helpdesc = self.yellowcontext()
		self["helpdesc"].setText(helpdesc)
		helpdesc2 = self.homecontext2()
		self["helpdesc2"].setText(helpdesc2)
		self["helpdesc2"].show()

	def yellowcontext(self):
		conthelp = "    HOME - MAIN\n\n"
		conthelp += ("    (MENU BUTTON):\n")
		conthelp += _("            Config Setup Options\n")
		conthelp += ("        ___________________________________\n")
		conthelp += ("    (5 BUTTON):\n")
		conthelp += _("            MediaPlayer\n")
		conthelp += ("        ___________________________________\n")
		conthelp += ("    (9/HELP BUTTON):\n")
		conthelp += _("            Help\n")
		conthelp += ("        ___________________________________\n")
		conthelp += ("    (PVR/FILELIST/2 BUTTON):\n")
		conthelp += _("            Open Movie Folder\n")
		conthelp += ("        ___________________________________\n")
		conthelp += ("    (EPG/INFO/0 BUTTON):\n")
		conthelp += _("            Epg guide or imdb/tmdb\n")
		conthelp += ("        ___________________________________\n")
		conthelp += ("    (GREEN BUTTON):\n ")
		conthelp += _("            Start Download or Record Selected Channel:\n")
		conthelp += _("            Set 'Live Player Active' in Setting:\n")
		conthelp += _("            Set 'No' for Record Live\n")
		conthelp += ("        ___________________________________\n")
		conthelp += ("    (YELLOW BUTTON):\n")
		conthelp += _("            Start Download All Episodes Series\n")
		conthelp += ("    (BLUE BUTTON):\n")
		conthelp += _("            Search LIve/Movie")
		conthelp += ("        ___________________________________\n")
		return conthelp

	def green(self):
		helpdesc = self.greencontext()
		helpdesc2 = self.homecontext2()
		self["helpdesc"].setText(helpdesc)
		self["helpdesc2"].setText(helpdesc2)
		self["helpdesc2"].show()

	def greencontext(self):
		conthelp = "    MENU CONFIG\n\n"
		conthelp += ("    (YELLOW BUTTON):\n")
		conthelp += ("        ___________________________________\n")
		conthelp += _("            If you have a file\n")
		conthelp += _("            /etc/enigma2/iptv.sh\n")
		conthelp += _("            Import with Yellow Button this file\n\n")
		conthelp += _("            Format:\n")
		conthelp += _("            USERNAME='xxxxxxxxxx'\n")
		conthelp += _("            PASSWORD='yyyyyyyyy'\n")
		conthelp += _("            url='http://server:port/xxyyzz'\n\n")
		conthelp += ("    (BLUE BUTTON):\n")
		conthelp += ("        ___________________________________\n")
		conthelp += _("            If you have a file:\n")
		conthelp += _("            /tmp/xc.txt\n")
		conthelp += _("            Import with Blue Button this file\n\n")
		conthelp += _("            Format:\n")
		conthelp += _("            host\t(host without http:// )\n")
		conthelp += _("            port\n")
		conthelp += _("            user\n")
		conthelp += _("            password\n")
		return conthelp

	def blue(self):
		helpdesc = self.bluecontext()
		self["helpdesc"].setText(helpdesc)
		helpdesc2 = self.homecontext2()
		self["helpdesc2"].setText(helpdesc2)
		self["helpdesc2"].hide()

	def bluecontext(self):
		conthelp = "    PLAYER XC\n"
		conthelp += ("        ___________________________________\n")
		conthelp += ("    (RED BUTTON):\n")
		conthelp += _("            Return to Channels List\n")
		conthelp += _("    (BLUE BUTTON):\n")
		conthelp += _("            Init Continue Play\n")
		conthelp += _("    (REC BUTTON):\n")
		conthelp += _("            Download Video \n")
		conthelp += _("    (STOP BUTTON):\n")
		conthelp += _("            Close/Stop Movie/Live\n\n")
		conthelp += ("UTILITY PLAYER M3U\n")
		conthelp += ("        ___________________________________\n")
		conthelp += _("    (GREEN BUTTON):\n")
		conthelp += _("            Remove file from list\n")
		conthelp += _("    (YELLOW BUTTON):\n")
		conthelp += _("            Export file m3u to Bouquet .tv\n")
		conthelp += _("    (BLUE BUTTON):\n")
		conthelp += _("            Download file m3u from current server\n\n")
		conthelp += ("UTILITY PLAYER M3U - OPEN FILE:\n")
		conthelp += ("        ___________________________________\n")
		conthelp += _("    When opening an .m3u file instead:\n")
		conthelp += _("   (GREEN BUTTON):\n")
		conthelp += _("           Reload List\n")
		conthelp += _("   (YELLOW BUTTON):\n")
		conthelp += _("           Download VOD selected channel\n")
		conthelp += _("   (BLUE BUTTON):\n")
		conthelp += _("           Search for a title in the list")
		return conthelp

	def exitx(self):
		self.close()

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
