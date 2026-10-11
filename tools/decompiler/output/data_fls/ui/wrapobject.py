# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\ui\wrapobject.py
import C_object, C_sys, C_publicEx, os
from pubcore.function import Functor
g_dPalPart = None

def GetPalPart():
    global g_dPalPart
    if g_dPalPart is None:
        g_dPalPart = {}
        try:
            oFile = open('141.palpart', 'r')
            sLineList = oFile.readlines()
            oFile.close()
            for sLine in sLineList:
                sLine = sLine.strip()
                if sLine and ':' in sLine:
                    sKey, sVal = sLine.split(':', 1)
                    lstVal = sVal.split('|')
                    g_dPalPart[sKey] = lstVal

        except:
            g_dPalPart = {}

    return g_dPalPart


class CSpine(C_object.CBaseObject):
    s_SpineObjs = {}

    def __init__(self, parent, path, w=-1, h=-1, bAsync=False, plist_num=0, imgOffset=0, fScale=1.0):
        C_object.CBaseObject.__init__(self, parent)
        plist_path = '%s.plist' % path
        self.m_Skel_path = '%s.skel' % path
        self.m_Atlas_path = '%s.atlas' % path
        self.m_RecordData = {}
        self.m_ImgOffset = imgOffset
        if bAsync:
            self.m_Loading = True
            self.m_Width = w
            self.m_Height = h
            if plist_num:
                self.m_LoadSet = set()
                for iIdx in range(plist_num):
                    self.m_LoadSet.add(iIdx)

                for iIdx in range(plist_num):
                    plist_path = '%s%s.plist' % (path, iIdx)
                    C_object.CSpriteFrameCache.GetInstance().AddSpriteFramesWithFileAsync(plist_path, self.AddFramesAsyncCallback, iIdx)

            else:
                self.m_LoadSet = set([1])
                C_object.CSpriteFrameCache.GetInstance().AddSpriteFramesWithFileAsync(plist_path, self.AddFramesAsyncCallback, 1)
        else:
            import crashinfo
            self.m_Loading = False
            msg = 'path=%s;' % path
            crashinfo.SpineInfo(msg)
            if plist_num:
                for iIdx in range(plist_num):
                    plist_path = '%s%s.plist' % (path, iIdx)
                    C_object.CSpriteFrameCache.GetInstance().AddSpriteFramesWithFile(plist_path)

            else:
                C_object.CSpriteFrameCache.GetInstance().AddSpriteFramesWithFile(plist_path)
            self.m_ImgSpt = C_object.CSpineAnimation.CreateFromSpriteFrame(self.m_Skel_path, self.m_Atlas_path, scale=fScale)
            msg += 'CreateFromSpriteFrame=%s;' % str(self.m_ImgSpt)
            crashinfo.SpineInfo(msg)
            if w == -1 or h == -1:
                if self.m_ImgSpt:
                    cw, ch = self.m_ImgSpt.GetContentSize()
                    cw = int(round(cw + 0.5))
                    ch = int(round(ch + 0.5))
                else:
                    cw, ch = (1, 1)
                if w == -1:
                    w = cw
                if h == -1:
                    h = ch
            self.m_Width = w
            self.m_Height = h
            if self.m_ImgSpt:
                self.m_ImgSpt.SetParent(self.GetCocosNode())
                self.m_ImgSpt.SetPos(w / 2, -h)
                self.m_ImgAni = self.m_ImgSpt.SetAnimation(0, 'stand', loop=True)
            msg += 'Finish!'
            crashinfo.SpineInfo(msg)

    def GetSize(self):
        if self.m_Loading:
            return (0, 0)
        return (
         self.m_Width, self.m_Height)

    def GetImgSpt(self):
        if self.m_Loading:
            self.m_RecordData['GetImgSpt'] = ()
            return
        return self.m_ImgSpt

    def SetAnimation(self, state, loop=True):
        if self.m_Loading:
            self.m_RecordData['SetAnimation'] = (
             state, loop)
            return
        if self.m_ImgSpt:
            self.m_ImgAni = self.m_ImgSpt.SetAnimation(0, state, loop)

    def SetShow(self, bShow):
        if self.m_Loading:
            self.m_RecordData['SetShow'] = (
             bShow,)
            return
        self.m_ImgSpt.SetVisible(bShow)

    def SetOpacity(self, iAlpha):
        if self.m_Loading:
            self.m_RecordData['SetOpacity'] = (
             iAlpha,)
            return
        self.m_ImgSpt.SetOpacity(iAlpha)

    def SetScale(self, iScale):
        if self.m_Loading:
            self.m_RecordData['SetScale'] = (
             iScale,)
            return
        self.m_ImgSpt.SetScale(iScale)

    def Pause(self):
        if self.m_Loading:
            self.m_RecordData['Pause'] = ()
            return
        self.m_ImgSpt.Pause()

    def Resume(self):
        if self.m_Loading:
            self.m_RecordData['Resume'] = ()
            return
        self.m_ImgSpt.Resume()

    def IsLoading(self):
        return self.m_Loading

    @staticmethod
    def OnObjDel(iID, oWeakref):
        if iID in CSpine.s_SpineObjs:
            CSpine.s_SpineObjs.pop(iID)

    @staticmethod
    def SpineAsyncDone(param):
        iID = param
        weakRef = CSpine.s_SpineObjs.get(iID, None)
        if not weakRef:
            return
        else:
            obj = weakRef()
            w, h = obj.m_Width, obj.m_Height
            if w == -1 or h == -1:
                if obj.m_ImgSpt:
                    cw, ch = obj.m_ImgSpt.GetContentSize()
                    cw = int(round(cw + 0.5))
                    ch = int(round(ch + 0.5))
                else:
                    cw, ch = (1, 1)
                if w == -1:
                    w = cw
                if h == -1:
                    h = ch
            obj.m_Width = w
            obj.m_Height = h
            obj.m_Clip = C_object.CClippingNode(w, h)
            obj.m_Clip.SetParent(obj.GetCocosNode())
            obj.m_Clip.SetPos(0, -h)
            if obj.m_ImgSpt:
                obj.m_ImgSpt.SetParent(obj.m_Clip)
                obj.m_ImgSpt.SetPos(w / 2, obj.m_ImgOffset)
                obj.m_ImgAni = obj.m_ImgSpt.SetAnimation(0, 'stand', loop=True)
            obj.m_Loading = False
            if obj.m_RecordData:
                for sFuncName, args in obj.m_RecordData.items():
                    func = getattr(obj, sFuncName, None)
                    if func:
                        func(*args)

                obj.m_RecordData = {}
            return

    def AddFramesAsyncCallback(self, iTag):
        if iTag in self.m_LoadSet:
            self.m_LoadSet.remove(iTag)
        if self.m_LoadSet:
            return
        import weakref
        iID = id(self)
        self.s_SpineObjs[iID] = weakref.ref(self, Functor(CSpine.OnObjDel, iID))
        self.m_ImgSpt = C_object.CSpineAnimation()
        self.m_ImgSpt.InitFromSpriteFrameAsync(self.m_Skel_path, self.m_Atlas_path, callback=CSpine.SpineAsyncDone, param=(iID,))

    def SetSpinePal(self, oSpine):
        oTColorManager = C_object.CTColorManager.GetInstance()
        oTColorManager.LoadPalProject('testpal/pal.pro')
        oMaterialObj = C_object.CMaterialObj2D()
        oMaterialObj.SetPalProject([1, 4, 7], '211_body')
        for sBoneName in oSpine.GetBonesNamesDict().itervalues():
            lSlots = oSpine.GetSlotsTuple(targetBoneName=sBoneName)
            if lSlots:
                for sSlot in lSlots:
                    lPlaceholderName = oSpine.GetPlaceholdersOnSlot(sSlot, hasSkinInfo=False)
                    if not lPlaceholderName:
                        continue
                    for sPlaceholderName in lPlaceholderName:
                        oSprite = oSpine.GetAttachment(sSlot, sPlaceholderName)
                        if oSprite:
                            oSprite.SetMaterialObj(oMaterialObj)

    def SetHSLPal(self, iHue):
        oSpine = self.m_ImgSpt
        if oSpine:
            sDir = os.path.dirname(self.m_Skel_path)
            lstPalBones = GetPalPart().get(sDir, [])
            for sBoneName in oSpine.GetBonesNamesDict().itervalues():
                if sBoneName in lstPalBones:
                    continue
                lSlots = oSpine.GetSlotsTuple(targetBoneName=sBoneName)
                if lSlots:
                    for sSlot in lSlots:
                        lPlaceholderName = oSpine.GetPlaceholdersOnSlot(sSlot, hasSkinInfo=False)
                        if not lPlaceholderName:
                            continue
                        for sPlaceholderName in lPlaceholderName:
                            oSprite = oSpine.GetAttachment(sSlot, sPlaceholderName)
                            if oSprite:
                                oSprite.SetHSL(True, iHue, 0, 0)


class CAnimSet(C_object.CBaseObject):

    def __init__(self, parent, path):
        obj = C_publicEx.CAnimSet()
        if not obj.InitWithFile(path):
            raise SystemError('Create CAnimSet Error:%s' % path)
        x, y, w, h = obj.GetValuableRect()
        C_object.CBaseObject.__init__(self, parent)
        self.m_Width, self.m_Height = int(round(w + 0.5)), int(round(h + 0.5))
        obj.SetParent(self.GetCocosNode())
        self.m_AnimSet = obj
        self.PlayAnim()

    def GetSize(self):
        return (
         self.m_Width, self.m_Height)

    def GetKeyPos(self):
        x, y, w, h = self.m_AnimSet.GetValuableRect()
        return (-int(x), int(h + y))

    def SetAnimSpeed(self, fSpeed):
        self.m_AnimSet.SetAnimSpeed(fSpeed)

    def PlayAnim(self, bOverSet=False, bIsLoop=False):
        self.m_AnimSet.PlayAnim(bOverSet, bIsLoop)

    def SetAnim(self, sStateName, bIsLoop=False):
        self.m_AnimSet.SetAnim(sStateName, bIsLoop)

    def StopAnim(self):
        self.m_AnimSet.StopAnim()

    def GetStateName(self):
        return self.m_AnimSet.GetStateName()

    def SetActionEndCb(self, func, *args):
        self.m_AnimSet.SetActionEndCb(func, *args)


class CAvatar(C_object.CBaseObject):

    def __init__(self, oParent, sPathList, sPack, w, h):
        C_object.CBaseObject.__init__(self, oParent)
        self.m_sSpriteFrameCacheList = []
        self.m_sPathList = sPathList
        self.m_sPack = sPack
        self.m_oImgList = []
        self.m_iWidth = w
        self.m_iHeight = h
        self.m_lstPal = []
        self.Init()

    def SetPalCase(self, lstPal):
        self.m_lstPal = lstPal
        self.RefreshPalCase()

    def RefreshPalCase(self):
        for iPos, iHue in enumerate(self.m_lstPal):
            if iPos >= len(self.m_oImgList):
                break
            oImg = self.m_oImgList[iPos]
            if isinstance(oImg, CSpine):
                oImg.SetHSLPal(iHue)

    def Init(self):
        self.m_oImgList = []
        self.m_sSpriteFrameCacheList = []
        for iIdx, sPath in enumerate(self.m_sPathList):
            oImg = self.CreateImg(sPath)
            if oImg is not None:
                oImg.SetZ(iIdx)
                if isinstance(oImg, CSpine):
                    self.m_sSpriteFrameCacheList.append(oImg.m_sPath)
            self.m_oImgList.append(oImg)

        self.RefreshPalCase()
        return

    def CreateImg(self, sPath):
        fImgScale = self.GetScale(sPath)
        sPath = sPath.replace('\\', '/')
        if sPath and sPath.endswith('.igs') or sPath.endswith('.png'):
            sTmpPath, sName = os.path.split(sPath)
            sTmpName, sExt = os.path.splitext(sName)
            if sTmpName.endswith('_'):
                sBorderName = '%s/%s/%scs_/%s' % (self.m_sPack, sTmpPath, sTmpName, sTmpName)
            else:
                sBorderName = '%s/%s/%s_cs/%s' % (self.m_sPack, sTmpPath, sTmpName, sTmpName)
            sBorderPathName = '%s.plist' % sBorderName
            if C_sys.LoadFile(sBorderPathName):
                oImg = CSpine(self, sBorderName, self.m_iWidth, self.m_iHeight, fScale=fImgScale)
                oImg.m_sPath = sBorderPathName
            elif sExt == '.igs':
                try:
                    oImg = C_object.CImagesObject(self, sPath, self.m_sPack)
                except:
                    oImg = None

            else:
                try:
                    oImg = C_object.CBitmapObject(self, sPath, self.m_sPack)
                except:
                    oImg = None

        else:
            oImg = None
        return oImg

    def Refresh(self, sPathList, sPack, w, h):
        if w != self.m_iWidth or h != self.m_iHeight or sPack != self.m_sPack or len(sPathList) != len(self.m_sPathList):
            self.m_iWidth = w
            self.m_iHeight = h
            self.ClearSpriteFrames(self.m_sSpriteFrameCacheList)
            self.m_sPathList = sPathList
            self.m_sPack = sPack
            self.Init()
            return
        else:
            sRemoveList = []
            bHasBodyChg = self.CheckIsHasBodyChange(sPathList)
            for iIdx, sOrgPath in enumerate(self.m_sPathList):
                sCmpPath = sPathList[iIdx]
                if sCmpPath != sOrgPath or bHasBodyChg and sCmpPath and self.CheckIsBodyPath(sCmpPath):
                    oOrgImg = self.m_oImgList[iIdx]
                    if oOrgImg and isinstance(oOrgImg, CSpine):
                        sRemoveList.append(oOrgImg.m_sPath)
                    oImg = self.CreateImg(sCmpPath)
                    if oImg is not None:
                        oImg.SetZ(iIdx)
                        if isinstance(oImg, CSpine):
                            self.m_sSpriteFrameCacheList.append(oImg.m_sPath)
                    self.m_oImgList[iIdx] = oImg

            self.m_sPathList = sPathList
            self.RefreshPalCase()
            for sRmove in sRemoveList:
                if sRmove in self.m_sSpriteFrameCacheList:
                    self.m_sSpriteFrameCacheList.remove(sRmove)

            self.ClearSpriteFrames(sRemoveList)
            return

    def CheckIsHasBodyChange(self, sPathList):
        for iIdx, sOrgPath in enumerate(self.m_sPathList):
            sCmpPath = sPathList[iIdx]
            if sCmpPath and sCmpPath != sOrgPath and self.CheckIsBodyPath(sCmpPath):
                return True

        return False

    def CheckIsBodyPath(self, sPath):
        _, sFileName = os.path.split(sPath)
        sPart = sFileName[2:4]
        sBody = sFileName[:2]
        if sBody in ('25', '26'):
            return sPart in ('00', '06', '01', '02', '03', '05', '08')
        else:
            if sBody in ('27', '28'):
                return sPart in ('00', '06', '01', '02', '03', '05', '08')
            if sBody in ('29', '30'):
                return sPart in ('00', '06', '01', '02', '03', '05', '08', '07', '09',
                                 '12')
            if sBody in ('31', '32'):
                return sPart in ('00', '06', '01', '02', '03', '05', '08')
            return False

    def GetScale(self, sPath):
        _, sFileName = os.path.split(sPath)
        sPart = sFileName[2:4]
        sBody = sFileName[:2]
        if sBody in ('29', '30'):
            if sPart not in ('13', ):
                return 0.9
        return 1.0

    def ClearSpriteFrames(self, sPathList):
        if not sPathList:
            return
        oMgr = C_object.CSpriteFrameCache.GetInstance()
        for sPath in sPathList:
            oMgr.RemoveSpriteFramesFromFile(sPath)

        oMgr = C_object.CTextureCache.GetInstance()
        oMgr.RemoveUnusedTextures()
