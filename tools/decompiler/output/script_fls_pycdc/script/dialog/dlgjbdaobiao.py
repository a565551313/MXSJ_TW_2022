# pycdc 交叉复核产物 · script.fls entry 3994
# co_filename(原始)='script/dialog/dlgjbdaobiao.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3994.pyc (Python 2.5)

import interface
import ui
import combdialog
import combmacro
import os
g_FindDaoBiao = None

def ModuleReset():
    global g_FindDaoBiao
    g_FindDaoBiao = None

RES_PATH = 'H:\\mx_trunk\\Tools\\daobiao1\\old\\res\\\xbf\xcd\xbb\xa7\xb6\xcb\xbe\xe7\xb1\xbe'
BAT_PATH = 'H:\\mx_trunk\\Tools\\daobiao1\\old\\\xa6\xdb\xb0\xca\xa5\xcd\xa6\xa8'
TXT_PATH = 'H:\\mx_trunk\\Tools\\daobiao1\\old\\data\\jubentxt'

class CClickRichText(interface.CClickRichText):
    
    def GetPar(self):
        par = self.GetParent()
        while par and par.GetParent() != interface.DialogPanel:
            par = par.GetParent()
        return par

    
    def LeftUp(self):
        interface.CClickRichText.LeftUp(self)
        parent = self.GetPar()
        if parent and hasattr(parent, 'OnBtnLeftUp'):
            parent.OnBtnLeftUp(self)
        



class CMyEdit(interface.CEdit):
    
    def MsgEnter(self):
        if isinstance(g_FindDaoBiao, CJubenDaobiaoDlg):
            g_FindDaoBiao.OnEditEnter()
        



class CTableItemBase(ui.CTableCheckBox):
    
    def __init__(self, parent, info, taskID):
        sItNormalPath = parent.GetTableInfo()['sItNormalPath']
        sItEnterPath = parent.GetTableInfo()['sItEnterPath']
        sItSelectPath = parent.GetTableInfo()['sItSelectPath']
        ui.CTableCheckBox.__init__(self, parent, parent.m_Items, parent.m_ItemWidth, parent.m_ItemHeight, sItNormalPath, sItEnterPath, sItSelectPath, msgid = len(parent.m_Items) + 1)
        self.InitCtrl(parent.m_Widths, parent.m_ItemHeight, info, taskID)

    
    def InitCtrl(self, widths, itemheight, info, taskID):
        self.m_Widths = widths
        self.m_Height = itemheight
        self.Refresh(info, taskID)

    
    def Refresh(self, info, taskID):
        self.m_SheetObjects = []
        ww = 2
        iLen = len(info)
        for idx, text in enumerate(info):
            itemobj = CClickRichText(self, 0, 0, self.m_Widths[idx], '#u%s' % text, 16776960, 16776960, interface.FontLT14_3, msgid = 0)
            itemobj.m_PathTxt = text
            itemobj.m_Type = idx
            itemobj.m_TaskID = taskID
            (itemw, itemh) = itemobj.GetSize()
            itemobj.SetPos(ww + (self.m_Widths[idx] - itemw) / 2, (self.m_Height - itemh) / 2)
            ww += self.m_Widths[idx] - 2
            self.m_SheetObjects.append(itemobj)
        



class CJubenDaobiaoDlg(combdialog.CCombDialog):
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/jubendaobiao.dlg')
        interface.Center(self)
        self.InitDialog()

    
    def InitDialog(self):
        self.InitPath()
        self.CreateSearchEdit()
        self.RefreshList()

    
    def InitPath(self):
        global RES_PATH, BAT_PATH, TXT_PATH
        import cfg
        res_path = cfg.GetData('jubenpath.ini', 'Path', 'RES_PATH')
        bat_path = cfg.GetData('jubenpath.ini', 'Path', 'BAT_PATH')
        txt_path = cfg.GetData('jubenpath.ini', 'Path', 'TXT_PATH')
        if res_path:
            RES_PATH = res_path
        
        if bat_path:
            BAT_PATH = bat_path
        
        if txt_path:
            TXT_PATH = txt_path
        

    
    def CreateSearchEdit(self):
        self.m_SearchEdit = combmacro.CEDIT(CMyEdit, 'search_edit', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_SearchEdit.Active(True)
        self.m_SearchEdit.SetLimit(20)

    
    def ClearTable(self):
        excelTable = self.GetObject('table')
        excelTable.Clear()
        self.RefreshTableScrollBar()

    
    def RefreshList(self, searchTxt = None):
        excelTable = self.GetObject('table')
        excelTable.Clear()
        excelLst = self.GetAllExcel()
        for excelName in excelLst:
            if searchTxt and searchTxt not in excelName:
                continue
            
            taskID = excelName[1:-4]
            itemobj = CTableItemBase(excelTable, (excelName, '\xa5\xcd\xa6\xa8py\xbe\xc9\xaa\xed\xbc\xc6\xbe\xda', '\xa5\xcd\xa6\xa8txt\xb4\xfa\xb8\xd5\xbc\xc6\xbe\xda'), taskID)
        
        self.RefreshTableScrollBar()

    
    def GetAllExcel(self):
        excelLst = os.listdir(RES_PATH)
        taskIDLst = []
        for excelName in excelLst:
            if 't' in excelName:
                taskIDLst.append(excelName)
                continue
        
        return taskIDLst

    
    def RefreshTableScrollBar(self):
        exelTable = self.GetObject('table')
        bar = exelTable.m_VScrollBar
        if hasattr(bar, 'm_Bar'):
            curPos = bar.m_Bar.m_CurPos
        else:
            curPos = 0
        exelTable.ResetItems()
        exelTable.ResetScrollBar()
        if exelTable.m_VScrollBar and curPos:
            exelTable.m_VScrollBar.SetBarPos(curPos)
        

    
    def SetFindDesc(self, desc):
        self.m_FindDesc = combmacro.CRICHTEXT(interface.CRichTextObject, 'finddesc', self, desc, interface.FontLT14_3, 16776960)

    
    def CloseWindow(self):
        global g_FindDaoBiao
        if g_FindDaoBiao:
            g_FindDaoBiao = None
        

    
    def OnSearch(self):
        searchTxt = self.m_SearchEdit.GetText()
        None(None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, self.RefreshList, searchTxt)

    
    def OnBtnLeftUp(self, clickObj):
        self.m_FindDesc = None
        if clickObj.m_Type == 0:
            path = os.path.join(RES_PATH + '\\%s' % clickObj.m_PathTxt)
            if os.path.exists(path):
                os.system(path)
                return None
            else:
                self.SetFindDesc('\xa4\xa3\xa6s\xa6b\xb8\xd3exel\xaa\xed')
        elif clickObj.m_Type == 1:
            self.OutputData(clickObj.m_TaskID, 1)
        elif clickObj.m_Type == 2:
            self.OutputData(clickObj.m_TaskID, 2)
        

    
    def OutputData(self, taskID, mode = 1):
        path = os.path.join(BAT_PATH + '\\txt\xbc@\xa5\xbb.bat')
        curpath = os.getcwd()
        self.CreateNewBat(path, taskID, mode)
        import usermacro
        usermacro.NORMAL_MSG('\xb6}\xa9l\xbe\xc9\xaa\xed')
        os.chdir(BAT_PATH)
        os.system('txt\xbc@\xa5\xbb.bat')
        os.chdir(curpath)
        usermacro.NORMAL_MSG('\xbe\xc9\xaa\xed\xa6\xa8\xa5\\')

    
    def CreateNewBat(self, path, taskID, mode):
        result = 'call patch.bat\n\r' + 'cd ..\\makeres\n\r' + 'python e2p_jubentxt.py %src1%\\\xab\xc8\xa4\xe1\xba\xdd\xbc@\xa5\xbb\\\xbc@\xa5\xbb\xb0\xd1\xbc\xc6.xls %src_res%\\%src4% %target%\\%src5%\n\r'
        result = result.replace('%src4%', 't%s.xls' % taskID)
        result = result.replace('%src_res%', RES_PATH.replace('\\', '\\\\'))
        if mode == 1:
            result = result.replace('%src5%', 'juben\\task%s.py' % taskID)
        elif mode == 2:
            result = result.replace('%target%\\%src5%', '%s\\task%s.txt' % (TXT_PATH, taskID))
        
        WriteFile(path, result)

    
    def OnOutputAllData(self, mode):
        excelLst = os.listdir(RES_PATH)
        for excelName in excelLst:
            if 't' in excelName:
                taskID = excelName[1:-4]
                self.OutputData(taskID, mode)
                continue
        

    
    def OnTextJuben(self):
        text = self.m_SearchEdit.GetText()
        lst = text.split()
        startPos = endPos = 0
        if len(lst) == 4:
            taskID = int(lst[0])
            jubenID = int(lst[1])
            startPos = int(lst[2])
            endPos = int(lst[3])
        
        if len(lst) == 3:
            taskID = int(lst[0])
            jubenID = int(lst[1])
            startPos = int(lst[2])
        elif len(lst) == 2:
            taskID = int(lst[0])
            jubenID = int(lst[1])
        
        import juben
        juben.TestJuBen(taskID, jubenID, startPos, endPos)

    
    def OnEditEnter(self):
        text = self.m_SearchEdit.GetText()
        lst = text.split()
        if len(lst) > 1:
            self.OnTextJuben()
        else:
            self.OnSearch()

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 3:
            self.OnSearch()
        elif msgid == 4:
            self.RefreshList()
        elif msgid == 5:
            self.OnOutputAllData(1)
        elif msgid == 6:
            self.OnOutputAllData(2)
        elif msgid == 7:
            self.OnTextJuben()
        



def ShowDaoBiaoDlg():
    global g_FindDaoBiao
    if not g_FindDaoBiao:
        g_FindDaoBiao = CJubenDaobiaoDlg()
    


def WriteFile(filepath, info):
    batFile = open(filepath, 'wb')
    batFile.write(info)
    batFile.close()
