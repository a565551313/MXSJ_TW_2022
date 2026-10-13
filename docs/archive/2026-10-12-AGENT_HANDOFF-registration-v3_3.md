> ⚠️ **已归档（2026-10-14 整理）**：原 `AGENT_HANDOFF.md`（根目录）。注册 UI v3.3 交付时期的完整状态快照与接手指南。
> 文中“当前/下一步/分支”等描述是 2026-10-12 前后的历史快照，路径与计数可能已失效；保留仅用于证据追溯。
> 现行内容以 [AGENTS.md（长期规则与地图）](../../AGENTS.md)；[docs/STATUS.md（当前状态）](../STATUS.md)；[tools/client_patches/V3_3_DELIVERY_AND_ACCEPTANCE.md（v3.3 交付哈希、安装/回退、验收清单）](../../tools/client_patches/V3_3_DELIVERY_AND_ACCEPTANCE.md) 为准。

# MXSJ 项目完整交接：后续 Agent 从这里开始

> 交接日期：2026-10-12（用户时区 Asia/Shanghai）。
> 仓库：`a565551313/MXSJ_TW_2022`。
> 本轮业务代码基线：`2b913f5`（v3.3 控件修正，已提交、已推送）。
> 当前工作分支：`arena/b53b33e6-mxsj-tw-2022`。
> 本文是**截至该基线的状态快照与接手指南**，不是新功能验收书。
> **最重要：v3.3 已交付，但用户尚未反馈 v3.3 实测结果。不要宣称五个显示/输入问题已经全部通过原生验收。**

---

## 0. 先读这一页：接手时不能弄错的事实

1. 当前紧接着要做的是**注册 UI v3.3 的原生复测闭环**，不是马上另起服务端，也不是再重新设计整套 UI。
2. 用户最新已收到 v3.3 网盘包；该包已针对协议按钮无字、左上角黑块、注册按钮叠字、上一步旧箭头、光标不可见/不闪烁做修正。
3. 用户给的两张截图是 **v3.2**：新协议、新表单都已显示，但存在上述问题。它们不是 v3.3 成功截图。
4. **90 项客户端补丁测试、22 项 CPython 2.5 执行审计通过**。交接时又重跑了这些检查；仍不等于 Windows 原生渲染/输入验收。
5. 交接时另重跑了 **161 项架构测试、96/96 文件名映射核对、22 个待审 CSV 批次文件核验**。这些也不能证明真实玩法可运行。
6. 首页与注册模块已解耦：**仅点击消息 2 才加载注册模块**。这是 v3.2 已实现、v3.3 保留的要求，不要退回首页 eager import。
7. 注册目前是**离线预览**：有三个字段与本地校验，没有真实账号创建、注册 HTTP 请求、验证码、账号保存或假成功。
8. v3.3 **必须同时安装 FLS 和 8 张 PNG**。四张按钮 PNG 已变化；图片目录沿用 `registration_preview_v3`，目录名没有升版不代表内容没变。
9. 仅 entry **337 / 4007** 被改；其他 **5000** 条原样，选区后条款/登录 entry **4806** 未改。原始 FLS、key DB 未覆盖。
10. 服务端只有工程边界/契约/设计和独立的只读数据复核工具；**还没有可游玩的游戏服务端、账号数据库、网关运行实现或地图闭环**。
11. 当前用户明确要本交接文档并提交推送；本轮交接不新增 UI 补丁、不再次上传同一个包、不合入 master。
12. 下一步先读本文第 1–14 节，再按第 16 节行动；长期服务端方向在第 18 节。

### 当前唯一推荐下载链接

**v3.3 控件修正测试候选：**

https://drive.google.com/file/d/11M9rwP36u0-KLP9WaO3YGjNRbGmvf4Rc/view?usp=drivesdk

文件：`MXSJ_registration_preview_v3.3_controls.zip`，24,399,852 字节。

不是正式发布，不是已经原生验收完成的版本。

---

## 1. 用户目标、合作方式与不能擅自改变的范围

### 1.1 长期目标

- 用 Python 实现可长期维护的回合制游戏服务端，本地和后续公网运行共用正式架构，不接受一次性临时 Mock 当成正式基础。
- 可以修改客户端；先做好最小可逆客户端副本，再逐步打通：
  **注册 → 选区 → 登录 → 创建角色 → 进入地图**。
- 第一条真实链路就包含网关，不是业务写完后再硬接一个网关。
- 方向为 asyncio + PostgreSQL、统一账号、区服内角色、类型化且可替换的接入适配。
- 网关有连接、安全与私有 GM 管理入口的设计要求，但不能把玩家监听与 GM 权限混在一起。
- 用户希望多人/多 Agent 按目录和接口协作，不要把所有工作描述成必须由用户一个人完成。

### 1.2 当前客户端 UI 的具体要求

- 首页入口标题为简体 **「注册账号」**。
- 点击入口进入独立新注册协议。
- 协议样式参考的是**选完区服以后出现的服务条款页**，即 `login/service.dlg`；不是选服页面。
- 表单只使用 `login_new/newlogin_800.dlg` 布局/底图；**不得实例化原登录控制器**来借用布局。
- 不再用旧 `reg2`、2980 手机注册及右侧老步骤 UI。
- 原选区后条款/登录流程保持不变；不继承拒绝断线、重连、打开运营网页等旧业务。
- 首页文字处理独立，注册模块只在点击时加载。
- 保留三个字段与 v2.2 本地校验：邮箱、密码、确认密码；Info 入口直接弹离线提示。
- 「上一步」「拒绝」不保存、不提交。
- 所有修改只用于**完整客户端测试副本**，保留回退办法。

### 1.3 用户沟通与交付偏好

- 用户要求“先改完再传”，不能先上传一个尚未完成约定方案的候选再让用户试。
- 出问题先独立自查、复现和改测试，不要只让用户提供日志或让用户反复盲试。
- 用户要求上传 Google Drive 并给链接；**不需要 Gmail，不要自行改成邮件投递或公开分享**。
- 不把静态 PNG、假控件模型截图或标准 Python 测试说成客户端真实截图/真实原生验收。
- 用户曾否定老旧 UI，不要借“回退稳定”为理由把新预览默认改回旧风格；旧版仅用于恢复客户端。
- 若再次分配任务给多个 Agent，每份提示应是**独立完整、可复制的一块**，重复必要背景，不要求用户自行拼装公共说明。

### 1.4 仓库与数据边界

- 不把未审 CSV 发布为 `server/game_data/` 正式配置。
- 当前授权不是合入 master，也不是生产环境发布。
- 不对原包、密钥数据库、不相关模块做顺带修补。
- 不自动启动根目录 `mock_server.py`，其历史行为可能涉及客户端修改。
- 不执行整份反编译/恢复游戏模块。数据研究仍坚持只读解析与受限字面量重建。
- v3.3 审计仅额外执行**明确选出的无外联控件方法**，底层引擎全为替身；这不授权执行任意恢复代码或敏感模块。
- 不恢复曾删除的敏感 entry 1288 大范围 dump，不在日志或交付包里放账号、票据、密钥、密码。

---

## 2. 当前状态与版本历史

| 版本/阶段 | 实际进度与证据 | 如何使用这个结论 |
|---|---|---|
| v1 | 最小可逆注册第一页预览；用户确认同意/拒绝导航 | 历史导航证据，不覆盖后续表单/渲染 |
| v2 | 旧基础表单尝试，用户无法打开；后查与 email2 等不支持控件有关 | 不作为当前可用版本 |
| v2.1 | 移除不支持的次级控件；用户确认表单、提示和导航 | 可作已知可用恢复参考；不是新外观 |
| v2.2 | 加必填/邮箱/密码/确认校验，Info 分流 | 原生校验验收未完整收到；后续一直继承该逻辑 |
| v3 | 服务条款风格协议 + 登录底图表单，加入 PNG 标题 | **用户实测启动黑屏，停用** |
| v3.1 | 确认并修复 EXEC 的 -1/None 参数错误，首页导入增加保护 | 仍 eager import；曾提前上传，用户指出应改完再传；不是最终入口方案 |
| v3.2 | 首页标题独立，点击才导入/构造新页 | 用户两张截图证实新协议和新表单能显示，但报告五类显示/输入问题 |
| **v3.3** | 按真实控件接口修正坐标/透明度，完整替换按钮，显式光标颜色/层级 | **已构建、测试、提交推送、上传；尚未收到用户原生反馈** |

### 2.1 最近提交，按时间从新到旧

| 提交 | 内容 |
|---|---|
| `2b913f5` | v3.3 按钮、说明入口、光标层级修正 |
| `0c71c45` | v3.2 首页独立标题、点击才加载注册 |
| `194dd0f` | 独立复跑 v3 黑屏自查的来源记录 |
| `f707f4e` | 修正 EXEC 真正 None 操作数与启动保护 |
| `d2f24e0` | 用户黑屏后暂停 v3 的文档记录 |
| `e2dc5e6` | 最初 v3 新视觉预览 |
| `998144e` | v2.2 本地校验 |
| `2b27382` / `8059455` | v2.1 用户截图记录 / 修正不支持控件 |
| `05d9446` / `14f4f29` | 安全/GM 与可拆分网关设计（不是运行实现） |
| `70285ff` / `d9721d8` | H/I/J 只读复核工具集成验收 / 集成修正 |

这些代码提交已在当前远程工作分支上。本文提交将位于它们之后；不需要重新 cherry-pick 或重新合并已完成阶段。

---

## 3. v3.2 用户原生反馈：五项问题的原始语境

用户先发送两张游戏窗口截图，文字反馈：

> 1,注册协议的两个按钮没有文本。2、注册界面左上角一块黑色、注册账号按钮叠加了登录游戏文本，上一步按钮不正确

随后补充：

> 还有输入框没有光标闪烁

截图可直接观察到：

- 新协议底图、滚动正文、简体“注册协议”标题已显示；底部两个金色按钮没有可见标签。
- 新表单有紫色卡片、三个字段；左上角有黑色“离线预览说明”块。
- “注册账号”与原“登录游戏”视觉重叠。
- “上一步”仍配旧返回箭头，不是统一的新按钮。
- 单张截图不能证明时间上的闪烁是否发生；“不闪烁”来自用户明确反馈，不应仅凭静态截图反推完整焦点状态。

历史附件名为 `image-1.png`、`image-2.png`。**本次接手检查环境未找到 `/home/user/uploads/`，截图未作为仓库文件保存。**
不要伪造不存在的文件链接；需要像素级比较/动态光标证明时，请以聊天附件或用户新录屏为准。

这些截图不说明原生协议、注册业务、邮箱校验、全部按钮命中区或原选区流程都通过了。

---

## 4. v3.3 实际改了什么，哪些只是待验证假设

### 4.1 已独立复现的硬错误：CClickBox 参数误用

原 entry 3854 的接口：

```python
CClickBox.__init__(self, parent, w, h, color, alpha, msgid)
```

旧代码把“坐标”当成 color/alpha：

```python
interface.CClickBox(self, 200, 28, 300, 394, 3)
# 实际：color=300, alpha=394；位置没有设置，仍是 (0,0)。
```

旧 Python 测试替身也错误地声明为 `(parent,w,h,x,y,msgid)`，因此此前模型测试假通过。

现在：

```python
button = interface.CClickBox(panel, width, height, 0, 0, msgid)
button.SetPos(x, y)
button.SetZ(2)
button.m_PreviewCaption = _picture(button, name, 0, 0)
```

- 说明入口是 `(300,394)`，尺寸 `(200,28)`，颜色/透明度为 0。
- 测试替身按原档参数修正，加入签名与原始代码对象核对。
- CPython 2.5 审计直接执行原 `CClickBox.__init__`，仅 C++ 盒子/点击原语替身化，复现旧调用留在原点的结果。
- 这是确定错误，不需要把截图黑块归咎于用户放错文件。

### 4.2 按钮整体替换，而非在旧控件上再叠一行字

- 协议消息 1/2 的旧控件完整隐藏并禁用。
- 新按钮放在各旧按钮的中心位置，统一 112×34。
- 表单旧登录与返回控件也隐藏并禁用，不再依赖 `SetText('')` 清除旧资源。
- 新表单“上一步”放 `(270,468)`，“注册账号”放 `(430,468)`，都是 112×34 金色带字图。
- 四张按钮图把背景和文字放在同一张 PNG 内，减少旧资源文字层/背景内容不一致的问题。
- 图片是用仓库已有字体与 Pillow 生成的完整按钮底图，不是声称已经精确提取原生按钮所有动画/悬浮/按下状态。
- 当前新按钮使用 `CClickBox`，没有额外实现完整 hover/pressed 皮肤状态；如用户要求动效，需要另行设计和验证，不要描述为已经具备。

### 4.3 显示层级

原档依据：

- `CTextButton.SetTextPos` 会给文字 `SetZ(1)`。
- `CButton.SetPath` 给背景 `SetZ(-1)`。
- `ui.CImage`（entry 369）是容器，内部图像 `m_oImg` 的 Z 为 -1。

本轮显式设置：

| 对象 | 层级 |
|---|---:|
| `_picture` 创建的图片容器（含表单卡片） | Z=1 |
| 新动作点击框 | Z=2 |
| 点击框内图片 | Z=1（相对其父对象） |
| 三个输入框 | Z=2，高于同父卡片 |
| 输入框内 `m_Line` 光标 | Z=1（相对输入框） |
| 首页独立标题图片 | Z=1 |

这来自原生控件的使用方式与本次结构修正；真实引擎的裁剪、层级与事件命中仍需原生确认。
不能断言“协议按钮无字的唯一原因已证明就是 Z”，本轮采用的是消除旧控件依赖并明确前景层的修正。

### 4.4 光标：不要再造第二套闪烁计时器

原档中本来存在：

- `CEdit.Active(True)`：设置活动输入框，显示 `m_Line`，建立 `CreatePyCommand(20, Flash, 1)`。
- `Flash`：当前输入框仍活动则翻转显示状态；失焦后隐藏并终止相关命令。
- `MsgTab`：对 `m_NextEdit.Get()` 调用 `Active(True)`。
- `CRegEdit.Active`：调用 `interface.CEdit.Active`，可再通知父页面 OnActive。

本轮：

- 三字段构造显式传 `linecolor=0x805B45`，不依赖默认颜色。
- 显式设置输入框/光标 Z。
- 保留邮箱初始 Active、三框循环 Tab、密码遮罩与继承的编辑逻辑。
- 没有新建另一套 blink timer，没有全局改 `interface.CEdit`，没有修改所有游戏输入框。

审计运行了实际原档的构造器、Active（内含 Flash）、MsgTab、SetNextEdit、GetLineColor、IsActived；
在假时钟边界上逐框检查显示→隐藏→显示→Tab、末框绕回、失焦隐藏和命令释放。
**没有运行 Windows 鼠标事件派发或真实引擎帧时钟，所以仍需复测实际闪烁。**

### 4.5 本轮保持不变的部分

- 首页只在点击时加载注册。
- 协议/表单 DLG 选择与现有页面顺序。
- v2.2 校验及 Info 绕过校验的区别。
- 原选区后条款/登录模块。
- 原始 FLS、密钥库、生产静态配置。
- 8 张图片的文件名与目录；但四张按钮图内容已更改。

---

## 5. 当前 UI 行为、坐标与校验规则

### 5.1 实际路由

```text
首页 mainpage
  └─ 消息 2「注册账号」
       ├─ 点击时 import register
       ├─ register.Show(True) → 新 CRegPanel1 / login/service.dlg
       ├─ 构造成功才 mainpage.Show(False)
       └─ import/构造 Python 异常：打印错误，首页不隐藏

新协议 CRegPanel1
  ├─ 消息 1「同意」 → Step(1) → 新 CRegPanel2
  └─ 消息 2/3「拒绝/返回」 → 先 mainpage.Show(True)，再 register.Show(False)

新表单 CRegPanel2
  ├─ 消息 1「上一步」 → 继承 v2.2 路由回协议
  ├─ 消息 2「注册账号」 → 本地校验 → 离线提示，无真实提交
  └─ 消息 3「离线预览说明」 → 不读字段，直接离线提示
```

`register.GetData` 中旧标题辅助函数为兼容保留，**当前首页不调用它**。
不要因为看到这个函数还在，就误以为已退回 eager import；看 `home_registration_entry.py` 和构建报告。

### 5.2 协议页

- `login/service.dlg`。
- 获取 `loc_msg`，读取其坐标/尺寸创建 `chatoutput.COutput`。
- 字体 `interface.FontLT14_3`，颜色 `interface.COLOR_1`。
- 正文每行末尾 `#r`，滚动初始化为 0。
- 标题图 `(280,83)`，240×34。
- 正文是明确的**离线预览说明**，不是正式运营服务条款，不能说用户已经接受正式法律协议。
- 简体标题/按钮以 PNG 显示；正文和历史提示仍主要为 CP950 繁体，未完成全客户端简体化。

### 5.3 表单页（800×600）

| 元素 | 位置/尺寸 |
|---|---|
| 布局 | `login_new/newlogin_800.dlg`，只加载布局，不跑 `CLoginIn` |
| 卡片 | `(200,138)`，400×300 |
| 邮箱框 | `(340,214)`，226×22，最多 32 |
| 密码框 | `(340,272)`，226×22，最多 16，密码遮罩 |
| 确认框 | `(340,330)`，226×22，最多 16，密码遮罩 |
| 说明入口 | `(300,394)`，200×28，透明点击框 |
| 上一步 | `(270,468)`，112×34 |
| 注册账号 | `(430,468)`，112×34 |

DLG 中多余的旧交互控件隐藏；模板部分静态装饰、顶部提示、底部年龄提示可能仍保留。
这不是新美术资源整包替换，也没有其他分辨率适配承诺。

### 5.4 校验边界

- 邮箱、密码、确认密码三个必填字段。
- 邮箱先 trim，最长 32；基本 ASCII 格式检查，最短长度受当前 CheckEmail 路径限制。
- 密码 6–16，确认必须完全一致。
- 当前使用的基本正则：`(?i)^[\w.-]+@[a-z\d-]+(\.[a-z\d-]+)+$`。
- 这不是完整 RFC 邮箱解析、DNS 校验或邮箱所有权验证。
- 编辑控件本身也有字符输入约束（`CMailEdit` / `CRegEdit`），不能只依据 DoNext 正则描述全部输入行为。
- `Info` 直接显示 **`離線預覽，未送出。`**；只有这个入口绕过字段读取与校验。
- 上一步/拒绝不能调用 Save 或真实提交；不要为演示效果制造“注册成功”。

---

## 6. 源码和证据地图

### 6.1 最优先阅读

| 路径 | 作用 |
|---|---|
| [`tools/client_patches/README.md`](../../tools/client_patches/README.md) | 客户端补丁最新入口与历史指引 |
| [`REGISTRATION_CONTROL_FIX_V3_3.md`](../../tools/client_patches/REGISTRATION_CONTROL_FIX_V3_3.md) | 五类问题、原生接口依据、本轮修正和验收边界 |
| [`registration_visual_overlay.py`](../../tools/client_patches/registration_visual_overlay.py) | 自写 Python 2.5 UI；图片、动作控件、新协议、新表单 |
| [`home_registration_entry.py`](../../tools/client_patches/home_registration_entry.py) | 独立首页标题与点击加载片段 |
| [`build_visual_preview.py`](../../tools/client_patches/build_visual_preview.py) | 最新 v3.3 构建器、映射、内联、定长重序列化、报告 |
| [`build_registration_preview.py`](../../tools/client_patches/build_registration_preview.py) | 原 v1–v2.2 定宽补丁、校验逻辑、FLS/字节码公用函数 |
| [`prepare_visual_assets.py`](../../tools/client_patches/prepare_visual_assets.py) | CPython 2.5 精确编译和 Pillow 图片生成 |
| [`visual_assets/manifest.json`](../../tools/client_patches/visual_assets/manifest.json) | 源码、编译产物、字体输入、8 张 PNG 哈希 |
| [`audit_visual_runtime.py`](../../tools/client_patches/audit_visual_runtime.py) | 从实际构建 FLS 提取片段、标准 opcode 转译和独立执行 |
| [`visual_runtime_harness.py2`](../../tools/client_patches/visual_runtime_harness.py2) | CPython 2.5 假引擎边界、原控件方法、失败路径与光标审计 |
| [`V3_3_RUNTIME_AUDIT.json`](../../tools/client_patches/V3_3_RUNTIME_AUDIT.json) | 本版 22 项结果、FLS SHA、原生未验证标记 |

### 6.2 测试文件

| 文件 | 重点 |
|---|---|
| `test_registration_preview.py` | 原始包约束、旧预览构建、网络调用隔离等 |
| `test_registration_validation.py` | v2.2 必填/格式/长度/一致性和 Info 分流 |
| `test_visual_preview.py` | UI 模型、新控件、图片尺寸、层级、接口签名与文件不变 |
| `test_visual_startup_guards.py` | None 操作数、懒加载、内联重定位、消息 2 路由、定长封装 |

### 6.3 历史资料不是当前状态源

- `REGISTRATION_LAZY_ENTRY_V3_2.md`：理解首页拆分，别把其 85/17 计数当成本轮计数。
- `V3_STARTUP_SELF_AUDIT.md`：理解黑屏硬错误与证据边界。
- `V3_1_RUNTIME_AUDIT.json` / `V3_2_RUNTIME_AUDIT.json`：历史版本哈希和审计。
- `REGISTRATION_VISUAL_PREVIEW_V3.md`：初版视觉方案和失败记录；不能照它重新分发 v3。
- `REGISTRATION_BASIC_FORM_PREVIEW_V2_1.md`、`REGISTRATION_VALIDATION_PREVIEW_V2_2.md`：历史恢复与校验来源。

### 6.4 原档条目定位

| entry | 文件/用途 |
|---:|---|
| 337 | `script/login/mainpage.py` |
| 4007 | `script/login/register.py` |
| 4806 | `script/login/loginin.py`，原选区后条款/登录，不修改 |
| 3854 | `script/interface.py`，CClickBox/CButton/CTextButton/CEdit/CCaret |
| 369 | `script/mxui/imagewidget.py`，CImage 真正实现 |
| 4537 | `script/mxui/ui.py`，聚合导出，不要以为 CImage 实现在此处 |
| 1156 | `script/mxui/textwidget.py` |
| 579 | `script/combdialog.py`，CCombPanel/布局载入 |
| 3564 | `combmacro` |

原脚本索引：`server/docs/catalog/script_entries.jsonl`。
旧反编译文本在 `tools/decompiler/output/script_fls/`；部分模块缺失或反编译不准确。
**原 code object / bytecode 才是接口签名与控制流的依据**，不要把不完整反编译当可执行源码。

---

## 7. FLS 格式、补丁封装和不能踩的坑

### 7.1 当前输入锁定

- `data/script.fls`：24,454,082 字节。
- SHA-256：`8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72`。
- key DB：`tools/decompiler/script_fls_keys.json`。
- SHA-256：`43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb`。
- 当前构建器拒绝非锁定基线；不是给任意用户修改包再打差分。

### 7.2 容器/VM

- `0SLF`，**12 字节头**，5002 条、每条 16 字节目录。
- 解码链：目录 → zlib → 五段 XOR → marshal/code object。
- 本轮是客户端自定义 **Python 2.5**，不是另一个 `data.fls` 的自定义 Python 2.7。
- marshal 内 code string 起点使用代码对象偏移 `+22`；不要套错布局。
- 原生 `HAVE_ARGUMENT=0x5f`；新 CPython 2.5 标准 opcode 必须先映射为客户端 opcode。
- 标准 `EXEC_STMT=85` 对应原生 `0x21`。
- 冻结文件是 CPython 2.5.6 的 marshal v2，小型自写代码对象，不是运行时下载 Python 源码。

### 7.3 本版两条载荷的固定参数

| entry | 解密后长度 | XOR keys | bounds |
|---:|---:|---|---|
| 337 | 10,335 | 226 / 28 / 112 / 247 / 187 | 2163 / 4281 / 6390 / 8473 |
| 4007 | 44,362 | 222 / 84 / 13 / 219 / 82 | 8966 / 17948 / 26868 / 35778 |

v3.3 重序列化后的真实尾常量填充：337 为 **307** 字节，4007 为 **8191** 字节。
这些数值仅对本版有效，改源码后以构建报告为准，不要硬写旧 padding。

### 7.4 构建路径

1. 先从原包生成 v2.2 `form-validate` 的语义基线。
2. 337：在两个方法中内联自写片段，重映射常量/名称/局部变量，重定位所有保留跳转。
   - `__init__` 的原可选 tg.id 尾块被替换；本版片段 `[426,781)`。
   - `OnMessage` 的原消息 2 动作块被替换；本版片段 `[90,195)`。
   - 不允许旧跳转落入被替换区间内部。
   - 两个方法过期 lnotab 清空，避免旧字节偏移误导；其他方法保持语义。
3. 4007：删除已禁用的旧 `CRegPanel2_2980` 类构造，以其常量槽 41 放置新 overlay。
   - 原 `[488,513)` 构造块改成 EXEC + NOP。
   - globals/locals 从真正 None 常量查找，不硬编码“常量 0 就是 None”。
4. 两条载荷重建 intern 表，补一个真实尾部常量到原长度；独立解析必须消耗完整载荷，不依赖忽略尾垃圾。
5. 使用原 keys/bounds 加密回去，解密往返校验。
6. 针对**原包**追加两份载荷与新目录，保留原主体；比较其他 5000 条目录与压缩载荷逐字节不变。
7. 写到仓库外，不覆盖已有 FLS；打包前再次比较哈希、测试报告与图片。

### 7.5 历史硬错误及其他风险

- v3 register 模块 `consts[0] == -1`，`consts[1] is None`。
  错误 EXEC 入栈是 `(code,-1,-1)`，独立复现 `TypeError: exec: arg 2 must be a dictionary or None`。
- v3.1 仅给 eager import 加保护，仍不满足用户后续点击加载要求。
- v3.2 修好了隔离，但模型误写 CClickBox 签名，漏掉真实 UI bug。
- 目前重序列化/原生 VM/资源渲染仍存在非标准解释器无法完全验证的边界。
- Python 异常保护不保证原生崩溃、死锁、卡住、资源加载硬失败可恢复。
- 隐藏旧页必须在目标创建成功之后；不要重新引入先隐藏、后导入导致的空白页。
- 首页原可选 `tg.id` 推广标识块被替换，**不再显示该标识**。这是已记录的副作用，不是无副作用字符串替换。

---

## 8. 交付包、哈希、链接及恢复版本

### 8.1 当前 v3.3

| 项目 | 值 |
|---|---|
| 源码提交 | `2b913f5` |
| ZIP 文件名 | `MXSJ_registration_preview_v3.3_controls.zip` |
| ZIP 大小 | 24,399,852 bytes |
| ZIP SHA-256 | `717fed1f22c3e6c1c9ceeccca190078268ac0797a0823f6db06c053373a156aa` |
| FLS 大小 | 24,556,254 bytes |
| FLS SHA-256 | `6ef84a13c23ca0abfaa7a9febf8ba49b4df569a9cf65286c4b1844f9df63cddb` |
| Drive ID | `11M9rwP36u0-KLP9WaO3YGjNRbGmvf4Rc` |
| Drive 链接 | https://drive.google.com/file/d/11M9rwP36u0-KLP9WaO3YGjNRbGmvf4Rc/view?usp=drivesdk |

ZIP 有 14 个文件：FLS、8 张图片、安装 README、verification、OFFLINE_TESTS、V3_3_RUNTIME_AUDIT、控件修正文档。
无字体文件，无完整客户端，无账号凭据。

当前本地（交接时存在，之后必须重新检查）：

```text
/home/user/artifacts/MXSJ_registration_preview_v3.3_controls.zip
/home/user/artifacts/MXSJ_registration_preview_v3.3_controls.zip.sha256
/home/user/artifacts/mxsj-registration-preview-v3.3/
```

FLS 可确定性复建；若重新组 ZIP，README、时间戳、压缩工具或测试耗时文本改变会导致 ZIP SHA 不同。
不要因内部 FLS 相同就声称重新生成的完整 ZIP 与旧交付逐字节相同。

### 8.2 当前图片哈希

目录均为 `photo/registration_preview_v3/`。

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

权威机器清单以 `visual_assets/manifest.json` 与交付 `verification.json` 为准。

### 8.3 旧版仅供追溯，不要把链接串错

| 版本 | Drive 链接 | 状态 |
|---|---|---|
| v3.2 | https://drive.google.com/file/d/1P2zK9Dt-De3VQnK3JSSBEvTFsjJCodny/view?usp=drivesdk | 用户已报告控件缺陷，非最新 |
| v3.1 | https://drive.google.com/file/d/1MVInZtJmx0k-Gml9y6IPTGvxTqQ6AHi6/view?usp=drivesdk | 提前上传的未拆分候选，不推荐 |
| v3 | https://drive.google.com/file/d/1GoKdMuw9Tmrs_bF3B1eVRhQOjnM9JA33/view?usp=drivesdk | **原生启动黑屏，停用** |
| v2.2 | https://drive.google.com/file/d/1Frqlr0sR_N0x793X1GLV9vckPNYJIrDQ/view?usp=drivesdk | 历史本地校验预览 |
| v2.1 | https://drive.google.com/file/d/1aos6ny8VWAw09vKL20lBW-7uhRSc6Qh3/view?usp=drivesdk | 曾确认可用的恢复参考，旧外观 |

旧 FLS 识别：

```text
原包   8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
v2.1   ed40cbade80a42b6924b9a99edffefbaa4100dbf624ebd653a789d8b7283c0ba
v2.2   29d36efac4d1d941cec0f50a1b3956d24ba65f925b066756e9510362de1f0938
v3     b26af0973ac1fb28f0d2b482e2d24a710d682e4ff51b2ec1a586c219a75cc4a2
v3.1   1a0283d0b031f33868e875984fffa91b2ce7eed66de823d94efc9d25f196654e
v3.2   51187b3806497cab206cf2581cbcd2dbb0fe8ec4be4928a9bad41aebf2e105f3
v3.3   6ef84a13c23ca0abfaa7a9febf8ba49b4df569a9cf65286c4b1844f9df63cddb
```

旧 v3.2 ZIP：24,396,468 bytes，SHA `a8b674f3b9130b3149a27eb4406130b7e893441811e9e7544f0f2702a33a6714`。
失败 v3 ZIP：24,392,175 bytes，SHA `34a69e0a0cd588dbcb95bdf77eef36d78f7f48f436c493ea0fd924b5f37bece6`。
历史自查曾重建与该 v3 FLS 一致的单文件审计 ZIP；它不是原完整交付 ZIP，不可用于安装分发。

---

## 9. 接手环境检查与常见“快照恢复”问题

### 9.1 第一组只读命令

```bash
cd /home/user/MXSJ_TW_2022
git status --short
git branch --show-current
git log -8 --oneline
sha256sum data/script.fls tools/decompiler/script_fls_keys.json
ls tools/client_patches/visual_assets
```

本会话工作分支固定如页首；延续此会话时只在该分支提交并推送。
如果新 Agent 在另一独立会话中有不同分支约束，遵守其实际工作环境，不擅自切换、覆盖或 force-push 本分支。

### 9.2 曾真实发生的环境恢复异常

有两次新工作环境中：

- HEAD 回到根基线 `3bee451`。
- `server/`、`tools/client_patches/` 显示为 untracked，但实际内容已经与远程新版一致。
- `.cache`、编译器、artifacts 或 uploads 可能消失。

因此**不要看到 untracked 就删目录，也不要看到旧 HEAD 就覆盖现有文件**。
本轮修复前先 fetch 指定远程分支，以 `git ls-tree -rz` 和逐文件 blob 哈希比对；确认所有远程跟踪文件存在且完全一致后才恢复索引/HEAD。
使用 `-z` 处理中文文件名，不能把 Git 引号转义后的字符串当成真实路径。

如果有任何不一致：先保存差异与备份、确定是用户变更还是快照缺件，再处理；不要机械照抄 `reset --hard`、`clean -fd` 或覆盖性 restore。
本文不提供自动重置脚本，避免下一位在不同状态下误删用户工作。

### 9.3 临时工具路径

交接时存在：

```text
/home/user/.cache/v3-ui-fix/cpython-2.5.6/python
/home/user/.cache/v3-ui-fix/venv/                 # Pillow 构建环境
/home/user/.cache/v3-ui-fix/configure.log
/home/user/.cache/v3-ui-fix/make.log
/home/user/.cache/v3-ui-fix/inspect.py            # 临时控件检查脚本，不是产品源码
/home/user/.cache/v3-ui-fix/details.py
/home/user/artifacts/handoff-checks/             # 本次交接复查输出
```

`.cache` 不是可依赖的长期交付。编译器消失可重建；普通 FLS 构建只用已入库冻结文件，无需该编译器。

---

## 10. 可复制的构建、测试与审计命令

### 10.1 只运行已冻结代码的普通构建

只需要 Python 3.11+ 标准库，不需 Pillow 或 Python 2.5。

```bash
cd /home/user/MXSJ_TW_2022
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/client_patches -v

# 必须选择新的仓库外目录；已有 data/script.fls 时构建器会拒绝覆盖。
PYTHONDONTWRITEBYTECODE=1 python3 tools/client_patches/build_visual_preview.py \
  --allow-unverified-candidate \
  --output-dir /home/user/artifacts/registration-next-check
```

本版不改源码的输出 FLS 应为第 8 节 v3.3 SHA。参数 `--allow-unverified-candidate` 是刻意保留的原生未验收提醒，不要为了省事移除。

### 10.2 修改自写 Python 2.5 源码后冻结

- 不要用 Python 3 编译出 pyc 再塞给客户端。
- `registration_visual_overlay.py` 与 `home_registration_entry.py` 必须维持 Python 2.5 语法。
- 只编译自写片段，不编译整份反编译 register/mainpage 替换原游戏逻辑。

```bash
# 只改代码，保留已有 PNG，不需要 Pillow：
python3 tools/client_patches/prepare_visual_assets.py --code-only \
  --python25 /home/user/.cache/v3-ui-fix/cpython-2.5.6/python

# 改了绘图内容，使用有 Pillow 的 Python 3 环境重绘并冻结：
/home/user/.cache/v3-ui-fix/venv/bin/python tools/client_patches/prepare_visual_assets.py \
  --python25 /home/user/.cache/v3-ui-fix/cpython-2.5.6/python
```

修改源后不更新 manifest 会被构建器拒绝，这是预期保护。
重绘所用字体是仓库已有 `Fonts/FZLanTingYuan-DB-GBK.ttf`，**不把字体打包分发**。
图片相关依赖升级可能改变编码字节；先查看 diff、实际图片及哈希，再冻结。

### 10.3 如果 CPython 2.5.6 编译器不存在

该旧版本只用于隔离的离线编译/审计，不是服务器运行版本，也不用于访问真实账号或网络服务。

```bash
mkdir -p /home/user/.cache/registration-compiler
curl -L --fail \
  https://codeload.github.com/python/cpython/tar.gz/refs/tags/v2.5.6 \
  -o /home/user/.cache/registration-compiler/cpython-2.5.6.tar.gz
tar -xzf /home/user/.cache/registration-compiler/cpython-2.5.6.tar.gz \
  -C /home/user/.cache/registration-compiler
cd /home/user/.cache/registration-compiler/cpython-2.5.6
./configure --without-threads CFLAGS='-O2 -fcommon -fno-strict-aliasing' > ../configure.log 2>&1
make -j4 python > ../make.log 2>&1
./python -S -c 'import sys; print sys.version_info[:3]'
# 应为 (2, 5, 6)；只构建核心 python，无需 make install。
```

需要 Pillow 时可在仓库外创建 Python 3 venv 并安装，不改生产依赖清单。

### 10.4 独立执行审计

```bash
cd /home/user/MXSJ_TW_2022
PYTHONDONTWRITEBYTECODE=1 python3 tools/client_patches/audit_visual_runtime.py \
  --python25 /home/user/.cache/v3-ui-fix/cpython-2.5.6/python \
  --report /home/user/artifacts/registration-next-runtime-audit.json
```

说明：

- 构建实际 FLS，再从中提取片段，不是只运行源文件模型。
- 把自定义 opcode 反映射到标准 CPython 2.5 后执行。
- 还会独立解析两个完整 marshal，但不执行两个完整游戏模块。
- 本版额外选择 entry 3854 的控件方法，原生底层为替身。
- `--shipped-zip` 只接受已知失败 v3 FLS SHA。没有旧 ZIP 时直接省略，旧错误用已知操作数组合回归。
- 本版记录的 `shipped_v3_fls_sha256: null` 就是省略了该参数，不能声称重新读取了原交付 ZIP。

### 10.5 后端/静态资料的只读回归

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s server/tests/architecture -v
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/verify_source_map.py
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/export_review_csv.py --check
```

这些不是游戏运行命令，不会建立账号服务或证明报文兼容。

---

## 11. 交接时重新执行的检查

本次仅写交接文档之前，在 `2b913f5` 业务代码上重新执行：

| 检查 | 本次结果 | 不能外推为 |
|---|---|---|
| client_patches unittest | 90 PASS | Windows 引擎、实际鼠标、光标时钟已通过 |
| CPython 2.5 runtime audit | 22 PASS；FLS SHA 与 v3.3 相同 | 完整恢复游戏模块已运行 |
| server architecture | 161 PASS | 玩法/数据库/网关已有实现 |
| verify_source_map | 96/96 | 96 个模块规则真实可玩 |
| export_review_csv --check | 22 文件一致 | 可发布生产 game_data |
| 原包/key DB SHA | 与锁定值一致 | 所有历史密钥语义都已认证 |
| 当前已交付 ZIP SHA | 与第 8 节一致 | 新 Windows 安装已验收 |

机器摘要：[`notes/handoff/2026-10-12-checks.json`](../../notes/handoff/2026-10-12-checks.json)。
原始输出在 `/home/user/artifacts/handoff-checks/`，其存续需重新检查。
本轮没有重跑 H/I/J 的浏览器与 API 全套；不要把第 17 节历史计数写成本轮新执行。

---

## 12. Windows 安装、核对与回退

用户之前的环境：`D:\Lager\夢想世界`、客户端 2.27.2、800×600。
路径可能已被用户复制/改名；操作前确认目标是**测试副本**。

1. 关闭客户端和更新器。
2. 备份测试副本的 `data\script.fls` 与 `photo\registration_preview_v3` 子目录。
3. 解压 v3.3 ZIP。
4. 把包内 `data\script.fls` 放到测试副本对应位置。
5. 把完整 8 张 PNG 合并覆盖到对应专用子目录；**不能覆盖/删除整个 photo**。
6. 核对实际安装 FLS，而不是只核对下载目录里的 FLS。
7. 从完整测试客户端入口启动，避免更新器又换回旧包。
8. 建议断网检查 UI，但不能因此宣称整个客户端已被补丁网络隔离。

PowerShell（在实际测试客户端根目录执行）：

```powershell
Get-FileHash .\data\script.fls -Algorithm SHA256
Get-ChildItem .\photo\registration_preview_v3\*.png | Get-FileHash -Algorithm SHA256
```

若用户说“改了没变化”，先核对实际安装 FLS/8 图哈希、运行路径、更新器是否覆盖。
若是真实渲染/焦点问题，应自查代码与资源机制，不要把“核对文件”当推卸所有问题的答案。

回退：

- 退出客户端，恢复配套备份 FLS/图片。
- 可恢复原包或曾确认可用的 v2.1。
- 不拿明确失败的 v3 做恢复基线。
- 新图片对子版本可能不同，回退时不要混用。
- 只有需清理本补丁时才删除专用子目录，绝不删除整个 photo。
- 用户回传 pylog/gamelog 前应遮掉账号、票据等敏感值。

---

## 13. 下一位 Agent 的验收清单

下面每项都要区分“静态/模型已通过”和“用户真实客户端已通过”。截至交接，v3.3 的原生列均为**待验证**。

### 13.1 启动与新路由

- [ ] 首页可正常显示，无新黑屏/卡住。
- [ ] 首页“注册账号”可见，点击区域正确。
- [ ] 点击后进入新协议，原首页不会先变空白。
- [ ] 拒绝后返回首页，再次点击仍正常。
- [ ] 原选区入口仍能进入原流程，没被新注册绑定覆盖。

### 13.2 协议

- [ ] 同意/拒绝都有文字，金色背景一致，没有残留旧字。
- [ ] 按钮图片与点击命中范围一致，未被滚动/背景遮挡。
- [ ] 正文可滚动，标题不遮盖滚动区。
- [ ] 同意只进入新表单，不发送注册/旧点击统计。

### 13.3 表单

- [ ] 左上角无黑块，“离线预览说明”在卡片下部规定位置。
- [ ] “注册账号”只有一份文字，原“登录游戏”不再出现。
- [ ] “上一步”是新金色按钮，旧箭头/旧点击区没有残留。
- [ ] 三个编辑区接受输入，无背景/图片挡住文字或点击。
- [ ] 密码和确认字段遮罩正常。

### 13.4 光标与焦点（最好短录屏，而非一张静态截图）

- [ ] 初次进入时邮箱有清晰可见的闪烁光标。
- [ ] 鼠标分别点击三个框，光标只在活动框中显示。
- [ ] 每框观察至少数次明暗切换。
- [ ] Tab 顺序邮箱→密码→确认→邮箱。
- [ ] 切换到按钮/其他窗口/返回上页时，不留下旧光标或多条光标。
- [ ] 返回后再次进入，焦点与命令没有泄漏或叠加。

### 13.5 离线校验/返回

- [ ] 空表单点 Info，直接显示“離線預覽，未送出。”，不先报必填。
- [ ] 空表单点注册，给必填提示。
- [ ] 密码小于 6、不一致、邮箱格式错误走正确提示。
- [ ] 输入框本身限制与校验上限一致；粘贴长字符串也不能绕过。
- [ ] 合法假数据只显示离线提示，没有注册成功假象。
- [ ] 上一步不保存、不提交；拒绝不触发原拒绝断线逻辑。

不要未经用户反馈把复选框直接勾全。若用户只认可其中一项，逐项记录，不要把局部认可泛化为版本全部通过。

---

## 14. 按现象排查：先做什么，不要做什么

| 现象 | 优先核查 | 不要直接下结论 |
|---|---|---|
| 与 v3.2 一模一样 | 实际运行目录；FLS SHA；四张按钮是否仍旧图；更新器 | 用户肯定放错了，或代码肯定没问题 |
| 仍有左上角黑块 | 是否运行新 `_action`；CClickBox 参数；是否别处仍有旧调用 | PNG 透明通道一定损坏 |
| 按钮文字仍不可见 | 整个旧控件是否隐藏；新图是否装好；父对象/Z/裁剪；PNG尺寸 | 全靠再加一张字幕图能解决 |
| 叠字或旧箭头仍在 | 残留图是否来自独立 DLG 静态对象；通过真实对象/资源定位 | 猜 anonymous 名称并全删页面对象 |
| 能输入但光标不闪 | 实际焦点 IsActived、m_Line 显示/色/位置/Z、Flash 调度、失焦时序 | 必定是没有写计时器；直接加第二个 Timer |
| 不能点击/输入 | 父对象消息处理/命中区/层级；隐藏控件是否仍拦截；窗口焦点 | 仅靠截图证明逻辑正确 |
| 再次黑屏 | 先恢复已知可用状态；新日志与已安装 SHA；锁定导入/构造/原生边界 | v3 EXEC 修好了，所以绝不可能是补丁问题 |
| 校验行为回归 | v2.2 基线是否仍使用；Info 参数是否 false；字段访问是否误接旧控件 | 改文案掩盖分支错误 |

建议每轮修正严格限制到可证实问题，新增能复现旧 bug 的测试，再构建下一候选；不要只修改测试期望让失败变绿。
本轮最重要的教训正是：**测试替身也会错，而且可能与实现共享同一错误假设。**

---

## 15. 提交、推送与交付流程

### 15.1 每次客户端修改

1. 查看 branch/status，保留用户已有变更。
2. 明确待修问题与原生/静态证据。
3. 修改自写片段/必要构建逻辑，控制 entry 范围。
4. 源码有改动就更新冻结文件和 manifest。
5. 跑客户端测试、CPython 2.5 审计；按影响范围跑架构/数据检查。
6. 生成新的仓库外目录，不覆盖旧包。
7. 核对 source/key DB 不变、5000 条未改、登录模块未改。
8. 写版本说明、安装/回退/已验证与未验证边界。
9. 提交源码、测试、小型冻结资产与文档；**不要 git add 24 MB 交付 FLS/ZIP**。
10. 只推当前工作分支；没有用户授权，不开合并生产/master 的动作。
11. 打包验证 ZIP 成员、CRC、FLS/PNG SHA、报告与包一致。
12. **改完且检查完成以后再上传**，拿到工具返回的真实链接才给用户。

本会话推送命令：

```bash
git push origin arena/b53b33e6-mxsj-tw-2022
```

不要 force push，不需要修改远程认证配置；认证出错应提示重新连接，不索要密码或 token。

### 15.2 Drive

- 当前 v3.3 已上传，不要交接后重复上传无变化的副本。
- 后续要新交付时，先加载 Google Drive 工具并读取实际工具结构。
- 已用上传工具的本地 `file_path` 成功上传约 24 MB ZIP，不需要把整包 base64 塞进对话。
- 不自动 make_public、改权限、发 Gmail、删除旧文件。
- 上传成功不等于用户验收；提交推送成功也不等于客户端正确。

---

## 16. 接手后的优先级与停止条件

### P0：先建立真实状态

1. 阅读本文和 v3.3 修正文档。
2. 核对最新分支/提交，确认是否已有后续用户反馈或新代码，避免在过时状态上重做。
3. 验证原包/key DB 与冻结文件存在。
4. 用户尚未回报时，说明最新 v3.3 已交付，可询问具体五项复测情况；**无需再问“是否开始修复”**。
5. 若有新失败，优先复现接口/渲染/焦点问题，再提供下一个真实修正版，不盲目重发 v3.3。

### P1：完成注册 UI 闭环

- 对第 13 节做逐项记录。
- 确认重复进入/返回、原选区流程不受影响。
- 需要客户端日志/录屏时，仅索取最小相关信息，提醒脱敏。
- 对实际画面问题，不能只附新 PNG 说“这就是修好的客户端截图”。
- 验收完成后写清具体环境、安装哈希、证据和未覆盖项；不要丢掉离线预览限制。

### P2：经用户确认进入真实纵向切片

先提交/推送当前稳定客户端里程碑，再实现账号/网关/选区/角色/地图的真实闭环。
此阶段必须重新定义后端契约、迁移、凭据存储和错误语义；不能直接把当前离线 DoNext 改为旧运营 HTTP 请求。

### 停止条件

- 原输入 SHA 不匹配：停止构建，调查不同版本，不放宽锁定。
- 新片段超出原定长预算：停止，不悄悄改 XOR 边界或丢弃不相关函数凑空间。
- 原生闪退/黑屏：停止反复覆盖，保留备份与日志。
- 测试接口与实际原档不一致：修接口/测试证据，不增加绕过。
- 涉及账号真实凭据、生产 GM、master 合并或生产数据发布：不能沿用离线 UI 授权自动推进。

---

## 17. 其他已完成工作：数据、H/I/J 复核工具，不要重做

### 17.1 一级目录不是完整玩法

- `server/README.md` 为服务端工程骨架总入口。
- 21 个一级责任区，81 个细分工作包，5002 条材料索引。
- 索引覆盖不代表玩法规则完整；大量条目仍未映射到工作包。
- 模块边界与拥有者见 `server/docs/MODULES.md`、`SUBSYSTEMS.md`、`OWNERSHIP.md`、`INTERFACES.md`。

### 17.2 用户要的是静态配置，不是玩家实例数据

此前“道具列表、宠物列表”明确指客户端静态模板，不是玩家背包或玩家已拥有宠物。
CSV 可以使用，但要保留来源、原始 ID、异常、覆盖写和顺序，不为简体显示目标掩盖解码损坏。

当前批次：`server/docs/csv_checks/batch_001/`，**22 个文件，含 17 个 CSV**。
这仍是待审批次，不是 `server/game_data` 生产发布。

本次 exporter 核验结果：

| 来源 | 原始记录 | 待审 CSV | 隔离 |
|---|---:|---:|---:|
| 1945 道具 | 6852 | 6851 | 1 |
| 2027 宠物详细 | 135 | 135 | 0 |
| 2954 宠物资质 | 132 | 131 | 1 |
| 3205 宠物技能 | 581 | 579 | 2 |

- 隔离四条：72548、2800、719、4406，按批次证据理解各自原因，不擅改数值。
- 资质缺失：3010、4021、4022，缺失不是零。
- 3205：**590 次写、581 个唯一键、9 次覆盖**，保留覆盖证据，不只留下最后字典值。
- 同名技能歧义：`終級命中` → 329/355；`高級命中` → 229/255，不靠名称猜唯一 ID。
- 地图/NPC 两个来源分离；顺序、零 ID、重复和差异保留。
- 不要重建已完成的 581 技能分析，也不要把历史“无法重建主表”的旧文档当当前结论。

材料阅读优先级：

1. `server/docs/csv_checks/BATCH_001.md`、`batch_001/manifest.json`、`validation.json`。
2. `server/docs/csv_checks/AGENT_G_CONSOLIDATION.md` 与 A–F 的专项证据。
3. `server/docs/review_browser/ACCEPTANCE.md`。
4. `CSV_READINESS.md`、`CLIENT_DATA_AGENT_HANDOFF.md` 等早期资料是历史背景，其中计数/未完成状态可能已被后续批次取代。

历史 Agent A 的替换、E 的边界修正、G 的集成及 PR 收尾都已有提交；不要按旧分工再重派一遍。
已结束的 PR 审查授权只针对当时事项，不自动变成所有未来 PR 的合并授权。

### 17.3 只读复核 API/网页已完成，不是游戏网关

入口：

```text
server/apps/review_api/
server/apps/review_web/
server/tools/review_browser_checks/
server/docs/review_browser/
```

`70285ff` / `d9721d8` 已完成有界 H/I/J 集成修正和验收。历史报告分别记录：

- H 目录测试 34、API 测试 27。
- I 前端 112 通过，9 个在线项默认跳过；单独真实 API 联调 12 通过（与前述有重叠，不能相加宣传）。
- I TypeScript / Vite 构建通过。
- J 独立验收 68 通过。
- 真正 Chromium 16 场景，不是 jsdom 冒充浏览器。
- 分页提前空页/total 漂移/重复 `_pk` 等被拒绝。
- manifest 哈希、隔离数量、覆盖证据完整性检查通过；不是数字签名认证。

历史详细命令、证据、工具依赖见 `server/docs/review_browser/ACCEPTANCE.md`。
**本交接只重跑架构/来源映射/CSV 核对，没重跑全部 H/I/J 浏览器链。**
复核 API/网页持续保持只读，不能复用其接口做账号服务、GM 写操作或游戏网关。

---

## 18. 长期服务端路线：设计已纳入，运行实现尚未开始

必须先读：

- [`server/docs/GATEWAY.md`](../../server/docs/GATEWAY.md)
- [`server/docs/GATEWAY_SECURITY_GM.md`](../../server/docs/GATEWAY_SECURITY_GM.md)
- [`server/docs/INTERFACES.md`](../../server/docs/INTERFACES.md)
- [`server/docs/OWNERSHIP.md`](../../server/docs/OWNERSHIP.md)
- [`server/docs/BATTLE.md`](../../server/docs/BATTLE.md)

### 18.1 架构边界

- 第一版 Python 同进程模块化网关，未来可分离；不是一开始堆微服务。
- transport 管帧、连接、长度/速率、有界发送队列；不管伤害或资产。
- protocol 管白名单和客户端字段映射，不允许客户端指定 Python 模块/函数。
- runtime 管可信会话、连接代数、状态拥有者与路由。
- application/domain 通过类型化端口工作，不持有 socket/StreamWriter，不直接导入接入实现。
- PostgreSQL 事务、幂等、唯一约束等必须真实实现；不能让一个 socket 会话持有长事务。
- 跨模块只走 contracts，不跨目录写对方私有仓储。
- 数据库迁移链、公共 DTO、依赖清单、bootstrap 由指定负责人整合，防止多人互相覆盖。

### 18.2 第一条真实切片建议验收次序（计划，不是已实现）

1. 明确客户端协议接入与现代/legacy 适配边界，禁止先接旧运营接口。
2. 账号注册与安全凭据存储、统一账号标识、错误/限流/幂等契约。
3. 网关接入、认证前白名单、票据用途/期限/撤销与会话归属。
4. 区服选择及区服绑定身份。
5. 登录、会话接管/重连语义。
6. 创角事务、账号-区服-角色归属和唯一性。
7. 最小地图实例与角色状态拥有者、进入/退出/恢复。
8. 针对重复请求、断连、越权、队列满、持久化失败的真实端到端测试。

上述项目尚未交付，不能给用户一个不存在的游戏服务启动命令。
生产 Python 版本和依赖仍需基础设施负责人统一锁定，不把离线编译器 Python 2.5 当服务端版本。

### 18.3 网关安全与 GM

- 公网玩家入口、私有 GM 管理入口、内部服务入口隔离。
- GM 默认关闭，私有网络接入、应用身份/MFA/权限/审批/审计均需真正实现。
- GM 不接受玩家票据、不信任客户端自报 `source=admin`，不提供通用 SQL/shell/任意脚本。
- 管理写操作经 administration 与业务端口，不直接改线上实体或数据库表。
- 应用网关不可能独自抵抗超过链路带宽的 DDoS；上游防护、资源预算与压测另行建设。
- 当前安全与 GM 均是设计，不是已上线防护能力；不要承诺能防全部外挂或攻击。

---

## 19. 快速禁止清单：已踩过的坑不要再踩

- 不再分发失败 v3 当有效预览。
- 不再把未实现的“点击加载方案”用 v3.1 包冒充交付。
- 不默认常量 0 是 None，必须按实际常量值查找。
- 不把 CClickBox 的 color/alpha 当 x/y；不让 fake 接口靠猜。
- 不在旧登录 PNG/按钮上只叠新文字，忽略整个旧控件背景。
- 不因没有看到光标就加第二套定时器，先看原生 Active/Flash。
- 不让首页标题依赖注册模块 import。
- 不先隐藏当前页再创建目标页。
- 不把 `login/service.dlg` 误认成选服页面。
- 不把登录控制器一起复用到新注册表单。
- 不恢复 reg2/2980 老外观作为默认新方案。
- 不把 90/22 或 161 项通过写成原生/玩法通过。
- 不把已缺失的附件、artifacts、编译器路径说成必然可用。
- 不向用户索取真实邮箱、密码、票据；只用 `preview@example.invalid` / `Preview123` 等假数据。
- 不用简繁转换掩盖数据提取损坏，不用默认零补缺失，不擅自交换异常资质值。
- 不执行完整恢复游戏脚本，不重建敏感 entry 1288 dump。
- 不因为文件显示 untracked 就删除 server/tools；先核对快照与远程内容。
- 不把大 ZIP/FLS、node_modules、构建编译器或浏览器缓存入 Git。
- 不额外发送 Gmail、开放 Drive 权限、删除用户旧文件或合入 master。

---

## 20. 给下一位 Agent 的完整启动提示（可整块复制）

```text
你接手 a565551313/MXSJ_TW_2022 项目，请先阅读根目录 AGENT_HANDOFF.md，
再阅读 tools/client_patches/REGISTRATION_CONTROL_FIX_V3_3.md 和相关源码/测试。
业务代码当前基线是 2b913f5；交接文档提交在其后。先核对实际 git status、分支、最新提交，
不要直接重置、删除 untracked 目录或覆盖用户变更。遵守你所在会话的分支约束。

当前优先任务不是重写服务端，而是完成注册 UI v3.3 的 Windows 原生复测闭环。
v3.3 已上传：
https://drive.google.com/file/d/11M9rwP36u0-KLP9WaO3YGjNRbGmvf4Rc/view?usp=drivesdk
FLS SHA256 为 6ef84a13c23ca0abfaa7a9febf8ba49b4df569a9cf65286c4b1844f9df63cddb。
截至交接尚未收到 v3.3 用户反馈；不要宣称已通过原生验收，不要无变化重复上传。

用户给的是 v3.2 截图，报告：协议按钮无字、说明入口左上角黑块、注册与登录叠字、
上一步旧箭头、输入框无光标闪烁。v3.3 已按真实 CClickBox color/alpha 接口改定位，
完整隐藏禁用旧按钮并换金色带字 PNG，输入框显式设置深色光标和 Z，保留原生 Active/Flash/Tab。
必须同时安装 FLS 与 8 张 PNG；四张按钮图已改，目录仍叫 photo/registration_preview_v3。

当前 90 项客户端补丁测试、22 项 CPython 2.5 审计通过。
审计运行自写片段及精选原始控件方法，底层渲染、鼠标和调度器仍为替身，不等于 Windows 运行。
交接复查另有 161 项架构、96/96 来源文件名、22 个待审 CSV 文件通过，不是玩法实现证据。

保持首页标题独立，消息 2 点击时才 import register，目标成功才隐藏当前页。
协议用 login/service.dlg；表单只用 login_new/newlogin_800.dlg 布局，不能运行原登录控制器。
仅改337/4007，原选区后条款/登录4806与其他5000条保持不变；源 FLS/key DB 不覆盖。
保留三字段必填/邮箱/密码6–16/一致性校验，Info 直接“離線預覽，未送出。”；
无真实提交、验证码、账号保存或假成功。只用测试副本与假数据。

收到反馈后先按原档接口自查和复现，新增能复现旧问题的测试，再改源码/冻结资产，
检查后再打包上传 Drive。不能先上传未改完的包，不要只让用户盲试。
用户要 Drive 链接，不要 Gmail或自动公开分享。无授权不合入master或发布生产game_data。

长期目标是 Python/asyncio/PostgreSQL 的注册→选区→登录→创角→进图，第一条真实链路就含网关。
网关、安全、私有GM已有设计但没有运行实现。H/I/J只读数据复核工具已收尾，不能拿它当游戏网关。
不要重做已完成的静态数据分析或把待审CSV当正式服务端规则。
先汇报你核对到的实际状态和下一步；有不确定就分清已确认事实与待验证假设，再开展工作。
```

---

## 21. 交接完成的定义

- 本文及复查摘要入库。
- 明确 v3.3 尚未原生验收，没有把待办写成完成。
- 给出精确链接、哈希、源码基线、构建/审计/安装/恢复命令。
- 新 Agent 能定位真实接口、历史错误和独立证据，不依赖上一会话的临时缓存。
- 保留长期设计与数据工作边界，避免重做已完成事项或越权推进生产发布。
- 文档提交推送到当前工作分支；**不创建新 UI 交付，不改变产品代码，不合入 master**。
