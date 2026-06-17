# Plan: minimum travel time, car-then-train

Verdict: logic-heavy (graph shortest path with a one-way state switch + dense
Dijkstra over N up to 1000 => N^2 nodes). Plan first.

## Data & invariants
- N cities, D[i][j] symmetric, D[i][i]=0, D[i][j]>0 for i!=j. 0-indexed internally.
- Cost car edge i->j: D[i][j]*A. Cost train edge i->j: D[i][j]*B + C.
- State = (city, mode) where mode in {CAR, TRAIN}.
  - In CAR you may take a car edge (stay CAR) OR switch to TRAIN at the same
    city for free (transition CAR->TRAIN, same city). No reverse switch.
  - In TRAIN you may only take train edges (stay TRAIN).
- dist_car[v]   = min time to reach v while still allowed to use car (started car).
- dist_train[v] = min time to reach v already committed to train.
- Invariant: a Dijkstra-settled node's distance is final (non-negative edge
  weights, since A,B,C,D >= 1 / >= 0 => all edges >= 0).

## Control flow
1. Read N,A,B,C and DxN matrix.
2. dist_car: standard Dijkstra from city 0 using only car edges.
     dist_car[0]=0; relax car edges D[u][v]*A.
3. For each city u, free switch: dist_train_start[u] = dist_car[u]
   (arrive at u by car, then board train at u for 0 extra).
4. dist_train: Dijkstra with multi-source initialization = dist_train_start[]
   (all cities seeded), relaxing only train edges D[u][v]*B + C.
   This lets the optimal answer switch at the best city.
5. Answer for destination N-1 = min(dist_car[N-1], dist_train[N-1]).
   (Pure car all the way, or switch somewhere then train.)

Dijkstra over dense graph: since edges form a complete graph, use O(N^2)
array-based Dijkstra (pick unvisited min each step, relax all). Avoids heap
overhead, fine for N=1000 (1e6 ops x2).

## Edge cases
- N=2: answer = min(D[0][1]*A, D[0][1]*B+C). Both Dijkstras cover it.
- Switching at city 0 immediately => pure train path; covered by seeding all
  cities incl. 0 in train sources.
- Switching at destination N-1 has no benefit (no further travel) but is
  harmless; dist_car[N-1] already considered.
- Large values: D*B+C up to 1e6*1e6+1e6 ~1e12 per edge, path up to ~1e3 edges
  => sums up to ~1e15+. Use 64-bit ints. Python ints are arbitrary precision,
  so no overflow. Initialize unreached with a very large sentinel (or inf).
- Diagonal D[i][i]=0 self-edges: harmless (zero-cost self loop), never improves.

## Interface contract
- Input: stdin as specified. Output: single integer = min minutes.
- All-integer arithmetic; print as integer (no float; values exceed 2^53 so
  avoid float Dijkstra distances — use Python int).
