# pycdc 交叉复核产物 · script.fls entry 2662
# co_filename(原始)='script/rankmgr.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_2662.pyc (Python 2.5)

'''
\xd3\xc3\xd3\xda\xb9\xdc\xc0\xed\xc5\xc5\xd0\xd0\xb0\xf1
\xba\xf3\xd0\xf8\xcd\xc6\xbd\xf8\xba\xcf\xb2\xa2\xd2\xd4\xc7\xb0\xb5\xc4\xc5\xc5\xd0\xd0\xb0\xf1\xc4\xda\xc8\xdd
'''
import interface
import C_sys
import world
import misc
import dlgnewrank
import slot
g_RankMgr = None

def ModuleReset():
    global g_RankMgr
    g_RankMgr = None


def GetRankMgr():
    global g_RankMgr
    if not g_RankMgr:
        g_RankMgr = CRankMgr()
    
    return g_RankMgr


class CRankMgr(slot.ISignalSubject):
    s_Rank_INFO = 'RankInfoRefresh'
    s_Dir2Func = {
        1101: 'S2CCardRankInfo',
        1102: 'S2CCardRankInfo' }
    
    def __init__(self):
        slot.ISignalSubject.\x83\x83\xb9\x9e\x99t(self)
        self.ssCreate('RankMgrAdd')
        self.ssCreate('RankMgrDel')
        self.m_InfoDct = { }

    
    def S2COpenRankDlg(self, netobj):
        self.m_CurDlgType = 1001
        dlgnewrank.Open(1001)

    
    def S2CShowRankInfo(self, netobj):
        lst = self.GetLstData(1101, netobj)
        self.m_CurDir = 1101
        if not self.m_InfoDct.get(1001, None):
            self.m_InfoDct[1001] = { }
        
        self.m_InfoDct[1001][1101] = lst
        self.ssEmit(self.s_Rank_INFO)

    
    def S2CShowOldRankInfo(self, netobj):
        lst = self.GetLstData(1102, netobj)
        self.m_CurDir = 1102
        if not self.m_InfoDct.get(1001, None):
            self.m_InfoDct[1001] = { }
        
        self.m_InfoDct[1001][1102] = lst
        self.ssEmit(self.s_Rank_INFO)

    
    def GetLstData(self, idir, netobj):
        funcname = self.s_Dir2Func[idir]
        func = getattr(self, funcname)
        if callable(func):
            lst = func(netobj)
            return lst
        
        return []

    
    def S2CCardRankInfo(self, netobj):
        lst = []
        length = netobj.UnpackInt(1)
        for i in xrange(length):
            ranking = netobj.UnpackInt(1)
            ipoint = netobj.UnpackInt(4)
            winturn = netobj.UnpackInt(2)
            playerid = netobj.UnpackInt(4)
            serverlen = netobj.UnpackInt(1)
            servername = netobj.UnpackString(serverlen)
            namelen = netobj.UnpackInt(1)
            name = netobj.UnpackString(namelen)
            lst.append((ranking, winturn, playerid, name, ipoint, servername))
        
        return lst

    
    def C2SOpenOneRank(cls, idir):
        import nethuodong
        import nethdcardgame
        nethdcardgame.C2SOpenOneRank(idir)

    
    def GetCurDlgType(self):
        return self.m_CurDlgType

    
    def GetCurDir(self):
        return self.m_CurDir

    
    def GetCurInfo(self):
        data = self.m_InfoDct[self.m_CurDlgType]
        if not data:
            return None
        
        return data.get(self.m_CurDir, None)

    
    def GetCurTableInfo(self):
        import rankdlgdata
        return rankdlgdata.GetInfo(self.m_CurDlgType, self.m_CurDir)

    
    def SwitchShow(self, idir):
        if self.m_CurDir == idir:
            return None
        
        if self.m_InfoDct[self.m_CurDlgType].get(idir) != None:
            self.m_CurDir = idir
            self.ssEmit(self.s_Rank_INFO)
        else:
            self.C2SOpenOneRank({
                1101: 14,
                1102: 15 }[idir])
