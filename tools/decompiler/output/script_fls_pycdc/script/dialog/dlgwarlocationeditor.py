# pycdc 交叉复核产物 · script.fls entry 4874
# co_filename(原始)='script/dialog/dlgwarlocationeditor.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4874.pyc (Python 2.5)

import \xef\xf3sys
import interface
import combdialog
import walker
emoteLst = ('stand', 'clap', 'cry', 'dance', 'hi', 'love', 'laugh', 'sit', 'walk', 'attack', 'hit', 'magic', 'guard', 'die')
emote2idx = []([ (emote, idx) for idx, emote in enumerate(emoteLst) ])
g_DlgEditor = None
g_IsNewNpc = True
g_AddFakeNpc = None
g_FakeNpcDir = -1
g_TestNewLocation = 0

def ModuleReset():
    global g_DlgEditor, g_IsNewNpc, g_AddFakeNpc, g_FakeNpcDir, g_TestNewLocation
    g_DlgEditor = None
    g_IsNewNpc = True
    g_AddFakeNpc = None
    g_FakeNpcDir = -1
    g_TestNewLocation = 0
    COprateMgr.ResetClear()


def Show():
    global g_DlgEditor
    if g_DlgEditor:
        g_DlgEditor.SetShow(True)
    else:
        g_DlgEditor = CDlgEditor()


def CloseWindow():
    global g_DlgEditor
    g_DlgEditor = None


def CreateFakeRole():
    global g_AddFakeNpc
    selectedNpcID = COprateMgr.GetSelectedNpcID()
    if g_IsNewNpc or not selectedNpcID:
        defaultShape = 111
        defaultDesc = {
            'color': [
                0,
                0,
                0],
            'weapon': [
                0,
                0,
                0],
            'wing': [
                0],
            'Realcolor': [
                0,
                0,
                0] }
    else:
        (_, defaultShape, defaultDesc, _, _, _, _, _) = COprateMgr.GetNpcInfo(selectedNpcID)
    import walker
    import cursor
    if not g_AddFakeNpc:
        g_AddFakeNpc = walker.CFakeRole(cursor.Cursor, 0, defaultShape, defaultDesc)
    
    g_AddFakeNpc.SetDirection(g_FakeNpcDir)


def DoCancel():
    global g_AddFakeNpc
    g_AddFakeNpc = None
    import key
    key.RegisterHotKey(key.VK_SPACE)
    COprateMgr.SetAllNpcShow(True)


def SetNpc():
    import cursor
    (cx, cy) = cursor.GetCursorPos()
    selectedNpcID = COprateMgr.GetSelectedNpcID()
    if g_IsNewNpc or not selectedNpcID:
        defaultShape = 111
        defaultDesc = {
            'color': [
                0,
                0,
                0],
            'weapon': [
                0,
                0,
                0],
            'wing': [
                0],
            'Realcolor': [
                0,
                0,
                0] }
        defaultID = COprateMgr.GetDefaultID()
        defalutName = '%d\xb8\xb9' % defaultID
        defalutEmote = 0
    else:
        (defaultID, defaultShape, defaultDesc, _, _, _, defalutName, defalutEmote) = COprateMgr.GetNpcInfo(selectedNpcID)
    AddClientNpc(defaultID, defaultShape, defaultDesc, cx, cy, g_FakeNpcDir, defalutName, defalutEmote)
    DoCancel()


def AddClientNpc(id, shape, desc, x, y, direct, name, emote, isOperate = True):
    global g_FakeNpcDir
    obj = COprateMgr.GetNpc(id)
    if obj:
        obj.ChangeShape(shape, desc)
    else:
        bg = COprateMgr.GetWarBG()
        obj = CTestWarrior(bg, id, shape, desc)
        obj.SetTestID(id)
        COprateMgr.AddNpc(id, obj)
    npcInfo = [
        id,
        shape,
        desc,
        x,
        y,
        direct,
        name,
        emote]
    if isOperate:
        COprateMgr.AddNewAction((COprateMgr.GetNpcInfo(id), npcInfo))
    
    COprateMgr.SetNpcInfo(id, npcInfo)
    obj.SetPos(x, y)
    obj.SetZ(y)
    obj.SetDirection(direct)
    obj.SetName(name, None, 0, interface.COLOR_43)
    obj.SetEmote(emote, False)
    obj.Select()
    g_FakeNpcDir = direct


class CDlgEditor(combdialog.CCombDialog):
    INITNPCS = [
        [
            'x1',
            437,
            502,
            16,
            111,
            {
                'color': [
                    0,
                    0,
                    0],
                'weapon': [
                    0,
                    0,
                    0],
                'wing': [
                    0],
                'Realcolor': [
                    0,
                    0,
                    0] },
            'stand'],
        [
            'x2',
            511,
            465,
            16,
            111,
            {
                'color': [
                    0,
                    0,
                    0],
                'weapon': [
                    0,
                    0,
                    0],
                'wing': [
                    0],
                'Realcolor': [
                    0,
                    0,
                    0] },
            'stand'],
        [
            'x3',
            585,
            428,
            16,
            111,
            {
                'color': [
                    0,
                    0,
                    0],
                'weapon': [
                    0,
                    0,
                    0],
                'wing': [
                    0],
                'Realcolor': [
                    0,
                    0,
                    0] },
            'stand'],
        [
            'x4',
            659,
            391,
            16,
            111,
            {
                'color': [
                    0,
                    0,
                    0],
                'weapon': [
                    0,
                    0,
                    0],
                'wing': [
                    0],
                'Realcolor': [
                    0,
                    0,
                    0] },
            'stand'],
        [
            'x5',
            733,
            354,
            16,
            111,
            {
                'color': [
                    0,
                    0,
                    0],
                'weapon': [
                    0,
                    0,
                    0],
                'wing': [
                    0],
                'Realcolor': [
                    0,
                    0,
                    0] },
            'stand'],
        [
            'xx1',
            357,
            462,
            16,
            2020,
            {
                'color': [
                    0,
                    0,
                    0],
                'weapon': [
                    0,
                    0,
                    0],
                'wing': [
                    0],
                'Realcolor': [
                    0,
                    0,
                    0] },
            'stand'],
        [
            'xx2',
            431,
            425,
            16,
            2020,
            {
                'color': [
                    0,
                    0,
                    0],
                'weapon': [
                    0,
                    0,
                    0],
                'wing': [
                    0],
                'Realcolor': [
                    0,
                    0,
                    0] },
            'stand'],
        [
            'xx3',
            505,
            388,
            16,
            2020,
            {
                'color': [
                    0,
                    0,
                    0],
                'weapon': [
                    0,
                    0,
                    0],
                'wing': [
                    0],
                'Realcolor': [
                    0,
                    0,
                    0] },
            'stand'],
        [
            'xx4',
            579,
            351,
            16,
            2020,
            {
                'color': [
                    0,
                    0,
                    0],
                'weapon': [
                    0,
                    0,
                    0],
                'wing': [
                    0],
                'Realcolor': [
                    0,
                    0,
                    0] },
            'stand'],
        [
            'xx5',
            534,
            314,
            16,
            2020,
            {
                'color': [
                    0,
                    0,
                    0],
                'weapon': [
                    0,
                    0,
                    0],
                'wing': [
                    0],
                'Realcolor': [
                    0,
                    0,
                    0] },
            'stand']]
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/warlocation.dlg')
        self.SetPos(50, 100)
        self.CreateEdits()
        self.Inits()

    
    class CMyEdit(interface.CEdit):
        
        def MsgEnter(self):
            par = self.GetParent()
            if hasattr(par, 'ConfirmChange'):
                par.ConfirmChange()
            


    
    def CreateEdits(self):
        import wrapinterface
        edtInfoLst = [
            ('edt_npc', 'm_NameEdit'),
            ('edt_shape', 'm_ShapeEdit'),
            ('edt_color', 'm_ColorEdit'),
            ('edt_dir', 'm_DirEdit')]
        import combmacro
        for objName, attr in enumerate(edtInfoLst):
            editObj = combmacro.CEDIT(self.CMyEdit, objName, self, 0, interface.FontLT14_3)
            setattr(self, attr, editObj)
            editObj.SetLimit(40)
            if idx == 0:
                editObj.Active(True)
                continue
        

    
    def Inits(self):
        if not self.INITNPCS:
            return None
        
        
        def doAddNpc(obj):
            for name, x, y, direct, shape, desc, emote in enumerate(self.INITNPCS):
                if not name:
                    name = ''
                
                emote = emote2idx.get(emote, 0)
                AddClientNpc(1000 + idx, shape, desc, x, y, direct, name, emote, '')
            
            obj.m_AddNpcCmd = None

        self.m_AddNpcCmd = self.CreatePyCommand(30, doAddNpc)
        self.MoveLine(0, 500, 740, 130)

    
    def MoveLine(self, iX1, iY1, iX2, iY2):
        self.m_Line = interface.CLine(None, iX1, iY1, iX2, iY2, 16711680, 2)
        self.m_Line.SetZ(2)

    
    def Desc2Txt(self, desc):
        colorLst = []
        colorLst.extend(desc['color'])
        colorLst.extend(desc['weapon'])
        if 'weapon2' in desc and 'weapon3' in desc:
            del colorLst[-1]
            colorLst.extend(desc['weapon2'])
            colorLst.extend(desc['weapon3'])
        
        colorStrLst = [ str(i) for i in colorLst ]
        return ','.join(colorStrLst)

    
    def SetNpcInfo(self, npcInfo = None):
        if not npcInfo:
            self.m_NameEdit.Clear()
            self.m_ShapeEdit.Clear()
            self.m_ColorEdit.Clear()
            self.m_DirEdit.Clear()
            return None
        
        (id, shape, desc, x, y, direct, name, emote) = npcInfo
        
        try:
            emoteTxt = emoteLst[emote]
        except:
            emoteTxt = 'stand'

        direct /= 4
        direct = ((direct % 2) * 4 + direct / 2) % 8 + 1
        shapeTxt = '%d|%s' % (shape, emoteTxt)
        colorTxt = self.Desc2Txt(desc)
        posTxt = '%d,%d,%d' % (x, y, direct)
        self.m_NameEdit.SetText(name)
        self.m_ShapeEdit.SetText(shapeTxt)
        self.m_ColorEdit.SetText(colorTxt)
        self.m_DirEdit.SetText(posTxt)

    
    def GetNpcName(self):
        nameTxt = self.m_NameEdit.GetText()
        return nameTxt

    
    def GetNpcShape(self):
        shapeTxt = self.m_ShapeEdit.GetText()
        import usermacro
        
        try:
            (sShape, sEmote) = shapeTxt.split('|')
            shape = int(sShape)
            emote = emote2idx.get(sEmote, 0)
        except:
            usermacro.PROMPT_MSG('\xbd\xd0\xab\xf6\xa1u\xb3y\xab\xac\xbds\xb8\xb9|\xb0\xca\xa7@\xa1v\xaa\xba\xae\xe6\xa6\xa1\xbf\xe9\xa4J\xb3y\xab\xac')
            return None

        return (shape, emote)

    
    def GetNpcDesc(self):
        txt = self.m_ColorEdit.GetText()
        txtLst = txt.split(',')
        iLen = len(txtLst)
        if iLen not in (6, 9):
            import usermacro
            usermacro.PROMPT_MSG('\xbd\xd0\xbf\xe9\xa4J6\xa6\xec\xa9\xce9\xa6\xec\xacV\xa6\xe2\xabH\xae\xa7')
            return None
        
        idxLst = [ int(i) for i in txtLst ]
        desc = {
            'wing': [
                0] }
        return desc

    
    def GetNpcPos(self):
        posTxt = self.m_DirEdit.GetText()
        
        try:
            (x, y, dire) = posTxt.split(',')
            dire = (int(dire) + 7) % 8
            dire = ((dire % 4) * 2 + dire / 4) * 4
        except:
            import usermacro
            usermacro.PROMPT_MSG('\xbd\xd0\xab\xf6\xa1ux,y,dir\xa1v\xaa\xba\xae\xe6\xa6\xa1\xbf\xe9\xa4J\xa6\xec\xb8m\xabH\xae\xa7')
            return None

        return (int(x), int(y), dire)

    
    def AddNpc(self):
        global g_IsNewNpc
        import world
        import key
        g_IsNewNpc = True
        world.AddTestWarrior()
        CreateFakeRole()
        key.RegisterHotKey(key.VK_SPACE, CreateFakeRole)

    
    def DelNpc(self):
        selectedNpcID = COprateMgr.GetSelectedNpcID()
        if not selectedNpcID:
            import usermacro
            usermacro.PROMPT_MSG('\xbd\xd0\xa5\xfd\xbf\xef\xbe\xdc\xbb\xdd\xadn\xa7R\xb0\xa3\xaa\xbaNPC')
            return None
        
        self.SetNpcInfo()
        COprateMgr.AddNewAction((COprateMgr.GetNpcInfo(selectedNpcID), None))
        COprateMgr.DelNpc(selectedNpcID)
        COprateMgr.SetSelectedNpcID(None)

    
    def MoveNpc(self):
        global g_IsNewNpc
        selectedNpcID = COprateMgr.GetSelectedNpcID()
        if not selectedNpcID:
            import usermacro
            usermacro.PROMPT_MSG('\xbd\xd0\xa5\xfd\xbf\xef\xbe\xdc\xbb\xdd\xadn\xb2\xbe\xb0\xca\xaa\xbaNPC')
            return None
        
        import world
        import key
        g_IsNewNpc = False
        world.AddTestWarrior()
        npcObj = COprateMgr.GetNpc(selectedNpcID)
        npcObj.SetShow(False)
        CreateFakeRole()
        key.RegisterHotKey(key.VK_SPACE, CreateFakeRole)

    
    def ConfirmChange(self):
        selectedNpcID = COprateMgr.GetSelectedNpcID()
        if not selectedNpcID:
            import usermacro
            usermacro.PROMPT_MSG('\xbd\xd0\xa5\xfd\xbf\xef\xbe\xdc\xbb\xdd\xadn\xad\xd7\xa7\xef\xaa\xbaNPC')
            return None
        
        name = self.GetNpcName()
        shapeInfo = self.GetNpcShape()
        desc = self.GetNpcDesc()
        posInfo = self.GetNpcPos()
        if not shapeInfo and desc and posInfo:
            return None
        
        (shape, emote) = shapeInfo
        (x, y, direct) = posInfo
        AddClientNpc(selectedNpcID, shape, desc, x, y, direct, name, emote)

    
    def HideWindow(self):
        self.SetShow(False)
        import dlgminipanel
        dlgminipanel.ShowTestWarriorPanel()

    
    def LoadNpcInfo(self):
        if getattr(self, 'm_AddNpcCmd', None):
            import usermacro
            usermacro.PROMPT_MSG('NPC\xa9|\xa5\xbc\xa5[\xb8\xfc\xa6\xa8\xa5\\\xa1A\xbd\xd0\xb5y\xab\xe1\xa6A\xb8\xd5')
        
        import map
        npcInfoLst = COprateMgr.GetWarData()
        if not npcInfoLst:
            return None
        
        
        def doAddNpc(obj):
            for name, x, y, direct, shape, desc, emote in enumerate(npcInfoLst):
                if not name:
                    name = ''
                
                emote = emote2idx.get(emote, 0)
                AddClientNpc(10000 + idx, shape, desc, x, y, direct, name, emote, '')
            
            obj.m_AddNpcCmd = None

        self.m_AddNpcCmd = self.CreatePyCommand(30, doAddNpc)

    
    def OnResetLine(self):
        import commondialog
        import misc
        commondialog.ShowInputDialog('\xbd\xd0\xbf\xe9\xa4J\xa7\xa4\xbc\xd0\xa1C\xaa\xec\xa9l\xa7\xa4\xbc\xd00 500 740 130', misc.Functor(self.OnResetLineCB))

    
    def OnResetLineCB(self, oDlg, sTxt):
        sPosList = sTxt.split()
        
        try:
            self.MoveLine(int(sPosList[0]), int(sPosList[1]), int(sPosList[2]), int(sPosList[3]))
        except:
            pass


    
    def OnMessage(self, msgid):
        if self.m_AddNpcCmd:
            import usermacro
            usermacro.PROMPT_MSG('NPC\xa5\xbf\xa6b\xb8\xfc\xa4J\xa4\xa4\xa1A\xbd\xd0\xb5y\xab\xe1\xa6A\xb8\xd5')
            return None
        
        if msgid == 1:
            self.HideWindow()
        elif msgid == 2:
            self.AddNpc()
        elif msgid == 3:
            self.DelNpc()
        elif msgid == 4:
            self.MoveNpc()
        elif msgid == 5:
            self.ConfirmChange()
        elif msgid == 6:
            COprateMgr.SaveNpcInfo()
        elif msgid == 7:
            COprateMgr.LastAction()
        elif msgid == 8:
            COprateMgr.NextAction()
        elif msgid == 9:
            self.LoadNpcInfo()
        elif msgid == 10:
            COprateMgr.ReleaseAll()
        elif msgid == 11:
            self.OnResetLine()
        



class CTestWarrior(walker.CFakeRole):
    
    def SetTestID(self, checkID):
        self.m_CheckID = checkID

    
    def LeftUp(self):
        t = \xef\xf3sys.GetTime()
        if hasattr(self, 'm_LeftUpTime'):
            if t - self.m_LeftUpTime < 5000:
                self.LeftDoubleClick()
                return None
            
        
        self.m_LeftUpTime = t
        self.Select()

    
    def Select(self):
        import world
        selectedNpcID = COprateMgr.GetSelectedNpcID()
        lastSelectedNpc = COprateMgr.GetNpc(selectedNpcID)
        if lastSelectedNpc:
            lastSelectedNpc.SetAura()
        
        self.SetAura(13)
        COprateMgr.SetSelectedNpcID(self.m_CheckID)
        g_DlgEditor.SetNpcInfo(COprateMgr.GetNpcInfo(self.m_CheckID))

    
    def LeftDoubleClick(self):
        if g_DlgEditor:
            g_DlgEditor.MoveNpc()
        



class CWarBG(interface.CStretchImagesObject, interface.CBase):
    
    def __init__(self, parent, fileName, pakage):
        interface.CStretchImagesObject.__init__(self, parent, fileName, pakage)
        self.MessageProcess()

    
    def LeftUp(self):
        COprateMgr.NextAction()

    
    def RightUp(self):
        COprateMgr.LastAction()

    
    def CreateWarBG():
        import ratio
        fileName = None if ratio.Is1366x768() or ratio.Is1366x708() else 'warbackground_1.igs'
        scale = None if ratio.Is1024x768() else 1
        bgObj = CWarBG(None, fileName, interface.UIPath)
        bgObj.SetScale(scale)
        bgObj.SetZ(1)
        return bgObj

    CreateWarBG = staticmethod(CreateWarBG)


class COprateMgr:
    s_WarBG = None
    s_LastActLst = []
    s_NextActLst = []
    s_NpcInfo = { }
    s_NpcDct = { }
    s_SelectedNpcID = None
    
    def ResetClear(cls):
        cls.s_WarBG = None
        cls.s_LastActLst = []
        cls.s_NextActLst = []
        cls.s_NpcInfo = { }
        cls.s_NpcDct = { }
        cls.s_SelectedNpcID = None

    ResetClear = classmethod(ResetClear)
    
    def StartEditor(cls):
        cls.GetWarBG()
        Show()

    StartEditor = classmethod(StartEditor)
    
    def ReleaseAll(cls):
        cls.s_WarBG = None
        cls.s_LastActLst = []
        cls.s_NextActLst = []
        cls.s_NpcInfo = { }
        cls.s_NpcDct = { }
        cls.s_SelectedNpcID = None
        CloseWindow()
        import dlgminipanel
        if isinstance(dlgminipanel.g_MiniPanel, dlgminipanel.CTestWarriorMiniPanel):
            dlgminipanel.CloseMiniPanel()
        

    ReleaseAll = classmethod(ReleaseAll)
    
    def AddNewAction(cls, iTuple):
        if iTuple == (None, None):
            return None
        
        cls.s_LastActLst.append(iTuple)
        cls.s_NextActLst = []

    AddNewAction = classmethod(AddNewAction)
    
    def LastAction(cls):
        if not cls.s_LastActLst:
            return None
        
        (lastNpcInfo, nextNpcInfo) = cls.s_LastActLst.pop()
        cls.s_NextActLst.append((lastNpcInfo, nextNpcInfo))
        if lastNpcInfo is None:
            cls.DelNpc(nextNpcInfo[0])
        else:
            AddClientNpc(isOperate = False, *lastNpcInfo)

    LastAction = classmethod(LastAction)
    
    def NextAction(cls):
        if not cls.s_NextActLst:
            return None
        
        (lastNpcInfo, nextNpcInfo) = cls.s_NextActLst.pop()
        cls.s_LastActLst.append((lastNpcInfo, nextNpcInfo))
        if nextNpcInfo is None:
            cls.DelNpc(lastNpcInfo[0])
        else:
            AddClientNpc(isOperate = False, *nextNpcInfo)

    NextAction = classmethod(NextAction)
    
    def GetWarBG(cls):
        if not cls.s_WarBG:
            cls.s_WarBG = CWarBG.CreateWarBG()
        
        return cls.s_WarBG

    GetWarBG = classmethod(GetWarBG)
    
    def GetDefaultID(cls):
        num = len(cls.s_NpcInfo)
        if num > 0:
            for idx in range(1, num + 1):
                if idx not in cls.s_NpcInfo:
                    return idx
                    continue
            
        
        return num + 1

    GetDefaultID = classmethod(GetDefaultID)
    
    def SetSelectedNpcID(cls, idx):
        cls.s_SelectedNpcID = idx

    SetSelectedNpcID = classmethod(SetSelectedNpcID)
    
    def GetSelectedNpcID(cls):
        return cls.s_SelectedNpcID

    GetSelectedNpcID = classmethod(GetSelectedNpcID)
    
    def AddNpc(cls, idx, obj):
        cls.s_NpcDct[idx] = obj

    AddNpc = classmethod(AddNpc)
    
    def DelNpc(cls, idx):
        if idx in cls.s_NpcInfo:
            del cls.s_NpcInfo[idx]
            del cls.s_NpcDct[idx]
        

    DelNpc = classmethod(DelNpc)
    
    def GetNpc(cls, idx):
        return cls.s_NpcDct.get(idx)

    GetNpc = classmethod(GetNpc)
    
    def SetAllNpcShow(cls, isShow):
        for npcObj in cls.s_NpcDct.values():
            npcObj.SetShow(isShow)
        

    SetAllNpcShow = classmethod(SetAllNpcShow)
    
    def SetNpcInfo(cls, idx, info):
        cls.s_NpcInfo[idx] = info

    SetNpcInfo = classmethod(SetNpcInfo)
    
    def GetNpcInfo(cls, idx):
        return cls.s_NpcInfo.get(idx)

    GetNpcInfo = classmethod(GetNpcInfo)
    
    def Get800x600Pos(cls, x, y):
        import ratio
        rateX = 800 / ratio.WINDOW_WIDTH
        rateY = 600 / ratio.WINDOW_HEIGHT
        x = int(x * rateX)
        y = int(y * rateY)
        return (x, y)

    Get800x600Pos = classmethod(Get800x600Pos)
    
    def SaveNpcInfo(cls):
        idLst = cls.s_NpcInfo.keys()
        idLst.sort()
        npcLst = []
        for npcID in idLst:
            (npcID, shape, desc, x, y, direct, name, emote) = cls.GetNpcInfo(npcID)
            if npcID <= npcID:
                pass
            elif npcID <= 1010:
                continue
            
            direct /= 4
            direct = ((direct % 2) * 4 + direct / 2) % 8 + 1
            (x, y) = cls.Get800x600Pos(x, y)
            txt = '%s\t%d,%d,%d\t' % (name, x, y, direct)
            shapeTxt = '%d(%d,%d,%d,%d,%d,%d)' % (shape, desc['color'][0], desc['color'][1], desc['color'][2], desc['weapon'][0], desc['weapon'][1], desc['weapon'][2])
            txt += shapeTxt
            if 'weapon2' in desc and 'weapon3' in desc:
                colorTxt = '\tDESC(%d,%d,%d,%d,%d,%d,%d,%d,%d)' % (desc['color'][0], desc['color'][1], desc['color'][2], desc['weapon'][0], desc['weapon'][1], desc['weapon2'][0], desc['weapon2'][1], desc['weapon3'][0], desc['weapon3'][1])
                txt += colorTxt
            
            txt = '%s\t%s' % (txt, emoteLst[emote])
            if emote != 0:
                txt += '(EMOTE%d)' % emote
            
            npcLst.append(txt)
        
        import os
        ls = os.linesep
        f = open('data/warlocation.desc', 'w')
        []([ '%s%s' % (line, '\n') for line in npcLst ])
        f.close()
        import usermacro
        cwd = os.getcwd()
        fileName = '%s\\%s' % (cwd, 'data\\warlocation.desc')
        usermacro.PROMPT_MSG('\xbe\xc9\xa5X\xbc\xc6\xbe\xda\xa6\xa8\xa5\\\xa1A\xbd\xd0\xacd\xac\xdd%s' % fileName)

    SaveNpcInfo = classmethod(SaveNpcInfo)
    
    def GetWarData(cls):
        import os
        import \xef\xf3sys
        cwd = os.getcwd()
        
        try:
            path = \xef\xf3sys.GetOpenFileName('\xbf\xef\xbe\xdc\xb9\xcf\xa4\xf9', '\xa4\xe5\xa5\xbb(*.txt)\x00*.desc\x00', '')
        except:
            path = None
        finally:
            os.chdir(cwd)

        if not path:
            return None
        
        f = file(path, 'r')
        data = f.read()
        f.close()
        if not data:
            return []
        
        npcInfoLst = []
        for line in data.split('\n'):
            info = line.split('\t')
            if len(info) != 4:
                continue
            
            name = info[0]
            (x, y, direct) = info[1].split(',')
            (shape, subinfo) = info[2].split('(')
            (c1, c2, c3, w1, w2, w3) = subinfo[:-1].split(',')
            desc = {
                'color': [
                    int(c1),
                    int(c2),
                    int(c3)],
                'weapon': [
                    int(w1),
                    int(w2),
                    int(w3)],
                'wing': [
                    0],
                'Realcolor': [
                    0,
                    0,
                    0] }
            emote = info[3]
            npcInfoLst.append([
                name,
                int(x),
                int(y),
                int(direct),
                int(shape),
                desc,
                emote])
        
        return npcInfoLst

    GetWarData = classmethod(GetWarData)


def TestNewLocation(warLocation):
    global g_TestNewLocation
    g_TestNewLocation = warLocation


def GetTestWarLocation():
    return g_TestNewLocation
