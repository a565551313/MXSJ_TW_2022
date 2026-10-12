import type { ReactNode } from 'react'
import type { RawJson } from '../api/types'
import { asciiHint } from '../lib/hex'
import { ByteHexView } from './ByteHexView'
import { SafeText } from './SafeText'

function isBytesObject(value: unknown): value is { bytes_hex: string } {
  return (
    typeof value === 'object' &&
    value !== null &&
    'bytes_hex' in value &&
    typeof (value as { bytes_hex?: unknown }).bytes_hex === 'string'
  )
}

function isDictObject(value: unknown): value is { dict: Array<[RawJson, RawJson]> } {
  return typeof value === 'object' && value !== null && Array.isArray((value as { dict?: unknown }).dict)
}

function isTupleObject(value: unknown): value is { tuple: RawJson[] } {
  return (
    typeof value === 'object' && value !== null && Array.isArray((value as { tuple?: unknown }).tuple)
  )
}

function isListObject(value: unknown): value is { list: RawJson[] } {
  return typeof value === 'object' && value !== null && Array.isArray((value as { list?: unknown }).list)
}

/**
 * Renders the typed JSON evidence tree used by quarantine.jsonl /
 * overwrite_evidence.jsonl (bytes as `{bytes_hex}`, mappings as `{dict: [...]}`,
 * sequences as `{tuple: [...]}` / `{list: [...]}`).
 *
 * Boundaries: only values whose bytes are all printable ASCII may show an ASCII
 * hint, and that hint is attached to *structure keys* (like the byte-encoded
 * field name `name`). Source values are always rendered as hex.
 */
export function RawJsonView({ value, depth = 0 }: { value: RawJson; depth?: number }): ReactNode {
  if (isBytesObject(value)) {
    return <ByteHexView hex={value.bytes_hex} />
  }

  if (isDictObject(value)) {
    return (
      <dl className="raw-dict">
        {value.dict.map((pair, index) => {
          const [key, entryValue] = pair
          const keyHex = isBytesObject(key) ? key.bytes_hex : null
          const hint = keyHex ? asciiHint(keyHex) : null
          return (
            <div className="raw-dict__row" key={index}>
              <dt>
                {keyHex ? (
                  <ByteHexView hex={keyHex} label={`键 #${index}`} asciiHintText={hint} />
                ) : (
                  <RawJsonView value={key} depth={depth + 1} />
                )}
              </dt>
              <dd>
                <RawJsonView value={entryValue} depth={depth + 1} />
              </dd>
            </div>
          )
        })}
      </dl>
    )
  }

  if (isTupleObject(value) || isListObject(value)) {
    const entries = isTupleObject(value) ? value.tuple : value.list
    const kind = isTupleObject(value) ? 'tuple' : 'list'
    return (
      <ol className="raw-seq" data-raw-seq={kind}>
        {entries.map((entry, index) => (
          <li key={index}>
            <RawJsonView value={entry} depth={depth + 1} />
          </li>
        ))}
      </ol>
    )
  }

  if (Array.isArray(value)) {
    return (
      <ol className="raw-seq" data-raw-seq="array">
        {value.map((entry, index) => (
          <li key={index}>
            <RawJsonView value={entry} depth={depth + 1} />
          </li>
        ))}
      </ol>
    )
  }

  if (typeof value === 'object' && value !== null) {
    return <pre className="raw-fallback">{JSON.stringify(value, null, 2)}</pre>
  }

  return <SafeText value={value} />
}
