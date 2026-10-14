#!/bin/sh
# Build a CPython 2.5.6 interpreter (needed to compile Py2.5 modules for
# script.fls). Verified 2026-10-14 in the sandbox (GCC 12, x86-64 Linux):
# the stock 2.5.6 sources build with -std=gnu89 and produce a working
# `python` binary that can py_compile our authored modules.
# Usage: sh build_python25.sh [target-dir]   (default /tmp/py25build)
set -e
DIR="${1:-/tmp/py25build}"
mkdir -p "$DIR"
cd "$DIR"
if [ ! -f py25.tgz ]; then
  curl -sL https://codeload.github.com/python/cpython/tar.gz/refs/tags/v2.5.6 -o py25.tgz
fi
if [ ! -d cpython-2.5.6 ]; then
  tar xzf py25.tgz
fi
cd cpython-2.5.6
if [ ! -f python ]; then
  CFLAGS="-O1 -std=gnu89 -fwrapv -w" ./configure --disable-shared --without-threads
  make -j4 python
fi
./python -V
echo "OK: $DIR/cpython-2.5.6/python"
