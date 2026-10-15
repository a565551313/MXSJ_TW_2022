# pycdc 交叉复核产物 · script.fls entry 1025
# co_filename(原始)='script/mxgame/activity/summerdiscount/dgtsummerdiscount.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1025.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2021/5/20 9:59
\xd7\xf7\xd5\xdf: \xbf\xec\xc0\xd6\xcb\xae
\xce\xc4\xbc\xfe: dgtsummerdiscount
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import delegatebase
import mdsummerdiscount
import netfashiondress
import dialoguecommondata
import charpath
import dlgnpc
import misc
import autofindpath
import chardefine
import descinterface
import permission
ANIMATION_NAME = {
    7: chardefine.STATE_ATTACK,
    8: chardefine.STATE_STAND,
    9: chardefine.STATE_WALK }

class CSummerDiscountDgt(delegatebase.CDelegateBase):
    
    def Init(self):
        self.EditInit()
        self.InitView()

    
    def EditInit(self):
        \x9a\xa3\x9cew = self.GetView()
        \x9a\xa3\x9cew.ssConnect(\x9a\xa3\x9cew.SS_ClickBtnBuy, self.OnClickBtnBuy)
        \x9a\xa3\x9cew.ssConnect(\x9a\xa3\x9cew.SS_ClickFashionIcon, self.OnClickFashionIcon)
        \x9a\xa3\x9cew.ssConnect(\x9a\xa3\x9cew.SS_ClickDirection, self.OnClickDirection)
        \x9a\xa3\x9cew.ssConnect(\x9a\xa3\x9cew.SS_ClickAction, self.OnClickAction)
        \x9a\xa3\x9cew.ssConnect(\x9a\xa3\x9cew.SS_ClickPageBtn, self.OnChangePageView)
        oModel = self.GetModel()
        oModel.ssConnect(oModel.SS_ChangeBtnType, self.OnUpdateBtn)
        oModel.ssConnect(oModel.SS_ChangePage, self.OnChangePage)
        oModel.ssConnect(oModel.SS_ChangeRoleDirection, self.OnChangeRoleDir)

    
    def InitView(self):
        oModel = self.GetModel()
        iPage = oModel.GetPage()
        \x9a\xa3\x9cew = self.GetView()
        \x9a\xa3\x9cew.InitPageBtn(iPage)
        \x9a\xa3\x9cew.SetPageViewShow(iPage)
        \x9a\xa3\x9cew.UpdateGifts(iPage)
        self.OnUpdateBtn()
        self.UpdateFashionView()
        netfashiondress.C2SGetCanBuyState()

    
    def OnChangePageView(self, iMsgId):
        oModel = self.GetModel()
        oModel.SetPage(iMsgId - 1)

    
    def OnChangePage(self):
        \x9a\xa3\x9cew = self.GetView()
        oModel = self.GetModel()
        iPage = oModel.GetPage()
        \x9a\xa3\x9cew.SetPageViewShow(iPage)
        \x9a\xa3\x9cew.UpdateGifts(iPage)
        self.UpdateFashionRole()
        self.OnUpdateBtn()

    
    def UpdateFashionView(self):
        self.UpdateFashionRole()
        self.UpdateFashionSelectSpr()

    
    def UpdateFashionRole(self):
        oModel = self.GetModel()
        \x9a\xa3\x9cew = self.GetView()
        dInfoList = oModel.GetFashionInfo()
        \x9a\xa3\x9cew.UpdateFashionIcon(dInfoList)
        iSelectFashionId = oModel.GetSelectFashionId()
        iPage = oModel.GetPage()
        dInfo = oModel.GetFashionInfoByIdx(iSelectFashionId)
        self.RefreshViewRole(iPage, dInfo)
        iNowDir = oModel.GetRoleDir()
        \x9a\xa3\x9cew.ChangeDir(iNowDir * 4)

    
    def RefreshViewRole(self, iPage, dInfo):
        \x9a\xa3\x9cew = self.GetView()
        (iHeroShape, dDesc) = charpath.GetHeroShow()
        descinterface.ClearDescByKey(dDesc, [
            chardefine.DESC.KEY_HORSE,
            chardefine.DESC.KEY_TRACK,
            chardefine.DESC.KEY_AURA,
            chardefine.DESC.WING])
        if iPage == 1:
            lstFashionColor = dInfo.get('lstColor', [
                0,
                0,
                0])
            descinterface.SetFashion(dDesc, dInfo.get('iFashionId', 0), lstFashionColor[0], lstFashionColor[1], lstFashionColor[2])
        
        \x9a\xa3\x9cew.RefreshRole(iHeroShape, iPage, dDesc)

    
    def UpdateFashionSelectSpr(self):
        \x9a\xa3\x9cew = self.GetView()
        oModel = self.GetModel()
        iSelectFashionId = oModel.GetSelectFashionId()
        \x9a\xa3\x9cew.SetSelcetSprShow(iSelectFashionId)

    
    def OnClickBtnBuy(self, iMsgId):
        oModel = self.GetModel()
        iPage = oModel.GetPage()
        if iPage == 1:
            if permission.IsOpenOldWearFashion() or charpath.IsUseNewRes():
                netfashiondress.C2SBuyFashionGift(iPage, iMsgId - 9)
            else:
                sTxt = dialoguecommondata.GetDialogueWithoutI2nTips('fashion', 1003)
                dlgnpc.ShowClientDlg(sTxt, '', misc.Functor(self.OnClickBuyCB))
        elif iPage == 2:
            netfashiondress.C2SBuyFashionGift(iPage, iMsgId - 9)
        

    
    def OnClickBuyCB(self, iMsgID):
        if iMsgID == 1:
            autofindpath.AutoFind('\xb6\xb3\xb3\xb6\xa8\xa6', (39, 20), sNpcName = '\xb9C\xc0\xb8\xb3]\xb8m\xba\xde\xb2z\xad\xfb')
        

    
    def OnClickFashionIcon(self, iIdx):
        oModel = self.GetModel()
        \x9a\xa3\x9cew = self.GetView()
        oModel.SetSelectFashionId(iIdx)
        dInfo = oModel.GetFashionInfoByIdx(iIdx)
        iPage = oModel.GetPage()
        self.RefreshViewRole(iPage, dInfo)
        iNowDir = oModel.GetRoleDir()
        \x9a\xa3\x9cew.ChangeDir(iNowDir * 4)
        self.UpdateFashionSelectSpr()

    
    def OnClickDirection(self, iMsgID):
        oModel = self.GetModel()
        iNowDir = oModel.GetRoleDir()
        if iMsgID == 5:
            iNowDir -= 1
        elif iMsgID == 6:
            iNowDir += 1
        
        iDirection = (iNowDir + 8) % 8
        oModel.SetRoleDir(iDirection)

    
    def OnChangeRoleDir(self):
        oModel = self.GetModel()
        \x9a\xa3\x9cew = self.GetView()
        iNowDir = oModel.GetRoleDir()
        \x9a\xa3\x9cew.ChangeDir(iNowDir * 4)

    
    def OnClickAction(self, iMsgID):
        \x9a\xa3\x9cew = self.GetView()
        \x9a\xa3\x9cew.SetRoleAnimation(ANIMATION_NAME[iMsgID])

    
    def OnUpdateBtn(self):
        oModel = self.GetModel()
        \x9a\xa3\x9cew = self.GetView()
        iPage = oModel.GetPage()
        iState = oModel.GetStateBuyPage(iPage)
        \x9a\xa3\x9cew.UpdateBuyBtn(iState == 0)

    
    def GetModel(self):
        return mdsummerdiscount.GetCSummerDiscountModel()
