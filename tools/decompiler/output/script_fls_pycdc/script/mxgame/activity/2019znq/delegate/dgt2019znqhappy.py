# pycdc 交叉复核产物 · script.fls entry 2698
# co_filename(原始)='script/mxgame/activity/2019znq/delegate/dgt2019znqhappy.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_2698.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2019/10/28 14:08
\xd7\xf7\xd5\xdf: zwy
\xce\xc4\xbc\xfe: dgt2019znqhappy
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import delegatebase
import md2019znq
import mx2019znqdata
import misc

class C2019ZNQHappyDgt(delegatebase.CDelegatePaginationBase):
    
    def GetView(self):
        ''':rtype: dlg2019znqhappy.C2019ZNQHappy'''
        return delegatebase.CDelegatePaginationBase.GetView(self)

    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_OpenWeb, self.OnOpenWeb)
        oView.ssConnect(oView.SS_GetReward, self.OnGetReward)
        oModel = md2019znq.Get2019ZNQModel()
        oModel.ssConnect(oModel.SS_CelebrationRateChg, self.OnCelebrationRateChg)
        oModel.ssConnect(oModel.SS_CelebrationSelfScoreChg, self.OnCelebrationSelfScoreChg)
        oModel.ssConnect(oModel.SS_CelebrationAllScoreChg, self.OnCelebrationAllScoreChg)
        oModel.ssConnect(oModel.SS_CelebrationRewardInfoChg, self.OnCelebrationRewardChg)
        self.OnCelebrationRateChg(oModel.GetCelebrationRate())
        self.OnCelebrationAllScoreChg(oModel.GetCelebrateAllScore())
        self.OnCelebrationSelfScoreChg(oModel.GetCelebrateSelfScore())
        self.OnCelebrationRewardChg()

    
    def OnCelebrationRateChg(self, iRate):
        self.GetView().SetExpRate(iRate)

    
    def OnCelebrationSelfScoreChg(self, iScore):
        self.GetView().SetSelfScore(self.GetShowScore(iScore))

    
    def OnCelebrationAllScoreChg(self, iScore):
        self.GetView().SetAllScore(self.GetShowScore(iScore))
        self.GetView().SetExpNum(str(iScore))

    
    def OnCelebrationRewardChg(self):
        iAllScore = md2019znq.Get2019ZNQModel().GetCelebrateAllScore()
        dRewardInfo = md2019znq.Get2019ZNQModel().GetCelebrationRewardInfo()
        dOrgInfo = misc.DeepCopy(mx2019znqdata.CELEBRATION_DATA)
        for iRewardID, bGet in dRewardInfo.iteritems():
            if iRewardID not in dOrgInfo:
                continue
            
            dOrgInfo[iRewardID]['bGet'] = bGet
            dOrgInfo[iRewardID]['bCanGet'] = iAllScore >= dOrgInfo[iRewardID]['iCondition']
        
        self.GetView().RefreshReward(dOrgInfo)

    
    def OnOpenWeb(self):
        import net
        net.OpenUrl('https://mx.duoyi.com/act/anniversary/2019/')

    
    def OnGetReward(self, iRewardIdx):
        import csyearback
        csyearback.C2GSGetPlayItem(iRewardIdx)

    
    def GetShowScore(self, iScore):
        iScore = max(iScore, 0)
        if iScore <= iScore:
            pass
        elif iScore < 10000:
            return str(iScore)
        elif iScore <= iScore:
            pass
        elif iScore < 100000:
            \xc8\xef\xd6\xcb = '%0.3f' % float(iScore) / 10000
            return '%s\xb8U' % \xc8\xef\xd6\xcb[:-1]
        elif iScore <= iScore:
            pass
        elif iScore < 1000000:
            \xc8\xef\xd6\xcb = '%0.2f' % float(iScore) / 10000
            return '%s\xb8U' % \xc8\xef\xd6\xcb[:-1]
        elif iScore <= iScore:
            pass
        elif iScore < 100000000:
            return '%s\xb8U' % iScore / 10000
        else:
            \xc8\xef\xd6\xcb = '%0.3f' % float(iScore) / 100000000
            return '%s\xbb\xf5' % \xc8\xef\xd6\xcb[:-1]
