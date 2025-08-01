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
from datetime import datetime, timedelta
from os import chmod
from os.path import join
from re import DOTALL, findall
from socket import setdefaulttimeout
from sys import version_info
from time import altzone, timezone, localtime  # , strftime, strptime, mktime

# Conditional imports
try:
    from xml.etree.ElementTree import fromstring, tostring
except ImportError:
    from xml.etree.cElementTree import fromstring, tostring

# Third-party imports
from six import PY3, text_type

# Enigma2 imports
from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Plugins.Plugin import PluginDescriptor
from Screens.MovieSelection import MovieSelection
from Screens.Screen import Screen
from enigma import getDesktop

# Local package imports
from . import (
    _,
    b64decoder,
    version,
    make_request,
    check_port,
    plugin_path,
)
from .addons import Utils, html_conv
from .addons.Console import Console as xcConsole
from .addons.NewOeSk import ctrlSkin
from .addons.modul import globalsxp, Panel_list
from .xcConfig import cfg, xc_config
from .xcHelp import xc_help
from .xcMain import xc_Main
from .xcMaker import xc_maker
from .xcPlaylist import xc_Playlist
from .xcPlayerUri import aspect_manager, xc_Play
from .xcShared import autostart
from .xcSkin import skin_path, xcm3ulistEntry, xcM3UList
from .xcTask import xc_StreamTasks


# global fixed
_session = None
globalsxp.eserv = int(cfg.services.value)
globalsxp.infoname = str(cfg.infoname.value)
globalsxp.Path_Movies = str(cfg.pthmovie.value)  # + "/"
globalsxp.Path_Movies2 = globalsxp.Path_Movies
globalsxp.piclogo = join(plugin_path, 'skin/fhd/iptvlogo.jpg'),
globalsxp.pictmp = "/tmp/poster.jpg"
enigma_path = '/etc/enigma2/'
epgimport_path = '/etc/epgimport/'
iconpic = join(plugin_path, 'plugin.png')
input_file = '/tmp/mydata.json'
iptvsh = "/etc/enigma2/iptv.sh"
ntimeout = float(cfg.timeout.value)
output_file = '/tmp/mydata2.json'
Path_Picons = str(cfg.pthpicon.value) + "/"
Path_XML = str(cfg.pthxmlfile.value) + "/"
xc_list = "/tmp/xc.txt"
setdefaulttimeout(5)
screenwidth = getDesktop(0).size()

if PY3:
    unicode = text_type


class xc_home(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        skin = join(skin_path, 'xc_home.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            skin = f.read()
        self.skin = ctrlSkin('xc_home', skin)
        try:
            Screen.setTitle(self, _('%s') % 'MAIN MENU')
        except BaseException:
            try:
                self.setTitle(_('%s') % 'MAIN MENU')
            except BaseException:
                pass
        self.list = []
        self["Text"] = Label("")
        self["version"] = Label(version)
        self['menu'] = xcM3UList([])
        self["key_red"] = Label(_("Exit"))
        self["key_green"] = Label(_("Select"))
        self["key_yellow"] = Label(_("Movie"))
        self["key_blue"] = Label(_("M3u Loader"))
        self["actions"] = HelpableActionMap(
            self,
            "XCpluginActions",
            {
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
                "info": self.xc_Help
            },
            -1
        )
        self.onFirstExecBegin.append(self.check_dependencies)
        self.onLayoutFinish.append(self.updateMenuList)

    def check_dependencies(self):
        dependencies = True
        try:
            pythonFull = float(str(version_info.major) +
                               "." + str(version_info.minor))
            if pythonFull < 3.9:
                print("*** checking python version ***", pythonFull)
        except Exception as e:
            print("**** missing dependencies ***", e)
            dependencies = False

        if dependencies is False:
            chmod(join(plugin_path, 'dependencies.sh', 0o0755))
            cmd1 = ". /usr/lib/enigma2/python/Plugins/Extensions/XCplugin/dependencies.sh"
            self.session.openWithCallback(
                self.xcClean,
                xcConsole,
                title="Checking Dependencies",
                cmdlist=[cmd1],
                closeOnSuccess=True)
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
        aspect_manager.restore_aspect()
        self.close()

    def xc_Help(self):
        self.session.openWithCallback(self.xcClean, xc_help)

    def taskManager(self):
        self.session.openWithCallback(self.xcClean, xc_StreamTasks)

    def xcPlay(self):
        self.session.open(xc_Play)

    def showMovies(self):
        self.session.open(MovieSelection)

    """
    # def Team(self):
        # # self.session.openWithCallback(self.OpenList, xc_Playlist(globalsxp.STREAMS))
        # self.session.openWithCallback(self.OpenList, xc_Playlist, globalsxp.STREAMS)

    # def OpenList(self, callback=None):
        # host, port, username, password = self.load_config()

        # if host and username and password:
            # globalsxp.STREAMS = iptv_streamse()
            # globalsxp.STREAMS.read_config()
            # if "exampleserver" not in globalsxp.STREAMS.xtream_e2portal_url:
                # globalsxp.STREAMS.get_list(globalsxp.STREAMS.xtream_e2portal_url)
                # self.session.openWithCallback(check_configuring, xc_Main)
            # else:
                # message = _("First Select the list or enter it in Config")
                # Utils.web_info(message)
        # else:
            # message = _("Please configure the server details first")
            # self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=10)
    """

    def Team(self):
        # Ensure consistent calling pattern
        self.session.open(xc_Playlist, globalsxp.STREAMS)

    def OpenList(self, callback=None):
        host, port, username, password = self.load_config()
        if host and username and password:
            globalsxp.STREAMS = iptv_streamse()
            globalsxp.STREAMS.read_config()
            if "exampleserver" not in globalsxp.STREAMS.xtream_e2portal_url:
                globalsxp.STREAMS.get_list(
                    globalsxp.STREAMS.xtream_e2portal_url)
                self.session.open(xc_Main)  # Remove callback if not needed
            else:
                message = _("First Select the list or enter it in Config")
                Utils.web_info(message)
        else:
            message = _("Please configure the server details first")
            self.session.open(
                MessageBox,
                message,
                type=MessageBox.TYPE_INFO,
                timeout=10)

    def load_config(self):
        try:
            # Verifica se esistono valori salvati nella configurazione
            host = cfg.hostaddress.value
            port = cfg.port.value
            username = cfg.user.value
            password = cfg.passw.value
            # Controlla se ci sono valori validi
            if host and username and password:
                print(
                    "Loaded config: " +
                    host +
                    ", " +
                    str(port) +
                    ", " +
                    username)
                # Restituisci i valori configurati
                return host, port, username, password
            else:
                print("No valid config found.")
                return None, None, None, None
        except Exception as e:
            print("Error loading config: " + str(e))
            return None, None, None, None

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
        elif sel == ('MAKER BOUQUET'):
            self.session.open(xc_maker)
        elif sel == ('DOWNLOADER'):
            self.taskManager()
        elif sel == ('M3U LOADER'):
            self.session.open(xc_Play)
        elif sel == ('CONFIG'):
            self.config()
        elif sel == ('ABOUT & HELP'):
            self.xc_Help()


timezone_offsets = {
    # Europa
    "Europe/London": 0,          # UTC+0
    "Europe/Berlin": 3600,       # UTC+1
    "Europe/Paris": 3600,        # UTC+1
    "Europe/Rome": 3600,         # UTC+1
    "Europe/Moscow": 10800,      # UTC+3
    "Europe/Athens": 7200,       # UTC+2
    "Europe/Madrid": 3600,       # UTC+1
    "Europe/Lisbon": 0,          # UTC+0
    "Europe/Dublin": 0,          # UTC+0

    # America
    "America/New_York": -18000,  # UTC-5
    "America/Chicago": -21600,   # UTC-6
    "America/Denver": -25200,    # UTC-7
    "America/Los_Angeles": -28800,  # UTC-8
    "America/Toronto": -18000,   # UTC-5
    "America/Sao_Paulo": -10800,  # UTC-3
    "America/Argentina/Buenos_Aires": -10800,  # UTC-3
    "America/Mexico_City": -21600,  # UTC-6
    "America/Phoenix": -25200,   # UTC-7 (no DST)

    # Asia
    "Asia/Tokyo": 32400,         # UTC+9
    "Asia/Shanghai": 28800,      # UTC+8
    "Asia/Hong_Kong": 28800,     # UTC+8
    "Asia/Singapore": 28800,     # UTC+8
    "Asia/Seoul": 32400,         # UTC+9
    "Asia/Dubai": 14400,         # UTC+4
    "Asia/Kolkata": 19800,       # UTC+5:30
    "Asia/Jakarta": 25200,       # UTC+7
    "Asia/Bangkok": 25200,       # UTC+7

    # Africa
    "Africa/Cairo": 7200,        # UTC+2
    "Africa/Johannesburg": 7200,  # UTC+2
    "Africa/Lagos": 3600,        # UTC+1
    "Africa/Casablanca": 0,      # UTC+0
    "Africa/Nairobi": 10800,     # UTC+3

    # Oceania
    "Australia/Sydney": 36000,   # UTC+10
    "Australia/Melbourne": 36000,  # UTC+10
    "Australia/Brisbane": 36000,  # UTC+10 (no DST)
    "Australia/Perth": 28800,    # UTC+8
    "Pacific/Auckland": 43200,   # UTC+12
    "Pacific/Honolulu": -36000,  # UTC-10

    # Altri
    "UTC": 0,                    # UTC+0
    "GMT": 0,                    # UTC+0
    "Etc/GMT": 0,                # UTC+0
    "Etc/GMT+1": -3600,          # UTC-1
    "Etc/GMT+12": -43200,        # UTC-12
    "Etc/GMT-14": 50400,         # UTC+14
}


# Funzione per ottenere l'offset del fuso orario locale
def get_local_offset():
    """Get the local timezone offset (in seconds)"""
    if localtime().tm_isdst == 1:
        return -altzone  # Daylight saving time
    else:
        return -timezone  # Standard time


# Funzione per formattare la differenza di tempo
def format_time_diff(time_diff):
    """Format the time difference in hours, minutes, and seconds"""
    hours, remainder = divmod(time_diff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:02}:{:02}:{:02}".format(hours, minutes, seconds)


# Recupera l'offset locale in secondi
local_offset = get_local_offset()
# Ottieni l'orario corrente in UTC
local_time_utc = datetime.utcnow()
# Calcola l'orario locale sottraendo l'offset
local_time = local_time_utc + timedelta(seconds=local_offset)


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
            print("\n-----------CONFIG START----------")
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

            # globalsxp.timeserver = self.xtream_e2portal_url + '/player_api.php?username=' + str(self.username) + '&password=' + str(self.password)

            print('Host: %s\nUsername: %s\nPassword:%s' %
                  (self.xtream_e2portal_url, self.username, self.password))
            print("-----------CONFIG END----------\n")
            return self.username, self.password
        except Exception as e:
            print("++++++++++ERROR READ CONFIG+++++++++++++ ", e)
            return None, None

    def get_list(self, url=None):
        globalsxp.stream_live = False
        self.url = check_port(url)
        self.list_index = 0
        globalsxp.iptv_list_tmp = []
        root = None
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
        description2 = ''
        description3 = ''
        chan_counter = 0
        try:
            # print("!!!!!!!!-------------------- URL %s" % self.url)
            if '&type' in self.url:
                globalsxp.next_request = 1
            elif "_get" in self.url:
                globalsxp.next_request = 2  # don't use it

            root = self._request(self.url)

            if len(root) > 0:
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
                    vodRating = "0"

                    # Category name
                    title_element = channel.find('title')
                    if title_element is not None and title_element.text is not None:
                        # Passiamo il testo decodificato
                        name = b64decoder(title_element.text)
                        # print('channels: Title:', type(name), name)

                        name = html_conv.html_unescape(name)

                    # Category description
                    description_element = channel.find('description')
                    if description_element is not None and description_element.text is not None:
                        description = b64decoder(
                            description_element.text)  # Passiamo il testo decodificato
                        # print('channels: Description:', type(description), description)

                    # Category desc_image
                    desc_image_id_element = channel.find('desc_image')
                    if desc_image_id_element is not None and desc_image_id_element.text is not None:
                        desc_image = desc_image_id_element.text.strip()
                        if desc_image != "n/A" and desc_image != "":
                            if desc_image.startswith("https"):
                                desc_image = desc_image.replace(
                                    "https", "http")
                            # print('channels:desc_image:', type(desc_image), desc_image)

                    # Category ID
                    category_id_element = channel.find('category_id')
                    if category_id_element is not None and category_id_element.text is not None:
                        category_id = category_id_element.text.strip()
                        # print('channels: Category ID:', type(category_id), category_id)

                    # Category stream_url list channel
                    stream_url_id_element = channel.find('stream_url')
                    if stream_url_id_element is not None and stream_url_id_element.text is not None:
                        globalsxp.stream_url = stream_url_id_element.text.strip()
                    else:
                        print('channels: Stream URL not found or is empty.')

                    # Playlist URL
                    playlist_url_element = channel.find('playlist_url')
                    if playlist_url_element is not None and playlist_url_element.text is not None:
                        playlist_url = playlist_url_element.text

                    # Category piconname
                    piconname_id_element = channel.find('logo')
                    if piconname_id_element is not None and piconname_id_element.text is not None:
                        piconname = piconname_id_element.text
                    if globalsxp.stream_url:
                        globalsxp.isStream = True
                    else:
                        globalsxp.isStream = False

                    # Check if the stream URL contains "/live/"
                    if "/live/" in globalsxp.stream_url:
                        globalsxp.stream_live = True
                        epgnowtime = ''
                        epgnowdescription = ''
                        epgnexttitle = ''
                        epgnexttime = ''
                        epgnextdescription = ''
                        timematch = []
                        titlematch = ''
                        if description != '':
                            # Extract event titles
                            titlematch = findall(
                                r'\[\d{2}:\d{2}\]\s*(.*?)\n', description)
                            # Extract the schedules and descriptions
                            timematch = findall(
                                r'\[(\d{2}:\d{2})\]', description)
                            epgnowdescription = findall(
                                r'\((.*?)\)', description, DOTALL)
                            # print('timematch =', timematch)
                            # print('descriptionmatch =', epgnowdescription)
                            # Get timezone and timestamp from server
                            server_timezone = globalsxp.timezone
                            server_time_str = globalsxp.timeserver
                            server_timestamp = globalsxp.timestamp
                            print(
                                "server_timezone is {}".format(server_timezone))
                            print(
                                "server_time_str is {}".format(server_time_str))
                            print(
                                "server_timestamp is {}".format(server_timestamp))
                            # Convert server timestamp to datetime
                            server_time = datetime.utcfromtimestamp(
                                server_timestamp)
                            print(
                                "Server time converted:",
                                server_time.strftime("%Y-%m-%d %H:%M:%S"))
                            # Calculate the real local time
                            local_time = datetime.now()
                            print(
                                "Local system time:",
                                local_time.strftime("%Y-%m-%d %H:%M:%S"))
                            # Calculate the time difference between server and
                            # local
                            difference_time = local_time - server_time
                            difference_hour = int(
                                difference_time.total_seconds() / 3600)
                            print(
                                "Hour difference (local - server):",
                                difference_hour)
                            # Apply custom offset from cfg
                            try:
                                user_offset = int(cfg.uptimezone.value)
                            except (ValueError, AttributeError):
                                user_offset = 0
                            print("user_offset:", user_offset)
                            final_offset = timedelta(
                                hours=difference_hour + user_offset)
                            print(
                                "Total offset (server + user):", final_offset)
                            # Process events (if at least two times found)
                            if len(timematch) >= 2:
                                time1_str = timematch[0]
                                time2_str = timematch[1]
                                # Convert times to datetime
                                base_date = local_time.date()
                                time1_dt = datetime.strptime(
                                    time1_str, "%H:%M")
                                time2_dt = datetime.strptime(
                                    time2_str, "%H:%M")
                                start_time = datetime.combine(
                                    base_date, time1_dt.time())
                                end_time = datetime.combine(
                                    base_date, time2_dt.time())
                                # If the end time is before the start time
                                # (e.g. 11:00 PM -> 1:00 AM), add a day
                                if end_time <= start_time:
                                    end_time += timedelta(days=1)
                                # Add calculated offset
                                start_time += final_offset
                                end_time += final_offset
                                epgnowtime = "[{}-{}]".format(
                                    start_time.strftime("%H:%M"),
                                    end_time.strftime("%H:%M")
                                )
                                print(
                                    "Adjusted Event Time EPG Format:", epgnowtime)
                            else:
                                print(
                                    "There are not enough times found to calculate the duration.")

                        # Process the next event (if any)
                        if len(timematch) > 1:
                            next_time_str = timematch[1].strip()
                            try:
                                # Combines the current date with the time of
                                # the next event
                                next_event_time = datetime.strptime(
                                    local_time.strftime('%Y-%m-%d') + " " + next_time_str, "%Y-%m-%d %H:%M")
                                # Apply local offset
                                next_event_time_utc = next_event_time - \
                                    timedelta(seconds=local_offset)
                                # If the event is in the past, add a day
                                if next_event_time_utc < local_time_utc:
                                    next_event_time_utc += timedelta(days=1)
                                    print("Next event is scheduled for tomorrow.")
                                # Calculate the difference from the current
                                # time (time remaining)
                                time_diff_next = next_event_time_utc - local_time_utc
                                # Calculate the duration of the next event
                                time1_utc_plus1 = datetime.strptime(
                                    timematch[0], "%H:%M")
                                time2_utc_plus1 = datetime.strptime(
                                    timematch[1], "%H:%M")
                                diff = (
                                    time2_utc_plus1 - time1_utc_plus1).total_seconds() / 60
                                # Calculate the end time of the event
                                end_time_utc = next_event_time_utc + \
                                    timedelta(minutes=diff)
                                end_time_str_utc = end_time_utc.strftime(
                                    "%H:%M")
                                epgnexttime = "[{}-{}]".format(
                                    next_event_time_utc.strftime("%H:%M"),
                                    end_time_str_utc
                                )
                                print(
                                    "Next Event Adjusted Time (UTC):", epgnexttime)
                                print(
                                    "Time Difference for Next Event:",
                                    format_time_diff(time_diff_next))

                            except ValueError as e:
                                print(
                                    "Error: Invalid next event time format. Details:", e)

                            epgnexttitle = titlematch[1].strip() if len(
                                titlematch) > 1 else ''
                            epgnextdescription = epgnowdescription[1].strip() if len(
                                epgnowdescription) > 1 else ''
                            # print('epgnexttitle:', epgnexttitle)
                            # print('epgnextdescription:', epgnextdescription)
                            description = html_conv.html_unescape(
                                epgnowdescription[1] if len(epgnowdescription) > 1 else '') + '\n\n'
                            description2 = epgnexttime + ' ' + epgnexttitle + '\n\n' + epgnextdescription

                    elif ("/movie/" in globalsxp.stream_url) or ("/series/" in globalsxp.stream_url) or ("vod_streams" in globalsxp.stream_url):
                        # print('movie globalsxp.stream_url==================================', globalsxp.stream_url)
                        globalsxp.stream_live = False

                        def parse_description(description_b64):
                            decoded = b64decoder(description_b64)
                            info = {}
                            for line in decoded.splitlines():
                                if ":" in line:
                                    key, value = line.split(":", 1)
                                    info[key.strip()] = value.strip()
                            return info

                        # Estrazione dai tag XML
                        NAME = channel.find("title").text if channel.find(
                            "title") is not None else ""
                        O_NAME = channel.find("O_NAME").text if channel.find(
                            "O_NAME") is not None else ""
                        COVER_BIG = channel.find("desc_image").text if channel.find(
                            "desc_image") is not None else ""
                        DESCRIPTION = channel.find("description").text if channel.find(
                            "description") is not None else ""
                        PLOT = channel.find("PLOT").text if channel.find(
                            "PLOT") is not None else ""
                        DURATION = channel.find("DURATION").text if channel.find(
                            "DURATION") is not None else ""
                        GENRE = channel.find("GENRE").text if channel.find(
                            "GENRE") is not None else ""
                        RELEASEDATE = channel.find("RELEASEDATE").text if channel.find(
                            "RELEASEDATE") is not None else ""
                        RATING = channel.find("RATING").text if channel.find(
                            "RATING") is not None else ""

                        # Decodifica e parsing avanzato se DESCRIPTION esiste
                        metadata = {}
                        if DESCRIPTION:
                            metadata = parse_description(DESCRIPTION)

                        # Titolo
                        if "NAME" in metadata:
                            vodTitle = metadata["NAME"]
                        elif NAME:
                            vodTitle = b64decoder(NAME)
                        elif O_NAME:
                            vodTitle = b64decoder(O_NAME)
                        else:
                            vodTitle = name  # fallback

                        # Picon
                        piconname = COVER_BIG if COVER_BIG else ""

                        # Descrizione
                        if "DESCRIPTION" in metadata:
                            vodDescription = metadata["DESCRIPTION"]
                        elif "PLOT" in metadata:
                            vodDescription = metadata["PLOT"]
                        elif DESCRIPTION:
                            vodDescription = b64decoder(DESCRIPTION)
                        elif PLOT:
                            vodDescription = b64decoder(PLOT)
                        else:
                            vodDescription = "DESCRIPTION: -- --"

                        # Altri campi disponibili
                        vodGenre = metadata.get("GENRE", GENRE)
                        vodRating = metadata.get("RATING", RATING)
                        vodDirector = metadata.get("DIRECTOR", "")
                        vodTrailer = metadata.get("YOUTUBE_TRAILER", "")
                        vodDuration = metadata.get("DURATION", DURATION)
                        vodReleaseDate = metadata.get(
                            "RELEASEDATE", RELEASEDATE)

                        description3 = (
                            str(vodTitle) + "\n\n" +
                            str(vodDescription) + "\n\n" +
                            "Genre: " + str(vodGenre) + "\n" +
                            "Duration: " + str(vodDuration) + "\n" +
                            "Release: " + str(vodReleaseDate) + "\n" +
                            "Rating: " + str(vodRating) + "\n" +
                            "Director: " + str(vodDirector) + "\n" +
                            "Trailer: " + str(vodTrailer)
                        )

                        description = html_conv.html_unescape(description3)
                        # print('vodDescription: ', vodDescription)
                        # print('channels name: ', name)
                        # print('channels description:', description)

                    chan_tulpe = (
                        str(chan_counter),
                        str(name),
                        description,
                        str(piconname),
                        globalsxp.stream_url,
                        playlist_url,
                        category_id,
                        str(desc_image),
                        str(description2),
                        str(vodRating)
                    )
                    globalsxp.iptv_list_tmp.append(chan_tulpe)
                    globalsxp.btnsearch = globalsxp.next_request

        except Exception as e:
            print('----- get_list failed: ', e)

        if len(globalsxp.iptv_list_tmp):
            self.iptv_list = globalsxp.iptv_list_tmp
            globalsxp.iptv_list = self.iptv_list
        return

    def _request(self, url):
        if "exampleserver" not in str(cfg.hostaddress.value):
            TYPE_PLAYER = '/enigma2.php'
            # TYPE_PLAYER = '/player_api.php'
            url = url.strip(" \t\n\r")
            if globalsxp.next_request == 1:
                url = check_port(url)
                if not url.find(":"):
                    self.port = str(cfg.port.value)
                    full_url = self.xtream_e2portal_url + ':' + self.port
                    url = url.replace(self.xtream_e2portal_url, full_url)
            else:
                url = url + TYPE_PLAYER + "?" + "username=" + \
                    self.username + "&password=" + self.password
            globalsxp.urlinfo = url
            try:
                # Effettua la richiesta HTTP
                res = make_request(globalsxp.urlinfo)
                if res is not None:
                    try:
                        res_xml = fromstring(res)
                        if res_xml is not None:
                            res_string = tostring(
                                res_xml, encoding='utf-8', method='xml').decode('utf-8')
                            file_path = join('/tmp', 'canali_temp.xml')
                            with open(file_path, 'w') as temp_file:
                                temp_file.write(res_string)
                                temp_file.flush()
                                globalsxp.temp_prev_list = res_string
                            return res_xml
                    except Exception as e:
                        print("Error during XML parsing: " + str(e))
                        return None
                else:
                    print("Request failed or no content received.")
                    return None
            except Exception as e:
                print("Error during request or XML processing: " + str(e))
                return None


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


def check_configuring():
    if cfg.autobouquetupdate.value is True:
        """Check for new config values for auto start"""
        if globalsxp.autoStartTimer is not None:
            globalsxp.autoStartTimer.update()
        return


def get_next_wakeup():
    return -1


mainDescriptor = PluginDescriptor(
    name="XCplugin Forever",
    description=version,
    where=PluginDescriptor.WHERE_MENU,
    fnc=menu)


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
