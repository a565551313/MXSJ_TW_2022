# pycdc 交叉复核产物 · script.fls entry 3020
# co_filename(原始)='script/wrap/wrapmath.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3020.pyc (Python 2.5)

import math

def LimitRange(x, minx, maxx):
    x = max(minx, x)
    x = min(maxx, x)
    return x


def LimitInRect(x, y, upperLeftx, upperLefty, lowerRightx, lowerRighty):
    x = LimitRange(x, upperLeftx, lowerRightx)
    y = LimitRange(y, upperLefty, lowerRighty)
    return (x, y)


def GetTriangleArea(x1, y1, x2, y2, x3, y3):
    a = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    b = math.sqrt((x3 - x2) ** 2 + (y3 - y2) ** 2)
    c = math.sqrt((x3 - x1) ** 2 + (y3 - y1) ** 2)
    p = (a + b + c) / 2
    z = p * (p - a) * (p - b) * (p - c)
    if z < 0:
        area = 0
    else:
        area = math.sqrt(z)
    return area


def IsPointInQuad(px, py, x1, y1, x2, y2, x3, y3, x4, y4):
    t1 = GetTriangleArea(px, py, x1, y1, x2, y2)
    t2 = GetTriangleArea(px, py, x3, y3, x2, y2)
    t3 = GetTriangleArea(px, py, x4, y4, x3, y3)
    t4 = GetTriangleArea(px, py, x4, y4, x1, y1)
    q1 = GetTriangleArea(x1, y1, x2, y2, x3, y3)
    q2 = GetTriangleArea(x1, y1, x3, y3, x4, y4)
    return abs(q1 + q2 - (t1 + t2 + t3 + t4)) < 0.01


def CalculatePoint(sx, sy, ex, ey, m):
    l = math.sqrt((ex - sx) * (ex - sx) + (ey - sy) * (ey - sy))
    if l < m:
        return None
    
    if sy == ey:
        if sx > ex:
            x1 = sx - m
            y1 = sy
            x2 = sx - m
            y2 = sy
        else:
            x1 = sx + m
            y1 = sy
            x2 = sx + m
            y2 = sy
    elif sx == ex:
        if sy > ey:
            x1 = sx
            y1 = sy - m
            x2 = sx
            y2 = sy - m
        else:
            x1 = sx
            y1 = sy + m
            x2 = sx
            y2 = sy + m
    else:
        x = 1 * (ex - sx)
        y = 1 * (ey - sy)
        n = x * x / (y * y) + 1
        b1 = math.sqrt(m * m / n)
        a1 = (x / y) * b1
        x1 = a1 + sx
        y1 = b1 + sy
        b2 = -1 * b1
        a2 = -1 * a1
        x2 = a2 + sx
        y2 = b2 + sy
    minx = min(ex, sx)
    maxx = max(ex, sx)
    miny = min(ey, sy)
    maxy = max(ey, sy)
    if x1 <= x1:
        pass
    elif x1 <= maxx:
        if y1 <= y1:
            pass
        elif y1 <= maxy:
            return (int(x1), int(y1))
        elif x2 <= x2:
            pass
        elif x2 <= maxx:
            if y2 <= y2:
                pass
            elif y2 <= maxy:
                return (int(x2), int(y2))
            

CHINESE_NEGATIVE = '\xadt'
CHINESE_ZERO = '\xb9s'
CHINESE_DIGITS = [
    '',
    '\xa4@',
    '\xa4G',
    '\xa4T',
    '\xa5|',
    '\xa4\xad',
    '\xa4\xbb',
    '\xa4C',
    '\xa4K',
    '\xa4E']
CHINESE_UNITS = [
    '',
    '\xa4Q',
    '\xa6\xca',
    '\xa4d']
CHINESE_GROUP_UNITS = [
    '',
    '\xb8U',
    '\xbb\xf5',
    '\xa5\xfc']

def IntNumberToSmallChineseStr(number):
    if number == 0:
        return CHINESE_ZERO
    
    combList = []
    if number < 0:
        combList.append(CHINESE_NEGATIVE)
    
    number = abs(number)
    digitList = []
    while number != 0:
        (number, lastDigit) = divmod(number, 10)
        digitList.append(lastDigit)
    digitList.reverse()
    length = len(digitList)
    groupIsZero = True
    needZero = False
    for index, digit in enumerate(digitList):
        position = length - 1 - index
        unit = position % len(CHINESE_UNITS)
        group = position / len(CHINESE_UNITS)
        if digit != 0:
            if needZero:
                combList.append(CHINESE_ZERO)
            
            if (digit != 1 and unit != 1 and not groupIsZero or group == 0) and needZero:
                combList.append(CHINESE_DIGITS[digit])
            
            combList.append(CHINESE_UNITS[unit])
        
        if groupIsZero:
            pass
        groupIsZero = digit == 0
        if unit == 0 and not groupIsZero:
            combList.append(CHINESE_GROUP_UNITS[group])
        
        if not digit == 0 and unit != 0:
            pass
        needZero = groupIsZero
        if unit == 0:
            groupIsZero = True
            continue
    
    return ''.join(combList)


def PtInPolygon(dPoint, tPolygon):
    '''
\t\xb1q\xaaA\xb0\xc8\xbe\xb9\xb7h\xaa\xba\xadp\xba\xe2\xa4@\xad\xd3\xc2I\xacO\xa7_\xa6b\xa4@\xad\xd3\xa6h\xc3\xe4\xa7\xce\xa4\xa4\xaa\xba\xba\xe2\xaak

\t\xaeg\xbdu\xaak\xa8D\xc2I\xa6b\xa6h\xc3\xe4\xa7\xce\xa4\xba
\t\xb9LP\xc2I\xa6V\xa5k\xa7@\xa5\xad+\xa6\xe6\xa9\xf3X\xb6b\xaa\xba\xaeg\xbdu
\t\xa8D\xb8\xd3\xaa\xbd\xbdu\xbbP\xa6h\xc3\xe4\xa7\xce\xaa\xba\xa5\xe6\xc2I\xad\xd3\xbc\xc6
\t\xb5\xb2\xaaG\xac\xb0\xa9_\xbc\xc6\xabh\xa6b\xa6h\xc3\xe4\xa7\xce\xa4\xba\xa1A\xb0\xb8\xbc\xc6\xa6b\xa6h\xc3\xe4\xa7\xce\xa5~
\t'''
    (x, y) = dPoint
    iCount = len(tPolygon)
    iCross = 0
    for i in xrange(iCount):
        (x1, y1) = tPolygon[i]
        (x2, y2) = tPolygon[(i + 1) % iCount]
        if y1 == y2:
            continue
        
        if y <= y:
            pass
        elif not y < max(y1, y2):
            continue
        
        if x * (y2 - y1) * (y2 - y1) < ((y - y1) * (x2 - x1) + x1 * (y2 - y1)) * (y2 - y1):
            iCross += 1
            continue
        min(y1, y2)
    
    return iCross % 2


def GetPointTypeInLine(x1, y1, x2, y2, fPointX, fPointY):
    '''
\t\xa7P\xc2_\xc2I\xa6b\xbdu\xa4W\xaa\xba\xa6\xec\xb8m
\t:param x1: \xbdu\xacq\xb0_\xa9lx
\t:param y1: \xbdu\xacq\xb0_\xa9ly
\t:param x2: \xbdu\xacq\xb5\xb2\xa7\xf4x
\t:param y2: \xbdu\xacq\xb5\xb2\xa7\xf4y
\t:param fPointX: \xa7P\xc2_\xc2Ix
\t:param fPointY: \xa7P\xc2_\xc2Iy
\t:return: d < 0, \xc2I\xa6b\xaa\xbd\xbdu\xa5\xaa\xb0\xbc;d = 0\xa1A\xc2I\xa6b\xaa\xbd\xbdu\xa4W;d > 0, \xc2I\xa6b\xaa\xbd\xbdu\xa5k\xb0\xbc
\t'''
    x1 = float(x1)
    y1 = float(y1)
    x2 = float(x2)
    y2 = float(y2)
    a = y2 - y1
    b = x1 - x2
    c = x2 * y1 - x1 * y2
    return a * fPointX + b * fPointY + c


def IsCircleIntersectLineSeg(fCenterX, fCenterY, fRaduis, x1, y1, x2, y2):
    '''
\t\xb6\xea\xbbP\xbdu\xacq\xb8I\xbc\xb2\xc0\xcb\xb4\xfa
\t:param fCenterX: \xb6\xea\xa4\xdfx
\t:param fCenterY: \xb6\xea\xa4\xdfy
\t:param fRaduis: \xa5b\xae|
\t:param x1: \xbdu\xacq\xb0_\xa9lx
\t:param y1: \xbdu\xacq\xb0_\xa9ly
\t:param x2: \xbdu\xacq\xb5\xb2\xa7\xf4x
\t:param y2: \xbdu\xacq\xb5\xb2\xa7\xf4y
\t:return:
\t'''
    fCenterX = float(fCenterX)
    fCenterY = float(fCenterY)
    fRaduis = float(fRaduis)
    x1 = float(x1)
    y1 = float(y1)
    x2 = float(x2)
    y2 = float(y2)
    vx1 = fCenterX - x1
    vy1 = fCenterY - y1
    vx2 = x2 - x1
    vy2 = y2 - y1
    fLen = math.sqrt(vx2 * vx2 + vy2 * vy2)
    vx2 /= fLen
    vy2 /= fLen
    u = vx1 * vx2 + vy1 * vy2
    x0 = 0
    y0 = 0
    if u <= 0:
        x0 = x1
        y0 = y1
    elif u >= fLen:
        x0 = x2
        y0 = y2
    else:
        x0 = x1 + vx2 * u
        y0 = y1 + vy2 * u
    return (fCenterX - x0) * (fCenterY - x0) + (fCenterY - y0) * (fCenterY - y0) <= fRaduis * fRaduis


def IsCircleIntersectFan(x, y, r, x1, y1, x2, y2, theta):
    '''
\t\xa7P\xc2_\xb6\xea\xbbP\xae\xb0\xa7\xce\xacO\xa7_\xac\xdb\xa5\xe6
\t:param x: \xb6\xea\xa4\xdf
\t:param y: \xb6\xea\xa4\xdf
\t:param r: \xa5b\xae|
\t:param x1: \xae\xb0\xa7\xce\xb6\xea\xa4\xdf
\t:param y1: \xae\xb0\xa7\xce\xb6\xea\xa4\xdf
\t:param x2: \xae\xb0\xa7\xce\xa5\xbf\xabe\xa4\xe8\xb3\xcc\xbb\xb7\xc2I
\t:param y2: \xae\xb0\xa7\xce\xa5\xbf\xabe\xa4\xe8\xb3\xcc\xbb\xb7\xc2I
\t:param theta: \xae\xb0\xa7\xce\xa7\xa8\xa8\xa4\xa9\xb7\xab\xd7\xad\xc8(0,pi)
\t:return:
\t'''
    vx = x2 - x1
    vy = y2 - y1
    iFanR = math.sqrt(vx * vx + vy * vy)
    if (x - x1) * (x - x1) + (y - y1) * (y - y1) > (iFanR + r) * (iFanR + r):
        return False
    
    h = theta * 0.5
    if not math.cos(h):
        pass
    s = math.sin(h)
    x3 = x1 + (vx * c - vy * s)
    y3 = y1 + vx * s + vy * c
    x4 = x1 + vx * c + vy * s
    y4 = y1 + -vx * s + vy * c
    d1 = GetPointTypeInLine(x, y, x1, y1, x3, y3)
    d2 = GetPointTypeInLine(x, y, x4, y4, x1, y1)
    if d1 >= 0 and d2 >= 0:
        return True
    
    if IsCircleIntersectLineSeg(x, y, r, x1, y1, x3, y3):
        return True
    
    if IsCircleIntersectLineSeg(x, y, r, x1, y1, x4, y4):
        return True
    
    return False


class CVector(object):
    
    class CVectorIterator(object):
        
        def __init__(self, data):
            self.m_lstData = data
            self.m_iOffset = 0

        
        def next(self):
            if self.m_iOffset >= len(self.m_lstData):
                raise StopIteration('end')
            
            item = self.m_lstData[self.m_iOffset]
            self.m_iOffset += 1
            return item


    
    def __init__(self, lst = ()):
        import misc
        if type(lst) != list and type(lst) != tuple and type(lst) != set:
            raise 'type mismatched: CVector need set/list/tuple, but %s given' % type(lst)
        
        self.m_iLength = len(lst)
        self.m_lstData = misc.DeepCopy(list(lst))

    
    def append(self, iVal):
        if type(iVal) != int and type(iVal) != float:
            raise 'type mismatched: CVector need int/float value, but %s given' % type(iVal)
        
        self.m_lstData.append(iVal)
        self.m_iLength += 1

    
    def pop(self, iIdx):
        if iIdx >= self.m_iLength:
            raise 'Index out of range : %s' % iIdx
        
        self.m_lstData.pop(iIdx)
        self.m_iLength -= 1

    
    def data(self):
        import misc
        return misc.DeepCopy(self.m_lstData)

    
    def __add__(self, other):
        if type(other) == type(self):
            if len(self) != len(other):
                raise 'list length mismatched: %s and %s' % (len(self), len(other))
            
            oRes = CVector()
            for iIdx in range(len(self)):
                oRes.append(self.m_lstData[iIdx] + other.m_lstData[iIdx])
            
            return oRes
        elif type(other) == float or type(other) == int:
            oRes = CVector()
            for iIdx in range(len(self)):
                oRes.append(self.m_lstData[iIdx] + other)
            
        return oRes

    
    def __radd__(self, other):
        return self + other

    
    def __mul__(self, other):
        if type(other) == type(self):
            if len(self) != len(other):
                raise 'list length mismatched: %s and %s' % (len(self), len(other))
            
            oRes = CVector()
            for iIdx in range(len(self)):
                oRes.append(self.m_lstData[iIdx] * other.m_lstData[iIdx])
            
        elif type(other) != int and type(other) != float:
            raise 'type mismatched: type %s and type %s' % (type(self), type(other))
        
        oRes = CVector()
        for iIdx in range(len(self)):
            oRes.append(self.m_lstData[iIdx] * other)
        
        return oRes

    
    def __div__(self, other):
        if type(other) == type(self):
            if len(self) != len(other):
                raise 'list length mismatched: %s and %s' % (len(self), len(other))
            
            oRes = CVector()
            for iIdx in range(len(self)):
                oRes.append(self.m_lstData[iIdx] / other.m_lstData[iIdx])
            
        elif type(other) != int and type(other) != float:
            raise 'type mismatched: type %s and type %s' % (type(self), type(other))
        
        oRes = CVector()
        for iIdx in range(len(self)):
            oRes.append(self.m_lstData[iIdx] / other)
        
        return oRes

    
    def __sub__(self, other):
        return self + -other

    
    def __rsub__(self, other):
        return -self + other

    
    def __rdiv__(self, other):
        if type(other) == type(self):
            if len(self) != len(other):
                raise 'list length mismatched: %s and %s' % (len(self), len(other))
            
            oRes = CVector()
            for iIdx in range(len(self)):
                oRes.append(other.m_lstData[iIdx] / self.m_lstData[iIdx])
            
        elif type(other) != int and type(other) != float:
            raise 'type mismatched: type %s and type %s' % (type(self), type(other))
        
        oRes = CVector()
        for iIdx in range(len(self)):
            oRes.append(other / self.m_lstData[iIdx])
        
        return oRes

    
    def __rmul__(self, other):
        return self * other

    
    def __len__(self):
        return self.m_iLength

    
    def __neg__(self):
        oRes = CVector()
        for iIdx in range(self.m_iLength):
            oRes.append(-self.m_lstData[iIdx])
        
        return oRes

    
    def __getitem__(self, iIdx):
        return self.m_lstData[iIdx]

    
    def __setitem__(self, key, value):
        self.m_lstData[key] = value
        return value

    
    def __iter__(self):
        return CVector.CVectorIterator(self.m_lstData)

    
    def __abs__(self):
        import math
        fSum = 0
        for val in self.m_lstData:
            fSum = val * val
        
        return math.sqrt(fSum)

    
    def DeepCopy(self):
        return CVector(self.m_lstData)



def Round(oVector):
    oTmp = oVector.DeepCopy()
    for iIdx in range(len(oTmp)):
        oTmp[iIdx] = int(round(oTmp[iIdx]))
    
    return oTmp


def OneNorm(oVector):
    iRes = 0
    for iVal in oVector:
        iRes += abs(iVal)
    
    return iRes


def Test():
    (x1, y1) = (0, 0)
    (x2, y2) = (2, 2)
    (fPointX, fPointY) = (1, 1)
    print GetPointTypeInLine(x1, y1, x2, y2, fPointX, fPointY)
    (x1, y1) = (0, 0)
    (x2, y2) = (2, 2)
    (fPointX, fPointY) = (1, 0.5)
    print GetPointTypeInLine(x1, y1, x2, y2, fPointX, fPointY)
    (x1, y1) = (0, 0)
    (x2, y2) = (2, 2)
    (fPointX, fPointY) = (1, 1.5)
    print GetPointTypeInLine(x1, y1, x2, y2, fPointX, fPointY)
    print '====================='
    (fCenterX, fCenterY) = (0, 0)
    fRaduis = 2
    (x1, y1) = (0.5, 0.5)
    (x2, y2) = (-0.5, 0.5)
    print IsCircleIntersectLineSeg(fCenterX, fCenterY, fRaduis, x1, y1, x2, y2)
    (fCenterX, fCenterY) = (0, 0)
    fRaduis = 2
    (x1, y1) = (-0.5, 0.5)
    (x2, y2) = (0.5, 0.5)
    print IsCircleIntersectLineSeg(fCenterX, fCenterY, fRaduis, x1, y1, x2, y2)
    (fCenterX, fCenterY) = (0, 0)
    fRaduis = 2
    (x1, y1) = (-5, 1)
    (x2, y2) = (5, 1)
    print IsCircleIntersectLineSeg(fCenterX, fCenterY, fRaduis, x1, y1, x2, y2)
    (fCenterX, fCenterY) = (0, 0)
    fRaduis = 2
    (x1, y1) = (-5, 5)
    (x2, y2) = (5, 5)
    print IsCircleIntersectLineSeg(fCenterX, fCenterY, fRaduis, x1, y1, x2, y2)
