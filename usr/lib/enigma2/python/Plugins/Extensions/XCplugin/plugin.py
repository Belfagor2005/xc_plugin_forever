#!/usr/bin/python
# -*- coding: utf-8 -*-


'''
****************************************
*        coded by Lululla              *
*             skin by MMark            *
*  update     02/06/2024               *
*       Skin by MMark                  *
****************************************
#--------------------#
'''
from __future__ import print_function
from . import _, paypal
from . import Utils
from . import html_conv
import codecs
from Components.AVSwitch import AVSwitch
try:
    from Components.AVSwitch import iAVSwitch
except Exception as e:
    print(e)

try:
    from enigma import eAVSwitch
except Exception:
    from enigma import eAVControl as eAVSwitch
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.config import ConfigSubsection, config, ConfigYesNo
from Components.config import ConfigEnableDisable
from Components.config import ConfigSelectionNumber, ConfigClock
from Components.config import ConfigSelection, getConfigListEntry, NoSave
from Components.config import ConfigText, ConfigDirectory
from Components.config import ConfigPassword  # , configfile
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from Components.MultiContent import MultiContentEntryPixmapAlphaTest
from Components.Pixmap import Pixmap
from Components.ProgressBar import ProgressBar
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.Task import Task, Condition, Job, job_manager as JobManager
from Plugins.Plugin import PluginDescriptor
from Screens.Console import Console
# from Screens.InfoBar import MoviePlayer
from Screens.Standby import Standby
from Screens.InfoBarGenerics import InfoBarSubtitleSupport, \
    InfoBarMenu, InfoBarSeek, InfoBarNotifications, \
    InfoBarAudioSelection
from Screens.LocationBox import LocationBox
from Screens.MessageBox import MessageBox
from Screens.MovieSelection import MovieSelection
from Screens.Screen import Screen
from Screens.TaskView import JobView
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools.Directories import SCOPE_PLUGINS
from Tools.Directories import resolveFilename
from Tools.Downloader import downloadWithProgress
from enigma import RT_HALIGN_CENTER, RT_VALIGN_CENTER
from enigma import RT_HALIGN_LEFT
# from enigma import gPixmapPtr
from enigma import eTimer
from enigma import eListboxPythonMultiContent
from enigma import eServiceReference
from enigma import ePicLoad
from enigma import gFont
from enigma import iPlayableService
from enigma import loadPNG
from enigma import getDesktop
from os import listdir, remove, system
from os.path import splitext
from os.path import exists as file_exists
from twisted.web.client import downloadPage
import base64
import os
import re
import six
import socket
import sys
import time


# try:
    # from xml.etree.cElementTree import ElementTree, fromstring
# except ImportError:
    # from xml.etree.ElementTree import ElementTree, fromstring
try:
    from xml.etree.cElementTree import fromstring
except ImportError:
    from xml.etree.ElementTree import fromstring
global STREAMS, piclogo, pictmp, skin_path
global isStream, btnsearch, eserv, re_search
global series, urlinfo
_session = " "
version = "XC Forever V.3.0"
plugin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('XCplugin'))
iconpic = os.path.join(plugin_path, 'plugin.png')
filterlist = os.path.join(plugin_path, 'cfg/filterlist.txt')
enigma_path = '/etc/enigma2/'
epgimport_path = '/etc/epgimport/'
pictmp = "/tmp/poster.jpg"
xc_list = "/tmp/xc.txt"
iptvsh = "/etc/enigma2/iptv.sh"
iptv_list_tmp = []
re_search = False
series = False
isStream = False
btnsearch = 0
next_request = 0
stream_url = ""
urlinfo = ""
pythonVer = sys.version_info.major
PY3 = False
if pythonVer == 3:
    PY3 = True
if PY3:
    from urllib.request import urlopen, Request
    from urllib.parse import urlparse
else:
    from urllib2 import urlopen, Request
    from urlparse import urlparse

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

modelive = [("1", "Dvb(1)"), ("4097", "IPTV(4097)")]
modemovie = [("4097", "IPTV(4097)")]
if file_exists("/usr/bin/gstplayer"):
    modelive.append(("5001", "Gstreamer(5001)"))
    modemovie.append(("5001", "Gstreamer(5001)"))
if file_exists("/usr/bin/exteplayer3"):
    modelive.append(("5002", "Exteplayer3(5002)"))
    modemovie.append(("5002", "Exteplayer3(5002)"))
if file_exists('/var/lib/dpkg/info'):
    modelive.append(("8193", "eServiceUri(8193)"))
    modemovie.append(("8193", "eServiceUri(8193)"))


def clear_caches():
    try:
        os.system("echo 1 > /proc/sys/vm/drop_caches")
        os.system("echo 2 > /proc/sys/vm/drop_caches")
        os.system("echo 3 > /proc/sys/vm/drop_caches")
    except:
        pass


# kiddac solution
def defaultMoviePath():
    result = config.usage.default_path.value
    if not os.path.isdir(result):
        from Tools import Directories
        return Directories.defaultRecordingLocation(config.usage.default_path.value)
    return result


if not os.path.isdir(config.movielist.last_videodir.value):
    try:
        config.movielist.last_videodir.value = defaultMoviePath()
        config.movielist.last_videodir.save()
    except:
        pass

config.plugins.XCplugin = ConfigSubsection()
cfg = config.plugins.XCplugin
cfg.LivePlayer = ConfigEnableDisable(default=False)
cfg.autobouquetupdate = ConfigEnableDisable(default=False)
cfg.autoupdate = ConfigEnableDisable(default=False)
cfg.badcar = ConfigEnableDisable(default=False)
cfg.bouquettop = ConfigSelection(default="Bottom", choices=["Bottom", "Top"])
cfg.data = ConfigYesNo(default=False)
cfg.fixedtime = ConfigClock(default=0)
cfg.hostaddress = ConfigText(default="exampleserver.com")
cfg.infoexp = ConfigYesNo(default=False)
cfg.infoname = NoSave(ConfigText(default="myBouquet"))
cfg.last_update = ConfigText(default="Never")
cfg.live = ConfigSelection(default='1', choices=modelive)
cfg.passw = ConfigPassword(default="******", fixed_size=False, censor="*")
cfg.pdownmovie = ConfigSelection(default="JobManager", choices=["JobManager", "Direct", "Requests"])
cfg.picons = ConfigEnableDisable(default=False)
cfg.port = ConfigText(default="80", fixed_size=False)
cfg.pthmovie = ConfigDirectory(default=config.movielist.last_videodir.value)
cfg.pthpicon = ConfigDirectory(default="/media/hdd/picon")
cfg.pthxmlfile = ConfigDirectory(default="/etc/enigma2/xc")
cfg.screenxl = ConfigEnableDisable(default=False)
cfg.services = ConfigSelection(default='4097', choices=modemovie)
cfg.strtmain = ConfigEnableDisable(default=True)
cfg.timeout = ConfigSelectionNumber(default=10, min=5, max=80, stepwidth=5)
cfg.timetype = ConfigSelection(default="interval", choices=[("interval", _("interval")), ("fixed time", _("fixed time"))])
cfg.typelist = ConfigSelection(default="Multi Live & VOD", choices=["Multi Live & VOD", "Multi Live/Single VOD", "Combined Live/VOD"])
cfg.typem3utv = ConfigSelection(default="MPEGTS to TV", choices=["M3U to TV", "MPEGTS to TV"])
cfg.updateinterval = ConfigSelectionNumber(default=24, min=1, max=48, stepwidth=1)
cfg.user = ConfigText(default="Enter_Username", visible_width=50, fixed_size=False)


screenwidth = getDesktop(0).size()
if screenwidth.width() == 2560:
    CHANNEL_NUMBER = [3, 4, 120, 60, 0]
    CHANNEL_NAME = [130, 4, 1800, 60, 1]
    FONT_0 = ("Regular", 52)
    FONT_1 = ("Regular", 52)
    BLOCK_H = 80
    skin_path = os.path.join(plugin_path, 'skin/uhd')
    piclogo = os.path.join(plugin_path, 'skin/uhd/iptvlogo.jpg')
elif screenwidth.width() == 1920:
    CHANNEL_NUMBER = [3, 0, 100, 50, 0]
    CHANNEL_NAME = [110, 0, 1200, 50, 1]
    FONT_0 = ("Regular", 32)
    FONT_1 = ("Regular", 32)
    BLOCK_H = 50
    skin_path = os.path.join(plugin_path, 'skin/fhd')
    piclogo = os.path.join(plugin_path, 'skin/fhd/iptvlogo.jpg')
else:
    CHANNEL_NUMBER = [3, 0, 50, 40, 0]
    CHANNEL_NAME = [75, 0, 900, 40, 1]
    FONT_0 = ("Regular", 24)
    FONT_1 = ("Regular", 24)
    BLOCK_H = 40
    skin_path = os.path.join(plugin_path, 'skin/hd')
    piclogo = os.path.join(plugin_path, 'skin/hd/iptvlogo.jpg')

if file_exists('/var/lib/dpkg/info'):
    skin_path = skin_path + '/dreamOs'


def copy_poster():
    system("cd / && cp -f " + piclogo + " " + pictmp)


global Path_Movies
global Path_Movies2
global infoname
copy_poster()
eserv = int(cfg.services.value)
infoname = str(cfg.infoname.value)
ntimeout = float(cfg.timeout.value)
socket.setdefaulttimeout(5)
Path_Movies = str(cfg.pthmovie.value) + "/"
Path_Movies2 = Path_Movies
Path_Picons = str(cfg.pthpicon.value) + "/"
Path_XML = str(cfg.pthxmlfile.value) + "/"


def check_port(url):
    line = url.strip()
    protocol = 'http://'
    domain = ''
    port = ''
    if str(cfg.port.value) != '80':
        port = str(cfg.port.value)
    else:
        port = '80'
    host = ''
    urlsplit1 = line.split("/")
    protocol = urlsplit1[0] + "//"
    if len(urlsplit1) > 2:
        domain = urlsplit1[2].split(':')[0]
        if len(urlsplit1[2].split(':')) > 1:
            port = urlsplit1[2].split(':')[1]
    host = "%s%s:%s" % (protocol, domain, port)
    if not url.startswith(host):
        url = str(url.replace(protocol + domain, host))
    return url


def returnIMDB(text_clear):
    TMDB = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('TMDB'))
    IMDb = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('IMDb'))
    if file_exists(TMDB):
        try:
            from Plugins.Extensions.TMBD.plugin import TMBD
            text = html_conv.html_unescape(text_clear)
            _session.open(TMBD.tmdbScreen, text, 0)
        except Exception as e:
            print("[XCF] Tmdb: ", e)
        return True
    elif file_exists(IMDb):
        try:
            from Plugins.Extensions.IMDb.plugin import main as imdb
            text = html_conv.html_unescape(text_clear)
            imdb(_session, text)
        except Exception as e:
            print("[XCF] imdb: ", e)
        return True
    # else:
        # text_clear = html_conv.html_unescape(text_clear)
        # _session.open(MessageBox, text_clear, MessageBox.TYPE_INFO)
        # return True
    return False


EXTENSIONS = {
    "mts": "movie",
    "m2ts": "movie",
    "pls": "music",
    "vdr": "movie",
    "vob": "movie",
    "ogm": "movie",
    "wmv": "movie",
    "ts": "movie",
    "avi": "movie",
    "divx": "movie",
    "mpg": "movie",
    "mpeg": "movie",
    "mkv": "movie",
    "mp4": "movie",
    "mov": "movie",
    "trp": "movie",
    "m4v": "movie",
    "flv": "movie",
    "m3u8": "movie"}


EXTDOWN = {
    ".avi": "movie",
    ".divx": "movie",
    ".mpg": "movie",
    ".mpeg": "movie",
    ".mkv": "movie",
    ".mov": "movie",
    ".m4v": "movie",
    ".flv": "movie",
    ".m3u8": "movie",
    ".relinker": "movie",
    ".mp4": "movie"}


class xc_home(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        skin = os.path.join(skin_path, 'xc_home.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setup_title = ('MAIN MENU')
        self.list = []
        self["Text"] = Label("")
        self["version"] = Label(version)
        self['text'] = xcM3UList([])
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
            "help": self.helpx,
            "menu": self.config,
            "movielist": self.taskManager,
            "2": self.showMovies,
            "pvr": self.showMovies,
            "showMediaPlayer": self.showMovies,
            "info": self.helpx}, -1)
        self.onFirstExecBegin.append(self.check_dependencies)
        self.onLayoutFinish.append(self.updateMenuList)

    def check_dependencies(self):
        dependencies = True
        try:
            pythonFull = float(str(sys.version_info.major) + "." + str(sys.version_info.minor))
            print("***** python version *** %s" % pythonFull)
            if pythonFull < 3.9:
                print("*** checking multiprocessing ***")
        except Exception as e:
            print("**** missing dependencies ***")
            print(e)
            dependencies = False

        if dependencies is False:
            os.chmod(os.path.join(plugin_path, 'dependencies.sh', 0o0755))
            cmd1 = ". /usr/lib/enigma2/python/Plugins/Extensions/XCplugin/dependencies.sh"
            self.session.openWithCallback(self.start, Console, title="Checking Dependencies", cmdlist=[cmd1], closeOnSuccess=True)
        else:
            self.start()

    def start(self):
        Utils.OnclearMem()

    def config(self):
        self.session.open(xc_config)

    def button_ok(self):
        self.keyNumberGlobalCB(self['text'].getSelectedIndex())

    def exitY(self):
        Utils.ReloadBouquets()
        self.close()

    def Team(self):
        self.session.open(OpenServer)

    def helpx(self):
        self.session.open(xc_help)

    def taskManager(self):
        self.session.open(xc_StreamTasks)

    def xcPlay(self):
        self.session.open(xc_Play)

    def showMovies(self):
        try:
            self.session.open(MovieSelection)
        except:
            pass

    def OpenList(self):
        global STREAMS
        STREAMS = iptv_streamse()
        STREAMS.read_config()
        if "exampleserver.com" not in STREAMS.xtream_e2portal_url:
            STREAMS.get_list(STREAMS.xtream_e2portal_url)
            self.session.openWithCallback(check_configuring, xc_Main)
        else:
            message = (_("First Select the list or enter it in Config"))
            Utils.web_info(message)

    def updateMenuList(self):
        global infoname
        self.menu_list = []
        for x in self.menu_list:
            del self.menu_list[0]
        list = []
        for x in Panel_list:
            list.append(xcm3ulistEntry(x))
            self.menu_list.append(x)
        self['text'].setList(list)
        infoname = str(STREAMS.playlistname)
        if cfg.infoexp.getValue:
            if str(cfg.infoname.value) != 'myBouquet':
                infoname = str(cfg.infoname.value)
        self["Text"].setText(infoname)

    def keyNumberGlobalCB(self, idx):
        sel = self.menu_list[idx]
        if sel == ('HOME'):
            self.OpenList()
        elif sel == ('PLAYLIST'):
            self.session.open(OpenServer)
        elif sel == ('MAKER BOUQUET'):
            self.session.open(xc_maker)
        elif sel == ('MOVIE'):
            self.taskManager()
        elif sel == ('PLAYER UTILITY'):
            self.session.open(xc_Play)
        elif sel == ('CONFIG'):
            self.session.open(xc_config)
        elif sel == ('ABOUT & HELP'):
            self.session.open(xc_help)


class xc_config(Screen, ConfigListScreen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        skin = os.path.join(skin_path, 'xc_config.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setup_title = ('XCplugin Forever')
        self.list = []
        self.onChangedEntry = []
        self["playlist"] = Label("Xstream Code Setup")
        self["version"] = Label(version)
        self['statusbar'] = Label()
        self["description"] = Label("")
        self["key_red"] = Label(_("Back"))
        self["key_green"] = Label(_("Save"))
        self["key_blue"] = Label(_("Import") + " txt")
        self["key_yellow"] = Label(_("Import") + " sh")
        self["actions"] = HelpableActionMap(self, "XCpluginActions", {
            "home": self.extnok,
            "cancel": self.extnok,
            "left": self.keyLeft,
            "right": self.keyRight,
            "up": self.keyUp,
            "down": self.keyDown,
            "help": self.helpx,
            "yellow": self.iptv_sh,
            "green": self.cfgok,
            "blue": self.ImportInfosServer,
            "showVirtualKeyboard": self.KeyText,
            "ok": self.ok
        }, -1)
        self.update_status()
        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)
        self.createSetup()
        self.showhide()
        self.onLayoutFinish.append(self.layoutFinished)

    def iptv_sh(self, answer=None):
        if answer is None:
            self.session.openWithCallback(self.iptv_sh, MessageBox, _("Import Server from /ect/enigma2/iptv.sh?"))
        elif answer:
            if file_exists(iptvsh) and os.stat(iptvsh).st_size > 0:
                with open(iptvsh, 'r') as f:
                    fpage = f.read()
                regexcat = 'USERNAME="(.*?)".*?PASSWORD="(.*?)".*?url="http://(.*?):(.*?)/get.php.*?'
                match = re.compile(regexcat, re.DOTALL).findall(fpage)
                for usernamesh, passwordsh, urlsh, ports in match:
                    urlsh = urlsh.replace('"', '')
                    usernamesh = usernamesh.replace('"', '')
                    passwordsh = passwordsh.replace('"', '')
                    cfg.hostaddress.setValue(urlsh)
                    cfg.port.setValue(ports)
                    cfg.user.setValue(usernamesh)
                    cfg.passw.setValue(passwordsh)
                self.xml_plugin()
                # filesave = "xc_" + str(cfg.user.value) + ".xml"
                # self.session.open(MessageBox, _("File saved to %s !" % filesave), MessageBox.TYPE_INFO, timeout=5)
                self.ConfigText()
                self.createSetup()
            else:
                self.session.open(MessageBox, (_("Missing %s !") % iptvsh), MessageBox.TYPE_INFO, timeout=4)
        else:
            return

    def ImportInfosServer(self, answer=None):
        if answer is None:
            self.session.openWithCallback(self.ImportInfosServer, MessageBox, _("Import Server from /tmp/xc.tx?"))
        elif answer:
            if file_exists(xc_list) and os.stat(xc_list).st_size > 0:
                with codecs.open(xc_list, "r", encoding="utf-8") as f:
                    chaine = f.readlines()
                url = chaine[0].replace("\n", "").replace("\t", "").replace("\r", "")
                port = chaine[1].replace("\n", "").replace("\t", "").replace("\r", "").replace(":", "_")
                user = chaine[2].replace("\n", "").replace("\t", "").replace("\r", "").replace(":", "_")
                pswrd = chaine[3].replace("\n", "").replace("\t", "").replace("\r", "")
                cfg.hostaddress.setValue(url)
                cfg.port.setValue(port)
                cfg.user.setValue(user)
                cfg.passw.setValue(pswrd)
                self.xml_plugin()
                # filesave = "xc_" + str(cfg.user.value) + ".xml"
                # self.session.open(MessageBox, _("File saved to %s !" % filesave), MessageBox.TYPE_INFO, timeout=5)
                self.ConfigText()
                self.createSetup()
            else:
                self.session.open(MessageBox, _("File not found %s" % xc_list), MessageBox.TYPE_INFO, timeout=5)
        else:
            return

    def update_status(self):
        if cfg.autobouquetupdate:
            self['statusbar'].setText(_("Last channel update: %s") % cfg.last_update.value)

    def layoutFinished(self):
        self.setTitle(self.setup_title)

    def helpx(self):
        self.session.open(xc_help)

    def createSetup(self):
        self.editListEntry = None
        self.list = []
        indent = "- "

        self.list.append(getConfigListEntry(_("Data Server Configuration:"), cfg.data, (_("Your Server Login and data input"))))
        if cfg.data.getValue():
            # self.list.append(getConfigListEntry(_("Old/New panel"), cfg.panel, (_("Select Panel used"))))
            self.list.append(getConfigListEntry(indent + (_("Server URL")), cfg.hostaddress, (_("Enter Server Url without 'http://' your_domine"))))
            self.list.append(getConfigListEntry(indent + (_("Server PORT")), cfg.port, (_("Enter Server Port Eg.:'8080'"))))
            self.list.append(getConfigListEntry(indent + (_("Server Username")), cfg.user, (_("Enter Username"))))
            self.list.append(getConfigListEntry(indent + (_("Server Password")), cfg.passw, (_("Enter Password"))))
        self.list.append(getConfigListEntry(_("Server Timeout"), cfg.timeout, (_("Timeout Server (sec)"))))

        self.list.append(getConfigListEntry(_("Folder user file .xml"), cfg.pthxmlfile, (_("Configure folder containing .xml files\nPress 'OK' to change location."))))
        self.list.append(getConfigListEntry(_("Media Folder "), cfg.pthmovie, (_("Configure folder containing movie/media files\nPress 'OK' to change location."))))

        # self.list.append(getConfigListEntry(_("Show/Hide Live Channel "), cfg.showlive, (_("Show/Hide Live Channel"))))
        # if cfg.showlive.value is True:
        self.list.append(getConfigListEntry(_("Main Screen XL"), cfg.screenxl, (_("Active Main Screen Large"))))
        self.list.append(getConfigListEntry(_("LivePlayer Active "), cfg.LivePlayer, (_("Live Player for Stream .ts: set No for Record Live"))))
        if cfg.LivePlayer.value is True:
            self.list.append(getConfigListEntry(indent + (_("Live Services Type")), cfg.live, (_("Configure service Reference Dvb-Iptv-Gstreamer-Exteplayer3"))))

        self.list.append(getConfigListEntry(_("Download Type "), cfg.pdownmovie, (_("Configure type of download movie: JobManager/Direct."))))

        self.list.append(getConfigListEntry(_("Filter Bad Tag"), cfg.badcar, (_("Filter Bad Tag"))))

        self.list.append(getConfigListEntry(_("Bouquet style "), cfg.typelist, (_("Configure the type of conversion in the favorite list"))))
        if cfg.typelist.value == "Combined Live/VOD":
            self.list.append(getConfigListEntry(indent + (_("Conversion type Output ")), cfg.typem3utv, (_("Configure type of stream to be downloaded by conversion"))))

        self.list.append(getConfigListEntry(_("Vod Services Type"), cfg.services, (_("Configure service Reference Iptv-Gstreamer-Exteplayer3"))))

        self.list.append(getConfigListEntry(_("Name Bouquet Configuration:"), cfg.infoexp, (_("Set Name for MakerBouquet"))))
        if cfg.infoexp.getValue():
            self.list.append(getConfigListEntry(indent + (_("Name Bouquet Export")), cfg.infoname, (_("Configure name of exported bouquet. Default is myBouquet"))))

        self.list.append(getConfigListEntry(_("Place IPTV bouquets at "), cfg.bouquettop, (_("Configure to place the bouquets of the converted lists"))))

        self.list.append(getConfigListEntry(_("Automatic bouquet update (schedule):"), cfg.autobouquetupdate, (_("Active Automatic Bouquet Update"))))
        if cfg.autobouquetupdate.getValue():
            self.list.append(getConfigListEntry(indent + (_("Schedule type:")), cfg.timetype, (_("At an interval of hours or at a fixed time"))))
            if cfg.timetype.value == "interval":
                self.list.append(getConfigListEntry(2 * indent + (_("Update interval (hours):")), cfg.updateinterval, (_("Configure every interval of hours from now"))))
            if cfg.timetype.value == "fixed time":
                self.list.append(getConfigListEntry(2 * indent + (_("Time to start update:")), cfg.fixedtime, (_("Configure at a fixed time"))))
        self.list.append(getConfigListEntry(_("Picons IPTV "), cfg.picons, (_("Download Picons ?"))))
        if cfg.picons.value:
            self.list.append(getConfigListEntry(indent + (_("Picons IPTV bouquets to ")), cfg.pthpicon, (_("Configure folder containing picons files\nPress 'OK' to change location."))))
        self.list.append(getConfigListEntry(_("Auto Update Plugin "), cfg.autoupdate, (_("Set ON for Auto Update Plugin"))))
        self.list.append(getConfigListEntry(_("Link in Main Menu "), cfg.strtmain, (_("Display XCplugin in Main Menu"))))

        self["config"].list = self.list
        self["config"].l.setList(self.list)
        self.setInfo()

    def setInfo(self):
        try:
            sel = self['config'].getCurrent()[2]
            if sel:
                self['description'].setText(str(sel))
            else:
                self['description'].setText(_('SELECT YOUR CHOICE'))
            return
        except Exception as e:
            print("Error ", e)

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()

    def getCurrentEntry(self):
        return self["config"].getCurrent()[0]

    def showhide(self):
        pass

    def getCurrentValue(self):
        return str(self["config"].getCurrent()[1].getText())

    def createSummary(self):
        from Screens.Setup import SetupSummary
        return SetupSummary

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.createSetup()
        self.showhide()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.createSetup()
        self.showhide()

    def keyDown(self):
        self['config'].instance.moveSelection(self['config'].instance.moveDown)
        self.createSetup()
        self.showhide()

    def keyUp(self):
        self['config'].instance.moveSelection(self['config'].instance.moveUp)
        self.createSetup()
        self.showhide()

    def ok(self):
        sel = self["config"].getCurrent()[1]
        if sel and sel == cfg.pthmovie:
            self.setting = "pthmovie"
            self.openDirectoryBrowser(cfg.pthmovie.value, self.setting)
        if sel and sel == cfg.pthxmlfile:
            self.setting = "pthxmlfile"
            self.openDirectoryBrowser(Path_XML, self.setting)
        if sel and sel == cfg.pthpicon:
            self.setting = "pthpicon"
            self.openDirectoryBrowser(cfg.pthpicon.value, self.setting)
        else:
            pass

    def openDirectoryBrowser(self, path, itemcfg):
        if file_exists("/usr/bin/apt-get"):
            path = None
        if itemcfg == "pthmovie":
            try:
                self.session.openWithCallback(
                    self.openDirectoryBrowserCB,
                    LocationBox,
                    windowTitle=_("Choose Directory:"),
                    text=_("Choose directory"),
                    currDir=str(path),
                    bookmarks=config.movielist.videodirs,
                    autoAdd=True,
                    editDir=True,
                    inhibitDirs=["/bin", "/boot", "/dev", "/home", "/lib", "/proc", "/run", "/sbin", "/sys", "/var"])
                    # minFree=15)
            except Exception as e:
                print("openDirectoryBrowser get failed: ", e)
        elif itemcfg == "pthxmlfile":
            try:
                self.session.openWithCallback(
                    self.openDirectoryBrowserCD,
                    LocationBox,
                    windowTitle=_("Choose Directory:"),
                    text=_("Choose directory"),
                    currDir=str(path),
                    bookmarks=config.movielist.videodirs,
                    autoAdd=True,
                    editDir=True,
                    inhibitDirs=["/bin", "/boot", "/dev", "/home", "/lib", "/proc", "/run", "/sbin", "/sys", "/var"])
                    # minFree=15)

            except Exception as e:
                print("openDirectoryBrowser get failed: ", e)
        elif itemcfg == "pthpicon":
            try:
                self.session.openWithCallback(
                    self.openDirectoryBrowserCE,
                    LocationBox,
                    windowTitle=_("Choose Directory:"),
                    text=_("Choose directory"),
                    currDir=str(path),
                    bookmarks=config.movielist.videodirs,
                    autoAdd=True,
                    editDir=True,
                    inhibitDirs=["/bin", "/boot", "/dev", "/home", "/lib", "/proc", "/run", "/sbin", "/sys", "/var"])
                    # minFree=15)
            except Exception as e:
                print("openDirectoryBrowser get failed: ", e)
        # ConfigListScreen.keyOK(self)

    def openDirectoryBrowserCB(self, path):
        if path is not None:
            cfg.pthmovie.setValue(path)
        return

    def openDirectoryBrowserCD(self, path):
        if path is not None:
            cfg.pthxmlfile.setValue(path)
        return

    def openDirectoryBrowserCE(self, path):
        if path is not None:
            cfg.pthpicon.setValue(path)
        return

    def cfgok(self):
        if cfg.picons.value:
            if not file_exists(cfg.picons.value):
                self.session.open(MessageBox, _("%s NOT DETECTED!" % cfg.picons.value), MessageBox.TYPE_INFO, timeout=4)
                return
        if cfg.pthxmlfile.value:
            if not file_exists(cfg.pthxmlfile.value):
                self.session.open(MessageBox, _("%s NOT DETECTED!" % cfg.pthxmlfile.value), MessageBox.TYPE_INFO, timeout=4)
                return
        if cfg.pthmovie.value:
            if not file_exists(cfg.pthmovie.value):
                self.session.open(MessageBox, _("%s NOT DETECTED!" % cfg.pthmovie.value), MessageBox.TYPE_INFO, timeout=4)
                return
        self.save()

    def save(self):
        if self["config"].isChanged():
            for x in self["config"].list:
                x[1].save()
            self.xml_plugin()
            self.session.open(MessageBox, _("Settings saved successfully !"), MessageBox.TYPE_INFO, timeout=5)
        self.close()

    def xml_plugin(self):
        try:
            if str(cfg.user.value) != 'Enter_Username':
                usernames = 'None'
                if os.path.exists(Path_XML + '/xclink.txt'):
                    with codecs.open(Path_XML + '/xclink.txt', "r+", encoding="utf-8") as f:
                        lines = f.readlines()
                        # f.seek(0)
                        # f.close()
                        for line in lines:
                            if line.startswith('#'):
                                continue
                            if line.startswith('http'):
                                pattern = r"http://([^:/]+)(?::(\d+))?/get.php\?username=([^&]+)&password=([^&]+)&type=([^&]+)"  # &output=([^&]+)"
                                match = re.match(pattern, line)
                                if match:
                                    usernames = match.group(3)

                        if str(usernames) in str(cfg.user.value) and str(usernames) != 'None':
                            print('===>>', str(usernames))
                            print('Line Exist in playlist lines')
                        else:
                            linecode = 'http://' + str(cfg.hostaddress.value) + ':' + str(cfg.port.value) + '/get.php?username=' + str(cfg.user.value) + '&password=' + str(cfg.passw.value) + '&type=m3u_plus'
                            f.write('\n' + str(linecode) + '\n')
                            print('<<===', str(linecode))
                            self.session.open(MessageBox, _("Line Append to playlist"), type=MessageBox.TYPE_WARNING, timeout=5)
                return
        except Exception as e:
            print("xcConfig xml_plugin failed: ", e)

    def KeyText(self):
        sel = self["config"].getCurrent()
        if sel:
            self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=self["config"].getCurrent()[0], text=self["config"].getCurrent()[1].value)

    def VirtualKeyBoardCallback(self, callback=None):
        if callback is not None and len(callback):
            self["config"].getCurrent()[1].value = callback
            self["config"].invalidate(self["config"].getCurrent())
        return

    def extnok(self, answer=None):
        if answer is None:
            self.session.openWithCallback(self.extnok, MessageBox, _("Really close without saving settings?"))
        elif answer:
            for x in self["config"].list:
                x[1].cancel()
            self.close()
        else:
            return

    def ConfigText(self):
        STREAMS.read_config()
        STREAMS.get_list(STREAMS.xtream_e2portal_url)


class iptv_streamse():
    def __init__(self):
        global MODUL, iptv_list_tmp
        self.plugin_version = ""
        self.playlistname = ""
        self.playlistname_tmp = ""
        self.next_page_url = ""
        self.next_page_text = ""
        self.prev_page_url = ""
        self.prev_page_text = ""
        self.trial = ""
        self.banned_text = ""
        self.systems = ""
        self.playhack = ""
        self.url_tmp = ""
        self.next_page_url_tmp = ""
        self.next_page_text_tmp = ""
        self.prev_page_url_tmp = ""
        self.prev_page_text_tmp = ""
        self.iptv_list = []
        self.iptv_list_tmp = []
        self.iptv_list_history = []
        self.esr_id = 4097
        self.list_index_tmp = 0
        self.list_index = 0
        self.ar_id_start = 0
        self.ar_id_end = 0
        self.ar_id_player = 0
        self.play_vod = False
        self.play_iptv = False
        self.video_status = False
        self.server_oki = True
        self.ar_start = True
        self.img_loader = False
        self.cont_play = False
        self.disable_audioselector = False
        self.hostaddress = str(cfg.hostaddress.value)
        self.port = str(cfg.port.value)
        self.hosts = "http://" + str(cfg.hostaddress.value)
        self.xtream_e2portal_url = self.hosts + ':' + self.port
        self.username = str(cfg.user.value)
        self.password = str(cfg.passw.value)

    def MoviesFolde(self):
        return Path_Movies

    def getValue(self, definitions, default):
        Len = len(definitions)
        return Len > 0 and definitions[Len - 1].text or default

    def read_config(self):
        try:
            print("-----------CONFIG NEW START----------")
            username = self.username
            if username and username != "" and 'Enter' not in username:
                self.username = username
                print('ok user')
            password = str(cfg.passw.value)
            if password and password != "" and 'Enter' not in password:
                self.password = password
                print('ok password')
            # plugin_version = version
            print("-----------CONFIG NEW END----------")
        except Exception as e:
            print("++++++++++ERROR READ CONFIG+++++++++++++ ")
            print(e)

    def get_list(self, url=None):
        global stream_live, iptv_list_tmp, stream_url, btnsearch, isStream, next_request, infoname
        stream_live = False
        stream_url = ""
        self.url = check_port(url)
        self.list_index = 0
        iptv_list_tmp = []
        xml = None
        btnsearch = 0
        next_request = 0
        isStream = False
        try:
            print("!!!!!!!!-------------------- URL %s" % self.url)
            if '&type' in self.url:
                next_request = 1
            elif "_get" in self.url:
                next_request = 2
            xml = self._request(self.url)
            if xml:
                self.playlistname = ""
                self.category_title = ""
                self.category_id = ""
                self.next_page_url = ""
                self.next_page_text = ""
                self.prev_page_url = ""
                self.prev_page_text = ""
                self.prev_page_text_element = ""
                self.next_page_text_element = ""
                playlistname_exists = xml.findtext('playlist_name')
                if playlistname_exists:
                    self.playlistname = xml.findtext('playlist_name')  # .encode('utf-8')
                    infoname = str(self.playlistname)
                    if cfg.infoexp.getValue():
                        infoname = str(cfg.infoname.value)
                next_page_url = xml.findtext("next_page_url")
                if next_page_url:
                    self.next_page_url = next_page_url[0].attrib.get("text")  # .encode("utf-8")
                next_page_text_element = xml.findall("next_page_url")
                if next_page_text_element:
                    self.next_page_text = next_page_text_element[0].attrib.get("text")  # .encode("utf-8")
                prev_page_url = xml.findtext("prev_page_url")
                if prev_page_url:
                    self.prev_page_url = prev_page_url[0].attrib.get("text")
                prev_page_text_element = xml.findall("prev_page_url")
                if prev_page_text_element:
                    self.prev_page_text = prev_page_text_element[0].attrib.get("text")  # .encode("utf-8")

                chan_counter = 0
                for channel in xml.findall("channel"):
                    chan_counter += 1
                    title64 = ''
                    name = ''
                    description64 = ''
                    description = ''
                    category_id = ''
                    playlist_url = ''
                    desc_image = ''
                    stream_url = ''
                    piconname = ''
                    # ts_stream = ''
                    nameepg = ''
                    # description1 = ''
                    description2 = ''
                    description3 = ''
                    title64 = channel.findtext('title')
                    name = base64.b64decode(title64).decode('utf-8')
                    # test bad char from kiddac plugin
                    if config.plugins.XCplugin.badcar.value is True:
                        name = Utils.badcar(name)
                    description64 = channel.findtext('description')
                    description = base64.b64decode(description64).decode('utf-8')
                    try:
                        name = ''.join(chr(ord(c)) for c in name).decode('utf-8')
                    except:
                        # name = ''.join(chr(ord(c)) for c in name)
                        pass
                    try:
                        description = ''.join(chr(ord(c)) for c in description).decode('utf-8')
                    except:
                        # description = ''.join(chr(ord(c)) for c in description)
                        pass

                    stream_url = Utils.checkStr(channel.findtext('stream_url'))
                    piconname = Utils.checkStr(channel.findtext("logo"))
                    category_id = Utils.checkStr(channel.findtext('category_id'))
                    # ts_stream = Utils.checkStr(channel.findtext("ts_stream"))
                    playlist_url = Utils.checkStr(channel.findtext('playlist_url'))
                    desc_image = Utils.checkStr(channel.findtext('desc_image'))
                    if desc_image and desc_image != "n/A" and desc_image != "":
                        if desc_image.startswith("https"):
                            desc_image = desc_image.replace("https", "http")
                    # if PY3:
                        # desc_image = desc_image.encode()
                    # epgnowtitle = ''
                    # #####################
                    if stream_url:
                        isStream = True
                        stream_url = str(stream_url)
                        # print('isStream: ', isStream)
                    if stream_url and "/live/" in stream_url:
                        '''
                        if isStream and "/live/" in stream_url:
                        if isStream and "get_live_streams" in stream_url:
                        '''
                        # print("****** is live stream **** ")
                        stream_live = True
                        epgnowtime = ''
                        epgnowdescription = ''
                        epgnexttitle = ''
                        epgnexttime = ''
                        epgnextdescription = ''
                        '''
                        if len(name.split("[")) > 1:
                            name = name.split("[")[0].strip()
                            print('name 1 : ------- ', name)
                            if len(name.split("[")) > 0:
                                name = name.split("[")[1].strip()
                                print('name 2 : ------- ', name)
                        if len(name.split("[")) > 1:
                            name = name.split("[")[0].strip()
                        else:
                            name = str(name)
                        '''
                        name = html_conv.html_unescape(name)
                        # print('Name html_unescape: ', name)
                        if description != '':
                            # try:
                            timematch = re.findall(r'\[(\d\d:\d\d)\]', description)
                            titlematch = re.findall(r'\[\d\d:\d\d\](.*)', description)
                            # print('=============timematch: ', timematch)
                            # print('=============titlematch: ', titlematch)
                            descriptionmatch = re.findall(r'\n(?s)\((.*?)\)', description)
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
                            description1 = epgnowtime + ' ' + name + '\n' + epgnowdescription
                            description2 = epgnexttime + ' ' + epgnexttitle + '\n' + epgnextdescription
                            description = html_conv.html_unescape(description1)
                            description2 = html_conv.html_unescape(description2)
                            # except Exception as e:
                                # description = html_conv.html_unescape(description)
                                # print('------------- description failed: ', e)
                    # if isStream and ("get_vod" or "get_series") in str(stream_url):
                    # elif isStream and ("/movie/" or "/series/") in str(stream_url):
                    # if isStream and ("/movie/") in str(stream_url):
                    elif stream_url and ("/movie/" or "/series/") in str(stream_url):
                        stream_live = False
                        vodItems = {}
                        name = str(name)
                        vodTitle = ''
                        vodDescription = ''
                        vodDuration = ''
                        vodGenre = ''
                        vodLines = description.splitlines()
                        for line in vodLines:
                            vodItems[(line.partition(": ")[0])] = Utils.checkStr(line.partition(": ")[-1])
                        if "NAME" in vodItems:
                            vodTitle = ((vodItems["NAME"])).strip()
                        elif "O_NAME" in vodItems:
                            vodTitle = ((vodItems["O_NAME"])).strip()
                        else:
                            vodTitle = str(name)

                        if "COVER_BIG" in vodItems and vodItems["COVER_BIG"] and vodItems["COVER_BIG"] != "null":
                            piconname = str(vodItems["COVER_BIG"]).strip()

                        if "DESCRIPTION" in vodItems:
                            vodDescription = str(vodItems["DESCRIPTION"]).strip()
                        elif "PLOT" in vodItems:
                            vodDescription = str(vodItems["PLOT"]).strip()
                        else:
                            vodDescription = str('TRAMA')

                        if "DURATION" in vodItems:
                            vodDuration = str(vodItems["DURATION"]).strip()
                        else:
                            vodDuration = str('DURATION: -- --')

                        if "GENRE" in vodItems:
                            vodGenre = str(vodItems["GENRE"]).strip()
                        else:
                            vodGenre = str('GENRE: -- --')

                        description3 = str(vodTitle) + '\n' + str(vodGenre) + '\nDuration: ' + str(vodDuration) + '\n' + str(vodDescription)
                        description = html_conv.html_unescape(description3)
                    chan_tulpe = (
                        str(chan_counter),
                        str(name),
                        str(description),
                        str(piconname),
                        stream_url,
                        playlist_url,
                        str(category_id),
                        desc_image,
                        str(description2),
                        str(nameepg))
                    iptv_list_tmp.append(chan_tulpe)

                    btnsearch = next_request
        except Exception as e:
            print('------------- get_list failed: ', e)

        if len(iptv_list_tmp):
            self.iptv_list = iptv_list_tmp
            iptv_list_tmp = self.iptv_list
        print("IPTV_LIST_LEN = %s" % len(iptv_list_tmp))
        return

    def _request(self, url):
        res = url
        if "exampleserver" not in str(cfg.hostaddress.value):
            global urlinfo, next_request
            TYPE_PLAYER = '/enigma2.php'
            TYPE_PLAYER2 = '/player_api.php'
            url = url.strip(" \t\n\r")
            if next_request == 1:
                # url = check_port(url)
                if not url.find(":"):
                    self.port = str(cfg.port.value)
                    full_url = self.xtream_e2portal_url + ':' + self.port
                    url = url.replace(self.xtream_e2portal_url, full_url)
                url = url
            else:
                url = url + TYPE_PLAYER + "?" + "username=" + self.username + "&password=" + self.password
            urlinfo = url
            # urlinfo = Utils.checkRedirect(url)
            try:
                import requests
                from requests.adapters import HTTPAdapter, Retry
                retries = Retry(total=1, backoff_factor=1)
                adapter = HTTPAdapter(max_retries=retries)
                http = requests.Session()
                http.mount("http://", adapter)
                http.mount("https://", adapter)
                r = http.get(urlinfo, headers={'User-Agent': Utils.RequestAgent()}, timeout=10, verify=False)  # , stream=True)
                r.raise_for_status()
                if r.status_code == requests.codes.ok:
                    res = r.text
                    res = fromstring(res)
            except Exception as e:
                print('error requests -----------> ', e)
            return res
        else:
            res = None
            return res

    def make_request(self, url):
        link = url
        try:
            import requests
            response = requests.get(url, verify=False)
            if response.status_code == 200:
                link = requests.get(url, headers={'User-Agent': Utils.RequestAgent()}, timeout=15, verify=False, stream=True).text
        except ImportError:
            req = Request(url)
            req.add_header('User-Agent', 'E2 Plugin Vhannibal')
            response = urlopen(req, None, 10)
            link = response.read().decode('utf-8')
            response.close()
        except Exception as e:
            print('make_reequest error:', e)
        return link

    def checkGZIP(self, url):
        from io import StringIO
        import gzip
        hdr = {"User-Agent": "Enigma2 - Plugin"}
        response = None
        request = Request(url, headers=hdr)
        try:
            response = urlopen(request, timeout=20)
            if response.info().get('Content-Encoding') == 'gzip':
                buffer = StringIO(response.read())
                deflatedContent = gzip.GzipFile(fileobj=buffer)
                if PY3:
                    return deflatedContent.read().decode('utf-8')
                else:
                    return deflatedContent.read()
            else:
                if PY3:
                    return response.read().decode('utf-8')
                else:
                    return response.read()
            print(response)
            print(type(response))
        except Exception as e:
            print(e)
            return None


class xc_Main(Screen):
    def __init__(self, session):
        global STREAMS
        global _session
        global channel_list2
        global re_search
        global infoname
        _session = session
        Screen.__init__(self, session)
        self.session = session
        skin = os.path.join(skin_path, 'xc_Main.xml')
        if cfg.screenxl.value:
            skin = os.path.join(skin_path, 'xc_Mainxl.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setup_title = ('XCplugin Forever')
        self.channel_list = STREAMS.iptv_list
        self.index = STREAMS.list_index
        channel_list2 = self.channel_list
        self.index2 = self.index
        self.banned = False
        self.banned_text = ""
        self.search = ''
        re_search = False
        self.downloading = False
        self.pin = False
        self.icount = 0
        self.errcount = 0
        self.passwd_ok = False
        self.temp_index = 0
        self.temp_channel_list = None
        self.temp_playlistname = None
        self.temp_playname = str(STREAMS.playlistname)
        self.url_tmp = None
        self.video_back = False
        self.filter_search = []
        self.mlist = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.mlist.l.setFont(0, gFont(FONT_0[0], FONT_0[1]))
        self.mlist.l.setFont(1, gFont(FONT_1[0], FONT_1[1]))
        self.mlist.l.setItemHeight(BLOCK_H)
        if cfg.infoexp.getValue():
            infoname = str(cfg.infoname.value)
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
        self["key_red"] = Label(_("Back"))
        self["key_green"] = Label(_("Rec Movie"))
        self["key_yellow"] = Label(_("Rec Series"))
        self["key_blue"] = Label(_("Search"))
        self["key_green"].hide()
        self["key_yellow"].hide()
        self["key_blue"].hide()
        self["key_text"] = Label("2")
        self["poster"] = Pixmap()
        self["Text"] = Label(infoname)
        self["playlist"].setText(self.temp_playname)
        self.go()
        self["actions"] = HelpableActionMap(self, "XCpluginActions", {
            "cancel": self.exitY,
            "home": self.exitY,
            "1": self.update_list,
            "green": self.check_download_vod,
            "yellow": self.check_download_ser,
            "blue": self.search_text,
            "ok": self.ok,
            "info": self.show_more_info,
            "epg": self.show_more_info,
            "0": self.show_more_info,
            "showMediaPlayer": self.showMovies,
            "5": self.showMediaPlayer,
            "2": self.taskManager,
            "pvr": self.taskManager,
            "movielist": self.taskManager,
            "help": self.helpx,
            "power": self.power}, -1)
        self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onFirstExecBegin.append(self.checkinf)
        # self.onShown.append(self.show_all)
        self.onLayoutFinish.append(self.show_all)
        # self.onShown.append(self.show_all)

    def ok(self):
        if not len(iptv_list_tmp):
            self.session.open(MessageBox, _("No data or playlist not compatible with XCplugin."), type=MessageBox.TYPE_WARNING, timeout=5)
            return
        self.index = self.mlist.getSelectionIndex()
        selected_channel = self.channel_list[self.mlist.getSelectionIndex()]
        STREAMS.list_index = self.mlist.getSelectionIndex()
        title = selected_channel[1]
        if selected_channel[0] != "[H]":
            title = ("[-]   ") + selected_channel[1]
        selected_channel_history = (
            "[H]",
            title,
            selected_channel[2],
            selected_channel[3],
            selected_channel[4],
            selected_channel[5],
            selected_channel[6],
            selected_channel[7],
            selected_channel[8],
            selected_channel[9])
        STREAMS.iptv_list_history.append(selected_channel_history)
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
        global title
        try:
            if self.temp_index > -1:
                self.index = self.temp_index
            selected_channel = STREAMS.iptv_list[self.index]
            playlist_url = selected_channel[5]
            if playlist_url is not None:
                STREAMS.get_list(playlist_url)
                self.update_channellist()
            elif selected_channel[4] is not None:
                self.set_tmp_list()
                STREAMS.video_status = True
                STREAMS.play_vod = False
                title = str(selected_channel[2])
                self.Entered()
        except Exception as e:
            print(e)

    def Entered(self):
        self.pin = True
        if stream_live is True:
            STREAMS.video_status = True
            STREAMS.play_vod = False
            print("------------------------ LIVE ------------------")
            if cfg.LivePlayer.value is False:
                self.session.openWithCallback(self.check_standby, xc_Player)  # vod
            else:
                self.session.openWithCallback(self.check_standby, nIPTVplayer)  # live
        else:
            STREAMS.video_status = True
            STREAMS.play_vod = True
            print("----------------------- MOVIE ------------------")
            self.session.openWithCallback(self.check_standby, xc_Player)

    def go(self):
        self.mlist.setList(list(map(channelEntryIPTVplaylist, self.channel_list)))
        self.mlist.onSelectionChanged.append(self.update_description)
        self["feedlist"] = self.mlist
        self["feedlist"].moveToIndex(0)

    def update_list(self):
        global STREAMS
        STREAMS = iptv_streamse()
        STREAMS.read_config()
        if "exampleserver.com" not in STREAMS.xtream_e2portal_url:
            STREAMS.get_list(STREAMS.xtream_e2portal_url)
            self.update_channellist()

    def button_updater(self):
        global infoname
        if cfg.infoexp.getValue():
            infoname = str(cfg.infoname.value)
        self["Text"].setText(infoname)
        self["playlist"].setText(self.temp_playname)

        if isStream and btnsearch == 1:
            self["key_blue"].show()
            self["key_green"].show()
            self["key_yellow"].show()
        elif 'series' in urlinfo:
            self["key_blue"].show()
            self["key_green"].show()
            self["key_yellow"].show()

    def update_description(self):
        if not len(iptv_list_tmp):
            return
        if re_search is True:
            self.channel_list = iptv_list_tmp
        self.index = self.mlist.getSelectionIndex()
        try:
            self["info"].setText("")
            self["description"].setText("NO DESCRIPTIONS")
            try:
                if file_exists(pictmp):
                    remove(pictmp)
            except OSError as error:
                print(error)
            self['poster'].instance.setPixmapFromFile(piclogo)
            selected_channel = self.channel_list[self.index]
            if selected_channel[2] is not None:
                if stream_live is True:
                    description = selected_channel[2]
                    description2 = selected_channel[8]
                    description3 = selected_channel[6]
                    description_3 = description3.split(" #-# ")
                    descall = str(description) + '\n\n' + str(description2)
                    self["description"].setText(descall)
                    # print('------------------------------------------ descall desc', descall)
                    if description_3:
                        if len(description_3) > 1:
                            self["info"].setText(str(description_3[1]))
                else:
                    description = str(selected_channel[2])
                    self["description"].setText(description)
                    # print('------------------------------------------ else desc', description)
                pixim = six.ensure_binary(selected_channel[7])
                # if PY3:
                    # pixim = pixim.decode('utf-8') #.encode()
                # print('self pixim   ', str(pixim))
                # if (pixim != "" or pixim != "n/A" or pixim is not None or pixim != "null"):
                if pixim != "":
                    parsed = urlparse(pixim)
                    domain = parsed.hostname
                    scheme = parsed.scheme
                    if scheme == "https" and sslverify:
                        sniFactory = SNIFactory(domain)
                        downloadPage(pixim, pictmp, sniFactory, timeout=ntimeout).addCallback(self.image_downloaded, pictmp).addErrback(self.downloadError)
                    else:
                        downloadPage(pixim, pictmp).addCallback(self.image_downloaded, pictmp).addErrback(self.downloadError)
        except Exception as e:
            print(e)

    def image_downloaded(self, data, pictmp):
        if file_exists(pictmp):
            try:
                self.decodeImage(pictmp)
            except Exception as e:
                print("* error ** %s" % e)
                self.downloadError()

    def decodeImage(self, png):
        if file_exists(png):
            if self["poster"].instance:
                size = self['poster'].instance.size()
                self.scale = AVSwitch().getFramebufferScale()
                self.picload = ePicLoad()
                try:
                    iAVSwitch.setAspectRatio(STREAMS.ar_id_player)
                except:
                    eAVSwitch.getInstance().setAspectRatio(STREAMS.ar_id_player)
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
                self["poster"].instance.setPixmapFromFile(piclogo)
        except Exception as e:
            print('error poster', e)

    def update_channellist(self):
        if not len(iptv_list_tmp):
            return
        self.channel_list = STREAMS.iptv_list
        if re_search is False:
            self.channel_list = iptv_list_tmp

        if 'season' or 'series' in str(stream_url).lower():
            # if '.mp4' or '.mkv' or 'avi' or '.flv' or '.m3u8' in str(stream_url):
            # if ext in EXTDOWN:
            global series
            series = True
            streamfile = '/tmp/streamfile.txt'
            with open(streamfile, 'w') as f:
                f.write(str(self.channel_list).replace("\t", "").replace("\r", "").replace('None', '').replace("'',", "").replace(' , ', '').replace("), ", ")\n").replace("''", '').replace(" ", ""))
                f.write('\n')
                f.close()
        self.mlist.moveToIndex(0)
        self.mlist.setList(list(map(channelEntryIPTVplaylist, self.channel_list)))
        self.update_description()
        self.button_updater()

    def show_all(self):
        try:
            if re_search is True:
                self.channel_list = iptv_list_tmp
                self.mlist.onSelectionChanged.append(self.update_description)
                self["feedlist"] = self.mlist
                self["feedlist"].moveToIndex(0)
            else:
                self.channel_list = STREAMS.iptv_list

            self.mlist.moveToIndex(0)
            self.mlist.setList(list(map(channelEntryIPTVplaylist, self.channel_list)))
            self.mlist.selectionEnabled(1)

            self.button_updater()
        except Exception as e:
            print(e)

    def search_text(self):
        global re_search
        if re_search is True:
            re_search = False
        self.session.openWithCallback(self.filterChannels, VirtualKeyBoard, title=_("Filter this category..."), text=self.search)

    def filterChannels(self, result):
        if result:
            self.filter_search = []
            self.search = result
            self.filter_search = [channel for channel in self.channel_list if str(result).lower() in channel[1].lower()]
            if len(self.filter_search):
                global re_search, iptv_list_tmp
                re_search = True
                iptv_list_tmp = self.filter_search
                self.mlist.setList(list(map(channelEntryIPTVplaylist, iptv_list_tmp)))
                self.mlist.onSelectionChanged.append(self.update_description)
                self.index = self.mlist.getSelectionIndex()
                self["feedlist"] = self.mlist
                self.button_updater()
            else:
                self.resetSearch()

    def resetSearch(self):
        global re_search
        re_search = False
        self.filter_search = []

# try for back to the list
# # def load_from_tmp(self):
# # STREAMS.iptv_list = STREAMS.iptv_list_tmp
# # STREAMS.list_index = STREAMS.list_index_tmp
# # STREAMS.playlistname = STREAMS.playlistname_tmp
# # STREAMS.url = STREAMS.url_tmp
# # STREAMS.next_page_url = STREAMS.next_page_url_tmp
# # STREAMS.next_page_text = STREAMS.next_page_text_tmp
# # STREAMS.prev_page_url = STREAMS.prev_page_url_tmp
# # STREAMS.prev_page_text = STREAMS.prev_page_text_tmp
# # self.index = STREAMS.list_index
# STREAMS.read_config()
# STREAMS.get_list(STREAMS.xtream_e2portal_url)
    def mmark(self):
        global iptv_list_tmp
        Utils.del_jpg()
        copy_poster()
        self.temp_index = 0
        self.list_index = 0
        self.temp_channel_list = None
        # self.temp_playlistname = None
        self.url_tmp = None
        self.video_back = False
        STREAMS.video_status = False
        iptv_list_tmp = channel_list2
        STREAMS.iptv_list = channel_list2
        STREAMS.list_index = self.index2
        self.update_channellist()
        self.decodeImage(piclogo)
        global infoname
        infoname = self.temp_playname
        self["playlist"].setText(infoname)

    def exitY(self):
        global btnsearch
        '''
        print('btnsearch = ',btnsearch)
        print('next_request = ',next_request)
        print('re_search = ',re_search)
        print('isStream = ',isStream)
        print('STREAM VIDEO STATUS : ', str(STREAMS.video_status))
        print('STREAM VIDEO BACK : ', str(self.video_back))
        if STREAMS.video_status and self.video_back == False:
            self.video_back = True
            self.back_to_video()
        '''
        try:
            # if next_request == 1 and btnsearch == 1:
            # print('btttnsearch ', btnsearch)
            if btnsearch == 1:
                btnsearch = 0
                self["key_blue"].hide()
                self["key_green"].hide()
                self["key_yellow"].hide()
                self.mmark()
            # # elif isStream and "/live/" in str(stream_url) and btnsearch == 1:
            # elif stream_url and "/live/" in stream_url and btnsearch == 1:
                # btnsearch = 0
                # self["key_blue"].hide()
                # self["key_green"].hide()
                # self["key_yellow"].hide()
                # self.mmark()
            # # elif isStream and "/movie/" in str(stream_url) and btnsearch == 1:
            # elif stream_url and ("/movie/" or "/series/") in stream_url and btnsearch == 1:
                # btnsearch = 0
                # self["key_blue"].hide()
                # self["key_green"].hide()
                # self["key_yellow"].hide()
                # self.mmark()
            else:
                self.close()
        except Exception as e:
            print('error on exit: ', e)
            self.close()

    def showMediaPlayer(self):
        try:
            from Plugins.Extensions.MediaPlayer.plugin import MediaPlayer
            self.session.open(MediaPlayer)
        except:
            self.session.open(MessageBox, _("The MediaPlayer plugin is not installed!\nPlease install it."), type=MessageBox.TYPE_INFO, timeout=10)

    def showMovies(self):
        try:
            self.session.open(MovieSelection)
        except:
            pass

    def helpx(self):
        self.session.open(xc_help)

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
        selected_channel = iptv_list_tmp[self.index]
        if selected_channel:
            name = str(selected_channel[1])
            show_more_infos(name, self.index)

    def checkinf(self):
        try:
            TIME_GMT = '%d-%m-%Y %H:%M:%S'
            self["max_connect"].setText("Max Connect: 0")
            self["active_cons"].setText("User Active: 0")
            self["exp"].setText("- ? -")
            self["created_at"].setText("- ? -")
            self["server_protocol"].setText("Protocol: - ? -")
            self["timezone"].setText("Timezone: - ? -")
            status = created_at = exp_date = active_cons = max_connections = host = '- ? -'
            auth = 'Not Authorised'
            user = passw = ''
            if cfg.hostaddress != 'exampleserver.com':
                host = cfg.hostaddress.value
            ports = cfg.port.value
            if cfg.user.value != "Enter_Username":
                user = cfg.user.value
            if cfg.passw != '******':
                passw = cfg.passw.value
            # urlinfo = 'http://' + str(host) + ':' + str(ports) + '/player_api.php?username=' + str(user) + '&password=' + str(passw) + '&action=user&sub=info'
            urlinfo = 'http://' + str(host) + ':' + str(ports) + '/player_api.php?username=' + str(user) + '&password=' + str(passw)
            import requests
            from requests.adapters import HTTPAdapter
            hdr = {"User-Agent": "Enigma2 - XCForever Plugin"}
            r = ""
            adapter = HTTPAdapter()
            http = requests.Session()
            http.mount("http://", adapter)
            http.mount("https://", adapter)
            r = http.get(urlinfo, headers=hdr, timeout=ntimeout, verify=False, stream=True)
            r.raise_for_status()
            if r.status_code == requests.codes.ok:
                y = r.json()
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
                                if created_at:
                                    created_at = time.strftime(TIME_GMT, time.gmtime(int(created_at)))
                                    self["created_at"].setText('Start date:\n' + created_at)
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
                                        self["exp"].setText("Expired")
                                    else:
                                        self["exp"].setText("Server Not Responding" + str(exp_date))
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
        global series
        titleserie = str(STREAMS.playlistname)
        if series is True and btnsearch == 1:
            if answer is None:
                self.streamfile = '/tmp/streamfile.txt'
                if file_exists(self.streamfile) and os.stat(self.streamfile).st_size > 0:
                    self.session.openWithCallback(self.check_download_ser, MessageBox, _("ATTENTION!!!\nDOWNLOAD ALL EPISODES SERIES\nSURE???"))
            elif answer:
                self.icount = 0
                try:
                    self["state"].setText("Download SERIES")
                    Path_Movies2 = Path_Movies + titleserie + '/'
                    if not file_exists(Path_Movies2):
                        system("mkdir " + Path_Movies2)
                    if Path_Movies2.endswith("//") is True:
                        Path_Movies2 = Path_Movies2[:-1]
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
                                    self.title = Utils.cleantitle(name) + ext
                                    self.title = self.title.lower()
                                    self.icount += 1
                                    cmd = "wget --no-cache --no-dns-cache -U '%s' -c '%s' -O '%s%s' --post-data='action=purge'" % ('Enigma2 - XC Forever Plugin', url, str(Path_Movies2), self.title)
                                    if "https" in str(url):
                                        cmd = "wget --no-check-certificate --no-cache --no-dns-cache -U '%s' -c '%s' -O '%s%s' --post-data='action=purge'" % ('Enigma2 - XC Forever Plugin', url, str(Path_Movies2), self.title)
                                    JobManager.AddJob(downloadJob(self, cmd, Path_Movies2, self.title))
                                    self.downloading = True
                            # self.createMetaFile(self.title, self.title)
                        except Exception as e:
                            print(e)
                            pass

                    else:
                        series = False
                    Utils.OnclearMem()

                except Exception as e:
                    print(e)
                    series = False
        else:
            self.session.open(MessageBox, _("Only Series Episodes Allowed!!!"), MessageBox.TYPE_INFO, timeout=5)

    def check_download_vod(self):
        self.index = self.mlist.getSelectionIndex()
        selected_channel = iptv_list_tmp[self.index]
        if selected_channel:
            self.title = str(selected_channel[1])
            self.vod_url = selected_channel[4]
            self.desc = str(selected_channel[2])
            if self.vod_url is not None and btnsearch == 1:
                pth = urlparse(self.vod_url).path
                ext = splitext(pth)[-1]
                if ext != '.ts':
                    filename = Utils.cleantitle(self.title)
                    if ext not in EXTDOWN:
                        ext = '.avi'
                    filename = filename + ext
                    self.filename = filename.lower()  # + ext
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
                self.file_down = Path_Movies + self.filename
                if cfg.pdownmovie.value == "JobManager":
                    try:
                        self.timerDownload.callback.append(self.downloadx)
                    except:
                        self.timerDownload_conn = self.timerDownload.timeout.connect(self.downloadx)
                elif cfg.pdownmovie.value == "Requests":
                    try:
                        import requests
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
                self.session.open(MessageBox, _('Download Failed\n\n' + self.filename + "\n\n" + Path_Movies + '\n' + self.filename), MessageBox.TYPE_WARNING)
                self.downloading = False

    def downloady(self):
        if self.downloading is True:
            from .downloader import imagedownloadScreen
            Utils.OnclearMem()
            self.session.open(imagedownloadScreen, self.filename, self.file_down, self.vod_url)
        else:
            return

    def downloadx(self):
        cmd = "wget --no-cache --no-dns-cache -U '%s' -c '%s' -O '%s' --post-data='action=purge'" % ('Enigma2 XC Forever Plugin', str(self.vod_url), str(self.file_down))
        if "https" in str(self.vod_url):
            cmd = "wget --no-check-certificate --no-cache --no-dns-cache -U '%s' -c '%s' -O '%s' --post-data='action=purge'" % ('Enigma2 - XC Forever Plugin', str(self.vod_url), str(self.file_down))
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
            with open("%s/%s.meta" % (Path_Movies, filename), "wb") as f:
                f.write("%s\n%s\n%s\n%i\n" % (serviceref.toString(), str(filmtitle), "", time.time()))
        except Exception as e:
            print(e)
        return

    def check_standby(self, myparam=None):
        debug(myparam, "check_standby")
        if myparam:
            self.power()

    def power(self):
        self.session.nav.stopService()
        self.session.open(Standby)

    def set_tmp_list(self):
        self.index = self.mlist.getSelectionIndex()
        STREAMS.list_index = self.index
        STREAMS.list_index_tmp = STREAMS.list_index
        if re_search is True:
            STREAMS.iptv_list_tmp = iptv_list_tmp
        else:
            STREAMS.iptv_list_tmp = STREAMS.iptv_list
        STREAMS.playlistname_tmp = STREAMS.playlistname
        STREAMS.url_tmp = STREAMS.url
        STREAMS.next_page_url_tmp = STREAMS.next_page_url
        STREAMS.next_page_text_tmp = STREAMS.next_page_text
        STREAMS.prev_page_url_tmp = STREAMS.prev_page_url
        STREAMS.prev_page_text_tmp = STREAMS.prev_page_text

    def load_from_tmp(self):
        STREAMS.iptv_list = STREAMS.iptv_list_tmp
        STREAMS.list_index = STREAMS.list_index_tmp
        STREAMS.playlistname = STREAMS.playlistname_tmp
        STREAMS.url = STREAMS.url_tmp
        STREAMS.next_page_url = STREAMS.next_page_url_tmp
        STREAMS.next_page_text = STREAMS.next_page_text_tmp
        STREAMS.prev_page_url = STREAMS.prev_page_url_tmp
        STREAMS.prev_page_text = STREAMS.prev_page_text_tmp
        self.index = STREAMS.list_index

    def back_to_video(self):
        try:
            self.video_back = False
            self.load_from_tmp()
            self.channel_list = STREAMS.iptv_list
            self.session.open(xc_Player)
        except Exception as e:
            print(e)


class IPTVInfoBarShowHide():
    """ InfoBar show/hide control, accepts toggleShow and hide actions, might start
    fancy animations. """
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
        }, 0)
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
        self.session = session
        _session = session
        self.recorder_sref = None
        skin = os.path.join(skin_path, 'xc_Player.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        InfoBarBase.__init__(self, steal_current_service=True)
        IPTVInfoBarShowHide.__init__(self)
        InfoBarSeek.__init__(self, actionmap="InfobarSeekActions")
        InfoBarAudioSelection.__init__(self)
        InfoBarSubtitleSupport.__init__(self)
        SubsSupport.__init__(self, searchSupport=True, embeddedSupport=True)
        SubsSupportStatus.__init__(self)
        # self.orig_aspect = int(self.getAspect())
        try:
            self.init_aspect = int(self.getAspect())
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
        self.scale = AVSwitch().getFramebufferScale()
        self.picload = ePicLoad()
        try:
            self.picload.PictureData.get().append(self.setCover)
        except:
            self.picload_conn = self.picload.PictureData.connect(self.setCover)
        self.state = self.STATE_PLAYING
        self.cont_play = STREAMS.cont_play
        self.service = None
        self.recorder = False
        self.vod_url = None
        self.timeshift_url = None
        self.timeshift_title = None
        self.error_message = ""
        if recorder_sref:
            self.recorder_sref = recorder_sref
            self.session.nav.playService(recorder_sref)
        else:
            self.index = STREAMS.list_index
            self.channelx = iptv_list_tmp[STREAMS.list_index]
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
        self["actions"] = HelpableActionMap(self, "XCpluginActions", {
                                                  "info": self.show_more_info,
                                                  "epg": self.show_more_info,
                                                  "0": self.show_more_info,
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
                                                  "tv": self.stopnew,
                                                  "stop": self.stopnew,
                                                  "2": self.restartVideo,
                                                  "help": self.helpx,
                                                  "power": self.power_off}, -1)
        self.onFirstExecBegin.append(self.play_vod)
        self.onShown.append(self.setCover)
        self.onShown.append(self.show_info)
        self.onPlayStateChanged.append(self.__playStateChanged)
        return

    def getAspect(self):
        return AVSwitch().getAspectRatioSetting()

    def exitx(self):
        if STREAMS.playhack == "":
            STREAMS.play_vod = False
            self.video_back = False
        # self.setAspect(self.orig_aspect)
        self.close()

    def getAspectString(self, aspectnum):
        return {
            0: '4:3 Letterbox',
            1: '4:3 PanScan',
            2: '16:9',
            3: '16:9 always',
            4: '16:10 Letterbox',
            5: '16:10 PanScan',
            6: '16:9 Letterbox'
        }[aspectnum]

    def setAspect(self, aspect):
        map = {
            0: '4_3_letterbox',
            1: '4_3_panscan',
            2: '16_9',
            3: '16_9_always',
            4: '16_10_letterbox',
            5: '16_10_panscan',
            6: '16_9_letterbox'
        }
        config.av.aspectratio.setValue(map[aspect])
        try:
            AVSwitch().setAspectRatio(aspect)
        except:
            pass

    def av(self):
        temp = int(self.getAspect())
        temp += 1
        if temp > 6:
            temp = 0
        self.new_aspect = temp
        self.setAspect(temp)

    def setCover(self):
        try:
            self.channelx = iptv_list_tmp[STREAMS.list_index]
            self['poster'].instance.setPixmapFromFile(piclogo)
            self.pixim = str(self.channelx[7])
            if (self.pixim != "" or self.pixim != "n/A" or self.pixim is not None or self.pixim != "null"):
                if PY3:
                    self.pixim = six.ensure_binary(self.pixim)
                if self.pixim.startswith(b"https") and sslverify:
                    parsed_uri = urlparse(self.pixim)
                    domain = parsed_uri.hostname
                    sniFactory = SNIFactory(domain)
                    downloadPage(self.pixim, pictmp, sniFactory, timeout=ntimeout).addCallback(self.image_downloaded, pictmp).addErrback(self.downloadError)
                else:
                    downloadPage(self.pixim, pictmp).addCallback(self.image_downloaded, pictmp).addErrback(self.downloadError)
            else:
                self.downloadError()
                print("setCover err")
        except Exception as e:
            print(e)
            self.downloadError()

    def decodeImage(self, png):
        self["poster"].hide()
        if file_exists(png):
            size = self['poster'].instance.size()
            self.picload = ePicLoad()
            self.scale = AVSwitch().getFramebufferScale()
            self.picload.setPara([size.width(), size.height(), self.scale[0], self.scale[1], 0, 1, '#00000000'])
            # _l = self.picload.PictureData.get()
            # del self.picload
            if file_exists("/var/lib/dpkg/status"):
                self.picload.startDecode(png, False)
            else:
                self.picload.startDecode(png, 0, 0, False)
            ptr = self.picload.getData()
            if ptr is not None:
                self['poster'].instance.setPixmap(ptr)
                self['poster'].show()
            return

    def image_downloaded(self, data, pictmp):
        if file_exists(pictmp):
            try:
                self.decodeImage(pictmp)
            except Exception as e:
                print("* error ** %s" % e)

    def downloadError(self, error=""):
        try:
            if self["poster"].instance:
                self["poster"].instance.setPixmapFromFile(piclogo)
            print('error download: ', error)
        except Exception as e:
            print('error downloadError poster', e)

    def showAfterSeek(self):
        if isinstance(self, IPTVInfoBarShowHide):
            self.doShow()

    def timeshift_autoplay(self):
        if self.timeshift_url:
            try:
                eserv = int(cfg.services.value)
                self.reference = eServiceReference(eserv, 0, self.timeshift_url)
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
            STREAMS.cont_play = self.cont_play

    def timeshift(self):
        if self.timeshift_url:
            try:
                eserv = int(cfg.services.value)
                self.reference = eServiceReference(eserv, 0, self.timeshift_url)
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
        STREAMS.cont_play = self.cont_play

    def show_info(self):
        if STREAMS.play_vod is True:
            self["state"].setText(" PLAY     >")
        self.hideTimer.start(5000, True)
        if self.cont_play:
            self["cont_play"].setText("Auto Play ON")
        else:
            self["cont_play"].setText("Auto Play OFF")

    def helpx(self):
        self.session.open(xc_help)

    def restartVideo(self):
        try:
            index = STREAMS.list_index
            video_counter = len(iptv_list_tmp)
            if index < video_counter:
                if iptv_list_tmp[index][4] is not None:
                    STREAMS.list_index = index
                    self.player_helper()
        except Exception as e:
            print(e)

    def nextVideo(self):
        try:
            index = STREAMS.list_index + 1
            video_counter = len(iptv_list_tmp)
            if index < video_counter:
                if iptv_list_tmp[index][4] is not None:
                    STREAMS.list_index = index
                    self.player_helper()
        except Exception as e:
            print(e)

    def prevVideo(self):
        try:
            index = STREAMS.list_index - 1
            if index > -1:
                if iptv_list_tmp[index][4] is not None:
                    STREAMS.list_index = index
                    self.player_helper()
        except Exception as e:
            print(e)

    def player_helper(self):
        self.show_info()
        self.channelx = iptv_list_tmp[STREAMS.list_index]
        STREAMS.play_vod = False
        STREAMS.list_index_tmp = STREAMS.list_index
        self.setCover()
        self.play_vod()

    def record(self):
        try:
            if STREAMS.trial != '':
                self.session.open(MessageBox, 'Trialversion dont support this function', type=MessageBox.TYPE_INFO, timeout=10)
            else:
                try:
                    self.session.open(MessageBox, 'BLUE = START PLAY RECORDED VIDEO', type=MessageBox.TYPE_INFO, timeout=5)
                    self.session.nav.stopService()
                    self['state'].setText('RECORD')
                    pth = urlparse(self.vod_url).path
                    ext = splitext(pth)[-1]
                    filename = Utils.cleantitle(self.titlex)
                    if ext not in EXTDOWN:
                        ext = '.avi'
                    filename = filename + ext
                    self.filename = filename.lower()  # + ext
                    cmd = "wget --no-cache --no-dns-cache -U %s -c '%s' -O '%s%s' --post-data='action=purge'" % ('Enigma2 - XC Forever Plugin', self.vod_url, str(Path_Movies), self.filename)
                    if "https" in str(self.vod_url):
                        cmd = "wget --no-check-certificate --no-cache --no-dns-cache -U %s -c '%s' -O '%s%s' --post-data='action=purge'" % ('Enigma2 - XC Forever Plugin', self.vod_url, str(Path_Movies), self.filename)
                    self.timeshift_url = Path_Movies + self.filename

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
            with open('%s/%s.meta' % (Path_Movies, filename), 'w') as f:
                f.write('%s\n%s\n%s\n%i\n' % (serviceref.toString(), filmtitle, "", time.time()))
        except Exception as e:
            print(e)
            print('ERROR metaFile')

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

    def stopnew(self):
        if STREAMS.playhack == "":
            self.session.nav.stopService()
            STREAMS.play_vod = False
            self.recorder = False
            self.video_back = False
            self.session.nav.playService(self.initialservice)
        self.exitx()

    def power_off(self):
        self.close(1)

    def nextAR(self):
        message = nextAR()
        self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=3)

    def prevAR(self):
        message = prevAR()
        self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=3)

    def show_more_info(self):
        index = STREAMS.list_index
        if self.vod_url is not None:
            name = str(self.channelx[1])
            show_more_infos(name, index)

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
        self.channelx = iptv_list_tmp[STREAMS.list_index]
        self.vod_url = self.channelx[4]
        self.titlex = self.channelx[1]
        self.descr = self.channelx[2]
        if self.descr != '' or self.descr is not None:
            text_clear = str(self.descr)
            self["programm"].setText(text_clear)
        try:
            if self.vod_url is not None:
                print("------------------------ MOVIE ------------------")
                print('--->' + self.vod_url + '<------')
                self.session.nav.stopService()
                eserv = int(cfg.services.value)
                self.reference = eServiceReference(eserv, 0, self.vod_url)
                self.reference.setName(self.titlex)
                self.session.nav.playService(self.reference)
            else:
                if self.error_message:
                    self.session.open(MessageBox, self.error_message, type=MessageBox.TYPE_INFO, timeout=3)
                else:
                    self.session.open(MessageBox, "NO VIDEOSTREAM FOUND", type=MessageBox.TYPE_INFO, timeout=3)

                self.video_back = False
                self.close()
        except Exception as e:
            print(e)


class xc_StreamTasks(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        skin = os.path.join(skin_path, 'xc_StreamTasks.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setup_title = ('XCplugin Forever')
        self["movielist"] = List([])
        self["key_green"] = Label(_("Remove"))
        self["key_red"] = Label(_("Close"))
        self['totalItem'] = Label()
        self['label2'] = Label()
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions"], {
                                    "ok": self.keyOK,
                                    "esc": self.keyClose,
                                    "exit": self.keyClose,
                                    "green": self.message1,
                                    "red": self.keyClose,
                                    "blue": self.keyBlue,
                                    "cancel": self.keyClose}, -1)
        self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
        self.Timer = eTimer()
        try:
            self.Timer_conn = self.Timer.timeout.connect(self.TimerFire)
        except:
            self.Timer.callback.append(self.TimerFire)
        self.onLayoutFinish.append(self.layoutFinished)
        self.onClose.append(self.__onClose)

    def __onClose(self):
        del self.Timer

    def layoutFinished(self):
        self.Timer.startLongTimer(2)

    def TimerFire(self):
        self.Timer.stop()
        self.rebuildMovieList()

    def rebuildMovieList(self):
        if file_exists(Path_Movies):
            self.movielist = []
            self.getTaskList()
            self.getMovieList()
            self["movielist"].setList(self.movielist)
            self["movielist"].updateList(self.movielist)
        else:
            message = "The Movie path not configured or path not exist!!!"
            Utils.web_info(message)
            self.close()

    def getTaskList(self):
        for job in JobManager.getPendingJobs():
            self.movielist.append((
                job,
                job.name,
                job.getStatustext(),
                int(100 * job.progress // float(job.end)),
                str(100 * job.progress // float(job.end)) + "%"))
        if len(self.movielist) >= 0:
            self.Timer.startLongTimer(10)
        return

    def getMovieList(self):
        global filelist, file1
        free = _('Free Space')
        folder = _('Movie Folder')
        self.totalItem = '0'
        file1 = False
        filelist = ''
        self.pth = ''
        freeSize = "-?-"
        if os.path.isdir(cfg.pthmovie.value):
            filelist = listdir(cfg.pthmovie.value)
            if filelist is not None:
                file1 = True
                filelist.sort()
                count = 0
                for filename in filelist:
                    if file_exists(Path_Movies + filename):
                        extension = filename.split('.')
                        extension = extension[-1].lower()
                        if extension in EXTENSIONS:
                            count = count + 1
                            self.totalItem = str(count)
                            movieFolder = os.statvfs(cfg.pthmovie.value)
                            try:
                                stat = movieFolder
                                freeSize = Utils.convert_size(float(stat.f_bfree * stat.f_bsize))
                            except Exception as e:
                                print(e)
                    titel2 = '%s: %s %s' % (folder, str(freeSize), free)
                    self['label2'].setText(titel2)
                    self['totalItem'].setText('Item %s' % str(self.totalItem))
                    self.movielist.append(("movie", filename, _("Finished"), 100, "100%"))
        else:
            titel2 = '(%s offline)' % folder
            self['label2'].setText(titel2)
            self['totalItem'].setText('Item %s' % str(self.totalItem))

    def keyOK(self):
        global file1
        # listsx = self.movielist
        # index = self["movielist"].getSelectionIndex()
        current = self["movielist"].getCurrent()
        path = Path_Movies
        if current:
            if current[0] == "movie":
                if file1 is True:
                    path = Path_Movies
                url = path + current[1]
                name = current[1]
                file1 = False
                isFile = file_exists(url)
                if isFile:
                    self.session.open(M3uPlay2, name, url)
                else:
                    self.session.open(MessageBox, _("Is Directory or file not exist"), MessageBox.TYPE_INFO, timeout=5)
            else:
                job = current[0]
                self.session.openWithCallback(self.JobViewCB, JobView, job)

    def keyBlue(self):
        pass

    def JobViewCB(self, why):
        pass

    def keyClose(self):
        if STREAMS.playhack == "":
            self.session.nav.stopService()
            self.session.nav.playService(self.initialservice)
        self.close()

    def message1(self, answer=None):
        current = self["movielist"].getCurrent()
        sel = Path_Movies + current[1]
        sel2 = self.pth + current[1]
        dom = sel
        if answer is None:
            self.session.openWithCallback(self.message1, MessageBox, _("Do you want to remove %s ?") % dom)
        elif answer:
            if file_exists(sel):
                if self.Timer:
                    self.Timer.stop()
                cmd = 'rm -f ' + sel
                system(cmd)
                self.session.open(MessageBox, sel + _(" Movie has been successfully deleted\nwait time to refresh the list..."), MessageBox.TYPE_INFO, timeout=5)
            elif file_exists(sel2):
                if self.Timer:
                    self.Timer.stop()
                cmd = 'rm -f ' + sel2
                system(cmd)
                self.session.open(MessageBox, sel2 + _(" Movie has been successfully deleted\nwait time to refresh the list..."), MessageBox.TYPE_INFO, timeout=5)
            else:
                self.session.open(MessageBox, _("The movie not exist!\nwait time to refresh the list..."), MessageBox.TYPE_INFO, timeout=5)
            self.onShown.append(self.rebuildMovieList)
        else:
            return


class xc_help(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        skin = os.path.join(skin_path, 'xc_help.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setup_title = ('XCplugin Forever')
        self["version"] = Label(version)
        self["key_red"] = Label(_("Back"))
        self["key_green"] = Label(_("Config"))
        self["key_yellow"] = Label(_("Main"))
        self["key_blue"] = Label(_("Player"))
        self["helpdesc"] = Label()
        self["helpdesc2"] = Label()
        self["paypal"] = Label()
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {
            "red": self.exitx,
            "green": self.green,
            "yellow": self.yellow,
            "blue": self.blue,
            "ok": self.exitx,
            "cancel": self.exitx}, -1)
        self.onLayoutFinish.append(self.finishLayout)

    def finishLayout(self):
        helpdesc = self.homecontext()
        helpdesc2 = self.homecontext2()
        pay = paypal()
        self["paypal"].setText(pay)
        self["helpdesc"].setText(helpdesc)
        self["helpdesc2"].setText(helpdesc2)

    def homecontext(self):
        conthelp = "%s\n\n" % version
        conthelp += "original code by Dave Sully, Doug Mackay\n\n"
        conthelp += "Modded by Lululla\n\n"
        conthelp += "Skin By: Mmark - Info e2skin.blogspot.it\n\n"
        conthelp += "*************************************\n\n"
        conthelp += "Please reports bug or info to forums:\n\n"
        conthelp += "Corvoboys - linuxsat-support\n\n"
        conthelp += "*************************************\n\n"
        conthelp += "Special thanks to:\n"
        conthelp += "MMark, Pcd, KiddaC\n"
        conthelp += "aime_jeux, Support, Enigma1969, linuxsat-support.com\n"
        conthelp += "and all those i forgot to mention.\n\n"
        return conthelp

    def homecontext2(self):
        conthelp = "Config Folder file xml %s\n" % cfg.pthxmlfile.value
        conthelp += "Config Media Folder %s/\n" % cfg.pthmovie.value
        conthelp += "LivePlayer Active %s\n" % cfg.LivePlayer.value
        conthelp = "Current Service Type: %s\n" % cfg.services.value
        conthelp += _("Current configuration for creating the bouquet\n    > %s Conversion %s\n\n") % (cfg.typem3utv.getValue(), cfg.typelist.getValue())

        return conthelp

    def yellow(self):
        helpdesc = self.yellowcontext()
        self["helpdesc"].setText(helpdesc)
        helpdesc2 = self.homecontext2()
        self["helpdesc2"].setText(helpdesc2)
        self["helpdesc2"].show()

    def yellowcontext(self):
        conthelp = "HOME - MAIN\n"
        conthelp += _("    (MENU BUTTON):\n")
        conthelp += _("            Config Setup Options\n")
        conthelp += _("    (5 BUTTON):\n")
        conthelp += _("            MediaPlayer\n")
        conthelp += _("    (9/Help BUTTON):\n")
        conthelp += _("            Help\n")
        conthelp += _("    (PVR/FILELIST/2 BUTTON):\n")
        conthelp += _("            Open Movie Folder\n")
        conthelp += _("    (EPG/INFO/0 BUTTON):\n")
        conthelp += _("            Epg guide or imdb/tmdb\n")
        conthelp += _("    (GREEN BUTTON):\n ")
        conthelp += _("            Start Download or Record Selected Channel:\n")
        conthelp += _("            Set 'Live Player Active' in Setting:\n")
        conthelp += _("            Set 'No' for Record Live\n")
        conthelp += _("    (YELLOW BUTTON):\n")
        conthelp += _("            Start Download All Episodes Series\n")
        conthelp += _("    (BLUE BUTTON): Search LIve/Movie")
        return conthelp

    def green(self):
        helpdesc = self.greencontext()
        helpdesc2 = self.homecontext2()
        self["helpdesc"].setText(helpdesc)
        self["helpdesc2"].setText(helpdesc2)
        self["helpdesc2"].show()

    def greencontext(self):
        conthelp = "MENU CONFIG\n\n"
        conthelp += _("    (YELLOW BUTTON):\n")
        conthelp += _("            If you have a file format:\n")
        conthelp += _("            /etc/enigma2/iptv.sh\n")
        conthelp += _("            USERNAME='xxxxxxxxxx'\n")
        conthelp += _("            PASSWORD='yyyyyyyyy'\n")
        conthelp += _("            url='http://server:port/xxyyzz'\n")
        conthelp += _("            Import with Yellow Button this file\n\n")

        conthelp += _("    (BLUE BUTTON):\n")
        conthelp += _("            If you have a file format:\n")
        conthelp += _("            /tmp/xc.txt\n")
        conthelp += _("            host\t(host without http:// )\n")
        conthelp += _("            port\n")
        conthelp += _("            user\n")
        conthelp += _("            password\n")
        conthelp += _("            Import with Blue Button this file")
        return conthelp

    def blue(self):
        helpdesc = self.bluecontext()
        self["helpdesc"].setText(helpdesc)

        helpdesc2 = self.homecontext2()
        self["helpdesc2"].setText(helpdesc2)

        self["helpdesc2"].hide()

    def bluecontext(self):
        conthelp = "PLAYER XC\n"
        conthelp += _("    (RED BUTTON):\n")
        conthelp += _("            Return to Channels List\n")
        conthelp += _("    (BLUE BUTTON):\n")
        conthelp += _("            Init Continue Play\n")
        conthelp += _("    (REC BUTTON):\n")
        conthelp += _("            Download Video \n")
        conthelp += _("    (STOP BUTTON):\n")
        conthelp += _("            Close/Stop Movie/Live\n")
        conthelp += ("        ___________________________________\n\n")
        conthelp += _("UTILITY PLAYER M3U\n")
        conthelp += _("    (GREEN BUTTON):\n")
        conthelp += _("            Remove file from list\n")
        conthelp += _("    (YELLOW BUTTON):\n")
        conthelp += _("            Export file m3u to Bouquet .tv\n")
        conthelp += _("    (BLUE BUTTON):\n")
        conthelp += _("            Download file m3u from current server\n\n")
        conthelp += _("UTILITY PLAYER M3U - OPEN FILE:\n")
        conthelp += _("    When opening an .m3u file instead:\n")
        conthelp += _("   (GREEN BUTTON):\n")
        conthelp += _("           Reload List\n")
        conthelp += _("   (YELLOW BUTTON):\n")
        conthelp += _("           Download VOD selected channel\n")
        conthelp += _("   (BLUE BUTTON):\n")
        conthelp += _("           Search for a title in the list\n")
        return conthelp

    def exitx(self):
        self.close()


class xc_Epg(Screen):
    def __init__(self, session, text_clear):
        Screen.__init__(self, session)
        self.session = session
        skin = os.path.join(skin_path, 'xc_epg.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setup_title = ('XCplugin Forever')
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {
            "red": self.close,
            "cancel": self.close,
            "ok": self.close}, -1)
        text = text_clear
        self["key_red"] = Label(_("Back"))
        self["text_clear"] = StaticText()
        self["text_clear"].setText(text)


class xc_maker(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        skin = os.path.join(skin_path, 'xc_maker.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setup_title = ('XCplugin Forever')
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
            "menu": self.config,
            "help": self.helpx,
            "green": self.maker,
            "yellow": self.remove}, -1)
        self.onLayoutFinish.append(self.updateMenuList)

    def config(self):
        self.session.open(xc_config)

    def exitY(self):
        self.close()

    def helpx(self):
        self.session.open(xc_help)

    def updateMenuList(self):
        global infoname
        if cfg.infoexp.getValue():
            infoname = str(cfg.infoname.value)
        self["description"].setText(self.getabout())
        self["Text"].setText(infoname)

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
        # Utils.ReloadBouquets()

    def save_tv(self, result):
        if result:
            save_old()
            self.session.open(MessageBox, _("Reload Playlists in progress...") + "\n\n\n" + _("wait please..."), MessageBox.TYPE_INFO, timeout=8)
            return

    def createCfgxml(self, result):
        if result:
            make_bouquet()
            self.session.open(MessageBox, _("Reload Playlists in progress...") + "\n\n\n" + _("wait please..."), MessageBox.TYPE_INFO, timeout=8)
            return

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
        conthelp += _("   Create XC Live/VOD Bouquets\n")
        conthelp += _("    You need to configure the type of output\n")
        conthelp += _("    in the config menu\n\n")
        conthelp += _("YELLOW BUTTON:\n")
        conthelp += _("    Removes all the bouquets that have been\n")
        conthelp += _("    created with XCplugin\n\n")
        conthelp += _("HELP BUTTON:\n")
        conthelp += _("    Go to Help info plugin\n\n\n")
        conthelp += "        ___________________________________\n\n"
        conthelp += "Config Folder file xml %s\n" % cfg.pthxmlfile.value
        conthelp += "Config Media Folder %s/\n" % cfg.pthmovie.value
        conthelp += "LivePlayer Active %s\n" % cfg.LivePlayer.value
        conthelp += "Current Service Type: %s\n" % cfg.services.value
        conthelp += _("Current configuration for creating the bouquet\n    > %s Conversion %s\n\n") % (cfg.typem3utv.getValue(), cfg.typelist.getValue())
        conthelp += "        ___________________________________\n\n"
        conthelp += "Time is what we want most,\n"
        conthelp += "    but what we use worst.(William Penn)"
        return conthelp


class OpenServer(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        skin = os.path.join(skin_path, 'xc_OpenServer.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setup_title = ('XCplugin Forever')
        self.list = []
        self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
        self["list"] = xcM3UList([])
        self["Text"] = Label("Select Server")
        self["version"] = Label(version)
        self["playlist"] = Label("")
        self["key_red"] = Label(_("Back"))
        self["key_green"] = Label()
        self["key_yellow"] = Label(_("Remove"))
        self["key_blue"] = Label(_("Info"))
        self["live"] = Label("")
        self["actions"] = HelpableActionMap(self, "XCpluginActions", {
            "ok": self.selectlist,

            "home": self.close,
            "cancel": self.close,
            "yellow": self.message1,
            "blue": self.infoxc,
            "info": self.helpx,
            "help": self.helpx}, -1)
        self.onLayoutFinish.append(self.openList)
        # self.onShow.append(self.openList)

    def selOn(self, host, port, username, password, png=None):
        try:
            TIME_GMT = '%d-%m-%Y %H:%M:%S'
            auth = status = created_at = exp_date = active_cons = max_connections = server_protocol = timezone = '- ? -'
            # url_info = 'http://' + str(host) + ':' + str(port) + '/player_api.php?username=' + str(user) + '&password=' + str(passw) + '&action=user&sub=info'
            # urlinfo = 'http://' + str(host) + ':' + str(port) + '/player_api.php?username=' + str(user) + '&password=' + str(passw)
            urlinfo = 'http://' + str(host) + ':' + str(port) + '/player_api.php?username=' + str(username) + '&password=' + str(password)
            import requests
            from requests.adapters import HTTPAdapter
            hdr = {"User-Agent": "Enigma2 - XCForever Plugin"}
            r = ""
            adapter = HTTPAdapter()
            http = requests.Session()
            http.mount("http://", adapter)
            http.mount("https://", adapter)
            r = http.get(urlinfo, headers=hdr, timeout=15, verify=False, stream=True)
            r.raise_for_status()
            if r.status_code == requests.codes.ok:
                print('r.status code: ', r.status_code)
                y = r.json()
                if "user_info" in y:
                    if "auth" in y["user_info"]:
                        if y["user_info"]["auth"] == 1:
                            auth = (y["user_info"]["auth"])
                            status = (y["user_info"]["status"])
                            created_at = (y["user_info"]["created_at"])
                            exp_date = (y["user_info"]["exp_date"])
                            # active_cons = (y["user_info"]["active_cons"])
                            # max_connections = (y["user_info"]["max_connections"])
                            # server_protocol = (y["server_info"]["server_protocol"])
                            # timezone = (y["server_info"]["timezone"])
                            if created_at:
                                created_at = time.strftime(TIME_GMT, time.gmtime(int(created_at)))
                            if exp_date:
                                exp_date = time.strftime(TIME_GMT, time.gmtime(int(exp_date)))
                            if str(auth) == "1":  # force for message popup
                                if str(status) == "Active":
                                    auth = "Active\nExp date: " + str(exp_date)
                                elif str(status) == "Banned":
                                    auth = "Banned"
                                elif str(status) == "Disabled":
                                    auth = "Disabled"
                                elif str(status) == "Expired":
                                    auth = "Expired"
                                elif str(status) == "None":
                                    auth = "N/A"
                                    status = 'N/A'
                                elif status is None:
                                    auth = "N/A"
                                    status = 'N/A'
                                else:
                                    auth = "Server Not Responding" + str(exp_date)
                                    status = 'N/A'
                                print('auth=', auth)
                                print('status=', str(status))
                                # active_cons = "User Active Now: " + str(active_cons)
                                # max_connections = "Max Connect: " + str(max_connections)
                                # server_protocol = "Protocol: " + str(server_protocol)
                                # timezone = "Timezone: " + str(timezone)
                                return str(status)
        except Exception as e:
            status = 'N/A'
            message = ("Error %s") % (e)
            print(str(message))

    def openList(self):
        self.names = []
        self.urls = []
        # self.pics = []
        if os.path.exists(Path_XML + '/xclink.txt'):
            with codecs.open(Path_XML + '/xclink.txt', "r", encoding="utf-8") as f:
                lines = f.readlines()
                f.seek(0)
                name = ''
                # host = ''
                port = ''
                username = ''
                # password = ''
                # listtype = ''
                for line in lines:
                    if line.startswith('#'):
                        continue
                    elif line.startswith('http'):
                        print('line is:', line)
                        # Estrai l'host, la porta, l'username, la password e il tipo dalla linea
                        pattern = r"http://([^:/]+)(?::(\d+))?/get.php\?username=([^&]+)&password=([^&]+)&type=([^&]+)"  # &output=([^&]+)"
                        match = re.match(pattern, line)
                        if match:
                            host = match.group(1)
                            if match.group(2):
                                port = match.group(2)  # or 80
                            username = match.group(3)
                            password = match.group(4)
                            # listtype = match.group(5)
                            # output = match.group(6)
                            namelx = self.selOn(str(host), str(port), str(username), str(password))
                            if namelx == 'None' or namelx is None:
                                namelx = 'N/A'
                            name = '(' + str(namelx) + ')' + ' xc_' + str(username)
                            print(str(name))
                            self.names.append(name)
                            self.urls.append(line)
                            # self.pics.append(pngd)

                        m3ulistxc(self.names, self["list"])
        self["live"].setText(str(len(self.names)) + " Team")
        global infoname
        if cfg.infoexp.getValue():
            infoname = str(cfg.infoname.value)
        self["playlist"].setText(infoname)

    def Start_iptv_player(self):
        global STREAMS
        STREAMS = iptv_streamse()
        STREAMS.read_config()
        if "exampleserver.com" not in STREAMS.xtream_e2portal_url:
            STREAMS.get_list(STREAMS.xtream_e2portal_url)
            self.session.openWithCallback(check_configuring, xc_Main)
        else:
            self.session.open(xc_Main)

    def selectlist(self):
        try:
            idx = self["list"].getSelectionIndex()
            dom = self.urls[idx]
            pattern = r"http://([^:/]+)(?::(\d+))?/get.php\?username=([^&]+)&password=([^&]+)&type=([^&]+)"  # &output=([^&]+)"
            match = re.match(pattern, dom)
            if match:
                host = match.group(1)
                if match.group(2):
                    port = match.group(2)
                    cfg.port.setValue(str(port))
                username = match.group(3)
                password = match.group(4)
                # listtype = match.group(5)
                cfg.hostaddress.setValue(str(host))
                cfg.user.setValue(str(username))
                cfg.passw.setValue(str(password))
                self.Start_iptv_player()
        except IOError as e:
            print(e)

    def infoxc(self):
        try:
            idx = self["list"].getSelectionIndex()
            dom = self.urls[idx]
            print('link dom:', dom)
            TIME_GMT = '%d-%m-%Y %H:%M:%S'
            auth = status = created_at = exp_date = active_cons = max_connections = server_protocol = timezone = '- ? -'
            host = ''
            username = ''
            password = ''
            port = '80'
            pattern = r"http://([^:/]+)(?::(\d+))?/get.php\?username=([^&]+)&password=([^&]+)&type=([^&]+)"  # &output=([^&]+)"
            match = re.match(pattern, dom)
            if match:
                host = match.group(1)
                if match.group(2):
                    port = match.group(2)
                else:
                    port = '80'
                username = match.group(3)
                password = match.group(4)
                # listtype = match.group(5)
                # output = match.group(6)
            # url_info = 'http://' + str(host) + ':' + str(port) + '/player_api.php?username=' + str(user) + '&password=' + str(passw) + '&action=user&sub=info'
            # urlinfo = 'http://' + str(host) + ':' + str(port) + '/player_api.php?username=' + str(user) + '&password=' + str(passw)
            urlinfo = 'http://' + str(host) + ':' + str(port) + '/player_api.php?username=' + str(username) + '&password=' + str(password)
            print('urlinfo:', urlinfo)
            import requests
            from requests.adapters import HTTPAdapter
            hdr = {"User-Agent": "Enigma2 - XCForever Plugin"}
            r = ""
            adapter = HTTPAdapter()
            http = requests.Session()
            http.mount("http://", adapter)
            http.mount("https://", adapter)
            r = http.get(urlinfo, headers=hdr, timeout=15, verify=False, stream=True)
            r.raise_for_status()
            if r.status_code == requests.codes.ok:
                y = r.json()
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
                            if str(auth) == "1":  # force for message popup
                                if str(status) == "Active":
                                    auth = "Active\nExp date: " + str(exp_date)
                                elif str(status) == "Banned":
                                    auth = "Banned"
                                elif str(status) == "Disabled":
                                    auth = "Disabled"
                                elif str(status) == "Expired":
                                    auth = "Expired"
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
                    # self.openList()
            except OSError as error:
                print(error)
                self.session.open(MessageBox, nam + _(" not exist!\nwait time to refresh the list..."), MessageBox.TYPE_INFO, timeout=5)
            self["live"].setText(str(len(self.names)) + " Team")
            m3ulistxc(self.names, self["list"])
        else:
            return

    def helpx(self):
        # self.session.open(xc_help)
        self.session.open(MessageBox, _("Put your lines to the %s/xclink.txt'.\nFormat type:\n\nhttp://YOUR_HOST/get.php?username=USERNAME&password=PASSWORD&type=m3u\n\nhttp://YOUR_HOST:YOUR_PORT/get.php?username=USERNAME&password=PASSWORD&type=m3u_plus'\n\nSelect list from Menulist" % Path_XML), MessageBox.TYPE_INFO, timeout=5)


class nIPTVplayer(Screen, InfoBarBase, IPTVInfoBarShowHide, InfoBarSeek, InfoBarAudioSelection, InfoBarSubtitleSupport, SubsSupportStatus, SubsSupport):
    STATE_IDLE = 0
    STATE_PLAYING = 1
    STATE_PAUSED = 2
    ENABLE_RESUME_SUPPORT = True
    ALLOW_SUSPEND = True

    def __init__(self, session, recorder_sref=None):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        self.recorder_sref = None
        skin = os.path.join(skin_path, 'xc_iptv_player.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        InfoBarBase.__init__(self, steal_current_service=True)
        IPTVInfoBarShowHide.__init__(self)
        InfoBarSeek.__init__(self, actionmap="InfobarSeekActions")
        InfoBarAudioSelection.__init__(self)
        InfoBarSubtitleSupport.__init__(self)
        SubsSupport.__init__(self, searchSupport=True, embeddedSupport=True)
        SubsSupportStatus.__init__(self)
        # self.orig_aspect = int(self.getAspect())
        try:
            self.init_aspect = int(self.getAspect())
        except:
            self.init_aspect = 0
        self.new_aspect = self.init_aspect

        self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
        self["channel_name"] = Label("")
        self["programm"] = Label("")
        self["poster"] = Pixmap()
        STREAMS.play_vod = False
        self.channel_list = iptv_list_tmp
        self.index = STREAMS.list_index
        self.channely = iptv_list_tmp[STREAMS.list_index]
        self.live_url = self.channely[4]
        self.titlex = self.channely[1]
        self.descr = self.channely[2]
        self.cover = self.channely[3]
        self.pixim = self.channely[7]
        self.service = None
        self["actions"] = HelpableActionMap(self, "XCpluginActions", {
            "info": self.show_more_info,
            "0": self.show_more_info,
            "home": self.exitx,
            "cancel": self.exitx,
            "stop": self.exitx,
            "help": self.helpx,
            "up": self.prevChannel,
            "down": self.nextChannel,
            "next": self.nextChannel,
            "previous": self.prevChannel,
            "channelUp": self.nextAR,
            "channelDown": self.prevAR,
            "power": self.power_off}, -1)
        self.onFirstExecBegin.append(self.play_channel)

    def getAspect(self):
        try:
            return AVSwitch().getAspectRatioSetting()
        except:
            pass

    def getAspectString(self, aspectnum):
        return {
            0: '4:3 Letterbox',
            1: '4:3 PanScan',
            2: '16:9',
            3: '16:9 always',
            4: '16:10 Letterbox',
            5: '16:10 PanScan',
            6: '16:9 Letterbox'
        }[aspectnum]

    def setAspect(self, aspect):
        map = {
            0: '4_3_letterbox',
            1: '4_3_panscan',
            2: '16_9',
            3: '16_9_always',
            4: '16_10_letterbox',
            5: '16_10_panscan',
            6: '16_9_letterbox'
        }
        config.av.aspectratio.setValue(map[aspect])
        try:
            AVSwitch().setAspectRatio(aspect)
        except:
            pass

    def av(self):
        temp = int(self.getAspect())
        temp += 1
        if temp > 6:
            temp = 0
        self.new_aspect = temp
        self.setAspect(temp)

    def nextAR(self):
        message = nextAR()
        self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=3)

    def prevAR(self):
        message = prevAR()
        self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=3)

    def exitx(self):
        self.session.nav.stopService()
        self.session.nav.playService(self.initialservice)
        # self.setAspect(self.orig_aspect)
        self.close()

    def power_off(self):
        self.close(1)

    def play_channel(self):
        try:
            self.channely = iptv_list_tmp[self.index]
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
                        # if PY3:
                        self.cover = six.ensure_binary(self.cover)
                        if self.cover.startswith(b"https") and sslverify:
                            parsed_uri = urlparse(self.cover)
                            domain = parsed_uri.hostname
                            sniFactory = SNIFactory(domain)
                            downloadPage(self.cover, pictmp, sniFactory, timeout=ntimeout).addCallback(self.image_downloaded, pictmp).addErrback(self.downloadError)
                        else:
                            downloadPage(self.cover, pictmp).addCallback(self.image_downloaded, pictmp).addErrback(self.downloadError)
            except Exception as e:
                print(e)
            try:
                print('eserv ----++++++play channel nIPTVplayer 2+++++---')
                if cfg.LivePlayer.value is True:
                    eserv = int(cfg.live.value)
                if str(splitext(self.live_url)[-1]) == ".m3u8":
                    if eserv == 1:
                        eserv = 4097

                self.session.nav.stopService()
                if self.live_url != "" and self.live_url is not None:
                    sref = eServiceReference(eserv, 0, self.live_url)
                    sref.setName(str(self.titlex))
                    try:
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
            STREAMS.list_index = self.index
            STREAMS.list_index_tmp = self.index
            self.play_channel()

    def prevChannel(self):
        index = self.index
        index -= 1
        if index == -1:
            index = len(self.channel_list) - 1
        if self.channel_list[index][4] is not None:
            self.index = index
            STREAMS.list_index = self.index
            STREAMS.list_index_tmp = self.index
            self.play_channel()

    def helpx(self):
        self.session.open(xc_help)

    def show_more_info(self):
        selected_channel = iptv_list_tmp[self.index]
        if selected_channel:
            name = str(self.titlex)
            show_more_infos(name, self.index)

    def decodeImage(self, png):
        self["poster"].hide()
        if file_exists(png):
            size = self['poster'].instance.size()
            self.picload = ePicLoad()
            self.scale = AVSwitch().getFramebufferScale()
            self.picload.setPara([size.width(), size.height(), self.scale[0], self.scale[1], 0, 1, '#00000000'])
            # _l = self.picload.PictureData.get()
            # del _l[:]
            if file_exists("/var/lib/dpkg/status"):
                self.picload.startDecode(png, False)
            else:
                self.picload.startDecode(png, 0, 0, False)
            ptr = self.picload.getData()
            if ptr is not None:
                self['poster'].instance.setPixmap(ptr)
                self['poster'].show()
            return

    def image_downloaded(self, data, pictmp):
        if file_exists(pictmp):
            try:
                self.decodeImage(pictmp)
            except Exception as e:
                print("* error ** %s" % e)
                pass
            except:
                pass

    def downloadError(self, error=""):
        try:
            if self["poster"].instance:
                self["poster"].instance.setPixmapFromFile(piclogo)
        except Exception as e:
            print('error poster', e)


class xc_Play(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        skin = os.path.join(skin_path, 'xc_M3uLoader.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setup_title = ('XCplugin Forever')
        self.list = []
        self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
        self["list"] = xcM3UList([])
        self.downloading = False
        self.name = Path_Movies
        self["path"] = Label(_("Put .m3u Files in Folder %s") % Path_Movies)
        self["version"] = Label(version)
        self["Text"] = Label("M3u Utility")
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self["progress"].hide()
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
                    self.Movies.append(root + '/' + name)
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
        if self.Movies:
            path = self.Movies[idx]
            if idx < 0 or idx is None:
                return
            else:
                name = path
                if ".m3u" in name:
                    self.session.open(xc_M3uPlay, name)
                    return
                else:
                    name = self.names[idx]
                    sref = eServiceReference(4097, 0, path)
                    sref.setName(name)
                    self.session.openWithCallback(self.backToIntialService, xc_Player, sref)

    def backToIntialService(self, ret=None):
        self.session.nav.stopService()
        self.session.nav.playService(self.initialservice)

    def cancel(self):
        self.close()

    def message1(self, answer=None):
        idx = self["list"].getSelectionIndex()
        if idx < 0 or idx is None:
            return
        dom = self.Movies[idx]
        if answer is None:
            self.session.openWithCallback(self.message1, MessageBox, _("Do you want to remove: %s ?") % dom)
        elif answer:
            try:
                remove(dom)
                print("% s removed successfully" % dom)
                self.session.open(MessageBox, dom + _("   has been successfully deleted\nwait time to refresh the list..."), MessageBox.TYPE_INFO, timeout=5)
                del self.names[idx]
                self.refreshmylist()
            except OSError as error:
                print(error)
                print("File path can not be removed")
                self.session.open(MessageBox, dom + _("   not exist!"), MessageBox.TYPE_INFO, timeout=5)
        else:
            return

    def message3(self, answer=None):
        if "exampleserver.com" not in STREAMS.xtream_e2portal_url:
            if self.downloading is True:
                self.session.open(MessageBox, _("Wait... downloading in progress ..."), MessageBox.TYPE_INFO, timeout=5)
                return
            if answer is None:
                self.session.openWithCallback(self.message3, MessageBox, _("Download M3u File?"))
            elif answer:
                self.downloading = False
                if "exampleserver.com" not in STREAMS.xtream_e2portal_url:
                    self.m3u_url = urlinfo.replace("enigma2.php", "get.php")
                    self.m3u_url = self.m3u_url + '&type=m3u_plus&output=ts'
                    self.m3ulnk = ('wget %s -O ' % self.m3u_url)
                    self.name_m3u = str(cfg.user.value)
                    self.pathm3u = Path_Movies + self.name_m3u + '.m3u'
                    if file_exists(self.pathm3u):
                        cmd = 'rm -f ' + self.pathm3u
                        system(cmd)
                    try:
                        self.downloading = True
                        self.download = downloadWithProgress(self.m3u_url, self.pathm3u)
                        self.download.addProgress(self.downloadProgress)
                        self.download.start().addCallback(self.check).addErrback(self.showError)
                    except Exception as e:
                        print(e)
                else:
                    self.session.open(MessageBox, _('No Server Configured to Download!!!'), MessageBox.TYPE_WARNING)
                    pass
            else:
                return
        else:
            self.refreshmylist()

    def downloadProgress(self, recvbytes, totalbytes):
        self["progress"].show()
        self['progress'].value = int(100 * recvbytes // float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes // 1024, totalbytes // 1024, 100 * recvbytes // float(totalbytes))

    def check(self, fplug):
        checkfile = self.pathm3u
        if file_exists(checkfile):
            self['progresstext'].text = ''
            self.progclear = 0
            self['progress'].setValue(self.progclear)
            self.downloading = False
            self.refreshmylist()

    def showError(self, error):
        self.downloading = False
        self.session.open(MessageBox, _('Download Failed!!!'), MessageBox.TYPE_WARNING)
        self.refreshmylist()

    def message2(self):
        idx = self["list"].getSelectionIndex()
        dom = self.names[idx]
        name = self.Movies[idx]
        if idx < 0 or idx is None:
            return
        if ".m3u" in name:
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
        if idx < 0 or idx is None:
            return
        else:
            name = Path_Movies + self.names[idx]
            namel = self.names[idx]
            xcname = "userbouquet.%s.tv" % namel.replace(".m3u", "").replace(" ", "")
            desk_tmp = ""
            in_bouquets = 0
            if file_exists("/etc/enigma2/%s" % xcname):
                remove("/etc/enigma2/%s" % xcname)
            with open("/etc/enigma2/%s" % xcname, "w") as outfile:
                outfile.write("#NAME %s\r\n" % namel.replace(".m3u", "").replace(" ", "").capitalize())
                for line in open("%s" % name):
                    if line.startswith("http://") or line.startswith("https://"):
                        outfile.write('#SERVICE 4097:0:1:0:0:0:0:0:0:0:%s' % line.replace(':', '%3a'))
                        outfile.write("#DESCRIPTION %s" % desk_tmp)
                    elif line.startswith("#EXTINF"):
                        desk_tmp = "%s" % line.split(",")[-1]
                    elif "<stream_url><![CDATA" in line:
                        outfile.write('#SERVICE 4097:0:1:0:0:0:0:0:0:0:%s\r\n' % line.split("[")[-1].split("]")[0].replace(":", "%3a"))
                        outfile.write("#DESCRIPTION %s\r\n" % desk_tmp)
                    elif "<title>" in line:
                        if "<![CDATA[" in line:
                            desk_tmp = "%s\r\n" % line.split("[")[-1].split("]")[0]
                        else:
                            desk_tmp = "%s\r\n" % line.split("<")[1].split(">")[1]
                outfile.close()
                self.session.open(MessageBox, _("Check on favorites lists..."), MessageBox.TYPE_INFO, timeout=5)
            if file_exists("/etc/enigma2/bouquets.tv"):
                for line in open("/etc/enigma2/bouquets.tv"):
                    if xcname in line:
                        in_bouquets = 1
                if in_bouquets == 0:
                    if file_exists("/etc/enigma2/%s" % xcname) and file_exists("/etc/enigma2/bouquets.tv"):
                        Utils.remove_line("/etc/enigma2/bouquets.tv", xcname)
                        with open("/etc/enigma2/bouquets.tv", "a") as outfile:
                            outfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % xcname)
                outfile.close()
            self.session.open(MessageBox, _("Reload Playlists in progress...") + "\n\n\n" + _("wait please..."), MessageBox.TYPE_INFO, timeout=8)
            Utils.ReloadBouquets()


class xc_M3uPlay(Screen):
    def __init__(self, session, name):
        Screen.__init__(self, session)
        self.session = session
        skin = os.path.join(skin_path, 'xc_M3uPlay.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setup_title = ('XCplugin Forever')
        self.list = []
        self.name = name
        self.downloading = False
        global search_ok
        self.search = ''
        search_ok = False
        self["list"] = xcM3UList([])
        self["version"] = Label(version)
        self["key_red"] = Label(_("Back"))
        self["key_green"] = Label(_("Reload"))
        self["key_yellow"] = Label(_("Download"))
        self["key_blue"] = Label(_("Search"))
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
                            global search_ok
                            search_ok = True
                            url = url.replace(" ", "").replace("\\n", "")
                            self.names.append(str(name))
                            self.urls.append(str(url))
                    if search_ok is True:
                        m3ulistxc(self.names, self["list"])

                        self["live"].setText(str(len(self.names)) + " Stream")
                    else:
                        search_ok = False
                        self.resetSearch()
            except:
                pass
        else:
            self.playList()

    def playList(self):
        global search_ok
        search_ok = False
        self.names = []
        self.urls = []
        self.pics = []
        pic = pictmp
        try:
            if file_exists(self.name):
                fpage = ''
                try:
                    with codecs.open(str(self.name), "r", encoding="utf-8") as f:
                        fpage = f.read()
                except:
                    pass
                if "#EXTM3U" and 'tvg-logo' in fpage:
                    regexcat = 'EXTINF.*?tvg-logo="(.*?)".*?,(.*?)\\n(.*?)\\n'
                    match = re.compile(regexcat, re.DOTALL).findall(fpage)
                    for pic, name, url in match:
                        url = url.replace(' ', '').replace('\\n', '')
                        self.names.append(str(name))
                        self.urls.append(str(url))
                        self.pics.append(str(pic))
                else:
                    regexcat = '#EXTINF.*?,(.*?)\\n(.*?)\\n'
                    match = re.compile(regexcat, re.DOTALL).findall(fpage)
                    for name, url in match:
                        url = url.replace(' ', '').replace('\\n', '')
                        self.names.append(str(name))
                        self.urls.append(str(url))
                        self.pics.append(str(pic))
                m3ulistxc(self.names, self['list'])
                # self.xxd = m3ulistxc
                self["live"].setText('N.' + str(len(self.names)) + " Stream")
            else:
                self.session.open(MessageBox, _('File Unknow!!!'), MessageBox.TYPE_INFO, timeout=5)
        except Exception as e:
            print('error exception: ', e)

    def runChannel(self):
        idx = self["list"].getSelectionIndex()
        # ln = 0
        # for x in self.list:
            # ln +=1
        # ln = ln
        # ln = len(self.xxd([0],[0]))
        # listsx = self.list
        # listsx = [channel for channel in m3ulistxc if idx > 0]
        # print('lnnnnn =', str(ln))
        if idx < 0 or idx is None:
            return
        else:
            name = self.names[idx]
            url = self.urls[idx]
            self.session.open(M3uPlay2, name, url)
            return

    def runRec(self, answer=None):
        idx = self["list"].getSelectionIndex()
        self.namem3u = self.names[idx]
        urlm3u = self.urls[idx]
        pth = urlparse(urlm3u).path
        ext = splitext(pth)[1]
        if ext not in EXTDOWN:
            ext = '.avi'
        self.urlm3u = Utils.decodeUrl(urlm3u)
        if ext in EXTDOWN or ext == '.avi':
            if answer is None:
                self.session.openWithCallback(self.runRec, MessageBox, _("DOWNLOAD VIDEO?\n%s") % self.namem3u)
            elif answer:
                filename = Utils.cleantitle(self.namem3u)
                filename = filename + ext
                self.in_tmp = Path_Movies + filename.lower()
                self.downloading = True
                self.download = downloadWithProgress(self.urlm3u, self.in_tmp)
                self.download.addProgress(self.downloadProgress)
                self.download.start().addCallback(self.check).addErrback(self.showError)
            else:
                return
        else:
            self.session.open(MessageBox, _("Only VOD Movie allowed!!!"), MessageBox.TYPE_INFO, timeout=5)

    def downloadProgress(self, recvbytes, totalbytes):
        self["progress"].show()
        self['progress'].value = int(100 * recvbytes // float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes // 1024, totalbytes // 1024, 100 * recvbytes // float(totalbytes))

    def check(self, fplug):
        checkfile = self.in_tmp
        if file_exists(checkfile):
            self['progresstext'].text = ''
            self.progclear = 0
            self['progress'].setValue(self.progclear)

    def showError(self, error):
        self.downloading = False
        print("download error =", error)
        self.session.open(MessageBox, _('Download Failed!!!'), MessageBox.TYPE_WARNING)

    def resetSearch(self):
        global re_search
        re_search = False
        if len(self.names):
            for x in self.names:
                del x
        self.playList()

    def cancel(self):
        if search_ok is True:
            self.resetSearch()
        else:
            self.close()


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
        # self.orig_aspect = int(self.getAspect())
        try:
            self.init_aspect = int(self.getAspect())
        except:
            self.init_aspect = 0
        self.new_aspect = self.init_aspect
        self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
        url = url.replace(':', '%3a')
        self.url = url
        self.name = name

        # self.index = idx
        # self.list = listsx

        # self.itemscount = len(self.list())

        # ln = len(self.xxd([0,0]))

        self.state = self.STATE_PLAYING
        self['actions'] = ActionMap(['MoviePlayerActions', 'MovieSelectionActions', 'MediaPlayerActions',
                                     'EPGSelectActions', 'MediaPlayerSeekActions', 'SetupActions', 'ColorActions',
                                     'InfobarShowHideActions', 'InfobarActions', 'DirectionActions', 'InfobarSeekActions'], {
                                    'leavePlayer': self.cancel,
                                    'epg': self.showIMDB,
                                    # 'info': self.showIMDB,
                                    'info': self.cicleStreamType,
                                    'tv': self.cicleStreamType,
                                    'stop': self.leavePlayer,
                                    'cancel': self.cancel,
                                    # 'channelDown': self.previousitem,
                                    # 'channelUp': self.nextitem,
                                    # 'down': self.previousitem,
                                    # 'up': self.nextitem,
                                    'back': self.cancel}, -1)

        self.onFirstExecBegin.append(self.cicleStreamType)
        self.onClose.append(self.cancel)

    # def nextitem(self):
        # currentindex = int(self.index) + 1
        # if currentindex == self.itemscount:
            # currentindex = 0
        # self.currentindex = currentindex
        # i = self.currentindex
        # item = self.list[i][0]
        # self.name = item[0]
        # self.url = item[1]
        # self.cicleStreamType()

    # def previousitem(self):
        # currentindex = int(self.currentindex) - 1
        # if currentindex < 0:
            # currentindex = self.itemscount - 1
        # self.currentindex = currentindex
        # i = self.currentindex
        # item = self.list[i][0]
        # self.name = item[0]
        # self.url = item[1]
        # self.cicleStreamType()

    def getAspect(self):
        return AVSwitch().getAspectRatioSetting()

    def getAspectString(self, aspectnum):
        return {0: '4:3 Letterbox',
                1: '4:3 PanScan',
                2: '16:9',
                3: '16:9 always',
                4: '16:10 Letterbox',
                5: '16:10 PanScan',
                6: '16:9 Letterbox'}[aspectnum]

    def setAspect(self, aspect):
        map = {0: '4_3_letterbox',
               1: '4_3_panscan',
               2: '16_9',
               3: '16_9_always',
               4: '16_10_letterbox',
               5: '16_10_panscan',
               6: '16_9_letterbox'}

        config.av.aspectratio.setValue(map[aspect])
        try:
            AVSwitch().setAspectRatio(aspect)
        except:
            pass

    def av(self):
        temp = int(self.getAspect())
        temp = temp + 1
        if temp > 6:
            temp = 0
        self.new_aspect = temp
        self.setAspect(temp)

    def showIMDB(self):
        text_clear = self.name
        if returnIMDB(text_clear):
            print('M3uPlay2 show imdb/tmdb')

    def openPlay(self, servicetype, url):
        name = self.name
        ref = "{0}:0:1:0:0:0:0:0:0:0:{1}:{2}".format(servicetype, url.replace(":", "%3a"), name.replace(":", "%3a"))
        sref = eServiceReference(ref)
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
        if file_exists("/usr/bin/apt-get"):
            streamtypelist.append("8193")
        for index, item in enumerate(streamtypelist, start=0):
            if str(item) == str(self.servicetype):
                currentindex = index
                break
        nextStreamType = islice(cycle(streamtypelist), currentindex + 1, None)
        self.servicetype = int(next(nextStreamType))
        # print('servicetype2: ', self.servicetype)
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
        self.session.nav.stopService()
        self.session.nav.playService(self.initialservice)
        if not self.new_aspect == self.init_aspect:
            try:
                self.setAspect(self.init_aspect)
            except:
                pass
        self.close()

    def leavePlayer(self):
        self.cancel()


Panel_list = [('CONFIG'), ('HOME'), ('PLAYLIST'), ('MAKER BOUQUET'),
              ('MOVIE'), ('PLAYER UTILITY'), ('ABOUT & HELP')]


def xcm3ulistEntry(name):
    png0 = plugin_path + '/skin/pic/xcselh.png'
    pngl = plugin_path + '/skin/pic/xcon.png'
    # png2 = plugin_path + '/skin/hd/xcselh.png'
    # png0 = LoadPixmap(cached=True,
                      # path=resolveFilename(SCOPE_PLUGINS,
                                           # "Extensions/XCplugin/skin/uhd/{}".format('xcselh.png')))
    # png1 = LoadPixmap(cached=True,
                      # path=resolveFilename(SCOPE_PLUGINS,
                                           # "Extensions/XCplugin/skin/fhd/{}".format('xcselh.png')))
    # png2 = LoadPixmap(cached=True,
                      # path=resolveFilename(SCOPE_PLUGINS,
                                           # "Extensions/XCplugin/skin/hd/{}".format('xcselh.png')))
    res = [name]
    white = 16777215

    if screenwidth.width() == 2560:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 4), size=(86, 54), png=loadPNG(png0)))
        res.append(MultiContentEntryText(pos=(140, 0), size=(1800, 60), font=0, text=name, color=white, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    elif screenwidth.width() == 1920:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(64, 40), png=loadPNG(pngl)))
        res.append(MultiContentEntryText(pos=(80, 0), size=(1000, 50), font=0, text=name, color=white, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(66, 40), png=loadPNG(pngl)))
        res.append(MultiContentEntryText(pos=(80, 0), size=(500, 50), font=0, text=name, color=white, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    return res


def m3ulistxc(data, list):
    icount = 0
    mlist = []
    for line in data:
        name = data[icount]
        mlist.append(xcm3ulistEntry(name))
        icount += 1
    list.setList(mlist)


class xcM3UList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        if screenwidth.width() == 2560:
            self.l.setItemHeight(70)
            self.l.setFont(0, gFont("Regular", 54))
        elif screenwidth.width() == 1920:
            self.l.setItemHeight(50)
            self.l.setFont(0, gFont("Regular", 32))
        else:
            self.l.setItemHeight(50)
            self.l.setFont(0, gFont("Regular", 24))


class downloadJob(Job):
    def __init__(self, toolbox, cmdline, filename, filmtitle):
        Job.__init__(self, filmtitle)
        self.cmdline = cmdline
        self.filename = filename
        self.toolbox = toolbox
        self.retrycount = 0
        downloadTask(self, cmdline, filename, filmtitle)

    def retry(self):
        assert self.status == self.FAILED
        self.restart()

    def cancel(self):
        self.abort()


class downloadTaskPostcondition(Condition):
    RECOVERABLE = True

    def check(self, task):
        if task.returncode == 0 or task.error is None:
            return True
        else:
            return False
            return

    def getErrorMessage(self, task):
        return {
            task.ERROR_CORRUPT_FILE: _("MOVIE DOWNLOAD FAILED!") + '\n\n' + _("DOWNLOADED FILE CORRUPTED:") + '\n%s' % task.lasterrormsg,
            task.ERROR_RTMP_ReadPacket: _("MOVIE DOWNLOAD FAILED!") + '\n\n' + _("COULD NOT READ RTMP PACKET:") + '\n%s' % task.lasterrormsg,
            task.ERROR_SEGFAULT: _("MOVIE DOWNLOAD FAILED!") + '\n\n' + _("SEGMENTATION FAULT:") + '\n%s' % task.lasterrormsg,
            task.ERROR_SERVER: _("MOVIE DOWNLOAD FAILED!") + '\n\n' + _("SERVER RETURNED ERROR:") + '\n%s' % task.lasterrormsg,
            task.ERROR_UNKNOWN: _("MOVIE DOWNLOAD FAILED!") + '\n\n' + _("UNKNOWN ERROR:") + '\n%s' % task.lasterrormsg
        }[task.error]


class downloadTask(Task):
    if PY3:
        ERROR_CORRUPT_FILE, ERROR_RTMP_ReadPacket, ERROR_SEGFAULT, ERROR_SERVER, ERROR_UNKNOWN = list(range(5))
    else:
        ERROR_CORRUPT_FILE, ERROR_RTMP_ReadPacket, ERROR_SEGFAULT, ERROR_SERVER, ERROR_UNKNOWN = range(5)

    def __init__(self, job, cmdline, filename, filmtitle):
        Task.__init__(self, job, "Downloading ..." + filmtitle)
        self.toolbox = job.toolbox
        self.setCmdline(cmdline)
        self.filename = filename
        self.filmtitle = filmtitle
        self.error = None
        self.lasterrormsg = None
        self.progress = 0
        self.lastprogress = 0
        self.firstrun = True
        self.starttime = time.time()

    def processOutput(self, data):
        global ui
        if PY3:
            data = str(data)
        try:
            if data.find("%") != -1:
                tmpvalue = re.findall(r'(\d+?%)', data)[-1].rstrip("%")
                self.progress = int(float(tmpvalue))

                if self.firstrun:
                    self.firstrun = False
                    if ui:
                        self.toolbox.updatescreen()

                elif self.progress == 100:
                    self.lastprogress = int(self.progress)
                    if ui:
                        self.toolbox.updatescreen()

                elif int(self.progress) != int(self.lastprogress):
                    self.lastprogress = int(self.progress)

                    elapsed_time = time.time() - self.starttime
                    if ui and elapsed_time > 2:
                        self.starttime = time.time()
                        self.toolbox.updatescreen()
                else:
                    Task.processOutput(self, data)

        except Exception as errormsg:
            print("Error processOutput: " + str(errormsg))
            Task.processOutput(self, data)

    def processOutputLine(self, line):
        pass

    def afterRun(self):
        if self.getProgress() == 100 or self.progress == 100:
            try:
                self.toolbox.download_finished(self.filename, self.filmtitle)
            except Exception as e:
                print(e)


VIDEO_ASPECT_RATIO_MAP = {0: "4:3 Letterbox", 1: "4:3 PanScan", 2: "16:9", 3: "16:9 Always", 4: "16:10 Letterbox", 5: "16:10 PanScan", 6: "16:9 Letterbox"}
VIDEO_FMT_PRIORITY_MAP = {"38": 1, "37": 2, "22": 3, "18": 4, "35": 5, "34": 6}


def nextAR():
    STREAMS.ar_id_player += 1
    if STREAMS.ar_id_player > 6:
        STREAMS.ar_id_player = 0
    try:
        eAVSwitch.getInstance().setAspectRatio(STREAMS.ar_id_player)
        return VIDEO_ASPECT_RATIO_MAP[STREAMS.ar_id_player]
    except Exception as e:
        print(e)
        return _("Resolution Change Failed")


def prevAR():
    STREAMS.ar_id_player -= 1
    if STREAMS.ar_id_player == -1:
        STREAMS.ar_id_player = 6
    try:
        eAVSwitch.getInstance().setAspectRatio(STREAMS.ar_id_player)
        return VIDEO_ASPECT_RATIO_MAP[STREAMS.ar_id_player]
    except Exception as e:
        print(e)
        return _("Resolution Change Failed")


def channelEntryIPTVplaylist(entry):
    menu_entry = [
        entry,
        (eListboxPythonMultiContent.TYPE_TEXT, CHANNEL_NUMBER[0], CHANNEL_NUMBER[1], CHANNEL_NUMBER[2], CHANNEL_NUMBER[3], CHANNEL_NUMBER[4], RT_HALIGN_CENTER | RT_VALIGN_CENTER, "%s" % entry[0]),
        (eListboxPythonMultiContent.TYPE_TEXT, CHANNEL_NAME[0], CHANNEL_NAME[1], CHANNEL_NAME[2], CHANNEL_NAME[3], CHANNEL_NAME[4], RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[1])]
    return menu_entry


def debug(obj, text=""):
    print("%s" % text + " %s\n" % obj)


def uninstaller():
    """Clean up routine to remove any previously made changes
    """
    try:
        for fname in listdir(enigma_path):
            if 'userbouquet.xc_' in fname:
                remove(os.path.join(enigma_path, fname))
            elif 'bouquets.tv.bak' in fname:
                remove(os.path.join(enigma_path, fname))
        if os.path.isdir(epgimport_path):
            for fname in listdir(epgimport_path):
                if 'xc_' in fname:
                    remove(os.path.join(epgimport_path, fname))
        os.rename(os.path.join(enigma_path, 'bouquets.tv'), os.path.join(enigma_path, 'bouquets.tv.bak'))
        tvfile = open(os.path.join(enigma_path, 'bouquets.tv'), 'w+')
        bakfile = open(os.path.join(enigma_path, 'bouquets.tv.bak'), 'r+')
        for line in bakfile:
            if '.xc_' not in line:
                tvfile.write(line)

        bakfile.close()
        tvfile.close()
    except Exception as e:
        print(e)
        raise


# chan_counter,
# str(name),
# str(description),
# piconname,
# stream_url,
# playlist_url,
# str(category_id),
# desc_image,
# str(description2),
# nameepg)
# self.title = str(selected_channel[1])
# self.vod_url = selected_channel[4]
# self.desc = str(selected_channel[2])
# returnIMDB = False
def show_more_infos(name, index):
    text_clear = name
    if "exampleserver.com" not in STREAMS.xtream_e2portal_url:
        selected_channel = iptv_list_tmp[index]
        if selected_channel:
            if stream_live is True:
                text_clear = selected_channel[9]
                # print('text_clear: ', str(text_clear))
            if returnIMDB(text_clear):
                print('show imdb/tmdb')
            else:
                text2 = selected_channel[2]
                text3 = selected_channel[8]
                text_clear += str(text2) + '\n\n' + str(text3)
                _session.open(xc_Epg, text_clear)
    else:
        message = (_("Please enter correct server parameters in Config\n no valid list "))
        Utils.web_info(message)


def save_old():
    fldbouquet = "/etc/enigma2/bouquets.tv"
    namebouquet = STREAMS.playlistname.lower()
    tag = "xc_"
    xc12 = urlinfo.replace("enigma2.php", "get.php") + '&type=dreambox&output=mpegts'
    xc13 = urlinfo.replace("enigma2.php", "get.php") + '&type=m3u_plus&output=ts'
    in_bouquets = 0
    desk_tmp = xcname = ''
    try:
        if cfg.typem3utv.value == 'MPEGTS to TV':
            # xc2 = '&type=dreambox&output=mpegts'
            if file_exists('%suserbouquet.%s%s_.tv' % (enigma_path, tag, namebouquet)):
                remove('%suserbouquet.%s%s_.tv' % (enigma_path, tag, namebouquet))
            try:
                localFile = '%suserbouquet.%s%s_.tv' % (enigma_path, tag, namebouquet)  # ' #resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('tvaddon'))
                r = Utils.getUrl(xc12)
                with open(localFile, 'w') as f:
                    f.write(r)
            except Exception as e:
                print('touch one: ', e)
            xcname = 'userbouquet.%s%s_.tv' % (tag, namebouquet)

        else:
            if file_exists(Path_Movies + namebouquet + ".m3u"):
                remove(Path_Movies + namebouquet + ".m3u")
            try:
                localFile = '%s%s.m3u' % (Path_Movies, namebouquet)
                r = Utils.getUrl(xc13)
                with open(localFile, 'w') as f:
                    f.write(r)
            except Exception as e:
                print('touch two: ', e)

            name = namebouquet.replace('.m3u', '')
            xcname = 'userbouquet.%s%s_.tv' % (tag, name)
            if file_exists('/etc/enigma2/%s' % xcname):
                remove('/etc/enigma2/%s' % xcname)
            with open('/etc/enigma2/%s' % xcname, 'w') as outfile:
                outfile.write('#NAME %s\r\n' % name.capitalize())
                for line in open(Path_Movies + '%s.m3u' % name):
                    if line.startswith('http://') or line.startswith('https://'):
                        outfile.write('#SERVICE 4097:0:1:0:0:0:0:0:0:0:%s' % line.replace(':', '%3a'))
                        outfile.write('#DESCRIPTION %s' % desk_tmp)
                    elif line.startswith('#EXTINF'):
                        desk_tmp = '%s' % line.split(',')[-1]
                    elif '<stream_url><![CDATA' in line:
                        outfile.write('#SERVICE 4097:0:1:0:0:0:0:0:0:0:%s\r\n' % line.split('[')[-1].split(']')[0].replace(':', '%3a'))
                        outfile.write('#DESCRIPTION %s\r\n' % desk_tmp)
                    elif '<title>' in line:
                        if '<![CDATA[' in line:
                            desk_tmp = '%s\r\n' % line.split('[')[-1].split(']')[0]
                        else:
                            desk_tmp = '%s\r\n' % line.split('<')[1].split('>')[1]
                outfile.close()

        # print('-----check in bouquet.tv')
        for line in open(fldbouquet):
            if xcname in line:
                in_bouquets = 1
        if in_bouquets == 0:
            new_bouquet = open("/etc/enigma2/new_bouquets.tv", "w")
            file_read = open(fldbouquet).readlines()
            if cfg.bouquettop.value == "Top":
                new_bouquet.write('#NAME User - bouquets (TV)\n')
                new_bouquet.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % xcname)
                for line in file_read:
                    if line.startswith("#NAME"):
                        continue
                    new_bouquet.write(line)
                new_bouquet.close()
            else:
                for line in file_read:
                    new_bouquet.write(line)
                new_bouquet.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % xcname)
                new_bouquet.close()
            system('cp -rf /etc/enigma2/bouquets.tv /etc/enigma2/backup_bouquets.tv')
            system('mv -f /etc/enigma2/new_bouquets.tv /etc/enigma2/bouquets.tv')
    except Exception as e:
        print(e)


def make_bouquet():
    global infoname
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
    m3u_url = urlinfo.replace("enigma2.php", "get.php")
    epg_url = urlinfo.replace("enigma2.php", "xmltv.php")
    if cfg.infoexp.getValue():
        infoname = str(cfg.infoname.value)

    with open(configfilexml, 'w') as f:
        configtext = '<config>\r\n'
        configtext += '\t<supplier>\r\n'
        configtext += '\t\t<name>' + infoname + '</name>\r\n'
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
    dom = str(STREAMS.playlistname)
    com = ("python %s") % e2m3u2bouquet
    _session.open(Console, _("Conversion %s in progress: ") % dom, ["%s" % com], closeOnSuccess=True)


def menu(menuid, **kwargs):
    if menuid == "mainmenu":
        return [("XCplugin", main, "XCplugin", 4)]
    else:
        return []


def main(session, **kwargs):
    global STREAMS
    STREAMS = iptv_streamse()
    STREAMS.read_config()
    if "exampleserver.com" not in STREAMS.xtream_e2portal_url:
        STREAMS.get_list(STREAMS.xtream_e2portal_url)
        session.openWithCallback(check_configuring, xc_home)
    else:
        session.open(xc_home)


_session = None
autoStartTimer = None
_firstStart = True


class AutoStartTimer:
    def __init__(self, session):
        print("*** running AutoStartTimerFxy ***")
        self.session = session
        if _firstStart:
            if cfg.autoupdate.value is True:
                self.runUpdate()
        self.timer = eTimer()
        try:
            self.timer.callback.append(self.on_timer)
        except:
            self.timer_conn = self.timer.timeout.connect(self.on_timer)
        self.timer.start(100, 1)
        # self.update()

    def runUpdate(self):
        print("*** running update ***")
        global _firstStart
        try:
            from . import Update
            Update.upd_done()
            _firstStart = False
        except Exception as e:
            print('error Fxy', e)

    def get_wake_time(self):
        if cfg.autobouquetupdate.value:
            if cfg.timetype.value == "interval":
                interval = int(cfg.updateinterval.value)
                nowt = time.time()
                return int(nowt) + interval * 60 * 60
            if cfg.timetype.value == "fixed time":
                ftc = cfg.fixedtime.value
                now = time.localtime(time.time())
                fwt = int(time.mktime((now.tm_year,
                                       now.tm_mon,
                                       now.tm_mday,
                                       ftc[0],
                                       ftc[1],
                                       now.tm_sec,
                                       now.tm_wday,
                                       now.tm_yday,
                                       now.tm_isdst)))
                return fwt
        else:
            return -1

    def update(self, constant=0):
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
            next = wake - now
            self.timer.startLongTimer(next)
        else:
            wake = -1
        return wake

    def on_timer(self):
        self.timer.stop()
        now = int(time.time())
        wake = now
        constant = 0
        if cfg.timetype.value == "fixed time":
            wake = self.get_wake_time()
        if wake - now < 60:
            try:
                self.startMain()
                self.update()
                localtime = time.asctime(time.localtime(time.time()))
                cfg.last_update.value = localtime
                cfg.last_update.save()
            except Exception as e:
                print(e)
        self.update(constant)

    def startMain(self):
        from Plugins.Extensions.XCplugin.plugin import iptv_streamse
        global STREAMS
        STREAMS = iptv_streamse()
        STREAMS.read_config()
        STREAMS.get_list(STREAMS.xtream_e2portal_url)
        if str(cfg.typelist.value) == "Combined Live/VOD":
            save_old()
        else:
            make_bouquet()


def check_configuring():
    if cfg.autobouquetupdate.value is True:
        """Check for new config values for auto start
        """
        global autoStartTimer
        if autoStartTimer is not None:
            autoStartTimer.update()
        return


def autostart(reason, session=None, **kwargs):
    global autoStartTimer
    global _firstStart
    global _session
    if reason == 0 and _session is None:
        if session is not None:
            _session = session
            _firstStart = True
            if autoStartTimer is None:
                autoStartTimer = AutoStartTimer(session)
    return


def get_next_wakeup():
    return -1


mainDescriptor = PluginDescriptor(name="XCplugin Forever", description=version, where=PluginDescriptor.WHERE_MENU, fnc=menu)


def Plugins(**kwargs):
    result = [PluginDescriptor(name="XCplugin Forever", description=version, where=[PluginDescriptor.WHERE_AUTOSTART, PluginDescriptor.WHERE_SESSIONSTART], fnc=autostart, wakeupfnc=get_next_wakeup),
              PluginDescriptor(name="XCplugin", description=version, where=PluginDescriptor.WHERE_PLUGINMENU, icon=iconpic, fnc=main)]  # fnc=Start_iptv_player)]
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
# for convertion bouquet credits
# Thanks to @author: Dave Sully, Doug Mackay
# for use e2m3u2bouquet.e2m3u2bouquet -- Enigma2 IPTV m3u to bouquet parser
# @copyright:  2017 All rights reserved.
# @license:        GNU GENERAL PUBLIC LICENSE version 3
# @deffield
# CONVERT TEAM TO ALL FAVORITES LIST MULTIVOD + EPG
# Open the epgimporter plugin via extension's menu.
# Press the blue button to select the sources.
# Select the entry e2m3uBouquet and press the OK button
# Save it with the green button
# Run a manual import using the yellow button manual.
# Save the input with the green button.
# After a while should you the events imported.
# It takes a while so be patient.
# #######################################
# ===================Skin by Mmark Edition for Xc Plugin Infinity please don't copy o remove this
# send credits to autor   ;)
