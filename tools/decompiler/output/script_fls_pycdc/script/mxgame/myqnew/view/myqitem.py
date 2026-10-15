# pycdc 交叉复核产物 · script.fls entry 414
# co_filename(原始)='script/mxgame/myqnew/view/myqitem.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_414.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: ${DATE} ${TIME}
\xd7\xf7\xd5\xdf: ${AuthorName}
\xce\xc4\xbc\xfe: ${NAME}
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import math
import avatar
import C_sys
import banword
import defines
import interface
import combdialog
import misc
import newmyqbase
import myqdefine
import myqinterface
import myqsignal
import ui
import cursor
import usermacro
import wrapinterface
import wrapui
import myqphotoitem

class CLineDlgItem(combdialog.CCombSubWnd):
    
    def __init__(self, oParent, sDlgName):
        combdialog.CCombSubWnd.__init__(self, oParent, sDlgName)
        self.SetIgnoreEsc(True)

    
    def GetSize(self):
        if self.GetObject('bg'):
            return self.GetObject('bg').GetSize()
        elif self.GetObject('loc_bg'):
            return self.GetObject('loc_bg').GetSize()
        elif self.GetObject('frame_bg'):
            return self.GetObject('frame_bg').GetSize()
        else:
            return (0, 0)

    
    def Hold(self):
        oParent = self.GetParent()
        if isinstance(oParent, CCutTalkList):
            oParent.Hold()
        

    
    def DoHoldLeftDown(self, iHoldX, iHoldY):
        oParent = self.GetParent()
        if isinstance(oParent, CCutTalkList):
            oParent.DoHoldLeftDown(iHoldX, iHoldY)
        

    
    def DoHoldLeftUp(self):
        oParent = self.GetParent()
        if isinstance(oParent, CCutTalkList):
            oParent.DoHoldLeftUp()
        

    
    def DoCancel(self):
        pass

    
    def Show(self):
        pass



class CCutTalkList(ui.CCutList, interface.CHoldObject):
    
    def __init__(self, oParent, iX, iY, iW, iH):
        ui.CCutList.__init__(self, oParent, iW, iH, iVSpace = 0, sBarStyle = 'SCROLL_NORMAL', bBarInPanel = False)
        self.m_bIsRefresh = False
        self.m_iCounter = 0
        self.m_iListType = myqdefine.TYPE_MYMAIN
        self.m_iScrollDir = 0
        self.m_tCachePos = 0
        self.m_iCursorY = 0
        self.SetPos(iX, iY)

    
    def ResetScroller(self):
        self.ResetBarStype('SCROLL_NORMAL', defines.STYLE5_KEY)

    
    def SetListType(self, iType):
        self.m_iListType = iType

    
    def SetIsRefresh(self, bRefresh):
        self.m_bIsRefresh = bRefresh

    
    def GetLen(self):
        return len(self.m_ItemList)

    
    def DelItem(self, iPos):
        if iPos > iPos:
            pass
        elif iPos > self.GetLen():
            return None
        
        del self.m_ItemList[iPos]

    
    def Topmost(self):
        pass

    
    def Hold(self):
        (iX, iY) = cursor.GetPos()
        iWheel = abs(iY - self.m_iCursorY)
        if iWheel > 0:
            bUp = iY > self.m_iCursorY
            if bUp:
                self.MouseWheelUp(iWheel * 0.03)
            else:
                self.MouseWheelDown(iWheel * 0.03)
            self.m_iCursorY = iY
        

    
    def Leave(self):
        if interface.Hold:
            if interface.Hold.Get() == self or isinstance(myqphotoitem.CPhoto, interface.Hold.Get()):
                self.LeftUp()
            

    
    def DoHoldLeftDown(self, iHoldX, iHoldY):
        interface.Hold = interface.CShadowObject(self)
        interface.HoldX = iHoldX
        interface.HoldY = iHoldY
        (_, self.m_iCursorY) = cursor.GetPos()
        self.IgnoreSonMessage(True)

    
    def DoHoldLeftUp(self):
        if interface.Hold:
            interface.Hold = None
            self.IgnoreSonMessage(False)
        
        self.m_iCursorY = 0

    
    def MouseWheelUp(self, p):
        ui.CCutList.MouseWheelUp(self, p)
        self.m_iScrollDir = 0
        myqinterface.GetMYQContext().CloseFriendMenu()

    
    def MouseWheelDown(self, p):
        ui.CCutList.MouseWheelDown(self, p)
        self.m_iScrollDir = 1
        myqinterface.GetMYQContext().CloseFriendMenu()

    
    def ScrollToItem(self, idx):
        self.m_iCounter = 0
        ui.CCutList.ScrollToItem(self, idx)

    
    def BarChange(self, iPos):
        ui.CCutList.BarChange(self, iPos)
        if self.m_tCachePos != iPos:
            self.m_tCachePos = iPos
            self.m_iCounter = 0
        elif self.m_iScrollDir == 0:
            self.m_iCounter += 1
        elif self.m_iScrollDir == 1:
            self.m_iCounter += 1
        
        if self.m_iCounter > 4:
            if self.m_iListType == myqdefine.TYPE_MYMAIN:
                myqsignal.Emit(myqsignal.SS_RequestRefresh, self.m_iScrollDir, False)
            else:
                myqsignal.Emit(myqsignal.SS_RequestRefresh_Friend, self.m_iScrollDir, False)
            self.m_iCounter = 0
        



class CLoadingItem(interface.CBoxObject):
    Height = 30
    
    def GetNewID(self):
        return self.m_sMomentID

    
    def __init__(self, parent, w):
        interface.CBoxObject.__init__(self, parent, w, self.Height, 16777215, 0)
        self.m_sMomentID = -1
        self.m_Width = w
        self.m_TextObj = interface.CTextObject(self, '\xa5\xbf\xa6b\xa5[\xb8\xfc\xa4\xa4,\xbd\xd0\xb5y\xad\xd4...', interface.FontLT12, interface.COLOR_9)
        (tw, th) = self.m_TextObj.GetSize()
        x = (w - tw) / 2
        y = (self.Height - th) / 2
        self.m_TextObj.SetPos(x, y)
        filename = 'combdialog/\xd2\xe6\xcd\xf8\xc8\xa6/loading\xb6\xaf\xbb\xad/loading.spr'
        obj = ui.CImage(None, 'combdialog/\xd2\xe6\xcd\xf8\xc8\xa6/loading\xb6\xaf\xbb\xad/loading.igs', interface.UIPath)
        (iw, ih) = obj.GetSize()
        self.m_LoadImg = interface.CSpriteObject(self, filename, interface.UIPath)
        x = x - iw - 2
        y = (self.Height - ih) / 2
        self.m_LoadImg.SetPos(x, y)
        self.m_LoadImg.CreateCommand(1, 'animation')



class CBoxObject(interface.CBoxObject, interface.CBase):
    
    def __init__(self, parent, w, h):
        interface.CBoxObject.__init__(self, parent, w, h, 0, 0)
        self.MessageProcess()
        self.Topmost()

    
    def Enter(self):
        parent = self.GetParent()
        if parent:
            parent.Enter()
        

    
    def Leave(self):
        parent = self.GetParent()
        if parent:
            parent.Leave()
        

    
    def LeftUp(self):
        (x, y) = cursor.GetPos()
        objects = C_sys.GetObjects(x, y)
        for obj in objects:
            funName = 'LeftUp'
            if isinstance(obj, interface.CButton) and hasattr(obj, funName):
                getattr(obj, funName)()
                break
                continue
        



class CTalkContent(newmyqbase.CTalkContent, CLineDlgItem):
    
    def __init__(self, oParent, w):
        CLineDlgItem.__init__(self, oParent, 'dialog4/mengyouquan_new/myq_top.dlg')
        self.m_iWidth = w
        self.m_iHeight = 0
        self.m_bFoldFlag = True
        self.m_oTalkText = self.GetObject('rtxt_content')
        self.m_oHeadShot = None
        self.m_oHotBox = None
        self.SetShowObject('loc_hotmoment', False)
        self.SetShowObject('loc_realshow', False)

    
    def Show(self):
        self.ShowHeadShot()
        self.ShowName()
        self.ShowContent()
        self.ShowCateGory()
        self.ShowBtnType()
        self.Refresh()

    
    def ShowBtnType(self):
        pass

    
    def ShowCateGory(self):
        import friend
        iUserID = myqinterface.GetMYQContext().GetRoleID()
        bMine = self.m_iUserID == iUserID
        bFriend = friend.IsFriend(self.m_iUserID)
        bSameGroup = myqinterface.GetMYQContext().GetRelationShip(self.m_iUserID) == myqdefine.RELATION_SAMEGROUP
        if bSameGroup == myqdefine.RELATION_STRANGER:
            bSameGroup = self.m_bIsSameGroup
        
        sText = ''
        if bMine:
            sText = '\xa6\xdb\xa4v'
        elif bFriend:
            sText = '\xa6n\xa4\xcd'
        elif bSameGroup:
            sText = '\xa6P\xc0\xb0'
        else:
            sText = '\xad\xaf\xa5\xcd\xa4H'
        self.GetObject('text_category').SetText(sText)

    
    def ShowHeadShot(self, sPath = ''):
        if not sPath:
            sPath = self.m_sHeadIcon
        
        if not sPath or type(sPath) == int:
            sPath = myqdefine.DEFAULT_TALK_PIC
        
        if not self.m_oHeadShot:
            oLocHead = self.GetObject('loc_touxiang')
            self.m_oHeadShot = CTalkHeadShot(self, sPath, 3, 50, 50, iScale = 0.85, iPlayerID = self.m_iUserID)
            self.m_oHeadShot.SetPos(*oLocHead.GetPos())
            iUserID = myqinterface.GetMYQContext().GetRoleID()
            bMine = self.m_iUserID == iUserID
            if not bMine:
                self.m_oHeadShot.SetClickCB(misc.Functor(self.OpenFriendDlg))
            
            self.m_oHeadShot.SetMouseMoveCB(misc.Functor(self.MouseWheelDown), misc.Functor(self.MouseWheelUp))
        else:
            self.m_oHeadShot.RefreshHead(sPath)

    
    def ShowName(self, sName = ''):
        if not sName:
            sName = self.m_sUserName
        
        self.GetObject('text_name').SetText(sName)

    
    def ShowContent(self):
        sContent = banword.IsValidChat(self.m_sContent)[1]
        sContent = newmyqbase.ReplaceForwardLink(sContent)
        sContent = newmyqbase.ReplaceEmoteCn2Num(sContent)
        (sContent, _, self.m_LinkObj) = wrapui.ReplaceLink(sContent, self)
        (iWidth, _) = self.m_oTalkText.GetSize()
        iFont = self.m_oTalkText.GetFont()
        iShowPos = newmyqbase.GetExtandTxtPos(iWidth, iFont, sContent, 2)
        iShowPos5 = newmyqbase.GetExtandTxtPos(iWidth, iFont, sContent, 5)
        if iShowPos:
            if self.m_bFoldFlag:
                self.m_bFoldFlag = False
                restcontent = sContent[iShowPos:]
                sContent = sContent[:iShowPos]
                sContent += '...#B#c(%d)#u\xaei\xb6}#n#c()#n' % len(self.m_LinkObj)
            else:
                sContent += ' #B#c(%d)#u\xa6\xac\xb0_#n#c()#n' % len(self.m_LinkObj)
                self.m_bFoldFlag = True
        
        if (interface.IsStyle3() or interface.IsStyle4()) and '#G' in sContent:
            sContent = sContent.replace('#G', '#CLR3#n')
        
        self.m_oTalkText.SetText(sContent)
        sAtText = ''
        for sName in self.m_sAiteList:
            sAtText += '@%s ' % sName
        
        self.GetObject('rtxt_aitelist').SetText(sAtText)

    
    def OpenFriendDlg(self):
        myqinterface.CacheFriendInfo(self.m_iUserID, self.m_sUserName, self.m_sHeadIcon)
        myqinterface.ShowFriendMenu(self.m_iUserID, self.m_sUserName)

    
    def Refresh(self):
        self.SetShowObject('loc_hotmoment', self.m_bHotMoment)
        if not (self.m_bHotMoment):
            pass
        self.SetShowObject('loc_realshow', self.m_bRealShow)
        if not (self.m_bHotMoment):
            pass
        self.SetShowObject('loc_biaoqian', not (self.m_bRealShow))
        (_, iHeight) = self.m_oTalkText.GetTextSize()
        iTextHeight = self.m_oTalkText.GetPos()[1] + iHeight
        oAtText = self.GetObject('rtxt_aitelist')
        oAtText.SetShow(bool(self.m_sAiteList))
        (_, iAiteHeight) = oAtText.GetTextSize()
        if self.m_sAiteList:
            iTextHeight += 2
            oAtText.SetPos(oAtText.GetPos()[0], iTextHeight)
            iTextHeight += iAiteHeight
        
        oCateGory = self.GetObject('text_category')
        oLocCateGory = self.GetObject('loc_biaoqian')
        iCateGoryHeight = oLocCateGory.GetPos()[1] + oCateGory.GetSize()[1] + 2
        self.m_iHeight = max(iTextHeight, iCateGoryHeight)
        self.GetObject('loc_bg').SetSize(self.m_iWidth, self.m_iHeight)
        self.m_oHotBox = ui.CHotBox(self, self.m_iWidth, self.m_iHeight, 0)
        self.m_oHotBox.SetMouseWheelEnable(True)
        self.m_oHotBox.SetLeftUpCB(misc.Functor(self.OnHotLeftUp))
        self.m_oHotBox.SetLeftDownCB(misc.Functor(self.OnHotLeftDown))
        myqsignal.Emit(myqsignal.SS_RefreshTaskList)

    
    def RefreshTime(self):
        pass

    
    def OnHotLeftUp(self):
        CLineDlgItem.LeftUp(self)

    
    def OnHotLeftDown(self):
        CLineDlgItem.LeftDown(self)
        (iX, iY) = cursor.GetPos()
        (iTextX, iTextY) = self.m_oTalkText.GetScreenPos()
        iClickID = self.m_oTalkText.GetTextObj().ClickID(iX - iTextX, iY - iTextY)
        if iClickID >= 0 and self.m_LinkObj.get(iClickID, None):
            self.m_LinkObj[iClickID].OnLeftUp()
            return None
        
        if iClickID != -1:
            self.ShowContent()
            self.Refresh()
        

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.OpenFriendDlg()
        



class CTalkContentSmall(CTalkContent):
    
    def __init__(self, oParent, w):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/friend/friend_myq/friend_myq_top.dlg')
        self.m_iWidth = w
        self.m_iHeight = 0
        self.m_bFoldFlag = True
        self.m_oTalkText = self.GetObject('rtxt_content')
        self.m_oHeadShot = None
        self.m_oHotBox = None
        self.SetIgnoreEsc(True)
        self.InitDlg()

    
    def InitDlg(self):
        self.GetObject('btn_del').SetZ(10)
        self.GetObject('btn_jubao').SetZ(10)

    
    def ShowBtnType(self):
        iOwnerID = self.m_iUserID
        iUserID = myqinterface.GetMYQContext().GetRoleID()
        if iOwnerID == iUserID:
            self.GetObject('btn_del').SetShow(True)
            self.GetObject('btn_jubao').SetShow(False)
        else:
            self.GetObject('btn_del').SetShow(False)
            self.GetObject('btn_jubao').SetShow(True)

    
    def ShowHeadShot(self, sPath = ''):
        if not sPath:
            sPath = self.m_sHeadIcon
        
        if not sPath or type(sPath) == int:
            sPath = myqdefine.DEFAULT_TALK_PIC
        
        if not self.m_oHeadShot:
            oLocHead = self.GetObject('loc_touxiang')
            self.m_oHeadShot = CTalkHeadShot(self, sPath, 3, 45, 45, iScale = 0.7, iPlayerID = self.m_iUserID)
            self.m_oHeadShot.SetPos(*oLocHead.GetPos())
            iUserID = myqinterface.GetMYQContext().GetRoleID()
            bMine = self.m_iUserID == iUserID
            if not bMine:
                self.m_oHeadShot.SetClickCB(misc.Functor(self.OpenFriendDlg))
            
            self.m_oHeadShot.SetMouseMoveCB(misc.Functor(self.MouseWheelDown), misc.Functor(self.MouseWheelUp))
        else:
            self.m_oHeadShot.RefreshHead(sPath)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            myqsignal.Emit(myqsignal.SS_DeleteNew, self.m_sMomentID)
        elif iMsgID == 2:
            import dlgreport
            dlgreport.C2GSNewOpenReport(self.m_iUserID, self.m_sUserName, dlgreport.TYPE_HAOYOUXIU, dData = {
                'sMomentID': self.m_sMomentID,
                'sReport': self.m_sReportDescText }, bForce = True)
        



class CTalkHeadShot(interface.CBoxObject, interface.CClickObject):
    
    def __init__(self, parent, url, itype, w = 45, h = 45, iScale = 0.9, iPlayerID = None):
        import myqphotoitem
        interface.CBoxObject.__init__(self, parent, w * iScale, h * iScale, 16777215, 0)
        interface.CClickObject.__init__(self, 1)
        if type(url) in (list, tuple):
            (p1, p2, p3, p4) = url
            (p1, p2, p3, p4) = avatar.TransPhotoInt(p1, p2, p3, p4)
            self.m_HeadShot = avatar.GetSmallImgBy4Int(self, p1, p2, p3, p4, scale = iScale)
            if iPlayerID:
                avatar.UpdateAvatarPal(self.m_HeadShot, iPlayerID)
            
        elif type(url) == int:
            self.m_HeadShot = ui.CImage(self, 'combdialog/\xba\xc3\xd3\xd1\xc1\xc4\xcc\xec/icon/%d.igs' % url, 'interface')
        elif type(url) == str:
            self.m_HeadShot = myqphotoitem.CPhotoObject(self, url, itype, w * iScale, h * iScale)
        
        self.m_sHead = url
        self.m_iType = itype
        self.m_iScale = iScale
        self.m_Width = w
        self.m_Height = h
        self.m_oClickCB = None
        self.m_oMouseeDownCB = None
        self.m_oMouseeUpCB = None
        self.m_sEnterShowName = ''
        self.m_oTips = None

    
    def RefreshHead(self, sHead):
        import myqphotoitem
        if self.m_sHead == sHead:
            return None
        
        self.m_sHead = sHead
        if type(sHead) in (list, tuple):
            (p1, p2, p3, p4) = sHead
            par = self.GetParent()
            self.m_HeadShot = avatar.GetSmallImgBy4Int(self, p1, p2, p3, p4, scale = self.m_iScale)
        elif type(sHead) == int:
            self.m_HeadShot = ui.CImage(self, 'combdialog/\xba\xc3\xd3\xd1\xc1\xc4\xcc\xec/icon/%d.igs' % sHead, 'interface')
        elif type(sHead) == str:
            self.m_HeadShot = myqphotoitem.CPhotoObject(self, sHead, self.m_iType, self.m_Width, self.m_Height)
        

    
    def SetGrey(self):
        if self.m_HeadShot and isinstance(self.m_HeadShot, avatar.CSmallAvatarImg):
            self.m_HeadShot.SetGrey()
        

    
    def SetEnterShowName(self, sName):
        self.m_sEnterShowName = sName

    
    def SetClickCB(self, oCB):
        self.m_oClickCB = oCB

    
    def SetMouseMoveCB(self, oDownCB, oUpCB):
        self.m_oMouseeDownCB = oDownCB
        self.m_oMouseeUpCB = oUpCB

    
    def Enter(self):
        if self.m_oClickCB:
            cursor.Load(cursor.LINK_CURSOR)
        
        if self.m_sEnterShowName:
            self.m_oTips = wrapinterface.CTextTips(None, -1, self.m_sEnterShowName, interface.FontLT14_3, direct = 1)
            self.m_oTips.SetOwner(self)
        

    
    def Leave(self):
        if self.m_oClickCB:
            cursor.Load(cursor.NORMAL_CURSOR)
        
        self.m_oTips = None

    
    def LeftUp(self):
        if self.m_oClickCB:
            self.m_oClickCB()
        

    
    def MouseWheelDown(self, p):
        if self.m_oMouseeDownCB:
            self.m_oMouseeDownCB(p)
        

    
    def MouseWheelUp(self, p):
        if self.m_oMouseeUpCB:
            self.m_oMouseeUpCB(p)
        



class CTalkPhoto(interface.CBoxObject, newmyqbase.CTalkPhoto):
    BASE = 10
    PSize = (120, 120)
    
    def __init__(self, parent, w, h, posx = 70, \x83\x9c\x80\x8a = 0):
        interface.CBoxObject.__init__(self, parent, w, h, 16777215, 0)
        self.m_iWidth = w
        self.m_iHeight = h
        self.m_PosX = posx
        self.m_PosY = \x83\x9c\x80\x8a
        self.m_Type = 5
        self.m_oPhotoList = []
        self.m_oTextNum = None

    
    def Show(self):
        import myqphotoitem
        sPhotoList = self.m_sPhotoUrl.split(',')
        self.m_oPhotoList = []
        self.m_iHeight = 0
        iType = 1
        for iIdx, sPath in enumerate(sPhotoList):
            oPhoto = myqphotoitem.CPhoto(self, sPath, iType, self.PSize[0], self.PSize[1], iIdx + self.BASE)
            iX = (iIdx % 2) * (self.PSize[0] + 5) + self.m_PosX
            iY = (iIdx / 2) * (self.PSize[1] + 5) + self.m_PosY
            oPhoto.SetPos(iX, iY)
            self.m_oPhotoList.append(oPhoto)
        
        iNum = len(sPhotoList)
        self.m_oTextNum = interface.CTextObject(self, '\xa6@%d\xb1i' % iNum, interface.FontLT12, 6710886)
        self.m_iHeight = self.PSize[1]
        iTextX = self.PSize[0] + 5 + self.m_PosX
        iTextY = self.PSize[1] + 5 + self.m_PosY
        if iNum % 2 == 0:
            iTextX *= 2
        
        if iNum > 2:
            iTextY *= 2
            self.m_iHeight += self.PSize[1]
        
        (_, iTextHeight) = self.m_oTextNum.GetSize()
        self.m_oTextNum.SetPos(iTextX, iTextY - iTextHeight)
        self.m_iHeight += iTextHeight
        self.SetSize(self.m_iWidth, self.m_iHeight)

    
    def ShowOriPhotoDlg(self, idx = 10):
        import myqphotoitem
        iRealIdx = idx - self.BASE
        sPhotoList = self.m_sPhotoUrl.split(',')
        if iRealIdx <= iRealIdx:
            pass
        elif iRealIdx < len(sPhotoList):
            myqphotoitem.ShowOriPhotoDlg(sPhotoList, iRealIdx)
        



class CTalkPhotoSmall(CTalkPhoto):
    PSize = (100, 70)
    
    def Show(self):
        import myqphotoitem
        sPhotoList = self.m_sPhotoUrl.split(',')
        self.m_oPhotoList = []
        self.m_iHeight = 0
        iType = 1
        sPath = sPhotoList[0]
        oPhoto = myqphotoitem.CPhoto(self, sPath, iType, self.PSize[0], self.PSize[1], self.BASE)
        iX = self.m_PosX
        iY = self.m_PosY
        oPhoto.SetPos(iX, iY)
        self.m_oPhotoList.append(oPhoto)
        iNum = len(sPhotoList)
        self.m_oTextNum = interface.CTextObject(self, '\xa6@%d\xb1i' % iNum, interface.FontLT12, 6710886)
        iNum = 1
        self.m_iHeight = self.PSize[1]
        iTextX = self.m_PosX
        iTextY = self.PSize[1] + 5 + self.m_PosY
        if iNum % 2 == 0:
            iTextX *= 2
        
        if iNum > 2:
            iTextY *= 2
            self.m_iHeight += self.PSize[1]
        
        (_, iTextHeight) = self.m_oTextNum.GetSize()
        self.m_oTextNum.SetPos(iTextX, iTextY + iTextHeight / 2)
        self.m_iHeight += iTextHeight + 5
        self.SetSize(self.m_iWidth, self.m_iHeight)



class CTalkBottom(CLineDlgItem, newmyqbase.CTalkBottom):
    
    def __init__(self, parent, w, iType = 0):
        CLineDlgItem.__init__(self, parent, 'dialog4/mengyouquan_new/myq_mid.dlg')
        self.m_Width = w
        self.m_PraisesDlg = None
        self.m_ReplyDlg = None
        self.m_LineDlg = None
        self.m_iType = iType
        self.m_iLastClick = 0

    
    def Show(self):
        self.ShowCommentText()
        self.ShowFromTxt()
        self.ShowPraise()
        self.ShowBtnType()

    
    def SetCommentNum(self, iNum):
        self.m_sCommentNum = iNum

    
    def ShowFromTxt(self):
        iPostTime = self.m_iPostTime
        sTimeText = newmyqbase.TransTime(iPostTime)
        sFromText = '%s' % self.m_sSource
        self.GetObject('text_time').SetText(sTimeText)
        self.GetObject('text_location').SetText(sFromText)
        self.GetObject('text_location').SetShow(bool(self.m_sSource))
        if not self.m_sSource:
            iX = self.GetObject('text_time').GetPos()[0]
            iY = self.GetObject('btn_zan2').GetPos()[1]
            self.GetObject('text_time').SetPos(iX, iY)
        

    
    def ShowCommentText(self):
        self.GetObject('text_huifu').SetText(str(self.m_sCommentNum))

    
    def ShowPraise(self):
        self.GetObject('text_zan').SetText(str(self.m_iPraiseNum))
        self.SelectPraisesBtn(self.m_bMyPraise)

    
    def ShowBtnType(self):
        iOwnerID = self.m_iOwnerID
        iUserID = myqinterface.GetMYQContext().GetRoleID()
        if iOwnerID == iUserID:
            self.GetObject('Btn_del').SetShow(True)
            self.GetObject('Btn_jubao').SetShow(False)
        else:
            self.GetObject('Btn_del').SetShow(False)
            self.GetObject('Btn_jubao').SetShow(True)

    
    def SelectPraisesBtn(self, bMyPraise):
        btn1 = self.GetObject('btn_zan1')
        btn2 = self.GetObject('btn_zan2')
        btn1.SetShow(not bMyPraise)
        btn2.SetShow(bMyPraise)

    
    def ShowReplyDlg(self):
        dData = { }
        dData['iTargetID'] = 0
        dData['iOwnerID'] = self.m_iOwnerID
        dData['sMomentID'] = self.m_sMomentID
        dData['sTargetCommentID'] = ''
        myqsignal.Emit(myqsignal.SS_OpenCommentTalk, dData)

    
    def TalkPraises(self, dPraiseDataList):
        self.m_bMyPraise = False
        self.m_dPraiseData = dPraiseDataList
        self.m_iPraiseNum = len(dPraiseDataList)
        iUserID = myqinterface.GetMYQContext().GetRoleID()
        for dData in self.m_dPraiseData:
            if dData['userid'] == iUserID:
                self.m_bMyPraise = True
                break
                continue
        
        self.ShowPraise()

    
    def OnMessage(self, iMsgID):
        if iMsgID in (2, 5):
            iTime = C_sys.GetTime()
            if iTime - self.m_iLastClick <= iTime - self.m_iLastClick:
                pass
            elif iTime - self.m_iLastClick < 5000:
                usermacro.PROMPT_MSG('\xbe\xde\xa7@\xb9L\xa9\xf3\xc0W\xc1c\xa1A\xbd\xd0\xb5y\xab\xe1\xa6A\xb8\xd5')
                return None
            
            self.m_iLastClick = iTime
            iType = 0 if iMsgID == 2 else 1
            myqsignal.Emit(myqsignal.SS_ClickPraise, iType, self.m_iOwnerID, self.m_sMomentID)
        elif iMsgID == 4:
            import dlgreport
            dlgreport.C2GSNewOpenReport(self.m_iOwnerID, self.m_sUserName, dlgreport.TYPE_HAOYOUXIU, dData = {
                'sMomentID': self.m_sMomentID,
                'sReport': self.m_sReportDescText }, bForce = True)
        elif iMsgID == 3:
            self.ShowReplyDlg()
        elif iMsgID == 1:
            myqsignal.Emit(myqsignal.SS_DeleteNew, self.m_sMomentID)
        



class CTalkBottomSmall(CTalkBottom):
    DEFAULT_HEIGHT = 24
    
    def __init__(self, oParent, w, iType = 0):
        CLineDlgItem.__init__(self, oParent, 'dialog/friend/friend_myq/friend_myq_mid.dlg')
        self.m_Width = w
        self.m_PraisesDlg = None
        self.m_ReplyDlg = None
        self.m_LineDlg = None
        self.m_iType = iType
        self.m_iLastClick = 0
        self.SetIgnoreEsc(True)

    
    def ShowFromTxt(self):
        iPostTime = self.m_iPostTime
        sTimeText = newmyqbase.TransTime(iPostTime)
        sFromText = '%s' % self.m_sSource
        self.GetObject('text_time').SetText(sTimeText)
        self.GetObject('text_location').SetText(sFromText)
        self.GetObject('text_location').SetShow(bool(self.m_sSource))
        if self.m_sSource:
            (_, iHeight) = self.GetObject('text_location').GetSize()
            (iCurWidth, _) = self.GetSize()
            self.GetObject('loc_bg').SetSize(iCurWidth, self.DEFAULT_HEIGHT + iHeight)
        

    
    def ShowBtnType(self):
        pass



class CCommentBase(CLineDlgItem, newmyqbase.CCommentBase):
    
    def __init__(self, oParent, w):
        CLineDlgItem.__init__(self, oParent, 'dialog4/mengyouquan_new/myq_bottom_item.dlg')
        self.m_oHeadShot = None
        self.SetOffsetX()

    
    def SetOffsetX(self):
        pass

    
    def DeleteComment(self):
        iPIDLst = []
        if self.m_iReplyUserID != -1:
            iPIDLst.append(self.m_iReplyUserID)
        
        myqsignal.Emit(myqsignal.SS_DeleteCommentTalk, self.m_iOwnerUserID, self.m_sMomentID, self.m_sCommentID, self.m_sContent, iPIDLst)

    
    def ShowReplyDlg(self):
        dData = { }
        dData['iTargetID'] = self.m_iUserID
        dData['iOwnerID'] = self.m_iOwnerUserID
        dData['sMomentID'] = self.m_sMomentID
        dData['sTargetCommentID'] = None if self.m_sParentCommentID else self.m_sCommentID
        myqsignal.Emit(myqsignal.SS_OpenCommentTalk, dData)

    
    def FormatText(self):
        sText = banword.IsValidChat(self.m_sContent)[1]
        sText = newmyqbase.ReplaceForwardLink(sText)
        sText = newmyqbase.ReplaceEmoteCn2Num(sText)
        iCmtUserID = self.m_iUserID
        sCmtNick = self.m_sUserName
        iBCmtUserID = self.m_iReplyUserID
        sBCmtNick = self.m_sReplyUserName
        sNameTxt = '#c286ad6#c(%d)%s#c()#n' % (iCmtUserID, sCmtNick)
        if self.m_iReplyUserID > 1:
            sBNameTxt = '#c0b5798#c(%d)%s#c()#n' % (iBCmtUserID, sBCmtNick)
            sText = '%s \xa6^\xb4_ %s\xa1G%s' % (sNameTxt, sBNameTxt, sText)
        else:
            sText = '%s\xa1G%s' % (sNameTxt, sText)
        return sText

    
    def FormatTimeText(self):
        iCmtTime = int(self.m_iCommentTime)
        sText = '  #c777777%s#n' % newmyqbase.TransTime(iCmtTime)
        return sText

    
    def DrawLine(self):
        w = self.m_iWidth
        h = self.m_iHeight
        linedata = [
            (1, h, 0, 0),
            (1, h, w - 1, 0)]
        self.m_Lines = []
        for w, h, x, y in linedata:
            line = interface.CBoxObject(self, w, h, 13619151, 256)
            line.SetPos(x, y)
            self.m_Lines.append(line)
        

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.ShowReplyDlg()
        elif msgid == 2:
            self.DeleteComment()
        



class CCommentItem(CCommentBase):
    INDENT_WIDTH = 12
    
    def Show(self):
        sContent = self.FormatText()
        sAtText = ''
        for sName in self.m_sAiteList:
            sAtText += '@%s ' % sName
        
        if sAtText:
            sAtText = ' #c0b5798%s#n' % sAtText
        
        self.GetObject('rtxt_huifuneirong').SetText(sContent + sAtText)
        sTime = self.FormatTimeText()
        self.GetObject('rtxt_time').SetText(sTime)
        self.ShowHeadShot()
        self.ShowDelBtn()
        self.RefreshSize()

    
    def RefreshSize(self):
        oContent = self.GetObject('rtxt_huifuneirong')
        oTime = self.GetObject('rtxt_time')
        oHuifu = self.GetObject('rtxt_huifu')
        oDel = self.GetObject('rtxt_delete')
        (_, iTextY) = oContent.GetPos()
        iTextHeight = oContent.GetTextSize()[1]
        iTimeHeight = oTime.GetTextSize()[1]
        oTime.SetPos(oTime.GetPos()[0], iTextY + iTextHeight + 2)
        oHuifu.SetPos(oHuifu.GetPos()[0], iTextY + iTextHeight)
        oDel.SetPos(oDel.GetPos()[0], iTextY + iTextHeight)
        (iDefaultWidth, iDefaultHeight) = self.GetObject('frame_bg').GetSize()
        iTotHeight = iTextY + iTextHeight + 2 + iTimeHeight
        if iTotHeight > iDefaultHeight:
            self.GetObject('frame_bg').SetSize(iDefaultWidth, iTotHeight)
            self.GetObject('loc_bg').SetSize(iDefaultWidth, iTotHeight)
        

    
    def SetOffsetX(self):
        (iX, iY) = self.GetPos()
        self.GetObject('loc_item').SetPos(iX + self.INDENT_WIDTH, iY)

    
    def ShowDelBtn(self):
        iUserID = myqinterface.GetMYQContext().GetRoleID()
        bShow = self.m_iUserID == iUserID
        self.SetShowObject('rtxt_delete', bShow)
        self.SetShowObject('rtxt_huifu', not bShow)

    
    def ShowHeadShot(self, sPath = ''):
        if not sPath:
            sPath = self.m_sHeadIcon
        
        if not sPath or type(sPath) == int:
            sPath = myqdefine.DEFAULT_TALK_PIC
        
        if not self.m_oHeadShot:
            oLocHead = self.GetObject('loc_touxiang')
            self.m_oHeadShot = CTalkHeadShot(oLocHead, sPath, 3, 50, 50, iScale = 0.6, iPlayerID = self.m_iUserID)
            iUserID = myqinterface.GetMYQContext().GetRoleID()
            bMine = self.m_iUserID == iUserID
            if not bMine:
                self.m_oHeadShot.SetClickCB(misc.Functor(self.OpenFriendDlg))
            
            self.m_oHeadShot.SetMouseMoveCB(misc.Functor(self.MouseWheelDown), misc.Functor(self.MouseWheelUp))
        else:
            self.m_oHeadShot.RefreshHead(sPath)

    
    def OpenFriendDlg(self):
        myqinterface.CacheFriendInfo(self.m_iUserID, self.m_sUserName, self.m_sHeadIcon)
        myqinterface.ShowFriendMenu(self.m_iUserID, self.m_sUserName)

    
    def RefreshTime(self):
        self.Show()



class CCommentReplyItem(CCommentItem):
    INDENT_WIDTH = 60
    
    def __init__(self, oParent, w):
        CLineDlgItem.__init__(self, oParent, 'dialog4/mengyouquan_new/myq_bottom_item2.dlg')
        self.m_oHeadShot = None
        self.SetOffsetX()



class CCommentNextButton(CLineDlgItem, newmyqbase.CCommentNextButton):
    
    def __init__(self, oParent, w):
        CLineDlgItem.__init__(self, oParent, 'dialog4/mengyouquan_new/myq_jiazaihuifu.dlg')
        self.m_Width = w
        self.m_bShowMore = False
        self.m_dMoreDataList = []
        self.GetObject('save_comment').SetShow(False)
        self.GetObject('hloc_zhankaishouqi').SetMouseWheelEnable(True)
        self.GetObject('hloc_zhankaishouqi').SetEnterCB(misc.Functor(self.OnHotEnter))
        self.GetObject('hloc_zhankaishouqi').SetLeaveCB(misc.Functor(self.OnHotLeave))
        self.m_oClickCB = None

    
    def GetShowMore(self):
        return self.m_bShowMore

    
    def SetMoreData(self, dMoreDataList):
        self.m_dMoreDataList = dMoreDataList

    
    def AddMoreData(self, dMoreData):
        if dMoreData not in self.m_dMoreDataList:
            self.m_dMoreDataList.append(dMoreData)
        

    
    def DeleteCmtData(self, sCommentID):
        for dCmtData in self.m_dMoreDataList:
            if dCmtData.get('commentguid') == sCommentID:
                self.m_dMoreDataList.remove(dCmtData)
                break
                continue
        

    
    def GetMoreData(self):
        return self.m_dMoreDataList

    
    def SetClickCB(self, oCB):
        self.m_oClickCB = oCB

    
    def SwitchCommentState(self):
        self.GetObject('save_comment').SetShow(self.m_bShowMore)
        self.GetObject('load_comment').SetShow(not (self.m_bShowMore))

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            if self.m_oClickCB and self.m_dMoreDataList:
                self.m_bShowMore = not (self.m_bShowMore)
                self.m_oClickCB(self, self.m_bShowMore)
            
        

    
    def OnHotEnter(self):
        cursor.Load(cursor.LINK_CURSOR)

    
    def OnHotLeave(self):
        cursor.Load(cursor.NORMAL_CURSOR)



class CSmallCommentBase(CLineDlgItem, newmyqbase.CCommentBase):
    
    def __init__(self, oParent, w):
        CLineDlgItem.__init__(self, oParent, 'dialog/friend/friend_myq/friend_myq_huifu.dlg')
        self.SetIgnoreEsc(True)

    
    def FormatText(self):
        sText = banword.IsValidChat(self.m_sContent)[1]
        sText = newmyqbase.ReplaceForwardLink(sText)
        sText = newmyqbase.ReplaceEmoteCn2Num(sText)
        sText = '#c(10)%s #c()' % sText
        iCmtUserID = self.m_iUserID
        sCmtNick = self.m_sUserName
        iBCmtUserID = self.m_iReplyUserID
        sBCmtNick = self.m_sReplyUserName
        sNameTxt = '#c0b5798#c(%d)%s#c()#n' % (iCmtUserID, sCmtNick)
        if self.m_iReplyUserID > 1:
            sBNameTxt = '#c0b5798#c(%d)%s#c()#n' % (iBCmtUserID, sBCmtNick + '\xa1G')
            sText = '%s \xa6^\xb4_ %s%s' % (sNameTxt, sBNameTxt, sText)
        else:
            sNameTxt = '#c0b5798#c(%d)%s#c()#n' % (iCmtUserID, sCmtNick + '\xa1G')
            sText = '%s%s' % (sNameTxt, sText)
        return sText

    
    def FormatTimeText(self):
        iCmtTime = int(self.m_iCommentTime)
        sText = '  #c777777%s#n' % newmyqbase.TransTime(iCmtTime)
        return sText



class CCommentItemSmall(CSmallCommentBase):
    
    def __init__(self, parent, w):
        CSmallCommentBase.__init__(self, parent, w)
        self.m_oHotBox = None

    
    def Show(self):
        sText = self.FormatText()
        oTextObj = self.GetObject('text_huifu')
        sAtText = ''
        for sName in self.m_sAiteList:
            sAtText += '@%s ' % sName
        
        if sAtText:
            sAtText = ' #c0b5798%s#n' % sAtText
        
        oTextObj.SetText(sText + sAtText)
        (_, iHeight) = oTextObj.GetTextSize()
        iTarHeight = iHeight + 5
        (iDefaultWidth, _) = self.GetObject('frame_bg').GetSize()
        self.GetObject('loc_bg').SetSize(iDefaultWidth, iTarHeight)
        self.GetObject('frame_bg').SetSize(iDefaultWidth, iTarHeight)
        self.m_oHotBox = ui.CHotBox(self, iDefaultWidth, iTarHeight, 999)
        self.m_oHotBox.SetMouseWheelEnable(True)
        self.m_oHotBox.SetEnterCB(misc.Functor(self.OnItemEnterCB))
        self.m_oHotBox.SetLeaveCB(misc.Functor(self.OnItemLeaveCB))

    
    def RefreshTime(self):
        self.Show()

    
    def OnItemEnterCB(self):
        cursor.Load(cursor.LINK_CURSOR)

    
    def OnItemLeaveCB(self):
        cursor.Load(cursor.NORMAL_CURSOR)

    
    def OnHotClick(self):
        (iX, iY) = cursor.GetPos()
        oTextObj = self.GetObject('text_huifu')
        (iTextX, iTextY) = oTextObj.GetScreenPos()
        iClickID = oTextObj.GetTextObj().ClickID(iX - iTextX, iY - iTextY)
        if iClickID == -1:
            return None
        elif iClickID == 10:
            if not self.m_bMine:
                self.ShowReplyDlg()
            else:
                usermacro.PROMPT_MSG('\xa5u\xaf\xe0\xa6^\xb4_\xa8\xe4\xa5L\xa4H\xaa\xba\xb5\xfb\xbd\xd7#3')
        elif iClickID != myqinterface.GetMYQRoleID():
            self.OpenFriendDlg()
        else:
            usermacro.PROMPT_MSG('\xacO\xa7A\xa6\xdb\xa4v\xa7r#20')

    
    def OpenFriendDlg(self):
        if self.m_iUserID == myqinterface.GetMYQRoleID():
            iUserID = self.m_iReplyUserID
            sName = self.m_sReplyUserName
            sHead = self.m_sReplyHeadIcon
        else:
            iUserID = self.m_iUserID
            sName = self.m_sUserName
            sHead = self.m_sHeadIcon
        myqinterface.CacheFriendInfo(iUserID, sName, sHead)
        myqinterface.ShowFriendMenu(iUserID, sName)

    
    def ShowReplyDlg(self):
        dData = { }
        dData['iTargetID'] = self.m_iUserID
        dData['iOwnerID'] = self.m_iOwnerUserID
        dData['sMomentID'] = self.m_sMomentID
        dData['sTargetCommentID'] = None if self.m_sParentCommentID else self.m_sCommentID
        myqsignal.Emit(myqsignal.SS_OpenCommentTalk, dData)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 999:
            self.OnHotClick()
        



class CCommentNextButtonSmall(CCommentNextButton, newmyqbase.CCommentNextButton):
    
    def __init__(self, oParent, w):
        CLineDlgItem.__init__(self, oParent, 'dialog/friend/friend_myq/friend_myq_zhankai.dlg')
        self.SetIgnoreEsc(True)
        self.m_Width = w
        self.m_bShowMore = False
        self.m_dMoreDataList = []
        self.GetObject('save_comment').SetShow(False)
        self.GetObject('hloc_zhankaishouqi').SetMouseWheelEnable(True)
        self.GetObject('hloc_zhankaishouqi').SetEnterCB(misc.Functor(self.OnHotEnter))
        self.GetObject('hloc_zhankaishouqi').SetLeaveCB(misc.Functor(self.OnHotLeave))
        self.m_oClickCB = None



class CTalkPraiseItem(CLineDlgItem, newmyqbase.CTalkPraise):
    OFFSET_X = 8
    OFFSET_Y = 5
    MAX_LINE_SHOW = 7
    ITEM_WIDTH = 27
    DEFAULT_HEIGHT = 45
    DEFAULT_Y = -44
    
    def __init__(self, parent, w, itype = 0):
        CLineDlgItem.__init__(self, parent, 'dialog4/mengyouquan_new/myq_dianzan.dlg')
        self.m_iWidth = w
        self.m_iHeigth = 0
        self.m_iPraiseNum = 0
        self.m_iType = itype
        self.m_oHeadList = []
        self.m_oMoreHeadList = []
        self.m_bShowMore = False
        self.m_dUserID2Head = { }

    
    def Show(self):
        self.RefreshPraiseData()

    
    def SetPraiseData(self, sMomentID, dDataList):
        self.m_sMomentID = sMomentID
        self.m_dPraiseData = dDataList
        self.RefreshPraiseData()

    
    def RefreshPraiseData(self):
        import myqinterface
        self.m_oHeadList = []
        (iStartX, iStartY) = self.GetObject('loc_praise').GetPos()
        for idx, dData in enumerate(self.m_dPraiseData):
            sUserPic = dData.get('userpic')
            if type(sUserPic) == str:
                sPath = misc.ReadJson(sUserPic)
            else:
                sPath = sUserPic
            if not sPath:
                sPath = myqdefine.DEFAULT_TALK_PIC
            
            iUserID = dData.get('userid')
            sPath = [
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None].GetUserRealTouXiang(iUserID, sPath)
            oHead = CTalkHeadShot(self, sPath, 3, 45, 45, iScale = 0.6, iPlayerID = iUserID)
            if idx + 1 > self.MAX_LINE_SHOW:
                self.m_oMoreHeadList.append(oHead)
            else:
                self.m_oHeadList.append(oHead)
            iX = iStartX + (self.ITEM_WIDTH + self.OFFSET_X) * (idx % self.MAX_LINE_SHOW)
            iY = iStartY + (idx / self.MAX_LINE_SHOW) * (self.ITEM_WIDTH + self.OFFSET_Y)
            oHead.SetPos(iX, iY)
            iMyUserID = myqinterface.GetMYQContext().GetRoleID()
            sNickName = misc.AsciiStr2BinaryStr(dData.get('nickname'))
            sName = self.GetUserRealName(iUserID, sNickName)
            bMine = iMyUserID == iUserID
            if not bMine:
                oHead.SetClickCB(misc.Functor(self.OpenFriendDlg, iUserID, sName, sPath))
            
            oHead.SetEnterShowName(sName)
            oHead.SetMouseMoveCB(misc.Functor(self.MouseWheelDown), misc.Functor(self.MouseWheelUp))
            oHead.SetZ(10)
            self.BindPhotoRefresh(oHead, iUserID)
        
        self.RefreshShowMore()

    
    def BindPhotoRefresh(self, oHead, iUserID):
        import logicrefreshuserinfo
        oLogic = logicrefreshuserinfo.GetRefreshUserInfoLogic()
        oLogic.AddUser2PhotoEvent(iUserID, oHead.RefreshHead)

    
    def OpenFriendDlg(self, iUserID, sUserName, sHeadIcon):
        myqinterface.CacheFriendInfo(iUserID, sUserName, sHeadIcon)
        myqinterface.ShowFriendMenu(iUserID, sUserName)

    
    def RefreshShowMore(self):
        for oHead in self.m_oMoreHeadList:
            oHead.SetShow(self.m_bShowMore)
        
        iW = self.GetObject('frame_bg').GetSize()[0]
        iH = self.DEFAULT_HEIGHT
        if self.m_bShowMore:
            iLen = len(self.m_oMoreHeadList)
            iHNum = math.ceil(float(iLen) / self.MAX_LINE_SHOW)
            if iHNum == 0 and iLen > 0:
                iHNum = 1
            
            iH += iHNum * (self.ITEM_WIDTH + self.OFFSET_Y)
        
        self.m_iHeigth = iH
        bBtnShow = len(self.m_oMoreHeadList) > 0
        if bBtnShow:
            pass
        self.GetObject('btn_huifu').SetShow(not (self.m_bShowMore))
        if bBtnShow:
            pass
        self.GetObject('btn_huifu2').SetShow(self.m_bShowMore)
        self.GetObject('frame_bg').SetSize(iW, self.m_iHeigth)
        self.GetObject('loc_bg').SetSize(iW, self.m_iHeigth)
        oImg = self.GetObject('img_fjx1')
        oImg.SetPos(oImg.GetPos()[0], iH)
        myqsignal.Emit(myqsignal.SS_RefreshTaskList)

    
    def OnMessage(self, msgid):
        if msgid in (1, 2):
            self.m_bShowMore = not (self.m_bShowMore)
            self.RefreshShowMore()
        



class CTalkPraiseItemSmall(CTalkPraiseItem):
    DEFAULT_LINE_X = -7
    DEFAULT_LINE_Y = -17
    
    def __init__(self, parent, w, itype = 0):
        CLineDlgItem.__init__(self, parent, 'dialog/friend/friend_myq/friend_myq_bottom.dlg')
        self.m_iWidth = w
        self.m_iPraiseNum = 0
        self.m_iType = itype
        self.m_oHeadList = []
        self.m_oMoreHeadList = []
        self.m_bShowMore = False
        self.m_bBindSignal = False
        self.m_tPraiseUserInfo = { }
        self.SetIgnoreEsc(True)

    
    def RefreshPraiseData(self, *args):
        sPlayerNameText = ''
        iCount = 0
        iMoreCount = 0
        for idx, dData in enumerate(self.m_dPraiseData):
            if iCount > 3:
                iMoreCount += 1
                continue
            sUserPic = dData.get('userpic')
            if type(sUserPic) == str:
                sPath = misc.ReadJson(sUserPic)
            else:
                sPath = sUserPic
            if not sPath:
                sPath = myqdefine.DEFAULT_TALK_PIC
            
            iUserID = dData.get('userid')
            sPath = self.GetUserRealTouXiang(iUserID, sPath)
            sNickName = misc.AsciiStr2BinaryStr(dData.get('nickname'))
            sName = self.GetUserRealName(iUserID, sNickName)
            sPlayerNameText += '#c(%d)%s#c()\xa1A' % (iUserID, sName)
            self.m_tPraiseUserInfo[iUserID] = (sName, sPath)
            iCount += 1
            iMoreCount += 1
        
        if iMoreCount - iCount > 0:
            sPlayerNameText += '\xb5\xa5\xa6@%d\xa4H\xc4\xb1\xb1o\xab\xdc\xc3\xd9' % iMoreCount
        
        self.GetObject('text_name').SetText(sPlayerNameText)
        self.BindNameRefresh()
        self.RefreshShowMore()

    
    def RefreshShowMore(self):
        (_, iHeight) = self.GetObject('text_name').GetTextSize()
        iHeight = max(17, iHeight)
        iHeight += 2
        oImg = self.GetObject('img_fjx1')
        oImg.SetPos(oImg.GetPos()[0], iHeight)
        iHeight += 1
        (iDefaultWidth, _) = self.GetObject('frame_bg').GetSize()
        self.GetObject('frame_bg').SetSize(iDefaultWidth, iHeight)
        self.GetObject('loc_bg').SetSize(iDefaultWidth, iHeight)
        self.m_oHotBox = ui.CHotBox(self, iDefaultWidth, iHeight, 999)
        self.m_oHotBox.SetMouseWheelEnable(True)
        myqsignal.Emit(myqsignal.SS_RefreshTaskList)

    
    def OnHotClick(self):
        (iX, iY) = cursor.GetPos()
        oTextObj = self.GetObject('text_name')
        (iTextX, iTextY) = oTextObj.GetScreenPos()
        iClickID = oTextObj.GetTextObj().ClickID(iX - iTextX, iY - iTextY)
        if iClickID == -1:
            return None
        elif iClickID != myqinterface.GetMYQRoleID():
            self.OpenFriendDlgByID(iClickID)
        else:
            usermacro.PROMPT_MSG('\xacO\xa7A\xa6\xdb\xa4v\xa7r#20')

    
    def OpenFriendDlgByID(self, iUserID):
        if iUserID not in self.m_tPraiseUserInfo:
            return None
        
        (sName, sPath) = self.m_tPraiseUserInfo[iUserID]
        myqinterface.CacheFriendInfo(iUserID, sName, sPath)
        myqinterface.ShowFriendMenu(iUserID, sName)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 999:
            self.OnHotClick()
        

    
    def BindNameRefresh(self):
        import logicrefreshuserinfo
        if self.m_bBindSignal:
            return None
        
        self.m_bBindSignal = True
        oLogic = logicrefreshuserinfo.GetRefreshUserInfoLogic()
        iCount = 0
        iMoreCount = 0
        for _, dData in enumerate(self.m_dPraiseData):
            if iCount > 3:
                iMoreCount += 1
                continue
            iUserID = dData.get('userid')
            iCount += 1
            oLogic.AddUser2PhotoEvent(iUserID, self.RefreshPraiseData)
        



class COtherTopItem(CLineDlgItem):
    
    def __init__(self, parent, iW):
        CLineDlgItem.__init__(self, parent, 'dialog4/mengyouquan_new/myq_weituoinfo.dlg')
        self.m_Width = iW
        self.m_oTextObj = None

    
    def GetNewID(self):
        return ''

    
    def RefreshData(self, dInfo):
        sInfo = dInfo['sText']
        oText = self.GetObject('text_name')
        (iX, iY) = oText.GetPos()
        self.SetShowObject('text_name', False)
        sInfo = interface.CRichTextObject.ChangeText(sInfo, sType = 'iLowColor')
        self.m_oTextObj = wrapinterface.CLinkRichTextObject(self, oText.GetSize()[0], oText.GetFont(), sInfo, oText.GetColor())
        self.m_oTextObj.SetPos(iX, iY)



class COtherTopItemSmall(COtherTopItem):
    
    def __init__(self, parent, iW):
        CLineDlgItem.__init__(self, parent, 'dialog/friend/friend_myq/friend_myq_weituoinfo.dlg')
        self.m_Width = iW
        self.m_oTextObj = None



class CTextEdit(interface.CMultilineEdit):
    
    def AddChar(self, char, dExtInfo = None):
        self.DeleteSelected()
        if hasattr(self, 'm_Forbiden') and self.m_Forbiden and not (self.m_IsSet):
            usermacro.PROMPT_MSG('\xa4w\xb9F\xa8\xec\xbf\xe9\xa4J\xa4W\xad\xad')
            return None
        
        interface.CMultilineEdit.AddChar(self, char)
        self.m_EditTip = None
        self.RefreshParent()

    
    def SetText(self, txt, dExtInfo = None):
        self.m_IsSet = True
        interface.CMultilineEdit.SetText(self, txt)
        self.m_IsSet = False

    
    def _Filter(self, txt):
        return txt

    
    def RefreshParent(self):
        parent = self.GetParent()
        if hasattr(parent, 'RefreshFontNum'):
            parent.RefreshFontNum()
        

    
    def MsgDelete(self):
        interface.CMultilineEdit.MsgDelete(self)
        self.RefreshParent()

    
    def MsgBack(self):
        interface.CMultilineEdit.MsgBack(self)
        self.RefreshParent()

    
    def Forbiden(self, flag):
        self.m_Forbiden = flag

    
    def DeleteSelected(self):
        if self.m_SelectedBegin < self.m_Cursor:
            del self.m_Data[self.m_SelectedBegin - 1:self.m_Cursor - 1]
            self.m_Cursor = self.m_SelectedBegin
        elif self.m_SelectedBegin > self.m_Cursor:
            del self.m_Data[self.m_Cursor - 1:self.m_SelectedBegin - 1]
            self.m_SelectedBegin = self.m_Cursor
        else:
            return None
        self.RefreshPos(self.m_Cursor)
        self.SetCursor(self.m_Cursor, True)
        self.Forbiden(False)

    
    def SetTxtTip(self, txt, color = 8947848):
        self.m_TipTxt = txt
        self.m_TipColor = color
        self.ShowTxtTip()

    
    def GetTxtTip(self):
        return self.m_TipTxt

    
    def ShowTxtTip(self):
        self.m_EditTip = None
        if hasattr(self, 'm_TipTxt') and self.m_TipTxt != '':
            self.m_EditTip = interface.CRichTextObject(self, self.m_Width, interface.FontLT14_3, self.m_TipTxt, self.m_TipColor)
