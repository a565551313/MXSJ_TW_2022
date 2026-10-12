import type { ReactNode } from 'react'
import type { AptitudeStatus, AptitudeStatusInfo } from '../api/reviewApi'
import { isTrue, rawText } from '../lib/display'

export function Badge({
  children,
  tone = 'neutral',
  title,
}: {
  children: ReactNode
  tone?: 'neutral' | 'warn' | 'danger' | 'info' | 'ok'
  title?: string
}) {
  return (
    <span className={`badge badge--${tone}`} title={title}>
      {children}
    </span>
  )
}

/** Every row keeps its source review status visible; nothing claims native proof. */
export function ReviewStatusBadge({ status }: { status?: unknown }) {
  const text = rawText(status)
  if (!text) return <span className="muted">（未标注）</span>
  const isCandidate = text.includes('candidate') || text.includes('not_native')
  return (
    <Badge tone={isCandidate ? 'warn' : 'neutral'} title="来源复核状态，逐字显示，未转换">
      {text}
    </Badge>
  )
}

export function SourceTag({ entry, table }: { entry?: unknown; table?: unknown }) {
  const entryText = rawText(entry)
  const tableText = rawText(table)
  if (!entryText && !tableText) return null
  return (
    <span className="source-tag">
      {entryText ? <span>条目 {entryText}</span> : null}
      {tableText ? <span>{tableText}</span> : null}
    </span>
  )
}

export function ZeroIdBadge({ value, label }: { value: unknown; label: string }) {
  const text = rawText(value)
  if (text === null || text.trim() !== '0') return null
  return (
    <Badge tone="info" title="来源记录就是 0；不隐藏、不重新编号">
      {label} 0
    </Badge>
  )
}

export function ExplicitMappingBadge({ value }: { value: unknown }) {
  return isTrue(value) ? (
    <Badge tone="ok" title="SHAPETABLE 中存在显式映射">
      显式映射
    </Badge>
  ) : (
    <Badge tone="neutral" title="无显式映射，按客户端 Shape2Image 规则回退到自身 shape ID">
      回退映射
    </Badge>
  )
}

export function DuplicateBadge({ count }: { count: number }) {
  if (count <= 1) return null
  return (
    <Badge tone="warn" title="同一场景/键存在多条记录；不做折叠">
      重复 ×{count}
    </Badge>
  )
}

const APTITUDE_TONE: Record<AptitudeStatus, 'ok' | 'warn' | 'danger' | 'neutral'> = {
  present: 'ok',
  missing_in_source_table: 'danger',
  quarantined: 'danger',
  unknown: 'neutral',
}

export const APTITUDE_STATUS_TEXT: Record<AptitudeStatus, string> = {
  present: '资质存在',
  missing_in_source_table: '资质缺失',
  quarantined: '资质隔离',
  unknown: '资质状态未知',
}

export function AptitudeStatusBadge({ info }: { info: AptitudeStatusInfo }) {
  return <Badge tone={APTITUDE_TONE[info.status]}>{APTITUDE_STATUS_TEXT[info.status]}</Badge>
}

export function AmbiguousBadge({ count }: { count: number }) {
  return (
    <Badge tone="warn" title="同名技能命中多个 ID；全部候选都保留，不默认取第一个">
      同名多 ID（{count} 个候选）
    </Badge>
  )
}
