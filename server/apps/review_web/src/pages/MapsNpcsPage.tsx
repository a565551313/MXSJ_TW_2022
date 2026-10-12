import { useEffect, useMemo, useState } from 'react'
import {
  fetchMapDataset,
  fetchMapDatasets,
  fetchNpcAgreement,
  fetchNpcs,
} from '../api/client'
import type {
  AgreementPage,
  AgreementRow,
  MapDatasetPage,
  MapDatasetSummary,
  MapRow,
  NpcPage,
  NpcRecord,
  NpcSourceKey,
} from '../api/types'
import { AsyncSection } from '../components/AsyncSection'
import { Badge, DuplicateBadge, ReviewStatusBadge, SourceTag, ZeroIdBadge } from '../components/Badges'
import { Pagination, SearchBar } from '../components/Controls'
import { DataTable, type Column } from '../components/DataTable'
import { SafeText } from '../components/SafeText'
import { useApiResource } from '../hooks/useApiResource'
import { useDebouncedValue } from '../hooks/useDebouncedValue'
import { rawText, rawTextOrMarker } from '../lib/display'

const NPC_SOURCES: Array<{ key: NpcSourceKey; label: string; note: string }> = [
  {
    key: 'npcposdata_2601',
    label: '条目 2601 · npcposdata_records',
    note: '记录身份 (scene_id, record_index)；1,335 条记录不是唯一 NPC 数。',
  },
  {
    key: 'minimapnpcpos_2804',
    label: '条目 2804 · minimapnpcpos_pos_records',
    note: '记录身份 (scene_id, scene_display_name, record_index)；1,344 条记录不是唯一 NPC 数。',
  },
]

const AGREEMENT_LABELS: Record<string, string> = {
  identical_sequence: '顺序与内容一致',
  identical_multiset_different_order: '内容相同、顺序不同',
  content_difference: '内容存在差异',
  only_in_npcposdata_2601: '仅存在于 2601',
  only_in_minimapnpcpos_2804: '仅存在于 2804',
}

function recordIdentity(row: NpcRecord): string {
  const sceneId = rawText((row as { scene_id?: unknown }).scene_id) ?? '—'
  const displayName = rawText((row as { scene_display_name?: unknown }).scene_display_name)
  const recordIndex = rawText((row as { record_index?: unknown }).record_index) ?? '—'
  return displayName ? `${sceneId} / ${displayName} / #${recordIndex}` : `${sceneId} / #${recordIndex}`
}

function npcColumns(): Array<Column<NpcRecord>> {
  const base: Array<Column<NpcRecord>> = [
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
          <code>{rawTextOrMarker(row.npcid)}</code>
          <ZeroIdBadge value={row.npcid} label="ID" />
        </span>
      ),
    },
    {
      key: 'display_name',
      label: 'display_name',
      render: (row) => <SafeText value={row.display_name} />,
    },
    {
      key: 'secondary_name',
      label: 'secondary_name',
      render: (row) => <SafeText value={row.secondary_name} />,
    },
    { key: 'type', label: 'type', render: (row) => <code>{rawTextOrMarker(row.type)}</code> },
    { key: 'x', label: 'x', render: (row) => <code>{rawTextOrMarker(row.x)}</code> },
    { key: 'y', label: 'y', render: (row) => <code>{rawTextOrMarker(row.y)}</code> },
    {
      key: 'field6',
      label: 'field6',
      render: (row) => <SafeText value={row.field6} />,
    },
    { key: 'shape', label: 'shape', render: (row) => <SafeText value={row.shape} /> },
    {
      key: 'real_name',
      label: 'real_name',
      render: (row) => <SafeText value={row.real_name} />,
    },
  ]
  return base
}

function MapDatasetSection() {
  const datasetsResource = useApiResource(
    (signal) => fetchMapDatasets({ signal }),
    [],
  )
  const [selected, setSelected] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(1)
  const debouncedQuery = useDebouncedValue(query, 250)

  useEffect(() => {
    if (selected === null && datasetsResource.data && datasetsResource.data.datasets.length > 0) {
      setSelected(datasetsResource.data.datasets[0].dataset_key)
    }
  }, [datasetsResource.data, selected])

  useEffect(() => {
    setPage(1)
  }, [debouncedQuery, selected])

  const rowsResource = useApiResource<MapDatasetPage | null>(
    (signal) =>
      selected
        ? fetchMapDataset(selected, { q: debouncedQuery, page, page_size: 25 }, { signal })
        : Promise.resolve(null),
    [selected, debouncedQuery, page],
  )

  const summary: MapDatasetSummary | null = useMemo(() => {
    if (rowsResource.data?.dataset) return rowsResource.data.dataset
    if (datasetsResource.data && selected) {
      return datasetsResource.data.datasets.find((item) => item.dataset_key === selected) ?? null
    }
    return null
  }, [rowsResource.data, datasetsResource.data, selected])

  const columns: Array<Column<MapRow>> = useMemo(() => {
    const definitions = summary?.columns ?? []
    if (definitions.length > 0) {
      return definitions.map((column) => ({
        key: column.name,
        label: column.name,
        render: (row: MapRow) => <SafeText value={row[column.name]} />,
      }))
    }
    const first = rowsResource.data?.items[0]
    if (!first) return []
    return Object.keys(first).map((key) => ({
      key,
      label: key,
      render: (row: MapRow) => <SafeText value={row[key]} />,
    }))
  }, [summary, rowsResource.data])

  return (
    <div className="panel">
      <h2>地图 / 场景 / 别名数据集</h2>
      <p className="muted">
        每个数据集独立展示自己的来源条目与列，不与其他数据集合并，也不虚构统一的地图表。
        E 的 CSV 保留其原有格式（最小引号、CRLF），空单元格同时表示空值与空文本。
      </p>

      <AsyncSection
        loading={datasetsResource.loading}
        error={datasetsResource.error}
        empty={(datasetsResource.data?.datasets.length ?? 0) === 0}
        onRetry={datasetsResource.reload}
        loadingLabel="正在读取数据集清单…"
      >
        {datasetsResource.data ? (
          <div className="tabs" role="tablist" aria-label="数据集">
            {datasetsResource.data.datasets.map((dataset) => (
              <button
                key={dataset.dataset_key}
                type="button"
                role="tab"
                aria-selected={selected === dataset.dataset_key}
                className={selected === dataset.dataset_key ? 'tab tab--active' : 'tab'}
                onClick={() => setSelected(dataset.dataset_key)}
              >
                {dataset.dataset_key}
              </button>
            ))}
          </div>
        ) : null}
      </AsyncSection>

      {summary ? (
        <div className="dataset-meta" data-testid="dataset-meta">
          <SourceTag entry={summary.source_entry} table={summary.source_table} />
          <Badge tone="neutral">行数 {rawTextOrMarker(summary.rows)}</Badge>
          <Badge tone="info">主键 {summary.primary_key?.join(' + ') ?? '（未提供）'}</Badge>
          <ReviewStatusBadge status={summary.review_status} />
          {summary.notes ? <p className="muted dataset-meta__notes">{summary.notes}</p> : null}
        </div>
      ) : null}

      <SearchBar
        value={query}
        onChange={setQuery}
        label="搜索当前数据集"
        placeholder="按 ID、名称或任意列内容搜索"
        hint="搜索由后端执行；前端不对结果做去重或合并。"
      />

      <AsyncSection
        loading={rowsResource.loading}
        error={rowsResource.error}
        empty={(rowsResource.data?.items.length ?? 0) === 0}
        onRetry={rowsResource.reload}
        loadingLabel="正在读取数据集…"
      >
        {rowsResource.data ? (
          <>
            <DataTable
              columns={columns}
              rows={rowsResource.data.items}
              rowKey={(_row, index) => String(index)}
              testId="map-dataset-table"
            />
            <Pagination
              page={rowsResource.data.page}
              pageSize={rowsResource.data.page_size}
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

function NpcRecordsSection() {
  const [source, setSource] = useState<NpcSourceKey>('npcposdata_2601')
  const [query, setQuery] = useState('')
  const [sceneId, setSceneId] = useState('')
  const [page, setPage] = useState(1)
  const debouncedQuery = useDebouncedValue(query, 250)
  const debouncedScene = useDebouncedValue(sceneId, 250)

  useEffect(() => {
    setPage(1)
  }, [source, debouncedQuery, debouncedScene])

  const resource = useApiResource<NpcPage>(
    (signal) =>
      fetchNpcs(
        {
          source,
          q: debouncedQuery,
          scene_id: debouncedScene,
          page,
          page_size: 25,
        },
        { signal },
      ),
    [source, debouncedQuery, debouncedScene, page],
  )

  const duplicateCounts = useMemo(() => {
    const counts = new Map<string, number>()
    for (const row of resource.data?.items ?? []) {
      const key = `${rawText((row as { scene_id?: unknown }).scene_id)}::${rawText(
        (row as { npcid?: unknown }).npcid,
      )}`
      counts.set(key, (counts.get(key) ?? 0) + 1)
    }
    return counts
  }, [resource.data])

  const columns = useMemo<Array<Column<NpcRecord>>>(() => {
    const base = npcColumns()
    return [
      base[0],
      {
        key: 'duplicate',
        label: '重复',
        render: (row) => {
          const key = `${rawText((row as { scene_id?: unknown }).scene_id)}::${rawText(
            (row as { npcid?: unknown }).npcid,
          )}`
          return <DuplicateBadge count={duplicateCounts.get(key) ?? 1} />
        },
      },
      ...base.slice(1),
    ]
  }, [source, duplicateCounts])

  const active = NPC_SOURCES.find((item) => item.key === source)

  return (
    <div className="panel">
      <h2>NPC 位置记录（按来源分开）</h2>
      <p className="muted">
        两个来源各自保留复合记录身份、零 ID 与重复记录。不把 (scene_id, npcid) 当作唯一主键，
        也不把两个来源合成一个「唯一真实 NPC 表」。
      </p>

      <div className="tabs" role="tablist" aria-label="NPC 来源">
        {NPC_SOURCES.map((item) => (
          <button
            key={item.key}
            type="button"
            role="tab"
            aria-selected={source === item.key}
            className={source === item.key ? 'tab tab--active' : 'tab'}
            onClick={() => setSource(item.key)}
          >
            {item.label}
          </button>
        ))}
      </div>
      {active ? <p className="muted">{active.note}</p> : null}

      {resource.data ? (
        <div className="dataset-meta" data-testid="npc-source-info">
          <SourceTag entry={resource.data.source_info.source_entry} table={resource.data.source_info.source_table} />
          <Badge tone="neutral">本来源记录数 {rawTextOrMarker(resource.data.source_info.total)}</Badge>
          <Badge tone="info">
            npcid = 0 的记录 {rawTextOrMarker(resource.data.source_info.zero_npcid_records)}（全部保留）
          </Badge>
          <Badge tone="neutral">
            记录主键 {resource.data.source_info.primary_key.join(' + ')}
          </Badge>
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
        empty={(resource.data?.items.length ?? 0) === 0}
        onRetry={resource.reload}
        loadingLabel="正在读取 NPC 记录…"
      >
        {resource.data ? (
          <>
            <DataTable
              columns={columns}
              rows={resource.data.items}
              rowKey={(_row, index) => String(index)}
              testId="npc-table"
            />
            <p className="muted">
              「重复」按当前页内的 (scene_id, npcid) 计数，仅提示同键多记录事实；不做折叠、
              不合并单元格，也不据此推断唯一 NPC 数。
            </p>
            <Pagination
              page={resource.data.page}
              pageSize={resource.data.page_size}
              total={resource.data.total}
              onPage={setPage}
              loading={resource.loading}
            />
          </>
        ) : null}
      </AsyncSection>
    </div>
  )
}

function AgreementSection() {
  const [sceneId, setSceneId] = useState('')
  const [page, setPage] = useState(1)
  const debouncedScene = useDebouncedValue(sceneId, 250)

  useEffect(() => {
    setPage(1)
  }, [debouncedScene])

  const resource = useApiResource<AgreementPage>(
    (signal) => fetchNpcAgreement({ scene_id: debouncedScene, page, page_size: 25 }, { signal }),
    [debouncedScene, page],
  )

  const columns: Array<Column<AgreementRow>> = [
    { key: 'scene_id', label: 'scene_id', render: (row) => <code>{rawTextOrMarker(row.scene_id)}</code> },
    { key: 'npcid', label: 'npcid', render: (row) => <code>{rawTextOrMarker(row.npcid)}</code> },
    {
      key: 'records_2601',
      label: '2601 记录数',
      render: (row) => <code>{rawTextOrMarker(row.records_2601)}</code>,
    },
    {
      key: 'records_2804',
      label: '2804 记录数',
      render: (row) => <code>{rawTextOrMarker(row.records_2804)}</code>,
    },
    {
      key: 'agreement',
      label: '对比结果',
      render: (row) => (
        <span>
          <Badge tone={row.agreement === 'identical_sequence' ? 'ok' : 'warn'}>{row.agreement}</Badge>
          {AGREEMENT_LABELS[row.agreement] ? (
            <span className="muted"> {AGREEMENT_LABELS[row.agreement]}</span>
          ) : null}
        </span>
      ),
    },
  ]

  return (
    <div className="panel">
      <h2>来源对照（2601 vs 2804，仅非零 NPC ID）</h2>
      <p className="muted">
        对照表只描述两个来源在非零 NPC ID 上的记录差异，不代表服务端坐标已确认，也不把差异静默合并。
      </p>

      {resource.data ? (
        <ul className="chip-list" data-testid="agreement-counts">
          {Object.entries(resource.data.agreement_counts ?? {}).map(([key, value]) => (
            <li key={key}>
              <span className="chip-list__name">{key}</span>
              <span className="chip">{String(value)}</span>
            </li>
          ))}
        </ul>
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
        empty={(resource.data?.items.length ?? 0) === 0}
        onRetry={resource.reload}
        loadingLabel="正在读取来源对照…"
      >
        {resource.data ? (
          <>
            <DataTable
              columns={columns}
              rows={resource.data.items}
              rowKey={(_row, index) => String(index)}
              testId="agreement-table"
            />
            <Pagination
              page={resource.data.page}
              pageSize={resource.data.page_size}
              total={resource.data.total}
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
      <NpcRecordsSection />
      <AgreementSection />
    </section>
  )
}
