/**
 * Raw JSON value as the backend stores it for quarantined values and overwrite
 * evidence (`{bytes_hex}` / `{dict: [[k, v], …]}` / `{tuple: […]}` / `{list: […]}`).
 *
 * This is the only thing the UI may do with it: show it. No decoding is implied
 * by the type itself - `evidenceName()` decodes CP950 byte runs explicitly, and
 * anything it cannot decode stays on screen as raw hex.
 */
export type RawJson =
  | { bytes_hex: string }
  | { dict: Array<[RawJson, RawJson]> }
  | { tuple: RawJson[] }
  | { list: RawJson[] }
  | string
  | number
  | boolean
  | null
  | RawJson[]
