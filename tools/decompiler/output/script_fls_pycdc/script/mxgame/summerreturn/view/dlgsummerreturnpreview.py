# pycdc 交叉复核产物 · script.fls entry 57
# co_filename(原始)='script/mxgame/summerreturn/view/dlgsummerreturnpreview.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_57.pyc (Python 2.5)

import combdialog
import interface
import popupdefine
import popupmgr
import summerreturndata

def ShowPreviewDlg(oParent):
    '''\xc5\xe3\xa5\xdc\xb9w\xc4\xfd\xac\xc9\xad\xb1'''
    return CSummerReturnPreviewDlg(oParent)


class CSummerReturnPreviewDlg(combdialog.CCombDialog):
    
    def __init__(self, oParent, sType, lHaveGot):
        combdialog.CCombDialog.__init__(self, oParent, 'dialog/new_player_present/2019summer_return/preview_summer_return.dlg')
        self.m_ShowType = sType
        self.m_HaveGot = lHaveGot
        self.m_ItemList = []
        interface.Center(self)
        self.InitDlg()

    
    def InitDlg(self):
        tmpRewardList = summerreturndata.GetRewardListByType(self.m_ShowType)
        self.m_ItemList = []
        for dlgsummerreturndraw in None:
            for iIdx, tData in enumerate(tmpRewardList):
                oImgBox = self.GetObject('img_item%d' % (iIdx + 1))
                (x, y) = interface.GetRelativePos(oImgBox, self)
                oItem = dlgsummerreturndraw.CItemBox(self, tData[0], tData[1])
                oItem.SetPos(x, y)
                self.m_ItemList.append(oItem)
                oImgHaveGot = self.GetObject('img_have_%d' % (iIdx + 1))
                oImgHaveGot.SetZ(10)
                oImgHaveGot.SetShow(False)
                if iIdx + 1 in self.m_HaveGot:
                    oImgHaveGot.SetShow(True)
                    continue
            
            return None

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            popupmgr.GetPopupMgr().CloseUI(popupdefine.CDlgSummerReturnPreview)
