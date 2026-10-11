# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\lib\simplejson_encoder.py
from __future__ import absolute_import
import re
from operator import itemgetter
import decimal
from simplejson_compat import u, unichr, binary_type, text_type, string_types, integer_types, PY3

def _import_speedups():
    return (None, None)


c_encode_basestring_ascii, c_make_encoder = _import_speedups()
from simplejson_decoder import PosInf
ESCAPE = re.compile(u'\ux00-\x1f\\"\b\f\n\r\t0x20280x2029]')
ESCAPE_ASCII = re.compile('([\\\\"]|[^\\ -~])')
HAS_UTF8 = re.compile('[\\x80-\\xff]')
ESCAPE_DCT = {'\\': '\\\\', 
   '"': '\\"', 
   '': '\\b', 
   '': '\\f', 
   '\n': '\\n', 
   '\r': '\\r', 
   '\t': '\\t'}
for i in range(32):
    ESCAPE_DCT.setdefault(chr(i), '\\u%04x' % (i,))

for i in [8232, 8233]:
    ESCAPE_DCT.setdefault(unichr(i), '\\u%04x' % (i,))

FLOAT_REPR = repr

class RawJSON(object):

    def __init__(self, encoded_json):
        self.encoded_json = encoded_json


def encode_basestring(s, _PY3=PY3, _q=u('"')):
    if _PY3:
        if isinstance(s, binary_type):
            s = s.decode('utf-8')
        if type(s) is not text_type:
            s = text_type(s)
    elif isinstance(s, str) and HAS_UTF8.search(s) is not None:
        s = s.decode('utf-8')
    if type(s) not in string_types:
        s = text_type(s)

    def replace(match):
        return ESCAPE_DCT[match.group(0)]

    return _q + ESCAPE.sub(replace, s) + _q


def py_encode_basestring_ascii(s, _PY3=PY3):
    if _PY3:
        if isinstance(s, binary_type):
            s = s.decode('utf-8')
        if type(s) is not text_type:
            s = text_type(s)
    elif isinstance(s, str) and HAS_UTF8.search(s) is not None:
        s = s.decode('utf-8')
    if type(s) not in string_types:
        s = text_type(s)

    def replace(match):
        s = match.group(0)
        try:
            return ESCAPE_DCT[s]
        except KeyError:
            n = ord(s)
            if n < 65536:
                return '\\u%04x' % (n,)
            n -= 65536
            s1 = 55296 | n >> 10 & 1023
            s2 = 56320 | n & 1023
            return '\\u%04x\\u%04x' % (s1, s2)

    return '"' + str(ESCAPE_ASCII.sub(replace, s)) + '"'


encode_basestring_ascii = c_encode_basestring_ascii or py_encode_basestring_ascii

class JSONEncoder(object):
    item_separator = ', '
    key_separator = ': '

    def __init__(self, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, sort_keys=False, indent=None, separators=None, encoding='utf-8', default=None, use_decimal=True, namedtuple_as_object=True, tuple_as_array=True, bigint_as_string=False, item_sort_key=None, for_json=False, ignore_nan=False, int_as_string_bitcount=None, iterable_as_array=False):
        self.skipkeys = skipkeys
        self.ensure_ascii = ensure_ascii
        self.check_circular = check_circular
        self.allow_nan = allow_nan
        self.sort_keys = sort_keys
        self.use_decimal = use_decimal
        self.namedtuple_as_object = namedtuple_as_object
        self.tuple_as_array = tuple_as_array
        self.iterable_as_array = iterable_as_array
        self.bigint_as_string = bigint_as_string
        self.item_sort_key = item_sort_key
        self.for_json = for_json
        self.ignore_nan = ignore_nan
        self.int_as_string_bitcount = int_as_string_bitcount
        if indent is not None and not isinstance(indent, string_types):
            indent = indent * ' '
        self.indent = indent
        if separators is not None:
            self.item_separator, self.key_separator = separators
        elif indent is not None:
            self.item_separator = ','
        if default is not None:
            self.default = default
        self.encoding = encoding
        return

    def default(self, o):
        raise TypeError(repr(o) + ' is not JSON serializable')

    def encode(self, o):
        if isinstance(o, binary_type):
            _encoding = self.encoding
            if _encoding is not None and not _encoding == 'utf-8':
                o = o.decode(_encoding)
        if isinstance(o, string_types):
            if self.ensure_ascii:
                return encode_basestring_ascii(o)
            else:
                return encode_basestring(o)

        chunks = self.iterencode(o, _one_shot=True)
        if not isinstance(chunks, (list, tuple)):
            chunks = list(chunks)
        if self.ensure_ascii:
            return ('').join(chunks)
        else:
            return (u'').join(chunks)
            return

    def iterencode(self, o, _one_shot=False):
        if self.check_circular:
            markers = {}
        else:
            markers = None
        if self.ensure_ascii:
            _encoder = encode_basestring_ascii
        else:
            _encoder = encode_basestring
        if self.encoding != 'utf-8':

            def _encoder(o, _orig_encoder=_encoder, _encoding=self.encoding):
                if isinstance(o, binary_type):
                    o = o.decode(_encoding)
                return _orig_encoder(o)

        def floatstr(o, allow_nan=self.allow_nan, ignore_nan=self.ignore_nan, _repr=FLOAT_REPR, _inf=PosInf, _neginf=-PosInf):
            if o != o:
                text = 'NaN'
            elif o == _inf:
                text = 'Infinity'
            elif o == _neginf:
                text = '-Infinity'
            elif type(o) != float:
                o = float(o)
            return _repr(o)
            if ignore_nan:
                text = 'null'
            elif not allow_nan:
                raise ValueError('Out of range float values are not JSON compliant: ' + repr(o))
            return text

        key_memo = {}
        int_as_string_bitcount = 53 if self.bigint_as_string else self.int_as_string_bitcount
        if _one_shot and c_make_encoder is not None and self.indent is None:
            _iterencode = c_make_encoder(markers, self.default, _encoder, self.indent, self.key_separator, self.item_separator, self.sort_keys, self.skipkeys, self.allow_nan, key_memo, self.use_decimal, self.namedtuple_as_object, self.tuple_as_array, int_as_string_bitcount, self.item_sort_key, self.encoding, self.for_json, self.ignore_nan, decimal.Decimal, self.iterable_as_array)
        else:
            _iterencode = _make_iterencode(markers, self.default, _encoder, self.indent, floatstr, self.key_separator, self.item_separator, self.sort_keys, self.skipkeys, _one_shot, self.use_decimal, self.namedtuple_as_object, self.tuple_as_array, int_as_string_bitcount, self.item_sort_key, self.encoding, self.for_json, self.iterable_as_array, Decimal=decimal.Decimal)
        try:
            return _iterencode(o, 0)
        finally:
            key_memo.clear()

        return


class JSONEncoderForHTML(JSONEncoder):

    def encode(self, o):
        chunks = self.iterencode(o, True)
        if self.ensure_ascii:
            return ('').join(chunks)
        else:
            return (u'').join(chunks)

    def iterencode(self, o, _one_shot=False):
        chunks = super(JSONEncoderForHTML, self).iterencode(o, _one_shot)
        for chunk in chunks:
            chunk = chunk.replace('&', '\\u0026')
            chunk = chunk.replace('<', '\\u003c')
            chunk = chunk.replace('>', '\\u003e')
            yield chunk


def _make_iterencode(markers, _default, _encoder, _indent, _floatstr, _key_separator, _item_separator, _sort_keys, _skipkeys, _one_shot, _use_decimal, _namedtuple_as_object, _tuple_as_array, _int_as_string_bitcount, _item_sort_key, _encoding, _for_json, _iterable_as_array, _PY3=PY3, ValueError=ValueError, string_types=string_types, Decimal=None, dict=dict, float=float, id=id, integer_types=integer_types, isinstance=isinstance, list=list, str=str, tuple=tuple, iter=iter):
    if _use_decimal and Decimal is None:
        Decimal = decimal.Decimal
    if _item_sort_key and not callable(_item_sort_key):
        raise TypeError('item_sort_key must be None or callable')
    elif _sort_keys and not _item_sort_key:
        _item_sort_key = itemgetter(0)
    if _int_as_string_bitcount is not None and (_int_as_string_bitcount <= 0 or not isinstance(_int_as_string_bitcount, integer_types)):
        raise TypeError('int_as_string_bitcount must be a positive integer')

    def _encode_int(value):
        skip_quoting = _int_as_string_bitcount is None or _int_as_string_bitcount < 1
        if type(value) not in integer_types:
            value = int(value)
        if skip_quoting or -1 << _int_as_string_bitcount < value < 1 << _int_as_string_bitcount:
            return str(value)
        else:
            return '"' + str(value) + '"'

    def _iterencode_list(lst, _current_indent_level):
        if not lst:
            yield '[]'
            return
        else:
            if markers is not None:
                markerid = id(lst)
                if markerid in markers:
                    raise ValueError('Circular reference detected')
                markers[markerid] = lst
            buf = '['
            if _indent is not None:
                _current_indent_level += 1
                newline_indent = '\n' + _indent * _current_indent_level
                separator = _item_separator + newline_indent
                buf += newline_indent
            else:
                newline_indent = None
                separator = _item_separator
            first = True
            for value in lst:
                if first:
                    first = False
                else:
                    buf = separator
                if isinstance(value, string_types) or _PY3 and isinstance(value, binary_type):
                    yield buf + _encoder(value)
                elif isinstance(value, RawJSON):
                    yield buf + value.encoded_json
                elif value is None:
                    yield buf + 'null'
                elif value is True:
                    yield buf + 'true'
                elif value is False:
                    yield buf + 'false'
                elif isinstance(value, integer_types):
                    yield buf + _encode_int(value)
                elif isinstance(value, float):
                    yield buf + _floatstr(value)
                elif _use_decimal and isinstance(value, Decimal):
                    yield buf + str(value)
                else:
                    yield buf
                    for_json = _for_json and getattr(value, 'for_json', None)
                    if for_json and callable(for_json):
                        chunks = _iterencode(for_json(), _current_indent_level)
                    elif isinstance(value, list):
                        chunks = _iterencode_list(value, _current_indent_level)
                    else:
                        _asdict = _namedtuple_as_object and getattr(value, '_asdict', None)
                        if _asdict and callable(_asdict):
                            chunks = _iterencode_dict(_asdict(), _current_indent_level)
                        elif _tuple_as_array and isinstance(value, tuple):
                            chunks = _iterencode_list(value, _current_indent_level)
                        elif isinstance(value, dict):
                            chunks = _iterencode_dict(value, _current_indent_level)
                        else:
                            chunks = _iterencode(value, _current_indent_level)
                    for chunk in chunks:
                        yield chunk

            if first:
                yield '[]'
            elif newline_indent is not None:
                _current_indent_level -= 1
                yield '\n' + _indent * _current_indent_level
            yield ']'
            if markers is not None:
                del markers[markerid]
            return

    def _stringify_key(key):
        if isinstance(key, string_types):
            pass
        elif isinstance(key, binary_type):
            key = key.decode(_encoding)
        elif isinstance(key, float):
            key = _floatstr(key)
        elif key is True:
            key = 'true'
        elif key is False:
            key = 'false'
        elif key is None:
            key = 'null'
        elif isinstance(key, integer_types):
            if type(key) not in integer_types:
                key = int(key)
            key = str(key)
        elif _use_decimal and isinstance(key, Decimal):
            key = str(key)
        elif _skipkeys:
            key = None
        else:
            raise TypeError('key ' + repr(key) + ' is not a string')
        return key

    def _iterencode_dict(dct, _current_indent_level):
        if not dct:
            yield '{}'
            return
        else:
            if markers is not None:
                markerid = id(dct)
                if markerid in markers:
                    raise ValueError('Circular reference detected')
                markers[markerid] = dct
            yield '{'
            if _indent is not None:
                _current_indent_level += 1
                newline_indent = '\n' + _indent * _current_indent_level
                item_separator = _item_separator + newline_indent
                yield newline_indent
            else:
                newline_indent = None
                item_separator = _item_separator
            first = True
            if _PY3:
                iteritems = dct.items()
            else:
                iteritems = dct.iteritems()
            if _item_sort_key:
                items = []
                for k, v in dct.items():
                    if not isinstance(k, string_types):
                        k = _stringify_key(k)
                        if k is None:
                            continue
                    items.append((k, v))

                items.sort(key=_item_sort_key)
            else:
                items = iteritems
            for key, value in items:
                if not (_item_sort_key or isinstance(key, string_types)):
                    key = _stringify_key(key)
                    if key is None:
                        continue
                if first:
                    first = False
                else:
                    yield item_separator
                yield _encoder(key)
                yield _key_separator
                if isinstance(value, string_types) or _PY3 and isinstance(value, binary_type):
                    yield _encoder(value)
                elif isinstance(value, RawJSON):
                    yield value.encoded_json
                elif value is None:
                    yield 'null'
                elif value is True:
                    yield 'true'
                elif value is False:
                    yield 'false'
                elif isinstance(value, integer_types):
                    yield _encode_int(value)
                elif isinstance(value, float):
                    yield _floatstr(value)
                elif _use_decimal and isinstance(value, Decimal):
                    yield str(value)
                else:
                    for_json = _for_json and getattr(value, 'for_json', None)
                    if for_json and callable(for_json):
                        chunks = _iterencode(for_json(), _current_indent_level)
                    elif isinstance(value, list):
                        chunks = _iterencode_list(value, _current_indent_level)
                    else:
                        _asdict = _namedtuple_as_object and getattr(value, '_asdict', None)
                        if _asdict and callable(_asdict):
                            chunks = _iterencode_dict(_asdict(), _current_indent_level)
                        elif _tuple_as_array and isinstance(value, tuple):
                            chunks = _iterencode_list(value, _current_indent_level)
                        elif isinstance(value, dict):
                            chunks = _iterencode_dict(value, _current_indent_level)
                        else:
                            chunks = _iterencode(value, _current_indent_level)
                    for chunk in chunks:
                        yield chunk

            if newline_indent is not None:
                _current_indent_level -= 1
                yield '\n' + _indent * _current_indent_level
            yield '}'
            if markers is not None:
                del markers[markerid]
            return

    def _iterencode(o, _current_indent_level):
        if isinstance(o, string_types) or _PY3 and isinstance(o, binary_type):
            yield _encoder(o)
        elif isinstance(o, RawJSON):
            yield o.encoded_json
        elif o is None:
            yield 'null'
        elif o is True:
            yield 'true'
        elif o is False:
            yield 'false'
        elif isinstance(o, integer_types):
            yield _encode_int(o)
        elif isinstance(o, float):
            yield _floatstr(o)
        else:
            for_json = _for_json and getattr(o, 'for_json', None)
            if for_json and callable(for_json):
                for chunk in _iterencode(for_json(), _current_indent_level):
                    yield chunk

            elif isinstance(o, list):
                for chunk in _iterencode_list(o, _current_indent_level):
                    yield chunk

            else:
                _asdict = _namedtuple_as_object and getattr(o, '_asdict', None)
                if _asdict and callable(_asdict):
                    for chunk in _iterencode_dict(_asdict(), _current_indent_level):
                        yield chunk

                elif _tuple_as_array and isinstance(o, tuple):
                    for chunk in _iterencode_list(o, _current_indent_level):
                        yield chunk

                elif isinstance(o, dict):
                    for chunk in _iterencode_dict(o, _current_indent_level):
                        yield chunk

                elif _use_decimal and isinstance(o, Decimal):
                    yield str(o)
                else:
                    while _iterable_as_array:
                        try:
                            o = iter(o)
                        except TypeError:
                            break

                        for chunk in _iterencode_list(o, _current_indent_level):
                            yield chunk

                        return

                    if markers is not None:
                        markerid = id(o)
                        if markerid in markers:
                            raise ValueError('Circular reference detected')
                        markers[markerid] = o
                    o = _default(o)
                    for chunk in _iterencode(o, _current_indent_level):
                        yield chunk

                    if markers is not None:
                        del markers[markerid]
        return

    return _iterencode
