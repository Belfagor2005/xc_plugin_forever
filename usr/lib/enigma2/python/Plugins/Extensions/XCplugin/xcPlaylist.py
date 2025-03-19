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
#  update     23/02/2025               *
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

from . import _, version, retTest
from .addons.modul import globalsxp
from .addons.NewOeSk import ctrlSkin
from .xcConfig import cfg
from .xcSkin import skin_path, m3ulistxc, xcM3UList

from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from os.path import exists as file_exists, join
import codecs
from re import match
from time import strftime, gmtime
# from .plugin import iptv_streamse

Path_XML = str(cfg.pthxmlfile.value) + "/"


class xc_Playlist(Screen):
	def __init__(self, session, STREAMS):
		Screen.__init__(self, session)
		skin = join(skin_path, 'xc_Playlist.xml')
		with codecs.open(skin, "r", encoding="utf-8") as f:
			skin = f.read()
		self.skin = ctrlSkin('xc_Playlist', skin)
		try:
			Screen.setTitle(self, _('%s') % 'SERVER MENU')
		except:
			try:
				self.setTitle(_('%s') % 'SERVER MENU')
			except:
				pass

		self.list = []
		self.streams = STREAMS
		if self.streams is None:
			raise ValueError("STREAMS must not be None")

		# self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
		if hasattr(self.session, 'nav'):
			self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
		else:
			self.initialservice = None  # Gestisci il caso quando 'nav' non è disponibile
		self["list"] = xcM3UList([])
		self["Text"] = Label("Select Server")
		self["version"] = Label(version)
		self["infoname"] = Label("")
		self["key_red"] = Label(_("Back"))
		self["key_green"] = Label("Select")
		self["key_yellow"] = Label(_("Remove"))
		self["key_blue"] = Label(_("Info"))
		self["live"] = Label("")

		self["actions"] = HelpableActionMap(self, "XCpluginActions", {
			"ok": self.selectlist,
			"green": self.selectlist,
			"home": self.close,
			"cancel": self.close,
			"yellow": self.message1,
			"blue": self.infoxc,
			"info": self.xc_Help,
			"help": self.xc_Help}, -1)
		self.onLayoutFinish.append(self.openList)

	def selOn(self, host, port, username, password):
		try:
			TIME_GMT = '%d-%m-%Y'
			auth = "N/A"
			exp_date = "N/A"
			status = "N/A"
			globalsxp.urlinfo = 'http://' + str(host) + ':' + str(port) + '/player_api.php?username=' + str(username) + '&password=' + str(password)
			self.ycse = retTest(globalsxp.urlinfo)
			if self.ycse:
				y = self.ycse
				if "user_info" in y and "auth" in y["user_info"]:
					if y["user_info"]["auth"] == 1:
						exp_date = y["user_info"].get("exp_date", "N/A")
						exp_date = strftime(TIME_GMT, gmtime(int(exp_date))) if exp_date else "N/A"
						status = y["user_info"].get("status", "N/A")
						auth = status if status in ["Active", "Banned", "Disabled", "Expired", "None"] else "N/A"
					else:
						auth = "Server Not Responding"

					time_now = (y["server_info"]["time_now"])
					if time_now:
						globalsxp.timeserver = str(time_now)

			return auth, exp_date

		except Exception as e:
			print("selOn Error Exception: %s" % e)
			return "N/A", "N/A"

	def openList(self):
		self.names = []
		self.urls = []

		if file_exists(Path_XML + '/xclink.txt'):
			with codecs.open(Path_XML + '/xclink.txt', "r", encoding="utf-8") as f:
				lines = f.readlines()
				name = ''
				host = ''
				port = '80'
				username = ''
				password = ''
				exp_date = ''
				for line in lines:
					if line.startswith('#'):
						continue
					elif line.startswith('http'):
						pattern = r"http://([^:/]+)(?::(\d+))?/get.php\?username=([^&]+)&password=([^&]+)&type=([^&]+)"
						matchx = match(pattern, line)

						if matchx:
							host = matchx.group(1)
							if matchx.group(2):
								port = matchx.group(2)
							username = matchx.group(3)
							password = matchx.group(4)
							namelx, exp_date = self.selOn(str(host), str(port), str(username), str(password))
							if namelx in [None, "None"]:
								namelx = "N/A"
							# print('namelx, exp_date=', namelx, exp_date)
							name = '(' + str(namelx) + ')' + ' ' + str(username) + ' Expiry:' + str(exp_date)
							user, passw = self.streams.read_config()  # Ora restituisce i valori corretti
							# print('globalsxp.STREAMS.read_config:', user, passw)
							if str(username) == user and str(password) == passw:
								name = "X (" + str(namelx) + ") " + str(username) + " Expiry:" + str(exp_date)
							self.names.append(name)
							self.urls.append(line)

		m3ulistxc(self.names, self["list"])
		self["live"].setText(str(len(self.names)) + " Team")
		if cfg.infoexp.getValue():
			globalsxp.infoname = str(cfg.infoname.value)
		self["infoname"].setText(globalsxp.infoname)

	def selectlist(self):
		try:
			idx = self["list"].getSelectionIndex()
			if idx is None or idx < 0 or idx >= len(self.names):
				return
			nom = self.names[idx]
			dom = self.urls[idx]
			if 'active' not in nom.lower():
				message = ("User: %s\n\nIs Not Active or Server not responding!\nSelect another list...") % (str(nom))
				print(str(message))
				self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=10)
				return
			port = '80'
			pattern = r"http://([^:/]+)(?::(\d+))?/get.php\?username=([^&]+)&password=([^&]+)&type=([^&]+)"  # &output=([^&]+)"
			matchx = match(pattern, dom)
			if matchx:
				host = matchx.group(1)
				if matchx.group(2):
					port = matchx.group(2)
				cfg.port.setValue(str(port))
				username = matchx.group(3)
				password = matchx.group(4)
				cfg.hostaddress.setValue(str(host))
				cfg.user.setValue(str(username))
				cfg.passw.setValue(str(password))

				message = ("User: %s\n\nIs Active on Config") % (str(username))
				print(str(message))
				self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=10)
				self.close()
		except IOError as e:
			print(e)

	def infoxc(self):
		try:
			idx = self["list"].getSelectionIndex()
			if idx is None or idx < 0 or idx >= len(self.names):
				return
			dom = self.urls[idx]
			TIME_GMT = '%d-%m-%Y %H:%M'
			auth = status = created_at = exp_date = active_cons = max_connections = server_protocol = time_now = '- ? -'
			host = ''
			username = ''
			password = ''
			port = '80'
			pattern = (r"http://([^:/]+)(?::(\d+))?/get.php\?username=([^&]+)&password=([^&]+)&type=([^&]+)")
			matchx = match(pattern, dom)
			if matchx:
				host = matchx.group(1)
				if matchx.group(2):
					port = matchx.group(2)
				username = matchx.group(3)
				password = matchx.group(4)
			globalsxp.urlinfo = ('http://' + str(host) + ':' + str(port) + '/player_api.php?username=' + str(username) + '&password=' + str(password))
			self.ycse = retTest(globalsxp.urlinfo)
			if self.ycse:
				y = self.ycse
				if "user_info" in y:
					if "auth" in y["user_info"]:
						if y["user_info"]["auth"] == 1:
							auth = y["user_info"]["auth"]
							status = y["user_info"]["status"]
							created_at = y["user_info"]["created_at"]
							exp_date = y["user_info"]["exp_date"]
							active_cons = y["user_info"]["active_cons"]
							max_connections = y["user_info"]["max_connections"]
							server_protocol = y["server_info"]["server_protocol"]
							time_now = y["server_info"]["time_now"]
							time_zone = y["server_info"]["timezone"]

							created_at = strftime(TIME_GMT, gmtime(int(created_at))) if created_at else "Null"
							exp_date = strftime(TIME_GMT, gmtime(int(exp_date))) if exp_date else "Null"
							status_messages = {
								"Active": "Active\nExp date: " + str(exp_date),
								"Banned": "Banned\nExp date: " + str(exp_date),
								"Disabled": "Disabled",
								"Expired": "Expired\nExp date: " + str(exp_date),
							}
							auth = status_messages.get(status, "Server Not Responding\nExp date: " + str(exp_date))

							active_cons = "User Active Now: " + str(active_cons)
							max_connections = "Max Connect: " + str(max_connections)
							server_protocol = "Protocol: " + str(server_protocol)
							time_now = "Time Now: " + str(time_now)
							time_zone = "Time Zone: " + str(time_zone)

							# globalsxp.timeserver = time_now
							# globalsxp.timezone = time_zone

							message = ("User: %s\n\nStatus: %s\n\nLine make at: %s\n\n%s\n\n%s\n\n%s\n\n%s") % (
								str(username), str(auth), str(created_at), str(active_cons), str(max_connections), str(server_protocol), str(time_now)
							)
							print(str(message))
							self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=20)

		except Exception as e:
			status = 'N/A'
			message = ("Error Exception %s") % (e)
			print(str(message))
		except Exception as e:
			message = ("Error %s") % (e)
			print(str(message))
			self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=5)

	def message1(self, answer=None):
		idx = self["list"].getSelectionIndex()
		if idx is None or idx < 0 or idx >= len(self.names):
			return
		nam = self.names[idx]
		dom = self.urls[idx]
		if answer is None:
			self.session.openWithCallback(self.message1, MessageBox, _("Do you want to remove: %s?") % nam)
		elif answer:
			try:
				with codecs.open(Path_XML + '/xclink.txt', "r+") as f:
					lines = f.readlines()
					f.seek(0)
					f.truncate()
					for line in lines:
						if str(dom) in line:
							line = "#%s" % line
						f.write(line)
					self.session.open(MessageBox, nam + _(" has been successfully deleted\nwait time to refresh the list..."), MessageBox.TYPE_INFO, timeout=5)
					del self.names[idx]
					del self.urls[idx]
			except OSError as error:
				print(error)
				self.session.open(MessageBox, nam + _(" not exist!\nwait time to refresh the list..."), MessageBox.TYPE_INFO, timeout=5)
			self["live"].setText(str(len(self.names)) + " Team")
			m3ulistxc(self.names, self["list"])
		else:
			return

	def xc_Help(self):
		self.session.open(MessageBox, _("Put your lines to the %s/xclink.txt'.\nFormat type:\n\nhttp://YOUR_HOST/get.php?username=USERNAME&password=PASSWORD&type=m3u\n\nhttp://YOUR_HOST:YOUR_PORT/get.php?username=USERNAME&password=PASSWORD&type=m3u_plus'\n\nSelect list from Menulist" % Path_XML), MessageBox.TYPE_INFO, timeout=5)

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
