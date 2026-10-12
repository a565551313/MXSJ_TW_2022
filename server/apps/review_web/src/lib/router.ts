import { useEffect, useState } from 'react'

export type RouteName = 'overview' | 'items' | 'pets' | 'skills' | 'maps' | 'anomalies'

export interface Route {
  name: RouteName
  /** Detail identifier for /items/:id, /pets/:id and /skills/:id. */
  id: string | null
  query: URLSearchParams
  path: string
}

const NAVIGATION_EVENT = 'review-web:navigate'

const KNOWN: RouteName[] = ['overview', 'items', 'pets', 'skills', 'maps', 'anomalies']

export function parsePath(pathname: string, search = ''): Route {
  const path = pathname.replace(/\/+$/, '') || '/'
  const segments = path.split('/').filter((segment) => segment.length > 0)
  const head = segments[0] ?? 'overview'
  const name = (KNOWN as string[]).includes(head) ? (head as RouteName) : 'overview'
  const id = segments.length > 1 ? decodeURIComponent(segments.slice(1).join('/')) : null
  return {
    name,
    id: id && id.length > 0 ? id : null,
    query: new URLSearchParams(search),
    path,
  }
}

export function useRoute(): Route {
  const [route, setRoute] = useState<Route>(() =>
    parsePath(window.location.pathname, window.location.search),
  )

  useEffect(() => {
    const sync = () => setRoute(parsePath(window.location.pathname, window.location.search))
    window.addEventListener('popstate', sync)
    window.addEventListener(NAVIGATION_EVENT, sync)
    return () => {
      window.removeEventListener('popstate', sync)
      window.removeEventListener(NAVIGATION_EVENT, sync)
    }
  }, [])

  return route
}

export function navigate(to: string): void {
  if (to === window.location.pathname + window.location.search) return
  window.history.pushState(null, '', to)
  window.dispatchEvent(new Event(NAVIGATION_EVENT))
}

export function hrefFor(name: RouteName, id?: string | null, query?: Record<string, string>): string {
  const base = name === 'overview' ? '/' : `/${name}`
  const path = id ? `${base}/${encodeURIComponent(id)}` : base
  const search = new URLSearchParams(query ?? {}).toString()
  return search.length > 0 ? `${path}?${search}` : path
}

/**
 * Anchor that keeps native link semantics (middle click, open in new tab) while
 * routing client side for plain left clicks.
 */
export function useLinkClick(): (event: React.MouseEvent<HTMLAnchorElement>, to: string) => void {
  return (event, to) => {
    if (event.defaultPrevented) return
    if (event.button !== 0) return
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return
    event.preventDefault()
    navigate(to)
  }
}
