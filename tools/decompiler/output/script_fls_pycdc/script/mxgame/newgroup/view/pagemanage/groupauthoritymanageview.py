# pycdc 交叉复核产物 · script.fls entry 3650
# co_filename(原始)='script/mxgame/newgroup/view/pagemanage/groupauthoritymanageview.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3650.pyc (Python 2.5)

'''
groupauthoritymanageview.py
create by xian90 2019/5/27 11:10
\xc4\xa3\xbf\xe9\xb9\xa6\xc4\xdc\xcb\xb5\xc3\xf7:
'''
import combdialog
import slot
import delegategroupauthority
import interface
import style
import wrapinterface
import usermacro

class CGroupAuthorityManageDlg(combdialog.CCombSubWnd, slot.ISignalSubject):
    BTNPOS = (0, 2, 3, 5, 4, 1)
    SS_DefaultPower = 'SS_DefaultPower'
    SS_ViewInitFinish = 'SS_ViewInitFinish'
    
    def __init__(self, pParent, pContext):
        combdialog.CCombSubWnd.__init__(self, pParent, 'dialog/group_new/group_manage/group_setpower.dlg')
        self.ssInit()
        self.SetIgnoreEsc(True)
        self.m_Table = self.GetObject('tab_member')
        self.m_Pos = []
        self.m_pDelegate = delegategroupauthority.CDelegateGroupAuthority(pContext, self)
        self.ssEmit(self.SS_ViewInitFinish)

    
    def RefreshGrantList(self, vMemberInfo):
        self.m_Table.Clear()
        x = self.m_Table.m_Widths[0] + self.m_Table.m_Widths[1] + self.m_Table.m_Widths[2] - 6
        self.m_Pos = [
            x]
        for w in self.m_Table.m_Widths[3:]:
            x += w - 2
            self.m_Pos.append(x)
        
        self.m_pDelegate.SetGrantData({ })
        for sName, sGrade, sZhiWeiLv, bDisable, iGrant, dInfo in vMemberInfo:
            box = self.m_Table.AddTextItem([
                sName,
                sGrade,
                sZhiWeiLv])
            box.m_Data = dInfo
            box.m_ID = dInfo['iId']
            box.m_Btn = []
            mask = 1
            for idx in xrange(6):
                x1 = self.m_Pos[self.BTNPOS[idx]]
                x2 = self.m_Pos[self.BTNPOS[idx] + 1]
                btn = CCheckButton(box, style.GetPath('combdialog/\xb0\xb4\xc5\xa5/\xd1\xa1\xd4\xf1.igs'), 0, 0, 0)
                if idx == 5:
                    btn.m_KickOut = True
                else:
                    btn.m_KickOut = False
                (w, h) = btn.GetSize()
                (_, h1) = box.GetSize()
                btn.SetPos((x2 + x1 - w) / 2, (h1 - h) / 2)
                box.m_Btn.append(btn)
                btn.Enable(not (mask & bDisable != 0))
                if mask & iGrant != 0:
                    btn.SetSelect(True)
                
                mask <<= 1
            
        
        self.m_Table.ResetItems()
        self.m_Table.ResetScrollBar()
        self.m_pDelegate.SetGrantData(self.GetGrantData())

    
    def GetGrantData(self):
        newGrantData = { }
        oldGrantData = self.m_pDelegate.GetGrantData()
        for box in self.m_Table.m_Items:
            grant = 0
            mask = 1
            for btn in box.m_Btn:
                if btn.IsSelected():
                    grant |= mask
                
                mask <<= 1
            
            if grant != oldGrantData.get(box.m_ID):
                newGrantData[box.m_ID] = grant
                continue
        
        return newGrantData

    
    def ChangePower(self):
        import commondialog
        newGrantData = self.GetGrantData()
        if not newGrantData:
            return None
        
        
        def ok(dlg):
            import netgroup
            grantInfo = dlg.m_Data
            for _ in xrange(10):
                if len(grantInfo) > 40:
                    netgroup.C2SChgGrant(grantInfo[:40])
                    grantInfo = grantInfo[40:]
                    continue
                netgroup.C2SChgGrant(grantInfo)
            

        dlg = commondialog.ShowMessageBox('\xc0\xb0\xac\xa3\xc5v\xad\xad\xb5o\xa5\xcd\xa4F\xc5\xdc\xa7\xf3\xa1A\xacO\xa7_\xabO\xa6s\xa1H', ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (ok, None))
        dlg.m_Data = newGrantData.items()

    
    def OnButtonSelect(self, btn):
        if btn.m_KickOut and btn.m_Selected:
            self.m_pDelegate.SetSelectCount(self.m_pDelegate.GetSelectCount() + 1)
            if self.m_pDelegate.GetSelectCount() > 4:
                btn.SetSelect(False)
                usermacro.PROMPT_MSG('\xb3\xcc\xa6h\xa5u\xaf\xe0\xb5\xb9\xa5|\xa6W\xc0\xb0\xac\xa3\xa6\xa8\xad\xfb\xa4\xc0\xb0t\xb6}\xb0\xa3\xc0\xb0\xb2\xb3\xc5v\xad\xad')
            
        elif btn.m_KickOut and not (btn.m_Selected):
            self.m_pDelegate.SetSelectCount(self.m_pDelegate.GetSelectCount() - 1)
        
        continue

    
    def OnHotBoxEnter(self, hotbox):
        if hotbox.m_Index > 2:
            return None
        
        hotbox.m_Tips = wrapinterface.CTextTips(None, 200, '\xc2I\xc0\xbb\xa5i\xb1\xc6\xa7\xc7', interface.FontLT14_3)

    
    def OnHotBoxLeave(self, hotbox):
        hotbox.m_Tips = None

    
    def OnHotBoxClick(self, hotbox):
        if hotbox.m_Index > 2:
            return None
        
        self.SortTable(hotbox.m_Index)

    
    def SortTable(self, idx):
        import group
        tab = self.m_Table
        if hasattr(tab, 'm_Reverse'):
            rev = not (tab.m_Reverse)
        else:
            rev = True
        sel = None
        for it in tab.m_Items:
            if it.IsSelected():
                sel = it.m_Data['id']
                continue
        
        if idx == 2:
            grant2order = {
                group.XuetuAdminGrant: 55 }
            
            infocmp = lambda x, y: if cmp(grant2order.get(x.m_Data['iZhiweiLv'], x.m_Data['iZhiweiLv']), grant2order.get(y.m_Data['iZhiweiLv'], y.m_Data['iZhiweiLv'])) and x.m_Data.get('iOnline'):
passcmp(x.m_Data['iOnline'], x.m_Data['iOnline'])
        elif idx == 1:
            
            infocmp = lambda x, y: if not cmp(y.m_Data['iGrade'], x.m_Data['iGrade']):
passcmp(y.m_Data.get('iOnline', 0), x.m_Data.get('iOnline', 0))
        else:
            
            infocmp = lambda x, y: if not cmp(x.m_Data['sName'], y.m_Data['sName']):
passcmp(y.m_Data.get('iOnline', 0), x.m_Data.get('iOnline', 0))
        tab.m_Items.sort(infocmp, reverse = not rev)
        tab.m_Reverse = rev
        tab.ResetItems()
        tab.ResetScrollBar()
        for box in tab.m_Items:
            if box.m_Data['iId'] == sel:
                it.Select(True)
                continue
        

    
    def OnMessage(self, msgid):
        if msgid == 2:
            self.ChangePower()
        elif msgid == 3:
            self.ssEmit(self.SS_DefaultPower)
        

    
    def Destroy(self):
        pass



class CCheckButton(interface.CButton):
    
    def __init__(self, parent, filename, x, y, msgid = 0):
        interface.CButton.__init__(self, parent, filename, x, y, msgid)
        self.m_Selected = False

    
    def LeftUp(self):
        interface.CButton.LeftUp(self)
        if self.m_Selected:
            self.SetSelect(False)
        else:
            self.SetSelect(True)

    
    def SetSelect(self, isSelected):
        if hasattr(self, 'm_EnableFlag') and not (self.m_EnableFlag):
            return None
        
        self.m_Selected = isSelected
        if isSelected:
            self.SetFrame(2)
        else:
            self.SetFrame(0)
        self.GetParent().GetParent().GetParent().OnButtonSelect(self)

    
    def Enable(self, isEnable):
        interface.CButton.Enable(self, isEnable)
        if isEnable:
            if self.m_Selected:
                self.SetFrame(2)
            else:
                self.SetFrame(0)
        else:
            self.SetFrame(3)

    
    def Enter(self):
        interface.CButton.Enter(self)
        if self.m_Selected:
            self.SetFrame(3)
        else:
            self.SetFrame(1)

    
    def Leave(self):
        interface.CButton.Leave(self)
        if self.m_Selected:
            self.SetFrame(2)
        else:
            self.SetFrame(0)

    
    def IsSelected(self):
        if not self.m_Selected and not hasattr(self, 'm_EnableFlag'):
            pass
        return self.m_EnableFlag
