import { useEffect, useState, type FormEvent, type ReactNode } from 'react'
import { PAGE_SIZE_OPTIONS } from '../api/contract'

export function SearchBar({
  value,
  onChange,
  onSubmit,
  placeholder,
  label = '搜索',
  hint,
}: {
  value: string
  onChange: (next: string) => void
  onSubmit?: () => void
  placeholder?: string
  label?: string
  hint?: ReactNode
}) {
  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
    onSubmit?.()
  }
  return (
    <form className="search-bar" onSubmit={handleSubmit} role="search">
      <label className="search-bar__label" htmlFor="review-search">
        {label}
      </label>
      <input
        id="review-search"
        className="search-bar__input"
        type="search"
        value={value}
        placeholder={placeholder}
        autoComplete="off"
        onChange={(event) => onChange(event.target.value)}
      />
      <button type="submit" className="button">
        搜索
      </button>
      {value.length > 0 ? (
        <button
          type="button"
          className="button button--ghost"
          onClick={() => {
            onChange('')
            onSubmit?.()
          }}
        >
          清除
        </button>
      ) : null}
      {hint ? <p className="search-bar__hint muted">{hint}</p> : null}
    </form>
  )
}

export function Pagination({
  page,
  pageSize,
  total,
  onPage,
  onPageSize,
  loading,
}: {
  page: number
  pageSize: number
  total: number
  onPage: (next: number) => void
  onPageSize?: (next: number) => void
  loading?: boolean
}) {
  const pageCount = pageSize > 0 ? Math.max(1, Math.ceil(total / pageSize)) : 1
  const [jump, setJump] = useState(String(page))

  useEffect(() => {
    setJump(String(page))
  }, [page])

  const hasPrevious = page > 1
  const hasNext = page < pageCount

  return (
    <nav className="pagination" aria-label="分页" data-testid="pagination">
      <button type="button" className="button" disabled={!hasPrevious || loading} onClick={() => onPage(page - 1)}>
        上一页
      </button>
      <span className="pagination__status" aria-live="polite">
        第 {page} / {pageCount} 页 · 共 {total.toLocaleString('en-US')} 条
        {loading ? '（加载中…）' : ''}
      </span>
      <button type="button" className="button" disabled={!hasNext || loading} onClick={() => onPage(page + 1)}>
        下一页
      </button>
      <form
        className="pagination__jump"
        onSubmit={(event) => {
          event.preventDefault()
          const parsed = Number.parseInt(jump, 10)
          if (Number.isFinite(parsed)) onPage(Math.min(Math.max(1, parsed), pageCount))
        }}
      >
        <label htmlFor="page-jump">跳至</label>
        <input
          id="page-jump"
          className="pagination__jump-input"
          value={jump}
          inputMode="numeric"
          onChange={(event) => setJump(event.target.value)}
        />
        <button type="submit" className="button button--ghost">
          跳转
        </button>
      </form>
      {onPageSize ? (
        <label className="pagination__size">
          每页
          <select
            value={pageSize}
            onChange={(event) => onPageSize(Number(event.target.value))}
            aria-label="每页条数"
          >
            {PAGE_SIZE_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>
      ) : null}
    </nav>
  )
}
