import mediainfolib

def readHDRMetadata(filePath):
    mi = mediainfolib.parse(filePath, full=False)
    for track in mi.tracks:
        if track.track_type == "Video":
            if isHDR10(track):
                minMDL, maxMDL = getMDL(track)
                return (minMDL, maxMDL, getMaxCLL(track), getMaxFALL(track))
            break

    return None

def isHDR10(track):
    return (
        track.track_type == "Video" and
        (track.codec_id in ("V_MPEGH/ISO/HEVC", "hvc1", "hev1") or track.codec_id_info == "High Efficiency Video Coding") and
        track.bit_depth in (10, "10 bits") and
        #track.color_space == "YUV" and track.chroma_subsampling in ("4:2:0", "4:2:0 (Type 2)") and
        track.color_primaries == "BT.2020" and track.transfer_characteristics in ("PQ", "SMPTE ST 2084")
    )

def getMDL(track):
    mdl = track.mastering_display_luminance
    if mdl != None:
        mdl = mdl.split()
        if len(mdl) == 6:
            try:
                return (float(mdl[1]), int(float(mdl[4])))
            except:
                return (0.0, 0)
    return (0.0, 0)

def getMaxCLL(track):
    val = track.maximum_content_light_level
    if val != None:
        try:
            return int(val.split()[0])
        except:
            return 0
    return 0

def getMaxFALL(track):
    val = track.maximum_frameaverage_light_level
    if val != None:
        try:
            return int(val.split()[0])
        except:
            return 0
    return 0
