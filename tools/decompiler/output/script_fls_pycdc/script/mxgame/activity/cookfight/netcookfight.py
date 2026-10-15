# pycdc 交叉复核产物 · script.fls entry 3039
# co_filename(原始)='script/mxgame/activity/cookfight/netcookfight.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3039.pyc (Python 2.5)

import net
import cookfightmgr

def GetNetObj(iSub):
    import nethuodong
    netobj = net.PacketPrepare(net.C2GS_HUODONG)
    if netobj:
        netobj.PacketAddPS(nethuodong.COOK_FIGHT)
        netobj.PacketAddI(iSub, 1)
    
    return netobj


def S2CRefreshCollectDlg(netobj):
    sName = netobj.UnpackPS()
    iLen = netobj.UnpackInt(1)
    dInfoList = []
    for _ in range(iLen):
        dInfo = { }
        dInfo['sName'] = netobj.UnpackPS()
        dInfo['iCur'] = netobj.UnpackInt(1)
        dInfo['iBest'] = netobj.UnpackInt(1)
        dInfoList.append(dInfo)
    
    cookfightmgr.GetMgr().RefreshCollectDlg(dInfoList, sName)


def S2CCloseCollectDlg(netobj):
    cookfightmgr.GetMgr().CloseCollectDlg()


def S2CRefreshCookDlg(netobj):
    sName = netobj.UnpackPS()
    iShowDark = netobj.UnpackInt(1)
    iDarkHeat = netobj.UnpackInt(2)
    iDark = netobj.UnpackInt(1)
    iFinishRatio = netobj.UnpackInt(1)
    iChangeFlag = netobj.UnpackInt(1)
    iBeChangeHeat = netobj.UnpackInt(1)
    iCurHeat = netobj.UnpackInt(2)
    iBestHeat = netobj.UnpackInt(2)
    LOG_DEBUG('>\xacO\xa7_\xc5\xe3\xa5\xdc\xb6\xc2\xb7t\xae\xc6\xb2z\xb1\xf8\xa5\xf3>>', iShowDark)
    LOG_DEBUG('>\xb6\xc2\xb7t\xae\xc6\xb2z\xa4\xf5\xad\xd4>>', iDarkHeat)
    LOG_DEBUG('>\xacO\xa7_\xb6}\xb1\xd2\xa4F\xb6\xc2\xb7t\xae\xc6\xb2z>>', iDark)
    LOG_DEBUG('>\xa7\xb9\xa6\xa8\xab\xd7>>', iFinishRatio)
    LOG_DEBUG('>\xa4\xf5\xad\xd4>>', iCurHeat, iBestHeat)
    LOG_DEBUG('>\xb7\xc5\xab\xd7\xc5\xdc\xa4\xc6>>', iChangeFlag, iBeChangeHeat)
    iLen = netobj.UnpackInt(1)
    dInfoList = []
    for _ in range(iLen):
        dInfo = { }
        dInfo['sName'] = netobj.UnpackPS()
        dInfo['iCur'] = netobj.UnpackInt(1)
        dInfo['iBest'] = netobj.UnpackInt(1)
        LOG_DEBUG(dInfo['sName'], dInfo['iCur'], dInfo['iBest'])
        dInfoList.append(dInfo)
    
    cookfightmgr.GetMgr().RefreshCookDlg(sName, iShowDark, iDarkHeat, iDark, iFinishRatio, iCurHeat, iBestHeat, dInfoList, iChangeFlag, iBeChangeHeat)


def S2CCloseCookDlg(netobj):
    cookfightmgr.GetMgr().CloseCookDlg()


def S2CStartCookTime(netobj):
    netobj.UnpackInt.cookfightmgr = None
    iStartTime = None(None)
    cookfightmgr.GetMgr().SetStartTime(iStartTime)

S2CFunc = {
    2: S2CRefreshCollectDlg,
    3: S2CCloseCollectDlg,
    4: S2CRefreshCookDlg,
    5: S2CCloseCookDlg,
    6: S2CStartCookTime }
WAR_CACHE = [
    2,
    3,
    4,
    5]

def CheckInWar(netobj, oFunc, iSub):
    import war
    import main
    if main.InWar() and iSub in WAR_CACHE:
        cmd = war.CCmd(war.ServerCmd)
        cmd.netobj = net.CNetServerCommand(netobj)
        cmd.func = oFunc
    else:
        oFunc(netobj)


def S2CProcess(netobj):
    iSub = netobj.UnpackInt(1)
    if iSub not in S2CFunc:
        LOG('S2CCookFight-%d \xaf\xca\xa4\xd6\xa9w\xb8q\xa1I' % iSub)
        return None
    
    import protocolprint
    oFunc = S2CFunc[iSub]
    LOG_DEBUG('S2CCookFight-%d' % iSub)
    protocolprint.AppendS2CSubInfo('CookFight', oFunc.__name__)
    CheckInWar(netobj, oFunc, iSub)
