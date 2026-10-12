/**
 * Fixture implementation of the *expected* review API surface.
 *
 * Used in exactly two places:
 *   1. `fixtures/serve-fixture-api.mjs` - the explicit, non-default fixture dev
 *      server behind `npm run dev:fixture`.
 *   2. The automated test suite, so tests exercise the same request/response
 *      shapes that the fixture demo shows.
 *
 * It is NOT a data source for the application, it is NOT integration evidence,
 * and the default run mode never touches it.
 */
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

export const REVIEW_PREFIX = '/api/v1/review'

const HERE = dirname(fileURLToPath(import.meta.url))
const FIXTURE_PATH = join(HERE, 'batch001.sample.json')

export function fixturePath() {
  return FIXTURE_PATH
}

export function loadFixture() {
  return JSON.parse(readFileSync(FIXTURE_PATH, 'utf8'))
}

function asText(value) {
  if (value === null || value === undefined) return ''
  return String(value)
}

function toPage(rows, searchParams) {
  const page = Math.max(1, Number.parseInt(searchParams.get('page') ?? '1', 10) || 1)
  const pageSize = Math.max(1, Math.min(200, Number.parseInt(searchParams.get('page_size') ?? '25', 10) || 25))
  const start = (page - 1) * pageSize
  return {
    items: rows.slice(start, start + pageSize),
    total: rows.length,
    page,
    page_size: pageSize,
  }
}

function notFound(message) {
  return { status: 404, body: { error: { code: 'NOT_FOUND', message } } }
}

function badRequest(message) {
  return { status: 400, body: { error: { code: 'INVALID_ARGUMENT', message } } }
}

function matchesText(haystack, needle) {
  if (!needle) return true
  return asText(haystack).toLowerCase().includes(needle.toLowerCase())
}

function aptitudStatusOf(fixture, petId) {
  const quarantined = fixture.anomalies.quarantine.find(
    (record) => asText(record.record_key) === asText(petId) && asText(record.entry_index) === '2954',
  )
  if (quarantined) {
    return {
      status: 'quarantined',
      reason: quarantined.reasons.join(', '),
      evidence_id: quarantined.anomaly_id,
    }
  }
  if (fixture.pet_aptitudes.some((row) => row.client_shape_id === petId)) {
    return { status: 'present', reason: null, evidence_id: null }
  }
  const missing = fixture.pet_aptitude_missing.find((row) => row.client_shape_id === petId)
  if (missing) {
    return { status: 'missing_in_source_table', reason: missing.reason, evidence_id: null }
  }
  return { status: 'unknown', reason: null, evidence_id: null }
}

function matchesForName(fixture, name) {
  return fixture.pet_skill_name_matches
    .filter((row) => row.skill_name_raw === name)
    .map((row) => ({
      skill_name_raw: row.skill_name_raw,
      skill_id: row.skill_id,
      match_count: Number(row.match_count),
      ambiguous: row.ambiguous === 'true',
    }))
}

function petDetail(fixture, petId) {
  const pet = fixture.pets.find((row) => row.client_shape_id === petId)
  if (!pet) return null
  const aptitude = fixture.pet_aptitudes.find((row) => row.client_shape_id === petId) ?? null
  const candidateSkills = fixture.pet_skill_candidates
    .filter((row) => row.client_shape_id === petId)
    .map((row) => ({
      sequence: Number(row.sequence),
      skill_name_raw: row.skill_name_raw,
      matches: matchesForName(fixture, row.skill_name_raw),
    }))
  const requiredSkills = fixture.pet_required_skills
    .filter((row) => row.client_shape_id === petId)
    .map((row) => ({
      skill_name_raw: row.skill_name_raw,
      matches: matchesForName(fixture, row.skill_name_raw),
    }))
  return {
    pet,
    aptitude,
    aptitude_status: aptitudStatusOf(fixture, petId),
    required_skills: requiredSkills,
    candidate_skills: candidateSkills,
  }
}

function skillDetail(fixture, skillId) {
  const skill = fixture.skills.find((row) => asText(row.skill_id) === asText(skillId))
  if (!skill) return null
  const overwrite = fixture.pet_skill_overwrites.find((row) => asText(row.skill_id) === asText(skillId)) ?? null
  const nameMatches = fixture.pet_skill_name_matches
    .filter((row) => asText(row.skill_id) === asText(skillId))
    .map((row) => ({
      skill_name_raw: row.skill_name_raw,
      skill_id: row.skill_id,
      match_count: Number(row.match_count),
      ambiguous: row.ambiguous === 'true',
    }))
  return { skill, overwrite, name_matches: nameMatches }
}

function datasetSummary(dataset) {
  const { rows_data, ...summary } = dataset
  return summary
}

function datasetRows(dataset, searchParams) {
  const needle = (searchParams.get('q') ?? '').trim()
  const sceneId = (searchParams.get('scene_id') ?? '').trim()
  return dataset.rows_data.filter((row) => {
    if (sceneId && asText(row.scene_id) !== sceneId) return false
    if (!needle) return true
    return Object.values(row).some((value) => matchesText(value, needle))
  })
}

/**
 * @param {any} fixture
 * @param {string} pathname
 * @param {URLSearchParams} searchParams
 * @returns {{status: number, body: unknown}}
 */
export function handleRequest(fixture, pathname, searchParams) {
  const path = pathname.replace(/\/+$/, '') || '/'
  if (!path.startsWith(REVIEW_PREFIX)) {
    return notFound(`未知路径：${pathname}`)
  }
  const rest = path.slice(REVIEW_PREFIX.length) || '/'

  if (rest === '/batch') {
    return { status: 200, body: fixture.batch }
  }

  if (rest === '/items') {
    const needle = (searchParams.get('q') ?? '').trim()
    const rows = fixture.items.filter(
      (row) => matchesText(row.name, needle) || asText(row.client_shape_id) === needle || matchesText(row.client_shape_id, needle),
    )
    return { status: 200, body: toPage(rows, searchParams) }
  }

  if (rest.startsWith('/items/')) {
    const id = decodeURIComponent(rest.slice('/items/'.length))
    const item = fixture.items.find((row) => row.client_shape_id === id)
    return item ? { status: 200, body: { item } } : notFound(`道具 ${id} 不在夹具样本中`)
  }

  if (rest === '/pets') {
    const needle = (searchParams.get('q') ?? '').trim()
    const rows = fixture.pets
      .filter((row) => matchesText(row.name, needle) || matchesText(row.client_shape_id, needle))
      .map((row) => ({ ...row, aptitude_status: aptitudStatusOf(fixture, row.client_shape_id) }))
    return { status: 200, body: toPage(rows, searchParams) }
  }

  if (rest.startsWith('/pets/')) {
    const id = decodeURIComponent(rest.slice('/pets/'.length))
    const detail = petDetail(fixture, id)
    return detail ? { status: 200, body: detail } : notFound(`宠物 ${id} 不在夹具样本中`)
  }

  if (rest === '/skills') {
    const needle = (searchParams.get('q') ?? '').trim()
    const rows = fixture.skills.filter(
      (row) => matchesText(row.name, needle) || matchesText(row.skill_id, needle),
    )
    return { status: 200, body: toPage(rows, searchParams) }
  }

  if (rest.startsWith('/skills/')) {
    const id = decodeURIComponent(rest.slice('/skills/'.length))
    const detail = skillDetail(fixture, id)
    return detail ? { status: 200, body: detail } : notFound(`技能 ${id} 不在夹具样本中`)
  }

  if (rest === '/maps/datasets') {
    return { status: 200, body: { datasets: fixture.maps.datasets.map(datasetSummary) } }
  }

  if (rest.startsWith('/maps/datasets/')) {
    const key = decodeURIComponent(rest.slice('/maps/datasets/'.length))
    const dataset = fixture.maps.datasets.find((row) => row.dataset_key === key)
    if (!dataset) return notFound(`数据集 ${key} 不在夹具样本中`)
    const rows = datasetRows(dataset, searchParams)
    return { status: 200, body: { ...toPage(rows, searchParams), dataset: datasetSummary(dataset) } }
  }

  if (rest === '/npcs/agreement') {
    const sceneId = (searchParams.get('scene_id') ?? '').trim()
    const rows = fixture.agreement.rows.filter(
      (row) => !sceneId || asText(row.scene_id) === sceneId,
    )
    return {
      status: 200,
      body: { ...toPage(rows, searchParams), agreement_counts: fixture.agreement.agreement_counts },
    }
  }

  if (rest === '/npcs') {
    const source = searchParams.get('source') ?? ''
    const entry = fixture.npcs[source]
    if (!entry) return badRequest(`不支持的来源 source=${source}`)
    const needle = (searchParams.get('q') ?? '').trim()
    const sceneId = (searchParams.get('scene_id') ?? '').trim()
    const rows = entry.rows.filter((row) => {
      if (sceneId && asText(row.scene_id) !== sceneId) return false
      if (!needle) return true
      return (
        matchesText(row.npcid, needle) ||
        matchesText(row.display_name, needle) ||
        matchesText(row.real_name, needle) ||
        matchesText(row.secondary_name, needle) ||
        matchesText(row.scene_id, needle)
      )
    })
    return { status: 200, body: { ...toPage(rows, searchParams), source_info: entry.source_info } }
  }

  if (rest === '/anomalies') {
    return { status: 200, body: fixture.anomalies }
  }

  return notFound(`未实现的夹具端点：${pathname}`)
}
