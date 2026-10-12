# 注册预览 v3.3：按钮、说明入口与光标修正

2026-10-12。用户的 v3.2 截图已显示新协议和新表单，说明该次运行能进入这些页面；
但协议按钮无文字，说明入口在左上角有黑底，注册按钮与旧“登录游戏”叠字，返回仍为旧箭头。
随后用户补充输入框无光标闪烁。不能将 v3.2 标为完整原生验收通过。

## 自查依据与改动

1. **确定的接口错误**：原 entry 3854 的 `CClickBox.__init__` 实参顺序是
   `(self, parent, w, h, color, alpha, msgid)`，不是旧测试替身假设的 x/y。
   旧调用 `(self,200,28,300,394,3)` 实际设置 color=300、alpha=394，位置仍为 (0,0)。
   本轮执行原始构造函数字节码（底层 C++ 原语替身）复现该参数错误。
   新调用颜色/透明度均 0，另用 `SetPos(300,394)` 定位说明入口。
   已修正 Python 3 测试替身，并直接核对其参数名与原档一致。
2. **不再给旧登录/箭头换字**：完整隐藏并禁用原消息 1/2 控件，创建独立透明点击框，
   配完整金色按钮 PNG（背景和简体文字同图），避免旧资源上的文字/箭头继续存在。
   协议两按钮按旧按钮中心定位；表单两个按钮为 (270,468)/(430,468)，统一 112×34。
   协议同意/拒绝与表单上一步/注册消息分别仍为 1/2。
   这是完整新按钮底图，不是声称已提取或复刻原生金色按钮资源的每个状态。
3. **显式层级**：原生 `CTextButton.SetTextPos` 会给文字 `SetZ(1)`，
   `CButton.SetPath` 给背景 `SetZ(-1)`；v3.2 自加标题未明确前景层。
   新图片明确 Z=1，新点击框 Z=2；首页仍独立设置标题，仅加前景 Z，不引入注册模块依赖。
   截图不能证明协议按钮无字只有这一个根因；本轮直接消除对旧按钮文字层的依赖。
4. **光标保留原生逻辑**：原 `CEdit.Active(True)` 已创建间隔 20 的 Flash 命令，
   Flash 在当前焦点控件上切换光标显示；`MsgTab` 对下个输入框调用 Active(True)。
   不新增竞争定时器、不替换全局焦点机制。三框显式传入深色 `linecolor=0x805B45`，
   输入框 Z=2 高于表单底图 Z=1，框内光标 Z=1；保留邮箱初始焦点、密码遮罩及循环 Tab。
   **尚无 Windows 日志确认光标缺失的唯一原因**，颜色/层级是针对本次显示问题的修正，
   不把假调度器跑通等同于 Windows 鼠标派发、计时与绘制已通过。

## 测试证据与边界

- **90 项**客户端补丁单元测试通过。
- **22 项** CPython 2.5.6 执行审计通过，见 `V3_3_RUNTIME_AUDIT.json`。
- 执行本轮 FLS 中提取的自写 overlay/首页片段；另选取原 entry 3854 的
  CClickBox 构造器与 CEdit 构造器、Active（含 Flash）、MsgTab、SetNextEdit、GetLineColor、IsActived。
  这些控件方法来自原始代码对象，不是重写的行为模型；不执行整个恢复模块。
- 图形原语、系统输入、Shadow 包装和调度器边界仍为替身。
  三框各自经过显示→隐藏→显示→Tab 转移，确认新焦点、旧光标隐藏与命令释放，以及末框回到邮箱。
  也检查 Active(False) 停止旧光标命令；不声称运行真实 OS 点击事件或真实时钟。
- 完整隐藏旧控件、透明度/坐标、消息分流、图片尺寸、前景层级及继承本地校验通过。
- 旧 v3 EXEC 参数错误回归本轮采用已知错误操作数组合，不是重新下载旧 ZIP。
- 两个完整条目可由独立 CPython 2.5 marshal reader 解析；源 FLS/密钥库不变。

仍只改变 337/4007；其他 5000 条字节相同，原选区后的条款/登录 entry 4806 未改。
不改变 v3.2 点击加载、不运行登录控制器、不提交注册、不保存凭据、不模拟成功。
本轮未验证 Windows 引擎、PNG 渲染/命中区/裁剪、鼠标焦点和实际光标闪烁。

## 复现和安装

```bash
python3 tools/client_patches/build_visual_preview.py --allow-unverified-candidate \
  --output-dir /home/user/artifacts/NEW_V3_3_DIRECTORY
python3 -m unittest discover -s tools/client_patches -v
python3 tools/client_patches/audit_visual_runtime.py --python25 /path/to/cpython-2.5.6/python \
  --report /home/user/artifacts/V3_3_RUNTIME_AUDIT.json
# 冻结代码/重绘图片：Python 3 + Pillow，以及 CPython 2.5.6
python3 tools/client_patches/prepare_visual_assets.py --python25 /path/to/cpython-2.5.6/python
```

生成的 24 MB FLS/ZIP 在仓库外，不提交二进制大包。小型冻结代码/PNG 与 manifest 入库可复现。
此次四张按钮图片已更新，**必须同时安装 FLS 和完整 8 张 PNG**；沿用目录
`photo/registration_preview_v3`，不能以“目录没改”为由沿用旧图。
只合并这一子目录，不替换/删除整个 photo；只用完整测试副本，退出游戏/更新器并备份 FLS。

验收顺序：协议两个金色按钮均有字→同意进入表单→无左上角黑块→两按钮无叠字/箭头→
逐框鼠标点击后观察光标闪烁→连续 Tab 绕回邮箱→密码遮罩→Info 空表单直接提示→
注册按钮本地校验→上一步/拒绝/再次进入。全部用假数据。
原生异常停止测试并恢复已知可用备份；原包或先前确认可用的 v2.1 可回退。
本包仍是离线测试候选，不是全客户端断网沙箱，也不是正式账号服务。
