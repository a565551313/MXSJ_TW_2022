# pycdc 交叉复核产物 · script.fls entry 4772
# co_filename(原始)='script/maze/createmazemap.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4772.pyc (Python 2.5)

import random

def GetMazeMapDict(iSeed, iLength = 15, iWidth = 15, iCellNum = 3, iBranchNum = 5, lstBranchLen = [
    3,
    5], lstDistances = [
    4,
    7], iCellLength = 2, iCellWidth = 2):
    mazeObj = CBuildMap()
    mazeObj.Init(iSeed, iLength, iWidth, iCellNum, iBranchNum, lstBranchLen, lstDistances, iCellLength, iCellWidth)
    mazeObj.Build()
    return mazeObj.GetMapDict()


class CBuildMap(object):
    
    def __init__(self):
        self.m_Cell = []
        self.m_Length = 15
        self.m_Width = 15
        self.m_Distances = [
            4,
            6]
        self.m_CellLength = 2
        self.m_CellWidth = 2
        self.m_CellNum = 3
        self.m_Map = { }
        self.m_ChooseNode = []
        self.m_Path = []
        self.m_Err = False
        self.m_BranchNum = 5
        self.m_BranchLen = [
            3,
            5]

    
    def Init(self, iSeed, iLength = 15, iWidth = 15, iCellNum = 3, iBranchNum = 5, lstBranchLen = [
        3,
        5], lstDistances = [
        4,
        7], iCellLength = 2, iCellWidth = 2):
        self.m_Seed = iSeed
        self.m_Length = iLength
        self.m_Width = iWidth
        self.m_Distances = lstDistances
        self.m_CellLength = iCellLength
        self.m_CellWidth = iCellWidth
        self.m_CellNum = iCellNum
        self.m_BranchNum = iBranchNum
        self.m_BranchLen = lstBranchLen
        self.m_RandObj = random.Random()
        self.m_RandObj.seed(iSeed)

    
    def GetMapDict(self):
        return self.m_Map

    
    def Build(self):
        dMap = { }
        for i in xrange(self.m_Length - 4):
            dMap[i] = { }
            for j in xrange(self.m_Width - 4):
                dMap[i][j] = 0
            
        
        lstAllPath = []
        lstAllRoom = []
        dRoomDict = { }
        dRoomPos = { }
        lRoomPos = []
        for iRoom in xrange(1, self.m_CellNum + 1):
            iRoomIdx = 100 + iRoom
            if not dRoomDict:
                x = -(self.m_CellLength)
                y = self.GetRandom(0, self.m_Width - 4 - self.m_CellWidth)
                lRoomPos = self.BuildRoomPos(x, y)
                dRoomDict[iRoomIdx] = []
                for i, j in lRoomPos:
                    dMap[i][j] = iRoomIdx
                    dRoomDict[iRoomIdx].append((i, j))
                    dRoomPos[(i, j)] = iRoomIdx
                
            self.m_Length - 4
            iTrunkLen = self.GetRandom(self.m_Distances[0] + 2, self.m_Distances[1])
            bBuild = False
            lSrcPos = self.ShufferList(sorted(dRoomPos.keys()))
            for x1, y1 in lSrcPos:
                iSrcRoom = dRoomPos[(x1, y1)]
                (x0, y0) = dRoomDict[iSrcRoom][0]
                k1 = -(self.m_CellLength) if x1 > x0 else -1
                k2 = self.m_Length - 4 if y1 - y0 else -1
                for iHen in xrange(1, iTrunkLen + 2):
                    x2 = x1 + k1 * iHen
                    y2 = y1 + k2 * (iTrunkLen - iHen)
                    bValid = True
                    lRoomPos = self.BuildRoomPos(x2, y2)
                    for i, j in lRoomPos:
                        if not self.CheckDictVal(dMap, i, j, 0):
                            bValid = False
                            break
                            continue
                        0
                    
                    if not bValid:
                        continue
                    
                    bValid = True
                    (d1, d2) = sorted([
                        x2 + -k1 * self.m_Distances[1],
                        x2 + k1 * self.m_Distances[1]])
                    (d3, d4) = sorted([
                        y2 + -k2 * self.m_Distances[1],
                        y2 + k2 * self.m_Distances[1]])
                    for i in xrange(d1, d2):
                        for j in xrange(d3, d4):
                            if abs(i - x2) + abs(j - y2) > self.m_Distances[0]:
                                continue
                            
                            if self.IsCell(dMap, i, j):
                                bValid = False
                                break
                                continue
                        
                        if not bValid:
                            break
                            continue
                    
                    if not bValid:
                        continue
                    
                    bValid = True
                    for _ in xrange(iHen):
                        bValid = True
                        PathList = []
                        lRoute = self.ShufferList([
                            (1, 0)] * iHen + [
                            (0, 1)] * (iTrunkLen - iHen))
                        i = x1
                        j = y1
                        for r1, r2 in enumerate(lRoute):
                            i = i + k1 * r1
                            j = j + k2 * r2
                            if idx == 0:
                                if not self.ValidInserPos(dMap, i, j):
                                    bValid = False
                                    break
                                
                            elif self.CheckConnectPos(dMap, i, j):
                                bValid = False
                                break
                            
                            if not bValid:
                                break
                            
                            PathList.append((i, j))
                        
                        if bValid:
                            break
                            continue
                    
                    if not bValid:
                        continue
                    
                    bValid = True
                    iBlkVal = 300 + iRoom
                    for i, j in PathList:
                        dMap[i][j] = iBlkVal
                        lstAllPath.append((i, j))
                    
                    dRoomDict[iRoomIdx] = []
                    for i, j in lRoomPos:
                        dMap[i][j] = iRoomIdx
                        dRoomDict[iRoomIdx].append((i, j))
                        dRoomPos[(i, j)] = iRoomIdx
                        lstAllRoom.append((i, j))
                    
                    bBuild = True
                
                if bBuild:
                    break
                    continue
            
            if not bBuild:
                break
                continue
        
        if len(dRoomDict) < self.m_CellNum:
            self.m_Err = True
        else:
            dMap = self.BuildBranch(dMap, lstAllPath, lstAllRoom)
            self.m_Map = self.OutSideMap(dMap)
            self.m_Room = self.OutSideRoom(dRoomDict)

    
    def OutSideRoom(self, dRoomDict):
        dNewRoom = { }
        for iRoomIdx, lstRoom in dRoomDict.items():
            dNewRoom[iRoomIdx] = []
            for i, j in lstRoom:
                dNewRoom[iRoomIdx].append((i + 2, j + 2))
            
        
        return dNewRoom

    
    def OutSideMap(self, dMap):
        dNewMap = { }
        for i in xrange(self.m_Length):
            dNewMap[i] = { }
            for j in xrange(self.m_Width):
                if i <= i:
                    pass
                elif i < self.m_Length - 2:
                    if j <= j:
                        pass
                    elif j < self.m_Width - 2:
                        dNewMap[i][j] = dMap[i - 2][j - 2]
                        continue
                dNewMap[i][j] = 0
            
        
        return dNewMap

    
    def BuildBranch(self, dMap, lstAllPath, lstAllRoom):
        lstAllNode = self.ShufferList(lstAllPath + lstAllRoom)
        BranchNum = 0
        iNum = 0
        lstAllBranch = []
        for k1, k2 in lstAllNode:
            iNum += 1
            lstBranch = []
            for _ in xrange(self.m_BranchLen[1]):
                bTrass = False
                bBreak = False
                bBranch = False
                lstDir = self.ShufferList([
                    (k1 + 1, k2),
                    (k1, k2 + 1),
                    (k1 - 1, k2),
                    (k1, k2 - 1)])
                for i, j in lstDir:
                    if i < 0 and j < 0 and i >= self.m_Length - 4 and j >= self.m_Width - 4 or (i, j) in lstBranch:
                        continue
                    
                    if len(lstBranch) == 0:
                        if not self.ValidInserPos(dMap, i, j):
                            continue
                        else:
                            bBranch = True
                    elif not self.CheckConnectPos(dMap, i, j) and self.CheckBranchPos(lstBranch, i, j):
                        bBranch = True
                    else:
                        bBranch = False
                    if bBranch:
                        lstBranch.append((i, j))
                        k1 = i
                        k2 = j
                        bTrass = True
                        break
                        continue
                
                if bTrass:
                    continue
                    continue
            
            if len(lstBranch) >= self.m_BranchLen[0]:
                BranchNum += 1
                for x, y in lstBranch:
                    dMap[x][y] = 400 + BranchNum
                    lstAllBranch.append((x, y))
                
                if BranchNum >= self.m_BranchNum:
                    break
                
            BranchNum >= self.m_BranchNum
        
        return dMap

    
    def CheckBranchPos(self, lstBranch, i, j):
        iNum = 0
        for x, y in [
            (i + 1, j),
            [
                i,
                j + 1],
            [
                i - 1,
                j],
            [
                i,
                j - 1]]:
            if (x, y) in lstBranch:
                iNum += 1
                continue
        
        if iNum >= 2:
            return False
        
        return True

    
    def Print(self, dMap):
        sMsg = ''
        for j in xrange(self.m_Width - 1, -1, -1):
            for i in xrange(self.m_Length):
                iNum = dMap[i][j]
                if iNum / 100 == 1:
                    sMsg += '   '
                    continue
                if iNum / 100 == 3:
                    sMsg += '   '
                    continue
                if iNum / 100 == 4:
                    sMsg += '   '
                    continue
                sMsg += ' * '
            
            sMsg += '\n'
        
        return sMsg

    
    def IsCell(self, dMap, i, j):
        if i in dMap and j in dMap[i] and dMap[i][j] > 100:
            return 1
        
        return 0

    
    def ValidInserPos(self, dMap, i, j):
        dRound = { }
        idx = 0
        for i2 in (i - 1, i, i + 1):
            for j2 in (j - 1, j, j + 1):
                idx += 1
                if i2 == i and j2 == j:
                    continue
                
                if self.IsExploitPos(dMap, i2, j2):
                    dRound[idx] = 1
                    continue
                dRound[idx] = 0
            
        
        for tIndex in ((1, 2, 4), (2, 3, 6), (4, 7, 8), (6, 8, 9)):
            if dRound[tIndex[0]] and dRound[tIndex[1]] and dRound[tIndex[2]]:
                return False
                continue
        
        return True

    
    def BuildRoomPos(self, x, y):
        lRoomPos = []
        for i in xrange(x, x + self.m_CellLength):
            for j in xrange(y, y + self.m_CellWidth):
                lRoomPos.append((i, j))
            
        
        return lRoomPos

    
    def ShufferList(self, NodeList):
        iNum = len(NodeList)
        for i in xrange(iNum):
            iPos = self.GetRandom(0, iNum - 1)
            val = NodeList[iPos]
            NodeList[iPos] = NodeList[i]
            NodeList[i] = val
        
        return NodeList

    
    def CheckDictVal(self, dMap, i, j, *args):
        if i in dMap and j in dMap[i] and dMap[i][j] in args:
            return 1
        
        return 0

    
    def CheckDictValUnEqual(self, dMap, i, j, *args):
        if i in dMap and j in dMap[i] and dMap[i][j] not in args:
            return 1
        
        return 0

    
    def IsExploitPos(self, dMap, i, j):
        if self.CheckDictValUnEqual(dMap, i, j, 0):
            return 1
        
        return 0

    
    def CheckConnectPos(self, dMap, i, j):
        for i2, j2 in [
            (i - 1, j),
            (i + 1, j),
            (i, j - 1),
            (i, j + 1)]:
            if self.IsExploitPos(dMap, i2, j2):
                return True
                continue
        
        return False

    
    def GetRandom(self, iMin, iMax):
        iNum = self.m_RandObj.randint(iMin, iMax)
        return iNum
