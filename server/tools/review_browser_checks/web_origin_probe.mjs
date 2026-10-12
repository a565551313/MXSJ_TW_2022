/** Probe the current frontend contract through a real web origin (not product code).
 * Every failure, including import/network/shape errors, is written to --out.
 * Usage: node --experimental-strip-types web_origin_probe.mjs --app-dir DIR --origin URL --out FILE
 */
import { mkdirSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { pathToFileURL } from 'node:url'

const args = {}
for (let i = 2; i < process.argv.length; i += 1) {
  if (process.argv[i].startsWith('--')) args[process.argv[i].slice(2)] = process.argv[++i]
}
const origin = (args.origin || '').replace(/\/$/, '')
const report = { stage: 'phase3_web_origin_contract', origin, checks: [], requests: [] }
const record = (check, title, problems, detail = {}) => report.checks.push({
  check, title, status: problems.length ? 'fail' : 'pass', detail: { ...detail, problems },
})

async function fetchText(path, headers = {}) {
  if (typeof path !== 'string' || !path.startsWith('/') || path.startsWith('//')) {
    return { status: null, body: '', problems: [`invalid relative path: ${String(path)}`] }
  }
  try {
    const response = await fetch(`${origin}${path}`, { headers, signal: AbortSignal.timeout(5000) })
    return { status: response.status, body: await response.text(), problems: [] }
  } catch (error) {
    return { status: null, body: '', problems: [`request failed: ${String(error)}`] }
  }
}

async function endpoint(label, path, required, shape = 'object') {
  const response = await fetchText(path, { Accept: 'application/json' })
  const problems = [...response.problems]
  if (response.status !== 200) problems.push(`HTTP ${response.status}`)
  let payload
  try { payload = JSON.parse(response.body) } catch { problems.push('response is not JSON') }
  if (shape === 'array') {
    if (!Array.isArray(payload)) problems.push('expected array')
  } else if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    problems.push('expected object')
  } else {
    for (const key of required) if (!(key in payload)) problems.push(`missing field: ${key}`)
    if (required.includes('records')) {
      if (!Array.isArray(payload.records)) problems.push('records is not an array')
      if (!Number.isInteger(payload.total) || payload.total < 0) problems.push('invalid total')
      if (required.includes('offset') && (payload.offset !== 0 || payload.count !== payload.records?.length)) {
        problems.push('offset/count do not match requested page')
      }
    }
  }
  report.requests.push({ label, path, status: response.status, problems })
  return { status: response.status, problems }
}

async function run() {
  if (!args['app-dir'] || !origin) throw new Error('--app-dir and --origin are required')
  const contract = await import(pathToFileURL(join(args['app-dir'], 'src/api/contract.ts')).href)
  const { API_PATHS: paths, DATASET: datasets, buildQuery, DEFAULT_PAGE_SIZE: size } = contract
  if (!paths || !datasets || typeof paths.records !== 'function' || typeof paths.record !== 'function'
      || typeof buildQuery !== 'function' || !Number.isInteger(size)) {
    throw new Error('frontend contract lacks current dataset/offset-limit interface')
  }
  report.frontend_contract = { datasets, page_size: size }

  const page = await fetchText('/')
  const pageProblems = [...page.problems]
  if (page.status !== 200) pageProblems.push(`GET / returned HTTP ${page.status}`)
  const scripts = [...page.body.matchAll(/<script[^>]+src=["']([^"']+)["']/g)].map(m => m[1])
  const links = [...page.body.matchAll(/<link[^>]+href=["']([^"']+)["']/g)].map(m => m[1])
  if (!scripts.length) pageProblems.push('missing script entry point')
  if ([...scripts, ...links].some(url => !url.startsWith('/') || url.startsWith('//'))) {
    pageProblems.push('entry page must use same-origin relative assets')
  }
  record('W-10', 'entry page uses relative assets', pageProblems, { status: page.status, scripts, links })

  const moduleProblems = []
  for (const path of scripts) {
    const asset = await fetchText(path)
    if (asset.status !== 200) moduleProblems.push(`${path}: HTTP ${asset.status}`)
    moduleProblems.push(...asset.problems)
    // Dev-server tooling can legitimately contain localhost. Only actual URL
    // strings in application entry modules are a signal here, not prose words.
    if (!/^\/@(?:vite|fs|id)\//.test(path) && !path.includes('/node_modules/')
        && /https?:\/\/(?:localhost|127\.0\.0\.1|0\.0\.0\.0)/.test(asset.body)) {
      moduleProblems.push(`${path}: application uses absolute sandbox URL`)
    }
  }
  record('W-11', 'application entry modules are reachable', moduleProblems)

  const listProblems = []
  for (const id of new Set(Object.values(datasets))) {
    const result = await endpoint(id, paths.records(id) + buildQuery({ offset: 0, limit: size }),
      ['dataset', 'total', 'offset', 'limit', 'count', 'records'])
    listProblems.push(...result.problems.map(p => `${id}: ${p}`))
  }
  record('W-12', 'dataset lists use records/total/offset/limit envelopes', listProblems)

  const auxiliary = [
    ['health', paths.health, ['status', 'datasets_count']],
    ['batch', paths.batch, ['batch', 'tables_summary', 'validation_summary', 'native_loader_confirmed']],
    ['datasets', paths.datasets, ['datasets', 'total']],
    ['quarantine', paths.quarantine, ['records', 'total']],
    ['overwrites', paths.overwrites, ['records', 'total']],
    ['missingAptitudes', paths.missingAptitudes, [], 'array'],
    ['ambiguousSkills', paths.ambiguousSkills, [], 'array'],
  ]
  const auxiliaryProblems = []
  for (const [name, path, fields, shape] of auxiliary) {
    const result = await endpoint(name, path, fields, shape)
    auxiliaryProblems.push(...result.problems.map(p => `${name}: ${p}`))
  }
  record('W-13', 'batch and evidence endpoints agree with current contract', auxiliaryProblems)

  const detailProblems = []
  for (const [id, key] of [[datasets.items, '11'], [datasets.pets, '2010'], [datasets.petSkills, '101']]) {
    const result = await endpoint(`${id} detail`, paths.record(id, key), ['_pk'])
    detailProblems.push(...result.problems.map(p => `${id}: ${p}`))
  }
  record('W-14', 'single-record details are reachable', detailProblems)

  const proxied = await endpoint('proxy', paths.records(datasets.items) + buildQuery({ offset: 0, limit: 1 }),
    ['records', 'total', 'offset', 'count'])
  record('W-15', 'web origin proxies the real API', proxied.problems, { status: proxied.status })
  const host = await fetchText('/', { Host: 'review-preview.e2b.app', Origin: 'https://review-preview.e2b.app',
    'X-Forwarded-Proto': 'https' })
  record('W-16', 'preview Host/Origin headers accepted',
    [...host.problems, ...(host.status === 200 ? [] : [`HTTP ${host.status}`])])
}

try { await run() } catch (error) {
  record('W-CONTRACT', 'probe must complete and report errors', [String(error)])
} finally {
  const fail = report.checks.filter(c => c.status === 'fail').length
  report.summary = { total: report.checks.length, pass: report.checks.length - fail, fail }
  report.status = fail ? 'fail' : 'pass'
  const text = JSON.stringify(report, null, 2) + '\n'
  if (args.out) { mkdirSync(dirname(args.out), { recursive: true }); writeFileSync(args.out, text) }
  else console.log(text)
  process.exitCode = fail ? 1 : 0
}
