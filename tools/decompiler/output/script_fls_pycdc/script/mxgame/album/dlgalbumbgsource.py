# pycdc 交叉复核产物 · script.fls entry 2025
# co_filename(原始)='script/mxgame/album/dlgalbumbgsource.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2025.pyc (Python 2.5)

import interface
import combmacro
import combdialog
import ui
import wrapinterface
import albumpublic
import albumdata
PAGECOUNT = 9

class CSourceDlg(combdialog.CCombDialog):
    
    def __init__(self, parent, itype):
        combdialog.CCombDialog.__init__(self, parent, 'dialog/album/bgsource.dlg')
        interface.Center(self)
        self.m_LastClickTime = 0
        self.m_LastMsgid = 0
        self.InitSource(itype)

    
    def InitPageInfo(self):
        self.m_PageCount = (len(self.m_Data) + PAGECOUNT - 1) / PAGECOUNT
        self.m_PageCountObj = combmacro.CTEXT(interface.CTextObject, 'locPageCount', self, str(self.m_PageCount), interface.FontLT14_3, 16777215, align = interface.ALIGN_LEFT | interface.ALIGN_MIDDLE)
        self.m_PageEdit = combmacro.CEDIT(wrapinterface.CNumberEditEx, 'locPage', self, 16777215, interface.FontLT14_3)

    
    def InitSource(self, itype):
        self.m_DataType = itype
        self.m_Data = albumdata.GetData(itype)
        if itype == albumpublic.SOURCE_CHAT:
            self.m_Data[0] = None
        
        self.InitPageInfo()
        self.GoPage(1)

    
    def OnEditChange(self, edit):
        if edit == self.m_PageEdit:
            if edit.GetNumber() > self.m_PageCount:
                edit.SetText(str(self.m_PageCount))
            
        

    
    def GoPage(self, page):
        if page <= 0 or page > self.m_PageCount:
            return None
        
        import albumpublic
        self.m_Selected = -1
        self.m_CurrentPage = page
        self.m_CurrentPageObj = combmacro.CTEXT(interface.CTextObject, 'locCurrentPage', self, str(page), interface.FontLT14_3, 16777215, align = interface.ALIGN_LEFT | interface.ALIGN_MIDDLE)
        self.GetObject('btnPrePage').Enable(page > 1)
        self.GetObject('btnNextPage').Enable(page < self.m_PageCount)
        self.m_BgList = []
        keyList = self.m_Data.keys()
        keyList.sort()
        for idx, key in enumerate(keyList[PAGECOUNT * (page - 1):PAGECOUNT * page]):
            value = self.m_Data[key]
            (smallLocw, smallLoch) = self.GetObject('locBg%d' % idx).GetSize()
            (bigLocw, bigLoch) = self.GetObject('locBigBg%d' % idx).GetSize()
            (x, y, wBg, hBg) = self.GetLocData('locBg%d' % idx)
            if not value:
                self.m_BgList.append(albumpublic.CSourceObj(self, x, y, wBg, hBg, 1000 + (page - 1) * PAGECOUNT + idx, 1, 1, '\xc2I\xc0\xbb\xa5i\xb2K\xa5[\xa4\xe5\xa6r', None))
                continue
            
            fileName = value[0]
            path = value[1]
            if fileName.endswith('.igs'):
                (w, h) = ui.CImage(None, fileName, path).GetSize()
            else:
                (w, h) = interface.CSpriteObject(None, fileName, path).GetResSize()
            normalScale = min(smallLocw * 1 / w, smallLoch * 1 / h)
            stretchScale = min(bigLocw * 1 / w, bigLoch * 1 / h)
            self.m_BgList.append(albumpublic.CSourceObj(self, x, y, wBg, hBg, 1000 + (page - 1) * PAGECOUNT + idx, normalScale, stretchScale, fileName, path))
        

    
    def ShowTextDlg(self):
        self.GetParent().ShowTextDlg()

    
    def ConfirmUse(self, idx):
        if idx == -1:
            return None
        
        if self.m_DataType == albumpublic.SOURCE_CHAT and self.m_CurrentPage == 1 and idx == 0:
            self.ShowTextDlg()
            return None
        
        keyList = self.m_Data.keys()
        keyList.sort()
        key = keyList[idx]
        parent = self.GetParent()
        if self.m_DataType == albumpublic.SOURCE_BG:
            (filename, path) = self.m_Data[key]
            parent.SetBg(filename, path)
        elif self.m_DataType == albumpublic.SOURCE_BIANKUANG:
            parent.SetBianKuang(key)
        elif self.m_DataType == albumpublic.SOURCE_STATICDEC:
            parent.SetStaticSource(key)
        elif self.m_DataType == albumpublic.SOURCE_DYNATICDEC:
            parent.SetDySource(key)
        elif self.m_DataType == albumpublic.SOURCE_CHAT:
            parent.SetChatSource(key)
        
        self.CloseWindow()

    
    def ViewSource(self, key = -1):
        import usermacro
        if key != -1:
            self.m_Selected = key
        
        if (self.m_Selected == -1 or self.m_DataType == albumpublic.SOURCE_CHAT) and self.m_Selected == 0:
            usermacro.PROMPT_MSG('\xbd\xd0\xbf\xef\xbe\xdc\xa4@\xba\xd8\xb8\xea\xb7\xbd')
            return None
        
        import dlgalbumbgsourcereview
        import dlgalbumpicsourcereview
        self.m_ViewSourceDlg = None
        if self.m_DataType in (albumpublic.SOURCE_BG, albumpublic.SOURCE_BIANKUANG):
            self.m_ViewSourceDlg = dlgalbumbgsourcereview.CBgSourceViewDlg(self, self.m_DataType, self.m_Selected + 1)
        elif self.m_DataType in (albumpublic.SOURCE_STATICDEC, albumpublic.SOURCE_DYNATICDEC, albumpublic.SOURCE_CHAT):
            self.m_ViewSourceDlg = dlgalbumpicsourcereview.CSourceViewDlg(self, self.m_DataType, self.m_Selected + 1)
        

    
    def CloseWindow(self):
        self.SetShow(False)

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 2:
            self.GoPage(self.m_PageEdit.GetNumber())
        elif msgid == 3:
            self.GoPage(self.m_CurrentPage - 1)
        elif msgid == 4:
            self.GoPage(self.m_CurrentPage + 1)
        elif msgid == 5:
            self.ViewSource()
        elif msgid == 6:
            self.ConfirmUse(self.m_Selected)
        elif msgid <= msgid:
            del self.m_Data.GoPage
        elif msgid < 1000 + len:
            import time
            self.m_Selected = msgid - 1000
            for obj in self.m_BgList:
                obj.SetSelect(False)
            
            self.m_BgList[self.m_Selected % PAGECOUNT].SetSelect(True)
            nowTime = time.time()
            if nowTime - self.m_LastClickTime < 0.5 and self.m_LastMsgid == msgid:
                self.ConfirmUse(self.m_Selected)
            
            self.m_LastClickTime = nowTime
            self.m_LastMsgid = msgid
