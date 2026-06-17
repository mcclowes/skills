# Existing compound components in this codebase

The real dot-notation APIs for the compound components already shipped here.
Use these exact sub-component names and props — don't invent variants. When in
doubt, open the component's own file (e.g. `components/Dashboard/Dashboard.tsx`).

## Team (`components/Team/`)

```tsx
import Team from '@/components/Team';

<Team team={teamData} gameweek={20}>
  <Team.ShareButton />
  <Team.Summary />
  <Team.Formation>
    <Team.Position type="goa" />
    <Team.Position type="def" />
    <Team.Position type="mid" />
    <Team.Position type="fwd" />
    <Team.Bench />
  </Team.Formation>
</Team>

// Backwards compatible — renders default composition
<Team team={teamData} gameweek={20} />
```

- `Team.ShareButton` — share button with loading state
- `Team.Summary` — stats summary bar (cost, predicted, transfers)
- `Team.Formation` — wrapper for position rows
- `Team.Position` — position row (`type: 'goa' | 'def' | 'mid' | 'fwd'`)
- `Team.Bench` — bench players section

## Dashboard (`components/Dashboard/`)

```tsx
import Dashboard from '@/components/Dashboard';

<Dashboard
  className={styles.pageContainer}
  onPlayerClick={handlePlayerClick}
  onHotPlayerClick={handleHotPlayerClick}
>
  <Dashboard.Header
    title="Team Name"
    subtitle="Manager Name"
    ctaText="Optimize your team"
    ctaHref="/optimize"
  />

  <Dashboard.Stats
    stats={[
      { title: 'GW20', value: 65, description: 'Rank: 1,234' },
      { title: 'Overall', value: 1250, description: 'Rank: 50,000' },
    ]}
  />

  <Dashboard.PerformanceChart data={historyData} currentGameweek={20} />

  <Dashboard.Deadline gameweekName="GW21" deadlineTime={deadline} />

  <Dashboard.TeamGrid title="Starting XI" players={startingXI} />
  <Dashboard.TeamGrid title="Bench" players={bench} />

  <Dashboard.HotPlayers players={hotPlayers} />

  <Dashboard.GameweekInfo gameweek={gameweekData} />

  <Dashboard.AuthCTA isLoggedIn={!!user} hasFplTeamId={!!fplTeamId} />
</Dashboard>;
```

- `Dashboard.Header` — page header with title, subtitle, CTA
- `Dashboard.Stats` — row of stat cards
- `Dashboard.Section` — generic section wrapper
- `Dashboard.PerformanceChart` — weekly performance chart
- `Dashboard.Deadline` — next deadline display
- `Dashboard.TeamGrid` — player card grid
- `Dashboard.HotPlayers` — hot players section
- `Dashboard.GameweekInfo` — gameweek info for welcome page
- `Dashboard.AuthCTA` — login/signup prompt

## PlayersPage (`components/PlayersPage/`)

```tsx
import PlayersPage from '@/components/PlayersPage';

<PlayersPage
  className={styles.pageContainer}
  view={view}
  onTabChange={handleTabChange}
  refetching={refetching}
>
  <PlayersPage.Header title="Players" />
  <PlayersPage.Tabs />

  <PlayersPage.SearchInput
    value={search}
    onChange={setSearch}
    placeholder="Search players..."
  />

  <PlayersPage.Table
    data={players}
    columns={columns}
    sortBy={sortBy}
    sortOrder={sortOrder}
    onSort={handleSort}
    onRowClick={handleRowClick}
  />

  <PlayersPage.LoadingSkeleton />
  <PlayersPage.ErrorState error={error} onRetry={handleRetry} />
  <PlayersPage.EmptyState onRetry={handleRetry} />
  <PlayersPage.InlineError error={error} onRetry={handleRetry} />
</PlayersPage>;
```

## AuthForm (`components/AuthForm/`)

```tsx
import AuthForm from '@/components/AuthForm';

<AuthForm
  onSubmit={handleSubmit}
  loading={loading}
  error={error}
  success={success}
  hideFormOnSuccess
>
  <AuthForm.Header title="Welcome back" subtitle="Sign in to your account" />

  <AuthForm.Messages redirectMessage={redirectMessage} />

  <AuthForm.Form>
    <AuthForm.Group>
      <AuthForm.Label htmlFor="email">Email</AuthForm.Label>
      <AuthForm.Input
        id="email"
        name="email"
        type="email"
        placeholder="you@example.com"
        required
        autoComplete="email"
      />
    </AuthForm.Group>

    <AuthForm.Group>
      <AuthForm.Label htmlFor="password" forgotPasswordLink>
        Password
      </AuthForm.Label>
      <AuthForm.Input
        id="password"
        name="password"
        type="password"
        placeholder="Your password"
        required
        autoComplete="current-password"
      />
    </AuthForm.Group>

    <AuthForm.SubmitButton loadingText="Signing in...">
      Sign in
    </AuthForm.SubmitButton>
  </AuthForm.Form>

  <AuthForm.Footer>
    Don't have an account? <AuthForm.Link href="/signup">Sign up</AuthForm.Link>
  </AuthForm.Footer>
</AuthForm>;
```

## Modal (`components/UIKit/Modal/`)

```tsx
import Modal from '@/components/UIKit/Modal';

<Modal open={isOpen} doClose={handleClose} closeIcon>
  <Modal.Inner size="medium">
    <Modal.Header>Modal Title</Modal.Header>
    <Modal.Content>
      <p>Modal content goes here</p>
    </Modal.Content>
  </Modal.Inner>
</Modal>;
```
