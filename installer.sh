#!/bin/bash

## setup command=wget -q --no-check-certificate "https://raw.githubusercontent.com/Belfagor2005/xc_plugin_forever/main/installer.sh?inline=false" -O - | /bin/sh

## Only This 2 lines to edit with new version ######
version='4.9'
changelog='Fix DreamOs System'

## Setup paths
TMPPATH=/tmp/XCplugin-main
FILEPATH=/tmp/main.tar.gz
PLUGINPATH=/usr/lib/enigma2/python/Plugins/Extensions/XCplugin
[ -d /usr/lib64 ] && PLUGINPATH=/usr/lib64/enigma2/python/Plugins/Extensions/XCplugin

## Cleanup previous runs
cleanup() {
    rm -rf "$TMPPATH" >/dev/null 2>&1
    rm -f "$FILEPATH" >/dev/null 2>&1
}
cleanup

## Determine system type
if [ -f /var/lib/dpkg/status ]; then
    STATUS=/var/lib/dpkg/status
    OSTYPE=DreamOs
else
    STATUS=/var/lib/opkg/status
    OSTYPE=Dream
fi

## Install required tools
install_requirements() {
    echo "Checking system requirements..."
    
    # Install wget if missing
    if ! command -v wget >/dev/null 2>&1; then
        echo "Installing wget..."
        if [ "$OSTYPE" = "DreamOs" ]; then
            apt-get update && apt-get install -y wget || return 1
        else
            opkg update && opkg install wget || return 1
        fi
    fi
    
    # Install Python dependencies
    PYTHON_VERSION=$(python -c "import sys; print(sys.version_info[0])" 2>/dev/null || echo "2")
    if [ "$PYTHON_VERSION" = "3" ]; then
        echo "Python 3 detected"
        Packagesix=python3-six
        Packagerequests=python3-requests
    else
        echo "Python 2 detected"
        Packagerequests=python-requests
    fi
    
    # Install requests package
    if ! grep -qs "Package: $Packagerequests" "$STATUS"; then
        echo "Installing $Packagerequests..."
        if [ "$OSTYPE" = "DreamOs" ]; then
            apt-get update && apt-get install -y "$Packagerequests" || return 1
        else
            opkg update && opkg install "$Packagerequests" || return 1
        fi
    fi
    
    # For OE2.0 systems install additional deps
    if [ "$OSTYPE" = "Dream" ]; then
        echo "Installing additional dependencies..."
        opkg update && opkg install ffmpeg gstplayer exteplayer3 enigma2-plugin-systemplugins-serviceapp || return 1
    fi
    
    return 0
}

## Download and install plugin
install_plugin() {
    echo "Downloading plugin..."
    
    GITHUB_URL="https://github.com/Belfagor2005/xc_plugin_forever/archive/main.tar.gz"
    
    if ! wget --no-check-certificate -O "$FILEPATH" "$GITHUB_URL"; then
        echo "Download failed!"
        return 1
    fi
    
    if [ ! -s "$FILEPATH" ]; then
        echo "Downloaded file is empty!"
        return 1
    fi
    
    echo "Extracting plugin..."
    mkdir -p "$TMPPATH" && cd "$TMPPATH" || return 1
    tar -xzf "$FILEPATH" || return 1
    
    echo "Installing files..."
    cp -r "$TMPPATH/xc_plugin_forever-main/usr" / || return 1
    
    return 0
}

## Main installation process
if install_requirements && install_plugin; then
    if [ -d "$PLUGINPATH" ]; then
        echo "#########################################################"
        echo "#               INSTALLED SUCCESSFULLY                  #"
        echo "#########################################################"
        
        echo "System Information:"
        echo "BOX MODEL: $(head -n 1 /etc/hostname 2>/dev/null || echo "Unknown")"
        echo "IMAGE: $(grep '^distro=' /etc/image-version 2>/dev/null | cut -d= -f2)"
        echo "VERSION: $(grep '^version=' /etc/image-version 2>/dev/null | cut -d= -f2)"
        echo "PYTHON: $(python --version 2>&1)"
        
        echo "Restarting enigma2..."
        sleep 3
        killall -9 enigma2
        exit 0
    else
        echo "Error: Plugin files not found in $PLUGINPATH"
    fi
else
    echo "Error: Installation failed!"
fi

cleanup
exit 1
