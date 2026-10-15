# pycdc 交叉复核产物 · script.fls entry 1287
# co_filename(原始)='script/mxgame/activity/ladderrank/delegate/dgtrewardpreview.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1287.pyc (Python 2.5)

import delegatebase

class CRewardPreviewDelegate(delegatebase.CDelegateBase):
    
    def Init(self):
        self.InitRewardView()

    
    def InitRewardView(self):
        oModel = self.GetModel()
        dDataList = oModel.GetAllRewardList()
        for dData in dDataList:
            dData['bShowMark'] = dData['iRank'] == oModel.GetMyInfo()['iDanRank']
        
        dData = self
        None().RefreshRewardTbView(dDataList)

    
    def GetModel(self):
        import ladderrankmgr
        return ladderrankmgr.GetRoomMgr()



class CDanRewardPreviewDelegate(delegatebase.CDelegateBase):
    
    def Init(self):
        self.InitDanRewardView()

    
    def InitDanRewardView(self):
        oView = self.GetView()
        oModel = self.GetModel()
        oView.ClearRewardList()
        for dData in oModel.GetDanRewardList():
            oView.AddRewardListItem(dData)
        
        oView.ResetCommentList()

    
    def GetModel(self):
        import ladderrankmgr
        return ladderrankmgr.GetRoomMgr()
