// Real offline Chromium integration for the production task-oriented handbook.
// This is NOT a semantic review or a Qt/Windows test.
const { chromium: playwright } = require("playwright-core");
const distribution = require("@sparticuz/chromium");
const chromium = distribution.default;
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");
const { pathToFileURL } = require("node:url");
const { parseArgs } = require("node:util");
const { values } = parseArgs({ options: {
  site: { type: "string" }, artifacts: { type: "string" },
} });
if (!values.site || !values.artifacts) throw new Error("--site and --artifacts required");
fs.mkdirSync(values.artifacts, { recursive: false });
let browser;
(async () => {
  const bin = path.resolve(path.dirname(require.resolve("@sparticuz/chromium")), "../bin");
  await distribution.inflate(path.join(bin, "al2023.tar.br"));
  distribution.setupLambdaEnvironment(path.join(os.tmpdir(), "al2023/lib"));
  if (process.env.MXSJ_MANUAL_TEST_FONT) {
    await distribution.inflate(path.join(bin, "fonts.tar.br"));
    const font = path.resolve(process.env.MXSJ_MANUAL_TEST_FONT);
    fs.copyFileSync(font, path.join(os.tmpdir(), "fonts", path.basename(font)));
  }
  browser = await playwright.launch({ executablePath: await chromium.executablePath(),
    args: chromium.args.filter(a => !a.startsWith("--disable-web-security") &&
      !a.startsWith("--allow-running-insecure-content")), headless: true });
  const context = await browser.newContext({ viewport: {width: 1440, height: 1000}, offline: true });
  const page = await context.newPage(), errors = [], requests = [];
  page.on("pageerror", e => errors.push(String(e)));
  page.on("console", e => { if (e.type() === "error") errors.push(e.text()); });
  page.on("request", r => requests.push(r.url()));
  await page.goto(pathToFileURL(path.join(path.resolve(values.site), "index.html")).href);
  await page.locator("#guide-results button").first().waitFor();
  assert.equal(await page.locator("#guide-results button").count(), 6);
  assert.equal(await page.locator("#guide-workspace").isVisible(), true);
  assert.equal(await page.locator("#module-workspace").isVisible(), false);
  const data = JSON.parse(await page.locator("#manual-data").textContent());
  assert.equal(data.coverage.accepted, 16);
  assert.equal(data.guides.length, 6);
  for (const q of ["刷新失败", "验证码", "Enter", "NextCmd"]) {
    await page.locator("#guide-query").fill(q);
    assert.ok(await page.locator("#guide-results button").count() > 0, q);
    assert.match(await page.locator("#guide-detail").innerText(), /未独立审核/);
  }
  await page.locator("#guide-query").fill("没有编写的任务xyz");
  assert.equal(await page.locator("#guide-results button").count(), 0);
  assert.match(await page.locator("#guide-detail").innerText(), /尚无匹配专题/);
  await page.locator("#show-modules").click();
  await page.locator("#show-guides").click();
  assert.equal(await page.locator("#guide-workspace").isVisible(), true);
  await page.locator("#guide-query").fill("");
  let refsChecked = 0;
  for (const guide of data.guides) {
    await page.locator("#guide-results button").filter({hasText: guide.title}).click();
    const panel = page.locator("#guide-detail");
    assert.match(await panel.innerText(), /应如何检查（不是已执行）/);
    assert.match(await panel.innerText(), /修改入口与建议（待验证）/);
    assert.equal(await panel.locator("details").count(),
      guide.steps.flatMap(s => s.references).flatMap(r => r.evidence).length);
    const ref = guide.steps[0].references[0];
    await panel.getByRole("button", {name: `打开函数：${ref.function}`, exact: true}).first().click();
    assert.equal(await page.locator("#module-workspace").isVisible(), true);
    assert.equal(await page.locator(`#function-${ref.function_index}`).innerText(), ref.function);
    assert.match(await page.locator("#detail h2").innerText(), new RegExp(ref.path.replaceAll(".", "\\.")));
    await page.reload();
    assert.equal(await page.locator(`#function-${ref.function_index}`).innerText(), ref.function);
    await page.locator("#show-guides").click();
    await page.locator("#guide-results button").filter({hasText: guide.title}).click();
    await page.locator("#guide-detail").getByRole("button", {
      name: `定位证据：${ref.evidence_ids[0]}`, exact: true }).first().click();
    assert.ok(await page.locator(`#evidence-${ref.evidence_ids[0]}`).count());
    assert.match(page.url(), /section=evidence/);
    refsChecked += 2;
    await page.locator("#show-guides").click();
  }
  // Verify the pending battle dependency isn't cosmetically upgraded to acceptance.
  await page.locator("#guide-results button").filter({hasText: "修改战斗表现"}).click();
  assert.match(await page.locator("#guide-detail").innerText(), /引用模块：待审核/);
  await page.reload();
  assert.match(await page.locator("#guide-detail h2").innerText(), /修改战斗表现/);
  await page.locator("#guide-results button").filter({hasText: "修改首页公告"}).click();
  await page.locator("#guide-detail details summary").first().click();
  assert.match(await page.locator("#guide-detail details pre").first().innerText(), /^\d+: /);
  await page.screenshot({path: path.join(values.artifacts, "guide-desktop.png"), fullPage: false});
  await page.setViewportSize({width: 390, height: 844});
  const width = await page.evaluate(() => [document.documentElement.scrollWidth, innerWidth]);
  assert.ok(width[0] <= width[1], "mobile horizontal overflow");
  await page.screenshot({path: path.join(values.artifacts, "guide-mobile.png"), fullPage: false});
  await page.setViewportSize({width: 1440, height: 1000});
  await page.locator("#show-modules").click();
  await page.locator("#query").fill("script/hero.py");
  await page.locator("#results button").first().click();
  await page.getByRole("button", {name: "关联与修改", exact: true}).click();
  await page.getByRole("button", {name: "跳转：script/char/npc.py", exact: true}).click();
  assert.equal(await page.locator("#detail h2").innerText(), "script/char/npc.py");
  assert.deepEqual(errors, []);
  assert.ok(requests.every(u => u.startsWith("file:")));
  const report = { browser: await browser.version(), protocol: "file://", offline: true,
    guides: data.guides.length, steps: data.guides.reduce((n,g) => n + g.steps.length, 0),
    function_and_evidence_jumps_and_function_reload_checked: refsChecked,
    source_preview_verified: true, mobile_no_horizontal_overflow: true,
    unknown_task_is_not_fake_completion: true, pending_battle_not_self_approved: true,
    guide_deep_link_reload: true, legacy_module_navigation: "hero→npc",
    errors, requests, not_tested: "Qt/Windows/EXE/game and guide semantic acceptance" };
  fs.writeFileSync(path.join(values.artifacts, "browser-result.json"), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report, null, 2));
})().catch(e => { console.error(e); process.exitCode = 1; })
  .finally(async () => { if (browser) await browser.close(); });
