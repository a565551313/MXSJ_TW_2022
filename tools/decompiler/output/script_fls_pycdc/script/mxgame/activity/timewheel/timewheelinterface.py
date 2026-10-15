# pycdc 交叉复核产物 · script.fls entry 2070
# co_filename(原始)='script/mxgame/activity/timewheel/timewheelinterface.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2070.pyc (Python 2.5)

import timewheelcontext
import misc
import permission

def GetTimeWheelContext():
    ''':rtype: timewheelcontext.CTimeWheelContext'''
    return timewheelcontext.GetContext()


def GetTimeWheelDataMgr():
    ''':rtype: timewheeldatamgr.CTimeWheelDataMgr'''
    oContext = GetTimeWheelContext()
    return oContext.GetTimeWheelDataMgr()


def GetTimeWheelTaskDelegateDataMgr():
    ''':rtype: mdtimewheelweituo.CTimeWheelWeituoMd'''
    oContext = GetTimeWheelContext()
    return oContext.GetTimeWheelTaskDelegateDataMgr()


def ShowTimeWheelDlg(iPage, dExtend = None):
    oContext = GetTimeWheelContext()
    oContext.ShowTimeWheelDlg(iPage, dExtend)


def ShowRecordTimeWheelDlg():
    oContext = GetTimeWheelContext()
    oContext.ShowRecordTimeWheelDlg()


def SetRecordTimeWheelDlg(iPage, dExtend = None):
    oContext = GetTimeWheelContext()
    oContext.SetRecordPage(iPage, dExtend)


def ShowTimeWheelPublishDlg(iMode):
    oContext = GetTimeWheelContext()
    oContext.ShowWeituoPublishDlgNew(iMode)


def CloseTimeWheelDlg():
    for None in GetTimeWheelContext():
        return None


def ShowWeiTuoGetDlg(iType, bAutoSelect):
    oContext = GetTimeWheelContext()
    oContext.ShowWeituoGetDlg(iType, bAutoSelect)


def ShowQuickGetWeituoRreward():
    oContext = GetTimeWheelContext()
    oContext.ShowQuickGetWeituoRreward()


def CloseWeiTuoGetDlg():
    oContext = GetTimeWheelContext()
    oContext.CloseWeituoGetDlg()


def IsOpenWeituo():
    if misc.IsFreshManServer():
        return False
    
    if CheckIsOpenWeituo_Level():
        pass
    return CheckIsOpenWeituo_WarKuafu()


def CheckIsOpenWeituo_WarKuafu():
    import misc
    import mainmenu
    if misc.IsInKuafuServer():
        return False
    else:
        return True


def CheckIsOpenWeituo_Level():
    import hero
    return hero.GetProp('m_Grade') >= 25


def CheckIsOpenSpecial():
    import hero
    return hero.GetProp('m_Grade') >= 25


def CheckIsHaveEntrustReward():
    oEntrustMgr = GetTimeWheelTaskDelegateDataMgr()
    bHaveReward = oEntrustMgr.GetEntrustRewardRedDot()
    return bHaveReward
