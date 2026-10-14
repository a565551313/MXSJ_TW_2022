# 归档文档索引

本目录存放**已被取代的历史快照**。它们不再描述当前状态，但按项目原则（旧报告是证据演进记录，标注被推翻而不是删除）予以保留。
每个文件顶部都有归档横幅，说明原路径、时期和应改读的现行文档。

**不要**依据这里的任何“下一步 / 当前分支 / 待办 / 计数”开展工作；现行入口是根目录 [AGENTS.md](../../AGENTS.md) 与 [docs/STATUS.md](../STATUS.md)。

| 归档文件 | 原路径 | 时期 | 被什么取代 |
|---|---|---|---|
| [2026-10-12-AGENT_HANDOFF-registration-v3_3.md](2026-10-12-AGENT_HANDOFF-registration-v3_3.md) | `AGENT_HANDOFF.md` | 2026-10-12，注册 UI v3.3 交付 | `AGENTS.md`、`docs/STATUS.md`、[`tools/client_patches/V3_3_DELIVERY_AND_ACCEPTANCE.md`](../../tools/client_patches/V3_3_DELIVERY_AND_ACCEPTANCE.md) |
| [2026-10-12-map-editor-handover.md](2026-10-12-map-editor-handover.md) | `work/dream-world-connect-login-map/report/map-editor-handover-20261012.md` | 2026-10-12，地图编辑器 PR #25 | [`map_editor/PR25_REVIEW.md`](../../map_editor/PR25_REVIEW.md)、[`map_editor/README.md`](../../map_editor/README.md) |
| [2026-10-11-CLIENT_DATA_AGENT_HANDOFF.md](2026-10-11-CLIENT_DATA_AGENT_HANDOFF.md) | `server/docs/CLIENT_DATA_AGENT_HANDOFF.md` | 2026-10-11，静态数据提取分工 | [`server/docs/csv_checks/BATCH_001.md`](../../server/docs/csv_checks/BATCH_001.md)、[`server/docs/CSV_READINESS.md`](../../server/docs/CSV_READINESS.md) |
| [work-20261010/HANDOVER-20261010.md](work-20261010/HANDOVER-20261010.md) | `work/dream-world-connect-login-map/HANDOVER-20261010.md` | 2026-10-10 | [`report/client-status-20261012.md`](../../work/dream-world-connect-login-map/report/client-status-20261012.md)、[`work/.../INDEX.md`](../../work/dream-world-connect-login-map/INDEX.md) |
| [work-20261010/HANDOFF-agent-20261010.md](work-20261010/HANDOFF-agent-20261010.md) | `work/dream-world-connect-login-map/HANDOFF-agent-20261010.md` | 2026-10-10 | 同上 |
| [work-20261010/QUICK_START.md](work-20261010/QUICK_START.md) | `work/dream-world-connect-login-map/QUICK_START.md` | 2026-10-10 | `AGENTS.md`；其命令字/帧格式结论已被 client-status-20261012 推翻 |
| [work-20261010/TASK_DISPATCH.md](work-20261010/TASK_DISPATCH.md) | `work/dream-world-connect-login-map/TASK_DISPATCH.md` | 2026-10-10，多 Agent 分派总纲 | 分派已完成；任务书仍在 [`work/.../task-briefs/`](../../work/dream-world-connect-login-map/task-briefs/) |
| [work-20261010/DISPATCH_OVERVIEW.md](work-20261010/DISPATCH_OVERVIEW.md) | `work/dream-world-connect-login-map/DISPATCH_OVERVIEW.md` | 2026-10-10 | 同上 |
| [work-20261010/发给其他会话的指令.md](work-20261010/发给其他会话的指令.md) | `work/dream-world-connect-login-map/发给其他会话的指令.md` | 2026-10-10，一次性分派提示词 | 同上 |
| [work-20261010/handoff-20261009.md](work-20261010/handoff-20261009.md) | `work/dream-world-connect-login-map/report/handoff-20261009.md` | 2026-10-09 | 当时已被 HANDOVER-20261010 取代；二者现一并归档 |
| [route-scope-20261009/](route-scope-20261009/) | `work/route/`、`work/master-route-20261009-*/` | 2026-10-09 | 外部 “reverse-skill” 路由框架残留，无证据价值 |

## 归档约定

1. 文件被新文档**完整取代**后才归档；仍被测试、工具或证据链直接引用的文件（例如 `server/docs/csv_checks/*`、`work/.../evidence/*`、`work/.../timeline.md`）留在原地。
2. 归档时：`git mv` 到本目录（保留原文件名或加日期前缀）→ 顶部加横幅 → 修正文内相对链接 → 更新仓库内指向它的链接 → 在本表登记。
3. 不修改归档文件的正文内容；需要纠错时在现行文档里写明“被推翻的结论 + 新依据”。
