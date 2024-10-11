#!/usr/bin/python
# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

from __future__ import absolute_import
__author__ = "Lululla"
__email__ = "ekekaz@gmail.com"
__copyright__ = 'Copyright (c) 2024 Lululla'
__license__ = "GPL-v2"
__version__ = "1.0.0"

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
import gettext
import os
from os import environ as os_environ

PluginLanguageDomain = 'XCplugin'
PluginLanguagePath = 'Extensions/XCplugin/locale'
isDreamOS = False
if os.path.exists("/usr/bin/apt-get"):
    isDreamOS = True


def paypal():
    conthelp = "If you like what I do you\n"
    conthelp += "can contribute with a coffee\n"
    conthelp += "scan the qr code and donate € 1.00"
    return conthelp


def wanStatus():
    publicIp = ''
    try:
        file = os.popen('wget -qO - ifconfig.me')
        public = file.read()
        publicIp = "Wan %s" % (str(public))
    except:
        if os.path.exists("/tmp/currentip"):
            os.remove("/tmp/currentip")
    return publicIp


def localeInit():
    if isDreamOS:
        lang = language.getLanguage()[:2]
        os_environ["LANGUAGE"] = lang
    gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))


if isDreamOS:
    def _(txt):
        return gettext.dgettext(PluginLanguageDomain, txt) if txt else ""
else:
    def _(txt):
        translated = gettext.dgettext(PluginLanguageDomain, txt)
        if translated:
            return translated
        else:
            print(("[%s] fallback to default translation for %s" % (PluginLanguageDomain, txt)))
            return gettext.gettext(txt)
