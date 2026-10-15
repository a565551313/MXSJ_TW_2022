# 离线浏览器开发检查

不参与用户依赖/Windows EXE构建。这是A第一批20条样板的Linux浏览器冒烟，扩容后由A同步维护验收预期；不是语义审核。

```bash
cd script_manual/browser_tests
npm ci
node check.cjs --site /absolute/path/to/newly-exported-site --artifacts /absolute/path/to/new-output-directory
```

仅从npm下载固定版playwright-core与Chromium。使用包内真实Linux Chromium及所带动态库，不使用缺符号的桩库；未禁用web security/CSP。浏览器context断网，以 `file://` 打开导出HTML，检查路径/中文/函数/多词搜索、诚实覆盖计数、消息分支、来源警告/证据状态、配置入口、关联跳转与深链重开、筛选、空状态、390px无横向溢出、无JS/CSP报错、无外网请求，输出截图与JSON。

沙箱缺中文系统字体时，可用 `MXSJ_MANUAL_TEST_FONT=/path/to/locally-licensed-font.ttf` 仅给测试浏览器注册字体；不嵌入站点、不随工具再分发。

artifact目录必须不存在，建议放仓库外。浏览器二进制、node_modules、截图和导出站点都不入库。不把Linux浏览器通过说成Windows或原生游戏通过。
