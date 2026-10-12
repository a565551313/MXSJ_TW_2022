import type { ReactNode } from 'react'
import { isApiError } from '../api/client'

export function LoadingPanel({ label = '加载中…' }: { label?: string }) {
  return (
    <div className="panel panel--state" role="status" aria-live="polite" data-testid="loading-state">
      <span className="spinner" aria-hidden="true" />
      {label}
    </div>
  )
}

export function EmptyPanel({ children }: { children: ReactNode }) {
  return (
    <div className="panel panel--state" data-testid="empty-state">
      {children}
    </div>
  )
}

export function ErrorPanel({
  error,
  onRetry,
  title = '无法加载数据',
}: {
  error: unknown
  onRetry?: () => void
  title?: string
}) {
  const apiError = isApiError(error) ? error : null
  return (
    <div className="panel panel--error" role="alert" data-testid="error-state">
      <h3>{title}</h3>
      {apiError?.kind === 'schema' ? (
        <p className="error-schema-hint">
          这是<strong>接口结构错误</strong>：HTTP 请求成功，但响应结构与契约不符。
          页面不会把缺失字段补成空数组或 0 来掩盖差异。
        </p>
      ) : null}
      <p data-testid="error-message">
        {apiError ? apiError.message : error instanceof Error ? error.message : String(error)}
      </p>
      <dl className="error-detail">
        {apiError ? (
          <>
            <dt>请求</dt>
            <dd>
              <code>{apiError.url}</code>
            </dd>
            <dt>类型</dt>
            <dd>{apiError.kind}</dd>
            {apiError.status !== undefined ? (
              <>
                <dt>HTTP</dt>
                <dd>{apiError.status}</dd>
              </>
            ) : null}
            {apiError.code ? (
              <>
                <dt>代码</dt>
                <dd>{apiError.code}</dd>
              </>
            ) : null}
            {apiError.details !== undefined ? (
              <>
                <dt>响应内容</dt>
                <dd>
                  <pre className="raw-fallback">
                    {typeof apiError.details === 'string'
                      ? apiError.details
                      : JSON.stringify(apiError.details, null, 2).slice(0, 2000)}
                  </pre>
                </dd>
              </>
            ) : null}
          </>
        ) : null}
      </dl>
      <p className="muted">
        本页不会在 API 失败时改用测试夹具或假数据；请确认复核 API 已启动，且端点与{' '}
        <code>server/docs/review_browser/API_CONTRACT.md</code> 一致。
      </p>
      {onRetry ? (
        <button type="button" className="button" onClick={onRetry} data-testid="retry-button">
          重試
        </button>
      ) : null}
    </div>
  )
}

export function AsyncSection({
  loading,
  error,
  empty,
  onRetry,
  loadingLabel,
  children,
}: {
  loading: boolean
  error: unknown | null
  empty: boolean
  onRetry?: () => void
  loadingLabel?: string
  children: ReactNode
}) {
  if (error) return <ErrorPanel error={error} onRetry={onRetry} />
  if (loading) return <LoadingPanel label={loadingLabel} />
  if (empty) return <EmptyPanel>没有符合条件的记录。</EmptyPanel>
  return <>{children}</>
}
