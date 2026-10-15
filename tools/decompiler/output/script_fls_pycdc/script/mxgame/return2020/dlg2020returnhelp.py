# pycdc 交叉复核产物 · script.fls entry 421
# co_filename(原始)='script/mxgame/return2020/dlg2020returnhelp.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_421.pyc (Python 2.5)

import avatar
import avatarfrmstyledata
import combdialog
import interface
import item
import misc
import pagedlgbase
import seamaildefines
import slot
import ui
import wrapinterface

class CRecruitHelpDialog(combdialog.CCombSubWnd, slot.ISignalSubject, pagedlgbase.COnePageDlgBase):
    SS_OnPageOpen = 'SS_OnPageOpen()'
    SS_ClickPreviewBtn = 'SS_ClickPreviewBtn(iIdx)'
    SS_ClickFindBtn = 'SS_ClickFindBtn()'
    SS_ClickGoBtn = 'SS_ClickGoBtn(iIdx)'
    SS_ClickGetReward = 'SS_ClickGetReward(iIdx)'
    SS_RequestData = 'SS_RequestData'
    sUIName = 'dialog/new_player_present/return/return_assist.dlg'
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent)
        pagedlgbase.COnePageDlgBase.__init__(self)
        self.m_oTaskIconList = []
        self.m_dPlayerPhoto = { }
        self.m_dPlayerPhotoClickBox = { }
        self.m_dRewardAni = { }
        self.ssInit()
        self.InitDelegate()

    
    def SetTaskInfo(self, dTaskList):
        self.m_oTaskIconList = []
        if not dTaskList:
            for iIdx in xrange(2):
                if iIdx == 0:
                    self.GetObject('text_num%d' % (iIdx + 1)).SetText('%s/%s' % (0, 30))
                else:
                    self.GetObject('text_num%d' % (iIdx + 1)).SetText('%s/%s' % (0, 1))
                self.GetObject('progress_activity%d' % (iIdx + 1)).SetRate(0)
            
            return None
        
        for iIdx in xrange(min(2, \xd5en(dTaskList))):
            dInfo = dTaskList[iIdx]
            self.GetObject('text_target%d' % (iIdx + 1)).SetText(dInfo['sDesc'])
            self.GetObject('text_rewardnum%d' % (iIdx + 1)).SetText('x%s' % dInfo['iReward'])
            self.GetObject('text_num%d' % (iIdx + 1)).SetText('%s/%s' % (dInfo['iCur'], dInfo['iMax']))
            self.GetObject('progress_activity%d' % (iIdx + 1)).SetRate(min(1000, dInfo['iCur'] * 1000 / dInfo['iMax']))
            if dInfo['tIconPath']:
                oImg = ui.CImage(self.GetObject('loc_icon%d' % (iIdx + 1)), dInfo['tIconPath'][0], dInfo['tIconPath'][1])
                interface.Center(oImg, dInfo['tIconOffset'][0], dInfo['tIconOffset'][1])
                self.m_oTaskIconList.append(oImg)
                continue
        

    
    def SetPlayerInfo(self, iPos, dInfo):
        iPos += 1
        if dInfo is None:
            self.m_dPlayerPhoto[iPos] = None
            self.m_dPlayerPhotoClickBox[iPos] = None
        else:
            (iX, iY) = self.GetObject('loc_touxiang%s' % iPos).GetPos()
            iZ = self.GetObject('loc_touxiang%s' % iPos).GetZ()
            (iW, iH) = self.GetObject('loc_touxiang%s' % iPos).GetSize()
            tPhoto = dInfo['tPhoto']
            iSex = dInfo['iSex']
            oPhoto = avatar.GetSmallImgBy4Int(self, tPhoto[0], tPhoto[1], tPhoto[2], tPhoto[3], iSex)
            avatar.CheckAndAutoAddAvatarFrm(oPhoto, dInfo['iID'], avatarfrmstyledata.AVATAR_FRM_LOCATION_6)
            oPhoto.SetPos(iX, iY)
            oPhoto.SetZ(iZ)
            self.m_dPlayerPhoto[iPos] = oPhoto
            oBox = interface.CClickBox(oPhoto, iW, iH)
            oBox.SetRightUpCB(misc.Functor(self.OnClickPhoto, dInfo['iID']))
            self.m_dPlayerPhotoClickBox[iPos] = oBox

    
    def OnClickPhoto(self, iPlayerID):
        import netfriend
        netfriend.C2SFindPlayerByID(iPlayerID)

    
    def SetRewardIconState(self, iPos, iState):
        iPos += 1
        if iState == seamaildefines.REWARDSTATE_CANGET:
            (iX, iY, iW, iH) = self.GetLocData('img_summon%s' % iPos)
            oFlashAni = interface.CSpriteObject(self, '\xd4\xd3\xcd\xbc/\xce\xef\xc6\xb7\xb1\xdf\xbf\xf2\xc1\xf7\xb9\xe2.spr', 'interface')
            oFlashAni.SetPos(iX + iW / 2 - 1, iY + iH / 2 - 1)
            oFlashAni.SetZ(11)
            oFlashAni.CreateCommand(1, 'animation')
            self.m_dRewardAni[iPos] = oFlashAni
        else:
            self.m_dRewardAni[iPos] = None
        if iState == seamaildefines.REWARDSTATE_HASGET:
            self.GetObject('img_gift%s' % iPos).SetGrey()
        else:
            self.GetObject('img_gift%s' % iPos).SetLight(8)

    
    def ShowPreviewDlg(self, dItemsData):
        oDlg = CPreviewRewardDialog.OpenUI()
        oDlg.SetData(dItemsData)

    
    def ClosePreviewDlg(self):
        CPreviewRewardDialog.CloseUI()

    
    def SetHelpProcess(self, iTotal):
        self.GetObject('text_progressnow').SetText(str(iTotal))
        self.GetObject('progress_activity3').SetRate(min(1000, iTotal * 1000 / max(seamaildefines.REWARDCONFIG.values())))

    
    def VOpenPage(self, dExtend = None):
        self.SetShow(True)
        self.ssEmit(self.SS_OnPageOpen)
        self.ssEmit(self.SS_RequestData)

    
    def VClose(self):
        self.SetShow(False)

    
    def InitDelegate(self):
        import dgt2020returnhelp
        self.m_DelegateList = [
            dgt2020returnhelp.C2020ReturnHelpDelegate(self)]

    
    def HideFindBtn(self, bIsHide):
        oFindBtn = self.GetObject('btn_find')
        oFindBtn.SetShow(not bIsHide)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.ssEmit(self.SS_ClickFindBtn)
        elif iMsgID in (2, 3):
            self.ssEmit(self.SS_ClickGoBtn, iMsgID - 2)
        elif iMsgID in (5, 6, 7):
            self.ssEmit(self.SS_ClickGetReward, iMsgID - 5)
        elif iMsgID in (8, 9, 10):
            self.ssEmit(self.SS_ClickPreviewBtn, iMsgID - 8)
        



class CSearchTeamDialog(combdialog.CCombDialog):
    sUIName = 'dialog/new_player_present/return/return_selectfriend.dlg'
    
    def __init__(self, oParent):
        combdialog.CCombDialog.__init__(self, oParent)



class CPreviewRewardDialog(combdialog.CCombDialog):
    sUIName = 'dialog/new_player_present/return/return_preview.dlg'
    
    def __init__(self, oParent):
        combdialog.CCombDialog.__init__(self, oParent)
        self.m_oItemList = []

    
    def SetData(self, dData):
        self.m_oItemList = []
        self.GetObject('text_timetitle').SetText(dData['sTitle'])
        oImageFrame = self.GetObject('img_item2')
        for iIdx, dItem in enumerate(dData['dItemList']):
            oLoc = oImageFrame.GetImageByIndex(iIdx)
            if dItem['iShape'] == 9002:
                dItem['iAmount'] = 300000
            
            iShape = None if dItem['iShape'] not in item.DICT_SPECIALSHAPE else item.ReplaceShape(dItem['iShape'])
            oIcon = CPreviewItemIcon(oLoc, iShape, dItem['iAmount'], 100 + iIdx)
            self.m_oItemList.append(oIcon)
        

    
    def CloseWindow(self):
        self.CloseUI()

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        



class CPreviewItemIcon(wrapinterface.CItemIcon):
    
    def Enter(self):
        self.ShowTips()

    
    def Leave(self):
        self.HideTips()

    
    def SetQuantity(self, quantity, flag = False, sQuantityFont = None):
        import gamefont
        self.m_Quantity = quantity
        self.m_QuantityText = None
        if quantity > 1 or flag:
            font = gamefont.CreateFont(gamefont.TYPE_SONGTI, 14, bEdge = True)
            if quantity >= 10000:
                sStr = '%2d\xb8U' % quantity / 10000
            else:
                sStr = '%2d' % quantity
            self.m_QuantityText = interface.CTextObject(self.m_Image, sStr, font, 16777215, 0)
            (w, _) = self.m_QuantityText.GetSize()
            self.m_QuantityText.SetPos(45 - w, 28)
