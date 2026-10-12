# 注册原生界面预览 v3

2026-10-12。用户要求先提交/推送再制作一版效果；开工前工作区干净，HEAD `998144e`，
已执行 `git push origin arena/b53b33e6-mxsj-tw-2022`，结果 Everything up-to-date。

**68 项离线检查通过。v3 尚未经过 Windows 原生客户端验收。**
不把新生成的控件底图当成实际客户端截图；界面效果、资源加载、字体、遮挡、点击及滚动都待用户验证。

## 已采用的页面方案

- 协议页直接使用 `login/service.dlg`，不是 `login/reg1.dlg`，也不是选服页布局。
  复现当前 CServiceMessageDialog 的 `loc_msg` / COutput 文本与滚动方式；按原始字节码给每行补 `#r`。
  同意进入注册；拒绝返回首页。没有调用原 ShowService/ShowLogin 或原拒绝断线逻辑。
- 注册页只加载 `login_new/newlogin_800.dlg` 的布局/底图，不实例化 CLoginIn，不运行登录、账号记录、计时器或登录请求。
  以浅紫表单面板覆盖中央旧表单，三个输入框独立创建，不依赖 email2 或第三个 DLG 占位控件。
  邮箱 → 密码 → 确认密码循环焦点，密码遮罩。现有原生返回/登录按钮复用点击区，改为上一步/注册账号。
  登录页中的其他有消息 ID 控件隐藏，注册控制器也不会处理它们的联网动作。
- 首页找 `m_Frames` 中唯一 `m_MsgID == 2` 的文本按钮，清除旧文字后挂「注册账号」标题图；
  不猜匿名控件名称，也不改其消息、尺寸或点击区。若不唯一/无 SetText，保留原按钮并记录 NOT installed，不能视为改字成功。
- 新标题、标签和按钮文字是简体中文 PNG，用当前客户端自带 FZLanTingYuan 字体绘制，不走台版字节串解码。
  不复制或发布字体文件。协议正文暂为明确标识的繁体离线预览说明，不是旧运营商条款，也不是正式法律协议。
- 仅以 800×600 为本轮目标；没有承诺其他分辨率、动画背景、全部旧静态装饰或游戏内 UI 已改造。

## 安全/功能边界

继承 v2.2 的实际 CRegPanel2 校验及 OnMessage：注册按钮传 true 验证，说明入口传 false 直接离线提示。
没有新提交接口、验证码、外部浏览器、登录控制器、账号保存或成功模拟。
原选区后条款流程所在 entry 4806 完全未改。
原始模块、其他新闻/资源/登录等功能仍可能联网；这不是全客户端断网沙箱。

## 包装方式变化与风险

旧的定宽补丁不足以容纳新资源路径/构造器。本版保留 v2.2 基线，然后：

1. mainpage entry 337：仅把 CMainPage.__init__ 的可选 tg.id 读取/显示块（426–570）换为
   import register; register.GetData(self)。版本显示、此前首页初始化和末尾返回均保留。
   **预览版不再读取/展示 tg.id 推广标识**，并非无副作用的字符串替换。
2. register entry 4007：删除已禁用的 CRegPanel2_2980 类代码常量，在该槽放置新编译的界面代码对象。
   原模块 488–512 的旧类构造块变为 EXEC_STMT(code, None, None)，在当前模块命名空间执行已编译对象。
   没有动态执行 .py 源文件，没有 execfile/eval/网络代码下载，也不依赖客户端自带编译器。
   覆盖两个页面类；新表单继承原 v2.2 已校验类。保留无害 CRegPanel2_2980 类型供旧 isinstance 检查。
3. 原 register 树的其他函数及常量语义逐项保持；重新生成 intern 表，重排后的 marshal 填充到原 44,362 字节。
   填充是根常量表最后一个真实字符串，不依赖忽略尾部垃圾。原 XOR keys/bounds/总长保持，往返严格一致。
   **这不再是 v2.2 的 marshal 原布局不变方案**；需要原生加载器验证，不能套用旧版成功结论。
4. 除 337/4007 外，其他 5000 个条目的目录记录和压缩内容仍字节相同；源 FLS、密钥库、master/生产数据不变。

## 源码、冻结产物与重建

- `registration_visual_overlay.py`：独立编写的 Python 2.5 界面源码，不是执行恢复代码。
- `visual_assets/overlay.py25`：CPython 2.5.6 编译的标准 opcode marshal，小型可追溯冻结产物。
- `visual_assets/manifest.json`：源码、编译结果、字体输入与八张 PNG 的哈希。
- `prepare_visual_assets.py`：Pillow 绘字与精确版本编译；编译源来自 CPython 官方 v2.5.6 标签。
- `build_visual_preview.py`：标准 opcode 转换为客户端映射、严格语义往返、定长封装与独立输出。

仅从已锁定的原始 FLS 构建，不对用户已修改包做差分：

```bash
# 普通重建只使用冻结产物，不要求本机安装 Python 2.5 或 Pillow。
python3 tools/client_patches/build_visual_preview.py \
  --output-dir /home/user/artifacts/NEW_VISUAL_OUTPUT
python3 -m unittest discover -s tools/client_patches -v

# 修改界面源码/PNG 后，需安装 Pillow 并重新冻结；必须 CPython 2.5.6。
python3 tools/client_patches/prepare_visual_assets.py --python25 /path/to/python2.5
```

本次在 Linux 从官方 CPython v2.5.6 源码构建编译器，只调用 compile/marshal，不运行游戏源码。
构建器检测 manifest 过期时拒绝继续；目标二进制在仓库外，冻结小型界面代码和 PNG 入库以便复现。

## 验证证据

68 项含先前 58 项及 10 项 v3 检查：范围/确定性/总长度、登录模块未改、源码和 PNG 哈希/尺寸、
首页消息 ID 定位与歧义日志、服务页模板/滚动数据、同意/拒绝不登录断线、三输入框/遮罩/焦点、
继承校验和说明分流、原始文件不变。
界面逻辑模型仅执行自写界面源码（转为 Python 3 print 语法），使用假原生控件，不能验证真实 DLG 或图片加载。
编译器生成的每个新代码对象通过 opcode/参数/跳转边界检查，marshal 解析消耗全部载荷并通过语义往返。

- 交付 ZIP SHA-256：`34a69e0a0cd588dbcb95bdf77eef36d78f7f48f436c493ea0fd924b5f37bece6`
- v3 FLS：24,555,836 bytes。
- v3 FLS SHA-256：`b26af0973ac1fb28f0d2b482e2d24a710d682e4ff51b2ec1a586c219a75cc4a2`
- 新 register 载荷仍 44,362 bytes，其中最后常量填充 8,806 bytes。

## 安装/回滚/验收

ZIP 同时含 `data/script.fls` 与 `photo/registration_preview_v3/*.png`，必须一起放入完整测试客户端根目录。
只合并本次命名空间，不覆盖或删除整个 photo 目录，不改原始客户端。关闭客户端/更新器后保留原包和上一版 FLS。
启动先看首页「注册账号」，再看协议页，最后注册页；各发一张截图以检查遮挡/残留装饰。
若首页仍为旧文字，查日志 RegistrationVisualPreview v3: homepage caption NOT installed。
若启动失败/空白/按钮无反应，停止继续并回传本次新 pylog/gamelog，恢复上一版 FLS；移除新增图片子目录即可清理资源。
只用假数据，仍需重新验证本地校验、说明弹窗及回退路径。新协议正文只是界面测试说明。
