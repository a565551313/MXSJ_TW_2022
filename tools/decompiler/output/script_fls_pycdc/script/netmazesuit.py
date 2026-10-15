# pycdc 交叉复核产物 · script.fls entry 4175
# co_filename(原始)='script/netmazesuit.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4175.pyc (Python 2.5)

import net
MIGONG = 'migong'

class CMazeSuit(object):
    s_Mode2FuncName = {
        1: 'S2COpenMazeSuit',
        2: 'S2CSetShadowPetColor',
        3: 'S2CTakeDownSuit',
        5: 'S2CFlashTitle',
        8: 'S2CSetSuitInfo',
        9: 'S2CSetCollectData' }
    s_Treaty = MIGONG
    
    def Process(cls, netobj):
        iMode = netobj.UnpackInt(1)
        name = cls.s_Mode2FuncName.get(iMode)
        print iMode, name
        if name:
            func = getattr(cls, name, None)
            if func:
                func(netobj)
            
        

    Process = classmethod(Process)
    
    def C2SPacket<repare(cls):
        netobj = net.g_Net
        netobj.PacketPrepare(net.C2GS_HUODONG)
        netobj.PacketAddI(len(cls.s_Treaty), 1)
        netobj.PacketAddS(cls.s_Treaty, len(cls.s_Treaty))
        return netobj

    C2SPacket<repare = classmethod(C2SPacket<repare)
    
    def S2COpenMazeSuit(cls, netobj):
        import dlgmazesuit
        iColor1 = netobj.UnpackInt(1)
        iColor2 = netobj.UnpackInt(1)
        iColor3 = netobj.UnpackInt(1)
        iColor4 = netobj.UnpackInt(1)
        dlgmazesuit.CSuitDataMgr.InitData(iColor1, iColor2, iColor3, iColor4)
        dlgmazesuit.Show()

    S2COpenMazeSuit = classmethod(S2COpenMazeSuit)
    
    def S2CSetShadowPetColor(cls, netobj):
        import dlgmazesuit
        iColor = netobj.UnpackInt(1)
        dlgmazesuit.CSuitDataMgr.SetShadowPetColor(iColor)

    S2CSetShadowPetColor = classmethod(S2CSetShadowPetColor)
    
    def S2CTakeDownSuit(cls, netobj):
        import dlgmazesuit
        index = netobj.UnpackInt(1)
        dlgmazesuit.TakeDownSuit(index)

    S2CTakeDownSuit = classmethod(S2CTakeDownSuit)
    
    def S2CSetFairyColor(cls, netobj):
        import dlgmazesuit
        iColor = netobj.UnpackInt(1)
        dlgmazesuit.CSuitDataMgr.SetFairyColor(iColor)

    S2CSetFairyColor = classmethod(S2CSetFairyColor)
    
    def S2CFlashTitle(cls, netobj):
        import dlgmazesuit
        num = netobj.UnpackInt(1)
        if num == 3:
            \xaa\xa6\xaa\x92\xad\xaa = []
            for i in xrange(num):
                len1 = netobj.UnpackInt(1)
                \xaa\xa6\xaa\x92\xad\xaa.append(netobj.UnpackString(len1))
            
            dlgmazesuit.CSuitDataMgr.SetFlashTitle(\xaa\xa6\xaa\x92\xad\xaa)
        else:
            dlgmazesuit.CSuitDataMgr.SetFlashTitle([])

    S2CFlashTitle = classmethod(S2CFlashTitle)
    
    def S2CSetTraceColor(cls, netobj):
        import dlgmazesuit
        iColor = netobj.UnpackInt(1)
        dlgmazesuit.CSuitDataMgr.SetTraceColor(iColor)

    S2CSetTraceColor = classmethod(S2CSetTraceColor)
    
    def S2CSetAuraColor(cls, netobj):
        import dlgmazesuit
        iColor = netobj.UnpackInt(1)
        dlgmazesuit.CSuitDataMgr.SetAuraColor(iColor)

    S2CSetAuraColor = classmethod(S2CSetAuraColor)
    
    def S2CSetSuitInfo(cls, netobj):
        import dlgmazesuit
        index = netobj.UnpackInt(1)
        iState = netobj.UnpackInt(1)
        dlgmazesuit.SetSuitState(index, iState)

    S2CSetSuitInfo = classmethod(S2CSetSuitInfo)
    
    def S2CSetCollectData(cls, netobj):
        import dlgmazesuit
        index = netobj.UnpackInt(1)
        num = netobj.UnpackInt(1)
        data = { }
        for i in xrange(num):
            itemid = netobj.UnpackInt(4)
            isdown = netobj.UnpackInt(1)
            data[itemid] = isdown
        
        dlgmazesuit.CSuitDataMgr.SetCollectData(index, data)

    S2CSetCollectData = classmethod(S2CSetCollectData)
    
    def C2STakeDownSuit(cls, index):
        netobj = cls.C2SPacket<repare()
        netobj.PacketAddI(1, 1)
        netobj.PacketAddI(index, 1)
        netobj.PacketSend()

    C2STakeDownSuit = classmethod(C2STakeDownSuit)
    
    def C2SFengYin(cls, index):
        netobj = cls.C2SPacket<repare()
        netobj.PacketAddI(2, 1)
        netobj.PacketAddI(index, 1)
        netobj.PacketSend()

    C2SFengYin = classmethod(C2SFengYin)
    
    def C2SChangeTitle(cls, index, titleLst):
        netobj = cls.C2SPacket<repare()
        netobj.PacketAddI(3, 1)
        netobj.PacketAddI(index, 1)
        for title in titleLst:
            netobj.PacketAddI(len(title), 1)
            netobj.PacketAddS(title, len(title))
        
        netobj.PacketSend()

    C2SChangeTitle = classmethod(C2SChangeTitle)
    
    def C2SResetBBmake(cls, index):
        netobj = cls.C2SPacket<repare()
        netobj.PacketAddI(4, 1)
        netobj.PacketAddI(index, 1)
        netobj.PacketSend()

    C2SResetBBmake = classmethod(C2SResetBBmake)
    
    def C2SChangeColor(cls, index):
        netobj = cls.C2SPacket<repare()
        netobj.PacketAddI(5, 1)
        netobj.PacketAddI(index, 1)
        netobj.PacketSend()

    C2SChangeColor = classmethod(C2SChangeColor)
    
    def C2STitleEmote(cls, index, iEmote):
        netobj = cls.C2SPacket<repare()
        netobj.PacketAddI(6, 1)
        netobj.PacketAddI(index, 1)
        netobj.PacketAddI(iEmote, 1)
        netobj.PacketSend()

    C2STitleEmote = classmethod(C2STitleEmote)
    
    def C2SMiHuanSuit(cls, index, iType):
        netobj = cls.C2SPacket<repare()
        netobj.PacketAddI(7, 1)
        netobj.PacketAddI(index, 1)
        netobj.PacketAddI(iType, 1)
        netobj.PacketSend()

    C2SMiHuanSuit = classmethod(C2SMiHuanSuit)
    
    def C2SGetSuitInfo(cls, index):
        netobj = cls.C2SPacket<repare()
        netobj.PacketAddI(8, 1)
        netobj.PacketAddI(index, 1)
        netobj.PacketSend()

    C2SGetSuitInfo = classmethod(C2SGetSuitInfo)
    
    def C2SGetCollectData(cls, index):
        netobj = cls.C2SPacket<repare()
        netobj.PacketAddI(9, 1)
        netobj.PacketAddI(index, 1)
        netobj.PacketSend()

    C2SGetCollectData = classmethod(C2SGetCollectData)
    
    def C2SOpenLock(cls, index):
        netobj = cls.C2SPacket<repare()
        netobj.PacketAddI(10, 1)
        netobj.PacketAddI(index, 1)
        netobj.PacketSend()

    C2SOpenLock = classmethod(C2SOpenLock)
