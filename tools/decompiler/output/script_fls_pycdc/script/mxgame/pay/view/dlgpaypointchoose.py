# pycdc 交叉复核产物 · script.fls entry 2141
# co_filename(原始)='script/mxgame/pay/view/dlgpaypointchoose.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2141.pyc (Python 2.5)

import paydefines
import combdialog
import paywidget
import paydata

class CPointChooseBase(object):
    
    def __init__(self, oPointChangeCB = None):
        self.m_PointChangeCB = oPointChangeCB
        self.m_iLastPoint = None

    
    def SetActive(self, bActive):
        if bActive:
            if self.m_iLastPoint is None:
                self.SetDefaultPoint()
            else:
                self.OnPointChange(self.m_iLastPoint)
        

    
    def SetBuyType(self, iBuyType):
        pass

    
    def SetDefaultPoint(self):
        pass

    
    def OnPointChange(self, iPoint):
        self.m_iLastPoint = iPoint
        if self.m_PointChangeCB:
            self.m_PointChangeCB(iPoint)
        



class CCardPointDialog(combdialog.CCombSubWnd, CPointChooseBase):
    '''
\t\xc1\xca\xb6R\xb1H\xb0\xe2\xa5d\xae\xc9\xaa\xba\xc2I\xbc\xc6\xbf\xef\xbe\xdc
\t'''
    
    def __init__(self, oParent, oPointChangeCB = None):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/pay/pay_xz_jsk.dlg')
        CPointChooseBase.__init__(self, oPointChangeCB)
        oParent.ssConnect(oParent.SS_DialogLeftUp, self.OnLeftUp)
        self.m_Editor = None
        self.UpdateRmb()

    
    def SetActive(self, bActive):
        CPointChooseBase.SetActive(self, bActive)
        self.SetShow(bActive)
        if not bActive:
            self.OnLeftUp()
        

    
    def SetDefaultPoint(self):
        self.OnMessage(1)

    
    def OnLeftUp(self):
        if self.m_Editor and self.m_Editor.IsEditing():
            self.EndPointEdit()
            iNum = self.m_Editor.GetNum()
            if iNum > 0:
                self.OnPointChange(self.m_Editor.GetNum() * paydefines.MINIAMOUNT_CARD)
            else:
                self.SetDefaultPoint()
            self.UpdateRmb()
        

    
    def ShowSelArea(self, iIndex):
        if iIndex == 5:
            self.GetObject('img_pay_uninput').SetShow(False)
            self.GetObject('img_pay_input').SetShow(True)
        else:
            self.GetObject('img_pay_uninput').SetShow(True)
            self.GetObject('img_pay_input').SetShow(False)
        for idx in range(1, 5):
            if idx == iIndex:
                self.GetObject('img_num%s_select' % iIndex).SetShow(True)
                self.GetObject('img_num%s_unselect' % iIndex).SetShow(False)
                continue
            self.GetObject('img_num%s_select' % idx).SetShow(False)
            self.GetObject('img_num%s_unselect' % idx).SetShow(True)
        

    
    def StartPointEdit(self):
        import misc
        if not self.m_Editor:
            self.m_Editor = paywidget.CPointEdit(self, 'txt_editnotice', self.GetObject('txt_editnotice'))
            self.m_Editor.SetMaxNum(paydefines.MAX_CARD)
            self.m_Editor.SetMsgEnterCB(self.OnLeftUp)
            self.m_Editor.SetCharChangeCB(misc.Functor(self.OnCharChange))
        
        self.m_Editor.StartEdit()
        self.ShowSelArea(5)

    
    def EndPointEdit(self):
        if self.m_Editor:
            self.m_Editor.EndEdit()
        

    
    def OnCharChange(self):
        if self.m_Editor and self.m_Editor.IsEditing():
            iNum = self.m_Editor.GetNum()
            if iNum > 0:
                self.OnPointChange(iNum * paydefines.MINIAMOUNT_CARD)
            
            self.UpdateRmb()
        

    
    def UpdateRmb(self):
        if self.m_Editor:
            iNum = self.m_Editor.GetNum()
        else:
            iNum = 0
        self.GetObject('txt_rmb').ReplaceText({
            '$money': str(iNum * paydefines.MINIAMOUNT_CARD / 10) })
        iDiscount = paydata.GetChargeOffer(iNum * paydefines.MINIAMOUNT_CARD)
        self.GetObject('img_discount').SetShow(iDiscount < 1)
        self.GetObject('txt_discount').SetShow(iDiscount < 1)
        self.GetObject('txt_discount').ReplaceText({
            '$des': str(int(iDiscount * 100)) })
        self.GetObject('text_price5').ReplaceText({
            '$total': str(1 * int(iNum) * 15 * int(iDiscount * 100) / 100) })

    
    def OnMessage(self, iMsgID):
        dPointMap = {
            1: 150,
            2: 300,
            3: 1500,
            4: 3000 }
        if iMsgID in dPointMap:
            self.OnPointChange(dPointMap[iMsgID])
            self.ShowSelArea(iMsgID)
            self.EndPointEdit()
        
        if iMsgID == 5:
            self.StartPointEdit()
        



class CGoldPointDialog(combdialog.CCombSubWnd, CPointChooseBase):
    '''
\t\xc1\xca\xb6R\xa5@\xb0^\xae\xc9\xaa\xba\xc2I\xbc\xc6\xbf\xef\xbe\xdc
\t'''
    POINT_MAP = {
        1: 50,
        2: 300,
        3: 1500,
        4: 3000 }
    
    def __init__(self, oParent, oPointChangeCB = None):
        '''
\t\t:param CPayMainDialog oParent:
\t\t'''
        import mdpay
        if not mdpay.Is50Limit():
            self.POINT_MAP = {
                1: 150,
                2: 300,
                3: 1500,
                4: 3000 }
            combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/pay/pay_xz_sg_150.dlg')
        else:
            combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/pay/pay_xz_sg.dlg')
        CPointChooseBase.__init__(self, oPointChangeCB)
        oParent.ssConnect(oParent.SS_DialogLeftUp, self.OnLeftUp)
        self.m_Editor = None
        self.UpdateRmb()

    
    def SetActive(self, bActive):
        CPointChooseBase.SetActive(self, bActive)
        self.SetShow(bActive)
        if not bActive:
            self.OnLeftUp()
        

    
    def SetDefaultPoint(self):
        self.OnMessage(1)

    
    def OnLeftUp(self):
        if self.m_Editor and self.m_Editor.IsEditing():
            self.EndPointEdit()
            iNum = self.m_Editor.GetNum()
            if iNum > 0:
                self.OnPointChange(self.m_Editor.GetNum())
            else:
                self.SetDefaultPoint()
            self.UpdateRmb()
        

    
    def ShowSelArea(self, iIndex):
        if iIndex == 5:
            self.GetObject('img_pay_uninput').SetShow(False)
            self.GetObject('img_pay_input').SetShow(True)
        else:
            self.GetObject('img_pay_uninput').SetShow(True)
            self.GetObject('img_pay_input').SetShow(False)
        for idx in range(1, 5):
            if idx == iIndex:
                self.GetObject('img_num%s_select' % iIndex).SetShow(True)
                self.GetObject('img_num%s_unselect' % iIndex).SetShow(False)
                continue
            self.GetObject('img_num%s_select' % idx).SetShow(False)
            self.GetObject('img_num%s_unselect' % idx).SetShow(True)
        

    
    def StartPointEdit(self):
        import misc
        import mdpay
        if not self.m_Editor:
            self.m_Editor = paywidget.CPointEdit(self, 'txt_editnotice', self.GetObject('txt_editnotice'))
            if mdpay.Is50Limit():
                self.m_Editor.SetMiniNum(paydefines.MINIAMOUNT_GOLD)
            else:
                self.m_Editor.SetMiniNum(150)
            self.m_Editor.SetMaxNum(paydefines.MAX_GOLD)
            self.m_Editor.SetMsgEnterCB(self.OnLeftUp)
            self.m_Editor.SetCharChangeCB(misc.Functor(self.OnCharChange))
        
        self.m_Editor.StartEdit()
        self.ShowSelArea(5)

    
    def EndPointEdit(self):
        if self.m_Editor:
            self.m_Editor.EndEdit()
        

    
    def OnCharChange(self):
        import mdpay
        if self.m_Editor and self.m_Editor.IsEditing():
            iNum = self.m_Editor.GetNum()
            if mdpay.Is50Limit():
                if iNum % paydefines.MINIAMOUNT_GOLD == 0 and iNum / paydefines.MINIAMOUNT_GOLD > 0:
                    self.OnPointChange(iNum)
                
            elif iNum % 150 == 0 and iNum / 150 > 0:
                self.OnPointChange(iNum)
            
        
        self.UpdateRmb()

    
    def UpdateRmb(self):
        if self.m_Editor:
            iNum = self.m_Editor.GetNum()
        else:
            iNum = 0
        self.GetObject('txt_rmb').ReplaceText({
            '$money': str(iNum / 10) })
        iDiscount = paydata.GetChargeOffer(iNum)
        self.GetObject('img_discount').SetShow(iDiscount < 1)
        self.GetObject('txt_discount').SetShow(iDiscount < 1)
        self.GetObject('txt_discount').ReplaceText({
            '$des': str(int(iDiscount * 100)) })
        self.GetObject('text_price5').ReplaceText({
            '$total': str(1 * int(iNum / 10) * int(iDiscount * 100) / 100) })

    
    def OnMessage(self, iMsgID):
        if iMsgID in self.POINT_MAP:
            self.OnPointChange(self.POINT_MAP[iMsgID])
            self.ShowSelArea(iMsgID)
            self.EndPointEdit()
        
        if iMsgID == 5:
            self.StartPointEdit()
        



class CMobilePointDialog(combdialog.CCombSubWnd, CPointChooseBase):
    '''
\t\xa4\xe2\xbe\xf7\xa5d\xa4\xe4\xa5I\xae\xc9\xaa\xba\xafS\xae\xed\xc2I\xbc\xc6\xbf\xef\xbe\xdc
\t'''
    
    def __init__(self, oParent, oPointChangeCB = None):
        while None:
            CPointChooseBase.__init__(self, oPointChangeCB)
            return None

    
    def SetActive(self, bActive):
        CPointChooseBase.SetActive(self, bActive)
        self.SetShow(bActive)

    
    def SetBuyType(self, iBuyType):
        dMap = {
            paydefines.BUYTYPE_MOBILE_CARD: ('txt_carddes1', 'txt_carddes2'),
            paydefines.BUYTYPE_MOBILE_GOLD: ('txt_golddes1', 'txt_golddes2') }
        for iEachType, tObjNames in dMap.iteritems():
            if iEachType == iBuyType:
                bShow = True
            else:
                bShow = False
            for sName in tObjNames:
                self.GetObject(sName).SetShow(bShow)
            
        

    
    def SetDefaultPoint(self):
        self.OnMessage(1)

    
    def ShowSelArea(self, iIndex):
        for idx in range(1, 3):
            if idx == iIndex:
                self.GetObject('img_num%s_select' % iIndex).SetShow(True)
                self.GetObject('img_num%s_unselect' % iIndex).SetShow(False)
                continue
            self.GetObject('img_num%s_select' % idx).SetShow(False)
            self.GetObject('img_num%s_unselect' % idx).SetShow(True)
        

    
    def OnMessage(self, iMsgID):
        dPointMap = {
            1: 500,
            2: 1000 }
        if iMsgID in dPointMap:
            self.OnPointChange(dPointMap[iMsgID])
            self.ShowSelArea(iMsgID)
