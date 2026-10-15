# pycdc 交叉复核产物 · script.fls entry 4611
# co_filename(原始)='script/yard/luckyfish/view/dlgfudaishareitem.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4611.pyc (Python 2.5)

import interface
import avaterload

class CAvatarNameItem(interface.CBoxObject):
    
    def __init__(self, oParent, sName, iID, iNormalColor):
        interface.CBoxObject.__init__(self, oParent, 0, 0, 0, 0)
        self.m_iNormalColor = iNormalColor
        self.m_iID = iID
        self.m_sName = sName
        self.m_oAvatar = None
        self.m_oNameItem = None
        self.Init()
        self.InitSignal()

    
    def InitSignal(self):
        oAvatarMgr = avaterload.Get()
        oAvatarMgr.ssConnect(oAvatarMgr.SS_LoadAvaterFinished, self.OnLoadAvaterFinished)

    
    def GetID(self):
        return self.m_iID

    
    def Init(self):
        '''
\t\t\xa5]\xa7t\xa4@\xad\xd3\xc0Y\xb9\xb3\xa1A\xa4@\xad\xd3\xa6W\xa6r\xa1A\xc0Y\xb9\xb3\xbc\xc8\xaf\xca, \xa5i\xa5\x1c\xfe\xe9\xe5\xe1\xf1\x9a\xe5\x92\xf2\xb2\xee\t\x94\r\xed\xe7\xfe\xee\xe5\xe1\xf02^]]n&1 !&:n^]]'''
        self.CreateAvatar()
        (_, iPosY) = self.m_oAvatar.GetPos()
        (iWidth, iHeight) = self.m_oAvatar.GetSize()
        self.m_oNameItem = interface.CTextObject(self, self.m_sName, interface.FontLT14_3, self.m_iNormalColor)
        (iNameW, iNameH) = self.m_oNameItem.GetSize()
        iNameX = iWidth + 5
        iNamey = -(iNameH - iHeight) / 2
        self.m_oNameItem.SetPos(iNameX, iNamey)
        iW = iWidth + iNameW + 5
        iH = iHeight
        self.SetSize(iW, iH)

    
    def OnLoadAvaterFinished(self, dAvatar):
        if not self.m_iID:
            return None
        
        if self.m_iID not in dAvatar:
            return None
        
        self.CreateAvatar()

    
    def CreateAvatar(self):
        import avatar
        import world
        import friend
        import dlgrank
        oAvatarMgr = avaterload.Get()
        tAvatar = oAvatarMgr.GetAvatar(self.m_iID, 'yardluckyfish')
        if not not tAvatar:
            for None in tAvatar == (-1, -1, -1, -1):
                oFriend = friend.GetControl().GetSafePlayer(self.m_iID)
                tAvatar = getattr(oFriend, 'm_PhotoArr', None)
                if not tAvatar:
                    iShape = world.GetObjRealShape(self.m_iID)
                    tAvatar = avatar.GetShapeDefaultPhoto(iShape)
                
            tAvatar
            if len(tAvatar) > 4:
                tAvatar = avatar.PhotoArr2Int(tAvatar)
            
        oAvatar = dlgrank.CRankCellAvatar(self)
        oAvatar.SetAvatar(tAvatar)
        self.m_oAvatar = oAvatar
