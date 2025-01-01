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
from . import (
    _,
    b64decoder,
    version,
    make_request,
    check_port,
    retTest,
)
from .addons import Utils
from .addons import html_conv
from .addons.Console import Console as xcConsole
from .addons.downloader2 import imagedownloadScreen
from .addons.modul import (
    cleanNames,
    copy_poster,
    EXTDOWN,
    globalsxp,
    Panel_list,
)
from .addons.NewOeSk import ctrlSkin
from .xcConfig import xc_config, cfg
from .xcEpg import show_more_infos
from .xcHelp import xc_help
from .xcMaker import xc_maker, save_old
# from .xcOpenServer import OpenServer
from .xcPlaylist import xc_Playlist
from .xcPlayerUri import xc_Play, nIPTVplayer, xc_Player, sslverify, SNIFactory
from .xcShared import FONT_0, FONT_1, BLOCK_H
from .xcShared import skin_path, xcm3ulistEntry, xcM3UList, channelEntryIPTVplaylist
from .xcTask import xc_StreamTasks, downloadJob

from Components.ActionMap import HelpableActionMap
from Components.config import config
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from Components.Task import job_manager as JobManager
from enigma import (
    eListboxPythonMultiContent,
    ePicLoad,
    eServiceReference,
    eTimer,
    gFont,
    getDesktop,
)
from os import remove, system
from os.path import splitext
from os.path import exists as file_exists

from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.MovieSelection import MovieSelection
from Screens.Screen import Screen
from Screens.Standby import Standby
from Screens.TaskView import JobView
from Screens.VirtualKeyBoard import VirtualKeyBoard
from six.moves.urllib.parse import urlparse
from Tools.Directories import (SCOPE_PLUGINS, resolveFilename)
from twisted.web.client import downloadPage
from six import text_type

import codecs
import json
import os
import re
import requests
import shutil
import six
import socket
import sys
import time

plugin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('XCplugin'))

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


try:
    from Components.AVSwitch import AVSwitch
except ImportError:
    from Components.AVSwitch import eAVControl as AVSwitch

try:
    from xml.etree.cElementTree import fromstring, tostring
except ImportError:
    from xml.etree.ElementTree import fromstring, tostring


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
        self["key_blue"] = Label(_("Loader M3U"))
        self["actions"] = HelpableActionMap(self, "XCpluginActions", {
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
            "info": self.xc_Help}, -1)
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
        self.close()

    def Team(self):
        # self.session.open(OpenServer)
        self.session.openWithCallback(self.OpenList, xc_Playlist)

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
        if "exampleserver.com" not in globalsxp.STREAMS.xtream_e2portal_url:
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
            # self.session.open(xc_Playlist)
        elif sel == ('MAKER BOUQUET'):
            self.session.open(xc_maker)
        elif sel == ('DOWNLOADER'):
            self.taskManager()
        elif sel == ('M3U LOADER'):
            self.session.open(xc_Play)
        elif sel == ('CONFIG'):
            self.config()
        elif sel == ('ABOUT & HELP'):
            self.helpx()


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
            print("-----------CONFIG START----------")
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
            print('Host: %s\nUsername: %s\nPassword:%s\n' % (self.xtream_e2portal_url, self.username, self.password))
            print("-----------CONFIG END----------")
        except Exception as e:
            print("++++++++++ERROR READ CONFIG+++++++++++++ ", e)

    def get_list(self, url=None):
        globalsxp.stream_live = False
        self.url = check_port(url)
        self.list_index = 0
        globalsxp.iptv_list_tmp = []
        xml = None
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

            xml = self._request(self.url)
            if xml:
                root = xml
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
                    # Category description
                    description_element = channel.find('description')
                    if description_element is not None and description_element.text is not None:
                        description = b64decoder(description_element.text)  # Passiamo il testo decodificato
                        # print('channels: Description:', type(description), description)

                    # Playlist URL
                    playlist_url_element = channel.find('playlist_url')
                    if playlist_url_element is not None and playlist_url_element.text is not None:
                        playlist_url = playlist_url_element.text
                        # print('channels: Playlist URL:', type(playlist_url), playlist_url)

                    # Category ID
                    category_id_element = channel.find('category_id')
                    if category_id_element is not None and category_id_element.text is not None:
                        category_id = category_id_element.text.strip()
                        # print('channels: Category ID:', type(category_id), category_id)

                    # Category stream_url
                    stream_url_id_element = channel.find('stream_url')
                    if stream_url_id_element is not None and stream_url_id_element.text is not None:
                        globalsxp.stream_url = stream_url_id_element.text.strip()
                        # globalsxp.stream_url = globalsxp.stream_url
                        # print('channels: Stream URL:', type(globalsxp.stream_url), globalsxp.stream_url)
                    else:
                        print('channels: Stream URL not found or is empty.')

                    # Category piconname
                    piconname_id_element = channel.find('logo')
                    if piconname_id_element is not None and piconname_id_element.text is not None:
                        piconname = piconname_id_element.text
                        # print('channels: Category piconname:', type(piconname), piconname)

                    # Category desc_image
                    desc_image_id_element = channel.find('desc_image')
                    if desc_image_id_element is not None and desc_image_id_element.text is not None:
                        desc_image = desc_image_id_element.text.strip()
                        if desc_image != "n/A" and desc_image != "":
                            if desc_image.startswith("https"):
                                desc_image = desc_image.replace("https", "http")
                            # print('channels:desc_image:', type(desc_image), desc_image)
                    if globalsxp.stream_url:
                        globalsxp.isStream = True
                        print('globalsxp.isStream: ', globalsxp.isStream)

                    if "/live/" in globalsxp.stream_url:
                        # print("****** is live stream **** ")
                        globalsxp.stream_live = True
                        epgnowtime = ''
                        epgnowdescription = ''
                        epgnexttitle = ''
                        epgnexttime = ''
                        epgnextdescription = ''
                        # name = html.unescape(name)  # Usa 'html.unescape' per Python 3
                        name = html_conv.html_unescape(name)  # Usa 'html.unescape' per Python 3
                        if description != '':
                            timematch = re.findall(r'\[(\d{2}:\d{2})\]', description)
                            titlematch = re.findall(r'\[\d{2}:\d{2}\](.*)', description)
                            descriptionmatch = re.findall(r'\n\((.*?)\)', description)

                            if timematch:
                                if len(timematch) > 0:
                                    epgnowtime = timematch[0].strip()
                                if len(timematch) > 1:
                                    epgnexttime = timematch[1].strip()

                            if titlematch:
                                if len(titlematch) > 0:
                                    nameepg = titlematch[0].strip()
                                if len(titlematch) > 1:
                                    epgnexttitle = titlematch[1].strip()

                            if descriptionmatch:
                                if len(descriptionmatch) > 0:
                                    epgnowdescription = descriptionmatch[0].strip()
                                if len(descriptionmatch) > 1:
                                    epgnextdescription = descriptionmatch[1].strip()

                            # Compose the description
                            description = epgnowtime + ' ' + name + '\n' + epgnowdescription
                            # description = html.unescape(description)
                            description = html_conv.html_unescape(description)
                            description2 = epgnexttime + ' ' + epgnexttitle + '\n' + epgnextdescription
                            # description2 = html.unescape(description2)
                            description2 = html_conv.html_unescape(description2)

                    elif ("/movie/" in globalsxp.stream_url) or ("/series/" in globalsxp.stream_url):
                        globalsxp.stream_live = False
                        vodItems = {}
                        name = html_conv.html_unescape(name)
                        vodTitle = ''
                        vodDescription = ''
                        vodDuration = ''
                        vodGenre = ''
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
                            vodDescription = str('TRAMA')
                        # print('vodDescription: ', vodDescription)
                        if "DURATION" in vodItems:
                            vodDuration = str(vodItems["DURATION"]).strip()
                        else:
                            vodDuration = str('DURATION: -- --')
                        # print('vodDuration: ', vodDuration)
                        if "GENRE" in vodItems:
                            vodGenre = str(vodItems["GENRE"]).strip()
                        else:
                            vodGenre = str('GENRE: -- --')
                        # print('vodGenre: ', vodGenre)
                        description3 = str(vodTitle) + '\n' + str(vodGenre) + '\nDuration: ' + str(vodDuration) + '\n' + str(vodDescription)
                        description = html_conv.html_unescape(description3)

                    chan_tulpe = (str(chan_counter),
                                  str(name),
                                  description,
                                  str(piconname),
                                  globalsxp.stream_url,
                                  playlist_url,
                                  category_id,
                                  str(desc_image),
                                  str(description2),
                                  str(nameepg))
                    globalsxp.iptv_list_tmp.append(chan_tulpe)
                    globalsxp.btnsearch = globalsxp.next_request
        except Exception as e:
            print('----- get_list failed: ', e)

        if len(globalsxp.iptv_list_tmp):
            self.iptv_list = globalsxp.iptv_list_tmp
            globalsxp.iptv_list_tmp = self.iptv_list
        return

    def _request(self, url):
        if "exampleserver" not in str(cfg.hostaddress.value):
            TYPE_PLAYER = '/enigma2.php'
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
                res = make_request(globalsxp.urlinfo)
                res = fromstring(res)
                if res is not None:
                    res_string = tostring(res, encoding='utf-8', method='xml').decode('utf-8')
                    file_path = os.path.join('/tmp', 'canali_temp.xml')
                    with open(file_path, 'w') as temp_file:
                        temp_file.write(res_string)
                        temp_file.flush()
                        globalsxp.temp_prev_list = res_string
                return res
            except Exception as e:
                res = None
                print('error requests -----------> ', e)
            return res


class xc_Main(Screen):
    def __init__(self, session):
        global _session
        global channel_list2
        _session = session
        Screen.__init__(self, session)
        skin = os.path.join(skin_path, 'xc_Main.xml')
        if cfg.screenxl.value:
            skin = os.path.join(skin_path, 'xc_Mainxl.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            skin = f.read()
        self.skin = ctrlSkin('xc_Main', skin)

        try:
            Screen.setTitle(self, _('%s') % 'MAIN MENU')
        except:
            try:
                self.setTitle(_('%s') % 'MAIN MENU')
            except:
                pass
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
        self.mlist = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
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
        self["actions"] = HelpableActionMap(self, "XCpluginActions", {
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
            "power": self.power}, -1)
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
            self.session.open(MessageBox, _("No data or playlist not compatible with XCplugin."), type=MessageBox.TYPE_WARNING, timeout=5)
            return

        self.index = self.mlist.getSelectionIndex()
        selected_channel = self.channel_list[self.mlist.getSelectionIndex()]
        globalsxp.STREAMS.list_index = self.mlist.getSelectionIndex()

        self.temp_index = -1
        if selected_channel[9] is not None:
            self.temp_index = self.index
        self.pin = True

        if config.ParentalControl.configured.value:
            a = '+18', 'adult', 'hot', 'porn', 'sex', 'xxx'
            if any(s in str(selected_channel[1] or selected_channel[4] or selected_channel[5] or selected_channel[6]).lower() for s in a):
                self.allow2()
            else:
                self.pin = True
                self.pinEntered2(True)
        else:
            self.pin = True
            self.pinEntered2(True)

    def allow2(self):
        from Screens.InputBox import PinInput
        self.session.openWithCallback(self.pinEntered2, PinInput, pinList=[config.ParentalControl.setuppin.value], triesEntry=config.ParentalControl.retries.servicepin, title=_("Please enter the parental control pin code"), windowTitle=_("Enter pin code"))

    def pinEntered2(self, result):
        if not result:
            self.pin = False
            self.session.open(MessageBox, _("The pin code you entered is wrong."), type=MessageBox.TYPE_ERROR, timeout=5)
        self.ok_checked()

    def ok_checked(self):
        try:
            if self.temp_index > -1:
                self.index = self.temp_index
            selected_channel = globalsxp.STREAMS.iptv_list[self.index]
            playlist_url = selected_channel[5]

            # for return from player!!
            if file_exists(input_file):
                with codecs.open(input_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                def convert_to_string(entry):
                    if entry is None:
                        return ''
                    elif isinstance(entry, (tuple, list)):
                        return type(entry)(convert_to_string(item) for item in entry)
                    else:
                        return str(entry)
                string_channel_list = list(map(convert_to_string, data))

                with codecs.open(output_file, "w", encoding="utf-8") as f:
                    json.dump(string_channel_list, f)

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
                self.session.openWithCallback(self.check_standby, xc_Player)  # vod
            else:
                self.session.openWithCallback(self.check_standby, nIPTVplayer)  # live
        else:
            print("----------------------- MOVIE ------------------")
            globalsxp.STREAMS.video_status = True
            globalsxp.STREAMS.play_vod = True
            self.session.openWithCallback(self.check_standby, xc_Player)
        copy_poster()

    def go(self):
        self.mlist.setList(list(map(channelEntryIPTVplaylist, self.channel_list)))
        self.mlist.onSelectionChanged.append(self.update_description)
        self["menulist"] = self.mlist
        self["menulist"].moveToIndex(0)

    def update_list(self):
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
        self.index = self.mlist.getSelectionIndex()
        try:
            self["info"].setText("")
            self["description"].setText("NO DESCRIPTIONS")
            try:
                if file_exists(globalsxp.pictmp):
                    remove(globalsxp.pictmp)
            except OSError as error:
                print(error)
            self['poster'].instance.setPixmapFromFile(globalsxp.piclogo[0])
            selected_channel = self.channel_list[self.index]
            if selected_channel[2] is not None:
                if globalsxp.stream_live is True:
                    description = selected_channel[2]
                    description2 = selected_channel[8]
                    description3 = selected_channel[6]
                    description_3 = description3.split(" #-# ")
                    descall = str(description) + '\n\n' + str(description2)
                    self["description"].setText(descall)
                    if description_3:
                        if len(description_3) > 1:
                            self["info"].setText(str(description_3[1]))
                else:
                    description = str(selected_channel[2])
                    self["description"].setText(description)
                pixim = six.ensure_binary(selected_channel[7])
                if pixim != "":
                    parsed = urlparse(pixim)
                    domain = parsed.hostname
                    scheme = parsed.scheme
                    if scheme == "https" and sslverify:
                        sniFactory = SNIFactory(domain)
                        downloadPage(pixim, globalsxp.pictmp, sniFactory, timeout=ntimeout).addCallback(self.image_downloaded, globalsxp.pictmp).addErrback(self.downloadError)
                    else:
                        downloadPage(pixim, globalsxp.pictmp).addCallback(self.image_downloaded, globalsxp.pictmp).addErrback(self.downloadError)
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
                self.picload.setPara([size.width(), size.height(), self.scale[0], self.scale[1], 0, 1, 'FF000000'])
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
                f.write(str(self.channel_list).replace("\t", "").replace("\r", "").replace('None', '').replace("'',", "").replace(' , ', '').replace("), ", ")\n").replace("''", '').replace(" ", ""))
                f.write('\n')
                f.close()
        self.mlist.moveToIndex(0)
        self.mlist.setList(list(map(channelEntryIPTVplaylist, self.channel_list)))
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

            if os.path.exists("/usr/bin/apt-get"):
                def convert_to_str(entry):
                    if entry is None:
                        return ''
                    elif isinstance(entry, (tuple, list)):
                        return type(entry)(convert_to_str(item) for item in entry)
                    elif isinstance(entry, str):
                        return entry
                    elif isinstance(entry, text_type):
                        return entry.encode('utf-8')
                    else:
                        return str(entry)

                self.mlist.setList(
                    list(map(lambda x: channelEntryIPTVplaylist(convert_to_str(x)), self.channel_list))
                )
            else:
                self.mlist.setList(list(map(channelEntryIPTVplaylist, self.channel_list)))
            self.mlist.moveToIndex(0)
            self.mlist.selectionEnabled(1)
            self.button_updater()
        except Exception as e:
            print(e)

    def search_text(self):
        if globalsxp.re_search is True:
            globalsxp.re_search = False
        self.session.openWithCallback(self.filterChannels, VirtualKeyBoard, title=_("Filter this category..."), text=self.search)

    def filterChannels(self, result):
        if result:
            self.filter_search = []
            self.search = result
            self.filter_search = [channel for channel in self.channel_list if str(result).lower() in channel[1].lower()]
            if len(self.filter_search):
                globalsxp.re_search = True
                globalsxp.iptv_list_tmp = self.filter_search
                self.mlist.setList(list(map(channelEntryIPTVplaylist, globalsxp.iptv_list_tmp)))
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
        if os.path.exists("/usr/bin/apt-get"):

            def convert_to_string(entry):
                if entry is None:
                    return ''
                elif isinstance(entry, (tuple, list)):
                    return type(entry)(convert_to_string(item) for item in entry)
                else:
                    return str(entry)
            string_channel_list = list(map(convert_to_string, self.channel_list))

            with codecs.open(input_file, "w", encoding="utf-8") as f:
                json.dump(string_channel_list, f)
        else:
            with open(input_file, 'w') as f:
                json.dump(self.channel_list, f)

    def load_from_tmp(self):
        if file_exists(output_file):
            with codecs.open(output_file, "r", encoding="utf-8") as f:
                self.channel_list = json.load(f)
                remove(output_file)
        else:
            if file_exists(input_file):
                with codecs.open(input_file, "r", encoding="utf-8") as f:
                    self.channel_list = json.load(f)

        if len(self.channel_list):
            globalsxp.iptv_list_tmp = self.channel_list
            globalsxp.STREAMS.iptv_list = self.channel_list

            self.mlist.setList(list(map(channelEntryIPTVplaylist, globalsxp.iptv_list_tmp)))
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
            shutil.copy(output_file, input_file)
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
            file_path = os.path.join('/tmp', 'canali_temp.xml')
            if file_exists(file_path):
                remove(file_path)
                print('======= remove /tmp/canali_temp.xml')
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
            self["timezone"].setText("Timezone: - ? -")
            status = auth = created_at = exp_date = active_cons = max_connections = host = '- ? -'
            username = password = ''
            if cfg.hostaddress != 'exampleserver.com':
                host = cfg.hostaddress.value
            port = cfg.port.value
            if cfg.user.value != "Enter_Username":
                username = cfg.user.value
            if cfg.passw != '******':
                password = cfg.passw.value
            globalsxp.urlinfo = 'http://' + str(host) + ':' + str(port) + '/player_api.php?username=' + str(username) + '&password=' + str(password)
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
                                max_connections = (y["user_info"]["max_connections"])
                                if exp_date:
                                    exp_date = time.strftime(TIME_GMT, time.gmtime(int(exp_date)))

                                if str(auth) == "1":
                                    if str(status) == "Active":
                                        self["exp"].setText("Active\nExp date: " + str(exp_date))
                                    elif str(status) == "Banned":
                                        self["exp"].setText("Banned")
                                    elif str(status) == "Disabled":
                                        self["exp"].setText("Disabled")
                                    elif str(status) == "Expired":
                                        self["exp"].setText("Expired\nExp date: " + str(exp_date))
                                    else:
                                        self["exp"].setText("Server Not Responding" + str(exp_date))
                                    if created_at:
                                        created_at = time.strftime(TIME_GMT, time.gmtime(int(created_at)))
                                        self["created_at"].setText('Start date:\n' + created_at)

                                    self["max_connect"].setText("Max Connect: " + str(max_connections))
                                    self["active_cons"].setText("User Active: " + str(active_cons))
                                server_protocol = (y["server_info"]["server_protocol"])
                                self["server_protocol"].setText("Protocol: " + str(server_protocol))
                                timezone = (y["server_info"]["timezone"])
                                self["timezone"].setText("Timezone: " + str(timezone))
                            except Exception as e:
                                print('error checkinf : ', e)
        except Exception as e:
            print('checkinf: ', e)

    def check_download_ser(self, answer=None):
        titleserie = str(globalsxp.STREAMS.playlistname)
        if globalsxp.series is True and globalsxp.btnsearch == 1:
            if answer is None:
                self.streamfile = '/tmp/streamfile.txt'
                if file_exists(self.streamfile) and os.stat(self.streamfile).st_size > 0:
                    self.session.openWithCallback(self.check_download_ser, MessageBox, _("ATTENTION!!!\nDOWNLOAD ALL EPISODES SERIES\nSURE???"))
            elif answer:
                self.icount = 0
                try:
                    self["state"].setText("Download SERIES")
                    globalsxp.Path_Movies2 = globalsxp.Path_Movies + titleserie + '/'
                    if not file_exists(globalsxp.Path_Movies2):
                        system("mkdir " + globalsxp.Path_Movies2)
                    if globalsxp.Path_Movies2.endswith("//") is True:
                        globalsxp.Path_Movies2 = globalsxp.Path_Movies2[:-1]
                    read_data = ''
                    with codecs.open(self.streamfile, "r", encoding="utf-8") as f:
                        read_data = f.read()
                    if read_data != "":
                        try:
                            regexcat = ".*?,'(.*?)','(.*?)'.*?\\n"
                            match = re.compile(regexcat, re.DOTALL).findall(read_data)
                            for name, url in match:
                                if url.startswith('http'):
                                    ext = str(splitext(url)[-1])
                                    if ext not in EXTDOWN:
                                        ext = '.avi'
                                    cleanName = cleanNames(name)
                                    self.title = titleserie + '_' + cleanName.lower()
                                    self.icount += 1
                                    cmd = "wget --no-cache --no-dns-cache -U '%s' -c '%s' -O '%s%s'" % ('Enigma2 - XC Forever Plugin', url, str(globalsxp.Path_Movies2), self.title)
                                    if "https" in str(url):
                                        cmd = "wget --no-check-certificate --no-cache --no-dns-cache -U '%s' -c '%s' -O '%s%s'" % ('Enigma2 - XC Forever Plugin', url, str(globalsxp.Path_Movies2), self.title)
                                    JobManager.AddJob(downloadJob(self, cmd, globalsxp.Path_Movies2, self.title))
                                    self.downloading = True
                            # self.createMetaFile(self.title, self.title)
                        except Exception as e:
                            print(e)
                            pass

                    else:
                        globalsxp.series = False
                    Utils.OnclearMem()

                except Exception as e:
                    print(e)
                    globalsxp.series = False
        else:
            self.session.open(MessageBox, _("Only Series Episodes Allowed!!!"), MessageBox.TYPE_INFO, timeout=5)

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
                    self.session.openWithCallback(self.download_vod, MessageBox, _("DOWNLOAD VIDEO?"), type=MessageBox.TYPE_YESNO, timeout=5)
                else:
                    if cfg.LivePlayer.value is True:
                        self.session.open(MessageBox, _("Live Player Active in Setting: set No for Record Live"), MessageBox.TYPE_INFO, timeout=5)
                        return
            else:
                self.session.open(MessageBox, _("No Video to Download/Record!!"), MessageBox.TYPE_INFO, timeout=5)

    def download_vod(self, result):
        if result:
            try:
                self["state"].setText("Download MOVIE")
                system('sleep 3')
                self.downloading = True
                self.timerDownload = eTimer()
                self.file_down = globalsxp.Path_Movies + self.filename

                if cfg.pdownmovie.value == "JobManager":
                    try:
                        self.timerDownload.callback.append(self.downloadx)
                    except:
                        self.timerDownload_conn = self.timerDownload.timeout.connect(self.downloadx)

                elif cfg.pdownmovie.value == "Requests":
                    try:
                        r = requests.get(self.vod_url, verify=False)
                        if r.status_code == requests.codes.ok:
                            with open(self.file_down, 'wb') as f:
                                f.write(r.content)
                    except Exception as e:
                        print('error requests: ', e)
                        self.downloading = False
                else:
                    try:
                        self.timerDownload.callback.append(self.downloady)
                    except:
                        self.timerDownload_conn = self.timerDownload.timeout.connect(self.downloady)
                self.timerDownload.start(300, True)
            except:
                self.session.open(MessageBox, _('Download Failed\n\n' + self.filename + "\n\n" + globalsxp.Path_Movies + '\n' + self.filename), MessageBox.TYPE_WARNING)
                self.downloading = False

    def downloady(self):
        if self.downloading is True:
            Utils.OnclearMem()
            self.session.open(imagedownloadScreen, self.filename, self.file_down, self.vod_url)
        else:
            return

    def downloadx(self):
        cmd = "wget --no-cache --no-dns-cache -U '%s' -c '%s' -O '%s'" % ('Enigma2 XC Forever Plugin', str(self.vod_url), str(self.file_down))
        if "https" in str(self.vod_url):
            cmd = "wget --no-check-certificate --no-cache --no-dns-cache -U '%s' -c '%s' -O '%s'" % ('Enigma2 - XC Forever Plugin', str(self.vod_url), str(self.file_down))
        self.downloading = False
        try:
            JobManager.AddJob(downloadJob(self, cmd, self.file_down, self.title))
            Utils.OnclearMem()
        except Exception as e:
            print(e)
        self.createMetaFile(self.filename, self.filename)
        self.LastJobView()

    def eError(self, error):
        print("----------- %s" % error)
        self.downloading = False

    def createMetaFile(self, filename, filmtitle):
        try:
            serviceref = eServiceReference(4097, 0, filename)
            with open("%s/%s.meta" % (globalsxp.Path_Movies, filename), "wb") as f:
                f.write("%s\n%s\n%s\n%i\n" % (serviceref.toString(), str(filmtitle), "", time.time()))
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


# def main(session, **kwargs):
    # globalsxp.STREAMS = iptv_streamse()
    # if "exampleserver.com" not in globalsxp.STREAMS.xtream_e2portal_url:
        # globalsxp.STREAMS.read_config()
        # globalsxp.STREAMS.get_list(globalsxp.STREAMS.xtream_e2portal_url)
    # session.open(xc_home)


# def check_configuring(session):
    # from .plugin import xc_Main
    # if cfg.autobouquetupdate.value is True:
        # """Check for new config values for auto start"""
        # if globalsxp.autoStartTimer is not None:
            # globalsxp.autoStartTimer.update()
    # session.open(xc_Main)


def check_configuring():
    if cfg.autobouquetupdate.value is True:
        """Check for new config values for auto start"""
        if globalsxp.autoStartTimer is not None:
            globalsxp.autoStartTimer.update()
        return


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
            Utils.web_info(message)


def autostart(reason, session=None, **kwargs):
    global _session
    if reason == 0 and _session is None:
        if session is not None:
            _session = session
            if globalsxp.autoStartTimer is None:
                globalsxp.autoStartTimer = AutoStartTimer(_session)
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
