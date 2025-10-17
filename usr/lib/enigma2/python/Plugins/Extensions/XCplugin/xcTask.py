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
#  Latest Update: 17/10/2025           *
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
from os.path import exists as file_exists, isdir, join, getsize
from re import findall
from six import PY3
# from time import time
import codecs

# Enigma2 imports
from enigma import eTimer, eServiceReference

# Local imports
from . import _
from .addons import Utils
from .addons.modul import (
    globalsxp,
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
    """Manages aspect ratio settings for the plugin"""

    def __init__(self):
        self.save_current_aspect()
        print("[INFO] Initial aspect ratio saved:", self.init_aspect)

    def save_current_aspect(self):
        """Save current aspect ratio setting"""
        try:
            self.init_aspect = self.get_current_aspect()
            print("[INFO] Current aspect ratio saved:", self.init_aspect)
        except Exception as e:
            print("[ERROR] Failed to save aspect ratio:", str(e))
            self.init_aspect = 0

    def get_current_aspect(self):
        """Get current aspect ratio setting"""
        try:
            aspect = AVSwitch().getAspectRatioSetting()
            return int(aspect) if aspect is not None else 0
        except (ValueError, TypeError, Exception) as e:
            print("[ERROR] Failed to get aspect ratio:", str(e))
            return 0

    def restore_aspect(self):
        """Restore original aspect ratio"""
        try:
            if hasattr(self, 'init_aspect') and self.init_aspect is not None:
                print("[INFO] Restoring aspect ratio to:", self.init_aspect)
                AVSwitch().setAspectRatio(self.init_aspect)
            else:
                print("[WARNING] No initial aspect ratio to restore")
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
        self.pth = cfg.pthmovie.value if hasattr(
            cfg, 'pthmovie') and cfg.pthmovie.value else ""
        self.movielist = []
        self["filelist"] = List([])
        self["key_green"] = Label(_("Remove"))
        self["key_red"] = Label(_("Close"))
        self["key_yellow"] = Label(_("Pause/Resume"))
        self["key_blue"] = Label()
        self['totalItem'] = Label()
        self['label2'] = Label()
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions"], {
            "ok": self.keyOK,
            "esc": self.keyClose,
            "exit": self.keyClose,
            "green": self.message1,
            "yellow": self.toggle_pause_resume,
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

    def layoutFinished(self):
        self.Timer.startLongTimer(2)
        self.progress_timer = eTimer()
        try:
            self.progress_timer_conn = self.progress_timer.timeout.connect(
                self.updateProgress)
        except BaseException:
            self.progress_timer.callback.append(self.updateProgress)
        self.progress_timer.start(6500)

    def updateProgress(self):
        """Force progress update"""
        self.rebuildMovieList()

    def rebuildMovieList(self):
        if globalsxp.Path_Movies and file_exists(globalsxp.Path_Movies):
            self.movielist = []
            print("[DEBUG] Starting rebuildMovieList - cleared movielist")

            self.getTaskList()

            temp_movielist = []
            filelist = listdir(
                cfg.pthmovie.value) if isdir(
                cfg.pthmovie.value) else []

            if filelist:
                active_job_files = set()
                for job in JobManager.getPendingJobs() + JobManager.active_jobs:
                    if hasattr(job, 'filename') and job.filename:
                        import os
                        base_name = os.path.basename(job.filename)
                        active_job_files.add(base_name.lower())

                for filename in filelist:
                    if filename.lower() not in active_job_files:
                        full_path = globalsxp.Path_Movies + filename
                        if file_exists(full_path):
                            extension = filename.split('.')[-1].lower()
                            if extension in EXTENSIONS and EXTENSIONS[extension] == "movie":
                                temp_movielist.append(
                                    ("movie", filename, "Finished", 100, "100%"))
                                print(
                                    "[DEBUG] Added completed movie: {}".format(filename))

            self.movielist.extend(temp_movielist)

            print("[DEBUG] Final movielist: {} items".format(len(self.movielist)))
            for i, item in enumerate(self.movielist):
                item_type = "JOB" if isinstance(item[0], Job) else "MOVIE"
                print("  [{}] {}: {} - {}".format(i,
                      item_type, item[1], item[2]))

            self["filelist"].setList(self.movielist)
            self["filelist"].updateList(self.movielist)
        else:
            message = "The Movie path is not configured correctly or does not exist!!!"
            Utils.web_info(message)
            self.close()

    def toggle_pause_resume(self):
        """Toggle pause/resume for selected download task"""
        current = self["filelist"].getCurrent()
        if current is None or not isinstance(
                current, tuple) or len(current) < 2:
            self.session.open(
                MessageBox,
                _("No task selected!"),
                MessageBox.TYPE_INFO,
                timeout=5)
            return

        job = current[0]

        if not isinstance(job, Job):
            self.session.open(
                MessageBox,
                _("Cannot pause/resume this item"),
                MessageBox.TYPE_INFO,
                timeout=5)
            return

        try:
            NOT_STARTED = 0
            IN_PROGRESS = 1
            FINISHED = 2
            FAILED = 3

            job_name = getattr(job, 'name', 'Unknown')

            if job.status == NOT_STARTED:
                print("[TASK] Starting job: {}".format(job_name))
                job.start_manually()
                message = _("Download started: {}").format(job_name)

            elif job.status == IN_PROGRESS:
                print("[TASK] Stopping job: {}".format(job_name))
                job.abort()

                job.status = NOT_STARTED
                message = _("Download stopped: {}").format(job_name)

            elif job.status == FAILED:
                print("[TASK] Restarting failed job: {}".format(job_name))
                job.status = IN_PROGRESS
                job.start_manually()
                message = _("Download restarted: {}").format(job_name)

            else:  # FINISHED
                message = _("Cannot modify this task status")

            self.session.open(
                MessageBox,
                message,
                MessageBox.TYPE_INFO,
                timeout=3
            )

            self.rebuildMovieList()

        except Exception as e:
            print("[TASK] Error toggling pause/resume: {}".format(e))
            self.session.open(
                MessageBox,
                _("Error controlling download: {}").format(str(e)),
                MessageBox.TYPE_ERROR,
                timeout=5
            )

    def __onClose(self):
        try:
            if self.Timer and self.Timer.isActive():
                self.Timer.stop()
            if hasattr(
                    self,
                    'progress_timer') and self.progress_timer.isActive():
                self.progress_timer.stop()
            del self.Timer
            if hasattr(self, 'progress_timer'):
                del self.progress_timer
        except BaseException:
            pass

        import gc
        gc.collect()

    def TimerFire(self):
        self.Timer.stop()
        self.rebuildMovieList()

    def updatescreen(self):
        """Force update of the task list"""
        print("[UPDATE] Forcing screen update...")
        self.rebuildMovieList()

    def download_finished(self):
        print("download_finished ...")

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
            if filelist:
                file1 = True
                filelist.sort()
                count = 0

                active_job_files = set()
                for job in JobManager.getPendingJobs() + JobManager.active_jobs:
                    if isinstance(job, Job) and hasattr(job, 'filename'):
                        job_filename = getattr(job, 'filename', '')
                        if job_filename:
                            import os
                            base_name = os.path.basename(job_filename)
                            active_job_files.add(base_name.lower())

                print(
                    "[DEBUG] Active job files: {}".format(
                        len(active_job_files)))

                for filename in filelist:
                    full_path = globalsxp.Path_Movies + filename

                    if isdir(full_path):
                        try:
                            series_has_active_jobs = False
                            for job_file in active_job_files:
                                if filename.lower() in job_file.lower():
                                    series_has_active_jobs = True
                                    break

                            if not series_has_active_jobs:
                                self.movielist.append(
                                    ("series_folder", filename, "Series Folder", 100, "100%"))
                                print(
                                    "[DEBUG] Added series folder: {}".format(filename))
                        except Exception as e:
                            print(
                                "Error processing series folder {}: {}".format(
                                    filename, e))

                    elif file_exists(full_path):
                        extension = filename.split('.')[-1].lower()
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
                            titel2 = '{}: {} {}'.format(
                                folder, str(freeSize), free)
                            self['label2'].setText(titel2)
                            self['totalItem'].setText(
                                'Item {}'.format(str(self.totalItem)))

                            filename_lower = filename.lower()
                            has_active_job = filename_lower in active_job_files

                            if has_active_job:
                                print(
                                    "[DEBUG] Skipping movie {} - has active job".format(filename))
                            else:
                                self.movielist.append(
                                    ("movie", filename, "Finished", 100, "100%"))
                                print(
                                    "[DEBUG] Added completed movie: {}".format(filename))

                if not filelist:
                    titel2 = '({} offline)'.format(folder)
                    self['label2'].setText(titel2)
                    self['totalItem'].setText(
                        'Item {}'.format(str(self.totalItem)))

    def getTaskList(self):
        try:
            print("[DEBUG] Pending jobs: {}".format(
                len(JobManager.getPendingJobs())))
            print("[DEBUG] Active jobs: {}".format(
                len(JobManager.active_jobs)))

            all_jobs = JobManager.getPendingJobs() + JobManager.active_jobs
            seen = set()
            unique_jobs = []
            for job in all_jobs:
                job_id = id(job)
                if job_id not in seen:
                    seen.add(job_id)
                    unique_jobs.append(job)

            print(
                "[DEBUG] Total unique jobs to process: {}".format(
                    len(unique_jobs)))

            for i, job in enumerate(unique_jobs):
                try:
                    if not hasattr(job, 'status'):
                        continue

                    job_class_name = job.__class__.__name__
                    if job_class_name != 'downloadJob':
                        print("[DEBUG] Skipping system job: {}".format(job_class_name))
                        continue

                    NOT_STARTED = 0
                    IN_PROGRESS = 1
                    FINISHED = 2
                    FAILED = 3

                    job_name = getattr(job, 'name', 'Unknown')
                    job_filename = getattr(job, 'filename', '')

                    is_series = "series" in job_name.lower(
                    ) or "serie" in job_name.lower() or "episode" in job_name.lower()
                    print(
                        "[DEBUG] Processing job {}: {}, Status: {}, Series: {}".format(
                            i, job_name, job.status, is_series))

                    if job.status != FINISHED:
                        current_progress = 0
                        if hasattr(job, 'tasks') and job.tasks:
                            for task in job.tasks:
                                if hasattr(task, 'progress'):
                                    current_progress = task.progress
                                    break

                        if job.status == NOT_STARTED:
                            status_text = _("PAUSED")
                            current_progress = 0
                        elif job.status == IN_PROGRESS:
                            status_text = _("DOWNLOADING")
                        elif job.status == FAILED:
                            status_text = _("FAILED")
                        else:
                            status_text = job.getStatustext() if hasattr(
                                job, 'getStatustext') else _('UNKNOWN')

                        display_name = job_name
                        if job_filename and is_series:
                            import os
                            base_name = os.path.basename(job_filename)
                            display_name = "SERIES: {}".format(base_name)

                        list_entry = (
                            job,
                            display_name,
                            status_text,
                            current_progress,
                            "{}%".format(current_progress)
                        )
                        self.movielist.append(list_entry)
                        print(
                            "[DEBUG] ADDED JOB to movielist: {} - Status: {}".format(display_name, job.status))

                except Exception as e:
                    print("Error processing job {}: {}".format(i, e))
        except Exception as e:
            print("Error in getTaskList: {}".format(e))

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
        self.sel2 = cfg.pthmovie.value + \
            filename if hasattr(cfg, 'pthmovie') and cfg.pthmovie.value else ""
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

    def remove_download(self):
        """Remove download task without deleting file"""
        current = self["filelist"].getCurrent()
        if current is None or not isinstance(
                current, tuple) or len(current) < 2:
            self.session.open(
                MessageBox,
                _("No task selected!"),
                MessageBox.TYPE_INFO,
                timeout=5)
            return

        job = current[0]
        if isinstance(job, Job):
            job_name = getattr(job, 'name', 'Unknown')
            self.session.openWithCallback(
                lambda result: self.confirm_remove(result, job),
                MessageBox,
                _("Remove download task for {}?").format(job_name),
                MessageBox.TYPE_YESNO
            )
        else:
            self.session.open(
                MessageBox,
                _("Cannot remove this item"),
                MessageBox.TYPE_INFO,
                timeout=5)

    def confirm_remove(self, result, job):
        if result:
            try:
                job.cancel()
                print(
                    "[TASK] Removed: {}".format(
                        getattr(
                            job,
                            'name',
                            'Unknown')))
                self.rebuildMovieList()
                self.session.open(
                    MessageBox,
                    _("Download task removed"),
                    MessageBox.TYPE_INFO,
                    timeout=3
                )
            except Exception as e:
                print("[TASK] Error removing job: {}".format(e))
                self.session.open(
                    MessageBox,
                    _("Error removing task: {}").format(str(e)),
                    MessageBox.TYPE_ERROR,
                    timeout=5
                )


def shell_quote(s):
    return "'" + s.replace("'", "'\"'\"'") + "'"


class downloadJob(Job):
    def __init__(self, toolbox, cmdline, filename, filmtitle):
        Job.__init__(self, filmtitle)

        def enigma_quote(s):
            if isinstance(s, bytes):
                s = s.decode('utf-8', 'ignore')
            s = str(s).replace("'", "'\"'\"'")
            return "'" + s + "'"

        if isinstance(cmdline, list):
            quoted_cmd = []
            for arg in cmdline:
                arg_str = str(arg)
                if ' ' in arg_str or any(
                        char in arg_str for char in '()[]{}!$&*?;'):
                    quoted_cmd.append(enigma_quote(arg_str))
                else:
                    quoted_cmd.append(arg_str)
            cmdline = " ".join(quoted_cmd)
        else:
            cmdline = str(cmdline)

        self.cmdline = cmdline
        print("cmdline= {}".format(self.cmdline))
        print("type cmdline= {}".format(type(self.cmdline)))

        self.filename = filename
        self.toolbox = toolbox
        self.retrycount = 0

        self.task = downloadTask(self, self.cmdline, filename, filmtitle)
        self.addTask(self.task)

        self.status = self.NOT_STARTED
        print("[JOB] Job created in MANUAL state: {}".format(filmtitle))

    def start_manually(self):
        """Start job manually"""
        if self.status == self.NOT_STARTED:
            print("[JOB] Manually starting: {}".format(self.name))
            self.status = self.IN_PROGRESS
            self.runNext()
        else:
            print("[JOB] Cannot start job - status is: {}".format(self.status))

    def retry(self):
        """Retry failed job"""
        if self.status == self.FAILED:
            print("[JOB] Retrying: {}".format(self.name))
            self.status = self.NOT_STARTED
            self.start_manually()
        else:
            print("[JOB] Cannot retry job - status is: {}".format(self.status))

    def cancel(self):
        """Cancel job"""
        print("[JOB] Cancelling: {}".format(self.name))
        self.abort()

    def jobFinished(self, job, task, events):
        """Called when job finishes"""
        print("[JOB] Job finished: {}".format(self.name))
        self.status = self.FINISHED
        if hasattr(self.toolbox, 'updatescreen'):
            self.toolbox.updatescreen()

    def jobFailed(self, job, task, events):
        """Called when job fails"""
        print("[JOB] Job failed: {}".format(self.name))
        self.status = self.FAILED
        if hasattr(self.toolbox, 'updatescreen'):
            self.toolbox.updatescreen()


class downloadTaskPostcondition(Condition):
    RECOVERABLE = True

    def check(self, task):
        """Check if task completed successfully"""
        if not isinstance(task, downloadTask):
            return False

        # The task is considered successful if:
        # 1. The return code is 0
        # 2. There are no errors set
        # 3. The file exists and is of reasonable size
        success = (task.returncode == 0 and
                   task.error is None and
                   file_exists(task.filename) and
                   getsize(task.filename) > 1024)

        print("[POST-CONDITION] Check result for {}: {}".format(task.filmtitle, success))
        return success

    def getErrorMessage(self, task):
        if not isinstance(task, downloadTask):
            return _("Unknown task error")

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

        error_msg = errors.get(task.error, _("Unknown error: %s") % task.lasterrormsg)
        print("[POST-CONDITION] Error message for {}: {}".format(task.filmtitle, error_msg))
        return error_msg


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

        self.postconditions = [downloadTaskPostcondition()]
        print("[TASK] Task created for: {}".format(filmtitle))

    def processOutput(self, data):
        """Process wget output to extract progress"""
        try:
            if data is None:
                return

            data_str = ""
            if isinstance(data, bytes):
                try:
                    data_str = data.decode("utf-8", "ignore")
                except UnicodeDecodeError:
                    data_str = data.decode("latin-1", "ignore")
            elif isinstance(data, str):
                data_str = data
            else:
                data_str = str(data)

            # if data_str.strip():
                # print("[DOWNLOAD OUTPUT] {}".format(data_str.strip()))

            if '%' in data_str:
                percentages = findall(r'(\d+)%', data_str)
                if percentages:
                    try:
                        new_progress = max(map(int, percentages))
                        if 0 <= new_progress <= 100 and new_progress > self.progress:
                            self.progress = new_progress
                            self.setProgress(self.progress)
                            print("[DOWNLOAD PROGRESS] {}: {}%".format(self.filmtitle, self.progress))

                            if hasattr(self.toolbox, 'updatescreen'):
                                self.toolbox.updatescreen()
                    except ValueError as e:
                        print("[PROGRESS PARSE ERROR] {}".format(e))

        except Exception as e:
            print("[PROGRESS ERROR] {}".format(e))

    def afterRun(self):
        """Called after download completes"""
        print("[DOWNLOAD TASK] afterRun called - Progress: {}%, Return code: {}".format(self.progress, self.returncode))

        try:
            if self.returncode == 0:
                if file_exists(self.filename):
                    file_size = getsize(self.filename)
                    print("[DOWNLOAD TASK] File exists, size: {} bytes".format(file_size))

                    if file_size > 1024:
                        self.progress = 100
                        self.setProgress(100)
                        print("[DOWNLOAD COMPLETE] {}: 100%".format(self.filmtitle))

                        if hasattr(self.toolbox, 'updatescreen'):
                            self.toolbox.updatescreen()

                        try:
                            if hasattr(self.toolbox, 'download_finished'):
                                self.toolbox.download_finished(self.filename, self.filmtitle)
                        except Exception as e:
                            print("Error in download_finished:", e)
                    else:
                        print("[DOWNLOAD TASK] Download failed - file too small")
                        self.error = self.ERROR_FILESYSTEM
                        self.lasterrormsg = _("Downloaded file is too small")
                else:
                    print("[DOWNLOAD TASK] Download failed - file not found")
                    self.error = self.ERROR_FILESYSTEM
                    self.lasterrormsg = _("Downloaded file not found")
            else:
                print("[DOWNLOAD FAILED] {}: returncode={}".format(self.filmtitle, self.returncode))
                self.error = self.ERROR_UNKNOWN
                self.lasterrormsg = _("Download failed with return code: {}").format(self.returncode)

        except Exception as e:
            print("Error in afterRun:", e)
            self.error = self.ERROR_UNKNOWN
            self.lasterrormsg = _("Error verifying download: {}").format(str(e))

        Task.afterRun(self)

    def processOutputLine(self, line):
        """Process individual output lines"""
        pass

    def prepare(self):
        """Prepare task before execution"""
        print("[DOWNLOAD TASK] Preparing download: {}".format(self.filmtitle))
        return 0

    def cleanup(self, failed):
        """Cleanup after task completion"""
        print("[DOWNLOAD TASK] Cleanup for: {} (failed: {})".format(self.filmtitle, failed))


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
