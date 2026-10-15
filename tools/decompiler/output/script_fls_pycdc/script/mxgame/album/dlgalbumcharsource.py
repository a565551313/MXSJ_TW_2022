# pycdc 交叉复核产物 · script.fls entry 554
# co_filename(原始)='script/mxgame/album/dlgalbumcharsource.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_554.pyc (Python 2.5)

import interface
import combmacro
import combdialog
import wrapinterface
PAGECOUNT = 9
ROLEID2NAME = [
    [
        111,
        '\xb3p\xbb\xbb\xabL'],
    [
        112,
        '\xc5R\xc6E\xa4\xf5'],
    [
        211,
        '\xad\xe2\xaai\xbfP'],
    [
        212,
        '\xad\xb7\xb9a\xa8\xe0'],
    [
        121,
        '\xa4\xd1\xc2\xcd\xa4l'],
    [
        122,
        '\xb6\xb3\xb5L\xa4\xdf'],
    [
        221,
        '\xa5\xc9\xc3\xb9\xabb'],
    [
        222,
        '\xb2H\xb2M\xac\xee'],
    [
        131,
        '\xc3t\xb4\xf0\xa4l'],
    [
        132,
        '\xaa\xa2\xa6p\xad\xb7'],
    [
        231,
        '\xa4d\xa4\xdb\xbd\xba'],
    [
        232,
        '\xb5\xb5\xb9\xe4\xb5M']]

class CSourceDlg(combdialog.CCombDialog):
    
    def __init__(self, parent):
        combdialog.CCombDialog.__init__(self, parent, 'dialog/album/charsource.dlg')
        interface.Center(self)
        self.m_CurrentPage = 1
        self.m_LastClickTime = 0
        self.m_LastMsgid = 0
        import albumdata
        self.m_FileList = albumdata.GetCharData()
        self.m_RoleList = combmacro.CLISTBOX(interface.CListBox, 'locRole', self, interface.COLOR_12, interface.FontLT14_3)
        self.m_RoleList.SetItemProp(2, 16, 72)
        self.m_RoleList.m_SelectNotify = True
        for _, name in ROLEID2NAME:
            self.m_RoleList.AddTextItem(name)
        
        self.m_RoleList.SetReadOnly(True)
        self.m_RoleList.OnSelect(1)
        self.GoPage(1)

    
    def OnSelect(self, sel):
        self.m_RoleID = ROLEID2NAME[sel - 1][0]
        self.m_Data = { }
        for key, value in self.m_FileList.items():
            if key / 100 == self.m_RoleID:
                self.m_Data[key] = value
                continue
        
        self.m_PageCount = (len(self.m_Data) + PAGECOUNT - 1) / PAGECOUNT
        self.m_PageCountObj = combmacro.CTEXT(interface.CTextObject, 'locPageCount', self, str(self.m_PageCount), interface.FontLT14_3, 16777215, align = interface.ALIGN_LEFT | interface.ALIGN_MIDDLE)
        self.GoPage(self.m_CurrentPage)

    
    def GoPage(self, page):
        if page <= 0 or page > self.m_PageCount:
            return None
        
        import albumpublic
        self.m_Selected = -1
        self.m_CurrentPage = page
        self.m_CurrentPageObj = combmacro.CTEXT(interface.CTextObject, 'locCurrentPage', self, import albumpublic, interface.FontLT14_3, 16777215, align = interface.ALIGN_RIGHT | interface.ALIGN_MIDDLE)
        self.GetObject('btnPrePage').Enable(page > 1)
        self.GetObject('btnNextPage').Enable(page < self.m_PageCount)
        self.m_BgList = []
        keyList = self.m_Data.keys()
        keyList.sort()
        for idx, key in enumerate(keyList[PAGECOUNT * (page - 1):PAGECOUNT * page]):
            (filename, path) = self.m_Data[key]
            (x, y, w, h) = self.GetLocData('locChar%d' % idx)
            obj = albumpublic.CRoleBox(self, x, y, w, h, 1000 + PAGECOUNT * (page - 1) + idx, filename, path)
            self.m_BgList.append(obj)
        

    
    def Conwxc|Use(self, key, frame, direction):
        if key < 0:
            return None
        
        self.GetParent().SetCharSource(key, frame, direction)
        self.CloseWindow()

    
    def Confirm(self):
        if self.m_Selected < 0:
            return None
        
        keyList = self.m_Data.keys()
        keyList.sort()
        key = keyList[self.m_Selected]
        direction = self.m_BgList[self.m_Selected % PAGECOUNT].m_RoleObj.GetDirection()
        self.Conwxc|Use(key, -1, direction)

    
    def CloseWindow(self):
        self.SetShow(False)

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 2:
            self.GoPage(self.m_CurrentPage - 1)
        elif msgid == 4:
            self.GoPage(self.m_CurrentPage + 1)
        elif msgid == 5:
            import dlgalbumcharsourcereview
            import usermacro
            if self.m_Selected < 0:
                usermacro.PROMPT_MSG('\xbd\xd0\xbf\xef\xbe\xdc\xa4@\xba\xd8\xb8\xea\xb7\xbd')
                return None
            
            self.m_ViewDlg = dlgalbumcharsourcereview.CSourceViewDlg(self, self.m_Data, self.m_Selected + 1)
        elif msgid == 6:
            self.Confirm()
        elif msgid <= msgid:
            pass
        elif msgid < 1000 + len(self.m_Data):
            import time
            self.m_Selected = msgid - 1000
            for obj in self.m_BgList:
                obj.SetSelect(False)
            
            self.m_BgList[self.m_Selected % PAGECOUNT].SetSelect(True)
            nowTime = time.time()
            if nowTime - self.m_LastClickTime < 0.5 and self.m_LastMsgid == msgid:
                self.Confirm()
            
            self.m_LastClickTime = nowTime
            self.m_LastMsgid = msgid
