# pycdc 交叉复核产物 · script.fls entry 3289
# co_filename(原始)='script/mxui/component/showrolecomponent/selectrolecolor.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_3289.pyc (Python 2.5)

'''
'''
import misc
import roleshapdesc
import slot
import delegateroleshapedesc
import combdialog
import interface
import appearancedefine as define
import permission

class CRolePartCtrl(combdialog.CCombSubWnd, slot.ISignalSubject):
    SS_OnClickSelect = 'SS_OnClickSelect'
    
    def __init__(self, oParent, sMarkList, iType, iStyle = 0):
        if iStyle == 0:
            if permission.IsTestServerByNewYanzhiguan():
                combdialog.CCombSubWnd.__init__(self, oParent, 'dialog4/appearance_newstyle/selectrole/rolepartctrl.dlg')
            else:
                combdialog.CCombSubWnd.__init__(self, oParent, 'dialog4/appearance/selectrole/rolepartctrl.dlg')
        elif iStyle == 1:
            if permission.IsTestServerByNewYanzhiguan():
                combdialog.CCombSubWnd.__init__(self, oParent, 'dialog4/appearance_newstyle/selectrole/rolepartctrl.dlg')
            else:
                combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/appearance/selectrole/rolepartctrl.dlg')
        
        self.m_DelegateList = []
        self.m_sMarkList = sMarkList
        self.m_iType = iType
        self.ssInit()
        self.SetIgnoreEsc(True)
        self.InitDelegate(sMarkList, iType)

    
    def InitDelegate(self, sMarkList, iType):
        dTypeData = {
            define.PART_SHOW_HORSE: delegateroleshapedesc.CPartRoleHorse,
            define.PART_SHOW_WING: delegateroleshapedesc.CPartRoleWing,
            define.PART_SHOW_AURA: delegateroleshapedesc.CPartRoleAura,
            define.PART_SHOW_FASHION: delegateroleshapedesc.CPartRoleFashion }
        self.m_DelegateList = [
            dTypeData[iType](self, sMarkList)]

    
    def GetBtnSelect(self):
        return self.GetObject('btn_select').IsSelected()

    
    def SetSelect(self, bSelect):
        self.GetObject('btn_select').SetSelect(bSelect)

    
    def SetText(self, sName):
        self.GetObject('txt_name').SetText(sName)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.ssEmit(self.SS_OnClickSelect)
        



def AlignPartCtrl(oLoc, iMax, oAlignList):
    '''
\t\xadn\xa8DoLoc\xbbPoAlignList\xa4\xa4\xa4\xb8\xaf\xc0\xa5\xb2\xb6\xb7\xbe\xd6\xa6\xb3\xac\xdb\xa6P\xaa\xba\xa4\xf7\xb9\xef\xb9\xb3
\t:param oLoc: \xadI\xb4\xba\xa8\xcc\xbf\xe0\xb9\xef\xb9\xb3
\t:param iMax: \xb3\xcc\xa4j\xb1\xa1\xaap\xaa\xba\xa7G\xa7\xbd
\t:param oAlignList: \xbb\xdd\xadn\xb1\xc6\xa6C\xaa\xba\xb9\xef\xb6H\xa6C\xaa\xed
\t:return:
\t'''
    if not oLoc:
        return None
    
    (iW, iH) = oLoc.GetSize()
    (iX, iY) = oLoc.GetPos()
    oAlignList = _[1]
    iLen = len(oAlignList)
    iEach = int(iW / float(iMax))
    iOffX = max(0, iMax - iLen) * iEach / 2
    for iPos, oAlign in enumerate(oAlignList):
        (iAlignW, iAlignH) = oAlign.GetParent().GetSize()
        (iPosX, iPosY) = interface.GetAlignXY(iAlignW, iAlignH, iEach, iH, interface.ALIGN_CENTER_MIDDLE)
        oAlign.GetParent().SetPos(iX + iPosX + iEach * iPos + iOffX, iY + iPosY)
        oAlign.GetParent().SetZ(1)
    


class CChangeColorOneDlg(combdialog.CCombSubWnd, slot.ISignalSubject):
    SS_OnClickRight = 'SS_OnClickRight'
    SS_OnClickLeft = 'SS_OnClickLeft'
    SS_OnClickSelect = 'SS_OnClickSelect'
    
    def __init__(self, oParent, sMark):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog4/appearance/selectrole/selectcolor.dlg')
        self.m_DelegateList = []
        self.m_sMark = sMark
        self.m_oRoleObj = roleshapdesc.CRolePhoto(self.GetObject('loc_item'), sMark)
        interface.\xd5enter(self.m_oRoleObj)
        self.ssInit()
        self.InitDelegate(sMark)
        self.SetIgnoreEsc(True)

    
    def InitDelegate(self, sMark):
        self.m_DelegateList = [
            delegateroleshapedesc.CDelegateChangeDirRole(self, sMark)]

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.ssEmit(self.SS_OnClickSelect)
        elif iMsgID == 3:
            self.ssEmit(self.SS_OnClickLeft)
        elif iMsgID == 4:
            self.ssEmit(self.SS_OnClickRight)
        



class CSelectColorDlg(combdialog.CCombSubWnd):
    '''
\t\xa4G\xbf\xef\xa4@\xa8\xa4\xa6\xe2\xac\xc9\xad\xb1
\t'''
    
    def __init__(self, oParent, sMarkList, oClickCB):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog4/appearance/selectrole/appearance_project.dlg')
        self.m_oClickCB = misc.Functor(oClickCB)
        self.m_sMarkList = sMarkList
        self.m_oRoleObjDict = { }
        self.InitRoleObj(sMarkList)
        self.SetIgnoreEsc(True)

    
    def InitRoleObj(self, sMarkList):
        sLocList = [
            'loc_project1',
            'loc_project2']
        for iPos, sMark in enumerate(sMarkList):
            oRolePhoto = roleshapdesc.CRolePhoto(self.GetObject(sLocList[iPos]), sMark)
            oRolePhoto.ssConnect(oRolePhoto.SS_OnClickRole, misc.Functor(self.OnClickSelect, sMark))
            self.m_oRoleObjDict[sMark] = oRolePhoto
        

    
    def OnClickSelect(self, sMark):
        if self.m_oClickCB and callable(self.m_oClickCB):
            self.m_oClickCB(sMark)
