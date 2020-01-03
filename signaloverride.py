import os
import platform
import xbmc

AUTO_DISABLE_DELAY = 1000 #could probably be even lower
ON_SUPPORTED_PLATFORM = (platform.uname()[1] == "osmc" and platform.uname()[2].startswith("3."))

def enable(minMDL, maxMDL, maxCLL, maxFALL):
    if not ON_SUPPORTED_PLATFORM:
        xbmc.executebuiltin('Notification("HDR10 Toneremapper", "Signal overriding not supported on this device")')
        return

    minMDL = minMDL*10000
    customHDRStr = "8500,39850,6550,2300,35400,14600,15635,16450,%d,%d,%d,%d" % (int(maxMDL), int(minMDL), int(maxCLL), int(maxFALL))

    # changing customer_master_display_en will trigger a signal_change_flag and cause
    # amvecm_cp_hdr_info() to read the new HDR10 metadata from customer_hdmi_display_param

    os.system("echo \"9,16,%s\" | sudo tee /sys/module/am_vecm/parameters/customer_hdmi_display_param" % customHDRStr)
    os.system("echo \"%s\" | sudo tee /sys/module/am_vecm/parameters/customer_master_display_param" % customHDRStr)

    os.system("echo \"1\" | sudo tee /sys/module/am_vecm/parameters/customer_hdmi_display_en")
    os.system("echo \"1\" | sudo tee /sys/module/am_vecm/parameters/customer_master_display_en")

    # disabling in this order will not disable the override during playback
    # instead it will automatically make the display switch back to SDR in the menu
    xbmc.sleep(AUTO_DISABLE_DELAY)
    os.system("echo \"0\" | sudo tee /sys/module/am_vecm/parameters/customer_master_display_en")
    xbmc.sleep(AUTO_DISABLE_DELAY)
    os.system("echo \"0\" | sudo tee /sys/module/am_vecm/parameters/customer_hdmi_display_en")

def disable():
    if not ON_SUPPORTED_PLATFORM:
        return

    os.system("echo \"0\" | sudo tee /sys/module/am_vecm/parameters/customer_hdmi_display_en")
    os.system("echo \"0\" | sudo tee /sys/module/am_vecm/parameters/customer_master_display_en")
