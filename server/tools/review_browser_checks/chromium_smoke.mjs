/** Actual Chromium, separate from jsdom. Install tools outside product source:
 * npm install --prefix /path/to/tools puppeteer-core@25.13.0 @sparticuz/chromium@153.0.0
 * REVIEW_BROWSER_TOOLS=/path/to/tools node chromium_smoke.mjs --origin URL --out FILE
 */
import assert from 'node:assert/strict'
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import { dirname, join, resolve } from 'node:path'
import fs from 'node:fs/promises'

const args = {}
for (let i = 2; i < process.argv.length; i++) if (process.argv[i].startsWith('--')) args[process.argv[i].slice(2)] = process.argv[++i]
const report = { check: 'U-05', title: 'actual Chromium routes, interactions and failure paths', status: 'fail', detail: { cases: [] } }
let browser
try {
  assert.ok(process.env.REVIEW_BROWSER_TOOLS, 'REVIEW_BROWSER_TOOLS is required')
  const require = createRequire(join(resolve(process.env.REVIEW_BROWSER_TOOLS), 'package.json'))
  const { default: puppeteer } = await import(pathToFileURL(require.resolve('puppeteer-core')))
  const { default: chromium, inflate } = await import(pathToFileURL(require.resolve('@sparticuz/chromium')))
  const lib = resolve(dirname(require.resolve('@sparticuz/chromium')), '../bin/al2023.tar.br')
  await inflate(lib)
  process.env.LD_LIBRARY_PATH = ['/tmp/al2023/lib', process.env.LD_LIBRARY_PATH].filter(Boolean).join(':')
  browser = await puppeteer.launch({ executablePath: await chromium.executablePath(), args: chromium.args, headless: true })
  report.detail.browser = await browser.version()
  const page = await browser.newPage()
  await page.setViewport({ width: 1365, height: 900 })
  const errors = [], bad = []
  page.on('pageerror', e => errors.push(e.message))
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()) })
  page.on('response', r => { if (r.url().includes('/api/v1/') && r.status() >= 400) bad.push(r.url()) })
  async function go(path) {
    errors.length = 0; bad.length = 0
    await page.goto(args.origin + path, { waitUntil: 'networkidle0' })
    await page.waitForNetworkIdle()
    return page.evaluate(() => document.body.innerText)
  }
  function success(label, body) {
    assert.ok(body.length > 300, `${label}: blank/short page`)
    assert.ok(!body.includes('无法加载数据'), `${label}: loading failure`)
    assert.deepEqual(errors, [], `${label}: console errors`)
    assert.deepEqual(bad, [], `${label}: failed API requests`)
    report.detail.cases.push({ label, status: 'pass' })
  }
  for (const route of ['/', '/items', '/pets', '/skills', '/maps', '/anomalies', '/items/41052', '/pets/2800', '/pets/3010', '/skills/4573']) {
    success(route, await go(route))
  }
  await go('/items')
  await page.evaluate(() => [...document.querySelectorAll('button')].find(b => b.textContent.trim() === '下一页').click())
  await page.waitForFunction(() => document.querySelector('.pagination__status')?.textContent.includes('第 2 /'))
  report.detail.cases.push({ label: 'items next page', status: 'pass' })
  await page.type('input[type=search]', '時空石')
  await page.waitForFunction(() => document.querySelector('tbody')?.textContent.includes('41052') && document.querySelectorAll('tbody tr').length === 1)
  report.detail.cases.push({ label: 'search 時空石 returns one row 41052', status: 'pass' })
  const maps = await go('/maps')
  assert.ok(maps.includes('2601') && maps.includes('2804'), 'both NPC source panels visible')
  report.detail.cases.push({ label: 'NPC sources remain separate', status: 'pass' })
  const partial = await page.evaluate(async () => {
    const { fetchAllRecords } = await import('/src/api/reviewApi.ts')
    const original = window.fetch
    window.fetch = async url => {
      const offset = Number(new URL(String(url), location.origin).searchParams.get('offset'))
      const records = offset === 0 ? [{ _pk: '1', skill_name_raw: 'TEST_ONLY' }] : []
      return new Response(JSON.stringify({ dataset: 'synthetic', total: 3, offset, limit: 500, count: records.length, records }), { status: 200 })
    }
    try { return { returned: await fetchAllRecords('synthetic', {}) } }
    catch (e) { return { code: e.code, message: e.message } }
    finally { window.fetch = original }
  })
  assert.equal(partial.code, 'INCOMPLETE_RESULT_SET')
  report.detail.cases.push({ label: 'early empty page rejects partial success', status: 'pass', result: partial })
  await page.setViewport({ width: 390, height: 844 })
  success('mobile anomalies', await go('/anomalies'))
  const screenshot = join(dirname(args.out), 'chromium-mobile-anomalies.png')
  await fs.mkdir(dirname(args.out), { recursive: true })
  await page.screenshot({ path: screenshot, fullPage: true })
  report.detail.screenshot = screenshot
  await page.setRequestInterception(true)
  page.on('request', req => req.url().endsWith('/api/v1/review/batch')
    ? req.respond({ status: 200, contentType: 'application/json', body: '{}' }) : req.continue())
  const invalid = await go('/')
  assert.ok(invalid.includes('接口结构错误'), 'invalid 200 response must show explicit schema error')
  report.detail.cases.push({ label: 'invalid 200 payload shows schema error, not white screen', status: 'pass' })
  report.status = 'pass'
} catch (error) {
  report.detail.error = String(error.stack || error)
} finally {
  if (browser) await browser.close()
  await fs.mkdir(dirname(args.out), { recursive: true })
  await fs.writeFile(args.out, JSON.stringify(report, null, 2) + '\n')
  console.log(JSON.stringify(report))
  process.exitCode = report.status === 'pass' ? 0 : 1
}
