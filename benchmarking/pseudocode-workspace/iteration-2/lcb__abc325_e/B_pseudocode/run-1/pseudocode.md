# Plan: minimum travel time city 1 → N, car then train

Verdict: logic-heavy (graph modeling + Dijkstra on dense graph, switch-once
constraint, integer overflow). Planning the core first.

## Data & invariants
- N cities, complete graph, D[i][j] symmetric, D[i][i]=0, D[i][j]>0 for i≠j.
- Car edge cost i→j = D[i][j]*A.
- Train edge cost i→j = D[i][j]*B + C.
- Two "modes": 0 = still allowed to use car (haven't switched), 1 = train only.
  Switch car→train is free, happens at a city, irreversible.
- Key insight: once you switch to train you never go back. So path =
  car-only prefix (cities 1..k) then train-only suffix (cities k..N), switch at
  some city k.
- Invariant: dist_car[v] = min time to reach v using only car.
  dist_train[v] = min time to reach v where the train phase has begun (i.e. you
  may have switched at v or earlier and arrived by train).

## Control flow
Approach: two Dijkstra-like passes on a dense graph (N≤1000, O(N^2) per pass fine).

1. Compute dist_car[v] for all v: Dijkstra from node 1 with car edge weights
   D[u][v]*A. dist_car[1]=0.

2. Compute dist_train[v]: a node may enter the train phase by switching at any
   city u, at cost dist_car[u] (switch is free). Then travel by train.
   So run Dijkstra where initial distance of every node u is dist_car[u]
   (representing "switch at u, then continue by train"), and relax using train
   edges D[u][v]*B + C.
   - init dist_train[u] = dist_car[u] for all u (you could switch immediately on
     arrival, including doing zero train moves).
   - relax: dist_train[v] = min(dist_train[v], dist_train[u] + D[u][v]*B + C).

3. Answer = dist_train[N].
   (dist_train[N] already covers the pure-car case via dist_car[N], since
   dist_train initialized to dist_car and N's own switch costs nothing.)

Dijkstra on dense graph: use O(N^2) array version (no heap needed, N=1000 →
1e6 ops per pass), pick unvisited min each step.

## Edge cases & failure modes
- Direct car only, no train (sample 2 effectively): covered because
  dist_train init = dist_car, so answer ≤ dist_car[N].
- Switch at city 1 immediately (all train): covered, dist_car[1]=0 so
  dist_train init at 1 = 0, train edges from 1 included.
- Overflow: D up to 1e6, A/B up to 1e6 → single edge up to 1e12; path up to
  ~1000 edges → ~1e15, plus C. Use Python ints (unbounded) — no overflow.
- Self loops D[i][i]=0 harmless.
- N=2: works, single edge each mode.

## Interface contract
- Read N A B C then N×N matrix from stdin.
- Print single integer dist_train[N].
- Pure computation, no mutation of input semantics.
