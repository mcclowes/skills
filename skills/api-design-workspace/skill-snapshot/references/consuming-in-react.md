# Consuming the `issues` pattern in React

Reference implementation for clients consuming the `issues` array. Use when a developer asks how to *handle* these responses — typing them, rendering errors vs warnings, or wiring them through an SDK.

## Types

```tsx
type IssueSeverity = 'error' | 'warning' | 'info'

interface IssueMessage {
  title: string
  detail: string
}

interface IssueLinks {
  documentation?: string
  portal?: string
  api?: string
}

interface IssueThirdParty {
  provider: string
  code?: string
  message?: string
}

interface Issue {
  issue: string
  severity: IssueSeverity
  dateTime: string
  active?: boolean
  message?: IssueMessage
  links?: IssueLinks
  thirdParty?: IssueThirdParty
}

interface ApiResponse {
  correlationId: string
  issues: Issue[]
}
```

Note `issue` is typed as `string`, not a union — consumers must tolerate unknown codes as the taxonomy grows. The code carries the whole classification as `{domain}.{class}.{reason}`; there is no separate `type` field, so read the class from the code (the second segment) when you need to branch on it.

## Forwarding issues from a form

```tsx
import { useState } from 'react'

interface VerificationFormProps {
  onIssue: (issues: Issue[], correlationId: string) => void
}

function VerificationForm({ onIssue }: VerificationFormProps) {
  const [loading, setLoading] = useState(false)

  async function handleSubmit() {
    setLoading(true)

    try {
      const response = await fetch('/api/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Correlation-ID': crypto.randomUUID(),
        },
        body: JSON.stringify({ documentType: 'passport' }),
      })

      const data: ApiResponse = await response.json()

      if (!response.ok && data.issues?.length) {
        onIssue(data.issues, data.correlationId)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <button onClick={handleSubmit} disabled={loading}>
      {loading ? 'Verifying...' : 'Verify'}
    </button>
  )
}
```

## Rendering errors and warnings consistently

```tsx
export default function App() {
  const [issues, setIssues] = useState<Issue[]>([])
  const [correlationId, setCorrelationId] = useState<string | null>(null)

  function handleIssue(issues: Issue[], correlationId: string) {
    setIssues(issues)
    setCorrelationId(correlationId)
  }

  const errors = issues.filter((i) => i.severity === 'error')
  const warnings = issues.filter((i) => i.severity === 'warning')

  return (
    <div>
      <VerificationForm onIssue={handleIssue} />

      {errors.map((issue, idx) => (
        <div key={idx} role="alert">
          <strong>{issue.message?.title ?? issue.issue}</strong>
          <p>{issue.message?.detail}</p>
          {issue.links?.documentation && (
            <a href={issue.links.documentation}>Find out more</a>
          )}
        </div>
      ))}

      {warnings.map((issue, idx) => (
        <div key={idx} role="status">
          <strong>{issue.message?.title ?? issue.issue}</strong>
          <p>{issue.message?.detail}</p>
        </div>
      ))}

      {correlationId && <small>Reference: {correlationId}</small>}
    </div>
  )
}
```

Two details worth keeping: fall back to the machine code (`issue.issue`) when `message` is absent, and always surface the `correlationId` so a user can quote it to support. `role="alert"` vs `role="status"` mirrors the `error`/`warning` split for assistive tech.

## SDK-level integration

If your API has an SDK or wrapper, surface issues through a provider pattern so cross-cutting handling (like auth redirects) lives in one place:

```tsx
function EmbedderApp() {
  function handleIssue(issues: Issue[], correlationId: string) {
    // The class is the second segment of the issue code — parse, don't store twice.
    const unauthorized = issues.find((i) => i.issue.split('.')[1] === 'unauthorized')

    if (unauthorized) {
      redirectToLogin({
        reason: unauthorized.message?.title,
        ref: correlationId,
      })
    }
  }

  return (
    <ApiProvider onIssue={handleIssue}>
      <Verification />
    </ApiProvider>
  )
}
```
