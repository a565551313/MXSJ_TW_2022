import type { AnomaliesPayload, QuarantineRecord } from '../api/types'

/**
 * Review invariants for batch_001.
 *
 * This list is the *specification* a reviewer wants to keep true (see
 * `server/docs/csv_checks/BATCH_001.md` §4 and the Agent G consolidation). It is
 * deliberately hardcoded - not as data, but as the thing being checked.
 *
 * Every verdict below is computed from the API response, so if the backend ever
 * stops quarantining a record, changes the candidate IDs of an ambiguous skill
 * name, or starts zero-filling a missing aptitude, the panel reports
 * `未通过`/`未提供` instead of quietly showing the old story.
 */

export interface InvariantResult {
  id: string
  label: string
  ok: boolean
  /** What the API actually returned, shown next to the verdict. */
  actual: string
}

export interface InvariantSpec {
  id: string
  label: string
  check: (payload: AnomaliesPayload) => { ok: boolean; actual: string }
}

function quarantineOf(payload: AnomaliesPayload, entry: string, key: string): QuarantineRecord | undefined {
  return payload.quarantine.find(
    (record) => String(record.entry_index) === entry && String(record.record_key) === key,
  )
}

function candidateIdsOf(payload: AnomaliesPayload, name: string): string[] {
  const ids: string[] = []
  for (const row of payload.ambiguous_skill_names) {
    if (row.skill_name_raw !== name) continue
    for (const piece of String(row.skill_id).split(/[,、\s]+/)) {
      const trimmed = piece.trim()
      if (trimmed.length > 0 && !ids.includes(trimmed)) ids.push(trimmed)
    }
  }
  return ids
}

function describeIds(ids: string[]): string {
  return ids.length > 0 ? ids.join(' / ') : '（API 未返回该名称的候选）'
}

export const REVIEW_INVARIANTS: InvariantSpec[] = [
  {
    id: 'item-72548-quarantined',
    label: '条目 1945：道具 72548 继续隔离，原始非法字节保留',
    check: (payload) => {
      const record = quarantineOf(payload, '1945', '72548')
      return {
        ok: Boolean(record) && record!.reasons.length > 0,
        actual: record ? record.reasons.join(', ') : '（隔离清单中没有 1945 / 72548）',
      }
    },
  },
  {
    id: 'aptitude-2800-quarantined',
    label: '条目 2954：资质 2800 整行继续隔离，未批准的候选不落地',
    check: (payload) => {
      const record = quarantineOf(payload, '2954', '2800')
      return {
        ok: Boolean(record) && record!.reasons.length > 0,
        actual: record ? record.reasons.join(', ') : '（隔离清单中没有 2954 / 2800）',
      }
    },
  },
  {
    id: 'skill-719-quarantined',
    label: '条目 3205：技能 719 继续隔离',
    check: (payload) => {
      const record = quarantineOf(payload, '3205', '719')
      return { ok: Boolean(record), actual: record ? record.reasons.join(', ') : '（未隔离）' }
    },
  },
  {
    id: 'skill-4406-quarantined',
    label: '条目 3205：技能 4406 继续隔离',
    check: (payload) => {
      const record = quarantineOf(payload, '3205', '4406')
      return { ok: Boolean(record), actual: record ? record.reasons.join(', ') : '（未隔离）' }
    },
  },
  ...['3010', '4021', '4022'].map((petId) => ({
    id: `aptitude-missing-${petId}`,
    label: `资质缺失：宠物 ${petId} 在条目 2954 中没有记录（不补零）`,
    check: (payload: AnomaliesPayload) => {
      const row = payload.missing_aptitudes.find((item) => String(item.client_shape_id) === petId)
      return {
        ok: Boolean(row),
        actual: row ? `reason = ${row.reason}` : '（缺失清单中没有该 ID）',
      }
    },
  })),
  {
    id: 'ambiguous-229-255',
    label: '同名技能：高級命中 保留全部候选 229 / 255',
    check: (payload) => {
      const ids = candidateIdsOf(payload, '高級命中')
      return {
        ok: ['229', '255'].every((id) => ids.includes(id)),
        actual: describeIds(ids),
      }
    },
  },
  {
    id: 'ambiguous-329-355',
    label: '同名技能：終級命中 保留全部候选 329 / 355',
    check: (payload) => {
      const ids = candidateIdsOf(payload, '終級命中')
      return {
        ok: ['329', '355'].every((id) => ids.includes(id)),
        actual: describeIds(ids),
      }
    },
  },
]

export function evaluateInvariants(payload: AnomaliesPayload): InvariantResult[] {
  return REVIEW_INVARIANTS.map((spec) => {
    try {
      const { ok, actual } = spec.check(payload)
      return { id: spec.id, label: spec.label, ok, actual }
    } catch (error) {
      return {
        id: spec.id,
        label: spec.label,
        ok: false,
        actual: `检查失败：${error instanceof Error ? error.message : String(error)}`,
      }
    }
  })
}
