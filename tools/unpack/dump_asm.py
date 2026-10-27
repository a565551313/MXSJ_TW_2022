# IDAPython script run via idat.exe batch mode.
# Usage (from IDA dir or with idat on PATH):
#   idat.exe -A -S"dump_asm.py" <input_pe>
# It reads ranges from D:/MXSJ_TW_2022/tools/unpack/asm_ranges.txt
# (one line per range: <start_hex> <end_hex> [label]) and writes
# D:/MXSJ_TW_2022/tools/unpack/asm_out.txt
import idc, ida_ua, idaapi, os

RANGES_FILE = r"D:/MXSJ_TW_2022/tools/unpack/asm_ranges.txt"
OUT_FILE    = r"D:/MXSJ_TW_2022/tools/unpack/asm_out.txt"

def disasm_range(start, end, label, out):
    out.append("")
    out.append("========== %s  [0x%X - 0x%X] ==========" % (label, start, end))
    ea = start
    while ea < end:
        insn = ida_ua.insn_t()
        ok = ida_ua.create_insn(ea, insn)
        if ok:
            line = idc.generate_disasm_line(ea, idc.GENDSM_FORCE_CODE)
            if line is None:
                line = ""
            out.append("0x%X  %s" % (ea, line))
            ea += insn.size
        else:
            b = idc.get_wide_byte(ea)
            out.append("0x%X  ??  %02X" % (ea, b))
            ea += 1

def main():
    try:
        with open(RANGES_FILE, "r") as f:
            lines = f.read().splitlines()
    except Exception as e:
        print("cannot read ranges:", e)
        return
    out = []
    for ln in lines:
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        parts = ln.split()
        if len(parts) < 2:
            continue
        start = int(parts[0], 16)
        end = int(parts[1], 16)
        label = parts[2] if len(parts) > 2 else ""
        disasm_range(start, end, label, out)
    with open(OUT_FILE, "w") as f:
        f.write("\n".join(out))
    print("wrote", OUT_FILE, "lines:", len(out))

main()
