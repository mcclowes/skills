# ABC325 E — Car / Train shortest path

## Problem restated
- N cities, symmetric distance matrix D (D[i][i]=0, D[i][j]>0 for i≠j).
- Car edge i→j cost = D[i][j] * A.
- Train edge i→j cost = D[i][j] * B + C.
- Start in car mode at city 1. May switch car→train at a city, for free, once
  (irreversibly). End at city N.
- Minimize total time.

## Key insight
Two modes form a layered graph:
- Layer 0 (CAR): can move by car between any cities; can drop down to layer 1
  (train) at the same city for 0 cost (the one-way switch).
- Layer 1 (TRAIN): can move by train between any cities; cannot go back to car.

Once in train mode you stay in train mode. So an optimal route is:
  car from city 1 ... reach some city k (k may be 1, meaning switch immediately,
  or k may be N, meaning never use train) ... then train to N.

Because all-car or all-train segments are themselves shortest paths in a
complete graph, but the graph is complete and edge costs satisfy triangle-ish
behaviour only sometimes (train has +C per hop, so multi-hop train can be worse
or better than direct). So we cannot assume direct hop is optimal — must run a
real shortest path.

## Data & invariants
- nodes: state = (city, mode), mode in {0=car, 1=train}. 2N states.
- dist[state] = best known time from start state (city0, car).
- Invariant (Dijkstra): when a state is popped from the min-heap, dist[state] is
  final/optimal. Never relax an already-finalized state to a smaller value.
- Edge costs are non-negative (A,B,C,D ≥ 0 given constraints ≥1), so Dijkstra valid.

## Control flow
Graph is dense (complete), N up to 1000 → 2N=2000 states, each with up to N
neighbors. Plain O(V^2) Dijkstra is fine (2000^2 = 4e6). Heap-based also fine.
Use O(V^2) Dijkstra to avoid heap overhead / be safe.

```
read N, A, B, C
read D[N][N]

# states indexed 0..2N-1: car state for city c = c; train state for city c = N + c
INF = large
dist[*] = INF
dist[city0 car = 0] = 0
visited[*] = false

repeat 2N times:
  u = unvisited state with min dist   # linear scan
  if dist[u] == INF: break
  visited[u] = true
  (city, mode) = decode(u)

  if mode == car (u < N):
    # 1) free switch to train at same city
    relax(train_state(city)) with cost dist[u] + 0
    # 2) car moves to every other city j
    for j in 0..N-1, j != city:
      relax(car_state(j)) with dist[u] + D[city][j]*A
  else: # train mode
    # train moves to every other city j (no switch back)
    for j in 0..N-1, j != city:
      relax(train_state(j)) with dist[u] + D[city][j]*B + C

answer = min(dist[car_state(N-1)], dist[train_state(N-1)])
print answer
```

`relax(v, newcost)`: if not visited[v] and newcost < dist[v]: dist[v]=newcost.

## Edge cases & failure modes
- N=2: trivial, still handled by loop.
- Self loop D[i][i]=0: skip j==city (cost would be 0 car / C train, harmless but
  skip to avoid useless train-with-C self relax; skipping is safe since staying
  put never helps).
- Switching at city N itself counts: answer takes min over both modes at city N,
  so a pure-car route ending at N is captured by car_state(N-1).
- Never switching: car_state(N-1) covers it.
- Switch immediately at city 1: handled — at city0 car we relax train_state(0).
- Overflow: max cost ~ (N-1 hops) * (D*max ... ) → roughly 1000 * (1e6*1e6 + 1e6)
  ≈ 1e15, fits in 64-bit / Python int (Python unbounded). Use INF ~ 1e18.

## Interface contract
- Input: stdin per format. Output: single integer (min minutes) to stdout.
- Pure computation, deterministic.

## Sample checks
- Sample 1 → 78. Route: car 1→3 (16) + car 3→2 (24) + train 2→4 (5*5+13=38) = 78.
- Sample 2 → 1 (car 1→3 direct = 1*1=1; train too expensive).
- Sample 3 → 168604826785.
```
