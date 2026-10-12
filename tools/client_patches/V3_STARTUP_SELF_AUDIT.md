# v3 黑屏：自查复现与 v3.1 候选修正

2026-10-12。用户要求先由助手自行检查，而非只等待用户日志。

## 结论与证据边界

**已从实际交付 v3 FLS 找到确定的启动阻断错误，并用独立 CPython 2.5.6 复现。**
不是泛泛猜测图片路径或要求用户再覆盖文件。该错误在图片加载之前即可发生。
这可以解释首页初始化失败链路，但没有本次原生运行日志，仍不能断言它是用户机器上的唯一问题。
修正只称 v3.1 候选，没有宣称 Windows 黑屏问题已实机验收。

实际检查的已交付 FLS SHA-256：
`b26af0973ac1fb28f0d2b482e2d24a710d682e4ff51b2ec1a586c219a75cc4a2`

## 硬错误：模块常量 0 不是 None

entry 4007 的模块级常量为：

```text
co_consts[0] == -1
co_consts[1] is None
co_consts[41] == 新界面代码对象
```

旧构建器在模块代码 488 处注入：

```text
LOAD_CONST 41
LOAD_CONST 0
LOAD_CONST 0
EXEC_STMT
```

所以不是注释中声称的 `(code, None, None)`，而是 `(code, -1, -1)`。
旧逻辑误把多个普通函数中“常量 0 是 None”的情况套到了模块代码。
`valid_code` 只校验索引范围和跳转，并不检查 EXEC 的命名空间实参类型，因此此前的离线检查没抓住。

独立 CPython 2.5.6 执行结果：

```text
TypeError: exec: arg 2 must be a dictionary or None
executed before fix: []
executed with None: ['overlay entered']
```

客户端 mxmain.dll 自身也包含相同的 `exec: arg 2 must be a dictionary or None` 错误字符串。
这不是“将源文件在 Python 3 中运行没问题”一类替代结论：本轮读取了交付物的实际入口指令/常量，
将新增代码的客户端 opcode 反映射为标准 opcode 后，在 Python 2.5 执行相应入口片段。

修正：按值和类型找到模块唯一的 None 常量，不再写死 0，甚至不固定成 1。
缺少或有歧义则构建失败。新增对最终归档实际 EXEC 操作数的回归检查。

## 一并发现并修正的失败处理

1. **首页模块导入没有异常隔离。**
   原 GetData 内的 try/except 不能捕获此前 import register 的失败。
   修正把 import 和 GetData 调用一起放进原首页 try 块的定宽区域，记录异常后走原返回，保留首页。
   日志前缀为 `login/mainpage.dlg`；没有无声吞错。这只能处理 Python 异常，不能恢复原生进程崩溃。
2. **切页先隐藏旧页，后创建目标。**
   首页入口改为先 register.Show(True)，成功后才 mainpage.Show(False)。
   协议页拒绝也改成先创建首页，成功后再关闭协议页。目标构造失败时不主动销毁旧页。
3. **清除按钮文字早于图片加载。**
   新图片先加载、检查非零尺寸，再清除旧字并挂载新标题。
   图片加载抛错或为空时保留原文字，输出 NOT installed；不会因为缺图先把按钮清空。

没有改 PNG 内容、正式登录/选区模块或增加网络/凭据保存行为。
当前构建器增加 `--allow-unverified-candidate` 显式开关；默认不产出未经原生验收的新包，防止误用为稳定版。
旧 v3 ZIP 没有覆盖、改写或重新上传，仍然应停用。

## 新增独立审计，而非只重复旧测试

`audit_visual_runtime.py` + `visual_runtime_harness.py2`：

- 对完整候选 marshal 用真正的 CPython 2.5 读取，仅解析，不执行完整游戏模块。
- 从已交付 v3 提取坏的入口操作数，确认在界面代码执行前抛 TypeError。
- 运行修正后的编译入口，确认新定义写入预期模块命名空间。
- 运行新编译的首页标题、协议和表单控制逻辑，使用假原生控件。
- 协议正文在转换后为 CP950 字节串，不仅仅是 Python 3 源码中的 Unicode。
- 重放正常导入、ImportError、标题函数错误，以及真实坏 EXEC 参数导致的导入失败，首页保护均返回并记录。
- 检查图片抛错/空图时文字保留；目标页构造抛错时当前页不被主动隐藏。

完整游戏模块、原生 DLL、真实 UI、联网接口均未执行；没有把该审计写成 Windows 游戏实测。
原始脚本未执行。只执行本轮自写界面代码和改变后的少量入口/调用片段，边界为假的 UI/模块对象。

## 执行结果

- 客户端补丁/界面回归：**79 项通过**（原 68 项 + 11 项新增）。
- 独立 CPython 2.5 执行审计：**14 项通过**，详见 `V3_1_RUNTIME_AUDIT.json`。
- 服务端架构回归：**161 项通过**。
- `git diff --check` 通过；原 FLS、密钥库未变。
- 候选仍只改变 337/4007；其他 5000 条目录记录/压缩载荷不变。

候选 FLS（仅在离线审计中生成，目前未新打包/上传）：

- SHA-256：`1a0283d0b031f33868e875984fffa91b2ce7eed66de823d94efc9d25f196654e`
- 大小：24,555,932 bytes。

## 复现

```bash
python3 -m unittest discover -s tools/client_patches -v
python3 tools/client_patches/audit_visual_runtime.py \
  --python25 /path/to/CPython-2.5.6/python \
  --shipped-zip /path/to/MXSJ_registration_preview_v3.zip \
  --report /path/to/runtime-results.json
```

省略 --shipped-zip 时使用相同的坏操作数回归样例；本次审计确实传入了原交付 ZIP。
审计要求 Python 2.5.6，并验证旧 v3 的 FLS 哈希；不下载或执行外部游戏脚本。
普通单元测试不要求 Python 2.5，独立审计必须明确另外运行，不能混为一项已自动完成的测试。

## 仍待确认

原生定制 VM 的加载/执行、FLS XOR 链路在真实客户端上的行为、模板控件类型、PNG 路径、层级遮挡、
真实输入/焦点/滚动、页面切换及其他分辨率仍需后续原生验收。
不要求用户为了本轮自查再试旧 v3，也不把剩余未验证范围包装成已解决。

## 本次独立复核补记

再次复核时，从 Git 中修正前的构建器和冻结产物重建旧 v3，而非重新下载云盘 ZIP。
重建 FLS 的 SHA-256 精确匹配已交付 v3：
`b26af0973ac1fb28f0d2b482e2d24a710d682e4ff51b2ec1a586c219a75cc4a2`。
临时审计 ZIP 仅包含此相同 FLS，不能声称其 ZIP 文件本身等同原交付 ZIP。

从官方 CPython v2.5.6 标签重新构建解释器，传入上述相同 FLS 重跑执行审计：14 项通过。
客户端补丁单元测试另行重跑：79 项通过。修正候选的 FLS 哈希仍为
`1a0283d0b031f33868e875984fffa91b2ce7eed66de823d94efc9d25f196654e`。
本次没有执行原生 Windows 游戏、没有执行完整恢复模块、没有重新打包或上传供用户安装的候选包。
