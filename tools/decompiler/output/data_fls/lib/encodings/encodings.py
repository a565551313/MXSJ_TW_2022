# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\lib\encodings\encodings.py
import codecs, types, aliases
_cache = {}
_unknown = '--unknown--'
_import_tail = ['*']
_norm_encoding_map = '                                              . 0123456789       ABCDEFGHIJKLMNOPQRSTUVWXYZ      abcdefghijklmnopqrstuvwxyz                                                                                                                                     '
_aliases = aliases.aliases

class CodecRegistryError(LookupError, SystemError):
    pass


def normalize_encoding(encoding):
    if type(encoding) is types.UnicodeType:
        encoding = encoding.encode('latin-1')
    return ('_').join(encoding.translate(_norm_encoding_map).split())


def search_function(encoding):
    entry = _cache.get(encoding, _unknown)
    if entry is not _unknown:
        return entry
    else:
        norm_encoding = normalize_encoding(encoding)
        aliased_encoding = _aliases.get(norm_encoding) or _aliases.get(norm_encoding.replace('.', '_'))
        if aliased_encoding is not None:
            modnames = [
             aliased_encoding,
             norm_encoding]
        else:
            modnames = [
             norm_encoding]
        for modname in modnames:
            if not modname:
                continue
            try:
                mod = __import__(modname, globals(), locals(), _import_tail)
            except ImportError:
                pass
            else:
                break

        else:
            mod = None

        try:
            getregentry = mod.getregentry
        except AttributeError:
            mod = None

        if mod is None:
            _cache[encoding] = None
            return
        entry = getregentry()
        if not isinstance(entry, codecs.CodecInfo):
            if not 4 <= len(entry) <= 7:
                raise CodecRegistryError, 'module "%s" (%s) failed to register' % (
                 mod.__name__, mod.__file__)
            if not callable(entry[0]) or not callable(entry[1]) or entry[2] is not None and not callable(entry[2]) or entry[3] is not None and not callable(entry[3]) or len(entry) > 4 and entry[4] is not None and not callable(entry[4]) or len(entry) > 5 and entry[5] is not None and not callable(entry[5]):
                raise CodecRegistryError, 'incompatible codecs in module "%s" (%s)' % (
                 mod.__name__, mod.__file__)
            if len(entry) < 7 or entry[6] is None:
                entry += (None, ) * (6 - len(entry)) + (mod.__name__.split('.', 1)[1],)
            entry = codecs.CodecInfo(*entry)
        _cache[encoding] = entry
        try:
            codecaliases = mod.getaliases()
        except AttributeError:
            pass

        for alias in codecaliases:
            if not _aliases.has_key(alias):
                _aliases[alias] = modname

        return entry


codecs.register(search_function)
