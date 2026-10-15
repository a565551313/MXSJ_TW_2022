# pycdc 交叉复核产物 · script.fls entry 3641
# co_filename(原始)='script/mxgame/newguide/subdailog/dlgcollectequip.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3641.pyc (Python 2.5)

import combdialog
import slot
import interface
import makeitemicon
import timer
import misc
import action
import math
EQUIP_NAME_LIST = [
    'wuqi',
    'toukui',
    'yifu',
    'xianglian',
    'yaodai',
    'jiezhi',
    'huwan',
    'xiezi']
BASE_ACTION_FRAME = 30
MOVE_SPEED_STANRD = BASE_ACTION_FRAME * 0.8 / 450
g_CollectEquipDialog = None

def ModuleReset():
    global g_CollectEquipDialog
    g_CollectEquipDialog = None


def ShowByAni():
    Show(False)
    g_CollectEquipDialog.ShowByAni()


def Show(flag):
    global g_CollectEquipDialog
    if g_CollectEquipDialog is None:
        g_CollectEquipDialog = CCollectEquipDailog()
    
    g_CollectEquipDialog.SetShow(flag)
    g_CollectEquipDialog.Topmost()


class CCollectEquipDailog(combdialog.CCombDialog, slot.ISignalSubject):
    SS_OPENEQUIPBYINDEX = 'OnOpenEquipByIndex()'
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog4/guide/zhuangbeishouji.dlg')
        self.m_iCurCompeleteId = -1
        self.m_iCurEquipId = -1
        self.m_oDelayShowTimeHandler = None
        self.m_oDelayCloseTimeHandler = None
        self.m_oImgFlyEquipIcon = None
        self.m_oCurSelEquipBg = None
        self.m_oStretchObj = None
        self.m_bIsSetShow = False
        self.ssInit()
        self.InitDelegate()
        self.InitUI()

    
    def InitDelegate(self):
        import dgtcollectequip
        self.m_lstDelegate = [
            dgtcollectequip.CCollectEquipDelegate(self)]

    
    def ShowByAni(self):
        self.m_bIsSetShow = False
        self.ssEmit(self.SS_OPENEQUIPBYINDEX)

    
    def SetDlgPos(self):
        import ratio
        x = ratio.WINDOW_WIDTH - self.GetSize()[0]
        x /= 2
        y = ratio.WINDOW_HEIGHT - self.GetSize()[1]
        y /= 2
        self.SetPos(x, y)

    
    def InitUI(self):
        self.m_oEquipBgList = []
        self.m_oLocEquipList = []
        self.m_oImgEquipList = []
        self.m_oEquipList = []
        self.m_oEquipSelList = []
        self.m_oNeedSetAlphaList = []
        self.SetDlgPos()
        for idx in range(8):
            oImgEquipBg = self.GetObject('img_equip_%s' % EQUIP_NAME_LIST[idx])
            oImgEquipBg.SetShow(False)
            oLocEquip = self.GetObject('loc_%s' % EQUIP_NAME_LIST[idx])
            oImgEquip = self.GetObject('img_%s' % EQUIP_NAME_LIST[idx])
            oImgIconBg1 = self.GetObject('img_equipbg_%s' % EQUIP_NAME_LIST[idx])
            oImgIconBg2 = self.GetObject('img_equipbg_%s_1' % EQUIP_NAME_LIST[idx])
            oImgIconBg2.SetShow(False)
            self.m_oEquipBgList.append(oImgEquipBg)
            self.m_oLocEquipList.append(oLocEquip)
            self.m_oImgEquipList.append(oImgEquip)
            self.m_oEquipSelList.append(oImgIconBg2)
            self.m_oNeedSetAlphaList.append(oImgEquip)
            self.m_oNeedSetAlphaList.append(oImgIconBg1)
            self.m_oNeedSetAlphaList.append(oImgIconBg2)
        
        self.m_oImgBgDown = self.GetObject('img_bgdown')
        self.m_oNeedSetAlphaList.append(self.m_oImgBgDown)
        self.m_oNeedSetAlphaList.append(self.GetObject('img_bgtop'))

    
    def UpdateUI(self, dDataList = None):
        if self.m_oDelayCloseTimeHandler:
            self.m_oDelayCloseTimeHandler.Release()
            self.m_oDelayCloseTimeHandler = None
        
        self.m_oEquipList = []
        if not dDataList:
            pass
        dDataList = []
        self.SetComVisible(True)
        iLenData = len(dDataList)
        for idx, oLocEquip in enumerate(self.m_oLocEquipList):
            if idx < iLenData:
                dData = dDataList[idx]
                oEquip = None
                if dData['iItemId'] > 0:
                    oEquip = makeitemicon.CNeedItemIcon(oLocEquip, dData['iItemId'], 1000 + idx)
                    oEquip.DelNeedTxt()
                    oEquip.SetFreeze(False)
                    self.m_oImgEquipList[idx].SetShow(False)
                    self.m_oEquipSelList[idx].SetShow(True)
                else:
                    self.m_oImgEquipList[idx].SetShow(True)
                    self.m_oEquipSelList[idx].SetShow(False)
                None(None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, self.m_oEquipList.append, oEquip)
            
            self.m_oEquipBgList[idx].SetShow(False)
        

    
    def CloseWindow(self):
        self.m_oImgFlyEquipIcon = None
        self.m_oStretchObj = None
        g_CollectEquipDialog.SetShow(False)

    
    def ScaleBgAni(self):
        self.SetComVisible(False)
        self.m_oStretchObj = interface.CStretchImagesObject(self, 'combdialog4/\xd4\xd3\xcd\xbc/\xce\xd2\xd2\xaa\xb1\xe4\xc7\xbf/bg.igs', 'interface')
        self.m_oStretchObj.SetPos(*self.m_oImgBgDown.GetPos())
        oActionScale = action.CScaleTo(BASE_ACTION_FRAME * 0.3, 1, 0.1, self.MoveToMengxinComplete)
        action.AddAction(self.m_oStretchObj, oActionScale)

    
    def SetComVisible(self, bShow):
        for oCom in self.m_oNeedSetAlphaList:
            if hasattr(oCom, 'SetShow'):
                oCom.SetShow(bShow)
                continue
        
        for oCom in self.m_oEquipBgList:
            if hasattr(oCom, 'SetShow'):
                oCom.SetShow(bShow)
                continue
        
        for oCom in self.m_oEquipSelList:
            if hasattr(oCom, 'SetShow'):
                oCom.SetShow(bShow)
                continue
        
        for oCom in self.m_oEquipList:
            if hasattr(oCom, 'SetShow'):
                oCom.SetShow(bShow)
                continue
        
        self.GetObject('text_times').SetShow(bShow)
        self.GetObject('text_time3').SetShow(bShow)

    
    def OnDelayShowFunc(self, idx):
        if self.m_oEquipList[idx - 1] and hasattr(self.m_oEquipList[idx - 1], 'SetShow'):
            self.m_oEquipList[idx - 1].SetShow(True)
        
        self.m_oEquipBgList[idx - 1].SetShow(True)
        self.m_oEquipSelList[idx - 1].SetShow(True)
        self.m_oImgEquipList[idx - 1].SetShow(False)

    
    def SetAlpha(self, iAlpha):
        if not self.m_bIsSetShow:
            self.m_bIsSetShow = True
            self.SetShow(True)
        
        for oCom in self.m_oNeedSetAlphaList:
            if hasattr(oCom, 'SetAlpha'):
                oCom.SetAlpha(iAlpha)
                continue
            LOG_DEBUG('\xb8\xd3\xb1\xb1\xa5\xf3\xa8S\xa6\xb3\xb3]\xb8malpha\xaa\xba\xa8\xe7\xbc\xc6', oCom)
        

    
    def StopAllActions(self):
        action.RemoveTargetAction(self)
        if self.m_oImgFlyEquipIcon:
            action.RemoveTargetAction(self.m_oImgFlyEquipIcon)
        
        if self.m_oCurSelEquipBg:
            action.RemoveTargetAction(self.m_oCurSelEquipBg)
        
        if self.m_oStretchObj:
            action.RemoveTargetAction(self.m_oStretchObj)
            self.m_oStretchObj = None
        

    
    def MoveToComplete(self, oAction = None):
        self.m_oImgFlyEquipIcon.SetShow(False)
        self.m_oCurSelEquipItem.SetShow(True)
        self.m_oCurSelEquipBg.SetAlpha(0)
        self.m_oCurSelEquipBg.SetShow(True)
        oActionFade = action.CAlphaChange(BASE_ACTION_FRAME * 0.45, 0, 255)
        action.AddAction(self.m_oCurSelEquipBg, oActionFade)
        self.m_oDelayCloseTimeHandler = timer.Timer(0.6, misc.Functor(self.ScaleBgAni), 0, self)

    
    def MoveToMengxinComplete(self, oAction):
        self.CloseWindow()

    
    def ConvertWorldToNodeSpace(self, x, y):
        (iWorldX, iWorldY) = self.GetScreenPos()
        return (x - iWorldX, y - iWorldY)

    
    def GetSpeedFrame(self, iIconPosX, iIconPosY, iEndPosX, iEndPosY):
        fCurDis = math.sqrt((iEndPosX - iIconPosX) ** 2 + (iEndPosY - iIconPosY) ** 2)
        return MOVE_SPEED_STANRD * fCurDis

    
    def OpenEquipByIndex(self, idx, iEquipId, iPosX, iPosY):
        self.m_iCurCompeleteId = idx
        self.m_iCurEquipId = iEquipId
        if idx > len(self.m_oLocEquipList):
            return None
        
        oEquip = makeitemicon.CNeedItemIcon(self.m_oLocEquipList[idx - 1], iEquipId, 1000 + idx - 1)
        oEquip.DelNeedTxt()
        oEquip.SetFreeze(False)
        self.m_oEquipList[idx - 1] = oEquip
        if hasattr(self.m_oEquipList[idx - 1], 'SetShow'):
            self.m_oEquipList[idx - 1].SetShow(False)
        
        if hasattr(self.m_oEquipSelList[idx - 1], 'SetShow'):
            self.m_oEquipSelList[idx - 1].SetShow(True)
        
        self.StopAllActions()
        oActionFade = action.CAlphaChange(BASE_ACTION_FRAME * 0.45, 0, 255)
        action.AddAction(self, oActionFade)
        self.m_oImgFlyEquipIcon = makeitemicon.CNeedItemIcon(self, iEquipId, 2000)
        self.m_oImgFlyEquipIcon.DelNeedTxt()
        self.m_oImgFlyEquipIcon.SetFreeze(False)
        self.m_oImgFlyEquipIcon.HideTips()
        self.m_oImgFlyEquipIcon.SetZ(1)
        (iIconPosX, iIconPosY) = self.ConvertWorldToNodeSpace(iPosX, iPosY)
        self.m_oImgFlyEquipIcon.SetPos(iIconPosX, iIconPosY)
        (iEndPosX, iEndPosY) = self.m_oLocEquipList[idx - 1].GetPos()
        fFrame = self.GetSpeedFrame(iIconPosX, iIconPosY, iEndPosX, iEndPosY)
        oActionFly = action.CMoveTo(fFrame, iEndPosX, iEndPosY, self.MoveToComplete)
        action.AddAction(self.m_oImgFlyEquipIcon, oActionFly)
        self.m_oCurSelEquipBg = self.m_oEquipBgList[idx - 1]
        self.m_oCurSelEquipItem = self.m_oEquipList[idx - 1]
        self.m_oImgEquipList[idx - 1].SetShow(False)
