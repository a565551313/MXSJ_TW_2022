# pycdc 交叉复核产物 · script.fls entry 560
# co_filename(原始)='script/blacklist/characteristic.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_560.pyc (Python 2.5)

'''\xcc\xd8\xd5\xf7\xd6\xb5\xbc\xec\xb2\xe9\xc4\xa3\xbf\xe9
'''
import processlib
g_ProcessDct = { }
g_ProcessPathList = []
g_RunObject = None

def ModuleReset(mode = 0):
    global g_ProcessDct, g_ProcessPathList, g_RunObject
    g_ProcessDct = { }
    g_ProcessPathList = []
    g_RunObject = None
    CCheckHomeKey.Clear()


def Start():
    global g_RunObject
    if not g_RunObject:
        import interface
        g_RunObject = interface.CBaseObject(None)
    
    
    def CheckLoop(obj, lst, rule):
        if not rule:
            args = lst.pop()
            rule = CRules(*args)
        
        if rule.Run():
            return (lst, rule)
        
        if lst:
            return (lst, None)
        
        print '\xafS\xbcx\xad\xc8\xc0\xcb\xacd\xa7\xb9\xb2\xa6~~~~~~'

    g_RunObject.CreatePyCommand(30, CheckLoop, g_RuleList[::-1], None)


class CCharacteristic(object):
    
    def Run(self):
        '''\xb6}\xb1\xd2\xa4@\xa6\xb8\xafS\xbcx\xad\xc8\xc0\xcb\xacd\xa1A\xc0\xcb\xacd\xb5L\xbb~\xabh\xaa\xf0\xa6^False\xaa\xed\xa5\xdc\xb5\xb2\xa7\xf4\xa1A\xa7_\xabh\xaa\xf0\xa6^True\xaa\xed\xa5\xdc\xc1\xd9\xbb\xdd\xadn\xc4~\xc4\xf2\xb0\xf5\xa6\xe6\xa1A\xc0\xcb\xacd\xb5\xb2\xaaG\xa6bGetResult\xb8\xcc\xc0\xf2\xa8\xfa
\t\t'''
        return False

    
    def GetResult(self):
        '''\xc0\xcb\xacd\xb5\xb2\xaaG\xa1A\xaa\xf0\xa6^None\xa9\xce\xaa\xc5\xa6r\xb2\xc5\xa6\xea\xaa\xed\xa5\xdc\xb5L\xbb~\xa1A\xa7_\xabh\xaa\xf0\xa6^\xb5\xb2\xaaG\xa4\xe5\xa5\xbb
\t\t'''
        return ''



class CRules(object):
    
    def __init__(self, \xa8\xb5\xa8le, *args):
        self.m_Title = \xa8\xb5\xa8le
        self.m_List = [ cls() for cls in args ]
        self.m_DescList = []

    
    def Run(self):
        '''
\t\t\xb6}\xb1\xd2\xa4@\xad\xd3\xb3W\xabh\xc0\xcb\xacd\xa1A\xa8\xcc\xa6\xb8\xb9\xef\xa6h\xad\xd3\xafS\xbcx\xad\xc8\xb1\xd2\xb0\xca\xc0\xcb\xacd\xa1A\xafS\xbcx\xad\xc8\xc0\xcb\xacd\xa7\xb9\xb2\xa6\xabh\xc4~\xc4\xf2\xa4U\xa4@\xad\xd3\xafS\xa9\xba\xad\xc8\xa1A\xa7_\xabh\xaa\xf0\xa6^True\xb5\xa5\xab\xdd\xa4U\xa4@\xa6\xb8\xc0\xcb\xacd\xa1F\xa9\xd2\xa6\xb3\xafS\xbcx\xad\xc8\xc0\xcb\xacd\xa7\xb9\xb2\xa6\xabh\xaa\xf0\xa6^False\xaa\xed\xa5\xdc\xb5\xb2\xa7\xf4\xa5\xbb\xb3W\xabh
\t\t\xa8C\xad\xd3\xafS\xbcx\xad\xc8\xb3\xa3\xb2\xc5\xa6X\xa1A\xabh\xbb{\xa9w\xb2\xc5\xa6X\xa6\xb9\xb3W\xabh\xa1A\xb0O\xbf\xfd\xa4\xa7
\t\t'''
        while self.m_List:
            characteristic = self.m_List[-1]
            if characteristic.Run():
                return True
            
            desc = characteristic.GetResult()
            if desc:
                self.m_DescList.append(desc)
            
            self.m_List.pop()
        if self.m_DescList:
            if self.m_Title == 'Mxsj':
                print '%s:' % self.m_Title + ';'.join(self.m_DescList)
                if ('Home\xc1\xe4\xab\xf6\xa4U' in self.m_DescList or 'F7\xad\xb8\xa6\xe6\xb4\xd1\xa1AF8\xaa\xec\xaf\xc5\xad\xb8\xa6\xe6\xb4\xd1' in self.m_DescList) and '\xa4\xc0\xbf\xeb\xb2v800X600' in self.m_DescList and '\xc3\xf6\xb3\xac\xb3\xf5\xb4\xba\xafS\xae\xc4' in self.m_DescList and '\xab\xcc\xbd\xaanpc\xa9P\xb3\xf2\xaa\xb1\xaea' in self.m_DescList:
                    self.Log('%s:' % self.m_Title + ';'.join(self.m_DescList))
                
            else:
                self.Log('%s:' % self.m_Title + ';'.join(self.m_DescList))
        else:
            print '%s \xc0\xcb\xacd\xa7\xb9\xb2\xa6' % self.m_Title
        return False

    
    def Log(self, msg):
        import blacklist
        blacklist.C2SResult(37, msg, True, tExtData = (37, msg))
        print msg



class CShortKeyFly(CCharacteristic):
    
    def Run(self):
        import shortcut
        iconInfoLst = []
        for scheme in range(shortcut.CShortcutMgr.s_MaxScheme[shortcut.SHORTCUT_HERO]):
            for pos in range(6, 8):
                dSchemeData = shortcut.CShortcutMgr.GetSchemeData(shortcut.SHORTCUT_HERO, scheme)
                if pos in dSchemeData:
                    iconInfoLst.append((dSchemeData[pos][1], pos))
                    continue
            
        
        import item
        import skillicondata
        count = 0
        for iconInfo in iconInfoLst:
            (iconID, pos) = iconInfo
            it = item.GetItemWithKeyID(iconID)
            if it:
                if pos == 6 and skillicondata.GetItemIconID(it.m_Shape) == 'war/shortkey/\xb7\xc9\xd0\xd0\xc6\xec.igs':
                    count += 1
                
                if pos == 7 and skillicondata.GetItemIconID(it.m_Shape) == 'war/shortkey/\xb3\xf5\xbc\xb6\xb7\xc9\xd0\xd0\xc6\xec.igs':
                    count += 1
                
            skillicondata.GetItemIconID(it.m_Shape) == 'war/shortkey/\xb3\xf5\xbc\xb6\xb7\xc9\xd0\xd0\xc6\xec.igs'
        
        if count >= 2:
            self.m_Result = 'F7\xad\xb8\xa6\xe6\xb4\xd1\xa1AF8\xaa\xec\xaf\xc5\xad\xb8\xa6\xe6\xb4\xd1'
        
        return False

    
    def GetResult(self):
        return getattr(self, 'm_Result', None)



class CResolution800X600(CCharacteristic):
    
    def Run(self):
        import ratio
        if ratio.WINDOW_WIDTH == 800 and ratio.WINDOW_HEIGHT == 600:
            self.m_Result = '\xa4\xc0\xbf\xeb\xb2v800X600'
        
        return False

    
    def GetResult(self):
        return getattr(self, 'm_Result', None)



class CSceneEffect(CCharacteristic):
    
    def Run(self):
        import mapani
        if not mapani.g_SceneEffect:
            self.m_Result = '\xc3\xf6\xb3\xac\xb3\xf5\xb4\xba\xafS\xae\xc4'
        
        return False

    
    def GetResult(self):
        return getattr(self, 'm_Result', None)



class CShilePlayerAroundNpc(CCharacteristic):
    
    def Run(self):
        
        try:
            import cfg
            value = int(cfg.GetData('mx.ini', 'Game', 'npcAroundShow'))
        except:
            value = 0

        if value:
            self.m_Result = '\xab\xcc\xbd\xaanpc\xa9P\xb3\xf2\xaa\xb1\xaea'
        
        return False

    
    def GetResult(self):
        return getattr(self, 'm_Result', None)



class CGameWndStyle(CCharacteristic):
    
    def Run(self):
        import interface
        if interface.STYLE == 1:
            self.m_Result = '\xad\xb7\xae\xe62'
        
        return False

    
    def GetResult(self):
        return getattr(self, 'm_Result', None)



class CChatWndStyle(CCharacteristic):
    
    def Run(self):
        import chatoutput
        if chatoutput.g_CurChatOutput and isinstance(chatoutput.g_CurChatOutput, chatoutput.CChatOutput):
            self.m_Result = '\xb2\xe1\xa4\xd1\xae\xd8\xa4\xba\xb8m'
        
        return False

    
    def GetResult(self):
        return getattr(self, 'm_Result', None)



class CCheckHomeKey(CCharacteristic):
    s_HomeKeyDown = False
    MAXCOUNT = 180
    s_CurCount = 0
    
    def Run(self):
        CCheckHomeKey.s_CurCount += 1
        import chatoutput
        if CCheckHomeKey.s_HomeKeyDown:
            self.m_Result = 'Home\xc1\xe4\xab\xf6\xa4U'
        elif CCheckHomeKey.s_CurCount < CCheckHomeKey.MAXCOUNT:
            return True
        
        return False

    
    def GetResult(self):
        return getattr(self, 'm_Result', None)

    
    def Clear(cls):
        CCheckHomeKey.s_CurCount = 0

    Clear = classmethod(Clear)


class CShuoshu(CCharacteristic):
    
    def Run(self):
        for pid, name in processlib.GetProcessDict().iteritems():
            if '\xbb\xa1\xae\xd1\xa6h\xb6}' in name:
                self.m_Result = name
                break
                continue
        
        return False

    
    def GetResult(self):
        return getattr(self, 'm_Result', None)



class CHideWizard(CCharacteristic):
    
    def Run(self):
        dct = processlib.GetProcessDict()
        wizard_name = None
        dll_count = 0
        dll_name = processlib.GetSelfName()
        for pid, name in dct.iteritems():
            if 'HideWizard' in name:
                wizard_name = name
            
            if dll_name in name:
                dll_count += 1
                continue
        
        if wizard_name:
            miss_count = dll_count
            for path in processlib.GetProcessPathList():
                if dll_name in path:
                    miss_count -= 1
                    continue
            
            self.m_Result = '%s %d %d' % (wizard_name, dll_count, miss_count)
        
        return False

    
    def GetResult(self):
        return getattr(self, 'm_Result', None)


g_RuleList = [
    ('Mxsj', CCheckHomeKey, CShortKeyFly, CResolution800X600, CSceneEffect, CShilePlayerAroundNpc, CGameWndStyle, CChatWndStyle),
    ('\xbb\xa1\xae\xd1\xa6h\xb6}', CShuoshu),
    ('\xb5L\xbc~\xc1\xf4\xc2\xc3', CHideWizard)]
