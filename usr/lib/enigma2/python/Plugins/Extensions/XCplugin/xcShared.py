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
from . import _
from .addons.modul import globalsxp
from .addons.Utils import web_info
from .xcConfig import cfg
from .xcMaker import xc_maker, save_old

from enigma import eTimer
import time


class AutoStartTimer:
	def __init__(self, session):
		print("*** running AutoStartTimer XC-Forever ***")
		global _session
		self.session = session
		_session = session
		self.timer = eTimer()
		try:
			self.timer.callback.append(self.on_timer)
		except:
			self.timer_conn = self.timer.timeout.connect(self.on_timer)
		self.timer.start(100, True)
		self.update()

	def get_wake_time(self):
		if cfg.autobouquetupdate.value is True:
			if cfg.timetype.value == "interval":
				interval = int(cfg.updateinterval.value)
				nowt = time.time()
				return int(nowt) + interval * 60 * 60
			if cfg.timetype.value == "fixed time":
				ftc = cfg.fixedtime.value
				now = time.localtime(time.time())
				fwt = int(time.mktime((
					now.tm_year,  # Anno corrente
					now.tm_mon,   # Mese corrente
					now.tm_mday,  # Giorno corrente
					ftc[0],       # Ora fissa configurata
					ftc[1],       # Minuti fissi configurati
					0,            # Secondi impostati a 0
					now.tm_wday,  # Giorno della settimana corrente
					now.tm_yday,  # Giorno dell'anno corrente
					now.tm_isdst  # Indicatore dell'ora legale
				)))
				return fwt
		else:
			return -1

	def update(self, constant=0):
		if cfg.autobouquetupdate.value is True:
			self.timer.stop()
			wake = self.get_wake_time()
			nowt = time.time()
			now = int(nowt)
			if wake > 0:
				if wake < now + constant:
					if cfg.timetype.value == "interval":
						interval = int(cfg.updateinterval.value)
						wake += interval * 60 * 60
					elif cfg.timetype.value == "fixed time":
						wake += 86400
				next = wake - int(nowt)
				if next > 3600:
					next = 3600
				if next <= 0:
					next = 60
				self.timer.startLongTimer(next)
			else:
				wake = -1
			return wake

	def on_timer(self):
		if cfg.autobouquetupdate.value is True:
			self.timer.stop()
			now = int(time.time())
			wake = now
			constant = 0
			if cfg.timetype.value == "fixed time":
				wake = self.get_wake_time()
			if abs(wake - now) < 60:
				try:
					self.startMain()
					constant = 60
					localtime = time.asctime(time.localtime(time.time()))
					cfg.last_update.value = localtime
					cfg.last_update.save()
				except Exception as e:
					print(e)
			self.update(constant)

	def startMain(self):
		from Plugins.Extensions.XCplugin.plugin import iptv_streamse
		globalsxp.STREAMS = iptv_streamse()
		if "exampleserver.com" not in globalsxp.STREAMS.xtream_e2portal_url:
			globalsxp.STREAMS.read_config()
			globalsxp.STREAMS.get_list(globalsxp.STREAMS.xtream_e2portal_url)
			if str(cfg.typelist.value) == "Combined Live/VOD":
				save_old()
			else:
				xc_maker_instance = xc_maker()
				xc_maker_instance.make_bouquet(_session)
		else:
			message = (_("First Select the list or enter it in Config"))
			web_info(message)


def autostart(reason, session=None, **kwargs):
	global _session
	_session = session
	if reason == 0 and _session is None:
		if session is not None:
			_session = session
			if globalsxp.autoStartTimer is None:
				globalsxp.autoStartTimer = AutoStartTimer(_session)
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