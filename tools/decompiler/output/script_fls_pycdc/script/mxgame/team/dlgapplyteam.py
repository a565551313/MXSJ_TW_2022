# pycdc 交叉复核产物 · script.fls entry 3817
# co_filename(原始)='script/mxgame/team/dlgapplyteam.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3817.pyc (Python 2.5)

import interface
import C_sys
import combdialog
import combmacro
import stackcheck
g_ApplyTeamDlg = None

def ModuleReset():
    global g_ApplyTeamDlg
    g_ApplyTeamDlg = None


def Show():
    global g_ApplyTeamDlg
    if not g_ApplyTeamDlg:
        g_ApplyTeamDlg = CApplyTeamDlg()
    
    g_ApplyTeamDlg.SetShow(True)
    g_ApplyTeamDlg.CheckKuafu()


def Switch():
    global g_ApplyTeamDlg
    if not g_ApplyTeamDlg:
        g_ApplyTeamDlg = CApplyTeamDlg()
        g_ApplyTeamDlg.CheckKuafu()
    else:
        bShow = g_ApplyTeamDlg.GetShow()
        g_ApplyTeamDlg.SetShow(not bShow)
        if not bShow:
            g_ApplyTeamDlg.CheckKuafu()
        
        g_ApplyTeamDlg.Topmost()

MEMBERTEXT_DICT = {
    '\xbfN\xc2\xf9': '\xbfN\xc2\xf9\xa8\xea\xb8g\xc5\xe7\xa1A\xa6Y\xa6n\xad\xb9\xaa\xab++++++\xa1C',
    '\xb0\xc6\xa5\xbb': '\xb0\xc6\xa5\xbb\xb6\xa4\xa5\xee\xa1A\xa5h\xaa\xba\xb6i\xb2\xd5\xa1C',
    '\xb0\xa3\xc5]': '\xb0\xa3\xc5]\xb6\xa4\xa5\xee\xa1A\xadn\xb8g\xc5\xe7\xaa\xba\xb3t\xab\xd7\xb6i\xb2\xd5\xa4F+++\xa1C',
    '\xbe\xc7\xae{\xa5\xf4\xb0\xc8': '\xbe\xc7\xae{\xa5\xf4\xb0\xc8\xa1A\xa5h\xaa\xba\xb6i\xb2\xd5\xa1C',
    '\xb0g\xaec': '\xb0g\xaec\xb6\xa4\xa5\xee\xa1A\xa5h\xaa\xba\xb6i\xb2\xd5\xa4F+++++\xa1C',
    '\xb7\xed\xabe\xac\xa1\xb0\xca': '\xac\xa1\xb0\xca\xb6}\xb2\xd5\xa4F\xa1A\xa5h\xaa\xba++++\xa1C' }
TEAM_DICT = {
    '\xbfN\xc2\xf9': '\xbfN\xc2\xf9\xa8D\xb2\xd5\xa1A\xa4\xd6\xa4H\xaa\xba+++\xa1C',
    '\xb0\xa3\xc5]': '\xb0\xa3\xc5]\xa8D\xb2\xd5\xa1A\xa4\xd6\xa4H\xaa\xba\xb2\xd5\xa7\xda\xa1C',
    '\xb0\xc6\xa5\xbb': '\xb0\xc6\xa5\xbb\xa8D\xb2\xd5\xa1A\xa4\xd6\xa4H\xaa\xba\xa5[\xa1C',
    '\xbe\xc7\xae{\xa5\xf4\xb0\xc8': '\xa8D\xb2\xd5\xbe\xc7\xae{\xa5\xf4\xb0\xc8\xa1A\xa4\xd6\xa4H\xaa\xba+++\xa1C',
    '\xb0g\xaec': '\xb0g\xaec\xa8D\xb2\xd5\xa1A\xa4\xd6\xa4H\xaa\xba\xa5[\xa7\xda\xa1C',
    '\xb7\xed\xabe\xac\xa1\xb0\xca': '\xac\xa1\xb0\xca\xa8D\xb2\xd5\xa1A\xa4\xd6\xa4H\xaa\xba\xa5[\xa7\xda+++\xa1C' }
BTNTIPS_DICT = {
    '\xbfN\xc2\xf9': '\xa8\xec\xbbP\xa6\xdb\xa4v\xb5\xa5\xaf\xc5\xac\xdb\xaa\xf1\xaa\xba\xb3\xf5\xb4\xba\xb2\xd5\xb6\xa4\xb7t\xb9p\xbe\xd4\xb0\xab\xa1A\xa5i\xc0\xf2\xb1o\xb8g\xc5\xe7\xbc\xfa\xc0y',
    '\xb0\xc6\xa5\xbb': '\xa4H\xaa\xab\xb5\xa5\xaf\xc5\xb9F\xa8\xec30\xaf\xc5\xab\xe1\xa1A\xa5i\xa5H\xa6b#Y\xa9\xfa\xa4\xeb\xab\xb0\xa1]253,180\xa1^#n\xaa\xba\xac\xef\xa6\xe6\xaa\xcc\xb6i\xa4J\xb0\xc6\xa5\xbb\xa1A\xa5i\xc0\xf2\xb1o\xaa\xab\xab~\xbc\xfa\xc0y',
    '\xb0\xa3\xc5]': '\xa4H\xaa\xab\xb5\xa5\xaf\xc5\xb9F\xa8\xec20\xaf\xc5\xab\xe1\xa1A\xa5i\xa5H\xa6b#Y\xa9\xfa\xa4\xeb\xab\xb0\xa1]278,191\xa1^#n\xaa\xba\xb0\xa3\xc5]\xaev\xbb\xe2\xa8\xfa\xb0\xa3\xc5]\xa5\xf4\xb0\xc8\xa1A\xa5i\xc0\xf2\xb1o\xb8g\xc5\xe7\xbc\xfa\xc0y',
    '\xbe\xc7\xae{\xa5\xf4\xb0\xc8': '\xaaA\xb0\xc8\xbe\xb9\xb6}\xa9\xf140\xa4\xd1\xab\xe1\xa6b#Y\xa9\xfa\xa4\xeb\xab\xb0\xa1]301,178\xa1^#n\xaa\xba\xc0\xb0\xac\xa3\xbe\xc7\xae{\xab\xfc\xa4\xde\xa4H\xbb\xe2\xa8\xfa\xbe\xc7\xae{\xa5\xf4\xb0\xc8\xa1A\xa5i\xc0\xf2\xb1o\xaa\xab\xab~\xbc\xfa\xc0y\xa9M\xae\xb7\xae\xbb\xa8\xec\xc5\xdc\xb2\xa7\xb9\xda\xb7Q\xa5\xf8\xc3Z\xa1B\xa8\xc4\xa8\xc4\xafW\xa1B\xa4p\xc6F\xb3\xc0',
    '\xb0g\xaec': '\xaaA\xb0\xc8\xbe\xb9\xb5\xa5\xaf\xc5\xa1\xd955\xaf\xc5\xa1A\xa4H\xaa\xab\xb5\xa5\xaf\xc5\xb9F\xa8\xec50\xaf\xc5\xab\xe1\xb2\xd5\xa6\xa85\xa4H\xb6\xa4\xa5\xee\xa1A\xa8\xcf\xa5\xce\xb9D\xa8\xe3#Y\xae\xc9\xaa\xc5\xa4\xa7\xbd\xfc#n\xb6i\xa4J\xb0g\xaec\xb6i\xa6\xe6\xb1\xb4\xc0I\xa1A\xa5i\xc0\xf2\xb1o\xaa\xab\xab~\xbc\xfa\xc0y',
    '\xb7\xed\xabe\xac\xa1\xb0\xca': '\xb6\xa4\xaa\xf8\xa1A\xb6\xa4\xa5\xee\xabD\xba\xa1\xad\xfb\xa1A\xb6\xa4\xaa\xf8\xb5\xa5\xaf\xc5\xa1\xd930' }

class CMyListBox(interface.CListBox):
    
    def __init__(self, parent, color, font, x, y, w, h, fname = 'combdialog/\xca\xfa\xb9\xf6\xb6\xaf\xcc\xf5/down.igs'):
        interface.CListBox.__init__(self, parent, color, font, x, y, w, h, fname = 'combdialog/\xca\xfa\xb9\xf6\xb6\xaf\xcc\xf5/down.igs')
        (dw, dh) = self.m_DownButton.GetSize()
        self.m_Box = interface.CClickBox(self, w - dw, h, 0, 0, 1)
        (self.m_OneWide, _) = interface.CTextObject(self, '\xa7\xda', font, 255, 0).GetSize()

    
    def AddText(self, txt):
        (w, _) = self.GetSize()
        txt = txt.center((w / self.m_OneWide) * 2)
        interface.CListBox.AddText(self, txt)

    
    def SelectText(self, txt):
        if txt in self.m_TextList:
            idx = self.m_TextList.index(txt)
            self.OnSelect(idx + 1)
        

    
    def OnSelect(self, sel):
        interface.CListBox.OnSelect(self, sel)
        self.GetParent().OnSaveBtn(sel)



class CFubenListBox(CMyListBox):
    
    def OnSelect(self, sel):
        CMyListBox.OnSelect(self, sel)
        self.GetParent().OnFubenListSelect(sel)



class CDefaultTextEdit(interface.CEdit):
    
    def SetDefaultText(self, default):
        self.m_DefautlText = interface.CTextObject(self, default, interface.FontLT14_3, 10066329, 0)

    
    def AddChar(self, char):
        self.m_Color = interface.COLOR_1
        interface.CEdit.AddChar(self, char)
        if hasattr(self, 'm_DefautlText') and self.m_DefautlText and self.GetText():
            self.m_DefautlText = None
        



class CApplyTeamDlg(combdialog.CCombDialog):
    s_SendGap = 60
    TIPS_WIDE = 310
    BTN_LIST = [
        'btn_shaoshuang',
        'btn_chumo',
        'btn_fuben',
        'btn_xuetu',
        'btn_maze',
        'btn_huodong']
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/applyteam.dlg')
        interface.Center(self)
        self.SelItemBtn = None
        self.SelTypeBtn = None
        import hero
        propitem = hero.g_Name2PropItem['m_Grade']
        propitem.AddRefreshCallbackWithID('CApplyTeamDlg', self.Refresh)
        self.Refresh()
        (x, y, w, h) = self.GetLocData('btn_member')
        self.m_MemberBox = interface.CClickBox(self, 50, h + 5, 0, 0, msgid = 41)
        self.m_MemberBox.SetPos((x - 1) + w, y - 1)
        import teamui
        if teamui.IsTeam():
            self.GetObject('btn_member').LeftUp()
        
        self.GetObject('btn_shaoshuang').LeftUp()
        
        try:
            self.LoadBtnState()
        except:
            pass

        self.m_InitFinish = True
        self.CreateCodeEdit()

    
    def CreateCodeEdit(self):
        self.m_CodeEdit = combmacro.CEDIT(CDefaultTextEdit, 'desc', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_CodeEdit.SetLimit(42)
        self.m_CodeEdit.Active(True)
        self.RefreshEditText()

    
    def GetDefaultEditText(self):
        data = MEMBERTEXT_DICT
        desc = data[self.SelItemBtn.m_Text]
        return desc

    
    def RefreshEditText(self):
        if getattr(self, 'm_CodeEdit', None):
            editText = self.m_CodeEdit.GetText()
            if not editText:
                sText = self.GetDefaultEditText()
                self.m_CodeEdit.SetDefaultText(sText)
            
        

    
    def CheckKuafu(self):
        import misc
        if not misc.IsInKuafuServer():
            return None
        
        lValid = [
            'btn_shaoshuang',
            'btn_chumo',
            'btn_fuben',
            'btn_maze']
        for name in self.BTN_LIST:
            btn = self.GetObject(name)
            bValid = name in lValid
            if not bValid:
                btn.SetSelect(False)
                btn.Enable(bValid)
                None(btn.SetFrame if bValid else 1)
                continue
        
        for name in lValid:
            if self.GetObject(name).IsSelected():
                break
                continue
        

    
    def LoadBtnState(self):
        import hero
        st = hero.GetPrivateData('team', 'CApplyTeamDlg')
        if not st:
            return None
        
        lst = st.split(',')
        if len(lst) != 6:
            return None
        
        (btn1Name, btn2Name) = lst[:2]
        self.GetObject(btn1Name).LeftUp()
        self.GetObject(btn2Name).LeftUp()
        listBoxList = [
            self.m_SceneList,
            self.m_FubenList,
            self.m_FubenGradeList,
            self.m_MazeList]
        for txt, listBox in zip(lst[2:], listBoxList):
            if txt in listBox.m_TextList:
                listBox.SelectText(txt)
                continue
        

    
    def OnSaveBtn(self, sel):
        self.SaveBtnState()

    
    def SaveBtnState(self):
        if not hasattr(self, 'm_InitFinish'):
            return None
        
        lst = []
        if self.GetObject('btn_member').IsSelected():
            lst.append('btn_member')
        
        for name in self.BTN_LIST:
            if self.SelItemBtn == self.GetObject(name):
                lst.append(name)
                break
                continue
        
        listBoxList = [
            self.m_SceneList,
            self.m_FubenList,
            self.m_FubenGradeList,
            self.m_MazeList]
        for listBox in listBoxList:
            lst.append(listBox.GetText().strip())
        
        txt = ','.join(lst)
        import hero
        hero.SavePrivateData('team', 'CApplyTeamDlg', txt)

    
    def OnButtonEnter(self, btn):
        import wrapinterface
        txt = BTNTIPS_DICT[btn.m_Text]
        self.m_Tips = wrapinterface.CTextTips(None, self.TIPS_WIDE, txt, interface.FontLT14_3, direct = 1)
        self.m_Tips.SetOwner(btn)

    
    def OnButtonLeave(self, btn):
        self.m_Tips = None

    
    def Refresh(self):
        self.RefreshSceneList()
        self.RefreshMazeList()
        self.RefreshFubenList()

    
    def OnSelect(self, sel):
        import usermacro
        import misc
        import hero
        import teamui
        serverDay = misc.GetServerDay()
        serverGrade = hero.g_Prop.m_GradeLimit
        if sel.m_MsgID == 13:
            if not hero.g_Prop.m_Grade >= 30:
                usermacro.PROMPT_MSG('\xa4H\xaa\xab\xb5\xa5\xaf\xc5\xa1\xd930\xaf\xc5\xa1A\xa4~\xa5i\xa5H\xb6i\xa6\xe6\xb0\xc6\xa5\xbb\xa5\xf4\xb0\xc8')
                return False
            
        elif sel.m_MsgID == 14:
            if not serverDay > 40:
                usermacro.PROMPT_MSG('\xaaA\xb0\xc8\xbe\xb9\xb6}\xa9\xf1\xa4\xd1\xbc\xc6\xa1\xd640\xa4\xd1\xa1A\xa4~\xa5i\xa5H\xb6i\xa6\xe6\xbe\xc7\xae{\xa5\xf4\xb0\xc8')
                return False
            
        elif sel.m_MsgID == 15:
            if not serverGrade >= 55 and hero.g_Prop.m_Grade >= 50:
                usermacro.PROMPT_MSG('\xaaA\xb0\xc8\xbe\xb9\xb5\xa5\xaf\xc5\xa1\xd955\xaf\xc5\xa1A\xa4H\xaa\xab\xb5\xa5\xaf\xc5\xa1\xd950\xaf\xc5\xa1A\xa4~\xa5i\xa5H\xb6i\xa6\xe6\xb0g\xaec\xa5\xf4\xb0\xc8')
                return False
            
        elif sel.m_MsgID == 16:
            if not hero.g_Prop.m_Grade >= 30:
                usermacro.PROMPT_MSG('\xa4H\xaa\xab\xb5\xa5\xaf\xc5\xa1\xd930\xaf\xc5\xa1A\xa4~\xa5i\xa5H\xb6i\xa6\xe6\xac\xa1\xb0\xca')
                return False
            
        
        if sel.m_MsgID < sel.m_MsgID:
            pass
        elif sel.m_MsgID < 20:
            self.SelItemBtn = sel
        elif sel.m_MsgID < sel.m_MsgID:
            pass
        elif sel.m_MsgID < 30:
            self.SelTypeBtn = sel
        
        self.RefreshDesc()
        self.SaveBtnState()
        self.RefreshEditText()
        return True

    
    def SetShow(self, s):
        import teamui
        combdialog.CCombDialog.SetShow(self, s)
        if s:
            self.m_CodeEdit.Active(True)
            self.RefreshEditText()
        

    
    def OnFubenListSelect(self, sel):
        self.RefreshFubenGradeList()

    
    def RefreshFubenGradeList(self):
        lastName = None
        lastIdx = None
        if hasattr(self, 'm_FubenGradeList') and self.m_FubenGradeList:
            lastName = self.m_FubenGradeList.GetText().strip()
        
        import applyteamdata
        import hero
        fubenName = self.m_FubenList.GetText().strip()
        lst = []
        for data in applyteamdata.FUBEN_DATA:
            if data['fuben'] != fubenName:
                continue
            
            if hero.g_Prop.m_Grade >= 100:
                gap = 25
            else:
                gap = 0
            if hero.g_Prop.m_Grade + gap >= data['difficultyGrade']:
                if data['difficulty'] not in lst:
                    lst.append(data['difficulty'])
                
            data['difficulty'] not in lst
        
        self.m_FubenGradeList = combmacro.CLISTBOX(CMyListBox, 'pos_fubenGrade', self, 16777215, interface.FontLT14_3)
        self.m_FubenGradeList.SetItemProp(2, 16, len(lst) * 18)
        self.m_FubenGradeList.SetLimit(30)
        for idx, name in enumerate(lst):
            self.m_FubenGradeList.AddTextItem(name)
            if lastName == name:
                lastIdx = idx + 1
                continue
        
        if lastIdx:
            self.m_FubenGradeList.OnSelect(lastIdx)
        else:
            self.m_FubenGradeList.OnSelect(1)
        self.m_FubenGradeList.Enable(False)

    
    def RefreshDesc(self):
        self.m_Desc = None
        if not self.SelItemBtn:
            return None
        
        if not self.SelTypeBtn:
            return None
        

    
    def RefreshSceneList(self):
        import applyteamdata
        import hero
        lastName = None
        lastIdx = None
        nearIdx = None
        nearGrade = None
        if hasattr(self, 'm_SceneList') and self.m_SceneList:
            lastName = self.m_SceneList.GetText().strip()
        
        lst = []
        for data in applyteamdata.SHAOSHUANG_DATA:
            if hero.g_Prop.m_Grade + 20 >= data['grade']:
                lst.append(data)
                continue
        
        lst.reverse()
        if len(lst) > 10:
            ilen = 10
        else:
            ilen = len(lst)
        self.m_SceneList = combmacro.CLISTBOX(CMyListBox, 'pos_scene', self, 16777215, interface.FontLT14_3)
        self.m_SceneList.SetItemProp(2, 16, ilen * 18)
        self.m_SceneList.SetLimit(30)
        for idx, data in enumerate(lst):
            name = data['name']
            self.m_SceneList.AddTextItem(name)
            if lastName == name:
                lastIdx = idx + 1
            
            if hero.g_Prop.m_Grade <= data['grade']:
                if not nearGrade or nearGrade > data['grade']:
                    nearIdx = idx + 1
                
            nearGrade > data['grade']
        
        if lastIdx:
            self.m_SceneList.OnSelect(lastIdx)
        elif nearIdx:
            self.m_SceneList.OnSelect(nearIdx)
        else:
            self.m_SceneList.OnSelect(1)
        self.m_SceneList.Enable(False)

    
    def RefreshMazeList(self):
        import applyteamdata
        import hero
        lastName = None
        lastIdx = None
        if hasattr(self, 'm_MazeList') and self.m_MazeList:
            lastName = self.m_MazeList.GetText().strip()
        
        lst = []
        for data in applyteamdata.MAZE_DATA:
            if hero.g_Prop.m_Grade >= data['grade']:
                lst.append(data['name'])
                continue
        
        if len(lst) > 10:
            ilen = 10
        else:
            ilen = len(lst)
        self.m_MazeList = combmacro.CLISTBOX(CMyListBox, 'pos_maze', self, 16777215, interface.FontLT14_3)
        self.m_MazeList.SetItemProp(2, 16, len(lst) * 18)
        self.m_MazeList.SetLimit(30)
        for idx, name in enumerate(lst):
            self.m_MazeList.AddTextItem(name)
            if lastName == name:
                lastIdx = idx + 1
                continue
        
        if lastIdx:
            self.m_MazeList.OnSelect(lastIdx)
        else:
            self.m_MazeList.OnSelect(1)
        self.m_MazeList.Enable(False)

    
    def RefreshFubenList(self):
        import applyteamdata
        import hero
        lastName = None
        lastIdx = None
        if hasattr(self, 'm_FubenList') and self.m_FubenList:
            lastName = self.m_FubenList.GetText().strip()
        
        lst = []
        for data in applyteamdata.FUBEN_DATA:
            if hero.g_Prop.m_Grade >= 100:
                if data['fuben'] not in lst:
                    lst.append(data['fuben'])
                
            data['fuben'] not in lst
            if hero.g_Prop.m_Grade >= max(data['difficultyGrade'], data['grade']):
                if data['fuben'] not in lst:
                    lst.append(data['fuben'])
                
            data['fuben'] not in lst
        
        lst.reverse()
        if len(lst) > 10:
            ilen = 10
        else:
            ilen = len(lst)
        self.m_FubenList = combmacro.CLISTBOX(CFubenListBox, 'pos_fubenName', self, 16777215, interface.FontLT14_3)
        self.m_FubenList.SetItemProp(2, 16, ilen * 18)
        self.m_FubenList.SetLimit(30)
        for idx, name in enumerate(lst):
            self.m_FubenList.AddTextItem(name)
            if lastName == name:
                lastIdx = idx + 1
                continue
        
        if lastIdx:
            self.m_FubenList.OnSelect(lastIdx)
        else:
            self.m_FubenList.OnSelect(1)
        self.m_FubenList.Enable(False)

    
    def Confirm(self):
        import teamui
        import usermacro
        iTime = C_sys.GetTime()
        if hasattr(self, 'm_LastFreshTime1') and self.m_LastFreshTime1 + self.s_SendGap * 10000 > iTime:
            second = self.s_SendGap - (iTime - self.m_LastFreshTime1) / 10000
            if second >= 60:
                minute = second / 60
                second = second % 60
                txt = '%d\xa4\xc0%d\xac\xed' % (minute, second)
            else:
                txt = '%d\xac\xed' % second
            usermacro.PROMPT_MSG('\xbd\xd0\xa6b%s\xab\xe1\xa6A\xb5o\xb0e\xb2\xd5\xb6\xa4\xabH\xae\xa7' % txt)
            return None
        
        if self.GetObject('btn_member').IsSelected():
            if not teamui.IsTeam():
                
                def callback(obj):
                    dlg = obj.Get()
                    if dlg:
                        dlg.Confirm()
                    

                usermacro.PROMPT_MSG('\xa5\xd1\xa9\xf3\xa7A\xb7\xed\xabe\xa8S\xa6\xb3\xb6\xa4\xa5\xee\xa1A\xac\xb0\xa7A\xb3\xd0\xab\xd8\xa4F\xb6\xa4\xa5\xee')
                teamui.SetRefreshStatusCallBack(callback, interface.CShadowObject(self))
                teamui.MakeTeamOnlySelf()
                return None
            
            if teamui.GetTeamMemberCount() == 5:
                usermacro.PROMPT_MSG('\xb1z\xaa\xba\xb6\xa4\xa5\xee\xa4w\xb8g\xba\xa1\xad\xfb\xa1A\xa4\xa3\xaf\xe0\xb5o\xa7G\xb2\xd5\xb6\xa4\xae\xf8\xae\xa7')
                return None
            
        
        txt = self.GetSendText()
        self.m_LastFreshTime1 = C_sys.GetTime()
        print '\xb2\xd5\xb6\xa4\xb5o\xb0eSend', txt
        import netchat
        stackcheck.SetBeforeCall(stackcheck.KEY_CHATINPUT)
        netchat.C2SPlayerChat(20, txt)

    
    def GetMidTextEndText(self):
        import applyteamdata
        import hero
        import teamui
        if self.SelItemBtn.m_Text == '\xbfN\xc2\xf9':
            sceneName = self.m_SceneList.GetText().strip()
            sceneGrade = applyteamdata.GetSceneGradeByName(sceneName)
            midText = sceneName
        elif self.SelItemBtn.m_Text == '\xb0\xa3\xc5]':
            pass
        elif self.SelItemBtn.m_Text == '\xbe\xc7\xae{\xa5\xf4\xb0\xc8':
            '' = ''
            endText = 'g>=20'
        elif self.SelItemBtn.m_Text == '\xb0g\xaec':
            mazeName = self.m_MazeList.GetText().strip()
            mazeGrade = applyteamdata.GetMazeGradeByName(mazeName)
            midText = mazeName
            endText = 'g>=%d' % mazeGrade
        elif self.SelItemBtn.m_Text == '\xb0\xc6\xa5\xbb':
            fubenName = self.m_FubenList.GetText().strip()
            difficult = self.m_FubenGradeList.GetText().strip()
            (grade, difficultyGrade) = applyteamdata.GetFubenGrade(fubenName, difficult)
            myGrade = hero.g_Prop.m_Grade
            midText = fubenName + difficult
            endText = 'abs(%d-g)<=30 and ((g<100 and g>=%d) or (g>=100 and g+25>=%d))' % (myGrade, difficultyGrade, difficultyGrade)
        elif self.SelItemBtn.m_Text == '\xb7\xed\xabe\xac\xa1\xb0\xca':
            midText = ''
            endText = 'g>=30'
        
        return (midText, endText)

    
    def GetSendText(self):
        (markText, joinText, startText) = self.GetMemberText()
        (midText, endText) = self.GetMidTextEndText()
        desc = self.GetInputText()
        txt = startText + midText + desc + joinText + markText + endText
        return txt

    
    def GetInputText(self):
        data = MEMBERTEXT_DICT
        desc = data[self.SelItemBtn.m_Text]
        if self.m_CodeEdit.GetText().strip():
            import chatinput
            editText = self.m_CodeEdit.GetText().strip()
            editText = chatinput.EmoteFilter(editText)
            editText = editText.replace('#', '**')
            desc = desc.split('\xa1A')[0] + '\xa1A' + editText + '\xa1C'
        
        return desc

    
    def GetMemberText(self):
        import hero
        import teamui
        className = hero.id2class(hero.g_Prop.m_Class)
        if self.GetObject('btn_member').IsSelected():
            markText = '&@&'
            joinText = '#s(58, %d)' % hero.g_ID
            startText = '#G\xa1]%d\xaf\xc5%s\xa1A\xb6\xa4\xa5\xee\xa4H\xbc\xc6\xa1G%d\xa1^#n' % (hero.g_Prop.m_Grade, className, teamui.GetTeamMemberCount())
        else:
            markText = '&^&'
            joinText = '#s(59, %d)' % hero.g_ID
            startText = '#G\xa1]%d\xaf\xc5%s\xa1^#n' % (hero.g_Prop.m_Grade, className)
        return (markText, joinText, startText)

    
    def CloseWindow(self):
        self.SetShow(False)
        self.m_CodeEdit.Active(False)

    
    def OnMessage(self, msgid):
        if msgid in (1, 7):
            self.CloseWindow()
        elif msgid == 6:
            import hero
            import usermacro
            import banword
            if hero.g_Prop.m_Huoli < 5 or hero.g_Prop.m_Tili < 5:
                usermacro.PROMPT_MSG('\xb5o\xa7G\xb2\xd5\xb6\xa4\xabH\xae\xa7\xbb\xdd\xadn5\xc2I\xc5\xe9\xa4O\xa9M\xac\xa1\xa4O')
                return None
            
            txt = self.m_CodeEdit.GetText().strip()
            if txt and not banword.IsValidOnIntrodruce(txt):
                usermacro.PROMPT_MSG('\xa7A\xaa\xba\xb5o\xa8\xa5\xa4\xa4\xa5]\xa7t\xb9H\xb8T\xb5\xfc\xbby\xa1I')
                return None
            
            self.Confirm()
        elif msgid == 41:
            self.GetObject('btn_member').LeftUp()
