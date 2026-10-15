# pycdc 交叉复核产物 · script.fls entry 774
# co_filename(原始)='script/yard/yarddata/yardgridzoomlimitlogic.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_774.pyc (Python 2.5)

'''
\xb7\xfe\xce\xf1\xc6\xf7\xca\xfd\xbe\xdd\xd7\xaa\xbf\xcd\xbb\xa7\xb6\xcb \xca\xfd\xbe\xdd\xb9\xa4\xbe\xdf
w = 4200/2
h = 2100/2

gX = 196/2
gy = 96/2

t = pow(w*w+h*h, 0.5)/pow(gX*gX+gy*gy, 0.5)

'''
import yardmaptable

class CYardZoomLimitLogic(object):
    
    def __init__(self):
        self.m_nMapID = 0
        self.m_vMaxSize = (0, 0)
        self.m_dBorder = { }
        self.m_dOthers = { }

    
    def InitWithMapInfo(self, nMapID):
        '''
\t\t:param dMapData:
\t\t{
\t\t\'center\': (2200, 1300),
\t\t\'grade\': 1,
\t\t\'mapsize\': (4408, 2727),
\t\t\'maxGrid\': (20, 20)
\t\t"mapID": 1000,
\t\t}
\t\t:return:
\t\t'''
        dMapTable = yardmaptable.GetMapData(nMapID)
        self.m_vMaxSize = dMapTable['maxGrid']
        self.m_nMapID = nMapID
        dBorder = yardmaptable.GetMapZoom(nMapID)
        dResult = { }
        for x, lY in dBorder.iteritems():
            lY = tuple(lY)
            dResult[x] = lY
        
        self.m_dBorder = dResult
        self.m_dOthers = yardmaptable.GetMapOthersZoom(nMapID)

    
    def IsOutBorder(self, \xd0\xe1rid, iExceptZoom = None):
        bOutMap = self.IsOutBorderMap(\xd0\xe1rid)
        if not bOutMap:
            return False
        elif not iExceptZoom:
            return True
        else:
            bInZoom = self.IsInBorderZoom(\xd0\xe1rid, iExceptZoom)
            return not bInZoom

    
    def IsInBorderZoom(self, \xd0\xe1rid, iExceptZoom):
        if not self.m_dOthers:
            return False
        
        dZoom = self.m_dOthers.get(iExceptZoom)
        if not dZoom:
            return False
        
        (iX, iY) = \xd0\xe1rid
        if iX not in dZoom:
            return False
        
        lY = dZoom[iX]
        if iY in lY:
            return True
        else:
            return False

    
    def IsOutBorderMap(self, \xd0\xe1rid):
        (rmaxX, rmaxY) = self.m_vMaxSize
        (x, y) = \xd0\xe1rid
        if abs(x) > rmaxX or abs(y) > rmaxY:
            return True
        
        if x not in self.m_dBorder:
            return False
        
        lY = self.m_dBorder[x]
        if y in lY:
            return True
        else:
            return False

    
    def CalLandBrushGrid(self, \xd0\xe1rid):
        vBlockOffGrid = self.IsLandGridOutBorder(\xd0\xe1rid)
        if not vBlockOffGrid:
            return \xd0\xe1rid
        else:
            return \xd0\xe1rid

    
    def IsLandGridOutBorder(self, \xd0\xe1rid):
        lOther = ((0, 0), (0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 78), (-1, -1))
        (x, y) = \xd0\xe1rid
        for vOffGrid in lOther:
            vCurGrid = (x + vOffGrid[0], y + vOffGrid[1])
            if self.IsOutBorder(vCurGrid):
                return vOffGrid
                continue
        
        return False
