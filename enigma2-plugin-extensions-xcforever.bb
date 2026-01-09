SUMMARY = "XC Plugin Forever"
MAINTAINER = "Lululla"
SECTION = "base"
PRIORITY = "required"
LICENSE = "CLOSED"

require conf/license/license-gplv2.inc

inherit gitpkgv allarch

SRCREV = "${AUTOREV}"
PV = "3.9+git${SRCPV}"
PKGV = "3.9+git${GITPKGV}"
PR = "r0"

SRC_URI = "git://github.com/Belfagor2005/xc_plugin_forever.git;protocol=https;branch=main"

S = "${WORKDIR}/git"

do_patch[noexec] = "1"
do_configure[noexec] = "1"
do_compile[noexec] = "1"

do_install() {
    install -d ${D}${libdir}/enigma2/python/Components/Renderer
    install -d ${D}${libdir}/enigma2/python/Plugins/Extensions/XCplugin
    
    # Componenti Renderer
    if [ -d "${S}/usr/lib/enigma2/python/Components/Renderer" ]; then
        cp -rf ${S}/usr/lib/enigma2/python/Components/Renderer/*.py \
               ${D}${libdir}/enigma2/python/Components/Renderer/
    fi
    
    # Plugin XC
    if [ -d "${S}/usr/lib/enigma2/python/Plugins/Extensions/XCplugin" ]; then
        cp -rf ${S}/usr/lib/enigma2/python/Plugins/Extensions/XCplugin/* \
               ${D}${libdir}/enigma2/python/Plugins/Extensions/XCplugin/
    fi
    
    # File di configurazione
    if [ -d "${S}/etc/enigma2/xc" ]; then
        install -d ${D}/etc/enigma2
        cp -r "${S}/etc/enigma2/xc" "${D}/etc/enigma2/"
    elif [ -f "${S}/etc/enigma2/xc" ]; then
        install -d ${D}/etc/enigma2
        install -m 644 "${S}/etc/enigma2/xc" "${D}/etc/enigma2/xc"
    fi
}

FILES:${PN} = " \
    ${libdir}/enigma2/python/Components/Renderer/*.py \
    ${libdir}/enigma2/python/Plugins/Extensions/XCplugin \
    /etc/enigma2 \
"