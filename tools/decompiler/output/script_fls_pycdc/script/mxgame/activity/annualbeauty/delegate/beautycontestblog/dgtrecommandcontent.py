# pycdc 交叉复核产物 · script.fls entry 470
# co_filename(原始)='script/mxgame/activity/annualbeauty/delegate/beautycontestblog/dgtrecommandcontent.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_470.pyc (Python 2.5)

import annualbeautydefine
import delegatebase
import fusaidefine
import httpannualbeautycontest
import httpplayershow
import mdfusai
import misc
import netannualbeauty
import usermacro

class CDgtRecommandContent(delegatebase.CDelegateBase):
    
    def __init__(self, oView, sDispatcherName):
        self.m_sDispatcherName = sDispatcherName
        delegatebase.CDelegateBase.__init__(self, oView)

    
    def \xfe\xdc\xcd\xef\xd0\xdc\xce(self):
        '''
\t\t:rtype: fusairecommendcontent.CRecommandContent
\t\t'''
        return self.m_ViewRef.Get()

    
    def Init(self):
        oView = self.\xfe\xdc\xcd\xef\xd0\xdc\xce()
        oView.ssConnect(oView.SS_ReqRecommandInfo, self.OnReqRecommandInfo)
        oView.ssConnect(oView.SS_OnGotoMainPage, self.OnGotoMainPage)
        oView.ssConnect(oView.SS_OpenBidding, self.OnOpenBidding)
        oMgr = mdfusai.GetMgr()
        oMgr.ssConnect(oMgr.SS_UpdateSysRecommendInfo, self.OnUpdateSysRecommendInfo)
        oView.SetShowAuctionBtn(False)

    
    def OnOpenBidding(self, iPid, iServId):
        netannualbeauty.C2SFSOpenAuction(iPid, iServId)

    
    def OnGotoMainPage(self, dFlyerInfo):
        mdfusai.GetMgr().ChangeFlyTabPage(dFlyerInfo, fusaidefine.FUSAI_TAB_BLOG)

    
    def OnUpdateSysRecommendInfo(self, dSysRecommendInfo):
        oView = self.\xfe\xdc\xcd\xef\xd0\xdc\xce()
        oView.SetShowAuctionBtn(mdfusai.GetMgr().IsJoin())
        oView.SetSysRecommendInfo(dSysRecommendInfo)
        dFlyerInfo = dSysRecommendInfo.get('flyerInfo')
        httpannualbeautycontest.GetBlogList(misc.Functor(self.OnReqCallBack), str(dFlyerInfo.get(annualbeautydefine.KEY_SERVERID)), dFlyerInfo.get(annualbeautydefine.KEY_PID), fusaidefine.PLAYER_BLOG, fusaidefine.PLAYER_CONTENT_BLOG, fusaidefine.ACTIVITY_ID, fusaidefine.SORT_BY_TIME, 1, 1)

    
    def OnReqRecommandInfo(self):
        netannualbeauty.C2SOpenRecommendView()

    
    def OnReqCallBack(self, data, bSucceed, *args):
        (iPid, iContenttype) = args[0]
        data = httpplayershow.Parse(data, bSucceed)
        if not bSucceed:
            usermacro.PROMPT_MSG('\xba\xf4\xb5\xb8\xc1c\xa6\xa3, \xc0\xf2\xa8\xfa\xaa\xb1\xaea\xb0\xca\xbaA\xa5\xa2\xb1\xd1')
            return None
        
        iCode = data.get('Code')
        if iCode:
            usermacro.PROMPT_MSG('\xbc\xc6\xbe\xda\xb2\xa7\xb1`\xa1Acode:%d' % iCode)
            return None
        
        dExtData = data.get('ext_data')
        oMgr = mdfusai.GetBlogInfoMgr()
        oMgr.AddBlogInfos(iPid, data.get('iRecordscount'), dExtData)
        dBlogData = oMgr.GetBlogInfos(iPid)
        oView = self.\xfe\xdc\xcd\xef\xd0\xdc\xce()
        oView.SetWebBlogData(dBlogData)
