# MXSJ 只读数据复核网页（frontend only）

batch_001 静态数据复核材料的**只读**浏览前端：搜索道具、查看宠物与技能、按来源查看地图/NPC、
检查隔离与缺失证据。没有编辑、删除、导入或发布功能。

> **数据接入状态：待接口联调。** 前端默认只连接 Python 复核 API（`/api/v1/review/`）。
> 接口契约由 Agent H 提供（`server/docs/review_browser/API_CONTRACT.md`，截至本基线尚未出现）。
> API 失败时页面显示错误，**不会**回退到夹具数据。

完整说明、接口需求清单与测试结果见 [`../../docs/review_browser/FRONTEND.md`](../../docs/review_browser/FRONTEND.md)。

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
| `npm test` | Vitest + Testing Library 测试 |
| `npm run typecheck` | `tsc --noEmit` |
| `npm run build` / `npm run preview` | 生产构建 / 预览构建产物 |
| `npm run fixture:api` | **显式**启动夹具 API（仅回环 `127.0.0.1:8788`） |
| `npm run dev:fixture` | **显式**夹具演示模式（页面显示红色“非真实数据”横幅） |
| `npm run fixtures:rebuild` | 由冻结 CSV 重建夹具样本（`-- --check` 校验字节一致） |

## 目录

```
src/api/          接口客户端与契约常量（唯一的路径/参数来源）
src/components/   安全文本、十六进制证据、表格、分页、横幅等
src/pages/        批次概览 / 道具 / 宠物 / 技能 / 地图·NPC / 异常与证据
src/lib/          显示辅助、十六进制、路由、不变量自检规范
src/test/         仅测试使用：夹具 fetch stub、渲染辅助、架构守卫
fixtures/         夹具样本与其构建/服务脚本（生产代码不引用）
```

## 绝对边界

- 浏览器只请求相对路径 `/api/...`，不访问沙箱 `localhost`/`127.0.0.1`；
- 前端**不读取**仓库 CSV，也不复制全部 CSV 作为第二数据源；
- 不使用 `dangerouslySetInnerHTML`，不执行公式/脚本/客户端富文本标记；
- 不做简繁转换，不补零、不折叠重复记录、不默认选中同名技能的候选 ID；
- 所有页面常驻“复核候选，非正式规则”说明。
