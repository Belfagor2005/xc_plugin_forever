#!/bin/bash

## setup command=wget -q --no-check-certificate "https://raw.githubusercontent.com/Belfagor2005/xc_plugin_forever/main/installer.sh?inline=false" -O - | /bin/sh

## Only This 2 lines to edit with new version ######
version='4.9'
changelog='Fix DreamOs System'
##
TMPPATH=/tmp/XCplugin-main
FILEPATH=/tmp/main.tar.gz
OSTYPE=Dream
STATUS=/var/lib/opkg/status
if [ ! -d /usr/lib64 ]; then
    PLUGINPATH=/usr/lib/enigma2/python/Plugins/Extensions/XCplugin
else
    PLUGINPATH=/usr/lib64/enigma2/python/Plugins/Extensions/XCplugin
fi

## Remove tmp directory
[ -r $TMPPATH ] && rm -rf $TMPPATH > /dev/null 2>&1

## Remove tmp file
[ -r $FILEPATH ] && rm -f $FILEPATH > /dev/null 2>&1

## Remove old plugin directory
[ -r $PLUGINPATH ] && rm -rf $PLUGINPATH > /dev/null 2>&1

## check depends packges
if [ -f /var/lib/dpkg/status ]; then
    STATUS=/var/lib/dpkg/status
    OSTYPE=DreamOs
else
    STATUS=/var/lib/opkg/status
    OSTYPE=Dream
fi

echo ""
if [ -f /usr/bin/wget ]; then
    echo "wget exist"
else
    if [ $OSTYPE = "DreamOs" ]; then
        echo "Installing wget for DreamOS..."
        apt-get update && apt-get install wget -y
    else
        echo "Installing wget..."
        opkg update && opkg install wget
    fi
fi

if python --version 2>&1 | grep -q '^Python 3\.'; then
    echo "You have Python3 image"
    PYTHON=PY3
    Packagesix=python3-six
    Packagerequests=python3-requests
else
    echo "You have Python2 image"
    PYTHON=PY2
    Packagerequests=python-requests
fi

echo ""
if [ $PYTHON = "PY3" ]; then
    if ! grep -qs "Package: $Packagesix" $STATUS; then
        echo "Installing python3-six..."
        if [ $OSTYPE = "DreamOs" ]; then
            apt-get update && apt-get install python3-six -y
        else
            opkg update && opkg install python3-six
        fi
    fi
fi

echo ""
if ! grep -qs "Package: $Packagerequests" $STATUS; then
    echo "Installing $Packagerequests..."
    if [ $OSTYPE = "DreamOs" ]; then
        apt-get update && apt-get install $Packagerequests -y
    else
        opkg update && opkg install $Packagerequests
    fi
fi

## Download and install plugin
mkdir -p $TMPPATH
cd $TMPPATH
set -e

if [ $OSTYPE = "DreamOs" ]; then
    echo "# Your image is OE2.5/2.6 #"
else
    echo "# Your image is OE2.0 #"
    echo "Installing additional dependencies..."
    opkg update && opkg install ffmpeg gstplayer exteplayer3 enigma2-plugin-systemplugins-serviceapp
fi

echo "Downloading plugin..."
wget --no-check-certificate -O $FILEPATH 'https://github.com/Belfagor2005/xc_plugin_forever/archive/refs/heads/main.tar.gz'
tar -xzf $FILEPATH -C $TMPPATH
cp -r $TMPPATH/xc_plugin_forever-main/usr /
set +e

## Check if plugin installed correctly
if [ ! -d $PLUGINPATH ]; then
    echo "Error: Plugin not installed correctly!"
    rm -rf $TMPPATH > /dev/null 2>&1
    rm -f $FILEPATH > /dev/null 2>&1
    exit 1
fi

## Cleanup
rm -rf $TMPPATH > /dev/null 2>&1
rm -f $FILEPATH > /dev/null 2>&1
sync

## Show install info
FILE="/etc/image-version"
box_type=$(head -n 1 /etc/hostname 2>/dev/null)
distro_value=$(grep '^distro=' "$FILE" 2>/dev/null | awk -F '=' '{print $2}')
distro_version=$(grep '^version=' "$FILE" 2>/dev/null | awk -F '=' '{print $2}')
python_vers=$(python --version 2>&1)

echo "#########################################################
#               INSTALLED SUCCESSFULLY                  #
#                developed by LULULLA                   #
#               https://corvoboys.org                   #
#########################################################
#           your Device will RESTART Now                #
#########################################################
^^^^^^^^^^Debug information:
BOX MODEL: $box_type
OO SYSTEM: $OSTYPE
PYTHON: $python_vers
IMAGE NAME: $distro_value
IMAGE VERSION: $distro_version"

sleep 5
killall -9 enigma2
exit 0
