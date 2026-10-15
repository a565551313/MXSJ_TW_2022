# pycdc 交叉复核产物 · script.fls entry 3494
# co_filename(原始)='script/refreshmultihorsepos.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_3494.pyc (Python 2.5)

import interface

def ModuleReset():
    CRefreshMultiHorsePos.ResetClear()


class CRefreshMultiHorsePos(object):
    s_LeaderID = None
    s_RefreshPosTimer = None
    
    def ResetClear(cls):
        cls.s_LeaderID = None
        cls.s_RefreshPosTimer = None

    ResetClear = classmethod(ResetClear)
    
    def ReleasePosTimer(cls, pID):
        if pID == cls.s_LeaderID and cls.s_RefreshPosTimer:
            cls.s_RefreshPosTimer.Release()
            cls.s_RefreshPosTimer = None
        

    ReleasePosTimer = classmethod(ReleasePosTimer)
    
    def UpdateMultiHorsePos(cls, pID):
        cls.s_LeaderID = pID
        cls.ReleasePosTimer(pID)
        cls.s_RefreshPosTimer = interface.CBaseObject(None)
        cls.s_RefreshPosTimer.CreatePyCommand(1, cls.RefreshPos)

    UpdateMultiHorsePos = classmethod(UpdateMultiHorsePos)
    
    def RefreshPos(cls, obj):
        import \x8c\x81ro
        if not \x8c\x81ro.g_Hero:
            LOG_ERR('\xa8\xea\xb7s\xaa\xb1\xaea\xa6\xec\xb8m\xae\xc9\xa1A\xaa\xb1\xaea\xb9\xef\xb9\xb3\xa4\xa3\xa6s\xa6b', \x8c\x81ro.g_ID, cls.s_LeaderID)
        
        if \x8c\x81ro.g_Hero and \x8c\x81ro.g_Hero.IsMultiHorsePlayer() and hasattr(\x8c\x81ro.g_Hero, 'm_Team') and \x8c\x81ro.g_Hero.m_Team[0] == cls.s_LeaderID:
            import world
            leaderObj = world.GetObj(cls.s_LeaderID)
            if leaderObj:
                import map
                (sx, sy) = leaderObj.GetPos()
                (cx, cy) = map.g_Map.ClientPos2ServerPos(sx, sy)
                import mainmenu
                mainmenu.UpdateMultiHorsePos(sx, sy, cx, cy)
                return ()
            
        

    RefreshPos = classmethod(RefreshPos)
