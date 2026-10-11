# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\lib\simplejson_decoder.py
from __future__ import absolute_import
import re, sys, struct
from simplejson_compat import b, u, text_type, binary_type, PY3, unichr
from simplejson_scanner import make_scanner, JSONDecodeError

def _import_c_scanstring():
    return


c_scanstring = _import_c_scanstring()
__all__ = [
 'JSONDecoder']
FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL

def _floatconstants():
    if sys.version_info < (2, 6):
        _BYTES = ('7FF80000000000007FF0000000000000').decode('hex')
        if sys.byteorder != 'big':
            _BYTES = _BYTES[:8][::-1] + _BYTES[8:][::-1]
        nan, inf = struct.unpack('dd', _BYTES)
    else:
        nan = float('nan')
        inf = float('inf')
    return (
     nan, inf, -inf)


NaN, PosInf, NegInf = _floatconstants()
_CONSTANTS = {'-Infinity': NegInf, 
   'Infinity': PosInf, 
   'NaN': NaN}
STRINGCHUNK = re.compile('(.*?)(["\\\\\\x00-\\x1f])', FLAGS)
BACKSLASH = {'"': (u('"')), 
   '\\': (u('\\u005c')), '/': (u('/')), 'b': (u('')), 
   'f': (u('')), 'n': (u('\n')), 'r': (u('\r')), 't': (u('\t'))}
DEFAULT_ENCODING = 'utf-8'

def py_scanstring(s, end, encoding=None, strict=True, _b=BACKSLASH, _m=STRINGCHUNK.match, _join=u('').join, _PY3=PY3, _maxunicode=sys.maxunicode):
    if encoding is None:
        encoding = DEFAULT_ENCODING
    chunks = []
    _append = chunks.append
    begin = end - 1
    while 1:
        chunk = _m(s, end)
        if chunk is None:
            raise JSONDecodeError('Unterminated string starting at', s, begin)
        end = chunk.end()
        content, terminator = chunk.groups()
        if content:
            if not _PY3 and not isinstance(content, text_type):
                content = text_type(content, encoding)
            _append(content)
        if terminator == '"':
            break
        elif terminator != '\\':
            if strict:
                msg = 'Invalid control character %r at'
                raise JSONDecodeError(msg, s, end)
            else:
                _append(terminator)
                continue
        try:
            esc = s[end]
        except IndexError:
            raise JSONDecodeError('Unterminated string starting at', s, begin)

        if esc != 'u':
            try:
                char = _b[esc]
            except KeyError:
                msg = 'Invalid \\X escape sequence %r'
                raise JSONDecodeError(msg, s, end)

            end += 1
        else:
            msg = 'Invalid \\uXXXX escape sequence'
            esc = s[end + 1:end + 5]
            escX = esc[1:2]
            if len(esc) != 4 or escX == 'x' or escX == 'X':
                raise JSONDecodeError(msg, s, end - 1)
            try:
                uni = int(esc, 16)
            except ValueError:
                raise JSONDecodeError(msg, s, end - 1)

            end += 5
            if _maxunicode > 65535 and uni & 64512 == 55296 and s[end:end + 2] == '\\u':
                esc2 = s[end + 2:end + 6]
                escX = esc2[1:2]
                if len(esc2) == 4 and not (escX == 'x' or escX == 'X'):
                    try:
                        uni2 = int(esc2, 16)
                    except ValueError:
                        raise JSONDecodeError(msg, s, end)

                    if uni2 & 64512 == 56320:
                        uni = 65536 + (uni - 55296 << 10 | uni2 - 56320)
                        end += 6
            char = unichr(uni)
        _append(char)

    return (
     _join(chunks), end)


scanstring = c_scanstring or py_scanstring
WHITESPACE = re.compile('[ \\t\\n\\r]*', FLAGS)
WHITESPACE_STR = ' \t\n\r'

def JSONObject(state, encoding, strict, scan_once, object_hook, object_pairs_hook, memo=None, _w=WHITESPACE.match, _ws=WHITESPACE_STR):
    s, end = state
    if memo is None:
        memo = {}
    memo_get = memo.setdefault
    pairs = []
    nextchar = s[end:end + 1]
    if nextchar != '"':
        if nextchar in _ws:
            end = _w(s, end).end()
            nextchar = s[end:end + 1]
        if nextchar == '}':
            if object_pairs_hook is not None:
                result = object_pairs_hook(pairs)
                return (
                 result, end + 1)
            pairs = {}
            if object_hook is not None:
                pairs = object_hook(pairs)
            return (pairs, end + 1)
        if nextchar != '"':
            raise JSONDecodeError('Expecting property name enclosed in double quotes', s, end)
    end += 1
    while True:
        key, end = scanstring(s, end, encoding, strict)
        key = memo_get(key, key)
        if s[end:end + 1] != ':':
            end = _w(s, end).end()
            if s[end:end + 1] != ':':
                raise JSONDecodeError("Expecting ':' delimiter", s, end)
        end += 1
        try:
            if s[end] in _ws:
                end += 1
                if s[end] in _ws:
                    end = _w(s, end + 1).end()
        except IndexError:
            pass

        value, end = scan_once(s, end)
        pairs.append((key, value))
        try:
            nextchar = s[end]
            if nextchar in _ws:
                end = _w(s, end + 1).end()
                nextchar = s[end]
        except IndexError:
            nextchar = ''

        end += 1
        if nextchar == '}':
            break
        elif nextchar != ',':
            raise JSONDecodeError("Expecting ',' delimiter or '}'", s, end - 1)
        try:
            nextchar = s[end]
            if nextchar in _ws:
                end += 1
                nextchar = s[end]
                if nextchar in _ws:
                    end = _w(s, end + 1).end()
                    nextchar = s[end]
        except IndexError:
            nextchar = ''

        end += 1
        if nextchar != '"':
            raise JSONDecodeError('Expecting property name enclosed in double quotes', s, end - 1)

    if object_pairs_hook is not None:
        result = object_pairs_hook(pairs)
        return (
         result, end)
    else:
        pairs = dict(pairs)
        if object_hook is not None:
            pairs = object_hook(pairs)
        return (
         pairs, end)


def JSONArray(state, scan_once, _w=WHITESPACE.match, _ws=WHITESPACE_STR):
    s, end = state
    values = []
    nextchar = s[end:end + 1]
    if nextchar in _ws:
        end = _w(s, end + 1).end()
        nextchar = s[end:end + 1]
    if nextchar == ']':
        return (values, end + 1)
    if nextchar == '':
        raise JSONDecodeError("Expecting value or ']'", s, end)
    _append = values.append
    while True:
        value, end = scan_once(s, end)
        _append(value)
        nextchar = s[end:end + 1]
        if nextchar in _ws:
            end = _w(s, end + 1).end()
            nextchar = s[end:end + 1]
        end += 1
        if nextchar == ']':
            break
        elif nextchar != ',':
            raise JSONDecodeError("Expecting ',' delimiter or ']'", s, end - 1)
        try:
            if s[end] in _ws:
                end += 1
                if s[end] in _ws:
                    end = _w(s, end + 1).end()
        except IndexError:
            pass

    return (values, end)


class JSONDecoder(object):

    def __init__(self, encoding=None, object_hook=None, parse_float=None, parse_int=None, parse_constant=None, strict=True, object_pairs_hook=None):
        if encoding is None:
            encoding = DEFAULT_ENCODING
        self.encoding = encoding
        self.object_hook = object_hook
        self.object_pairs_hook = object_pairs_hook
        self.parse_float = parse_float or float
        self.parse_int = parse_int or int
        self.parse_constant = parse_constant or _CONSTANTS.__getitem__
        self.strict = strict
        self.parse_object = JSONObject
        self.parse_array = JSONArray
        self.parse_string = scanstring
        self.memo = {}
        self.scan_once = make_scanner(self)
        return

    def decode(self, s, _w=WHITESPACE.match, _PY3=PY3):
        if _PY3 and isinstance(s, binary_type):
            s = s.decode(self.encoding)
        obj, end = self.raw_decode(s)
        end = _w(s, end).end()
        if end != len(s):
            raise JSONDecodeError('Extra data', s, end, len(s))
        return obj

    def raw_decode(self, s, idx=0, _w=WHITESPACE.match, _PY3=PY3):
        if idx < 0:
            raise JSONDecodeError('Expecting value', s, idx)
        if _PY3 and not isinstance(s, text_type):
            raise TypeError('Input string must be text, not bytes')
        if len(s) > idx:
            ord0 = ord(s[idx])
            if ord0 == 65279:
                idx += 1
            elif ord0 == 239 and s[idx:idx + 3] == '\ufeff':
                idx += 3
        return self.scan_once(s, idx=_w(s, idx).end())
