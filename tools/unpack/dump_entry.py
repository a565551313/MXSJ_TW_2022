# IDAPython: 把 chunk 映射到 VA 0x401000 并反汇编，写到 entry_asm.txt
import idc, ida_ua, ida_bytes, ida_segment

CHUNK = r"C:\chunk_entry.bin"
BASE  = 0x401000
OUT   = r"D:\MXSJ_TW_2022\tools\unpack\entry_asm.txt"

def main():
    data = open(CHUNK, "rb").read()
    n = len(data)
    ok = ida_segment.add_segm(0, BASE, BASE + n, ".entry", "CODE")
    ida_bytes.put_bytes(BASE, data)
    lines = []
    ea = BASE
    while ea < BASE + n:
        insn = ida_ua.insn_t()
        if ida_ua.create_insn(ea, insn):
            line = idc.generate_disasm_line(ea, idc.GENDSM_FORCE_CODE)
            lines.append("0x%X  %s" % (ea, line if line else ""))
            ea += insn.size
        else:
            lines.append("0x%X  ??  %02X" % (ea, idc.get_wide_byte(ea)))
            ea += 1
    with open(OUT, "w") as f:
        f.write("\n".join(lines))
    print("wrote", OUT, "lines:", len(lines), "segadd:", ok)

main()
