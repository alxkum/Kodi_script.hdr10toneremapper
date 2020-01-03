# From script.hdr10toneremapper: script for "Custom Function"-method to implement your own handling
# Function must return tuple of (MinMDL, MaxMDL, MaxCLL, MaxFALL) to be sent via HDMI.

def customFunction(minMDL, maxMDL, maxCLL, maxFALL, addon):
    return (minMDL, 1000, 0, 0)
