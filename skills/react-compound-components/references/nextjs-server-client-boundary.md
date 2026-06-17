# Next.js server/client boundary — the full picture

This pattern is built on React Context and hooks (`createContext`, `useContext`,
`useState`), which are **client-only**. In the App Router, components are Server
Components by default and cannot call these hooks — the moment a file uses them
it needs `'use client'`.

The practical consequence: **a compound component is a Client Component**. The
root provider and every sub-component that reads context render on the client and
ship their JS to the browser. They can't be pure Server Components, so you don't
get RSC's zero-JS rendering or the ability to `await` data directly inside them.

This is **not** a reason to avoid the pattern — it's an effective, composable API
and the cost is usually small (a layout shell is cheap). You just need to wire
data and interactivity deliberately.

## 1. Fetch data in a Server Component, pass it in as props

Don't fetch inside the compound component. Keep the fetching in a Server Component
parent (where you can `await` directly) and pass plain data down as props. The
client compound tree becomes a pure rendering/interaction layer.

```tsx
// app/team/page.tsx — Server Component (no 'use client')
import Team from '@/components/Team';

export default async function TeamPage() {
  const team = await getTeam(); // server-side fetch, never reaches the client bundle
  return <Team team={team} gameweek={20} />; // Team is the client boundary
}
```

## 2. Server Components can still live *inside* the tree via `children` (the "donut")

Marking a component `'use client'` does **not** force everything it renders to be
client-side. Anything you pass through `children` (or any prop slot) is rendered
by *its own parent* — so a Server Component can be slotted into a client compound
shell. Use this "donut" pattern for server-rendered content (heavy lists,
server-only data) nested visually within the interactive layout.

```tsx
// page.tsx (Server Component)
<Dashboard onPlayerClick={...}>          {/* client shell */}
  <Dashboard.Section title="Feed">
    <ServerRenderedFeed />               {/* stays a Server Component */}
  </Dashboard.Section>
</Dashboard>
```

Note that dot-notation sub-components (`Dashboard.Section`) are themselves client
components — they're attached to the client root and read context. It's the
content you *pass into* them that can stay on the server.

## 3. Event handlers can't cross the server→client boundary

Props passed from a Server Component into a Client Component must be serializable.
**Functions are not serializable**, so you cannot pass an `onPlayerClick` handler
from a Server Component into the compound root (the "event handler props on root"
best practice assumes a client-side caller). Options:

- Make the immediate parent a Client Component (`'use client'`) so it can define
  the handler.
- Use a [Server Action](https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations)
  for mutations, which *can* be passed across the boundary.

## 4. If there's no shared state or interactivity, you may not need context at all

The whole point of the context machinery is sharing state without prop drilling.
For a purely static, presentational layout, a context-based compound component
forces an unnecessary client boundary. Plain composition (or keeping it as Server
Components) is lighter. Reach for this pattern when the shared-state/interaction
payoff justifies going client-side.
