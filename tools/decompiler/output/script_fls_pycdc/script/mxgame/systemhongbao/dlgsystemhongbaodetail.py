# pycdc 交叉复核产物 · script.fls entry 2959
# co_filename(原始)='script/mxgame/systemhongbao/dlgsystemhongbaodetail.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_2959.pyc (Python 2.5)

import combdialog
import interface
import wrapinterface
g_RecordSystemHongbaoDlg = None

def ModuleReset():
    global g_RecordSystemHongbaoDlg
    g_RecordSystemHongbaoDlg = None


def SetShow(bShow, dHongbaoData):
    global g_RecordSystemHongbaoDlg, g_RecordSystemHongbaoDlg
    if bShow:
        if not g_RecordSystemHongbaoDlg:
            g_RecordSystemHongbaoDlg = CRecordSystemHongbaoDialog(dHongbaoData)
        
    else:
        g_RecordSystemHongbaoDlg = None


class CClickImage(interface.CImageBox):
    
    def __init__(self, parent, fname, path, tips = ''):
        interface.CImageBox.__init__(self, parent, fname, path, 0)
        self.m_TipsTxt = tips
        self.m_Tips = None

    
    def Enter(self):
        if self.m_TipsTxt == '':
            return None
        
        self.m_Tips = wrapinterface.CTextTips(None, -1, self.m_TipsTxt, interface.FontLT14_3, direct = 1)
        self.m_Tips.SetOwner(self)

    
    def Leave(self):
        self.m_Tips = None

    
    def LeftUp(self):
        pass

    
    def LeftDown(self):
        pass

    
    def RightUp(self):
        pass

    
    def RightDown(self):
        pass



class CRecordItem(combdialog.CCombSubWnd):
    
    def __init__(self, parent, dData):
        combdialog.CCombSubWnd.__init__(self, parent, 'dialog/worldhongbao/recordinfo.dlg')
        self.SetIgnoreEsc(True)
        self.m_dData = dData
        self.m_oIcon = None
        self.m_oImg1 = None
        self.m_oImg2 = None
        if self.GetObject('txt_relation'):
            pass
        self.GetObject('txt_relation').SetShow(False)
        self.RefreshData()

    
    def RefreshIcon(self):
        import avatar
        (p1, p2, p3, p4) = self.m_dData['iPhotoList']
        iSex = self.m_dData['iSex']
        (x, y, _, _) = self.GetLocData('loc_icon')
        oIcon = avatar.GetSmallImgBy4Int(self, p1, p2, p3, p4, iSex, 0.8)
        oIcon.SetPos(x, y)
        self.m_oIcon = oIcon

    
    def RefreshName(self, sName):
        oName = self.GetObject('text_name')
        oName.SetText(sName)

    
    def RefreshCash(self, iCash):
        import misc
        oCash = self.GetObject('text_cash')
        sCash = misc.GetCashString(iCash)
        sTextCashList = [
            '%s\xb2{\xaa\xf7' % sCash,
            '%s\xa9\xe8\xa5\xce\xaa\xf7' % sCash,
            '\xa4p\xba\xd6\xb3U']
        sText = sTextCashList[self.m_dData['iCashType'] - 1]
        oCash.SetText(sText)

    
    def RefreshTitle(self = None):
        bFast = self.m_dData.get('bFast', None)
        bMost = self.m_dData.get('bMost', None)
        LOG_DEBUG('bFast, bMost: ', bFast, bMost)
        if bFast:
            iCashType = self.m_dData['iCashType']
            sTips = None if iCashType == 3 else '\xa5H\xb0{\xb9q\xa4\xa7\xb6\xd5\xb2\xc4\xa4@\xad\xd3\xb6}\xb1\xd2\xa4F\xac\xf5\xa5]'
            (x, y, _, _) = self.GetLocData('loc_img1')
            oImg = CClickImage(self, 'combdialog/\xd4\xd3\xcd\xbc/\xc9\xc1\xb5\xe7.igs', 'interface', sTips)
            oImg.SetPos(x, y)
            self.m_oImg1 = oImg
        
        if bMost:
            if bFast:
                (x, y, _, _) = self.GetLocData('loc_img2')
            else:
                (x, y, _, _) = self.GetLocData('loc_img1')
            if self.m_dData['iCashType'] == 1:
                sTips = '\xeam\x91j\x9f\xc5\xe8Y\xb7m\xa8\xec\xac\xf5\xa5]\xaa\xba\xb3\xcc\xa6h\xb2{\xaa\xf7'
            elif self.m_dData['iCashType'] == 2:
                sTips = '\xc2E\xb9B\xb7\xed\xc0Y\xb7m\xa8\xec\xac\xf5\xa5]\xaa\xba\xb3\xcc\xa6h\xa9\xe8\xa5\xce\xaa\xf7'
            else:
                sTips = ''
            oImg = CClickImage(self, 'combdialog/\xd4\xd3\xcd\xbc/\xba\xe8\xd4\xcb.igs', 'interface', sTips)
            oImg.SetPos(x, y)
            self.m_oImg2 = oImg
        

    
    def RefreshData(self):
        self.RefreshIcon()
        self.RefreshName(self.m_dData['sName'])
        self.RefreshCash(self.m_dData['iCash'])
        self.RefreshTitle()



class CRecordSystemHongbaoDialog(combdialog.CCombDialog):
    
    def __init__(self, dHongbaoData):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/worldhongbao/record1.dlg')
        interface.Center(self)
        self.m_dHongbaoData = dHongbaoData
        self.m_oIcon = None
        self.m_oBlessIcon = None
        self.m_oRecordList = None
        self.RefreshData()

    
    def RefreshIcon(self, iPhotoList, iSex, iBlessPhotoList, iBlessSex):
        import avatar
        (iP1, iP2, iP3, iP4) = iPhotoList
        oIcon = avatar.GetSmallImgBy4Int(self, iP1, iP2, iP3, iP4, iSex)
        (iX, iY, _, _) = self.GetLocData('loc_icon')
        oIcon.SetPos(iX, iY)
        self.m_oIcon = oIcon
        (iBlessP1, iBlessP2, iBlessP3, iBlessP4) = iBlessPhotoList
        oBlessIcon = avatar.GetSmallImgBy4Int(self, iBlessP1, iBlessP2, iBlessP3, iBlessP4, iBlessSex)
        (iBlessX, iBlessY, _, _) = self.GetLocData('loc_bless_icon')
        oBlessIcon.SetPos(iBlessX, iBlessY)
        self.m_oBlessIcon = oBlessIcon

    
    def RefreshName(self, sName, sBlessName):
        oName = self.GetObject('text_name')
        oName.SetText(sName)
        oBlessNmae = self.GetObject('text_bless_name')
        oBlessNmae.SetText(sBlessName)

    
    def RefreshMsg(self, sMsg):
        oMsg = self.GetObject('text_msg')
        oMsg.SetText(sMsg)

    
    def RefreshCash(self, bHongbaoStatus, iCash, iCashType):
        import misc
        if iCash is None and iCashType is None:
            sText = None if bHongbaoStatus else ''
        elif iCashType == 3:
            sText = '\xa7A\xc0\xf2\xb1o\xa4F\xa4p\xba\xd6\xb3U'
        else:
            sCash = misc.GetCashString(iCash)
            if iCashType == 1:
                sText = '\xa7A\xc0\xf2\xb1o\xa4F%s\xb2{\xaa\xf7' % sCash
            else:
                sText = '\xa7A\xc0\xf2\xb1o\xa4F%s\xa9\xe8\xa5\xce\xaa\xf7' % sCash
        oCash = self.GetObject('text_cash')
        oCash.SetText(sText)

    
    def RefreshTotal(self, iNum, iMaxNum):
        import misc
        sText = '\xa4w\xbb\xe2\xa8\xfa%d/%d' % (iNum, iMaxNum)
        oTotalCash = self.GetObject('text_total')
        oTotalCash.SetText(sText)

    
    def GetDataById(self, dDataList, iId):
        for dData in dDataList:
            if iId == dData['iId']:
                return dData
                continue
        

    
    def SortOtherRecordData(self, dRecordDataList, iFastIdList, iMostIdList):
        '''
\t\t\xb1\xc6\xa7\xc7\xac\xf5\xa5]\xbc\xc6\xbe\xda
\t\t:param dRecordDataList:\t\xad\xec\xa9l\xac\xf5\xa5]\xbc\xc6\xbe\xda
\t\t:param iFastIdList:\t\xb3\xcc\xa7\xd6\xbb\xe2\xa8\xfa\xac\xf5\xa5]ID\xa6C\xaa\xed-\xb2{\xaa\xf7, \xba\xd6\xb3U, \xa9\xe8\xa5\xce\xaa\xf7
\t\t:param iMostIdList:\t\xb3\xcc\xa6h\xbb\xe2\xa8\xfa\xac\xf5\xa5]
\t\t:return: \xac\xf5\xa5]\xb0O\xbf\xfd\xa6C\xaa\xed
\t\t'''
        import copy
        dTempList = []
        if not iFastIdList and not iMostIdList:
            return dRecordDataList
        
        dNewRecordList = copy.deepcopy(dRecordDataList)
        for iFastId in iFastIdList:
            for dRecord in dNewRecordList:
                if dRecord['iId'] == iFastId:
                    dRecord['bFast'] = True
                    dTempList.append(dRecord)
                    dNewRecordList.remove(dRecord)
                    break
                    continue
            
        
        for iMostId in iMostIdList:
            for dRecord in dNewRecordList:
                if dRecord['iId'] == iMostId:
                    dRecord['bMost'] = True
                    dTempList.append(dRecord)
                    dNewRecordList.remove(dRecord)
                    break
                    continue
            
        
        dTempList.extend(dNewRecordList)
        return dTempList

    
    def RefreshRecordList(self, dRecordList, iFastIdList, iMostIdList):
        import \xfci
        dNewRecordList = self.SortOtherRecordData(dRecordList, iFastIdList, iMostIdList)
        (x, y, w, h) = self.GetLocData('loc_list')
        oRecordList = \xfci.CList(self, x, y, w, h, alpha = 0, sType = 'SCROLL_YELLOW')
        for dRecordData in dNewRecordList:
            oItem = CRecordItem(oRecordList, dRecordData)
            oRecordList.AddItem(oItem)
        
        oRecordList.Refresh()
        oRecordList.ResetScrollBar()
        self.m_oRecordList = oRecordList

    
    def RefreshData(self):
        dData = self.m_dHongbaoData
        self.RefreshIcon(dData['iPhotoList'], dData['iSex'], dData['iBlessPhotoList'], dData['iBlessSex'])
        self.RefreshName(dData['sName'], dData['sBlessName'])
        self.RefreshMsg(dData['sMsg'])
        (iMyCash, iCashType) = self.GetMyCash(dData['dRecordList'])
        LOG_DEBUG('iMyCash: ', iMyCash)
        LOG_DEBUG('iCashType: ', iCashType)
        self.RefreshCash(dData['iCurNum'] >= dData['iMaxNum'], iMyCash, iCashType)
        self.RefreshTotal(dData['iCurNum'], dData['iMaxNum'])
        self.RefreshRecordList(dData['dRecordList'], dData['iFastIdList'], dData['iMostIdList'])

    
    def GetMyCash(self, dRecordList):
        import hero
        iHeroId = hero.GetHeroID()
        for dData in dRecordList:
            if dData['iId'] == iHeroId:
                return (dData['iCash'], dData['iCashType'])
                continue
        
        return (None, None)

    
    def OnCloseWindow(self):
        global g_RecordSystemHongbaoDlg
        g_RecordSystemHongbaoDlg = None

    
    def OnMessage(self, iMsgId):
        if iMsgId == 1:
            self.OnCloseWindow()
