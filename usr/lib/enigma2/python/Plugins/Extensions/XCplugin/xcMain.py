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
from json import dump, load
from os import remove, stat, system, makedirs
from os.path import exists as file_exists, join, splitext, normpath
from re import DOTALL, compile
from shutil import copy
from socket import setdefaulttimeout
from time import gmtime, strftime, time
import sys

# Third-party imports
# from requests import get, codes
from six import PY3, ensure_binary, text_type
from six.moves.urllib.parse import urlparse
from twisted.web.client import downloadPage

# Enigma2 imports
from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from Components.Task import job_manager as JobManager
from Components.config import config
from Screens.MessageBox import MessageBox
from Screens.MovieSelection import MovieSelection
from Screens.Screen import Screen
from Screens.Standby import Standby
from Screens.TaskView import JobView
from Screens.VirtualKeyBoard import VirtualKeyBoard
from enigma import (
    eListboxPythonMultiContent,
    ePicLoad,
    eServiceReference,
    eTimer,
    gFont,
)
from enigma import ePoint, eSize
from Tools.LoadPixmap import LoadPixmap

# Local package imports
from . import (
    _,
    plugin_path,
    retTest,
    version,
)
from .addons import Utils
from .addons.NewOeSk import ctrlSkin
from .addons.downloader2 import imagedownloadScreen
from .addons.modul import (
    EXTDOWN,
    cleanNames,
    copy_poster,
    globalsxp,
)
from .xcConfig import cfg
from .xcEpg import show_more_infos
from .xcHelp import xc_help
from .xcPlayerUri import (
    AVSwitch,
    SNIFactory,
    aspect_manager,
    nIPTVplayer,
    sslverify,
    xc_Player,
)
from .xcSkin import (
    BLOCK_H,
    FONT_0,
    FONT_1,
    channelEntryIPTVplaylist,
    skin_path,
)
from .xcTask import downloadJob, xc_StreamTasks

# global fixed
_session = None
globalsxp.infoname = str(cfg.infoname.value)
globalsxp.Path_Movies = str(cfg.pthmovie.value)  # + "/"
globalsxp.Path_Movies2 = globalsxp.Path_Movies
globalsxp.piclogo = join(plugin_path, 'skin/fhd/iptvlogo.jpg'),
globalsxp.pictmp = "/tmp/poster.jpg"
input_file = '/tmp/mydata.json'
ntimeout = float(cfg.timeout.value)
output_file = '/tmp/mydata2.json'
setdefaulttimeout(5)


if PY3:
    unicode = text_type


def to_bytes(s):
    if sys.version_info[0] >= 3:
        if isinstance(s, str):
            return s.encode("utf-8")
        return s
    else:
        return s


class xc_Main(Screen):
    def __init__(self, session):
        global _session
        global channel_list2
        _session = session
        Screen.__init__(self, session)
        skin = join(skin_path, 'xc_Main.xml')
        if cfg.screenxl.value:
            skin = join(skin_path, 'xc_Mainxl.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            skin = f.read()
        self.skin = ctrlSkin('xc_Main', skin)
        # print('skin=\n', self.skin)

        try:
            Screen.setTitle(self, _('%s') % 'MAIN MENU')
        except BaseException:
            try:
                self.setTitle(_('%s') % 'MAIN MENU')
            except BaseException:
                pass

        self.checkinf()  # test for timezone

        # iptv_list_tmp
        self.channel_list = globalsxp.STREAMS.iptv_list
        self.index = globalsxp.STREAMS.list_index  # 0   ??
        channel_list2 = self.channel_list
        self.index2 = self.index
        self.search = ''
        globalsxp.re_search = False
        self.downloading = False
        self.pin = False
        self.temp_index = 0
        self.temp_playname = str(globalsxp.STREAMS.playlistname)
        self.filter_search = []

        self.mlist = MenuList(
            [],
            enableWrapAround=True,
            content=eListboxPythonMultiContent)
        self.mlist.l.setFont(0, gFont(FONT_0[0], FONT_0[1]))
        self.mlist.l.setFont(1, gFont(FONT_1[0], FONT_1[1]))
        self.mlist.l.setItemHeight(BLOCK_H)

        if cfg.infoexp.getValue():
            globalsxp.infoname = str(cfg.infoname.value)
        self["exp"] = Label("")
        self["max_connect"] = Label("")
        self["active_cons"] = Label("")
        self["server_protocol"] = Label("")
        self["created_at"] = Label("")
        self["timezone"] = Label("")
        self["info"] = Label()
        self["playlist"] = Label()
        self["description"] = StaticText('')

        self.rating_stars_cache = {}
        self._rating_stars_fill_orig_pos = None

        # Use Pixmap instead of StaticText
        self["rating_stars"] = Pixmap()
        self["rating_stars_fill"] = Pixmap()
        self["rating_value"] = Label()

        self.stars_empty_pixmap = None
        self.stars_filled_pixmap = None
        self.stars_fill_position = None
        self.bar_width = 315
        self.bar_height = 32

        self["state"] = Label()
        self["version"] = Label(version)
        self["key_red"] = Label(_("HOME"))
        self["key_green"] = Label(_("Rec Movie"))
        self["key_yellow"] = Label(_("Rec Series"))
        self["key_blue"] = Label(_("Search"))
        self["key_green"].hide()
        self["key_yellow"].hide()
        self["key_blue"].hide()
        self["key_text"] = Label("2")
        self["poster"] = Pixmap()
        self["Text"] = Label(globalsxp.infoname)
        self["playlist"].setText(self.temp_playname)

        self.go()

        self["actions"] = HelpableActionMap(
            self,
            "XCpluginActions",
            {
                "cancel": self.exitY,
                "home": self.update_list,
                "red": self.update_list,
                "1": self.update_list,
                "green": self.check_download_vod,
                "yellow": self.check_download_ser,
                "blue": self.search_text,
                "ok": self.ok,
                "info": self.show_more_info,
                "epg": self.show_more_info,
                "0": self.show_more_info,
                "showMediaPlayer": self.showMovies,
                "5": self.showMovies,
                "2": self.taskManager,
                "pvr": self.taskManager,
                "movielist": self.taskManager,
                "help": self.xc_Help,
                "power": self.power
            },
            -1
        )
        self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onFirstExecBegin.append(self.checkinf)
        # self.onLayoutFinish.append(self.show_all)
        self.onShown.append(self.show_all)

    def updatescreen(self):
        print("Updating screen...")

    def download_finished(self):
        print("download_finished ...")

    def ok(self):
        if not len(globalsxp.iptv_list_tmp):
            self.session.open(
                MessageBox,
                _("No data or playlist not compatible with XCplugin."),
                type=MessageBox.TYPE_WARNING,
                timeout=5)
            return

        self.index = self.mlist.getSelectionIndex()
        selected_channel = self.channel_list[self.mlist.getSelectionIndex()]
        globalsxp.STREAMS.list_index = self.mlist.getSelectionIndex()

        self.temp_index = self.index if selected_channel[4] else -1
        self.pin = True

        if config.ParentalControl.configured.value:
            a = '+18', 'adult', 'hot', 'porn', 'sex', 'xxx'
            if any(s in str(selected_channel[1] or selected_channel[4]
                   or selected_channel[5] or selected_channel[6]).lower() for s in a):
                self.allow2()
            else:
                self.pin = True
                self.pinEntered2(True)
        else:
            self.pin = True
            self.pinEntered2(True)

    def allow2(self):
        from Screens.InputBox import PinInput
        self.session.openWithCallback(
            self.pinEntered2,
            PinInput,
            pinList=[
                config.ParentalControl.setuppin.value],
            triesEntry=config.ParentalControl.retries.servicepin,
            title=_("Please enter the parental control pin code"),
            windowTitle=_("Enter pin code"))

    def pinEntered2(self, result):
        if not result:
            self.pin = False
            self.session.open(
                MessageBox,
                _("The pin code you entered is wrong."),
                type=MessageBox.TYPE_ERROR,
                timeout=5)
        self.ok_checked()

    def ok_checked(self):
        try:
            if self.temp_index > -1:
                self.index = self.temp_index
            # selected_channel = globalsxp.STREAMS.iptv_list_tmp[self.index]
            selected_channel = globalsxp.STREAMS.iptv_list[self.index]
            playlist_url = selected_channel[5]

            # for return from player!!
            if file_exists(input_file):
                with codecs.open(input_file, "r", encoding="utf-8") as f:
                    data = load(f)

                def convert_to_string(entry):
                    if entry is None:
                        return ''
                    elif isinstance(entry, (tuple, list)):
                        return type(entry)(convert_to_string(item)
                                           for item in entry)
                    else:
                        return str(entry)
                string_channel_list = list(map(convert_to_string, data))

                with codecs.open(output_file, "w", encoding="utf-8") as f:
                    dump(string_channel_list, f)

            self.set_tmp_list()

            if playlist_url is not None:
                globalsxp.STREAMS.get_list(playlist_url)
                self.update_channellist()

            elif selected_channel[4] is not None:
                globalsxp.STREAMS.video_status = True
                globalsxp.STREAMS.play_vod = False
                self.Entered()

        except Exception as e:
            print(e)

    def Entered(self):
        self.pin = True
        if globalsxp.stream_live is True:
            print("------------------------ LIVE ------------------")
            globalsxp.STREAMS.video_status = True
            globalsxp.STREAMS.play_vod = True
            if cfg.LivePlayer.value is False:
                self.session.openWithCallback(
                    self.check_standby, xc_Player)  # vod
            else:
                self.session.openWithCallback(
                    self.check_standby, nIPTVplayer)  # live
        else:
            print("----------------------- MOVIE ------------------")
            globalsxp.STREAMS.video_status = True
            globalsxp.STREAMS.play_vod = True
            self.session.openWithCallback(self.check_standby, xc_Player)
        copy_poster()

    def go(self):
        self.mlist.setList(
            list(map(channelEntryIPTVplaylist, self.channel_list)))
        self.mlist.onSelectionChanged.append(self.update_description)
        self["menulist"] = self.mlist
        self["menulist"].moveToIndex(0)

    def update_list(self):
        from Plugins.Extensions.XCplugin.plugin import iptv_streamse
        globalsxp.STREAMS = iptv_streamse()
        if "exampleserver.com" not in globalsxp.STREAMS.xtream_e2portal_url:
            globalsxp.STREAMS.read_config()
            globalsxp.STREAMS.get_list(globalsxp.STREAMS.xtream_e2portal_url)
            self.update_channellist()

    def button_updater(self):
        if cfg.infoexp.getValue():
            globalsxp.infoname = str(cfg.infoname.value)
        self["Text"].setText(globalsxp.infoname)
        self["playlist"].setText(self.temp_playname)

        if globalsxp.isStream and globalsxp.btnsearch == 1:
            self["key_blue"].show()
            self["key_green"].show()
            self["key_yellow"].show()

        elif 'series' in globalsxp.urlinfo:
            self["key_blue"].show()
            self["key_green"].show()
            self["key_yellow"].show()

    def update_description(self):
        if not len(globalsxp.iptv_list_tmp):
            return

        if globalsxp.re_search is True:
            self.channel_list = globalsxp.iptv_list_tmp

        try:
            self["info"].setText("")
            self["description"].setText("NO DESCRIPTIONS")

            try:
                if file_exists(globalsxp.pictmp):
                    remove(globalsxp.pictmp)
            except OSError as error:
                print(error)

            self["poster"].instance.setPixmapFromFile(globalsxp.piclogo[0])
            self.index = self.mlist.getSelectionIndex()
            selected_channel = self.channel_list[self.index]

            try:
                rating = 0.0
                if len(selected_channel) > 9 and selected_channel[9]:
                    try:
                        rating = float(selected_channel[9])
                    except (ValueError, TypeError):
                        rating = 0.0

                rating = max(0.0, min(10.0, rating))
                percent = rating / 10.0

                empty_path = "/usr/lib/enigma2/python/Plugins/Extensions/XCplugin/skin/pic/starsbar_empty.png"
                filled_path = "/usr/lib/enigma2/python/Plugins/Extensions/XCplugin/skin/pic/starsbar_filled.png"

                if self.stars_empty_pixmap is None:
                    self.stars_empty_pixmap = LoadPixmap(empty_path)
                    print("[RATING] Empty pixmap loaded: " +
                          ("success" if self.stars_empty_pixmap else "failed"))

                if self.stars_filled_pixmap is None:
                    self.stars_filled_pixmap = LoadPixmap(filled_path)
                    print("[RATING] Filled pixmap loaded: " +
                          ("success" if self.stars_filled_pixmap else "failed"))

                if self.stars_empty_pixmap:
                    self["rating_stars"].instance.setPixmap(
                        self.stars_empty_pixmap)
                    self["rating_stars"].show()
                    print("[RATING] Empty stars shown")

                filled_width = max(1, int(self.bar_width * percent))

                if self.stars_filled_pixmap and filled_width > 0:
                    current_pos = self["rating_stars_fill"].getPosition()
                    print(
                        "[RATING] Current position before: " +
                        str(current_pos))

                    self["rating_stars_fill"].instance.setPixmap(
                        self.stars_filled_pixmap)
                    self["rating_stars_fill"].instance.resize(
                        eSize(filled_width, self.bar_height))

                    if self.stars_fill_position is None:
                        x, y = self["rating_stars"].getPosition()
                        self.stars_fill_position = (x, y)
                        print(
                            "[RATING] Initial position set: (" + str(x) + ", " + str(y) + ")")

                    self["rating_stars_fill"].move(
                        ePoint(
                            self.stars_fill_position[0],
                            self.stars_fill_position[1]))

                    new_pos = self["rating_stars_fill"].getPosition()
                    print("[RATING] New position after move: " + str(new_pos))

                    self["rating_stars_fill"].hide()
                    self["rating_stars_fill"].show()
                    print(
                        "[RATING] Filled stars shown at " +
                        str(filled_width) +
                        "px")
                else:
                    self["rating_stars_fill"].hide()
                    print("[RATING] Filled stars hidden")

                if "rating_value" in self:
                    self["rating_value"].setText("{0:.1f}".format(rating))
                    self["rating_value"].show()

                print("[RATING] Updated to " + str(rating) + "/10.0")

            except Exception as e:
                print("[RATING ERROR] " + str(e))
                import traceback
                traceback.print_exc()

            if selected_channel[2] is not None:
                if globalsxp.stream_live is True:
                    description = selected_channel[2]
                    description2 = selected_channel[8]
                    description3 = selected_channel[6]
                    description_3 = description3.split(" #-# ")
                    descall = str(description) + "\n\n" + str(description2)
                    self["description"].setText(descall)
                    if description_3 and len(description_3) > 1:
                        self["info"].setText(str(description_3[1]))
                else:
                    description = str(selected_channel[2])
                    self["description"].setText(description)

                pixim = ensure_binary(selected_channel[7])
                if pixim != "":
                    parsed = urlparse(pixim)
                    domain = parsed.hostname
                    scheme = parsed.scheme
                    if scheme == "https" and sslverify:
                        sniFactory = SNIFactory(domain)
                        downloadPage(
                            pixim,
                            globalsxp.pictmp,
                            sniFactory,
                            timeout=ntimeout).addCallback(
                            self.image_downloaded,
                            globalsxp.pictmp).addErrback(
                            self.downloadError)
                    else:
                        downloadPage(pixim, globalsxp.pictmp).addCallback(
                            self.image_downloaded, globalsxp.pictmp
                        ).addErrback(self.downloadError)

            self.button_updater()

        except Exception as e:
            print(e)

    def image_downloaded(self, data, pictmp):
        if file_exists(globalsxp.pictmp):
            try:
                self.decodeImage(globalsxp.pictmp)
            except Exception as e:
                print("* error ** %s" % e)
                self.downloadError()

    def decodeImage(self, png):
        if file_exists(png):
            if self["poster"].instance:
                size = self['poster'].instance.size()
                self.scale = AVSwitch().getFramebufferScale()
                self.picload = ePicLoad()
                AVSwitch().setAspectRatio(globalsxp.STREAMS.ar_id_player)
                self.picload.setPara(
                    [size.width(), size.height(), self.scale[0], self.scale[1], 0, 1, 'FF000000'])
                if file_exists('/var/lib/dpkg/info'):
                    self.picload.startDecode(png, False)
                else:
                    self.picload.startDecode(png, 0, 0, False)
                ptr = self.picload.getData()
                if ptr is not None:
                    self['poster'].instance.setPixmap(ptr)
                    self['poster'].show()
                else:
                    self.downloadError()
                return

    def downloadError(self, error=""):
        try:
            if self["poster"].instance:
                self["poster"].instance.setPixmapFromFile(globalsxp.piclogo[0])
        except Exception as e:
            print('error poster', e)

    def update_channellist(self):
        if not len(globalsxp.iptv_list_tmp):
            return
        if globalsxp.re_search is False:
            self.channel_list = globalsxp.iptv_list_tmp

        if 'season' or 'series' in str(globalsxp.stream_url).lower():
            globalsxp.series = True

            streamfile = '/tmp/streamfile.txt'
            with open(streamfile, 'w') as f:
                f.write(
                    str(
                        self.channel_list).replace(
                        "\t",
                        "").replace(
                        "\r",
                        "").replace(
                        'None',
                        '').replace(
                        "'',",
                        "").replace(
                            ' , ',
                            '').replace(
                                "), ",
                                ")\n").replace(
                                    "''",
                                    '').replace(
                                        " ",
                        ""))
                f.write('\n')
                f.close()
        self.mlist.moveToIndex(0)
        self.mlist.setList(
            list(map(channelEntryIPTVplaylist, self.channel_list)))
        self.update_description()

    def show_all(self):
        try:
            if globalsxp.re_search is True:
                self.channel_list = globalsxp.iptv_list_tmp
                self.mlist.onSelectionChanged.append(self.update_description)
                self["menulist"] = self.mlist
                self["menulist"].moveToIndex(0)
            else:
                self.channel_list = globalsxp.STREAMS.iptv_list

            if file_exists("/usr/bin/apt-get"):
                def convert_to_str(entry):
                    if entry is None:
                        return ''
                    elif isinstance(entry, (tuple, list)):
                        return type(entry)(convert_to_str(item)
                                           for item in entry)
                    elif isinstance(entry, str):
                        return entry
                    elif isinstance(entry, text_type):
                        return entry.encode('utf-8')
                    else:
                        return str(entry)

                self.mlist.setList(list(map(lambda x: channelEntryIPTVplaylist(
                    convert_to_str(x)), self.channel_list)))
            else:
                self.mlist.setList(
                    list(map(channelEntryIPTVplaylist, self.channel_list)))
            self.mlist.moveToIndex(0)
            self.mlist.selectionEnabled(1)
            self.button_updater()
        except Exception as e:
            print(e)

    def search_text(self):
        if globalsxp.re_search is True:
            globalsxp.re_search = False
        self.session.openWithCallback(
            self.filterChannels,
            VirtualKeyBoard,
            title=_("Filter this category..."),
            text=self.search)

    def filterChannels(self, result):
        if result:
            self.filter_search = []
            self.search = result
            self.filter_search = [channel for channel in self.channel_list if str(
                result).lower() in channel[1].lower()]
            if len(self.filter_search):
                globalsxp.re_search = True
                globalsxp.iptv_list_tmp = self.filter_search
                self.mlist.setList(
                    list(map(channelEntryIPTVplaylist, globalsxp.iptv_list_tmp)))
                self.mlist.onSelectionChanged.append(self.update_description)
                self.index = self.mlist.getSelectionIndex()
                self["menulist"] = self.mlist
            else:
                self.resetSearch()
            self.button_updater()

    def resetSearch(self):
        globalsxp.re_search = False
        self.filter_search = []

    def set_tmp_list(self):
        if file_exists("/usr/bin/apt-get"):

            def convert_to_string(entry):
                if entry is None:
                    return ''
                elif isinstance(entry, (tuple, list)):
                    return type(entry)(convert_to_string(item)
                                       for item in entry)
                else:
                    return str(entry)
            string_channel_list = list(
                map(convert_to_string, self.channel_list))

            with codecs.open(input_file, "w", encoding="utf-8") as f:
                dump(string_channel_list, f)
        else:
            with open(input_file, 'w') as f:
                dump(self.channel_list, f)

    def load_from_tmp(self):
        if file_exists(output_file):
            with codecs.open(output_file, "r", encoding="utf-8") as f:
                self.channel_list = load(f)
                remove(output_file)
        else:
            if file_exists(input_file):
                with codecs.open(input_file, "r", encoding="utf-8") as f:
                    self.channel_list = load(f)

        if len(self.channel_list):
            globalsxp.iptv_list_tmp = self.channel_list
            globalsxp.STREAMS.iptv_list = self.channel_list

            self.mlist.setList(
                list(map(channelEntryIPTVplaylist, globalsxp.iptv_list_tmp)))
            self.mlist.onSelectionChanged.append(self.update_description)
            self.index = self.mlist.getSelectionIndex()
            self["menulist"] = self.mlist

    def mmark(self):
        self.temp_index = 0
        if globalsxp.STREAMS.video_status is True:
            globalsxp.STREAMS.video_status = False
        self.load_from_tmp()
        globalsxp.STREAMS.list_index = self.index2
        print('=========== self show_all')
        self.show_all()

        self.decodeImage(globalsxp.piclogo[0])
        globalsxp.infoname = self.temp_playname
        self["playlist"].setText(globalsxp.infoname)

    def exitY(self):
        keywords = ['get_series', 'get_vod', 'get_live']
        copy_poster()
        if file_exists(output_file) and globalsxp.STREAMS.video_status is True:
            copy(output_file, input_file)
            remove(output_file)

        if file_exists(input_file):
            with codecs.open(input_file, "r", encoding="utf-8") as f:
                content = f.read()
                if any(keyword in content for keyword in keywords):
                    print('=========== self show_all now')
                    self.mmark()

        if globalsxp.btnsearch == 1:
            globalsxp.btnsearch = 0
            self["key_blue"].hide()
            self["key_green"].hide()
            self["key_yellow"].hide()
            print('go mmark')
            self.mmark()
        else:
            if cfg.stoplayer.value is True:
                print('=========== self stoplayer')
                globalsxp.STREAMS.play_vod = False
                self.session.nav.stopService()
                self.session.nav.playService(self.initialservice)

            if file_exists(input_file):
                with codecs.open(input_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if any(keyword in content for keyword in keywords):
                        remove(input_file)
                        print('======= remove /tmp/mydata.json')
            file_path = join('/tmp', 'canali_temp.xml')
            if file_exists(file_path):
                remove(file_path)
                print('======= remove /tmp/canali_temp.xml')

            aspect_manager.restore_aspect()

            self.close()

    def showMovies(self):
        self.session.open(MovieSelection)

    def xc_Help(self):
        self.session.openWithCallback(self.checkinf, xc_help)

    def taskManager(self):
        self.session.open(xc_StreamTasks)

    def LastJobView(self):
        currentjob = None
        for job in JobManager.getPendingJobs():
            currentjob = job
        if currentjob is not None:
            self.session.open(JobView, currentjob)
        else:
            self.downloading = False

    def show_more_info(self):
        self.index = self.mlist.getSelectionIndex()
        selected_channel = globalsxp.iptv_list_tmp[self.index]
        if selected_channel:
            name = str(selected_channel[1])
            show_more_infos(name, self.index, _session)

    def checkinf(self):
        try:
            TIME_GMT = '%d-%m-%Y %H:%M:%S'
            self["max_connect"].setText("Max Connect: 0")
            self["active_cons"].setText("User Active: 0")
            self["exp"].setText("- ? -")
            self["created_at"].setText("- ? -")
            self["server_protocol"].setText("Protocol: - ? -")
            self["timezone"].setText("Time Now: - ? -")
            status = auth = created_at = exp_date = active_cons = max_connections = host = '- ? -'
            username = password = ''
            if cfg.hostaddress != 'exampleserver.com':
                host = cfg.hostaddress.value
            port = cfg.port.value
            if cfg.user.value != "Enter_Username":
                username = cfg.user.value
            if cfg.passw != '******':
                password = cfg.passw.value
            globalsxp.urlinfo = 'http://' + str(host) + ':' + str(
                port) + '/player_api.php?username=' + str(username) + '&password=' + str(password)
            self.ycse = retTest(globalsxp.urlinfo)
            if self.ycse:
                y = self.ycse
                if "user_info" in y:
                    if "auth" in y["user_info"]:
                        if y["user_info"]["auth"] == 1:
                            try:
                                status = (y["user_info"]["status"])
                                auth = (y["user_info"]["auth"])
                                created_at = (y["user_info"]["created_at"])
                                exp_date = (y["user_info"]["exp_date"])
                                active_cons = (y["user_info"]["active_cons"])
                                max_connections = (
                                    y["user_info"]["max_connections"])
                                if exp_date:
                                    exp_date = strftime(
                                        TIME_GMT, gmtime(int(exp_date)))

                                if str(auth) == "1":
                                    if str(status) == "Active":
                                        self["exp"].setText(
                                            "Active\nExp date: " + str(exp_date))
                                    elif str(status) == "Banned":
                                        self["exp"].setText("Banned")
                                    elif str(status) == "Disabled":
                                        self["exp"].setText("Disabled")
                                    elif str(status) == "Expired":
                                        self["exp"].setText(
                                            "Expired\nExp date: " + str(exp_date))
                                    else:
                                        self["exp"].setText(
                                            "Server Not Responding" + str(exp_date))
                                    if created_at:
                                        created_at = strftime(
                                            TIME_GMT, gmtime(int(created_at)))
                                        self["created_at"].setText(
                                            'Start date:\n' + created_at)

                                    self["max_connect"].setText(
                                        "Max Connect: " + str(max_connections))
                                    self["active_cons"].setText(
                                        "User Active: " + str(active_cons))
                                server_protocol = (
                                    y["server_info"]["server_protocol"])
                                self["server_protocol"].setText(
                                    "Protocol: " + str(server_protocol))
                                time_now = (y["server_info"]["time_now"])
                                time_zone = (y["server_info"]["timezone"])
                                time_stamp = (
                                    y["server_info"]["timestamp_now"])
                                globalsxp.timeserver = time_now
                                globalsxp.timezone = time_zone
                                globalsxp.timestamp = time_stamp
                                # Apply user-configured time adjustment
                                self["timezone"].setText(
                                    "Time Now: " + str(time_now))
                            except Exception as e:
                                print('error checkinf : ', e)
        except Exception as e:
            print('checkinf: ', e)

    def check_download_ser(self, answer=None):
        titleserie = str(globalsxp.STREAMS.playlistname)
        if globalsxp.series is True and globalsxp.btnsearch == 1:
            if answer is None:
                self.streamfile = '/tmp/streamfile.txt'
                if file_exists(
                        self.streamfile) and stat(
                        self.streamfile).st_size > 0:
                    self.session.openWithCallback(
                        self.check_download_ser,
                        MessageBox,
                        _("ATTENTION!!!\nDOWNLOAD ALL EPISODES SERIES\nSURE???")
                    )
            elif answer:
                self.icount = 0
                try:
                    self["state"].setText("Download SERIES")

                    # Build and normalize path safely
                    globalsxp.Path_Movies2 = normpath(
                        join(globalsxp.Path_Movies, titleserie))

                    # Create directory if it does not exist
                    if not file_exists(globalsxp.Path_Movies2):
                        try:
                            makedirs(globalsxp.Path_Movies2)
                        except Exception as e:
                            print("Failed to create directory:", e)

                    read_data = ""
                    with codecs.open(self.streamfile, "r", encoding="utf-8") as f:
                        read_data = f.read()

                    if read_data != "":
                        try:
                            regexcat = r".*?,'(.*?)','(.*?)'.*?\n"
                            match = compile(
                                regexcat, DOTALL).findall(read_data)
                            for name, url in match:
                                if url.startswith('http'):
                                    ext = splitext(url)[-1]
                                    if ext not in EXTDOWN:
                                        ext = '.avi'
                                    cleanName = cleanNames(name)
                                    self.title = titleserie + '_' + cleanName.lower()
                                    self.icount += 1

                                    output_path = join(
                                        globalsxp.Path_Movies2, self.title)

                                    if url.startswith("https"):
                                        cmd = "wget --no-check-certificate -U Enigma2 - XC Forever Plugin -c {} -O {}".format(
                                            url, output_path)
                                    else:
                                        cmd = "wget -U Enigma2 - XC Forever Plugin -c {} -O {}".format(
                                            url, output_path)

                                    # cmd_bytes = cmd.encode('utf-8')
                                    JobManager.AddJob(
                                        downloadJob(
                                            self,
                                            cmd,
                                            globalsxp.Path_Movies2,
                                            self.title))

                                    self.downloading = True

                        except Exception as e:
                            print("Error parsing or downloading:", e)

                    else:
                        globalsxp.series = False

                    Utils.OnclearMem()

                except Exception as e:
                    print("General error in download series:", e)
                    globalsxp.series = False
        else:
            self.session.open(
                MessageBox,
                _("Only Series Episodes Allowed!!!"),
                MessageBox.TYPE_INFO,
                timeout=5)

    def check_download_vod(self):
        self.index = self.mlist.getSelectionIndex()
        selected_channel = globalsxp.iptv_list_tmp[self.index]
        if selected_channel:
            self.title = str(selected_channel[1])
            self.vod_url = selected_channel[4]
            self.desc = str(selected_channel[2])
            if self.vod_url is not None and globalsxp.btnsearch == 1:
                pth = urlparse(self.vod_url).path
                ext = splitext(pth)[-1]
                if ext != '.ts':
                    cleanName = cleanNames(self.title)
                    if ext not in EXTDOWN:
                        ext = '.avi'
                    filename = cleanName + ext
                    self.filename = filename.lower()
                    self.session.openWithCallback(self.download_vod, MessageBox, _(
                        "DOWNLOAD VIDEO?"), type=MessageBox.TYPE_YESNO, timeout=5)
                else:
                    if cfg.LivePlayer.value is True:
                        self.session.open(
                            MessageBox,
                            _("Live Player Active in Setting: set No for Record Live"),
                            MessageBox.TYPE_INFO,
                            timeout=5)
                        return
            else:
                self.session.open(
                    MessageBox,
                    _("No Video to Download/Record!!"),
                    MessageBox.TYPE_INFO,
                    timeout=5)

    def download_vod(self, result):
        if result:
            try:
                self["state"].setText("Download MOVIE")
                system('sleep 3')
                self.downloading = True
                self.timerDownload = eTimer()
                self.file_down = join(globalsxp.Path_Movies, self.filename)

                if cfg.pdownmovie.value == "JobManager":
                    try:
                        self.timerDownload.callback.append(self.downloadx)
                    except BaseException:
                        self.timerDownload_conn = self.timerDownload.timeout.connect(
                            self.downloadx)

                else:
                    try:
                        self.timerDownload.callback.append(self.downloady)
                    except BaseException:
                        self.timerDownload_conn = self.timerDownload.timeout.connect(
                            self.downloady)
                self.timerDownload.start(300, True)
            except BaseException:
                self.session.open(
                    MessageBox,
                    _(
                        'Download Failed\n\n' +
                        self.filename +
                        "\n\n" +
                        globalsxp.Path_Movies +
                        '\n' +
                        self.filename),
                    MessageBox.TYPE_WARNING)
                self.downloading = False

    def downloady(self):
        if self.downloading is True:
            Utils.OnclearMem()
            self.session.open(
                imagedownloadScreen,
                self.filename,
                self.file_down,
                self.vod_url)
        else:
            return

    def downloadx(self):
        try:
            user_agent = "Enigma2 - XC Forever Plugin"
            vod_url = str(self.vod_url)
            file_down = str(self.file_down)

            # DEBUG: Stampa i valori per verifica
            print("[DEBUG] vod_url:", vod_url)
            print("[DEBUG] file_down:", file_down)

            # Funzione di quoting per percorsi con spazi
            def enigma_quote(s):
                s = s.replace("'", "'\"'\"'")
                return "'" + s + "'"

            # Applica quoting solo se necessario
            quoted_vod_url = vod_url if ' ' not in vod_url else enigma_quote(
                vod_url)
            quoted_file_down = file_down if ' ' not in file_down else enigma_quote(
                file_down)

            if vod_url.startswith("https"):
                cmd = 'wget --no-check-certificate -U %s -c %s -O %s' % (
                    enigma_quote(user_agent),
                    quoted_vod_url,
                    quoted_file_down
                )
            else:
                cmd = 'wget -U %s -c %s -O %s' % (
                    enigma_quote(user_agent),
                    quoted_vod_url,
                    quoted_file_down
                )

            print("[DEBUG] Final command:", cmd)

            # Crea e aggiungi il job
            job = downloadJob(self, cmd, file_down, self.title)
            JobManager.AddJob(job)

            print("[INFO] Job created successfully")
            self.downloading = False
            Utils.OnclearMem()
            self.createMetaFile(self.filename, self.filename)
            self.LastJobView()
            return True

        except Exception as e:
            print("[ERROR] in downloadx:", str(e))
            # Mostra un messaggio all'utente
            self.session.open(
                MessageBox,
                _("Download error: %s") % str(e),
                MessageBox.TYPE_ERROR
            )
            return False

    def eError(self, error):
        print("----------- %s" % error)
        self.downloading = False

    def createMetaFile(self, filename, filmtitle):
        try:
            serviceref = eServiceReference(4097, 0, filename)
            with open("%s/%s.meta" % (globalsxp.Path_Movies, filename), "wb") as f:
                f.write(
                    "%s\n%s\n%s\n%i\n" %
                    (serviceref.toString(), str(filmtitle), "", time()))
        except Exception as e:
            print(e)
        return

    def check_standby(self, myparam=None):
        copy_poster()
        if myparam:
            self.power()

    def power(self):
        self.session.nav.stopService()
        self.session.open(Standby)

    """
    def back_to_video(self):
        try:
            self.load_from_tmp()
            self.channel_list = globalsxp.STREAMS.iptv_list
            self.session.open(xc_Player)
        except Exception as e:
            print(e)
    """

# ===================Time is what we want most, but what we use worst=====
#
# Time is the best author. It always writes the perfect ending (Charlie Chaplin)
#
# by Lululla & MMark -thanks my friend PCD and aime_jeux and other friends
# thank's to Linux-Sat-support forum - MasterG
# thanks again to KiddaC for all the tricks we exchanged, and not just the tricks ;)
# -------------------------------------------------------------------------------------
# ===================Skin by Mmark Edition for Xc Plugin Infinity please don't copy o remove this
# send credits to autor Lululla  ;)
