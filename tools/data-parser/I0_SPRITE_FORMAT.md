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

## Truecolor variants: T4 / T5 (2026-10-14, from real item.fls)

Four unnamed entries exported from the user's real `item.fls`
(idx 225/236/625/639) turned out to be a direct-color sibling of
the family above:

* Same 14-byte header, frame dir, `totalLines == sum(frameH)` and
  the same row token grammar — but **no palette at all**: wherever
  the indexed grammar carries a 1-byte palette index, T4/T5 carry a
  **3-byte RGB** pixel (RUN = cnt/alpha-byte/RGB, SINGLE = RGB with
  alpha in the token, LIT = cnt×RGB, REP = RGB).
* Line-length table is **u8 for T4, u16 for T5** (the I0 vs I1
  split, respectively). All four samples parse with
  `data_end == entry length` exactly, and rendering them produces
  clean item illustrations (weapons / wings / spellbook) — colors
  verified in RGB byte order.
* Implemented in both decoders: `resource_editor/core/codecs/sprite.py`
  (0.3.6) and `ui_editor/core/sprite.py` (`Sprite.direct`,
  `_decode_row_direct`). Encoder still only writes I0/T0/I1.

Also identified while classifying the same export batch (not
sprites, export raw as-is): `interface.fls` entries starting with
`0x1C` + a 27-char hash string are **Spine skeleton binaries**
(versions `3.4.02` / `3.6.52`, big-endian floats, `imagesPath`
`./images/`, root bone first; attachments named e.g. `tx_2_8_2_17`,
`Btxx_18_houtoufa`), and large `sound.fls` entries are RIFF WAV
(PCM / GSM610 tag 49 / IMA-ADPCM tag 17) plus tiny GBK text
redirect records like `1 weapon3\士兵攻击.wav`.

## I4: 16-bit direct colour (2026-10-20, from real interface.fls)

`interface.fls` 的 `.igs` 图里还有 `I4`：与 T4 同构，但**行内颜色是 2 字节
RGB565 小端**（不是 3 字节 RGB888），无调色板，行长表 **u8**。

* 判定（真包样本，729 个目录型基路径里 3 个族的九片/三片全是 I4）：
  按 2 字节解，`totalLines == sum(frameH)` 之后每行都正好铺满帧宽并收尾；
  按 3 字节解则行行越界。
* `combdialog\游戏知道\三宫\知道蓝分割线\left.igs`（50×2）解出
  `(0,149,230)` 纯蓝，与「蓝分割线」的命名相符——这也是判定 565 小端
  而非大端的旁证（大端会得到偏黄绿的颜色）。
* 4×4 的九片角块也是 I4（例如 `combdialog2\杂图\聊天气泡左\middle\middle.igs`，
  46 B，单行 `0x84 0xf2 0x4e 0x00` = REP×4 + RGB565 `0x4ef2`）。
* 已实现：`mx_common/sprite_format.py`（`MAGICS`/`DIRECT_MAGICS` 加入 `I4`，
  新增 `DIRECT_COLOR_BYTES = {I4: 2, T4: 3, T5: 3}`、`U16_LEN_MAGICS`），
  `ui_editor/core/sprite.py` 与 `resource_editor/core/codecs/sprite.py` 两个落点；
  在这批真样本上两边 RGBA 逐字节一致。编码器仍只写 I0/T0/I1。

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
