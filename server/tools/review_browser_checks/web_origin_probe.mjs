/**
 * Browser-origin contract probe (Agent J acceptance tool, not a product file).
 *
 * It asks the *real* front end what it is going to request — by importing
 * `src/api/contract.ts` (the single adaptation point the front end documents) —
 * and then issues exactly those requests against the real web origin (Vite dev
 * server / preview), which proxies to the real Python review API.
 *
 * This is what catches "HTML returns 200 but the page is blank": the entry page
 * can be served while every data path 404s or returns a different envelope than
 * the front end parses.
 *
 * Usage:
 *   node --experimental-strip-types web_origin_probe.mjs --app-dir <dir> --origin <url> [--out report.json]
 */
import { writeFileSync } from 'node:fs'
import { pathToFileURL } from 'node:url'
import { join } from 'node:path'

function parseArgs(argv) {
  const args = {}
  for (let i = 0; i < argv.length; i += 1) {
    const key = argv[i]
    if (key.startsWith('--')) {
      const value = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : 'true'
      args[key.slice(2)] = value
    }
  }
  return args
}

const args = parseArgs(process.argv.slice(2))
const appDir = args['app-dir']
const origin = (args.origin || '').replace(/\/$/, '')
if (!appDir || !origin) {
  console.error('usage: web_origin_probe.mjs --app-dir <dir> --origin <url> [--out file]')
  process.exit(2)
}

const contract = await import(pathToFileURL(join(appDir, 'src/api/contract.ts')).href)
const API_PATHS = contract.API_PATHS
const DEFAULT_PAGE_SIZE = contract.DEFAULT_PAGE_SIZE ?? 25

const report = {
  stage: 'phase3_web_origin_contract',
  origin,
  frontend_contract: { API_PATHS, DEFAULT_PAGE_SIZE },
  checks: [],
  requests: [],
}

function record(check, title, status, detail) {
  report.checks.push({ check, title, status, detail })
}

/* ---------------------------------------------------------------- page HTML */
async function fetchText(path, headers = {}) {
  const response = await fetch(`${origin}${path}`, { headers: { Accept: '*/*', ...headers } })
  return { status: response.status, headers: Object.fromEntries(response.headers), body: await response.text() }
}

const page = await fetchText('/')
const absoluteHostRe = /(?:src|href)\s*=\s*["']https?:\/\/(?:localhost|127\.0\.0\.1|0\.0\.0\.0)/i
const pageProblems = []
if (page.status !== 200) pageProblems.push(`GET / returned HTTP ${page.status}`)
if (/(localhost|127\.0\.0\.1|0\.0\.0\.0)/.test(page.body)) {
  pageProblems.push('the served HTML mentions a sandbox host')
}
if (absoluteHostRe.test(page.body)) pageProblems.push('an asset is loaded from an absolute sandbox URL')
const scriptSrcs = [...page.body.matchAll(/<script[^>]+src=["']([^"']+)["']/g)].map((m) => m[1])
const linkHrefs = [...page.body.matchAll(/<link[^>]+href=["']([^"']+)["']/g)].map((m) => m[1])
if (!scriptSrcs.length) pageProblems.push('the served HTML has no <script src> entry point')
record('W-10', 'entry page is served by the web origin with relative assets',
  pageProblems.length ? 'fail' : 'pass',
  { status: page.status, scripts: scriptSrcs, links: linkHrefs, problems: pageProblems })

/* --------------------------------------------------------- entry module(s) */
const moduleProblems = []
const moduleResults = []
// `/@vite/*`, `/@fs/*`, `/@id/*` and `/node_modules/*` are dev-server tooling,
// not application modules: Vite's own client legitimately contains "localhost".
const isDevServerModule = (src) => /^\/(@vite|@fs|@id)\//.test(src) || src.includes('/node_modules/')
for (const src of scriptSrcs.filter((s) => s.startsWith('/'))) {
  const asset = await fetchText(src)
  const entry = { src, status: asset.status, bytes: asset.body.length,
                  kind: isDevServerModule(src) ? 'dev-server' : 'application' }
  moduleResults.push(entry)
  if (asset.status !== 200) moduleProblems.push(`${src} returned HTTP ${asset.status}`)
  if (asset.status === 200 && entry.kind === 'application'
      && /(localhost|127\.0\.0\.1|0\.0\.0\.0)/.test(asset.body)) {
    moduleProblems.push(`${src} contains a sandbox host reference`)
  }
}
record('W-11', 'the page entry module loads and holds no sandbox host', moduleProblems.length ? 'fail' : 'pass',
  { modules: moduleResults, problems: moduleProblems })

/* ----------------------------------------------- every endpoint the app uses */
const EXPECTED_ENVELOPES = {
  '/api/v1/review/batch': { required: ['batch'], shape: 'object' },
  '/api/v1/review/datasets': { required: ['datasets'], shape: 'object' },
  '/api/v1/review/quarantine': { required: ['records'], shape: 'object' },
  '/api/v1/review/overwrites': { required: ['records'], shape: 'object' },
  '/api/v1/review/missing-aptitudes': { required: [], shape: 'array' },
  '/api/v1/review/ambiguous-skills': { required: [], shape: 'array' },
}
// The front end's list pages parse `Page<T> = { items, total, page, page_size }`.
const LIST_REQUIRED = ['items', 'total', 'page', 'page_size']

const listEndpoints = ['items', 'pets', 'skills'].map((key) => ({
  label: key,
  path: `${API_PATHS[key]}?page=1&page_size=${DEFAULT_PAGE_SIZE}`,
}))
const objectEndpoints = [
  { label: 'batch', path: API_PATHS.batch },
  { label: 'anomalies', path: API_PATHS.anomalies },
  { label: 'mapDatasets', path: API_PATHS.mapDatasets },
  { label: 'npcs', path: `${API_PATHS.npcs}?source=2601&page=1&page_size=${DEFAULT_PAGE_SIZE}` },
  { label: 'npcAgreement', path: `${API_PATHS.npcAgreement}?page=1&page_size=${DEFAULT_PAGE_SIZE}` },
]
const detailEndpoints = [
  { label: 'item detail', path: `${API_PATHS.items}/11` },
  { label: 'pet detail', path: `${API_PATHS.pets}/1010` },
  { label: 'skill detail', path: `${API_PATHS.skills}/101` },
]

async function probeEndpoint(entry, requiredKeys, listLike) {
  let response
  let body
  try {
    const result = await fetchText(entry.path, { Accept: 'application/json' })
    response = result
    body = result.body
  } catch (error) {
    report.requests.push({ label: entry.label, path: entry.path, error: String(error) })
    return { label: entry.label, path: entry.path, status: null, ok: false,
             problem: `request failed: ${error}` }
  }
  let payload = null
  let parsed = false
  try {
    payload = JSON.parse(body)
    parsed = true
  } catch {
    parsed = false
  }
  const problems = []
  if (response.status !== 200) problems.push(`HTTP ${response.status}`)
  if (response.status === 200 && !parsed) problems.push('response is not JSON')
  if (parsed && requiredKeys.length) {
    const actual = listLike ? (Array.isArray(payload) ? '<array>' : Object.keys(payload))
      : Object.keys(payload)
    const missing = requiredKeys.filter((key) => !(payload && typeof payload === 'object' && key in payload))
    if (missing.length) {
      problems.push(`missing keys ${JSON.stringify(missing)} (got ${JSON.stringify(actual)})`)
    }
  }
  const record_ = { label: entry.label, path: entry.path, status: response.status, parsed,
                    keys: parsed && payload && typeof payload === 'object' && !Array.isArray(payload)
                      ? Object.keys(payload) : (Array.isArray(payload) ? '<array>' : null),
                    problems }
  report.requests.push(record_)
  return record_
}

const entryProblems = []
for (const entry of listEndpoints) {
  const result = await probeEndpoint(entry, LIST_REQUIRED, true)
  if (result.problems.length) {
    entryProblems.push(`${entry.label} (${entry.path}): ${result.problems.join('; ')}`)
  }
}
record('W-12', 'the list pages get the {items,total,page,page_size} envelope they parse',
  entryProblems.length ? 'fail' : 'pass', entryProblems.length ? entryProblems : report.requests.slice(-3))

const objectProblems = []
for (const entry of objectEndpoints) {
  const key = entry.path.split('?')[0]
  const spec = EXPECTED_ENVELOPES[key] || { required: [] }
  const result = await probeEndpoint(entry, spec.required, false)
  if (result.problems.length) {
    objectProblems.push(`${entry.label} (${entry.path}): ${result.problems.join('; ')}`)
  }
}
record('W-13', 'the overview/anomaly/npc/map pages get their endpoints',
  objectProblems.length ? 'fail' : 'pass', objectProblems.length ? objectProblems : 'all reachable')

const detailProblems = []
for (const entry of detailEndpoints) {
  const result = await probeEndpoint(entry, ['_pk'], false)
  if (result.problems.length) detailProblems.push(`${entry.label} (${entry.path}): ${result.problems.join('; ')}`)
}
record('W-14', 'detail pages resolve a single record', detailProblems.length ? 'fail' : 'pass',
  detailProblems.length ? detailProblems : 'all reachable')

/* ----------------------------------------------- the API behind the proxy */
const proxied = await probeEndpoint({ label: 'api-through-proxy', path: '/api/v1/review/datasets/items/records?offset=0&limit=1' },
  ['records', 'total'], false)
record('W-15', 'the web origin proxies /api to the review API', proxied.problems.length ? 'fail' : 'pass',
  { status: proxied.status, problems: proxied.problems })

/* ------------------------------------------- proxy header compatibility */
let headerCheck = { status: null }
try {
  const response = await fetch(`${origin}/`, { headers: { Host: 'review-preview.e2b.app',
    Origin: 'https://review-preview.e2b.app', 'X-Forwarded-Proto': 'https' } })
  headerCheck = { status: response.status }
} catch (error) {
  headerCheck = { status: null, error: String(error) }
}
record('W-16', 'the web origin tolerates a proxied Host/Origin header',
  headerCheck.status === 200 ? 'pass' : 'fail', headerCheck)

const failures = report.checks.filter((c) => c.status === 'fail')
report.summary = {
  total: report.checks.length,
  pass: report.checks.filter((c) => c.status === 'pass').length,
  fail: failures.length,
}
report.status = failures.length ? 'fail' : 'pass'
report.status_meaning = {
  pass: 'every path the front end requests is served with the envelope it parses',
  fail: 'the entry page is served, but the application cannot load its data',
}[report.status]

const text = JSON.stringify(report, null, 2)
if (args.out) writeFileSync(args.out, `${text}\n`)
else console.log(text)
process.exit(report.status === 'fail' ? 1 : 0)
