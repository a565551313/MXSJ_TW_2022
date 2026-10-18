# 原生客户端文本格式：已实现子集与待确认事项

日期：2026-10-18。证据来自仓库本地文件与反编译候选，**未完成原始字节码逐分支核验或 Windows 原生客户端验收**。
不执行反编译游戏脚本；本文不是对远端现存内容或官方完整协议的断言。

## 已实现：三个文本资源

HTTP GET／HEAD 路径为 `/news.txt`、`/service.txt`、`/server.txt`，正文直接提供文件字节，Content-Type 为 text/plain，不附加 UTF-8 charset。
生成器以 UTF-8 JSON 为操作员输入，严格编码为 Big5，无 BOM，统一 CRLF 换行；不可编码字符报错，不忽略或替换。
本地原始样本是 LF，候选代码部分分支按 CRLF 切行，故采用 CRLF 作为待验收输出策略，不声称唯一合法换行。

### 公告与客服公告

- `news`：纯文本段落；不包 JSON，不添加 HTML。
- `service`：纯文本，可保留样本中的 `#Y客服公告`；不解释／发明其他富文本标记。
- 证据：`tools/decompiler/output/script_fls/script/login/mainpage.py` 的 `refreshbulletin`、`refreshService`。
  候选代码找 HTTP 头结束位置，分别将正文以 wb 写入 news.txt/service.txt。本地同名文件可按 Big5 解码。

### 基础区服列表

```text
測試區
本地測試服 127.0.0.1 3134 3 &
```

单 token 行为分组名；其后按空白分隔的五字段行为 `name ip port reserve type`。
证据：`tools/decompiler/output/script_fls/script/login/selectserver.py` 的 `Refresh`、`ServerInfo`、`GetServerInfo`。
候选 Refresh 从 update.ini 读取 ServerList，经 HTTP 请求后将正文写入 server.ini。
解析候选将第 3 项转整数，第 4/5 项保留为 reserve/type；生成器不解释这两个字段。
示例的 `3` 和 `&` 沿用已有样本，不宣称表示区服编号、在线状态或任何其他含义。

输入模式：`groups: [{name, servers: [{name, ip, port, reserve, type}]}]`。
生成器只接受 IPv4、端口 1..65535，名称及不透明字段禁止空白／控制字符和分段标记；不生成附加段。
这是工程侧的有限输入约束，不是已证明官方只支持 IPv4 或仅支持这些名字。
示例地址为 127.0.0.1，仅供同机测试，不表示 TCP 服务已经启动；远程部署须填写玩家可达网关地址。

## 未知／待复核：禁止补造

| 项目 | 现有线索 | 后续需要的证据 | 当前处理 |
|---|---|---|---|
| reserve/type 语义 | 字段赋值及样本 `3 &` | 沿消费者与原始字节码核验 | 原样输出显式配置，不增加解释 |
| 可选 serverid | 候选代码出现第六字段转整数 | 后续使用、唯一性及省略影响 | 生成器不开放，传入报错 |
| 等号分段、推荐记录、别名、代理列表 | 本地样本与解析候选 | 完整分段规则、索引、必要性、界面行为 | 不生成，基础列表可能不足以驱动全部界面 |
| 地址是否接受域名／IPv6 | 字段名为 ip；存在地址拆分路径 | 连接调用链及客户端测试 | 生成器只接受 IPv4 |
| servernotice.txt | update.ini 的 ServerNotice | 请求入口、内容样本、解析代码 | 未配置，404 |
| httpupdate.txt | update.ini 的 UpdateURL | 启动器清单解析、版本比较、路径／校验字段 | 未配置，404；不假报最新 |
| filemd5.txt | FileInfoURL 与历史研究 | 完整行格式、编码、路径规范和错误行为 | 未配置，404 |
| 更新包封装 | 启动器、mxupd.exe、ResLib.dll | 下载→解包／差分→替换链路及真实测试包 | 不生成／不执行补丁 |
| MiniPage 网页 | 配置及 WebBrowser 控件研究 | 页面契约、旧浏览器能力和信任限制 | 不制作伪兼容页面 |
| HTTP 兼容 | CHttpObject 候选返回含响应头数据 | net.py／原生 HTTP 实现的 chunked、gzip、304、重定向与 TLS 行为 | 通用 WSGI 功能不算原生验收；代理勿擅自启用压缩／改写 |
| nocheck 行为 | Refresh 候选存在提前返回 | 原始字节码与实际刷新测试 | 联调须检查；本服务不修改该文件 |
| 历史官方 URL 存活 | update.ini 的域名／路径 | 可访问环境只读 GET，记录响应头与原始字节 | 本轮未探测，不报告已失效或仍可用 |

更新研究优先查 mxLauncher.exe、patch/mxupd.exe、ResLib.dll 的配置读取／清单解析／下载／替换调用链。
`patch/mx.bin` 的启动器自更新材料不能当通用资源包格式；FLS 容器格式也不能直接当补丁封装。

## 验收与发布边界

单元测试验证生成字节、严格 Big5、CRLF、输入拒绝、HTTP 实际应用返回体和未知路径 404，不证明游戏 UI 已接受。
生成器只能输出到全新的目录，不覆写已有发布或客户端目录；输出内容验证完后再由操作员切换服务配置。
运行目录需可信、无并发恶意写入。正式发布须先有完整文件、再切换清单；多副本切换及原生更新信任链仍未实现。
不自动修改客户端 update.ini/server.ini，不访问官方服务，不迁入 Mock 的免认证或加密绕过。
