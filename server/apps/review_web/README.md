# MXSJ 只读数据复核网页（frontend only）

> **检查入口**：当前类型检查／测试／构建及跳过数量见 [STATUS](../../../docs/STATUS.md)。默认测试的在线项跳过不等于实时 API 验收；jsdom 不是实际浏览器。
> 本轮依赖审计对 Vitest 开发依赖链有告警，尚未升级；不能等同于生产静态页面漏洞，也不能忽略。先评估利用条件和升级兼容性，不盲目使用 `npm audit fix --force`。

batch_001 静态数据复核材料的**只读**浏览前端：搜索道具、查看宠物与技能、按来源查看地图/NPC、
检查隔离与缺失证据。没有编辑、删除、导入或发布功能。

> **数据接入状态：已接入 Agent H 的真实复核 API**（PR #22 head
> `9f6ab439a2ecdee37b59b99ddf95e77691490a0f`，契约 `server/docs/review_browser/API_CONTRACT.md`）。
> 前端默认只连接该 API（`/api/v1/review/datasets/{id}/records?offset&limit` 等），
> 失败时显示错误，**不会**回退到夹具/捕获数据。真实联调结果见
> [`../../docs/review_browser/FRONTEND.md`](../../docs/review_browser/FRONTEND.md) §6。

## 快速开始

```bash
npm ci
npm run dev                     # 默认：真实 API 模式，绑定 0.0.0.0:5173
```

后端地址（仅服务器侧代理使用，浏览器只发相对路径 `/api/...`）：

```bash
VITE_API_PROXY_TARGET=http://127.0.0.1:8000 npm run dev   # 默认值
```

## 命令

| 命令 | 作用 |
|---|---|
| `npm run dev` | 开发服务器（0.0.0.0，`/api` 代理到 Python 后端） |
| `npm test` | Vitest + Testing Library（在线联调部分默认跳过） |
| `REVIEW_API_BASE=http://127.0.0.1:8000 npx vitest run src/api/liveBackend.test.ts` | 对真实后端的在线联调（真实 HTTP） |
| `npm run typecheck` | `tsc --noEmit` |
| `npm run build` / `npm run preview` | 生产构建 / 预览构建产物 |
| `npm run fixture:capture` | 捕获 H 的真实响应到 `fixtures/h_api/` |
| `npm run fixture:check` | 与在线后端逐字节比对已提交的捕获 |
| `npm run fixture:api` | **显式**启动捕获回放服务（仅回环 `127.0.0.1:8788`） |
| `npm run dev:fixture` | **显式**回放模式（页面显示红色“非真实数据”横幅） |

## 目录

```
src/api/          契约常量、结构校验、客户端、领域组合（唯一的路径/参数来源）
src/components/   安全文本、十六进制证据、表格、分页、错误边界、横幅
src/pages/        批次概览 / 道具 / 宠物 / 技能 / 地图·NPC / 异常与证据
src/lib/          显示辅助、十六进制、路由、不变量自检规范
src/test/         仅测试使用：捕获回放 fetch stub、渲染辅助、架构守卫
fixtures/h_api/   H 真实响应捕获 + manifest（生产代码不引用）
```

## 绝对边界

- 浏览器只请求相对路径 `/api/...`，不访问沙箱 `localhost`/`127.0.0.1`；
- 前端**不读取**仓库 CSV，也不复制全部 CSV 作为第二数据源；
- 响应必须通过运行时结构校验，结构不符会显示「接口结构错误」，缺失字段不补 `[]`/`0`；
- 不使用 `dangerouslySetInnerHTML`，不执行公式/脚本/客户端富文本标记；
- 不做简繁转换，不补零、不折叠重复记录、不默认选中同名技能的候选 ID；
- 所有页面常驻“复核候选，非正式规则”说明。
