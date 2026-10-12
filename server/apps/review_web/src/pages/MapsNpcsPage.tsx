import { useEffect, useMemo, useState } from 'react'
import { DEFAULT_PAGE_SIZE, MAP_DATASET_KEYS, type NpcSourceKey } from '../api/contract'
import {
  asText,
  loadAgreement,
  loadMapDatasets,
  loadNpcSourcePage,
  queryDatasetRecords,
  type AgreementView,
  type ApiRecord,
  type DatasetMeta,
  type Envelope,
  type NpcSourcePage,
} from '../api/reviewApi'
import { AsyncSection } from '../components/AsyncSection'
import { Badge, DuplicateBadge, SourceTag, ZeroIdBadge } from '../components/Badges'
import { Pagination, SearchBar } from '../components/Controls'
import { DataTable, type Column } from '../components/DataTable'
import { SafeText } from '../components/SafeText'
import { useApiResource } from '../hooks/useApiResource'
import { useDebouncedValue } from '../hooks/useDebouncedValue'
import { rawText, rawTextOrMarker } from '../lib/display'

const NPC_SOURCES: Array<{ key: NpcSourceKey; label: string; note: string }> = [
  {
    key: 'npcposdata_records',
    label: '条目 2601 · npcposdata_records',
    note: '记录身份 (scene_id, record_index)；接口把复合主键拼成 _pk（如 1001:0）。1,335 条记录不是唯一 NPC 数。',
  },
  {
    key: 'minimapnpcpos_pos_records',
    label: '条目 2804 · minimapnpcpos_pos_records',
    note: '记录身份 (scene_id, scene_display_name, record_index)，_pk 如 1001:永澤城:0。1,344 条记录不是唯一 NPC 数。',
  },
]

const AGREEMENT_LABELS: Record<string, string> = {
  identical_sequence: '顺序与内容一致',
  identical_multiset_different_order: '内容相同、顺序不同',
  content_difference: '内容存在差异',
  only_in_npcposdata_2601: '仅存在于 2601',
  only_in_minimapnpcpos_2804: '仅存在于 2804',
}

const NPC_COLUMN_LABELS: Record<string, string> = {
  display_name: 'display_name',
  secondary_name: 'secondary_name',
  field6: 'field6',
  real_name: 'real_name',
  scene_display_name: 'scene_display_name',
}

function recordIdentity(record: ApiRecord): string {
  const pk = asText(record, '_pk')
  const sceneId = asText(record, 'scene_id')
  const sceneName = asText(record, 'scene_display_name')
  const index = asText(record, 'record_index')
  const parts = [sceneId ?? '—']
  if (sceneName) parts.push(sceneName)
  if (index !== null) parts.push(`#${index}`)
  return pk ? `${parts.join(' / ')}（_pk=${pk}）` : parts.join(' / ')
}

function npcColumns(): Array<Column<ApiRecord>> {
  return [
    {
      key: 'identity',
      label: '记录身份',
      render: (row) => <code data-testid="npc-identity">{recordIdentity(row)}</code>,
    },
    {
      key: 'npcid',
      label: 'npcid',
      render: (row) => (
        <span className="npcid-cell">
          <code>{rawTextOrMarker(asText(row, 'npcid'))}</code>
          <ZeroIdBadge value={asText(row, 'npcid')} label="ID" />
        </span>
      ),
    },
    ...['display_name', 'secondary_name', 'type', 'x', 'y', 'field6', 'shape', 'real_name'].map((key) => ({
      key,
      label: NPC_COLUMN_LABELS[key] ?? key,
      render: (row: ApiRecord) =>
        key === 'type' || key === 'x' || key === 'y' ? (
          <code>{rawTextOrMarker(asText(row, key))}</code>
        ) : (
          <SafeText value={asText(row, key)} />
        ),
    })),
  ]
}

function MapDatasetSection() {
  const datasetsResource = useApiResource<{ datasets: DatasetMeta[]; issues: string[] }>(
    async (signal) => {
      const { datasets, errors } = await loadMapDatasets(MAP_DATASET_KEYS, { signal })
      const available = new Set(datasets.map((dataset) => dataset.id))
      const issues = MAP_DATASET_KEYS.filter((key) => !available.has(key)).map(
        (key) => `接口未返回数据集 ${key} 的元数据，本节不显示该来源`,
      )
      for (const failure of errors) {
        issues.push(`数据集 ${failure.dataset} 元数据读取失败：${failure.error instanceof Error ? failure.error.message : String(failure.error)}`)
      }
      return { datasets, issues }
    },
    [],
  )

  const [selected, setSelected] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(1)
  const debouncedQuery = useDebouncedValue(query, 250)

  useEffect(() => {
    if (selected === null && datasetsResource.data && datasetsResource.data.datasets.length > 0) {
      setSelected(datasetsResource.data.datasets[0].id)
    }
  }, [datasetsResource.data, selected])

  useEffect(() => {
    setPage(1)
  }, [debouncedQuery, selected])

  const summary = useMemo(
    () => datasetsResource.data?.datasets.find((item) => item.id === selected) ?? null,
    [datasetsResource.data, selected],
  )

  const rowsResource = useApiResource<Envelope | null>(
    async (signal) => {
      if (!selected) return null
      return queryDatasetRecords(
        selected,
        { offset: (page - 1) * DEFAULT_PAGE_SIZE, limit: DEFAULT_PAGE_SIZE, q: debouncedQuery },
        { signal },
      )
    },
    [selected, debouncedQuery, page],
  )

  const columns = useMemo<Array<Column<ApiRecord>>>(() => {
    const definitions = summary?.columns ?? []
    if (definitions.length > 0) {
      return definitions.map((column) => ({
        key: column.name,
        label: column.name,
        render: (row: ApiRecord) => <SafeText value={asText(row, column.name)} />,
      }))
    }
    const first = rowsResource.data?.records[0]
    if (!first) return []
    return Object.keys(first).map((key) => ({
      key,
      label: key,
      render: (row: ApiRecord) => <SafeText value={asText(row, key)} />,
    }))
  }, [summary, rowsResource.data])

  return (
    <div className="panel">
      <h2>地图 / 场景 / 别名数据集</h2>
      <p className="muted">
        每个数据集独立查询自己的 <code>/datasets/&lt;id&gt;/records</code>，各自保留来源条目与列定义，
        不与其他数据集合并，也不虚构统一的地图表。E 的 CSV 保留原有格式（最小引号、CRLF）：
        空单元格在接口中为 <code>null</code> 或空串，本页原样显示。
      </p>

      <AsyncSection
        loading={datasetsResource.loading}
        error={datasetsResource.error}
        empty={(datasetsResource.data?.datasets.length ?? 0) === 0}
        onRetry={datasetsResource.reload}
        loadingLabel="正在读取数据集清单…"
      >
        {datasetsResource.data ? (
          <>
            <div className="tabs" role="tablist" aria-label="数据集">
              {datasetsResource.data.datasets.map((dataset) => (
                <button
                  key={dataset.id}
                  type="button"
                  role="tab"
                  aria-selected={selected === dataset.id}
                  className={selected === dataset.id ? 'tab tab--active' : 'tab'}
                  onClick={() => setSelected(dataset.id)}
                >
                  {dataset.id}
                </button>
              ))}
            </div>
            {datasetsResource.data.issues.map((issue) => (
              <p className="muted" key={issue}>
                {issue}
              </p>
            ))}
          </>
        ) : null}
      </AsyncSection>

      {summary ? (
        <div className="dataset-meta" data-testid="dataset-meta">
          <SourceTag entry={summary.source_entry} table={summary.source_table} />
          <Badge tone="neutral">全表行数 {rawTextOrMarker(summary.rows)}</Badge>
          <Badge tone="info">
            主键 {summary.primary_key.length > 0 ? summary.primary_key.join(' + ') : '（接口未提供）'}
          </Badge>
          {summary.notes ? <p className="muted dataset-meta__notes">{summary.notes}</p> : null}
        </div>
      ) : null}

      <SearchBar
        value={query}
        onChange={setQuery}
        label="搜索当前数据集"
        placeholder="按 ID、名称或任意列内容搜索"
        hint="搜索由后端执行；前端不对结果去重或合并来源。"
      />

      <AsyncSection
        loading={rowsResource.loading}
        error={rowsResource.error}
        empty={(rowsResource.data?.records.length ?? 0) === 0}
        onRetry={rowsResource.reload}
        loadingLabel="正在读取数据集…"
      >
        {rowsResource.data ? (
          <>
            <DataTable
              columns={columns}
              rows={rowsResource.data.records}
              rowKey={(row) => String(row._pk ?? '')}
              testId="map-dataset-table"
            />
            <Pagination
              page={page}
              pageSize={DEFAULT_PAGE_SIZE}
              total={rowsResource.data.total}
              onPage={setPage}
              loading={rowsResource.loading}
            />
          </>
        ) : null}
      </AsyncSection>
    </div>
  )
}

function NpcSourceSection({ source }: { source: NpcSourceKey }) {
  const meta = NPC_SOURCES.find((item) => item.key === source) as (typeof NPC_SOURCES)[number]
  const [query, setQuery] = useState('')
  const [sceneId, setSceneId] = useState('')
  const [page, setPage] = useState(1)
  const debouncedQuery = useDebouncedValue(query, 250)
  const debouncedScene = useDebouncedValue(sceneId, 250)

  useEffect(() => {
    setPage(1)
  }, [debouncedQuery, debouncedScene])

  const resource = useApiResource<NpcSourcePage>(
    (signal) =>
      loadNpcSourcePage(source, { page, pageSize: DEFAULT_PAGE_SIZE, search: debouncedQuery, sceneId: debouncedScene }, { signal }),
    [source, page, debouncedQuery, debouncedScene],
  )

  const duplicateCounts = useMemo(() => {
    const counts = new Map<string, number>()
    for (const row of resource.data?.envelope.records ?? []) {
      const key = `${asText(row, 'scene_id')}::${asText(row, 'npcid')}`
      counts.set(key, (counts.get(key) ?? 0) + 1)
    }
    return counts
  }, [resource.data])

  const columns = useMemo<Array<Column<ApiRecord>>>(() => {
    const base = npcColumns()
    return [
      base[0],
      {
        key: 'duplicate',
        label: '同页重复',
        render: (row: ApiRecord) => {
          const key = `${asText(row, 'scene_id')}::${asText(row, 'npcid')}`
          return <DuplicateBadge count={duplicateCounts.get(key) ?? 1} />
        },
      },
      ...base.slice(1),
    ]
  }, [duplicateCounts])

  return (
    <div className="panel" data-testid={`npc-source-${source}`}>
      <h2>{meta.label}</h2>
      <p className="muted">{meta.note}</p>

      {resource.data ? (
        <div className="dataset-meta" data-testid="npc-source-info">
          <SourceTag
            entry={resource.data.meta?.source_entry}
            table={resource.data.meta?.source_table}
          />
          <Badge tone="neutral">本来源记录数 {rawTextOrMarker(resource.data.envelope.total)}</Badge>
          <Badge tone="info">
            npcid = 0 的记录 {rawTextOrMarker(resource.data.zeroNpcIdTotal)}（全部保留）
          </Badge>
          <Badge tone="neutral">
            记录主键 {resource.data.meta?.primary_key.join(' + ') ?? '（接口未提供）'}
          </Badge>
          {resource.data.metaError ? (
            <Badge tone="warn">数据集元数据读取失败，计数仍来自 rows 接口</Badge>
          ) : null}
        </div>
      ) : null}

      <div className="filters">
        <SearchBar
          value={query}
          onChange={setQuery}
          label="搜索 NPC"
          placeholder="按 npcid、显示名或 real_name 搜索"
        />
        <label className="filters__field">
          场景 ID
          <input
            className="search-bar__input"
            value={sceneId}
            inputMode="numeric"
            onChange={(event) => setSceneId(event.target.value)}
            placeholder="如 1005"
          />
        </label>
      </div>

      <AsyncSection
        loading={resource.loading}
        error={resource.error}
        empty={(resource.data?.envelope.records.length ?? 0) === 0}
        onRetry={resource.reload}
        loadingLabel="正在读取 NPC 记录…"
      >
        {resource.data ? (
          <>
            <DataTable
              columns={columns}
              rows={resource.data.envelope.records}
              rowKey={(row) => String(row._pk ?? '')}
              testId="npc-table"
            />
            <p className="muted">
              「同页重复」只按当前页内的 (scene_id, npcid) 计数，提示同键多记录事实；不折叠、不合并单元格，
              也不据此推断唯一 NPC 数。记录顺序保持接口返回顺序。
            </p>
            <Pagination
              page={page}
              pageSize={DEFAULT_PAGE_SIZE}
              total={resource.data.envelope.total}
              onPage={setPage}
              loading={resource.loading}
            />
          </>
        ) : null}
      </AsyncSection>
    </div>
  )
}

const agreementColumns: Array<Column<ApiRecord>> = [
  { key: 'scene_id', label: 'scene_id', render: (row) => <code>{rawTextOrMarker(asText(row, 'scene_id'))}</code> },
  { key: 'npcid', label: 'npcid', render: (row) => <code>{rawTextOrMarker(asText(row, 'npcid'))}</code> },
  {
    key: 'records_2601',
    label: '2601 记录数',
    render: (row) => <code>{rawTextOrMarker(asText(row, 'records_2601'))}</code>,
  },
  {
    key: 'records_2804',
    label: '2804 记录数',
    render: (row) => <code>{rawTextOrMarker(asText(row, 'records_2804'))}</code>,
  },
  {
    key: 'agreement',
    label: '对比结果',
    render: (row) => {
      const value = rawText(asText(row, 'agreement')) ?? '（空）'
      return (
        <span>
          <Badge tone={value === 'identical_sequence' ? 'ok' : 'warn'}>{value}</Badge>
          {AGREEMENT_LABELS[value] ? <span className="muted"> {AGREEMENT_LABELS[value]}</span> : null}
        </span>
      )
    },
  },
]

function AgreementSection() {
  const [sceneId, setSceneId] = useState('')
  const [page, setPage] = useState(1)
  const debouncedScene = useDebouncedValue(sceneId, 250)

  useEffect(() => {
    setPage(1)
  }, [debouncedScene])

  const resource = useApiResource<AgreementView>(
    (signal) => loadAgreement({ page, pageSize: DEFAULT_PAGE_SIZE, sceneId: debouncedScene }, { signal }),
    [page, debouncedScene],
  )

  return (
    <div className="panel">
      <h2>来源对照（2601 vs 2804，仅非零 NPC ID）</h2>
      <p className="muted">
        对照表只描述两个来源在非零 NPC ID 上的记录差异，不代表服务端坐标已确认，也不把差异静默合并。
        下面的分类计数由前端遍历<strong>全表记录</strong>（不只第一页）后统计。
      </p>

      {resource.data ? (
        <>
          <ul className="chip-list" data-testid="agreement-counts">
            {Object.entries(resource.data.counts).map(([key, value]) => (
              <li key={key}>
                <span className="chip-list__name">{key}</span>
                <span className="chip">{String(value)}</span>
              </li>
            ))}
          </ul>
          <p className="muted">
            全表 {resource.data.total} 行；当前筛选返回 {resource.data.envelope.total} 行。
          </p>
        </>
      ) : null}

      <label className="filters__field">
        场景 ID
        <input
          className="search-bar__input"
          value={sceneId}
          inputMode="numeric"
          onChange={(event) => setSceneId(event.target.value)}
          placeholder="留空显示全部"
        />
      </label>

      <AsyncSection
        loading={resource.loading}
        error={resource.error}
        empty={(resource.data?.envelope.records.length ?? 0) === 0}
        onRetry={resource.reload}
        loadingLabel="正在读取来源对照…"
      >
        {resource.data ? (
          <>
            <DataTable
              columns={agreementColumns}
              rows={resource.data.envelope.records}
              rowKey={(row) => String(row._pk ?? '')}
              testId="agreement-table"
            />
            <Pagination
              page={page}
              pageSize={DEFAULT_PAGE_SIZE}
              total={resource.data.envelope.total}
              onPage={setPage}
              loading={resource.loading}
            />
          </>
        ) : null}
      </AsyncSection>
    </div>
  )
}

export function MapsNpcsPage() {
  return (
    <section className="page" data-testid="page-maps">
      <h1>地图 / NPC</h1>
      <p className="page__lede">
        不同来源分开展示，各自保留来源条目、复合记录身份、零 ID 与重复记录。
        <code>related_id_unresolved</code> 仍未定性，两个来源的尺寸/坐标不合并为服务端坐标系统。
      </p>
      <MapDatasetSection />
      <NpcSourceSection source="npcposdata_records" />
      <NpcSourceSection source="minimapnpcpos_pos_records" />
      <AgreementSection />
    </section>
  )
}
