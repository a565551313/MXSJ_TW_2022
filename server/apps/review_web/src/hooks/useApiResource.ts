import { useCallback, useEffect, useRef, useState, type DependencyList } from 'react'

export interface ApiResource<T> {
  data: T | null
  error: unknown | null
  /** True while a request is in flight, including the first one. */
  loading: boolean
  /** True when the last successful response was for different parameters. */
  reload: () => void
}

function isAbortError(error: unknown): boolean {
  return (
    typeof error === 'object' &&
    error !== null &&
    'name' in error &&
    (error as { name?: string }).name === 'AbortError'
  )
}

/**
 * Runs a loader whenever `deps` change.
 *
 * There is deliberately no fixture/fallback branch here: if the request fails,
 * `error` is set and `data` stays null. The UI shows the failure.
 */
export function useApiResource<T>(
  loader: (signal: AbortSignal) => Promise<T>,
  deps: DependencyList,
): ApiResource<T> {
  const loaderRef = useRef(loader)
  loaderRef.current = loader

  const [state, setState] = useState<{ data: T | null; error: unknown | null; loading: boolean }>({
    data: null,
    error: null,
    loading: true,
  })
  const [nonce, setNonce] = useState(0)

  useEffect(() => {
    const controller = new AbortController()
    let active = true
    setState((previous) => ({ data: previous.data, error: null, loading: true }))

    loaderRef.current(controller.signal).then(
      (data) => {
        if (!active) return
        setState({ data, error: null, loading: false })
      },
      (error: unknown) => {
        if (!active || isAbortError(error)) return
        setState({ data: null, error, loading: false })
      },
    )

    return () => {
      active = false
      controller.abort()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, nonce])

  const reload = useCallback(() => setNonce((value) => value + 1), [])

  return { data: state.data, error: state.error, loading: state.loading, reload }
}
