# pycdc 交叉复核产物 · script.fls entry 3417
# co_filename(原始)='script/mxgame/nethuodong/activity/nethddafuweng2v2.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3417.pyc (Python 2.5)

import huodongdefine
import mdtasktrace
import net

def GetDafuweng2v2NetObj():
    netobj = net.PacketPrepare(net.C2GS_HUODONG)
    netobj.PacketAddPS(huodongdefine.DAFUWENG2V2)
    return netobj


def ShowRewardDlg(netobj):
    rewardLst = { }
    iLen = netobj.UnpackInt(1)
    for idx in xrange(iLen):
        shape = netobj.UnpackInt(4)
        amount = netobj.UnpackInt(2)
        rewardLst[idx] = (shape, amount)
    
    import richman
    richman.ShowRewardDlg(rewardLst)


def HideTaskFollowPanel(netobj):
    iType = netobj.UnpackInt(1)
    bResult = (None,)
    if iType == 1:
        bResult = False
    
    mdtasktrace.GetModel().SetTaskFrameIsExpand(bResult)


def C2SAnswerReward():
    netobj = GetDafuweng2v2NetObj()
    netobj.PacketAddI(1, 1)
    netobj.PacketSend()

S2CFunc = {
    1: ShowRewardDlg,
    2: HideTaskFollowPanel }

def S2CDafuweng2v2Process(netobj):
    iSub = netobj.UnpackInt(1)
    if iSub not in S2CFunc:
        LOG('S2CDafuweng2v2-%d \xaf\xca\xa4\xd6\xa9w\xb8q\xa1I' % iSub)
        return None
    
    import protocolprint
    oFunc = S2CFunc[iSub]
    protocolprint.AppendS2CSubInfo('Dafuweng2v2', oFunc.__name__)
    oFunc(netobj)
