# mx_common —— 编辑器共享核心（唯一真源）

> **维护入口**：当前副本数量与检查结果以 [STATUS](../docs/STATUS.md) 为准。改真源后先分发，再测试受影响编辑器；精灵交叉测试需要 Pillow。共享副本一致只证明字节同步，不证明原生客户端兼容；具体格式仍需独立对照。

| 模块 | 内容 | 分发到 |
|---|---|---|
| `mxhash.py` | 路径哈希 `mx_hash()`（`mxmain.dll` VA `0x48EF80` 的指令级复刻）+ 严格的 `path_hash()` | ui_editor、resource_editor 的 `core/` |
| `native_layout.py` | `.dlg` 原生存储：`path_bytes()`、按键派生 XOR、字面量校验、旧密文读取兼容 | 同上 |
| `output_paths.py` | 输出路径保护 `guard_output()`（拒绝源别名 / 越界 / 符号链接） | 同上 |
| `sprite_format.py` | 精灵格式常量与 alpha 折算（I0/T0/I1/T4/T5 共用的那一层） | 同上 |

## 为什么是「复制」而不是「依赖」

编辑器要能在**只有 Python 和 PySide6** 的机器上双击运行（`bootstrap.py`
只装 `PySide6`/`Pillow`，不装本包，也不要求 `PYTHONPATH`）。把格式代码做成
一个被 import 的第三方包，会让交付链多一环——历史上这正是 `mxhash.py` /
`native_layout.py` 在两个编辑器里各存一份、`sprite.py` 各自演化成两种实现的
原因（见 `docs/analysis/ui_editor_analysis_20261016.md` P1-2）。

## 一致性的保障

```bash
python3 tools/devkit/vendor_core.py --check    # 0 报告 = 没有漂移
python3 tools/devkit/vendor_core.py --diff     # 看漂移在哪
python3 tools/devkit/vendor_core.py --write    # 按真源重写副本
python3 -m unittest discover -s tools/devkit/tests   # 含漂移测试
```

`--check` 比对的是**字节**：副本 = 生成横幅 + 真源全文。手改副本一定会被
`--check` 和测试抓住。

**只做「同源」还不够**：`sprite.py` / `sprite_encode.py` 与资源编辑器的
`core/codecs/sprite.py` 是同一格式的不同落点（一个输出 RGBA 字节喂 `QImage`、
一个输出 Pillow 图），不能强行合成一个模块；它们的**行为一致性**由
`tools/devkit/tests/test_sprite_parity.py` 交叉验证（真实精灵 + 合成图，
两边编解码互测），格式常量则来自本包 `sprite_format.py`。

## 改这里的注意事项

- 修改会让编辑器里运行的代码变化：改完必须跑对应编辑器的测试套件
  （`ui_editor`、`resource_editor`）与 `ruff`、`check_windows_compat.py`。
- `mxhash.py` / `native_layout.py` / `output_paths.py` 与仓库里其它实现
  （`tools/data-parser/mx_path_hash.py`、`resource_editor/core/containers/`）
  保持同源关系，动之前先看 `notes/fls_path_hash_and_dlg.md` 与
  `notes/native_dlg_path_cipher.md`。
