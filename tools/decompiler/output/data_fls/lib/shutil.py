# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\lib\shutil.py
import os, sys, stat
from os.path import abspath
__all__ = [
 'copyfileobj', 'copyfile', 'copymode', 'copystat', 'copy', 'copy2', 
 'copytree', 
 'move', 'rmtree', 'Error']

class Error(EnvironmentError):
    pass


def copyfileobj(fsrc, fdst, length=16384):
    while 1:
        buf = fsrc.read(length)
        if not buf:
            break
        fdst.write(buf)


def _samefile(src, dst):
    if hasattr(os.path, 'samefile'):
        try:
            return os.path.samefile(src, dst)
        except OSError:
            return False

    return os.path.normcase(os.path.abspath(src)) == os.path.normcase(os.path.abspath(dst))


def copyfile(src, dst):
    if _samefile(src, dst):
        raise Error, '`%s` and `%s` are the same file' % (src, dst)
    fsrc = None
    fdst = None
    try:
        fsrc = open(src, 'rb')
        fdst = open(dst, 'wb')
        copyfileobj(fsrc, fdst)
    finally:
        if fdst:
            fdst.close()
        if fsrc:
            fsrc.close()

    return


def copymode(src, dst):
    if hasattr(os, 'chmod'):
        st = os.stat(src)
        mode = stat.S_IMODE(st.st_mode)
        os.chmod(dst, mode)


def copystat(src, dst):
    st = os.stat(src)
    mode = stat.S_IMODE(st.st_mode)
    if hasattr(os, 'utime'):
        os.utime(dst, (st.st_atime, st.st_mtime))
    if hasattr(os, 'chmod'):
        os.chmod(dst, mode)


def copy(src, dst):
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    copyfile(src, dst)
    copymode(src, dst)


def copy2(src, dst):
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    copyfile(src, dst)
    copystat(src, dst)


def copytree(src, dst, symlinks=False):
    names = os.listdir(src)
    os.makedirs(dst)
    errors = []
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks)
            else:
                copy2(srcname, dstname)
        except (IOError, os.error) as why:
            errors.append((srcname, dstname, str(why)))
        except Error as err:
            errors.extend(err.args[0])

    try:
        copystat(src, dst)
    except WindowsError:
        pass
    except OSError as why:
        errors.extend((src, dst, str(why)))

    if errors:
        raise Error, errors


def rmtree(path, ignore_errors=False, onerror=None):
    if ignore_errors:

        def onerror(*args):
            return

    elif onerror is None:

        def onerror(*args):
            raise

    names = []
    try:
        names = os.listdir(path)
    except os.error as err:
        onerror(os.listdir, path, sys.exc_info())

    for name in names:
        fullname = os.path.join(path, name)
        try:
            mode = os.lstat(fullname).st_mode
        except os.error:
            mode = 0

        if stat.S_ISDIR(mode):
            rmtree(fullname, ignore_errors, onerror)
        else:
            try:
                os.remove(fullname)
            except os.error as err:
                onerror(os.remove, fullname, sys.exc_info())

    try:
        os.rmdir(path)
    except os.error:
        onerror(os.rmdir, path, sys.exc_info())

    return


def move(src, dst):
    try:
        os.rename(src, dst)
    except OSError:
        if os.path.isdir(src):
            if destinsrc(src, dst):
                raise Error, "Cannot move a directory '%s' into itself '%s'." % (src, dst)
            copytree(src, dst, symlinks=True)
            rmtree(src)
        else:
            copy2(src, dst)
            os.unlink(src)


def destinsrc(src, dst):
    return abspath(dst).startswith(abspath(src))
