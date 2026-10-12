/**
 * Real page smoke test (Agent J acceptance tool).
 *
 * A browser engine is not available in this sandbox, so this script does the
 * closest honest thing: it *builds* the delivered front end with Vite (the
 * application's own toolchain, unmodified source) into a temporary IIFE bundle
 * and executes that bundle inside a jsdom document whose `fetch` is wired to the
 * real web origin (Vite dev server / preview, which proxies to the real review
 * API). It then records:
 *
 *   - every console message, unhandled rejection and uncaught error,
 *   - every HTTP request the application issues (status + body preview),
 *   - the rendered text/HTML of `#root` after the first paint settles.
 *
 * That is what turns "HTTP 200 on index.html" into "the page really paints" or
 * "the page really is blank, and here is the error it logged".
 *
 * Limits are reported explicitly: layout, screenshots and a real browser's
 * console require Chrome/Firefox, which this sandbox cannot install.
 *
 * Usage:
 *   node --experimental-strip-types web_ui_smoke.mjs --app-dir <dir> --origin <url> [--out report.json]
 */
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import { join, resolve } from 'node:path'
import { writeFileSync, mkdtempSync, readdirSync, readFileSync } from 'node:fs'
import { tmpdir } from 'node:os'

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
  console.error('usage: web_ui_smoke.mjs --app-dir <dir> --origin <url> [--out file]')
  process.exit(2)
}

const report = {
  stage: 'phase3_web_ui_smoke',
  engine: 'jsdom executing the application own Vite build (no browser engine in this sandbox)',
  origin,
  console: [],
  requests: [],
  checks: [],
  status: 'not_executed',
}
const record = (check, title, status, detail) => {
  report.checks.push({ check, title, status, detail })
}
const safeString = (value) => {
  if (typeof value === 'string') return value
  if (value instanceof Error) return `${value.name}: ${value.message}`
  try {
    return JSON.stringify(value)
  } catch {
    return String(value)
  }
}
const finish = (code) => {
  const failures = report.checks.filter((c) => c.status === 'fail')
  const unexecuted = report.checks.filter((c) => c.status === 'not_executed')
  report.summary = {
    pass: report.checks.filter((c) => c.status === 'pass').length,
    fail: failures.length,
    not_executed: unexecuted.length,
    console_messages: report.console.length,
    requests: report.requests.length,
  }
  report.status = failures.length ? 'fail'
    : (report.checks.length && unexecuted.length === report.checks.length ? 'not_executed' : 'pass')
  const text = JSON.stringify(report, null, 2)
  if (args.out) writeFileSync(args.out, `${text}\n`)
  else console.log(text)
  process.exit(code ?? (report.status === 'fail' ? 1 : 0))
}

const appPath = resolve(appDir)
let require
try {
  require = createRequire(join(appPath, 'package.json'))
} catch (error) {
  record('U-00', 'the application workspace is usable', 'not_executed',
    `cannot resolve modules from ${appPath}: ${error}`)
  finish(3)
}

/* ------------------------------------------------------------------- build */
const outDir = mkdtempSync(join(tmpdir(), 'mxsj-ui-smoke-dist-'))
let bundled = null
try {
  const vite = await import(pathToFileURL(join(appPath, 'node_modules/vite/dist/node/index.js')).href)
  // Resolve the app's own plugin through its package entry (its exports map
  // decides which file that is) instead of guessing a dist filename.
  const reactPluginPath = require.resolve('@vitejs/plugin-react')
  const reactPlugin = await import(pathToFileURL(reactPluginPath).href)
  await vite.build({
    root: appPath,
    configFile: false, // the app's own config is authoritative at runtime; the smoke
                       // build only needs the same toolchain in an IIFE format.
    logLevel: 'error',
    build: {
      outDir,
      emptyOutDir: true,
      minify: false,
      sourcemap: false,
      modulePreload: false,
      rollupOptions: {
        input: join(appPath, 'index.html'),
        output: { format: 'iife', entryFileNames: 'app.js', assetFileNames: 'asset.[ext]' },
      },
    },
    plugins: [reactPlugin.default ? reactPlugin.default() : reactPlugin()],
  })
  const assets = readdirSync(outDir)
  const bundleName = assets.find((name) => name.endsWith('.js'))
  bundled = bundleName ? readFileSync(join(outDir, bundleName), 'utf8') : null
  record('U-01', 'the delivered front end builds with its own toolchain',
    bundled ? 'pass' : 'fail',
    bundled ? { outDir, files: assets } : { outDir, files: assets, problem: 'no javascript bundle produced' })
} catch (error) {
  record('U-01', 'the delivered front end builds with its own toolchain', 'fail',
    `vite build failed: ${safeString(error?.stack || error)}`)
  finish()
}

/* -------------------------------------------------------------------- DOM */
let JSDOM, VirtualConsole
try {
  ;({ JSDOM, VirtualConsole } = require('jsdom'))
} catch (error) {
  record('U-02', 'jsdom available for the render harness', 'not_executed',
    `jsdom is not installed in the application workspace: ${error}`)
  finish(3)
}

const virtualConsole = new VirtualConsole()
const dom = new JSDOM('<!doctype html><html><body><div id="root"></div></body></html>', {
  url: `${origin}/`,
  pretendToBeVisual: true,
  runScripts: 'dangerously',
  virtualConsole,
})
const { window } = dom

for (const level of ['log', 'info', 'warn', 'error', 'debug']) {
  window.console[level] = (...parts) => {
    const message = parts.map(safeString).join(' ')
    report.console.push({ level, message: message.slice(0, 2000) })
  }
}
window.addEventListener('error', (event) => {
  report.console.push({ level: 'uncaught', message: safeString(event.error?.stack || event.message) })
})
window.addEventListener('unhandledrejection', (event) => {
  report.console.push({ level: 'unhandledrejection', message: safeString(event.reason?.stack || event.reason) })
})

// Network capture: the app's relative fetches go to the real web origin.
const nativeFetch = globalThis.fetch
window.fetch = async (input, init) => {
  const url = typeof input === 'string' ? input : input.url
  const absolute = url.startsWith('http') ? url : `${origin}${url.startsWith('/') ? '' : '/'}${url}`
  const entry = { url: absolute, method: (init?.method || 'GET').toUpperCase() }
  report.requests.push(entry)
  try {
    const response = await nativeFetch(absolute, { ...init, redirect: 'follow' })
    const clone = response.clone()
    entry.status = response.status
    entry.content_type = response.headers.get('content-type')
    const text = await clone.text()
    entry.body_preview = text.slice(0, 160)
    if (text.trim().startsWith('{')) {
      const payload = JSON.parse(text)
      if (payload && typeof payload === 'object' && payload.error) {
        entry.problem = `error envelope: ${safeString(payload.error).slice(0, 160)}`
      }
    } else {
      entry.problem = 'response is not JSON (the front end parses JSON)'
    }
    return response
  } catch (error) {
    entry.error = String(error)
    throw error
  }
}
window.AbortController = globalThis.AbortController ?? window.AbortController
window.requestAnimationFrame = (cb) => window.setTimeout(() => cb(Date.now()), 0)
window.cancelAnimationFrame = (id) => window.clearTimeout(id)

/* ------------------------------------------------------------- run the app */
let root, container
try {
  window.eval(bundled)
} catch (error) {
  report.console.push({ level: 'fatal', message: safeString(error?.stack || error) })
}

const settle = Number(args.timeout ?? 6000)
const deadline = Date.now() + settle
try {
  while (Date.now() < deadline) {
    await new Promise((resolvePromise) => setTimeout(resolvePromise, 200))
    container = window.document.getElementById('root')
    const text = (container?.textContent || '').replace(/\s+/g, ' ').trim()
    if (text.length > 20 && report.requests.length > 0) {
      await new Promise((resolvePromise) => setTimeout(resolvePromise, 400))
      break
    }
  }
} catch (error) {
  report.console.push({ level: 'harness', message: safeString(error?.stack || error) })
}
container = window.document.getElementById('root')
const rootText = (container?.textContent || '').replace(/\s+/g, ' ').trim()
const rootHtml = (container?.innerHTML || '').slice(0, 4000)
report.rendered = { text: rootText.slice(0, 600), html: rootHtml }
record('U-02', 'the mounted application renders visible content',
  rootText.length >= 20 ? 'pass' : 'fail',
  rootText.length >= 20 ? { text: rootText.slice(0, 300) }
    : { text: rootText, html: rootHtml.slice(0, 1200),
        hint: 'the bundle executed and mounted, but painted nothing (white screen)' })

const badRequests = report.requests.filter((r) => r.status !== 200 || r.problem)
record('U-03', 'every request the application issues succeeds',
  report.requests.length === 0 ? 'fail' : (badRequests.length ? 'fail' : 'pass'),
  report.requests.length === 0 ? { problem: 'the application issued no request at all' }
    : (badRequests.length ? badRequests.slice(0, 12) : { requests: report.requests.slice(0, 8) }))

const appConsoleErrors = report.console.filter((m) => m.level === 'error' || m.level === 'uncaught'
  || m.level === 'unhandledrejection' || m.level === 'fatal')
record('U-04', 'the application reports no console error while loading',
  appConsoleErrors.length ? 'fail' : 'pass', appConsoleErrors.slice(0, 12))

record('U-05', 'real-browser-only checks', 'not_executed',
  'jsdom does not execute real-browser checks; set REVIEW_BROWSER_TOOLS for the separate Chromium probe')

dom.window.close()
finish()
