# pycdc 交叉复核产物 · script.fls entry 458
# co_filename(原始)='script/mxgame/newgroup/view/pagemanage/groupskillresearchview.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_458.pyc (Python 2.5)

'''
groupskillresearchview.py
create by xian90 2019/5/27 11:10
\xc4\xa3\xbf\xe9\xb9\xa6\xc4\xdc\xcb\xb5\xc3\xf7:
'''
import combdialog
import slot
import delegategroupskillresearch
import interface
import misc

class CGroupSkillResearchDlg(combdialog.CCombSubWnd, slot.ISignalSubject):
    SS_OnClickActiveSkill = 'SS_OnClickActiveSkill(iSkillID)'
    SS_OnSelectSkillItem = 'SS_OnSelectSkillItem()'
    SS_RefreshView = 'SS_RefreshView()'
    
    def __init__(self, pParent, pContext):
        combdialog.CCombSubWnd.__init__(self, pParent, 'dialog/group_new/group_manage/group_skillstudy.dlg')
        self.ssInit()
        self.SetIgnoreEsc(True)
        self.m_oPreItem = None
        self.m_iActiveSkillId = 0
        self.InitView()
        self.m_pDelegate = delegategroupskillresearch.CDelegateGroupSkillResearch(pContext, self)

    
    def InitView(self):
        self.m_oPreItem = None
        self.m_iActiveSkillId = 0
        self.GetObject('text_curActiveSkillName').SetText('')

    
    def RefreshView(self):
        self.InitView()
        self.ssEmit(self.SS_RefreshView)

    
    def CreateSkillList(self, lstSkillInfo):
        if not lstSkillInfo:
            return None
        
        oTitleList = self.GetObject('tab_detail')
        oTitleList.Clear()
        for dSkillInfo in lstSkillInfo:
            d = dSkillInfo['info']
            oItem = CGroupSkillStudyItem(oTitleList, interface.COLOR_1, interface.COLOR_1, interface.COLOR_386, misc.Functor(self.SelectItem))
            oItem.SetData(d.get('name'), dSkillInfo)
            oItem.UpdateText()
            oTitleList.AddItem(oItem)
        
        oTitleList.ResetItems()
        oTitleList.ResetScrollBar()

    
    def SetActiveSkill(self, iSkillId, sSkillName):
        import usermacro
        self.m_iActiveSkillId = iSkillId
        if iSkillId:
            sTmp = self.GetObject('text_curActiveSkillName').GetText()
            if sTmp and sTmp != '' and sTmp != sSkillName:
                usermacro.PROMPT_MSG('\xa7\xde\xaf\xe0\xa4\xc1\xb4\xab\xa1G%s' % sSkillName)
            
            self.GetObject('text_curActiveSkillName').SetText(sSkillName)
        else:
            self.GetObject('text_curActiveSkillName').SetText('')

    
    def SetSelectItem(self, iSkillId):
        oTitleList = self.GetObject('tab_detail')
        lstItems = oTitleList.GetItems()
        for oItem in lstItems:
            iTmpSkillId = oItem.GetSkillID()
            if iSkillId and iSkillId == iTmpSkillId:
                oItem.SetSelect(True)
                self.m_oPreItem = oItem
                continue
            oItem.SetSelect(False)
        

    
    def SelectItem(self, oItem):
        iSkillId = oItem.GetSkillID()
        self.m_iActiveSkillId = iSkillId
        self.ssEmit(self.SS_OnSelectSkillItem, iSkillId)

    
    def OnActiveSkill(self):
        self.ssEmit(self.SS_OnClickActiveSkill, self.m_iActiveSkillId)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 3:
            self.OnActiveSkill()
        

    
    def Destroy(self):
        pass



class CGroupSkillStudyItem(combdialog.CCombSubWnd):
    
    def __init__(self, oParent, iNormalColor, iSelectColor = 16777215, iBgColor = 15981202, oSelectFunc = None):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/group_new/group_manage/group_skillstudyitem.dlg')
        (_, _, iW, iH) = self.GetLocData('loc_size')
        self.m_oSelect = interface.CBoxObject(self.GetObject('loc_size'), iW, iH, iBgColor)
        self.m_oSelect.SetShow(False)
        self.m_bSelect = False
        self.m_iSelectColor = iSelectColor
        self.m_iNormalColor = iNormalColor
        self.m_oSelectFunc = oSelectFunc
        self.m_oSkillData = None
        self.m_sSkillName = ''

    
    def UpdateText(self):
        self.GetObject('text_name').SetText(self.m_sSkillName)
        self.GetObject('text_desc').SetText(self.m_oSkillData.get('desc'))
        self.GetObject('text_lv').SetText(str(self.m_oSkillData.get('lv')))
        self.GetObject('text_progress').SetText(self.m_oSkillData.get('progress'))
        self.RefreshTextColor(self.m_iNormalColor)

    
    def RefreshTextColor(self, iColor):
        self.GetObject('text_name').SetColor(iColor)
        self.GetObject('text_desc').SetColor(iColor)
        self.GetObject('text_lv').SetColor(iColor)
        self.GetObject('text_progress').SetColor(iColor)

    
    def SetData(self, sName, dSkillData):
        self.m_sSkillName = sName
        self.m_oSkillData = dSkillData

    
    def GetSkillID(self):
        if not self.m_oSkillData:
            return 0
        
        return self.m_oSkillData.get('id', 0)

    
    def GetSkillName(self):
        return self.m_sSkillName

    
    def LeftUp(self):
        if self.m_bSelect:
            return None
        
        self.SetSelect(True)
        if self.m_oSelectFunc:
            None(None, None, None, None, None, None, None, None, None, None, None, None, None, self.m_oSelectFunc, self)
        

    
    def LeftDown(self):
        pass

    
    def SetSelect(self, bSelect):
        if self.m_bSelect == bSelect:
            return None
        
        self.m_bSelect = bSelect
        self.m_oSelect.SetShow(bSelect)
        if bSelect:
            self.RefreshTextColor(self.m_iSelectColor)
        else:
            self.RefreshTextColor(self.m_iNormalColor)

    
    def Enter(self):
        if self.m_bSelect:
            return None
        
        self.m_oSelect.SetShow(True)

    
    def Leave(self):
        if self.m_bSelect:
            return None
        
        self.m_oSelect.SetShow(False)
