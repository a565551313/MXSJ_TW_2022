# 注册预览 v3.2：点击时才加载新界面

2026-10-12。落实用户“直接指向新界面”的方案，而非仅交付启动保护候选。
**v3 停用；提前上传的 v3.1 不符合本轮入口拆分要求，不作为本轮交付。**
本版仍是离线测试候选，尚无 Windows 原生验收，不能承诺已消除所有黑屏原因。

## 实际改动

- `mainpage.CMainPage.__init__`：移除原可选 `tg.id` 块及 v3.1 的注册模块调用。
  首页标题代码内联在 mainpage 中，只使用本来已有的 `ui`，无任何 import，
  不调用 `register.GetData`，不初始化注册面板。按消息 ID 2 唯一定位按钮，加载
  `home_register.png` 后才清除旧文字。资源或控件异常时保留旧文字并打印 `NOT installed`。
  注册模块自身即使无法导入，也不是该标题路径的依赖。
- `mainpage.CMainPage.OnMessage`：只有消息 ID 2 的动作块才执行
  `import register; register.Show(True)`。原地区判断、旧注册网页地址分支在此块中被移除，
  不只是保留不可达旧分支。导入/构造 Python 异常会记录 `cannot open registration` 并返回，
  不隐藏首页。成功后再隐藏首页，保留原按钮音效。
- 新入口调用已替换的注册协议类，协议用 `login/service.dlg`；同意进入仅使用
  `login_new/newlogin_800.dlg` 布局的新表单。拒绝返回首页。没有加载登录控制器业务。
  原选区后条款/登录 entry 4806 字节不变。
- 延用 v3.1 的 EXEC 真正 None 操作数修复、先构造目标再隐藏当前页；
  延用 v2.2 三字段本地校验与 Info 直接提示，不发送注册资料、不保存账号或模拟成功。
- 注册 overlay 中旧 `GetData` 标题辅助函数保留兼容，但首页已不再调用它。
  本轮不声称整个客户端不存在其他模块导入或联网路径。

## 封装与范围

仅修改 entry 337 / 4007，其他 5000 个目录记录和压缩载荷完全一致。
源 `data/script.fls`、密钥数据库、master、生产游戏数据均未更改。

新增 `home_registration_entry.py` 为独立编写的 Python 2.5 代码，冻结为
`visual_assets/home_entry.py25`，编译器版本/源码/产物哈希写入 manifest。
构建时只读取冻结对象并映射 opcode，不执行恢复的游戏源码。

337 现在也重建 intern 表；两个方法内联片段后显式重定位所有保留指令的跳转目标和
常量/名称/局部变量操作数，拒绝跳入被替换区域内部的旧跳转。其他方法逐项语义对比。
两个修改方法的过期行号偏移表清空，避免误导调试定位。旧可选 `tg.id` 推广标识不再显示。
新增真实尾部填充常量，337 仍为 10,335 字节（填充 329），4007 仍为 44,362 字节。
两个条目的原 XOR keys、bounds、长度均保持，独立解密和完整 marshal 解析通过。
**337 的重新序列化同样需要原生加载器验证，不把 CPython 检查等同于游戏启动成功。**

## 本轮检查

- 85 项客户端补丁单元测试通过。
- 17 项独立 CPython 2.5.6 执行审计通过，记录见 `V3_2_RUNTIME_AUDIT.json`。
- 从本轮实际生成 FLS 中提取内联代码，反映射为标准 opcode 后执行；不是只测试源代码副本。
- 首页标题：正常、图片缺失、空尺寸、按钮歧义、非文字控件五种路径，禁用所有 import
  的测试仍通过，重复创建首页不导入注册模块。
- 点击：正常、导入失败、实际旧 EXEC 错误、构造失败四种路径；只在点击时触发 import，
  失败时不隐藏首页，成功先注册页后首页隐藏，重复进入仍有效。
- 逐条核对两个方法未替换区域的指令含义、操作数与跳转目的地；消息 2 的真假分支检查通过。
- 两个完整条目均由独立 CPython 2.5 marshal reader 解析，但**不执行整个恢复游戏模块**。
  UI 控件、导入器和引擎边界是假对象，不验证真实 DLG 渲染、原生图片解码、层级或点击。
- 旧错误回归使用此前从历史提交重建、FLS 哈希与失败 v3 一致的审计 ZIP，
  并非重新拿到原完整交付 ZIP；审计强制检查失败 FLS 的已知 SHA。

本版 FLS：24,555,986 字节，SHA-256：
`51187b3806497cab206cf2581cbcd2dbb0fe8ec4be4928a9bad41aebf2e105f3`。
八张 PNG 内容不变，仍使用 `photo/registration_preview_v3/` 命名空间。

## 重建

```bash
# 普通构建只需冻结文件，不依赖 Python 2.5/Pillow。
python3 tools/client_patches/build_visual_preview.py --allow-unverified-candidate \
  --output-dir /home/user/artifacts/NEW_V3_2_DIRECTORY
python3 -m unittest discover -s tools/client_patches -v

# 仅更新代码，不重绘 PNG；必须是 CPython 2.5.6。
python3 tools/client_patches/prepare_visual_assets.py --code-only --python25 /path/to/python2.5
python3 tools/client_patches/audit_visual_runtime.py --python25 /path/to/python2.5 \
  --report /home/user/artifacts/V3_2_RUNTIME_AUDIT.json
```

## 安装、验收、回退

只用完整测试客户端副本，关闭游戏和更新器，备份当前 FLS。
同时复制 ZIP 中 `data/script.fls` 和 `photo/registration_preview_v3/` 的 8 张图片，
只合并这一图片子目录，不替换或删除整个 photo。旧 v3/v3.1 FLS 不与本包混用。

顺序检查：首页「注册账号」→新协议→新表单；同意/拒绝/上一步；再次进入；
三个必填字段、邮箱最长 32/格式、密码 6–16/一致；Info 不读字段直接提示。
测试数据仅用 `preview@example.invalid` / `Preview123`，无实际注册服务。
原选区流程仍需原生回归；布局仅针对 800×600。

若黑屏、闪退、卡住或无响应，停止并恢复原包或用户此前确认可用的 v2.1 FLS，
保留本次日志（回传前遮掉账号/票据）。Python 异常保护无法覆盖原生崩溃或卡住。
本补丁不做全客户端网络隔离，建议断网检查界面，不要求关闭安全软件。
