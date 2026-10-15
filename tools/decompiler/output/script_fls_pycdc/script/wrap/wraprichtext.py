# pycdc 交叉复核产物 · script.fls entry 3118
# co_filename(原始)='script/wrap/wraprichtext.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3118.pyc (Python 2.5)

import interface

class WrapRichText(interface.CCutRichTextObject):
    
    def __init__(self, parent, w, fontid, txt, normalcolor = None, pReplaceColorFunc = None):
        import wrapui
        (result, _, self.m_LinkObj) = wrapui.ReplaceLink(txt)
        if pReplaceColorFunc:
            result = pReplaceColorFunc(result, self.m_LinkObj)
        
        if normalcolor == None:
            normalcolor = 0
        
        interface.CCutRichTextObject.__init__(self, parent, w, fontid, result, normalcolor)



class CScrollRichText(interface.CScrollRichText):
    
    def AddTxt(self, txt, font, color, oRichText = None, pReplaceColorFunc = None):
        if oRichText == None:
            oRichText = WrapRichText
        
        self.m_RTObj = oRichText(self, self.m_MaxW, font, txt, color, pReplaceColorFunc)
        self.m_RTH = self.m_RTObj.GetHeight()
        self.m_RTObj.SetPos(0, 0)
        self.m_FontH = interface.g_FontSize[font] + 2
        self.m_LineCount = self.m_RTH / self.m_FontH
        if self.m_RTH % self.m_FontH != 0:
            self.m_LineCount += 1
        
        self.m_PageCount = self.m_MaxH / self.m_FontH
        self.m_CheckCmd = None
        self.m_CurLinkID = -1

    
    def CheckCursor(self):
        txtobj = self.m_RTObj
        if len(txtobj.m_LinkObj) == 0:
            return None
        
        hasLink = False
        import cursor
        (x, y) = cursor.GetPos()
        (rx, ry) = txtobj.GetScreenPos()
        clickid = int(txtobj.ClickID(x - rx, y - ry))
        if clickid >= 0:
            hasLink = True
            if self.m_CurLinkID == clickid:
                return ()
            
            self.m_CurLinkID = clickid
            if txtobj.m_LinkObj.get(clickid, None):
                obj = txtobj.m_LinkObj[clickid]
                obj.OnEnter()
            
            self.OnEnterLink()
        
        if not hasLink and self.m_CurLinkID != -1:
            obj = txtobj.m_LinkObj[self.m_CurLinkID]
            obj.OnLeave()
            self.OnLeaveLink()
            self.m_CurLinkID = -1
        

    
    def OnEnterLink(self):
        import cursor
        cursor.SetLinkCursor(True)

    
    def OnLeaveLink(self):
        import cursor
        cursor.SetLinkCursor(False)

    
    def CreateCheckCmd(self):
        
        def check(obj):
            obj.CheckCursor()
            return ()

        self.ReleaseCheckCmd()
        self.m_CheckCmd = self.CreatePyCommand(2, check)

    
    def ReleaseCheckCmd(self):
        if self.m_CheckCmd:
            self.m_CheckCmd.Release()
            self.m_CheckCmd = None
        

    
    def Enter(self):
        self.CreateCheckCmd()

    
    def Leave(self):
        self.ReleaseCheckCmd()
        if self.m_CurLinkID != -1:
            self.OnLeaveLink()
            obj = self.m_RTObj.m_LinkObj[self.m_CurLinkID]
            obj.OnLeave()
            self.m_CurLinkID = -1
        

    
    def BarChange(self, pos):
        interface.CScrollRichText.BarChange(self, pos)
        parent = self.GetParent()
        if hasattr(parent, 'OnScrollBarChange'):
            parent.OnScrollBarChange(pos)
        

    
    def LeftUp(self):
        interface.CScrollRichText.LeftUp(self)
        import cursor
        (x, y) = cursor.GetPos()
        txtobj = self.m_RTObj
        del txtobj.GetScreenPos.interface
        (rx, ry) = None
        clickid = int(txtobj.ClickID(x - rx, y - ry))
        if clickid < 0:
            return None
        
        if txtobj.m_LinkObj.get(clickid, None):
            obj = txtobj.m_LinkObj[clickid]
            obj.OnLeftUp(rx, ry)
