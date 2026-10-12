import { Component, type ErrorInfo, type ReactNode } from 'react'
import { schemaIssuesOf } from '../api/client'

/**
 * Keeps a render-time failure inside one page section instead of blanking the
 * whole application. Nothing is hidden: the message, the stack and (for schema
 * errors) the offending JSON paths are printed, and a retry button re-mounts the
 * section.
 */
export class ErrorBoundary extends Component<
  { children: ReactNode; label: string; resetKey?: string },
  { error: Error | null; info: ErrorInfo | null }
> {
  override state: { error: Error | null; info: ErrorInfo | null } = { error: null, info: null }

  static getDerivedStateFromError(error: Error) {
    return { error, info: null }
  }

  override componentDidCatch(error: Error, info: ErrorInfo) {
    this.setState({ error, info })
  }

  override componentDidUpdate(previous: { resetKey?: string }) {
    if (previous.resetKey !== this.props.resetKey && this.state.error) {
      this.setState({ error: null, info: null })
    }
  }

  override render() {
    const { error, info } = this.state
    if (!error) return this.props.children

    const issues = schemaIssuesOf(error)

    return (
      <div className="crash-panel" role="alert" data-testid="crash-panel">
        <h2>页面区块渲染失败：{this.props.label}</h2>
        <p>
          这是前端渲染错误，不是“没有数据”。<strong>没有</strong>任何字段被补成空值来兜底；
          请把下面的信息报给开发者。
        </p>
        <p data-testid="crash-message">{error.message}</p>
        {error.stack ? <pre className="raw-fallback">{error.stack.slice(0, 2000)}</pre> : null}
        {issues ? (
          <>
            <h3>接口结构问题</h3>
            <ul>
              {issues.map((issue, index) => (
                <li key={index}>
                  <code>{issue.path}</code>：期望 {issue.expected}，实际 {issue.actual}
                </li>
              ))}
            </ul>
            <p className="muted">
              请求：<code>{error instanceof Error && 'url' in error ? String(error.url) : '（未知）'}</code>
            </p>
          </>
        ) : null}
        {info?.componentStack ? (
          <details>
            <summary>组件栈</summary>
            <pre className="raw-fallback">{info.componentStack.slice(0, 1500)}</pre>
          </details>
        ) : null}
        <button
          type="button"
          className="button"
          onClick={() => this.setState({ error: null, info: null })}
          data-testid="crash-retry"
        >
          重试
        </button>
      </div>
    )
  }
}
