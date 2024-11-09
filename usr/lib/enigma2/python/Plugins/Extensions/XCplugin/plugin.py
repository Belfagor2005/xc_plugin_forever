#!/usr/bin/python
# -*- coding: utf-8 -*-


'''
****************************************
*        coded by Lululla              *
*             skin by MMark            *
*  update     12/10/2024               *
*       Skin by MMark                  *
****************************************
'''
from __future__ import print_function
from . import (
    _,
    b64decoder,
    developer_url,
    installer_url,
    isDreamOS,
    make_request,
    paypal,
)
from . import Utils
from . import html_conv
from .modul import (
    cleanNames,
    clear_caches,
    copy_poster,
    EXTDOWN,
    EXTENSIONS,
    getAspect,
    globalsxp,
    nextAR,
    prevAR,
    Panel_list,
    setAspect,
)
from .Console import Console as xcConsole
from .downloader import downloadWithProgress

from Components.ActionMap import ActionMap, HelpableActionMap
from Components.config import (
    ConfigClock,
    ConfigDirectory,
    ConfigEnableDisable,
    ConfigPassword,
    ConfigSelection,
    ConfigSelectionNumber,
    ConfigSubsection,
    ConfigText,
    ConfigYesNo,
    config,
    configfile,
    getConfigListEntry,
    NoSave,
)
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import (MultiContentEntryText, MultiContentEntryPixmapAlphaTest)
from Components.Pixmap import Pixmap
from Components.ProgressBar import ProgressBar
from Components.ServiceEventTracker import (ServiceEventTracker, InfoBarBase)
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.Task import (
    Condition,
    Job,
    job_manager as JobManager,
    Task,
)

from datetime import datetime
from Plugins.Plugin import PluginDescriptor

from Screens.Standby import Standby
from Screens.InfoBarGenerics import (
    InfoBarAudioSelection,
    InfoBarMenu,
    InfoBarNotifications,
    InfoBarSeek,
    InfoBarSubtitleSupport,
)

from requests.adapters import HTTPAdapter, Retry
from Screens.LocationBox import LocationBox
from Screens.MessageBox import MessageBox
from Screens.MovieSelection import MovieSelection
from Screens.Screen import Screen
from Screens.TaskView import JobView
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools.Directories import (SCOPE_PLUGINS, resolveFilename)

from enigma import (
    eListboxPythonMultiContent,
    ePicLoad,
    eServiceReference,
    eTimer,
    gFont,
    getDesktop,
    iPlayableService,
    loadPNG,
    RT_HALIGN_CENTER,
    RT_HALIGN_LEFT,
    RT_VALIGN_CENTER,
)

from os import (listdir, remove, system)
from os.path import splitext, isdir
from os.path import exists as file_exists

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


try:
    from Components.AVSwitch import AVSwitch
except ImportError:
    from Components.AVSwitch import eAVControl as AVSwitch

try:
    from xml.etree.cElementTree import fromstring, tostring  # , ElementTree as ET
except ImportError:
    from xml.etree.ElementTree import fromstring, tostring  # , ElementTree as ET


from six.moves.urllib.parse import urlparse
if six.PY3:
    unicode = str
    from urllib.request import (urlopen, Request)
elif six.PY2:
    from urllib2 import (urlopen, Request)


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


currversion = '3.6'
version = "XC Forever V.%s" % currversion
plugin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('XCplugin'))
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


def defaultMoviePath():
    result = config.usage.default_path.value
    if not isdir(result):
        from Tools import Directories
        return Directories.defaultRecordingLocation(config.usage.default_path.value)
    return result


if not isdir(config.movielist.last_videodir.value):
    try:
        config.movielist.last_videodir.value = defaultMoviePath()
        config.movielist.last_videodir.save()
    except:
        pass


config.plugins.XCplugin = ConfigSubsection()
cfg = config.plugins.XCplugin
cfg.LivePlayer = ConfigEnableDisable(default=False)
cfg.autobouquetupdate = ConfigEnableDisable(default=False)
cfg.badcar = ConfigEnableDisable(default=False)
cfg.bouquettop = ConfigSelection(default="Bottom", choices=["Bottom", "Top"])
cfg.data = ConfigYesNo(default=False)
cfg.fixedtime = ConfigClock(default=0)
cfg.infoexp = ConfigYesNo(default=False)
cfg.stoplayer = ConfigYesNo(default=True)
cfg.infoname = NoSave(ConfigText(default="myBouquet"))
cfg.last_update = ConfigText(default="Never")
cfg.live = ConfigSelection(default='1', choices=modelive)
cfg.hostaddress = ConfigText(default="exampleserver.com")
cfg.user = ConfigText(default="Enter_Username", visible_width=50, fixed_size=False)
cfg.passw = ConfigPassword(default="******", visible_width=50, fixed_size=False, censor="*")
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
screenwidth = getDesktop(0).size()
socket.setdefaulttimeout(5)


def check_port(url):
    print('check_port url init=', check_port)
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
    print('check_port return url =', url)
    return url


def retTest(url):
    try:
        retries = Retry(total=1, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retries)
        http = requests.Session()
        http.mount("http://", adapter)
        http.mount("https://", adapter)
        r = http.get(url, headers={'User-Agent': Utils.RequestAgent()}, timeout=10, verify=False)  # , stream=True)
        r.raise_for_status()
        if r.status_code == requests.codes.ok:
            print('retTest r.status code: ', r.status_code)
            ycse = r.json()
            # print('ycse -----------> ', ycse)
            return ycse
    except Exception as e:
        return False
        print('error retTest requests -----------> ', e)


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
            if pythonFull < 3.9:
                print("*** checking python version ***", pythonFull)
        except Exception as e:
            print("**** missing dependencies ***", e)
            dependencies = False

        if dependencies is False:
            os.chmod(os.path.join(plugin_path, 'dependencies.sh', 0o0755))
            cmd1 = ". /usr/lib/enigma2/python/Plugins/Extensions/XCplugin/dependencies.sh"
            self.session.openWithCallback(self.start, xcConsole, title="Checking Dependencies", cmdlist=[cmd1], closeOnSuccess=True)
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
        self.session.open(MovieSelection)

    def OpenList(self):
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
        self['text'].setList(list)
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
            self.list.append(getConfigListEntry(indent + (_("Server URL")), cfg.hostaddress, (_("Enter Server Url without 'http://' your_domine"))))
            self.list.append(getConfigListEntry(indent + (_("Server PORT")), cfg.port, (_("Enter Server Port Eg.:'8080'"))))
            self.list.append(getConfigListEntry(indent + (_("Server Username")), cfg.user, (_("Enter Username"))))
            self.list.append(getConfigListEntry(indent + (_("Server Password")), cfg.passw, (_("Enter Password"))))
        self.list.append(getConfigListEntry(_("Server Timeout"), cfg.timeout, (_("Timeout Server (sec)"))))
        self.list.append(getConfigListEntry(_("Folder user file .xml"), cfg.pthxmlfile, (_("Configure folder containing .xml files\nPress 'OK' to change location."))))
        self.list.append(getConfigListEntry(_("Media Folder "), cfg.pthmovie, (_("Configure folder containing movie/media files\nPress 'OK' to change location."))))

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

        self.list.append(getConfigListEntry(_("Stop Player on Exit"), cfg.stoplayer, (_("If player active STOP player riproduction on exit"))))

        self.list.append(getConfigListEntry(_("Name Bouquet Configuration:"), cfg.infoexp, (_("Set Name for MakerBouquet"))))
        if cfg.infoexp.getValue():
            self.list.append(getConfigListEntry(indent + (_("Name Bouquet Export")), cfg.infoname, (_("Configure name of exported bouquet. Default is myBouquet"))))

        self.list.append(getConfigListEntry(_("Place IPTV bouquets at "), cfg.bouquettop, (_("Configure to place the bouquets of the converted lists"))))

        self.list.append(getConfigListEntry(_("Automatic bouquet update (schedule):"), cfg.autobouquetupdate, (_("Active Automatic Bouquet Update"))))
        if cfg.autobouquetupdate.value is True:
            self.list.append(getConfigListEntry(indent + (_("Schedule type:")), cfg.timetype, (_("At an interval of hours or at a fixed time"))))
            if cfg.timetype.value == "interval":
                self.list.append(getConfigListEntry(2 * indent + (_("Update interval (hours):")), cfg.updateinterval, (_("Configure every interval of hours from now"))))
            if cfg.timetype.value == "fixed time":
                self.list.append(getConfigListEntry(2 * indent + (_("Time to start update:")), cfg.fixedtime, (_("Configure at a fixed time"))))
        self.list.append(getConfigListEntry(_("Picons IPTV "), cfg.picons, (_("Download Picons ?"))))
        if cfg.picons.value:
            self.list.append(getConfigListEntry(indent + (_("Picons IPTV bouquets to ")), cfg.pthpicon, (_("Configure folder containing picons files\nPress 'OK' to change location."))))
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
        try:
            callback_map = {
                "pthmovie": self.openDirectoryBrowserCB(cfg.pthmovie),
                "pthxmlfile": self.openDirectoryBrowserCB(cfg.pthxmlfile),
                "pthpicon": self.openDirectoryBrowserCB(cfg.pthpicon)
            }

            if itemcfg in callback_map:
                self.session.openWithCallback(
                    callback_map[itemcfg],
                    LocationBox,
                    windowTitle=_("Choose Directory:"),
                    text=_("Choose directory"),
                    currDir=str(path),
                    bookmarks=config.movielist.videodirs,
                    autoAdd=True,
                    editDir=True,
                    inhibitDirs=["/bin", "/boot", "/dev", "/home", "/lib", "/proc", "/run", "/sbin", "/sys", "/usr", "/var"]
                )
        except Exception as e:
            print(e)

    def openDirectoryBrowserCB(self, config_entry):
        def callback(path):
            if path is not None:
                config_entry.setValue(path)
        return callback

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
            cfg.hostaddress.save()
            cfg.port.save()
            cfg.user.save()
            cfg.passw.save()
            configfile.save()
            self.xml_plugin()
            self.session.open(MessageBox, _("Settings saved successfully !"), MessageBox.TYPE_INFO, timeout=5)
        self.close()

    def xml_plugin(self):
        try:
            if str(cfg.hostaddress.value) != 'exampleserver.com':
                usernames = 'None'
                if file_exists(Path_XML + '/xclink.txt'):
                    with codecs.open(Path_XML + '/xclink.txt', "r+", encoding="utf-8") as f:
                        lines = f.readlines()
                        f.seek(0)
                        for line in lines:
                            if line.startswith('#'):
                                continue
                            if line.startswith('http'):
                                pattern = r"http://([^:/]+)(?::(\d+))?/get.php\?username=([^&]+)&password=([^&]+)&type=([^&]+)"  # &output=([^&]+)"
                                match = re.match(pattern, line)
                                if match:
                                    usernames = match.group(3)

                        if str(usernames) in str(cfg.user.value) and str(usernames) != 'None':
                            print('Line Exist in playlist lines')
                        else:
                            linecode = 'http://' + str(cfg.hostaddress.value) + ':' + str(cfg.port.value) + '/get.php?username=' + str(cfg.user.value) + '&password=' + str(cfg.passw.value) + '&type=m3u_plus'
                            f.write('\n' + str(linecode) + '\n')
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
        globalsxp.STREAMS.read_config()
        globalsxp.STREAMS.get_list(globalsxp.STREAMS.xtream_e2portal_url)


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
                    # Category name
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

                    elif ("/movie/" or "/series/") in globalsxp.stream_url:
                        globalsxp.stream_live = False
                        vodItems = {}
                        name = html_conv.html_unescape(name)
                        vodTitle = ''
                        vodDescription = ''
                        vodDuration = ''
                        vodGenre = ''
                        vodLines = description.splitlines()
                        for line in vodLines:
                            vodItems[(line.partition(": ")[0])] = (line.partition(": ")[-1])
                        if "NAME" in vodItems:
                            vodTitle = Utils.checkStr((vodItems["NAME"])).strip()
                        elif "O_NAME" in vodItems:
                            vodTitle = Utils.checkStr((vodItems["O_NAME"])).strip()
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
        self.session = session
        skin = os.path.join(skin_path, 'xc_Main.xml')
        if cfg.screenxl.value:
            skin = os.path.join(skin_path, 'xc_Mainxl.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setup_title = ('XCplugin Forever')
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
            "help": self.helpx,
            "power": self.power}, -1)
        self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onFirstExecBegin.append(self.checkinf)
        # self.onLayoutFinish.append(self.show_all)
        self.onShown.append(self.show_all)

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

            # test for return from player!!
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

    def go(self):
        self.mlist.setList(list(map(channelEntryIPTVplaylist, self.channel_list)))
        self.mlist.onSelectionChanged.append(self.update_description)
        self["feedlist"] = self.mlist
        self["feedlist"].moveToIndex(0)

    def update_list(self):
        globalsxp.STREAMS = iptv_streamse()
        globalsxp.STREAMS.read_config()
        if "exampleserver.com" not in globalsxp.STREAMS.xtream_e2portal_url:
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
            self['poster'].instance.setPixmapFromFile(globalsxp.piclogo)
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
                self["poster"].instance.setPixmapFromFile(globalsxp.piclogo)
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
                self["feedlist"] = self.mlist
                self["feedlist"].moveToIndex(0)
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
                self["feedlist"] = self.mlist
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
            self["feedlist"] = self.mlist

    def mmark(self):
        copy_poster()
        self.temp_index = 0
        if globalsxp.STREAMS.video_status is True:
            globalsxp.STREAMS.video_status = False
        self.load_from_tmp()
        globalsxp.STREAMS.list_index = self.index2
        print('=========== self show_all')
        self.show_all()

        self.decodeImage(globalsxp.piclogo)
        globalsxp.ui = False
        globalsxp.infoname = self.temp_playname
        self["playlist"].setText(globalsxp.infoname)

    def exitY(self):
        keywords = ['get_series', 'get_vod', 'get_live']
        
        if file_exists(output_file) and globalsxp.STREAMS.video_status is True:
            shutil.copy(output_file, input_file)
            remove(output_file)        
        
        if file_exists(input_file):
            with codecs.open(input_file, "r", encoding="utf-8") as f:
                content = f.read()
                if any(keyword in content for keyword in keywords):
                    print('=========== self show_all now')
                    self.mmark()
                    # self.show_all()

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
        selected_channel = globalsxp.iptv_list_tmp[self.index]
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
        globalsxp.ui = True
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
            from .downloader2 import imagedownloadScreen
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
        # debug(myparam, "check_standby")
        if myparam:
            self.power()

    def power(self):
        self.session.nav.stopService()
        self.session.open(Standby)

    '''
    def back_to_video(self):
        try:
            self.load_from_tmp()
            self.channel_list = globalsxp.STREAMS.iptv_list
            self.session.open(xc_Player)
        except Exception as e:
            print(e)
    '''


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
        self["actions"] = HelpableActionMap(self, "XCpluginActions", {
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
                                                  "help": self.helpx,
                                                  "power": self.power_off}, -1)
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
            self['poster'].instance.setPixmapFromFile(globalsxp.piclogo)
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
                self["poster"].instance.setPixmapFromFile(globalsxp.piclogo)
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

    def helpx(self):
        self.session.open(xc_help)

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
                    # filename = Utils.cleantitle(self.titlex)
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


class xc_StreamTasks(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        skin = os.path.join(skin_path, 'xc_StreamTasks.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setup_title = ('XCplugin Forever')
        try:
            self.init_aspect = int(getAspect())
        except:
            self.init_aspect = 0
        self.new_aspect = self.init_aspect
        self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
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
        if file_exists(globalsxp.Path_Movies):
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
        global file1
        free = _('Free Space')
        folder = _('Movie Folder')
        self.totalItem = '0'
        file1 = False
        filelist = ''
        self.pth = ''
        freeSize = "-?-"
        if isdir(cfg.pthmovie.value):
            filelist = listdir(cfg.pthmovie.value)
            if filelist is not None:
                file1 = True
                filelist.sort()
                count = 0
                for filename in filelist:
                    if file_exists(globalsxp.Path_Movies + filename):
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
        current = self["movielist"].getCurrent()
        path = globalsxp.Path_Movies
        if current:
            if current[0] == "movie":
                if file1 is True:
                    path = globalsxp.Path_Movies
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

    def message1(self, answer=None):
        current = self["movielist"].getCurrent()
        if current is None:
            self.session.open(MessageBox, _("No movie selected!"), MessageBox.TYPE_INFO, timeout=5)
            return
        self.sel = globalsxp.Path_Movies + current[1]
        self.sel2 = self.pth + current[1]
        if answer is None:
            self.session.openWithCallback(self.message1, MessageBox, _("Do you want to remove %s ?") % self.sel)
        elif answer:
            if file_exists(self.sel):
                # print("File exists:", self.sel)
                if self.Timer:
                    self.Timer.stop()
                self.removeFiles(self.sel)
                self.session.open(MessageBox, _("Movie has been successfully deleted"), MessageBox.TYPE_INFO, timeout=5)
                self.rebuildMovieList()
            elif file_exists(self.sel2):
                # print("File exists:", self.sel2)
                if self.Timer:
                    self.Timer.stop()
                self.removeFiles(self.sel2)
                self.session.open(MessageBox, _("Movie has been successfully deleted"), MessageBox.TYPE_INFO, timeout=5)
                self.rebuildMovieList()
            else:
                # print("File not found:", self.sel, "or", self.sel2)  # Stampa di debug
                self.session.open(MessageBox, _("The movie does not exist!"), MessageBox.TYPE_INFO, timeout=5)
                self.onShown.append(self.rebuildMovieList)
        else:
            return

    def removeFiles(self, targetfile):
        if file_exists(targetfile):
            try:
                remove(targetfile)
                self.session.open(MessageBox, targetfile + _(" Movie has been successfully deleted\nwait time to refresh the list..."), MessageBox.TYPE_INFO, timeout=5)
                self.onShown.append(self.rebuildMovieList)
            except OSError as e:
                print("Error removing file:", e)
                self.session.open(MessageBox, _("Error deleting the file: ") + str(e), MessageBox.TYPE_INFO, timeout=5)
        else:
            self.session.open(MessageBox, _("File not found!"), MessageBox.TYPE_INFO, timeout=5)


class xc_help(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        skin = os.path.join(skin_path, 'xc_help.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setup_title = ('XCplugin Forever')
        self.Update = False
        self["version"] = Label(version)
        self["key_red"] = Label(_("Back"))
        self["key_green"] = Label(_("Config"))
        self["key_yellow"] = Label(_("Main"))
        self["key_blue"] = Label(_("Player"))
        self["helpdesc"] = Label()
        self["helpdesc2"] = Label()
        self["paypal"] = Label()
        self['actions'] = ActionMap(['OkCancelActions',
                                     'DirectionActions',
                                     'HotkeyActions',
                                     'InfobarEPGActions',
                                     'ColorActions',
                                     'ChannelSelectBaseActions'], {'ok': self.exitx,
                                                                   'back': self.exitx,
                                                                   'cancel': self.exitx,
                                                                   'yellow': self.yellow,
                                                                   'green': self.green,
                                                                   'blue': self.blue,
                                                                   'yellow_long': self.update_dev,
                                                                   'info_long': self.update_dev,
                                                                   'infolong': self.update_dev,
                                                                   'showEventInfoPlugin': self.update_dev,
                                                                   'red': self.exitx}, -1)
        self.timer = eTimer()
        if os.path.exists('/usr/bin/apt-get'):
            self.timer_conn = self.timer.timeout.connect(self.check_vers)
        else:
            self.timer.callback.append(self.check_vers)
        self.timer.start(500, 1)
        self.onLayoutFinish.append(self.finishLayout)

    def check_vers(self):
        remote_version = '0.0'
        remote_changelog = ''
        req = Request(Utils.b64decoder(installer_url), headers={'User-Agent': 'Mozilla/5.0'})
        page = urlopen(req).read()
        if six.PY3:
            data = page.decode("utf-8")
        else:
            data = page.encode("utf-8")
        if data:
            lines = data.split("\n")
            for line in lines:
                if line.startswith("version"):
                    remote_version = line.split("=")
                    remote_version = line.split("'")[1]
                if line.startswith("changelog"):
                    remote_changelog = line.split("=")
                    remote_changelog = line.split("'")[1]
                    break
        self.new_version = remote_version
        self.new_changelog = remote_changelog
        # if float(currversion) < float(remote_version):
        if currversion < remote_version:
            self.Update = True
            self['key_yellow'].show()
            self['key_green'].show()
            self.session.open(MessageBox, _('New version %s is available\n\nChangelog: %s\n\nPress info_long or yellow_long button to start force updating.') % (self.new_version, self.new_changelog), MessageBox.TYPE_INFO, timeout=5)

    def update_me(self):
        if self.Update is True:
            self.session.openWithCallback(self.install_update, MessageBox, _("New version %s is available.\n\nChangelog: %s \n\nDo you want to install it now?") % (self.new_version, self.new_changelog), MessageBox.TYPE_YESNO)
        else:
            self.session.open(MessageBox, _("Congrats! You already have the latest version..."),  MessageBox.TYPE_INFO, timeout=4)

    def update_dev(self):
        req = Request(Utils.b64decoder(developer_url), headers={'User-Agent': 'Mozilla/5.0'})
        page = urlopen(req).read()
        data = json.loads(page)
        remote_date = data['pushed_at']
        strp_remote_date = datetime.strptime(remote_date, '%Y-%m-%dT%H:%M:%SZ')
        remote_date = strp_remote_date.strftime('%Y-%m-%d')
        self.session.openWithCallback(self.install_update, MessageBox, _("Do you want to install update ( %s ) now?") % (remote_date), MessageBox.TYPE_YESNO)

    def install_update(self, answer=False):
        if answer:
            self.session.open(xcConsole, title='Upgrading...', cmdlist=('wget -q "--no-check-certificate" ' + Utils.b64decoder(installer_url) + ' -O - | /bin/sh'), finishedCallback=self.myCallback, closeOnSuccess=False, showStartStopText=True, skin=None)
        else:
            self.session.open(MessageBox, _("Update Aborted!"),  MessageBox.TYPE_INFO, timeout=3)

    def myCallback(self, result=None):
        print('result:', result)
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
        conthelp += "original code by Dave Sully, Doug Mackay\n\n"
        conthelp += "Modded by Lululla\n\n"
        conthelp += "Skin By: Mmark - Info e2skin.blogspot.it\n\n"
        conthelp += "*************************************\n\n"
        conthelp += "Please reports bug or info to forums:\n\n"
        conthelp += "Corvoboys - linuxsat-support\n\n"
        conthelp += "*************************************\n\n"
        conthelp += "Special thanks to:\n"
        conthelp += "MMark, Pcd, KiddaC\n\n"
        conthelp += "FOR UPDATE PLUGIN PRESS INFO_LONG\n"
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
        if cfg.infoexp.getValue():
            globalsxp.infoname = str(cfg.infoname.value)
        self["description"].setText(self.getabout())
        self["Text"].setText(globalsxp.infoname)

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
        conthelp += _("Current configuration for creating the bouquet\n%s Conversion %s\n\n") % (cfg.typem3utv.getValue(), cfg.typelist.getValue())
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
        self["playlist"].setText(globalsxp.infoname)

    def Start_iptv_player(self):
        globalsxp.STREAMS = iptv_streamse()
        globalsxp.STREAMS.read_config()
        if "exampleserver.com" not in globalsxp.STREAMS.xtream_e2portal_url:
            globalsxp.STREAMS.get_list(globalsxp.STREAMS.xtream_e2portal_url)
            self.session.openWithCallback(check_configuring, xc_Main)
        else:
            self.session.open(xc_Main)

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
                self.Start_iptv_player()
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

    def helpx(self):
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
            "help": self.helpx,
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
                # print('globalsxp.eserv ----++++++play channel nIPTVplayer 2+++++---')
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

    def helpx(self):
        self.session.open(xc_help)

    def show_more_info(self):
        selected_channel = globalsxp.iptv_list_tmp[self.index]
        if selected_channel:
            name = str(self.titlex)
            show_more_infos(name, self.index)

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
                self["poster"].instance.setPixmapFromFile(globalsxp.piclogo)
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
        self["Text"] = Label()
        self["Text"].setText("M3u Utility")
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
        # if self.Movies:
        name = self.Movies[idx]
        if idx < 0 or idx is None:
            return
        else:
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
        if idx < 0 or idx is None:
            return
        dom = self.Movies[idx]
        # print("Attempting to remove file:", dom)
        if answer is None:
            self.session.openWithCallback(self.message1, MessageBox, _("Do you want to remove: %s ?") % dom)
        elif answer:
            try:
                remove(dom)
                # print("% s removed successfully" % dom)
                self.session.open(MessageBox, dom + _("   has been successfully deleted\nwait time to refresh the list..."), MessageBox.TYPE_INFO, timeout=5)
                del self.names[idx]  # Verifica se self.Movies invece di self.names
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
        dom = self.names[idx]
        name = self.Movies[idx]
        if idx < 0 or idx is None:
            return
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
        if idx < 0 or idx is None:
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
        self.session = session
        skin = os.path.join(skin_path, 'xc_M3uPlay.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setup_title = ('XCplugin Forever')
        self.list = []
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
        self.names[:] = [0, 0]
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
        if idx < 0 or idx is None:
            return
        else:
            name = self.names[idx]
            url = self.urls[idx]
            self.session.open(M3uPlay2, name, url)
            return

    def runRec(self, answer=None):
        self.downloading = False
        idx = self["list"].getSelectionIndex()
        if idx < 0 or idx is None:
            return
        else:
            self.name_m3u = self.names[idx]
            self.urlm3u = self.urls[idx]
            pth = urlparse(self.urlm3u).path
            ext = splitext(pth)[1]
            if ext not in EXTDOWN:
                ext = '.avi'
            # self.urlm3u = Utils.decodeUrl(self.urlm3u)
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
                        # print("Direct download mode")
                        self.downloadz()
                    else:
                        try:
                            self.downloading = True
                            # print("Starting download with progress for:", self.urlm3u)
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
            from .downloader2 import imagedownloadScreen
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
            '''
        # if self.downloading:
            # self.session.openWithCallback(self.abort, MessageBox, _('Are you sure to stop download.'), MessageBox.TYPE_YESNO)
            '''
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
        self['actions'] = ActionMap(['MoviePlayerActions', 'MovieSelectionActions', 'MediaPlayerActions',
                                     'EPGSelectActions', 'MediaPlayerSeekActions', 'SetupActions', 'ColorActions',
                                     'InfobarShowHideActions', 'InfobarActions', 'DirectionActions', 'InfobarSeekActions'], {
                                    'leavePlayer': self.cancel,
                                    'epg': self.showIMDB,
                                    'info': self.cicleStreamType,
                                    'tv': self.cicleStreamType,
                                    'stop': self.leavePlayer,
                                    'cancel': self.cancel,
                                    'back': self.cancel}, -1)

        self.onFirstExecBegin.append(self.cicleStreamType)
        self.onClose.append(self.cancel)

    def showIMDB(self):
        text_clear = self.name
        if returnIMDB(text_clear):
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


def xcm3ulistEntry(name):
    png0 = os.path.join(plugin_path, 'skin/pic/xcselh.png')
    pngl = os.path.join(plugin_path, 'skin/pic/xcon.png')
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
    if six.PY3:
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
        if six.PY3:
            data = str(data)
        try:
            if data.find("%") != -1:
                tmpvalue = re.findall(r'(\d+?%)', data)[-1].rstrip("%")
                self.progress = int(float(tmpvalue))

                if self.firstrun:
                    self.firstrun = False
                    if globalsxp.ui:
                        self.toolbox.updatescreen()

                elif self.progress == 100:
                    self.lastprogress = int(self.progress)
                    if globalsxp.ui:
                        self.toolbox.updatescreen()

                elif int(self.progress) != int(self.lastprogress):
                    self.lastprogress = int(self.progress)

                    elapsed_time = time.time() - self.starttime
                    if globalsxp.ui and elapsed_time > 2:
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


if screenwidth.width() == 2560:
    CHANNEL_NUMBER = [3, 4, 120, 60, 0]
    CHANNEL_NAME = [130, 4, 1800, 60, 1]
    FONT_0 = ("Regular", 52)
    FONT_1 = ("Regular", 52)
    BLOCK_H = 80
    skin_path = os.path.join(plugin_path, 'skin/uhd')
    globalsxp.piclogo = os.path.join(plugin_path, 'skin/uhd/iptvlogo.jpg')

elif screenwidth.width() == 1920:
    CHANNEL_NUMBER = [3, 0, 100, 50, 0]
    CHANNEL_NAME = [110, 0, 1200, 50, 1]
    FONT_0 = ("Regular", 32)
    FONT_1 = ("Regular", 32)
    BLOCK_H = 50
    skin_path = os.path.join(plugin_path, 'skin/fhd')
    globalsxp.piclogo = os.path.join(plugin_path, 'skin/fhd/iptvlogo.jpg')

else:
    CHANNEL_NUMBER = [3, 0, 50, 40, 0]
    CHANNEL_NAME = [75, 0, 900, 40, 1]
    FONT_0 = ("Regular", 24)
    FONT_1 = ("Regular", 24)
    BLOCK_H = 40
    skin_path = os.path.join(plugin_path, 'skin/hd')
    globalsxp.piclogo = os.path.join(plugin_path, 'skin/hd/iptvlogo.jpg')


if isDreamOS:
    skin_path = os.path.join(skin_path, 'dreamOs')


def channelEntryIPTVplaylist(entry):
    menu_entry = [
        entry,
        (eListboxPythonMultiContent.TYPE_TEXT, CHANNEL_NUMBER[0], CHANNEL_NUMBER[1], CHANNEL_NUMBER[2], CHANNEL_NUMBER[3], CHANNEL_NUMBER[4], RT_HALIGN_CENTER | RT_VALIGN_CENTER, "%s" % entry[0]),
        (eListboxPythonMultiContent.TYPE_TEXT, CHANNEL_NAME[0], CHANNEL_NAME[1], CHANNEL_NAME[2], CHANNEL_NAME[3], CHANNEL_NAME[4], RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[1])]
    return menu_entry


def uninstaller():
    """Routine di pulizia per rimuovere eventuali modifiche precedenti"""
    try:
        for fname in listdir(enigma_path):
            file_path = os.path.join(enigma_path, fname)
            if 'userbouquet.xc_' in fname or 'bouquets.tv.bak' in fname:
                remove(file_path)
        if isdir(epgimport_path):
            for fname in listdir(epgimport_path):
                if 'xc_' in fname:
                    remove(os.path.join(epgimport_path, fname))
        os.rename(os.path.join(enigma_path, 'bouquets.tv'), os.path.join(enigma_path, 'bouquets.tv.bak'))
        with open(os.path.join(enigma_path, 'bouquets.tv'), 'w+') as tvfile, \
             open(os.path.join(enigma_path, 'bouquets.tv.bak'), 'r+') as bakfile:
            for line in bakfile:
                if '.xc_' not in line:
                    tvfile.write(line)
    except Exception as e:
        print("Errore durante il processo di disinstallazione: ", e)
        raise


def returnIMDB(text_clear):
    TMDB = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('TMDB'))
    tmdb = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('tmdb'))
    IMDb = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('IMDb'))
    text = html_conv.html_unescape(text_clear)
    if os.path.exists(TMDB):
        try:
            from Plugins.Extensions.TMBD.plugin import TMBD
            _session.open(TMBD.tmdbScreen, text, 0)
        except Exception as e:
            print("[XCF] Tmdb: ", str(e))
        return True

    elif os.path.exists(tmdb):
        try:
            from Plugins.Extensions.tmdb.plugin import tmdb
            _session.open(tmdb.tmdbScreen, text, 0)
        except Exception as e:
            print("[XCF] Tmdb: ", str(e))
        return True

    elif os.path.exists(IMDb):
        try:
            from Plugins.Extensions.IMDb.plugin import main as imdb
            imdb(_session, text)
        except Exception as e:
            print("[XCF] imdb: ", str(e))
        return True
    else:
        _session.open(MessageBox, text, MessageBox.TYPE_INFO)
        return True
    return False


def show_more_infos(name, index):
    text_clear = re.sub(r'\b\d{4}\b.*', '', name).strip()  # name
    if "exampleserver.com" not in globalsxp.STREAMS.xtream_e2portal_url:
        selected_channel = globalsxp.iptv_list_tmp[index]
        if selected_channel:
            if globalsxp.stream_live is True:
                text_clear = selected_channel[9]

        if returnIMDB(text_clear):
            print('show imdb/tmdb')
        else:
            text2 = selected_channel[2]
            text3 = selected_channel[8]
            text4 = selected_channel[9]
            text_clear += (str(text2)
                           + '\n\n' + str(text3)
                           + '\n\n' + str(text4))
            _session.open(xc_Epg, text_clear)
    else:
        message = (_("Please enter correct server parameters in Config\n no valid list "))
        Utils.web_info(message)


def save_old():
    fldbouquet = "/etc/enigma2/bouquets.tv"
    namebouquet = globalsxp.STREAMS.playlistname.lower()
    tag = "xc_"
    xc12 = globalsxp.urlinfo.replace("enigma2.php", "get.php") + '&type=dreambox&output=mpegts'
    xc13 = globalsxp.urlinfo.replace("enigma2.php", "get.php") + '&type=m3u_plus&output=ts'
    in_bouquets = False
    desk_tmp = xcname = ''
    try:
        if cfg.typem3utv.value == 'MPEGTS to TV':
            file_path = os.path.join(enigma_path, 'userbouquet.%s%s_.tv' % (tag, namebouquet))
            if file_exists(file_path):
                remove(file_path)
            try:
                localFile = os.path.join(enigma_path, 'userbouquet.%s%s_.tv' % (tag, namebouquet))
                r = Utils.getUrl(xc12)
                with open(localFile, 'w') as f:
                    f.write(r)
            except Exception as e:
                print('Error downloading or writing TV file: ', e)
            xcname = 'userbouquet.%s%s_.tv' % (tag, namebouquet)
        else:
            if file_exists(os.path.join(globalsxp.Path_Movies, namebouquet + ".m3u")):
                remove(os.path.join(globalsxp.Path_Movies, namebouquet + ".m3u"))
            try:
                localFile = os.path.join(globalsxp.Path_Movies, '%s.m3u' % namebouquet)
                r = Utils.getUrl(xc13)
                with open(localFile, 'w') as f:
                    f.write(r)
            except Exception as e:
                print('Error downloading or writing TV file: ', e)
            name = namebouquet.replace('.m3u', '')
            xcname = 'userbouquet.%s%s_.tv' % (tag, name)
            if file_exists('/etc/enigma2/%s' % xcname):
                remove('/etc/enigma2/%s' % xcname)
            try:
                with open('/etc/enigma2/%s' % xcname, 'w') as outfile:
                    outfile.write('#NAME %s\r\n' % name.capitalize())
                    desk_tmp = ""
                    with open(os.path.join(globalsxp.Path_Movies, '%s.m3u' % name)) as infile:
                        for line in infile:
                            if line.startswith('http://') or line.startswith('https://'):
                                outfile.write('#SERVICE 4097:0:1:0:0:0:0:0:0:0:%s\r\n' % line.strip().replace(':', '%3a'))
                                outfile.write('#DESCRIPTION %s\r\n' % desk_tmp)
                            elif line.startswith('#EXTINF'):
                                desk_tmp = '%s' % line.split(',')[-1].strip()
                            elif '<stream_url><![CDATA' in line:
                                outfile.write('#SERVICE 4097:0:1:0:0:0:0:0:0:0:%s\r\n' % line.split('[')[-1].split(']')[0].strip().replace(':', '%3a'))
                                outfile.write('#DESCRIPTION %s\r\n' % desk_tmp)
                            elif '<title>' in line:
                                if '<![CDATA[' in line:
                                    desk_tmp = '%s' % line.split('[')[-1].split(']')[0].strip()
                                else:
                                    desk_tmp = '%s' % line.split('<')[1].split('>')[1].strip()
            except Exception as e:
                print('Error creating bouquet: ', e)

        for line in open(fldbouquet):
            if xcname in line:
                in_bouquets = True
        if in_bouquets is False:
            try:
                with open("/etc/enigma2/new_bouquets.tv", "w") as new_bouquet:
                    with open(fldbouquet, "r") as f:
                        file_read = f.readlines()

                    if cfg.bouquettop.value == "Top":
                        new_bouquet.write('#NAME User - bouquets (TV)\n')
                        new_bouquet.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "{}" ORDER BY bouquet\r\n'.format(xcname))
                        new_bouquet.writelines(line for line in file_read if not line.startswith("#NAME"))
                    else:
                        new_bouquet.writelines(file_read)
                        new_bouquet.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "{}" ORDER BY bouquet\r\n'.format(xcname))
            except IOError as e:
                print("An error occurred while accessing the file: {}".format(e))
            system('cp -rf /etc/enigma2/bouquets.tv /etc/enigma2/backup_bouquets.tv')
            system('mv -f /etc/enigma2/new_bouquets.tv /etc/enigma2/bouquets.tv')
    except Exception as e:
        print(e)


def make_bouquet():
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
    m3u_url = globalsxp.urlinfo.replace("enigma2.php", "get.php")
    epg_url = globalsxp.urlinfo.replace("enigma2.php", "xmltv.php")
    if cfg.infoexp.getValue():
        globalsxp.infoname = str(cfg.infoname.value)

    with open(configfilexml, 'w') as f:
        configtext = '<config>\r\n'
        configtext += '\t<supplier>\r\n'
        configtext += '\t\t<name>' + globalsxp.infoname + '</name>\r\n'
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
    dom = str(globalsxp.STREAMS.playlistname)
    com = ("python %s") % e2m3u2bouquet
    _session.open(xcConsole, _("Conversion %s in progress: ") % dom, ["%s" % com], closeOnSuccess=True)


def menu(menuid, **kwargs):
    if menuid == "mainmenu":
        return [("XCplugin", main, "XCplugin", 4)]
    else:
        return []


def main(session, **kwargs):
    globalsxp.STREAMS = iptv_streamse()
    globalsxp.STREAMS.read_config()
    if "exampleserver.com" not in globalsxp.STREAMS.xtream_e2portal_url:
        globalsxp.STREAMS.get_list(globalsxp.STREAMS.xtream_e2portal_url)
        session.openWithCallback(check_configuring, xc_home)
    else:
        session.open(xc_home)


class AutoStartTimer:
    def __init__(self, session):
        print("*** running AutoStartTimer XC-Forever ***")
        self.session = session
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
        globalsxp.STREAMS.read_config()
        globalsxp.STREAMS.get_list(globalsxp.STREAMS.xtream_e2portal_url)
        if str(cfg.typelist.value) == "Combined Live/VOD":
            save_old()
        else:
            make_bouquet()


def check_configuring():
    if cfg.autobouquetupdate.value is True:
        """Check for new config values for auto start
        """
        if globalsxp.autoStartTimer is not None:
            globalsxp.autoStartTimer.update()
        return


def autostart(reason, session=None, **kwargs):
    global _session
    if reason == 0 and _session is None:
        if session is not None:
            _session = session
            if globalsxp.autoStartTimer is None:
                globalsxp.autoStartTimer = AutoStartTimer(session)
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


# def debug(obj, text=""):
    # print("%s" % text + " %s\n" % obj)


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
