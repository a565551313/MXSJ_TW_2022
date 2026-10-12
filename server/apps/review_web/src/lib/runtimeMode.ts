/**
 * Runtime data mode.
 *
 * `api`      - the only default. Talks to `/api/v1/review/...`; on failure the
 *              UI shows an error and never substitutes fixture data.
 * `fixture`  - opt-in, explicit (`npm run dev:fixture`), marked by a permanent
 *              banner. Serves a small curated batch_001 sample from
 *              `fixtures/` for UI work and for tests. It is NOT integration
 *              evidence and must never be described as such.
 */
export type DataMode = 'api' | 'fixture'

export const DATA_MODE: DataMode =
  import.meta.env.VITE_REVIEW_DATA_MODE === 'fixture' ? 'fixture' : 'api'

export const IS_FIXTURE_MODE = DATA_MODE === 'fixture'
