# pycdc 交叉复核产物 · script.fls entry 1998
# co_filename(原始)='script/dialog/dlgsummonwar.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1998.pyc (Python 2.5)

import interface
import combdialog
g_PetsInfo = { }
g_WarDlg = None
g_TextTips = None
g_PetsOrder = {
    16: [
        0] * 16,
    8: [
        0] * 8,
    4: [
        0] * 4,
    2: [
        0] * 2,
    1: [
        0] }

def ModuleReset():
    global g_WarDlg, g_TextTips, g_PetsInfo, g_PetsOrder
    g_WarDlg = None
    g_TextTips = None
    g_PetsInfo = { }
    g_PetsOrder = {
        16: [
            0] * 16,
        8: [
            0] * 8,
        4: [
            0] * 4,
        2: [
            0] * 2,
        1: [
            0] }


def Show():
    global g_WarDlg, g_WarDlg
    if g_WarDlg:
        g_WarDlg = None
        ClearPetsInfo()
    else:
        g_WarDlg = CWarDialog()


def ClearPetsInfo():
    global g_PetsInfo, g_PetsOrder
    g_PetsInfo = { }
    g_PetsOrder = {
        16: [
            0] * 16,
        8: [
            0] * 8,
        4: [
            0] * 4,
        2: [
            0] * 2,
        1: [
            0] }


def Group2PID(group):
    return g_PetsOrder[16][group]


def Set16Pets(pets, pos):
    if 'pid' in pets:
        pid = pets['pid']
        g_PetsInfo[pid] = pets
        g_PetsOrder[16][pos] = pid
    


def Set8Pets(pgroup, pos):
    g_PetsOrder[8][pos] = Group2PID(pgroup)


def Set4Pets(pgroup, pos):
    g_PetsOrder[4][pos] = Group2PID(pgroup)


def Set2Pets(pgroup, pos):
    g_PetsOrder[2][pos] = Group2PID(pgroup)


def SetWinner(pgroup):
    while None:
        g_PetsOrder[1][0] = pgroup
        return None


def C2SPlayMatch(match):
    import net
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_HOUSE)
    netobj.PacketAddI(18, 1)
    netobj.PacketAddI(match, 1)
    netobj.PacketSend()


def ShowTextTips(txt):
    global g_TextTips, g_TextTips
    if txt:
        import wrapinterface
        g_TextTips = wrapinterface.CTextTips(None, -1, txt, interface.FontLT14_3)
        g_TextTips.Topmost()
    else:
        g_TextTips = None


class CImageBox(interface.CImageBox):
    
    def Enter(self):
        parent = self.GetParent()
        if parent and hasattr(parent, 'OnEnter'):
            parent.OnEnter(self)
        

    
    def Leave(self):
        
        try:
            parent = self.GetParent()
        except SystemError:
            return None

        if parent and hasattr(parent, 'OnLeave'):
            parent.OnLeave(self)
        



class CSummonFrame(interface.CBoxObject):
    
    def __init__(self, parent, info, photo_right = True):
        alpha = interface.COLOR_280
        interface.CBoxObject.__init__(self, parent, 148, 48, 0, alpha)
        self.SetOwnerName(info[0])
        self.SetSummonName(info[1])
        self.SetSummonPhoto(info[2])
        self.SetSummonID(info[3])
        self.SetSummonPos(info[4])
        self.Refresh(photo_right)

    
    def SetSummonID(self, id):
        self.m_SID = id

    
    def SetSummonPos(self, pos):
        self.m_SPos = pos

    
    def SetOwnerName(self, name):
        self.m_OwnerName = interface.CTextObject(self, name, interface.FontLT14_3, interface.COLOR_1)

    
    def SetSummonName(self, name):
        self.m_SummonName = interface.CTextObject(self, name, interface.FontLT14_3, interface.COLOR_1)

    
    def SetSummonPhoto(self, photo):
        self.m_Photo = CImageBox(self, photo, interface.UIPath, 0)

    
    def OnEnter(self, obj):
        sid = self.m_SID
        txt = '\xae\xf0\xa6\xe5 ?#r\xa7\xf0\xc0\xbb ?#r\xaak\xb3N\xa7\xf0\xc0\xbb ?#r\xa8\xbe\xbfm ?#r\xaak\xb3N\xa8\xbe\xbfm ?#r\xb3t\xab\xd7 ?'
        if sid in g_PetsInfo:
            import petfightdata
            data = petfightdata.GetPetData(g_PetsInfo[sid])
            data = data['attr']
            [
                'hp',
                'at',
                'df',
                'mg',
                'md',
                'sp']
            txt = '\xae\xf0\xa6\xe5 %d#r\xa7\xf0\xc0\xbb %d#r\xaak\xb3N\xa7\xf0\xc0\xbb %d#r\xa8\xbe\xbfm %d#r\xaak\xb3N\xa8\xbe\xbfm %d#r\xb3t\xab\xd7 %d' % (data['hp'], data['at'], data['mg'], data['df'], data['md'], data['sp'])
        
        ShowTextTips(txt)

    
    def OnLeave(self, obj):
        ShowTextTips(None)

    
    def Refresh(self, photo_right):
        if photo_right:
            POSITION = [
                (105, 5),
                (5, 5),
                (5, 29)]
        else:
            POSITION = [
                (5, 5),
                (48, 5),
                (48, 29)]
        for idx, item in enumerate([
            self.m_Photo,
            self.m_OwnerName,
            self.m_SummonName]):
            (w, h) = POSITION[idx]
            item.SetPos(*POSITION[idx])
        


SHAPE_TO_FILENAME = {
    1: TW_NOCHANGE('\xd0\xa1\xce\xda\xb9\xea'),
    2: TW_NOCHANGE('\xc0\xf0\xd3\xe3'),
    3: TW_NOCHANGE('\xc7\xe0\xcd\xdc'),
    4: TW_NOCHANGE('\xc2\xdd'),
    5: TW_NOCHANGE('\xd5\xe4\xd6\xe9\xc2\xed\xbc\xd7'),
    6: TW_NOCHANGE('\xd0\xa1\xb3\xf3\xd3\xe3'),
    7: TW_NOCHANGE('\xbb\xf0\xd1\xe6\xcf\xba'),
    8: TW_NOCHANGE('\xba\xa3\xd4\xc2\xcb\xae\xc4\xb8'),
    9: TW_NOCHANGE('\xc6\xdf\xb2\xca\xc9\xf1\xd3\xe3'),
    10: TW_NOCHANGE('\xc1\xfa\xd3\xe3'),
    11: TW_NOCHANGE('\xb5\xc6\xc1\xfd\xd3\xe3'),
    12: TW_NOCHANGE('\xf7\xa5\xd3\xe3'),
    13: TW_NOCHANGE('\xc1\xfa\xb9\xea'),
    14: TW_NOCHANGE('\xb7\xd6\xcb\xae\xf6\xef'),
    31: TW_NOCHANGE('\xb4\xf3\xbb\xc6\xb9\xb7'),
    32: TW_NOCHANGE('\xba\xfb\xb5\xfb\xc8\xae'),
    33: TW_NOCHANGE('\xcc\xa4\xd4\xc2\xba\xfc'),
    34: TW_NOCHANGE('\xcd\xcc\xd4\xc6\xca\xde'),
    35: TW_NOCHANGE('\xc0\xc1\xd0\xdc'),
    36: TW_NOCHANGE('\xbe\xc5\xc9\xab\xc2\xb9'),
    37: TW_NOCHANGE('\xcc\xab\xb3\xf5\xca\xde'),
    38: TW_NOCHANGE('\xbb\xf0\xba\xef'),
    61: TW_NOCHANGE('\xf0\xd0\xf0\xc4'),
    62: TW_NOCHANGE('\xb1\xe4\xc9\xab\xc1\xfa'),
    63: TW_NOCHANGE('\xc1\xfa\xc3\xa8'),
    91: TW_NOCHANGE('\xba\xfb\xb5\xfb'),
    92: TW_NOCHANGE('\xba\xfb\xb5\xfb'),
    93: TW_NOCHANGE('\xba\xfb\xb5\xfb'),
    94: TW_NOCHANGE('\xba\xfb\xb5\xfb'),
    95: TW_NOCHANGE('\xba\xfb\xb5\xfb'),
    96: TW_NOCHANGE('\xba\xfb\xb5\xfb'),
    97: TW_NOCHANGE('\xba\xfb\xb5\xfb'),
    98: TW_NOCHANGE('\xba\xfb\xb5\xfb'),
    99: TW_NOCHANGE('\xba\xfb\xb5\xfb'),
    121: TW_NOCHANGE('\xd0\xa1\xbb\xa8\xc3\xa8'),
    122: TW_NOCHANGE('\xbc\xa6'),
    123: TW_NOCHANGE('\xbc\xa6'),
    124: TW_NOCHANGE('\xd0\xdc\xc3\xa8\xcd\xc3'),
    125: TW_NOCHANGE('\xb2\xa8\xcb\xb9\xc3\xa8') }

class CWarDialog(combdialog.CCombDialog):
    SHAPE_NUM = range(1, 15) + range(31, 39) + range(61, 64) + range(91, 100) + range(121, 126)
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/summon_fight/summonwar.dlg')
        interface.Center(self)
        self.m_SummonList = [
            None] * 16
        self.m_IconMsgBase = 200
        self.m_IconList = [
            None] * 15
        self.Refresh()

    
    def Refresh(self):
        for idx, pid in enumerate(g_PetsOrder[16]):
            if pid:
                pet = g_PetsInfo[pid]
                self.SetSummon(idx, pid)
                continue
        
        print '16\xb1j\xabH\xae\xa7\xa8\xea\xb7s'
        for idx, pid in enumerate(g_PetsOrder[8]):
            if pid:
                pet = g_PetsInfo[pid]
                self.SetIcon(idx, pid)
                pos = pet['pos']
                p1 = ('left', 'right')[pos / 8]
                p2 = ('up', 'down')[pos % 2]
                obj = self.GetObject('%s_%s_16_8' % (p1, p2))
                img = obj.GetImage(0, pos / 2 % 4)
                img.SetFrame(1)
                continue
        
        print '8\xb1j\xabH\xae\xa7\xa8\xea\xb7s'
        for idx, pid in enumerate(g_PetsOrder[4]):
            if pid:
                pet = g_PetsInfo[pid]
                self.SetIcon(8 + idx, pid)
                pos = pet['pos']
                p1 = ('left', 'right')[pos / 8]
                p2 = ('up', 'down')[pos / 2 % 2]
                obj = self.GetObject('%s_%s_8_4' % (p1, p2))
                img = obj.GetImage(0, pos / 4 % 2)
                img.SetFrame(1)
                continue
        
        print '4\xb1j\xabH\xae\xa7\xa8\xea\xb7s'
        for idx, pid in enumerate(g_PetsOrder[2]):
            if pid:
                pet = g_PetsInfo[pid]
                self.SetIcon(12 + idx, pid)
                pos = pet['pos']
                p1 = ('left', 'right')[pos / 8]
                p2 = ('up', 'down')[pos / 4 % 2]
                obj = self.GetObject('%s_%s_4_2' % (p1, p2))
                img = obj.GetImage(0, 0)
                img.SetFrame(1)
                continue
        
        print '2\xb1j\xabH\xae\xa7\xa8\xea\xb7s'
        if len(g_PetsOrder[1]) and g_PetsOrder[1][0]:
            pid = g_PetsOrder[1][0]
            pet = g_PetsInfo[pid]
            self.SetIcon(14, pid)
            pos = pet['pos']
            obj = self.GetObject('final')
            img = obj.GetImage(0, int(pos >= 8))
            img.SetFrame(1)
        
        print '1\xb1j\xabH\xae\xa7\xa8\xea\xb7s'

    
    def SetSummon(self, index, petid):
        import style
        pet = g_PetsInfo[petid]
        shape = pet['shape']
        owner = pet['owner']
        sname = pet['name']
        pet['pos'] = index
        sfr = self.m_SummonList[index]
        fname = 'summon/%s.igs' % SHAPE_TO_FILENAME[shape]
        if sfr is None:
            sfr = CSummonFrame(self, [
                owner,
                sname,
                fname,
                petid,
                index], index < 8)
            self.m_SummonList[index] = sfr
        else:
            sfr.SetOwnerName(owner)
            sfr.SetSummonName(sname)
            sfr.SetSummonPhoto(fname)
            sfr.Refresh(index < 8)
        if index < 8:
            objname = 'panel_left'
        else:
            objname = 'panel_right'
        obj = self.GetObject(objname)
        img = obj.GetImage(0, index % 8)
        (x1, y1) = obj.GetPos()
        (x2, y2) = img.GetPos()
        offx = style.GetInt(self.GetDlgPath(), 'data_sfr')
        sfr.SetPos(x1 + x2 + offx, y1 + y2)

    
    def SetIcon(self, pos, petid):
        if petid in g_PetsInfo:
            pet = g_PetsInfo[petid]
            img = CImageBox(self, 'summon/%s.igs' % SHAPE_TO_FILENAME[pet['shape']], interface.UIPath, self.m_IconMsgBase + pos)
            img.m_SmPos = pet['pos']
            
            def _GetPos(pos):
                _ObjData = {
                    0: ('icon0', 0, 0),
                    1: ('icon0', 0, 1),
                    2: ('icon0', 0, 2),
                    3: ('icon0', 0, 3),
                    4: ('icon1', 0, 0),
                    5: ('icon1', 0, 1),
                    6: ('icon1', 0, 2),
                    7: ('icon1', 0, 3),
                    8: ('icon2', 0, 0),
                    9: ('icon2', 0, 1),
                    10: ('icon3', 0, 0),
                    11: ('icon3', 0, 1),
                    12: ('icon4', 0, 0),
                    13: ('icon4', 0, 2),
                    14: ('icon4', 0, 1) }
                (name, row, col) = _ObjData[pos]
                obj = self.GetObject(name)
                img = obj.GetImage(row, col)
                (x1, y1) = obj.GetPos()
                (x2, y2) = img.GetPos()
                return (x1 + x2 + 4, y1 + y2 + 4)

            img.SetPos(*_GetPos(pos))
            self.m_IconList[pos] = img
        

    
    def OnEnter(self, obj):
        if hasattr(obj, 'm_SmPos'):
            sfr = self.m_SummonList[obj.m_SmPos]
            if hasattr(sfr, 'OnEnter'):
                sfr.OnEnter(None)
            
        

    
    def OnLeave(self, obj):
        if hasattr(obj, 'm_SmPos'):
            sfr = self.m_SummonList[obj.m_SmPos]
            if hasattr(sfr, 'OnLeave'):
                sfr.OnLeave(None)
            
        

    
    def OnMessage(self, msgid):
        if msgid == 1:
            Show()
        elif msgid <= msgid:
            pass
        elif msgid < self.m_IconMsgBase + 15:
            C2SPlayMatch(msgid - self.m_IconMsgBase)
        else:
            print 'CWarDialog::OnMessage ', msgid
