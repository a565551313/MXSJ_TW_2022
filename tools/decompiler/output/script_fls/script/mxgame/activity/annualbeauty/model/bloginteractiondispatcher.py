# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\mxgame\activity\annualbeauty\model\bloginteractiondispatcher.py
import slot
SS_ClickZanBtn = 'SS_ClickZanBtn(sServId, iPid, iWbId)'
SS_ClickReviewBtn = 'SS_ClickReviewBtn(sServId, iPid, iWbId)'
SS_ClickReviewBtnInReview = 'SS_ClickReviewBtnInReview(sServId, iPid, iWbId)'
SS_ClickDelBlogBtn = 'SS_ClickDelBlogBtn(sServId, iPid, iWbId)'
SS_ClickReportClick = 'SS_ClickReportClick(sServId, iPid, iWbId)'
SS_ReqFlyerInfo = 'SS_ReqFlyerInfo(dFlyInfo, iPage, iPageSize)'
SS_ReqFlyerImgWall = 'SS_ReqFlyerImgWall(dFlyInfo, iStep)'
SS_ReqContributeRank = 'SS_ReqContributeRank(iPid, sServId)'
SS_RefreshBlog = 'SS_RefreshBlog()'
SS_RefreshReply = 'SS_RefreshReply(iPid, iServId, iWbid)'
g_Instances = None

def GetInstance(sName='flyer'):
    global g_Instances
    if not g_Instances:
        g_Instances = {}
    oInstance = g_Instances.get(sName)
    if not oInstance:
        oInstance = CBlogInterationDispatcher()
        g_Instances[sName] = oInstance
    return oInstance


def ModuleReset():
    global g_Instances
    g_Instances = None
    return


class CBlogInterationDispatcher(slot.ISignalSubject):

    def __init__(self):
        self.ssInit()
        return


return
