import { hexBytes, hexRows } from '../lib/hex'

/**
 * Renders preserved raw bytes as hexadecimal.
 *
 * Invalid CP950 byte runs (for example item 72548's name) are shown here as hex.
 * They are never decoded, never replaced by a replacement character, and never
 * displayed as if they were a normal name.
 */
export function ByteHexView({
  hex,
  label,
  asciiHintText,
}: {
  hex: string | null | undefined
  label?: string
  /** Only ever supplied for JSON structure keys, never for source values. */
  asciiHintText?: string | null
}) {
  const view = hexBytes(hex)
  const rows = hexRows(hex)

  if (view.byteLength === 0) {
    return (
      <span className="muted">
        {label ? `${label}：` : ''}（无字节）
      </span>
    )
  }

  return (
    <span className="byte-hex">
      {label ? <span className="byte-hex__label">{label}：</span> : null}
      {asciiHintText ? <code className="byte-hex__hint">{asciiHintText}</code> : null}
      <code className="byte-hex__body" data-testid="byte-hex">
        {rows.map((row, index) => (
          <span key={index} className="byte-hex__row">
            {row}
          </span>
        ))}
      </code>
      <span className="byte-hex__meta">
        {view.byteLength} 字节（十六进制，未解码{view.malformed ? '，输入不是规范十六进制' : ''}）
      </span>
    </span>
  )
}
