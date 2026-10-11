# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\lib\json.py
import string, types

class _StringGenerator(object):

    def __init__(self, string):
        self.string = string
        self.index = -1

    def peek(self):
        i = self.index + 1
        if i < len(self.string):
            return self.string[i]
        else:
            return
            return

    def next(self):
        self.index += 1
        if self.index < len(self.string):
            return self.string[self.index]
        raise StopIteration

    def all(self):
        return self.string


class WriteException(Exception):
    pass


class ReadException(Exception):
    pass


class JsonReader(object):
    hex_digits = {'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15}
    escapes = {'t': '\t', 'n': '\n', 'f': '', 'r': '\r', 'b': ''}

    def read(self, s):
        self._generator = _StringGenerator(s)
        result = self._read()
        return result

    def _read(self):
        self._eatWhitespace()
        peek = self._peek()
        if peek is None:
            raise ReadException, "Nothing to read: '%s'" % self._generator.all()
        if peek == '{':
            return self._readObject()
        else:
            if peek == '[':
                return self._readArray()
            if peek == '"':
                return self._readString()
            if peek == '-' or peek.isdigit():
                return self._readNumber()
            if peek == 't':
                return self._readTrue()
            if peek == 'f':
                return self._readFalse()
            if peek == 'n':
                return self._readNull()
            if peek == '/':
                self._readComment()
                return self._read()
            raise ReadException, "Input is not valid JSON: '%s'" % self._generator.all()
            return

    def _readTrue(self):
        self._assertNext('t', 'true')
        self._assertNext('r', 'true')
        self._assertNext('u', 'true')
        self._assertNext('e', 'true')
        return True

    def _readFalse(self):
        self._assertNext('f', 'false')
        self._assertNext('a', 'false')
        self._assertNext('l', 'false')
        self._assertNext('s', 'false')
        self._assertNext('e', 'false')
        return False

    def _readNull(self):
        self._assertNext('n', 'null')
        self._assertNext('u', 'null')
        self._assertNext('l', 'null')
        self._assertNext('l', 'null')
        return

    def _assertNext(self, ch, target):
        if self._next() != ch:
            raise ReadException, "Trying to read %s: '%s'" % (target, self._generator.all())

    def _readNumber(self):
        isfloat = False
        result = self._next()
        peek = self._peek()
        while peek is not None and (peek.isdigit() or peek == '.'):
            isfloat = isfloat or peek == '.'
            result = result + self._next()
            peek = self._peek()

        try:
            if isfloat:
                return float(result)
            else:
                return int(result)

        except ValueError:
            raise ReadException, "Not a valid JSON number: '%s'" % result

        return

    def _readString(self):
        result = ''
        self._assertNext('"', '"')
        try:
            while self._peek() != '"':
                ch = self._next()
                if ch == '\\':
                    ch = self._next()
                    if ch in 'brnft':
                        ch = self.escapes[ch]
                    elif ch == 'u':
                        ch4096 = self._next()
                        ch256 = self._next()
                        ch16 = self._next()
                        ch1 = self._next()
                        n = 4096 * self._hexDigitToInt(ch4096)
                        n += 256 * self._hexDigitToInt(ch256)
                        n += 16 * self._hexDigitToInt(ch16)
                        n += self._hexDigitToInt(ch1)
                        ch = unichr(n)
                    elif ch not in '"/\\':
                        raise ReadException, "Not a valid escaped JSON character: '%s' in %s" % (ch, self._generator.all())
                result = result + ch

        except StopIteration:
            raise ReadException, "Not a valid JSON string: '%s'" % self._generator.all()

        self._assertNext('"', '"')
        return result

    def _hexDigitToInt(self, ch):
        try:
            result = self.hex_digits[ch.upper()]
        except KeyError:
            try:
                result = int(ch)
            except ValueError:
                raise ReadException, 'The character %s is not a hex digit.' % ch

        return result

    def _readComment(self):
        self._assertNext('/', '/')
        second = self._next()
        if second == '/':
            self._readDoubleSolidusComment()
        elif second == '*':
            self._readCStyleComment()
        else:
            raise ReadException, 'Not a valid JSON comment: %s' % self._generator.all()

    def _readCStyleComment(self):
        try:
            done = False
            while not done:
                ch = self._next()
                done = ch == '*' and self._peek() == '/'
                if not done and ch == '/' and self._peek() == '*':
                    raise ReadException, "Not a valid JSON comment: %s, '/*' cannot be embedded in the comment." % self._generator.all()

            self._next()
        except StopIteration:
            raise ReadException, 'Not a valid JSON comment: %s, expected */' % self._generator.all()

    def _readDoubleSolidusComment(self):
        try:
            ch = self._next()
            while ch != '\r' and ch != '\n':
                ch = self._next()

        except StopIteration:
            pass

    def _readArray(self):
        result = []
        self._assertNext('[', '[')
        done = self._peek() == ']'
        while not done:
            item = self._read()
            result.append(item)
            self._eatWhitespace()
            done = self._peek() == ']'
            if not done:
                ch = self._next()
                if ch != ',':
                    raise ReadException, "Not a valid JSON array: '%s' due to: '%s'" % (self._generator.all(), ch)

        self._assertNext(']', ']')
        return result

    def _readObject(self):
        result = {}
        self._assertNext('{', '{')
        done = self._peek() == '}'
        while not done:
            key = self._read()
            if isinstance(key, list):
                key = tuple(key)
            if not isinstance(key, (types.StringType, tuple, int, float, tuple)):
                raise ReadException, 'Not a valid JSON object key (should be a string, tuple, int, float, tuple): %s' % key
            self._eatWhitespace()
            ch = self._next()
            if ch != ':':
                raise ReadException, "Not a valid JSON object: '%s' due to: '%s'" % (self._generator.all(), ch)
            self._eatWhitespace()
            val = self._read()
            result[key] = val
            self._eatWhitespace()
            done = self._peek() == '}'
            if not done:
                ch = self._next()
                if ch != ',':
                    raise ReadException, "Not a valid JSON array: '%s' due to: '%s'" % (self._generator.all(), ch)

        self._assertNext('}', '}')
        return result

    def _eatWhitespace(self):
        p = self._peek()
        while p is not None and p in string.whitespace or p == '/':
            if p == '/':
                self._readComment()
            else:
                self._next()
            p = self._peek()

        return

    def _peek(self):
        return self._generator.peek()

    def _next(self):
        return self._generator.next()


class JsonWriter(object):

    def _append(self, s):
        self._results.append(s)

    def write(self, obj, escaped_forward_slash=False):
        self._escaped_forward_slash = escaped_forward_slash
        self._results = []
        self._write(obj)
        return ('').join(self._results)

    def _write(self, obj):
        ty = type(obj)
        if ty is types.DictType:
            n = len(obj)
            self._append('{')
            for k, v in obj.items():
                self._write(k)
                self._append(':')
                self._write(v)
                n = n - 1
                if n > 0:
                    self._append(',')

            self._append('}')
        elif ty is types.ListType or ty is types.TupleType:
            n = len(obj)
            self._append('[')
            for item in obj:
                self._write(item)
                n = n - 1
                if n > 0:
                    self._append(',')

            self._append(']')
        elif ty is types.StringType or ty is types.UnicodeType:
            self._append('"')
            obj = obj.replace('\\', '\\\\')
            if self._escaped_forward_slash:
                obj = obj.replace('/', '\\/')
            obj = obj.replace('"', '\\"')
            obj = obj.replace('', '\\b')
            obj = obj.replace('', '\\f')
            obj = obj.replace('\n', '\\n')
            obj = obj.replace('\r', '\\r')
            obj = obj.replace('\t', '\\t')
            self._append(obj)
            self._append('"')
        elif ty is types.IntType or ty is types.LongType:
            self._append(str(obj))
        elif ty is types.FloatType:
            self._append('%f' % obj)
        elif obj is True:
            self._append('true')
        elif obj is False:
            self._append('false')
        elif obj is None:
            self._append('null')
        else:
            raise WriteException, 'Cannot write in JSON: %s' % repr(obj)
        return


def write(obj, escaped_forward_slash=False):
    return JsonWriter().write(obj, escaped_forward_slash)


def read(s):
    return JsonReader().read(s)
