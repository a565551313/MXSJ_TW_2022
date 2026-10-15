# pycdc 交叉复核产物 · script.fls entry 1539
# co_filename(原始)='script/usermacro.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1539.pyc (Python 2.5)

import chardefine
import interface
import monsterdata
import skilliconpath
import ui
import wrapinterface
import C_sys
import style
ITEMTYPE = 0
SKILLTYPE = 1
ROLETYPE = 2
MODELTYPE = 3
PETICONTYPE = 4
ANITYPE = 5
ICONTYPE = 6
IMMORTTYPE = 7
ACHIEVETYPE = 10
SKILLCOMPREHEND = 11
DICT_LIFE = {
    ITEMTYPE: 1,
    SKILLTYPE: 2,
    ROLETYPE: 2,
    MODELTYPE: 3,
    PETICONTYPE: 2,
    ANITYPE: 3,
    ICONTYPE: 2,
    IMMORTTYPE: 3,
    ACHIEVETYPE: 3 }
MOVE_HEIGHT = 60
MOVE_TEXT_WIGHT = 600
SHOW_TEXT_TIME = 5
g_PromptTips = []
g_PromptLastXY = None
g_MoveHint = None
g_MoveHintInfoList = []
g_MoveBar = None
g_MoveText = None
g_MoveTextQueue = []
g_HintPanel = None
g_MoveBarH = 20
g_iShowType = 1
g_RollTextQueue = []
g_RollText = None
g_RollBar = None

def ModuleReset():
    global g_PromptTips, g_PromptLastXY, g_MoveHint, g_MoveHintInfoList, g_MoveBar, g_MoveText, g_MoveTextQueue, g_HintPanel, g_MoveBarH, g_iShowType, g_RollTextQueue, g_RollText, g_RollBar
    g_PromptTips = []
    g_PromptLastXY = None
    g_MoveHint = None
    g_MoveHintInfoList = []
    g_MoveBar = None
    g_MoveText = None
    g_MoveTextQueue = []
    g_HintPanel = None
    g_MoveBarH = 20
    g_iShowType = 1
    g_RollTextQueue = []
    g_RollText = None
    g_RollBar = None


def debugmsg(txt):
    import permission
    import misc
    if not permission.IsInNet() or misc.GetServerID() in (30001, 30302, 30321, 30322):
        return None
    
    NORMAL_MSG(txt)


def systemmsg(txt):
    import chatoutput
    chatoutput.AddChat('#s(8)%s' % txt)


def systips(txt):
    import chatoutput
    chatoutput.AddChat('#s(13)%s' % txt)


def normalmsg(txt, bShowColor = True):
    import chatoutput
    if bShowColor:
        sText = '#Y' + txt
    else:
        sText = '#W' + txt
    chatoutput.AddChat(sText)


def RemoveTipsObj(obj):
    if obj in g_PromptTips:
        g_PromptTips.remove(obj)
    


def RemoveTipsByText(sText):
    if sText:
        for oTips in g_PromptTips:
            if getattr(oTips, 'm_TipsText', '') == sText:
                RemoveTipsObj(oTips)
                break
                continue
        
    


def IsMsgShiled(txt):
    import re
    if txt.find('$Repeat') >= 0:
        txt = txt.replace('$Repeat', '')
        return (False, txt)
    
    notShiledLst = ('\xb5\xb9\xa4\xa9\xa4F\xac\xef\xa6\xe6\xaa\xcc[0-9]+?\xad\xd3\xaf\xab\xaf\xb5\xb8H\xa4\xf9',)
    for sTxt in notShiledLst:
        notShiledTxt = re.compile(sTxt)
        if re.match(notShiledTxt, txt):
            break
            continue
    else:
        return (True, txt)
    return (False, txt)


def promptmsg(txt, panel = None, lastsecond = 3):
    import juben
    if juben.IsPlayJuben():
        return None
    
    (flag, txt) = IsMsgShiled(txt)
    for tipsObj in g_PromptTips:
        if getattr(tipsObj, 'm_TipsText', None) == txt and flag:
            tipsObj.SetShow(True)
            tipsObj.m_ShowFrames = lastsecond * 30
            return None
            continue
    
    tipsObj = CTextTips(panel, 200, txt, interface.FontLT14_3, edge = 8)
    tipsObj.m_TipsText = txt
    AddPromptTips(tipsObj, lastsecond)
    return tipsObj


def AddItemPrpmptTips(iShape, sTxt, \xc5Width, iLastsecond = 3):
    global g_HintPanel
    if g_HintPanel is None:
        g_HintPanel = interface.CPanel(None)
        g_HintPanel.SetZ(600)
    
    iNewWidth = IgnoreIconWidth(iShape, \xc5Width)
    if iShape == 31220:
        oItemTips = CreateItemTips31220(g_HintPanel, iShape, sTxt, iNewWidth)
    elif iShape == 0:
        oItemTips = CTextTips(g_HintPanel, \xc5Width - 2, sTxt, interface.FontLT14_3, edge = 8)
    else:
        oItemTips = CreateItemTips(g_HintPanel, iShape, sTxt, iNewWidth)
    if not oItemTips:
        LOG('\xb3\xd0\xab\xd8\xc4\xc6\xb9D\xa8\xe3\xae\xd8\xb2\xa7\xb1`---->', iShape, sTxt)
        return None
    
    AddPromptTips(oItemTips, iLastsecond)


def IgnoreIconWidth(iShape, iOldwidth):
    import item
    oIcon = item.CreateItem44Image(None, iShape)
    (iw, _) = oIcon.GetResSize()
    iNewWidth = iOldwidth - iw
    return iNewWidth


def AddPromptTips(oTips, lastsecond):
    import ratio
    import wrapeffect
    if ratio.Is1024x768():
        (x, y) = (420, 180)
    elif ratio.Is1366x768():
        (x, y) = (548, 180)
    elif ratio.Is1366x708():
        (x, y) = (548, 150)
    elif ratio.Is1280x960():
        (x, y) = (530, 276)
    else:
        (x, y) = (300, 130)
    
    def tick(obj):
        obj.m_ShowFrames -= 1
        if obj.m_ShowFrames <= 0:
            obj.m_TipsAni.Release()
            g_PromptTips.remove(obj)
            return None
        
        if hasattr(obj, 'm_MoveObj') and obj.m_MoveObj:
            if obj.m_MoveObj.GetCurrentFrame() < obj.m_MoveObj.GetFrameAmount() - 1:
                obj.m_MoveObj.NextFrame()
            
        
        return ()

    oTips.SetPos(x, y)
    oTips.m_ShowFrames = lastsecond * 30
    oTips.m_TipsAni = oTips.CreatePyCommand(1, tick)
    g_PromptTips.insert(0, oTips)
    if len(g_PromptTips) > 6:
        g_PromptTips.pop()
    
    h = 0
    for promptTip in g_PromptTips[1:]:
        h += promptTip.GetSize()[1]
        goalY = y - h
        (_, srcY) = promptTip.GetPos()
        if srcY <= goalY:
            continue
        
        promptTip.m_MoveObj = wrapeffect.CreateMoveEffect(promptTip, x, goalY, 2)
    


def StrikeFunc(iType):
    FuncLst = {
        1: 'LeftDown',
        2: 'LeftUp',
        3: 'RightDown',
        4: 'RightUp' }
    funcname = FuncLst.get(iType, '')
    if not funcname:
        return None
    
    import cursor
    import item
    import dlgitempet
    (x, y) = cursor.GetPos()
    objects = C_sys.GetObjects(x, y)
    objLst = (item.CInterfaceBase, dlgitempet.CItemPetDlg)
    for obj in objects:
        if isinstance(obj, objLst):
            func1 = getattr(obj, funcname, None)
            if callable(func1):
                func1()
            
            break
            continue
    


class CHintBase:
    
    def CheckFunc(cls, obj, tick):
        tick = tick + 1
        if tick < obj.m_LifeTime:
            return (tick,)
        
        obj.DelHintFunc()

    CheckFunc = classmethod(CheckFunc)
    
    def StartCheck(self, iLife = 5):
        if getattr(self, 'm_CheckCmd', None):
            self.m_CheckCmd.Release()
            self.m_CheckCmd = None
        
        self.m_LifeTime = iLife
        self.m_CheckCmd = self.CreatePyCommand(30, CHintBase.CheckFunc, 0)

    
    def SetLife(self, iLife):
        self.m_LifeTime = iLife

    
    def DelHintFunc(self):
        global g_MoveHint
        g_MoveHint = None
        nexthint()

    
    def LeftUp(self):
        self.SetShow(False)
        if getattr(self, 'm_CheckCmd', None):
            self.m_CheckCmd.Release()
            self.m_CheckCmd = None
            self.DelHintFunc()
        

    
    def RightUp(self):
        self.LeftUp()
        StrikeFunc(4)



class CTextHint(CHintBase, wrapinterface.CTextTips):
    pass


class CIconHint(CHintBase, wrapinterface.CIconTips):
    pass


class CIconLearnSkill(CHintBase, wrapinterface.CWalkerTips):
    pass


class CModelHint(CHintBase, wrapinterface.CModelTips):
    pass


class CSpriteHint(CHintBase, wrapinterface.CSpriteTips):
    pass


class CAvatarHint(CHintBase, wrapinterface.CAvatarTips):
    pass


class CPillSkillHint(CHintBase, wrapinterface.CPillSkillTips):
    pass


class CTextTips(wrapinterface.CTextTips):
    
    def LeftUp(self):
        self.SetShow(False)

    
    def RightUp(self):
        self.SetShow(False)
        StrikeFunc(4)



class CSrollRichTextObject(interface.CViewportObject):
    
    def __init__(self, parent, w, h, fontid, sTxt, normalcolor):
        import wrapui
        interface.CViewportObject.__init__(self, parent, w, h)
        (sTxt, _, _) = wrapui.ReplaceLink(sTxt)
        self.m_RichTextObject = interface.CRichTextObject(self, 2000, fontid, sTxt, normalcolor)
        (iRichTextWidth, _) = self.m_RichTextObject.GetSize()
        if iRichTextWidth > w:
            interface.CenterLeft(self.m_RichTextObject)
        else:
            interface.Center(self.m_RichTextObject)

    
    def SetSize(self, w, h):
        if w > 0 and h > 0:
            interface.CViewportObject.SetSize(self, w, h)
        

    
    def GetRichTextObj(self):
        return self.m_RichTextObject



def CreateSpriteIconHint(parent, width, path, txt, Font):
    
    try:
        return CSpriteHint(parent, width, 'item44', path, 'item', txt, Font)
    except:
        return None



def movehint(iType, iShape, sTxt, \xc5Width = -1, iShow = 1):
    global g_iShowType
    g_MoveHintInfoList.append((iType, iShape, sTxt, \xc5Width))
    g_iShowType = iShow
    nexthint()


def nexthint():
    global g_HintPanel, g_MoveHint, g_MoveHint
    if g_MoveHint and g_iShowType == 1:
        return None
    
    if len(g_MoveHintInfoList) <= 0:
        return None
    
    if g_HintPanel is None:
        g_HintPanel = interface.CPanel(None)
        g_HintPanel.SetZ(600)
    
    (iType, iShape, sTxt, \xc5Width) = g_MoveHintInfoList.pop(0)
    if DI_TYPE_2_FUNC.get(iType, None):
        g_MoveHint = DI_TYPE_2_FUNC[iType](g_HintPanel, iShape, sTxt, \xc5Width)
    else:
        g_MoveHint = CTextHint(g_HintPanel, \xc5Width, sTxt, interface.FontLT14_3, edge = 6)
    (w, h) = g_MoveHint.GetSize()
    import ratio
    x = (ratio.WINDOW_WIDTH - w) / 2
    y = 100
    iLife = DICT_LIFE.get(iType, 1)
    g_MoveHint.SetPos(x, y)
    g_MoveHint.StartCheck(iLife)


def GetHongbaoTxtH(iTxth):
    if iTxth > 25:
        if iTxth > 40:
            h = iTxth + 5
        else:
            h = 45
    elif iTxth > 20:
        h = iTxth + 5
    else:
        h = 25
    return h


def rolltext(txt, iTime = SHOW_TEXT_TIME):
    global g_HintPanel, g_RollBar, g_RollText
    import ratio
    
    def Show(obj):
        if g_RollText is None or g_RollBar is None:
            return None
        
        (iW, iH) = g_RollBar.GetSize()
        if iH >= g_MoveBarH:
            StartMove()
            return None
        
        iH += 2
        g_RollBar.SetSize(iW, iH)
        return ()

    
    def Hide(obj):
        if g_RollText is None or g_RollBar is None:
            return None
        
        (iW, iH) = g_RollBar.GetSize()
        if iH <= 0:
            g_RollText.CreatePyCommand(1, Clear)
            return None
        
        iH -= 2
        g_RollBar.SetSize(iW, iH)
        g_RollText.SetSize(iW, iH)
        return ()

    
    def Clear(obj):
        global g_RollText, g_RollBar
        if g_RollBar:
            g_RollBar.Release()
        
        if g_RollText:
            g_RollText.Release()
        
        g_RollText = None
        g_RollBar = None

    
    def StartMove():
        if g_RollText is None or g_RollBar is None:
            return None
        
        interface.Center(g_RollText)
        g_RollText.SetShow(True)
        g_RollBar.CreatePyCommand(90, WaitHide)

    
    def WaitHide(obj):
        g_RollBar.CreatePyCommand(1, RollText)

    
    def RollText(obj):
        oRichText = g_RollText.GetRichTextObj()
        (x, y) = oRichText.GetPos()
        (txtWidth, _) = oRichText.GetSize()
        if x < -txtWidth:
            g_RollBar.CreatePyCommand(1, Hide)
            return None
        
        x -= 1
        oRichText.SetPos(x, y)
        return ()

    if txt is None:
        return None
    
    if g_HintPanel is None:
        g_HintPanel = interface.CPanel(None)
        g_HintPanel.SetZ(600)
    
    if g_RollBar is None:
        g_RollBar = interface.CBoxObject(g_HintPanel, ratio.WINDOW_WIDTH, 4, 0, 64)
        g_RollBar.SetShow(True)
        g_RollBar.SetPos(0, 90)
    
    g_RollText = CSrollRichTextObject(g_RollBar, MOVE_TEXT_WIGHT, g_MoveBarH, interface.FontLT14_3, txt, 16776960)
    interface.Center(g_RollText)
    g_RollText.SetZ(10000)
    g_RollText.SetShow(False)
    (iBarW, iBarH) = g_RollBar.GetSize()
    if iBarH >= g_MoveBarH:
        StartMove()
    else:
        g_RollBar.CreatePyCommand(1, Show)


def movetext(txt, iTime = SHOW_TEXT_TIME, iType = 0):
    import ratio
    import hongbaospecialtips
    
    def movebar(ob, n, h, maxh):
        (x, _) = ob.GetPos()
        x -= n
        if x <= 0:
            x = 0
        
        y = MOVE_HEIGHT + (g_MoveBarH - h) / 2
        ob.SetPos(x, y)
        (w, _) = ob.GetSize()
        if isinstance(ob, interface.CBoxObject):
            ob.SetSize(w, h)
        
        if h < maxh:
            return (0, h + 1, maxh)
        else:
            showtext()

    
    def hidebar(ob, n, h, minh):
        global g_MoveBar
        (x, _) = ob.GetPos()
        (w, _) = ob.GetSize()
        w -= n
        if w < 1:
            w = 1
        
        y = MOVE_HEIGHT + (g_MoveBarH - h) / 2
        ob.SetPos(x, y)
        if isinstance(ob, interface.CBoxObject):
            ob.SetSize(w, h)
        
        if h > minh:
            return (n, h - 1, minh)
        else:
            g_MoveBar.SetShow(False)
            g_MoveBar = None
            nexttext()

    
    def clear(ob):
        global g_MoveText
        g_MoveText.Release()
        g_MoveText = None
        g_MoveBar.hide = True
        if isinstance(g_MoveBar, hongbaospecialtips.CHongbaoMoveBar):
            g_MoveBar.Stop()
        
        g_MoveBar.CreatePyCommand(1, hidebar, 0, g_MoveBarH, 4)

    
    def nexttext():
        global g_HintPanel, g_MoveBar, g_MoveBar, g_MoveBarH
        if g_MoveText or g_MoveBar:
            return None
        
        if len(g_MoveTextQueue) > 0:
            if g_HintPanel is None:
                g_HintPanel = interface.CPanel(None)
                g_HintPanel.SetZ(600)
            
            if g_MoveBar is None:
                txt = g_MoveTextQueue[0]
                par = None
                if iType == 1:
                    g_MoveBar = hongbaospecialtips.CreateHongbaoMoveBar(g_HintPanel, txt, 800, MOVE_TEXT_WIGHT)
                    x = (ratio.WINDOW_WIDTH - 800) / 2
                    g_MoveBar.SetPos(x, -50)
                else:
                    g_MoveBar = interface.CBoxObject(g_HintPanel, ratio.WINDOW_WIDTH, 4, 0, 64)
                    g_MoveBar.SetPos(0, 90)
                txtObj = interface.CRichTextObject(par, MOVE_TEXT_WIGHT, interface.FontLT14_3, txt, 16776960)
                (w, h) = txtObj.GetSize()
                g_MoveBarH = h
                g_MoveBar.m_Text = []
                g_MoveBar.CreatePyCommand(1, movebar, 1, 4, g_MoveBarH)
                return None
            
        

    
    def showtext():
        global g_MoveText
        txt = g_MoveTextQueue[0]
        del g_MoveTextQueue[0]
        g_MoveText = interface.CRichTextObject(g_MoveBar, MOVE_TEXT_WIGHT, interface.FontLT14_3, txt, 16776960)
        g_MoveText.SetZ(10000)
        (w, h) = g_MoveText.GetSize()
        (bw, bh) = g_MoveBar.GetSize()
        x = (bw - w) / 2
        y = (bh - h) / 2
        offy = style.GetInt('usermacro', 'data_offy')
        y += offy
        if hasattr(g_MoveBar, 'm_oFrame'):
            y += 3
        
        if isinstance(g_MoveBar, hongbaospecialtips.CHongbaoMoveBar):
            g_MoveBar.Start()
        
        g_MoveText.SetPos(x, y)
        g_MoveText.CreatePyCommand(iTime * 30, clear)

    import cg
    if cg.IsShowCg() or cg.IsShowCgForWarDlg():
        return None
    
    g_MoveTextQueue.append(txt)
    nexttext()


def CreateItemTips31220(parent, iShape, sTxt, \xc5Width):
    import itemdata
    
    try:
        obj = CreateSpriteIconHint(parent, \xc5Width, '%.5d' % itemdata.Shape2Image(iShape), sTxt, interface.FontLT14_3)
    except SystemError:
        obj = CIconHint(parent, \xc5Width, 'item44/00000.igs', 'item', sTxt, interface.FontLT14_3)

    return obj


def CreateItemTips(parent, iShape, sTxt, \xc5Width):
    import item
    
    try:
        (sPath, sPack) = item.GetItem44ImagePath(iShape)
        obj = CIconHint(parent, \xc5Width, sPath, sPack, sTxt, interface.FontLT14_3)
        if monsterdata.IsMonster(iShape):
            oIcon = obj.GetIcon()
            (iW, _) = oIcon.GetSize()
            oIcon.m_oFrament = ui.CImage(oIcon, 'combdialog4/\xd4\xd3\xcd\xbc/\xcb\xe9\xc6\xac\xbd\xc7\xb1\xea44.png', interface.UIPath)
            oIcon.m_oFrament.SetPos(iW - 15, 0)
    except SystemError:
        obj = CIconHint(parent, \xc5Width, 'item44/00000.igs', 'item', sTxt, interface.FontLT14_3)

    return obj


def CreateSkillTips(parent, iShape, sTxt, \xc5Width):
    (sPath, sPack) = skilliconpath.GetSummonSkillIconPath(iShape)
    obj = CIconHint(parent, \xc5Width, sPath, sPack, sTxt, interface.FontLT14_3)
    return obj


def CreateRoleTips(parent, iShape, sTxt, \xc5Width):
    
    try:
        obj = CIconHint(parent, \xc5Width, 'photo/hero/%.3d.igs' % iShape, 'misc', sTxt, interface.FontLT14_3)
    except SystemError:
        obj = CIconHint(parent, \xc5Width, 'photo/hero/001.igs', 'misc', sTxt, interface.FontLT14_3)

    return obj


def CreateModelTips(parent, iShape, sTxt, \xc5Width):
    
    try:
        obj = CModelHint(parent, \xc5Width, iShape, sTxt, interface.FontLT14_3)
    except SystemError:
        obj = CSpriteHint(parent, \xc5Width, '0000', 'stand', chardefine.PCK_CHAR, sTxt, interface.FontLT14_3)

    return obj


def CreatePetIconTips(parent, iShape, sTxt, \xc5Width):
    
    try:
        obj = CIconHint(parent, \xc5Width, 'photo/summon/%.4d.igs' % iShape, 'misc', sTxt, interface.FontLT14_3)
    except SystemError:
        obj = CIconHint(parent, \xc5Width, 'photo/summon/0000.igs', 'misc', sTxt, interface.FontLT14_3)

    return obj


def CreateAniTips(parent, iShape, sTxt, \xc5Width):
    
    try:
        obj = CIconLearnSkill(parent, \xc5Width, 'ani/%.3d.igs' % iShape, 'misc', sTxt, interface.FontLT14_3)
    except SystemError:
        obj = CIconHint(parent, \xc5Width, 'ani/001.igs', 'misc', sTxt, interface.FontLT14_3)

    obj.SetAni()
    import sound
    sound.Play('action/graspskill.wav')
    return obj


def CreateIconTips(parent, iShape, sTxt, \xc5Width):
    
    try:
        obj = CAvatarHint(parent, \xc5Width, iShape, sTxt, interface.FontLT14_3)
    except SystemError:
        obj = CIconHint(parent, \xc5Width, 'photo/hero/001.igs', 'misc', sTxt, interface.FontLT14_3)

    return obj


def CreateImmortTips(parent, iShape, sTxt, \xc5Width):
    
    try:
        obj = CPillSkillHint(parent, \xc5Width, iShape, sTxt, interface.FontLT14_3)
    except SystemError:
        (sPath, sPack) = skilliconpath.GetSummonSkillIconPath(0)
        obj = CIconHint(parent, \xc5Width, sPath, sPack, sTxt, interface.FontLT14_3)

    return obj


def CreateAchieveTips(parent, iShape, sTxt, \xc5Width):
    
    try:
        obj = CIconHint(parent, \xc5Width, 'badge/120/%d.igs' % iShape, 'misc', sTxt, interface.FontLT14_3)
    except SystemError:
        obj = CIconHint(parent, \xc5Width, 'badge/120/11001.igs', 'misc', sTxt, interface.FontLT14_3)

    return obj

DI_TYPE_2_FUNC = {
    ITEMTYPE: CreateItemTips,
    SKILLTYPE: CreateSkillTips,
    ROLETYPE: CreateRoleTips,
    MODELTYPE: CreateModelTips,
    PETICONTYPE: CreatePetIconTips,
    ANITYPE: CreateAniTips,
    ICONTYPE: CreateIconTips,
    IMMORTTYPE: CreateImmortTips,
    ACHIEVETYPE: CreateAchieveTips }
NORMAL_MSG = normalmsg
SYSTEM_MSG = systemmsg
PROMPT_MSG = promptmsg
MOVE_MSG = movehint
MOVE_TEXT = movetext
TIPS_MSG = systips
ROLL_TEXT = rolltext
TRYAGAIN = '\xbe\xde\xa7@\xb9L\xa9\xf3\xc0W\xc1c\xa1A\xbd\xd0\xb5y\xab\xe1\xa6A\xb9\xc1\xb8\xd5'
TRYLATER = '\xbe\xde\xa7@\xb9L\xa9\xf3\xc0W\xc1c\xa1A\xbd\xd0\xb5y\xab\xe1\xa6A\xb9\xc1\xb8\xd5\xa1]\xadn\xa8D\xa8\xe2\xa6\xb8\xb6\xa1\xb9j\xa6\xdc\xa4\xd6%s\xac\xed\xa1^'
