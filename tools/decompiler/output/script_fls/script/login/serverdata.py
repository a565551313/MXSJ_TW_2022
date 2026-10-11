# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\serverdata.py
SERVER_TYPE_NORMAL = 0
SERVER_TYPE_TX = 1
SERVER_TYPE_JJ = 2
SERVER_TYPE_ZBS = 3
SERVER_TYPE_KFFB = 6
SERVER_TYPE_PROXY = 7
SERVER_TYPE_KFHD = 8
SERVER_TYPE_ALLOT = 9
SERVER_TYPE_CODE = 10
SERVER_TYPE_ALLSTAR = 11
SERVER_TYPE_CONFIG = {SERVER_TYPE_KFFB: (411, 412, 30331, 30531, 30131, 30132, 30181, 30182, 7121, 16, 30351, 30551, 30831), 
   SERVER_TYPE_JJ: (111, 414, 415, 416, 417, 419, 30142, 30144, 30192, 30194, 112, 14, 30195, 30196, 30361,
 30551, 30832, 30326), 
   SERVER_TYPE_KFHD: (420, 30136, 30186, 30331, 30631, 30551, 30831), 
   SERVER_TYPE_TX: (101, 30141, 30191, 102, 11, 30353), 
   SERVER_TYPE_ZBS: (125, 30143, 30193, 42583), 
   SERVER_TYPE_PROXY: (131, 132, 133, 30398, 30598, 30098, 30099, 7120, 120, 33991, 33992, 33993, 30391,
 33994, 33995, 30591, 15, 30899), 
   SERVER_TYPE_ALLSTAR: (30197, 30145, 30354, 33801)}
CONFIG_IP_LIST = [
 75, 
 76, 
 77, 
 78, 
 79, 
 80, 
 81]
g_ServerInfoDict = {}

def SetServerInfoDict(iID, dInfo):
    global g_ServerInfoDict
    g_ServerInfoDict[iID] = dInfo
    return


def IsInServerInfoDict(iID):
    if iID in g_ServerInfoDict:
        return True
    return False


def GetServerNameByID(iID):
    import serverbattledefine
    if iID in serverbattledefine.SERVERID2NAME:
        return serverbattledefine.SERVERID2NAME[iID]
    if iID in g_ServerInfoDict:
        return g_ServerInfoDict[iID]['name']
    else:
        return
    return


def GetServerInfoByID(iID):
    if iID in g_ServerInfoDict:
        return g_ServerInfoDict[iID]
    else:
        return
    return


def GetServerIDByName(sName):
    for (iServerID, dictInfo) in g_ServerInfoDict.iteritems():
        if dictInfo['name'] == sName:
            return iServerID

    return 0


def GetServerType(iServerID):
    for (iType, tServer) in SERVER_TYPE_CONFIG.items():
        if iServerID in tServer:
            return iType

    return SERVER_TYPE_NORMAL


def IsKuafuServer(iServerID):
    return GetServerType(iServerID) in (SERVER_TYPE_KFFB, SERVER_TYPE_JJ, SERVER_TYPE_KFHD, SERVER_TYPE_ZBS)


def IsFightServer(iServerID):
    return GetServerType(iServerID) == SERVER_TYPE_ZBS


def IsTianXuanServer(iServerID):
    return GetServerType(iServerID) == SERVER_TYPE_TX


def IsAllSTARServer(iServerID):
    return GetServerType(iServerID) == SERVER_TYPE_ALLSTAR


def IsJingJiServer(iServerID):
    return GetServerType(iServerID) == SERVER_TYPE_JJ


return
