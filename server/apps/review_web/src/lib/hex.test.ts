import { describe, expect, it } from 'vitest'
import { asciiHint, byteLengthOf, formatHexGroups, hexBytes, hexRows } from './hex'

describe('hex helpers', () => {
  it('formats preserved bytes as lower-case hex groups', () => {
    expect(formatHexGroups('c2f9a448a7a4c34dc5e9c5e784')).toBe('c2 f9 a4 48 a7 a4 c3 4d c5 e9 c5 e7 84')
    expect(byteLengthOf('c2f9a448a7a4c34dc5e9c5e784')).toBe(13)
  })

  it('keeps empty input empty instead of inventing bytes', () => {
    expect(hexBytes('').byteLength).toBe(0)
    expect(formatHexGroups(null)).toBe('')
    expect(byteLengthOf(undefined)).toBe(0)
  })

  it('wraps long byte runs into rows', () => {
    const rows = hexRows('00112233445566778899aabbccddeeff0102', 8)
    expect(rows).toHaveLength(3)
    expect(rows[0]).toBe('00 11 22 33 44 55 66 77')
    expect(rows[2]).toBe('01 02')
  })

  it('never produces an ASCII hint for invalid CP950 bytes of item 72548', () => {
    // DATA[72548][0] name bytes from quarantine.jsonl
    expect(asciiHint('c2f9a448a7a4c34dc5e9c5e784')).toBeNull()
    // and definitely not a decoded replacement character
    expect(asciiHint('c2f9a448a7a4c34dc5e9c5e784')).not.toBe('���')
  })

  it('only produces an ASCII hint for printable ASCII structure keys', () => {
    expect(asciiHint('6e616d65')).toBe('name')
    expect(asciiHint('64657363')).toBe('desc')
    expect(asciiHint('00ff')).toBeNull()
    expect(asciiHint('a9c0b0caa44f')).toBeNull()
  })
})
