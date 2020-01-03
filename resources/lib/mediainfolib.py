import os
import platform
import ctypes
import xbmcaddon
from pymediainfo import MediaInfo

cwd = xbmcaddon.Addon().getAddonInfo("path").decode("utf-8")

archMap = {
    "armv7": "aarch64",
    "AMD64": "x86_64"
}

def parse(filePath, full=True):
    arch = platform.uname()[4]
    if archMap.has_key(arch):
        arch = archMap[arch]

    lib = os.path.join(cwd, "resources", "mediainfolib", arch)
    dependencies = [] #hold references to make sure lib doesn't get unloaded too early

    if os.name != "nt": #preload all dependencies
        dependencies.append(ctypes.CDLL(os.path.join(lib, "libcurl-gnutls.so")))
        dependencies.append(ctypes.CDLL(os.path.join(lib, "libmms.so")))
        dependencies.append(ctypes.CDLL(os.path.join(lib, "libtinyxml2.so")))
        dependencies.append(ctypes.CDLL(os.path.join(lib, "libzen.so")))
        lib = os.path.join(lib, "libmediainfo.so")
    else:
        lib = os.path.join(lib, "MediaInfo.dll")

    lib = lib.encode("ascii")

    filePath = mountVideoFile(filePath) #mount if necessary
    mi = MediaInfo.parse(filePath, full=full, library_file=lib)
    unmountVideoFile()

    return mi

videoFileMounted = False

def mountVideoFile(filePath):
    global videoFileMounted

    if filePath.startswith("nfs://") and os.name != "nt":
        filePath = filePath[6:]
        sepFirst = filePath.index("/")
        sepLast = filePath.rindex("/")
        host = filePath[0:sepFirst]
        dir = filePath[sepFirst:sepLast]

        mountPath = os.path.join(cwd, "resources", "media", "tmpmount")
        os.system("sudo mount -t nfs %s:\"%s\" %s" % (host, dir, mountPath))
        videoFileMounted = True

        filePath = os.path.join(mountPath, filePath[sepLast+1:])

    return filePath

def unmountVideoFile():
    global videoFileMounted

    if videoFileMounted:
        os.system("sudo umount %s" % os.path.join(cwd, "resources", "media", "tmpmount"))
        videoFileMounted = False
