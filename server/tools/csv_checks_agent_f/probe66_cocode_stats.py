#!/usr/bin/env python3
"""Agent F probe 66 — code-only opcode counts for entry 244.

The shared probe structurally parses the root marshal code object and counts
Duoyi opcodes only in its derived co_code range. Raw decrypt and every
transpilation explicitly disable solve_py25_co_span; co_consts are outside the
counted range. See probe65_final.py for the separate strict DATA/constant audit.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import probe65_final  # noqa: E402


if __name__ == '__main__':
    probe65_final.print_code_statistics()
