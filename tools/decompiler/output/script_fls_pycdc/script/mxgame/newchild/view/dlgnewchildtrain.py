# pycdc 交叉复核产物 · script.fls entry 662
# co_filename(原始)='script/mxgame/newchild/view/dlgnewchildtrain.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_662.pyc (Python 2.5)

'''
================================================================================
\xd7\xf7\xd5\xdf: jiangweichao
\tdlgnewchildtrain\xa3\xba\xd0\xc2\xd7\xd3\xc5\xae\xcf\xb5\xcd\xb3 - \xd7\xd3\xc5\xae\xc5\xe0\xd1\xf8\xbd\xe7\xc3\xe6
================================================================================
'''
import combdialog
import dgtnewchildtrain
import interface
import makeitemicon
import misc
import newchilddefine
import slot
import style
import ui

class CChildTrainDialog(combdialog.CCombSubWnd, slot.ISignalSubject):
    SS_AddPlan = 'SS_AddPlan(idx)'
    SS_DecPlan = 'SS_DecPlan(idx)'
    SS_RecommendPlan = 'SS_RecommendPlan()'
    SS_Adult = 'SS_Adult()'
    SS_UseItem = 'SS_UseItem()'
    SS_SelectItem = 'SS_SelectItem(iShape)'
    
    def __init__(self, parent, iChild):
        combdialog.CCombSubWnd.__init__(self, parent, 'dialog/newchild/childtrain.dlg')
        self.ssInit()
        self.m_ClickText = None
        self.m_UseIcon = []
        self.m_oTips = None
        self.m_oSelectBox = None
        self.m_iSelectIndex = 0
        self.InitDialog()
        self.m_oDelegate = dgtnewchildtrain.CChildTrainDelegate(self, iChild)

    
    def InitDialog(self):
        self.CreateClickText()
        self.CreateUseIcon()
        self.HideScrollBar()
        self.OnShowAdultBtn(False)

    
    def CreateClickText(self):
        (x, y, w, _) = self.GetLocData('loc_clicktext')
        self.m_ClickText = interface.CClickRichText(self, x, y, w, '#u\xb1\xc0\xaf\xf2\xa4\xe8\xae\xd7#n', interface.COLOR_4, interface.COLOR_5, interface.FontLT14_3, 11)
        self.m_ClickText.SetEnterCB(misc.Functor(self.OnClickTextEnter))
        self.m_ClickText.SetLeaveCB(misc.Functor(self.OnClickTextLeave))

    
    def OnClickTextEnter(self):
        import wrapinterface
        self.m_oTips = wrapinterface.CTextTips(self.m_ClickText, -1, '\xc2I\xc0\xbb\xab\xe1\xae\xda\xbe\xda\xa4l\xa4k\xacy\xac\xa3\xa4\xc0\xb0t\xa6X\xbeA\xaa\xba\xb9D\xa8\xe3\xa8\xcf\xa5\xce\xadp\xb9\xba', interface.FontLT14_3)

    
    def OnClickTextLeave(self):
        self.m_oTips = None

    
    def CreateUseIcon(self):
        import item
        self.m_UseIcon = []
        oFrame = self.GetObject('img_use')
        (fx, fy) = oFrame.GetPos()
        for idx in xrange(5):
            iShape = newchilddefine.IDX2ITEM[idx + 1]
            oIcon = CBackItem(self)
            (x, y) = oFrame.GetImage(0, idx).GetPos()
            oIcon.SetPos(fx + x, fy + y)
            oIcon.AddClickAddCB(self.OnAddItem)
            iItemNum = item.GetItemNum(iShape)
            if iItemNum > 0:
                oIcon.CreateBackNeedItemIcon(iShape, iOwn = iItemNum, bFreeze = False)
                oIcon.AddBackNeedItemIconLeftCB(self.OnSelectItem, iShape)
            else:
                oIcon.CreateNeedAddItemBtn(iShape, 0, 0)
                oIcon.CreateBackNeedItemIcon(iShape, iOwn = iItemNum, bFreeze = True)
                if self.m_iSelectIndex == idx + 1:
                    self.ssEmit(self.SS_SelectItem, 0)
                
            self.m_UseIcon.append(oIcon)
        

    
    def CreateSelectView(self, iShape):
        if iShape == 0:
            self.m_oSelectBox = None
            self.m_iSelectIndex = 0
        else:
            idx = newchilddefine.ITEM2IDX.get(iShape, 0)
            if idx > 0:
                (x, y) = self.m_UseIcon[idx - 1].GetPos()
                oBox = ui.CImage(self, style.GetPath('common/select.igs'), interface.UIPath)
                oBox.SetPos(x - 3, y - 3)
                oBox.SetZ(1)
                self.m_oSelectBox = oBox
                self.m_iSelectIndex = idx
            

    
    def HideScrollBar(self):
        oTable = self.GetObject('tab_plan')
        oTable.GetScrollBar().SetShow(False)
        for oText in oTable.m_TitleObjects:
            oText.SetShow(False)
        

    
    def SetProgress(self, dPlan, dUse):
        for idx in xrange(5):
            iType = idx + 1
            oProgress = self.GetObject('progress_%d' % iType)
            oText = self.GetObject('txt_plan%d' % iType)
            iPlan = dPlan[iType]
            iUse = dUse[iType]
            sUse = self.GetMyFloatString(iUse)
            oText.SetText('%s/%d' % (sUse, iPlan / 100))
            if iPlan == 0:
                iRate = 0
            else:
                iRate = int(1000 * iUse / iPlan)
            oProgress.SetRate(iRate)
        

    
    def SetZZ(self, dZZText, dZZRange):
        for idx in xrange(5):
            iType = idx + 1
            self.GetObject('txt_zz%d' % iType).SetText(dZZText[iType])
            self.GetObject('txt_low%d' % iType).SetText(str(dZZRange[iType][0]))
            self.GetObject('txt_high%d' % iType).SetText(str(dZZRange[iType][1]))
        

    
    def SetTotalUse(self, iTotalUse, iTotalPlan):
        sUse = self.GetMyFloatString(iTotalUse)
        self.GetObject('txt_plan').ReplaceText({
            '$a': sUse,
            '$b': str(iTotalPlan / 100) })
        if iTotalUse >= 5000:
            self.OnShowAdultBtn(True)
        else:
            self.OnShowAdultBtn(False)

    
    def SetTodayUse(self, iToday):
        self.GetObject('txt_today').ReplaceText({
            '$a': str(iToday),
            '$b': '5' })

    
    def GetMyFloatString(self, iNum):
        if (iNum / 100) * 100 == iNum:
            return str(iNum / 100)
        
        return '%.2f' % iNum / 100

    
    def OnIconEnter(self, oIcon):
        oIcon.ShowTips()

    
    def OnIconLeave(self, oIcon):
        oIcon.HideTips()

    
    def OnShowAdultBtn(self, bShow):
        hideList = [
            'btn_use']
        for sName in hideList:
            obj = self.GetObject(sName)
            if obj:
                pass
            obj.SetShow(not bShow)
        
        showList = [
            'btn_adult']
        for sName in showList:
            obj = self.GetObject(sName)
            if obj:
                pass
            obj.SetShow(bShow)
        

    
    def OnAddItem(self, dData):
        import mdconvenientpurchase
        import builddefine
        mdconvenientpurchase.OpenGetAccessDlg(dData[builddefine.KEY_NEED_SHAPE])

    
    def OnSelectItem(self, iShape):
        self.ssEmit(self.SS_SelectItem, iShape)

    
    def OnUseItem(self):
        self.ssEmit(self.SS_UseItem)

    
    def OnAddPlan(self, idx):
        self.ssEmit(self.SS_AddPlan, idx)

    
    def OnDecPlan(self, idx):
        self.ssEmit(self.SS_DecPlan, idx)

    
    def OnRecommendPlan(self):
        self.ssEmit(self.SS_RecommendPlan)

    
    def OnAdult(self):
        self.ssEmit(self.SS_Adult)

    
    def OnMessage(self, iMsgID):
        if iMsgID <= iMsgID:
            pass
        elif iMsgID <= 5:
            while None:
                pass
        self.OnAddPlan
        if iMsgID <= iMsgID:
            pass
        elif iMsgID <= 10:
            self.OnDecPlan(iMsgID - 5)
        elif iMsgID == 11:
            self.OnRecommendPlan()
        elif iMsgID == 12:
            self.OnAdult()
        elif iMsgID == 13:
            self.OnUseItem()
        



class CBackItem(makeitemicon.CBackItem):
    
    def CreateBackNeedItemIcon(self, iShape, iOwn = 0, iNeed = 1, bFreeze = True, iLv = 0):
        '''
\t\t\xb3\xd0\xab\xd8\xa4@\xad\xd3\xa4\xa3\xa5i\xc2I\xc0\xbb\xaa\xba\xaa\xab\xab~
\t\t'''
        self.m_oNeedFirstItemIcon = makeitemicon.CNeedItemIcon(self, iShape, 999, iUIStyle = self.m_iUIStyle)
        self.m_oNeedFirstItemIcon.SetLv(iLv)
        interface.Center(self.m_oNeedFirstItemIcon)
        self.m_oNeedFirstItemIcon.SetFreeze(bFreeze)
        self.m_oNeedFirstItemIcon.SetOwnTxt(iOwn)

    
    def AddBackNeedItemIconLeftCB(self, oFunc, *args):
        if self.m_oNeedFirstItemIcon:
            self.m_oNeedFirstItemIcon.SetLeftUpCB(oFunc, *args)
