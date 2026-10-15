# pycdc 交叉复核产物 · script.fls entry 3303
# co_filename(原始)='script/yard/yarddata/yarduploaddatalogic.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_3303.pyc (Python 2.5)

'''
\xcd\xa5\xd4\xba\xc9\xcf\xb4\xab\xca\xfd\xbe\xdd\xb5\xc4
\xd3\xc9\xd3\xda\xca\xfd\xbe\xdd\xb9\xfd\xb6\xe0\xa3\xba

\xbf\xcd\xbb\xa7\xb6\xcb \xb2\xbb\xc4\xdc\xb7\xd6\xb0\xfc\xcc\xab\xb6\xe0\xcb\xf9\xd2\xd4 \xb5\xc3\xb6\xa8\xca\xb1\xc9\xcf\xb4\xab

'''
import netyard
import timer
import yardviewsignal
import yards2ctools
import misc
UPLOAD_LEN = 20

class CYardUploadLogic(object):
    
    def CalLandChangedData(cls, dNewData, dOldData):
        dChangeData = { }
        for sKey, pValue in dNewData.iteritems():
            if not pValue:
                continue
            
            pOldValue = dOldData.get(sKey)
            if pOldValue != pValue:
                dChangeData[sKey] = pValue
                continue
        
        for sKey, pValue in dOldData.iteritems():
            if not pValue:
                continue
            
            pNewValue = dNewData.get(sKey)
            if not pNewValue:
                dChangeData[sKey] = None
                continue
        
        return dChangeData

    CalLandChangedData = classmethod(CalLandChangedData)
    
    def CalFurnitureChangedData(cls, dNewData, dOldData):
        lAddFur = []
        lDelFur = []
        for vGrid, lFur in dNewData.iteritems():
            lOldFur = dOldData.get(vGrid)
            if lFur == lOldFur:
                continue
            
            for pValue in lFur:
                if not lOldFur or pValue not in lOldFur:
                    pValue['vpos'] = vGrid
                    lAddFur.append(pValue)
                    continue
            
        
        lDel = []
        for vGrid, lFur in dOldData.iteritems():
            lNewFur = dNewData.get(vGrid)
            for pValue in lFur:
                if not lNewFur or pValue not in lNewFur:
                    pValue['vpos'] = vGrid
                    lDelFur.append(pValue)
                    continue
                import yardothers
                shapeID = pValue['shapeID']
                direct = pValue['direct']
                if not yardothers.CheckEditFurnitureHasDirect(shapeID, direct):
                    if pValue not in lDelFur:
                        lDelFur.append(pValue)
                        lDel.append(pValue)
                    
                pValue not in lDelFur
            
        
        LOG(lDel)
        return (lAddFur, lDelFur)

    CalFurnitureChangedData = classmethod(CalFurnitureChangedData)
    
    def __init__(self):
        self.m_nSumLen = 0
        self.m_lUpLoadQueue = []
        self.m_pTimer = None

    
    def IsUpLoading(self):
        if self.m_pTimer:
            return True
        else:
            return False

    
    def Clear(self):
        self.m_lUpLoadQueue = []
        self.m_nSumLen = 0
        self.ReleaseTimer()

    
    def AddEvent2Queue(self, pEvent, bEnd = False):
        if pEvent in self.m_lUpLoadQueue:
            return None
        
        if bEnd:
            self.m_lUpLoadQueue.insert(0, pEvent)
        else:
            self.m_lUpLoadQueue.append(pEvent)
        self.m_nSumLen = len(self.m_lUpLoadQueue)

    
    def PackLand2UpLoadQueue(self, dLand):
        if not dLand:
            return None
        
        nLen = len(dLand)
        nNum = (nLen + UPLOAD_LEN - 1) / UPLOAD_LEN
        lKey = dLand.\xc5\xcbys()
        for i in range(nNum):
            nStart = i * UPLOAD_LEN
            nEnd = min(nStart + UPLOAD_LEN, nLen)
            lTKey = lKey[nStart:nEnd]
            dData = { }
            for pKey in lTKey:
                pValue = dLand[pKey]
                dData[pKey] = pValue
            
            sData = yards2ctools.PackClientLandData(dData)
            pFunc = misc.Functor(netyard.C2SYardLandChanged, sData)
            self.m_lUpLoadQueue.append(pFunc)
        

    
    def ReleaseTimer(self):
        if self.m_pTimer:
            self.m_pTimer.Release()
            self.m_pTimer = None
        

    
    def StartUpLoad(self):
        self.ReleaseTimer()
        self.m_nSumLen = len(self.m_lUpLoadQueue)
        self.m_pTimer = timer.Timer(0.01, self.UpLoadDataLoop, -1, oRelayObj = self)

    
    def UpLoadDataLoop(self):
        if not self.m_lUpLoadQueue:
            self.ReleaseTimer()
            yardviewsignal.Emit(yardviewsignal.SS_YardUpLoad_StateChanged, self.m_nSumLen, len(self.m_lUpLoadQueue))
            return None
        
        pEvent = self.m_lUpLoadQueue.pop()
        print 'len:', pEvent.m_Func, len(self.m_lUpLoadQueue)
        pEvent()
        yardviewsignal.Emit(yardviewsignal.SS_YardUpLoad_StateChanged, self.m_nSumLen, len(self.m_lUpLoadQueue))
