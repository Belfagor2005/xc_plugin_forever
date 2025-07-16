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
from os.path import exists as file_exists, join
from re import compile
from time import gmtime, strftime, time

# Enigma2 imports
from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen

from enigma import eTimer

from threading import Thread, Lock
from requests import Session
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter

# Local imports
from . import _, version  # , retTest
from .addons.NewOeSk import ctrlSkin
from .addons.modul import globalsxp
from .xcConfig import cfg
from .xcSkin import m3ulistxc, skin_path, xcM3UList


Path_XML = str(cfg.pthxmlfile.value) + "/"
DEFAULT_HOST = "exampleserver.com"
DEFAULT_USER = "Enter_Username"


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

		if hasattr(self.session, 'nav'):
			self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
		else:
			self.initialservice = None
		self.url_pattern = compile(r"http://([^:/]+)(?::(\d+))?/get\.php\?username=([^&]+)&password=([^&]+)&type=([^&]+)")
		self.session_http = Session()
		self.session_http.mount('http://', HTTPAdapter(pool_connections=10, pool_maxsize=100))
		self.cache = {}
		self.active = True

		self.gui_update_timer = eTimer()

		try:
			self.gui_update_timer_conn = self.gui_update_timer.timeout.connect(self._safe_update)
		except:
			self.gui_update_timer.callback.append(self._safe_update)
		
		# self.gui_update_timer_conn = self.gui_update_timer.timeout.get().append(self._safe_update)
		# self.gui_update_timer.callback.append(self._safe_update)

		self.need_gui_update = False
		self.update_lock = Lock()

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
		self.onClose.append(self.cleanup)

	# def cleanup(self):
		# """Clean up resources when the screen is closed"""
		# self.active = False
		# self.session_http.close()

	def cleanup(self):
		"""Clean up resources when the screen is closed"""
		self.active = False
		try:
			if hasattr(self, 'gui_update_timer'):
				self.gui_update_timer.stop()
				try:
					self.gui_update_timer_conn = None
				except:
					pass
		except:
			pass
		
		try:
			self.session_http.close()
		except:
			pass
		
		try:
			if hasattr(self, 'executor'):
				self.executor.shutdown(wait=False)
		except:
			pass

	def selOn(self, host, port, username, password):
		"""Check server status with caching and timeout"""
		if host == DEFAULT_HOST or username == DEFAULT_USER:
			return "Excluded", "Default values"

		cache_key = "{}:{}:{}".format(host, port, username)
		if cache_key in self.cache and self.cache[cache_key]["expiry"] > time():
			return self.cache[cache_key]["data"]

		try:
			# Build URL without f-string
			globalsxp.urlinfo = "http://" + host + ":" + str(port) + "/player_api.php?username=" + username + "&password=" + password

			response = self.session_http.get(globalsxp.urlinfo, timeout=5)
			response.raise_for_status()
			y = response.json()

			auth = "N/A"
			exp_date = "N/A"
			status = "N/A"
			if "user_info" in y and "auth" in y["user_info"]:
				if y["user_info"]["auth"] == 1:
					exp_date = y["user_info"].get("exp_date", "N/A")
					exp_date = strftime("%d-%m-%Y", gmtime(int(exp_date))) if exp_date else "N/A"
					status = y["user_info"].get("status", "N/A")
					auth = status if status in ["Active", "Banned", "Disabled", "Expired", "None"] else "N/A"
				else:
					auth = "Server Not Responding"

				if "server_info" in y:
					time_now = y["server_info"].get("time_now")
					time_zone = y["server_info"].get("timezone")
					time_stamp = y["server_info"].get("timestamp_now")

					if time_now:
						globalsxp.timeserver = str(time_now)
					if time_zone:
						globalsxp.timezone = str(time_zone)
					if time_stamp:
						globalsxp.time_stamp = str(time_stamp)

			result = (auth, exp_date)
			# Cache result for 1 hour
			self.cache[cache_key] = {"data": result, "expiry": time() + 3600}
			return result

		except Exception as e:
			print("selOn Error: " + str(e))
			return "N/A", "N/A"

	def openList(self):
		self.names = []
		self.urls = []
		self.entries = []

		if file_exists(Path_XML + "/xclink.txt"):
			with codecs.open(Path_XML + "/xclink.txt", "r", encoding="utf-8") as f:
				for line in f:
					if line.startswith("#"):
						continue

					matchx = self.url_pattern.match(line)
					if matchx:
						host = matchx.group(1)
						port = matchx.group(2) or "80"
						username = matchx.group(3)
						password = matchx.group(4)
						if host == DEFAULT_HOST or username == DEFAULT_USER:
							print("Skipping default values: " + host + " | " + username)
							continue
						self.names.append("(Verifica...) " + username)
						self.urls.append(line)
						self.entries.append((host, port, username, password))

		m3ulistxc(self.names, self["list"])
		self["live"].setText(str(len(self.names)) + " Team")
		if cfg.infoexp.getValue():
			globalsxp.infoname = str(cfg.infoname.value)
		self["infoname"].setText(globalsxp.infoname)

		Thread(target=self.verify_servers).start()

	def verify_servers(self):
		"""Parallel verification of servers"""
		if not self.entries:
			return
		try:
			with ThreadPoolExecutor(max_workers=5) as executor:
				futures = {}
				for idx, (host, port, username, password) in enumerate(self.entries):
					if not self.active:
						break
					future = executor.submit(self.selOn, host, port, username, password)
					futures[future] = idx

				for future in as_completed(futures):
					if not self.active:
						break

					idx = futures[future]
					try:
						auth, exp_date = future.result()
						host, port, username, password = self.entries[idx]

						# Build the display name
						if auth in [None, "None", "Excluded"]:
							auth = "N/A"

						user, passw = self.streams.read_config()
						if username == user and password == passw:
							name = "X (" + auth + ") " + username + " Expiry:" + exp_date
						else:
							name = "(" + auth + ") " + username + " Expiry:" + exp_date

						# Update the list
						with self.update_lock:
							self.names[idx] = name
							self.need_gui_update = True

						# Schedule a batch GUI update
						self.schedule_gui_update()

					except Exception as e:
						print("Error verifying server: " + str(e))
						with self.update_lock:
							self.names[idx] = "Error: " + username
							self.need_gui_update = True
						self.schedule_gui_update()

			# Final update to be sure
			self.schedule_gui_update(immediate=True)
		except Exception as e:
			print("Exception in verify_servers: " + str(e))

	def schedule_gui_update(self, immediate=False):
		"""Schedule a batch GUI update"""
		if not self.active:
			return

		# Start the timer if not already active
		if not self.gui_update_timer.isActive():
			delay = 100 if immediate else 500  # 100ms for immediate, 500ms for batch
			self.gui_update_timer.start(delay, True)  # Single shot

	def _safe_update(self):
		"""Safe batch GUI update in the main thread"""
		if not self.active or not self.need_gui_update:
			return

		try:
			with self.update_lock:
				m3ulistxc(self.names, self["list"])
				self["live"].setText(str(len(self.names)) + " Team")
				self.need_gui_update = False
		except Exception as e:
			print("Error during GUI update: " + str(e))

	def selectlist(self):
		try:
			idx = self["list"].getSelectionIndex()
			if idx is None or idx < 0 or idx >= len(self.names):
				return
			nom = self.names[idx]
			dom = self.urls[idx]
			if "active" not in nom.lower() or "excluded" in nom.lower() or "n/a" in nom.lower():
				message = (
					"User: " + nom + "\n\n"
					"Is Not Active or Server not responding!\n"
					"Select another list..."
				)
				self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=10)
				return
			port = "80"
			matchx = self.url_pattern.match(dom)
			if matchx:
				host = matchx.group(1)
				if matchx.group(2):
					port = matchx.group(2)

				username = matchx.group(3)
				password = matchx.group(4)
				cfg.port.setValue(port)
				cfg.hostaddress.setValue(host)
				cfg.user.setValue(username)
				cfg.passw.setValue(password)
				self.save_config()

				message = "User: " + username + "\n\nIs Active on Config"
				self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=10)
				self.close()
		except Exception as e:
			print("selectlist Error: " + str(e))

	def save_config(self):
		"""Save the updated configurations in the configuration file."""
		try:
			cfg.save()
			print("Configurations saved successfully.")
		except Exception as e:
			print("Error saving config: " + str(e))

	def infoxc(self):
		try:
			idx = self["list"].getSelectionIndex()
			if idx < 0 or idx >= len(self.urls):
				return
			dom = self.urls[idx]
			TIME_GMT = "%d-%m-%Y %H:%M"
			auth = status = created_at = exp_date = active_cons = max_connections = server_protocol = time_now = "- ? -"
			matchx = self.url_pattern.match(dom)
			if matchx:
				host = matchx.group(1)
				port = matchx.group(2) or "80"
				username = matchx.group(3)
				password = matchx.group(4)
				globalsxp.urlinfo = (
					"http://" + host + ":" + port + "/player_api.php?username=" + username + "&password=" + password
				)
				try:
					response = self.session_http.get(globalsxp.urlinfo, timeout=5)
					if response.status_code == 200:
						y = response.json()

						if "user_info" in y:
							if y["user_info"].get("auth") == 1:
								status = y["user_info"].get("status", "N/A")
								created_at = y["user_info"].get("created_at", "N/A")
								exp_date = y["user_info"].get("exp_date", "N/A")
								active_cons = y["user_info"].get("active_cons", "N/A")
								max_connections = y["user_info"].get("max_connections", "N/A")
								server_protocol = y["server_info"].get("server_protocol", "N/A")
								time_now = y["server_info"].get("time_now", "N/A")
								time_zone = y["server_info"].get("timezone", "N/A")

								# Timestamp conversion
								created_at = (
									strftime(TIME_GMT, gmtime(int(created_at))) if created_at and created_at.isdigit() else created_at
								)
								exp_date = (
									strftime(TIME_GMT, gmtime(int(exp_date))) if exp_date and exp_date.isdigit() else exp_date
								)

								# Status message mapping
								status_msgs = {
									"Active": "Active\nExp date: " + exp_date,
									"Banned": "Banned\nExp date: " + exp_date,
									"Disabled": "Disabled",
									"Expired": "Expired\nExp date: " + exp_date,
								}
								auth = status_msgs.get(status, "Server Not Responding\nExp date: " + exp_date)

								# Build message
								message = (
									"User: " + username + "\n\nStatus: " + auth + "\n\n"
									"Line make at: " + created_at + "\n\n"
									"User Active Now: " + str(active_cons) + "\n\n"
									"Max Connect: " + str(max_connections) + "\n\n"
									"Protocol: " + server_protocol + "\n\n"
									"Time Now: " + time_now + "\n\n"
									"Time Zone: " + time_zone
								)
								self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=20)
								return

					# HTTP error handling
					if response.status_code == 401:
						message = "Error 401: Unauthorized for user " + username
					elif response.status_code == 404:
						message = "Error 404: API not found at " + host + ":" + port
					else:
						message = "HTTP Error " + str(response.status_code) + " for user " + username

					self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=10)
				except Exception as e:
					message = "Error retrieving info: " + str(e)
					self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=5)

		except Exception as e:
			print("infoxc Error: " + str(e))

	def message1(self, answer=None):
		idx = self["list"].getSelectionIndex()
		if idx < 0 or idx >= len(self.names):
			return

		nam = self.names[idx]
		dom = self.urls[idx]
		if answer is None:
			self.session.openWithCallback(
				self.message1,
				MessageBox,
				_("Do you want to remove: %s?") % nam
			)
		elif answer:
			try:
				with codecs.open(Path_XML + "/xclink.txt", "r+", encoding="utf-8") as f:
					lines = f.readlines()
					f.seek(0)
					f.truncate()
					for line in lines:
						if dom in line:
							line = "#" + line
						f.write(line)
				self.session.open(
					MessageBox,
					nam + " has been successfully deleted",
					MessageBox.TYPE_INFO,
					timeout=5
				)
				del self.names[idx]
				del self.urls[idx]
				self["live"].setText(str(len(self.names)) + " Team")
				m3ulistxc(self.names, self["list"])
			except Exception as e:
				self.session.open(
					MessageBox,
					nam + " not deleted! Error: " + str(e),
					MessageBox.TYPE_INFO,
					timeout=5
				)

	def xc_Help(self):
		help_msg = _(
			"Put your lines to the " + Path_XML + "/xclink.txt'.\nFormat type:\n\n"
			"http://YOUR_HOST/get.php?username=USERNAME&password=PASSWORD&type=m3u\n\n"
			"http://YOUR_HOST:YOUR_PORT/get.php?username=USERNAME&password=PASSWORD&type=m3u_plus'\n\n"
			"Select list from Menulist"
		)
		self.session.open(MessageBox, help_msg, MessageBox.TYPE_INFO, timeout=10)

	def close(self, *args, **kwargs):
		self.cleanup()
		try:
			if self.initialservice and hasattr(self.session, 'nav'):
				self.session.nav.playService(self.initialservice)
		except:
			pass
		Screen.close(self, *args, **kwargs)


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
