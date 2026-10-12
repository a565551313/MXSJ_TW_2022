import { useEffect, useState } from 'react'
import { DEFAULT_PAGE_SIZE } from '../api/contract'
import {
  getPetDetail,
  loadAptitudeStatusIndex,
  listPets,
  toPetRow,
  type AptitudeStatusInfo,
  type CandidateSkill,
  type Envelope,
  type PetDetail,
  type PetRow,
  type RequiredSkill,
  type SkillNameMatch,
} from '../api/reviewApi'
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

type PetListRow = PetRow & { aptitude_status?: AptitudeStatusInfo }

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
  {
    key: 'carry_grade',
    label: 'carry_grade',
    render: (row) => <code>{rawTextOrMarker(row.carry_grade)}</code>,
  },
  {
    key: 'maxskillnum_raw',
    label: 'maxskillnum_raw',
    render: (row) => <code>{rawTextOrMarker(row.maxskillnum_raw)}</code>,
  },
  {
    key: 'aptitude_status',
    label: '资质',
    render: (row) =>
      row.aptitude_status ? (
        <AptitudeStatusBadge info={row.aptitude_status} />
      ) : (
        <span className="muted">（未查询）</span>
      ),
  },
]

/**
 * Loads the aptitude status column from three bulk requests
 * (`/quarantine?entry_index=2954`, `/missing-aptitudes`, `pet_aptitudes`), not
 * from three requests per visible pet. On failure the column stays "未查询"
 * rather than pretending every pet is fine.
 */
function useAptitudeStatuses(
  rows: PetListRow[],
  enabled: boolean,
): Map<string, AptitudeStatusInfo> {
  const [map, setMap] = useState<Map<string, AptitudeStatusInfo>>(new Map())
  const ids = rows.map((row) => row.client_shape_id).filter((id): id is string => Boolean(id))
  const key = ids.join(',')

  useEffect(() => {
    if (!enabled || ids.length === 0) {
      setMap(new Map())
      return
    }
    const controller = new AbortController()
    let active = true
    loadAptitudeStatusIndex({ signal: controller.signal })
      .then((index) => {
        if (!active) return
        setMap(new Map(ids.map((petId) => [petId, index.statusOf(petId)] as const)))
      })
      .catch(() => {
        if (active) setMap(new Map())
      })
    return () => {
      active = false
      controller.abort()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, enabled])

  return map
}

function AptitudeTable({ detail }: { detail: PetDetail }) {
  if (!detail.aptitude) return null
  const onClick = useLinkClick()
  const fields = detail.aptitude.fields
  return (
    <div className="panel">
      <h2>资质（条目 2954）</h2>
      <dl className="aptitude-grid" data-testid="aptitude-table">
        {fields.map((field) => (
          <div className="aptitude-grid__cell" key={field.label}>
            <dt>{field.label}</dt>
            <dd>{field.value === null || field.value === '' ? '（源字段为空）' : field.value}</dd>
          </div>
        ))}
      </dl>
      <p className="muted">
        十个字段名按源表原文保留（如 <code>法力資質</code>、<code>法力資質最大值</code>），
        不重新解释为成长、面板或服务端上限公式；界面不对这些值做简繁转换。
        记录身份：<code>{String(detail.aptitude.record._pk ?? '')}</code>。
      </p>
      <p className="muted">
        该行来自 <code>/datasets/pet_aptitudes/records?client_shape_id=…</code>；
        隔离判定见下方状态区。
      </p>
      {detail.aptitude_status.status === 'quarantined' ? null : (
        <a
          href={hrefFor('anomalies')}
          onClick={(event) => onClick(event, hrefFor('anomalies'))}
        >
          查看异常与证据 →
        </a>
      )}
    </div>
  )
}

function AptitudeSection({ detail }: { detail: PetDetail }) {
  const onClick = useLinkClick()
  const info = detail.aptitude_status

  if (info.status === 'missing_in_source_table') {
    return (
      <div className="panel panel--warning" data-testid="aptitude-missing">
        <h3>资质缺失：{APTITUDE_STATUS_TEXT.missing_in_source_table}</h3>
        <p>
          宠物主表（条目 2027）存在该记录，但资质表（条目 2954）中没有对应行。缺失原因：
          <code>{rawTextOrMarker(info.reason)}</code>。
        </p>
        <p>
          <strong>本页不会把它显示为 0</strong>，也不会用其它来源补一行资质。
        </p>
        <p>
          <a href={hrefFor('anomalies')} onClick={(event) => onClick(event, hrefFor('anomalies'))}>
            在「异常与证据」页查看缺失清单与原因 →
          </a>
        </p>
      </div>
    )
  }

  if (info.status === 'quarantined') {
    return (
      <div className="panel panel--warning" data-testid="aptitude-quarantined">
        <h3>资质记录处于隔离状态</h3>
        <p>
          该记录在保存参数下出现未解决的数值冲突，因此整行继续隔离。隔离原因（接口原文）：
          <code>{rawTextOrMarker(info.reason)}</code>。
        </p>
        <p>
          <strong>不展示尚未批准的候选值</strong>，也不交换两列、不补零：未获批准的候选不会作为数值出现在本页。
          原始字节保留在「异常与证据」页。
        </p>
        <p>
          <a
            href={info.evidence_id ? hrefFor('anomalies', null, { focus: info.evidence_id }) : hrefFor('anomalies')}
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

  if (info.status === 'present') return <AptitudeTable detail={detail} />

  return (
    <div className="panel" data-testid="aptitude-unknown">
      <h3>资质状态未知</h3>
      <p className="muted">
        API 未返回可判定的资质状态（既没有资质行、也没有缺失记录或隔离记录），本页不猜测、不补零。
      </p>
    </div>
  )
}

function SkillMatchChips({ matches, name }: { matches: SkillNameMatch[]; name: string | null }) {
  const onClick = useLinkClick()
  if (matches.length === 0) {
    return (
      <span className="muted" data-testid="skill-matches-empty">
        未解析到候选 ID（<code>{name ?? '（源字段为空）'}</code> 在技能名称匹配表中没有精确匹配）
      </span>
    )
  }
  const ambiguous = matches.some((match) => match.ambiguous === true) || matches.length > 1
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
        <span className="muted chips__note">
          全部候选都保留（match_count={String(matches[0]?.match_count ?? '（API 未提供）')}），未默认选择第一个。
        </span>
      ) : null}
    </span>
  )
}

function RequiredSkillsSection({ skills }: { skills: RequiredSkill[] }) {
  if (skills.length === 0) {
    return (
      <div className="panel">
        <h2>必带技能（DATA.mustSkillName）</h2>
        <p className="muted" data-testid="required-skills-empty">
          <code>/datasets/pet_required_skills/records?client_shape_id=…</code> 返回 0 条：
          源记录没有提供 <code>mustSkillName</code> 字段，不补一个空技能，也不补 ID 0。
        </p>
      </div>
    )
  }
  return (
    <div className="panel">
      <h2>必带技能（DATA.mustSkillName）</h2>
      <ul className="skill-list" data-testid="required-skills">
        {skills.map((skill, index) => (
          <li key={`${skill.skill_name_raw ?? ''}-${index}`}>
            <SafeText value={skill.skill_name_raw} />
            <SkillMatchChips matches={skill.matches} name={skill.skill_name_raw} />
          </li>
        ))}
      </ul>
    </div>
  )
}

function CandidateSkillsSection({ skills, truncated }: { skills: CandidateSkill[]; truncated: boolean }) {
  if (skills.length === 0) {
    return (
      <div className="panel">
        <h2>候选技能（maySkillLst）</h2>
        <p className="muted" data-testid="candidate-skills-empty">
          该宠物在 <code>pet_skill_candidates</code> 中没有候选技能记录。
        </p>
      </div>
    )
  }
  return (
    <div className="panel">
      <h2>候选技能（maySkillLst）</h2>
      <p className="muted">
        按源 tuple 顺序（sequence 从 0 开始）排序展示，保留重复；顺序不代表概率。
        关联查询会取全部相关记录，不只第一页。
      </p>
      {truncated ? (
        <div className="panel--warning" role="alert">
          该宠物的候选技能超过前端单次关联查询上限，列表可能不完整，请勿据此判断技能数量。
        </div>
      ) : null}
      <ol className="skill-list skill-list--ordered" data-testid="candidate-skills">
        {skills.map((skill, index) => (
          <li key={`${skill.sequence ?? 'x'}-${index}`}>
            <span className="skill-list__seq">sequence {rawTextOrMarker(skill.sequence)}</span>
            <SafeText value={skill.skill_name_raw} />
            <SkillMatchChips matches={skill.matches} name={skill.skill_name_raw} />
          </li>
        ))}
      </ol>
    </div>
  )
}

function PetDetailPanel({ id }: { id: string }) {
  const detail = useApiResource<PetDetail>((signal) => getPetDetail(id, { signal }), [id])
  const onClick = useLinkClick()

  return (
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
                    <SourceTag entry={detail.data.pet.source_entry} table={detail.data.pet.source_table} />{' '}
                    <ReviewStatusBadge status={detail.data.pet.review_status} />
                  </dd>
                </div>
              </dl>
            </div>

            <AptitudeSection detail={detail.data} />
            <RequiredSkillsSection skills={detail.data.required_skills} />
            <CandidateSkillsSection skills={detail.data.candidate_skills} truncated={detail.data.truncated} />

            <div className="panel">
              <h2>计数一致性提示</h2>
              <p className="muted">
                候选技能 {detail.data.candidate_skills.length} 条 · 必带技能 {detail.data.required_skills.length} 条
                · 与 <code>maxskillnum_raw</code>（{rawTextOrMarker(detail.data.pet.maxskillnum_raw)}）
                的关系未获批准，本页不做上限校验或裁剪。
              </p>
            </div>
          </>
        ) : null}
      </AsyncSection>
    </div>
  )
}

export function PetsPage({ id }: { id: string | null }) {
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState<number>(DEFAULT_PAGE_SIZE)
  const debouncedQuery = useDebouncedValue(query, 250)

  useEffect(() => {
    setPage(1)
  }, [debouncedQuery, pageSize])

  const list = useApiResource<Envelope>(
    (signal) => listPets({ page, pageSize, search: debouncedQuery }, { signal }),
    [page, pageSize, debouncedQuery],
  )

  const baseRows = (list.data?.records ?? []).map(toPetRow)
  const statuses = useAptitudeStatuses(baseRows, !list.loading && !list.error)
  const rows: PetListRow[] = baseRows.map((row) => ({
    ...row,
    aptitude_status: row.client_shape_id ? statuses.get(row.client_shape_id) : undefined,
  }))

  return (
    <section className="page" data-testid="page-pets">
      <h1>宠物</h1>
      <p className="page__lede">
        主表（条目 2027）、资质（条目 2954）、候选技能与必带技能分开呈现。资质缺失或隔离会明确标出，
        不会显示为 0；同名技能的全部候选 ID 都保留。
      </p>

      {id ? <PetDetailPanel id={id} /> : null}

      <SearchBar
        value={query}
        onChange={setQuery}
        placeholder="输入宠物 ID（如 2800）或名称关键字"
        label="搜索宠物"
        hint="资质状态由 pet_aptitudes / pet_aptitude_missing / quarantine 三个接口组合判定，不用默认值兜底。"
      />

      <AsyncSection
        loading={list.loading}
        error={list.error}
        empty={(list.data?.records.length ?? 0) === 0}
        onRetry={list.reload}
        loadingLabel="正在读取宠物主表…"
      >
        {list.data ? (
          <>
            <DataTable
              columns={columns}
              rows={rows}
              rowKey={(row) => row.pk}
              selectedKey={id}
              onRowClick={(row) => row.client_shape_id && navigate(hrefFor('pets', row.client_shape_id))}
              testId="pets-table"
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
