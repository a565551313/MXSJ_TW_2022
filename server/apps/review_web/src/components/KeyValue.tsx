import type { ReactNode } from 'react'

export interface FieldSpec {
  label: string
  value: ReactNode
  /** Rendered under the value, e.g. the original source column name. */
  note?: ReactNode
}

export function KeyValue({ fields, testId }: { fields: FieldSpec[]; testId?: string }) {
  return (
    <dl className="keyvalue" data-testid={testId}>
      {fields.map((field) => (
        <div className="keyvalue__row" key={field.label}>
          <dt>{field.label}</dt>
          <dd>
            {field.value}
            {field.note ? <div className="keyvalue__note muted">{field.note}</div> : null}
          </dd>
        </div>
      ))}
    </dl>
  )
}
