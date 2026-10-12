/**
 * Architecture guards for the review browser.
 *
 * These read the app's own source files and fail if the runtime bundle starts
 * depending on test fixtures, on unsafe HTML injection, on an executable
 * formula path, or on an absolute sandbox URL.
 */
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs'
import { dirname, join, relative } from 'node:path'
import { describe, expect, it } from 'vitest'

/** Walks up from the working directory until the app's package.json is found. */
function findAppDir(): string {
  let current = process.cwd()
  for (let depth = 0; depth < 6; depth += 1) {
    if (existsSync(join(current, 'package.json')) && existsSync(join(current, 'src'))) {
      return current
    }
    current = dirname(current)
  }
  throw new Error(`could not locate the review_web app directory from ${process.cwd()}`)
}

const APP_DIR = findAppDir()
const SRC_DIR = join(APP_DIR, 'src')

function walk(dir: string, out: string[] = []): string[] {
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry)
    if (statSync(full).isDirectory()) {
      walk(full, out)
    } else {
      out.push(full)
    }
  }
  return out
}

const allFiles = walk(SRC_DIR).map((file) => file.split('\\').join('/'))
const productionFiles = allFiles.filter(
  (file) =>
    /\.(ts|tsx)$/.test(file) &&
    !file.endsWith('.test.ts') &&
    !file.endsWith('.test.tsx') &&
    !file.includes('/src/test/'),
)

function read(file: string): string {
  return readFileSync(file, 'utf-8')
}

/**
 * Removes block and line comments so that a comment *documenting* that we never
 * use `dangerouslySetInnerHTML` cannot itself trip the guard.
 */
function stripComments(source: string): string {
  return source.replace(/\/\*[\s\S]*?\*\//g, '').replace(/(^|[^:])\/\/.*$/gm, '$1')
}

describe('architecture guards', () => {
  it('found production sources to inspect', () => {
    expect(productionFiles.length).toBeGreaterThan(8)
  })

  it('keeps test fixtures out of the production bundle', () => {
    for (const file of productionFiles) {
      const text = read(file)
      const label = relative(APP_DIR, file)
      expect(text, `${label} must not import test fixtures`).not.toMatch(/from\s+['"][^'"]*fixtures\//)
      expect(text, `${label} must not import src/test helpers`).not.toMatch(/from\s+['"][^'"]*\/test\//)
      expect(text, `${label} must not reference the fixture sample`).not.toContain('batch001.sample')
      expect(text, `${label} must not reference the fixture server`).not.toContain('contractHandler')
    }
  })

  it('never injects raw HTML or evaluates source text', () => {
    for (const file of productionFiles) {
      const text = stripComments(read(file))
      const label = relative(APP_DIR, file)
      expect(text, `${label} must not use dangerouslySetInnerHTML`).not.toContain('dangerouslySetInnerHTML')
      expect(text, `${label} must not assign innerHTML`).not.toMatch(/\.innerHTML\s*=/)
      expect(text, `${label} must not use outerHTML`).not.toMatch(/\.outerHTML\s*=/)
      expect(text, `${label} must not call eval`).not.toMatch(/\beval\s*\(/)
      expect(text, `${label} must not build functions from strings`).not.toMatch(/new\s+Function\s*\(/)
      expect(text, `${label} must not call document.write`).not.toContain('document.write')
    }
  })

  it('only ever targets relative /api paths from the browser', () => {
    for (const file of productionFiles) {
      const text = read(file)
      const label = relative(APP_DIR, file)
      expect(text, `${label} must not hardcode a host`).not.toMatch(/https?:\/\/(localhost|127\.0\.0\.1|0\.0\.0\.0)/)
      expect(text, `${label} must not contain an absolute http URL`).not.toMatch(/['"`]https?:\/\//)
    }
  })

  it('keeps the client read-only (GET only)', () => {
    const client = read(join(SRC_DIR, 'api', 'client.ts'))
    expect(client).not.toMatch(/method:\s*'(POST|PUT|PATCH|DELETE)'/)
    const contract = read(join(SRC_DIR, 'api', 'contract.ts'))
    expect(client).toContain("method: 'GET'")
    expect(contract).toContain("'/api/v1/review'")
  })

  it('binds the dev server to 0.0.0.0 and allows the preview host through the proxy', () => {
    const config = read(join(APP_DIR, 'vite.config.ts'))
    expect(config).toMatch(/host:\s*'0\.0\.0\.0'/)
    expect(config).toMatch(/allowedHosts/)
    expect(config).toMatch(/proxy/)
    expect(config).toContain("'/api'")
  })

  it('keeps the fixture API on loopback so only the proxy can reach it', () => {
    const server = read(join(APP_DIR, 'fixtures', 'serve-fixture-api.mjs'))
    expect(server).toContain("'127.0.0.1'")
    expect(server).toContain('NOT real data, NOT integration evidence')
  })

  it('documents the pending integration status in the contract module', () => {
    const contract = read(join(SRC_DIR, 'api', 'contract.ts'))
    expect(contract).toContain('API_CONTRACT.md')
    expect(contract).toContain('PENDING')
    expect(contract).toContain('NOT been verified')
  })
})
