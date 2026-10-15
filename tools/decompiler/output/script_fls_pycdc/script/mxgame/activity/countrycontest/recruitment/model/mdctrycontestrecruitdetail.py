# pycdc 交叉复核产物 · script.fls entry 1358
# co_filename(原始)='script/mxgame/activity/countrycontest/recruitment/model/mdctrycontestrecruitdetail.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1358.pyc (Python 2.5)

'''
# @Time     : 2019/4/26 15:04
# @Author   : huyuhong01
# @File     : mdctrycontestmyrecruitment.py
# @Explain  : Model\xd5\xd0\xc4\xbc\xcf\xea\xc7\xe9
'''
import mvp
g_MyRecruitModel = None

def ModuleReset():
    global g_MyRecruitModel
    g_MyRecruitModel = None


def GetMyRecruitModel():
    global g_MyRecruitModel
    if not g_MyRecruitModel:
        g_MyRecruitModel = CCtryContestMyRecruitModel()
    
    return g_MyRecruitModel


class CCtryContestRecruitDetailModel(mvp.CEventModel):
    SS_RecruitmentInfoChange = 'SS_RecruitmentInfoChange'
    
    def __init__(self, *args, **kwargs):
        self.m_dRecruitmentInfo = None
        mvp.CEventModel.__init__(self, *args, **kwargs)

    
    def OnUpdate(self, dRecruitmentInfo = None):
        if dRecruitmentInfo is not None:
            self.m_dRecruitmentInfo = dRecruitmentInfo
            self.ssEmit(self.SS_RecruitmentInfoChange)
        

    
    def OnDestroy(self):
        pass

    
    def GetRecruitmentInfo(self):
        return self.m_dRecruitmentInfo

    return None %= None


class CCtryContestRecruitApplyModel(CCtryContestRecruitDetailModel):
    pass


class CCtryContestMyRecruitModel(CCtryContestRecruitDetailModel):
    
    def ClearMyRecruitmentInfo(self):
        self.m_dRecruitmentInfo = None

    
    def GetMyRecruitmentInfo(self):
        if not self.m_dRecruitmentInfo:
            return None
        
        import hero
        import misc
        dInfo = { }
        dInfo['playerid'] = hero.GetHeroID()
        dInfo['name'] = hero.GetHeroName()
        dInfo['serverid'] = misc.GetServerID()
        dInfo['sendclass'] = hero.GetProp('m_Class')
        dInfo['class'] = self.m_dRecruitmentInfo.get('class', [])
        dInfo['liupai'] = hero.GetProp('m_Liupai')
        dInfo['lv'] = hero.GetProp('m_Grade')
        dInfo['oltimes'] = self.m_dRecruitmentInfo.get('oltimes')
        dInfo['oltimee'] = self.m_dRecruitmentInfo.get('oltimee')
        dInfo['accountid'] = 0
        dInfo['iTitle'] = self.m_dRecruitmentInfo.get('iTitle')
        dInfo['desc'] = self.m_dRecruitmentInfo.get('desc')
        dInfo['iApply'] = 0
        dInfo['time'] = self.m_dRecruitmentInfo.get('time', 0)
        return dInfo
