# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\lib\simplejson.py
from __future__ import absolute_import
__version__ = '3.10.0'
__all__ = [
 'dump', 'dumps', 'load', 'loads', 
 'JSONDecoder', 'JSONDecodeError', 'JSONEncoder', 
 'OrderedDict', 
 'simple_first']
__author__ = 'Bob Ippolito <bob@redivi.com>'
from decimal import Decimal
from simplejson_scanner import JSONDecodeError
from simplejson_decoder import JSONDecoder
from simplejson_encoder import JSONEncoder

def _import_OrderedDict():
    import collections
    try:
        return collections.OrderedDict
    except AttributeError:
        import simplejson_ordered_dict
        return simplejson_ordered_dict.OrderedDict


OrderedDict = _import_OrderedDict()

def _import_c_make_encoder():
    try:
        from ._speedups import make_encoder
        return make_encoder
    except ImportError:
        return

    return


_default_encoder = JSONEncoder(skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, indent=None, separators=None, encoding='utf-8', default=None, use_decimal=True, namedtuple_as_object=True, tuple_as_array=True, iterable_as_array=False, bigint_as_string=False, item_sort_key=None, for_json=False, ignore_nan=False, int_as_string_bitcount=None)

def dump(obj, fp, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=None, encoding='utf-8', default=None, use_decimal=True, namedtuple_as_object=True, tuple_as_array=True, bigint_as_string=False, sort_keys=False, item_sort_key=None, for_json=False, ignore_nan=False, int_as_string_bitcount=None, iterable_as_array=False, **kw):
    global _default_encoder
    if not skipkeys and ensure_ascii and check_circular and allow_nan and cls is None and indent is None and separators is None and encoding == 'utf-8' and default is None and use_decimal and namedtuple_as_object and tuple_as_array and not iterable_as_array and not bigint_as_string and not sort_keys and not item_sort_key and not for_json and not ignore_nan and int_as_string_bitcount is None and not kw:
        iterable = _default_encoder.iterencode(obj)
    elif cls is None:
        cls = JSONEncoder
    iterable = cls(skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular, allow_nan=allow_nan, indent=indent, separators=separators, encoding=encoding, default=default, use_decimal=use_decimal, namedtuple_as_object=namedtuple_as_object, tuple_as_array=tuple_as_array, iterable_as_array=iterable_as_array, bigint_as_string=bigint_as_string, sort_keys=sort_keys, item_sort_key=item_sort_key, for_json=for_json, ignore_nan=ignore_nan, int_as_string_bitcount=int_as_string_bitcount, **kw).iterencode(obj)
    for chunk in iterable:
        fp.write(chunk)

    return


def dumps(obj, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=None, encoding='utf-8', default=None, use_decimal=True, namedtuple_as_object=True, tuple_as_array=True, bigint_as_string=False, sort_keys=False, item_sort_key=None, for_json=False, ignore_nan=False, int_as_string_bitcount=None, iterable_as_array=False, **kw):
    if not skipkeys and ensure_ascii and check_circular and allow_nan and cls is None and indent is None and separators is None and encoding == 'utf-8' and default is None and use_decimal and namedtuple_as_object and tuple_as_array and not iterable_as_array and not bigint_as_string and not sort_keys and not item_sort_key and not for_json and not ignore_nan and int_as_string_bitcount is None and not kw:
        return _default_encoder.encode(obj)
    else:
        if cls is None:
            cls = JSONEncoder
        return cls(skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular, allow_nan=allow_nan, indent=indent, separators=separators, encoding=encoding, default=default, use_decimal=use_decimal, namedtuple_as_object=namedtuple_as_object, tuple_as_array=tuple_as_array, iterable_as_array=iterable_as_array, bigint_as_string=bigint_as_string, sort_keys=sort_keys, item_sort_key=item_sort_key, for_json=for_json, ignore_nan=ignore_nan, int_as_string_bitcount=int_as_string_bitcount, **kw).encode(obj)


_default_decoder = JSONDecoder(encoding=None, object_hook=None, object_pairs_hook=None)

def load(fp, encoding=None, cls=None, object_hook=None, parse_float=None, parse_int=None, parse_constant=None, object_pairs_hook=None, use_decimal=False, namedtuple_as_object=True, tuple_as_array=True, **kw):
    return loads(fp.read(), encoding=encoding, cls=cls, object_hook=object_hook, parse_float=parse_float, parse_int=parse_int, parse_constant=parse_constant, object_pairs_hook=object_pairs_hook, use_decimal=use_decimal, **kw)


def loads(s, encoding=None, cls=None, object_hook=None, parse_float=None, parse_int=None, parse_constant=None, object_pairs_hook=None, use_decimal=False, **kw):
    global _default_decoder
    if cls is None and encoding is None and object_hook is None and parse_int is None and parse_float is None and parse_constant is None and object_pairs_hook is None and not use_decimal and not kw:
        return _default_decoder.decode(s)
    else:
        if cls is None:
            cls = JSONDecoder
        if object_hook is not None:
            kw['object_hook'] = object_hook
        if object_pairs_hook is not None:
            kw['object_pairs_hook'] = object_pairs_hook
        if parse_float is not None:
            kw['parse_float'] = parse_float
        if parse_int is not None:
            kw['parse_int'] = parse_int
        if parse_constant is not None:
            kw['parse_constant'] = parse_constant
        if use_decimal:
            if parse_float is not None:
                raise TypeError('use_decimal=True implies parse_float=Decimal')
            kw['parse_float'] = Decimal
        return cls(encoding=encoding, **kw).decode(s)


def _toggle_speedups(enabled):
    global _default_decoder
    global _default_encoder
    import simplejson_decoder as dec, simplejson_encoder as enc, simplejson_scanner as scan
    c_make_encoder = _import_c_make_encoder()
    if enabled:
        dec.scanstring = dec.c_scanstring or dec.py_scanstring
        enc.c_make_encoder = c_make_encoder
        enc.encode_basestring_ascii = enc.c_encode_basestring_ascii or enc.py_encode_basestring_ascii
        scan.make_scanner = scan.c_make_scanner or scan.py_make_scanner
    else:
        dec.scanstring = dec.py_scanstring
        enc.c_make_encoder = None
        enc.encode_basestring_ascii = enc.py_encode_basestring_ascii
        scan.make_scanner = scan.py_make_scanner
    dec.make_scanner = scan.make_scanner
    _default_decoder = JSONDecoder(encoding=None, object_hook=None, object_pairs_hook=None)
    _default_encoder = JSONEncoder(skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, indent=None, separators=None, encoding='utf-8', default=None)
    return


def simple_first(kv):
    return (
     isinstance(kv[1], (list, dict, tuple)), kv[0])
