import type { ReactNode } from 'react'

export interface Column<T> {
  key: string
  label: string
  render: (row: T) => ReactNode
  numeric?: boolean
  /** When false the cell is still rendered (never hidden on narrow screens). */
  hideOnNarrow?: boolean
}

/**
 * Read-only table. No sorting/filtering of source semantics is applied here:
 * every row the API returns is rendered, including duplicates and zero ids.
 */
export function DataTable<T>({
  columns,
  rows,
  rowKey,
  caption,
  selectedKey,
  onRowClick,
  testId,
}: {
  columns: Array<Column<T>>
  rows: T[]
  rowKey: (row: T, index: number) => string
  caption?: ReactNode
  selectedKey?: string | null
  onRowClick?: (row: T) => void
  testId?: string
}) {
  return (
    <div className="table-scroll">
      <table className="data-table" data-testid={testId}>
        {caption ? <caption className="data-table__caption">{caption}</caption> : null}
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key} scope="col" className={column.numeric ? 'is-numeric' : undefined}>
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => {
            const key = rowKey(row, index)
            const selected = selectedKey !== undefined && selectedKey !== null && selectedKey === key
            return (
              <tr
                key={key}
                className={selected ? 'is-selected' : undefined}
                onClick={onRowClick ? () => onRowClick(row) : undefined}
                tabIndex={onRowClick ? 0 : undefined}
                onKeyDown={
                  onRowClick
                    ? (event) => {
                        if (event.key === 'Enter' || event.key === ' ') {
                          event.preventDefault()
                          onRowClick(row)
                        }
                      }
                    : undefined
                }
              >
                {columns.map((column) => (
                  <td
                    key={column.key}
                    data-label={column.label}
                    className={column.numeric ? 'is-numeric' : undefined}
                  >
                    {column.render(row)}
                  </td>
                ))}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
