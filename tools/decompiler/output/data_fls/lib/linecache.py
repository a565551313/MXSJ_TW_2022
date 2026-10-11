# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\lib\linecache.py
import sys, os
__all__ = [
 'getline', 'clearcache', 'checkcache']

def getline(filename, lineno, module_globals=None):
    lines = getlines(filename, module_globals)
    if 1 <= lineno <= len(lines):
        return lines[lineno - 1]
    else:
        return ''


cache = {}

def clearcache():
    global cache
    cache = {}


def getlines(filename, module_globals=None):
    if filename in cache:
        return cache[filename][2]
    else:
        return updatecache(filename, module_globals)


def checkcache(filename=None):
    if filename is None:
        filenames = cache.keys()
    elif filename in cache:
        filenames = [
         filename]
    else:
        return
    for filename in filenames:
        size, mtime, lines, fullname = cache[filename]
        if mtime is None:
            continue
        try:
            stat = os.stat(fullname)
        except os.error:
            del cache[filename]
            continue

        if size != stat.st_size or mtime != stat.st_mtime:
            del cache[filename]

    return


def updatecache(filename, module_globals=None):
    if filename in cache:
        del cache[filename]
    if not filename or filename[0] + filename[-1] == '<>':
        return []
    fullname = filename
    try:
        stat = os.stat(fullname)
    except os.error as msg:
        basename = os.path.split(filename)[1]
        if module_globals and '__loader__' in module_globals:
            name = module_globals.get('__name__')
            loader = module_globals['__loader__']
            get_source = getattr(loader, 'get_source', None)
            if name and get_source:
                if basename.startswith(name.split('.')[-1] + '.'):
                    try:
                        data = get_source(name)
                    except (ImportError, IOError):
                        pass
                    else:
                        if data is None:
                            return []
                        else:
                            cache[filename] = (len(data), None, [line + '\n' for line in data.splitlines()], fullname)
                            return cache[filename][2]

        for dirname in sys.path:
            try:
                fullname = os.path.join(dirname, basename)
            except (TypeError, AttributeError):
                pass
            else:
                try:
                    stat = os.stat(fullname)
                    break
                except os.error:
                    pass

        else:
            return []

    try:
        fp = open(fullname, 'rU')
        lines = fp.readlines()
        fp.close()
    except IOError as msg:
        return []

    size, mtime = stat.st_size, stat.st_mtime
    cache[filename] = (size, mtime, lines, fullname)
    return lines
