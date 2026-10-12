# 只读复核工具：H / I / J 集成收尾验收

**结论：通过。** 2026-10-12，在工作分支 `arena/b53b33e6-mxsj-tw-2022` 合并
PR #22、#24、#23，并完成有界修复。没有合入 master，没有修改首批数据或正式 `game_data`。

本报告替代此前针对旧 H/I 提交的失败报告；历史问题与原报告可在 Git 历史中查阅。
范围仅为 Python 只读目录/API、静态数据复核网页及其验收，不代表游戏服务器或玩法已完成。

## 1. 实测代码

| 对象 | 提交 |
|---|---|
| H / PR #22 | `01e2adb465fb8bb67f872184e805f2ab6549cae8` |
| I / PR #24 | `4bef44fcdbbff228b67831cff7395e373532ffcb` |
| J / PR #23 | `85fc44ed401004fe7c4df40884e2a94c9dd6c4c7` |
| 三个 PR 合入后的工作分支 | `72ce8497336b25d80a5fd58be0010552ee385f2c` |
| **最终实测修复提交** | **`d9721d8df758d905830ac9519df09853bd5b6b38`** |

最终验证在正式仓库中运行，不是仅测 Agent 原分支或旧的临时组合。其后提交仅更新文档和验收证据。

## 2. 收尾修复

- **目录证据一致性**：加载时校验 JSONL 必需字段、非空 typed evidence、身份与原因；
  隔离总数及各来源数量须与 `validation.json` 一致；覆盖证据须与 CSV 摘要的身份、
  offset、数量及相同值标记一致。即使临时副本同步更新了 manifest 哈希，截短证据仍会拒绝加载。
  新增 11 个回归用例。此检查不是数字签名，不宣称能识别所有文件被一致重写的情况。
- **关联查询完整性**：`fetchAllRecords` 不再把提前空页当作成功结束；拒绝 total 漂移、
  错误 offset/count、重复 `_pk`、超出 total 的数据；保留安全上限。
  合法零结果和不同 `_pk` 的重复业务值仍可返回。新增 9 个回归用例。
- **验收工具自身**：修正非法排序断言位置；web probe 使用当前 `contract.ts` 路径构造器及
  `{dataset,total,offset,limit,count,records}`；失败统一记录 problems，不因缺字段二次崩溃。
  真实前端探测通过 `web_app_dir` 显式启用，避免污染 synthetic 正向对照。
  静态扫描排除构建产物中的第三方 React 代码，并新增回归测试，原负向检测仍保留。
- **真实浏览器**：新增独立 Chromium 驱动，与 jsdom 明确区分；缺少浏览器时保留未执行状态，
  不会把验收判为完整。runner 使用调用它的 Python 解释器；完整通过返回 0，否则返回 1。

## 3. 最终结果（分开计数）

| 检查 | 结果 |
|---|---|
| H 目录单元测试 | **34 通过** |
| H API 测试 | **27 通过** |
| I 前端测试 | **112 通过，9 个在线测试默认跳过** |
| I 单独真实 API 联调 | **12 通过，0 跳过**（包含上述 9 个在线测试，不能简单累加） |
| I TypeScript / Vite 生产构建 | **通过 / 通过** |
| J 独立验收套件 | **68 通过，0 跳过**；含正向、负向对照 |
| 原有架构套件 | **161 通过**（不是新增复核工具测试） |
| 导出器 `--check` | **22 文件核验通过** |
| 独立数据基线 | **30 项通过** |
| API 验收检查（含分页子项） | **20 项通过** |
| 静态策略扫描 | **8 项通过** |
| 页面运行时 / 构建 / Chromium | **12 项通过** |

总账本：`integration_acceptance_complete = true`；API、静态页、运行时待执行检查均为 **0**。

### 真实 Chromium，不是 jsdom 冒充

`HeadlessChrome/153.0.8010.0` 完成 **16 个场景**：

- 概览、道具、宠物、技能、地图/NPC、异常六页，无正常加载时 console error / API 失败；
- 详情 `/items/41052`、`/pets/2800`、`/pets/3010`、`/skills/4573`；
- 翻到第二页，搜索 `時空石` 得到单条 41052；两个 NPC 来源均可见；
- 模拟 total=3、先返回 1 条再空页，必须抛出 `INCOMPLETE_RESULT_SET`；
- 390×844 窄屏异常页渲染并截图；模拟 `/batch` 返回 200 `{}`，展示明确的接口结构错误。

这不是完整的跨浏览器兼容性、像素级视觉回归或无障碍审计；这些不在本次完成声明内。

## 4. 可追溯证据

位置：[`server/tools/review_browser_checks/evidence/`](../../tools/review_browser_checks/evidence/)

- `acceptance_report.json`：最终代码 SHA、环境、分阶段结果、执行计数与完整结论。
- `live_api_report.json`、`live_api_with_web_origin.json`：API 和真实 web origin 代理检查。
- `web_origin_probe.json`：当前前端契约端点；`web_ui_smoke.json`：生产构建在 jsdom 中执行。
- `chromium_smoke.json`：真实 Chromium 的 16 个场景；`chromium-mobile-anomalies.png`：本次截图。
- `closeout_checks.json`：目录/API/前端/在线联调的补充执行摘要，以及保护路径核对。

报告中的临时目录、端口是当次运行坐标，不是部署配置。
单独的 jsdom 报告中 U-05 仍是未执行，**总账本用同一会话的真实 Chromium 结果替换该项**。
无 web origin 的单独 API 报告同理不能替代完整集成结论。

## 5. 复跑

仓库根目录，Python 3.11+、Node 22.6+：

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r server/apps/review_api/requirements.txt
npm ci --prefix server/apps/review_web

# 浏览器工具独立安装，不写进前端生产依赖或提交 node_modules。
npm install --prefix /tmp/mxsj-browser-tools puppeteer-core@25.13.0 @sparticuz/chromium@153.0.0
REVIEW_BROWSER_TOOLS=/tmp/mxsj-browser-tools \
  python server/tools/review_browser_checks/acceptance_runner.py

python -m unittest discover -s server/tests/catalog -q
python -m unittest discover -s server/tests/review_api -q
npm --prefix server/apps/review_web run typecheck
npm --prefix server/apps/review_web test
npm --prefix server/apps/review_web run build
```

Chromium 自动准备脚本针对本轮 Linux 沙箱验证；其他平台可另行适配。
不配置 `REVIEW_BROWSER_TOOLS` 时其它检查仍运行，但真实浏览器项明确未执行，完整验收不判通过。
单独在线联调需先按 BACKEND.md 启动 API，再在前端目录执行：

```bash
REVIEW_API_BASE=http://127.0.0.1:8000 npx vitest run src/api/liveBackend.test.ts
```

## 6. 保护边界

与合并前 `5f23690` 对照，`server/docs/csv_checks/`、`server/game_data/`、导出器、
`data/`、`tools/`、`work/` 无变更；客户端/FLS/密钥库未改。
异常测试只操作临时副本，22 个批次文件仍通过导出器核验。
四条隔离、三条缺失、同名歧义、覆盖记录、NPC 零 ID、重复和顺序、来源分离继续保留。
未执行原始脚本或公式，未做简繁替换、参数擅改或正式数据发布。
