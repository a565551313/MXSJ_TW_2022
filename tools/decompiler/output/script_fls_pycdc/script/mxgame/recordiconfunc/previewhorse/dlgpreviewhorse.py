# pycdc 交叉复核产物 · script.fls entry 4909
# co_filename(原始)='script/mxgame/recordiconfunc/previewhorse/dlgpreviewhorse.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:03Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4909.pyc (Python 2.5)

import combdialog
import newappearancedefine
import recordiconfuncdefine
import slot
import walker
import clickcounter
import chardefine

class CPreviewRideDlg(combdialog.CCombDialog, slot.ISignalSubject):
    dRolePartForUIName = {
        'duanjinling': 'btn_selec3',
        'beijiguang': 'btn_selec4',
        'fairy': 'btn_selec1' }
    dBuyToApparance = {
        'iType': recordiconfuncdefine.PREVIEW_HORSE,
        'iPage': newappearancedefine.MAIN_PAGE_HORSE }
    sUIName = 'dialog4/friend/yulan_ride.dlg'
    SS_RollRoleMode = 'OnRollRoleMode(sType)'
    SS_ChangeRoleHideInfo = 'UpdateRolePartSelet(sType, bSel)'
    SS_ClickBuyBtn = 'OnClickBuy()'
    SS_ClosePreview = 'OnClosePreview'
    SS_OpenMultRidePreview = 'OnOpenMultRidePreview()'
    
    def __init__(self, oParent):
        combdialog.CCombDialog.__init__(self, oParent, self.sUIName)
        self.m_oRoleView = None
        self.m_oDelegateList = []
        self.ssInit()
        self.InitDelegate()

    
    def InitDelegate(self):
        import dgtpreviewhorse
        import previewbasedgt
        self.m_oDelegateList = [
            dgtpreviewhorse.CPreviewRideDgt(self),
            previewbasedgt.COperateRoleP"rtDgt(self),
            previewbasedgt.CUpdateRoleDgt(self)]

    
    def UpdateRoleView(self, iShape, dDesc, bIsUseNewRes, iDir = 1):
        '''\xa5\xcd\xa6\xa8\xa4@\xad\xd3\xa8\xa4\xa6\xe2\xbc\xd2\xab\xac'''
        oLoc = self.GetObject('loc_item')
        (iX, iY) = oLoc.GetPos()
        (iW, iH) = oLoc.GetSize()
        self.m_oRoleView = walker.CreateFakeWalker(self, 0, iShape, dDesc, iIsUseNewRes = bIsUseNewRes)
        self.m_oRoleView.Enable(False)
        self.m_oRoleView.SetDirection(iDir)
        self.m_oRoleView.SetZ(20)
        self.m_oRoleView.SetPos(iX + iW / 2, iY)

    
    def UpdateRoleDir(self, iDir):
        '''\xa4H\xaa\xab\xbc\xd2\xab\xac\xb1\xdb\xc2\xe0'''
        if self.m_oRoleView:
            self.m_oRoleView.SetDirection(iDir)
        

    
    def InitRolePartSelect(self, dInfo):
        '''\xc0q\xbb{\xbf\xef\xa4\xa4'''
        for sKey, oValue in dInfo.iteritems():
            self.UpdateRolePartSelect(sKey, oValue)
        

    
    def UpdateRolePartSelect(self, sType, bSelect):
        '''\xa7\xf3\xb7s\xb3\xe6\xad\xd3\xbf\xef\xa4\xa4'''
        if sType in self.dRolePartForUIName:
            self.GetObject(self.dRolePartForUIName[sType]).SetSelect(bSelect)
        elif sType == 'preview':
            iBtn = None if bSelect else 5
            sBtn = 'btn_selec%d' % iBtn
            for sUIBtn in [
                'btn_selec5',
                'btn_selec2']:
                self.GetObject(sUIBtn).SetSelect(sBtn == sUIBtn)
            
        

    
    def RollRoleMode(self, sType):
        '''sType: Clockwise, UnClockwise'''
        self.ssEmit(self.SS_RollRoleMode, sType)

    
    def ClickRolePartBtn(self, sType, bSel = None):
        self.ssEmit(self.SS_ChangeRoleHideInfo, sType, bSel)

    
    def LogPreviewTimes(self, sText):
        clickcounter.Log(sText)

    
    def CloseWindow(self):
        self.CloseUI()
        self.ssEmit(self.SS_ClosePreview)

    
    def HideSomeUI(self):
        '''\xa6p\xaaG\xa5\xb4\xb6}\xaa\xba\xacO\xa6\xdb\xa4v\xaa\xba,\xab\xcc\xbd\xaa\xa4@\xa8\xc7UI'''
        for sUIName in [
            'btn_selec2',
            'btn_selec5',
            'txt_shichuan',
            'btn_buy']:
            self.SetShowObject(sUIName, False)
        

    
    def CheckShowMultRideUI(self, bShow):
        '''\xacO\xa7_\xc5\xe3\xa5\xdc\xa6h\xa4H\xa7\xa4\xc3M\xbf\xef\xb6\xb5'''
        self.SetShowObject('loc_view', bShow)

    
    def ClickBuyBtn(self):
        self.ssEmit(self.SS_ClickBuyBtn, self.dBuyToApparance.get('iPage', 0))

    
    def OnMessage(self, iMsgID):
        if iMsgID == 3:
            self.RollRoleMode('Clockwise')
        elif iMsgID == 4:
            self.RollRoleMode('UnClockwise')
        elif iMsgID == 12:
            self.ClickBuyBtn()
        elif iMsgID == 16:
            self.ClickRolePartBtn(chardefine.DESC.HORSE_DECORATE_1)
        elif iMsgID == 17:
            self.ClickRolePartBtn(chardefine.DESC.HORSE_DECORATE_2)
        elif iMsgID == 19:
            self.ClickRolePartBtn(chardefine.DESC.KEY_FAIRY)
        elif iMsgID == 20:
            self.CloseWindow()
        elif iMsgID == 21:
            self.ClickRolePartBtn(recordiconfuncdefine.KEY_PREVIEW, False)
        elif iMsgID == 22:
            self.ClickRolePartBtn(recordiconfuncdefine.KEY_PREVIEW, True)
            self.LogPreviewTimes('\xa7\xa4\xc3M\xb9w\xc4\xfd-\xb9w\xc4\xfd\xa7\xa4\xc3M')
        elif iMsgID == 193:
            self.ssEmit(self.SS_OpenMultRidePreview)
