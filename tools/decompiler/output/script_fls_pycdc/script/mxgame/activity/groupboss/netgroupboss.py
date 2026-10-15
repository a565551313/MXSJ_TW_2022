# pycdc 交叉复核产物 · script.fls entry 2667
# co_filename(原始)='script/mxgame/activity/groupboss/netgroupboss.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2667.pyc (Python 2.5)

import dlggroupboss

def GetGroupBossNetObj(iSub):
    import net
    import nethuodong
    netobj = net.g_Net
    sTreaty = nethuodong.BOSSFIGHT
    if netobj:
        netobj.PacketPrepare(net.C2GS_HUODONG)
        netobj.PacketAddI(len(sTreaty), 1)
        netobj.PacketAddS(sTreaty, len(sTreaty))
        netobj.PacketAddI(iSub, 1)
        LOG_DEBUG('C2SGroupBoss-%d' % iSub)
    
    return netobj


def S2CGameBossHP(netobj):
    iMaxHP = netobj.UnpackInt(4)
    iCurHP = netobj.UnpackInt(4)
    dlggroupboss.ShowBossHP(iCurHP, iMaxHP)


def S2CCloseBossHP(netobj):
    dlggroupboss.CloseBossHP()


def S2CUpdatePanel(netobj):
    iStage = netobj.UnpackInt(1)
    iNeed = netobj.UnpackInt(1)
    dlggroupboss.ShowPanel(iStage, iNeed)


def S2CClosePanel(netobj):
    None(None, None, None, None, None, None, None, None, None, None, dlggroupboss.ClosePanel)

S2CFunc = {
    1: S2CGameBossHP,
    2: S2CCloseBossHP,
    3: S2CUpdatePanel,
    4: S2CClosePanel }

def S2CGroupBoss(netobj):
    iSub = netobj.UnpackInt(1)
    if iSub not in S2CFunc:
        LOG('S2CGroupBoss-%d \xaf\xca\xa4\xd6\xa9w\xb8q\xa1I' % iSub)
        return None
    
    import protocolprint
    8nc = S2CFunc[iSub]
    protocolprint.AppendS2CSubInfo('netGroupBoss', 8nc.__name__)
    8nc(netobj)
