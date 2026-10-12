import type { AnomalyBoard } from '../api/reviewApi'
import { evaluateInvariants } from '../lib/invariants'

/**
 * Shows the batch_001 review invariants and whether the live API response still
 * satisfies them. The list of invariants is a specification; every verdict and
 * every "actual" string is derived from API data at render time.
 */
export function InvariantCheck({ board }: { board: AnomalyBoard }) {
  const results = evaluateInvariants(board)
  const failed = results.filter((result) => !result.ok)

  return (
    <div className="panel" data-testid="invariant-panel">
      <h2>本批不变量自检</h2>
      <p className="muted">
        下面是 batch_001 文档要求保留的语义。判定结果完全来自接口返回值，不写死在页面里：
        若后端停止隔离某条记录、丢掉同名技能的候选 ID 或开始补零，这里会显示「未通过」。
      </p>
      <ul className="invariant-list">
        {results.map((result) => (
          <li key={result.id} className={result.ok ? 'invariant is-ok' : 'invariant is-failed'}>
            <span
              className={result.ok ? 'badge badge--ok' : 'badge badge--danger'}
              data-testid="invariant-verdict"
            >
              {result.ok ? '通过' : '未通过'}
            </span>
            <span className="invariant__label">{result.label}</span>
            <span className="invariant__actual muted">接口实际值：{result.actual}</span>
          </li>
        ))}
      </ul>
      {failed.length > 0 ? (
        <p className="invariant-summary" role="alert">
          有 {failed.length} 项不变量未通过：请先核对后端与导出器，不要据此更新正式数据。
        </p>
      ) : (
        <p className="invariant-summary muted">
          全部 {results.length} 项不变量在本接口返回值下成立。这不改变“复核候选”的定位。
        </p>
      )}
    </div>
  )
}
