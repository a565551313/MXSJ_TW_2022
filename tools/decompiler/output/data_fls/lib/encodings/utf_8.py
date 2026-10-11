# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\lib\encodings\utf_8.py
import codecs
encode = codecs.utf_8_encode

def decode(input, errors='strict'):
    return codecs.utf_8_decode(input, errors, True)


class IncrementalEncoder(codecs.IncrementalEncoder):

    def encode(self, input, final=False):
        return codecs.utf_8_encode(input, self.errors)[0]


class IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    _buffer_decode = codecs.utf_8_decode


class StreamWriter(codecs.StreamWriter):
    encode = codecs.utf_8_encode


class StreamReader(codecs.StreamReader):
    decode = codecs.utf_8_decode


def getregentry():
    return codecs.CodecInfo(name='utf-8', encode=encode, decode=decode, incrementalencoder=IncrementalEncoder, incrementaldecoder=IncrementalDecoder, streamreader=StreamReader, streamwriter=StreamWriter)
