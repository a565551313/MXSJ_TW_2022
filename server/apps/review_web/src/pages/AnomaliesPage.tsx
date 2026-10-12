import { useEffect, useRef } from 'react'
import { fetchAnomalies } from '../api/client'
import type { AnomaliesPayload, QuarantineRecord } from '../api/types'
import { AsyncSection } from '../components/AsyncSection'
import { AmbiguousBadge, Badge, ReviewStatusBadge, SourceTag } from '../components/Badges'
import { DataTable, type Column } from '../components/DataTable'
import { InvariantCheck } from '../components/InvariantCheck'
import { RawJsonView } from '../components/RawJsonView'
import { SafeText } from '../components/SafeText'
import { useApiResource } from '../hooks/useApiResource'
import { isTrue, rawTextOrMarker } from '../lib/display'
import { hrefFor, useLinkClick } from '../lib/router'
import type { MissingAptitudeRecord, SkillOverwriteRecord } from '../api/types'

const missingColumns: Array<Column<MissingAptitudeRecord>> = [
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

const overwriteColumns: Array<Column<SkillOverwriteRecord>> = [
  {
    key: 'write_order',
    label: 'write_order',
    render: (row) => <code>{rawTextOrMarker(row.write_order)}</code>,
  },
  {
    key: 'code_offset',
    label: 'code_offset',
    render: (row) => <code>{rawTextOrMarker(row.code_offset)}</code>,
  },
  {
    key: 'skill_id',
    label: 'skill_id',
    render: (row) => (
      <a href={hrefFor('skills', String(row.skill_id))} data-testid="overwrite-skill-link">
        <code>{rawTextOrMarker(row.skill_id)}</code>
      </a>
    ),
  },
  {
    key: 'old_name',
    label: 'old_name → new_name',
    render: (row) => (
      <span>
        <SafeText value={row.old_name} /> → <SafeText value={row.new_name} />
      </span>
    ),
  },
  {
    key: 'identical_values',
    label: 'identical_values',
    render: (row) =>
      isTrue(row.identical_values) ? (
        <Badge tone="neutral">true（值相同，仍是写入）</Badge>
      ) : (
        <Badge tone="warn">false（值已改变）</Badge>
      ),
  },
]

function QuarantineCard({ record, focused }: { record: QuarantineRecord; focused: boolean }) {
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
      <h4>隔离原因</h4>
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
        <RawJsonView value={record.value_under_applied_profile} />
      </div>
    </div>
  )
}

export interface AmbiguousGroup {
  skill_name_raw: string
  ids: string[]
  matchCount: number
  ambiguous: boolean
}

/**
 * Groups every candidate ID of one skill name together, so no ID can be dropped
 * by rendering only the first row. Tolerates both shapes an API might use: one
 * row per ID (batch_001 files), or a single row holding "229,255".
 */
function groupAmbiguous(rows: AnomaliesPayload['ambiguous_skill_names']): AmbiguousGroup[] {
  const groups = new Map<string, AmbiguousGroup>()
  for (const row of rows) {
    const key = row.skill_name_raw
    const ids = String(row.skill_id)
      .split(/[,、\s]+/)
      .map((piece) => piece.trim())
      .filter((piece) => piece.length > 0)
    const existing = groups.get(key)
    if (existing) {
      for (const id of ids) {
        if (!existing.ids.includes(id)) existing.ids.push(id)
      }
    } else {
      groups.set(key, {
        skill_name_raw: key,
        ids,
        matchCount: Number(row.match_count),
        ambiguous: row.ambiguous,
      })
    }
  }
  return Array.from(groups.values())
}

export function AnomaliesPage({ focus }: { focus?: string | null }) {
  const resource = useApiResource<AnomaliesPayload>((signal) => fetchAnomalies({ signal }), [])
  const onClick = useLinkClick()
  const groupedAmbiguous = groupAmbiguous(resource.data?.ambiguous_skill_names ?? [])

  return (
    <section className="page" data-testid="page-anomalies">
      <h1>异常与证据</h1>
      <p className="page__lede">
        四条隔离记录、缺失资质与技能歧义都在这里。每条记录同时给出源条目、隔离原因与原始字节证据；
        未获批准的候选值不会作为正常数值出现在其他页面。
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
              <h2>隔离记录（共 {resource.data.quarantine.length} 条）</h2>
              <ul className="anomaly-index" data-testid="quarantine-index">
                {resource.data.quarantine.map((record) => (
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
              {resource.data.quarantine.map((record) => (
                <QuarantineCard
                  key={record.anomaly_id}
                  record={record}
                  focused={focus !== null && focus !== undefined && focus === record.anomaly_id}
                />
              ))}
              <p className="muted">
                本页只显示本批参数下读到的原始字节证据：非法 CP950 字节以十六进制展示（不裁剪、不猜名），
                未获批准的替代候选不落地，异常值不被改写、两列不交换、缺失不补零。
                每一条隔离记录的判定见下方「本批不变量自检」。
              </p>
            </div>

            <InvariantCheck payload={resource.data} />

            <div className="panel">
              <h2>资质缺失（共 {resource.data.missing_aptitudes.length} 条）</h2>
              <p className="muted">
                这些宠物在资质表中没有记录，与「存在但被隔离」不同：两者都不补零。
              </p>
              {resource.data.missing_aptitudes.length === 0 ? (
                <p className="muted">（无）</p>
              ) : (
                <DataTable
                  columns={missingColumns}
                  rows={resource.data.missing_aptitudes}
                  rowKey={(row) => String(row.client_shape_id)}
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
                下面的候选 ID 直接来自接口返回值。
              </p>
              {groupedAmbiguous.length === 0 ? (
                <p className="muted">（无）</p>
              ) : (
                <ul className="chip-list" data-testid="ambiguous-list">
                  {groupedAmbiguous.map((group) => (
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
                      <span className="chip">match_count {group.matchCount}</span>
                      {group.ambiguous ? <AmbiguousBadge count={group.ids.length} /> : null}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="panel">
              <h2>重复键覆盖证据（共 {resource.data.skill_overwrites.length} 次写入）</h2>
              <p className="muted">
                条目 3205 的字典写入历史：即使旧值与新值相同，写入事实也保留；不能只导出最终值而丢掉旧值。
                完整旧值/新值源码树在 <code>overwrite_evidence.jsonl</code>，此处展示摘要字段。
              </p>
              {resource.data.skill_overwrites.length === 0 ? (
                <p className="muted">（无）</p>
              ) : (
                <DataTable
                  columns={overwriteColumns}
                  rows={resource.data.skill_overwrites}
                  rowKey={(row) => String(row.write_order)}
                  testId="overwrite-table"
                />
              )}
            </div>
          </>
        ) : null}
      </AsyncSection>
    </section>
  )
}
