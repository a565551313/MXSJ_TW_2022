# pycdc 交叉复核产物 · script.fls entry 4939
# co_filename(原始)='script/mxgame/activity/sevendaybonus/dlgsevendaybonus.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:03Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4939.pyc (Python 2.5)

import avatar
import combdialog
import dgtsevendaybonus
import dlginfo
import dlgnpc
import interface
import misc
import slot
import ui
import wrapinterface
THE_RULE = '1.2021\xa6~4\xa4\xeb29\xa4\xe99:00-5\xa4\xeb12\xa4\xe924:00\xabe\xa1A\xb5\xa5\xaf\xc5\xa1\xd930\xaf\xc5\xaa\xba\xaa\xb1\xaea\xba\xa1\xa8\xac\xbb\xe2\xa8\xfa\xb1\xf8\xa5\xf3\xab\xe1\xa5i\xc2I\xc0\xbb\xa9\xe2\xbc\xfa\xbb\xe2\xa8\xfa\xac\xdb\xc0\xb3\xaa\xba\xbc\xfa\xc0y\xa1C#n#r2.\xac\xa1\xb0\xca\xb4\xc1\xb6\xa1\xa6@\xa6\xb3\xa4C\xa4\xd1\xb5n\xb3\xb0\xbc\xfa\xc0y\xa1A\xaa\xb1\xaea\xb2\xd6\xadp\xb5n\xb3\xb0\xa4\xd1\xbc\xc6\xa9M\xb2\xd6\xadp\xac\xa1\xc5D\xab\xd7\xa7\xa1\xb9F\xa8\xec\xadn\xa8D\xab\xe1\xa7Y\xa5i\xa6b\xac\xdb\xc0\xb3\xaa\xba\xbc\xfa\xc0y\xa6\xc0\xa4\xa4\xc0H\xbe\xf7\xa9\xe2\xa8\xfa\xbc\xfa\xc0y\xa1C#n#r3.5\xa4\xeb13\xa4\xe99:00-5\xa4\xeb16\xa4\xe924:00\xb6}\xb1\xd2\xb8\xc9\xbb\xe2\xac\xa1\xb0\xca\xa1A\xb4\xc1\xb6\xa1\xb0\xd1\xbbP\xb9L\xb3\xd2\xb0\xca\xb8`\xa9\xe2\xbc\xfa\xa5B\xa5\xbc\xbb\xe2\xa8\xfa\xa7\xb97\xa6\xb8\xbc\xfa\xc0y\xaa\xba\xaa\xb1\xaea\xa5i\xaa\xe1\xb6O\xa4@\xa9w\xaa\xba\xa5N\xbb\xf9\xb8\xc9\xbb\xe2\xac\xdb\xc3\xf6\xbc\xfa\xc0y\xa1C#n#r'
HIDE_NODE_NAME = [
    'rtxt_huoyue',
    'text_shuoming']

def BuildSubWnd(oParent):
    return CSevenDayBonusDlg(oParent)


def OpenSevenDayBonusDlg():
    '''
\t:rtype: CSevenDayBonusDlg
\t'''
    CSevenDayBonusDlg.OpenUI()
    return CSevenDayBonusDlg.GetUI()


class CSevenDayBonusDlg(combdialog.CCombSubWnd, slot.ISignalSubject):
    sUIName = 'dialog4/activity/7day/choujiang.dlg'
    dOpenUIConfig = {
        'KEY_IS_IGNORE_ESC': True }
    SS_CheckBonus = 'SS_CheckBonus()'
    SS_ClickPreShowBtn = 'SS_ClickPreShowBtn(iIdx)'
    SS_ChangeActive = 'SS_ChangeActive(bActive)'
    SS_EnterDayBtn = 'SS_EnterDayBtn(iIdx)'
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent)
        self.ssInit()
        self.m_oExpandTriangle = []
        self.m_oDayButton = []
        self.m_DelegateList = []
        self.m_iLastExpandTriangleIdx = None
        self.m_oSpecialFlashObj = None
        self.m_oLegendTbHandle = None
        self.m_oExpandTriangle = []
        self.m_oRewardImg = []
        self.m_oItemFlashObj = None
        self.m_oPhoto = None
        self.m_iCheckInday = 0
        self.InitDelegate()

    
    def InitDelegate(self):
        self.m_DelegateList = [
            dgtsevendaybonus.CSevenDayBonusDgt(self)]

    
    def SetActive(self, bActive):
        self.ssEmit(self.SS_ChangeActive, bActive)

    
    def GetRewardFrame(self):
        '''
\t\t:rtype: combdialog.CImagesFrame
\t\t'''
        return self.GetObject('img_item1')

    
    def InitReward(self, oRewardDataList):
        oRewardFrame = self.GetRewardFrame()
        self.m_oRewardImg = []
        for iIdx, oRewardData in enumerate(oRewardDataList):
            iShape = oRewardData[0]
            iQuantity = oRewardData[2]
            oImg = CRewardItemIcon(oRewardFrame.GetImageByIndex(iIdx), iShape, iQuantity, iShape)
            interface.Center(oImg)
            self.m_oRewardImg.append(oImg)
        

    
    def InitLegend(self):
        self.m_oLegendTbHandle = CLegendTableViewHandle(self.GetObject('tebview_chuanwen'))
        self.m_oLegendTbHandle.RefreshList([])

    
    def SetLegend(self, lstData):
        self.m_oLegendTbHandle.RefreshList(lstData)

    
    def AddLegend(self, oData):
        self.m_oLegendTbHandle.AddList(oData)

    
    def SetSomeNodeShow(self, bShow):
        for sName in HIDE_NODE_NAME:
            self.SetShowObject(sName, bShow)
        

    
    def InitExpandTriangle(self, iDay):
        self.m_oExpandTriangle = []
        for iIdx in range(7):
            oItem = self.GetObject('img_xiabiao%d' % (iIdx + 1))
            oItem.SetShow(iDay == iIdx)
            self.m_oExpandTriangle.append(oItem)
        
        self.m_iLastExpandTriangleIdx = iDay

    
    def SwitchExpandTriangle(self, iIdx):
        if self.m_iLastExpandTriangleIdx is not None:
            self.m_oExpandTriangle[self.m_iLastExpandTriangleIdx].SetShow(False)
        
        self.m_oExpandTriangle[iIdx].SetShow(True)
        self.m_iLastExpandTriangleIdx = iIdx

    
    def InitDayButton(self):
        for iIdx in range(1, 8):
            oBtn = self.GetObject('txtbtn_%dday' % iIdx)
            self.m_oDayButton.append(oBtn)
        

    
    def SetButtonStatus(self, iIdx, iStatus):
        self.m_oDayButton[iIdx].SetFrame(iStatus)

    
    def SetAllButtonEnable(self, bEnable, iDay = -1):
        '''
\t\t:param bEnable:
\t\t:param iDay: \xafS\xae\xed\xb3B\xb2z\xad\xb6\xa4@\xaa\xbd\xac\xb0True
\t\t:return:
\t\t'''
        for iIdx, oBtn in enumerate(self.m_oDayButton):
            oBtn.Enable(bEnable)
            if iDay > 0 and iDay == iIdx:
                oBtn.Enable(True)
                continue
        

    
    def SetAllButtonStatus(self, iDay, bShow = True):
        for iIdx, oBtn in enumerate(self.m_oDayButton):
            oBtn.Enable(True)
            oBtn.SetClickNotSetFrame(iIdx > iDay)
            None(oBtn.SetFrame if iIdx > iDay else 0)
        
        self.SetSpecialFlashShow(bShow, iDay)

    
    def SetPoint(self, iPoint):
        self.GetObject('rtxt_huoyue').SetText('\xb2\xd6\xbfn\xac\xa1\xc5D\xab\xd7\xa1G%d' % iPoint)

    
    def SetDayBtnTips(self, sText):
        for oBtn in self.m_oDayButton:
            oBtn.SetTips(sText)
        

    
    def SetItemFlashShow(self, bShow, iIdx):
        if bShow:
            oRewardFrame = self.GetRewardFrame()
            oItem = oRewardFrame.GetImageByIndex(iIdx)
            oFlash = interface.CSpriteObject(oItem, '\xd4\xd3\xcd\xbc/\xce\xef\xc6\xb7\xb1\xdf\xbf\xf2\xc1\xf7\xb9\xe2.spr', 'interface')
            interface.Center(oFlash, offsetx = 30, offsety = 30)
            oFlash.SetZ(oItem.GetZ() + 50)
            oFlash.CreateCommand(1, 'animation')
        else:
            oFlash = None
        self.m_oItemFlashObj = oFlash

    
    def SetSpecialFlashShow(self, bShow, iDay):
        if bShow:
            oBtn = self.m_oDayButton[iDay]
            oFlash = ui.CImage(oBtn, 'combdialog4\\\xc3\xce\xcf\xeb3\xbb\xee\xb6\xaf\\\xc6\xdf\xc8\xd5\xb5\xc7\xc2\xbc\\\xb7\xd6\xd2\xb3\xb1\xdf\xbf\xf2\xc1\xf7\xb9\xe2.igs', 'interface')
            interface.Center(oFlash, offsetx = 28, offsety = 39)
            oFlash.SetZ(11)
            oFlash.CreateCommand(1, 'animation')
        else:
            oFlash = None
        self.m_oSpecialFlashObj = oFlash

    
    def SetProgress(self, iRatio):
        oProgress = self.GetObject('progress_huoyue')
        oProgress.SetRate(iRatio)

    
    def SetBonusStatus(self, sStatus):
        self.GetObject('btn_go').SetText(sStatus)

    
    def CanClose(self):
        self.SetActive(False)
        return True

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.ssEmit(self.SS_CheckBonus)
        elif iMsgID in set(range(2, 9)):
            iIdx = iMsgID - 2
            self.ssEmit(self.SS_ClickPreShowBtn, iIdx)
        elif iMsgID == 9:
            sText = THE_RULE
            dlgnpc.ShowClientDlg(sText, '', None)
        



class CRewardItemIcon(wrapinterface.CItemIcon):
    
    def __init__(self, oParent, iShape, iQuantity, iMsgID):
        wrapinterface.CItemIcon.__init__(self, oParent, iShape, iQuantity, iMsgID)
        self.m_oItemTips = None

    
    def Leave(self):
        wrapinterface.CItemIcon.Leave(self)
        self.m_oItemTips = None

    
    def Enter(self):
        del CItemIcon
        self
        self.m_oItemTips = wrapinterface.CItemTips(self.m_Shape, self.m_Path, self.m_Name, self.m_Info, self.m_InfoExt, charcount = 32)



class CNameItem(combdialog.CCombSubWnd):
    sUIName = 'dialog4/activity/7day/chuanwen.dlg'
    dOpenUIConfig = {
        'KEY_IS_IGNORE_ESC': True }
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent)
        self.m_oData = None
        (iX, iY, iW, iH) = self.GetLocData('text_name')
        oText = self.GetObject('text_name')
        sText = oText.GetText()
        iFont = oText.GetFont()
        iColor = oText.GetColor()
        self.m_oRollText = wrapinterface.CRollTextEx(self, iW, iH, iX, iY, sText, iFont, iColor, interface.ALIGN_LEFT_TOP)
        self.m_oRollText.SetPassUp(True)

    
    def SetName(self, sName):
        self.m_oRollText.SetText(sName)
        (iW, iH) = self.m_oRollText.GetTextSize()
        (iX, iY) = self.m_oRollText.GetPos()
        oText = self.GetObject('text_nam1')
        oText.SetPos(iX + iW, iY)

    
    def SetReward(self, sReward, iAmount):
        self.GetObject('rtxt_jiangli').ReplaceText({
            '$iAmount': str(iAmount),
            '$sReward': sReward })

    
    def SetAvatar(self, oDataList):
        (sName, iPlayerID, oAvatar, sItem, iAmount, oFrm) = oDataList
        (p1, p2, p3, p4) = oAvatar
        oPhoto = avatar.GetSmallImgBy4Int(self.GetObject('loc_touxiang'), p1, p2, p3, p4, scale = 0.7)
        (iX, iY, iW, iH) = self.GetLocData('loc_touxiang')
        oPhoto.SetSize(iW, iH)
        avatar.UpdateAvatarPal(oPhoto, iPlayerID)
        self.m_oPhoto = oPhoto

    
    def SetData(self, oDataList):
        self.m_oData = oDataList
        self.SetName(oDataList[0])
        self.SetReward(oDataList[3], oDataList[4])
        self.SetAvatar(oDataList)

    
    def RightUp(self):
        dlginfo.ShowInfoDialog(self.m_oData[1])

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            dlginfo.ShowInfoDialog(self.m_oData[1])
        



class CLegendTableViewHandle(object):
    
    def __init__(self, oTable):
        self.m_oTbview = oTable
        oTable.Enable(False)
        oTable.GetContainer().Enable(False)
        self.InitTableView()

    
    def GetTable(self):
        '''
\t\t:rtype: tableview.CTableView
\t\t'''
        return self.m_oTbview

    
    def InitTableView(self):
        self.GetTable().SetColumnNumber(1)
        self.GetTable().SetDelegateNewCellOfData(misc.Functor(self.OnDelegateNewCellOfData))
        self.GetTable().SetDelegateUpdateCellOfData(misc.Functor(self.OnDelegateUpdateCellOfData))
        self.GetTable().SetDelegateAlignOfData(misc.Functor(self.OnDelegateAlignOfData))
        self.GetTable().SetScorllBarShow(False)
        self.GetTable().SetShowBgLine(False)

    
    def CreateItem(self, oParent):
        return CNameItem(oParent)

    
    def UpdateItem(self, oItem, dData):
        oItem.SetData(dData)

    
    def OnDelegateNewCellOfData(self, oParent, dData):
        oItem = self.CreateItem(oParent)
        self.UpdateItem(oItem, dData)
        return oItem

    
    def OnDelegateUpdateCellOfData(self, oCell, dData, bReUes):
        if bReUes:
            self.UpdateItem(oCell, dData)
        

    
    def OnDelegateAlignOfData(self, dData):
        return interface.ALIGN_LEFT_TOP

    
    def RefreshList(self, dDatalst):
        oTable = self.GetTable()
        oTable.SetDataSource(dDatalst)
        oTable.Reload()

    
    def AddList(self, dData):
        oTable = self.GetTable()
        dDatalst = oTable.GetDataSource()
        dDatalst.append(dData)
        oTable.Reload(tUpdateIdxes = (len(dDatalst),))
