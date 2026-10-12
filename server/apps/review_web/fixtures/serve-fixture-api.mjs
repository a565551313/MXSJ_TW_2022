#!/usr/bin/env node
/**
 * EXPLICIT, NON-DEFAULT fixture API server.
 *
 *   npm run fixture:api          # http://127.0.0.1:8788/api/v1/review/...
 *   npm run dev:fixture          # Vite with the proxy pointed at this server
 *
 * The default `npm run dev` never uses this: it proxies to the Python review
 * API. Nothing here is integration evidence, and the UI shows a permanent
 * fixture banner whenever the fixture mode is active.
 */
import http from 'node:http'
import { handleRequest, loadFixture, fixturePath } from './contractHandler.mjs'

const PORT = Number(process.env.FIXTURE_API_PORT || 8788)
// Loopback only: this server is reached by the Vite proxy inside the sandbox,
// never by the user's browser. The app talks to its own origin's /api/... path.
const HOST = process.env.FIXTURE_API_HOST || '127.0.0.1'

const fixture = loadFixture()
console.log(`[fixture-api] serving ${fixturePath()}`)
console.log(`[fixture-api] NOT real data, NOT integration evidence. Endpoints: /api/v1/review/*`)

const server = http.createServer((request, response) => {
  const url = new URL(request.url ?? '/', `http://${request.headers.host ?? 'localhost'}`)
  const method = request.method ?? 'GET'

  if (method !== 'GET' && method !== 'HEAD') {
    response.writeHead(405, { 'content-type': 'application/json; charset=utf-8', allow: 'GET, HEAD' })
    response.end(
      JSON.stringify({ error: { code: 'METHOD_NOT_ALLOWED', message: '复核界面是只读的：夹具服务同样只接受 GET。' } }),
    )
    return
  }

  const { status, body } = handleRequest(fixture, url.pathname, url.searchParams)
  const payload = JSON.stringify(body, null, 2)
  response.writeHead(status, {
    'content-type': 'application/json; charset=utf-8',
    'content-length': Buffer.byteLength(payload),
    'cache-control': 'no-store',
    'x-review-fixture': 'true',
  })
  response.end(method === 'HEAD' ? undefined : payload)
})

server.listen(PORT, HOST, () => {
  console.log(`[fixture-api] listening on http://${HOST}:${PORT}`)
})
