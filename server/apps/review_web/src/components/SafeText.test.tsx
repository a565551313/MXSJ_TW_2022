import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { SafeFormula, SafeText } from './SafeText'

const HOSTILE = '<img src=x onerror="globalThis.__pwned = true"> <script>globalThis.__pwned = true</script>'

describe('safe text rendering', () => {
  it('renders source text as text, never as markup', () => {
    const { container } = render(<SafeText value={HOSTILE} />)
    const node = screen.getByTestId('safe-text')

    expect(node.textContent).toBe(HOSTILE)
    expect(container.querySelector('img')).toBeNull()
    expect(container.querySelector('script')).toBeNull()
    expect((globalThis as Record<string, unknown>).__pwned).toBeUndefined()
  })

  it('preserves client rich-text markers verbatim instead of interpreting them', () => {
    render(<SafeText value={'可以呼叫各種功能NPC以方便測試#r【類型】測試專用物品'} />)
    expect(screen.getByTestId('safe-text').textContent).toBe(
      '可以呼叫各種功能NPC以方便測試#r【類型】測試專用物品',
    )
  })

  it('shows formulas as opaque text without evaluating them', () => {
    const { container } = render(<SafeFormula value={"__import__('os').system('id')"} />)
    expect(screen.getByTestId('safe-formula').textContent).toBe("__import__('os').system('id')")
    expect(container.querySelector('script')).toBeNull()
  })

  it('marks empty source fields instead of showing 0', () => {
    render(<SafeText value={''} />)
    expect(screen.queryByTestId('safe-text')).toBeNull()
    expect(screen.getByText('（源字段为空）')).toBeInTheDocument()
    expect(screen.queryByText('0')).toBeNull()
  })

  it('keeps the literal value 0 distinguishable from an empty field', () => {
    render(<SafeText value={0} />)
    expect(screen.getByTestId('safe-text').textContent).toBe('0')
  })
})
