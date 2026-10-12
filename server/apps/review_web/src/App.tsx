import { REVIEW_API_PREFIX } from './api/contract'
import { ErrorBoundary } from './components/ErrorBoundary'
import { FixtureModeBanner, ReviewNotice } from './components/Notices'
import { hrefFor, useLinkClick, useRoute, type RouteName } from './lib/router'
import { DATA_MODE } from './lib/runtimeMode'
import { AnomaliesPage } from './pages/AnomaliesPage'
import { ItemsPage } from './pages/ItemsPage'
import { MapsNpcsPage } from './pages/MapsNpcsPage'
import { OverviewPage } from './pages/OverviewPage'
import { PetsPage } from './pages/PetsPage'
import { SkillsPage } from './pages/SkillsPage'

const NAV: Array<{ name: RouteName; label: string; hint: string }> = [
  { name: 'overview', label: '批次概览', hint: '批次、计数、校验、隔离与缺失' },
  { name: 'items', label: '道具', hint: '按 ID / 名称搜索' },
  { name: 'pets', label: '宠物', hint: '主表、资质、候选与必带技能' },
  { name: 'skills', label: '技能', hint: '描述、公式、重复覆盖' },
  { name: 'maps', label: '地图 / NPC', hint: '按来源分开，不合成唯一表' },
  { name: 'anomalies', label: '异常与证据', hint: '隔离、缺失、歧义与原始字节' },
]

export function App() {
  const route = useRoute()
  const onClick = useLinkClick()
  const active = NAV.find((item) => item.name === route.name)

  const pageKey = `${route.name}:${route.id ?? ''}:${route.query.get('focus') ?? ''}`

  return (
    <div className="app">
      <header className="app__header">
        <div>
          <h1 className="app__title">MXSJ 静态数据复核浏览器</h1>
          <p className="app__subtitle">
            只读浏览 batch_001 复核材料 · 前端不读取仓库 CSV · 数据由 <code>{REVIEW_API_PREFIX}</code> 提供
          </p>
        </div>
      </header>

      <nav className="app__nav" aria-label="主导航">
        {NAV.map((item) => (
          <a
            key={item.name}
            className={route.name === item.name ? 'nav-tab nav-tab--active' : 'nav-tab'}
            href={hrefFor(item.name)}
            title={item.hint}
            aria-current={route.name === item.name ? 'page' : undefined}
            onClick={(event) => onClick(event, hrefFor(item.name))}
          >
            {item.label}
          </a>
        ))}
      </nav>

      <FixtureModeBanner />
      <ReviewNotice />

      <main className="app__main" aria-label={active ? active.label : '内容'}>
        <ErrorBoundary label={active ? active.label : '页面'} resetKey={pageKey}>
          {route.name === 'overview' ? <OverviewPage /> : null}
          {route.name === 'items' ? <ItemsPage id={route.id} /> : null}
          {route.name === 'pets' ? <PetsPage id={route.id} /> : null}
          {route.name === 'skills' ? <SkillsPage id={route.id} /> : null}
          {route.name === 'maps' ? <MapsNpcsPage /> : null}
          {route.name === 'anomalies' ? <AnomaliesPage focus={route.query.get('focus')} /> : null}
        </ErrorBoundary>
      </main>

      <footer className="app__footer">
        <p>
          数据模式：<code>{DATA_MODE}</code> · 接口前缀：<code>{REVIEW_API_PREFIX}</code> · 页面不含任何编辑、
          删除、导入或发布动作。
        </p>
        <p className="muted">
          接口契约：Agent H <code>server/docs/review_browser/API_CONTRACT.md</code>（v1.0.0，PR #22
          提交 9f6ab439）。适配层位于 <code>src/api/</code>；前端说明见{' '}
          <code>server/docs/review_browser/FRONTEND.md</code>。
        </p>
      </footer>
    </div>
  )
}
