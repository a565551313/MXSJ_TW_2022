# pycdc 交叉复核产物 · script.fls entry 141
# co_filename(原始)='script/dialog/qixi/qixitest.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_141.pyc (Python 2.5)

import dlgqiximain
import mdmvpnormal
import qixidefine
import testbaseobj

def OnUpdateOneTask(sTaskName, iCurProgress, iMaxProgress):
    dInfo = mdmvpnormal.GetNormalMdMgr(mdmvpnormal.TYPE_QIXI_TASKLIST)
    tOldTaskLst = dInfo.GetMdData(mdmvpnormal.TYPE_QIXI_TASKLIST).get('iTaskLst', [])
    for idx, tTaskInfo in enumerate(tOldTaskLst):
        if tTaskInfo[0] == sTaskName:
            tOldTaskLst[idx] = (sTaskName, int(iCurProgress), int(iMaxProgress))
            break
            continue
    
    dInfo.SetMdData(mdmvpnormal.TYPE_QIXI_TASKLIST, dInfo.GetMdData(mdmvpnormal.TYPE_QIXI_TASKLIST))


class CTestFunc(testbaseobj.CTestBase):
    
    def TestOpenDlg(cls, iPage):
        '''
\t\t\xa5\xb4\xb6}\xa4C\xa4i\xac\xc9\xad\xb1
\t\t\xad\xb6\xc3\xb1(1)
\t\t'''
        iPage = int(iPage)
        mdmvpnormal.GetNormalMdMgr(mdmvpnormal.TYPE_QIXI_MAIN).SetMdData(qixidefine.KEY_MAIN_OPENPAGE, iPage)
        dlgqiximain.CQiXiMainDlg.\xa4\x9benUI()

    TestOpenDlg = classmethod(TestOpenDlg)
    
    def TestCheckRangeType(cls, bCheckRangeType):
        '''
\t\t\xb2K\xa5[\xc0\xcb\xacd\xa5\xb4\xa6L
\t\t\xacO\xa7_\xc5\xe3\xa5\xdc(0\xa9\xce1)
\t\t'''
        bCheckRangeType = bool(int(bCheckRangeType))
        import qixirangecheckctrl
        qixirangecheckctrl.CQiXiRangeCheckCtrl.DEBUG = bCheckRangeType

    TestCheckRangeType = classmethod(TestCheckRangeType)
    
    def TestCheckUpdateTask(cls, sName, iCur, iMax):
        '''
\t\t\xa8\xea\xb7s\xa5\xf4\xb0\xc8\xaa\xac\xbaA
\t\t\xa5\xf4\xb0\xc8\xa6W\xa6r \xb7\xed\xabe\xb6i\xab\xd7 \xb3\xcc\xa4j\xb6i\xab\xd7
\t\t'''
        OnUpdateOneTask(sName, iCur, iMax)

    TestCheckUpdateTask = classmethod(TestCheckUpdateTask)
    
    def TestMatchState(cls, iState):
        '''
\t\t\xa8\xea\xb7s\xa5\xf4\xb0\xc8\xaa\xac\xbaA
\t\t\xa5\xf4\xb0\xc8\xa6W\xa6r
\t\t'''
        import qixirangecheckctrl
        qixirangecheckctrl.SetMatchState(int(iState))

    TestMatchState = classmethod(TestMatchState)
