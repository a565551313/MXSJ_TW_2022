const { chromium: playwright } = require("playwright-core");
const chromium = require("@sparticuz/chromium").default;
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");
const { pathToFileURL } = require("node:url");
const { parseArgs } = require("node:util");
const { values } = parseArgs({
  options: { site: { type: "string" }, artifacts: { type: "string" } },
});
if (!values.site) throw new Error("--site <export directory> is required");
const site = pathToFileURL(
  path.join(path.resolve(values.site), "index.html"),
).href;
const artifacts =
  values.artifacts ||
  path.join(os.tmpdir(), `mxsj-manual-browser-${Date.now()}`);
fs.mkdirSync(artifacts, { recursive: false });
let browser;
(async () => {
  const distribution = require("@sparticuz/chromium");
  await distribution.inflate(
    path.resolve(
      path.dirname(require.resolve("@sparticuz/chromium")),
      "../bin/al2023.tar.br",
    ),
  );
  distribution.setupLambdaEnvironment(path.join(os.tmpdir(), "al2023/lib"));
  if (process.env.MXSJ_MANUAL_TEST_FONT) {
    await distribution.inflate(
      path.resolve(
        path.dirname(require.resolve("@sparticuz/chromium")),
        "../bin/fonts.tar.br",
      ),
    );
    const local = path.resolve(process.env.MXSJ_MANUAL_TEST_FONT);
    fs.copyFileSync(
      local,
      path.join(os.tmpdir(), "fonts", path.basename(local)),
    );
  }
  browser = await playwright.launch({
    executablePath: await chromium.executablePath(),
    args: chromium.args.filter(
      (a) =>
        !a.startsWith("--disable-web-security") &&
        !a.startsWith("--allow-running-insecure-content"),
    ),
    headless: true,
  });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1050 },
    offline: true,
  });
  const page = await context.newPage();
  const errors = [],
    requests = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("console", (e) => {
    if (e.type() === "error") errors.push(e.text());
  });
  page.on("request", (r) => requests.push(r.url()));
  await page.goto(site);
  await page.waitForSelector("#results button");
  assert.equal(await page.locator("#results button").count(), 20);
  assert.match(await page.locator("#stats").innerText(), /20\/5135/);
  for (const query of [
    "公告",
    "LOGIN\\MAINPAGE",
    "refreshbulletin",
    "公告 news.txt",
  ]) {
    await page.locator("#query").fill(query);
    assert.equal(await page.locator("#results button").count(), 1);
  }
  await page.locator("#results button").first().click();
  assert.match(await page.locator("#detail").innerText(), /原包对应未验证/);
  await page.getByRole("button", { name: "类与函数", exact: true }).click();
  assert.match(await page.locator("#detail").innerText(), /msgid == 30/);
  await page.getByRole("button", { name: "证据与来源", exact: true }).click();
  assert.match(
    await page.locator("#detail").innerText(),
    /verified_bytes_and_lines/,
  );
  await page.getByRole("button", { name: "关联与修改", exact: true }).click();
  assert.match(await page.locator("#detail").innerText(), /News/);
  await page
    .locator("#detail")
    .getByRole("button", { name: "script/login/register.py", exact: true })
    .click();
  assert.match(await page.locator("#detail").innerText(), /尚未解释职责/);
  await page.reload();
  assert.match(await page.locator("#detail").innerText(), /register.py/);
  await page.locator("#query").fill("");
  await page.locator("#domain").selectOption("network");
  assert.equal(await page.locator("#results button").count(), 4);
  await page.locator("#query").fill("公告");
  assert.equal(await page.locator("#results button").count(), 0);
  assert.match(await page.locator("#results").innerText(), /不等于/);
  await page.locator("#domain").selectOption("");
  await page.locator("#review").selectOption("accepted");
  assert.equal(await page.locator("#results button").count(), 0);
  await page.locator("#review").selectOption("");
  await page.locator("#results button").first().click();
  await page.getByRole("button", { name: "关联与修改", exact: true }).click();
  await page.screenshot({
    path: path.join(artifacts, "offline-desktop.png"),
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  const mobileWidth = await page.evaluate(() => ({
    content: document.documentElement.scrollWidth,
    viewport: innerWidth,
  }));
  console.log("MOBILE", mobileWidth);
  assert.ok(
    mobileWidth.content <= mobileWidth.viewport,
    "mobile horizontal overflow",
  );
  await page.screenshot({
    path: path.join(artifacts, "offline-mobile.png"),
    fullPage: true,
  });
  assert.deepEqual(errors, []);
  assert.ok(requests.every((u) => u.startsWith("file:")));
  const report = {
    browser: await browser.version(),
    protocol: "file://",
    offline: true,
    passed: [
      "20 path rows and honest coverage",
      "three-mode and multiword search",
      "source warning",
      "message branches",
      "evidence status",
      "resources/config guide",
      "related-module navigation",
      "deep-link reload",
      "domain filtering",
      "review filtering",
      "empty-state warning",
      "mobile no horizontal overflow",
      "no external network requests",
      "no page/CSP errors",
    ],
    page_errors: errors,
    requests,
  };
  fs.writeFileSync(
    path.join(artifacts, "browser-result.json"),
    JSON.stringify(report, null, 2),
  );
  await browser.close();
  console.log(JSON.stringify(report, null, 2));
})()
  .catch((e) => {
    console.error(e);
    process.exitCode = 1;
  })
  .finally(async () => {
    if (browser) await browser.close();
  });
