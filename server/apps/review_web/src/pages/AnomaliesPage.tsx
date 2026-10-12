import { useEffect, useRef, useState } from 'react'
import { DATASET, REVIEW_API_PREFIX } from '../api/contract'
import {
  evidenceName,
  loadAnomalyBoard,
  type AnomalyBoard,
  type ApiRecord,
  type OverwriteEvidenceEntry,
  type QuarantineEntry,
  type SkillOverwriteSummary,
} from '../api/reviewApi'
import { AsyncSection } from '../components/AsyncSection'
import { AmbiguousBadge, Badge, ReviewStatusBadge, SourceTag } from '../components/Badges'
import { DataTable, type Column } from '../components/DataTable'
import { InvariantCheck } from '../components/InvariantCheck'
import { RawJsonView } from '../components/RawJsonView'
import { SafeText } from '../components/SafeText'
import { useApiResource } from '../hooks/useApiResource'
import { rawTextOrMarker } from '../lib/display'
import { hrefFor, useLinkClick } from '../lib/router'

/* --------------------------------------------------------------- quarantine */

function quarantineCards(board: AnomalyBoard): Array<QuarantineEntry & { anomaly_id: string }> {
  return board.quarantine.map((entry) => ({
    ...entry,
    anomaly_id: `${entry.entry_index}:${entry.record_key}`,
  }))
}

function QuarantineCard({
  record,
  focused,
}: {
  record: QuarantineEntry & { anomaly_id: string }
  focused: boolean
}) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (focused && ref.current && typeof ref.current.scrollIntoView === 'function') {
      ref.current.scrollIntoView({ block: 'center' })
    }
  }, [focused])

  return (
    <div
      ref={ref}
      className={focused ? 'panel panel--warning is-focused' : 'panel panel--warning'}
      data-testid="quarantine-card"
      data-anomaly-id={record.anomaly_id}
    >
      <h3>
        条目 <code>{rawTextOrMarker(record.entry_index)}</code> · 表 {rawTextOrMarker(record.table)} · 记录键{' '}
        <code>{rawTextOrMarker(record.record_key)}</code>
      </h3>
      <p className="quarantine__ids">
        <span>
          anomaly_id: <code>{record.anomaly_id}</code>
        </span>
        <Badge tone="danger">已隔离</Badge>
        <Badge tone="warn">native_verified = {String(record.native_verified)}</Badge>
      </p>
      <h4>隔离原因（接口原文）</h4>
      <ul className="reason-list">
        {record.reasons.map((reason, index) => (
          <li key={index}>
            <code>{reason}</code>
          </li>
        ))}
      </ul>
      <h4>保存参数下读到的值（带类型的原始字节）</h4>
      <p className="muted">
        非法 CP950 字节在这里以十六进制原样展示：不解码、不替换成乱码占位符、不伪装成正常名称。
        这是本批明确参数下读到的值，不等于原生真实值。
      </p>
      <div className="raw-evidence" data-testid="raw-evidence">
        <RawJsonView value={record.value_under_applied_profile as never} />
      </div>
    </div>
  )
}

/* ---------------------------------------------------------- missing/matches */

interface MissingRow {
  client_shape_id: string | null
  pet_name: string | null
  reason: string | null
  source_entry: string | null
  source_table: string | null
  review_status: string | null
  pk: string
}

const missingColumns: Array<Column<MissingRow>> = [
  {
    key: 'client_shape_id',
    label: '宠物 ID',
    render: (row) => <code>{rawTextOrMarker(row.client_shape_id)}</code>,
  },
  { key: 'pet_name', label: '宠物名称', render: (row) => <SafeText value={row.pet_name} /> },
  {
    key: 'reason',
    label: '原因',
    render: (row) => <code data-testid="missing-reason">{rawTextOrMarker(row.reason)}</code>,
  },
  {
    key: 'source',
    label: '来源',
    render: (row) => <SourceTag entry={row.source_entry} table={row.source_table} />,
  },
  {
    key: 'review_status',
    label: '复核状态',
    render: (row) => <ReviewStatusBadge status={row.review_status} />,
  },
]

/* ---------------------------------------------------------------- overwrites */

const overwriteColumns: Array<Column<OverwriteEvidenceEntry>> = [
  { key: 'order', label: 'order', render: (row) => <code>{rawTextOrMarker(row.order)}</code> },
  {
    key: 'code_offset',
    label: 'code_offset',
    render: (row) => <code>{rawTextOrMarker(row.code_offset)}</code>,
  },
  {
    key: 'key',
    label: 'skill_id',
    render: (row) => (
      <a href={hrefFor('skills', String(row.key))} data-testid="overwrite-skill-link">
        <code>{rawTextOrMarker(row.key)}</code>
      </a>
    ),
  },
  {
    key: 'entry',
    label: '源条目 / 表',
    render: (row) => <SourceTag entry={row.entry_index} table={row.table} />,
  },
  {
    key: 'names',
    label: 'old_name → new_name',
    render: (row) => <OverwriteNames entry={row} />,
  },
]

/**
 * Old/new names are decoded from the byte dictionaries that came with the very
 * overwrite record - no extra per-row request, and no name is invented: when a
 * byte run cannot be decoded strictly the raw hex is shown instead.
 */
function OverwriteNames({ entry }: { entry: OverwriteEvidenceEntry }) {
  const oldName = evidenceName(entry.old_value)
  const newName = evidenceName(entry.new_value)
  const identical = oldName !== null && newName !== null ? oldName === newName : null

  if (oldName === null && newName === null) {
    return (
      <details>
        <summary className="muted">名称未能从证据解析，展开原始字节</summary>
        <div className="raw-evidence">
          <RawJsonView value={entry.old_value as never} />
          <RawJsonView value={entry.new_value as never} />
        </div>
      </details>
    )
  }

  return (
    <span data-testid="overwrite-names">
      <SafeText value={oldName} /> → <SafeText value={newName} />
      {identical === true ? (
        <Badge tone="neutral">值相同（仍是写入）</Badge>
      ) : identical === false ? (
        <Badge tone="warn">值已改变</Badge>
      ) : (
        <Badge tone="warn">无法从字节判定</Badge>
      )}
    </span>
  )
}

/* ------------------------------------------------------------------- page */

export function AnomaliesPage({ focus }: { focus?: string | null }) {
  const resource = useApiResource<AnomalyBoard>((signal) => loadAnomalyBoard({ signal }), [])
  const onClick = useLinkClick()
  const [showRawOverwrites, setShowRawOverwrites] = useState(false)

  const cards = resource.data ? quarantineCards(resource.data) : []
  const missing: MissingRow[] =
    resource.data?.missing_aptitudes.map((row) => ({
      client_shape_id: row.client_shape_id,
      pet_name: row.pet_name,
      reason: row.reason,
      source_entry: row.source_entry,
      source_table: row.source_table,
      review_status: row.review_status,
      pk: row.pk,
    })) ?? []

  return (
    <section className="page" data-testid="page-anomalies">
      <h1>异常与证据</h1>
      <p className="page__lede">
        隔离记录、缺失资质与技能歧义都在这里，全部来自 <code>{REVIEW_API_PREFIX}/quarantine</code>、
        <code>/missing-aptitudes</code>、<code>/ambiguous-skills</code>、<code>/overwrites</code> 四个接口。
        每条记录同时给出源条目、隔离原因与原始字节证据；未获批准的候选值不会作为正常数值出现在任何页面。
      </p>

      <AsyncSection
        loading={resource.loading}
        error={resource.error}
        empty={false}
        onRetry={resource.reload}
        loadingLabel="正在读取异常与证据…"
      >
        {resource.data ? (
          <>
            <div className="panel">
              <h2>
                隔离记录（接口 total {rawTextOrMarker(resource.data.quarantine_total)} 条，本次返回{' '}
                {cards.length} 条）
              </h2>
              <ul className="anomaly-index" data-testid="quarantine-index">
                {cards.map((record) => (
                  <li key={record.anomaly_id}>
                    <a
                      href={hrefFor('anomalies', null, { focus: record.anomaly_id })}
                      onClick={(event) =>
                        onClick(event, hrefFor('anomalies', null, { focus: record.anomaly_id }))
                      }
                    >
                      <code>{record.anomaly_id}</code>
                    </a>{' '}
                    条目 <code>{rawTextOrMarker(record.entry_index)}</code> 记录{' '}
                    <code>{rawTextOrMarker(record.record_key)}</code>
                  </li>
                ))}
              </ul>
              {cards.map((record) => (
                <QuarantineCard
                  key={record.anomaly_id}
                  record={record}
                  focused={Boolean(focus) && focus === record.anomaly_id}
                />
              ))}
              <p className="muted">
                本页只显示本批参数下读到的原始字节证据：非法 CP950 字节以十六进制展示（不裁剪、不猜名），
                未获批准的替代候选不落地，异常值不被改写、两列不交换、缺失不补零。
                每一条隔离记录的判定见下方「本批不变量自检」。
              </p>
            </div>

            <InvariantCheck board={resource.data} />

            <div className="panel">
              <h2>资质缺失（共 {missing.length} 条）</h2>
              <p className="muted">
                这些宠物在资质表中没有记录，与「存在但被隔离」不同：两者都不补零。
                数据来自 <code>{REVIEW_API_PREFIX}/missing-aptitudes</code>。
              </p>
              {missing.length === 0 ? (
                <p className="muted" data-testid="missing-aptitude-empty">
                  （接口返回 0 条缺失记录）
                </p>
              ) : (
                <DataTable
                  columns={missingColumns}
                  rows={missing}
                  rowKey={(row) => row.pk}
                  testId="missing-aptitude-table"
                />
              )}
              <p>
                <a href={hrefFor('pets')} onClick={(event) => onClick(event, hrefFor('pets'))}>
                  在宠物页查看这些 ID 的资质缺失提示 →
                </a>
              </p>
            </div>

            <div className="panel">
              <h2>技能歧义（同名命中多个 ID）</h2>
              <p className="muted">
                同名技能的全部候选 ID 都保留，任何一端都不默认择一；正式关联仍需独立证据。
                候选 ID 直接来自 <code>{REVIEW_API_PREFIX}/ambiguous-skills</code> 的返回值。
              </p>
              {resource.data.ambiguous_skill_names.length === 0 ? (
                <p className="muted" data-testid="ambiguous-empty">
                  （接口返回 0 条歧义记录）
                </p>
              ) : (
                <ul className="chip-list" data-testid="ambiguous-list">
                  {resource.data.ambiguous_skill_names.map((group) => (
                    <li key={group.skill_name_raw}>
                      <span className="chip-list__name">{group.skill_name_raw}</span>
                      {group.ids.map((id) => (
                        <a
                          key={id}
                          className="chip chip--link"
                          href={hrefFor('skills', id)}
                          onClick={(event) => onClick(event, hrefFor('skills', id))}
                        >
                          ID {id}
                        </a>
                      ))}
                      <span className="chip">match_count {String(group.match_count ?? '（API 未提供）')}</span>
                      {group.ambiguous ? <AmbiguousBadge count={group.ids.length} /> : null}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="panel">
              <h2>
                重复键覆盖证据（接口 total {rawTextOrMarker(resource.data.overwrites_total)} 次写入，本次返回{' '}
                {resource.data.skill_overwrites.length} 条）
              </h2>
              <p className="muted">
                条目 3205 的字典写入历史：即使旧值与新值相同，写入事实也保留；不能只导出最终值而丢掉旧值。
                数据来自 <code>{REVIEW_API_PREFIX}/overwrites</code>，旧/新名称由证据字节判定。
              </p>
              {resource.data.skill_overwrites.length === 0 ? (
                <p className="muted" data-testid="overwrite-empty">
                  （接口返回 0 条覆盖记录）
                </p>
              ) : (
                <>
                  <DataTable
                    columns={overwriteColumns}
                    rows={resource.data.skill_overwrites}
                    rowKey={(row) => String(row.order)}
                    testId="overwrite-table"
                  />
                  <button
                    type="button"
                    className="button button--ghost"
                    onClick={() => setShowRawOverwrites((value) => !value)}
                  >
                    {showRawOverwrites ? '收起原始字节证据' : '展开全部原始字节证据'}
                  </button>
                  {showRawOverwrites ? (
                    <div className="raw-evidence" data-testid="overwrite-raw-all">
                      {resource.data.skill_overwrites.map((entry) => (
                        <details key={entry.order}>
                          <summary>
                            order {entry.order} · key {entry.key} · code_offset {entry.code_offset}
                          </summary>
                          <h4>old_value</h4>
                          <RawJsonView value={entry.old_value as never} />
                          <h4>new_value</h4>
                          <RawJsonView value={entry.new_value as never} />
                        </details>
                      ))}
                    </div>
                  ) : null}
                </>
              )}
            </div>

            <div className="panel">
              <h2>相关数据集</h2>
              <p className="muted">
                上述数据对应数据集：<code>{DATASET.petAptitudeMissing}</code>、
                <code>{DATASET.petSkillNameMatches}</code>、<code>{DATASET.petSkillOverwrites}</code>
                。如需逐条浏览，可在「地图 / NPC」页以外的数据集视图中查询，或直接调用
                <code> /datasets/&lt;id&gt;/records</code>。
              </p>
              <p className="muted">
                技能 719、4406 处于隔离状态，因此它们不会出现在技能数据集（
                <code>{DATASET.petSkills}</code>）中；未确认的字段不作推测。
              </p>
            </div>
          </>
        ) : null}
      </AsyncSection>
    </section>
  )
}

/** Re-export for tests: the exact skill-overwrite record shape used above. */
export type { SkillOverwriteSummary, ApiRecord }
