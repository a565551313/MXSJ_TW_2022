import type { ReactNode } from 'react'
import { EMPTY_FIELD_MARKER, rawText } from '../lib/display'

/**
 * Safe rendering of opaque source text.
 *
 * The value is inserted as a React text child, so React escapes it. There is no
 * `dangerouslySetInnerHTML`, no formula evaluation and no client rich-text
 * marker expansion anywhere in this app: `#r`, `#n`, `[@...]` and similar
 * sequences stay exactly as they appear in the source bytes.
 */
export function SafeText({
  value,
  className,
  empty = EMPTY_FIELD_MARKER,
}: {
  value: unknown
  className?: string
  empty?: ReactNode
}) {
  const text = rawText(value)
  if (text === null || text.length === 0) {
    return <span className="muted">{empty}</span>
  }
  return (
    <span className={className} data-testid="safe-text">
      {text}
    </span>
  )
}

/** Monospace variant for formula-ish fields that must only be displayed. */
export function SafeFormula({ value }: { value: unknown }) {
  const text = rawText(value)
  if (text === null || text.length === 0) {
    return <span className="muted">{EMPTY_FIELD_MARKER}</span>
  }
  return (
    <code className="formula-raw" data-testid="safe-formula">
      {text}
    </code>
  )
}
