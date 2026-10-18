# script_link：布局 ⇄ 脚本联动索引生成器

> **状态：现役索引职责／旧解码生成链待评估**。本轮仅盘点，没有重建索引；优先读 [依赖清单](../DEPENDENCIES.md)。生成器仍 import batch_decompile，不因脚本编辑器 dev7 发布而自动换成新原生算法。UI 运行只读取随包产物。
> `--out` 默认指向受跟踪的 UI 索引并直接写入；试验应显式指定仓库外新路径，核查差异后再决定更新。下方失败数量和耗时是旧生成记录，不是本轮实测。

`build_script_index.py` 对 `data/script.fls` 全部 5,002 条做基线转译
（复用 `../decompiler/batch_decompile.py` 的 Py2.5 转译器，不跑反编译），
解析标准 Python 2.5 marshal 与字节码，静态挖脚本与布局的关联：

- 哪个模块的哪个类加载了哪个 `.dlg`；
- 脚本按名取了哪些控件（`GetObject('name')`），哪些是读位置的占位锚点；
- 代码现造按钮的皮肤/文字/消息号（`*Button*(self, 'skin.igs', ...)`），
  并配给同函数内最近的占位锚点。

产物 `ui_editor/src/ui_editor/data/script_index.json`（编辑器运行时加载，
见 `ui_editor/src/ui_editor/core/script_index.py`）。客户端脚本或密钥库
变化后须先固定输入并审查差异，再考虑重新生成；以下是历史维护命令，不要无参数覆盖当前产物：

```bash
python3 tools/script_link/build_script_index.py --workers 8
python3 -m unittest tools/script_link/test_build_script_index.py
```

静态边界：动态拼名、变量传参挖不到；15 条基线转译失败的条目不在索引内
（清单在 JSON 的 `stats.failed`）。生成用时约 10 秒。
