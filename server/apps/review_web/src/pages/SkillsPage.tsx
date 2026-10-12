import { useEffect, useState } from 'react'
import { DEFAULT_PAGE_SIZE } from '../api/contract'
import { fetchSkill, fetchSkills } from '../api/client'
import type { SkillDetail, SkillRecord } from '../api/types'
import { AsyncSection } from '../components/AsyncSection'
import { AmbiguousBadge, Badge, ReviewStatusBadge, SourceTag } from '../components/Badges'
import { Pagination, SearchBar } from '../components/Controls'
import { DataTable, type Column } from '../components/DataTable'
import { SafeFormula, SafeText } from '../components/SafeText'
import { useApiResource } from '../hooks/useApiResource'
import { useDebouncedValue } from '../hooks/useDebouncedValue'
import { isTrue, rawTextOrMarker } from '../lib/display'
import { hrefFor, navigate, useLinkClick } from '../lib/router'

const columns: Array<Column<SkillRecord>> = [
  {
    key: 'skill_id',
    label: '技能 ID',
    render: (row) => <code data-testid="skill-id">{rawTextOrMarker(row.skill_id)}</code>,
  },
  { key: 'name', label: '名称', render: (row) => <SafeText value={row.name} /> },
  {
    key: 'type_code_raw',
    label: 'type_code_raw',
    render: (row) => <code>{rawTextOrMarker(row.type_code_raw)}</code>,
  },
  {
    key: 'review_status',
    label: '复核状态',
    render: (row) => <ReviewStatusBadge status={row.review_status} />,
  },
]

function OverwritePanel({ detail }: { detail: SkillDetail }) {
  const overwrite = detail.overwrite
  if (!overwrite) {
    return (
      <div className="panel">
        <h2>重复键覆盖摘要</h2>
        <p className="muted">
          该技能 ID 不在 9 次重复键写入的覆盖清单中（清单见「异常与证据」页）。
        </p>
      </div>
    )
  }
  const identical = isTrue(overwrite.identical_values)
  return (
    <div className={identical ? 'panel' : 'panel panel--warning'} data-testid="overwrite-panel">
      <h2>重复键覆盖摘要</h2>
      <dl className="keyvalue">
        <div className="keyvalue__row">
          <dt>写入顺序 write_order</dt>
          <dd>
            <code>{rawTextOrMarker(overwrite.write_order)}</code>
          </dd>
        </div>
        <div className="keyvalue__row">
          <dt>字节码偏移 code_offset</dt>
          <dd>
            <code>{rawTextOrMarker(overwrite.code_offset)}</code>
          </dd>
        </div>
        <div className="keyvalue__row">
          <dt>旧值 → 新值</dt>
          <dd>
            <SafeText value={overwrite.old_name} /> → <SafeText value={overwrite.new_name} />
            {identical ? <Badge tone="neutral">identical_values = true</Badge> : <Badge tone="warn">值已改变</Badge>}
          </dd>
        </div>
        <div className="keyvalue__row">
          <dt>覆盖证据</dt>
          <dd>
            {identical
              ? '该次覆盖的旧值与新值相同：字典语义没有变化，但写入事实仍然保留，不因值相同而删除证据。'
              : '该次覆盖改变了值：不能只导出最终值而丢掉旧值。'}
            <div className="keyvalue__note muted">
              完整的旧值/新值源码树在 <code>overwrite_evidence.jsonl</code>；「异常与证据」页按写入顺序列出全部 9 次。
            </div>
          </dd>
        </div>
      </dl>
    </div>
  )
}

export function SkillsPage({ id }: { id: string | null }) {
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
    (signal) => fetchSkills({ q: debouncedQuery, page, page_size: pageSize }, { signal }),
    [debouncedQuery, page, pageSize],
  )

  const detail = useApiResource(
    (signal) => (id ? fetchSkill(id, { signal }) : Promise.resolve(null)),
    [id],
  )

  return (
    <section className="page" data-testid="page-skills">
      <h1>技能</h1>
      <p className="page__lede">
        展示原始描述与资源公式文本。公式<strong>只展示、不计算</strong>：前端不执行 eval、不解释公式、
        不展开客户端标记。条目 3205 的 719、4406 仍处于隔离状态，因此不在列表中。
      </p>

      {id ? (
        <div className="panel panel--detail" data-testid="skill-detail">
          <div className="panel__header">
            <h2>技能详情 #{id}</h2>
            <a href={hrefFor('skills')} onClick={(event) => onClick(event, hrefFor('skills'))}>
              返回列表
            </a>
          </div>
          <AsyncSection
            loading={detail.loading}
            error={detail.error}
            empty={!detail.loading && detail.data === null}
            onRetry={detail.reload}
            loadingLabel="正在读取技能详情…"
          >
            {detail.data ? (
              <>
                <div className="panel">
                  <h2>原始字段（条目 3205）</h2>
                  <dl className="keyvalue">
                    <div className="keyvalue__row">
                      <dt>skill_id</dt>
                      <dd>
                        <code>{rawTextOrMarker(detail.data.skill.skill_id)}</code>
                      </dd>
                    </div>
                    <div className="keyvalue__row">
                      <dt>名称</dt>
                      <dd>
                        <SafeText value={detail.data.skill.name} />
                      </dd>
                    </div>
                    <div className="keyvalue__row">
                      <dt>type_code_raw</dt>
                      <dd>
                        <code>{rawTextOrMarker(detail.data.skill.type_code_raw)}</code>
                        <div className="keyvalue__note muted">保留原始分类整数，不解释为业务类型</div>
                      </dd>
                    </div>
                    <div className="keyvalue__row">
                      <dt>来源</dt>
                      <dd>
                        <SourceTag
                          entry={detail.data.skill.source_entry}
                          table={detail.data.skill.source_table}
                        />{' '}
                        <ReviewStatusBadge status={detail.data.skill.review_status} />
                      </dd>
                    </div>
                  </dl>
                </div>

                <div className="panel">
                  <h2>原始描述 description_raw</h2>
                  <SafeText value={detail.data.skill.description_raw} className="raw-text" />
                  <div className="keyvalue__note muted">
                    按源文本原样显示；不执行其中的标记或脚本片段。
                  </div>
                </div>

                <div className="panel">
                  <h2>资源公式（原始文本）</h2>
                  <p className="muted">仅展示，不计算。空值与 0 分开显示，不补值。</p>
                  <dl className="keyvalue">
                    <div className="keyvalue__row">
                      <dt>fpneed_raw</dt>
                      <dd>
                        <SafeFormula value={detail.data.skill.fpneed_raw} />
                      </dd>
                    </div>
                    <div className="keyvalue__row">
                      <dt>mpneed_raw</dt>
                      <dd>
                        <SafeFormula value={detail.data.skill.mpneed_raw} />
                      </dd>
                    </div>
                    <div className="keyvalue__row">
                      <dt>hpneed_raw</dt>
                      <dd>
                        <SafeFormula value={detail.data.skill.hpneed_raw} />
                      </dd>
                    </div>
                  </dl>
                </div>

                <OverwritePanel detail={detail.data} />

                <div className="panel">
                  <h2>被宠物引用的情况</h2>
                  {detail.data.name_matches && detail.data.name_matches.length > 0 ? (
                    <ul className="chip-list" data-testid="skill-name-matches">
                      {detail.data.name_matches.map((match, index) => (
                        <li key={index}>
                          <span className="chip-list__name">{match.skill_name_raw}</span>
                          <span className="chip">ID {String(match.skill_id)}</span>
                          <span className="chip">match_count {match.match_count}</span>
                          {match.ambiguous ? <AmbiguousBadge count={match.match_count} /> : null}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="muted">
                      没有宠物候选名称精确匹配到该 ID（迁移中的名称匹配不重名、不做简繁或模糊匹配）。
                    </p>
                  )}
                </div>
              </>
            ) : null}
          </AsyncSection>
        </div>
      ) : null}

      <SearchBar
        value={query}
        onChange={setQuery}
        placeholder="输入技能 ID（如 229）或名称关键字"
        label="搜索技能"
        hint="同一名称可能命中多个 ID（如 229/255、329/355）：本页不默认选中任何一个。"
      />

      <AsyncSection
        loading={list.loading}
        error={list.error}
        empty={(list.data?.items.length ?? 0) === 0}
        onRetry={list.reload}
        loadingLabel="正在读取技能表…"
      >
        {list.data ? (
          <>
            <DataTable
              columns={columns}
              rows={list.data.items}
              rowKey={(row) => String(row.skill_id)}
              selectedKey={id}
              onRowClick={(row) => navigate(hrefFor('skills', String(row.skill_id)))}
              testId="skills-table"
            />
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
