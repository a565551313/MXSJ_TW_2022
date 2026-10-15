# pycdc 交叉复核产物 · script.fls entry 1154
# co_filename(原始)='script/mxgame/consignmentsalecenter/view/dlgconsignmallguildequip.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1154.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2019/12/19 17:22
\xd7\xf7\xd5\xdf: hzq
\xce\xc4\xbc\xfe: dlgconsignmallguildequip
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import combdialog
import c	nsignmalldefines
import consignmallwidget
import dlggetinfo
import interface
import misc
import slot
import \xbe\xa3\xa7\xafr
import tipsclosemgr
import wrapinterface
import wrapui
g_oEquipSkillTips = None

class CConsignmallGuildEquipDialog(combdialog.CCombSubWnd, slot.ISignalSubject):
    SS_Active = 'SS_Active'
    SS_ClickSort = 'OnSort(idx)'
    SS_ClickItem = 'OnItem(idx)'
    SS_ClickPage = 'OnPage(iOffset)'
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/salecenter/trade_equip.dlg')
        self.ssInit()
        self.m_bActive = None
        self.m_DelegateList = []
        self.InitDelegate()

    
    def InitDelegate(self):
        self.m_DelegateList = []
        import dgtconsignmallguildequip
        self.m_DelegateList.append(dgtconsignmallguildequip.CConsignmallGuildEquipDelegate(self))

    
    def OnEidtMessage(self, iMsgID):
        pass

    
    def SetAcitve(self, bAcitve):
        if bAcitve != self.m_bActive:
            self.SetShow(bAcitve)
            self.ssEmit(self.SS_Active, bAcitve)
        

    
    def UpdateActive(self):
        self.SetShow(True)
        self.ssEmit(self.SS_Active, True)

    
    def ClickPage(self, iPageOffset):
        self.ssEmit(self.SS_ClickPage, iPageOffset)

    
    def GetBarPos(self):
        oScrollBar = self.GetObject('tab_item').GetScrollBar()
        return None if oScrollBar else 0

    
    def SetBarPos(self, iBarPos):
        oScrollBar = self.GetObject('tab_item').GetScrollBar()
        if oScrollBar:
            oScrollBar.SetBarPos(iBarPos)
        

    
    def RefreshTable(self, dInfoList):
        '''
\t\t\xa8\xea\xb7s\xaa\xed\xae\xe6\xbc\xc6\xbe\xda
\t\t:param dInfoList:
\t\t{"iItID":\xb8\xcb\xb3\xc6id,
\t\t"iShapeID":"\xb3y\xab\xacid",
\t\t"iRemainTime":\xb3\xd1\xbel\xae\xc9\xb6\xa1,
\t\t"iCashType":\xb3f\xb9\xf4\xc3\xfe\xab\xac(0-\xb2{\xaa\xf7,1-\xb1H\xb0\xe2\xa5d),
\t\t"bCare": \xacO\xa7_\xc3\xf6\xaa`(0-\xa4\xa3\xc3\xf6\xaa`\xa1A1-\xa4\xa3\xc3\xf6\xaa`)
\t\t"iPrice":\xbb\xf9\xae\xe6,
\t\t"iPetType":\xc3d\xaa\xab\xc3\xfe\xab\xac\xa1A0-\xb4\xb6\xb3q 1-\xc5\xdc\xb2\xa7 2-\xb3\xa5\xa5\xcd
\t\t}
\t\t'''
        self.m_Data = dInfoList
        oTab = self.GetObject('tab_item')
        oTab.Clear()
        iLenData = len(dInfoList)
        for iIndex in xrange(iLenData):
            dItemData = dInfoList[iIndex]
            oRowBox = oTab.AddBoxItem()
            iId = dItemData['iItID']
            iShapId = dItemData['iShapeID']
            oItemIcon = consignmallwidget.CItemTradeGuild(oRowBox, iId, iShapId, False)
            oSkill = CHeroSkillItem(oRowBox, 200, dItemData['dSpecialSkillList'], dItemData['dSpecialEffList'], iId, iShapId)
            oItemSaleStatus = consignmallwidget.CItemSaleStatus(oRowBox, iId, dItemData['bCare'], c	nsignmalldefines.GUILD_GOODSTYPE_EQUIP, dItemData['iPrice'], dItemData['iCashType'])
            oTab.AddItemExtend(oRowBox, [
                oItemIcon,
                oSkill,
                oItemSaleStatus], bChangeColor = False)
        
        oTab.ResetItems()
        oTab.ResetScrollBar()

    
    def OnHotBoxEnter(self, hotbox):
        import wrapinterface
        if hotbox.m_Index in (0, 1, 2):
            self.m_HotBoxTips = wrapinterface.CTextTips(None, 80, '\xc2I\xc0\xbb\xa5i\xb1\xc6\xa7\xc7', interface.FontLT14_3, owner = hotbox)
        

    
    def OnHotBoxLeave(self, hotbox):
        self.m_HotBoxTips = None

    
    def OnHotBoxClick(self, hotbox):
        self.ssEmit(self.SS_ClickSort, hotbox.m_Index)

    
    def OnSelectedItem(self, iIndex):
        self.ssEmit(self.SS_ClickItem, iIndex)

    
    def OnMessage(self, iMsgID):
        if iMsgID <= iMsgID:
            pass
        elif iMsgID < 200:
            iIndex = iMsgID - 101
            self.OnSelectedItem(iIndex)
        
        self.OnEidtMessage(iMsgID)



class CHeroSkillItem(interface.CClickBox):
    
    def __init__(self, oParent, iWidth, dSkillList, dEffList, iItemId, iShape):
        interface.CClickBox.__init__(self, oParent, c	nsignmalldefines.GOOD_DESCRIBE_UI_LENGTH, oParent.GetSize()[1], alpha = 0)
        self.m_oLinkText = None
        self.m_oEnterBox = None
        self.m_oTip = None
        self.m_iItemID = iItemId
        self.m_iShape = iShape
        self.m_oEnterTime = None
        self.InitSkill(dSkillList, dEffList)
        self.SetPassScrollingMessagesUp(True)

    
    def InitSkill(self, dSkillList, dEffList):
        sMsg = ''
        for dSkill in dSkillList:
            sMsg += '%s(%s\xa6\xb8),' % (wrapui.CLinkSkillTips.Create(wrapui.CLinkSkillTips.TYPE_SPECIAL, dSkill['iID'], dSkill['iTimes']), dSkill['iTimes'])
        
        for dEff in dEffList:
            sMsg += '%s,' % wrapui.CLinkSkillTips.Create(wrapui.CLinkSkillTips.TYPE_EFF, dEff['iID'], dEff['iCnt'])
        
        if sMsg:
            sMsg = sMsg[0:-1]
        
        (iWidth, iHeight) = self.GetSize()
        self.m_oLinkText = wrapinterface.CLinkRichTextObject(self, iWidth, interface.FontLT14_3, sMsg, 16777215, ReplaceGreen)
        (iItW, iItH) = self.m_oLinkText.GetSize()
        (x, y) = interface.GetAlignXY(iItW, iItH, iWidth, iHeight, interface.ALIGN_CENTER_MIDDLE)
        self.m_oLinkText.SetPos(x, y)
        self.m_oLinkText.SetPassScrollingMessagesUp(True)

    
    def Enter(self):
        if tipsclosemgr.IsHandle():
            return None
        
        oParent = self.GetParent()
        oParent.Enter()
        if self.m_oEnterTime:
            self.m_oEnterTime.Release()
        
        self.m_oEnterTime = \xbe\xa3\xa7\xafr.Timer(c	nsignmalldefines.TIPS_WAIT_TIME, misc.Functor(self.CreateTips))

    
    def CreateTips(self):
        global g_oEquipSkillTips
        import dlggetinfo
        g_oEquipSkillTips = dlggetinfo.ShowTradeGuildItemInfo(self.m_iItemID, self.m_iShape)
        tipsclosemgr.Regist(g_oEquipSkillTips)
        self.m_oEnterTime = None

    
    def Leave(self):
        global g_oEquipSkillTips
        oParent = self.GetParent()
        if oParent:
            oParent.Leave()
        
        tipsclosemgr.CheckClose()
        g_oEquipSkillTips = None
        if self.m_oEnterTime:
            self.m_oEnterTime.Release()
        
        self.m_oEnterTime = None



def ReplaceGreen(sText):
    return sText.replace('#G', '#c12A42E')
