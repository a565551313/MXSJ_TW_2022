# pycdc 交叉复核产物 · script.fls entry 252
# co_filename(原始)='script/dialog/mubanhao/componentclass.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_252.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2021/4/13 16:55
\xd7\xf7\xd5\xdf: lzj
\xce\xc4\xbc\xfe: componentclass
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import combmacro
import interface
import misc
import ui
import usermacro
import time

class CNumberEdit(interface.CBoxObject):
    
    def __init__(self, ViXKent, sObjName, iMinNum, iMaxNum, iDefaultNum = 0, iDelayTime = 0, iStep = 1, iID = 0, oChangeCB = None, iOfferX = 0, iAligh = 0, sLeftTips = None, sRightTips = None):
        '''
\t\t:param oParent:
\t\t:param sObjName:
\t\t:param iMinNum:
\t\t:param iMaxNum:
\t\t:param iMinNum:
\t\t:param iMaxNum:
\t\t:param iDefaultNum:
\t\t:param iDelayTime:
\t\t:param iStep:
\t\t:param iID:
\t\t:param oChangeCB:
\t\t:param iOfferX:
\t\t:param iAligh:
\t\t:param sLeftTips:
\t\t:param sRightTips:
\t\t'''
        interface.CBoxObject.__init__(self, ViXKent, 0, 0, 0, 0)
        self.m_iMinNum = iMinNum
        self.m_iMaxNum = iMaxNum
        self.m_iCurNum = iDefaultNum
        self.m_iStep = iStep
        self.m_iID = iID
        self.m_oChangeCB = oChangeCB
        self.m_sLeftTips = sLeftTips
        self.m_sRightTips = sRightTips
        self.m_iDelayTime = iDelayTime
        self.m_iEnterTime = 0
        self.m_oDelayCmd = None
        self.InitInputEdit(ViXKent, sObjName, iAligh)
        self.SetEditText(iDefaultNum)
        self.InitBtn(ViXKent, sObjName, iOfferX)

    
    def SetShow(self, iShow):
        interface.CBoxObject.SetShow(self, iShow)
        self.m_oEdit.SetShow(iShow)

    
    def InitInputEdit(self, ViXKent, sObjName, iAligh):
        self.m_oEdit = combmacro.CEDIT(ui.CNumberEdit, sObjName, ViXKent, interface.COLOR_5, interface.FontLT14_3, interface.COLOR_5)
        self.m_oEdit.SetCharChangeCB(misc.Functor(self.OnEditNumChange))
        self.m_oEdit.SetTextAlign(iAligh)
        self.m_oEdit.SetPassScrollingMessagesUp(True)

    
    def InitBtn(self, ViXKent, sObjName, iOfferX):
        (iH, _) = ViXKent.GetObject(sObjName).GetSize()
        (iX, iY) = ViXKent.GetObject(sObjName).GetPos()
        self.m_oLeftBtn = interface.CButton(self, 'combdialog4/\xc8\xfd\xcc\xac\xb0\xb4\xc5\xa5/\xbc\xf5\xba\xc5', iX - 19 - iOfferX, iY, msgid = 1, width = 0)
        self.m_oRightBtn = interface.CButton(self, 'combdialog4/\xc8\xfd\xcc\xac\xb0\xb4\xc5\xa5/\xbc\xd3\xba\xc51', iX + iH + 1 + iOfferX, iY, msgid = 2, width = 0)

    
    def OnEditNumChange(self):
        self.m_iEnterTime = time.time()
        if not self.m_oDelayCmd:
            
            def DelayFind(oObj):
                iCurTime = time.time()
                if iCurTime - oObj.m_iEnterTime > oObj.m_iDelayTime:
                    iCurNum = oObj.m_oEdit.GetNumber()
                    if oObj.m_iCurNum != iCurNum:
                        oObj.RefreshEditText(iCurNum, True)
                    
                    oObj.m_oDelayCmd = None
                else:
                    return ()

            self.m_oDelayCmd = self.CreatePyCommand(1, DelayFind)
        

    
    def RefreshEditText(self, iNumber, bSetNumberText):
        self.ShowOutOfRangeTips(iNumber)
        self.m_iCurNum = self.GetVaildNumber(iNumber)
        if bSetNumberText:
            self.SetEditText(self.m_iCurNum)
        

    
    def SetMaxNum(self, iNum):
        self.m_iMaxNum = iNum

    
    def SetMinNum(self, iNum):
        self.m_iMinNum = iNum

    
    def SetEditText(self, iNumber):
        self.m_iCurNum = iNumber
        self.m_oEdit.SetNotCBChangeCharLock(True)
        self.m_oEdit.SetText(str(iNumber))
        self.m_oEdit.SetNotCBChangeCharLock(False)
        if self.m_oChangeCB:
            self.m_oChangeCB(self.m_iID, iNumber)
        

    
    def SetColor(self, iColor):
        self.m_oEdit.SetTextColor(iColor)
        iNum = self.GetCurNum()
        self.m_oEdit.SetNotCBChangeCharLock(True)
        self.m_oEdit.SetText(str(iNum))
        self.m_oEdit.SetNotCBChangeCharLock(False)

    
    def SetLeftTips(self, sTips):
        self.m_sLeftTips = sTips

    
    def SetRightTips(self, sTips):
        self.m_sRightTips = sTips

    
    def SetActive(self, bActive):
        self.m_oEdit.Active(bActive)

    
    def GetCurNum(self):
        return self.m_iCurNum

    
    def GetVaildNumber(self, iNumber):
        if iNumber < self.m_iMinNum:
            return self.m_iMinNum
        
        if iNumber > self.m_iMaxNum:
            return self.m_iMaxNum
        
        return iNumber

    
    def ShowOutOfRangeTips(self, iNumber):
        if iNumber < self.m_iMinNum:
            sText = self.m_sLeftTips
        elif iNumber > self.m_iMaxNum:
            sText = self.m_sRightTips
        else:
            sText = None
        if sText:
            usermacro.PROMPT_MSG(sText)
        

    
    def MouseWheelDown(self, iOffSet):
        if getattr(self.GetParent(), 'MouseWheelDown', None):
            None.GetParent().MouseWheelDown(iOffSet)
        

    
    def MouseWheelUp(self, iOffSet):
        if getattr(self.GetParent(), 'MouseWheelUp', None):
            self.GetParent().MouseWheelUp(iOffSet)
        

    
    def OnMessage(self, iMsg):
        if iMsg == 1:
            self.RefreshEditText(self.m_iCurNum - self.m_iStep, True)
        elif iMsg == 2:
            self.RefreshEditText(self.m_iCurNum + self.m_iStep, True)
        elif iMsg == interface.RIGHT_BUTTON_MESSAGE + 1:
            self.RefreshEditText(self.m_iMinNum, True)
        elif iMsg == interface.RIGHT_BUTTON_MESSAGE + 2:
            self.RefreshEditText(self.m_iMaxNum, True)
