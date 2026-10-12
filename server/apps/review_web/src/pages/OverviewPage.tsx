import { fetchBatchOverview } from '../api/client'
import type { BatchOverview, BatchTableSummary } from '../api/types'
import { AsyncSection } from '../components/AsyncSection'
import { Badge } from '../components/Badges'
import { DataTable, type Column } from '../components/DataTable'
import { useApiResource } from '../hooks/useApiResource'
import { formatCount, numericOrNull, rawText, rawTextOrMarker } from '../lib/display'
import { hrefFor, useLinkClick } from '../lib/router'

const COUNTER_LABELS: Record<string, string> = {
  items: '道具行数',
  pets: '宠物主表行数',
  pet_aptitudes: '宠物资质行数',
  pet_aptitude_missing: '资质缺失数',
  pet_skill_candidates: '候选技能行数',
  pet_required_skills: '必带技能行数',
  pet_skills: '技能行数',
  pet_skill_name_matches: '技能名称匹配行数',
  skill_write_count: '技能字典写入次数',
  skill_unique_count: '技能唯一 ID 数',
  skill_overwrite_count: '重复键覆盖次数',
  quarantined_record_count: '隔离记录数',
  pet_skill_names: '被引用技能名称数',
  ambiguous_pet_skill_names: '同名多 ID 名称数',
}

const COUNTER_ORDER = [
  'items',
  'pets',
  'pet_aptitudes',
  'pet_aptitude_missing',
  'pet_skill_candidates',
  'pet_required_skills',
  'pet_skills',
  'pet_skill_name_matches',
  'skill_write_count',
  'skill_unique_count',
  'skill_overwrite_count',
  'quarantined_record_count',
  'pet_skill_names',
  'ambiguous_pet_skill_names',
]

const tableColumns: Array<Column<BatchTableSummary>> = [
  {
    key: 'table_key',
    label: '源条目',
    render: (row) => <code>{rawTextOrMarker(row.table_key)}</code>,
  },
  {
    key: 'csv_file',
    label: '复核 CSV',
    render: (row) => <code>{rawTextOrMarker(row.csv_file)}</code>,
  },
  {
    key: 'label',
    label: '内容',
    render: (row) => rawTextOrMarker(row.label),
  },
  {
    key: 'source_records',
    label: '源记录数',
    numeric: true,
    render: (row) => formatCount(row.source_records),
  },
  {
    key: 'review_csv_records',
    label: '复核行数',
    numeric: true,
    render: (row) => formatCount(row.review_csv_records),
  },
  {
    key: 'quarantined_records',
    label: '隔离',
    numeric: true,
    render: (row) => {
      const value = numericOrNull(row.quarantined_records)
      const text = formatCount(row.quarantined_records)
      return value !== null && value > 0 ? <Badge tone="danger">{text}</Badge> : <span>{text}</span>
    },
  },
  {
    key: 'missing_records',
    label: '缺失',
    numeric: true,
    render: (row) =>
      row.missing_records === null || row.missing_records === undefined ? (
        <span className="muted">—</span>
      ) : (
        <Badge tone="warn">{formatCount(row.missing_records)}</Badge>
      ),
  },
  {
    key: 'source_table',
    label: '源表',
    render: (row) => <code>{rawTextOrMarker(row.source_table)}</code>,
  },
]

function ChecksPanel({ checks }: { checks: Record<string, string> }) {
  const entries = Object.entries(checks ?? {})
  if (entries.length === 0) return <p className="muted">（API 未提供校验状态）</p>
  return (
    <ul className="checks" data-testid="checks-list">
      {entries.map(([key, value]) => {
        const text = rawText(value) ?? ''
        const ok = text.toLowerCase() === 'pass'
        return (
          <li key={key}>
            <Badge tone={ok ? 'ok' : 'warn'}>{text || '（空）'}</Badge>
            <code>{key}</code>
          </li>
        )
      })}
    </ul>
  )
}

function CountersPanel({ overview }: { overview: BatchOverview }) {
  const counters = overview.counters ?? {}
  const known = COUNTER_ORDER.filter((key) => key in counters)
  const extra = Object.keys(counters).filter((key) => !COUNTER_ORDER.includes(key))
  if (known.length === 0 && extra.length === 0) {
    return <p className="muted">（API 未提供计数）</p>
  }
  return (
    <>
      <div className="counter-grid" data-testid="counter-grid">
        {[...known, ...extra].map((key) => (
          <div className="counter" key={key}>
            <span className="counter__value">{formatCount(counters[key])}</span>
            <span className="counter__label">{COUNTER_LABELS[key] ?? key}</span>
            <code className="counter__key">{key}</code>
          </div>
        ))}
      </div>
      {extra.length > 0 ? (
        <p className="muted">
          其中 {extra.length} 项计数没有对应标签，直接显示接口键名，不做猜测。
        </p>
      ) : null}
    </>
  )
}

function AmbiguousNames({ overview }: { overview: BatchOverview }) {
  const map = overview.ambiguous_pet_skill_names ?? {}
  const entries = Object.entries(map)
  if (entries.length === 0) return <p className="muted">（API 未提供同名技能候选）</p>
  return (
    <ul className="chip-list" data-testid="ambiguous-names">
      {entries.map(([name, ids]) => (
        <li key={name}>
          <span className="chip-list__name">{name}</span>
          {ids.map((id) => (
            <span className="chip" key={id}>
              ID {id}
            </span>
          ))}
        </li>
      ))}
    </ul>
  )
}

export function OverviewPage() {
  const resource = useApiResource<BatchOverview>((signal) => fetchBatchOverview({ signal }), [])
  const onClick = useLinkClick()

  return (
    <section className="page" data-testid="page-overview">
      <h1>批次概览</h1>
      <p className="page__lede">
        计数、校验状态与隔离/缺失数量全部来自复核 API，不在前端写死。若数值与 CSV 不一致，
        以 API 返回为准并核对导出器。
      </p>

      <AsyncSection
        loading={resource.loading}
        error={resource.error}
        empty={false}
        onRetry={resource.reload}
        loadingLabel="正在读取批次概览…"
      >
        {resource.data ? (
          <>
            <div className="panel">
              <h2>批次信息</h2>
              <dl className="keyvalue">
                <div className="keyvalue__row">
                  <dt>批次</dt>
                  <dd>
                    <code>{rawTextOrMarker(resource.data.batch_id)}</code>
                  </dd>
                </div>
                <div className="keyvalue__row">
                  <dt>状态</dt>
                  <dd>
                    <code>{rawTextOrMarker(resource.data.status)}</code>
                    {resource.data.native_verified === false ? (
                      <Badge tone="warn">native_verified = false</Badge>
                    ) : null}
                  </dd>
                </div>
                <div className="keyvalue__row">
                  <dt>文件数量</dt>
                  <dd>
                    复核 CSV：{formatCount(resource.data.csv_files)} · 输出文件合计：
                    {formatCount(resource.data.generated_files)}
                  </dd>
                </div>
              </dl>
            </div>

            <div className="panel">
              <h2>各表数量与隔离/缺失</h2>
              {resource.data.tables.length === 0 ? (
                <p className="muted">（API 未提供表清单）</p>
              ) : (
                <DataTable
                  columns={tableColumns}
                  rows={resource.data.tables}
                  rowKey={(row) => row.table_key}
                  testId="batch-tables"
                />
              )}
            </div>

            <div className="panel">
              <h2>计数</h2>
              <CountersPanel overview={resource.data} />
            </div>

            <div className="panel">
              <h2>校验状态</h2>
              <ChecksPanel checks={resource.data.checks} />
            </div>

            <div className="panel">
              <h2>同名技能多 ID 候选</h2>
              <p className="muted">
                同名命中多个 ID 时全部保留，不默认取第一个；任何正式关联仍需独立证据。
              </p>
              <AmbiguousNames overview={resource.data} />
              <p>
                <a href={hrefFor('anomalies')} onClick={(event) => onClick(event, hrefFor('anomalies'))}>
                  前往「异常与证据」查看完整候选与原始字节 →
                </a>
              </p>
            </div>

            <div className="panel">
              <h2>本批限制</h2>
              {resource.data.limitations && resource.data.limitations.length > 0 ? (
                <ul>
                  {resource.data.limitations.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              ) : (
                <p className="muted">（API 未提供 limitations）</p>
              )}
              {resource.data.input_hashes && Object.keys(resource.data.input_hashes).length > 0 ? (
                <>
                  <h3>输入哈希</h3>
                  <ul className="hash-list">
                    {Object.entries(resource.data.input_hashes).map(([file, hash]) => (
                      <li key={file}>
                        <code>{file}</code> <code className="hash">{hash}</code>
                      </li>
                    ))}
                  </ul>
                </>
              ) : null}
            </div>
          </>
        ) : null}
      </AsyncSection>
    </section>
  )
}
