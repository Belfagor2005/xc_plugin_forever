#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------#
#   edit by Lululla   #
#    skin by MMark    #
#      22/09/2023     #
# --------------------#

from .Utils import RequestAgent
from enigma import eTimer
from os import unlink
from twisted.internet import reactor
import os
import requests

try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request

sslverify = False
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


class DownloadWithProgress:
    def __init__(self, url, outputFile):
        print('url:', url)
        self.url = url
        self.outputFile = outputFile
        self.userAgent = RequestAgent()  # "HbbTV/1.1.1 (+PVR+RTSP+DL; Sonic; TV44; 1.32.455; 2.002) Bee/3.5"
        self.blockSize = 0
        self.totalSize = 0
        self.progress = 0
        self.progressCallback = None
        self.endCallback = None
        self.errorCallback = None
        self.stopFlag = False
        self.timer = eTimer()
        if os.path.exists('/var/lib/dpkg/info'):
            self.timer_conn = self.timer.timeout.connect(self.reportProgress)
        else:
            self.timer.callback.append(self.reportProgress)
        self.timer.start(500, 1)

    def start(self):
        try:
            request = Request(self.url, None, {"User-agent": RequestAgent()})
            feedFile = urlopen(request)
            metaData = feedFile.headers
            self.totalSize = int(metaData.get("Content-Length", 0))
            self.blockSize = max(min(self.totalSize // 100, 1024), 131071) if self.totalSize else 65536
        except OSError as err:
            if self.errorCallback:
                self.errorCallback(err)
            return self
        reactor.callInThread(self.run)
        return self

    def run(self):
        # requests.Response object = requests.get(url, params=None, allow_redirects=True, auth=None, cert=None, cookies=None, headers=None, proxies=None, stream=False, timeout=None, verify=True)
        # response = requests.get(self.url, headers={"User-agent": self.userAgent}, stream=True)  # Streaming, so we can iterate over the response.
        response = requests.get(self.url, headers={"User-agent": RequestAgent()}, stream=True)  # Streaming, so we can iterate over the response.
        try:
            with open(self.outputFile, "wb") as fd:
                for buffer in response.iter_content(self.blockSize):
                    if self.stopFlag:
                        response.close()
                        fd.close()
                        unlink(self.outputFile)
                        return True
                    self.progress += len(buffer)
                    if self.progressCallback:
                        self.timer.start(0, True)
                    fd.write(buffer)
            if self.endCallback:
                self.endCallback(self.outputFile)
        except OSError as err:
            if self.errorCallback:
                self.errorCallback(err)
        return False

    def stop(self):
        self.stopFlag = True

    def reportProgress(self):
        self.progressCallback(self.progress, self.totalSize)

    def addProgress(self, progressCallback):
        self.progressCallback = progressCallback

    def addEnd(self, endCallback):
        self.endCallback = endCallback

    def addError(self, errorCallback):
        self.errorCallback = errorCallback

    def setAgent(self, userAgent):
        self.userAgent = userAgent

    def addErrback(self, errorCallback):  # Temporary supprt for deprecated callbacks.
        print("[Downloader] Warning: DownloadWithProgress 'addErrback' is deprecated use 'addError' instead!")
        self.errorCallback = errorCallback
        return self

    def addCallback(self, endCallback):  # Temporary supprt for deprecated callbacks.
        print("[Downloader] Warning: DownloadWithProgress 'addCallback' is deprecated use 'addEnd' instead!")
        self.endCallback = endCallback
        return self


class downloadWithProgress(DownloadWithProgress):  # Class names should start with a Capital letter, this catches old code until that code can be updated.
    pass
