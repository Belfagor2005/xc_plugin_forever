#!/usr/bin/python
# Code by mfaraj57 and RAED (c) 2018

# python3
from __future__ import print_function
from . import _
from Components.ActionMap import ActionMap
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from enigma import eTimer, eConsoleAppContainer, getDesktop
from os import path as os_path
from Components.ProgressBar import ProgressBar
from Tools.Downloader import downloadWithProgress
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import os


try:
    from Components.HTMLComponent import *
except BaseException:
    print("KeyAdder: No HTMLComponent file found")

try:
    from Components.GUIComponent import *
except BaseException:
    print("KeyAdder: No GUIComponent file found")


# imagedownloadScreen screen
sz_w = getDesktop(0).size().width()

if sz_w == 1280:
    SKIN_imagedownloadScreen = """
<screen name="imagedownloadScreen" position="center,center" size="560,155" title="Downloading image...">
<widget name="activityslider" position="20,50" size="510,20" borderWidth="1" transparent="1" />
<widget name="package" position="20,5" size="510,45" font="Regular;18" halign="center" valign="center" transparent="1" />
<widget name="status" position="20,80" size="510,45" font="Regular;16" halign="center" valign="center" transparent="1" />
</screen>"""

else:
    SKIN_imagedownloadScreen = """
<screen name="imagedownloadScreen" position="center,center" size="805,232" title="Downloading image...">
<widget name="activityslider" position="30,75" size="755,30" borderWidth="1" transparent="1" />
<widget name="package" position="30,7" size="755,60" font="Regular;27" halign="center" valign="center" transparent="1" />
<widget name="status" position="30,120" size="755,60" font="Regular;24" halign="center" valign="center" transparent="1" />
</screen>"""

# progress screen
sz_w = getDesktop(0).size().width()

if sz_w == 1280:
    SKIN_Progress = """
<screen position="350,250"  size="550,155" title="Command execution..." >
<widget name="text" position="10,10"  size="550,130" font="Console;18" />
<widget name="slider" position="0,142" size="550,15" borderWidth="1" transparent="1" />
</screen>"""

else:
    SKIN_Progress = """
<screen position="500,430"  size="850,200" title="Command execution..." >
<widget name="text" position="20,20"  size="850,160" font="Console;24" />
<widget name="slider" position="0,185" size="850,20" borderWidth="1" transparent="1" />
</screen>"""


def log(label, data):
    data = str(data)
    open("/tmp/KeyAdder.log", "a").write("\n" + label + ":>" + data)


def getversioninfo():
    currversion = '1.0'
    version_file = resolveFilename(
        SCOPE_PLUGINS, "Extensions/KeyAdder/tools/version")
    if os.path.exists(version_file):
        try:
            fp = open(version_file, 'r').readlines()
            for line in fp:
                if 'version' in line:
                    currversion = line.split('=')[1].strip()
        except BaseException:
            pass
    return (currversion)


class imagedownloadScreen(Screen):
    def __init__(self, session, name='', target='', url=''):
        Screen.__init__(self, session)
        self.skin = SKIN_imagedownloadScreen
        self.target = target
        self.name = name
        self.url = url
        self["activityslider"] = ProgressBar()
        self["activityslider"].setRange((0, 100))
        self["activityslider"].setValue(0)
        self["status"] = Label(_("Downloading, please wait..."))
        self["package"] = Label(name)

        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions"],
            {
                "ok": self.dexit,
                "cancel": self.dexit
            },
            -1
        )
        self.downloading = False
        self.downloader = None
        self.setTitle(_('Connecting') + '...')
        self.timer = eTimer()
        try:
            self.timer.callback.append(self.startDownload)
        except AttributeError:
            self.timer_conn = self.timer.timeout.connect(self.startDownload)
        self.timer.start(5000, 1)

    def startDownload(self):
        try:
            self.timer.stop()
            del self.timer
        except Exception:
            pass
        self.downloading = True
        self['status'].setText(_('Connecting to server...'))

        # Use downloadWithProgress async downloader
        self.downloader = downloadWithProgress(self.url, self.target)
        self.downloader.addProgress(self.progress)
        d = self.downloader.start()
        d.addCallback(self.responseCompleted)
        d.addErrback(self.responseFailed)

    def progress(self, current, total):
        # Update progress bar and labels
        if total == 0:
            percent = 0
        else:
            percent = int(100 * current / float(total))

        self['activityslider'].setValue(percent)
        info = _('Downloading') + ' ' + '%d of %d kBytes (%.2f%%)' % (current //
                                                                      1024, total // 1024, 100 * current / float(total))
        self['package'].setText(self.name)
        self['status'].setText(info)
        self.setTitle(_('Downloading') + ' ' + str(percent) + '%...')

    def responseCompleted(self, data=None):
        # Called when download finished successfully
        print('[downloader] Download succeeded.')
        info = _('Download completed successfully.\nPress OK to exit.')
        self['status'].setText(info)
        self.setTitle(_('Download completed successfully.'))
        self.downloading = False
        self.success = True
        self.instance.show()

    def responseFailed(self, failure_instance=None, error_message=''):
        # Called when download fails
        print('[downloader] Download failed.')
        self.error_message = error_message
        if error_message == '' and failure_instance is not None:
            self.error_message = failure_instance.getErrorMessage()
        info = self.error_message
        self['status'].setText(info)
        self.setTitle(_('Download failed. Press OK to exit.'))
        self.downloading = False
        self.success = False

        self.instance.show()
        self.remove_target()

    def dexit(self):
        if self.downloading:
            self.session.openWithCallback(self.abort, MessageBox, _(
                'Are you sure to stop download?'), MessageBox.TYPE_YESNO)
        else:
            self.close(False)

    def remove_target(self):
        # Remove partially downloaded target file
        try:
            if os_path.exists(self.target):
                os.remove(self.target)
        except Exception:
            pass

    def abort(self, answer=True):
        if not answer:
            return
        if not self.downloading:
            try:
                if os_path.exists('/tmp/download_install.log'):
                    os.remove('/tmp/download_install.log')
            except Exception:
                pass
            self.close(False)
        elif self.downloader is not None:
            self.downloader.stop()
            self['status'].setText(_('Aborting...'))
            self.remove_target()
            try:
                self.close(False)
            except Exception:
                pass
        else:
            self.close(False)
