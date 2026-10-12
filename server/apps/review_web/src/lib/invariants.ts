import type { AnomalyBoard } from '../api/reviewApi'

/**
 * Review invariants for batch_001.
 *
 * The *specification* below is intentionally hardcoded: it is what a reviewer
 * wants to stay true. Every verdict and every "actual" string is computed from
 * the live API response, so if the backend stops quarantining a record, drops a
 * candidate ID, or starts returning a missing aptitude as a value, this panel
 * reports 未通过 instead of continuing to show the old story.
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
  check: (board: AnomalyBoard) => { ok: boolean; actual: string }
}

function quarantineOf(board: AnomalyBoard, entry: string, key: string) {
  return board.quarantine.find(
    (record) => String(record.entry_index) === entry && String(record.record_key) === key,
  )
}

function describeIds(ids: string[]): string {
  return ids.length > 0 ? ids.join(' / ') : '（接口未返回该名称的候选）'
}

export const REVIEW_INVARIANTS: InvariantSpec[] = [
  {
    id: 'item-72548-quarantined',
    label: '条目 1945：道具 72548 继续隔离，原始非法字节保留',
    check: (board) => {
      const record = quarantineOf(board, '1945', '72548')
      return {
        ok: Boolean(record) && record!.reasons.length > 0,
        actual: record ? record.reasons.join(', ') : '（隔离清单中没有 1945 / 72548）',
      }
    },
  },
  {
    id: 'aptitude-2800-quarantined',
    label: '条目 2954：资质 2800 整行继续隔离，未批准的候选不落地',
    check: (board) => {
      const record = quarantineOf(board, '2954', '2800')
      return {
        ok: Boolean(record) && record!.reasons.length > 0,
        actual: record ? record.reasons.join(', ') : '（隔离清单中没有 2954 / 2800）',
      }
    },
  },
  ...(['719', '4406'] as const).map((skillId) => ({
    id: `skill-${skillId}-quarantined`,
    label: `条目 3205：技能 ${skillId} 继续隔离`,
    check: (board: AnomalyBoard) => {
      const record = quarantineOf(board, '3205', skillId)
      return {
        ok: Boolean(record),
        actual: record ? record.reasons.join(', ') : '（未隔离）',
      }
    },
  })),
  ...['3010', '4021', '4022'].map((petId) => ({
    id: `aptitude-missing-${petId}`,
    label: `资质缺失：宠物 ${petId} 在条目 2954 中没有记录（不补零）`,
    check: (board: AnomalyBoard) => {
      const row = board.missing_aptitudes.find((item) => String(item.client_shape_id) === petId)
      return {
        ok: Boolean(row),
        actual: row ? `reason = ${row.reason ?? '（接口未提供）'}` : '（缺失清单中没有该 ID）',
      }
    },
  })),
  {
    id: 'ambiguous-229-255',
    label: '同名技能：高級命中 保留全部候选 229 / 255',
    check: (board) => {
      const group = board.ambiguous_skill_names.find((item) => item.skill_name_raw === '高級命中')
      const ids = group?.ids ?? []
      return { ok: ['229', '255'].every((id) => ids.includes(id)), actual: describeIds(ids) }
    },
  },
  {
    id: 'ambiguous-329-355',
    label: '同名技能：終級命中 保留全部候选 329 / 355',
    check: (board) => {
      const group = board.ambiguous_skill_names.find((item) => item.skill_name_raw === '終級命中')
      const ids = group?.ids ?? []
      return { ok: ['329', '355'].every((id) => ids.includes(id)), actual: describeIds(ids) }
    },
  },
]

export function evaluateInvariants(board: AnomalyBoard): InvariantResult[] {
  return REVIEW_INVARIANTS.map((spec) => {
    try {
      const { ok, actual } = spec.check(board)
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
