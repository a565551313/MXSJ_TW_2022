"""CPython2.5/2.7: complete marshal read of authored pyc, NEVER execute it."""

import marshal
import sys


def main():
    stream = open(sys.argv[1], "rb")
    try:
        stream.read(8)
        code = marshal.load(stream)
        if stream.read(1) or not isinstance(code, type(compile("", "<type>", "exec"))):
            return 2
    finally:
        stream.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
