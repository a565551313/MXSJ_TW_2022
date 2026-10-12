import { useEffect, useState } from 'react'
import { DEFAULT_PAGE_SIZE } from '../api/contract'
import { getItem, listItems, toItemRow, type Envelope, type ItemRow } from '../api/reviewApi'
import { AsyncSection } from '../components/AsyncSection'
import { ExplicitMappingBadge, ReviewStatusBadge, SourceTag } from '../components/Badges'
import { Pagination, SearchBar } from '../components/Controls'
import { DataTable, type Column } from '../components/DataTable'
import { SafeText } from '../components/SafeText'
import { useApiResource } from '../hooks/useApiResource'
import { useDebouncedValue } from '../hooks/useDebouncedValue'
import { rawTextOrMarker } from '../lib/display'
import { hrefFor, navigate, useLinkClick } from '../lib/router'

const columns: Array<Column<ItemRow>> = [
  {
    key: 'client_shape_id',
    label: '道具 ID',
    render: (row) => <code data-testid="item-id">{rawTextOrMarker(row.client_shape_id)}</code>,
  },
  { key: 'name', label: '名称', render: (row) => <SafeText value={row.name} /> },
  {
    key: 'category_code_raw',
    label: '类别代码',
    render: (row) => <code>{rawTextOrMarker(row.category_code_raw)}</code>,
  },
  {
    key: 'image_id',
    label: '图片映射 ID',
    render: (row) => <code>{rawTextOrMarker(row.image_id)}</code>,
  },
  {
    key: 'image_mapping_explicit',
    label: '映射方式',
    render: (row) => <ExplicitMappingBadge value={row.image_mapping_explicit} />,
  },
  {
    key: 'review_status',
    label: '复核状态',
    render: (row) => <ReviewStatusBadge status={row.review_status} />,
  },
]

function ItemDetailPanel({ id }: { id: string }) {
  const detail = useApiResource<ItemRow>((signal) => getItem(id, { signal }), [id])
  const onClick = useLinkClick()

  return (
    <div className="panel panel--detail" data-testid="item-detail">
      <div className="panel__header">
        <h2>道具详情 #{id}</h2>
        <a href={hrefFor('items')} onClick={(event) => onClick(event, hrefFor('items'))}>
          返回列表
        </a>
      </div>
      <AsyncSection
        loading={detail.loading}
        error={detail.error}
        empty={!detail.loading && detail.data === null}
        onRetry={detail.reload}
        loadingLabel="正在读取道具详情…"
      >
        {detail.data ? (
          <dl className="keyvalue">
            <div className="keyvalue__row">
              <dt>client_shape_id</dt>
              <dd>
                <code>{rawTextOrMarker(detail.data.client_shape_id)}</code>
              </dd>
            </div>
            <div className="keyvalue__row">
              <dt>名称</dt>
              <dd>
                <SafeText value={detail.data.name} />
              </dd>
            </div>
            <div className="keyvalue__row">
              <dt>category_code_raw</dt>
              <dd>
                <code>{rawTextOrMarker(detail.data.category_code_raw)}</code>
                <div className="keyvalue__note muted">原始整数，未解释为业务类别</div>
              </dd>
            </div>
            <div className="keyvalue__row">
              <dt>图片映射</dt>
              <dd>
                <code>image_id = {rawTextOrMarker(detail.data.image_id)}</code>{' '}
                <ExplicitMappingBadge value={detail.data.image_mapping_explicit} />
                <div className="keyvalue__note muted">
                  本轮没有图片资源 API：只展示映射 ID 与是否为显式映射，不提供图片预览，也不探测对应资源是否存在。
                </div>
              </dd>
            </div>
            <div className="keyvalue__row">
              <dt>来源</dt>
              <dd>
                <SourceTag entry={detail.data.source_entry} table={detail.data.source_table} />{' '}
                <ReviewStatusBadge status={detail.data.review_status} />
              </dd>
            </div>
            <div className="keyvalue__row">
              <dt>原始描述</dt>
              <dd>
                <SafeText value={detail.data.description_raw} className="raw-text" />
                <div className="keyvalue__note muted">
                  按源文本原样显示（含 <code>#r</code> 等标记），不执行富文本标记，不做简繁转换。
                </div>
              </dd>
            </div>
          </dl>
        ) : null}
      </AsyncSection>
    </div>
  )
}

export function ItemsPage({ id }: { id: string | null }) {
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState<number>(DEFAULT_PAGE_SIZE)
  const debouncedQuery = useDebouncedValue(query, 250)

  useEffect(() => {
    setPage(1)
  }, [debouncedQuery, pageSize])

  const list = useApiResource<Envelope>(
    (signal) => listItems({ page, pageSize, search: debouncedQuery }, { signal }),
    [page, pageSize, debouncedQuery],
  )

  const rows = (list.data?.records ?? []).map(toItemRow)
  const total = list.data?.total ?? 0
  const emptyState = !list.loading && !list.error && rows.length === 0

  return (
    <section className="page" data-testid="page-items">
      <h1>道具</h1>
      <p className="page__lede">
        按客户端显示目录 ID 或名称搜索。字段含义按 batch_001 manifest：<code>client_shape_id</code>{' '}
        是显示目录 ID，不是玩家背包实例 ID；<code>category_code_raw</code> 是原始整数，本批不替类别代码发明业务含义。
      </p>

      {id ? <ItemDetailPanel id={id} /> : null}

      <SearchBar
        value={query}
        onChange={setQuery}
        placeholder="输入道具 ID（如 12）或名称关键字"
        label="搜索道具"
        hint="查询由后端 /datasets/items/records 执行；前端不读取仓库 CSV。被隔离的记录不会出现在本表中。"
      />

      <AsyncSection
        loading={list.loading}
        error={list.error}
        empty={emptyState}
        onRetry={list.reload}
        loadingLabel="正在读取道具表…"
      >
        {list.data ? (
          <>
            <DataTable
              columns={columns}
              rows={rows}
              rowKey={(row) => row.pk}
              selectedKey={id}
              onRowClick={(row) =>
                row.client_shape_id && navigate(hrefFor('items', row.client_shape_id))
              }
              testId="items-table"
            />
            {rows.length === 0 ? (
              <p className="muted" data-testid="items-empty-hint">
                查询没有返回记录。若该行已被隔离（本批文档记载条目 1945 的 72548 仍在隔离中，其原始字节保留在
                「异常与证据」页），本页不会用占位名称伪装成正常道具。
              </p>
            ) : null}
            <Pagination
              page={page}
              pageSize={pageSize}
              total={total}
              onPage={setPage}
              onPageSize={setPageSize}
              loading={list.loading}
            />
          </>
        ) : null}
      </AsyncSection>

      {list.data && list.data.count !== list.data.records.length ? (
        <p className="muted">
          注意：接口声明 count={list.data.count}，本次返回 {list.data.records.length} 条；以实际返回为准。
        </p>
      ) : null}
      {list.data ? (
        <p className="muted">
          本页显示 offset {list.data.offset} 起共 {list.data.records.length} 条，过滤后总数 {total}
          {''}
          {list.data.limit ? `（limit ${list.data.limit}）` : ''}。
        </p>
      ) : null}
    </section>
  )
}
