# pycdc 交叉复核产物 · script.fls entry 394
# co_filename(原始)='script/mxgame/sevendaytarget/dlgsevendaypreview.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_394.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2020/12/8 14:19
\xd7\xf7\xd5\xdf: \xb2\xbb\xbc\xd3\xb1\xf9
\xce\xc4\xbc\xfe: dlgsevendaypreview
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import combdialog
import interface
import slot
import wrapinterface
import sevendaytargetdata
import dlgpayrmbpurchase
import mdpayrmbpurchase
import hero
import permission
SEVEN_DAY_TARGET_GIFT = 19

class CSevenDayPreviewDlg(combdialog.CCombDialog, slot.ISignalSubject):
    
    def __init__(self, oParent):
        sFileName = 'dialog4/sevenday/chongzhi.dlg'
        if permission.IsTestSevenDayTargetPreview():
            sFileName = 'dialog4/sevenday/chongzhi2.dlg'
        
        combdialog.CCombDialog.__init__(self, oParent, sFileName)
        self.ssInit()
        self.m_RewardItemList = []
        self.InitDlg()

    
    def InitDlg(self):
        self.SetRewardIcon()

    
    def SetRewardIcon(self):
        self.m_RewardItemList = []
        oImageFrames = self.GetObject('img_item')
        oImageList = oImageFrames.GetImageList()
        for \x94\x99x, oImage in enumerate(oImageList):
            dRewardData = sevendaytargetdata.GetPreviewReward(\x94\x99x)
            if not dRewardData:
                continue
            
            oItem = CItemIconWithName(oImage, dRewardData['iShape'], dRewardData['iRewCount'], 10)
            if dRewardData['sRewOtherDesc']:
                oItem.SetInfoExt(dRewardData['sRewOtherDesc'])
            
            if dRewardData['iFlash']:
                oItem.SetFlash(True)
            
            interface.Center(oItem)
            oImage.SetShow(True)
            self.m_RewardItemList.append(oItem)
        

    
    def OnEditMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseUI()
        elif iMsgID == 2:
            mdpayrmbpurchase.GetModel().SetBaseInfo(hero.GetHeroID(), SEVEN_DAY_TARGET_GIFT, 1)
            dlgpayrmbpurchase.Show()
        

    
    def OnMessage(self, iMsgID):
        self.OnEditMessage(iMsgID)



class CItemIconWithName(wrapinterface.CItemIcon):
    
    def __init__(self, oParent, iShape, iQuantity, iMsgID):
        wrapinterface.CItemIcon.__init__(self, oParent, iShape, iQuantity, iMsgID)
        self.m_oFlashObj = None

    
    def Enter(self):
        self.ShowTips()

    
    def Leave(self = None):
        self.HideTips()

    
    def SetFlash(self, bFlash):
        if bFlash and self.m_Image:
            (w, h) = self.GetSize()
            z = self.GetZ()
            oFlashObj = interface.qaB@[FW}PXWQt(self, '\xd4\xd3\xcd\xbc/\xce\xef\xc6\xb7\xb1\xdf\xbf\xf2\xc1\xf7\xb9\xe2.spr', 'interface')
            oFlashObj.SetPos(w / 2 - 1, h / 2 - 1)
            oFlashObj.SetZ(z + 1)
            oFlashObj.CreateCommand(1, 'animation')
        else:
            oFlashObj = None
        self.m_oFlashObj = oFlashObj
