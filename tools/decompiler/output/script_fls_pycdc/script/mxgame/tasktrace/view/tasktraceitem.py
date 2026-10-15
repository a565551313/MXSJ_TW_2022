# pycdc 交叉复核产物 · script.fls entry 1569
# co_filename(原始)='script/mxgame/tasktrace/view/tasktraceitem.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1569.pyc (Python 2.5)

import C_sys
import combdialog
import cursor
import dlgguidetips
import handobj
import interface
import mainmenudefines
import makeitemicon
import permission
import style
import tasktypedata
import timer
import ui
import wrapinterface
import tasktraceutil
import misc
import wrapui

class CTaskFollowTaskItem(combdialog.CCombSubWnd):
    
    def __init__(self, oParent, iFontID, iTaskID, oSwitchTaskCB, oDeleteCB, oBeforeClickCB, oAfterClickCB):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/track/taskitem.dlg')
        self.SetIgnoreEsc(True)
        self.m_iFontID = iFontID
        self.m_iTaskID = iTaskID
        self.m_oRichText = None
        self.m_bSelfEnter = False
        self.m_bHotboxEnter = False
        self.m_sText = None
        self.m_oBGBox = None
        self.m_oShadowBox = None
        self.m_CheckFrameTipsTimer = None
        self.m_oDeleteCB = oDeleteCB
        self.m_oBeforeClickCB = oBeforeClickCB
        self.m_oAfterClickCB = oAfterClickCB
        self.m_oSwitchTaskCB = oSwitchTaskCB
        self.m_oAutoFindEff = None
        self.m_oAutoFindCB = None
        self.m_iCurLinkID = -1
        self.m_HoldHandCmd = None
        self.m_oFollowBox = None
        self.m_oGuideTips = None
        self.m_oTaskRewardItem = None
        oHotbox = self.GetObject('hloc_close')
        oHotbox.SetEnterCB(misc.Functor(self.OnHotBoxEnter))
        oHotbox.SetLeaveCB(misc.Functor(self.OnHotBoxLeave))
        oHotbox.SetTipsFont(interface.FontLT12_1)
        self.CheckDeleteShow()

    
    def GetTaskID(self):
        return self.m_iTaskID

    
    def GetFontID(self):
        return self.m_iFontID

    
    def GetShowText(self):
        return self.m_sText

    
    def SetText(self, sText):
        if self.m_sText != sText:
            self.m_sText = sText
            self.RefreshText()
        

    
    def SetFont(self, iFontID):
        self.m_iFontID = iFontID
        self.RefreshText()

    
    def SetPreviewReward(self, iShape, iAmount):
        oTaskRewardItem = CTaskRewardItem(self.GetFollowBox(), iShape, iAmount)
        (_, iRewardH) = oTaskRewardItem.GetSize()
        (_, iFollowH) = self.GetFollowBox().GetSize()
        oTaskRewardItem.SetPos(0, (iFollowH - iRewardH) / 2)
        self.m_oTaskRewardItem = oTaskRewardItem

    
    def SetGuideTips(self, dGuideInfo, oGuideInfoClickCB = None):
        if dGuideInfo is not None:
            if not self.m_oGuideTips:
                sDesc = dGuideInfo.get('sDesc', '\xc2I\xc0\xbb#Y\xa4U\xa6E\xbdu\xa4\xe5\xa6r#n\xa5i\xa5H\xa6\xdb\xb0\xca\xb4M\xb8\xf4')
                sPos = dGuideInfo.get('tPos', '0, 0')
                tPos = sPos.split(',')
                sSize = dGuideInfo.get('tSize', '0, 0')
                tSize = sSize.split(',')
                iDir = dGuideInfo.get('iDir', 3)
                (iX, iY, _, _) = self.GetLocData('loc_content')
                self.m_oGuideTips = dlgguidetips.CGuideTips(self.GetFollowBox(), sDesc, iDir, int(tPos[0]) + iX, int(tPos[1]) + iY, int(tSize[0]), int(tSize[1]))
                if oGuideInfoClickCB and not isinstance(oGuideInfoClickCB, misc.Functor):
                    oGuideInfoClickCB = misc.Functor(oGuideInfoClickCB)
                
                self.m_oGuideTips.SetClickCB(oGuideInfoClickCB)
                self.m_oGuideTips.SetMovieHide()
            
        elif self.m_oGuideTips:
            self.m_oGuideTips = None
        

    
    def ShowAutoFindEff(self, iType, bHasScrollBar):
        self.m_oAutoFindEff = CTaskTraceAutoFindEff(self, iType, bHasScrollBar)

    
    def HideAutoFindEff(self):
        self.m_oAutoFindEff = None

    
    def SetAutoFindCB(self, oCB):
        self.m_oAutoFindCB = oCB

    
    def GetFollowBox(self):
        import mainmenu
        if not self.m_oFollowBox:
            oParent = self.GetParent()
            while oParent and not isinstance(oParent, mainmenu.CMainMenu):
                oParent = oParent.GetParent()
            oFollow = wrapinterface.CFollowObject(oParent, self, wrapinterface.CFollowObject.MODE_HEIGHT_1)
            oFollow.SetZ(mainmenudefines.Z_HIGHEST_VALUE)
            self.m_oFollowBox = oFollow
        
        return self.m_oFollowBox

    
    def ResetBoxBGBox(self):
        (iW, iH) = self.GetSize()
        if not (self.m_oBGBox) or self.m_oBGBox.GetSize() != (iW, iH):
            self.m_oBGBox = interface.CBoxObject(self, iW, iH, 0, 0)
        

    
    def GetSize(self):
        (iW, _) = self.GetObject('loc_bg').GetSize()
        iHeight = self.m_oRichText.GetHeight()
        return (iW, iHeight + 12)

    
    def CheckDeleteShow(self):
        if self.m_bSelfEnter or self.m_bHotboxEnter:
            self.SetShowObject('img_close', True)
            if not self.m_oShadowBox:
                (iW, iH) = self.GetSize()
                self.m_oShadowBox = interface.CBoxObject(self, iW, iH, 0, 130)
                self.m_oShadowBox.SetZ(-10)
            
        else:
            self.SetShowObject('img_close', False)
            if self.m_oShadowBox:
                self.m_oShadowBox = None
            

    
    def ShowTakeCursor(self, linkobj):
        import taskidchangetxtcolor
        import cursor
        import wrapui
        cursor.SetLinkCursor(True)
        if isinstance(linkobj, (wrapui.CLinkNpcPos, wrapui.CLinkNpc, wrapui.CLinkPosition)) and self.m_iTaskID in taskidchangetxtcolor.TASKIDLST:
            cursor.Load(cursor.TAKE_CURSOR)
            cursor.SetCursorTips(None)
        

    
    def EndLinkTipsTimer(self):
        if self.m_CheckFrameTipsTimer:
            self.m_CheckFrameTipsTimer.Release()
            self.m_CheckFrameTipsTimer = None
        
        self.m_ShowTips = None

    
    def StartLinkTipsTimer(self):
        self.EndLinkTipsTimer()
        
        def ShowLeftupTips(obj, linkObj, x, y):
            if hasattr(obj, 'm_OldLinkObj') and linkObj == obj.m_OldLinkObj:
                x = obj.m_OldX
                y = obj.m_OldY
            
            obj.m_OldLinkObj = linkObj

        
        def ShowLinkTips(obj):
            richText = obj.m_oRichText
            (x, y) = cursor.GetPos()
            (iClickID, oLink) = richText.GetLinkByCursor()
            if oLink:
                ShowLeftupTips(obj, oLink, x, y)
                if obj.m_iCurLinkID == iClickID:
                    return ()
                
                obj.m_iCurLinkID = iClickID
                obj.ShowTakeCursor(oLink)
                if isinstance(oLink, wrapui.CLinkNpcPos):
                    obj.m_TaskLinkTips = wrapinterface.CTextTips(None, -1, oLink.GetTipsText(), interface.FontLT12_1, direct = 0)
                    obj.m_TaskLinkTips.SetPos(x, y + 40)
                elif isinstance(oLink, wrapui.CLinkMarkImg):
                    oLink.OnEnter()
                    obj.m_LastEnter = oLink
                
            elif not permission.IsTestTaskFrameClick():
                if not cursor.IsNormalCursor():
                    cursor.Load(cursor.NORMAL_CURSOR)
                
            
            obj.m_TaskLinkTips = None
            obj.m_iCurLinkID = -1
            if hasattr(obj, 'm_LastEnter') and obj.m_LastEnter:
                obj.m_LastEnter.OnLeave()
            
            obj.m_ShowTips = None
            obj.m_OldLinkObj = None
            return ()

        self.m_CheckFrameTipsTimer = self.CreatePyCommand(1, ShowLinkTips)

    
    def OnCopyTaskInfo(self):
        import key
        import copylinkobj
        import kuafulink
        import nettask
        tTaskInfo = nettask.GetTaskInfo(self.m_iTaskID)
        if C_sys.IsKeyDown(key.VK_SHIFT) and len(tTaskInfo) > 1:
            copylinkobj.CreateCopyLink(kuafulink.CLinkTask.CLIENT_TYPE, tTaskInfo[1], self.m_iTaskID)
            return True
        
        return False

    
    def LeftUp(self):
        import usermacro
        import kuafutaskdata
        import dlgmap
        self.ReleaseHoldHand()
        if self.OnCopyTaskInfo():
            return None
        
        if not (dlgmap.g_AutoGoto) and misc.IsInKuafuServer() and self.m_iTaskID not in kuafutaskdata.GetData():
            sMsg = '\xa6\xb9\xb3\xf5\xb4\xba\xa4\xa3\xa4\xe4\xab\xf9\xa6\xdb\xb0\xca\xb4M\xb8\xf4'
            usermacro.PROMPT_MSG(sMsg)
            return None
        
        self.m_ShowTips = None
        (iClickID, oLink) = self.m_oRichText.GetLinkByCursor()
        bTestTaskFrameClick = permission.IsTestTaskFrameClick()
        if bTestTaskFrameClick and not oLink:
            oLink = self.m_oRichText.GetFirstLinkObj()
        
        if oLink:
            if self.m_oBeforeClickCB:
                self.m_oBeforeClickCB(self.m_iTaskID, iClickID, oLink)
            
            oLink.OnLeftUp()
            if self.m_oAfterClickCB:
                self.m_oAfterClickCB(self.m_iTaskID, iClickID, oLink)
            
        elif not bTestTaskFrameClick:
            tasktraceutil.CheckAllObjectClick()
        

    
    def LeftDown(self):
        if self.m_oSwitchTaskCB:
            self.DelayHoldHand()
        

    
    def Enter(self):
        self.m_bSelfEnter = True
        self.CheckDeleteShow()
        if self.m_oRichText:
            self.StartLinkTipsTimer()
            if permission.IsTestTaskFrameClick() and self.m_oRichText.GetFirstLinkObj():
                cursor.Load(cursor.LINK_CURSOR)
            
        

    
    def Leave(self):
        self.m_bSelfEnter = False
        self.m_iCurLinkID = -1
        self.CheckDeleteShow()
        self.EndLinkTipsTimer()
        if permission.IsTestTaskFrameClick() and self.m_oRichText and self.m_oRichText.GetFirstLinkObj():
            cursor.Load(cursor.NORMAL_CURSOR)
        

    
    def OnHotBoxEnter(self):
        self.m_bHotboxEnter = True
        self.CheckDeleteShow()

    
    def OnHotBoxLeave(self):
        self.m_bHotboxEnter = False
        self.CheckDeleteShow()

    
    def OnAutoFindPathCB(self, dValue):
        if self.m_oAutoFindCB:
            self.m_oAutoFindCB(dValue)
        

    
    def OnDelete(self):
        if self.m_oDeleteCB:
            self.m_oDeleteCB(self.m_iTaskID)
        

    
    def RefreshText(self):
        if self.m_sText is None:
            return None
        
        (iX, iY, iW, _) = self.GetLocData('loc_content')
        (iCX, iCY) = self.GetObject('loc_titlepoint').GetPos()
        self.m_oRichText = CTaskFollowText(self, iW, self.m_iFontID, self.m_sText, (iCX - iX, iCY - iY), self.m_iTaskID, 16777215)
        self.m_oRichText.SetPos(iX, iY)
        self.ResetBoxBGBox()
        if self.m_oAutoFindEff:
            self.m_oAutoFindEff.SetEffect()
        

    
    def DelayHoldHand(self):
        self.ReleaseHoldHand()
        
        def Hand(oItem, iTick):
            '''
\t\t\t:param CTaskFollowTaskItem oItem:
\t\t\t:param int iTick:
\t\t\t'''
            import handobj
            import cursor
            if not getattr(oItem, 'm_DelayHand', None) or handobj.IsHand():
                return None
            
            import key
            if not C_sys.IsKeyDown(key.LEFT_BUTTON_DOWN):
                return None
            
            if iTick < 4:
                return (iTick + 1,)
            
            iCurPos = cursor.GetCursorPos()
            if oItem.m_OrgPos == iCurPos:
                return (iTick,)
            
            oHand = CTaskSwapBox.CreateFromItem(cursor.Cursor, oItem)
            iOX = oItem.m_OppoPos[0] - oItem.m_OrgPos[0]
            iOY = oItem.m_OppoPos[1] - oItem.m_OrgPos[1]
            oHand.SetPos(iOX, iOY)
            oHand.SetAlpha(64)
            handobj.HandHoldTaskSwap(oHand, oItem.m_iTaskID, oItem.GetHoldDlgParent(), misc.Functor(oItem.SwapEndCallback))
            oItem.SetShow(False)

        self.m_HoldHandCmd = self.CreatePyCommand(1, Hand, 1)
        self.m_DelayHand = True
        import cursor
        self.m_OrgPos = cursor.GetCursorPos()
        self.m_OppoPos = self.GetOppositePos()

    
    def SwapEndCallback(self, oHoldParent):
        self.SetShow(True)

    
    def GetOppositePos(self):
        oParent = self.GetParent()
        (iX, iY) = self.GetPos()
        while oParent and oParent.GetParent() != interface.MainPanel:
            (iPX, iPY) = oParent.GetPos()
            iX += iPX
            iY += iPY
            oParent = oParent.GetParent()
        return (iX, iY)

    
    def OnHoldHand(self, hand, isTrue = True):
        if hand.m_Type == handobj.TYPE_HOLDTASKSWAP and hand.m_ParentDlg == self.GetHoldDlgParent():
            if hand.m_iTaskID != self.m_iTaskID:
                if self.m_oSwitchTaskCB:
                    self.m_oSwitchTaskCB(hand.m_iTaskID, self.m_iTaskID)
                
            
        

    
    def GetHoldDlgParent(self):
        return self.GetParent().GetParent()

    
    def OnHand(self, hand):
        oPar = self.GetParent()
        if hasattr(oPar, 'OnHand'):
            oPar.OnHand(hand)
        

    
    def ReleaseTimer(self):
        self.m_DelayHand = False
        if self.m_HoldHandCmd:
            self.m_HoldHandCmd.Release()
            self.m_HoldHandCmd = None
            return True
        
        return False

    
    def ReleaseHoldHand(self):
        if self.ReleaseTimer():
            handobj.Clear()
        

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.OnDelete()
        



class CTaskFollowText(wrapinterface.WrapRichText):
    COLORMAP = {
        interface.STYLE3_KEY: {
            '#G': '#c2be935',
            '#c12A42E': '#c2be935',
            '#R': '#cfe3332',
            '#W': '#cd2f2fd',
            '#n': '#n#cd2f2fd',
            '#c00FFFF': '#c00daff',
            '#c309ED9': '#c00daff',
            '#c0A83F5': '#c00daff',
            '#Y': '#cede200',
            '#c12a42e': '#c2be935',
            '#c00ffff': '#c00daff',
            '#c309ed9': '#c00daff',
            '#c0a83f5': '#c00daff' },
        interface.STYLE4_KEY: {
            '#G': '#c2ae834',
            '#c109126': '#c2ae834',
            '#R': '#cdb2845',
            '#W': '#cd2f2fd',
            '#n': '#n#cd2f2fd',
            '#c00FFFF': '#c00d9fe',
            '#c309ED9': '#c00d9fe',
            '#c286AD6': '#c00d9fe',
            '#c0A83F5': '#c00d9fe',
            '#Y': '#cede200',
            '#c00ffff': '#c00d9fe',
            '#c309ed9': '#c00d9fe',
            '#c286ad6': '#c00d9fe' } }
    
    def __init__(self, oParent, iW, iFontid, sTxt, tCirclePos, iTaskID = 0, iNormalcolor = None):
        self.m_RealTxt = sTxt
        import wrapui
        (sResult, _, self.m_LinkObj) = wrapui.ReplaceLink(sTxt)
        if iNormalcolor is None:
            iNormalcolor = wrapui.GetLinkColor(self.m_LinkObj)
        
        sOrgResult = sResult
        sResult = self.SwapColor(sResult)
        wrapinterface.WrapRichText.__init__(self, oParent, iW, iFontid, sResult, iNormalcolor)
        (_, _, self.m_LinkObj) = wrapui.ReplaceLink(sTxt, self)
        self.SetLinkMaxClientNum(iTaskID)
        self.ReplaceBlock()
        (iOffx, iOffy) = style.GetIntTuple('dlgtaskfollow.CMyText', 'data_rich')
        self.SetPos(iOffx, iOffy)
        self.SetCircleImg(sOrgResult, tCirclePos)
        for oLinkObj in self.m_LinkObj.itervalues():
            if isinstance(oLinkObj, wrapui.CLinkNpc) or isinstance(oLinkObj, wrapui.CLinkPosition):
                oLinkObj.SetAutoFindPathCallBack(oParent, 'OnAutoFindPathCB', {
                    'iTaskID': iTaskID })
                continue
        

    
    def SetCircleImg(self, sResult, tCirclePos):
        import ui
        if sResult.startswith('#cff68ed') or sResult.startswith('#cFC33FC'):
            sPath = 'combdialog4/\xd4\xd3\xcd\xbc/\xc8\xce\xce\xf1\xd7\xb7\xd7\xd9\xd4\xb2\xb5\xe3/\xd4\xb2\xb5\xe3_\xd7\xcf.png'
        elif sResult.startswith('#G') and sResult.startswith('#c00FFFF') or sResult.startswith('#c00ffff'):
            sPath = 'combdialog4/\xd4\xd3\xcd\xbc/\xc8\xce\xce\xf1\xd7\xb7\xd7\xd9\xd4\xb2\xb5\xe3/\xd4\xb2\xb5\xe3_\xc2\xcc.png'
        else:
            sPath = 'combdialog4/\xd4\xd3\xcd\xbc/\xc8\xce\xce\xf1\xd7\xb7\xd7\xd9\xd4\xb2\xb5\xe3/\xd4\xb2\xb5\xe3_\xbb\xd2.png'
        self.m_oCircleImg = ui.CImage(self, style.GetPath(sPath), interface.UIPath)
        (iOffsetx, iOffsety) = tCirclePos
        self.m_oCircleImg.SetPos(iOffsetx, iOffsety)

    
    def SwapColor(self, sRichText):
        iStyle = interface.GetStyle()
        if iStyle in self.COLORMAP:
            for sOriColor, sChangeColor in self.COLORMAP[iStyle].iteritems():
                sRichText = sRichText.replace(sOriColor, sChangeColor)
            
        
        return sRichText

    
    def SetLinkMaxClientNum(self, iTaskID):
        import nettask
        iAutoWalkLimit = tasktypedata.GetAutoWalkLimit(iTaskID)
        if iTaskID:
            if iAutoWalkLimit:
                iMaxClientNum = iAutoWalkLimit
            elif tasktypedata.AutoWalkEnable(nettask.GetTaskType(iTaskID)):
                iMaxClientNum = 1
            else:
                iMaxClientNum = wrapui.g_MaxClientNum
        else:
            iMaxClientNum = wrapui.g_MaxClientNum
        sTitle = nettask.GetTaskNameInNpcDlg(iTaskID)
        for oLink in self.m_LinkObj.itervalues():
            oLink.m_MaxClientNum = iMaxClientNum
            if hasattr(oLink, 'SetTaskName'):
                oLink.SetTaskName(sTitle)
                continue
        

    
    def GetLinkByCursor(self):
        (iX, iY) = cursor.GetPos()
        (iSX, iSY) = self.GetScreenPos()
        iClickID = int(self.ClickID(iX - iSX, iY - iSY))
        return (iClickID, self.m_LinkObj.get(iClickID, None))

    
    def GetFirstLinkObj(self):
        for oLinkObj in self.m_LinkObj.itervalues():
            return oLinkObj
        



class CTaskRewardItem(interface.CBoxObject):
    '''\xa5\xf4\xb0\xc8\xb0l\xc2\xdc\xbc\xfa\xc0y\xb9w\xc4\xfd'''
    
    def __init__(self, oParent, iShape, iNum):
        interface.CBoxObject.__init__(self, oParent, 44, 44, 16711680, 0)
        (self.m_dFrames, _) = combdialog.LoadDialog(self, 'dialog/mainmenu/com_taskreward.dlg', False)
        \x96\xbb\x96x = self.m_dFrames['box_reward']
        (iW, iH) = \x96\xbb\x96x.GetSize()
        self.SetSize(iW, iH)
        oImg = makeitemicon.CNeedItemIcon(\x96\xbb\x96x, iShape, 100)
        interface.Center(oImg, -4)
        oImg.DelNeedTxt()
        oImg.SetFreeze(False)
        oImg.GetObject('img_dft_000').SetShow(False)
        interface.CenterLeft(\x96\xbb\x96x)
        (iW, iH) = \x96\xbb\x96x.GetSize()
        (x, y) = \x96\xbb\x96x.GetPos()
        \x96\xbb\x96x.SetPos(x - iW, y)
        self.m_oRewardItemImage = oImg
        oText = self.m_dFrames['text_num']
        if iNum > 1:
            oText.SetText('%s' % iNum)
        else:
            oText.SetText('')
        (x, y) = oText.GetPos()
        oText.SetPos(x - iW, y)



class CMyButton(interface.CButton):
    
    def Enter(self):
        self.m_Tips = wrapinterface.CTextTips(None, -1, '\xc3\xf6\xb3\xac\xb0l\xc2\xdc', interface.FontLT12_1, direct = 1)
        self.m_Tips.SetOwner(self)
        self.GetParent().Enter()

    
    def Leave(self):
        self.m_Tips = None
        
        try:
            parent = self.GetParent()
        except SystemError:
            return None

        if not parent:
            return None
        
        parent.Leave()



class CTaskSwapBox(combdialog.CCombSubWnd):
    
    def CreateFromItem(cls, oParent, oItem):
        '''
\t\t:param oParent:
\t\t:param CTaskFollowTaskItem oItem:
\t\t:rtype: CTaskSwapBox
\t\t'''
        iTaskID = oItem.GetTaskID()
        iFontID = oItem.GetFontID()
        sTxt = oItem.GetShowText()
        return cls(oParent, iFontID, iTaskID, sTxt)

    CreateFromItem = classmethod(CreateFromItem)
    
    def __init__(self, oParent, iFontID, iTaskID, sTxt):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/track/taskitem.dlg')
        self.SetIgnoreEsc(True)
        self.m_sText = sTxt
        self.m_iFontID = iFontID
        self.m_iTaskID = iTaskID
        self.SetShowObject('img_close', False)
        self.RefreshText()

    
    def GetTaskID(self):
        return self.m_iTaskID

    
    def RefreshText(self):
        if self.m_sText is None:
            return None
        
        (iX, iY, iW, _) = self.GetLocData('loc_content')
        (iCX, iCY) = self.GetObject('loc_titlepoint').GetPos()
        self.m_oRichText = CTaskFollowText(self, iW, self.m_iFontID, self.m_sText, (iCX - iX, iCY - iY), self.m_iTaskID, 16777215)
        self.m_oRichText.SetPos(iX, iY)

    
    def GetSize(self):
        (iW, _) = self.GetObject('loc_bg').GetSize()
        iHeight = self.m_oRichText.GetHeight()
        return (iW, iHeight + 12)

    
    def SetAlpha(self, iAlpha):
        (iW, iH) = self.GetSize()
        self.m_oShadowBox = interface.CBoxObject(self, iW, iH, 13887739, iAlpha)
        self.m_oShadowBox.SetZ(10)



class CTaskTraceAutoFindEff(interface.CBaseObject):
    
    def __init__(self, oParent, iType, bHasScrollBar):
        interface.CBaseObject.__init__(self, oParent)
        self.m_iType = iType
        self.m_bHasScrollBar = bHasScrollBar
        if self.m_iType == 1:
            self.m_fCurPer = 0.8
            self.m_oChangeSizeTimer = timer.Timer(0.033, self.SetEffect, 4, self)
        else:
            self.m_fCurPer = 1
            self.m_oChangeSizeTimer = timer.Timer(0.033, self.SetEffect, 5, self)

    
    def SetEffect(self):
        lstEffectPath = [
            TW_NOCHANGE('\xd4\xd3\xcd\xbc/\xc8\xce\xce\xf1\xd1\xa1\xc7\xf8_\xc9\xcf/'),
            TW_NOCHANGE('\xd4\xd3\xcd\xbc/\xc8\xce\xce\xf1\xd1\xa1\xc7\xf8_\xcf\xc2/')]
        self.m_lstAutoFindPathEffect = []
        if self.m_iType == 0:
            self.m_fCurPer = 1
        elif self.m_iType == 1:
            self.m_fCurPer += 0.04
        elif self.m_iType == 2:
            self.m_fCurPer -= 0.05
        
        if self.m_fCurPer < 0.8:
            return None
        
        (iBoxW, iBoxH) = self.GetParent().GetSize()
        iFrameW = iBoxW
        iX = int((iFrameW / 2 - iFrameW * self.m_fCurPer / 2) + 3)
        iY = int(-8 * self.m_fCurPer)
        if not self.m_bHasScrollBar:
            iFrameW += 8
        
        for sEffectPath in lstEffectPath:
            oEffObj = ui.CHFrame(self, iFrameW * self.m_fCurPer, sEffectPath)
            self.m_lstAutoFindPathEffect.append(oEffObj)
            oEffObj.SetPos(int(iX), int(iY))
            iY += iBoxH * self.m_fCurPer - 10
