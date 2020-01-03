from imp import load_source

def passthrough(minMDL, maxMDL, maxCLL, maxFALL, addon):
    return (minMDL, maxMDL, maxCLL, maxFALL)

def maxCLLAsMaxMDL(minMDL, maxMDL, maxCLL, maxFALL, addon):
    if maxCLL > 0 and (maxCLL < maxMDL or addon.getSettingBool("preferMaxCLLSmaller") == False):
        return (minMDL, maxCLL, maxCLL, maxFALL)
    else:
        return (minMDL, maxMDL, maxCLL, maxFALL)

def customMaxMDL(minMDL, maxMDL, maxCLL, maxFALL, addon):
    return (minMDL, addon.getSettingInt("customMaxMDL"), 0, 0)

def customUserFunction(minMDL, maxMDL, maxCLL, maxFALL, addon):
    custom_toneremapper = load_source("custom_toneremapper", addon.getSetting("customFunctionFilePath"))
    return custom_toneremapper.customFunction(minMDL, maxMDL, maxCLL, maxFALL, addon)

def LG2017OLED(minMDL, maxMDL, maxCLL, maxFALL, addon):
    Y = maxMDL
    if maxCLL > 0 and (maxCLL < Y or addon.getSettingBool("preferMaxCLLSmaller") == False):
        Y = maxCLL

    if Y <= 500: #avoid unnecessary tonemapping LG 2017 OLEDs would otherwise do
        Y = 501
    elif Y < 850: #force a soft tonemapping curve (very slight clipping if between 801-849cd/m2)
        Y = min(Y, 800)
    elif Y < 1200: #avoid LG's broken ~1000nits tonemapping curves (everything between 801-1199cd/m2 is bugged on LG 2017 OLEDs)
        if addon.getSettingBool("lgSlightClipping1000"):
            Y = 800
        else:
            Y = 1200

    return (minMDL, Y, Y, maxFALL)

def LG2016OLED(minMDL, maxMDL, maxCLL, maxFALL, addon):
    Y = maxMDL
    if maxCLL > 0 and (maxCLL < Y or addon.getSettingBool("preferMaxCLLSmaller") == False):
        Y = maxCLL

    #this needs to be confirmed but 501 will most likely not result in tone mapping anyway
    if Y <= 500: #avoid unnecessary tonemapping LG 2016 OLEDs would otherwise do
        Y = 501

    return (minMDL, Y, Y, maxFALL)

Modes = {
    #0: unchanged,
    1: passthrough,
    2: maxCLLAsMaxMDL,
    3: customMaxMDL,
    4: customUserFunction,
    5: LG2017OLED,
    6: LG2016OLED
}
