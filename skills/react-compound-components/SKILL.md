---
name: react-compound-components
description: Guide for implementing React compound component patterns with dot notation in this codebase. Use when creating new UI components that have multiple related sub-components, building forms, dashboards, or pages with distinct sections, or when refactoring components that have complex prop drilling. Covers how to create context providers, define typed sub-components with displayName, and export namespaced APIs via dot notation. Activates for component composition, context providers, reusable UI patterns.
allowed-tools: Read, Write, Edit, Glob, Grep
---

# React Compound Components Pattern

## When to Use This Pattern

Use compound components when a component has multiple related sub-parts that need shared state — skip for simple 1-2 prop components or one-offs that won't be reused.

## Next.js Server/Client Boundary (Important)

This pattern requires `'use client'` — `createContext`, `useContext`, and `useState` are client-only.

- **Fetch data in a Server Component parent**, pass as props; content via `children` can still be a Server Component (the "donut" pattern).
- **Event handler props require a Client Component caller** — functions aren't serializable across the boundary; use Server Actions for mutations instead.
- **If there's no shared state or interactivity**, skip the pattern — plain composition avoids an unnecessary client boundary.

Full mechanics (donut pattern, why sub-components are themselves client, fix options): [references/nextjs-server-client-boundary.md](references/nextjs-server-client-boundary.md).

## Implementation Pattern

Create context, root, and sub-components in a single file:

```tsx
'use client';

import React, { createContext, useContext, type PropsWithChildren } from 'react';

// --- Context ---
interface MyComponentContextType {
  sharedState: string;
  onAction?: (value: string) => void;
}

const MyComponentContext = createContext<MyComponentContextType | null>(null);

function useMyComponentContext() {
  const context = useContext(MyComponentContext);
  if (!context) throw new Error('MyComponent compound components must be used within a MyComponent');
  return context;
}

// --- Sub-components ---
const MyComponentHeader: React.FC<{ title: string; subtitle?: string }> = ({ title, subtitle }) => (
  <header>
    <h1>{title}</h1>
    {subtitle && <p>{subtitle}</p>}
  </header>
);
MyComponentHeader.displayName = 'MyComponentHeader';

const MyComponentContent: React.FC<PropsWithChildren> = ({ children }) => {
  const { sharedState } = useMyComponentContext();
  return <div><span>State: {sharedState}</span>{children}</div>;
};
MyComponentContent.displayName = 'MyComponentContent';

const MyComponentFooter: React.FC<PropsWithChildren> = ({ children }) => (
  <footer>{children}</footer>
);
MyComponentFooter.displayName = 'MyComponentFooter';

// --- Root ---
interface MyComponentOwnProps {
  sharedState: string;
  onAction?: (value: string) => void;
  className?: string;
}

const MyComponent: React.FC<PropsWithChildren<MyComponentOwnProps>> & {
  Header: typeof MyComponentHeader;
  Content: typeof MyComponentContent;
  Footer: typeof MyComponentFooter;
} = ({ children, sharedState, onAction, className }) => (
  <MyComponentContext.Provider value={{ sharedState, onAction }}>
    <div className={className}>{children}</div>
  </MyComponentContext.Provider>
);

MyComponent.displayName = 'MyComponent';
MyComponent.Header = MyComponentHeader;
MyComponent.Content = MyComponentContent;
MyComponent.Footer = MyComponentFooter;

export default MyComponent;
```

## File Structure

```
components/
  MyComponent/
    MyComponent.tsx         # Main component with all sub-components
    MyComponent.module.scss # Styles
    index.tsx               # Re-exports
```

**index.tsx:**
```tsx
import MyComponent from './MyComponent';
export default MyComponent;
```

## Existing Compound Components

This codebase already ships several. Example:

```tsx
import Dashboard from '@/components/Dashboard';

<Dashboard onPlayerClick={handlePlayerClick}>
  <Dashboard.Header title="Team Name" subtitle="Manager Name" ctaText="Optimize" ctaHref="/optimize" />
  <Dashboard.Stats stats={[{ title: 'GW20', value: 65, description: 'Rank: 1,234' }]} />
  <Dashboard.PerformanceChart data={historyData} currentGameweek={20} />
  <Dashboard.TeamGrid title="Starting XI" players={startingXI} />
  <Dashboard.HotPlayers players={hotPlayers} />
</Dashboard>
```

**Before composing `Team`, `Dashboard`, `PlayersPage`, `AuthForm`, or `UIKit/Modal`, get the exact sub-component names and props from [references/existing-components.md](references/existing-components.md)** — don't guess them (e.g. it's `Dashboard.Deadline`/`.GameweekInfo`/`.AuthCTA` and `Team.Summary`/`Team.Position type="goa|def|mid|fwd"`). Open the component's own file to confirm anything not listed there.

## Best Practices

- **Backwards compatibility**: default to a `children ?? defaultContent` fallback in root when refactoring.
- **Event handlers on root**: pass them into the root, access via context in sub-components.
- **displayName on every sub-component**: required for readable React DevTools output.

## Migration Checklist

- [ ] Identify logical sub-sections of the component
- [ ] Create context type with shared state/handlers
- [ ] Create root component with context provider
- [ ] Extract sub-components with displayName
- [ ] Attach sub-components to root (`Root.SubComponent = ...`)
- [ ] Add backwards compatibility if needed
- [ ] Create `index.tsx` for clean exports
- [ ] Update existing usages
- [ ] Add TypeScript types for all props
