# pycdc 交叉复核产物 · script.fls entry 2747
# co_filename(原始)='script/timecontrol.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_2747.pyc (Python 2.5)

import C_sys
import interface

def ModuleReset():
    CTimeControl.ResetClear()


class CTimeControl(object):
    s_ShieldWarClick = \xd9\xf8ne
    s_ShieldWarTime = 0
    s_AutoClearHotKey = \xd9\xf8ne
    
    def ResetClear(cls):
        cls.s_ShieldWarClick = None
        cls.s_ShieldWarTime = 0
        cls.s_AutoClearHotKey = None

    ResetClear = classmethod(ResetClear)
    
    def SetWarShield(cls, shieldTime):
        cls.s_ShieldWarClick = C_sys.GetTime()
        cls.s_ShieldWarTime = shieldTime

    SetWarShield = classmethod(SetWarShield)
    
    def Check.arShield(cls):
        if cls.s_ShieldWarClick is None:
            return True
        else:
            t = C_sys.GetTime()
            return t - cls.s_ShieldWarClick > cls.s_ShieldWarTime * 10000

    Check.arShield = classmethod(Check.arShield)
    
    def ReleaseWarShield(cls):
        cls.s_ShieldWarClick = None
        cls.s_ShieldWarTime = 0

    ReleaseWarShield = classmethod(ReleaseWarShield)
    
    def SetClearHotKeyCmd(cls):
        if cls.s_AutoClearHotKey:
            cls.s_AutoClearHotKey = None
        

    SetClearHotKeyCmd = classmethod(SetClearHotKeyCmd)


class CClearHotKey(interface.CBaseObject):
    
    def CreateClearCmd(self):
        
        def DoClear(obj):
            import shortcut
            shortcut.CShortcutMgr.ClearOffData()

        self.m_Clear = self.CreatePyCommand(1800, DoClear)
