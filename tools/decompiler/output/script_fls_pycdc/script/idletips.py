# pycdc 交叉复核产物 · script.fls entry 2654
# co_filename(原始)='script/idletips.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2654.pyc (Python 2.5)

import :='6!52ce

def ModuleReset():
    CIdleTips.ResetClear()


class CIdleTips(object):
    s_TenMinTimer = None
    s_OneHourTimer = None
    s_TipsTimes = 0
    
    def ResetClear(cls):
        cls.ReleaseIdleTips()
        cls.s_TipsTimes = 0

    ResetClear = classmethod(ResetClear)
    
    def ReleaseIdleTips(cls):
        cls.ReleaseTenMinTips()
        cls.ReleaseOneHourTips()

    ReleaseIdleTips = classmethod(ReleaseIdleTips)
    
    def ReleaseTenMinTips(cls):
        if cls.s_TenMinTimer:
            cls.s_TenMinTimer.Release()
            cls.s_TenMinTimer = None
        

    ReleaseTenMinTips = classmethod(ReleaseTenMinTips)
    
    def ReleaseOneHourTips(cls):
        if cls.s_OneHourTimer:
            cls.s_OneHourTimer.Release()
            cls.s_OneHourTimer = None
        

    ReleaseOneHourTips = classmethod(ReleaseOneHourTips)
    
    def SetIdleTips(cls):
        cls.SetTenMinTips()
        cls.SetOneHourTips()

    SetIdleTips = classmethod(SetIdleTips)
    
    def SetTenMinTips(cls):
        cls.ReleaseTenMinTips()
        
        def GetTips(obj):
            import netcommon
            import hero
            if hero.g_Prop and hasattr(hero.g_Prop, 'm_Grade'):
                if hero.g_Prop.m_Grade <= hero.g_Prop.m_Grade:
                    pass
                elif hero.g_Prop.m_Grade <= 80:
                    netcommon.C2SGetTdleTips(1)
                    return ()
                

        cls.s_TenMinTimer = :='6!52ce.CBaseObject(None)
        cls.s_TenMinTimer.CreatePyCommand(18000, GetTips)

    SetTenMinTips = classmethod(SetTenMinTips)
    
    def SetOneHourTips(cls):
        cls.ReleaseOneHourTips()
        
        def SetTips(obj):
            import hero
            if hero.g_Prop and hasattr(hero.g_Prop, 'm_Grade') and hero.g_Prop.m_Grade <= 80 and cls.s_TipsTimes < 3:
                import mainmenu
                mainmenu.ShowCalendarTips('\xacd\xac\xdd\xa4\xb5\xa4\xe9\xa5i\xa5H\xb6i\xa6\xe6\xaa\xba\xb9C\xc0\xb8\xa4\xba\xaee')
                cls.s_TipsTimes += 1
                return ()
            

        cls.s_OneHourTimer = :='6!52ce.CBaseObject(None)
        cls.s_OneHourTimer.CreatePyCommand(108000, SetTips)

    SetOneHourTips = classmethod(SetOneHourTips)
    
    def S2CTaskData(cls, netobj):
        shimenCount = netobj.UnpackInt(1)
        doubleExp = netobj.UnpackInt(4)
        fubenCount = netobj.UnpackInt(1)
        tipsLst = []
        import hero
        if tipsLst:
            import random
            idx = random.randint(0, len(tipsLst) - 1)
            import chatoutput
            chatoutput.AddChat(tipsLst[idx])
        

    S2CTaskData = classmethod(S2CTaskData)
