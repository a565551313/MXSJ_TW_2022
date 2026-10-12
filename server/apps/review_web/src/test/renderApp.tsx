import { render, type RenderResult } from '@testing-library/react'
import { App } from '../App'

/** Renders the whole app at `path`, as the browser would after a reload. */
export function renderApp(path = '/'): RenderResult {
  window.history.pushState(null, '', path)
  return render(<App />)
}
