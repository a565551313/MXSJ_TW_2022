/**
 * Runtime structural validation for review API responses.
 *
 * Rules this module enforces:
 *   - every field the UI depends on is checked at runtime (no `as Foo` casts
 *     pretending a response matches a TypeScript interface);
 *   - a JSON body that is *syntactically* valid but structurally different from
 *     the contract produces a `ResponseSchemaError` naming the exact JSON path,
 *     the expected type and what actually arrived;
 *   - missing/odd fields are never silently replaced with `[]`, `0` or `''`, so
 *     a contract mismatch can not masquerade as "no data".
 *
 * JSDoc: "tolerated" inputs are deliberate, documented relaxations of the
 * contract (e.g. an integer sent as a numeric string). Everything else fails.
 */

export interface SchemaIssue {
  path: string
  expected: string
  actual: string
}

/** Raised when a response body does not match Agent H's contract. */
export class ResponseSchemaError extends Error {
  readonly url: string
  readonly issues: SchemaIssue[]
  readonly bodyPreview: string

  constructor(url: string, issues: SchemaIssue[], bodyPreview = '') {
    const summary = issues
      .slice(0, 4)
      .map((issue) => `${issue.path}: 期望 ${issue.expected}，实际 ${issue.actual}`)
      .join('；')
    super(`接口响应结构与契约不符（${issues.length} 处）：${summary}`)
    this.name = 'ResponseSchemaError'
    this.url = url
    this.issues = issues
    this.bodyPreview = bodyPreview
  }
}

export function isResponseSchemaError(error: unknown): error is ResponseSchemaError {
  return error instanceof ResponseSchemaError
}

export function describeValue(value: unknown): string {
  if (value === null) return 'null'
  if (Array.isArray(value)) return `array(${value.length})`
  const type = typeof value
  if (type === 'string') return `string(${JSON.stringify(String(value).slice(0, 40))})`
  if (type === 'number' || type === 'boolean') return `${type}(${String(value)})`
  if (type === 'object') return `object{${Object.keys(value as object).slice(0, 8).join(',')}}`
  return type
}

/**
 * Collects problems while walking a response, then throws once with all of
 * them. Callers read fields through the typed accessors, so an unreported
 * mismatch is impossible: a missing required field always records an issue.
 */
export class Validator {
  readonly issues: SchemaIssue[] = []

  constructor(private readonly url: string) {}

  issue(path: string, expected: string, actual: unknown): void {
    this.issues.push({ path, expected, actual: describeValue(actual) })
  }

  /** Present-and-correct check that also records a missing field. */
  private check(value: unknown, path: string, expected: string, predicate: (value: unknown) => boolean) {
    if (value === undefined) {
      this.issue(path, expected, undefined)
      return false
    }
    if (!predicate(value)) {
      this.issue(path, expected, value)
      return false
    }
    return true
  }

  object(value: unknown, path: string): Record<string, unknown> | null {
    if (!this.check(value, path, 'object', (v) => typeof v === 'object' && v !== null && !Array.isArray(v))) {
      return null
    }
    return value as Record<string, unknown>
  }

  array(value: unknown, path: string): unknown[] | null {
    if (!this.check(value, path, 'array', Array.isArray)) return null
    return value as unknown[]
  }

  requiredString(value: unknown, path: string): string | null {
    if (!this.check(value, path, 'string', (v) => typeof v === 'string')) return null
    return value as string
  }

  /** Tolerates a number sent for a text field only when explicitly requested. */
  stringOrNumberAsText(value: unknown, path: string): string | null {
    if (
      !this.check(value, path, 'string|number', (v) => typeof v === 'string' || typeof v === 'number') 
    ) {
      return null
    }
    return String(value)
  }

  optionalString(value: unknown, path: string): string | null {
    if (value === undefined || value === null) return null
    if (typeof value !== 'string') {
      this.issue(path, 'string|null', value)
      return null
    }
    return value
  }

  requiredNumber(value: unknown, path: string): number | null {
    if (!this.check(value, path, 'number', (v) => typeof v === 'number' && Number.isFinite(v))) return null
    return value as number
  }

  /**
   * Integer field: accepts a real number or an integer-valued string (tolerated,
   * documented relaxation). Rejects floats, empty strings and text.
   */
  intLike(value: unknown, path: string): number | null {
    if (typeof value === 'number' && Number.isInteger(value)) return value
    if (typeof value === 'string' && /^-?\d+$/.test(value.trim())) return Number(value.trim())
    if (value === undefined || value === null) {
      this.issue(path, 'int', value)
      return null
    }
    this.issue(path, 'int', value)
    return null
  }

  numberLike(value: unknown, path: string): number | null {
    if (typeof value === 'number' && Number.isFinite(value)) return value
    if (typeof value === 'string' && value.trim() !== '' && Number.isFinite(Number(value))) {
      return Number(value)
    }
    if (value === undefined || value === null) {
      this.issue(path, 'number', value)
      return null
    }
    this.issue(path, 'number', value)
    return null
  }

  bool(value: unknown, path: string): boolean | null {
    if (typeof value === 'boolean') return value
    // Tolerated: the frozen CSVs store "true"/"false"; the backend normally
    // converts them, but a string literal is still an unambiguous boolean.
    if (typeof value === 'string') {
      const text = value.trim().toLowerCase()
      if (text === 'true') return true
      if (text === 'false') return false
    }
    if (value === undefined || value === null) {
      this.issue(path, 'bool', value)
      return null
    }
    this.issue(path, 'bool', value)
    return null
  }

  /** bool | null, for columns the source itself leaves empty. */
  nullableBool(value: unknown, path: string): boolean | null {
    if (value === null || value === undefined) return null
    return this.bool(value, path)
  }

  /** string | null, for cells the source leaves blank (E legacy convention). */
  nullableText(value: unknown, path: string): string | null {
    if (value === null || value === undefined) return null
    if (typeof value === 'string') return value
    if (typeof value === 'number' || typeof value === 'boolean') return String(value)
    this.issue(path, 'string|number|bool|null', value)
    return null
  }

  /** int | null, for `int_or_empty` columns (null means the source cell was blank). */
  nullableIntLike(value: unknown, path: string): number | null {
    if (value === null || value === undefined) return null
    if (typeof value === 'number' && Number.isInteger(value)) return value
    if (typeof value === 'string') {
      const text = value.trim()
      if (text === '') return null
      if (/^-?\d+$/.test(text)) return Number(text)
    }
    this.issue(path, 'int|null', value)
    return null
  }

  throwIfInvalid(bodyPreview = ''): void {
    if (this.issues.length > 0) {
      throw new ResponseSchemaError(this.url, this.issues, bodyPreview)
    }
  }
}

/**
 * Raw record as returned by the API: typed column values plus the backend
 * generated `_pk` identity.
 */
export type ApiRecord = Record<string, unknown>
