# Run UNDER CPython 2.5.6 (built by build_python25.sh). Do not run with Py3.
# Compiles the authored register module with the original embedded filename
# so the produced marshal matches the stock module's identity.
import marshal
import sys

MAGIC = "\xb3\xf2\x0d\x0a"


def main():
    src_path, out_path = sys.argv[1], sys.argv[2]
    src = open(src_path, "rb").read()
    code = compile(src, "script\\login\\register.py", "exec")
    # header: magic + zero timestamp (obfuscator only checks the magic)
    data = MAGIC + "\x00\x00\x00\x00" + marshal.dumps(code)
    f = open(out_path, "wb")
    f.write(data)
    f.close()
    print("compiled %s -> %s (%d bytes)" % (src_path, out_path, len(data)))


main()
