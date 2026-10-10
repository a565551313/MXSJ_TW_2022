# Entry 84 — PARKED (manual-solve notes, 2026-10-10)

Module: `script\data\newpresentdata.py` (new-present/gift-box data table, ~7KB).
Status: v4-fail, v7-fail. Partial manual recovery below; full decode BLOCKED.

## Recovered ground truth (certain)
- keys = `[0xeb, 0xdb, 0x85, 0x64, 0xf6]` (all five verified by structure)
  - keys[0]=0xeb (exact0, root 'c')
  - keys[1]=0xdb ([1453,1682) co_code-opaque; 0xdb beats 0x20 on scoreF)
  - keys[2]=0x85 (PROVEN: 's'+len8, ints 25881/25882-consecutive, 's'+len114 at [1687,1710))
  - keys[3]=0x64 (PROVEN: brute-256 argmax-prog = FULL-consume 7106)
  - keys[4]=0xf6 (PROVEN: struct-hunt: len-14 "All_Describle1" @6933 + len-29
    "script\data\newpresentdata.py" @6967; note game-dev typo "Describle")
- bounds[0] = 1453 (tight plateau, co-edge)
- bounds[1] ≈ 1657–1682 (co_code-opaque window; 1657/1682 both "work", neither verifies)
- bounds[2] ≈ 2960–3068 (string-content-opaque; s@2949-len-113 valid under 0x85)
- bounds[3] ≈ 3683 (unverified; prog-FULL plateaus at many b3 = overrun-class)

## The blocker
With all five keys locked, best prog = 3068–3075 (never ok). Token-walk shows a
VALID (int,str) pair chain (15 pairs, lens 70–291, printable contents) from 500
to s@2949 (len 113, ends 3067), then 'l'@3067 (needs keys[3]=0x64 ✓) with
n=[3068,3072) HUGE under EVERY key/alignment:
- ⊕0x64: n = 0x050561c9 (84M, overrun)
- ⊕0xf6: n = 0x9797f35b (neg-1.75B, overrun)
- mixed (b3 inside n): all huge
- patch-n (lo=1/2/4): prog advances to 3075/3077/3081 then fails at next token
- brute b1/b2/b3/keys[3] (marshal_try-ok as criterion): NO ok anywhere
Diagnosis: chain self-validates to 3067 (15 consecutive valid pairs ≈ impossible
as coincidence) ⇒ 'l'@3067 REAL ⇒ n-field [3068,3072] ARCHIVE-CORRUPT (4 bytes,
like entry-24's 1-byte 'G') OR a 6th micro-segment. Patch-n alone insufficient
(next tokens also fail ⇒ corruption wider than 4B, or drift).
s-contents look like binary item-blobs + text fragments ("700+7000", "G150",
"FD", "EFD") — data table, not logic.

## Value recovered anyway
- filename ✓, 15 (id, blob) pairs ✓ (parseable to 3067), tail strings ✓
- enough for CATALOG (P1-item-adjacent data file)

## Next (Phase-2, if needed)
- constrained solve: `--fix-keys eb,db,85,64,f6` (+ try keys[1]=20)
- hex-edit exp[3068,3072]+neighbors guided by long-VALUE guess (2934 for lo=1)
- accept partial (data table; logic scripts matter more)
