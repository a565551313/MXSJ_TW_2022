# pycdc 交叉复核产物 · script.fls entry 1536
# co_filename(原始)='script/yard/yardmap/view/yardextraeff.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1536.pyc (Python 2.5)

'''
extra eff
'''
import C_sys
import interface
import misc
import mapani
g_Ani = { }

def ModuleReset():
    global g_Ani
    g_Ani = { }


class CExtraEff(interface.CBaseObject):
    
    def __init__(self, oParent, sAniFile, sPackage = 'mapobject', bUseSprite = \xb9\x9e\x93se, bUseOffSet = \xb9\x9e\x93se, dExtend = None):
        interface.CBaseObject.__init__(self, oParent)
        self.m_oAniList = []
        self.m_bUseOffSet = bUseOffSet
        self.m_bUseSprite = bUseSprite
        self.m_dExtend = dExtend
        mapani.InitIfNeeed()
        self.LoadEff(sAniFile, sPackage)

    
    def LoadEff(self, sAniFileName, sPackage):
        self.m_oAniList = []
        sData = GetAniByPath(sAniFileName, sPackage)
        if not sData:
            return None
        
        sData = sData.strip().replace('\r\n', '\n')
        sLineLst = sData.split('\n')
        for sLine in sLineLst[2:]:
            tInfo = sLine.strip().split(' ')
            if len(tInfo) == 3:
                (iAniIdx, iX, iY) = map(int, tInfo)
                oAni = self.CreateEffAni(iAniIdx, iX, iY)
                self.m_oAniList.append(oAni)
                continue
        

    
    def DelAniWithFileName(self, sFileName):
        for iIndex, oAni in enumerate(self.m_oAniList):
            if sFileName in oAni.m_FileName:
                del self.m_oAniList[iIndex]
                break
                continue
        

    
    def CreateEffAni(self, iAniIdx, iOffsetX, iOffsetY):
        sPath = mapani.GetResByIdx(iAniIdx)
        if isinstance(sPath, str):
            oRes = mapani.LoadRes(iAniIdx)
        else:
            oRes = sPath
        if not oRes:
            return None
        
        sFileName = oRes.m_FileName
        iZ = 0
        if isinstance(self.GetParent(), interface.CMapAddonObject) and not (self.m_bUseSprite):
            oAni = CMapAni(self.GetParent().GetParent())
            oAni.Load(sFileName, 'map')
            (iX, iY) = self.GetParent().GetPos()
            if hasattr(self.GetParent(), 'GetResKey'):
                (iKX, iKY) = self.GetParent().GetResKey()
            else:
                (iKX, iKY) = (0, 0)
            if self.m_bUseOffSet:
                oAni.SetPos((iX - iKX) + iOffsetX, (iY - iKY) + iOffsetY)
            else:
                oAni.SetPos(iX, iY)
            iZ = (iY - iKY) + iOffsetY
        else:
            oAni = interface.CSpriteObject(self, sFileName, 'map')
            if hasattr(self.GetParent(), 'GetResKey'):
                (iKX, iKY) = self.GetParent().GetResKey()
            else:
                (iKX, iKY) = (0, 0)
            (iX, iY) = (0, 0)
            if self.m_bUseOffSet:
                iZ = iOffsetY + 10000
                iX = -iKX + iOffsetX
                iY = -iKY + iOffsetY
                oAni.SetPos(-iKX + iOffsetX, -iKY + iOffsetY)
                oAni.SetZ(iOffsetY + 10000)
            
        oFuncZ = None
        if self.m_dExtend:
            oFuncZ = self.m_dExtend.get('oFuncZ', None)
        
        if oFuncZ:
            iZ = oFuncZ(sFileName, oAni, iZ, iX, iY)
        
        oAni.SetZ(iZ)
        iRandomFrame = misc.RandInt(0, oAni.FrameAmount() - 1)
        oAni.SetFrame(iRandomFrame)
        oAni.CreateCommand(0, 'animation')
        oAni.m_FileName = sFileName
        return oAni



class CWaterEff(CExtraEff):
    
    def CreateEffAni(self, iAniIdx, iX, iY):
        sPath = mapani.GetResByIdx(iAniIdx)
        if isinstance(sPath, str):
            oRes = mapani.LoadRes(iAniIdx)
        else:
            oRes = sPath
        sFileName = oRes.m_FileName
        if isinstance(self.GetParent(), interface.CMapAddonObject):
            cls = interface.CMapSpriteObject
        else:
            cls = interface.CSpriteObject
        oAni = cls(self.GetParent(), sFileName, 'map')
        (iKX, iKY) = (0, 0)
        if hasattr(self.GetParent(), 'GetResKey'):
            (iKX, iKY) = self.GetParent().GetResKey()
        
        oAni.SetPos(iX - iKX, iY - iKY)
        iRandomFrame = misc.RandInt(0, oAni.FrameAmount() - 1)
        oAni.SetFrame(iRandomFrame)
        oAni.CreateCommand(0, 'animation')
        return oAni

    
    def SetShow(self, bShow):
        CExtraEff.SetShow(self, bShow)
        for oAni in self.m_oAniList:
            oAni.SetShow(bShow)
        



class CMapAni(interface.CMapWalkerObject):
    
    def CSetDirection(self, *args):
        pass



def GetAniByPath(sPath, sPackage):
    global g_Ani
    tID = (sPath, sPackage)
    if tID not in g_Ani:
        if len(g_Ani) > 100:
            g_Ani = { }
        
        sData = C_sys.LoadFile(sPath, sPackage)
        g_Ani[tID] = sData
    
    return g_Ani[tID]
