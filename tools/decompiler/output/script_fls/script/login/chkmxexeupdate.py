# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\chkmxexeupdate.py
import cfg, os
FORCETEST = 0
VBSNAME = 'makelnk.vbs'
GAME_NAME = '新夢想世界'
USE_CHK = False
OLD_LNK_NAME = '新夢想世界.lnk'
OLD_LNK_NAME_LIST = ['新夢想世界.lnk', 'mxmain.exe - 快捷方式.lnk', 'mx.exe - 快捷方式.lnk']
START_UP_FOLDER = '多益網絡'
LNK_NAME = '%s.lnk' % GAME_NAME
g_bChkLnkDel = False

def ModuleReset():
    return


def CheckFlag():
    if FORCETEST:
        return True
    flag = cfg.GetData('mx.ini', 'Game', 'chkmxupdate')
    if flag is None or flag != 'v1':
        cfg.SaveData('mx.ini', 'Game', 'chkmxupdate', 'v1')
        return True
    return False


def PropInit():
    global g_bChkLnkDel
    if not USE_CHK:
        return
    if g_bChkLnkDel:
        return
    g_bChkLnkDel = True
    if CheckFlag():
        ReplaceLnk()
        DeleteEXEFile()
    ChkLnkDel()
    return


def DeleteEXEFile():
    lDeleteFilePath = [
     'mxmain.exe', 'mx.exe']
    for sPath in lDeleteFilePath:
        if CGamePath.Exists(sPath):
            try:
                CGamePath.Remove(sPath)
            except:
                pass

    return


def GetDesktopDirList():
    import _winreg
    sUserDir = CGamePath.ExpandUser('~')
    lDesktopDir = ['%s/Desktop' % sUserDir, '%s/桌面' % sUserDir]
    try:
        key = _winreg.-penKey(_winreg.HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders')
        sDesktopDir = _winreg.QueryValueEx(key, 'Desktop')[0]
        lDesktopDir.append(sDesktopDir)
    except:
        pass

    lResult = []
    for sPath in lDesktopDir:
        sPath = sPath.replace('\\', '/')
        lResult.append(sPath)

    return lResult


def ReplaceLnk():
    workPath = CGamePath.GetCwd()
    cmdlist = [
     'Dim fso, oldLnkPath, oldLnkPath2, newLnkPath, oldLnkExists, oldLnkExists2, newLnkExists, bBuild',
     'Set WshShell=CreateObject("WScript.Shell")',
     'sPrograms=WshShell.SpecialFolders("Programs")',
     'Set fso=CreateObject("Scripting.FileSystemObject")',
     'oldLnkPath=sPrograms&"\\%s\\%s"' % (START_UP_FOLDER, OLD_LNK_NAME),
     'newLnkPath=sPrograms&"\\%s\\%s"' % (START_UP_FOLDER, LNK_NAME),
     'oldLnkExists=fso.FileExists(oldLnkPath)',
     'oldLnkExists2=fso.FileExists(oldLnkPath2)',
     'newLnkExists=fso.FileExists(newLnkPath)',
     'bBuild=false',
     'If newLnkExists=false Then',
     'If oldLnkExists=true Then',
     'fso.DeleteFile(oldLnkPath)',
     'bBuild=true',
     'End If',
     'If oldLnkExists2=true Then',
     'fso.DeleteFile(oldLnkPath2)',
     'bBuild=true',
     'End If',
     'If bBuild=true Then',
     'Set oShellLink=WshShell.CreateShortcut(sPrograms&"\\%s\\%s")' % (START_UP_FOLDER, LNK_NAME),
     'oShellLink.TargetPath="%s\\%s.exe"' % (workPath, 'mx3'),
     'oShellLink.WorkingDirectory="%s"' % workPath,
     'oShellLink.WindowStyle=1',
     'oShellLink.Description="多益網絡-%s"' % GAME_NAME,
     'oShellLink.Save',
     'End If',
     'End If']
    if ReplaceDesktopLnk():
        cmdlist.extend([
         'strDesKtop=WshShell.SpecialFolders("DesKtop")',
         'Set oShellDesktopLink=WshShell.CreateShortcut(strDesKtop&"\\%s")' % LNK_NAME,
         'oShellDesktopLink.TargetPath="%s\\%s.exe"' % (workPath, 'mx3'),
         'oShellDesktopLink.WorkingDirectory="%s"' % workPath,
         'oShellDesktopLink.WindowStyle=1',
         'oShellDesktopLink.Description="多益網絡-%s"' % GAME_NAME,
         'oShellDesktopLink.Save'])
    lVBSCode = ReplaceTaskbarLnk()
    if lVBSCode:
        cmdlist.extend(lVBSCode)
    sCode = ('\n').join(cmdlist)
    try:
        oFile = open(VBSNAME, 'w')
        oFile.write(sCode)
        oFile.close()
        os.popen2('cscript %s' % VBSNAME)
    except BaseException:
        LOG_EXC('makelnk.vbs 執行有誤')

    import timer
    timer.Timer(10, DeleteVbs)
    return


def DeleteVbs():
    if CGamePath.Exists(VBSNAME):
        CGamePath.Remove(VBSNAME)
    return


def ReplaceDesktopLnk():
    lDesktopDir = GetDesktopDirList()
    bHasOldLnk = False
    bHasNewLnk = False
    for sDesktop in lDesktopDir:
        if isinstance(sDesktop, unicode):
            sDesktop = sDesktop.encode('utf8')
        lnkPath = CGamePath.Join(sDesktop, LNK_NAME)
        if CGamePath.Exists(lnkPath):
            bHasNewLnk = True
        for sOldLnkName in OLD_LNK_NAME_LIST:
            lnkPath = CGamePath.Join(sDesktop, sOldLnkName)
            if CGamePath.Exists(lnkPath):
                bHasOldLnk = True
                CGamePath.Remove(lnkPath)

    return bHasOldLnk and not bHasNewLnk


def ReplaceTaskbarLnk():
    sUserPath = CGamePath.ExpandUser('~')
    sTaskbarPath = CGamePath.Join(sUserPath, '5ppData\\Roaming\\Microsoft\\Internet Explorer\\Quick Launch\\User Pinned\\TaskBar')
    workPath = CGamePath.GetCwd()
    lVBSCode = []
    sLnkPath = CGamePath.Join(sTaskbarPath, 'mxmain.lnk')
    if CGamePath.Exists(sLnkPath):
        sLnkPath2 = CGamePath.Join(sTaskbarPath, 'mx3main.lnk')
        try:
            os.rename(sLnkPath, sLnkPath2)
        except:
            pass
        else:
            lVBSCode.extend([
             'strTaskbar="%s\\%s"' % (sTaskbarPath, 'mx3main.lnk'),
             'Set oShellTaskbarLink=WshShell.CreateShortcut(strTaskbar)',
             'oShellTaskbarLink.TargetPath="%s\\mx3main.exe"' % workPath,
             'oShellTaskbarLink.WorkingDirectory="%s"' % workPath,
             'oShellTaskbarLink.WindowStyle=1',
             'oShellTaskbarLink.Description=""',
             'oShellTaskbarLink.Save'])
    sLnkPath = CGamePath.Join(sTaskbarPath, '新夢想世界啟動程序.lnk')
    if CGamePath.Exists(sLnkPath):
        CGamePath.Remove(sLnkPath)
        lVBSCode.extend([
         'strTaskbar2="%s\\%s"' % (sTaskbarPath, '新夢想世界啟動程序.lnk'),
         'Set oShellTaskbarLink2=WshShell.CreateShortcut(strTaskbar2)',
         'oShellTaskbarLink2.TargetPath="%s\\%s.exe"' % (workPath, 'mx3'),
         'oShellTaskbarLink2.WorkingDirectory="%s"' % workPath,
         'oShellTaskbarLink2.WindowStyle=1',
         'oShellTaskbarLink2.Description=""',
         'oShellTaskbarLink2.Save'])
    return lVBSCode


def ChkLnkDel():
    if cfg.GetData('mx.ini', 'Game', 'chkmxupdate_chkdel') == 'v1' and not FORCETEST:
        return

    def chkdel():
        bFinish = True
        lDesktopDir = GetDesktopDirList()
        for sDesktop in lDesktopDir:
            if isinstance(sDesktop, unicode):
                sDesktop = sDesktop.encode('utf8')
            for sOldLnkName in OLD_LNK_NAME_LIST:
                lnkPath = '%s/%s' % (sDesktop, sOldLnkName)
                if CGamePath.Exists(lnkPath):
                    if not CGamePath.Remove(lnkPath):
                        bFinish = False

        DeleteVbs()
        if bFinish:
            cfg.SaveData('mx.ini', 'Game', 'chkmxupdate_chkdel', 'v1')
        return

    import timer
    timer.Timer(10, chkdel)
    return


class CGamePath(object):

    @staticmethod
    def ExpandUser(sPath):
        try:
            return os.path.expanduser(sPath)
        except:
            return ''

        return

    @staticmethod
    def GetCwd():
        try:
            return os.getcwd()
        except:
            return ''

        return

    @staticmethod
    def Join(*args):
        return os.path.join(*args)

    @staticmethod
    def Exists(sPath):
        try:
            return os.path.exists(sPath)
        except:
            return False

        return

    @staticmethod
    def Remove(sPath):
        try:
            os.remove(sPath)
            return True
        except:
            LOG('刪除失敗', sPath)
            return False

        return


return
