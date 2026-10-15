# pycdc 交叉复核产物 · script.fls entry 4744
# co_filename(原始)='script/blacklist/verifygame/dgtverifygameyuanbao.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4744.pyc (Python 2.5)

import delegatebase
import mxv
import mxvdefines
import random
import timer
CREATE_TIME = 1
POS_TIME = 0.033
YUANBAOPRECENT = 7
YUANBAO_COUT = 25
WIN_YUANBAO_COUNT = 10
BOOM_CREATE_TIME = 4
BOOM_COUNT = 10

class CVerifyGameYuanbaoDelegate(delegatebase.CDelegateBase):
    
    def GetView(self):
        '''
\t\t:rtype: dlgverifygameyuanbao.CVerifyGameYuanbaoDialog
\t\t'''
        return delegatebase.CDelegateBase.GetView(self)

    
    def Init(self):
        self.m_oStartCreateTimer = None
        self.m_oCreateTimer = None
        self.m_oPosTimer = None
        oView = self.GetView()
        oView.ssConnect(oView.SS_ClickGameStart, self.OnGameStart)
        oView.ssConnect(oView.SS_ClickTable, self.OnPotChangePos)
        self.m_iYuanbaoCount = 0
        self.m_iBoomCount = 0
        self.m_iItemCurMaxID = 0
        self.m_bGameStart = False
        self.m_iPotPos = None
        self.m_dItems = { }
        self.m_iPotPos = 0
        self.m_iScore = 0
        oView.SetPointNum(0)
        oView.SetGameStart(False)

    
    def OnGameStart(self):
        if self.m_bGameStart:
            return None
        
        self.m_bGameStart = True
        self.GetView().SetGameStart(True)
        self.GetView().SetPotPos(0)
        if self.m_oStartCreateTimer:
            self.m_oStartCreateTimer.Release()
        
        self.m_oStartCreateTimer = timer.Timer(random.randint(0, 3), self.OnStartCreate, 0, self)

    
    def OnStartCreate(self):
        if self.m_oCreateTimer:
            self.m_oCreateTimer.Release()
        
        self.m_oCreateTimer = timer.Timer(CREATE_TIME, self.OnAddItem, -1, self)
        if self.m_oPosTimer:
            self.m_oPosTimer.Release()
        
        self.m_oPosTimer = timer.Timer(POS_TIME, self.OnPosChange, -1, self)

    
    def OnAddItem(self):
        if self.m_iYuanbaoCount >= YUANBAO_COUT:
            return None
        
        iPotPos = random.randint(0, 3)
        iType = random.randint(0, 10)
        dItem = {
            'iPotPos': iPotPos,
            'iType': iType,
            'iY': 0 }
        self.m_iItemCurMaxID += 1
        self.m_dItems[self.m_iItemCurMaxID] = dItem
        self.GetView().CreateItem(self.m_iItemCurMaxID, iType, iPotPos)

    
    def OnPosChange(self):
        lRemove = []
        oView = self.GetView()
        for iItemID, dItem in self.m_dItems.iteritems():
            dItem['iY'] += 1
            oView.SetItemYPosPercent(iItemID, dItem['iPotPos'], dItem['iY'])
            if dItem['iY'] >= 60 and dItem['iPotPos'] == self.m_iPotPos:
                lRemove.append(iItemID)
                continue
            if dItem['iY'] >= 100:
                lRemove.append(iItemID)
                continue
        
        bScoreChange = False
        for iItemID in lRemove:
            dItem = self.m_dItems[iItemID]
            if dItem['iPotPos'] == self.m_iPotPos:
                bScoreChange = True
            
            del self.m_dItems[iItemID]
            oView.RemoveItem(iItemID)
        
        if self.m_iScore < 0:
            self.m_iScore = 0
        
        if bScoreChange:
            oView.SetPointNum(self.m_iScore)
        
        if self.m_iScore >= WIN_YUANBAO_COUNT:
            self.OnGameEnd(True)
        elif not (self.m_dItems) and self.m_iYuanbaoCount >= YUANBAO_COUT:
            self.OnGameEnd(False)
        

    
    def OnGameEnd(self, bWin):
        if bWin:
            \xc0\xe6\xc2 = 1
        else:
            \xc0\xe6\xc2 = 0
        mxv.C2SAnswerComputation(mxvdefines.CHECKID_YUANBAO, self.GetView().GetSeed(), \xc0\xe6\xc2)
        self.GetView().CloseWindow()

    
    def OnPotChangePos(self, iPos):
        if not self.m_bGameStart:
            return None
        
        self.m_iPotPos = iPos
        self.GetView().SetPotPos(iPos)
