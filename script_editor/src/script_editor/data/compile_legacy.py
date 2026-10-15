"""Only compile/marshal authored source. Compatible with CPython 2.5 and 2.7."""

import imp
import marshal
import sys


def main():
    source_path, output_path, filename_path = sys.argv[1:]
    stream = open(source_path, "rb")
    try:
        source = stream.read()
    finally:
        stream.close()
    stream = open(filename_path, "rb")
    try:
        # CPython 2.5 compile() coerces Unicode filename through ASCII.
        # Preserve original filename bytes (or caller-supplied UTF-8), never
        # implicitly transcode using the system codepage.
        filename = stream.read()
    finally:
        stream.close()
    try:
        code = compile(source, filename, "exec")
    except SyntaxError:
        error = sys.exc_info()[1]
        message = "SYNTAX:%d:%d\n" % (error.lineno or 0, error.offset or 0)  # noqa: UP031 - Python 2.5 has no str.format/f-strings
        sys.stderr.write(message)
        return 2
    stream = open(output_path, "wb")
    try:
        stream.write(imp.get_magic() + "\x00\x00\x00\x00")
        marshal.dump(code, stream)
    finally:
        stream.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
