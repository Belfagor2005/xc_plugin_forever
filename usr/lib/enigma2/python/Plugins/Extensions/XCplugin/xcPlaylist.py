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
from . import _, version, retTest
from .addons.modul import globalsxp
from .addons.NewOeSk import ctrlSkin
from .xcConfig import cfg
from .xcShared import skin_path, m3ulistxc, xcM3UList

from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from os.path import exists as file_exists
import codecs
import os
import re
import time

Path_XML = str(cfg.pthxmlfile.value) + "/"


class xc_Playlist(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		skin = os.path.join(skin_path, 'xc_Playlist.xml')
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
		self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
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
			# TIME_GMT = '%d-%m-%Y %H:%M:%S'
			auth = status = 'N/A'
			globalsxp.urlinfo = 'http://' + str(host) + ':' + str(port) + '/player_api.php?username=' + str(username) + '&password=' + str(password)
			self.ycse = retTest(globalsxp.urlinfo)
			if self.ycse:
				y = self.ycse
				if "user_info" in y:
					if "auth" in y["user_info"]:
						if y["user_info"]["auth"] == 1:
							auth = (y["user_info"]["auth"])
							status = (y["user_info"]["status"])
							if str(status) == "Active":
								auth = "Active"
							elif str(status) == "Banned":
								auth = "Banned"
							elif str(status) == "Disabled":
								auth = "Disabled"
							elif str(status) == "Expired":
								auth = "Expired"
							elif str(status) == "None":
								auth = "N/A"
							elif status is None:
								auth = "N/A"
							else:
								auth = "Server Not Responding"
							return str(auth)
				else:
					return str(auth)
			else:
				return str(auth)
		except Exception as e:
			message = ("selOn Error Exception %s") % (e)
			print(message)

	def openList(self):
		self.names = []
		self.urls = []
		if file_exists(Path_XML + '/xclink.txt'):
			with codecs.open(Path_XML + '/xclink.txt', "r", encoding="utf-8") as f:
				lines = f.readlines()
				f.seek(0)
				name = ''
				host = ''
				port = '80'
				username = ''
				password = ''
				for line in lines:
					if line.startswith('#'):
						continue
					elif line.startswith('http'):
						pattern = r"http://([^:/]+)(?::(\d+))?/get.php\?username=([^&]+)&password=([^&]+)&type=([^&]+)"
						match = re.match(pattern, line)
						if match:
							host = match.group(1)
							if match.group(2):
								port = match.group(2)
							username = match.group(3)
							password = match.group(4)
							namelx = self.selOn(str(host), str(port), str(username), str(password))
							if namelx == 'None' or namelx is None:
								namelx = 'N/A'
							name = '(' + str(namelx) + ')' + ' xc_' + str(username)
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
			dom = self.urls[idx]
			port = '80'
			pattern = r"http://([^:/]+)(?::(\d+))?/get.php\?username=([^&]+)&password=([^&]+)&type=([^&]+)"  # &output=([^&]+)"
			match = re.match(pattern, dom)
			if match:
				host = match.group(1)
				if match.group(2):
					port = match.group(2)
				cfg.port.setValue(str(port))
				username = match.group(3)
				password = match.group(4)
				cfg.hostaddress.setValue(str(host))
				cfg.user.setValue(str(username))
				cfg.passw.setValue(str(password))
				self.close()
		except IOError as e:
			print(e)

	def infoxc(self):
		try:
			idx = self["list"].getSelectionIndex()
			dom = self.urls[idx]
			TIME_GMT = '%d-%m-%Y %H:%M:%S'
			auth = status = created_at = exp_date = active_cons = max_connections = server_protocol = timezone = '- ? -'
			host = ''
			username = ''
			password = ''
			port = '80'
			pattern = r"http://([^:/]+)(?::(\d+))?/get.php\?username=([^&]+)&password=([^&]+)&type=([^&]+)"
			match = re.match(pattern, dom)
			if match:
				host = match.group(1)
				if match.group(2):
					port = match.group(2)
				username = match.group(3)
				password = match.group(4)
			globalsxp.urlinfo = 'http://' + str(host) + ':' + str(port) + '/player_api.php?username=' + str(username) + '&password=' + str(password)
			self.ycse = retTest(globalsxp.urlinfo)
			if self.ycse:
				y = self.ycse
				if "user_info" in y:
					if "auth" in y["user_info"]:
						if y["user_info"]["auth"] == 1:
							auth = (y["user_info"]["auth"])
							status = (y["user_info"]["status"])
							created_at = (y["user_info"]["created_at"])
							exp_date = (y["user_info"]["exp_date"])
							active_cons = (y["user_info"]["active_cons"])
							max_connections = (y["user_info"]["max_connections"])
							server_protocol = (y["server_info"]["server_protocol"])
							timezone = (y["server_info"]["timezone"])
							if created_at:
								created_at = time.strftime(TIME_GMT, time.gmtime(int(created_at)))
							if exp_date:
								exp_date = time.strftime(TIME_GMT, time.gmtime(int(exp_date)))
							if str(status) == "Active":
								auth = "Active\nExp date: " + str(exp_date)
							elif str(status) == "Banned":
								auth = "Banned\nExp date: " + str(exp_date)
							elif str(status) == "Disabled":
								auth = "Disabled"
							elif str(status) == "Expired":
								auth = "Expired\nExp date: " + str(exp_date)
							else:
								auth = "Server Not Responding" + str(exp_date)
							active_cons = "User Active Now: " + str(active_cons)
							max_connections = "Max Connect: " + str(max_connections)
							server_protocol = "Protocol: " + str(server_protocol)
							timezone = "Timezone: " + str(timezone)
							message = ("User: %s\n\nStatus: %s\n\nLine make at: %s\n\n%s\n\n%s\n\n%s\n\n%s") % (str(username), str(auth), str(created_at), str(active_cons), str(max_connections), str(server_protocol), str(timezone))
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
