# 注册预览 v3.3：交付事实、安装/回退与原生验收清单

> 本文是 v3.3 候选的**事实表**（哈希、链接、坐标、参数、命令、清单），从原根目录 `AGENT_HANDOFF.md`（已归档至
> [`docs/archive/2026-10-12-AGENT_HANDOFF-registration-v3_3.md`](../../docs/archive/2026-10-12-AGENT_HANDOFF-registration-v3_3.md)）抽出。
> 修正原理与控件接口依据见 [REGISTRATION_CONTROL_FIX_V3_3.md](REGISTRATION_CONTROL_FIX_V3_3.md)；项目级状态见 [`docs/STATUS.md`](../../docs/STATUS.md)。
>
> **状态：v3.3 已构建、测试、上传；截至 2026-10-14 仍未收到用户 Windows 原生验收反馈。** 下文验收清单的“原生”列全部为待验证。

## 1. 交付物

| 项目 | 值 |
|---|---|
| 源码提交 | `2b913f5` |
| ZIP 文件名 | `MXSJ_registration_preview_v3.3_controls.zip` |
| ZIP 大小 / SHA-256 | 24,399,852 bytes / `717fed1f22c3e6c1c9ceeccca190078268ac0797a0823f6db06c053373a156aa` |
| FLS 大小 / SHA-256 | 24,556,254 bytes / `6ef84a13c23ca0abfaa7a9febf8ba49b4df569a9cf65286c4b1844f9df63cddb` |
| Drive 链接 | https://drive.google.com/file/d/11M9rwP36u0-KLP9WaO3YGjNRbGmvf4Rc/view?usp=drivesdk （ID `11M9rwP36u0-KLP9WaO3YGjNRbGmvf4Rc`） |
| ZIP 内容 | 14 个文件：FLS、8 张 PNG、安装 README、verification、OFFLINE_TESTS、V3_3_RUNTIME_AUDIT、控件修正文档。无字体、无完整客户端、无凭据 |

FLS 可由仓库确定性复建；重新打 ZIP 时 README/时间戳/压缩工具差异会改变 ZIP SHA，**不要因内部 FLS 相同就宣称 ZIP 逐字节相同**。

### 1.1 8 张图片（目录 `photo/registration_preview_v3/`，必须与 FLS 一起安装）

| 图片 | SHA-256 |
|---|---|
| agree.png | `7cd988537acbf32e075d152834dc24392684b0deff96950c63b952c2887481ca` |
| back.png | `267ee0140a7abb221511e61b74e36e95016485dc2cd1203e2822d0624180d2e7` |
| form_card.png | `6c3886e369dd1d466b17268d31c4afa17f8fad1a774bc19aca97aa201f13538a` |
| home_register.png | `9470531d39b28d373a38afdf770b1f602476cbaa84269d9df42a3f28a3513144` |
| info.png | `701d80aa66fc0958b3009db107f92d6a7458d3f53bb74ee15fa803e570d566bf` |
| register.png | `09d6b3bde72d996efd5e59961d389810cd0c0e53e82aed87ba5cc84f2c622782` |
| reject.png | `8e185fe89b049242ed1de4d93080171c0334a96afa9682a3899c2c689a5eee53` |
| terms_title.png | `6a4ee87c281421d4bb1a3c267dbc637b775904cb984ae2e5d874425c2d260192` |

四张按钮图在 v3.3 已改内容但**文件名与目录名未变**；权威清单以 `visual_assets/manifest.json` 与交付包 `verification.json` 为准。

### 1.2 历史版本（仅追溯，不要串错链接）

| 版本 | FLS SHA-256 | Drive | 状态 |
|---|---|---|---|
| 原包 | `8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72` | — | 锁定输入 |
| v2.1 | `ed40cbade80a42b6924b9a99edffefbaa4100dbf624ebd653a789d8b7283c0ba` | [链接](https://drive.google.com/file/d/1aos6ny8VWAw09vKL20lBW-7uhRSc6Qh3/view?usp=drivesdk) | 曾确认可用的恢复参考，旧外观 |
| v2.2 | `29d36efac4d1d941cec0f50a1b3956d24ba65f925b066756e9510362de1f0938` | [链接](https://drive.google.com/file/d/1Frqlr0sR_N0x793X1GLV9vckPNYJIrDQ/view?usp=drivesdk) | 历史本地校验预览 |
| v3 | `b26af0973ac1fb28f0d2b482e2d24a710d682e4ff51b2ec1a586c219a75cc4a2` | [链接](https://drive.google.com/file/d/1GoKdMuw9Tmrs_bF3B1eVRhQOjnM9JA33/view?usp=drivesdk) | **原生黑屏，停用**（ZIP 24,392,175 B，SHA `34a69e0a…`） |
| v3.1 | `1a0283d0b031f33868e875984fffa91b2ce7eed66de823d94efc9d25f196654e` | [链接](https://drive.google.com/file/d/1MVInZtJmx0k-Gml9y6IPTGvxTqQ6AHi6/view?usp=drivesdk) | 提前上传的未拆分候选，不推荐 |
| v3.2 | `51187b3806497cab206cf2581cbcd2dbb0fe8ec4be4928a9bad41aebf2e105f3` | [链接](https://drive.google.com/file/d/1P2zK9Dt-De3VQnK3JSSBEvTFsjJCodny/view?usp=drivesdk) | 用户截图确认新协议/表单可显示，但报告 5 类控件缺陷（ZIP 24,396,468 B，SHA `a8b674f3…`） |
| **v3.3** | `6ef84a13c23ca0abfaa7a9febf8ba49b4df569a9cf65286c4b1844f9df63cddb` | 见上表 | **当前唯一推荐候选，待原生验收** |

## 2. v3.3 改了什么（摘要）

v3.2 用户反馈的 5 项：协议页两个按钮无文字；表单左上角黑块；「注册账号」与旧「登录游戏」叠字；「上一步」仍是旧箭头；输入框无闪烁光标。

- **已独立复现的硬错误**：原档 entry 3854 中 `CClickBox.__init__(self, parent, w, h, color, alpha, msgid)`，旧代码把坐标当成 color/alpha 传入，控件停在 (0,0) 形成黑块；且旧测试替身声明了同样错误的签名，导致假通过。现改为 `CClickBox(panel, w, h, 0, 0, msgid)` + `SetPos` + `SetZ(2)`。
- 协议页与表单页旧按钮**整体隐藏并禁用**，新按钮统一 112×34 金色带字 PNG（背景与文字在同一张图内）。
- 显式层级：图片容器 Z=1、动作点击框 Z=2、输入框 Z=2、输入框内光标 `m_Line` Z=1、首页标题 Z=1。
- 光标：三字段显式 `linecolor=0x805B45`，沿用原生 `CEdit.Active/Flash/MsgTab`，**没有新建第二套闪烁计时器**。
- 保持不变：首页只在点击消息 2 时才 `import register`；目标页构造成功后才隐藏首页；v2.2 校验；原选区后条款/登录 entry 4806；原始 FLS 与 key DB。

## 3. 路由、坐标与校验规则

```text
首页 mainpage（entry 337）
  └─ 消息 2「注册账号」→ 点击时 import register → register.Show(True) → 成功后 mainpage.Show(False)
新协议 CRegPanel1（login/service.dlg）
  ├─ 消息 1「同意」→ Step(1) → CRegPanel2
  └─ 消息 2/3「拒绝/返回」→ mainpage.Show(True)，再 register.Show(False)
新表单 CRegPanel2（login_new/newlogin_800.dlg，只加载布局，不运行 CLoginIn）
  ├─ 消息 1「上一步」→ 回协议
  ├─ 消息 2「注册账号」→ 本地校验 → 离线提示，无真实提交
  └─ 消息 3「离线预览说明」→ 不读字段，直接「離線預覽，未送出。」
```

| 元素（800×600） | 位置 / 尺寸 |
|---|---|
| 协议标题图 | (280,83)，240×34；正文 `chatoutput.COutput`，字体 `FontLT14_3`，颜色 `COLOR_1`，行尾 `#r` |
| 表单卡片 | (200,138)，400×300 |
| 邮箱框 | (340,214)，226×22，最多 32 字符，初始 Active |
| 密码框 / 确认框 | (340,272) / (340,330)，226×22，最多 16，密码遮罩 |
| 说明入口 | (300,394)，200×28，透明点击框 |
| 上一步 / 注册账号 | (270,468) / (430,468)，112×34 |

校验：三字段必填；邮箱 trim 后 ≤32、基础 ASCII 正则 `(?i)^[\w.-]+@[a-z\d-]+(\.[a-z\d-]+)+$`；密码 6–16；两次一致。合法输入也只显示离线提示，不创建账号、不保存凭据、不模拟成功。测试只用假数据如 `preview@example.invalid` / `Preview123`。

## 4. FLS 封装参数（仅对 v3.3 有效）

- 容器 `0SLF`，12 字节头，5002 条 × 16 字节目录；解码链 目录 → zlib → 五段 XOR → marshal。客户端是**定制 Python 2.5**（`HAVE_ARGUMENT=0x5F`，标准 `EXEC_STMT=85` 对应原生 `0x21`），marshal 内 code string 起点为代码对象偏移 `+22`。
- 锁定输入：`data/script.fls` 24,454,082 B，SHA `8b6e9266…`；key DB `tools/decompiler/script_fls_keys.json`，SHA `43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb`。构建器拒绝其它基线。

| entry | 文件 | 解密后长度 | XOR keys | bounds | v3.3 尾常量填充 |
|---:|---|---:|---|---|---:|
| 337 | `script/login/mainpage.py` | 10,335 | 226 / 28 / 112 / 247 / 187 | 2163 / 4281 / 6390 / 8473 | 307 B |
| 4007 | `script/login/register.py` | 44,362 | 222 / 84 / 13 / 219 / 82 | 8966 / 17948 / 26868 / 35778 | 8191 B |

填充值改源码后以构建报告为准，不要硬写。相关原档条目：3854 `interface.py`（CClickBox/CButton/CEdit）、369 `mxui/imagewidget.py`（CImage 真正实现）、4537 `mxui/ui.py`（仅聚合导出）、1156 `mxui/textwidget.py`、579 `combdialog.py`、4806 `login/loginin.py`（不改）。原脚本索引 `server/docs/catalog/script_entries.jsonl`；**接口签名以原 code object 为准，不以不完整反编译文本为准。**

已记录副作用：首页原可选 `tg.id` 推广标识块被替换，不再显示。

## 5. 构建、测试、审计命令

```bash
# 仓库根目录；只需 Python 3.11+ 标准库
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/client_patches -v     # 90 项
PYTHONDONTWRITEBYTECODE=1 python3 tools/client_patches/build_visual_preview.py \
  --allow-unverified-candidate --output-dir ../mxsj-registration-next     # 仓库外新目录；不改源码时输出 FLS SHA 应为 6ef84a13…

# 改了 Python 2.5 片段（registration_visual_overlay.py / home_registration_entry.py）后重新冻结：
python3 tools/client_patches/prepare_visual_assets.py --code-only --python25 /path/to/cpython-2.5.6/python
# 改了绘图：在带 Pillow 的 Python 3 环境运行同一脚本（不带 --code-only），字体用仓库 Fonts/FZLanTingYuan-DB-GBK.ttf，不随包分发

# 独立执行审计（从实际构建的 FLS 提取片段，映射回标准 opcode 后在 CPython 2.5.6 执行；22 项）
PYTHONDONTWRITEBYTECODE=1 python3 tools/client_patches/audit_visual_runtime.py \
  --python25 /path/to/cpython-2.5.6/python --report ../registration-runtime-audit.json
```

CPython 2.5.6 仅用于离线编译/审计，从 `https://codeload.github.com/python/cpython/tar.gz/refs/tags/v2.5.6` 取源，`./configure --without-threads CFLAGS='-O2 -fcommon -fno-strict-aliasing' && make -j4 python`，不需要 `make install`。`--allow-unverified-candidate` 是刻意保留的提醒开关，不要移除。改源码不更新 manifest 会被构建器拒绝，这是预期保护。

## 6. Windows 安装、核对与回退

用户历史环境：`D:\Lager\夢想世界`，客户端 2.27.2，800×600。**只在完整客户端测试副本上操作。**

1. 关闭客户端与更新器；备份副本的 `data\script.fls` 与 `photo\registration_preview_v3\`。
2. 解压 ZIP，放入 `data\script.fls`；把 **8 张 PNG 全部**合并到 `photo\registration_preview_v3\`（不覆盖、不删除整个 `photo`）。
3. 核对**实际安装位置**的 FLS 与 8 图哈希，不是只核对下载目录。
4. 从完整测试客户端入口启动，避免更新器换回旧包；建议断网检查 UI（这不等于整个客户端已被网络隔离）。

```powershell
Get-FileHash .\data\script.fls -Algorithm SHA256
Get-ChildItem .\photo\registration_preview_v3\*.png | Get-FileHash -Algorithm SHA256
```

回退：退出客户端，恢复配套备份；可恢复原包或 v2.1；不拿 v3 做恢复基线；图片与 FLS 子版本不要混用；只在清理本补丁时删除专用子目录。用户回传 pylog/gamelog 前先遮掉账号、票据。

## 7. 原生验收清单（每项区分“模型已通过”与“真实客户端已通过”）

**启动与路由**
- [ ] 首页正常显示，无黑屏/卡住；「注册账号」可见且点击区域正确
- [ ] 点击后进入新协议，首页不会先变空白；拒绝后返回首页，再次点击仍正常
- [ ] 原选区入口仍走原流程

**协议页**
- [ ] 同意/拒绝都有文字、金色背景一致、无残留旧字；图片与命中范围一致
- [ ] 正文可滚动，标题不遮挡；同意只进入新表单，不发送旧点击统计

**表单页**
- [ ] 左上角无黑块，「离线预览说明」在卡片下部规定位置
- [ ] 「注册账号」只有一份文字，无「登录游戏」残留；「上一步」是新金色按钮
- [ ] 三个编辑区可输入，密码/确认遮罩正常

**光标与焦点（建议短录屏）**
- [ ] 初次进入邮箱框有闪烁光标；点击三框光标只在活动框；每框可见多次明暗切换
- [ ] Tab 顺序 邮箱→密码→确认→邮箱；切走/返回后无残留或多条光标、无命令泄漏

**离线校验/返回**
- [ ] 空表单点 Info 直接显示「離線預覽，未送出。」；空表单点注册给必填提示
- [ ] 密码 <6、不一致、邮箱格式错误走对应提示；粘贴长串不能绕过上限
- [ ] 合法假数据只显示离线提示；上一步/拒绝不保存、不提交、不触发原拒绝断线逻辑

不要在未收到用户反馈时勾选任何一项；局部认可不泛化为整版通过。

## 8. 按现象排查

| 现象 | 先核查 | 不要直接下结论 |
|---|---|---|
| 与 v3.2 一模一样 | 实际运行目录、FLS SHA、四张按钮图是否仍旧图、更新器是否覆盖 | “用户放错了”或“代码肯定没问题” |
| 仍有左上角黑块 | 是否运行新 `_action`；CClickBox 参数；别处是否仍有旧调用 | PNG 透明通道损坏 |
| 按钮文字不可见 | 旧控件是否整体隐藏；新图是否装好；父对象/Z/裁剪；PNG 尺寸 | 再叠一张字幕图 |
| 叠字或旧箭头仍在 | 残留是否来自 DLG 静态对象，用真实对象/资源定位 | 猜名字删全部页面对象 |
| 能输入但光标不闪 | `IsActived`、`m_Line` 显示/色/位置/Z、Flash 调度、失焦时序 | 直接加第二个 Timer |
| 不能点击/输入 | 父对象消息处理/命中区/层级；隐藏控件是否仍拦截 | 仅靠截图证明逻辑正确 |
| 再次黑屏 | 先恢复已知可用状态；新日志 + 已安装 SHA；锁定导入/构造/原生边界 | “v3 EXEC 修好了所以不可能是补丁” |

每轮修正只针对可证实问题，先新增能复现旧 bug 的测试再改源码；**测试替身也可能与实现共享同一个错误假设**，接口以原 code object 核对。

## 9. 本专题的停止条件

- 原输入 SHA 不匹配：停止构建，不放宽锁定。
- 新片段超出原定长预算：停止，不改 XOR 边界、不丢弃无关函数凑空间。
- 原生闪退/黑屏：停止反复覆盖，保留备份与日志。
- 测试接口与原档不一致：修接口/测试，不加绕过。
- 涉及真实凭据、生产 GM、master 合并或生产数据发布：不能沿用离线 UI 的授权推进。
