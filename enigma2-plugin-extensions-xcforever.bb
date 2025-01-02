SUMMARY = "Lululla"
MAINTAINER = "Lululla"
SECTION = "base"
PRIORITY = "required"
LICENSE = "proprietary"

require conf/license/license-gplv2.inc

inherit gitpkgv
SRCREV = "${AUTOREV}"
PV = "1.0+git${SRCPV}"
PKGV = "1.0+git${GITPKGV}"
VER ="3.9"
PR = "r0"

SRC_URI = "git://github.com/Belfagor2005/xc_plugin_forever.git;protocol=https;branch=main"

S = "${WORKDIR}/git"

#FILES_${PN} = "/usr/* /etc*"
#do_install() {
#    cp -rp ${S}/usr* /etc* ${D}/ 
#}

FILES_${PN} = " ${libdir}/enigma2/python/Components/Renderer/* \
                ${libdir}/enigma2/python/Plugins/Extensions/XCplugin/* \
                /etc* \
                "
do_patch[noexec] = "1"
do_configure[noexec] = "1"
do_compile[noexec] = "1"
do_install() {
install -d ${D}${libdir}/enigma2/python/Components/Renderer
install -d ${D}${libdir}/enigma2/python/Plugins/Extensions/XCplugin
cp -rf ${S}/usr/lib/enigma2/python/Components/Renderer/*.py ${D}${libdir}/enigma2/python/Components/Renderer/
cp -rf ${S}/usr/lib/enigma2/python/Plugins/Extensions/XCplugin/* ${D}${libdir}/enigma2/python/Plugins/Extensions/XCplugin/
# cp -rf ${S}/etc/* /
}



