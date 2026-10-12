import { IS_FIXTURE_MODE } from '../lib/runtimeMode'
import { rawText } from '../lib/display'

/**
 * Permanent reminder that this data is a review candidate, not an approved
 * rule set. It is always rendered, on every page, independent of the API.
 */
export function ReviewNotice({
  batchId,
  status,
  nativeVerified,
  notice,
}: {
  batchId?: string | null
  status?: unknown
  nativeVerified?: boolean | null
  notice?: unknown
}) {
  const statusText = rawText(status)
  const noticeText = rawText(notice)
  return (
    <section className="notice notice--review" role="note" data-testid="review-notice">
      <h2>复核候选，非正式规则</h2>
      <p>
        本页展示的 batch_001 行是<strong>静态候选解码</strong>结果：可用于人工复核与目录浏览，
        <strong>不是</strong>原生加载器验证结果，也<strong>不是</strong>正式服务端规则表。
      </p>
      <ul>
        <li>未做简繁转换；名称、描述、颜色标记与资源公式均按源文本原样展示，不解释、不计算。</li>
        <li>隔离记录、缺失资质与同名技能多 ID 候选继续保留：不补零、不自动择一、不折叠重复记录。</li>
        <li>页面不提供任何编辑、删除、导入或发布动作。</li>
      </ul>
      <p className="notice__meta">
        {batchId ? (
          <>
            批次：<code>{batchId}</code>
          </>
        ) : null}
        {statusText ? (
          <>
            {' · '}状态：<code>{statusText}</code>
          </>
        ) : null}
        {nativeVerified === false ? ' · 原生验证：false' : null}
        {nativeVerified === true ? ' · 原生验证：true（与本页“复核候选”定位冲突，请核对后端）' : null}
      </p>
      {noticeText ? <p className="notice__api-notice">{noticeText}</p> : null}
    </section>
  )
}

/** Only visible in the explicit, non-default fixture mode. */
export function FixtureModeBanner() {
  if (!IS_FIXTURE_MODE) return null
  return (
    <section className="notice notice--fixture" role="alert" data-testid="fixture-banner">
      <h2>FIXTURE 演示模式：非真实 API 数据</h2>
      <p>
        当前由 <code>npm run dev:fixture</code> 启动，代理指向本地夹具服务
        （<code>fixtures/serve-fixture-api.mjs</code>），只提供 batch_001 的一小部分真实行样本，
        用于界面走查与自动化测试。
      </p>
      <p>
        <strong>这不是接口联调结果</strong>，不能作为真实数据接入的证据。默认模式
        <code>npm run dev</code> 只连接 Python 复核 API，失败时显示错误而不会回退到这里。
      </p>
    </section>
  )
}
