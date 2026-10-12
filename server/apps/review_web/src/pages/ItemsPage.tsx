import { useEffect, useState } from 'react'
import { fetchItem, fetchItems } from '../api/client'
import type { ItemRecord } from '../api/types'
import { AsyncSection } from '../components/AsyncSection'
import { ExplicitMappingBadge, ReviewStatusBadge, SourceTag } from '../components/Badges'
import { Pagination, SearchBar } from '../components/Controls'
import { DataTable, type Column } from '../components/DataTable'
import { SafeText } from '../components/SafeText'
import { useApiResource } from '../hooks/useApiResource'
import { useDebouncedValue } from '../hooks/useDebouncedValue'
import { rawTextOrMarker } from '../lib/display'
import { hrefFor, navigate, useLinkClick } from '../lib/router'
import { DEFAULT_PAGE_SIZE } from '../api/contract'

const columns: Array<Column<ItemRecord>> = [
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

export function ItemsPage({ id }: { id: string | null }) {
  const [query, setQuery] = useState(id ?? '')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState<number>(DEFAULT_PAGE_SIZE)
  const debouncedQuery = useDebouncedValue(query, 250)
  const onClick = useLinkClick()

  useEffect(() => {
    setPage(1)
  }, [debouncedQuery, pageSize])

  useEffect(() => {
    if (id !== null && id !== query) setQuery(id)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])

  const list = useApiResource(
    (signal) => fetchItems({ q: debouncedQuery, page, page_size: pageSize }, { signal }),
    [debouncedQuery, page, pageSize],
  )

  const detail = useApiResource(
    (signal) => (id ? fetchItem(id, { signal }) : Promise.resolve(null)),
    [id],
  )

  return (
    <section className="page" data-testid="page-items">
      <h1>道具</h1>
      <p className="page__lede">
        按客户端显示目录 ID 或名称搜索。字段含义按 batch_001 manifest：<code>client_shape_id</code>{' '}
        是显示目录 ID，不是玩家背包实例 ID；<code>category_code_raw</code> 是原始整数，本批不替类别代码发明业务含义。
      </p>

      {id ? (
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
              <>
                <dl className="keyvalue">
                  <div className="keyvalue__row">
                    <dt>client_shape_id</dt>
                    <dd>
                      <code>{rawTextOrMarker(detail.data.item.client_shape_id)}</code>
                    </dd>
                  </div>
                  <div className="keyvalue__row">
                    <dt>名称</dt>
                    <dd>
                      <SafeText value={detail.data.item.name} />
                    </dd>
                  </div>
                  <div className="keyvalue__row">
                    <dt>category_code_raw</dt>
                    <dd>
                      <code>{rawTextOrMarker(detail.data.item.category_code_raw)}</code>
                      <div className="keyvalue__note muted">原始整数，未解释为业务类别</div>
                    </dd>
                  </div>
                  <div className="keyvalue__row">
                    <dt>图片映射</dt>
                    <dd>
                      <code>image_id = {rawTextOrMarker(detail.data.item.image_id)}</code>{' '}
                      <ExplicitMappingBadge value={detail.data.item.image_mapping_explicit} />
                      <div className="keyvalue__note muted">
                        本轮没有图片资源 API：只展示映射 ID 与是否为显式映射，不提供图片预览，
                        也不探测对应资源是否存在。
                      </div>
                    </dd>
                  </div>
                  <div className="keyvalue__row">
                    <dt>来源</dt>
                    <dd>
                      <SourceTag
                        entry={detail.data.item.source_entry}
                        table={detail.data.item.source_table}
                      />{' '}
                      <ReviewStatusBadge status={detail.data.item.review_status} />
                    </dd>
                  </div>
                  <div className="keyvalue__row">
                    <dt>原始描述</dt>
                    <dd>
                      <SafeText value={detail.data.item.description_raw} className="raw-text" />
                      <div className="keyvalue__note muted">
                        按源文本原样显示（含 <code>#r</code> 等标记），不执行富文本标记，不做简繁转换。
                      </div>
                    </dd>
                  </div>
                </dl>
              </>
            ) : null}
          </AsyncSection>
        </div>
      ) : null}

      <SearchBar
        value={query}
        onChange={setQuery}
        placeholder="输入道具 ID（如 12）或名称关键字"
        label="搜索道具"
        hint="支持 ID 与名称；查询由后端执行，前端不读取 CSV。被隔离的记录不会出现在本表中。"
      />

      <AsyncSection
        loading={list.loading}
        error={list.error}
        empty={(list.data?.items.length ?? 0) === 0}
        onRetry={list.reload}
        loadingLabel="正在读取道具表…"
      >
        {list.data ? (
          <>
            <DataTable
              columns={columns}
              rows={list.data.items}
              rowKey={(row) => String(row.client_shape_id)}
              selectedKey={id}
              onRowClick={(row) => navigate(hrefFor('items', String(row.client_shape_id)))}
              testId="items-table"
            />
            <p className="muted" data-testid="items-empty-hint">
              若查不到记录：该行可能已被隔离（本批文档记载条目 1945 的 72548 仍在隔离中，
              其原始字节保留在「异常与证据」页），本页不会用占位名称伪装成正常道具。
            </p>
            <Pagination
              page={list.data.page}
              pageSize={list.data.page_size}
              total={list.data.total}
              onPage={setPage}
              onPageSize={setPageSize}
              loading={list.loading}
            />
          </>
        ) : null}
      </AsyncSection>
    </section>
  )
}
