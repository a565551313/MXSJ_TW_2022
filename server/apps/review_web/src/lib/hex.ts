/**
 * Hex rendering for preserved raw bytes.
 *
 * Requirement: invalid CP950 bytes are shown as hexadecimal. They are never
 * decoded, never replaced by a mojibake placeholder, and never presented as a
 * normal name. The only decoding-ish helper in this module is `asciiHint`,
 * which is restricted to bytes in the printable ASCII range and is only ever
 * used for JSON *structure keys* such as `name` / `desc` - never for values.
 */

export interface HexView {
  /** Lower-case two-digit hex bytes. */
  bytes: string[]
  byteLength: number
  /** True when the input was not clean hexadecimal and was preserved verbatim. */
  malformed: boolean
}

export function hexBytes(input: string | null | undefined): HexView {
  const text = (input ?? '').trim()
  if (text.length === 0) return { bytes: [], byteLength: 0, malformed: false }
  const clean = text.replace(/[^0-9a-fA-F]/g, '')
  const malformed = clean.length % 2 !== 0 || clean.length !== text.replace(/[\s:]/g, '').length
  const bytes: string[] = []
  for (let i = 0; i + 1 < clean.length + 1; i += 2) {
    const pair = clean.slice(i, i + 2)
    if (pair.length === 2) bytes.push(pair.toLowerCase())
  }
  return { bytes, byteLength: bytes.length, malformed }
}

/** Space separated, e.g. `c2 f9 a4 48 ...`. */
export function formatHexGroups(input: string | null | undefined): string {
  return hexBytes(input).bytes.join(' ')
}

export function byteLengthOf(input: string | null | undefined): number {
  return hexBytes(input).byteLength
}

/**
 * Printable-ASCII-only hint, e.g. `6e616d65` -> `name`.
 * Returns null unless *every* byte is in `0x20..0x7e`, so invalid CP950 byte
 * runs (like item 72548's name) can never be turned into a fake name.
 */
export function asciiHint(input: string | null | undefined): string | null {
  const { bytes } = hexBytes(input)
  if (bytes.length === 0) return null
  let out = ''
  for (const byte of bytes) {
    const code = Number.parseInt(byte, 16)
    if (!Number.isFinite(code) || code < 0x20 || code > 0x7e) return null
    out += String.fromCharCode(code)
  }
  return out
}

/** Splits a long hex run into rows of `perRow` bytes for monospace display. */
export function hexRows(input: string | null | undefined, perRow = 16): string[] {
  const { bytes } = hexBytes(input)
  const rows: string[] = []
  for (let i = 0; i < bytes.length; i += perRow) {
    rows.push(bytes.slice(i, i + perRow).join(' '))
  }
  return rows
}
