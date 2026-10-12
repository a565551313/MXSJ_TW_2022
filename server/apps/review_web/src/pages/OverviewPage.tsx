import { DATASET, REVIEW_API_PREFIX } from '../api/contract'
import {
  loadBatch,
  loadDatasets,
  loadHealth,
  type BatchPayload,
  type DatasetMeta,
  type HealthPayload,
  type TableSummary,
} from '../api/reviewApi'
import { AsyncSection } from '../components/AsyncSection'
import { Badge } from '../components/Badges'
import { DataTable, type Column } from '../components/DataTable'
import { useApiResource } from '../hooks/useApiResource'
import { formatCount, numericOrNull, rawText, rawTextOrMarker } from '../lib/display'
import { hrefFor, useLinkClick } from '../lib/router'

/** Table entry -> the dataset that carries its review rows. */
const ENTRY_DATASETS: Record<string, string> = {
  '1945': DATASET.items,
  '2027': DATASET.pets,
  '2954': DATASET.petAptitudes,
  '3205': DATASET.petSkills,
}

const COUNTER_LABELS: Record<string, string> = {
  missing_aptitude_count: '资质缺失数',
  pet_skill_names: '被引用技能名称数',
  quarantined_record_count: '隔离记录数',
  skill_write_count: '技能字典写入次数',
  skill_unique_count: '技能唯一 ID 数',
  skill_overwrite_count: '重复键覆盖次数',
  manifest_files_count: 'manifest 文件数',
  datasets_count: '数据集数',
  loaded_files_count: '启动加载文件数',
  total_records_count: '数据集记录合计',
}

interface TableRow extends TableSummary {
  table_key: string
  dataset_id: string | null
  dataset_rows: number | null
}

function tableColumns(datasets: DatasetMeta[]): Array<Column<TableRow>> {
  const byId = new Map(datasets.map((dataset) => [dataset.id, dataset]))
  return [
    {
      key: 'table_key',
      label: '源条目',
      render: (row) => <code>{row.table_key}</code>,
    },
    {
      key: 'dataset',
      label: '复核数据集',
      render: (row) =>
        row.dataset_id ? (
          <code data-testid="table-dataset">{row.dataset_id}</code>
        ) : (
          <span className="muted">（接口未提供对应数据集）</span>
        ),
    },
    {
      key: 'dataset_rows',
      label: '数据集行数',
      numeric: true,
      render: (row) => formatCount(row.dataset_rows),
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
      key: 'source_table',
      label: '源表',
      render: (row) => {
        const dataset = row.dataset_id ? byId.get(row.dataset_id) : undefined
        return <code>{rawTextOrMarker(asSourceTableText(dataset?.source_table))}</code>
      },
    },
  ]
}

function asSourceTableText(value: unknown): string | null {
  if (value === null || value === undefined) return null
  if (typeof value === 'string') return value
  if (Array.isArray(value)) return value.join(' / ')
  return String(value)
}

function ChecksPanel({ checks }: { checks: Record<string, string> }) {
  const entries = Object.entries(checks ?? {})
  if (entries.length === 0) return <p className="muted">（接口未提供校验状态）</p>
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

function CountersPanel({
  batch,
  health,
  datasets,
}: {
  batch: BatchPayload
  health: HealthPayload | null
  datasets: DatasetMeta[]
}) {
  const validation = batch.validation_summary
  const counters: Array<[string, number | null]> = [
    ['missing_aptitude_count', validation.missing_aptitude_count],
    ['pet_skill_names', validation.pet_skill_names],
    ['quarantined_record_count', validation.quarantined_record_count],
    ['skill_write_count', validation.skill_write_count],
    ['skill_unique_count', validation.skill_unique_count],
    ['skill_overwrite_count', validation.skill_overwrite_count],
    ['manifest_files_count', batch.manifest_files_count],
    ['datasets_count', datasets.length > 0 ? datasets.length : null],
    ['loaded_files_count', health?.loaded_files_count ?? null],
    ['total_records_count', health?.total_records_count ?? null],
  ]

  return (
    <>
      <div className="counter-grid" data-testid="counter-grid">
        {counters.map(([key, value]) => (
          <div className="counter" key={key}>
            <span className="counter__value">{formatCount(value)}</span>
            <span className="counter__label">{COUNTER_LABELS[key] ?? key}</span>
            <code className="counter__key">{key}</code>
          </div>
        ))}
      </div>
      <p className="muted">
        计数全部来自接口：<code>{REVIEW_API_PREFIX}/batch</code> 的 tables_summary / validation_summary，
        以及 <code>{REVIEW_API_PREFIX}/datasets</code>、<code>{REVIEW_API_PREFIX}/health</code>。
        接口没有返回的项显示为「（API 未提供）」，不会用 0 代替。
      </p>
    </>
  )
}

function AmbiguousNames({ batch }: { batch: BatchPayload }) {
  const entries = Object.entries(batch.validation_summary.ambiguous_pet_skill_names ?? {})
  if (entries.length === 0) return <p className="muted">（接口未提供同名技能候选）</p>
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
  const resource = useApiResource<{
    batch: BatchPayload
    health: HealthPayload | null
    datasets: DatasetMeta[]
    healthError: unknown | null
    datasetsError: unknown | null
  }>(async (signal) => {
    const [batch, healthResult, datasetsResult] = await Promise.all([
      loadBatch({ signal }),
      loadHealth({ signal }).then(
        (health) => ({ health, error: null as unknown }),
        (error: unknown) => ({ health: null, error }),
      ),
      loadDatasets({ signal }).then(
        (payload) => ({ payload, error: null as unknown }),
        (error: unknown) => ({ payload: null, error }),
      ),
    ])
    return {
      batch,
      health: healthResult.health,
      datasets: datasetsResult.payload?.datasets ?? [],
      healthError: healthResult.error,
      datasetsError: datasetsResult.error,
    }
  }, [])
  const onClick = useLinkClick()

  const rows: TableRow[] = resource.data
    ? Object.entries(resource.data.batch.tables_summary).map(([tableKey, summary]) => {
        const datasetId = ENTRY_DATASETS[tableKey] ?? null
        const dataset = resource.data?.datasets.find((item) => item.id === datasetId)
        return {
          table_key: tableKey,
          dataset_id: datasetId,
          dataset_rows: dataset?.rows ?? null,
          ...summary,
        }
      })
    : []

  return (
    <section className="page" data-testid="page-overview">
      <h1>批次概览</h1>
      <p className="page__lede">
        计数、校验状态与隔离/缺失数量全部来自复核 API（<code>/batch</code>、<code>/datasets</code>、
        <code>/health</code>），不在前端写死。若数值与 CSV 不一致，以接口返回为准并核对导出器。
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
                    <code>{rawTextOrMarker(resource.data.batch.batch)}</code>
                  </dd>
                </div>
                <div className="keyvalue__row">
                  <dt>原生加载器确认</dt>
                  <dd>
                    <code>native_loader_confirmed = {String(resource.data.batch.native_loader_confirmed)}</code>{' '}
                    {resource.data.batch.native_loader_confirmed ? (
                      <Badge tone="danger">接口声明已确认，与本页定位冲突，请核对</Badge>
                    ) : (
                      <Badge tone="warn">未确认</Badge>
                    )}
                  </dd>
                </div>
                <div className="keyvalue__row">
                  <dt>数据集</dt>
                  <dd>
                    清单 {formatCount(resource.data.datasets.length)} 个 · manifest 文件{' '}
                    {formatCount(resource.data.batch.manifest_files_count)} 个
                    {resource.data.health ? (
                      <>
                        {' '}
                        · 已加载 {formatCount(resource.data.health.loaded_files_count)} 个文件、
                        {formatCount(resource.data.health.total_records_count)} 条记录
                      </>
                    ) : null}
                  </dd>
                </div>
                {resource.data.healthError ? (
                  <div className="keyvalue__row">
                    <dt>健康检查</dt>
                    <dd className="muted">
                      /health 读取失败：{' '}
                      {resource.data.healthError instanceof Error
                        ? resource.data.healthError.message
                        : String(resource.data.healthError)}
                    </dd>
                  </div>
                ) : null}
                {resource.data.datasetsError ? (
                  <div className="keyvalue__row">
                    <dt>数据集清单</dt>
                    <dd className="muted">
                      /datasets 读取失败：{' '}
                      {resource.data.datasetsError instanceof Error
                        ? resource.data.datasetsError.message
                        : String(resource.data.datasetsError)}
                    </dd>
                  </div>
                ) : null}
              </dl>
              {Object.keys(resource.data.batch.csv_format).length > 0 ? (
                <details>
                  <summary>CSV 格式约定（来自 manifest）</summary>
                  <dl className="keyvalue">
                    {Object.entries(resource.data.batch.csv_format).map(([key, value]) => (
                      <div className="keyvalue__row" key={key}>
                        <dt>{key}</dt>
                        <dd>
                          <code>{value}</code>
                        </dd>
                      </div>
                    ))}
                  </dl>
                </details>
              ) : null}
            </div>

            <div className="panel">
              <h2>各表数量与隔离</h2>
              {rows.length === 0 ? (
                <p className="muted">（接口未提供 tables_summary）</p>
              ) : (
                <DataTable
                  columns={tableColumns(resource.data.datasets)}
                  rows={rows}
                  rowKey={(row) => row.table_key}
                  testId="batch-tables"
                />
              )}
            </div>

            <div className="panel">
              <h2>计数</h2>
              <CountersPanel
                batch={resource.data.batch}
                health={resource.data.health}
                datasets={resource.data.datasets}
              />
            </div>

            <div className="panel">
              <h2>校验状态</h2>
              <ChecksPanel checks={resource.data.batch.validation_summary.checks} />
            </div>

            <div className="panel">
              <h2>同名技能多 ID 候选</h2>
              <p className="muted">
                同名命中多个 ID 时全部保留，不默认取第一个；任何正式关联仍需独立证据。
              </p>
              <AmbiguousNames batch={resource.data.batch} />
              <p>
                <a href={hrefFor('anomalies')} onClick={(event) => onClick(event, hrefFor('anomalies'))}>
                  前往「异常与证据」查看完整候选与原始字节 →
                </a>
              </p>
            </div>

            <div className="panel">
              <h2>数据集清单</h2>
              <p className="muted">
                每个数据集都通过 <code>/datasets/&lt;id&gt;/records</code> 单独查询；
                本页只列出来源信息，不做合并。
              </p>
              <DataTable
                columns={[
                  { key: 'id', label: 'dataset_id', render: (d) => <code>{d.id}</code> },
                  { key: 'filename', label: '源文件', render: (d) => <code>{d.filename}</code> },
                  { key: 'rows', label: '行数', numeric: true, render: (d) => formatCount(d.rows) },
                  {
                    key: 'primary_key',
                    label: '主键',
                    render: (d) => (
                      <code>{d.primary_key.length > 0 ? d.primary_key.join(' + ') : '（未提供）'}</code>
                    ),
                  },
                  {
                    key: 'source_entry',
                    label: '源条目',
                    render: (d) => <code>{rawTextOrMarker(d.source_entry)}</code>,
                  },
                ]}
                rows={resource.data.datasets}
                rowKey={(d) => d.id}
                testId="datasets-table"
              />
            </div>
          </>
        ) : null}
      </AsyncSection>
    </section>
  )
}
