# pycdc 交叉复核产物 · script.fls entry 3009
# co_filename(原始)='script/taiwan/friend_fix.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3009.pyc (Python 2.5)


def CreatePages(self):
    import interface
    import style
    import dlgfriend
    self.m_Pages = []
    pagebtn = [
        ('combdialog/\xba\xc3\xd3\xd1\xc1\xc4\xcc\xec/\xb0\xb4\xc5\xa5/\xba\xc3\xd3\xd1\xd2\xb3\xc7\xa9.igs', '\xa6n\xa4\xcd\xa6C\xaa\xed'),
        ('combdialog/\xba\xc3\xd3\xd1\xc1\xc4\xcc\xec/\xb0\xb4\xc5\xa5/\xba\xc3\xd3\xd1\xd0\xe3\xd2\xb3\xc7\xa9/', '\xa6n\xa4\xcd\xb0\xca\xbaA'),
        ('combdialog/\xba\xc3\xd3\xd1\xc1\xc4\xcc\xec/\xb0\xb4\xc5\xa5/\xd7\xee\xbd\xfc\xd2\xb3\xc7\xa9.igs', '\xb3\xcc\xaa\xf1\xc1p\xc3\xb4'),
        ('combdialog/\xba\xc3\xd3\xd1\xc1\xc4\xcc\xec/\xb0\xb4\xc5\xa5/\xb8\xbd\xbd\xfc\xd2\xb3\xc7\xa9.igs', '\xa9P\xb3\xf2\xa6C\xaa\xed')]
    for filename, tips in enumerate(pagebtn):
        pageBtn = dlgfriend.j}@]ELk\]ton(self, style.GetPath(filename), tips, 0, 0, 20 + idx)
        pageBtn.SetZ(-2)
        if interface.IsNewStyle():
            pageBtn.Enlarge()
        
        self.m_Pages.append(pageBtn)
    
    (btnw, btnh) = self.m_Pages[0].GetSize()
    (x, y) = self.GetObject('loc_Tab').GetPos()
    for None in [
        2,
        0,
        3,
        1]:
        for idx in lSort:
            oTab = self.m_Pages[idx]
            oTab.SetPos((53 - btnw) / 2 + x, (29 - btnh) / 2 + y)
            x += 52
        
        return None


def Fix():
    import dlgfriend
    dlgfriend.CFriendDialog.CreatePages = CreatePages
