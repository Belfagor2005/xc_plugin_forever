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

from __future__ import absolute_import

# Built-in imports
from gettext import bindtextdomain, dgettext, gettext
from os import environ as os_environ, popen, remove
from os.path import exists, join

# Enigma2 imports
from Components.Language import language
from Components.config import config
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

# Local package imports
from .addons import Utils


__author__ = "Lululla"
__email__ = "ekekaz@gmail.com"
__copyright__ = 'Copyright (c) 2024 Lululla'
__license__ = "GPL-v2"
currversion = '4.9'
version = "XC Forever V.%s" % currversion
plugin_path = resolveFilename(
    SCOPE_PLUGINS,
    "Extensions/{}".format('XCplugin'))
installer_url = 'https://raw.githubusercontent.com/Belfagor2005/xc_plugin_forever/main/installer.sh=='
developer_url = 'aHR0cHM6Ly9hcGkuZ2l0aHViLmNvbS9yZXBvcy9CZWxmYWdvcjIwMDUveGNfcGx1Z2luX2ZvcmV2ZXI='
AgentRequest = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.3'
PluginLanguageDomain = 'XCplugin'
PluginLanguagePath = join(plugin_path, 'locale')


isDreamOS = False
if exists("/usr/bin/apt-get"):
    isDreamOS = True


def paypal():
    conthelp = "If you like what I do you\n"
    conthelp += "can contribute with a coffee\n"
    conthelp += "scan the qr code and donate € 1.00"
    return conthelp


def wanStatus():
    publicIp = ''
    try:
        file = popen('wget -qO - ifconfig.me')
        public = file.read()
        publicIp = "Wan %s" % (str(public))
    except BaseException:
        if exists("/tmp/currentip"):
            remove("/tmp/currentip")
    return publicIp


def localeInit():
    if isDreamOS:
        lang = language.getLanguage()[:2]
        os_environ["LANGUAGE"] = lang
    bindtextdomain(
        PluginLanguageDomain,
        resolveFilename(
            SCOPE_PLUGINS,
            PluginLanguagePath))


if isDreamOS:
    def _(txt):
        return dgettext(PluginLanguageDomain, txt) if txt else ""
else:
    def _(txt):
        translated = dgettext(PluginLanguageDomain, txt)
        if translated:
            return translated
        else:
            print(("[%s] fallback to default translation for %s" %
                  (PluginLanguageDomain, txt)))
            return gettext(txt)


def checkGZIP(url):
    url = url
    from io import StringIO
    import gzip
    import requests
    import sys
    if sys.version_info[0] == 3:
        from urllib.request import (urlopen, Request)
    else:
        from urllib2 import (urlopen, Request)

    hdr = {"User-Agent": AgentRequest}
    response = None
    request = Request(url, headers=hdr)
    try:
        response = urlopen(request, timeout=10)
        if response.info().get('Content-Encoding') == 'gzip':
            buffer = StringIO(response.read())
            deflatedContent = gzip.GzipFile(fileobj=buffer)
            if sys.version_info[0] == 3:
                return deflatedContent.read().decode('utf-8')
            else:
                return deflatedContent.read()
        else:
            if sys.version_info[0] == 3:
                return response.read().decode('utf-8')
            else:
                return response.read()

    except requests.exceptions.RequestException as e:
        print("Request error:", e)
    except Exception as e:
        print("Unexpected error:", e)
    return None


def b64decoder(s):
    s = str(s).strip()
    import base64
    import sys
    try:
        output = base64.b64decode(s)
        if sys.version_info[0] == 3:
            output = output.decode('utf-8')
        return output
    except Exception:
        padding = len(s) % 4
        if padding == 1:
            print('Invalid base64 string: {}'.format(s))
            return ""
        elif padding == 2:
            s += b'=='
        elif padding == 3:
            s += b'='
        else:
            return ""
        output = base64.b64decode(s)
        if sys.version_info[0] == 3:
            output = output.decode('utf-8')
        return output


def make_request(url, max_retries=3, base_delay=1):
    import time
    import socket
    import sys
    import six

    if sys.version_info[0] == 3:
        from urllib.request import (urlopen, Request)
        from urllib.error import URLError
    else:
        from urllib2 import (urlopen, Request)
        from urllib2 import URLError

    for attempt in range(max_retries):
        try:
            req = Request(url)
            req.add_header('User-Agent', AgentRequest)
            # start_time = time.time()
            response = urlopen(req, None, 30)
            # elapsed_time = time.time() - start_time
            # print('elapsed_time:', elapsed_time)
            if response.getcode() == 200:
                content = response.read()
                if not content:
                    return None
                try:
                    content = six.ensure_str(content, errors='replace')
                except UnicodeDecodeError:
                    print("Decoding error with 'utf-8', trying 'latin-1'...")
                    content = content.decode('latin-1', errors='replace')
                    # print("Contenuto decodificato con latin-1:\n", content)
                return content
        except URLError as e:
            if isinstance(e.reason, socket.timeout):
                delay = base_delay * (2 ** attempt)
                # print("Timeout occurred. Retrying in seconds...", str(delay))
                time.sleep(delay)
            else:
                print("URLError occurred:", str(e))
                return None
    print("Max retries reached.")
    return None


def check_port(url):
    print('check_port url init=', check_port)
    line = url.strip()
    protocol = 'http://'
    domain = ''
    port = ''
    if str(config.plugins.XCplugin.port.value) != '80':
        port = str(config.plugins.XCplugin.port.value)
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
        from requests.adapters import HTTPAdapter, Retry
        import requests
        retries = Retry(total=1, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retries)
        http = requests.Session()
        http.mount("http://", adapter)
        http.mount("https://", adapter)
        r = http.get(
            url,
            headers={
                'User-Agent': Utils.RequestAgent()},
            timeout=10,
            verify=False)  # , stream=True)
        r.raise_for_status()
        if r.status_code == requests.codes.ok:
            print('retTest r.status code: ', r.status_code)
            ycse = r.json()
            # print('ycse -----------> ', ycse)
            return ycse
    except Exception as e:
        return False
        print('error retTest requests -----------> ', e)
