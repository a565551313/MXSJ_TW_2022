# pycdc 交叉复核产物 · script.fls entry 3780
# co_filename(原始)='script/debug/dlguiprofile.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3780.pyc (Python 2.5)

import os
import misc
import slot
import combdialog
import showdrawtime
import timer
import interface
import ui
import usermacro

def ShowSwitch():
    if CUIProfileDlg.GetUI():
        CUIProfileDlg.CloseUI()
    elif not hasattr(interface.DialogPanel, 'GetAllChildrens'):
        usermacro.PROMPT_MSG('\xa6\xb9\xa4\xde\xc0\xba\xb5L\xaak\xa8\xcf\xa5\xce\xb8\xd3\xa9R\xa5O')
        return None
    
    CUIProfileDlg.OpenUI()


class CUIProfileDlg(combdialog.CCombDialog):
    MODE_IO = 1
    MODE_RENDER = 2
    sUIName = 'dialog4/profile.dlg'
    
    def __init__(self, oParent):
        combdialog.CCombDialog.__init__(self, oParent)
        self.SetIgnoreEsc(True)
        self.m_oModelDict = {
            self.MODE_IO: CIOProfileModel(),
            self.MODE_RENDER: CRenderProfileModel() }
        for iModeType, oModel in self.m_oModelDict.iteritems():
            oModel.ssConnect(oModel.SS_DataChange, misc.Functor(self.OnDataUpdate, iModeType))
        
        self.m_iCurMode = None
        self.m_dClickInfo = { }
        self.InitTableView()
        self.GetObject('btn_io').LeftUp()

    
    def InitTableView(self):
        oTableView = self.GetObject('table')
        oTableView.SetDelegateNewCellOfData(self.DelegateNewCellOfData)
        oTableView.SetDelegateUpdateCellOfData(self.DelegateUpdateCellOfData)
        oTableView.SetDelegateIdentifierOfData(self.DgtIdentifierOfData)

    
    def DelegateNewCellOfData(self, oContainer, oData):
        if oData['sType'] == 'dlg':
            oCell = CDlgItem(oContainer)
            oCell.SetDetailCB(misc.Functor(self.OnClickDetail))
        else:
            oCell = CWidgteItem(oContainer)
        oCell.SetData(oData)
        return oCell

    
    def DelegateUpdateCellOfData(self, oCell, oData, bReused):
        oCell.SetData(oData)

    
    def DgtIdentifierOfData(self, oData):
        return oData['sType']

    
    def SwitchMode(self, iMode):
        if self.m_iCurMode != iMode:
            self.m_iCurMode = iMode
            self.RefreshTableView()
        

    
    def OnDataUpdate(self, iMode):
        if self.m_iCurMode == iMode:
            self.RefreshTableView()
        

    
    def OnClickDetail(self, iMsgIdx):
        (iMode, sName) = self.m_dClickInfo[iMsgIdx]
        if self.m_oModelDict[iMode].GetShowDetailName() == sName:
            None(self.m_oModelDict[iMode].SetShowDetailName.m_oModelDict)
        else:
            self.m_oModelDict[iMode].SetShowDetailName(sName)
        if iMode == self.m_iCurMode:
            self.RefreshTableView()
        

    
    def RefreshTableView(self):
        dShowInfoList = []
        self.m_dClickInfo = { }
        dInfoList = self.m_oModelDict[self.m_iCurMode].GetAllInfo()
        sDetailName = self.m_oModelDict[self.m_iCurMode].GetShowDetailName()
        iIdx = 100
        for dInfo in dInfoList:
            iIdx += 1
            dShowInfoList.append({
                'sType': 'dlg',
                'sName': dInfo['sName'],
                'sDesc': dInfo['sDesc'],
                'bHasExpand': dInfo['sName'] == sDetailName,
                'iMsgIdx': iIdx })
            self.m_dClickInfo[iIdx] = (self.m_iCurMode, dInfo['sName'])
            if dInfo['sName'] == sDetailName:
                for dSon in dInfo['dSonList']:
                    dShowInfoList.append({
                        'sType': 'widget',
                        'sName': dSon['sName'],
                        'sDesc': dSon['sDesc'],
                        'sTips': dSon['sTips'] })
                
        
        oTableView = self.GetObject('table')
        oTableView.SetDataSource(dShowInfoList)
        oTableView.Reload()

    
    def ClearAllData(self):
        for iModeType, oModel in self.m_oModelDict.iteritems():
            oModel.Clear()
        

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseUI()
        elif iMsgID == 2:
            self.ClearAllData()
        elif iMsgID == 3:
            self.SwitchMode(self.MODE_IO)
        elif iMsgID == 4:
            self.SwitchMode(self.MODE_RENDER)
        



class CDlgItem(interface.CBoxObject):
    SIZE = (400, 20)
    NAME_SIZE = (200, 20)
    DESC_SIZE = (200, 20)
    START_POSX = 0
    
    def __init__(self, oParent):
        interface.CBoxObject.__init__(self, oParent, self.SIZE[0], self.SIZE[1], 0, 0)
        self.m_oDetailCB = None

    
    def SetData(self, dData):
        sName = dData['sName']
        sDesc = dData['sDesc']
        self.m_oNameTxt = ui.CRichTextObject(self, self.NAME_SIZE[0], self.NAME_SIZE[1], sName, interface.FontLT14_3, 4210829, iAlign = interface.ALIGN_LEFT_MIDDLE)
        self.m_oNameTxt.SetPos(self.START_POSX, 0)
        self.m_oDescTxt = ui.CRichTextObject(self, self.DESC_SIZE[0], self.DESC_SIZE[1], sDesc, interface.FontLT14_3, 4210829, iAlign = interface.ALIGN_LEFT_MIDDLE)
        self.m_oDescTxt.SetPos(self.NAME_SIZE[0] + self.START_POSX, 0)
        self.Other(dData)

    
    def Other(self, dData):
        self.m_iCBIdx = dData['iMsgIdx']
        bHasExpand = dData.get('bHasExpand', True)
        if not bHasExpand:
            sTxt = '#u\xb8\xd4\xb1\xa1#n'
        else:
            sTxt = '#u\xa6\xac\xb0_#n'
        dClickInfo = {
            'iEnterColor': 255,
            'iMsgID': 1 }
        self.m_oDetailTxt = ui.CRichTextObject(self, 50, 20, sTxt, interface.FontLT14_3, 255, bClick = True, dClickInfo = dClickInfo)
        self.m_oDetailTxt.SetPos(self.DESC_SIZE[0] + self.NAME_SIZE[0] + self.START_POSX, 0)

    
    def MouseWheelDown(self, p):
        oParent = self.GetParent()
        oParent.MouseWheelDown(p)

    
    def MouseWheelUp(self, p):
        oParent = self.GetParent()
        oParent.MouseWheelUp(p)

    
    def SetDetailCB(self, oCB):
        if oCB and not isinstance(oCB, misc.Functor):
            oCB = misc.Functor(oCB)
        
        self.m_oDetailCB = oCB

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            if self.m_oDetailCB:
                self.m_oDetailCB(self.m_iCBIdx)
            
        



class CWidgteItem(CDlgItem):
    SIZE = (400, 16)
    NAME_SIZE = (200, 16)
    DESC_SIZE = (200, 16)
    START_POSX = 20
    
    def Other(self, dData):
        sTips = dData.get('sTips', None)
        oParent = self.m_oNameTxt
        if sTips:
            (iW, iH) = oParent.GetSize()
            (iX, iY) = oParent.GetPos()
            dUIInfo = {
                'iWidth': iW,
                'iHeight': iH,
                'iTipsDirect': -1,
                'sTips': sTips }
            self.m_oTipsBox = CTipsBox(self, None, dUIInfo)
            self.m_oTipsBox.SetPos(iX, iY)
            self.m_oTipsBox.Topmost()
        else:
            self.m_oTipsBox = None



class CTipsBox(combdialog.CBoxWithTips):
    
    def __init__(self, parent, data, dUIInfo = None):
        combdialog.CBoxWithTips.__init__(self, parent, data, dUIInfo)
        self.SetPassScrollingMessagesUp(1)

    
    def Enter(self):
        import wrapinterface
        if not self.m_TipsStr:
            return None
        
        self.m_TipsObj = wrapinterface.CTextTips(None, self.m_TipsW, self.m_TipsStr, interface.FontLT14_3)
        self.m_TipsObj.SetOwner(self)

    
    def LeftUp(self):
        pass

    
    def LeftDown(self):
        pass

    
    def RightDown(self):
        pass

    
    def RightUp(self):
        pass



class CModelBase(slot.ISignalSubject):
    SS_DataChange = 'OnDataChange()'
    
    def __init__(self):
        self.ssInit()
        self.m_dInfoList = []
        self.m_sShowDetailName = ''
        self.Init()

    
    def SetShowDetailName(self, sShowDetailName):
        self.m_sShowDetailName = sShowDetailName

    
    def GetShowDetailName(self):
        return self.m_sShowDetailName

    
    def Clear(self):
        if self.m_dInfoList:
            self.m_dInfoList = []
            self.EmitUpdate()
        

    
    def Init(self):
        raise NotImplementedError

    
    def EmitUpdate(self):
        self.ssEmit(self.SS_DataChange)

    
    def GetAllInfo(self):
        return self.m_dInfoList



class CIOProfileModel(CModelBase):
    
    def Init(self):
        self.OnCheck(True)
        self.m_oCheckTimer = timer.Timer(1, self.OnCheck, -1)

    
    def OnCheck(self, bFirst = False):
        self.m_dInfoList = []
        for oChild in interface.DialogPanel.GetAllChildrens():
            if isinstance(oChild, (combdialog.CCombDialog, combdialog.CCombPanel)) and not isinstance(oChild, combdialog.CCombSubWnd):
                sName = getattr(oChild, 'm_DlgPath', str(oChild))
                if sName == CUIProfileDlg.sUIName:
                    continue
                
                dPathTime = { }
                self.GetDlgData(oChild, dPathTime)
                iTotalCost = 0
                for dInfo in dPathTime.itervalues():
                    for dEach in dInfo.itervalues():
                        iTotalCost += dEach['iCost']
                    
                
                dInfo = {
                    'sName': sName,
                    'sDesc': 'IO\xc1`\xaf\xd3\xae\xc9: #cED8200%s\xb2@\xac\xed#n' % iTotalCost / 10,
                    'dSonList': [] }
                iTmpPathTime = dPathTime.keys()
                iTmpPathTime.sort()
                for iFrame in iTmpPathTime:
                    iTotalCost = 0
                    for dEach in dPathTime[iFrame].itervalues():
                        iTotalCost += dEach['iCost']
                    
                    dSonInfo = {
                        'sName': '#R\xb2\xc4%s\xb4V#n' % iFrame,
                        'sDesc': 'IO\xc1`\xaf\xd3\xae\xc9: #cED8200%s\xb2@\xac\xed#n' % iTotalCost / 10,
                        'sTips': None }
                    dInfo['dSonList'].append(dSonInfo)
                    tPathTime = dPathTime[iFrame].items()
                    tPathTime.sort(key = (lambda p: -p[1]['iCost']))
                    for sPath, dPath in tPathTime:
                        dSonInfo = {
                            'sName': '%s x %s' % (os.path.basename(sPath), dPath['iTimes']),
                            'sTips': sPath,
                            'sDesc':  % '\xa5e\xa4\xf1: #cED8200%.02f %%#n' if iTotalCost else 0 }
                        dInfo['dSonList'].append(dSonInfo)
                    
                
                self.m_dInfoList.append(dInfo)
                continue
        
        self.EmitUpdate()

    
    def GetDlgData(self, oNode, dPathDict):
        dStatistic = getattr(oNode, 'm_dCostStatistic', { })
        for iFrame, dFrameDict in dStatistic.iteritems():
            dPathDict[iFrame] = { }
            for iTimes, iCost in dFrameDict.iteritems():
                dPathDict[iFrame][sPath] = {
                    'iTimes': iTimes,
                    'iCost': iCost,
                    'iFrame': iFrame }
            
        

    
    def GetChildTime(self, oNode, dPathDict):
        iTime = getattr(oNode, 'm_iLoadingCost', None)
        sPath = getattr(oNode, 'm_TempResourceName', None)
        if iTime is not None and sPath:
            if sPath in dPathDict:
                dPathDict[sPath]['iCost'] += iTime
                dPathDict[sPath]['iTimes'] += 1
            else:
                dPathDict[sPath] = {
                    'iCost': iTime,
                    'iTimes': 1 }
        
        for oChild in oNode.GetAllChildrens():
            self.GetChildTime(oChild, dPathDict)
        



class CRenderProfileModel(CModelBase):
    
    def Init(self):
        self.OnCheck(True)
        self.m_oCheckTimer = timer.Timer(1, self.OnCheck, -1)

    
    def OnCheck(self, bFirst = False):
        if not bFirst:
            self.m_dInfoList = []
            dTaskList = showdrawtime.GetCtrl().GetTaskList()
            dTaskList.sort(key = (lambda p: -p['iTotal']))
            for dTask in dTaskList:
                dInfo = { }
                if dTask['sName'] == CUIProfileDlg.sUIName:
                    continue
                
                dInfo['sName'] = dTask['sName']
                dInfo['sDesc'] = '\xb4\xe8\xacV\xc1`\xaf\xd3\xae\xc9: #cED8200%s#n' % dTask['iTotal']
                dInfo['dSonList'] = []
                lItems = dTask['dSonList'].items()
                lItems.sort(key = (lambda p: -p[1]))
                if dTask['iTotal']:
                    for sName, iTime in lItems:
                        dSonInfo = {
                            'sName': dTask['dNameMap'].get(sName, sName),
                            'sDesc': '\xa5e\xa4\xf1: #cED8200%.02f %%#n' % 1 * (int(iTime) * 10000 / int(dTask['iTotal'])) / 100,
                            'sTips': None }
                        dInfo['dSonList'].append(dSonInfo)
                    
                
                self.m_dInfoList.append(dInfo)
            
            self.EmitUpdate()
        
        showdrawtime.StartCheck(30, bPrint = 0)
