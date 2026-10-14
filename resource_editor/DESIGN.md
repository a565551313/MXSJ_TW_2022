# 资源编辑器设计方案（已确认，2026-10-13）

## 0.3.8 安全约定（取代下文历史原位覆盖流程）

保存必须输出新包，当前/历史基线与其他打开包均受保护（含硬/软链接）。
流式写入唯一临时文件 → 重解析/逐条校验 → 原子发布新包，失败不动旧输出。
导出执行源资源与目录边界检查；名称关联在保存后重建，导入路径按 entry_id
保留于会话。下文 `.bak`、同路径覆盖等内容仅记录旧版本设计。

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

## 0.2.0 实现增量（目录工作区与惰性加载）

* **目录式工作区**：以"设定目录"取代逐个选文件（QSettings 记住上次
  目录）。`gui/file_tree.py` 文件树只显示目录顶层 `.fls` 文件名，
  空目录可设定、可刷新；双击打开、单击选中；多包驻留切换不重读。
* **中间分页网格**：`gui/grid_panel.py` 以分页（25/50/100/200，
  默认 50）取代整表滚动，支持页码跳转与类型过滤；缩略图只生成
  当前页并 LRU 缓存。右侧改为"上预览（动画/文本/Hex 切换）+
  下检查器"，单击条目即在右侧小窗播放动画（用户定稿布局）。
* **惰性加载**：容器层新增 `readers.py`（os.pread 随机读）与
  `parse_index`（只读头+目录）。`PackDocument` 改为槽位+覆盖层：
  未改条目按需读取，`entry_kind` 只读 512B 头部嗅探分类；
  保存为流式写出（未改条目从源文件整段拷贝）+ 临时文件校验
  （`verify_saved`，消息上限 50 条）+ `.bak` + 原子替换。
  实测 1GB/22000 条合成包：打开 0.07s、嗅探全条 0.04~0.5s、
  内存 +14MB、改 1 条流式保存 1.5~2.7s。
* **一键启动**：根目录 `启动编辑器.bat` + `bootstrap.py`：
  自检 Python 版本与 PySide6/Pillow，缺失自动 pip 安装
  （官方→清华→阿里镜像），异常写 `启动日志.txt` 且窗口不闪退。
* 兼容：`build_bytes`/`verify_rebuilt` 等旧 API 保留（小包/测试），
  单元测试 17 个（新增惰性打开、bootstrap、目录工作区 GUI 冒烟）。

## 0.2.1 实现增量（Windows 兼容修复）

0.2.0 的惰性打开在真实 Windows 上首次实测即崩（用户实测目录
`D:\Lager\夢想世界\data`，49 个包）：`readers.py` 用了 POSIX
专属的 `os.pread`，Windows 的 `os` 模块没有这个函数。修复三处：

* **定位读可移植化**（`readers.py`）：模块级
  `_PREAD = getattr(os, "pread", None)`，有则用无状态 pread；
  无（Windows）则退化为「一把锁串行化 `lseek + read`」，锁只
  包住定位读本身，负载解码仍在锁外并行。打开文件统一带
  `O_BINARY`（POSIX 无此标志，用 `getattr` 兜底）——Windows
  文本模式会折叠 CRLF、把 0x1A 当 EOF，不带它二进制负载会被
  静默损坏，比报错更危险。
* **保存覆盖原文件**（`saver.py` + `document.py`）：Windows 上
  目标文件被文档的惰性读句柄占着时 `os.replace` 报
  PermissionError（POSIX 允许，故 Linux 测不出）。保存收尾改为：
  备份 → `doc.close()` 释放源句柄 → `os.replace`；替换失败时
  `doc.reopen_source()` 按原路径重开（槽位/撤销历史不动，编辑
  状态完整保留）再抛 `SaveError`；成功走原 `mark_saved` 重建基线。
* **版本号单点化**：`__init__.__version__` 更新为 0.2.1，
  GUI「关于」对话框改为读该常量（0.2.0 发布时两处曾不一致）。

回归测试（`tests/test_windows_compat.py`，新增 4 个）：`_PREAD`
置 None 强制回退路径下 read_at/copy_to/6 线程并发读逐字节校验
（样本含 0x1A 与 CRLF 字节）；「打开源文件 → 改一条 → 存回同一
路径」往返并校验 `.bak` 备份内容；mock `os.replace` 抛
PermissionError 后文档按原路径重开且 `is_modified` 保留。另以
删除 `os.pread` 的解释器把全套 21 个测试（含 GUI 离屏冒烟）
整场重跑，全绿——等于在 Linux 上整场模拟 Windows。

