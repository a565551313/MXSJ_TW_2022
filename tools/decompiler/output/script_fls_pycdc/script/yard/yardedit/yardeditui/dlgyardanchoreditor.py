# pycdc 交叉复核产物 · script.fls entry 2639
# co_filename(原始)='script/yard/yardedit/yardeditui/dlgyardanchoreditor.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_2639.pyc (Python 2.5)

'''

import dlgyardanchoreditor as d
d.ShowAnchorDlg()

'''
import combdialog
import interface
import ui
import misc
g_Dlg = None
S_PATH = 'mapobject/furniture'
S_DAOBIAO = 'X:/1mxsj/client_zlp/script/data/yardtable'

def ModuleReset():
    global g_Dlg
    g_Dlg = None


def ShowAnchorDlg():
    global g_Dlg
    if g_Dlg is None:
        g_Dlg = CEditor()
    


class CEditor(combdialog.CCombDialog):
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog4/yard/editor/yardfuroffset.dlg')
        interface.Center(self)
        self.Init()
        self.SetIgnoreEsc(True)

    
    def Init(self):
        self.m_Restyp = 1
        self.m_iStepX = 1
        self.m_iStepY = 1
        self.m_SelImg = None
        self.m_Mode = 1
        self.m_MgrData = CDataMgr().GetInstance()
        self.m_MgrData.InitData()
        oTable = self.GetObject('tableview')
        self.m_sSelectPath = ''
        self.m_pTableView = oTable
        oTable.SetDelegateNumberOfCells(self.tableViewDelegateNumberOfCells)
        oTable.SetDelegateSizeOfIndex(self.tableViewDelegateSizeOfIndex)
        oTable.SetDelegateNewCellOfIndex(self.tableViewDelegateNewCellOfIndex)
        oTable.SetDelegateUpdateCellOfIndex(self.tableViewDelegateUpdateCellOfIndex)
        oTable.SetDelegateIdentifierOfIndex(self.tableViewIdentifierOfIndex)
        oTable.SetScrollStep(20)
        self.m_pTableView.SetZ(99999)
        self.m_oIgsAnchorPoint = None
        self.m_oIgsAnchorOffPoint = None
        self.ResetEditResult()
        for sUI in ('btn_save',):
            pObj = self.GetObject(sUI)
            pObj.SetZ(1000)
        

    
    def ResetEditResult(self):
        self.m_lPath = self.m_MgrData.GetAllPath(S_PATH)
        self.m_pTableView.Reload()

    
    def OnSelectCallBack(self, sPath):
        self.m_sSelectPath = sPath
        dAllCell = self.m_pTableView.GetAllCell()
        for pCell in dAllCell.values():
            bSlect = pCell.GetData() == sPath
            pCell.Select(bSlect)
        
        self.SelectImg(sPath)

    
    def IsDir(self, idx):
        oData = self.m_lPath[idx]
        if isinstance(oData, str):
            return False
        else:
            return True

    
    def tableViewDelegateNumberOfCells(self):
        return len(self.m_lPath)

    
    def tableViewDelegateSizeOfIndex(self, iIdx):
        return 50

    
    def tableViewDelegateNewCellOfIndex(self, oContainer, iIdx):
        oCell = CIgsItem(oContainer)
        oData = self.m_lPath[iIdx]
        bDir = self.IsDir(iIdx)
        oCell.SetData(oData, bDir)
        oCell.SetSelectCallBack(self.OnSelectCallBack)
        bSelect = oData == self.m_sSelectPath
        oCell.Select(bSelect, False)
        return oCell

    
    def tableViewIdentifierOfIndex(self, index):
        return 'itemigs'

    
    def tableViewDelegateUpdateCellOfIndex(self, oCell, iIdx, bReused):
        oData = self.m_lPath[iIdx]
        bIsDir = self.IsDir(iIdx)
        oCell.SetData(oData, bIsDir)
        bSelect = oData == self.m_sSelectPath
        oCell.Select(bSelect, False)

    
    def SetMode(self, mode):
        self.m_Mode = mode

    
    def OnSelRes(self):
        if self.m_lPath:
            sPath = self.m_lPath[1]
            self.OnSelectCallBack(sPath)
        

    
    def SelectImg(self, sPath):
        self.m_CurSelIdx = sPath
        self.CreateImg()

    
    def CreateImg(self):
        (x, y, w, h) = self.GetLocData('box_img')
        self.m_SelImg = interface.CImagesObject(self, self.m_sSelectPath, S_PATH)
        self.m_vOriPos = (int(x + w / 2), int(y + h / 2))
        self.m_vOriPos1 = list(self.m_vOriPos)
        (wRes, hRes) = self.m_SelImg.GetSize()
        if wRes > w:
            self.m_vOriPos1[0] = self.m_vOriPos[0] - ((wRes - w) / 2 / 20) * 20
        
        if hRes > h / 2:
            self.m_vOriPos1[1] = self.m_vOriPos[0] + ((hRes - h / 2) / 20) * 20
        
        vPos = (self.m_vOriPos1[0], self.m_vOriPos1[1])
        self.m_SelImg.SetPos(*vPos)
        self.m_oClickObj = interface.CClickBox(self, 1, 1, color = 255, alpha = 256)
        self.m_oClickObj.SetPos(*vPos)
        self.m_oIgsAnchorPoint = CBlock(self.m_SelImg, 20, 20)
        self.m_oIgsAnchorPoint.SetMode(2)
        self.m_oIgsAnchorPoint.SetPos(-10, -10)
        self.m_oIgsAnchorOffPoint = CBlock(self.m_SelImg, 10, 10)
        self.m_oIgsAnchorOffPoint.SetMode(1)
        self.m_oIgsAnchorOffPoint.SetZ(100)
        self.m_oIgsAnchorOffPoint.SetPos(0, 0)
        dValue = self.m_MgrData.GetData(self.m_sSelectPath)
        vPos = dValue.get('offpos', (0, 0))
        self.SetAnchortOffPointPos(vPos)

    
    def SetAnchortOffPointPos(self, vOffPos):
        dValue = self.m_MgrData.GetData(self.m_sSelectPath)
        dValue['offpos'] = vOffPos
        if not self.m_oIgsAnchorOffPoint:
            return None
        
        vPos = (vOffPos[0] - 5, vOffPos[1] - 5)
        self.m_oIgsAnchorOffPoint.SetPos(*vPos)

    
    def CloseWindow(self):
        global g_Dlg
        g_Dlg = None

    
    def LeftDown(self):
        if not self.m_SelImg:
            return None
        
        (iX, iY) = self.m_oClickObj.GetScreenPos()
        import cursor
        (x, y) = cursor.GetCursorPos()
        vPos = (x - iX, y - iY)
        self.SetAnchortOffPointPos(vPos)

    
    def RightUp(self):
        self.CloseWindow()

    
    def SaveData(self):
        self.m_MgrData.SaveAllData()

    
    def OnMessage(self, msgid):
        if msgid == 4:
            self.CloseWindow()
        elif msgid == 8:
            self.SaveData()
        



class CBlock(interface.CBoxObject):
    
    def __init__(self, parent, w, h, color = 0, alpha = 128):
        interface.CBoxObject.__init__(self, parent, w, h, color, alpha)
        self.m_DefaultColor = color
        self.m_Mode = 0

    
    def SetMode(self, mode):
        Mode2Color = {
            0: self.m_DefaultColor,
            1: 16711680,
            2: 65280 }
        self.m_Mode = mode
        self.SetColor(Mode2Color.get(mode, self.m_DefaultColor))

    
    def GetMode(self):
        return self.m_Mode

    
    def SetBlockPos(self, x, y):
        self.m_Pos = (x, y)



class CIgsItem(combdialog.CCombSubWnd):
    S_UIPATH = 'dialog4/yard/yardblockitem.dlg'
    
    def __init__(self, pParent):
        combdialog.CCombSubWnd.__init__(self, pParent, self.S_UIPATH)
        self.m_pClickCallBack = None
        self.m_pClickSelectCallBack = None
        self.m_oData = None
        self.m_bSelect = False
        self.\x9f\xad\x82\xb0g = None
        self.m_pHot = None
        self.m_oDirText = None
        self.m_oNameText = None
        self.Init()

    
    def Init(self):
        self.\x9f\xad\x82\xb0g = self.GetObject('img_bg')
        self.m_oDirText = self.GetObject('text_dir')
        self.m_oNameText = self.GetObject('text_name')
        self.m_pHot = self.GetObject('loc_hot')
        self.m_pHot.SetMouseWheelEnable(1)

    
    def Clear(self):
        self.m_oData = None

    
    def GetData(self):
        return self.m_oData

    
    def SetData(self, oPath, bDir):
        self.m_oData = oPath
        self.m_oDirText.SetShow(False)
        self.m_oNameText.SetShow(False)
        self.m_pHot.SetShow(False)
        if bDir:
            self.m_oDirText.SetShow(True)
            sName = oPath[0]
            self.m_oDirText.SetText(sName)
        else:
            self.m_oNameText.SetShow(True)
            self.m_pHot.SetShow(True)
            self.m_oNameText.SetText(oPath)

    
    def SetClickedSkillCallBack(self, pClickCallBack):
        self.m_pClickCallBack = None
        if pClickCallBack:
            self.m_pClickCallBack = misc.Functor(pClickCallBack)
        

    
    def SetSelectCallBack(self, pClickCallBack):
        self.m_pClickSelectCallBack = None
        if pClickCallBack:
            self.m_pClickSelectCallBack = misc.Functor(pClickCallBack)
        

    
    def Select(self, bSelect, bCallBack = True):
        if self.m_bSelect == bSelect:
            return None
        
        oImage = self.\x9f\xad\x82\xb0g.GetImage(0, 0)
        if bSelect:
            oImage.SetFrame(1)
        else:
            oImage.SetFrame(0)
        self.m_bSelect = bSelect
        if self.m_pClickSelectCallBack and bSelect and bCallBack:
            self.m_pClickSelectCallBack(self.m_oData)
        

    
    def MouseWheelUp(self, p):
        self.GetParent().MouseWheelUp(p)

    
    def MouseWheelDown(self, p):
        self.GetParent().MouseWheelDown(p)

    
    def OnMessage(self, msgID):
        if msgID == 1:
            self.Select(True)
        



class CDataMgr(object):
    
    def __init__(self):
        self.m_Data = { }

    
    def GetInstance(cls):
        if not getattr(cls, 's_Instance', None):
            cls.s_Instance = cls()
        
        return cls.s_Instance

    GetInstance = classmethod(GetInstance)
    
    def InitData(self):
        sPath = '%s/yardfur2cursoffposdata.py' % S_DAOBIAO
        fobj = open(sPath, 'r')
        sData = fobj.read()
        
        try:
            DATA = None
            exec sData
        except:
            DATA = { }

        LOG('DATA:', len(DATA))
        import copy
        if DATA != None:
            self.m_Data = copy.deepcopy(DATA)
        else:
            self.m_Data = { }

    
    def SaveAllData(self):
        titleTxt = '# coding:gbk\ndef GetFur2CursorOffPos(sPath):\n\tsPath = sPath.split("/")[-1]\n\tif sPath.find(".") == -1:\n\t\tsPath = "%s.igs" % sPath\n\tdData = DATA.get(sPath)\n\tif not dData:\n\t\treturn (0, 0)\n\treturn dData.get("offpos", (0, 0))\n#auto produce not change\xa1C\n'
        sPath = '%s/yardfur2cursoffposdata.py' % S_DAOBIAO
        fobj = open(sPath, 'wb')
        fobj.write(titleTxt)
        import tool
        txt = tool.PowerPrint('DATA', self.m_Data)
        fobj.write(txt + '\n\n')
        fobj.close()

    
    def GetData(self, sPath):
        if sPath not in self.m_Data:
            self.m_Data[sPath] = { }
        
        return self.m_Data[sPath]

    
    def GetAllPath(self, sDir):
        import os
        lPath = []
        for sheet in os.listdir(sDir):
            sSubDir = os.path.join(sDir, sheet)
            sSubDir = sSubDir.replace('\\', '/')
            if os.path.isdir(sSubDir):
                continue
                continue
            for sEnd in ('.igs',):
                if sSubDir.endswith(sEnd):
                    sSubDir = sSubDir.split('/')[-1]
                    lPath.append(sSubDir)
                    break
                    continue
            
        
        if sDir.find('landigs') == -1:
            lPath.sort()
            return lPath
        
        dType2Path = { }
        lPath.sort()
        for sPath in lPath:
            sPath = sPath.split('/')[-1]
            sType = sPath.split('_')[0]
            if sType not in dType2Path:
                dType2Path[sType] = []
            
            lResult = dType2Path[sType]
            if sPath not in lResult:
                lResult.append(sPath)
                continue
        
        lPath = []
        for sKey, lResult in dType2Path.iteritems():
            lPath.append((sKey, True))
            lPath.extend(lResult)
        
        return lPath
