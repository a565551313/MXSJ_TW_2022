# 资源编辑器设计方案（已确认，2026-10-13）

## 决策记录

| 议题 | 结论 |
|---|---|
| 功能深度 | **一步到位全编辑器**：浏览 + 动画预览 + PNG 替换回写 + 重打包（内部仍按容器→解码→编码顺序逐层实现、逐层测试） |
| 工程位置 | 仓库顶层 `resource_editor/`，与 `map_editor/` 平级，src 布局 + pyproject |
| 首要功能 | 精灵**动画预览播放**（逐帧 + 画布锚点合成）为一等公民 |
| 语言 | 中文 UI + 中文注释；代码遵循 PEP8（ruff/flake8，行宽 88） |

## 架构

```
src/resource_editor/
├── app.py / __main__.py        # 入口
├── core/                       # 零 Qt 依赖，可无头测试
│   ├── errors.py               # 统一异常
│   ├── containers/             # fls0slf.py（0SLF） / flsdata.py（data.fls）
│   ├── codecs/                 # detect.py 嗅探 / sprite.py I0T0I1 编解码
│   ├── model/document.py       # PackDocument：脏标记、撤销、增删条目
│   └── services/               # exporter.py / verifier.py / saver.py
└── gui/                        # PySide6，单向依赖 core
    ├── main_window.py / entry_panel.py / inspector.py
    ├── workers.py              # QThreadPool 后台任务
    └── preview/                # sprite_view / animation_bar / image/text/hex
```

## 关键约定

* **存储字节与内容视图分离**：文档保存每个条目的"存储字节"；data.fls 的内容视图是其 raw-deflate 解压结果。未改动条目在重打包时逐字节原样写入。
* **0SLF 重打包**：16B 头 + 条目按序拼接 + 目录重编码，保留每条目的 `(entry_id, r1)`。
* **data.fls 重打包**：保留原 64B 头与条目名/字段，重建本地头（签名 `0xA0975237`，CRC=解压内容 CRC32）与中央目录（签名 `0x87F2017C`，尾部 `0xA1985237`）。
* **保存流程**：构建新包字节 → verifier 全量重解析+精灵全解码校验 → 原文件备份 `.bak` → 临时文件原子替换。
* **精灵编码器**：PNG → 量化到原调色板（或新建 256 色）→ 31 级 alpha → 逐行 token（SKIP/SINGLE/RUN/LIT/REP/EOL）→ 帧 4B 对齐；I0/T0 行长超 255 时报错提示改 I1；保存前解码往返误差报告经用户确认。
* script.fls 条目（zlib+XOR 字节码）只浏览不解码；effect.fls 41 个未破译条目只提供 Hex 查看（见 `tools/data-parser/I0_SPRITE_FORMAT.md`）。

## 验收

* 7 个资源包全部可打开；807 个精灵预览/导出与 `i0_sprite.py` CLI 结果一致。
* 任一条目替换图片保存后：重开新包，未改条目逐字节一致，改动精灵可正常解码且往返误差在报告范围内。
* `python -m unittest discover` 全绿（真实包缺失时自动 skip）。

## 实现状态

0.1.0 已实现（`src/resource_editor/`）：core 四层（containers/codecs/
model/services）与 PySide6 GUI 全部落地——两类容器读写、I0/T0/I1
编解码（含 PNG 替换编码器与往返误差报告）、动画预览播放、批量导出、
保存校验+备份。测试 12 个：合成往返、真实包 807 精灵全量解码、
像素级编码往返、文档撤销/保存、离屏 GUI 冒烟，当前全绿；
ruff（PEP8，行宽 88）零警告。离屏冒烟截图验证过条目缩略图、
画布锚点十字、调色板网格与动画播放；沙箱缺系统 GL 库，正式运行
环境（Windows）不受影响。
