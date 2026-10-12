import { useEffect, useState } from 'react'
import { DEFAULT_PAGE_SIZE } from '../api/contract'
import { fetchPet, fetchPets } from '../api/client'
import type {
  AptitudeStatus,
  AptitudeStatusInfo,
  CandidateSkill,
  PetAptitude,
  PetDetail,
  PetListRow,
  PetSkillNameMatch,
  RequiredSkill,
} from '../api/types'
import { AsyncSection } from '../components/AsyncSection'
import {
  APTITUDE_STATUS_TEXT,
  AmbiguousBadge,
  AptitudeStatusBadge,
  ReviewStatusBadge,
  SourceTag,
} from '../components/Badges'
import { Pagination, SearchBar } from '../components/Controls'
import { DataTable, type Column } from '../components/DataTable'
import { SafeText } from '../components/SafeText'
import { useApiResource } from '../hooks/useApiResource'
import { useDebouncedValue } from '../hooks/useDebouncedValue'
import { rawTextOrMarker } from '../lib/display'
import { hrefFor, navigate, useLinkClick } from '../lib/router'

function normalizeAptitudeStatus(row: PetListRow): AptitudeStatusInfo | null {
  const value = row.aptitude_status
  if (!value) return null
  if (typeof value === 'string') {
    return { status: value as AptitudeStatus }
  }
  return value
}

const columns: Array<Column<PetListRow>> = [
  {
    key: 'client_shape_id',
    label: '宠物 ID',
    render: (row) => <code data-testid="pet-id">{rawTextOrMarker(row.client_shape_id)}</code>,
  },
  { key: 'name', label: '名称', render: (row) => <SafeText value={row.name} /> },
  { key: 'liupai_raw', label: '流派', render: (row) => <SafeText value={row.liupai_raw} /> },
  {
    key: 'attack_type_raw',
    label: '攻击类型',
    render: (row) => <SafeText value={row.attack_type_raw} />,
  },
  { key: 'carry_grade', label: 'carry_grade', render: (row) => <code>{rawTextOrMarker(row.carry_grade)}</code> },
  {
    key: 'maxskillnum_raw',
    label: 'maxskillnum_raw',
    render: (row) => <code>{rawTextOrMarker(row.maxskillnum_raw)}</code>,
  },
  {
    key: 'aptitude_status',
    label: '资质',
    render: (row) => {
      const info = normalizeAptitudeStatus(row)
      if (!info) return <span className="muted">（API 未提供）</span>
      return <AptitudeStatusBadge info={info} />
    },
  },
]

const APTITUDE_COLUMN_ORDER = [
  '法力資質',
  '法力資質最大值',
  '防禦資質',
  '防禦資質最大值',
  '攻擊資質',
  '攻擊資質最大值',
  '速度資質',
  '速度資質最大值',
  '體力資質',
  '體力資質最大值',
]

function AptitudeTable({ aptitude }: { aptitude: PetAptitude }) {
  const keys = Object.keys(aptitude).filter(
    (key) => key !== 'client_shape_id' && key !== 'source_entry' && key !== 'source_table' && key !== 'review_status',
  )
  const ordered = [
    ...APTITUDE_COLUMN_ORDER.filter((key) => keys.includes(key)),
    ...keys.filter((key) => !APTITUDE_COLUMN_ORDER.includes(key)),
  ]
  return (
    <dl className="aptitude-grid" data-testid="aptitude-table">
      {ordered.map((key) => (
        <div className="aptitude-grid__cell" key={key}>
          <dt>{key}</dt>
          <dd>{rawTextOrMarker(aptitude[key])}</dd>
        </div>
      ))}
    </dl>
  )
}

function SkillMatchChips({ matches }: { matches: PetSkillNameMatch[] }) {
  const onClick = useLinkClick()
  if (matches.length === 0) {
    return <span className="muted">未解析到候选 ID（该名称在技能表中没有精确匹配）</span>
  }
  const ambiguous = matches.some((match) => match.ambiguous) || matches.length > 1
  return (
    <span className="chips" data-testid="skill-matches">
      <span className="chips__label">候选技能 ID：</span>
      {matches.map((match) => (
        <a
          key={String(match.skill_id)}
          className="chip chip--link"
          href={hrefFor('skills', String(match.skill_id))}
          onClick={(event) => onClick(event, hrefFor('skills', String(match.skill_id)))}
        >
          {String(match.skill_id)}
        </a>
      ))}
      {ambiguous ? <AmbiguousBadge count={matches.length} /> : null}
      {matches.length > 1 ? (
        <span className="muted chips__note">全部候选都保留，未默认选择第一个。</span>
      ) : null}
    </span>
  )
}

function AptitudeSection({ detail }: { detail: PetDetail }) {
  const onClick = useLinkClick()
  const info: AptitudeStatusInfo =
    detail.aptitude_status ?? { status: detail.aptitude ? 'present' : 'unknown' }

  if (info.status === 'missing_in_source_table') {
    return (
      <div className="panel panel--warning" data-testid="aptitude-missing">
        <h3>资质缺失：{APTITUDE_STATUS_TEXT.missing_in_source_table}</h3>
        <p>
          宠物主表（条目 2027）存在该记录，但资质表（条目 2954）中没有对应行。
          缺失原因：<code>{rawTextOrMarker(info.reason)}</code>。
        </p>
        <p>
          <strong>本页不会把它显示为 0</strong>，也不会用其它来源补一行资质。
        </p>
      </div>
    )
  }

  if (info.status === 'quarantined') {
    return (
      <div className="panel panel--warning" data-testid="aptitude-quarantined">
        <h3>资质记录处于隔离状态</h3>
        <p>
          该行在保存参数下出现未解决的数值冲突（例如源字段「法力資質」高于其对应的最大值列），
          因此整行继续隔离。
        </p>
        <p>
          <strong>不展示尚未批准的候选值</strong>，也不交换两列、不补零：未获批准的候选
          不会作为数值出现在本页。原始字节保留在「异常与证据」页。
        </p>
        <p>
          <a
            href={
              info.evidence_id
                ? hrefFor('anomalies', null, { focus: info.evidence_id })
                : hrefFor('anomalies')
            }
            onClick={(event) =>
              onClick(
                event,
                info.evidence_id
                  ? hrefFor('anomalies', null, { focus: info.evidence_id })
                  : hrefFor('anomalies'),
              )
            }
          >
            查看隔离记录与原始字节 →
          </a>
        </p>
      </div>
    )
  }

  if (info.status === 'present' && detail.aptitude) {
    return (
      <div className="panel">
        <h2>资质（条目 2954）</h2>
        <AptitudeTable aptitude={detail.aptitude} />
        <p className="muted">
          十个字段名按源表原文保留（如 <code>法力資質</code>、<code>法力資質最大值</code>），
          不重新解释为成长、面板或服务端上限公式；界面不对这些值做简繁转换。
        </p>
      </div>
    )
  }

  return (
    <div className="panel">
      <h3>资质状态未知</h3>
      <p className="muted">
        API 未返回可判定的资质状态（status = <code>{info.status}</code>），本页不猜测、不补零。
      </p>
    </div>
  )
}

function RequiredSkillsSection({ skills }: { skills: RequiredSkill[] }) {
  if (skills.length === 0) {
    return (
      <div className="panel">
        <h2>必带技能（DATA.mustSkillName）</h2>
        <p className="muted">
          源记录没有提供 <code>mustSkillName</code> 字段：不补一个空技能，也不补 ID 0。
        </p>
      </div>
    )
  }
  return (
    <div className="panel">
      <h2>必带技能（DATA.mustSkillName）</h2>
      <ul className="skill-list" data-testid="required-skills">
        {skills.map((skill, index) => (
          <li key={`${skill.skill_name_raw}-${index}`}>
            <SafeText value={skill.skill_name_raw} />
            <SkillMatchChips matches={skill.matches} />
          </li>
        ))}
      </ul>
    </div>
  )
}

function CandidateSkillsSection({ skills }: { skills: CandidateSkill[] }) {
  if (skills.length === 0) {
    return (
      <div className="panel">
        <h2>候选技能（maySkillLst）</h2>
        <p className="muted">该宠物在源表中没有候选技能元组。</p>
      </div>
    )
  }
  const ordered = [...skills].sort((a, b) => Number(a.sequence) - Number(b.sequence))
  return (
    <div className="panel">
      <h2>候选技能（maySkillLst）</h2>
      <p className="muted">
        保留源 tuple 顺序（从 0 开始），保留重复；顺序不代表概率。
      </p>
      <ol className="skill-list skill-list--ordered" data-testid="candidate-skills">
        {ordered.map((skill, index) => (
          <li key={`${skill.sequence}-${index}`}>
            <span className="skill-list__seq">sequence {rawTextOrMarker(skill.sequence)}</span>
            <SafeText value={skill.skill_name_raw} />
            <SkillMatchChips matches={skill.matches} />
          </li>
        ))}
      </ol>
    </div>
  )
}

export function PetsPage({ id }: { id: string | null }) {
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
    (signal) => fetchPets({ q: debouncedQuery, page, page_size: pageSize }, { signal }),
    [debouncedQuery, page, pageSize],
  )

  const detail = useApiResource(
    (signal) => (id ? fetchPet(id, { signal }) : Promise.resolve(null)),
    [id],
  )

  return (
    <section className="page" data-testid="page-pets">
      <h1>宠物</h1>
      <p className="page__lede">
        主表（条目 2027）、资质（条目 2954）、候选技能与必带技能分开呈现。资质缺失或隔离会明确标出，
        不会显示为 0；同名技能的全部候选 ID 都保留。
      </p>

      {id ? (
        <div className="panel panel--detail" data-testid="pet-detail">
          <div className="panel__header">
            <h2>宠物详情 #{id}</h2>
            <a href={hrefFor('pets')} onClick={(event) => onClick(event, hrefFor('pets'))}>
              返回列表
            </a>
          </div>
          <AsyncSection
            loading={detail.loading}
            error={detail.error}
            empty={!detail.loading && detail.data === null}
            onRetry={detail.reload}
            loadingLabel="正在读取宠物详情…"
          >
            {detail.data ? (
              <>
                <div className="panel">
                  <h2>主表（条目 2027）</h2>
                  <dl className="keyvalue">
                    <div className="keyvalue__row">
                      <dt>client_shape_id</dt>
                      <dd>
                        <code>{rawTextOrMarker(detail.data.pet.client_shape_id)}</code>
                      </dd>
                    </div>
                    <div className="keyvalue__row">
                      <dt>名称</dt>
                      <dd>
                        <SafeText value={detail.data.pet.name} />
                      </dd>
                    </div>
                    <div className="keyvalue__row">
                      <dt>liupai_raw</dt>
                      <dd>
                        <SafeText value={detail.data.pet.liupai_raw} />
                        <div className="keyvalue__note muted">源字段 liupai，未解释流派规则</div>
                      </dd>
                    </div>
                    <div className="keyvalue__row">
                      <dt>attack_type_raw</dt>
                      <dd>
                        <SafeText value={detail.data.pet.attack_type_raw} />
                      </dd>
                    </div>
                    <div className="keyvalue__row">
                      <dt>carry_grade</dt>
                      <dd>
                        <code>{rawTextOrMarker(detail.data.pet.carry_grade)}</code>
                      </dd>
                    </div>
                    <div className="keyvalue__row">
                      <dt>maxskillnum_raw</dt>
                      <dd>
                        <code>{rawTextOrMarker(detail.data.pet.maxskillnum_raw)}</code>
                        <div className="keyvalue__note muted">
                          不把 maxskillnum 擅自解释为服务端硬上限
                        </div>
                      </dd>
                    </div>
                    <div className="keyvalue__row">
                      <dt>address_raw</dt>
                      <dd>
                        <SafeText value={detail.data.pet.address_raw} className="raw-text" />
                      </dd>
                    </div>
                    <div className="keyvalue__row">
                      <dt>来源</dt>
                      <dd>
                        <SourceTag
                          entry={detail.data.pet.source_entry}
                          table={detail.data.pet.source_table}
                        />{' '}
                        <ReviewStatusBadge status={detail.data.pet.review_status} />
                      </dd>
                    </div>
                  </dl>
                </div>

                <AptitudeSection detail={detail.data} />
                <RequiredSkillsSection skills={detail.data.required_skills ?? []} />
                <CandidateSkillsSection skills={detail.data.candidate_skills ?? []} />

                <div className="panel">
                  <h2>计数一致性提示</h2>
                  <p className="muted">
                    候选技能 {detail.data.candidate_skills?.length ?? 0} 条 · 必带技能{' '}
                    {detail.data.required_skills?.length ?? 0} 条 ·
                    与 <code>maxskillnum_raw</code>（{rawTextOrMarker(detail.data.pet.maxskillnum_raw)}）
                    的关系未获批准，本页不做上限校验或裁剪。
                  </p>
                </div>
              </>
            ) : null}
          </AsyncSection>
        </div>
      ) : null}

      <SearchBar
        value={query}
        onChange={setQuery}
        placeholder="输入宠物 ID（如 2800）或名称关键字"
        label="搜索宠物"
        hint="资质缺失（如 3010、4021、4022）与资质隔离（如 2800）都会在列表中标出。"
      />

      <AsyncSection
        loading={list.loading}
        error={list.error}
        empty={(list.data?.items.length ?? 0) === 0}
        onRetry={list.reload}
        loadingLabel="正在读取宠物主表…"
      >
        {list.data ? (
          <>
            <DataTable
              columns={columns}
              rows={list.data.items}
              rowKey={(row) => String(row.client_shape_id)}
              selectedKey={id}
              onRowClick={(row) => navigate(hrefFor('pets', String(row.client_shape_id)))}
              testId="pets-table"
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
