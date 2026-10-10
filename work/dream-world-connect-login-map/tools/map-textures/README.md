# 已恢复地图底图（GEPJ → PNG）

`2101.png`, `2111.png`, `2112.png`, `2122.png`, `2303.png` 是从对应根目录 `map/*.map` 原件**离线只读**恢复的 2000×1500 RGB 场景底图；无标注的前景/角色、NPC、碰撞信息。每个 GEPJ 含 JPEG 共享头和 12 段独立 80×80 扫描流（4×3 拼为 320×240），49 分块按 7×7 合并并裁切。重建时 ImageMagick 解码了 2940 块，没有警告。`2303-sector-24.gepj.bin` 为先前抽出的原样私有格式样本，非独立 PNG/JPEG。

## 复现（本地 ImageMagick `convert` + Python 标准库，不联网）

在仓库根目录执行：

```bash
for f in map/*.map; do
  n=${f#map/}; n=${n%.map}
  PYTHONDONTWRITEBYTECODE=1 python3 work/dream-world-connect-login-map/tools/gepj_decoder.py "$f" \
    --output "work/dream-world-connect-login-map/tools/map-textures/$n.png"
done
# 单个 320×240 分块也可：--sector 16 --output /path/to/preview.png
```

| 文件 | 本次环境生成的 SHA256 |
|---|---|
| 2101.png | `719e824d3d503c658e365dfc85395359fae8a7d9cc3d5bad46d7b0242f8e8c83` |
| 2111.png | `83fddd61283999866dc6f900293b90db83fb58aba38132c03a74db4e509e9783` |
| 2112.png | `cd35202d18dcb853697e1c3d11c59b25ffd34d81a156a6f301db86df2ec1caa3` |
| 2122.png | `bce9841a31559216265c8fdab137a2b9fbaaa6c24c547a08cb36237b86d615f6` |
| 2303.png | `7a2dd3a7e9e22cb44341593e0599144569de1e30a46fe558200ca3173728169d` |

不同 JPEG 解码器版本可能产生不同 PNG 像素/哈希，**对原始地图的 SHA256 和无解码警告**才是重建的核心校验。详细格式和失败尝试记录见 `../../notes/task-c-地图分析/map-format-analysis.md`。
