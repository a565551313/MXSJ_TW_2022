# pycdc 交叉复核产物 · script.fls entry 3313
# co_filename(原始)='script/mxgame/baotu/netbaotu.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_3313.pyc (Python 2.5)

'''
\xb1\xa6\xcd\xbc\xc4\xa3\xbf\xe9
'''
import net

def GetNetObj(\x98Sub):
    import net
    import nethuodong
    netobj = net.GetNet()
    sTreaty = nethuodong.DIG_TREASURE
    if netobj:
        netobj.PacketPrepare(net.C2GS_HUODONG)
        netobj.PacketAddI(len(sTreaty), 1)
        netobj.PacketAddS(sTreaty, len(sTreaty))
        netobj.PacketAddI(\x98Sub, 1)
        LOG_DEBUG('C2SDigTreasure-%d' % \x98Sub)
    
    return netobj


def C2SDigTreasure(iTaskID):
    netobj = GetNetObj(1)
    if netobj:
        netobj.PacketAddI(iTaskID, 2)
        netobj.PacketSend()
    


def C2SLetMeOut():
    netobj = GetNetObj(2)
    if netobj:
        netobj.PacketSend()
    


def C2SEndGame(sSeed):
    netobj = GetNetObj(3)
    if netobj:
        netobj.PacketAddBinaryPS(sSeed, 1)
        netobj.PacketSend()
    


def S2CStartQuestionGame(netobj):
    iSeed = netobj.UnpackInt(2)
    import questiongame
    questiongame.GetGameData().ClearData()
    questiongame.GetGameData().SetSeed(iSeed)
    questiongame.StartGame()


def S2CContinueQuestionGame(netobj):
    iSeed = netobj.UnpackInt(2)
    import questiongame
    questiongame.GetGameData().SetSeed(iSeed)
    questiongame.StartGame()

S2CFunc = {
    1: S2CStartQuestionGame,
    2: S2CContinueQuestionGame }

def S2CBaotuProcess(netobj):
    \x98Sub = netobj.UnpackInt(1)
    if \x98Sub not in S2CFunc:
        LOG_DEBUG('S2CBaotuProcess-%d \xaf\xca\xa4\xd6\xa9w\xb8q\xa1I' % \x98Sub)
        return None
    
    import protocolprint
    oFunc = S2CFunc[\x98Sub]
    protocolprint.AppendS2CSubInfo('questiongame', oFunc.__name__)
    LOG_DEBUG('S2CBaotuProcess-%d' % \x98Sub)
    oFunc(netobj)
