# pycdc 交叉复核产物 · script.fls entry 2415
# co_filename(原始)='script/mxgame/shitu/view/dlgstshouyetudi.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_2415.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: ${DATE} ${TIME}
\xd7\xf7\xd5\xdf: ${AuthorName}
\xce\xc4\xbc\xfe: ${NAME}
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import combdialog
import slot
import pagedlgbase
import interface
import shitudefine
import dgtstshouyetudi

class CTudiShouyeDlg(combdialog.CCombSubWnd, slot.ISignalSubject, pagedlgbase.COnePageDlgBase):
    SS_ShowExpProcessInfo = 'SS_ShowExpProcessInfo()'
    SS_ClearExpProcessInfo = 'SS_ClearExpProcessInfo()'
    SS_JoinTask = 'SS_JoinTask(iTaskID)'
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/shitu/shitu_shouyetudi.dlg')
        pagedlgbase.COnePageDlgBase.__init__(self)
        self.ssInit()
        self.m_DelegateList = None
        self.m_ExpTipsBox = None
        self.m_ExpTips = None
        self.m_tShowTaskInfo = None
        self.m_oDesc = None
        self.InitDelegate()
        self.InitExpTipsBox()
        self.InitDlg()

    
    def VOpenPage(self, dExtend = None):
        self.SetShow(True)

    
    def \x8dClose(self):
        self.SetShow(False)

    
    def SetExp(self, iCur, iNxt):
        oProgress = self.GetObject('progress_chushi')
        if iNxt == 0:
            sRealNxt = '--'
            iRealNxt = 1
        else:
            sRealNxt = str(iNxt)
            iRealNxt = iNxt
        oProgress.SetRate(iCur * 1000 / iRealNxt)
        self.GetObject('text_progress').SetText('%s/%s' % (str(iCur), sRealNxt))

    
    def ShowExpTips(self, sTips):
        import wrapinterface
        self.m_ExpTips = wrapinterface.CTextTips(self, -1, sTips, interface.FontLT14_3, direct = 1, owner = self.m_ExpTipsBox)

    
    def ClearExpTips(self):
        self.m_ExpTips = None

    
    def ShowTaskList(self, dTaskList):
        oTable = self.GetObject('tab_it')
        oTable.Clear()
        self.GetObject('text_desc').SetShow(not bool(dTaskList))
        self.GetObject('txt_tips').SetShow(bool(dTaskList))
        self.GetObject('text_title').SetText('')
        self.GetObject('btn_join').SetShow(False)
        self.m_oDesc = None
        oSelectItem = None
        for dInfo in dTaskList:
            oIt = oTable.AddTextItem([
                dInfo[shitudefine.KEY_TASK_TITLE],
                dInfo[shitudefine.KEY_PLAYER_NAME]])
            oIt.m_dTaskInfo = dInfo
            if (dInfo[shitudefine.KEY_TASK_ID], dInfo[shitudefine.KEY_PLAYER_NAME]) == self.m_tShowTaskInfo:
                oSelectItem = oIt
                continue
        
        if oSelectItem is None:
            oSelectItem = oTable.GetItem(0)
        
        if oSelectItem:
            oSelectItem.LeftUp()
            self.m_tShowTaskInfo = (oSelectItem.m_dTaskInfo[shitudefine.KEY_TASK_ID], oSelectItem.m_dTaskInfo[shitudefine.KEY_PLAYER_NAME])
        
        oTable.ResetItems()
        oTable.ResetScrollBar()

    
    def ShowTaskInfo(self, iIdx):
        oItem = self.GetObject('tab_it').GetItem(iIdx)
        self.SetTaskTitle(oItem.m_dTaskInfo[shitudefine.KEY_TASK_TITLE])
        self.SetTaskDesc(oItem.m_dTaskInfo[shitudefine.KEY_TASK_TARGET], oItem.m_dTaskInfo[shitudefine.KEY_DESC], oItem.m_dTaskInfo[shitudefine.KEY_TASK_REWARD], oItem.m_dTaskInfo[shitudefine.KEY_TASK_CUR], oItem.m_dTaskInfo[shitudefine.KEY_TASK_SUM])
        self.GetObject('btn_join').SetShow(True)

    
    def SetTaskTitle(self, sTitle):
        self.GetObject('text_title').SetText(sTitle)

    
    def SetTaskDesc(self, sTarget, sDesc, sReward, iDoneNum, iSumNum):
        oTxt = self.GetObject('text_subtitle')
        iColor = oTxt.GetColor()
        sColro = interface.GetStrColor(iColor)
        if '$num' in sTarget:
            sTarget = sTarget.replace('$num', str(iSumNum))
        
        sTxt = ''
        sTxt = '%s%s\xa5\xf4\xb0\xc8\xa5\xd8\xbc\xd0#n#r%s#n#r#r' % (sTxt, sColro, sTarget)
        sTxt = '%s%s\xa5\xf4\xb0\xc8\xb4y\xadz#n#r%s#n#r#r' % (sTxt, sColro, sDesc)
        sTxt = '%s%s\xa5\xf4\xb0\xc8\xbc\xfa\xc0y#n#r%s#n#r#r' % (sTxt, sColro, sReward)
        sTxt = '%s%s\xa7\xb9\xa6\xa8\xa6\xb8\xbc\xc6#n#r%d/%d#n#r#r' % (sTxt, sColro, iDoneNum, iSumNum)
        import wrapinterface
        (x, y, w, h) = self.GetLocData('text_desc')
        oDesc = self.GetObject('text_desc')
        iColor = oDesc.GetColor()
        iFontID = oDesc.GetFont()
        self.m_oDesc = wrapinterface.WrapRichTextWithLinkCursor(self, w, iFontID, sTxt, normalcolor = iColor)
        self.m_oDesc.\xdc\xeatPos(x, y)

    
    def JoinTask(self):
        oTable = self.GetObject('tab_it')
        oItem = oTable.GetSelectItem()
        if not oItem:
            return None
        
        self.ssEmit(self.SS_JoinTask, oItem.m_dTaskInfo[shitudefine.KEY_TASK_ID])

    
    def InitDelegate(self):
        self.m_DelegateList = [
            dgtstshouyetudi.CShouYeTudiDgt(self)]

    
    def InitDlg(self):
        self.GetObject('text_subtitle').SetShow(False)

    
    def InitExpTipsBox(self):
        (x, y, w, h) = self.GetLocData('progress_chushi')
        self.m_ExpTipsBox = interface.CNotifyBox(self, w, h, alpha = 0, msgid = 1)
        self.m_ExpTipsBox.\xdc\xeatPos(x, y)

    
    def LeftUp(self):
        combdialog.CCombDialog.LeftUp(self)
        if self.m_oDesc:
            obj = self.m_oDesc.GetLinkObj()
            if obj and hasattr(obj, 'OnLeftUp'):
                obj.OnLeftUp()
            
        

    
    def OnEnter(self, iMsgID):
        if iMsgID == 1:
            self.ssEmit(self.SS_ShowExpProcessInfo)
        

    
    def OnLeave(self, iMsgID):
        if iMsgID == 1:
            self.ssEmit(self.SS_ClearExpProcessInfo)
        

    
    def OnMessage(self, iMsgID):
        if iMsgID == 2:
            self.JoinTask()
        elif iMsgID < iMsgID:
            pass
        elif iMsgID < 150:
            self.ShowTaskInfo(iMsgID - 101)
