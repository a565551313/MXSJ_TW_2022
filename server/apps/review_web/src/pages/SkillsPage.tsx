import { useEffect, useState } from 'react'
import { DEFAULT_PAGE_SIZE } from '../api/contract'
import {
  getSkillDetail,
  listSkills,
  toSkillRow,
  type Envelope,
  type SkillDetail,
  type SkillOverwriteSummary,
  type SkillRow,
} from '../api/reviewApi'
import { AsyncSection } from '../components/AsyncSection'
import { AmbiguousBadge, Badge, ReviewStatusBadge, SourceTag } from '../components/Badges'
import { Pagination, SearchBar } from '../components/Controls'
import { DataTable, type Column } from '../components/DataTable'
import { RawJsonView } from '../components/RawJsonView'
import { SafeFormula, SafeText } from '../components/SafeText'
import { useApiResource } from '../hooks/useApiResource'
import { useDebouncedValue } from '../hooks/useDebouncedValue'
import { rawTextOrMarker } from '../lib/display'
import { hrefFor, navigate, useLinkClick } from '../lib/router'

const columns: Array<Column<SkillRow>> = [
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

function OverwritePanel({ overwrite }: { overwrite: SkillOverwriteSummary }) {
  const identical = overwrite.identical_values
  return (
    <div
      className={identical === false ? 'panel panel--warning' : 'panel'}
      data-testid="overwrite-panel"
    >
      <h2>重复键覆盖摘要</h2>
      <dl className="keyvalue">
        <div className="keyvalue__row">
          <dt>写入顺序 order</dt>
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
            {identical === true ? (
              <Badge tone="neutral">值相同（仍是写入）</Badge>
            ) : identical === false ? (
              <Badge tone="warn">值已改变</Badge>
            ) : (
              <Badge tone="warn">无法从字节判定（见下方原始证据）</Badge>
            )}
            <div className="keyvalue__note muted">
              名称由覆盖证据的字节字典判定（严格 CP950 解码）：<code>name</code> 字节无法解码时不会伪造名称。
            </div>
          </dd>
        </div>
      </dl>
      <details open={identical === false}>
        <summary>覆盖证据原始字节（old_value / new_value）</summary>
        <div className="raw-evidence" data-testid="overwrite-raw">
          <h4>old_value</h4>
          <RawJsonView value={overwrite.old_value as never} />
          <h4>new_value</h4>
          <RawJsonView value={overwrite.new_value as never} />
        </div>
      </details>
    </div>
  )
}

function SkillDetailPanel({ id }: { id: string }) {
  const detail = useApiResource<SkillDetail>((signal) => getSkillDetail(id, { signal }), [id])
  const onClick = useLinkClick()

  return (
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
                    <SourceTag entry={detail.data.skill.source_entry} table={detail.data.skill.source_table} />{' '}
                    <ReviewStatusBadge status={detail.data.skill.review_status} />
                  </dd>
                </div>
              </dl>
            </div>

            <div className="panel">
              <h2>原始描述 description_raw</h2>
              <SafeText value={detail.data.skill.description_raw} className="raw-text" />
              <div className="keyvalue__note muted">按源文本原样显示；不执行其中的标记或脚本片段。</div>
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

            {detail.data.overwrites.length === 0 ? (
              <div className="panel">
                <h2>重复键覆盖摘要</h2>
                <p className="muted" data-testid="overwrite-none">
                  <code>/overwrites?key={id}</code> 返回 0 条：该技能 ID 不在 9 次重复键写入的覆盖清单中。
                </p>
              </div>
            ) : (
              detail.data.overwrites.map((overwrite) => (
                <OverwritePanel key={overwrite.pk} overwrite={overwrite} />
              ))
            )}

            <div className="panel">
              <h2>被宠物引用的情况</h2>
              {detail.data.name_matches.length > 0 ? (
                <ul className="chip-list" data-testid="skill-name-matches">
                  {detail.data.name_matches.map((match, index) => (
                    <li key={index}>
                      <span className="chip-list__name">{match.skill_name_raw}</span>
                      <span className="chip">ID {String(match.skill_id)}</span>
                      <span className="chip">match_count {String(match.match_count ?? '（API 未提供）')}</span>
                      {match.ambiguous ? <AmbiguousBadge count={match.match_count ?? 0} /> : null}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="muted" data-testid="skill-name-matches-empty">
                  <code>/datasets/pet_skill_name_matches/records?skill_id={id}</code> 返回 0 条：
                  没有宠物候选名称精确匹配到该 ID（不做简繁转换或模糊匹配）。
                </p>
              )}
            </div>
          </>
        ) : null}
      </AsyncSection>
    </div>
  )
}

export function SkillsPage({ id }: { id: string | null }) {
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState<number>(DEFAULT_PAGE_SIZE)
  const debouncedQuery = useDebouncedValue(query, 250)

  useEffect(() => {
    setPage(1)
  }, [debouncedQuery, pageSize])

  const list = useApiResource<Envelope>(
    (signal) => listSkills({ page, pageSize, search: debouncedQuery }, { signal }),
    [page, pageSize, debouncedQuery],
  )

  const rows = (list.data?.records ?? []).map(toSkillRow)

  return (
    <section className="page" data-testid="page-skills">
      <h1>技能</h1>
      <p className="page__lede">
        展示原始描述与资源公式文本。公式<strong>只展示、不计算</strong>：前端不执行 eval、不解释公式、
        不展开客户端标记。条目 3205 的 719、4406 仍处于隔离状态，因此不在列表中。
      </p>

      {id ? <SkillDetailPanel id={id} /> : null}

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
        empty={(list.data?.records.length ?? 0) === 0}
        onRetry={list.reload}
        loadingLabel="正在读取技能表…"
      >
        {list.data ? (
          <>
            <DataTable
              columns={columns}
              rows={rows}
              rowKey={(row) => row.pk}
              selectedKey={id}
              onRowClick={(row) => row.skill_id && navigate(hrefFor('skills', row.skill_id))}
              testId="skills-table"
            />
            <Pagination
              page={page}
              pageSize={pageSize}
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
