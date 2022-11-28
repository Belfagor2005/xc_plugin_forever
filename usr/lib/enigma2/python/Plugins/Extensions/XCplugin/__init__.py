#!/usr/bin/python
# -*- coding: utf-8 -*-

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
import gettext
import os
from os import environ as os_environ


# try:
    # from . import Utils
    # from . import Update
    # if Utils.zCheckInternet(1):
    # try:
        # Update.upd_done()
    # except Exception as e:
        # print('error ', str(e))
    # else:
        # from Screens.MessageBox import MessageBox
        # from Tools.Notifications import AddPopup
        # AddPopup(_("Sorry but No Internet :("),MessageBox.TYPE_INFO, 10, 'Sorry')            
# except:
    # import traceback
    # traceback.print_exc()

PluginLanguageDomain = 'XCplugin'
PluginLanguagePath = 'Extensions/XCplugin/locale'
try:
    from enigma import eMediaDatabase
    isDreamOS = True
except:
    isDreamOS = False

def localeInit():
    if isDreamOS: 
        lang = language.getLanguage()[:2] 
        os_environ["LANGUAGE"] = lang 
    gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))

           
if isDreamOS:  # check if DreamOS image
    _ = lambda txt: gettext.dgettext(PluginLanguageDomain, txt) if txt else ""
    localeInit()
    language.addCallback(localeInit)
else:
    def _(txt):
        if gettext.dgettext(PluginLanguageDomain, txt):
            return gettext.dgettext(PluginLanguageDomain, txt)
        else:
            print(("[%s] fallback to default translation for %s" % (PluginLanguageDomain, txt)))
            return gettext.gettext(txt)
    language.addCallback(localeInit())


