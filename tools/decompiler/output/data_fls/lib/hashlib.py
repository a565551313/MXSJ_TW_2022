# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\lib\hashlib.py
"""hashlib module - A common interface to many hash functions.

new(name, string='') - returns a new hash object implementing the
                       given hash function; initializing the hash
                       using the given string data.

Named constructor functions are also available, these are much faster
than using new():

md5(), sha1(), sha224(), sha256(), sha384(), and sha512()

More algorithms may be available on your platform but the above are
guaranteed to exist.

Choose your hash function wisely.  Some have known weaknesses.
sha384 and sha512 will be slow on 32 bit platforms.
"""

def __get_builtin_constructor(name):
    if name in ('SHA1', 'sha1'):
        import _sha
        return _sha.new
    if name in ('MD5', 'md5'):
        import _md5
        return _md5.new
    if name in ('SHA256', 'sha256', 'SHA224', 'sha224'):
        import _sha256
        bs = name[3:]
        if bs == '256':
            return _sha256.sha256
        if bs == '224':
            return _sha256.sha224
    elif name in ('SHA512', 'sha512', 'SHA384', 'sha384'):
        import _sha512
        bs = name[3:]
        if bs == '512':
            return _sha512.sha512
        if bs == '384':
            return _sha512.sha384
    raise ValueError, 'unsupported hash type'


def __py_new(name, string=''):
    return __get_builtin_constructor(name)(string)


def __hash_new(name, string=''):
    try:
        return _hashlib.new(name, string)
    except ValueError:
        return __get_builtin_constructor(name)(string)


try:
    import _hashlib
    new = __hash_new
    for opensslFuncName in filter((lambda n: n.startswith('openssl_')), dir(_hashlib)):
        funcName = opensslFuncName[len('openssl_'):]
        try:
            f = getattr(_hashlib, opensslFuncName)
            f()
            exec funcName + ' = f'
        except ValueError:
            try:
                exec funcName + ' = __get_builtin_constructor(funcName)'
            except ValueError:
                pass

    del f
    del opensslFuncName
    del funcName
except ImportError:
    new = __py_new
    md5 = __get_builtin_constructor('md5')
    sha1 = __get_builtin_constructor('sha1')
    sha224 = __get_builtin_constructor('sha224')
    sha256 = __get_builtin_constructor('sha256')
    sha384 = __get_builtin_constructor('sha384')
    sha512 = __get_builtin_constructor('sha512')
