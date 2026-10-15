# pycdc 交叉复核产物 · script.fls entry 4613
# co_filename(原始)='script/mxgame/shitu/delegate/dgtstshouyetudi.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4613.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: ${DATE} ${TIME}
\xd7\xf7\xd5\xdf: ${AuthorName}
\xce\xc4\xbc\xfe: ${NAME}
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import delegatebase
import mdshitu1
import netshitu1
import shitudefine

class CShouYeTudiDgt(delegatebase.CDelegatePaginationBase):
    
    def __init__(self, oView):
        self.m_bShowTipsFlag = False
        delegatebase.CDelegatePaginationBase.__init__(self, oView)

    
    def Init(self):
        oModel = mdshitu1.GetTudiShouyeModel()
        oModel.ssConnect(oModel.SS_TudiShouyeI( oChange, self.OnTudiShouyeInfoChange)
        oView = self.GetView()
        oView.ssConnect(oView.SS_JoinTask, self.OnJoinTask)

    
    def OnTudiShouyeInfoChange(self, iDegree, iDegreeMax, dTaskInfoList):
        oView = self.GetView()
        oView.SetExp(iDegree, iDegreeMax)
        dTaskList = self.ProcessTaskList(dTaskInfoList)
        oView.ShowTaskList(dTaskList)

    
    def OnJoinTask(self, iTaskID):
        import shitutaskdata
        import wrapui
        import autofindpath
        import tasktypedata
        dTaskInfo = shitutaskdata.GetTaskInfo(iTaskID)
        if dTaskInfo is None:
            return None
        
        if dTaskInfo['sSponsor'] == '\xaev\xa4\xf7':
            (_, sLink, _) = tasktypedata.GetData(3)
        else:
            sLink = dTaskInfo['sSponsor']
        dLinkInfo = wrapui.GetLinkDct(sLink)
        tData = wrapui.Split(dLinkInfo.\xe2\xe0t('context', ''))
        if len(tData) != 6:
            return None
        
        (sNpcName, _, sMapName, x, y, _) = tData
        x = int(x)
        y = int(y)
        autofindpath.AutoFind(sMapName, (x, y), sNpcName = sNpcName)

    
    def ShowExpProcessInfo(self):
        LOG_DEBUG('\xc5\xe3\xa5\xdc\xb6i\xab\xd7\xc3B\xa5~\xabH\xae\xa7')
        import hero
        netshitu1.C2SGetDegressExInfo(hero.GetRealID())
        self.m_bShowTipsFlag = True

    
    def OnDegreeExInfoChange(self, iPlayerID, iCurXLExp, iXLExpMax, iActive):
        import hero
        if hero.GetRealID() != iPlayerID:
            self.ClearExpProcessInfo()
            return None
        
        iLv = hero.GetProp('m_Grade', 0)
        sColorLst = [
            '#Y',
            '#G']
        txt1 = '\xb7\xed\xabe\xb5\xa5\xaf\xc5:%s%d/60#n#r' % (sColorLst[iLv >= 60], iLv)
        txt2 = '\xad\xd7\xb7\xd2\xb8g\xc5\xe7:%s%d/%d#n#r' % (sColorLst[iCurXLExp >= iXLExpMax], iCurXLExp, iXLExpMax)
        txt3 = '\xac\xa1\xc5D\xab\xd7:%s%d/3000#n#r' % (sColorLst[iActive >= 3000], iActive)
        sTips = '\r[\rs%s' % (txt1, txt2, txt3)
        self.GetView().ShowExpTips(sTips)

    
    def ClearExpProcessInfo(self):
        LOG_DEBUG('\xb2M\xb2z\xb6i\xab\xd7\xc3B\xa5~\xabH\xae\xa7')
        self.m_bShowTipsFlag = False
        oView = self.GetView()
        if not oView:
            return None
        
        oView.ClearExpTips()

    
    def ProcessTaskList(self, dTaskInfoList):
        import shitutaskdata
        dResultList = []
        for dTaskInfo in dTaskInfoList:
            iTaskID = dTaskInfo[shitudefine.KEY_TASK_ID]
            dTmp = shitutaskdata.GetTaskInfo(iTaskID)
            if not dTmp:
                continue
            
            if dTaskInfo[shitudefine.KEY_TASK_CUR] >= dTaskInfo[shitudefine.KEY_TASK_SUM]:
                continue
            
            dInfo = { }
            dInfo[shitudefine.KEY_PLAYER_NAME] = dTaskInfo[shitudefine.KEY_PLAYER_NAME]
            dInfo[shitudefine.KEY_TASK_ID] = iTaskID
            dInfo[shitudefine.KEY_TASK_CUR] = dTaskInfo[shitudefine.KEY_TASK_CUR]
            dInfo[shitudefine.KEY_TASK_SUM] = dTaskInfo[shitudefine.KEY_TASK_SUM]
            dInfo[shitudefine.KEY_TASK_TITLE] = dTmp['sTitle']
            dInfo[shitudefine.KEY_DESC] = dTmp['sDesc']
            dInfo[shitudefine.KEY_TASK_REWARD] = dTmp['sReward']
            dInfo[shitudefine.KEY_TASK_TARGET] = dTmp['sTarget']
            dResultList.append(dInfo)
        
        return dResultList
