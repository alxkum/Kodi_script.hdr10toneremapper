import os
import sys
from shutil import copyfile
import xbmc
import xbmcaddon

addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo("name")
cwd = addon.getAddonInfo("path").decode("utf-8")

sys.path.append(os.path.join(cwd, "resources", "lib"))

import video
import signaloverride
import remapping

pendingStop = False

def install():
    try:
        copyfile(os.path.join(cwd, "custom_toneremapper.py"), addon.getSetting("customFunctionFilePath"))
    except:
        pass

    xbmc.executebuiltin('Addon.OpenSettings(%s)' % addon.getAddonInfo("id"))
    xbmc.executebuiltin('Notification("HDR10 Toneremapper", "Please select your tone remapping mode!", 15000)')

def videoStarted():
    global pendingStop
    pendingStop = False

    #pre-filter for HEVC in 4K
    if xbmc.getInfoLabel("VideoPlayer.VideoCodec") != "hevc" or xbmc.getInfoLabel("VideoPlayer.VideoResolution") != "4K":
        return

    hdrData = video.readHDRMetadata(xbmc.Player().getPlayingFile())
    if hdrData == None or pendingStop == True:
        return

    overrideHDRData = None
    modeFn = remapping.Modes.get(addon.getSettingInt("mode"))

    if modeFn != None:
        overrideHDRData = modeFn(hdrData[0], hdrData[1], hdrData[2], hdrData[3], addon)

        if overrideHDRData == None or overrideHDRData[1] == 0:
            overrideHDRData = (1, addon.getSettingInt("fallbackMaxMDL"), 0, 0)

        delay = addon.getSettingInt("delay")
        if delay > 0:
            xbmc.sleep(delay*1000)

        signaloverride.enable(overrideHDRData[0], overrideHDRData[1], overrideHDRData[2], overrideHDRData[3])

    if addon.getSettingBool("notification"):
        Y = overrideHDRData[1] if overrideHDRData != None else 0

        if modeFn == None or modeFn == remapping.passthrough: #don't show override for "Unchanged" and "Passthrough"
            Y = 0

        showNotification(hdrData[1], hdrData[2], Y)

def videoStopped():
    global pendingStop
    pendingStop = True
    signaloverride.disable()

def showNotification(contentMaxMDL, contentMaxCLL, overrideY=0):
    t = "MaxMDL "+str(contentMaxMDL)
    if contentMaxCLL > 0:
        t += ", MaxCLL "+str(contentMaxCLL)
    if overrideY > 0:
        t += " -> "+str(overrideY)
    t += " cd/m2"

    xbmc.executebuiltin('Notification("HDR10", "%s", %d)' % (t, addon.getSettingInt("notificationDuration")*1000))


class PlayerHook(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self)

    def onAVStarted(self):
        videoStarted()

    def onPlayBackStopped(self):
        videoStopped()

    def onPlayBackEnded(self):
        videoStopped()


if __name__ == "__main__":
    if os.path.exists(addon.getSetting("customFunctionFilePath")) == False:
        install()

    player = PlayerHook()
    monitor = xbmc.Monitor()

    while not monitor.abortRequested():
        if monitor.waitForAbort(10):
            break

    del monitor
    del player
