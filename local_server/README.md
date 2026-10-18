# 本地测试服：共享服务端业务 + SQLite（第一阶段）

**定位不是另一个宽松 Mock，而是正式服务端的本地开发运行模式。**
账号、角色、会话与事务用例位于 `server/src/mxsj_server/`，本目录只负责启动、配置和本地操作员控制台。
后续 PostgreSQL 也必须复用相同业务服务，不复制第二套玩法代码。

> **当前只能验证账号／会话／角色元数据的基础闭环，还不能用游戏客户端登录进图。**
> 没有 TCP 游戏监听、legacy 认证适配、世界／战斗／任务／资产业务或 PostgreSQL 实现。
> 未实现功能明确拒绝，不伪造成功；原来的 `mock_server.py` 两份文件未移动或改动，也没有被新入口自动调用。

## 已实现与未实现

| 项 | 第一阶段状态 |
|---|---|
| 账号 | 操作员显式建号；scrypt 随机盐；错误密码拒绝；不存在账号不自动注册；原始密码不入库／日志 |
| 会话 | 随机票据，数据库只存摘要；到期校验；同区服登录接管递增 epoch；事务内再次校验旧会话；撤销持久化 |
| 角色 | 按账号／区服查询；名称与外观／门派许可组合校验；名称唯一、数量限制；创角与幂等回执同事务 |
| SQLite | 显式 schema v1 初始化、身份／版本／迁移摘要检查、外键、全同步提交、有界锁等待、异常回滚；不静默重置损坏库 |
| 本地入口 | 自检、初始化、检查、离线建号、交互控制台；无网络端口、无客户端写入 |
| 待迁移 | 真实客户端认证与协议、角色完整初始化／选角进图、世界／移动／任务／奖励等；不能将旧 Mock 的固定票据和免认证照搬 |
| 待实现 | PostgreSQL adapter／迁移、跨进程权威与完整网关限流／背压、封禁与管理权限等；本轮不声称生产可部署 |

## 目录与共享方式

```text
local_server/                          启动配置／操作员 CLI／Windows 构建入口
server/src/mxsj_server/
  bootstrap/local.py                   显式注入 Store、区服、策略、时钟
  modules/account/{domain,application}  凭据规则／建号、认证、撤销
  modules/character/{domain,application}角色规则／创建、查询
  runtime/{sessions,tickets}.py         可信上下文、票据与事务内会话校验
  persistence/ports.py                  存储端口与事务约定（不暴露 SQL）
  persistence/sqlite/                   SQLite 仓储、迁移及提交／回滚
server/tests/local_runtime/            真实临时 SQLite、并发／失败／重启回归
```

不把共享服务复制到本目录。Python 3.11+，SQLite 3.24+；运行仅需标准库。无需 PySide6、游戏资源、旧 Python VM、PostgreSQL 或复核网页依赖。

## 启动步骤（从仓库根）

1. 复制 `local_server/config.example.json` 为 `local_server/config.json`。
   配置和 `var/` 已忽略。相对数据库路径按**配置文件所在目录**解析，不按当前工作目录。
2. 自检后显式初始化，再由操作员建一个假测试账号：

```bash
python local_server/bootstrap.py --check-only
python local_server/run.py --config local_server/config.json init-db
python local_server/run.py --config local_server/config.json check
python local_server/run.py --config local_server/config.json provision --account player_one
python local_server/run.py --config local_server/config.json console
```

建号会交互询问并确认密码（12–128 UTF-8 字节，不回显）；不要用真实账号密码。
不提供明文密码命令行参数，也拒绝非交互标准输入传密码。建号是可信本机操作员操作，**不是玩家注册接口**。
初始化只创建指定数据库目录／文件，不自动导入旧 `mock_accounts.json`，不读写游戏 FLS／INI／nocheck。
已有无关数据库、未知版本或损坏文件拒绝操作，不以“修复”为由清库。
新文件在 POSIX 请求 0600，目录请求 0700；Windows 请使用当前用户私有目录／ACL，不能把 SQLite 文件放共享网络盘或公开目录。

控制台示例（密码在提示时输入）：

```text
login player_one
list
create HeroOne 111 1 create-001
create HeroOne 111 1 create-001
logout
quit
```

第二次相同 `create-001` 返回原角色，不重复创建；同键不同参数返回冲突。票据只保留在内存，不输出。
正常退出尝试撤销；强制终止时会话按有效期／下次登录接管失效，不承诺进程被杀时执行清理。
重启后账号、角色、幂等回执与会话代数仍在 SQLite 中。

Windows 也可在准备配置／建号后双击 `启动本地测试服.bat`，进入的是**操作员控制台，不是可进图服务**。
不自动下载依赖或改系统设置。`bootstrap.py` 异常日志只写异常类型，避免记录凭据。

## 规则不是“本地放宽版”

- 业务层不分 local／production 分支；只有装配选择持久化适配器。
- 当前创角策略示例只允许 `(appearance=111, school=1)`、最多 3 角色；名称需 2–12 字符且可无损装入 16 Big5 字节，初始元数据 level=1/revision=1。
  **这是显式工程测试策略，不是已恢复的完整官方创角／成长规则**；尚无背包、技能和资产初始化，后续按独立证据完善共同规则，不能在 SQLite 版中假装完成。
- `operator-utf8-v1` 仅标识本机凭据输入；旧客户端的凭据格式不得冒充原始 UTF-8 密码。legacy 认证策略尚未实现，当前直接拒绝。
- `RequestContext` 必须由可信 SessionAuthority 产生，不允许网络层反序列化客户端自报的账号、角色、source、epoch。
- 入队前验证不够：创角事务内再次校验会话、区服、到期与 epoch；同区服接管后的旧请求不能继续写。
- `source=ADMIN` 不绕过权限。当前只实现本人撤销，不提供网络 GM、SQL/shell 或任意脚本执行。
- 进图接口检查归属后返回 `NOT_IMPLEMENTED`；不知道的规则不默认通过。

## SQLite 与 PostgreSQL 的边界

SQLite 单事务连接使用 `BEGIN IMMEDIATE` 串行化写入（此阶段读用例也经同一事务端口），外键开启、`synchronous=FULL`，不是性能方案。
角色写入与幂等回执一起提交；提交失败不返回业务成功。锁超时返回 `TEMPORARILY_UNAVAILABLE`，重试使用同一 operation_id。
异步入口将阻塞 IO／哈希交给 worker；协程取消不保证线程／事务已取消，结果未知时必须按同一幂等键查询／重试，不能换键重做。

未来 PostgreSQL 适配器须在**不改变业务服务**的前提下实现显式行锁、唯一约束、隔离级别、会话 fencing 和相同事务结果，并复跑相同用例及 PostgreSQL 专属并发测试。
当前不提供 PostgreSQL 配置假入口，也不宣称只改连接串就能部署正式服。SQLite 通过不等于 PostgreSQL 已验收。

## 测试／构建

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s server/tests/local_runtime -v
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s server/tests/architecture
```

测试只用临时数据库、假凭据；包含真正 SQLite 提交被 reader 锁阻塞的失败测试，不只是 mock `commit`。
本轮结果见 [STATUS](../docs/STATUS.md)。数据库 schema／恢复策略见 [迁移说明](../server/migrations/README.md)。
Windows 可用 `build_exe.bat` 构建控制台 EXE（安装开发依赖→自检→本地测试→PyInstaller）；产物需要外部 `--config`，不内嵌账号／数据库／客户端。
EXE 使用示例：`MXSJLocalServer.exe --config C:\private\config.json check`。
**Windows BAT／EXE 尚未实机验收，本轮不交付已构建 EXE。** 当前是完整仓库中的本地运行入口，不是脱离共享 server 源码的独立源码 ZIP。

## 下一阶段（尚未实现）

1. 固定旧客户端登录／重登证据，设计可信 legacy 凭据适配及有界 TCP 会话状态机。
2. 将已核报文编解码从旧 Mock 迁入 protocol，禁止导入其启动／改包副作用。
3. 接通账号→完整创角→选角→单地图，先明确完整角色初始化与可信地图规则。
4. 任务／奖励同事务闭环，再扩展其它模块。PostgreSQL 适配与专属验收单独记录。
