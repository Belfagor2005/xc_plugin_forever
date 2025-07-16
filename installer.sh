#!/bin/bash

version='4.9'
changelog='Fix DreamOs System'

# Initialize variables
TMPPATH=/tmp/XCplugin-main
FILEPATH=/tmp/main.tar.gz
PLUGINPATH=/usr/lib/enigma2/python/Plugins/Extensions/XCplugin
[ -d /usr/lib64 ] && PLUGINPATH=/usr/lib64/enigma2/python/Plugins/Extensions/XCplugin

# Cleanup previous runs
cleanup() {
    [ -r $TMPPATH ] && rm -rf $TMPPATH >/dev/null 2>&1
    [ -r $FILEPATH ] && rm -f $FILEPATH >/dev/null 2>&1
}
cleanup

# Determine system type
if [ -f /var/lib/dpkg/status ]; then
    STATUS=/var/lib/dpkg/status
    OSTYPE=DreamOs
else
    STATUS=/var/lib/opkg/status
    OSTYPE=Dream
fi

# Install required tools
install_wget() {
    if ! command -v wget >/dev/null; then
        echo "Installing wget..."
        if [ $OSTYPE = "DreamOs" ]; then
            apt-get update && apt-get install -y wget || return 1
        else
            opkg update && opkg install wget || return 1
        fi
    fi
    return 0
}

# Main installation
if install_wget; then
    # Download and extract plugin
    mkdir -p $TMPPATH && cd $TMPPATH || exit 1
    
    if wget --no-check-certificate -O $FILEPATH 'https://github.com/Belfagor2005/xc_plugin_forever/archive/refs/heads/main.tar.gz' && \
       [ -s $FILEPATH ]; then
        tar -xzf $FILEPATH -C $TMPPATH && \
        cp -r $TMPPATH/xc_plugin_forever-main/usr /
        
        if [ -d $PLUGINPATH ]; then
            echo "Installation successful!"
            cleanup
            sync
            # Restart enigma2
            killall -9 enigma2
            exit 0
        fi
    fi
fi

echo "Installation failed!"
cleanup
exit 1
