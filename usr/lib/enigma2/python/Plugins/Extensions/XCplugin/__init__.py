#!/usr/bin/python
# -*- coding: utf-8 -*-
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
import gettext
from os import environ as os_environ
plugin_path = '/usr/lib/enigma2/python/Plugins/Extensions/XCplugin/'
PluginLanguageDomain = 'XCplugin'
PluginLanguagePath = plugin_path + 'locale'
try:
    from enigma import eMediaDatabase
    xcDreamOS = True
except:
    xcDreamOS = False

def localeInit():
    if xcDreamOS:
        lang = language.getLanguage()[:2]
        os_environ['LANGUAGE'] = lang
    gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))

if xcDreamOS:
    _ = lambda txt: (gettext.dgettext(PluginLanguageDomain, txt) if txt else '')
    localeInit()
    language.addCallback(localeInit)
else:
    def _(txt):
        if gettext.dgettext(PluginLanguageDomain, txt):
            return gettext.dgettext(PluginLanguageDomain, txt)
        else:
            # print ('[' + PluginLanguageDomain + '] fallback to default translation for ' + txt)
            return gettext.gettext(txt)
    language.addCallback(localeInit())