# Embedded file name: /usr/lib/enigma2/python/Plugins/Extensions/E2m3u2bouquet/e2m3u2bouquet.py
"""
e2m3u2bouquet.e2m3u2bouquet -- Enigma2 IPTV m3u to bouquet parser

@author:     Dave Sully, Doug Mackay
@copyright:  2017 All rights reserved.
@license:    GNU GENERAL PUBLIC LICENSE version 3
@deffield    updated: Updated
"""
from __future__ import print_function
import time
import sys
import os
import errno
import re
import unicodedata
import datetime
# import urllib
# import urlparse
import imghdr
# from . import imghdr
import tempfile
import glob
import ssl
import hashlib
import socket
from PIL import Image
from collections import OrderedDict

from sys import version_info
# PY3 = sys.version_info.major >= 3
PY3 = version_info[0] == 3

if PY3:
    from urllib.request import urlopen, Request
    from urllib.request import FancyURLopener
    from urllib.error import URLError, HTTPError
    from urllib.parse import urlparse
    from urllib.parse import urlencode, quote, quote_plus
    from urllib.parse import parse_qs
    from urllib.request import urlretrieve
    import urllib
    xrange = range
else:
    from urllib import urlretrieve
    from urllib import FancyURLopener
    from urllib2 import urlopen, Request
    from urllib2 import URLError, HTTPError
    from urlparse import urlparse
    from urlparse import parse_qs
    from urllib import urlencode, quote, quote_plus
    import urllib

def checkStr(txt):
    # convert variable to type str both in Python 2 and 3
    if PY3:
        # Python 3
        if type(txt) == type(bytes()):
            txt = txt.decode('utf-8')
    else:
        #Python 2
        if type(txt) == type(unicode()):
            txt = txt.encode('utf-8')

    return txt

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

try:
    from enigma import eDVBDB
except ImportError:
    eDVBDB = None
# from enigma import eDVBDB
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

def reload_bouquets():
    eDVBDB.getInstance().reloadServicelist()
    eDVBDB.getInstance().reloadBouquets()


from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from xml.sax.saxutils import escape
__all__ = []
__version__ = '0.8.5'
__date__ = '2017-06-04'
__updated__ = '2020-01-28'
DEBUG = 0
TESTRUN = 0
ENIGMAPATH = '/etc/enigma2/'
EPGIMPORTPATH = '/etc/epgimport/'
CFGPATH = os.path.join(ENIGMAPATH, 'e2m3u2bouquet/')
PICONSPATH = '/usr/share/enigma2/picon/'
IMPORTED = False
PLACEHOLDER_SERVICE = '#SERVICE 1:832:d:0:0:0:0:0:0:0:'

class CLIError(Exception):
    """Generic exception to raise and log different fatal errors."""

    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = 'E: %s' % msg

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg

headers        = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' }


class AppUrlOpener(FancyURLopener):
    """Set user agent for downloads
    """
    version = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'


def display_welcome():
    print('\n********************************')
    print('Starting Enigma2 IPTV bouquets v{}'.format(__version__))
    print(str(datetime.datetime.now()))
    print('********************************\n')


def display_end_msg():
    print('\n********************************')
    print('Enigma2 IPTV bouquets created ! ')
    print('********************************')
    print('\nTo enable EPG data')
    print('Please open EPG-Importer plugin.. ')
    print('Select sources and enable the new IPTV source')
    print("(will be listed as under 'XCplugin')")
    print('Save the selected sources, press yellow button to start manual import')
    print('You can then set EPG-Importer to automatically import the EPG every day')


def make_config_folder():
    """create config folder if it doesn't exist
    """
    try:
        os.makedirs(CFGPATH)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def uninstaller():
    """Clean up routine to remove any previously made changes
    """
    print('----Running uninstall----')
    try:
        print('Removing old IPTV bouquets...')
        for fname in os.listdir(ENIGMAPATH):
            if 'userbouquet.suls_iptv_' in fname:
                os.remove(os.path.join(ENIGMAPATH, fname))
            elif 'bouquets.tv.bak' in fname:
                os.remove(os.path.join(ENIGMAPATH, fname))

        print('Removing IPTV custom channels...')
        if os.path.isdir(EPGIMPORTPATH):
            for fname in os.listdir(EPGIMPORTPATH):
                if 'suls_iptv_' in fname:
                    os.remove(os.path.join(EPGIMPORTPATH, fname))

        print('Removing IPTV bouquets from bouquets.tv...')
        os.rename(os.path.join(ENIGMAPATH, 'bouquets.tv'), os.path.join(ENIGMAPATH, 'bouquets.tv.bak'))
        tvfile = open(os.path.join(ENIGMAPATH, 'bouquets.tv'), 'w+')
        bakfile = open(os.path.join(ENIGMAPATH, 'bouquets.tv.bak'))
        for line in bakfile:
            if '.suls_iptv_' not in line:
                tvfile.write(line)

        bakfile.close()
        tvfile.close()
    except Exception as e:
        print('Unable to uninstall')
        raise

    print('----Uninstall complete----')


def get_category_title(cat, category_options):
    """Return the title override if set else the title
    """
    if cat in category_options:
        if category_options[cat].get('nameOverride', False):
            return category_options[cat]['nameOverride']
        return cat
    return cat


def get_service_title(channel):
    """Return the title override if set else the title
    """
    if channel.get('nameOverride', False):
        return channel['nameOverride']
    return channel['stream-name']


def reload_bouquets():
    if not TESTRUN:
        print('\n----Reloading bouquets----')
        if eDVBDB:
            eDVBDB.getInstance().reloadBouquets()
            print('bouquets reloaded...')
        else:
            os.system('wget -qO - http://127.0.0.1/web/servicelistreload?mode=2 > /dev/null 2>&1 &')
            print('bouquets reloaded...')


def xml_escape(string):
    return escape(string, {'"': '&quot;',
     "'": '&apos;'})


def xml_safe_comment(string):
    """Can't have -- in xml comments"""
    return string.replace('--', '- - ')


def get_safe_filename(filename, fallback = ''):
    """Convert filename to safe filename
    """
    name = filename.replace(' ', '_').replace('/', '_')
    name =checkStr(name) #test
    if PY3:
        name = unicodedata.normalize('NFKD', name)
    else:
        name = unicodedata.normalize('NFKD', unicode(name, 'utf_8', errors='ignore')).encode('ASCII', 'ignore')
    name = re.sub('[^a-z0-9-_]', '', name.lower())
    if not name:
        name = fallback
    return name


def get_parser_args(program_license, program_version_message):
    parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
    urlgroup = parser.add_argument_group('URL Based Setup')
    urlgroup.add_argument('-m', '--m3uurl', dest='m3uurl', action='store', help='URL to download m3u data from (required)')
    urlgroup.add_argument('-e', '--epgurl', dest='epgurl', action='store', help='URL source for XML TV epg data sources')
    providergroup = parser.add_argument_group('Provider Based Setup')
    providergroup.add_argument('-n', '--providername', dest='providername', action='store', help='Host IPTV provider name (e.g. FAB/EPIC) (required)')
    providergroup.add_argument('-u', '--username', dest='username', action='store', help='Your IPTV username (required)')
    providergroup.add_argument('-p', '--password', dest='password', action='store', help='Your IPTV password (required)')
    parser.add_argument('-i', '--iptvtypes', dest='iptvtypes', action='store_true', help='Treat all stream references as IPTV stream type. (required for some enigma boxes)')
    parser.add_argument('-sttv', '--streamtype_tv', dest='sttv', action='store', type=int, help='Stream type for TV (e.g. 1, 4097, 5001 or 5002) overrides iptvtypes')
    parser.add_argument('-stvod', '--streamtype_vod', dest='stvod', action='store', type=int, help='Stream type for VOD (e.g. 4097, 5001 or 5002) overrides iptvtypes')
    parser.add_argument('-M', '--multivod', dest='multivod', action='store_true', help='Create multiple VOD bouquets rather single VOD bouquet')
    parser.add_argument('-a', '--allbouquet', dest='allbouquet', action='store_true', help='Create all channels bouquet')
    parser.add_argument('-P', '--picons', dest='picons', action='store_true', help='Automatically download of Picons, this option will slow the execution')
    parser.add_argument('-q', '--iconpath', dest='iconpath', action='store', help='Option path to store picons, if not supplied defaults to /usr/share/enigma2/picon/')
    parser.add_argument('-xs', '--xcludesref', dest='xcludesref', action='store_true', help='Disable service ref overriding from override.xml file')
    parser.add_argument('-b', '--bouqueturl', dest='bouqueturl', action='store', help='URL to download providers bouquet - to map custom service references')
    parser.add_argument('-bd', '--bouquetdownload', dest='bouquetdownload', action='store_true', help='Download providers bouquet (use default url) - to map custom service references')
    parser.add_argument('-bt', '--bouquettop', dest='bouquettop', action='store_true', help='Place IPTV bouquets at top')
    parser.add_argument('-U', '--uninstall', dest='uninstall', action='store_true', help='Uninstall all changes made by this script')
    parser.add_argument('-V', '--version', action='version', version=program_version_message)
    return parser


class Status():
    is_running = False
    message = ''


class ProviderConfig():

    def __init__(self):
        self.name = ''
        self.num = 0
        self.enabled = False
        self.settings_level = ''
        self.m3u_url = ''
        self.epg_url = ''
        self.username = ''
        self.password = ''
        self.provider_update_url = ''
        self.provider_hide_urls = False
        self.iptv_types = False
        self.streamtype_tv = ''
        self.streamtype_vod = ''
        self.multi_vod = False
        self.all_bouquet = False
        self.picons = False
        self.icon_path = ''
        self.sref_override = False
        self.bouquet_url = ''
        self.bouquet_download = False
        self.bouquet_top = False
        self.last_provider_update = 0


class Provider():

    def __init__(self, config):
        self._panel_bouquet_file = ''
        self._panel_bouquet = {}
        self._m3u_file = None
        self._category_order = []
        self._category_options = {}
        self._dictchannels = OrderedDict()
        self._xmltv_sources_list = None
        self.config = config
        return

    def _download_picon_file(self, channel):
        logo_url = channel['tvg-logo']
        if logo_url:
            if not logo_url.startswith('http'):
                logo_url = 'http://{}'.format(logo_url)
            piconname = self._get_picon_name(channel)
            picon_file_path = os.path.join(self.config.icon_path, piconname)
            existingpicon = filter(os.path.isfile, glob.glob(picon_file_path + '*'))
            if not existingpicon:
                if DEBUG:
                    print("Picon file doesn't exist downloading")
                    print('PiconURL: {}'.format(logo_url))
                elif not IMPORTED:
                    sys.stdout.write('.')
                    sys.stdout.flush()
                try:

                    response = checkStr(urlopen(logo_url))

                    # response = urllib.urlopen(logo_url)
                    info = response.info()
                    response.close()
                    if info.maintype == 'image':
                        urlretrieve(logo_url, picon_file_path)
                    else:
                        if DEBUG:
                            print('Download Picon - not an image, skipping')
                        self._picon_create_empty(picon_file_path)
                        return
                except Exception as e:
                    if DEBUG:
                        print(('Download picon urlopen error', e))
                    self._picon_create_empty(picon_file_path)
                    return

                self._picon_post_processing(picon_file_path)

    def _picon_create_empty(self, picon_file_path):
        """
        create an empty picon so that we don't retry this picon
        """
        open(picon_file_path + '.None', 'a').close()

    def _picon_post_processing(self, picon_file_path):
        """Check type of image received and convert to png
        if necessary
        """
        ext = ''
        try:
            ext = imghdr.what(picon_file_path)
        except Exception as e:
            if DEBUG:
                print(('Picon post processing - not an image or no file', e, picon_file_path))
            self._picon_create_empty(picon_file_path)
            return

        if ext is not None and ext != 'png':
            if DEBUG:
                print('Converting Picon to png')
            try:
                Image.open(picon_file_path).save('{}.{}'.format(picon_file_path, 'png'))
            except Exception as e:
                if DEBUG:
                    print(('Picon post processing - unable to convert image', e))
                self._picon_create_empty(picon_file_path)
                return

            try:
                os.remove(picon_file_path)
            except Exception as e:
                if DEBUG:
                    print(('Picon post processing - unable to remove non png file', e))
                return

        else:
            try:
                os.rename(picon_file_path, '{}.{}'.format(picon_file_path, ext))
            except Exception as e:
                if DEBUG:
                    print('Picon post processing - unable to rename file ', e)

        return

    def _get_picon_name(self, channel):
        """Convert the service name to a Picon Service Name
        """
        service_title = get_service_title(channel)
        name = service_title
        name = checkStr(name)
        
        if PY3:
            name = unicodedata.normalize('NFKD', name)
        else:
            name = unicodedata.normalize('NFKD', unicode(name, 'utf_8', errors='ignore')).encode('ASCII', 'ignore')
        
        
        # name = unicodedata.normalize('NFKD', unicode(name, 'utf_8', errors='ignore')).encode('ASCII', 'ignore')
        name = re.sub('[\\W]', '', name.replace('&', 'and').replace('+', 'plus').replace('*', 'star').lower())
        if not name:
            name = channel['serviceRef'].replace(':', '_').upper()
        return name

    def _parse_panel_bouquet(self):
        """Check providers bouquet for custom service references
        """
        if os.path.isfile(self._panel_bouquet_file):
            with open(self._panel_bouquet_file, 'r') as f:
                for line in f:
                    if '#SERVICE' in line:
                        service = line.strip().split(':')
                        if len(service) == 11:
                            pos = service[10].rfind('/')
                            if pos != -1 and pos + 1 != len(service[10]):
                                key = service[10][pos + 1:]
                                value = ':'.join((service[1],
                                 service[2],
                                 service[3],
                                 service[4],
                                 service[5],
                                 service[6],
                                 service[7],
                                 service[8],
                                 service[9]))
                                if value != '0:1:0:0:0:0:0:0:0':
                                    self._panel_bouquet[key] = value

            if not DEBUG:
                os.remove(self._panel_bouquet_file)

    def _set_streamtypes_vodcats(self, service_dict):
        """Set the stream types and VOD categories
        """
        parsed_stream_url = urlparse(service_dict['stream-url'])
        root, ext = os.path.splitext(parsed_stream_url.path)
        is_m3u8_vod = re.search('\\.[^/]+\\.m3u8$', parsed_stream_url.path)
        if parsed_stream_url.path.endswith('ts') or parsed_stream_url.path.endswith('.m3u8') or not ext and not is_m3u8_vod:
            service_dict['stream-type'] = '4097' if self.config.iptv_types else '1'
            if self.config.streamtype_tv:
                service_dict['stream-type'] = str(self.config.streamtype_tv)
        else:
            service_dict['category_type'] = 'vod'
            service_dict['group-title'] = u'VOD - {}'.format(service_dict['group-title'])
            service_dict['stream-type'] = '4097' if not self.config.streamtype_vod else str(self.config.streamtype_vod)

    def _parse_map_bouquet_xml(self):
        """Check for bouquets within mapping override file and applies if found
        """
        category_order = []
        mapping_file = self._get_mapping_file()
        if mapping_file:
            self._update_status('----Parsing custom bouquet order----')
            print('\n'.format(Status.message))
            try:
                tree = ET.ElementTree(file=mapping_file)
                for node in tree.findall('.//category'):
                    dictoption = {}
                    category = node.attrib.get('name')
                    if type(category) is not unicode:
                        category = category.decode('utf-8')
                    cat_title_override = node.attrib.get('nameOverride', '')
                    if type(cat_title_override) is not unicode:
                        cat_title_override = cat_title_override.decode('utf-8')
                    dictoption['nameOverride'] = cat_title_override
                    dictoption['enabled'] = node.attrib.get('enabled', True) == 'true'
                    category_order.append(category)
                    is_custom_category = node.attrib.get('customCategory', False) == 'true'
                    if is_custom_category:
                        dictoption['customCategory'] = True
                        if category not in self._dictchannels:
                            self._dictchannels[category] = []
                    self._category_options[category] = dictoption

                self._update_status('custom bouquet order applied...')
                print(Status.message)
            except Exception as e:
                msg = 'Corrupt override.xml file'
                print(msg)
                if DEBUG:
                    raise msg

        return category_order

    def _set_category_type(self):
        """set category type (live/vod)
        """
        for cat in self._category_order:
            if cat != 'VOD':
                if self._dictchannels.get(cat):
                    if self._category_options.get(cat) is None:
                        dictoption = {'nameOverride': '',
                         'enabled': True,
                         'customCategory': False,
                         type: 'live'}
                        self._category_options[cat] = dictoption
                    self._category_options[cat]['type'] = self._dictchannels[cat][0].get('category_type', 'live')
            elif self._category_options.get(cat) is None:
                dictoption = {'nameOverride': '',
                 'enabled': True,
                 'customCategory': False,
                 type: 'vod'}
                self._category_options[cat] = dictoption

        return

    def _parse_map_channels_xml(self):
        """Check for channels within mapping override file and apply if found
        """
        mapping_file = self._get_mapping_file()
        if mapping_file:
            self._update_status('----Parsing custom channel order, please be patient----')
            print('\n{}'.format(Status.message))
            try:
                tree = ET.ElementTree(file=mapping_file)
                i = 0
                for cat in self._dictchannels:
                    if self._category_options[cat].get('type', 'live') == 'live':
                        sortedchannels = []
                        listchannels = []
                        for node in tree.findall(u'.//channel[@categoryOverride="{}"]'.format(cat)):
                            node_name = node.attrib.get('name')
                            category = node.attrib.get('category')
                            channel_index = None
                            try:
                                channel_index = next((self._dictchannels[category].index(item) for item in self._dictchannels[category] if item['stream-name'] == node_name), None)
                            except KeyError:
                                pass

                            if channel_index is not None:
                                self._dictchannels[cat].append(self._dictchannels[category].pop(channel_index))

                        for x in self._dictchannels[cat]:
                            listchannels.append(x['stream-name'])

                        for node in tree.findall(u'.//channel[@category="{}"]'.format(cat)):
                            node_name = node.attrib.get('name')
                            if node_name == 'placeholder':
                                node_name = 'placeholder_' + str(i)
                                listchannels.append(node_name)
                                self._dictchannels[cat].append({'stream-name': node_name})
                                i += 1
                            sortedchannels.append(node_name)

                        sortedchannels.extend(listchannels)
                        listchannels = OrderedDict(((x, True) for x in sortedchannels)).keys()
                        channel_order_dict = {channel:index for index, channel in enumerate(listchannels)}
                        self._dictchannels[cat].sort(key=lambda x: channel_order_dict[x['stream-name']])

                self._update_status('custom channel order applied...')
                print(Status.message)
                channel_nodes = tree.iter('channel')
                for override_channel in channel_nodes:
                    name = override_channel.attrib.get('name')
                    category = override_channel.attrib.get('category')
                    category_override = override_channel.attrib.get('categoryOverride')
                    channel_index = None
                    channels_list = None
                    if category_override:
                        try:
                            channel_index = next((self._dictchannels[category_override].index(item) for item in self._dictchannels[category_override] if item['stream-name'] == name), None)
                        except KeyError:
                            pass

                    if category_override and channel_index is not None:
                        channels_list = self._dictchannels.get(category_override)
                    else:
                        channels_list = self._dictchannels.get(category)
                    if channels_list is not None and name != 'placeholder':
                        for x in channels_list:
                            if x['stream-name'] == name:
                                if override_channel.attrib.get('enabled') == 'false':
                                    x['enabled'] = False
                                x['nameOverride'] = override_channel.attrib.get('nameOverride', '')
                                x['categoryOverride'] = override_channel.attrib.get('categoryOverride', '')
                                x['tvg-id'] = override_channel.attrib.get('tvg-id', x['tvg-id'])
                                if override_channel.attrib.get('serviceRef', None) and self.config.sref_override:
                                    x['serviceRef'] = override_channel.attrib.get('serviceRef', x['serviceRef'])
                                    x['serviceRefOverride'] = True
                                x['stream-url'] = override_channel.attrib.get('streamUrl', x['stream-url'])
                                clear_stream_url = override_channel.attrib.get('clearStreamUrl') == 'true'
                                if clear_stream_url:
                                    x['stream-url'] = ''
                                break

                self._update_status('custom overrides applied...')
                print(Status.message)
            except Exception as e:
                msg = 'Corrupt override.xml file'
                print(msg)
                if DEBUG:
                    raise msg

        return

    def _get_mapping_file(self):
        mapping_file = None
        provider_safe_filename = self._get_safe_provider_filename()
        search_path = [os.path.join(CFGPATH, provider_safe_filename + '-sort-override.xml'), os.path.join(os.getcwd(), provider_safe_filename + '-sort-override.xml')]
        for path in search_path:
            if os.path.isfile(path):
                mapping_file = path
                break

        return mapping_file

    def _save_bouquet_entry(self, f, channel):
        """Add service to bouquet file
        """
        if not channel['stream-name'].startswith('placeholder_'):
            f.write('#SERVICE {}:{}:\n'.format(channel['serviceRef'], quote(channel['stream-url'])))
            f.write('#DESCRIPTION {}\n'.format(checkStr(get_service_title(channel))))
        else:
            f.write('{}\n'.format(PLACEHOLDER_SERVICE))

    def _get_bouquet_index_name(self, cat_filename, provider_filename):
        return '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.suls_iptv_{}_{}.tv" ORDER BY bouquet\n'.format(provider_filename, cat_filename)

    def _save_bouquet_index_entries(self, iptv_bouquets):
        """Add to the main bouquets.tv file
        """
        current_bouquet_indexes = self._get_current_bouquet_indexes()
        if iptv_bouquets:
            with open(os.path.join(ENIGMAPATH, 'bouquets.tv'), 'w') as f:
                f.write('#NAME Bouquets (TV)\n')
                if self.config.bouquet_top:
                    for bouquet in iptv_bouquets:
                        f.write(bouquet)

                    for bouquet in current_bouquet_indexes:
                        f.write(bouquet)

                else:
                    for bouquet in current_bouquet_indexes:
                        f.write(bouquet)

                    for bouquet in iptv_bouquets:
                        f.write(bouquet)

    def _get_current_bouquet_indexes(self):
        """Get all the bouquet indexes except this provider
        """
        current_bouquets_indexes = []
        with open(os.path.join(ENIGMAPATH, 'bouquets.tv'), 'r') as f:
            for line in f:
                if line.startswith('#NAME'):
                    continue
                elif '.suls_iptv_{}'.format(self._get_safe_provider_filename()) not in line:
                    current_bouquets_indexes.append(line)

        return current_bouquets_indexes

    def _create_all_channels_bouquet(self):
        """Create the Enigma2 all channels bouquet
        """
        self._update_status('----Creating all channels bouquet----')
        print('\n{}'.format(Status.message))
        bouquet_indexes = []
        provider_filename = self._get_safe_provider_filename()
        bouquet_name = '{} All Channels'.format(provider_filename)
        cat_filename = get_safe_filename(bouquet_name)
        bouquet_filepath = os.path.join(ENIGMAPATH, 'userbouquet.suls_iptv_{}_{}.tv'.format(provider_filename, cat_filename))
        if DEBUG:
            print('Creating: {}'.format(bouquet_filepath))
        with open(bouquet_filepath, 'w+') as f:
            f.write('#NAME {} - {}\n'.format(checkStr(self.config.name), checkStr(bouquet_name)))
            for i in xrange(100):
                f.write('{}\n'.format(PLACEHOLDER_SERVICE))

            channel_num = 1
            for cat in self._category_order:
                cat_enabled = False
                if self._category_options[cat].get('type', 'live') == 'live':
                    cat_enabled = self._category_options.get(cat, {}).get('enabled', True)
                if cat in self._dictchannels and cat_enabled:
                    cat_title = get_category_title(cat, self._category_options)
                    f.write('#SERVICE 1:64:0:0:0:0:0:0:0:0:\n')
                    f.write('#DESCRIPTION {}\n'.format(checkStr(cat_title)))
                    for x in self._dictchannels[cat]:
                        if x.get('enabled') or x['stream-name'].startswith('placeholder_'):
                            self._save_bouquet_entry(f, x)
                        channel_num += 1

                    while channel_num % 100 != 0:
                        f.write('{}\n'.format(PLACEHOLDER_SERVICE))
                        channel_num += 1

        bouquet_indexes.append(self._get_bouquet_index_name(cat_filename, provider_filename))
        self._update_status('all channels bouquet created ...')
        print(Status.message)
        return bouquet_indexes

    def _create_epgimport_source(self, sources, group = None):
        """Create epg-importer source file
        """
        indent = '  '
        provider_safe_filename = self._get_safe_provider_filename()
        source_name = '{} - {}'.format(provider_safe_filename, group) if group else provider_safe_filename
        channels_filename = os.path.join(EPGIMPORTPATH, 'suls_iptv_{}_channels.xml'.format(provider_safe_filename))
        source_filename = os.path.join(EPGIMPORTPATH, 'suls_iptv_{}.sources.xml'.format(get_safe_filename(source_name)))
        with open(os.path.join(EPGIMPORTPATH, source_filename), 'w+') as f:
            f.write('<sources>\n')
            f.write('{}<sourcecat sourcecatname="C Forever">\n'.format(indent))
            f.write('{}<source type="gen_xmltv" nocheck="1" channels="{}">\n'.format(2 * indent, channels_filename))
            f.write('{}<description>{}</description>\n'.format(3 * indent, xml_escape(checkStr(source_name))))
            for source in sources:
                f.write('{}<url><![CDATA[{}]]></url>\n'.format(3 * indent, source))

            f.write('{}</source>\n'.format(2 * indent))
            f.write('{}</sourcecat>\n'.format(indent))
            f.write('</sources>\n')

    def _get_category_id(self, cat):
        """Generate 32 bit category id to help make service refs unique"""
        return hashlib.md5(self.config.name.encode('utf-8') + cat.encode('utf-8')).hexdigest()[:8]

    def _has_m3u_file(self):
        return self._m3u_file is not None

    def _extract_user_details_from_url(self):
        """Extract username & password from m3u_url """
        if self.config.m3u_url:
            parsed = urlparse(self.config.m3u_url)
            username_param = parse_qs(parsed.query).get('username')
            if username_param:
                self.config.username = username_param[0]
            password_param = parse_qs(parsed.query).get('password')
            if password_param:
                self.config.password = password_param[0]

    def _update_status(self, message):
        Status.message = '{}: {}'.format(checkStr(self.config.name), message)

    def _process_provider_update(self):
        """Download provider update file from url"""
        downloaded = False
        updated = False
        path = tempfile.gettempdir()
        filename = os.path.join(path, 'provider-{}-update.txt'.format(self.config.name))
        self._update_status('----Downloading providers update file----')
        print('\n{}'.format(Status.message))
        print('provider update url = ', self.config.provider_update_url)
        try:
            context = ssl._create_unverified_context()
            urlretrieve(self.config.provider_update_url, filename, context=context)
            downloaded = True
        except Exception:
            pass

        if not downloaded:
            try:
                urlretrieve(self.config.provider_update_url, filename)
            except Exception as e:
                print('[e2m3u2b] process_provider_update error. Type:', type(e))
                print('[e2m3u2b] process_provider_update error: ', e)

        if os.path.isfile(filename):
            try:
                with open(filename, 'r') as f:
                    line = f.readline().strip()
                if line:
                    provider_tmp = {'name': line.split(',')[0],
                     'm3u': line.split(',')[1],
                     'epg': line.split(',')[2]}
                    if provider_tmp.get('name') and provider_tmp.get('m3u'):
                        self.config.name = provider_tmp['name']
                        self.config.m3u_url = provider_tmp['m3u']
                        self.config.epg_url = provider_tmp.get('epg', self.config.epg_url)
                        self.config.last_provider_update = int(time.time())
                        updated = True
            except IndexError as e:
                print('[e2m3u2b] _process_provider_update error unable to read providers update file')

            if not DEBUG:
                os.remove(filename)
        return updated

    def _get_safe_provider_filename(self):
        return get_safe_filename(self.config.name, 'provider{}'.format(self.config.num))

    def process_provider(self):
        Status.is_running = True
        if self.config.epg_url is None:
            self.config.epg_url = 'http://www.vuplus-community.net/rytec/rytecxmltv-UK.gz'
        if self.config.icon_path is None or TESTRUN == 1:
            self.config.icon_path = PICONSPATH
        if self.config.name is None:
            self.config.name = 'E2m3u2Bouquet'
        if self.config.username is None or self.config.password is None:
            self._extract_user_details_from_url()
        self.config.m3u_url = self.config.m3u_url.replace('USERNAME', quote_plus(self.config.username)).replace('PASSWORD', quote_plus(self.config.password))
        self.config.epg_url = self.config.epg_url.replace('USERNAME', quote_plus(self.config.username)).replace('PASSWORD', quote_plus(self.config.password))
        if self.config.bouquet_download and self.config.bouquet_url:
            self.config.bouquet_url = self.config.bouquet_url.replace('USERNAME', quote_plus(self.config.username)).replace('PASSWORD', quote_plus(self.config.password))
        if self.config.bouquet_download and not self.config.bouquet_url:
            pos = self.config.m3u_url.find('get.php')
            if pos != -1:
                self.config.bouquet_url = self.config.m3u_url[0:pos + 7] + '?username={}&password={}&type=dreambox&output=ts'.format(quote_plus(self.config.username), quote_plus(self.config.password))
        if self.config.bouquet_url:
            self.download_panel_bouquet()
        self.download_m3u()
        if self._has_m3u_file():
            self.parse_m3u()
        if self._dictchannels:
            self.parse_data()
            self.parse_map_xmltvsources_xml()
            self.save_map_xml()
            if self.config.picons:
                self.download_picons()
            self.create_bouquets()
            self._update_status('----Creating EPG-Importer config ----')
            print('\n{}'.format(Status.message))
            self.create_epgimporter_config()
            self._update_status('EPG-Importer config created...')
            print(Status.message)
        Status.is_running = False
        return

    def provider_update(self):
        if self.config.provider_update_url and self.config.username and self.config.password:
            return self._process_provider_update()
        return False

    def download_m3u(self):
        """Download m3u file from url"""
        path = tempfile.gettempdir()
        filename = os.path.join(path, 'e2m3u2bouquet.m3u')
        self._update_status('----Downloading m3u file----')
        print('\n{}'.format(Status.message))
        if DEBUG:
            print('m3uurl = {}'.format(self.config.m3u_url))
        try:
            urlretrieve(self.config.m3u_url, filename)
        except Exception as e:
            self._update_status('Unable to download m3u file from url')
            print(Status.message)
            filename = None

        self._m3u_file = filename
        return

    def parse_m3u(self):
        """core parsing routine"""
        self._update_status('----Parsing m3u file----')
        print('\n{}'.format(Status.message))
        try:
            if not os.path.getsize(self._m3u_file):
                msg = 'M3U file is empty. Check username & password'
                print(msg)
                if DEBUG:
                    raise Exception(msg)
        except Exception as e:
            print(e)
            if DEBUG:
                raise

        service_dict = {}
        valid_services_found = False
        service_valid = False
        with open(self._m3u_file, 'r') as f:
            for line in f:
                try:
                    checkStr(line)
                except UnicodeDecodeError:
                    line = line.decode('ascii', 'ignore').encode('ascii')

                if 'EXTM3U' in line or line.startswith('#') and not line.startswith('#EXTINF'):
                    continue
                elif 'EXTINF:' in line:
                    service_valid = False
                    service_dict = {'tvg-id': '',
                     'tvg-name': '',
                     'tvg-logo': '',
                     'group-title': '',
                     'stream-name': '',
                     'category_type': 'live',
                     'has_archive': False,
                     'stream-url': '',
                     'enabled': True,
                     'nameOverride': '',
                     'categoryOverride': '',
                     'serviceRef': '',
                     'serviceRefOverride': False}
                    if line.find('tvg-') == -1 and line.find('group-') == -1:
                        if DEBUG:
                            msg = "No extended playlist info found for this service'"
                            print(msg)
                        continue
                    elif not valid_services_found:
                        valid_services_found = True
                    channel = line.split('"')
                    pos = channel[0].find(' ')
                    channel[0] = channel[0][pos:]
                    for i in xrange(0, len(channel) - 2, 2):
                        service_dict[channel[i].lower().strip(' =')] = checkStr(channel[i + 1])

                    stream_name_pos = line.rfind('",')
                    if stream_name_pos != -1:
                        service_dict['stream-name'] = checkStr(line[stream_name_pos + 2:]).strip()
                    if service_dict['group-title'] == '':
                        service_dict['group-title'] = u'None'
                    service_valid = True
                elif ('http:' in line or 'https:' in line or 'rtmp:' in line or 'rtsp:' in line) and service_valid is True:
                    service_dict['stream-url'] = line.strip()
                    self._set_streamtypes_vodcats(service_dict)
                    if service_dict['group-title'] not in self._dictchannels:
                        self._dictchannels[service_dict['group-title']] = [service_dict]
                    else:
                        self._dictchannels[service_dict['group-title']].append(service_dict)

            if not valid_services_found:
                msg = "No extended playlist info found. Check m3u url should be 'type=m3u_plus'"
                print(msg)
                if DEBUG:
                    raise Exception(msg)
        if not DEBUG:
            if os.path.isfile(self._m3u_file):
                os.remove(self._m3u_file)

    def parse_data(self):
        sorted_categories = self._parse_map_bouquet_xml()
        self._category_order = self._dictchannels.keys()
        sorted_categories.extend(self._category_order)
        self._category_order = OrderedDict(((x, True) for x in sorted_categories)).keys()
        self._set_category_type()
        self._parse_map_channels_xml()
        for cat in self._category_order:
            num = 1
            if cat in self._dictchannels:
                for x in self._dictchannels[cat]:
                    cat_id = self._get_category_id(cat)
                    service_ref = '{:x}:{}:{}:0'.format(num, cat_id[:4], cat_id[4:])
                    if not x['stream-name'].startswith('placeholder_'):
                        if self._panel_bouquet and not x.get('serviceRefOverride'):
                            pos = x['stream-url'].rfind('/')
                            if pos != -1 and pos + 1 != len(x['stream-url']):
                                m3u_stream_file = x['stream-url'][pos + 1:]
                                if m3u_stream_file in self._panel_bouquet:
                                    x['serviceRef'] = '{}:{}'.format(x['stream-type'], self._panel_bouquet[m3u_stream_file])
                                    continue
                        if not x.get('serviceRefOverride'):
                            x['serviceRef'] = '{}:0:1:{}:0:0:0'.format(x['stream-type'], service_ref)
                        num += 1
                    else:
                        x['serviceRef'] = PLACEHOLDER_SERVICE

        vod_index = None
        if 'VOD' in self._category_order:
            vod_index = self._category_order.index('VOD')
        else:
            vod_index = len(self._category_order)
        if vod_index is not None:
            vod_categories = list((cat for cat in self._category_order if self._category_options[cat].get('type', 'live') == 'vod'))
            if len(vod_categories):
                self._category_order = [ x for x in self._category_order if x not in vod_categories ]
                self._category_order[vod_index:vod_index] = vod_categories
                try:
                    self._category_order.remove('VOD')
                except ValueError:
                    pass

        if DEBUG and TESTRUN:
            datafile = open(os.path.join(CFGPATH, 'channels.debug'), 'w+')
            for cat in self._category_order:
                if cat in self._dictchannels:
                    for line in self._dictchannels[cat]:
                        linevals = ''
                        for key, value in line.items():
                            if type(value) is bool:
                                linevals += str(value) + ':'
                            else:
                                linevals += checkStr(value) + ':'

                        datafile.write('{}\n'.format(linevals))

            datafile.close()
        self._update_status('Completed parsing data...')
        print(Status.message)
        return

    def download_panel_bouquet(self):
        """Download panel bouquet file from url
        """
        path = tempfile.gettempdir()
        filename = os.path.join(path, 'userbouquet.panel.tv')
        self._update_status('---Downloading providers bouquet file----')
        print('\n{}'.format(Status.message))
        if DEBUG:
            print('bouqueturl = {}'.format(self.config.bouquet_url))
        try:
            urlretrieve(self.config.bouquet_url, filename)
        except Exception as e:
            msg = 'Unable to download providers panel bouquet file'
            print(msg)
            if DEBUG:
                raise msg

        self._panel_bouquet_file = filename
        self._parse_panel_bouquet()

    def download_picons(self):
        self._update_status('----Downloading Picon files, please be patient----')
        print('\n{}'.format(Status.message))
        print('If no Picons exist this will take a few minutes')
        try:
            os.makedirs(self.config.icon_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        for cat in self._dictchannels:
            if self._category_options[cat].get('type', 'live') == 'live':
                for x in self._dictchannels[cat]:
                    if not x['stream-name'].startswith('placeholder_'):
                        self._download_picon_file(x)

        self._update_status('Picons download completed...')
        print('\n{}'.format(Status.message))
        print('Box will need restarted for Picons to show...')

    def parse_map_xmltvsources_xml(self):
        """Check for a mapping override file and parses it if found
        """
        self._xmltv_sources_list = {}
        mapping_file = self._get_mapping_file()
        if mapping_file:
            try:
                tree = ET.ElementTree(file=mapping_file)
                for group in tree.findall('.//xmltvextrasources/group'):
                    group_name = group.attrib.get('id')
                    urllist = []
                    for url in group:
                        urllist.append(url.text)

                    self._xmltv_sources_list[group_name] = urllist

            except Exception as e:
                msg = 'Corrupt override.xml file'
                print(msg)
                if DEBUG:
                    raise msg

    def save_map_xml(self):
        """Create mapping file"""
        mappingfile = os.path.join(CFGPATH, self._get_safe_provider_filename() + '-sort-current.xml')
        indent = '  '
        vod_category_output = False
        if self._dictchannels:
            with open(mappingfile, 'w') as f:
                f.write('<!--\r\n')
                f.write('{} E2m3u2bouquet Custom mapping file\r\n'.format(indent))
                f.write('{} Rearrange bouquets or channels in the order you wish\r\n'.format(indent))
                f.write('{} Disable bouquets or channels by setting enabled to "false"\r\n'.format(indent))
                f.write('{} Map DVB EPG to IPTV by changing channel serviceRef attribute to match DVB service reference\r\n'.format(indent))
                f.write('{} Map XML EPG to different feed by changing channel tvg-id attribute\r\n'.format(indent))
                f.write('{} Rename this file as {}-sort-override.xml for changes to apply\r\n'.format(indent, self._get_safe_provider_filename()))
                f.write('-->\r\n')
                f.write('<mapping>\r\n')
                f.write('{}<xmltvextrasources>\r\n'.format(indent))
                if not self._xmltv_sources_list:
                    f.write('{}<!-- Example Config\r\n'.format(2 * indent))
                    f.write('{}<group id="{}">\r\n'.format(2 * indent, 'UK - Freeview (xz)'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://www.xmltvepg.nl/rytecUK_Basic.xz'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://rytecepg.ipservers.eu/epg_data/rytecUK_Basic.xz'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://rytecepg.wanwizard.eu/rytecUK_Basic.xz'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://91.121.106.172/~rytecepg/epg_data/rytecUK_Basic.xz'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://www.vuplus-community.net/rytec/rytecUK_Basic.xz'))
                    f.write('{}</group>\r\n'.format(2 * indent))
                    f.write('{}<group id="{}">\r\n'.format(2 * indent, 'UK - FTA (xz)'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://www.xmltvepg.nl/rytecUK_FTA.xz'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://rytecepg.ipservers.eu/epg_data/rytecUK_FTA.xz'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://rytecepg.wanwizard.eu/rytecUK_FTA.xz'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://91.121.106.172/~rytecepg/epg_data/rytecUK_FTA.xz'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://www.vuplus-community.net/rytec/rytecUK_FTA.xz'))
                    f.write('{}</group>\r\n'.format(2 * indent))
                    f.write('{}<group id="{}">\r\n'.format(2 * indent, 'UK - International (xz)'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://www.xmltvepg.nl/rytecUK_int.xz'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://rytecepg.ipservers.eu/epg_data/rytecUK_int.xz'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://rytecepg.wanwizard.eu/rytecUK_int.xz'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://91.121.106.172/~rytecepg/epg_data/rytecUK_int.xz'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://www.vuplus-community.net/rytec/rytecUK_int.xz'))
                    f.write('{}</group>\r\n'.format(2 * indent))
                    f.write('{}<group id="{}">\r\n'.format(2 * indent, 'UK - Sky Live (xz)'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://www.xmltvepg.nl/rytecUK_SkyLive.xz'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://rytecepg.ipservers.eu/epg_data/rytecUK_SkyLive.xz'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://rytecepg.wanwizard.eu/rytecUK_SkyLive.xz'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://91.121.106.172/~rytecepg/epg_data/rytecUK_SkyLive.xz'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://www.vuplus-community.net/rytec/rytecUK_SkyLive.xz'))
                    f.write('{}</group>\r\n'.format(2 * indent))
                    f.write('{}<group id="{}">\r\n'.format(2 * indent, 'UK - Sky Dead (xz)'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://www.xmltvepg.nl/rytecUK_SkyDead.xz'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://rytecepg.ipservers.eu/epg_data/rytecUK_SkyDead.xz'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://rytecepg.wanwizard.eu/rytecUK_SkyDead.xz'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://91.121.106.172/~rytecepg/epg_data/rytecUK_SkyDead.xz'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://www.vuplus-community.net/rytec/rytecUK_SkyDead.xz'))
                    f.write('{}</group>\r\n'.format(2 * indent))
                    f.write('{}<group id="{}">\r\n'.format(2 * indent, 'UK - Sports/Movies (xz)'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://www.xmltvepg.nl/rytecUK_SportMovies.xz'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://rytecepg.ipservers.eu/epg_data/rytecUK_SportMovies.xz'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://rytecepg.wanwizard.eu/rytecUK_SportMovies.xz'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://91.121.106.172/~rytecepg/epg_data/rytecUK_SportMovies.xz'))
                    f.write('{}<url>{}</url>\r\n'.format(3 * indent, 'http://www.vuplus-community.net/rytec/rytecUK_SportMovies.xz'))
                    f.write('{}</group>\r\n'.format(2 * indent))
                    f.write('{}-->\r\n'.format(2 * indent))
                else:
                    for group in self._xmltv_sources_list:
                        f.write('{}<group id="{}">\r\n'.format(2 * indent, xml_escape(group)))
                        for source in self._xmltv_sources_list[group]:
                            f.write('{}<url>{}</url>\r\n'.format(3 * indent, xml_escape(source)))

                        f.write('{}</group>\r\n'.format(2 * indent))

                f.write('{}</xmltvextrasources>\r\n'.format(indent))
                f.write('{}<categories>\r\n'.format(indent))
                for cat in self._category_order:
                    if cat in self._dictchannels:
                        if self._category_options[cat].get('type', 'live') == 'live':
                            cat_title_override = self._category_options[cat].get('nameOverride', '')
                            f.write('{}<category name="{}" nameOverride="{}" enabled="{}" customCategory="{}"/>\r\n'.format(2 * indent, xml_escape(checkStr(cat)), xml_escape(checkStr(cat_title_override)), str(self._category_options[cat].get('enabled', True)).lower(), str(self._category_options[cat].get('customCategory', False)).lower()))
                        elif not vod_category_output:
                            cat_title_override = ''
                            cat_enabled = True
                            if 'VOD' in self._category_options:
                                cat_title_override = self._category_options['VOD'].get('nameOverride', '')
                                cat_enabled = self._category_options['VOD'].get('enabled', True)
                            f.write('{}<category name="{}" nameOverride="{}" enabled="{}" />\r\n'.format(2 * indent, 'VOD', xml_escape(checkStr(cat_title_override)), str(cat_enabled).lower()))
                            vod_category_output = True

                f.write('{}</categories>\r\n'.format(indent))
                f.write('{}<channels>\r\n'.format(indent))
                for cat in self._category_order:
                    if cat in self._dictchannels:
                        if self._category_options[cat].get('type', 'live') == 'live':
                            f.write('{}<!-- {} -->\r\n'.format(2 * indent, xml_safe_comment(xml_escape(checkStr(cat)))))
                            for x in self._dictchannels[cat]:
                                if not x['stream-name'].startswith('placeholder_'):
                                    f.write('{}<channel name="{}" nameOverride="{}" tvg-id="{}" enabled="{}" category="{}" categoryOverride="{}" serviceRef="{}" clearStreamUrl="{}" />\r\n'.format(2 * indent, xml_escape(checkStr(x['stream-name'])), xml_escape(checkStr(x.get('nameOverride', ''))), xml_escape(checkStr(x['tvg-id'])), str(x['enabled']).lower(), xml_escape(checkStr(x['group-title'])), xml_escape(checkStr(x.get('categoryOverride', ''))), xml_escape(x['serviceRef']), 'false' if x['stream-url'] else 'true'))
                                else:
                                    f.write('{}<channel name="{}" category="{}" />\r\n'.format(2 * indent, 'placeholder', xml_escape(checkStr(cat))))

                f.write('{}</channels>\r\n'.format(indent))
                f.write('</mapping>')

    def create_bouquets(self):
        """Create the Enigma2 bouquets
        """
        self._update_status('----Creating bouquets----')
        print('\n{}'.format(Status.message))
        if self._dictchannels:
            for fname in os.listdir(ENIGMAPATH):
                if 'userbouquet.suls_iptv_{}'.format(self._get_safe_provider_filename()) in fname:
                    os.remove(os.path.join(ENIGMAPATH, fname))

        iptv_bouquet_list = []
        if self.config.all_bouquet:
            iptv_bouquet_list = self._create_all_channels_bouquet()
        vod_categories = list((cat for cat in self._category_order if self._category_options[cat].get('type', 'live') == 'vod'))
        vod_category_output = False
        vod_bouquet_entry_output = False
        channel_number_start_offset_output = False
        cat_num = 0
        for cat in self._category_order:
            if self._category_options[cat].get('type', 'live') == 'live':
                cat_enabled = self._category_options.get(cat, {}).get('enabled', True)
            else:
                cat_enabled = self._category_options.get('VOD', {}).get('enabled', True)
            if cat in self._dictchannels and cat_enabled:
                cat_title = get_category_title(cat, self._category_options)
                cat_filename = get_safe_filename(cat_title, 'cat{}'.format(cat_num))
                provider_filename = self._get_safe_provider_filename()
                if cat in vod_categories and not self.config.multi_vod:
                    cat_filename = 'VOD'
                bouquet_filepath = os.path.join(ENIGMAPATH, 'userbouquet.suls_iptv_{}_{}.tv'.format(provider_filename, cat_filename))
                if DEBUG:
                    print('Creating: {}'.format(bouquet_filepath))
                if cat not in vod_categories or self.config.multi_vod:
                    with open(bouquet_filepath, 'w+') as f:
                        bouquet_name = '{} - {}'.format(checkStr(self.config.name), checkStr(cat_title))
                        if self._category_options[cat].get('type', 'live') == 'live':
                            if cat in self._category_options and self._category_options[cat].get('nameOverride', False):
                                bouquet_name = checkStr(self._category_options[cat]['nameOverride'])
                        elif 'VOD' in self._category_options and self._category_options['VOD'].get('nameOverride', False):
                            bouquet_name = '{} - {}'.format(checkStr(self._category_options['VOD']['nameOverride']), checkStr(cat_title).replace('VOD - ', ''))
                        channel_num = 0
                        f.write('#NAME {}\n'.format(checkStr(bouquet_name)))
                        if not channel_number_start_offset_output and not self.config.all_bouquet:
                            for i in xrange(100):
                                f.write('{}\n'.format(PLACEHOLDER_SERVICE))

                            channel_number_start_offset_output = True
                            channel_num += 1
                        for x in self._dictchannels[cat]:
                            if x.get('enabled') or x['stream-name'].startswith('placeholder_'):
                                self._save_bouquet_entry(f, x)
                            channel_num += 1

                        while channel_num % 100 != 0:
                            f.write('{}\n'.format(PLACEHOLDER_SERVICE))
                            channel_num += 1

                elif not vod_category_output and not self.config.multi_vod:
                    with open(bouquet_filepath, 'w+') as f:
                        bouquet_name = '{} - VOD'.format(checkStr(self.config.name))
                        if 'VOD' in self._category_options and self._category_options['VOD'].get('nameOverride', False):
                            bouquet_name = checkStr(self._category_options['VOD']['nameOverride'])
                        channel_num = 0
                        f.write('#NAME {}\n'.format(checkStr(bouquet_name)))
                        if not channel_number_start_offset_output and not self.config.all_bouquet:
                            for i in xrange(100):
                                f.write('{}\n'.format(PLACEHOLDER_SERVICE))

                            channel_number_start_offset_output = True
                            channel_num += 1
                        for vodcat in vod_categories:
                            if vodcat in self._dictchannels:
                                f.write('#SERVICE 1:64:0:0:0:0:0:0:0:0:\n')
                                f.write('#DESCRIPTION {}\n'.format(checkStr(vodcat)))
                                for x in self._dictchannels[vodcat]:
                                    self._save_bouquet_entry(f, x)
                                    channel_num += 1

                                while channel_num % 100 != 0:
                                    f.write('{}\n'.format(PLACEHOLDER_SERVICE))
                                    channel_num += 1

                        vod_category_output = True
                if cat not in vod_categories or cat in vod_categories and not vod_bouquet_entry_output:
                    iptv_bouquet_list.append(self._get_bouquet_index_name(cat_filename, provider_filename))
                    if cat in vod_categories and not self.config.multi_vod:
                        vod_bouquet_entry_output = True
            cat_num += 1

        self._save_bouquet_index_entries(iptv_bouquet_list)
        self._update_status('bouquets created ...')
        print(Status.message)

    def create_epgimporter_config(self):
        indent = '  '
        if DEBUG:
            print('creating EPGImporter config')
        try:
            os.makedirs(EPGIMPORTPATH)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        channels_filename = os.path.join(EPGIMPORTPATH, 'suls_iptv_{}_channels.xml'.format(self._get_safe_provider_filename()))
        if self._dictchannels:
            with open(channels_filename, 'w+') as f:
                f.write('<channels>\n')
                for cat in self._category_order:
                    if cat in self._dictchannels and self._category_options.get(cat, {}).get('enabled', True):
                        if self._category_options[cat].get('type', 'live') == 'live':
                            cat_title = get_category_title(cat, self._category_options)
                            f.write('{}<!-- {} -->\n'.format(indent, xml_safe_comment(xml_escape(checkStr(cat_title)))))
                            for x in self._dictchannels[cat]:
                                if not x['stream-name'].startswith('placeholder_'):
                                    tvg_id = x['tvg-id'] if x['tvg-id'] else get_service_title(x)
                                    if x['enabled']:
                                        epg_service_ref = x['serviceRef']
                                        pos = epg_service_ref.find(':')
                                        if pos != -1:
                                            epg_service_ref = '1{}'.format(epg_service_ref[pos:])
                                        f.write('{}<channel id="{}">{}:http%3a//example.m3u8</channel> <!-- {} -->\n'.format(indent, xml_escape(checkStr(tvg_id)), epg_service_ref, xml_safe_comment(xml_escape(checkStr(get_service_title(x))))))

                f.write('</channels>\n')
            self._create_epgimport_source([self.config.epg_url])
            for group in self._xmltv_sources_list:
                self._create_epgimport_source(self._xmltv_sources_list[group], group)


class Config():

    def __init__(self):
        self.providers = OrderedDict()

    def make_default_config(self, configfile):
        print('Default configuration file created in {}\n'.format(os.path.join(CFGPATH, 'config.xml')))
        f = open(configfile, 'wb')
        f.write('<!--\r\n    E2m3u2bouquet supplier config file\r\n    Add as many suppliers as required and run the script with no parameters\r\n    this config file will be used and the relevant bouquets set up for all suppliers entered\r\n    0 = No/false\r\n    1 = Yes/true\r\n    For elements with <![CDATA[]] enter value between brackets e.g. <![CDATA[mypassword]]>\r\n-->\r\n<config>\r\n    <supplier>\r\n        <name>Supplier Name 1</name><!-- Supplier Name -->\r\n        <enabled>1</enabled><!-- Enable or disable the supplier (0 or 1) -->\r\n        <m3uurl><![CDATA[http://address.yourprovider.com:80/get.php?username=USERNAME&password=PASSWORD&type=m3u_plus&output=ts]]></m3uurl><!-- Extended M3U url -->\r\n        <epgurl><![CDATA[http://address.yourprovider.com:80/xmltv.php?username=USERNAME&password=PASSWORD]]></epgurl><!-- XMLTV EPG url -->\r\n        <username><![CDATA[]]></username><!-- (Optional) will replace USERNAME placeholder in urls -->\r\n        <password><![CDATA[]]></password><!-- (Optional) will replace PASSWORD placeholder in urls -->\r\n        <iptvtypes>0</iptvtypes><!-- Change all streams to IPTV type (0 or 1) -->\r\n        <streamtypetv></streamtypetv><!-- (Optional) Custom TV stream type (e.g. 1, 4097, 5001 or 5002) -->\r\n        <streamtypevod></streamtypevod><!-- (Optional) Custom VOD stream type (e.g. 4097, 5001 or 5002) -->\r\n        <multivod>0</multivod><!-- Split VOD into seperate categories (0 or 1) -->\r\n        <allbouquet>1</allbouquet><!-- Create all channels bouquet -->\r\n        <picons>0</picons><!-- Automatically download Picons (0 or 1) -->\r\n        <iconpath>/usr/share/enigma2/picon/</iconpath><!-- Location to store picons -->\r\n        <xcludesref>1</xcludesref><!-- Disable service ref overriding from override.xml file (0 or 1) -->\r\n        <bouqueturl><![CDATA[]]></bouqueturl><!-- (Optional) url to download providers bouquet - to map custom service references -->\r\n        <bouquetdownload>0</bouquetdownload><!-- Download providers bouquet (use default url) must have username and password set above - to map custom service references -->\r\n        <bouquettop>0</bouquettop><!-- Place IPTV bouquets at top (0 or 1)-->\r\n    </supplier>\r\n    <supplier>\r\n        <name>Supplier Name</name><!-- Supplier Name -->\r\n        <enabled>0</enabled><!-- Enable or disable the supplier (0 or 1) -->\r\n        <m3uurl><![CDATA[http://address.yourprovider.com:80/get.php?username=USERNAME&password=PASSWORD&type=m3u_plus&output=ts]]></m3uurl><!-- Extended M3U url -->\r\n        <epgurl><![CDATA[http://address.yourprovider.com:80/xmltv.php?username=USERNAME&password=PASSWORD]]></epgurl><!-- XMLTV EPG url -->\r\n        <username><![CDATA[]]></username><!-- (Optional) will replace USERNAME placeholder in urls -->\r\n        <password><![CDATA[]]></password><!-- (Optional) will replace PASSWORD placeholder in urls -->\r\n        <iptvtypes>0</iptvtypes><!-- Change all streams to IPTV type (0 or 1) -->\r\n        <streamtypetv></streamtypetv><!-- (Optional) Custom TV service type (e.g. 1, 4097, 5001 or 5002) -->\r\n        <streamtypevod></streamtypevod><!-- (Optional) Custom VOD service type (e.g. 4097, 5001 or 5002) -->\r\n        <multivod>0</multivod><!-- Split VOD into seperate categories (0 or 1) -->\r\n        <allbouquet>1</allbouquet><!-- Create all channels bouquet -->\r\n        <picons>0</picons><!-- Automatically download Picons (0 or 1) -->\r\n        <iconpath>/usr/share/enigma2/picon/</iconpath><!-- Location to store picons -->\r\n        <xcludesref>1</xcludesref><!-- Disable service ref overriding from override.xml file (0 or 1) -->\r\n        <bouqueturl><![CDATA[]]></bouqueturl><!-- (Optional) url to download providers bouquet - to map custom service references -->\r\n        <bouquetdownload>0</bouquetdownload><!-- Download providers bouquet (use default url) must have username and password set above - to map custom service references -->\r\n        <bouquettop>0</bouquettop><!-- Place IPTV bouquets at top (0 or 1)--> \r\n    </supplier>\r\n</config>')

    def read_config(self, configfile):
        """ Read Config from file """
        self.providers = OrderedDict()
        try:
            tree = ET.ElementTree(file=configfile)
            provider_num = 0
            for node in tree.findall('.//supplier'):
                provider = ProviderConfig()
                if node is not None:
                    for child in node:
                        if child.tag == 'name':
                            provider.name = '' if child.text is None else child.text.strip()
                        if child.tag == 'enabled':
                            provider.enabled = True if child.text == '1' else False
                        if child.tag == 'settingslevel':
                            provider.settings_level = '' if child.text is None else child.text.strip()
                        if child.tag == 'm3uurl':
                            provider.m3u_url = '' if child.text is None else child.text.strip()
                        if child.tag == 'epgurl':
                            provider.epg_url = '' if child.text is None else child.text.strip()
                        if child.tag == 'username':
                            provider.username = '' if child.text is None else child.text.strip()
                        if child.tag == 'password':
                            provider.password = '' if child.text is None else child.text.strip()
                        if child.tag == 'providerupdate':
                            provider.provider_update_url = '' if child.text is None else child.text.strip()
                        if child.tag == 'providerhideurls':
                            provider.provider_hide_urls = True if child.text == '1' else False
                        if child.tag == 'iptvtypes':
                            provider.iptv_types = True if child.text == '1' else False
                        if child.tag == 'streamtypetv':
                            provider.streamtype_tv = '' if child.text is None else child.text.strip()
                        if child.tag == 'streamtypevod':
                            provider.streamtype_vod = '' if child.text is None else child.text.strip()
                        if child.tag == 'multivod':
                            provider.multi_vod = True if child.text == '1' else False
                        if child.tag == 'allbouquet':
                            provider.all_bouquet = True if child.text == '1' else False
                        if child.tag == 'picons':
                            provider.picons = True if child.text == '1' else False
                        if child.tag == 'iconpath':
                            provider.icon_path = '' if child.text is None else child.text.strip()
                        if child.tag == 'xcludesref':
                            provider.sref_override = True if child.text == '0' else False
                        if child.tag == 'bouqueturl':
                            provider.bouquet_url = '' if child.text is None else child.text.strip()
                        if child.tag == 'bouquetdownload':
                            provider.bouquet_download = True if child.text == '1' else False
                        if child.tag == 'bouquettop':
                            provider.bouquet_top = True if child.text == '1' else False
                        if child.tag == 'lastproviderupdate':
                            provider.last_provider_update = 0 if child.text is None else child.text.strip()
                        provider.num = provider_num

                if provider.name:
                    self.providers[provider.name] = provider
                    provider_num += 1

        except Exception as e:
            msg = 'Corrupt config.xml file'
            print(msg)
            if DEBUG:
                raise Exception(msg)

        return

    def write_config(self):
        """Write providers to config file
        Manually write instead of using ElementTree so that we can format the file for easy human editing
        (inc. Windows line endings)
        """
        config_file = os.path.join(os.path.join(CFGPATH, 'config.xml'))
        indent = '  '
        if self.providers:
            with open(config_file, 'wb') as f:
                f.write('<!--\r\n')
                f.write('{}E2m3u2bouquet supplier config file\r\n'.format(indent))
                f.write('{}Add as many suppliers as required\r\n'.format(indent))
                f.write('{}this config file will be used and the relevant bouquets set up for all suppliers entered\r\n'.format(indent))
                f.write('{}0 = No/False\r\n'.format(indent))
                f.write('{}1 = Yes/True\r\n'.format(indent))
                f.write('{}For elements with <![CDATA[]] enter value between empty brackets e.g. <![CDATA[mypassword]]>\r\n'.format(indent))
                f.write('-->\r\n')
                f.write('<config>\r\n')
                for key, provider in self.providers.items():
                    f.write('{}<supplier>\r\n'.format(indent))
                    f.write('{}<name>{}</name><!-- Supplier Name -->\r\n'.format(2 * indent, xml_escape(provider.name)))
                    f.write('{}<enabled>{}</enabled><!-- Enable or disable the supplier (0 or 1) -->\r\n'.format(2 * indent, '1' if provider.enabled else '0'))
                    f.write('{}<settingslevel>{}</settingslevel>\r\n'.format(2 * indent, provider.settings_level))
                    f.write('{}<m3uurl><![CDATA[{}]]></m3uurl><!-- Extended M3U url --> \r\n'.format(2 * indent, provider.m3u_url))
                    f.write('{}<epgurl><![CDATA[{}]]></epgurl><!-- XMLTV EPG url -->\r\n'.format(2 * indent, provider.epg_url))
                    f.write('{}<username><![CDATA[{}]]></username><!-- (Optional) will replace USERNAME placeholder in urls -->\r\n'.format(2 * indent, provider.username))
                    f.write('{}<password><![CDATA[{}]]></password><!-- (Optional) will replace PASSWORD placeholder in urls -->\r\n'.format(2 * indent, provider.password))
                    f.write('{}<providerupdate><![CDATA[{}]]></providerupdate><!-- (Optional) Provider update url -->\r\n'.format(2 * indent, provider.provider_update_url))
                    f.write('{}<providerhideurls>{}</providerhideurls><!-- (Optional) Hide Provider urls in plugin -->\r\n'.format(2 * indent, '1' if provider.provider_hide_urls else '0'))
                    f.write('{}<iptvtypes>{}</iptvtypes><!-- Change all TV streams to IPTV type (0 or 1) -->\r\n'.format(2 * indent, '1' if provider.iptv_types else '0'))
                    f.write('{}<streamtypetv>{}</streamtypetv><!-- (Optional) Custom TV stream type (e.g. 1, 4097, 5001 or 5002 -->\r\n'.format(2 * indent, provider.streamtype_tv))
                    f.write('{}<streamtypevod>{}</streamtypevod><!-- (Optional) Custom VOD stream type (e.g. 4097, 5001 or 5002 -->\r\n'.format(2 * indent, provider.streamtype_vod))
                    f.write('{}<multivod>{}</multivod><!-- Split VOD into seperate categories (0 or 1) -->\r\n'.format(2 * indent, '1' if provider.multi_vod else '0'))
                    f.write('{}<allbouquet>{}</allbouquet><!-- Create all channels bouquet (0 or 1) -->\r\n'.format(2 * indent, '1' if provider.all_bouquet else '0'))
                    f.write('{}<picons>{}</picons><!-- Automatically download Picons (0 or 1) -->\r\n'.format(2 * indent, '1' if provider.picons else '0'))
                    f.write('{}<iconpath>{}</iconpath><!-- Location to store picons) -->\r\n'.format(2 * indent, provider.icon_path if provider.icon_path else ''))
                    f.write('{}<xcludesref>{}</xcludesref><!-- Disable service ref overriding from override.xml file (0 or 1) -->\r\n'.format(2 * indent, '0' if provider.sref_override else '1'))
                    f.write('{}<bouqueturl><![CDATA[{}]]></bouqueturl><!-- (Optional) url to download providers bouquet - to map custom service references -->\r\n'.format(2 * indent, provider.bouquet_url))
                    f.write('{}<bouquetdownload>{}</bouquetdownload><!-- Download providers bouquet (uses default url) must have username and password set above - to map custom service references -->\r\n'.format(2 * indent, '1' if provider.bouquet_download else '0'))
                    f.write('{}<bouquettop>{}</bouquettop><!-- Place IPTV bouquets at top (0 or 1) -->\r\n'.format(2 * indent, '1' if provider.bouquet_top else '0'))
                    f.write('{}<lastproviderupdate>{}</lastproviderupdate><!-- Internal use -->\r\n'.format(2 * indent, provider.last_provider_update))
                    f.write('{}</supplier>\r\n'.format(indent))

                f.write('</config>\r\n')
        elif os.path.isfile(os.path.join(CFGPATH, 'config.xml')):
            print('no providers remove config')
            os.remove(os.path.join(CFGPATH, 'config.xml'))


def main(argv = None):
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)
    program_name = os.path.basename(sys.argv[0])
    program_version = 'v%s' % __version__
    program_build_date = str(__updated__)
    program_version_message = '%(prog)s {} ({})'.format(program_version, program_build_date)
    program_shortdesc = __doc__.split('\n')[1]
    program_license = '{}\n\n  Copyright 2017. All rights reserved.\n  Created on {}.\n  Licensed under GNU GENERAL PUBLIC LICENSE version 3\n  Distributed on an "AS IS" basis without warranties\n  or conditions of any kind, either express or implied.\n\nUSAGE\n'.format(program_shortdesc, str(__date__))
    try:
        parser = get_parser_args(program_license, program_version_message)
        args = parser.parse_args()
        uninstall = args.uninstall
        urllib._urlopener = AppUrlOpener()
        # if PY3:
            # urllib.request._urlopener = AppUrlOpener()
        # else:
            # urllib._urlopener = AppUrlOpener()
        socket.setdefaulttimeout(30)
        # display_welcome()
        if uninstall:
            uninstaller()
            reload_bouquets()
            print('Uninstall only, program exiting ...')
            sys.exit(1)
        else:
            make_config_folder()
        args_config = ProviderConfig()
        args_config.m3u_url = args.m3uurl
        args_config.epg_url = args.epgurl
        args_config.iptv_types = args.iptvtypes
        args_config.multi_vod = args.multivod
        args_config.all_bouquet = args.allbouquet
        args_config.bouquet_url = args.bouqueturl
        args_config.bouquet_download = args.bouquetdownload
        args_config.picons = args.picons
        args_config.icon_path = args.iconpath
        args_config.sref_override = not args.xcludesref
        args_config.bouquet_top = args.bouquettop
        args_config.name = args.providername
        args_config.username = args.username
        args_config.password = args.password
        args_config.streamtype_tv = args.sttv
        args_config.streamtype_vod = args.stvod
        if args_config.m3u_url:
            print('\n**************************************')
            print('E2m3u2bouquet - Command line based setup')
            print('**************************************\n')
            args_provider = Provider(args_config)
            args_provider.process_provider()
            reload_bouquets()
            display_end_msg()
        else:
            print('\n********************************')
            print('E2m3u2bouquet - Config based setup')
            print('********************************\n')
            e2m3u2b_config = Config()
            if os.path.isfile(os.path.join(CFGPATH, 'config.xml')):
                e2m3u2b_config.read_config(os.path.join(CFGPATH, 'config.xml'))
                providers_updated = False
                for key, provider_config in e2m3u2b_config.providers.items():
                    if provider_config.enabled:
                        if provider_config.name.startswith('Supplier Name'):
                            print('Please enter your details in the config file in - {}'.format(os.path.join(CFGPATH, 'config.xml')))
                            sys.exit(2)
                        else:
                            print('\n********************************')
                            print('Config based setup - {}'.format(checkStr(provider_config.name)))
                            print('********************************\n')
                            provider = Provider(provider_config)
                            if int(time.time()) - int(provider.config.last_provider_update) > 21600:
                                providers_updated = provider.provider_update()
                            provider.process_provider()
                    else:
                         print('\nProvider: {} is disabled - skipping.........\n'.format(provider_config.name))

                if providers_updated:
                    e2m3u2b_config.write_config()
                reload_bouquets()
                display_end_msg()
            else:
                e2m3u2b_config.make_default_config(os.path.join(CFGPATH, 'config.xml'))
                print('Please ensure correct command line options are passed to the program \nor populate the config file in {} \nfor help use --help\n'.format(os.path.join(CFGPATH, 'config.xml')))
                parser.print_usage()
                sys.exit(1)
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        if DEBUG:
            raise e
        indent = len(program_name) * ' '
        sys.stderr.write(program_name + ': ' + repr(e) + '\n')
        sys.stderr.write(indent + '  for help use --help')
        return 2

    return


if __name__ == '__main__':
    if TESTRUN:
        EPGIMPORTPATH = 'H:/Satelite Stuff/epgimport/'
        ENIGMAPATH = 'H:/Satelite Stuff/enigma2/'
        PICONSPATH = 'H:/Satelite Stuff/picons/'
        CFGPATH = os.path.join(ENIGMAPATH, 'e2m3u2bouquet/')
    sys.exit(main())
else:
    IMPORTED = True