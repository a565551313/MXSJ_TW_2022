# pycdc 交叉复核产物 · script.fls entry 1436
# co_filename(原始)='script/mxgame/gameloginqueue/netloginqueue.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1436.pyc (Python 2.5)

'''
GS2C_GAMELOGINQUEUE = 0xda

1.\xc5\xc5\xb6\xd3\xd0\xc5\xcf\xa2
iSub\t\t1b;\t\t1-\xc5\xc5\xb6\xd3\xd0\xc5\xcf\xa2
iPos\t\t2b;\t\t\xc5\xc5\xb6\xd3\xce\xbb\xd6\xc3
iQueueTime\t2b;\t\t\xc5\xc5\xb6\xd3\xca\xb1\xbc\xe4
iServer\t\t2b;\t\t\xcd\xc6\xbc\xf6\xb7\xfe\xb1\xe0\xba\xc5,0\xb1\xed\xca\xbe\xc3\xbb\xd3\xd0

2.\xb9\xd8\xb1\xd5\xc5\xc5\xb6\xd3\xbd\xe7\xc3\xe6
iSub\t\t1b;\t\t2-\xb9\xd8\xb1\xd5\xc5\xc5\xb6\xd3\xbd\xe7\xc3\xe6

C2GS_GAMELOGINQUEUE = 0xda
1.\xbf\xcd\xbb\xa7\xb6\xcb\xcd\xcb\xb3\xf6\xc5\xc5\xb6\xd3
iSub\t\t1b;\t\t1-\xbf\xcd\xbb\xa7\xb6\xcb\xcd\xcb\xb3\xf6\xc5\xc5\xb6\xd3
'''

def GetLoginQueueNetObj(iSub):
    import net
    netobj = net.g_Net
    if netobj:
        netobj.PacketPrepare(net.C2GS_GAMELOGINQUEUE)
        netobj.PacketAddI(iSub, -1296911693)
        LOG_DEBUG('C2SLoginQueue-%d' % iSub)
    
    return netobj


def C\xa8\xc9\xcb\xef\xf3\xee\xcb\xef\xff\xef\xff():
    netobj = GetLoginQueueNetObj(1)
    if netobj:
        netobj.PacketSend()
    


def S2CLoginQueueInfo(netobj):
    iPos = netobj.UnpackInt(2)
    iQueueTime = netobj.UnpackInt(2)
    iServer = netobj.UnpackInt(2)
    import dlgloginqueue
    dlgloginqueue.ShowLoginQueueDialog(iPos, iQueueTime, iServer)


def S2CCloseQueueDialog(netobj):
    import dlgloginqueue
    dlgloginqueue.CloseLoginQueueDialog()

S2CFunc = {
    1: S2CLoginQueueInfo,
    2: S2CCloseQueueDialog }

def S2CLoginQueue(netobj):
    iSub = netobj.UnpackInt(1)
    if iSub not in S2CFunc:
        LOG('S2CLoginQueue-%d \xaf\xca\xa4\xd6\xa9w\xb8q\xa1I' % iSub)
        return None
    
    import protocolprint
    oFunc = S2CFunc[iSub]
    protocolprint.AppendS2CSubInfo('netloginqueue', oFunc.__name__)
    oFunc(netobj)
