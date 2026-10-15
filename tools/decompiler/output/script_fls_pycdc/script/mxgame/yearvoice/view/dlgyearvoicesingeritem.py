# pycdc 交叉复核产物 · script.fls entry 4107
# co_filename(原始)='script/mxgame/yearvoice/view/dlgyearvoicesingeritem.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4107.pyc (Python 2.5)

import combdialog
import titletableview
import misc
import cursor
import interface
import yearvoice_define

class CGoodVoiceCell(titletableview.CTitleTableCell):
    
    def __init__(self, *args):
        titletableview.CTitleTableCell.__init__(self, *args)
        self.m_oOtherPart = COtherPart(self)
        self.m_oOtherPart.SetCallBack(self.OnOtherPartClickCallBack)
        self.m_oCallBack = None
        self.m_oUniqueID = None
        interface.Center(self.m_oOtherPart)

    
    def SetCallBack(self, oCallBack):
        self.m_oCallBack = misc.Functor(oCallBack)

    
    def OnOtherPartClickCallBack(self, sEvent):
        self.m_oCallBack(self.m_oUniqueID, sEvent)

    
    def SetData(self, dData):
        self.m_oUniqueID = dData['tUniqueID']
        self.m_oOtherPart.SetData(dData)
        bSelect = dData['bSelect']
        self.RealSelect(bSelect)

    
    def RealSelect(self, bSel):
        titletableview.CTitleTableCell.Select(self, bSel)

    
    def Select(self, bSelect):
        self.RealSelect(bSelect)
        self.m_oOtherPart.Select(bSelect)

    
    def GetUniqueID(self):
        return self.m_oUniqueID

    
    def Enter(self):
        titletableview.CTitleTableCell.Enter(self)
        self.m_oOtherPart.SetEnterState(True)

    
    def Leave(self):
        titletableview.CTitleTableCell.Leave(self)
        self.m_oOtherPart.SetEnterState(False)



class COtherPart(combdialog.CCombSubWnd):
    DBaseUI2Prop = {
        'text_num': 'iRenqi',
        'text_name': 'sSongName',
        'text_time': 'iTime' }
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog4/yearvoice/othersxcd_item.dlg')
        self.m_oCallBack = None
        self.m_oPhoto = None
        self.m_dData = { }

    
    def SetCallBack(self, oCallBack):
        self.m_oCallBack = misc.Functor(oCallBack)

    
    def SetData(self, dData):
        if self.m_dData == dData:
            return None
        
        self.m_dData = dData
        self.RefreshBaseView()
        self.RefreshAvatarView()
        self.RefreshGuanZhu()
        self.RefreshBtnShowState()

    
    def Select(self, bSel):
        if self.m_dData.get('bSelect') == bSel:
            return None
        
        self.m_dData['bSelect'] = bSel
        self.RefreshBtnShowState()

    
    def RefreshBaseView(self):
        for sUIName, sProp in self.DBaseUI2Prop.iteritems():
            if sUIName == 'text_num':
                iCurValue = self.m_dData.get(sProp, 0)
                sCurValue = yearvoice_define.RevertRenqi(iCurValue)
            elif sUIName == 'text_time':
                iCurValue = self.m_dData.get(sProp, 0)
                sCurValue = yearvoice_define.RevertTime(iCurValue)
            else:
                sCurValue = self.m_dData.get(sProp, '')
            oTextObj = self.GetObject(sUIName)
            oTextObj.SetText(sCurValue)
        
        for sName in ('btn_dianzan1', 'btn_dianzan2'):
            self.SetShowObject(sName, False)
        

    
    def RefreshGuanZhu(self):
        bGuanZhu = self.m_dData.get('bAttention', False)
        self.GetObject('btn_dianzan2').SetShow(bGuanZhu)

    
    def RefreshAvatarView(self):
        sPath = self.m_dData.get('sPath', '')
        sDir = self.m_dData.get('sDir', '')
        if sPath != '':
            if sPath in yearvoice_define.DPHOTO:
                self.m_oPhoto = interface.CBitmapObject(self, sPath, interface.UIPath)
            elif sDir != '':
                self.m_oPhoto = interface.CBitmapObject(self, sPath, sDir)
            else:
                self.m_oPhoto = interface.CBitmapObject(self, sPath)
            oBox = self.GetObject('loc_check2')
            self.m_oPhoto.SetZ(1)
            self.m_oPhoto.SetPos(*oBox.GetPos())
            self.m_oPhoto.SetSize(*oBox.GetSize())
        

    
    def RefreshBtnShowState(self):
        bSelect = self.m_dData.get('bSelect', False)
        bGuanZhu = self.m_dData.get('bAttention', False)
        self.SetShowObject('img_huoyan0', bSelect)
        self.SetShowObject('img_huoyan1', not bSelect)
        if bSelect and not bGuanZhu:
            self.SetShowObject('btn_dianzan1', True)
        

    
    def SetEnterState(self, bEnter):
        (iPosX, iPosY) = cursor.GetCursorPos()
        (iRealPosX, iRealPosY) = self.GetObject('btn_dianzan1').GetScreenPos()
        bSelect = self.m_dData.get('bSelect', False)
        bGuanZhu = self.m_dData.get('bAttention', False)
        if not bSelect:
            pass
        self.SetShowObject('img_huoyan0', bEnter)
        if not bSelect:
            pass
        self.SetShowObject('img_huoyan1', not bEnter)
        if not bGuanZhu:
            if iPosX >= iRealPosX - 20 and iPosX <= iRealPosX + 20 and iPosY >= iRealPosY - 10 and iPosY <= iRealPosY + 10:
                self.SetShowObject('btn_dianzan1', True)
                self.SetShowObject('img_huoyan0', True)
                self.SetShowObject('img_huoyan1', False)
            elif not bSelect:
                pass
            self.SetShowObject('btn_dianzan1', bEnter)
        

    
    def GetTouchObj(self):
        return self.GetParent()

    
    def BnEnter(self, *args):
        self.Enter()

    
    def BnLeave(self, *args):
        self.Leave()

    
    def Enter(self):
        if self.GetTouchObj():
            self.GetTouchObj().Enter()
        

    
    def Leave(self):
        if self.GetTouchObj():
            self.GetTouchObj().Leave()
        

    
    def RightUp(self):
        super(COtherPart, self).RightUp()
        if self.GetTouchObj():
            while None:
                pass
        self.GetTouchObj()

    
    def LeftUp(self):
        super(COtherPart, self).LeftUp()
        if self.GetTouchObj():
            self.GetTouchObj().LeftUp()
        

    
    def MouseWheelUp(self, p):
        self.GetParent().MouseWheelUp(p)

    
    def MouseWheelDown(self, p):
        self.GetParent().MouseWheelDown(p)

    
    def OnMessage(self, iMsgID):
        dMsg2Event = {
            1: 'Attention',
            2: 'UnAttention' }
        if iMsgID in dMsg2Event:
            sEvent = dMsg2Event[iMsgID]
            self.m_oCallBack(sEvent)
