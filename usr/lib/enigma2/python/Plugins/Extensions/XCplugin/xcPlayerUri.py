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
#  update     29/12/2024                *
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
from . import _, version, isDreamOS
from .addons import Utils
from .addons.downloader import downloadWithProgress
from .addons.downloader2 import imagedownloadScreen
from .addons.modul import (
	cleanNames,
	clear_caches,
	copy_poster,
	EXTDOWN,
	getAspect,
	globalsxp,
	nextAR,
	prevAR,
	setAspect,
)
from .addons.NewOeSk import ctrlSkin
from .xcConfig import cfg
from .xcEpg import returnIMDB, show_more_infos
from .xcHelp import xc_help
from .xcSkin import skin_path, m3ulistxc, xcM3UList
from .xcTask import downloadJob

from Components.ActionMap import ActionMap, HelpableActionMap
from Components.config import config
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ProgressBar import ProgressBar
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Components.Sources.StaticText import StaticText
from Components.Task import job_manager as JobManager
from enigma import (
	ePicLoad,
	eServiceReference,
	eTimer,
	iPlayableService,
)
from os import (remove, system)
from os.path import splitext
from os.path import exists as file_exists

from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.TaskView import JobView
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Screens.InfoBarGenerics import (
	InfoBarAudioSelection,
	InfoBarMenu,
	InfoBarNotifications,
	InfoBarSeek,
	InfoBarSubtitleSupport,
)
from six.moves.urllib.parse import urlparse
from twisted.web.client import downloadPage

import codecs
import os
import re
import six
import time

ntimeout = float(cfg.timeout.value)


try:
	from Components.AVSwitch import AVSwitch
except ImportError:
	from Components.AVSwitch import eAVControl as AVSwitch


try:
	from Plugins.Extensions.SubsSupport import SubsSupport, SubsSupportStatus
except ImportError:
	class SubsSupport(object):
		def __init__(self, *args, **kwargs):
			pass

	class SubsSupportStatus(object):
		def __init__(self, *args, **kwargs):
			pass

try:
	from twisted.internet import ssl
	from twisted.internet._sslverify import ClientTLSOptions
	sslverify = True
except:
	sslverify = False
if sslverify:
	class SNIFactory(ssl.ClientContextFactory):
		def __init__(self, hostname=None):
			self.hostname = hostname

		def getContext(self):
			ctx = self._contextFactory(self.method)
			if self.hostname:
				ClientTLSOptions(self.hostname, ctx)
			return ctx


class IPTVInfoBarShowHide():
	""" InfoBar show/hide control, accepts toggleShow and hide actions, might start fancy animations. """
	STATE_HIDDEN = 0
	STATE_HIDING = 1
	STATE_SHOWING = 2
	STATE_SHOWN = 3
	FLAG_CENTER_DVB_SUBS = 2048
	skipToggleShow = False

	def __init__(self):
		self["ShowHideActions"] = ActionMap(["InfobarShowHideActions"], {
			"toggleShow": self.OkPressed,
			"hide": self.hide,
		}, 1)
		self.__event_tracker = ServiceEventTracker(screen=self, eventmap={
			iPlayableService.evStart: self.serviceStarted,
		})
		self.__state = self.STATE_SHOWN
		self.__locked = 0
		self.hideTimer = eTimer()
		try:
			self.hideTimer_conn = self.hideTimer.timeout.connect(self.doTimerHide)
		except:
			self.hideTimer.callback.append(self.doTimerHide)
		self.hideTimer.start(5000, True)
		self.onShow.append(self.__onShow)
		self.onHide.append(self.__onHide)

	def OkPressed(self):
		self.toggleShow()

	def __onShow(self):
		self.__state = self.STATE_SHOWN
		self.startHideTimer()

	def __onHide(self):
		self.__state = self.STATE_HIDDEN

	def serviceStarted(self):
		if self.execing:
			if config.usage.show_infobar_on_zap.value:
				self.doShow()

	def startHideTimer(self):
		if self.__state == self.STATE_SHOWN and not self.__locked:
			self.hideTimer.stop()
			idx = config.usage.infobar_timeout.index
			if idx:
				self.hideTimer.start(idx * 1500, True)

		elif hasattr(self, "pvrStateDialog"):
			self.hideTimer.stop()
			self.skipToggleShow = False

	def doShow(self):
		self.hideTimer.stop()
		self.show()
		self.startHideTimer()

	def doTimerHide(self):
		self.hideTimer.stop()
		if self.__state == self.STATE_SHOWN:
			self.hide()

	def toggleShow(self):
		if self.skipToggleShow:
			self.skipToggleShow = False
			return
		if self.__state == self.STATE_HIDDEN:
			self.show()
			self.hideTimer.stop()
		else:
			self.hide()
			self.startHideTimer()

	def lockShow(self):
		try:
			self.__locked += 1
		except:
			self.__locked = 0
		if self.execing:
			self.show()
			self.hideTimer.stop()
			self.skipToggleShow = False

	def unlockShow(self):
		try:
			self.__locked -= 1
		except:
			self.__locked = 0
		if self.__locked < 0:
			self.__locked = 0
		if self.execing:
			self.startHideTimer()


class xc_Player(Screen, InfoBarBase, IPTVInfoBarShowHide, InfoBarSeek, InfoBarAudioSelection, InfoBarSubtitleSupport, SubsSupportStatus, SubsSupport):
	STATE_IDLE = 0
	STATE_PLAYING = 1
	STATE_PAUSED = 2
	ENABLE_RESUME_SUPPORT = True
	ALLOW_SUSPEND = True
	screen_timeout = 5000

	def __init__(self, session, recorder_sref=None):
		global _session
		Screen.__init__(self, session)
		_session = session
		self.recorder_sref = None

		skin = os.path.join(skin_path, 'xc_Player.xml')
		with codecs.open(skin, "r", encoding="utf-8") as f:
			skin = f.read()
		self.skin = ctrlSkin('xc_Player', skin)

		InfoBarBase.__init__(self, steal_current_service=True)
		IPTVInfoBarShowHide.__init__(self)
		InfoBarSeek.__init__(self, actionmap="InfobarSeekActions")
		InfoBarAudioSelection.__init__(self)
		InfoBarSubtitleSupport.__init__(self)
		SubsSupport.__init__(self, searchSupport=True, embeddedSupport=True)
		SubsSupportStatus.__init__(self)

		try:
			self.init_aspect = int(getAspect())
		except:
			self.init_aspect = 0
		self.new_aspect = self.init_aspect

		self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
		self["state"] = Label("")
		self["cont_play"] = Label("")
		self["key_record"] = Label("Record")
		self["key_red"] = Label("Back to List")
		self["key_stop"] = Label("Stop")
		self["programm"] = Label("")
		self["poster"] = Pixmap()
		self.state = self.STATE_PLAYING
		self.cont_play = globalsxp.STREAMS.cont_play
		self.service = None
		self.recorder = False
		self.vod_url = None
		self.timeshift_url = None
		self.timeshift_title = None
		self.error_message = ""
		if recorder_sref is not None:
			self.recorder_sref = recorder_sref
			self.session.nav.playService(recorder_sref)
		else:
			self.index = globalsxp.STREAMS.list_index
		self.channelx = globalsxp.iptv_list_tmp[globalsxp.STREAMS.list_index]
		self.vod_url = self.channelx[4]
		self.titlex = self.channelx[1]
		self.descr = self.channelx[2]
		self.cover = self.channelx[3]
		self.pixim = self.channelx[7]
		self.__event_tracker = ServiceEventTracker(
			screen=self,
			eventmap={
				iPlayableService.evStart: self.__serviceStarted,
				iPlayableService.evSeekableStatusChanged: self.__seekableStatusChanged,
				iPlayableService.evTuneFailed: self.__evTuneFailed,
				iPlayableService.evUpdatedInfo: self.__evUpdatedInfo,
				iPlayableService.evEOF: self.__evEOF,
			},
		)
		self["actions"] = HelpableActionMap(
			self,
			"XCpluginActions", {
				"info": self.show_more_info,
				"epg": self.show_more_info,
				"0": self.av,
				"back": self.exitx,
				"home": self.exitx,
				"cancel": self.exitx,
				"up": self.prevVideo,
				"down": self.nextVideo,
				"next": self.nextVideo,
				"previous": self.prevVideo,
				"channelUp": self.prevAR,
				"channelDown": self.nextAR,
				"instantRecord": self.record,
				"rec": self.record,
				"blue": self.timeshift_autoplay,
				"tv": self.exitx,
				"stop": self.exitx,
				"2": self.restartVideo,
				# "help": self.xc_Help,
				"power": self.power_off
			},
			-1)
		self.onFirstExecBegin.append(self.play_vod)
		self.onShown.append(self.setCover)
		self.onShown.append(self.show_info)
		self.onPlayStateChanged.append(self.__playStateChanged)
		return

	def av(self):
		temp = int(getAspect())
		temp += 1
		if temp > 6:
			temp = 0
		self.new_aspect = temp
		setAspect(temp)

	def exitx(self):
		copy_poster()
		if cfg.stoplayer.value is True:
			globalsxp.STREAMS.play_vod = False
			self.session.nav.stopService()
			self.session.nav.playService(self.initialservice)
		if self.new_aspect != self.init_aspect:
			try:
				setAspect(self.init_aspect)
			except:
				pass
		self.close()

	def setCover(self):
		try:
			self.channelx = globalsxp.iptv_list_tmp[globalsxp.STREAMS.list_index]
			self['poster'].instance.setPixmapFromFile(globalsxp.piclogo[0])
			self.pixim = str(self.channelx[7])
			if (self.pixim != "" or self.pixim != "n/A" or self.pixim is not None or self.pixim != "null"):
				if six.PY3:
					self.pixim = six.ensure_binary(self.pixim)
				if self.pixim.startswith(b"https") and sslverify:
					parsed_uri = urlparse(self.pixim)
					domain = parsed_uri.hostname
					sniFactory = SNIFactory(domain)
					downloadPage(self.pixim, globalsxp.pictmp, sniFactory, timeout=ntimeout).addCallback(self.image_downloaded, globalsxp.pictmp).addErrback(self.downloadError)
				else:
					downloadPage(self.pixim, globalsxp.pictmp).addCallback(self.image_downloaded, globalsxp.pictmp).addErrback(self.downloadError)
			else:
				self.downloadError()
		except Exception as e:
			print(e)
			self.downloadError()

	def image_downloaded(self, data, pictmp):
		if file_exists(globalsxp.pictmp):
			try:
				self.decodeImage(globalsxp.pictmp)
			except Exception as e:
				print("* error ** %s" % e)

	def decodeImage(self, png):
		self["poster"].hide()
		if file_exists(png):
			size = self['poster'].instance.size()
			self.picload = ePicLoad()
			self.scale = AVSwitch().getFramebufferScale()
			self.picload.setPara([size.width(), size.height(), self.scale[0], self.scale[1], 0, 1, '#00000000'])
			if isDreamOS:
				self.picload.startDecode(png, False)
			else:
				self.picload.startDecode(png, 0, 0, False)
			ptr = self.picload.getData()
			if ptr is not None:
				self['poster'].instance.setPixmap(ptr)
				self['poster'].show()
			return

	def downloadError(self, error=""):
		try:
			if self["poster"].instance:
				self["poster"].instance.setPixmapFromFile(globalsxp.piclogo[0])
			print('error download: ', error)
		except Exception as e:
			print('error downloadError poster', e)

	def showAfterSeek(self):
		if isinstance(self, IPTVInfoBarShowHide):
			self.doShow()

	def timeshift_autoplay(self):
		if self.timeshift_url:
			try:
				globalsxp.eserv = int(cfg.services.value)
				self.reference = eServiceReference(globalsxp.eserv, 0, self.timeshift_url)
				self.reference.setName(self.timeshift_title)
				self.session.nav.playService(self.reference)
			except Exception as e:
				print(e)
		else:
			if self.cont_play:
				self.cont_play = False
				self["cont_play"].setText("Auto Play OFF")
				self.session.open(MessageBox, 'Continue play OFF', type=MessageBox.TYPE_INFO, timeout=3)
			else:
				self.cont_play = True
				self["cont_play"].setText("Auto Play ON")
				self.session.open(MessageBox, 'Continue play ON', type=MessageBox.TYPE_INFO, timeout=3)
			globalsxp.STREAMS.cont_play = self.cont_play

	def timeshift(self):
		if self.timeshift_url:
			try:
				globalsxp.eserv = int(cfg.services.value)
				self.reference = eServiceReference(globalsxp.eserv, 0, self.timeshift_url)
				self.reference.setName(self.timeshift_title)
				self.session.nav.playService(self.reference)
			except Exception as e:
				print(e)

	def autoplay(self):
		if self.cont_play:
			self.cont_play = False
			self["cont_play"].setText("Auto Play OFF")
			self.session.open(MessageBox, "Auto Play OFF", type=MessageBox.TYPE_INFO, timeout=3)

		else:
			self.cont_play = True
			self["cont_play"].setText("Auto Play ON")
			self.session.open(MessageBox, "Auto Play ON", type=MessageBox.TYPE_INFO, timeout=3)
		globalsxp.STREAMS.cont_play = self.cont_play

	def show_info(self):
		if globalsxp.STREAMS.play_vod is True:
			self["state"].setText(" PLAY     >")
		self.hideTimer.start(5000, True)
		if self.cont_play:
			self["cont_play"].setText("Auto Play ON")
		else:
			self["cont_play"].setText("Auto Play OFF")

	def restartVideo(self):
		try:
			index = globalsxp.STREAMS.list_index
			video_counter = len(globalsxp.iptv_list_tmp)
			if index < video_counter:
				if globalsxp.iptv_list_tmp[index][4] is not None:
					globalsxp.STREAMS.list_index = index
					self.player_helper()
		except Exception as e:
			print(e)

	def nextVideo(self):
		try:
			index = globalsxp.STREAMS.list_index + 1
			video_counter = len(globalsxp.iptv_list_tmp)
			if index < video_counter:
				if globalsxp.iptv_list_tmp[index][4] is not None:
					globalsxp.STREAMS.list_index = index
					self.player_helper()
		except Exception as e:
			print(e)

	def prevVideo(self):
		try:
			index = globalsxp.STREAMS.list_index - 1
			if index > -1:
				if globalsxp.iptv_list_tmp[index][4] is not None:
					globalsxp.STREAMS.list_index = index
					self.player_helper()
		except Exception as e:
			print(e)

	def player_helper(self):
		self.show_info()
		self.channelx = globalsxp.iptv_list_tmp[globalsxp.STREAMS.list_index]
		globalsxp.STREAMS.play_vod = False
		globalsxp.STREAMS.list_index_tmp = globalsxp.STREAMS.list_index
		self.setCover()
		self.play_vod()

	def record(self):
		try:
			if globalsxp.STREAMS.trial != '':
				self.session.open(MessageBox, 'Trialversion dont support this function', type=MessageBox.TYPE_INFO, timeout=10)
			else:
				try:
					self.session.open(MessageBox, 'BLUE = START PLAY RECORDED VIDEO', type=MessageBox.TYPE_INFO, timeout=5)
					self.session.nav.stopService()
					self['state'].setText('RECORD')
					pth = urlparse(self.vod_url).path
					ext = splitext(pth)[-1]
					if ext not in EXTDOWN:
						ext = '.avi'
					filename = cleanNames(self.titlex) + ext
					self.filename = filename.lower()
					cmd = "wget --no-cache --no-dns-cache -U %s -c '%s' -O '%s%s'" % ('Enigma2 - XC Forever Plugin', self.vod_url, str(globalsxp.Path_Movies), self.filename)
					if "https" in str(self.vod_url):
						cmd = "wget --no-check-certificate --no-cache --no-dns-cache -U %s -c '%s' -O '%s%s'" % ('Enigma2 - XC Forever Plugin', self.vod_url, str(globalsxp.Path_Movies), self.filename)
					self.timeshift_url = globalsxp.Path_Movies + self.filename
					JobManager.AddJob(downloadJob(self, cmd, self.timeshift_url, self.titlex))
					self.createMetaFile(self.filename, self.filename)
					self.LastJobView()
					self.timeshift_title = '[REC] ' + self.titlex
					self.recorder = True
				except Exception as e:
					print('error record x: ', e)
		except Exception as e:
			print('error record: ', e)

	def createMetaFile(self, filename, filmtitle):
		try:
			serviceref = eServiceReference(4097, 0, self.timeshift_url)
			with open('%s/%s.meta' % (globalsxp.Path_Movies, filename), 'w') as f:
				f.write('%s\n%s\n%s\n%i\n' % (serviceref.toString(), filmtitle, "", time.time()))
		except Exception as e:
			print('ERROR metaFile', e)

	def LastJobView(self):
		currentjob = None
		for job in JobManager.getPendingJobs():
			currentjob = job
		if currentjob is not None:
			self.session.open(JobView, currentjob)
		return

	def __evUpdatedInfo(self):
		self.timerCache = eTimer()
		try:
			self.timerCache.stop()
		except:
			pass
		try:
			self.timerCache.callback.append(clear_caches)
		except:
			self.timerCache_conn = self.timerCache.timeout.connect(clear_caches)
		self.timerCache.start(600000, False)

	def __evTuneFailed(self):
		try:
			self.session.nav.stopService()
		except:
			pass

	def __evEOF(self):
		if self.cont_play:
			self.restartVideo()
		else:
			return

	def __seekableStatusChanged(self):
		print("seekable status changed!")

	def __serviceStarted(self):
		self["state"].setText(" PLAY     >")
		self["cont_play"].setText("Auto Play OFF")
		self.state = self.STATE_PLAYING

	def doEofInternal(self, playing):
		if not self.execing:
			return
		if not playing:
			return
		print("doEofInternal EXIT OR NEXT")
		self.session.open(MessageBox, "NO VIDEOSTREAM FOUND", type=MessageBox.TYPE_INFO, timeout=3)
		self.close()

	def power_off(self):
		self.close(1)

	def nextAR(self):
		message = nextAR()
		self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=3)

	def prevAR(self):
		message = prevAR()
		self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=3)

	def show_more_info(self):
		index = globalsxp.STREAMS.list_index
		if self.vod_url is not None:
			name = str(self.channelx[1])
			show_more_infos(name, index, _session)

	def __playStateChanged(self, state):
		self.hideTimer.start(5000, True)
		text = " " + self.seekstate[3]
		if self.seekstate[3] == ">":
			text = " PLAY     >"
		if self.seekstate[3] == "||":
			text = "PAUSE   ||"
		if self.seekstate[3] == ">> 2x":
			text = "        x2         >>"
		if self.seekstate[3] == ">> 4x":
			text = "        x4         >>"
		if self.seekstate[3] == ">> 8x":
			text = "        x8         >>"
		self["state"].setText(text)

	def play_vod(self):
		self.channelx = globalsxp.iptv_list_tmp[globalsxp.STREAMS.list_index]
		self.vod_url = self.channelx[4]
		self.titlex = self.channelx[1]
		self.descr = self.channelx[2]
		if self.descr != '' or self.descr is not None:
			text_clear = str(self.descr)
			self["programm"].setText(text_clear)
		try:
			if self.vod_url is not None:
				print('MOVIE --->', self.vod_url)
				globalsxp.STREAMS.play_vod = True
				self.session.nav.stopService()
				globalsxp.eserv = int(cfg.services.value)
				self.reference = eServiceReference(globalsxp.eserv, 0, self.vod_url)
				self.reference.setName(self.titlex)
				self.session.nav.playService(self.reference)
			else:
				if self.error_message:
					self.session.open(MessageBox, self.error_message, type=MessageBox.TYPE_INFO, timeout=3)
				else:
					self.session.open(MessageBox, "NO VIDEOSTREAM FOUND", type=MessageBox.TYPE_INFO, timeout=3)

				self.close()
		except Exception as e:
			print(e)


class nIPTVplayer(Screen, InfoBarBase, IPTVInfoBarShowHide, InfoBarSeek, InfoBarAudioSelection, InfoBarSubtitleSupport, SubsSupportStatus, SubsSupport):
	STATE_IDLE = 0
	STATE_PLAYING = 1
	STATE_PAUSED = 2
	ENABLE_RESUME_SUPPORT = True
	ALLOW_SUSPEND = True

	def __init__(self, session, recorder_sref=None):
		Screen.__init__(self, session)
		global _session
		_session = session
		self.recorder_sref = None
		skin = os.path.join(skin_path, 'xc_iptv_player.xml')
		with codecs.open(skin, "r", encoding="utf-8") as f:
			skin = f.read()
		self.skin = ctrlSkin('nIPTVplayer', skin)
		InfoBarBase.__init__(self, steal_current_service=True)
		IPTVInfoBarShowHide.__init__(self)
		InfoBarSeek.__init__(self, actionmap="InfobarSeekActions")
		InfoBarAudioSelection.__init__(self)
		InfoBarSubtitleSupport.__init__(self)
		SubsSupport.__init__(self, searchSupport=True, embeddedSupport=True)
		SubsSupportStatus.__init__(self)

		try:
			self.init_aspect = int(getAspect())
		except:
			self.init_aspect = 0
		self.new_aspect = self.init_aspect

		self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
		self["channel_name"] = Label("")
		self["programm"] = Label("")
		self["poster"] = Pixmap()
		globalsxp.STREAMS.play_vod = False
		self.channel_list = globalsxp.iptv_list_tmp
		self.index = globalsxp.STREAMS.list_index

		self["actions"] = HelpableActionMap(self, "XCpluginActions", {
			"info": self.show_more_info,
			"0": self.av,
			"home": self.exitx,
			"cancel": self.exitx,
			"stop": self.exitx,
			"help": self.xc_Help,
			"up": self.prevChannel,
			"down": self.nextChannel,
			"next": self.nextChannel,
			"previous": self.prevChannel,
			"channelUp": self.nextAR,
			"channelDown": self.prevAR,
			"power": self.power_off}, -1)
		self.onFirstExecBegin.append(self.play_channel)

	def av(self):
		temp = int(getAspect())
		temp += 1
		if temp > 6:
			temp = 0
		self.new_aspect = temp
		setAspect(temp)

	def nextAR(self):
		message = nextAR()
		self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=3)

	def prevAR(self):
		message = prevAR()
		self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=3)

	def exitx(self):
		copy_poster()
		if cfg.stoplayer.value is True:
			globalsxp.STREAMS.play_vod = False
			self.session.nav.stopService()
			self.session.nav.playService(self.initialservice)
		if self.new_aspect != self.init_aspect:
			try:
				setAspect(self.init_aspect)
			except:
				pass
		self.close()

	def power_off(self):
		self.close(1)

	def play_channel(self):
		try:
			self.channely = globalsxp.iptv_list_tmp[self.index]
			self["channel_name"].setText(self.channely[1])
			self.titlex = self.channely[1]
			self.descr = self.channely[2]
			self.cover = self.channely[3]
			self.live_url = self.channely[4]
			text_clear = ""
			if self.descr != '' or self.descr is not None:
				text_clear = str(self.descr)
			self["programm"].setText(text_clear)
			try:
				if (self.cover != "" or self.cover != "n/A" or self.cover is None or self.cover != "null"):
					if self.cover.find("http") == -1:
						self.downloadError()
					else:
						self.cover = six.ensure_binary(self.cover)
						if self.cover.startswith(b"https") and sslverify:
							parsed_uri = urlparse(self.cover)
							domain = parsed_uri.hostname
							sniFactory = SNIFactory(domain)
							downloadPage(self.cover, globalsxp.pictmp, sniFactory, timeout=ntimeout).addCallback(self.image_downloaded, globalsxp.pictmp).addErrback(self.downloadError)
						else:
							downloadPage(self.cover, globalsxp.pictmp).addCallback(self.image_downloaded, globalsxp.pictmp).addErrback(self.downloadError)
			except Exception as e:
				print(e)
			try:
				if cfg.LivePlayer.value is True:
					globalsxp.eserv = int(cfg.live.value)
				if str(splitext(self.live_url)[-1]) == ".m3u8":
					if globalsxp.eserv == 1:
						globalsxp.eserv = 4097

				self.session.nav.stopService()
				if self.live_url != "" and self.live_url is not None:
					sref = eServiceReference(globalsxp.eserv, 0, self.live_url)
					sref.setName(str(self.titlex))
					try:
						globalsxp.STREAMS.play_vod = True
						self.session.nav.playService(sref)
					except Exception as e:
						print(e)
			except Exception as e:
				print(e)
		except Exception as e:
			print(e)

	def nextChannel(self):
		index = self.index
		index += 1
		if index == len(self.channel_list):
			index = 0
		if self.channel_list[index][4] is not None:
			self.index = index
			globalsxp.STREAMS.list_index = self.index
			globalsxp.STREAMS.list_index_tmp = self.index
			self.play_channel()

	def prevChannel(self):
		index = self.index
		index -= 1
		if index == -1:
			index = len(self.channel_list) - 1
		if self.channel_list[index][4] is not None:
			self.index = index
			globalsxp.STREAMS.list_index = self.index
			globalsxp.STREAMS.list_index_tmp = self.index
			self.play_channel()

	def xc_Help(self):
		self.session.open(xc_help)

	def show_more_info(self):
		selected_channel = globalsxp.iptv_list_tmp[self.index]
		if selected_channel:
			name = str(self.titlex)
			show_more_infos(name, self.index, _session)

	def image_downloaded(self, data, pictmp):
		if file_exists(globalsxp.pictmp):
			try:
				self.decodeImage(globalsxp.pictmp)
			except Exception as e:
				print("* error ** %s" % e)
				pass
			except:
				pass

	def decodeImage(self, png):
		self["poster"].hide()
		if file_exists(png):
			size = self['poster'].instance.size()
			self.picload = ePicLoad()
			self.scale = AVSwitch().getFramebufferScale()
			self.picload.setPara([size.width(), size.height(), self.scale[0], self.scale[1], 0, 1, '#00000000'])
			# _l = self.picload.PictureData.get()
			# del _l[:]
			if isDreamOS:
				self.picload.startDecode(png, False)
			else:
				self.picload.startDecode(png, 0, 0, False)

			ptr = self.picload.getData()
			if ptr is not None:
				self['poster'].instance.setPixmap(ptr)
				self['poster'].show()
			return

	def downloadError(self, error=""):
		try:
			if self["poster"].instance:
				self["poster"].instance.setPixmapFromFile(globalsxp.piclogo[0])
		except Exception as e:
			print('error poster', e)


class xc_Play(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		skin = os.path.join(skin_path, 'xc_Play.xml')
		with codecs.open(skin, "r", encoding="utf-8") as f:
			skin = f.read()
		self.skin = ctrlSkin('xc_Play', skin)
		try:
			Screen.setTitle(self, _('%s') % 'PLAYER MENU')
		except:
			try:
				self.setTitle(_('%s') % 'PLAYER MENU')
			except:
				pass
		self.list = []
		try:
			self.init_aspect = int(getAspect())
		except:
			self.init_aspect = 0
		self.new_aspect = self.init_aspect
		self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
		self["list"] = xcM3UList([])
		self.downloading = False
		self.download = None
		self.name = globalsxp.Path_Movies
		self["path"] = Label(_("Put .m3u Files in Folder %s") % globalsxp.Path_Movies)
		self["version"] = Label(version)
		self["Text"] = Label("M3u Utility")
		self['progress'] = ProgressBar()
		self['progresstext'] = StaticText()
		self["progress"].hide()
		self['status'] = Label()
		self["key_red"] = Label(_("Back"))
		self["key_green"] = Label(_("Remove"))
		self["key_yellow"] = Label(_("Export") + _(" Bouquet"))
		self["key_blue"] = Label(_("Download") + _(" M3u"))
		self["actions"] = HelpableActionMap(self, "XCpluginActions", {
			"home": self.cancel,
			"green": self.message1,
			"yellow": self.message2,
			"blue": self.message3,
			"cancel": self.cancel,
			"ok": self.runList}, -2)
		self.onFirstExecBegin.append(self.openList)
		self.onLayoutFinish.append(self.layoutFinished)

	def openList(self):
		self.names = []
		self.Movies = []
		path = self.name
		AA = ['.m3u']
		for root, dirs, files in os.walk(path):
			for name in files:
				for x in AA:
					if x not in name:
						continue
					self.names.append(name)
					self.Movies.append(root + name)
		m3ulistxc(self.names, self['list'])

	def layoutFinished(self):
		pass

	def refreshmylist(self):
		self.names = []
		self.list = self.names
		self.names[:] = [0, 0]
		self.openList()

	def runList(self):
		idx = self["list"].getSelectionIndex()
		if idx is None or idx < 0 or idx >= len(self.names):
			return
		else:
			name = self.Movies[idx]
			if ".m3u" in name:
				self.session.open(xc_M3uPlay, name)
				return
			else:
				name = self.names[idx]
				sref = eServiceReference(4097, 0, name)
				sref.setName(name)
				self.session.openWithCallback(self.backToIntialService, xc_Player, sref)

	def backToIntialService(self, ret=None):
		if cfg.stoplayer.value is True:
			globalsxp.STREAMS.play_vod = False
			self.session.nav.stopService()
			self.session.nav.playService(self.initialservice)
		if self.new_aspect != self.init_aspect:
			try:
				setAspect(self.init_aspect)
			except:
				pass

	def cancel(self):
		self.close()

	def message1(self, answer=None):
		idx = self["list"].getSelectionIndex()
		if idx is None or idx < 0 or idx >= len(self.names):
			return
		dom = self.Movies[idx]
		if answer is None:
			self.session.openWithCallback(self.message1, MessageBox, _("Do you want to remove: %s ?") % dom)
		elif answer:
			try:
				remove(dom)
				self.session.open(MessageBox, dom + _("   has been successfully deleted\nwait time to refresh the list..."), MessageBox.TYPE_INFO, timeout=5)
				del self.names[idx]
				self.refreshmylist()
			except OSError as error:
				print("File path can not be removed", error)
				self.session.open(MessageBox, dom + _(" not exist!"), MessageBox.TYPE_INFO, timeout=5)
		else:
			return

	def message3(self, answer=None):
		if "exampleserver.com" not in globalsxp.STREAMS.xtream_e2portal_url:
			if self.downloading is True:
				self.session.open(MessageBox, _("Wait... downloading in progress ..."), MessageBox.TYPE_INFO, timeout=5)
				return
			if answer is None:
				self.session.openWithCallback(self.message3, MessageBox, _("Download M3u File?"))
			elif answer:
				self.downloading = False
				if "exampleserver.com" not in globalsxp.STREAMS.xtream_e2portal_url:
					self.urlm3u = globalsxp.urlinfo.replace("enigma2.php", "get.php")
					self.urlm3u = self.urlm3u + '&type=m3u_plus&output=ts'
					self.m3ulnk = ('wget %s -O ' % self.urlm3u)
					self.name_m3u = str(cfg.user.value)
					self.in_tmp = globalsxp.Path_Movies + self.name_m3u + '.m3u'
					if file_exists(self.in_tmp):
						cmd = 'rm -f ' + self.in_tmp
						system(cmd)
					if cfg.pdownmovie.value == "Direct":
						self.downloading = True
						self.downloadz()
					else:
						try:
							self.downloading = True
							self.download = downloadWithProgress(self.urlm3u, self.in_tmp)
							self.download.addProgress(self.downloadProgress)
							self.download.start().addCallback(self.check).addErrback(self.showError)
						except Exception as e:
							print(e)
				else:
					self.downloading = False
					self.session.open(MessageBox, _('No Server Configured to Download!!!'), MessageBox.TYPE_WARNING)
					pass
				self.refreshmylist()
			else:
				self.refreshmylist()
				return
		else:
			self.refreshmylist()

	def downloadz(self):
		if self.downloading is True:
			from .downloader2 import imagedownloadScreen
			Utils.OnclearMem()
			self.downloading = False
			self.session.open(imagedownloadScreen, self.name_m3u, self.in_tmp, self.urlm3u)
			self.refreshmylist()
		else:
			return

	def downloadProgress(self, recvbytes, totalbytes):
		self["progress"].show()
		if totalbytes > 0:
			self['progress'].value = int(100 * recvbytes // float(totalbytes))
			self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (
				recvbytes // 1024, totalbytes // 1024, 100 * recvbytes // float(totalbytes))
		else:
			self['progress'].value = 0
			self['progresstext'].text = '0 of 0 kBytes (0.00%%)'

	def check(self, fplug):
		checkfile = self.in_tmp
		if file_exists(checkfile):
			self.downloading = False
			self['status'].setText(_('Download Finished!'))
			self['progresstext'].text = ''
			self.progclear = 0
			self['progress'].setValue(self.progclear)
			self["progress"].hide()
			self.refreshmylist()

	def showError(self, error):
		self.downloading = False
		self.refreshmylist()

	def remove_target(self):
		try:
			if file_exists(self.in_tmp):
				remove(self.in_tmp)
		except:
			pass

	def abort(self, answer=True):
		if answer is False:
			return
		if not self.downloading:
			self.downloading = False
			self.close()
		elif self.download is not None:
			self.download.stop
			info = _('Aborting...')
			self['status'].setText(info)
			self.remove_target()
			self.downloading = False
			self.close()
		else:
			self.downloading = False
			self.close()
		return

	def message2(self):
		idx = self["list"].getSelectionIndex()
		if idx is None or idx < 0 or idx >= len(self.names):
			return
		dom = self.names[idx]
		name = self.Movies[idx]
		if ".m3u" in name:
			idx = self["list"].getSelectionIndex()
			self.session.openWithCallback(self.convert, MessageBox, _("Do you want to Convert %s to favorite .tv ?") % dom, MessageBox.TYPE_YESNO, timeout=15, default=True)
		else:
			return

	def convert(self, result):
		if result:
			self.convert_bouquet()
			return
		else:
			return

	def convert_bouquet(self):
		idx = self["list"].getSelectionIndex()
		if idx is None or idx < 0 or idx >= len(self.names):
			return
		else:
			name = os.path.join(globalsxp.Path_Movies, self.names[idx])
			namel = self.names[idx]
			xcname = "userbouquet.%s.tv" % namel.replace(".m3u", "").replace(" ", "")
			desk_tmp = ""
			in_bouquets = False
			bouquet_path = "/etc/enigma2/%s" % xcname
			if file_exists(bouquet_path):
				remove(bouquet_path)
			with open(bouquet_path, "w") as outfile:
				outfile.write("#NAME %s\r\n" % namel.replace(".m3u", "").replace(" ", "").capitalize())
				with open(name, "r") as infile:
					for line in infile:
						if line.startswith("http://") or line.startswith("https://"):
							outfile.write('#SERVICE 4097:0:1:0:0:0:0:0:0:0:%s\r\n' % line.replace(':', '%3a'))
							outfile.write("#DESCRIPTION %s\r\n" % desk_tmp)
						elif line.startswith("#EXTINF"):
							desk_tmp = line.split(",")[-1].strip()
						elif "<stream_url><![CDATA" in line:
							globalsxp.stream_url = line.split("[")[-1].split("]")[0].replace(":", "%3a")
							outfile.write('#SERVICE 4097:0:1:0:0:0:0:0:0:0:%s\r\n' % globalsxp.stream_url)
							outfile.write("#DESCRIPTION %s\r\n" % desk_tmp)
						elif "<title>" in line:
							if "<![CDATA[" in line:
								desk_tmp = line.split("[")[-1].split("]")[0].strip()
							else:
								desk_tmp = line.split("<")[1].split(">")[1].strip()

			self.session.open(MessageBox, _("Check on favorites lists..."), MessageBox.TYPE_INFO, timeout=5)
			with open("/etc/enigma2/bouquets.tv", "r") as bouquets_file:
				for line in bouquets_file:
					if xcname in line:
						in_bouquets = True
						break
			if not in_bouquets:
				with open("/etc/enigma2/bouquets.tv", "a") as bouquets_file:
					bouquets_file.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % xcname)
			self.session.open(MessageBox, _("Reload Playlists in progress...") + "\n\n\n" + _("wait please..."), MessageBox.TYPE_INFO, timeout=5)
			Utils.ReloadBouquets()


class xc_M3uPlay(Screen):
	def __init__(self, session, name):
		Screen.__init__(self, session)
		skin = os.path.join(skin_path, 'xc_M3uPlay.xml')
		with codecs.open(skin, "r", encoding="utf-8") as f:
			skin = f.read()
		self.skin = ctrlSkin('xc_M3uPlay', skin)
		try:
			Screen.setTitle(self, _('%s') % 'M3U UTILITY MENU')
		except:
			try:
				self.setTitle(_('%s') % 'M3U UTILITY MENU')
			except:
				pass
		self.name = name
		self.downloading = False
		self.download = None
		globalsxp.search_ok = False
		self.search = ''
		self["list"] = xcM3UList([])
		self["version"] = Label(version)
		self["key_red"] = Label(_("Back"))
		self["key_green"] = Label(_("Reload"))
		self["key_yellow"] = Label(_("Download"))
		self["key_blue"] = Label(_("Search"))
		self['status'] = Label()
		self['progress'] = ProgressBar()
		self['progresstext'] = StaticText()
		self["progress"].hide()
		self["actions"] = HelpableActionMap(self, "XCpluginActions", {
			"home": self.cancel,
			"cancel": self.cancel,
			"ok": self.runChannel,
			"green": self.playList,
			"yellow": self.runRec,
			"blue": self.search_m3u,
			"rec": self.runRec,
			"instantRecord": self.runRec,
			"ShortRecord": self.runRec}, -2)
		self["live"] = Label("")
		self.onLayoutFinish.append(self.playList)

	def search_m3u(self):
		self.session.openWithCallback(
			self.filterM3u,
			VirtualKeyBoard,
			title=("Filter this category..."),
			text=self.search)

	def filterM3u(self, result):
		if result:
			self.names = []
			self.urls = []
			search = result
			try:
				if file_exists(self.name):
					fpage = ''
					try:
						with codecs.open(str(self.name), "r", encoding="utf-8") as f:
							fpage = f.read()
					except:
						pass
					regexcat = "EXTINF.*?,(.*?)\\n(.*?)\\n"
					match = re.compile(regexcat, re.DOTALL).findall(fpage)
					for name, url in match:
						if str(search).lower() in name.lower():
							globalsxp.search_ok = True
							url = url.replace(" ", "").replace("\\n", "")
							self.names.append(str(name))
							self.urls.append(str(url))
					if globalsxp.search_ok is True:
						m3ulistxc(self.names, self["list"])
						self["live"].setText(str(len(self.names)) + " Stream")
					else:
						globalsxp.search_ok = False
						self.resetSearch()
			except:
				pass
		else:
			self.playList()

	def refreshmylist(self):
		self.names = []
		self.list = self.names
		self.playList()

	def playList(self):
		globalsxp.search_ok = False
		self.names = []
		self.urls = []
		self.pics = []
		pic = globalsxp.pictmp
		try:
			if file_exists(self.name):
				fpage = ''
				try:
					with codecs.open(self.name, "r", encoding="utf-8") as f:
						fpage = f.read()
				except Exception as e:
					print("Errore durante la lettura del file:", e)
					return
				if "#EXTM3U" in fpage and 'tvg-logo' in fpage:
					regexcat = r'EXTINF.*?tvg-logo="(.*?)".*?,(.*?)\n(.*?)\n'
					match = re.compile(regexcat, re.DOTALL).findall(fpage)
					for pic, name, url in match:
						url = url.replace(' ', '').replace('\n', '')
						self.names.append(str(name))
						self.urls.append(str(url))
						self.pics.append(pic)
				else:
					regexcat = r'#EXTINF.*?,(.*?)\n(.*?)\n'
					match = re.compile(regexcat, re.DOTALL).findall(fpage)
					for name, url in match:
						url = url.replace(' ', '').replace('\n', '')
						self.names.append(str(name))
						self.urls.append(str(url))
						self.pics.append(pic)
				m3ulistxc(self.names, self['list'])
				self["live"].setText('N.' + str(len(self.names)) + " Stream")
			else:
				self.session.open(MessageBox, _('File Unknow!!!'), MessageBox.TYPE_INFO, timeout=5)
		except Exception as e:
			print('Error processing M3U file:', e)

	def runChannel(self):
		idx = self["list"].getSelectionIndex()
		if idx is None or idx < 0 or idx >= len(self.names):
			return
		else:
			name = self.names[idx]
			url = self.urls[idx]
			self.session.open(M3uPlay2, name, url)
		return

	def runRec(self, answer=None):
		self.downloading = False
		idx = self["list"].getSelectionIndex()
		if idx is None or idx < 0 or idx >= len(self.names):
			return
		else:
			self.name_m3u = self.names[idx]
			self.urlm3u = self.urls[idx]
			pth = urlparse(self.urlm3u).path
			ext = splitext(pth)[1]
			if ext not in EXTDOWN:
				ext = '.avi'
			if ext in EXTDOWN or ext == '.avi':
				if answer is None:
					self.session.openWithCallback(self.runRec, MessageBox, _("DOWNLOAD VIDEO?\n%s") % self.name_m3u)
				elif answer:
					cleanName = cleanNames(self.name_m3u)
					filename = cleanName + ext
					self.in_tmp = globalsxp.Path_Movies + filename.lower()
					if file_exists(self.in_tmp):
						cmd = 'rm -f ' + self.in_tmp
						system(cmd)
					if cfg.pdownmovie.value == "Direct":
						self.downloading = True
						self.downloadz()
					else:
						try:
							self.downloading = True
							self.download = downloadWithProgress(self.urlm3u, self.in_tmp)
							self.download.addProgress(self.downloadProgress)
							self.download.start().addCallback(self.check).addErrback(self.showError)  # Usare le nuove funzioni
						except Exception as e:
							self.downloading = False
							print("Error during download:", e)
				else:
					return
			else:
				self.session.open(MessageBox, _("Only VOD Movie allowed!!!"), MessageBox.TYPE_INFO, timeout=5)

	def downloadz(self):
		if self.downloading:
			Utils.OnclearMem()
			self.session.open(imagedownloadScreen, self.name_m3u, self.in_tmp, self.urlm3u)
		else:
			print("Download not started")
			return

		self.downloading = False
		self.refreshmylist()

	def downloadProgress(self, recvbytes, totalbytes):
		self["progress"].show()
		if totalbytes > 0:
			self['progress'].value = int(100 * recvbytes // float(totalbytes))
			self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (
				recvbytes // 1024, totalbytes // 1024, 100 * recvbytes // float(totalbytes))
		else:
			self['progress'].value = 0
			self['progresstext'].text = '0 of 0 kBytes (0.00%%)'

	def check(self, fplug):
		checkfile = self.in_tmp
		if file_exists(checkfile):
			self.downloading = False
			self['status'].setText(_('Download Finished!'))
			self['progresstext'].setText('')
			self.progclear = 0
			self['progress'].setValue(self.progclear)
			self.refreshmylist()

	def showError(self, error):
		self.downloading = False
		print("download error =", error)

	def resetSearch(self):
		globalsxp.re_search = False
		if len(self.names):
			for x in self.names:
				del x
		self.playList()

	def cancel(self):
		if globalsxp.search_ok is True:
			self.resetSearch()
		else:
			self.close()

	def abort(self, answer=True):
		if answer is False:
			return
		if not self.downloading:
			self.downloading = False
			self.close()
		elif self.download is not None:
			self.downloading = False
			self.download.stop
			info = _('Aborting...')
			self['status'].setText(info)
			self.remove_target()
			self.close()
		else:
			self.downloading = False
			self.close()

	def remove_target(self):
		try:
			if file_exists(self.name_m3u):
				remove(self.name_m3u)
		except:
			pass


class M3uPlay2(Screen, InfoBarMenu, InfoBarBase, InfoBarSeek, InfoBarNotifications, InfoBarAudioSelection, IPTVInfoBarShowHide, InfoBarSubtitleSupport):
	STATE_IDLE = 0
	STATE_PLAYING = 1
	STATE_PAUSED = 2
	ENABLE_RESUME_SUPPORT = True
	ALLOW_SUSPEND = True

	def __init__(self, session, name, url):
		Screen.__init__(self, session)
		self.skinName = 'MoviePlayer'
		InfoBarMenu.__init__(self)
		InfoBarNotifications.__init__(self)
		InfoBarBase.__init__(self, steal_current_service=True)
		IPTVInfoBarShowHide.__init__(self)
		InfoBarSubtitleSupport.__init__(self)
		InfoBarSeek.__init__(self, actionmap='InfobarSeekActions')
		InfoBarAudioSelection.__init__(self)

		try:
			self.init_aspect = int(getAspect())
		except:
			self.init_aspect = 0
		self.new_aspect = self.init_aspect

		self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
		self.url = url.replace(':', '%3a')
		self.name = name
		self.state = self.STATE_PLAYING
		self['actions'] = ActionMap([
			'MoviePlayerActions',
			'MovieSelectionActions',
			'MediaPlayerActions',
			'EPGSelectActions',
			'MediaPlayerSeekActions',
			'SetupActions',
			'ColorActions',
			'InfobarShowHideActions',
			'InfobarActions',
			'DirectionActions',
			'InfobarSeekActions'], {
			'leavePlayer': self.cancel,
			'epg': self.showIMDB,
			'info': self.cicleStreamType,
			'tv': self.cicleStreamType,
			'stop': self.leavePlayer,
			'cancel': self.cancel,
			'back': self.cancel},
			-1)

		self.onFirstExecBegin.append(self.cicleStreamType)
		self.onClose.append(self.cancel)

	def showIMDB(self):
		text_clear = self.name
		if returnIMDB(text_clear) is True:
			print('M3uPlay2 show imdb/tmdb')

	def openPlay(self, servicetype, url):
		ref = "{0}:0:1:0:0:0:0:0:0:0:{1}:{2}".format(servicetype, url.replace(":", "%3a"), self.name.replace(":", "%3a"))
		sref = eServiceReference(ref)
		globalsxp.STREAMS.play_vod = True
		sref.setName(self.name)
		self.session.nav.stopService()
		self.session.nav.playService(sref)

	def cicleStreamType(self):
		from itertools import cycle, islice
		self.servicetype = int(cfg.services.value)  # '4097'
		url = str(self.url)
		if str(splitext(self.url)[-1]) == ".m3u8":
			if self.servicetype == "1":
				self.servicetype = "4097"
		currentindex = 0
		streamtypelist = ["4097"]
		if file_exists("/usr/bin/gstplayer"):
			streamtypelist.append("5001")
		if file_exists("/usr/bin/exteplayer3"):
			streamtypelist.append("5002")
		if isDreamOS:
			streamtypelist.append("8193")
		for index, item in enumerate(streamtypelist, start=0):
			if str(item) == str(self.servicetype):
				currentindex = index
				break
		nextStreamType = islice(cycle(streamtypelist), currentindex + 1, None)
		self.servicetype = int(next(nextStreamType))
		self.openPlay(self.servicetype, url)

	def doEofInternal(self, playing):
		if not self.execing:
			return
		if not playing:
			return
		print("doEofInternal EXIT OR NEXT")
		self.session.open(MessageBox, "NO VIDEOSTREAM FOUND", type=MessageBox.TYPE_INFO, timeout=3)
		self.close()

	def __evEOF(self):
		self.end = True

	def showVideoInfo(self):
		if self.shown:
			self.hideInfobar()
		if self.infoCallback is not None:
			self.infoCallback()
		return

	def showAfterSeek(self):
		if isinstance(self, IPTVInfoBarShowHide):
			self.doShow()

	def cancel(self):
		if file_exists('/tmp/hls.avi'):
			remove('/tmp/hls.avi')
		if cfg.stoplayer.value is True:
			globalsxp.STREAMS.play_vod = False
			self.session.nav.stopService()
			self.session.nav.playService(self.initialservice)
		if self.new_aspect != self.init_aspect:
			try:
				setAspect(self.init_aspect)
			except:
				pass
		self.close()

	def leavePlayer(self):
		self.cancel()

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
