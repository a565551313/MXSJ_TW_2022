# pycdc 交叉复核产物 · script.fls entry 956
# co_filename(原始)='script/dialog/dlgshare.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_956.pyc (Python 2.5)

import combdialog
import interface
import permission
g_ShareDlg = None
bk = None

def ModuleReset():
    global g_ShareDlg, bk
    g_ShareDlg = None
    bk = None


def Show(iShape, sName):
    global g_ShareDlg
    g_ShareDlg = CShareDlg(iShape, sName)


def ShowBiyi(iShape, sName):
    global g_ShareDlg
    g_ShareDlg = CBiyiShareDlg(iShape, sName)


def ShowSQ(iShape, sName):
    global g_ShareDlg
    g_ShareDlg = CSQShareDlg(iShape, sName)


class CShareDlg(combdialog.CCombDialog):
    DLGPATH = 'dialog2/summerlottery/summerlotterysmall.dlg'
    
    def __init__(self, iShape, sName, oParent = None):
        if oParent is None:
            oParent = interface.DialogPanel
        
        combdialog.CCombDialog.__init__(self, oParent, self.DLGPATH)
        self.SetPos(243, 173)
        self.Topmost()
        self.m_Shape = iShape
        self.m_Name = sName
        self.CreateItemUI()

    
    def CreateItemUI(self):
        if self.GetObject('box_own'):
            import combmacro
            self.m_ItemTxt = combmacro.CTEXT(interface.CTextObject, 'box_own', self, self.m_Name, interface.FontLT14_3, 16711680)
        
        box = self.GetObject('box_item')
        if box:
            import item
            self.m_ItemImg = item.CreateItem120Image(self, self.m_Shape)
            (x, y) = box.GetPos()
            self.m_ItemImg.SetPos(x + 3, y + 3)
        

    
    def ShowChoosePanel(self, bIsShow = True):
        import dlgsnapshotshare
        if bIsShow:
            textList = [
                'QQ\xaa\xc5\xb6\xa1']
            textTitle = '\xbaI\xb9\xcf\xa4\xc0\xa8\xc9\xa8\xec\xa1G'
            self.m_ChoosePanel = dlgsnapshotshare.CShareChoosePanel(interface.DialogPanel, self, textTitle, textList, interface.FontLT14_3)
            (x1, y1) = self.GetPos()
            btn = self.GetObject('share')
            (dx, dy) = btn.GetPos()
            (dw, dh) = btn.GetSize()
            self.m_ChoosePanel.SetPos(x1 + dx + dw, y1 + dy)
        else:
            self.m_ChoosePanel = None

    
    def DoSnapshotShare(self):
        global bk
        self.ShowChoosePanel(False)
        dirname = 'screen'
        import os
        import agqfyuwfo
        
        try:
            os.mkdir(dirname)
        except:
            pass

        import misc
        timetxt = '%d%02d%02d-%02d%02d%02d' % misc.LocalTime()[:6]
        fname = '%s\\%s.jpg' % (dirname, timetxt)
        bk = interface.CSnapshotBitmapObject(None, fname)
        bk.SetZ(999)
        
        def delayop(obj, fname):
            if not os.path.exists(fname):
                agqfyuwfo.PROMPT_MSG('\xbaI\xb9\xcf\xabO\xa6s\xa5\xa2\xb1\xd1, \xbd\xd0\xb5y\xab\xe1\xa6A\xb8\xd5')
                return None
            
            import httpplayershow
            import snapshotshare
            httpplayershow.UploadSnapshot(fname, snapshotshare.GetRandomDesc(), snapshotshare.GetRandomDesc(), UploadCallback)
            agqfyuwfo.NORMAL_MSG('\xa5\xbf\xa6b\xa4W\xb6\xc7\xb9\xcf\xa4\xf9\xa4\xa4, \xbd\xd0\xb5y\xad\xd4')

        self.DelayOp = self.CreatePyCommand(15, delayop, fname)

    
    def DoShareToYWQ(self):
        import mgrscreenshot
        self.ShowChoosePanel(False)
        self.m_YWQShareManage = mgrscreenshot.CShotManage()
        self.m_YWQShareManage.Show()
        owner = interface.CShadowObject(self)
        self.m_YWQShareManage.SetParent(owner)

    
    def CloseWindow(self):
        global g_ShareDlg
        g_ShareDlg = None

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.ShowChoosePanel()
        elif msgid == 2:
            self.CloseWindow()
        



class CBiyiShareDlg(CShareDlg):
    DLGPATH = 'dialog2/lottery/lotterysmall.dlg'
    
    def __init__(self, iShape, sName, oParent = None):
        CShareDlg.__init__(self, iShape, sName, oParent)
        (px, py) = self.GetParent().GetSize()
        self.SetPos((px - 318) / 2, (py - 355) / 2)

    
    def CreateItemUI(self):
        obj = self.GetObject('txt_name')
        if obj or len(self.m_Name) > 14:
            self.m_Name = self.m_Name[:4] + '\\n' + self.m_Name[4:]
        
        obj.SetText(self.m_Name)
        (x, y) = obj.GetSize()
        obj.SetPos((319 - x) / 2, (356 - y) / 2 - 65)
        box = self.GetObject('box_item')



class CSQShareDlg(CBiyiShareDlg):
    DLGPATH = 'dialog3/weaponlottery/lotterysmall.dlg'
    
    def __init__(self, iShape, sName):
        CBiyiShareDlg.__init__(self, iShape, sName, interface.CapturePanel)
        self.Capture(1, 0)

    
    def ShowChoosePanel(self, bIsShow = True):
        import dlgsnapshotshare
        if bIsShow:
            textList = [
                'QQ\xaa\xc5\xb6\xa1']
            textTitle = '\xbaI\xb9\xcf\xa4\xc0\xa8\xc9\xa8\xec\xa1G'
            self.m_ChoosePanel = dlgsnapshotshare.CShareChoosePanel(self, self, textTitle, textList, interface.FontLT14_3)
            btn = self.GetObject('share')
            (dx, dy) = btn.GetPos()
            (dw, dh) = btn.GetSize()
            self.m_ChoosePanel.SetPos(dx + dw, dy)
        else:
            self.m_ChoosePanel = None

    
    def CreateItemUI(self):
        obj = self.GetObject('txt_name')
        if obj:
            (ox, oy) = obj.GetPos()
            (ow, oh) = obj.GetSize()
            obj.SetText(self.m_Name)
            (w, h) = obj.GetSize()
            obj.SetPos(int((ow - w) / 2) + ox, int((oh - h) / 2) + oy)
        
        box = self.GetObject('box_item')
        if box:
            import item
            self.m_ItemImg = item.CreateItem120Image(self, self.m_Shape)
            (x, y) = box.GetPos()
            self.m_ItemImg.SetPos(x + 3, y + 3)
        



def UploadCallback(data, success, *args):
    import httpplayershow
    import agqfyuwfo
    resp = httpplayershow.Parse(data, success)
    if resp:
        succeed = resp.get('Succeed')
        if succeed:
            ext_data = resp.get('ext_data')
            url = ext_data.get('url')
            import net
            net.OpenUrl(url)
            agqfyuwfo.NORMAL_MSG('\xa4W\xb6\xc7\xb9\xcf\xa4\xf9\xa6\xa8\xa5\\, \xbd\xd0\xa6b\xbcu\xa5X\xaa\xba\xad\xb6\xad\xb1\xbe\xde\xa7@')
            import netcommon
            netcommon.C2SSnapshotSuccess(1)
        else:
            agqfyuwfo.PROMPT_MSG('\xa4W\xb6\xc7\xa5\xa2\xb1\xd1\xa1A\xbd\xd0\xb5y\xad\xd4\xad\xab\xb7s\xbaI\xb9\xcf\xa4\xc0\xa8\xc9')
            agqfyuwfo.NORMAL_MSG('\xa4W\xb6\xc7\xa5\xa2\xb1\xd1\xa1A\xbd\xd0\xb5y\xad\xd4\xad\xab\xb7s\xbaI\xb9\xcf\xa4\xc0\xa8\xc9')
    else:
        agqfyuwfo.PROMPT_MSG('\xba\xf4\xb5\xb8\xc1c\xa6\xa3\xa1A\xbd\xd0\xb5y\xad\xd4\xad\xab\xb7s\xbaI\xb9\xcf\xa4\xc0\xa8\xc9')
        agqfyuwfo.NORMAL_MSG('\xba\xf4\xb5\xb8\xc1c\xa6\xa3\xa1A\xbd\xd0\xb5y\xad\xd4\xad\xab\xb7s\xbaI\xb9\xcf\xa4\xc0\xa8\xc9')
