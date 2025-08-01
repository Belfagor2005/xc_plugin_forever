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
from os import listdir, remove, statvfs
from os.path import exists as file_exists, isdir, join
from re import findall
from six import PY3
from time import time
import codecs

# Enigma2 imports
from enigma import eTimer, eServiceReference

# Local imports
from . import _
from .addons import Utils
from .addons.modul import (
    # getAspect,
    globalsxp,
    # setAspect,
    EXTENSIONS,
)

# Components imports
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Sources.List import List
from Components.Task import (
    job_manager as JobManager,
    Condition,
    Job,
    Task,
)

# Screens imports
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen

from .addons.NewOeSk import ctrlSkin
from .xcConfig import cfg
from .xcSkin import skin_path


try:
    from Components.AVSwitch import AVSwitch
except ImportError:
    from Components.AVSwitch import eAVControl as AVSwitch


class AspectManager:
    def __init__(self):
        self.init_aspect = self.get_current_aspect()
        print("[INFO] Initial aspect ratio:", self.init_aspect)

    def get_current_aspect(self):
        """Restituisce l'aspect ratio attuale del dispositivo."""
        try:
            return int(AVSwitch().getAspectRatioSetting())
        except Exception as e:
            print("[ERROR] Failed to get aspect ratio:", str(e))
            return 0  # Valore di default in caso di errore

    def restore_aspect(self):
        """Ripristina l'aspect ratio originale all'uscita del plugin."""
        try:
            print("[INFO] Restoring aspect ratio to:", self.init_aspect)
            AVSwitch().setAspectRatio(self.init_aspect)
        except Exception as e:
            print("[ERROR] Failed to restore aspect ratio:", str(e))


aspect_manager = AspectManager()


class xc_StreamTasks(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        skin = join(skin_path, 'xc_StreamTasks.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            skin = f.read()

        self.skin = ctrlSkin('xc_StreamTasks', skin)
        try:
            Screen.setTitle(self, _('%s') % 'STREAMTASK MENU')
        except BaseException:
            try:
                self.setTitle(_('%s') % 'STREAMTASK MENU')
            except BaseException:
                pass

        self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()

        self["filelist"] = List([])
        self.movielist = []

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
            "cancel": self.keyClose},
            -1)

        self.Timer = eTimer()
        try:
            self.Timer_conn = self.Timer.timeout.connect(self.TimerFire)
        except BaseException:
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

    def updatescreen(self):
        print("Updating screen...")

    def download_finished(self):
        print("download_finished ...")

    def rebuildMovieList(self):
        if globalsxp.Path_Movies and file_exists(globalsxp.Path_Movies):
            self.movielist = []
            self.getTaskList()  # Get the list of pending tasks
            self.getMovieList()  # Get movie list from filesystem
            self["filelist"].setList(self.movielist)
            self["filelist"].updateList(self.movielist)
        else:
            message = "The Movie path is not configured correctly or does not exist!!!"
            Utils.web_info(message)
            self.close()

    def getTaskList(self):
        for job in JobManager.getPendingJobs():
            # Only add jobs that are not finished yet
            if job.status != job.FINISHED:
                self.movielist.append((
                    job,
                    job.name,
                    job.getStatustext(),
                    int(100 * job.progress // float(job.end)),
                    str(100 * job.progress // float(job.end)) + "%"))
            else:
                # Manage finished jobs separately
                self.movielist.append((
                    job,
                    job.name,
                    _("Finished"),
                    100,
                    "100%"))

        # Set timer to update list
        if len(self.movielist) >= 0:
            self.Timer.startLongTimer(10)

    def getMovieList(self):
        global file1
        free = _('Free Space')
        folder = _('Movie Folder')
        self.totalItem = '0'
        file1 = False
        self.movielist = []
        filelist = ''
        self.pth = ''
        freeSize = "-?-"
        if isdir(cfg.pthmovie.value):
            filelist = listdir(cfg.pthmovie.value)
            if filelist:
                file1 = True
                filelist.sort()
                count = 0
                for filename in filelist:
                    full_path = globalsxp.Path_Movies + filename
                    if file_exists(full_path):
                        extension = filename.split('.')[-1].lower()
                        # Check if it is a video file
                        if extension in EXTENSIONS and EXTENSIONS[extension] == "movie":
                            count += 1
                            self.totalItem = str(count)
                            movieFolder = statvfs(cfg.pthmovie.value)
                            try:
                                stat = movieFolder
                                freeSize = Utils.convert_size(
                                    float(stat.f_bfree * stat.f_bsize))
                            except Exception as e:
                                print(e)
                            titel2 = '%s: %s %s' % (
                                folder, str(freeSize), free)
                            self['label2'].setText(titel2)
                            self['totalItem'].setText(
                                'Item %s' % str(self.totalItem))

                            # Check if the job with the same file name already
                            # exists
                            for job in JobManager.getPendingJobs():
                                if isinstance(
                                        job,
                                        Job) and hasattr(
                                        job,
                                        'filename'):
                                    # Compares file name only (without
                                    # extension)
                                    if filename.lower().split(
                                            '.')[0] == job.filename.lower().split('.')[0]:
                                        continue

                            self.movielist.append(
                                ("movie", filename, ("Finished"), 100, "100%"))
            else:
                titel2 = '(%s offline)' % folder
                self['label2'].setText(titel2)
                self['totalItem'].setText('Item %s' % str(self.totalItem))

    def keyOK(self):
        global file1
        current = self["filelist"].getCurrent()

        # Defensive checks
        if current is None or not isinstance(
                current, tuple) or len(current) < 2:
            return

        job = current[0]
        filename = current[1]

        if job == "movie" and len(current) > 2 and current[2] == "Finished":
            path = globalsxp.Path_Movies
            url = path + filename
            name = filename
            file1 = False
            if file_exists(url):
                fileExtension = filename.split(".")[-1].lower()
                print("fileExtension=", fileExtension)
                if fileExtension in [
                    "mpg", "mpeg", "mkv", "m2ts", "vob", "mod",
                    "avi", "mp4", "divx", "mov", "flv", "3gp", "wmv"
                ]:
                    from Screens.InfoBar import MoviePlayer
                    fileRef = eServiceReference(
                        "4097:0:0:0:0:0:0:0:0:0:" + url)
                    fileRef.setName(name)
                    self.session.open(MoviePlayer, fileRef)
            else:
                self.session.open(
                    MessageBox,
                    _("Is Directory or file not exist"),
                    MessageBox.TYPE_INFO,
                    timeout=5
                )
        elif isinstance(job, str):
            # Placeholder for Job handling
            self.session.open(
                MessageBox,
                _("Invalid or unsupported job type"),
                MessageBox.TYPE_INFO,
                timeout=5)

    def keyBlue(self):
        pass

    def JobViewCB(self, why):
        pass

    def keyClose(self):
        if cfg.stoplayer.value is True:
            globalsxp.STREAMS.play_vod = False
            self.session.nav.stopService()
            self.session.nav.playService(self.initialservice)

        aspect_manager.restore_aspect()
        self.close()

    def message1(self, answer=None):
        current = self["filelist"].getCurrent()
        if current is None or not isinstance(
                current, tuple) or len(current) < 2:
            self.session.open(
                MessageBox,
                _("No movie selected!"),
                MessageBox.TYPE_INFO,
                timeout=5)
            return

        filename = current[1]
        if not any(entry[1] == filename for entry in self.movielist):
            self.session.open(
                MessageBox,
                _("No movie selected!"),
                MessageBox.TYPE_INFO,
                timeout=5)
            return

        self.sel = globalsxp.Path_Movies + filename
        self.sel2 = self.pth + filename
        if answer is None:
            self.session.openWithCallback(
                self.message1,
                MessageBox,
                _("Do you want to remove %s ?") %
                self.sel)
        elif answer:
            if file_exists(self.sel):
                if self.Timer:
                    self.Timer.stop()
                self.removeFiles(self.sel)
                self.session.open(
                    MessageBox,
                    _("Movie has been successfully deleted"),
                    MessageBox.TYPE_INFO,
                    timeout=5)
                self.rebuildMovieList()
            elif file_exists(self.sel2):
                if self.Timer:
                    self.Timer.stop()
                self.removeFiles(self.sel2)
                self.session.open(
                    MessageBox,
                    _("Movie has been successfully deleted"),
                    MessageBox.TYPE_INFO,
                    timeout=5)
                self.rebuildMovieList()
            else:
                self.session.open(
                    MessageBox,
                    _("The movie does not exist!"),
                    MessageBox.TYPE_INFO,
                    timeout=5)
                self.onShown.append(self.rebuildMovieList)
        else:
            return

    def removeFiles(self, targetfile):
        if file_exists(targetfile):
            try:
                remove(targetfile)
                self.session.open(
                    MessageBox,
                    targetfile +
                    _(" Movie has been successfully deleted\nwait time to refresh the list..."),
                    MessageBox.TYPE_INFO,
                    timeout=5)
                self.onShown.append(self.rebuildMovieList)
            except OSError as e:
                print("Error removing file:", e)
                self.session.open(
                    MessageBox,
                    _("Error deleting the file: ") +
                    str(e),
                    MessageBox.TYPE_INFO,
                    timeout=5)
        else:
            self.session.open(
                MessageBox,
                _("File not found!"),
                MessageBox.TYPE_INFO,
                timeout=5)


def shell_quote(s):
    return "'" + s.replace("'", "'\"'\"'") + "'"


class downloadJob(Job):
    def __init__(self, toolbox, cmdline, filename, filmtitle):
        Job.__init__(self, filmtitle)

        # Funzione di quoting per Enigma2
        def enigma_quote(s):
            if isinstance(s, bytes):
                s = s.decode('utf-8', 'ignore')
            s = s.replace("'", "'\"'\"'")
            return "'" + s + "'"

        # Converti lista in stringa quotata
        if isinstance(cmdline, list):
            quoted_cmd = []
            for arg in cmdline:
                if ' ' in arg or any(char in arg for char in '()[]{}!$&*?;'):
                    quoted_cmd.append(enigma_quote(arg))
                else:
                    quoted_cmd.append(arg)
            cmdline = " ".join(quoted_cmd)

        self.cmdline = cmdline
        print("cmdline=", self.cmdline)
        print("type cmdline=", type(self.cmdline))

        self.filename = filename
        self.toolbox = toolbox
        self.retrycount = 0
        downloadTask(self, self.cmdline, filename, filmtitle)

    def retry(self):
        assert self.status == self.FAILED
        self.restart()

    def cancel(self):
        self.abort()


class downloadTaskPostcondition(Condition):
    RECOVERABLE = True

    def check(self, task):
        return task.returncode == 0 and task.error is None

    def getErrorMessage(self, task):
        errors = {
            task.ERROR_CORRUPT_FILE: _("MOVIE DOWNLOAD FAILED!") +
            '\n\n' +
            _("DOWNLOADED FILE CORRUPTED:") +
            '\n%s' %
            task.lasterrormsg,
            task.ERROR_RTMP_ReadPacket: _("MOVIE DOWNLOAD FAILED!") +
            '\n\n' +
            _("COULD NOT READ RTMP PACKET:") +
            '\n%s' %
            task.lasterrormsg,
            task.ERROR_SEGFAULT: _("MOVIE DOWNLOAD FAILED!") +
            '\n\n' +
            _("SEGMENTATION FAULT:") +
            '\n%s' %
            task.lasterrormsg,
            task.ERROR_SERVER: _("MOVIE DOWNLOAD FAILED!") +
            '\n\n' +
            _("SERVER RETURNED ERROR:") +
            '\n%s' %
            task.lasterrormsg,
            task.ERROR_FILESYSTEM: _("MOVIE DOWNLOAD FAILED!") +
            '\n\n' +
            _("FILESYSTEM ERROR:") +
            '\n%s' %
            task.lasterrormsg,
            task.ERROR_UNKNOWN: _("MOVIE DOWNLOAD FAILED!") +
            '\n\n' +
            _("UNKNOWN ERROR:") +
            '\n%s' %
            task.lasterrormsg}
        return errors.get(task.error, _("Unknown error"))


class downloadTask(Task):
    if PY3:
        ERROR_CORRUPT_FILE, ERROR_RTMP_ReadPacket, ERROR_SEGFAULT, ERROR_SERVER, ERROR_UNKNOWN = list(
            range(5))
    else:
        ERROR_CORRUPT_FILE, ERROR_RTMP_ReadPacket, ERROR_SEGFAULT, ERROR_SERVER, ERROR_UNKNOWN = range(
            5)

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
        self.starttime = time()

    def processOutput(self, data):
        # Gestione compatibilità Python 2/3
        if not PY3:
            # In Python 2, data è già una stringa
            pass
        elif isinstance(data, bytes):
            # In Python 3, decodifichiamo i bytes in stringa
            data = data.decode("utf-8", "ignore")

        try:
            if data.find("%") != -1:
                tmpvalue = findall(r'(\d+?%)', data)[-1].rstrip("%")
                self.progress = int(float(tmpvalue))

                if self.firstrun:
                    self.firstrun = False
                    if hasattr(self.toolbox, 'updatescreen'):
                        self.toolbox.updatescreen()

                elif self.progress == 100:
                    self.lastprogress = int(self.progress)
                    if hasattr(self.toolbox, 'updatescreen'):
                        self.toolbox.updatescreen()

                elif int(self.progress) != int(self.lastprogress):
                    self.lastprogress = int(self.progress)
                    elapsed_time = time() - self.starttime
                    if elapsed_time > 2:
                        self.starttime = time()
                        if hasattr(self.toolbox, 'updatescreen'):
                            self.toolbox.updatescreen()
            else:
                # Passa i dati alla gestione originale
                if PY3:
                    # In Python 3, riconverti in bytes se necessario
                    Task.processOutput(self, data.encode("utf-8"))
                else:
                    Task.processOutput(self, data)
        except Exception as errormsg:
            print("Error processOutput: " + str(errormsg))
            Task.processOutput(self, data)

    def processOutputLine(self, line):
        pass

    def afterRun(self):
        if self.returncode != 0:
            # New error type for filesystem issues
            self.ERROR_FILESYSTEM = 5
            self.error = self.ERROR_FILESYSTEM
            self.lasterrormsg = _(
                "Filesystem error: Cannot write to destination")

        elif self.getProgress() == 100 or self.progress == 100:
            try:
                self.toolbox.download_finished(self.filename, self.filmtitle)
            except Exception as e:
                print(e)


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
