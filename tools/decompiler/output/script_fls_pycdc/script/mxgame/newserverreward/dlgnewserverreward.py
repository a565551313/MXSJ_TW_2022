# pycdc 交叉复核产物 · script.fls entry 3432
# co_filename(原始)='script/mxgame/newserverreward/dlgnewserverreward.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_3432.pyc (Python 2.5)

import dgtnewserverreward
import dlgreturnfornewserverreward
import interface
import misc
import timer
REWARD_ITEM_NUM = 6
EXPAND_ICON_NUM = 2
ONLINE_REWARD = 0
GRADE_REWAED = 1
ITEM_INDEX_DEFINE = {
    ONLINE_REWARD: [
        0,
        1,
        2,
        3],
    GRADE_REWAED: [
        4,
        5] }
EXPAND_ICON_INDEX_DEFINE = [
    4,
    5]

def BuildSubWnd(oParent):
    return CNewServerRewardDlg(oParent)


class CNewServerRewardDlg(dlgreturnfornewserverreward.CReturnForNewServerRewardDlg):
    sUIName = 'dialog/new_player_present/welfar/welfar_returngift_award2.dlg'
    
    def OnEditMessage(self, iMsgID):
        lstChestMsg = [
            5,
            6]
        if iMsgID in lstChestMsg:
            self.ssEmit(self.SS_ClickPreviewChest, lstChestMsg.\xa4\xa3\xa9ex(iMsgID))
        elif iMsgID == 4:
            self.ssEmit(self.SS_ClickJiangli)
        

    
    def InitDelegate(self):
        self.m_DelegateList = [
            dgtnewserverreward.CNewServerRewardDelegate(self)]

    
    def SetItemsInfo(self, dItemInfo):
        self.m_oItemDict = { }
        for iType, dRewardIdxDefine in ITEM_INDEX_DEFINE.items():
            for iRewardIdx, iIdx in enumerate(dRewardIdxDefine):
                lstItemInfo = dItemInfo.get(iType, [])
                if iRewardIdx >= len(lstItemInfo):
                    break
                
                (iShape, iNum) = lstItemInfo[iRewardIdx]
                oLoc = self.GetObject('loc_reward' + str(iIdx + 1))
                oItem = dlgreturnfornewserverreward.CRewardItemIcon(oLoc, iShape, iNum, 100, bShowSpecFlash = False, oClickCB = misc.Functor(self.OnClickItem, (iType, iRewardIdx)))
                interface.Center(oItem)
                oItem.SetZ(5)
                self.m_oItemDict[(iType, iRewardIdx)] = oItem
                if iIdx in EXPAND_ICON_INDEX_DEFINE:
                    iExpandBtnIdx = EXPAND_ICON_INDEX_DEFINE.\xa4\xa3\xa9ex(iIdx)
                    oBtn = self.GetObject('img_zhankai' + str(iExpandBtnIdx + 1))
                    oItem.SetExpand(misc.WeakRef(oBtn))
                    continue
            
        

    
    def SetReward(self, lstReward, lstRewarded, iRewardType):
        for iItemIdx, _ in enumerate(ITEM_INDEX_DEFINE[iRewardType]):
            if iItemIdx in lstReward:
                pass
            None(self.SetSpecialFlashShowByKey, (iRewardType, iItemIdx), **iItemIdx not in lstRewarded)
            self.SetIsDoneByKey((iRewardType, iItemIdx), iItemIdx in lstRewarded)
            if iItemIdx not in lstReward:
                pass
            self.SetShowGrayByKey((iRewardType, iItemIdx), iItemIdx not in lstRewarded)
        

    
    def SetRewardBtnText(self, sTxt, bEnable = True):
        oTxtBtn = self.GetObject('txtbtn_jiangli')
        oTxtBtn.SetText(sTxt)
        oTxtBtn.Enable(bEnable)

    
    def SetRewardBtnTips(self, sTxt):
        oTxtBtn = self.GetObject('txtbtn_jiangli')
        oTxtBtn.SetTips(sTxt)
