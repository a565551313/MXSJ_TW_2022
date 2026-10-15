# pycdc 交叉复核产物 · script.fls entry 1206
# co_filename(原始)='script/gamecode/gamepath.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1206.pyc (Python 2.5)

'''
\xc4\xa3\xbf\xe9\xd7\xf7\xd3\xc3\xa3\xba
1\xa1\xa2\xcd\xb3\xd2\xbbos\xa1\xa2os.path\xba\xcdshutil\xbd\xd3\xbf\xda\xb5\xc4\xb5\xf7\xd3\xc3
2\xa1\xa2cocos\xb6\xcb\xbb\xe1\xbc\xd3\xc8\xeb\xb1\xe0\xc2\xeb\xd7\xaa\xbb\xbb\xb4\xa6\xc0\xed

dy2d \xd7\xa8\xd3\xc3\xb5\xc4\xce\xb1\xb4\xfa\xc2\xeb\xa3\xac\xd6\xbb\xca\xc7\xd7\xf6\xbd\xd3\xbf\xda\xca\xca\xc5\xe4\xb7\xbd\xb1\xe3\xc0\xfb\xce\xaa
'''
import gamecode

def listdir(top):
    import os
    os.listdir(top)


def chdir(path):
    import os
    os.chdir(path)


def chmod(path, mode):
    import os
    os.chmod(path, mode)


def getcwd():
    import os
    return os.getcwd()


def getpid():
    import os
    return os.getpid()


def getenv(key, default = None):
    import os
    return os.environ.get(key, default)


def makedirs(name, mode = 511):
    import os
    return os.makedirs(name, mode)


def mkdir(path, mode = 511):
    import os
    return os.mkdir(path, mode)


def popen(command, mode = 'r', bufsize = None):
    import os
    continue
    bufsize is None
    return os.popen(command, mode)
    return os.popen(command, mode, bufsize)


def popen2(command, **kwargs):
    import os
    return os.popen2(command, **kwargs)


def remove(path):
    import os
    os.remove(path)


def removedirs(name):
    import os
    os.removedirs(name)


def rename(old, new):
    import os
    os.rename(old, new)


def rmdir(path):
    import os
    os.rmdir(path)


def spawnl(mode, file, *args):
    import os
    return os.spawnl(mode, file, *args)


def startfile(filepath, operation = None):
    import os
    if os.path.isdir(filepath):
        os.popen('start explorer %s' % filepath)
    else:
        os.popen('start %s' % filepath)


def stat(path):
    import os
    r = os.stat(path)
    return r


def system(command):
    import os
    return os.system(command)


def walk(top, topdown = True, onerror = None):
    import os
    return CGenerator(os.walk(top, topdown, onerror))


class CList(list):
    
    def pop(self, *args):
        ret = list.pop(self, *args)
        return gamecode.SysCodeToGameCode(ret)

    
    def __iter__(self):
        ret = list.__iter__(self)
        return CGenerator(ret)

    
    def __str__(self):
        ret = list.__str__(self)
        return gamecode.SysCodeToGameCode(ret)

    
    def __getitem__(self, *args):
        value = list.__getitem__(*args)
        return gamecode.SysCodeToGameCode(value)



class CGenerator(object):
    
    def __init__(self, generator):
        self.m_Gen = generator

    
    def __iter__(self):
        return self

    
    def next(self):
        return gamecode.SysCodeToGameCode(self.m_Gen.next())



def split(path):
    import os
    return os.path.split(path)


def dirname(path):
    import os
    return os.path.dirname(path)


def join(path, *paths):
    import os
    return os.path.join(path, *paths)


def normpath(path):
    import os
    return os.path.normpath(path)


def basename(path):
    import os
    return os.path.basename(path)


def splitext(path):
    import os
    return os.path.splitext(path)


def splitdrive(path):
    import os
    return os.path.splitdrive(path)


def exists(path):
    import os
    r = os.path.exists(gamecode.GameCodeToSysCode(path))
    return r

lexists = exists

def expanduser(path):
    import os
    path = gamecode.GameCodeToSysCode(path)
    return os.path.expanduser(path)


def expandvars(path):
    import os
    return os.path.expandvars(path)


def getatime(filename):
    import os
    return os.path.getatime(filename)


def getctime(filename):
    import os
    return os.path.getctime(filename)


def getmtime(filename):
    import os
    return os.path.getmtime(filename)


def getsize(filename):
    import os
    return os.path.getsize(filename)


def isabs(path):
    import os
    return os.path.isabs(path)


def isdir(path):
    import os
    return os.path.isdir(path)


def isfile(path):
    import os
    return os.path.isfile(path)


def copyfile(src, dst):
    import shutil
    return shutil.copyfile(src, dst)


def copy(src, dst):
    import shutil
    return shutil.copy(src, dst)


def rmtree(path, ignore_errors = False, onerror = None):
    import shutil
    return shutil.rmtree(path, ignore_errors, onerror)


def ExistInPackage(filename, pkgname):
    import C_sys
    return C_sys.Exist(filename, pkgname)


def ExistInFileSystem(filename, pkgname):
    return exists('%s/%s' % (pkgname, filename))


def Exist(filename, pkgname):
    if not ExistInPackage(filename, pkgname):
        pass
    return ExistInFileSystem(filename, pkgname)


def SafeRemove(path):
    
    try:
        remove(path)
        return True
    except:
        return False
