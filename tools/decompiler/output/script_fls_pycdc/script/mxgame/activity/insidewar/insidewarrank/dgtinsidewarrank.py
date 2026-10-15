# pycdc 交叉复核产物 · script.fls entry 1236
# co_filename(原始)='script/mxgame/activity/insidewar/insidewarrank/dgtinsidewarrank.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1236.pyc (Python 2.5)

import delegatebase
import mdinsidewarrank

class CServerRankDgt(delegatebase.CDelegateBase):
    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_CloseWindow, self.CloseWindow)
        oModel = mdinsidewarrank.GetServerBattleModel()
        oModel.ssConnect(oModel.SS_UpdataRankInfo, self.UpdateRankInfo)

    
    def CloseWindow(self):
        self.GetView().CloseWindow()

    
    def UpdateRankInfo(self):
        oView = self.GetView()
        oModel = mdinsidewarrank.GetServerBattleModel()
        dicRank = oModel.GetRecordDic()
        lstInfo = []
        for k, \xd3 in dicRank.items():
            sTeamName = \xd3.get('sTeamName')
            iScore = \xd3.get('iScore')
            iTeamID = \xd3.get('iTeamID')
            sRecord = '%d\xb3\xd3' % \xd3['iWinNum']
            tInfo = (sTeamName, iTeamID, iScore, sRecord)
            lstInfo.append(tInfo)
        
        lstInfo.sort(key = (lambda a: -a[2]))
        oView.UpdateRank(lstInfo)
