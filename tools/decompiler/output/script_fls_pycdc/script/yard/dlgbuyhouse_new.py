# pycdc 交叉复核产物 · script.fls entry 2590
# co_filename(原始)='script/yard/dlgbuyhouse_new.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_2590.pyc (Python 2.5)

import combdialog
import slot
import interface
import ui
import netyard
g_BuyHouse = None

def ModuleReset():
    global g_BuyHouse
    g_BuyHouse = None


def ShowBuyHouse(bFirstBuy):
    global g_BuyHouse
    if not g_BuyHouse:
        g_BuyHouse = CBuyHouseDlg()
    
    g_BuyHouse.Topmost()
    g_BuyHouse.SetFirstBuy(bFirstBuy)


def CloseWindows():
    global g_BuyHouse
    g_BuyHouse = None


class CBuyHouseDlg(combdialog.CCombDialog, slot.ISignalSubject):
    S_FIRST_BUYUI = ('btn_diyongbuy', 'txt_shougoutips', 'img_Tips3', 'txt_diyongbuy', 'img_diyongbuy')
    S_OTHER_BUYUI = ('btn_cashbuy1', 'txt_cashprice1', 'img_cash1', 'btn_sgbuy1', 'txt_sgprice1', 'img_sg1')
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/home/buyhouse.dlg')
        interface.Center(self)
        self.m_iLeftType = 1
        self.m_iRightType = 1
        self.m_oLeftImg = None
        self.m_oRightImg = None
        self.m_bFirstBuy = False
        self.RefreshSelectedView()
        self.RefreshSelectedBtn()

    
    def SetFirstBuy(self, bFirst):
        self.m_bFirstBuy = bFirst
        for sUIName in self.S_FIRST_BUYUI:
            self.SetShowObject(sUIName, bFirst)
        
        for sUIName in self.S_OTHER_BUYUI:
            self.SetShowObject(sUIName, not bFirst)
        

    
    def RefreshSelectedBtn(self):
        oBtnLst = {
            'Left': [
                'btn_waiguan1',
                'btn_shinei1'],
            'Right': [
                'btn_waiguan2',
                'btn_shinei2',
                'btn_2floor'] }
        oLeftBtn = self.GetObject(oBtnLst['Left'][self.m_iLeftType - 1])
        oRightBtn = self.GetObject(oBtnLst['Right'][self.m_iRightType - 1])
        oLeftBtn.SetSelect(True)
        oRightBtn.SetSelect(True)

    
    def RefreshSelectedView(self):
        oLeftLoc = self.GetObject('loc_preview1')
        oRightLoc = self.GetObject('loc_preview2')
        (iLX, iLY, iLW, iLH) = self.GetLocData('loc_preview1')
        (iRX, iRY, iRW, \xecRH) = [].GetLocData('loc_preview2')
        oImgLst = {
            'Left': [
                {
                    'sPath': ('furniture/29302a.igs', 'mapobject'),
                    'iScale': 0.25,
                    'tPos': (iLW / 2, iLH) },
                {
                    'sPath': ('2401.png', 'minimap'),
                    'iScale': 0.45,
                    'tPos': (-13, iLH / 2 - 50) }],
            'Right': [
                {
                    'sPath': ('furniture/29300a.igs', 'mapobject'),
                    'iScale': 0.25,
                    'tPos': (iRW / 2, \xecRH) },
                {
                    'sPath': ('2421.png', 'minimap'),
                    'iScale': 0.45,
                    'tPos': (-13, \xecRH / 2 - 50) },
                {
                    'sPath': ('2422.png', 'minimap'),
                    'iScale': 0.45,
                    'tPos': (-13, \xecRH / 2 - 50) }] }
        dLeftImgInfo = oImgLst['Left'][self.m_iLeftType - 1]
        dRightImgInfo = oImgLst['Right'][self.m_iRightType - 1]
        self.m_oLeftImg = ui.CStretchImage(oLeftLoc, dLeftImgInfo['sPath'][0], dLeftImgInfo['sPath'][1])
        self.m_oLeftImg.SetScale(dLeftImgInfo['iScale'])
        self.m_oLeftImg.SetPos(*dLeftImgInfo['tPos'])
        self.m_oRightImg = ui.CStretchImage(oRightLoc, dRightImgInfo['sPath'][0], dRightImgInfo['sPath'][1])
        self.m_oRightImg.SetScale(dRightImgInfo['iScale'])
        self.m_oRightImg.SetPos(*dRightImgInfo['tPos'])
        self.GetObject('img_housebg1').SetShow(self.m_iLeftType == 1)
        self.GetObject('img_housebg2').SetShow(self.m_iRightType == 1)

    
    def CloseWindow(self):
        CloseWindows()

    
    def OnBuyClick(self, iMsgID):
        iType = None if iMsgID in (2, 3, 12) else 2
        if iMsgID == 12:
            iCashType = 3
        elif iMsgID in (2, 4):
            pass
        
        iCashType = 2
        netyard.C2SBuyHouse(iType, iCashType)
        self.CloseWindow()

    
    def OnClickSelected(self, iMsgID):
        if iMsgID in (6, 8):
            self.m_iLeftType = 1
            self.m_iRightType = 1
        elif iMsgID in (7, 9):
            self.m_iLeftType = 2
            self.m_iRightType = 2
        else:
            self.m_iLeftType = 2
            self.m_iRightType = 3
        self.RefreshSelectedView()
        self.RefreshSelectedBtn()

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        elif iMsgID <= iMsgID:
            pass
        elif iMsgID <= 5 or iMsgID == 12:
            self.OnBuyClick(iMsgID)
        elif iMsgID <= iMsgID:
            pass
        elif iMsgID <= 10:
            self.OnClickSelected(iMsgID)
        elif iMsgID == 11:
            import dlgtool_lycos_new
            dlgtool_lycos_new.ShowHelper('\xaa\xb1\xaea\xa4\xa7\xaea')
