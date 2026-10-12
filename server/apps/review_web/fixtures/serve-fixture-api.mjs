#!/usr/bin/env node
/**
 * EXPLICIT, NON-DEFAULT fixture API server.
 *
 *   npm run fixture:api          # http://127.0.0.1:8788/api/v1/review/...
 *   npm run dev:fixture          # Vite with the proxy pointed at this server
 *
 * It replays the committed captures of Agent H's real review API
 * (`fixtures/h_api/`, produced by `fixtures/capture_h_api.py`). The default
 * `npm run dev` never uses this: it proxies to the Python review API.
 *
 * Nothing here is integration evidence: a replay answers only requests that were
 * captured, with the rows the backend returned, and any other request is
 * answered with an explicit FIXTURE_CAPTURE_MISSING error instead of invented
 * data. The UI shows a permanent banner whenever this mode is active.
 */
import http from 'node:http'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'
import { describeReplay, loadReplay, respond } from './h_api/replay.mjs'

const HERE = dirname(fileURLToPath(import.meta.url))
const CAPTURE_DIR = join(HERE, 'h_api')

const PORT = Number(process.env.FIXTURE_API_PORT || 8788)
// Loopback only: this server is reached by the Vite proxy inside the sandbox,
// never by the user's browser. The app talks to its own origin's /api/... path.
const HOST = process.env.FIXTURE_API_HOST || '127.0.0.1'

const replay = loadReplay(CAPTURE_DIR)
console.log(`[fixture-api] replaying ${describeReplay(replay)}`)
console.log(`[fixture-api] NOT real data, NOT integration evidence. Endpoints: /api/v1/review/*`)

const server = http.createServer((request, response) => {
  const url = new URL(request.url ?? '/', `http://${request.headers.host ?? 'localhost'}`)
  const method = request.method ?? 'GET'

  const { status, body, replay: meta } = respond(replay, {
    method,
    pathname: url.pathname,
    searchParams: url.searchParams,
  })
  const payload = JSON.stringify(body, null, 2)

  response.writeHead(status, {
    'content-type': 'application/json; charset=utf-8',
    'content-length': Buffer.byteLength(payload),
    'cache-control': 'no-store',
    'x-review-fixture': 'true',
    'x-review-fixture-capture': meta.capture_id ?? 'none',
  })
  response.end(method === 'HEAD' ? undefined : payload)
})

server.listen(PORT, HOST, () => {
  console.log(`[fixture-api] listening on http://${HOST}:${PORT}`)
})
