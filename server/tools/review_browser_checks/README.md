# review_browser_checks — Agent J 的独立验收工具

本目录是「静态数据复核工具」的**独立验收与回归**工具集，只依赖 Python 标准库，
**不导入** `server/tools/export_review_csv.py`（生产者）或 Agent H 的加载器代码，
所以这里算出的数字来自已提交的 CSV/JSON 制品本身，而不是生产者自报。

配套测试：`server/tests/review_browser_acceptance/`（**不是**原有 161 项架构测试的一部分）。
结论与未执行项见 [`server/docs/review_browser/ACCEPTANCE.md`](../../docs/review_browser/ACCEPTANCE.md)。

## 运行命令

```bash
# 1) 第一阶段：固定数据基线（独立复算，只读）
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/verify_data_baseline.py

# 2) 第一/二/三阶段汇总账本（会写 evidence/acceptance_report.json）
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/acceptance_runner.py

# 3) 验收测试（H/I 未交付时相关用例会显式标记 NOT EXECUTED）
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s server/tests/review_browser_acceptance -q

# 4) 第二阶段：对运行中的加载层/API 做契约驱动验收（需要 ops_*.json 映射）
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/probe_live_api.py \
    --base-url http://127.0.0.1:8100 --map server/tools/review_browser_checks/ops_<name>.json
# 或由本工具按契约里的启动命令在新进程启动：
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/probe_live_api.py \
    --start --command "<API_CONTRACT.md 中的启动命令，可用 {port} 占位>" \
    --dataset-root-env <契约声明的数据根环境变量> --map .../ops_<name>.json

# 5) 第三阶段：复核网页静态策略扫描
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/scan_review_web.py

# 6) 第三阶段：真启动 API + I 的 dev server，按前端自己的契约请求，并执行构建产物
cd server/apps/review_web && VITE_API_PROXY_TARGET=http://127.0.0.1:8000 PORT=5173 npm run dev &
node --experimental-strip-types server/tools/review_browser_checks/web_origin_probe.mjs \
    --app-dir server/apps/review_web --origin http://127.0.0.1:5173
node --experimental-strip-types server/tools/review_browser_checks/web_ui_smoke.mjs \
    --app-dir server/apps/review_web --origin http://127.0.0.1:5173
# 上面的会话也可以由 acceptance_runner.py 的 phase3_web_runtime 阶段自动完成
```

> 第二代 API/页面检查需要在 venv 中安装 fastapi/uvicorn/pydantic（H 的依赖）；
> 本机若为 PEP-668 externally-managed，请建 venv 后用其解释器运行探针
> （`probe_live_api.py` 的 `--command` / `ops_*.json` 的 `startup_command` 可写绝对路径）。

## 文件说明

| 文件 | 作用 |
|---|---|
| `batch_fixture.py` | 独立读取器：manifest 类型化解析、typed-JSON 证据解码、临时副本夹具 |
| `verify_data_baseline.py` | 第一阶段 30 项独立复算（数量、来源分离、零 ID、重复记录、顺序、隔离、参数批准、文本保真） |
| `probe_live_api.py` | 第二/三阶段契约驱动探针（API-01…API-15），支持 `--base-url` / `--start` / `--web-url` / `--integrity-scenarios` |
| `review_api_launch.py` | 用产品自己的工厂（默认 `create_app(ReviewCatalog.load(dir))`）起一个验收实例，便于把 API 指到临时副本 |
| `ops_review_api.json` | 操作映射：把探针绑定到 H 契约里的真实端点/参数/信封/启动命令 |
| `scan_review_web.py` | 页面/前端静态策略扫描（W-01…W-06、H-01）；区分产品代码/测试/夹具/构建配置/注释，只对产品运行时代码判违规，只能给提示的标 `review`（待人工确认） |
| `web_origin_probe.mjs` | 页面运行时：导入前端自己的 `src/api/contract.ts`，把它将要请求的每个端点打到真实 web origin（HTML 200 ≠ 页面可用） |
| `web_ui_smoke.mjs` | 页面运行时：用前端自己的 `vite build` 产物在 jsdom 中真实挂载，采集 console/未捕获异常/请求/渲染结果（无浏览器引擎时的替代验证，并如实标注局限） |
| `conformance_negative_control.py` | **仅用于自检的故障注入测试替身**，不是产品 API、不是契约提案 |
| `acceptance_runner.py` | 汇总各阶段（含 `phase3_web_runtime` 会话、原有 161 项架构测试、导出器 `--check`），输出账本 JSON |
| `evidence/` | 生成的账本与报告（`acceptance_report.json` 等） |

## 自检（负向/正向对照）

验收套件本身用故障注入替身验证过：`server/tests/review_browser_acceptance/test_harness_self_check.py`
对 `conformance_negative_control.py` 开启缺陷时，探针必须报出对应失败；关闭缺陷时必须全部通过。
如果某个检查不再能发现对应缺陷，该自检会失败 —— 防止验收套件变成永远绿色的空壳。

```bash
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/conformance_negative_control.py --emit-map /tmp/ops.json
```

## 依赖与配置

* 仅标准库；无 pip 安装步骤。
* 异常用例使用 `batch_fixture.write_temp_batch()` 生成**临时副本**，从不写入
  `server/docs/csv_checks/batch_001/`。
* 需要 Agent H 的 `API_CONTRACT.md`（API 前缀、启动命令、数据根环境变量）与验收方
  编写的 `ops_*.json` 操作映射；两者齐备前，动态检查一律记为 `not_executed`。
* `web_origin_probe.mjs` / `web_ui_smoke.mjs` 需要 `node >= 22.6`
  （`--experimental-strip-types`）以及 `server/apps/review_web/node_modules` 已安装。
* 真实浏览器渲染/截图需要 Chromium 或 Firefox；本轮环境没有，故 `U-05` 明确记为
  `not_executed`，不用替代手段冒充。
