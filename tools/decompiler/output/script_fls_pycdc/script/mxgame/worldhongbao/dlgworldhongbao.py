# pycdc 交叉复核产物 · script.fls entry 4198
# co_filename(原始)='script/mxgame/worldhongbao/dlgworldhongbao.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4198.pyc (Python 2.5)

import combdialog
import interface
import networldhongbao
g_WorldDlg = None
g_iOpenFrom = 0
ROW_ITEMS = 3
SPECIAL_DAY = {
    ((5, 20), (5, 20)): '1\xa1B\xa4\xb5\xa4\xe9\xaa\xe1\xb6O1314\xa5@\xac\xc9\xb0^\xc4m\xab\xd7(\xad\xec\xbb\xf91688)\xa5i\xa6b\xa5@\xac\xc9\xc0W\xb9D\xa6V\xa6n\xa4\xcd\xb5o\xb0e\xaf\xac\xba\xd6\xb1H\xbby',
    ((9, 30), (10, 8)): '1\xa1B\xb0\xea\xbcy\xb4\xc1\xb6\xa1\xa5\xce1350\xa5@\xac\xc9\xb0^\xc4m\xab\xd7\xa1]\xad\xec\xbb\xf91688\xa1^\xa5i\xa6b\xa5@\xac\xc9\xc0W\xb9D\xa6V\xa6n\xa4\xcd\xa9\xce\xa6P\xc0\xb0\xaa\xb1\xaea\xb5o\xaf\xac\xba\xd6',
    ((6, 24), (7, 29)): '1\xa1B\xa4\xb5\xa4\xe9\xaa\xe1\xb6O1350\xa5@\xac\xc9\xb0^\xc4m\xab\xd7(\xad\xec\xbb\xf91688)\xa5i\xa6b\xa5@\xac\xc9\xc0W\xb9D\xa6V\xa6n\xa4\xcd\xb5o\xb0e\xaf\xac\xba\xd6\xb1H\xbby' }

def ModuleReset():
    global g_WorldDlg, g_iOpenFrom
    g_WorldDlg = None
    g_iOpenFrom = 0


def SetShow(bShow, dBlessDataList):
    global g_WorldDlg, g_WorldDlg
    if bShow:
        if not g_WorldDlg:
            g_WorldDlg = CWorldHongbaoDialog(dBlessDataList)
        
        g_WorldDlg.SetShow(True)
    else:
        g_WorldDlg = None


def GetOpenFrom():
    return g_iOpenFrom


def SetOpenFrom(iOpenFrom = 0):
    global g_iOpenFrom
    g_iOpenFrom = iOpenFrom


def RefreshHongbaoStatus(iHongbaoId, iCharId):
    if not g_WorldDlg:
        return None
    
    g_WorldDlg.RefreshHongbaoStatus(iHongbaoId, iCharId)


def RefreshSystemHongbaoStatus(iHongbaoId, iServer, sActivityName):
    if not g_WorldDlg:
        return None
    
    g_WorldDlg.RefreshSystemHongbaoStatus(iHongbaoId, iServer, sActivityName)


class CHongbaoListItem(combdialog.CCombSubWnd):
    
    def __init__(self, parent, dblessDataList):
        combdialog.CCombSubWnd.__init__(self, parent, 'dialog/worldhongbao/item.dlg')
        self.SetIgnoreEsc(True)
        self.m_sItemNameList = [
            'loc_icon',
            'img_iconbg',
            'icon',
            'text_name',
            'text_bless_name',
            'text_label',
            'text_msg',
            'img_msg_bg',
            'img_bg',
            'btn_look']
        self.m_oIconList = []
        self.m_dblessDataList = dblessDataList
        self.RefreshData()

    
    def RefreshBtnStatus(self, iBtnStatus, iIndex):
        '''
\t\t\xa8\xea\xb7s\xab\xf6\xb6s\xc5\xe3\xa5\xdc\xaa\xac\xbaA
\t\t:param iBtnStatus: 0-\xa4\xa3\xa5i\xbb\xe2\xa8\xfa\xa1A1-\xa5i\xbb\xe2\xa8\xfa
\t\t:param iIndex: \xa7\xc7\xb8\xb9
\t\t'''
        oBtn = self.GetObject('btn_look%d' % iIndex)
        sText = None if iBtnStatus == 0 else '\xbb\xe2\xa8\xfa'
        oBtn.SetText(sText)

    
    def RefreshIcon(self, iPhotoList, iSex, iID, iIndex, iPlayerID = None):
        import avatar
        (p1, p2, p3, p4) = iPhotoList
        oIcon = avatar.GetSmallImgBy4Int(self, p1, p2, p3, p4, iSex, iPlayerID = iPlayerID)
        (x, y, _, _) = self.GetLocData('loc_icon%d' % iIndex)
        oIcon.SetPos(x, y)
        self.m_oIconList.append(oIcon)

    
    def RefreshText(self, sName, sBlessName, sMsg, iIndex):
        '''
\t\t# \xa8\xea\xb7s\xa4\xe5\xa5\xbb\xabH\xae\xa7
\t\t:param sName: \xa6W\xa6r
\t\t:param sBlessName: \xb3Q\xaf\xac\xba\xd6\xaa\xcc\xa6W\xa6r
\t\t:param sMsg: \xaf\xac\xba\xd6\xbby
\t\t'''
        oName = self.GetObject('text_name%d' % iIndex)
        oName.SetText(sName)
        oBlessName = self.GetObject('text_bless_name%d' % iIndex)
        oBlessName.SetText(sBlessName)
        oMsg = self.GetObject('text_msg%d' % iIndex)
        oMsg.SetText(sMsg)

    
    def SetShowItem(self, iIndex, bShow):
        for sName in self.m_sItemNameList:
            sObjName = '%s%d' % (sName, iIndex)
            obj = self.GetObject(sObjName)
            obj.SetShow(bShow)
        

    
    def RefreshBlessData(self, dBlessData, iIndex):
        iIndex = iIndex + 1
        if not dBlessData:
            self.SetShowItem(iIndex, False)
            return None
        
        self.SetShowItem(iIndex, True)
        self.RefreshIcon(dBlessData['iPhotoList'], dBlessData['iSex'], dBlessData['iHongbaoId'], iIndex, dBlessData.get('iCharId', 0))
        self.RefreshText(dBlessData['sName'], dBlessData['sBlessName'], dBlessData['sMsg'], iIndex)
        self.RefreshBtnStatus(dBlessData['iBtnStatus'], iIndex)

    
    def RefreshData(self):
        iMaxIndex = \xcf\xc6n(self.m_dblessDataList) - 1
        for iIndex in xrange(ROW_ITEMS):
            if iIndex > iMaxIndex:
                dBlessData = { }
            else:
                dBlessData = self.m_dblessDataList[iIndex]
            self.RefreshBlessData(dBlessData, iIndex)
        

    
    def OnBtnEvent(self, iIndex):
        dBlessData = self.m_dblessDataList[iIndex]
        if dBlessData['iType'] == 0:
            networldhongbao.C2SCheckWorldHongbao(dBlessData['iHongbaoId'], dBlessData['iCharId'])
        else:
            import netsystemhongbao
            netsystemhongbao.C2SLinkSystemHongbao(dBlessData['iHongbaoId'], dBlessData['iServer'], dBlessData['sActivityName'])

    
    def OnMessage(self, iMsgId):
        if iMsgId in (1, 2, 3):
            iIndex = iMsgId - 1
            self.OnBtnEvent(iIndex)
        



class CWorldHongbaoDialog(combdialog.CCombDialog):
    
    def __init__(self, dBlessDataList):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/worldhongbao/main.dlg')
        interface.Center(self)
        self.m_dBlessDataList = dBlessDataList
        self.m_oList = None
        self.InitHotArea()
        self.RefreshData()
        self.InitTextColor()
        self.InitDesc()

    
    def InitDesc(self):
        import time
        import misc
        lstTime = time.localtime(misc.GetServerCurrentTime())
        tNow = (lstTime[1], lstTime[2])
        sShowMsg = ''
        for tDay, sMsg in SPECIAL_DAY.iteritems():
            (tStart, tEnd) = tDay
            if tNow <= tNow:
                pass
            elif tNow <= tEnd:
                sShowMsg = sMsg
                break
                continue
        
        if sShowMsg:
            self.GetObject('txt_price').SetText(sShowMsg)
        
        self.SetShowObject('img_discount', bool(sShowMsg))

    
    def InitTextColor(self):
        oTxtShow = self.GetObject('text_show')
        if oTxtShow:
            oTxtShow.SetColor(5592575)
        

    
    def RefreshHongbaoStatus(self, iHongbaoId, iCharId):
        for iIndex, dBlessData in enumerate(self.m_dBlessDataList):
            bEqualHongbaoId = iHongbaoId == dBlessData['iHongbaoId']
            bEqualCharId = iCharId == dBlessData['iCharId']
            if bEqualHongbaoId and bEqualCharId:
                oItemList = self.m_oList.GetItems()
                (iRow, iCol) = self.GetRowByIndex(iIndex)
                oItem = oItemList[iRow]
                oItem.RefreshBtnStatus(0, iCol)
                continue
        

    
    def RefreshSystemHongbaoStatus(self, iHongbaoId, iServer, sActivityName):
        for iIndex, dBlessData in enumerate(self.m_dBlessDataList):
            bEqualHongbaoId = iHongbaoId == dBlessData['iHongbaoId']
            bSystemHongbao = dBlessData.get('iServer', None)
            if bEqualHongbaoId and bSystemHongbao:
                oItemList = self.m_oList.GetItems()
                (iRow, iCol) = self.GetRowByIndex(iIndex)
                oItem = oItemList[iRow]
                oItem.RefreshBtnStatus(0, iCol)
                continue
        

    
    def InitHotArea(self):
        oHotShow = self.GetObject('hot_show')
        if oHotShow:
            oHotShow.SetEnterCB(self.ChangeTxtShowColor1)
            oHotShow.SetLeaveCB(self.ChangeTxtShowColor2)
        

    
    def ClearHotArea(self):
        oHotShow = self.GetObject('hot_show')
        if oHotShow:
            oHotShow.SetEnterCB(None)
            oHotShow.SetLeaveCB(None)
        

    
    def ChangeTxtShowColor1(self):
        oTxtShow = self.GetObject('text_show')
        if oTxtShow:
            oTxtShow.SetColor(interface.COLOR_2)
        

    
    def ChangeTxtShowColor2(self):
        oTxtShow = self.GetObject('text_show')
        if oTxtShow:
            oTxtShow.SetColor(5592575)
        

    
    def GetRowByIndex(self, iIndex):
        iIndex += 1
        if iIndex % ROW_ITEMS == 0:
            iRow = iIndex / ROW_ITEMS - 1
            iCol = 3
        else:
            iRow = iIndex / ROW_ITEMS
            iCol = iIndex % ROW_ITEMS
        LOG_DEBUG('iRow, iCol: ', iRow, iCol)
        return (iRow, iCol)

    
    def SetShowBg(self, bShow):
        oImgBg = self.GetObject('img_not_hongbao')
        oImgBg.SetShow(bShow)
        oTextBg = self.GetObject('text_not_hongbao')
        oTextBg.SetShow(bShow)

    
    def RefreshList(self):
        import math
        import ui
        (x, y, w, h) = self.GetLocData('loc_list')
        if not self.m_dBlessDataList:
            return None
        
        oList = ui.CList(self, x, y, w, h, alpha = 0, sType = 'SCROLL_YELLOW')
        iMaxRow = int(math.ceil(\xcf\xc6n(self.m_dBlessDataList) * 1 / ROW_ITEMS))
        for iRow in xrange(iMaxRow):
            iStartIndex = iRow * ROW_ITEMS
            iEndIndex = iStartIndex + ROW_ITEMS
            dBlessDataList = self.m_dBlessDataList[iStartIndex:iEndIndex]
            oItem = CHongbaoListItem(oList, dBlessDataList)
            oList.AddItem(oItem)
        
        oList.Refresh()
        oList.ResetScrollBar()
        self.m_oList = oList

    
    def RefreshData(self):
        self.SetShowBg(not (self.m_dBlessDataList))
        self.RefreshList()

    
    def OnCloseWindow(self):
        global g_WorldDlg
        self.ClearHotArea()
        if g_WorldDlg:
            g_WorldDlg = None
        

    
    def OnMessage(self, iMsgId):
        if iMsgId == 1:
            self.OnCloseWindow()
        elif iMsgId == 2:
            import dlgsendworldhongbao
            dlgsendworldhongbao.SetShow(True)
        elif iMsgId == 5:
            import appearanceavatarfrmview
            appearanceavatarfrmview.ShowAvatarFrmDlg(26)
