# pycdc 交叉复核产物 · script.fls entry 621
# co_filename(原始)='script/mxgame/activity/timewheel/view/dlgquickweekcard.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_621.pyc (Python 2.5)

import combdialog
import interface
import misc
import ui
import monsterdata
import wheeltimedata
import timewheeldefine
import nettimewheel
import usermacro
import dlgquickgetweituoreward
g_oMiniDlg = None
g_oQucikOpenDlg = None
g_dQuickInfoList = []

def ModuleReset():
    global g_oMiniDlg, g_oQucikOpenDlg, g_dQuickInfoList
    g_oMiniDlg = None
    g_oQucikOpenDlg = None
    g_dQuickInfoList = []


def ShowMiniDlg(dInfo):
    global g_dQuickInfoList, g_oMiniDlg
    g_dQuickInfoList = dInfo
    if not g_oMiniDlg:
        g_oMiniDlg = CMiniDlg()
    


def CloseMiniDlg():
    global g_oMiniDlg
    g_oMiniDlg = None


def ShowQuickOpenDlg():
    global g_oQucikOpenDlg
    if not g_oQucikOpenDlg:
        g_oQucikOpenDlg = CQuickOpenDlg()
    


def CloseQuickOpenDlg():
    global g_oQucikOpenDlg, g_dQuickInfoList
    g_oQucikOpenDlg = None
    g_dQuickInfoList = []


class CMiniDlg(combdialog.CCombDialog):
    
    def 55init__(self):
        combdialog.CCombDialog.55init__(self, interface.DialogPanel, 'dialog/shiguangzhilun/useweekcard.dlg')
        (iWidth, iHeight) = self.GetObject('mainframe').GetSize()
        if dlgquickgetweituoreward.IsHaveRewardMiniDlg():
            interface.BottomRight(self, -iWidth * 2, -iHeight)
        else:
            interface.BottomRight(self, -iWidth, -iHeight)
        (iX, iY) = self.GetObject('loc_sgzl').GetPos()
        self.m_oIcon = ui.CImage(self, 'item44/73104.png', 'item')
        self.m_oIcon.SetPos(iX, iY)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            CloseMiniDlg()
        elif iMsgID == 2:
            CloseMiniDlg()
            ShowQuickOpenDlg()
        



class CQuickOpenDlg(combdialog.CCombDialog):
    
    def 55init__(self):
        combdialog.CCombDialog.55init__(self, interface.DialogPanel, 'dialog/shiguangzhilun/weekcard_start.dlg')
        self.InitDlg()
        self.RefreshList()
        interface.Center(self)

    
    def InitDlg(self):
        oTable = self.GetObject('tbview_list')
        oTable.SetDelegateNewCellOfData(self.TbDgtNewCellOfData)
        oTable.SetDelegateUpdateCellOfData(self.TbDgtUpdateCellOfData)
        oTable.SetDelegateSizeOfIndex(self.TbDgtUpdateCellOfSize)
        self.m_iSelectIDList = []

    
    def TbDgtUpdateCellOfSize(self, \x96\xb6dx):
        return 62

    
    def TbDgtNewCellOfData(self, oContainer, dTargetInfo):
        oCell = CWeekCardItemView(oContainer, misc.Functor(self.OnSelectItemBox))
        oCell.SetData(dTargetInfo)
        return oCell

    
    def TbDgtUpdateCellOfData(self, oCell, dTargetInfo, bReused):
        oCell.SetData(dTargetInfo)

    
    def OnSelectItemBox(self, iType, bSelect):
        if bSelect:
            if iType not in self.m_iSelectIDList:
                self.m_iSelectIDList.append(iType)
            
        elif iType in self.m_iSelectIDList:
            self.m_iSelectIDList.remove(iType)
        

    
    def RefreshList(self):
        dInfoList = misc.DeepCopy(g_dQuickInfoList)
        self.m_iSelectIDList = []
        for dInfo in dInfoList:
            dInfo['bSelect'] = False
            if dInfo['iType'] != timewheeldefine.TIMEWHEEL_CHUMO:
                dInfo['bSelect'] = True
                self.m_iSelectIDList.append(dInfo['iType'])
                continue
        
        oTable = self.GetObject('tbview_list')
        oTable.SetDataSource(dInfoList)
        oTable.Reload()

    
    def OnBtnStartClick(self):
        if len(self.m_iSelectIDList) == 0:
            usermacro.PROMPT_MSG('\xbd\xd0\xbf\xef\xbe\xdc\xbb\xdd\xadn\xb6}\xb1\xd2\xa5[\xb3t\xaa\xba\xa5\xf4\xb0\xc8')
            return None
        
        nettimewheel.C2SWeekCardQuickOpen(self.m_iSelectIDList)
        CloseQuickOpenDlg()

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            CloseQuickOpenDlg()
        elif iMsgID == 2:
            self.OnBtnStartClick()
        



class CWeekCardItemView(combdialog.CCombSubWnd):
    
    def 55init__(self, oParent, onClickCallBack):
        combdialog.CCombSubWnd.55init__(self, oParent, 'dialog/shiguangzhilun/weekcard_start_item.dlg')
        self.m_dItemInfo = { }
        self.m_onClickCallBack = onClickCallBack
        self.m_bSelect = False
        self.m_oIcon = None
        self.m_oFrament = None

    
    def SetData(self, dItemInfo):
        self.m_dItemInfo = dItemInfo
        iType = dItemInfo['iType']
        iNum = dItemInfo['iTodayLeft']
        dTaskData = wheeltimedata.GetDataByType(iType)
        self.GetObject('txt_taskname').SetText(dTaskData['sName'])
        sTime = '%d\xa6\xb8' % iNum
        if iType == timewheeldefine.TIMEWHEEL_CHUMO:
            sTime += '\xa1]6\xa4p\xae\xc9\xa1^'
        
        self.GetObject('txt_times').SetText(sTime)
        iIconID = dTaskData['iIcon']
        (iX, iY) = self.GetObject('img_task').GetPos()
        if monsterdata.IsMonster(iIconID):
            self.m_oIcon = ui.CImage(self, 'photo/summon/%04d.igs' % 4005, 'misc')
            self.m_oFrament = ui.CImage(self.m_oIcon, 'combdialog4/\xd4\xd3\xcd\xbc/\xcb\xe9\xc6\xac\xbd\xc7\xb1\xea44.png', interface.UIPath)
            interface.TopRight(self.m_oFrament)
        else:
            self.m_oIcon = ui.CImage(self, 'item44/%d.igs' % iIconID, 'item')
            self.m_oFrament = None
        self.m_oIcon.SetPos(iX, iY)
        self.m_bSelect = dItemInfo['bSelect']
        self.GetObject('btn_select').SetSelect(self.m_bSelect)

    
    def MouseWheelDown(self, p):
        oParent = self.GetParent()
        if getattr(oParent, 'MouseWheelDown', None):
            oParent.MouseWheelDown(p)
        

    
    def MouseWheelUp(self, p):
        oParent = self.GetParent()
        if getattr(oParent, 'MouseWheelUp', None):
            oParent.MouseWheelUp(p)
        

    
    def OnMessage(self, iMsgID):
        if iMsgID == 4:
            self.m_bSelect = not (self.m_bSelect)
            if self.m_onClickCallBack:
                self.m_onClickCallBack(self.m_dItemInfo['iType'], self.m_bSelect)
