# Arena Agent Mode：沙盒状态丢失的预防、判别与恢复

适用对象：在 **Arena.ai Agent Mode** 中接手本仓库的每个 agent。
长期入口：根 `AGENTS.md`「开始前的60秒」；当前真实进度仍只认 `docs/STATUS.md` 最新章节。

> **先保护工作字节，后修 Git 元数据；先对照远端，再判断是否丢工作。**
> 不执行 `git reset --hard`、`git clean`、删除/重建 `.git`，也不删除、移动或覆盖仓库根目录。
> 不把看见旧 HEAD、dirty 或 untracked，直接解释成「前一个 agent 没提交」。

## 1. 我们确实遇到过什么（事实，不是平台根因诊断）

本项目在 Arena 沙盒/会话恢复中不止一次遇到：

1. 先前可用的仓库外 venv、反编译候选、临时日志或构建环境不再可用，需要重新安装/重建。
2. Git HEAD/索引显示旧提交，但工作树保留较新文件，因而出现大量看似新增/修改的文件。
3. 当前环境与前轮记录不同，不能拿前轮环境、绝对路径或测试日志冒充本轮已执行。

具体一次见 `docs/STATUS.md` §3.49：先前分派提交 `9b0dea7` 已推到远端；恢复后本地显示 `8212b26`，工作文件却仍在。比较215条路径，212条与远端blob完全一致，3个bat仅换行形式不同，按Git属性过滤后的blob也一致。核完才修正分支指针与索引；没有覆盖工作文件、没有重新「补交」同一批文件。

这是**本仓库的观测记录**，不是所有 Arena 会话都会重置的断言，也不足以判断平台内部原因。目录缺失也可能是路径/挂载/权限变化，先核实。不能承诺本地副本或缓存一定持久。

## 2. 如何提前预防

### 每次开工

1. 读 `AGENTS.md`、本文件、`docs/STATUS.md` 最新章节及本任务的README。
2. 记录真实分支、HEAD、工作状态与解释器：
   ```sh
   pwd
   git status --short
   git branch --show-current
   git log -5 --oneline
   python --version
   ```
   解释器命令按本机实际名称选择；不要因为旧venv路径消失就改用错误版本继续跑。
3. 核对会话指定分支、交接的**完整提交号**与原始输入SHA。禁止切换/新建其他工作分支。
4. 按用户要求，**先保存已有工作、提交并推送，确认远端，再开展新工作**。已有dirty若归属不明，先保留并核对，不替别人提交或删除。

### 工作中建立可恢复检查点

- 完成一个可验证的小阶段，就把本阶段源码、必要的小证据和状态提交并推到**自己的固定分支**。不要把全部成果压在最后一次长运行之后。
- 用明确文件名 `git add <本任务文件...>`，不要把游戏包、生成ZIP、venv、node_modules、79MB语料、凭据带进去。
- 成功的 `git commit` 不等于已远端持久化；`git push` 成功后再核远端分支的完整OID。`git status` 干净也不能证明已推送。
- 当前状态写进 `docs/STATUS.md`；必要的机器回执放 `docs/evidence/`，记录输入/工具SHA、命令、实际通过/失败/跳过、范围与下一步。纯临时路径不是交付证据。
- 使用 [`templates/AGENT_CHECKPOINT.md`](templates/AGENT_CHECKPOINT.md) 记最小交接信息。不要只留聊天里的「已经跑过」或「东西在/tmp」。
- 大产物仍留仓库外。确需长期交付时，仅按用户授权上传到指定位置，并记录Drive文件ID、父目录、大小和校验和；**未经授权不能为备份擅自上传**。
- 写明依赖版本和可重建命令。不要把 `.venv`、编译缓存或后台服务当作可恢复的正式资产；长任务应分段、有超时、有明确退出码。
- GitHub/Drive回执也要小而具体；不存 `.git/config`、token、Cookie、账号密码或整份环境变量。

### 结束一轮前

```sh
# 把占位符替换为本会话固定分支，不要照抄尖括号。
git status --short
git branch --show-current
git rev-parse HEAD
git push origin <本会话固定分支>
git ls-remote --heads origin refs/heads/<本会话固定分支>
```

逐项确认远端OID与预期一致。失败不能写「已推送」；认证失败应请用户修复Arena的GitHub连接，不索要PAT/密码。合并PR必须读回真实base/head/state，不因聊天记忆称它已合或仍open。

## 3. 怀疑环境变化时：先止损与留证

1. 停止写包、覆盖导出、批量生成、清理以及Git reset/checkout操作。不要重新启动失联的长任务，先排除它仍在运行。
2. 确认所在目录、当前会话固定分支、HEAD、工作树和索引：
   ```sh
   pwd
   git branch --show-current
   git rev-parse HEAD
   git status --porcelain=v1
   git diff --stat
   git diff --cached --stat
   git ls-files --others --exclude-standard
   ```
   输出可能有个人路径，仅记录必要且脱敏的内容。不打印Git凭据配置。
3. **在修改Git元数据前保护差异**：将本任务的工作树/索引二进制diff、必要的untracked原创文件复制到仓库外的新目录；有本地独有提交时可另做Git bundle。不要把凭据、原游戏大包、敏感1288产物或整个`.git`打进备份。备份尚在同一沙盒，不能当成远端持久备份。
4. 留下差异路径清单和摘要；检查Git属性（特别是bat的CRLF），保留实际文件，不先统一换行。
5. 查询实际远端；联网成功时可安全fetch本会话分支，不改工作树：
   ```sh
   git ls-remote --heads origin refs/heads/<本会话固定分支>
   git fetch origin <本会话固定分支>
   ```
   本地 `origin/...` 在fetch之前也可能是旧值。以交接完整OID、fetch结果和GitHub实际PR为证，不追未知新head盲合。

若`.git`本身不可读/缺失，先保留工作文件和诊断信息，报告问题。不要在原目录 `git init`、重新clone覆盖或删除 `.git`；需要另建只读比较副本时先明确路径与固定分支，绝不替换本会话仓库根目录。

## 4. 按证据选择恢复路线

|观测|应做|不能做|
|---|---|---|
|仅venv/候选/缓存消失，Git与源码正常|依README重建依赖；按固定输入、版本、白名单重新恢复必要候选，再跑验证|声称旧日志是本轮执行；无必要重建全量语料|
|工作树干净，本地仅落后于已确认的本会话远端提交|核祖先、固定OID与任务范围后，`git merge --ff-only <已确认完整OID>`|reset hard；切master；盲追其他agent分支|
|旧HEAD + 大量dirty/untracked，但文件可能是新版|走下节逐文件比对，先证明是元数据错位|把文件删了再pull；把同一成果重复补交|
|有真正未提交改动/索引内容/本地独有提交|保护、归属核对；仅在本固定分支做保留性提交/冲突处理，不自动选择ours/theirs|把它们视作垃圾；用远端版本全部覆盖|
|源码确实缺失|先核是否只是路径变化；只从已推提交/授权交付回执恢复，明确丢了什么|凭聊天重写成「原版」；把不可重建的产物说成存在|
|远端也没有、且未留持久产物|如实报告不可恢复范围，按冻结输入重做；需原始输入时告知用户|伪造完成记录、SHA或测试结果|

### 特例：HEAD/索引旧，工作文件新（不是常规操作）

只有在下列条件**全部满足**时，才能考虑「只修元数据」：

- 已完成上节差异保护，且确定当前就是本会话的固定分支。
- 已确认要恢复到的远端**完整提交号**；不是凭记忆挑一个提交。
- 对目标树涉及的每条路径逐一核验存在性、类型、字节/过滤后Git blob、删除项、额外文件、索引和独有改动。**全部**差异可解释，不能抽样替代全量核验。
- 需要保留的真实改动与untracked文件已单独保护并获得处理结论；有任何未解释差异就停止，不使用下面命令。
- 事先了解这是修改分支引用和索引，不能把它当作安全的一键恢复工具。

单条路径的核对示意（不是完整核验脚本）：

```sh
git check-attr -a -- script_manual/build_exe.bat
git hash-object --path=script_manual/build_exe.bat script_manual/build_exe.bat
git rev-parse '<已确认目标完整OID>:script_manual/build_exe.bat'
```

`hash-object --path`会按该路径的Git属性处理CRLF；原字节不同但过滤后blob一致，应在回执中注明，不能谎称原字节相同。

**高级手工步骤，仅供已完成全量核验的agent：**先记录旧OID；以compare-and-swap更新当前固定分支引用，再用不带`-u`的`read-tree`重建索引，**不更新工作树文件**。以下占位符必须逐个替换，不能当批处理直接运行：

```sh
git update-ref refs/heads/<本会话固定分支> <目标完整OID> <刚记录的旧完整OID>
git read-tree <目标完整OID>
git status --short
git diff --stat
git diff --cached --stat
```

`update-ref`的旧OID条件不符或任何一步失败就停，别去掉条件强行重跑。修后若仍有dirty，不要clean或覆盖；继续解释差异。这个特例只证明元数据对齐，不替代来源核验、依赖重建或测试。

## 5. 恢复之后必须重新做什么

- 记录恢复前/后HEAD、远端OID、差异范围、采取的操作及没有采取的危险操作；不保存凭据。
- 当前环境重新核原包/工具SHA、Python与依赖版本；不能用不同引擎生成物覆盖旧证据。
- 重新运行与本任务相关的严格校验、单测、lint、Windows静态；GUI/实机没有环境就明确跳过。
- 说明哪些成果来自旧持久证据、哪些在本环境重新执行、哪些临时产物尚未重建。
- 仅临时文件丢失不意味着审核失效；但正文或引用来源变了字节，就必须重核SHA/重审，不能照抄旧accepted。
- 更新 `docs/STATUS.md`，推送本固定分支后核远端；再继续下一阶段，而不是不停反复「恢复」。

本脚本手册的安全再验入口：`python script_manual/check_manual.py`。它是只读结构/合成测试闸门，不重建原包、不运行游戏；Windows真跑应加`--require-gui`并按手册的Windows测试说明执行。
