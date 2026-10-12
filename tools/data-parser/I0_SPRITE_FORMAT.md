# I0 / T0 / I1 sprite format — notes

Status: **fully decoded & verified** (2026-10-13). Decoder + CLI:
[`i0_sprite.py`](i0_sprite.py) (spec also in its module docstring).
Batch export used for verification: `/home/user/fls_sprite_exports/`
(807 sprites → 1143 PNGs).

## Verified layout

```
<2s magic, u16 ver=1, u16 frameCount, u16 canvasW, u16 canvasH,
 u16 centerX, u16 centerY>                                   14 bytes
frame dir   frameCount * <u16 keyX, u16 keyY, u16 frameW, u16 frameH>
u32 totalLines == sum(frameH)
line table  u8 per line (I0/T0) | u16 per line (I1)
palette     I0/I1: 512 B RGB565 LE | T0: 768 B RGB888   (after the table!)
pixel rows  RLE token stream per row; each frame padded to a 4-byte
            boundary (padding counted in the last row's length)
```

Row tokens: `0x00` EOL · `0x01–0x1F` RUN(cnt=low5, alpha byte, index byte) ·
`0x20–0x3F` SINGLE(alpha=low5, index byte) · `0x40–0x7F` LIT(cnt=low6) ·
`0x80–0xBF` REP(cnt=low6, one index) · `0xC0–0xFF` SKIP(cnt=low6).
Alpha: `level * 255 // 31`. Frame origin on canvas:
`(centerX − keyX, centerY − keyY)`.

Corpus check: all **807/807** sprite entries in skill/skill2/passive/effect
parse with `data_end == entry length` and no row overrun; rendered icons
and multi-frame effects match the in-game art.

## Non-sprite entries in the same packs

* **PNG**: 26 entries each in skill.fls / skill2.fls, 31 in magicres5.fls
  (stored raw, standard PNG signature).
* **Redirect records** (skill.fls idx 70, 109): 21-byte text payloads
  `IG\r\nskill\r\n1621.igs\r\n` / `…\1620.igs\r\n` — the slot delegates to
  the named `.igs` image (`CImagesObject` in the native engine). Those
  named resources are **not** present in any pack shipped in this repo.
* **magicres5.fls**: 121 JSON (effect-composition configs + TexturePacker
  atlas metadata) + 31 PNG — a newer, JSON-driven effect pipeline,
  unrelated to the I0 format.

## Unidentified: 41 small binaries in effect.fls

Entries idx 2,4,6,7,10,11,14,15,16,18,20,21,22,24–27,29,31,32,34–37,39,
41,42,45,46,48,49,52,53,55,57–59,61–64 (15–207 bytes each). They sit in
groups of 1–4 immediately after sprite entries, so they almost certainly
belong to the same effects (native `CEffectObject` in `mxmain.dll`; no
Python-side loader exists).

What is known:

* Strong **period-4 record structure** (byte-autocorrelation at shift 4
  ≈ 0.22 vs ≈ 0.005 elsewhere).
* After an **8-byte header** (per-file, no obvious fields), records behave
  like **float32 pairs stored with the two halves swapped**: with the
  quads of each 8-byte unit exchanged, many files become clean arithmetic
  float ramps (e.g. idx 25: −999.00482 − k/64, an 8-step sawtooth looped
  3×; idx 27: paired ramps stepping −1.0 per pair). AP-smoothness of the
  swapped-float reading averages 0.62 vs ~0.2 for other readings.
* Same-length "twin" files exist (idx 36/37: 79 B; idx 52/53: 59 B),
  suggesting per-layer parameter sets.

Ruled out: zlib/raw-deflate/bz2/lzma at offsets 0–8; single-byte XOR;
4- and 8-byte repeating XOR keys (incl. self-key from the header);
in-record byte permutations; float64 (with/without half-swap);
plain float32/int16 streams. The huge exponent bytes in some files
(idx 57, 62, 63) also resist a pure float reading, so the family may
mix record types or add a transform not yet found.

Next step, if ever needed: locate the `CEffectObject` resource parser
in `mxmain.dll` and read the record layout from the disassembly
(the string `CEffectObject的SetBlendMode参数设置有误` at file offset
0x2B9984 is a starting landmark).
