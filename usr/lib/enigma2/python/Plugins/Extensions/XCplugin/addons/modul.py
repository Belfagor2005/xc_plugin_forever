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
from . import _

from Components.config import config
from os import system
import re
try:
    from Components.AVSwitch import AVSwitch
except ImportError:
    from Components.AVSwitch import eAVControl as AVSwitch
try:
    from types import SimpleNamespace
except ImportError:

    class SimpleNamespace:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)


globalsxp = SimpleNamespace(
    autoStartTimer=None,
    # channel_list2=None,
    btnsearch=0,
    eserv=None,
    infoname=None,
    iptv_list_tmp=[],
    isStream=False,
    next_request=0,
    Path_Movies2=None,
    Path_Movies=None,
    piclogo=None,
    pictmp="/tmp/poster.jpg",
    re_search=False,
    search_ok=None,
    series=False,
    STREAMS=None,
    stream_live=None,
    stream_url=None,
    ui=True,  #not used
    urlinfo=None,
    url_tmp=None,
)


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

Panel_list = [('HOME'), ('PLAYLIST'), ('MAKER BOUQUET'),
              ('DOWNLOADER'), ('M3U LOADER'), ('CONFIG'), ('ABOUT & HELP')]
VIDEO_ASPECT_RATIO_MAP = {0: "4:3 Letterbox", 1: "4:3 PanScan", 2: "16:9", 3: "16:9 Always", 4: "16:10 Letterbox", 5: "16:10 PanScan", 6: "16:9 Letterbox"}
VIDEO_FMT_PRIORITY_MAP = {"38": 1, "37": 2, "22": 3, "18": 4, "35": 5, "34": 6}


try:
    def copy_poster():
        import subprocess
        piclogo = str(globalsxp.piclogo[0])
        pictmp = str(globalsxp.pictmp)
        if isinstance(globalsxp.piclogo, tuple) and len(globalsxp.piclogo) == 1:
            piclogo = str(globalsxp.piclogo[0])  # Estrai il percorso dal primo (e unico) elemento della tupla
        else:
            print("Error: piclogo is not a single-element tuple!")
            piclogo = None
        if isinstance(globalsxp.pictmp, str):
            pictmp = str(globalsxp.pictmp)
        else:
            print("Error: pictmp is not a string!")
            pictmp = None
        if piclogo and pictmp:
            print("Executing the command 'copy_poster'...")
            command = ["cp", "-f", piclogo, pictmp]
            return_code = subprocess.call(command)
            if return_code != 0:
                print("Error executing command.")
            else:
                print("Command executed successfully.")
        else:
            print("Command not executed: piclogo or pictmp are invalid.")
    copy_poster()
except:
    pass


def clear_caches():
    try:
        system("echo 1 > /proc/sys/vm/drop_caches")
        system("echo 2 > /proc/sys/vm/drop_caches")
        system("echo 3 > /proc/sys/vm/drop_caches")
    except:
        pass


def cleanNames(name):
    cleanName = re.sub(r'[\'\<\>\:\"\/\\\|\?\*\(\)\[\]]', "", name)
    cleanName = re.sub(r"   ", " ", cleanName)
    cleanName = re.sub(r"  ", " ", cleanName)
    cleanName = re.sub(r"---", "-", cleanName)
    name = cleanName.strip()
    return name


def getAspect():
    return AVSwitch().getAspectRatioSetting()


def getAspectString(aspectnum):
    return {
        0: '4:3 Letterbox',
        1: '4:3 PanScan',
        2: '16:9',
        3: '16:9 always',
        4: '16:10 Letterbox',
        5: '16:10 PanScan',
        6: '16:9 Letterbox'
    }[aspectnum]


def setAspect(aspect):
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


def nextAR():
    globalsxp.STREAMS.ar_id_player += 1
    if globalsxp.STREAMS.ar_id_player > 6:
        globalsxp.STREAMS.ar_id_player = 0
    try:
        AVSwitch.getInstance().setAspectRatio(globalsxp.STREAMS.ar_id_player)
        return VIDEO_ASPECT_RATIO_MAP[globalsxp.STREAMS.ar_id_player]
    except Exception as e:
        print(e)
        return _("Resolution Change Failed")


def prevAR():
    globalsxp.STREAMS.ar_id_player -= 1
    if globalsxp.STREAMS.ar_id_player == -1:
        globalsxp.STREAMS.ar_id_player = 6
    try:
        AVSwitch.getInstance().setAspectRatio(globalsxp.STREAMS.ar_id_player)
        return VIDEO_ASPECT_RATIO_MAP[globalsxp.STREAMS.ar_id_player]
    except Exception as e:
        print(e)
        return _("Resolution Change Failed")
