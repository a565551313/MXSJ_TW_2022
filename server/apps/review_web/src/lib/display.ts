/**
 * Display-only helpers. Nothing here interprets source data: no Simplified /
 * Traditional conversion, no formula evaluation, no rich-text expansion, no
 * "missing means 0" substitution.
 */

/** Shown when the source field itself is empty; never rendered as `0`. */
export const EMPTY_FIELD_MARKER = '（源字段为空）'

/** Shown when the API does not provide a value the page wanted to display. */
export const NOT_PROVIDED_MARKER = '（API 未提供）'

export function rawText(value: unknown): string | null {
  if (value === null || value === undefined) return null
  if (typeof value === 'string') return value
  if (typeof value === 'number') return String(value)
  if (typeof value === 'boolean') return value ? 'true' : 'false'
  try {
    return JSON.stringify(value)
  } catch {
    return String(value)
  }
}

export function rawTextOrMarker(value: unknown): string {
  return rawText(value) ?? EMPTY_FIELD_MARKER
}

export function hasText(value: unknown): boolean {
  const text = rawText(value)
  return text !== null && text.trim().length > 0
}

export function isTrue(value: unknown): boolean {
  if (value === true) return true
  if (typeof value === 'string') return value.trim().toLowerCase() === 'true'
  return false
}

export function formatCount(value: unknown): string {
  const text = rawText(value)
  if (text === null) return NOT_PROVIDED_MARKER
  const parsed = Number(text)
  if (!Number.isFinite(parsed)) return text
  return parsed.toLocaleString('en-US')
}

export function numericOrNull(value: unknown): number | null {
  const text = rawText(value)
  if (text === null || text.trim().length === 0) return null
  const parsed = Number(text)
  return Number.isFinite(parsed) ? parsed : null
}

/** `0` stays `0`: zero NPC ids and zero sequences are real, visible values. */
export function isZeroId(value: unknown): boolean {
  const text = rawText(value)
  if (text === null) return false
  const trimmed = text.trim()
  return trimmed.length > 0 && Number(trimmed) === 0
}

export function pluralCount(count: number, unit: string): string {
  return `${formatCount(count)} ${unit}`
}
