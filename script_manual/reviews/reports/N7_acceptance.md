# N7_acceptance · 合并态集成验收六题

> 审核会话：**N7 新会话**（Arena 2026-10-16 分配的第 7 个新 agent，逻辑任务包 H / review）。
> 不是旧 H、不是 A；不代写作者正文。
> 每题分三层写：**证据**（本会话独立恢复的候选原行）/ **结论** / **未知**。
> 全部结论只来自**静态候选文本**，不由游戏截图、控件命名或模块职责推断。

## 0. 证据来源

本会话在仓库外用 Python 3.11.2 + uncompyle6 3.9.3 / xdis 6.1.8 / spark-parser 1.9.0 / click 8.5.0
独立恢复相关条目（行号为**含 6 行恢复头**的候选文件行号）：

| entry | 路径 | 行数 |
|---:|---|---:|
| 337 | `script/login/mainpage.py` | 338 |
| 4293 | `script/main.py` | 1579 |
| 4007 | `script/login/register.py` | 1311 |
| 4806 | `script/login/loginin.py` | 1442 |

另复用本会话恢复的 219 / 3854 / 3232 / 4832 / 3176 / 2170 / 871 / 516（见各模块 review）。

> 反编译产物**不是原始源码**；`decompile_ok` 只说明输出形状，不证明语义、可逆或可回编。
> 本文件所有“证据”都受此限制约束。

---

## 1. 公告失败出处

**证据**（`mainpage.py`，entry 337）

- L266 `def refreshbulletin(data, succeed):`
- **失败分支 ①**：L268-L270 `if not succeed:` → `commondialog.ShowMessageBox('刷新公告失敗', '確定')` → `return`
- **失败分支 ②**：L272-L274 `idx = data.find('\r\n\r\n')` → `if idx == -1:` → 同一个 `ShowMessageBox('刷新公告失敗', '確定')` → `return`
- 触发方：L232 `elif msgid == 30:`（OnMessage 的 30 号）；L234-L239 有 **180 秒节流**（`t - g_RefreshTim < 180` 时 `usermacro.PROMPT_MSG('請稍後再刷新')` 并 return）；L248 `httpobj = net.CHttpObject(web, 'get', refreshbulletin)`

**结论**：公告失败弹窗**只有一个函数 `refreshbulletin`，但有两个并列失败点**——HTTP `succeed` 为假，或响应体缺 `\r\n\r\n` 头/体分隔符。两者都弹同一句“刷新公告失敗”。

**未知 / 与现有正文的差异**

- `login/main.json` 的问答把两处合并表述为“HTTP失败或缺少头分隔符时弹”，方向正确，但**未给出 L268 与 L272 两个并列分支的行号**，读者无法区分是哪一种失败。建议补两条行段。
- A 的 C 预审已指出公告问答缺 `OnMessage(30)`（本会话实测为 **L232-L249**）；这一项是**地址选择所在处**，也**是节流所在处**，缺它就无法解释“点了刷新却没反应”。
- `succeed` 由引擎 `CHttpObject` 传入，其真值语义、超时与错误码**未核**；`CHttpObject` 的 `method` 参数未用（net.json 已保留该疑点）。
- 未请求任何公告 URL，未做网络实测。

---

## 2. 正文 / 地址 / 布局

**证据**（`mainpage.py`，entry 337）

| 层 | 位置 |
|---|---|
| **正文** | L279-L281 `f = open('news.txt', 'wb'); f.write(body); f.close()`（写入）；L159 `f = open('news.txt', 'r')`（读取）；L283 异常时回退 `g_News = body.split('\r\n')` |
| **地址** | L242 `if main.g_LangVersion == 0:` → L243 `web = cfg.GetData('update.ini', 'Setting', 'News')`；否则 L246 `web = cfg.GetData('update.ini', 'HK', 'News')`（另有 `Service` 同构，L244 / L247） |
| **节流时间戳** | L286 `cfg.SaveData('mx.ini', 'Game', 'refreshnews', '%f' % misc.Time())`；L316 读取同一键做 180s 判断 |
| **布局** | `login/mainpage.dlg`（见 `mainpage.json` 的 `resources`；本会话未读取该 `.dlg` payload） |

**结论**：正文是本地 **`news.txt`**（写成功才落盘，异常时只进内存 `g_News`）；地址来自 **`update.ini`**，且按 **`main.g_LangVersion == 0`** 在 `[Setting]` 与 `[HK]` 两个节之间二选一；布局是 **`login/mainpage.dlg`**。

**未知**

- **`.dlg` payload 未读取**，布局内的控件名/层级未逐项核对（红线：不读布局/图片 payload）。
- `main.g_LangVersion == 0` 的实际取值来源与“TW/HK”的对应关系**未核**——C 预审已明确要求不得把 `g_LangVersion` 直接附会成 TW/HK 映射，本会话维持该要求。
- `news.txt` 的编码未核；结合 `notes/title_and_chat_encoding.md` 的既有结论，中文正文的解释依赖系统 ANSI 代码页，**不能凭此判定文件损坏**。

---

## 3. 登录点击链

**证据**（`loginin.py`，entry 4806）

- L580 `def OnMessage(self, msgid):` → L582 `if msgid == 2:` → L583 `if not misc.IsTWServer():` → L584-L588 取 `chk_agree`，未选中则 `ShowMessageBox('請勾選「我同意多益通用戶協議」…')` 并 `return` → L589 `LoginOk()`
- L252 `def LoginOk():` → L269 `netlogin.C2SLoginIn(user, password)`（本函数内**无** `SaveAccount`）
- L663 `def OnLogin():`（另一入口）；`SaveAccount` 有 L509（方法）与 L1416（函数）两处

**结论（并纠正一处现存错误）**

- 协议勾选检查**只发生在 `not misc.IsTWServer()` 之内**（L583），不是全客户端都以勾选为前提。
- **`LoginOk` 不保存账号**；账号保存是 `OnLogin` 链上的 `SaveAccount`。
- 因此**基线** `loginin.json` 中那条“CLoginIn.OnMessage(2)…**LoginOk保存账号**；网络连接由 netserver.RandomConnect 与 netlogin 处理”的问答是**错的**，且与同一文件 `LoginOk` 的 summary、以及 `main.json` 的“账号保存在 OnLogin()”**互相矛盾**。该问题正是 A 的 C 预审第 1、2 项；**PR#39（N2）已修正**（改为“本函数不保存账号”“OnLogin 是另一个入口，LoginIn 存在才 SaveAccount”“仅 OneoffLogin/OneoffLogin2 内调用 RandomConnect，普通 LoginOk 提交到 netlogin.C2SLoginIn，不能拼成一个先后链”），本会话已核对 PR#39 文本与候选 L252-L269、L583-L589 一致。

**未知**

- `C2SLoginIn` 之后的**服务端往返**、失败回调 `LoginInErr` 的触发路径、`OnLogin` 由谁调用，**未在本会话恢复的四个条目内闭环**，不能把“点击 → 提交 → 保存账号”串成已确认成功链。
- 未做实机点击、未登陆真实服。

---

## 4. 注册逻辑 / 布局

**证据**：`register.py`（entry 4007，1311 行）已由本会话独立恢复成功（recovered/source/baseline/decompile_ok），但本轮**未对注册流程逐函数展开核对**。

**结论**：**本轮不给出注册链的验收结论。** 已核对的只有与登录链交叉的部分（注册入口在 `mainpage.OnMessage(2)`，见 `mainpage.json`；非 TW 时 `register.Show(True)`）。

**未知 / 阻塞**

- A 的 C 预审第 3 项已指出：注册问答只引 `register` 的 307–543，**无法证明 mainpage 入口或 confirm 布局**。本会话未验证 PR#39 是否已补齐这两段（**属未复核项，不计通过**）。
- 注册表单字段、校验、服务端响应、confirm 布局控件均**未核**。

---

## 5. main 主循环

**证据**（`main.py`，entry 4293）

- L579 `Loop = MainLoop`（模块级初值）
- L573-L576 `def SetMainLoop(): global Loop; Loop = MainLoop`
- L567-L570 `def SetWarLoop(): global Loop; Loop = WarLoop`
- L548-L554 `def WarLoop(mousex, mousey):` → `if not dlgwarrecord.IsWarRecPause(): import war; war.Process(True)` → **`r = MainLoop(mousex, mousey)`** → `return r`
- L557-L564 `def AfterRestart(...)`：`RestartTimes -= 1`，`if RestartTimes == 0: SetMainLoop()` 并按需 `blacklist.StartCheck()`
- L582-L583 `def InWar(): return Loop == WarLoop`
- L425 `def MainLoop(mousex, mousey)`；L497 `def Loop(cls)`；L552 `r = MainLoop(mousex, mousey)`；L560 `SetMainLoop()`

**结论**

- 主循环是**一个模块级可替换的函数指针 `Loop`**，默认 `MainLoop`；战斗时 `SetWarLoop()` 换成 `WarLoop`。
- **关键点：`WarLoop` 内部仍会调用 `MainLoop`**（L552），所以“切战斗循环”是**包装**而非**替换**；`InWar()` 用 `Loop == WarLoop` 判定。
- 重启动结束后由 `AfterRestart` 在 `RestartTimes` 归零时 `SetMainLoop()` 恢复。

**未知 / 与现有正文的差异**

- `battle/netwar.json` 写“S2CWarStart 调用 `main.SetWarLoop()` 将主循环切为战斗循环”“S2CWarEnd 后需恢复非战斗循环”，**方向正确**，但 `netwar.json` 自身也标注了 “S2CWarEnd 片段没有 SetMainLoop，录像分支可能 CloseGame”——**普通分支的恢复落点仍应由 N2 在 `main.py` 正文核对**，不能凭“结束应恢复”推定。
- A 的 BDF 报告已提示：core/war.CCmd 有录像过滤、End 分支正常路径才 `SetMainLoop`、录像可能 `CloseGame`。本会话**未**追完 `S2CWarEnd → 恢复` 的完整链，**该题只给到 `SetMainLoop/SetWarLoop/WarLoop/AfterRestart` 这一层，不给战斗结束恢复的结论**。
- `MainLoop` 内部的逐帧调度、消息泵、渲染调用顺序**未核**；未做实机。

---

## 6. 快捷键

**证据**

- `main.py`（4293）：L801 `def ClearHotKey():`（F1–F8、PageUp/PageDown、Alt+1–7、Alt+S、Alt+,、Alt+. 等）；L981 `def RegisterDefaultHotKey():`（L983 `key.RegisterHotKey(key.VK_CLOSE, ExitGame)`、L984 `VK_ESCAPE → HideWindow`、L985 `VK_ENTER → interface.DefaultButtonClick`）；L1118 `def SwitchHotKey(IsWar, bOldWar=None):`（L1121 `if g_DisableHotKey: return`，L1123 `hotkeys = dlgsysopt.g_HotKeys`）
- `key.py`（3232）：L142 `def RegisterHotKey(keys, func=None, *args)`、L161 `def RegisterHotKeyEx(keys, func=None, *args)`、L188 `def IsHotKey(char)`（只查表不执行）、L204 `def GetCallFunc(char, index)`（取 callback 不运行）

**结论**：快捷键有**两条并行入口**——`main.py` 的 `RegisterDefaultHotKey`（默认键，直接调 `key.RegisterHotKey` 绑定 `main` 内函数）与 `SwitchHotKey`（按战斗/非战斗经 `dlgsysopt.g_HotKeys` 切换）。`key.py` 只提供**登记表与查询**，不决定业务含义。

**未知**

- `RegisterHotKey` 与 `RegisterHotKeyEx` 的差异（是否跳过 SHIFT/CTRL/ALT）已在 `key.json` 记录；**原生事件顺序、线程、物理默认键位未推定**——`key.json` 维持 accepted 时已保留该边界。
- `mainmenu.json` 的 `CMainMenu.OnHotKeyMsg` 与 `main.SwitchHotKey` 之间的**先后与去重关系未核**；菜单 4 号信号→`SS_ClickSkill` 实际委托锻造（`makeequipctrl`）已在 `mainmenu.json` 保留，不能按 “Skill” 名字读成技能面板。
- 未做实机按键验证。

---

## 7. 其他集成闸门（本会话实测）

| 检查 | 命令 | 结果 |
|---|---|---|
| 严格来源 + full 目录 | `PYTHONPATH=script_manual/src python -m mxsj_manual validate --verify-evidence --require-full-inventory --repository .` | 退出 0；`5135/20/3/1` |
| 标准单测 | `PYTHONPATH=script_manual/src QT_QPA_PLATFORM=offscreen python -m unittest discover -s script_manual/tests` | **82 项 = 71 通过 + 11 跳过 + 0 失败** |
| 目录回归（PR#43） | `PYTHONPATH=.:script_manual/src python -m unittest discover -s script_manual/inventory -p 'test_signature_metadata.py'` | 32 项全通过；反向对照旧代码 13 失败 + 16 错误 |
| ruff | `ruff check script_manual script_manual/script_manual.spec` | All checks passed（ruff 0.17.1） |
| Windows 静态 | `python tools/devkit/check_windows_compat.py script_manual --strict` | 121 文件名 / 27 脚本；ERROR 0 WARNING 0 INFO 0 |
| 路径/中文/函数搜索 | 存在 GUI 测试 `test_search_chinese_and_function_and_path`、`test_path_first_list_and_coverage` | **因 PySide6/系统 Qt 缺失跳过，未执行，不计通过** |
| 模块跳转 | GUI 测试 `test_internal_module_link_navigates_by_identity` | **同上，跳过未执行** |
| 审核原字节 stale | `validate` 对正文字节变化会输出 `说明已变化，审核过期` | 已在 PR#40/PR#41 覆盖层实测触发；机制有效 |
| HTML 安全 | 存在 `test_reviews_export`、恶意文本转义用例（标准套件内） | 通过（非 GUI 部分） |
| 全目录体量 | `validate` 的 32MiB / 16MiB / 64MiB 上限 | 通过 |

### 未执行 / 明确跳过（**不得计为通过**）

- **11 项 Qt GUI 测试**：PySide6 / 系统 Qt 库缺失而跳过，包含中文与函数名搜索、按路径列目录与覆盖率、模块跳转、审核身份显示、tab 展示等。这些恰好是“路径/中文/函数搜索、模块跳转”验收点的**主要承载用例**，本轮**未执行**。
- **真实浏览器**：未运行；`jsdom` 亦未在本会话运行（历史由 A 执行，不属本会话结果）。
- **Windows / EXE / 游戏实机 / 原生引擎 / 服务端**：全部未执行。Linux 侧结论不得当作 Windows 或实机可用。
- **离线 HTML 构建**：本会话未生成站点（仓库外产物不入 Git）。
