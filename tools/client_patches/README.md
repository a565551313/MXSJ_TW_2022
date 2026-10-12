# 客户端局部测试补丁：注册流程预览

最新：[v2.2 本地校验预览](REGISTRATION_VALIDATION_PREVIEW_V2_2.md)，58 项离线检查通过，v2.2 原生实测待反馈。
用户已确认 v2.1 资料页、本地提示及返回流程；本轮把下一步校验与说明入口分开。
`--stage form-validate` 生成 v2.2；`form-basic` / `form` / 默认 `terms` 保留历史 v2.1 / v2 / v1。

## v1 第一页预览（历史交付）

2026-10-12。状态：**13 项离线检查通过；用户回传 Windows 注册第一页截图，并确认同意/拒绝均返回首页**。
仅该最小 UI 流程通过用户实测，详见 [验证记录](REGISTRATION_PREVIEW_VALIDATION.md)。
不属于正式注册功能，不是服务端实现，不修改原始客户端包。

## 用途

- 首页「申請會員」点击后，尝试显示现有 `register.Show(True)` 的服务条款第一页。
- 「我同意」和「我拒絕」均返回首页；原关闭动作仍退出游戏。
- 禁用 register.py 中全部 9 个直接 CHttpObject / OpenUrl 调用者，防止继续走旧运营商注册流程。
- 登录页不变，没有新增注册按钮、修改文本、全局切换 TAIWAN 或改变登录协议。
- 用户当前安装已显示第一页的布局/图片；其他安装、后续资料页及完整资源仍未验证。
- 不屏蔽客户端所有联网行为，其他公告/官网/登录功能未修改。测试无需输入任何真实凭据。

## 实现

`build_registration_preview.py` 仅支持精确 SHA-256 的原包与密钥数据库，使用原始 marshal reader，
不执行恢复代码、不运行启发式修复器，不调用现有常量差异“编译”路径。
只在原始自定义字节码中作固定长度替换，保留全部常量、函数元数据、XOR 分段长度与边界：

1. entry 337 / CMainPage.OnMessage：将注册动作内 IsTWServer() 判定的 9 字节改为 False + NOP，
   沿原有 false 分支进入 register.Show(True)，不影响其他按钮的地区判断。
2. entry 4007 / CRegPanel1.OnMessage：同意分支跳到原有返回首页路径，并跳过这一路的旧点击统计。
   保留原有 try/except 块结构，避免改变异常栈。
3. entry 4007 的 9 个直接联网/浏览器调用函数：改为 return None，剩余同长度 co_code 填 NOP。

不重新编译整个历史反编译文件，避免把反编译残缺逻辑或其他条目的边界问题写回客户端。
归档只追加两份新压缩载荷与新目录，更新头部目录指针；原始载荷全部保留。
未改变的 5000 条目录记录和压缩载荷逐字节比较。原始包、源码、密钥数据库都不覆盖。

## 重建与检查

仓库根目录，Python 3.11+ 标准库：

```bash
python3 -m unittest discover -s tools/client_patches -v
python3 tools/client_patches/build_registration_preview.py \
  --output-dir /home/user/artifacts/mxsj-registration-preview-v1
```

输出目录必须位于仓库外且不含已有 `data/script.fls`，否则拒绝覆盖。
生成的 24 MB 测试归档不提交 Git；脚本和回归测试可以重现。

- 原包 SHA-256：`8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72`
- 测试包 SHA-256：`345918e9ac2eef95ea98140fdbb70606a493dc682fce11f4c24ce178d86291eb`
- 测试包大小：24,558,185 bytes。

检查包括输入版本拒绝、空补丁一致性、确定性重建、目录/载荷范围、函数元数据、
指令参数/跳转对齐、原有返回路径、HTTP/browser 调用者全部早退、XOR 边界拒绝与原始文件不变。
这些检查**不代替原生 VM 执行或界面/资源测试**，不能宣称完整脚本解析/游戏功能验证通过。

## 用户测试与恢复

1. 关闭游戏和更新器，复制完整客户端目录作测试安装；不要用仅含 FLS 的补丁目录直接启动游戏。
2. 核对测试安装的原始 `data/script.fls` SHA-256；不匹配时停止，不强行覆盖不同版本。
3. 将原包改名为 `script.fls.before-registration-preview`，放入生成的新 `data/script.fls`。
4. 从测试安装的客户端入口启动；检查首页和「申請會員」，不需登录。可断网测试。
5. 记录第一页截图、同意/拒绝是否返回、报错或闪退日志；若正常，再确认进入选服页仍可返回。
6. 恢复时关闭客户端，移走测试 FLS，将备份改回 `script.fls`，核对原始哈希。

如果更新器覆盖测试包、反编译逻辑对应资源缺失或原生载入失败，保留日志并停止测试。
不要求关闭杀毒/系统保护，不提供任何安全软件绕过步骤。
