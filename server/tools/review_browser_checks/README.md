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
```

## 文件说明

| 文件 | 作用 |
|---|---|
| `batch_fixture.py` | 独立读取器：manifest 类型化解析、typed-JSON 证据解码、临时副本夹具 |
| `verify_data_baseline.py` | 第一阶段 30 项独立复算（数量、来源分离、零 ID、重复记录、顺序、隔离、参数批准、文本保真） |
| `probe_live_api.py` | 第二/三阶段契约驱动探针（API-01…API-15），支持 `--base-url` 或 `--start` |
| `scan_review_web.py` | 页面/前端静态策略扫描（W-01…W-06、H-01） |
| `conformance_negative_control.py` | **仅用于自检的故障注入测试替身**，不是产品 API、不是契约提案 |
| `acceptance_runner.py` | 汇总各阶段，输出账本 JSON |
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
