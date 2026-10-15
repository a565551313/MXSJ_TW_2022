# pycdc 交叉复核产物 · script.fls entry 112
# co_filename(原始)='script/mxgame/newgroup/delegate/delegatemanage/delegategroupskillresearch.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_112.pyc (Python 2.5)

'''
delegategroupskillresearch.py
create by xian90 2019/5/28 14:34
\xc4\xa3\xbf\xe9\xb9\xa6\xc4\xdc\xcb\xb5\xc3\xf7:
'''
import misc
import netgroup
import skilldata

class CDelegateGroupSkillResearch(object):
    
    def __init__(self, pContext, pView):
        super(CDelegateGroupSkillResearch, self).__init__()
        self.m_wrContext = misc.WeakRef(pContext)
        self.m_wrView = misc.WeakRef(pView)
        self.m_iReserveExp = 0
        self.m_iActiveSkillId = 0
        self.m_vSkillInfoList = []
        self.RequestData()
        self.InitSignal()

    
    def GetContext(self):
        return None if self.m_wrContext else None

    
    def GetView(self):
        return None if self.m_wrView else None

    
    def InitSignal(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_OnClickActiveSkill, self.OnClickActiveSkill)
        oView.ssConnect(oView.SS_OnSelectSkillItem, self.OnSelectSkillItem)
        oView.ssConnect(oView.SS_RefreshView, self.RequestData)
        import groupsignal
        groupsignal.Connect(groupsignal.SS_SetActiveSkill, self.OnActiveSkill)
        groupsignal.Connect(groupsignal.SS_ChangeSkillResearchInfo, self.OnRefreshSkillInfoList)

    
    def RequestData(self):
        LOG_DEBUG('--------\xc0\xb0\xac\xa3\xba\xde\xb2z\xac\xc9\xad\xb1\xa1A\xa7\xde\xaf\xe0\xac\xe3\xa8s\xa4\xc0\xad\xb6\xa1A\xbd\xd0\xa8D\xc0\xb0\xac\xa3\xa7\xde\xaf\xe0\xabH\xae\xa7--------')
        netgroup.C2SGetGroupSkill()

    
    def OnRefreshSkillInfoList(self, pDataManager, vInfo):
        LOG_DEBUG('--------\xc0\xb0\xac\xa3\xba\xde\xb2z\xac\xc9\xad\xb1\xa1A\xa7\xde\xaf\xe0\xac\xe3\xa8s\xa4\xc0\xad\xb6\xa1A\xaaA\xb0\xc8\xbe\xb9\xa8\xea\xb7s\xa7\xde\xaf\xe0\xabH\xae\xa7--------')
        self.m_vSkillInfoList = vInfo
        oView = self.GetView()
        dLocalData = skilldata.GetData(self.m_iActiveSkillId)
        sName = dLocalData.get('name')
        vSkillInfo = self.GetSkillInfo()
        vSkillInfo.sort(key = (lambda d: d['lv']), reverse = True)
        oView.CreateSkillList(vSkillInfo)
        oView.SetActiveSkill(self.m_iActiveSkillId, sName)
        oView.SetSelectItem(self.m_iActiveSkillId)

    
    def GetSkillInfo(self):
        vSkillInfo = []
        for dSkillBaseInfo in self.m_vSkillInfoList:
            dTmpSkillInfo = { }
            iSkillId = dSkillBaseInfo.get('id', 0)
            dTmpSkillInfo['id'] = iSkillId
            iSkillLv = dSkillBaseInfo.get('lv')
            dTmpSkillInfo['lv'] = iSkillLv
            iPoint = dSkillBaseInfo.get('point')
            dTmpSkillInfo['point'] = iPoint
            dData = skilldata.GetData(iSkillId)
            dTmpSkillInfo['desc'] = None if dData else ''
            iSkillLv += 1
            iCost = (iSkillLv ** 3 * 0.3 - iSkillLv ** 2 * 9) + 1200
            if iSkillLv > 70:
                iCost = iCost * ((iSkillLv - 70) * 0.02 + 1)
            
            dTmpSkillInfo['progress'] = '%d/%d' % (iPoint, iCost)
            dTmpSkillInfo['info'] = skilldata.GetData(iSkillId)
            vSkillInfo.append(dTmpSkillInfo)
        
        return vSkillInfo

    
    def OnSelectSkillItem(self, iSkillID):
        LOG_DEBUG('--------\xc0\xb0\xac\xa3\xba\xde\xb2z\xac\xc9\xad\xb1\xa1A\xa7\xde\xaf\xe0\xac\xe3\xa8s\xa4\xc0\xad\xb6\xa1A\xbf\xef\xbe\xdc\xa7\xde\xaf\xe0--------', iSkillID)
        oView = self.GetView()
        oView.SetSelectItem(iSkillID)

    
    def OnClickActiveSkill(self, iSkillID):
        LOG_DEBUG('--------\xc0\xb0\xac\xa3\xba\xde\xb2z\xac\xc9\xad\xb1\xa1A\xa7\xde\xaf\xe0\xac\xe3\xa8s\xa4\xc0\xad\xb6\xa1A\xb3q\xaa\xbe\xaaA\xb0\xc8\xbe\xb9\xac\xe3\xa8s\xa7\xde\xaf\xe0--------', self.m_iActiveSkillId, iSkillID)
        if self.m_iActiveSkillId == iSkillID:
            return None
        
        import netgroup
        netgroup.C2SSetActiveSkill(iSkillID)

    
    def OnActiveSkill(self, pDataManager, iSkillID):
        LOG_DEBUG('--------\xc0\xb0\xac\xa3\xba\xde\xb2z\xac\xc9\xad\xb1\xa1A\xa7\xde\xaf\xe0\xac\xe3\xa8s\xa4\xc0\xad\xb6\xa1A\xaaA\xb0\xc8\xbe\xb9\xa8\xea\xb7s\xac\xe3\xa8s\xaa\xba\xa7\xde\xaf\xe0--------', iSkillID)
        self.m_iActiveSkillId = iSkillID
        oView = self.GetView()
        dLocalData = skilldata.GetData(iSkillID)
        sName = dLocalData.get('name')
        oView.SetActiveSkill(iSkillID, sName)
        oView.SetSelectItem(iSkillID)
