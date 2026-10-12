/**
 * Types for the capture replay module (see replay.mjs).
 *
 * The replayed bodies are typed loosely on purpose: they are *test and demo*
 * data. The application never imports this module, and the runtime client still
 * validates every response structurally before any page can use it.
 */
export declare const REVIEW_PREFIX: string
export interface ReplayCapture {
  id: string
  method: string
  path: string
  query: string
  status: number
  file: string
  sha256: string
  bytes: number
  body: any
}
export interface ReplayBundle {
  dir: string
  manifest: { _capture: { provenance: string; capture_count: number; [key: string]: unknown }; captures: any[] }
  captures: ReplayCapture[]
}
export declare function loadReplay(dir: string): ReplayBundle
export declare function describeReplay(replay: ReplayBundle): string
export declare function respond(
  replay: ReplayBundle,
  request: { method?: string; pathname?: string; searchParams?: URLSearchParams | string },
): { status: number; body: unknown; replay: { capture_id: string | null; mode: string } }
