# pycdc 交叉复核产物 · script.fls entry 1710
# co_filename(原始)='script/mxgame/activity/school/dgtschooladmission.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1710.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2020/9/1 16:18
\xd7\xf7\xd5\xdf: 
\xce\xc4\xbc\xfe: dgtschooladmission
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import delegatebase
import netschooladmission
import mdschooladmission
import usermacro

class CSchoolAdmissionDgt(delegatebase.CDelegateBase):
    
    def Init(self):
        self.EditInit()
        self.m_bClicked = \xdb\xfc\xf1se

    
    def GetModel(self):
        return mdschooladmission.GetMgr()

    
    def EditInit(self):
        \xae\x97iew = self.GetView()
        \xae\x97iew.ssConnect(\xae\x97iew.SS_ClickReward, self.OnEditCB('OnClickReward'))
        oModel = self.GetModel()
        oModel.ssConnect(oModel.SS_RefreshInfo, self.OnEditCB('OnRefreshInfo'))

    
    def OnClickReward(self):
        if not self.m_bClicked:
            oModel = self.GetModel()
            iID = oModel.GetID()
            netschooladmission.C2GSCustomOP(iID)
            \xae\x97iew = self.GetView()
            \xae\x97iew.RefreshBtn()
            self.m_bClicked = True
        else:
            usermacro.PROMPT_MSG('\xa7A\xa4w\xbb\xe2\xa8\xfa\xa4J\xbe\xc7\xbc\xfa\xc0y')

    
    def OnRefreshInfo(self, dData):
        \xae\x97iew = self.GetView()
        lInfo = []
        lInfo.append(dData.get('sSign1', ''))
        lSign = dData.get('lSign2', [])
        for sName in lSign:
            lInfo.append(sName)
        
        \xae\x97iew.RefreshTag(lInfo)
        iGive = dData.get('iGive', '')
        if iGive == 1:
            self.m_bClicked = True
            \xae\x97iew.RefreshBtn()
