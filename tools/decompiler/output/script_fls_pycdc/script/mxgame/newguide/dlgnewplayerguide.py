# pycdc 交叉复核产物 · script.fls entry 4555
# co_filename(原始)='script/mxgame/newguide/dlgnewplayerguide.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4555.pyc (Python 2.5)

import combdialog
import interface
import misc
import pagedgtbase
import popupdefine
import popupmgr
import dlgmengxin
import dlgmiji
import dlgbianqiang
import slot
import dlgnewplayerguidecom
import ui

def ShowIWantUpgrade():
    oPopuMgr = popupmgr.GetPopupMgr()
    oDlg = oPopuMgr.GetUI(popupdefine.CMainGuideDialog)
    if oDlg:
        oPopuMgr.CloseUI(popupdefine.CMainGuideDialog, True)
    
    oDlg = oPopuMgr.OpenUI(popupdefine.CMainGuideDialog, None, [
        {
            'iSubPage': 1 }])
    oDlg.GotoIWantUpgrade()


def ShowByText(sFristPage, sSecondPage):
    dText2Page = {
        '\xb5\xde\xb7s\xa4\xa7\xb8\xf4': 0,
        '\xa6\xa8\xaa\xf8\xc4_\xa8\xe5': 1,
        '\xa7\xda\xadn\xc5\xdc\xb1j': 2 }
    oPopuMgr = popupmgr.GetPopupMgr()
    oDlg = oPopuMgr.GetUI(popupdefine.CMainGuideDialog)
    if oDlg:
        oPopuMgr.CloseUI(popupdefine.CMainGuideDialog, True)
    
    oDlg = oPopuMgr.OpenUI(popupdefine.CMainGuideDialog, None, [
        {
            'iSubPage': dText2Page.get(sFristPage, 0) }])
    oDlg.LeftupSecondBtn(sSecondPage)


def RefreshTaskInfo(dData, iPage):
    oDlg = GetMainDlg()
    if oDlg:
        oDlg.RefreshTaskInfo(dData, iPage)
    


def InitReward(iNum, iProgress, lAccomlish):
    '''
\t:param iNum:\xa5i\xbb\xe2\xa8\xfa\xa6h\xa4\xd6\xa6\xb8\xa1A0\xaa\xed\xa5\xdc\xa8S\xa6\xb3,-1\xaa\xed\xa5\xdc\xbb\xe2\xa7\xb9
\t:param iProgress:\xbc\xfa\xc0y\xb6i\xab\xd7
\t:param lAccomlish:\xa7\xb9\xa6\xa8\xbc\xfa\xc0y\xbb\xe2\xa8\xfa\xb1\xa1\xaap
\t'''
    oDlg = GetMainDlg()
    if oDlg:
        oDlg.InitReward(iNum, iProgress, lAccomlish)
    


def ShowPromptNum():
    oDlg = GetMainDlg()
    if oDlg:
        oMengXinDlg = oDlg.GetMengXinDlg()
        if oMengXinDlg:
            oMengXinDlg.UpdateBtnRedDot()
        
    


def UpdatePlayerGrowRedDot():
    oDlg = GetMainDlg()


def GetMainDlg():
    oDlg = popupmgr.GetPopupMgr().GetUI(popupdefine.CMainGuideDialog)
    return oDlg


def ShowWarFailTips(iImprove):
    import hero
    import misc
    if hero.GetProp('m_Grade') <= 50:
        sTxt = '\xbe\xd4\xb0\xab\xa5\xa2\xb1\xd1,\xa4\xa3\xadn\xae\xf0\xbek!\xa4p\xa9\xfd\xac\xb0\xb1z\xb7\xc7\xb3\xc6\xa4F\xadP\xb3\xd3\xa4\xe8\xaak\xa1C'
        sImprove = GetImproveText(iImprove)
        import dlgnpc
        dlgnpc.ShowClientNoitce('L\x1aL\x1a\nL\xacd\xac\xdd\xa7\xb9\xbe\xe3\xa6\xa8\xaa\xf8\xaf\xb5\xc4y\nL\xb5y\xab\xe1\xbe\xc7\xb2\xdf' % (sTxt, sImprove), '', misc.Functor(ClickMakeEquip, iImprove))
    


def ClickMakeEquip(iImprove, iMsgID):
    if iImprove <= iImprove:
        pass
    elif iImprove <= 7:
        if iMsgID == 1:
            DoImprove(iImprove)
        elif iMsgID == 2:
            popupmgr.GetPopupMgr().OpenUI(popupdefine.CMainGuideDialog, None, [
                {
                    'iSubPage': 1 }])
        
    elif iMsgID == 1:
        popupmgr.GetPopupMgr().OpenUI(popupdefine.CMainGuideDialog, None, [
            {
                'iSubPage': 1 }])
    


def GetImproveText(iImprove):
    if iImprove == 1:
        return '\nL\xb4\xa3\xb0\xaa\xa4H\xaa\xab\xb5\xa5\xaf\xc5'
    elif iImprove == 2:
        return '\nL\xb4\xa3\xb0\xaa\xbe\xd4\xb0\xab\xa7\xde\xaf\xe0\xb5\xa5\xaf\xc5'
    elif iImprove == 3:
        return '\nL\xb4\xa3\xb0\xaa\xa9\xdb\xa6\xa1\xb5\xa5\xaf\xc5'
    elif iImprove == 4:
        return '\nL\xa7\xf3\xb4\xab\xb1j\xa4O\xb8\xcb\xb3\xc6'
    elif iImprove == 5:
        return '\nL\xb4\xa3\xb0\xaa\xa4H\xaa\xab\xad\xd7\xb7\xd2'
    elif iImprove == 6:
        return '\nL\xb8\xcb\xb3\xc6\xc6^\xb4O\xc4_\xa5\xdb'
    elif iImprove == 7:
        return '\nL\xa7\xf3\xb4\xab\xb1j\xa4O\xa5l\xb3\xea\xc3~'
    else:
        return ''


def DoImprove(iImprove):
    import autofindpath
    import linkdefine
    import linkdlgctl
    import pet
    import playerguidemgr
    if iImprove == 1:
        popupmgr.GetPopupMgr().OpenUI(popupdefine.CMainGuideDialog, None, [
            {
                'iSubPage': 1,
                'iTaskId': 1 }])
    elif iImprove == 2:
        linkdlgctl.CLinkOpen(linkdefine.OpenFightDlg)
    elif iImprove == 3:
        linkdlgctl.CLinkOpen(linkdefine.OpenZhaoShiDlg)
    elif iImprove == 4:
        popupmgr.GetPopupMgr().OpenUI(popupdefine.CMainGuideDialog, None, [
            {
                'iSubPage': 1,
                'iTaskId': 4 }])
    elif iImprove == 5:
        linkdlgctl.CLinkOpen(linkdefine.OpenXiuLianDlg)
    elif iImprove == 6:
        linkdlgctl.CLinkOpen(linkdefine.OpenDaZao_BaoShiXiangQianDlg)
    elif iImprove == 7:
        if pet.GetPetCount() == 0:
            playerguidemgr.GetMgr().SetNpcPanelOption('\xa5\xe6\xa9\xf6\xc1`\xba\xde', 1, '\xa7\xda\xadn\xb6R\xbd\xe6\xb3\xa5\xa5\xcd\xa5l\xb3\xea\xc3~')
            autofindpath.AutoFind('\xa9\xfa\xa4\xeb\xab\xb0', (64, 134), sNpcName = '\xa5\xe6\xa9\xf6\xc1`\xba\xde')
        else:
            linkdlgctl.CLinkOpen(linkdefine.OpenXiChong)
    


class CMainGuideDialog(combdialog.CCombDialog, slot.ISignalSubject):
    BTN_NAME_LIST = [
        'btn_mengxinzhilu',
        'btn_chengzhangbaodian',
        'btn_woyaobianqiang']
    
    def __init__(self, oParent, dDefaultInitInfo = None):
        (self, oParent, 'dialog4/guide/zhiyinnew.dlg')
        self.ssInit()
        self.m_DlgHelpID = 5010
        self.m_oMengXin = None
        self.m_oMiji = None
        self.m_oBianQiang = None
        self.m_oImgPlayerGrowRedDot = None
        interface.Center(self)
        self.m_dDefaultInitInfo = dDefaultInitInfo
        iSubPage = 1
        if dDefaultInitInfo:
            iSubPage = dDefaultInitInfo.get('iSubPage', 1)
        
        self.InitDialog(iSubPage)
        self.m_oBtnCtrl = pagedgtbase.CBtnCtrl(self.BTN_NAME_LIST, misc.Functor(self.GetObject), misc.Functor(self.OnBtnShow))

    
    def RefreashWindow(self, dDefaultInitInfo):
        self.m_dDefaultInitInfo = dDefaultInitInfo
        iPage = self.m_dDefaultInitInfo.get('iSubPage', 1)
        if self.m_oMengXin:
            self.m_oMengXin.CheckIsNeedSwitch()
        
        self.ChoosePage(iPage)
        self.UpdateBtnEnable()

    
    def CloseWindow(self):
        dlgnewplayerguidecom.RemoveTips()
        popupmgr.GetPopupMgr().CloseUI(popupdefine.CMainGuideDialog, False)
        import netnewplayerguide
        netnewplayerguide.C2SCloseGetStrong()

    
    def InitReward(self, iNum, iProgress, lAccomlish):
        if self.m_CurMainPage == 0:
            self.m_oSubDialog.InitReward(iNum, iProgress, lAccomlish)
        

    
    def RefreshTaskInfo(self, dData, iPage):
        if self.m_CurMainPage == 0:
            self.m_oSubDialog.RefreshTaskInfo(dData, iPage)
        

    
    def GotoIWantUpgrade(self):
        if self.m_CurMainPage != 1:
            self.GetObject('btn_chengzhangbaodian').LeftUp()
        
        self.m_oSubDialog.LeftUpBtnByText('\xa4H\xaa\xab\xb4\xa3\xa4\xc9')

    
    def LeftupSecondBtn(self, sText):
        if self.m_CurMainPage == 1:
            self.m_oSubDialog.LeftUpBtnByText(sText)
        

    
    def InitDialog(self, iPage):
        self.m_oSubDialog = None
        self.m_CurMainPage = 0
        btnName = ('btn_mengxinzhilu', 'btn_chengzhangbaodian', 'btn_woyaobianqiang')[iPage]
        self.GetObject(btnName).LeftUp()
        self.GetObject(btnName).Leave()

    
    def SetTabSelect(self, iPage):
        btnName = ('btn_mengxinzhilu', 'btn_chengzhangbaodian', 'btn_woyaobianqiang')[iPage]
        if not self.GetObject(btnName).GetSelect():
            self.GetObject(btnName).SetSelect(True)
        

    
    def ShowSubPage(self, iPage, dDefaultInitInfo):
        import mdbianqiang
        bIsFirstOpenBianQiangDlg = mdbianqiang.GetModel().IsFirstOpenDlg()
        if iPage == 0:
            if not self.m_oMengXin:
                self.m_oSubDialog = self.CreateCMengxinDialog()
            else:
                self.m_oSubDialog = self.m_oMengXin
                import playerguidemgr
                iMxPage = self.m_oMengXin.GetCurPage()
                dData = playerguidemgr.GetMgr().GetTaskInfoByPage(iMxPage)
                self.m_oMengXin.UpdateBtnRedDot()
                self.m_oMengXin.RefreshTaskInfo(dData, iMxPage)
        elif iPage == 1:
            self.m_oSubDialog = self.CreateCMijiDialog(dDefaultInitInfo)
        elif iPage == 2:
            self.m_oSubDialog = self.CreateCBianQiangDialog()
        
        if self.m_oSubDialog:
            (x, y, w, h) = self.GetLocData('link_page')
            self.m_oSubDialog.SetPos(x, y)
            if iPage == 2 and bIsFirstOpenBianQiangDlg:
                self.m_oSubDialog.SetShow(False)
            else:
                self.m_oSubDialog.SetShow(True)
        

    
    def ChoosePage(self, iPage):
        self.m_CurMainPage = iPage
        self.ClearSubPage()
        self.SetTabSelect(iPage)
        self.ShowSubPage(iPage, self.m_dDefaultInitInfo)

    
    def OnBtnShow(self, sName):
        import hero
        import mdbianqiang
        iLv = hero.GetProp('m_Grade', 0)
        if sName == 'btn_mengxinzhilu':
            return iLv >= 20
        elif sName == 'btn_chengzhangbaodian':
            return iLv >= 20
        elif sName == 'btn_woyaobianqiang':
            iPageFinish = mdbianqiang.GetModel().GetRewardState()
            if 9 <= iLv:
                pass
            return iPageFinish != 2
        else:
            return False

    
    def UpdateBtnEnable(self):
        self.m_oBtnCtrl.CheckTabShow()

    
    def CheckPlayerGrowRedDot(self):
        import mdbianqiang
        iCount = mdbianqiang.GetModel().GetMengXinRedDotCount()
        if iCount > 0:
            self.m_oImgPlayerGrowRedDot = ui.CImage(self.GetObject('btn_woyaobianqiang'), 'combdialog/\xd4\xd3\xcd\xbc/\xcc\xe1\xca\xbe\xd0\xa1\xba\xec\xb5\xe3.igs', interface.UIPath)
            self.m_oImgPlayerGrowRedDot.SetZ(1)
            tSize = self.GetObject('btn_woyaobianqiang').GetSize()
            self.m_oImgPlayerGrowRedDot.SetPos(tSize[0] * 0.91, 0)
        else:
            self.m_oImgPlayerGrowRedDot = None

    
    def CreateCMengxinDialog(self):
        if not self.m_oMengXin:
            self.m_oMengXin = dlgmengxin.<2engxinDialog(self)
        
        return self.m_oMengXin

    
    def CreateCMijiDialog(self, dDefaultInitInfo):
        if not self.m_oMiji:
            self.m_oMiji = dlgmiji.CMijiDialog(self, 2, dDefaultInitInfo)
        else:
            self.m_oMiji.ForceUpdateView(dDefaultInitInfo)
        return self.m_oMiji

    
    def CreateCBianQiangDialog(self):
        if not self.m_oBianQiang:
            self.m_oBianQiang = dlgbianqiang.CBianQiangDialog(self)
        else:
            self.m_oBianQiang.ForceUpdateView()
        return self.m_oBianQiang

    
    def GetMiJiDlg(self):
        if self.m_CurMainPage != 1:
            return None
        
        return self.m_oSubDialog

    
    def GetMengXinDlg(self):
        if self.m_CurMainPage != 0:
            return None
        
        return self.m_oSubDialog

    
    def GetBianQiangDlg(self):
        if self.m_CurMainPage != 2:
            return None
        
        return self.m_oSubDialog

    
    def ClearSubPage(self):
        dlgnewplayerguidecom.RemoveTips()
        if self.m_oSubDialog:
            self.m_oSubDialog.SetShow(False)
        

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        elif iMsgID in (2, 3, 4):
            import playerguidemgr
            playerguidemgr.GetMgr().SetCurOpenIndex(iMsgID - 2)
            self.ChoosePage(iMsgID - 2)
