/**
 * Anti-white-screen test.
 *
 * A page component is made to throw during render (as a coding mistake would).
 * The requirement is that the app must not blank out: the header, the navigation
 * and the notices stay on screen, the failing page shows a crash panel with the
 * message, and the other pages still work afterwards.
 */
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { renderApp } from './test/renderApp'
import { installCaptureFetch } from './test/hApiReplay'

vi.mock('./pages/ItemsPage', () => ({
  ItemsPage: () => {
    throw new Error('渲染时故意抛出的错误（测试）')
  },
}))

const LONG = { timeout: 4000 }

describe('page level error boundary', () => {
  it('keeps the shell and reports the crash instead of a blank page', async () => {
    const errors = vi.spyOn(console, 'error').mockImplementation(() => {})
    installCaptureFetch()
    renderApp('/items')

    const panel = await screen.findByTestId('crash-panel', {}, LONG)
    expect(panel.textContent).toContain('页面区块渲染失败：道具')
    expect(screen.getByTestId('crash-message').textContent).toContain('渲染时故意抛出的错误（测试）')
    expect(panel.textContent).toContain('没有任何字段被补成空值来兜底')

    // The shell survives: it is an error inside one page, not a dead app.
    expect(screen.getByTestId('review-notice')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: '异常与证据' })).toBeInTheDocument()

    // Other pages still render normally.
    const user = userEvent.setup()
    await user.click(screen.getByRole('link', { name: '异常与证据' }))
    await waitFor(() => expect(screen.getByTestId('page-anomalies')).toBeInTheDocument(), LONG)
    expect(screen.queryByTestId('crash-panel')).toBeNull()

    errors.mockRestore()
  })
})
