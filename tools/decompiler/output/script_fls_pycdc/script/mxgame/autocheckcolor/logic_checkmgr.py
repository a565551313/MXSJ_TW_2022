# pycdc 交叉复核产物 · script.fls entry 1299
# co_filename(原始)='script/mxgame/autocheckcolor/logic_checkmgr.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1299.pyc (Python 2.5)

'''
======================================================
\xb5\xda\xd2\xbb\xb2\xbd\xa3\xba======
\xbc\xec\xb2\xe2\xb2\xbd\xd6\xe8
\t\xbc\xec\xcb\xf7\xbd\xe7\xc3\xe6\xb1\xb3\xbe\xb0\xc2\xb7\xbe\xb6\xa3\xac\xb6\xd4\xd3\xa6\xb5\xc4\xc2\xb7\xbe\xb6\xca\xc7\xb7\xf1\xd4\xda\xb5\xbc\xb1\xed\xd6\xd0
\tpath = {
\t\t"obj": oObj
\t\t"path1": path1,
\t\t"path2": path2,
\t}
\tUI\xb6\xd4\xcf\xf3 +
\t\xbc\xec\xcb\xf7 \xce\xc4\xb1\xbe+\xb8\xbb\xce\xc4\xb1\xbe\xa1\xa3

\xb5\xda\xb6\xfe\xb2\xbd:
\t\xb3\xf5\xb0\xe6 \xc5\xd0\xb6\xcf\xd1\xd5\xc9\xab\xc6\xa5\xc5\xe4\xa1\xa3

\xb5\xda\xc8\xfd\xb2\xbd\xa3\xba
\t\xb3\xf5\xb0\xe6 \xb6\xfe\xb4\xce\xbc\xec\xb2\xe2\xb9\xfd\xc2\xcb\xa3\xac\xc6\xe4\xcb\xfcUI\xb8\xb2\xb8\xc7\xa1\xa3
\t\xb3\xf5\xb0\xe6 \xbe\xcd\xc4\xc7\xc3\xb4\xa1\xa3
============================================================
'''
import usermacro
import misc
import autocheckinterface
MAX_CHECK_TIME = 100000
CHECK_NEED_PROP = ('sType', 'sID', 'wrDlg', 'lText', 'lRichText', 'iCheckTime')

class CLogicCheckMgr(object):
    
    def __init__(self):
        self.m_lCheckQueue = []
        self.m_dCheckContainer = { }
        self.m_lCheckResult = []

    
    def GetContext(self):
        ''':rtype:autocheckmgr.CAutoCheckMgr'''
        import autocheckinterface
        return autocheckinterface.GetCheckMgr()

    
    def AddRichText2CheckLogic(self, sKey, wrRichText):
        dDlgConfig = self.m_dCheckContainer.get(sKey, None)
        if not dDlgConfig:
            return None
        
        lRichText = dDlgConfig['lRichText']
        lRichText.append(wrRichText)

    
    def AddNormalText2CheckLogic(self, sKey, wrNormalText):
        dDlgConfig = self.m_dCheckContainer.get(sKey, None)
        if not dDlgConfig:
            return None
        
        lText = dDlgConfig['lText']
        lText.append(wrNormalText)

    
    def Add2CheckQueue(self, oDlg):
        if not oDlg:
            return None
        
        sType = autocheckinterface.GetDlgUnitTypeID(oDlg)
        sKey = autocheckinterface.GetCheckUniqueID(oDlg)
        if sKey in self.m_lCheckQueue:
            return None
        
        oContext = self.GetContext()
        oCheckBgLogic = oContext.GetCheckBgLogic()
        dResult = oCheckBgLogic.CheckDlgDestBg(oDlg)
        LOG('\xadJ\xaa\xe2\xb5Yautocheck:', dResult)
        if dResult:
            dResult['sType'] = sType
            dResult['sID'] = sKey
            dResult['wrDlg'] = misc.WeakRef(oDlg)
            dResult['lText'] = []
            dResult['lRichText'] = []
            self.m_dCheckContainer[sKey] = dResult
            self.m_lCheckQueue.append(sKey)
        

    
    def CheckLoop(self):
        if not self.m_lCheckQueue:
            return None
        
        lCheckQueue = []
        dCheckContainer = { }
        lDest = []
        sDest = ''
        for sKey in self.m_lCheckQueue:
            dCheckData = self.m_dCheckContainer[sKey]
            if not dCheckData:
                continue
            
            iCheckTime = dCheckData.get('iCheckTime', 0) + 1
            dCheckData['iCheckTime'] = iCheckTime
            sType = dCheckData['sType']
            (sDest, bContinue) = self.CheckIsDestDlg(dCheckData)
            if sDest:
                lDest.append(sType)
                if sType not in self.m_lCheckResult:
                    self.m_lCheckResult.append(sType)
                
            sType not in self.m_lCheckResult
            if bContinue and iCheckTime < MAX_CHECK_TIME:
                lCheckQueue.append(sKey)
                dCheckContainer[sKey] = dCheckData
                continue
        
        self.m_lCheckQueue = lCheckQueue
        self.m_dCheckContainer = dCheckContainer
        if sDest:
            (sTxt, tColor, sDlgPath) = sDest
            iColor = autocheckinterface.RGBColor2Int(tColor)
            sColor = '%s' % hex(iColor)
            sSend = '%s %s %s' % (sDlgPath, sTxt, sColor)
            self.SendLog(sSend)
        

    
    def CheckIsDestDlg(self, dCheckData):
        '''\xa7P\xc2_\xb7\xed\xabe\xac\xc9\xad\xb1\xacO\xa7_\xacO\xa5\xd8\xbc\xd0\xac\xc9\xad\xb1
\t\t1.\xba\xca\xb4\xfadlg\xa4U\xaa\xba \xa4\xe5\xa5\xbb\xa9M\xb4I\xa4\xe5\xa5\xbb\xc3C\xa6\xe2\xa9M\xadI\xb4\xba\xc3C\xa6\xe2\xb2\xd5\xa6X\xacO\xa7_\xac\xb0\xa5\xd8\xbc\xd0\xc3C\xa6\xe2
\t\t:param dCheckData:
\t\t:return \xacO\xa7_\xacO\xa5\xd8\xbc\xd0\xac\xc9\xad\xb1, \xacO\xa7_\xaf\xe0\xc4~\xc4\xf2\xba\xca\xb4\xfa
\t\t'''
        wrDlg = dCheckData['wrDlg']
        oDlg = wrDlg()
        if not oDlg:
            return (False, False)
        elif not None(None, None, None, None, None, None, None, None, None, None, None, None, autocheckinterface.IsUIRealShow, oDlg):
            return (False, True)
        
        lText = dCheckData['lText']
        oTextLogic = self.GetContext().GetCheckNormalTextLogic()
        lDestText = []
        dCheckData['lText'] = lDestText
        for wrText in lText:
            oText = wrText()
            if not oText:
                continue
            
            (bDest, bContinue) = oTextLogic.CheckTextIsDest(oText, dCheckData)
            if not bDest:
                if bContinue:
                    lDestText.append(wrText)
                
            bContinue
            return ((oText.GetText(), bDest, oDlg.GetDlgPath()), False)
        
        lRichText = dCheckData['lRichText']
        lDestRichText = []
        dCheckData['lRichText'] = lDestRichText
        oRichTextLogic = self.GetContext().GetCheckRichTextLogic()
        for wrText in lRichText:
            oText = wrText()
            if not oText:
                continue
            
            (bDest, bContinue) = oRichTextLogic.CheckTextIsDest(oText, dCheckData)
            if not bDest:
                if bContinue:
                    lDestRichText.append(wrText)
                
            bContinue
            return ((oText.GetText(), bDest, oDlg.GetDlgPath()), False)
        
        return (False, True)

    
    def SendLog(self, sMsg):
        import chatoutput
        chatoutput.AddChat('#s(21)\xb7\xed\xabe\xac\xc9\xad\xb1\xc3C\xa6\xe2\xb9L\xb7t\xa9\xce\xb9L\xabG %s' % sMsg)
        import netcommon
        netcommon.C2SSendRemoteLog('autocheckcolor %s' % sMsg)
