# pycdc 交叉复核产物 · script.fls entry 4858
# co_filename(原始)='script/mxgame/pet/dlggraphupgrade.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4858.pyc (Python 2.5)

'''
# @Time     : 2019/5/27
# @Author   : lizifeng
# @File     : dlggraphupgrade.py
# @Explain  : \xb9\xd6\xce\xef\xcd\xbc\xbc\xf8\xbd\xe2\xcb\xf8\xc9\xfd\xbc\xb6\xd5\xb9\xca\xbe\xbd\xe7\xc3\xe6
'''
import combdialog
import descinterface
import monsterdata
import summongraphrewarddata
import wrapinterface
import interface
import popupmgr
import popupdefine
import ui
import monstergraphdefine
import usermacro
import chatoutput
g_dCache = { }
g_iCacheIdx = 0

def ModuleReset():
    global g_dCache, g_iCacheIdx
    g_dCache = { }
    g_iCacheIdx = 0


def Show(dData):
    global g_iCacheIdx
    iId = dData['iId']
    iShape = summongraphrewarddata.GetShapeById(iId)
    sName = monsterdata.GetData(iShape)['name']
    iStar = dData['star']
    if iStar in (1, 2, 3):
        g_iCacheIdx += 1
        g_dCache[g_iCacheIdx] = dData
        sLink = '#s(50,[\xacd\xac\xdd\xb8\xd4\xb2\xd3],80,%s)' % g_iCacheIdx
        if iStar == 1:
            sTips = '#G%s#n\xb9\xcf\xc5\xb3\xa6\xac\xb6\xb0\xb9F\xa8\xec%s\xacP\xa1I\xb8\xd1\xc2\xea\xa4F\xc5\xdc\xa8\xad\xaf\xe0\xa4O\xa1I' % (sName, iStar)
            sChatTips = '#G%s#n#W\xb9\xcf\xc5\xb3\xa6\xac\xb6\xb0\xb9F\xa8\xec%s\xacP\xa1I\xb8\xd1\xc2\xea\xa4F\xc5\xdc\xa8\xad\xaf\xe0\xa4O\xa1I%s#n' % (sName, iStar, sLink)
        else:
            sTips = '#G%s#n\xb9\xcf\xc5\xb3\xa6\xac\xb6\xb0\xb9F\xa8\xec%s\xacP\xa1I\xb8\xea\xbd\xe8\xa5[\xa6\xa8\xbcW\xa5[\xa4F\xa1I' % (sName, iStar)
            sChatTips = '#G%s#n#W\xb9\xcf\xc5\xb3\xa6\xac\xb6\xb0\xb9F\xa8\xec%s\xacP\xa1I\xb8\xea\xbd\xe8\xa5[\xa6\xa8\xbcW\xa5[\xa4F\xa1I%s#n' % (sName, iStar, sLink)
        usermacro.MOVE_MSG(usermacro.PETICONTYPE, iShape, sTips)
        chatoutput.AddChat(sChatTips)
    else:
        oPopupMgr = popupmgr.GetPopupMgr()
        if oPopupMgr.IsOpen(popupdefine.CDlgGraphUpgrade):
            CloseDlg()
        
        popupmgr.GetPopupMgr().OpenUI(popupdefine.CDlgGraphUpgrade, lstParam = dData)


def ShowByCache(iCacheIdx):
    if iCacheIdx in g_dCache:
        popupmgr.GetPopupMgr().OpenUI(popupdefine.CDlgGraphUpgrade, lstParam = g_dCache[iCacheIdx])
    else:
        usermacro.PROMPT_MSG('\xc3\xec\xb1\xb5\xa4w\xa5\xa2\xae\xc4')


def CloseDlg():
    popupmgr.GetPopupMgr().CloseUI(popupdefine.CDlgGraphUpgrade)


def GetMaxStarNum():
    return monstergraphdefine.MAXSTARNUM


def GetShapeAndDesc(iShape, iOrnament):
    dDesc = descinterface.GetDefaultDesc()
    if iOrnament == 1 or iOrnament == 0:
        if 'weapon2' in dDesc:
            del dDesc['weapon2']
        
        if 'weapon3' in dDesc:
            del dDesc['weapon3']
        
        dDesc['weapon'] = [
            0,
            iOrnament,
            0]
    elif iOrnament == 2:
        if 'weapon3' in dDesc:
            del dDesc['weapon3']
        
        dDesc['weapon2'] = [
            0,
            2]
        dDesc['weapon'] = [
            0,
            1,
            0]
    elif iOrnament == 3:
        dDesc['weapon3'] = [
            0,
            3]
        dDesc['weapon2'] = [
            0,
            2]
        dDesc['weapon'] = [
            0,
            1,
            0]
    
    return (iShape, dDesc)


class CGraphUpgradeDlg(combdialog.CCombDialog):
    
    def __init__(self, oParent, dData):
        combdialog.CCombDialog.__init__(self, oParent, 'dialog4/newsummon/monster_unlock.dlg')
        self.m_oSummonName = self.GetObject('text_petname')
        self.m_oTitle = self.GetObject('text_title')
        self.m_oStarList = []
        self.m_oPetAni = None
        self.m_dData = dData
        for i in xrange(GetMaxStarNum()):
            oStar = self.GetObject('img_star%d' % (i + 1))
            oStar.SetShow(False)
            self.m_oStarList.append(oStar)
        
        self.SetData(dData)

    
    def SetData(self, dData):
        iId = dData['iId']
        iShape = summongraphrewarddata.GetShapeById(iId)
        iStar = dData['star']
        iLock = dData['lock']
        oTip = self.GetObject('tips_star')
        if iStar == 1:
            sTitle = '\xb8\xd1\xc2\xea\xc5\xdc\xa8\xad\xaf\xe0\xa4O'
        else:
            sTitle = '\xb9\xcf\xc5\xb3\xa4\xc9\xaf\xc5'
        self.m_oTitle.SetText(sTitle)
        for i in xrange(iStar):
            (iX, iY) = self.m_oStarList[i].GetPos()
            self.m_oStarList[i] = ui.CImage(self, 'combdialog4/\xd4\xd3\xcd\xbc/\xd0\xc71.png', interface.UIPath)
            self.m_oStarList[i].SetPos(iX, iY)
            self.m_oStarList[i].SetShow(True)
        
        for i in xrange(iStar, GetMaxStarNum()):
            (iX, iY) = self.m_oStarList[i].GetPos()
            self.m_oStarList[i] = ui.CImage(self, 'combdialog4/\xd4\xd3\xcd\xbc/\xd0\xc72.png', interface.UIPath)
            self.m_oStarList[i].SetPos(iX, iY)
            self.m_oStarList[i].SetShow(True)
        
        oTip.SetShow(True)
        oTip.SetTips(self.GetMonsterTips(iShape, iStar))
        if summongraphrewarddata.IsSpecial(iShape) or not iStar:
            for oStar in self.m_oStarList:
                oStar.SetShow(False)
            
            oTip.SetShow(False)
        
        sName = monsterdata.GetData(iShape)['name']
        if '\xc0\xc6\xa5\xfa\xab\xbd\xab\xbd' in sName:
            sName = '\xc0\xc6\xa5\xfa\xab\xbd\xab\xbd'
        
        self.m_oSummonName.SetText(sName)
        oLoc = self.GetObject('loc_petani')
        import petornamentdata
        import dlgpet
        iOrnamentNum = petornamentdata.GetOrnamentNum(iShape)
        (_, dDesc) = GetShapeAndDesc(iShape, iOrnamentNum)
        self.m_oPetAni = wrapinterface.CPetAni(self, iShape, dDesc, walkerClass = dlgpet.CFakeRole)
        interface.AlignObjects(self.m_oPetAni, oLoc, interface.ALIGN_CENTER_MIDDLE)

    
    def GetMonsterTips(self, iShape, iStar):
        import summongraphrewarddata
        import monstergraphdefine
        iId = summongraphrewarddata.GetIdByShape(iShape)
        sTips = ''
        if iStar < iStar:
            pass
        elif iStar <= GetMaxStarNum():
            sTips += '\xb7\xed\xabe\xacP\xaf\xc5\xb8\xea\xbd\xe8\xa5[\xa6\xa8\xa1G#r'
            dInfo = summongraphrewarddata.GetUpgradeReward(iId, iStar)
            if dInfo:
                for sZZ, \xc4\xe3um in dInfo.iteritems():
                    sTips += ' %s: +%d#r' % (monstergraphdefine.ZZ2NAME[sZZ], \xc4\xe3um)
                
            
        
        if iStar < GetMaxStarNum():
            if sTips != '':
                sTips += '#r'
            
            sTips += '\xa4U\xa4@\xacP\xaf\xc5\xb1N\xb9F\xa8\xec\xa1G#r'
            dInfo = summongraphrewarddata.GetUpgradeReward(iId, iStar + 1)
            if dInfo:
                for sZZ, \xc4\xe3um in dInfo.iteritems():
                    sTips += ' %s: +%d#r' % (monstergraphdefine.ZZ2NAME[sZZ], \xc4\xe3um)
                
            
        
        return sTips

    
    def RightUp(self):
        CloseDlg()

    
    def Hold(self):
        pass

    
    def OnMessage(self, iMsgId):
        if iMsgId == 1:
            CloseDlg()
