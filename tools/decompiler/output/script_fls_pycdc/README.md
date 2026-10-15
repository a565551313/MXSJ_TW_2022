# `script_fls_pycdc/` —— 第二引擎（pycdc）交叉复核产物

**是什么**：`data/script.fls` 里那些 *uncompyle6 只留下 52 字节失败占位、或根本没有产物* 的条目，
由第二个反编译引擎 pycdc 重新解出来的源码副本。2026-10-15 随「修 26 条 → 547 个占位换引擎复核」入库。

**不是什么**：不是可回放/可回编译的源码。用仓库自建的真 CPython 2.5.6 逐档 `compile()` 实测：
499 档里 **236 档原样可编译、263 档仍不合法**（pycdc 自身的错，例：解错缩进、把常量吐成非法表达式）。
所以**回编译管线（STATUS §5.2 ④）不要从这里取输入**；要回编的候选必须两个引擎都过 `compile()` 再挑。

## 生成方式

```sh
# 1) 建 pycdc（纯 C++，不需要 flex/bison；cmake 可用 pip 装）
/home/user/dec-venv/bin/pip install cmake
git clone -q --depth 1 https://github.com/zrax/pycdc
cmake -S pycdc -B pycdc/build && cmake --build pycdc/build -j4

# 2) 复核（只写语料下 pycdc/ 独立树，绝不覆盖 uncompyle6 产物；已存在一律跳过）
python3 tools/decompiler/crosscheck_pycdc.py --out <语料目录> \
    --accounting accounting.json --class failed --jobs 4 --timeout 25 \
    --write --keep-pyc <pyc目录> --ladder
```

工具不改 `batch_decompile.py` 一行（它的 SHA-256 被
`server/docs/csv_checks/agent_e_reproduction.json` 钉住），而是复用 `recover_entries.py`
的路径清洗与转译梯。细节见 `notes/opcode_mapping_and_decompilation.md` §4.5–§4.6。

## 三条使用约定

1. **只读与互证**：与 `../script_fls/` 下同路径文件对比可发现任一引擎的错解；每档头部有 entry 号与
   `co_filename` 原始值，可回查 `data/script.fls` 条目。
2. **文件名可能已清洗**：包内自报 `co_filename` 带 `\x00`/`?`/`*` 等非法字符时按分量替换成 `_`，
   深烂的收进 `script/mangled/`；原始值写在文件头与 `manifest.json` 里，不要按路径反推原文。
3. **`\xNN` 转义**：141 档含被转义的非 UTF-8 字节（pycdc 会原样吐 GBK 字节，直接把管道炸掉），
   这些位置**不可逐字节还原**，只做阅读参考；`manifest.json` 的 `escaped_bytes` 标了是哪档。

## `manifest.json`

`inputs` 记录三个锁定输入（归档、密钥库、`batch_decompile.py`）的 SHA-256；`engine.source_commit`
是 pycdc 的构建版本；`files[]` 逐档记 `entry` / `status` / `lines` / `escaped_bytes` /
`py25`（`raw` = 原样可编译、`top_return_only` = 剥掉模块顶层 `return` 后可编译、`no` = 都不行）
与 `uncompyle6`（该条目在 uncompyle6 侧的成色）。`residual_no_source` 指向两引擎加修复梯都拿不到的
61 条清单（随网盘包给出，不在仓库里复制）。
