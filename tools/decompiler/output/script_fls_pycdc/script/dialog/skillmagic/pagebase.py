# pycdc 交叉复核产物 · script.fls entry 961
# co_filename(原始)='script/dialog/skillmagic/pagebase.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_961.pyc (Python 2.5)

'''
================================================================================
\xd7\xf7\xd5\xdf: hfl
\xc3\xe8\xca\xf6: \xb7\xd6\xd2\xb3\xbb\xf9\xc0\xe0
\xd1\xf9\xc0\xfd:
\xd0\xc4\xb5\xc3:
================================================================================
'''
import misc
import combdialog

class CPageBase(combdialog.CCombSubWnd):
    S_UIPATH = ''
    
    def __init__(self, pSkillMagicDlg):
        self.m_wrSkillMagicDlg = misc.WeakRef(pSkillMagicDlg)
        if self.S_UIPATH:
            combdialog.CCombSubWnd.__init__(self, pSkillMagicDlg, self.S_UIPATH)
            self.SetZ(100)
            self.SetIgnoreEsc(True)

    
    def VGetCurSubPage(self):
        pass

    
    def GetSkillMagicDlg(self):
        return self.m_wrSkillMagicDlg()

    
    def IsVisible(self):
        bShow = self.GetShow()
        pSkillDlg = self.GetSkillMagicDlg()
        if not bShow or not pSkillDlg.GetShow():
            return False
        else:
            return True

    
    def getClassUIHeight(self, pClass, pParent, sUIName, nDefault):
        
        try:
            pObj = pClass(pParent)
            pObj = pObj.GetObject(sUIName)
            return pObj.GetSize()[1]
        except:
            return nDefault


    
    def VInit(self):
        '''\xaa\xec\xa9l\xa4\xc6
\t\t:return:
\t\t'''
        pass

    
    def VClose(self):
        '''\xc3\xf6\xb3\xac\xac\xc9\xad\xb1
\t\t:return:
\t\t'''
        pass

    
    def VOpenWithData(self, dData):
        '''
\t\t\xa8\xea\xb7s\xc5\xe3\xa5\xdc\xac\xc9\xad\xb1
\t\t:param dData:
\t\t:return:
\t\t'''
        pass

    
    def VClear(self):
        '''
\t\t\xb2M\xb2z
\t\t:return:
\t\t'''
        pass
