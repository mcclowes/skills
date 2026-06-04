# Laying out `orders.py` for effective AI-assisted work

Short version: split it into a small package by *layer*, not by cleverness. The single most useful thing you can do for an agent (and for yourself) is make each file have one obvious job, with names that say what's inside, so the agent can load only what it needs and edit without dragging unrelated code into context.

## Recommended layout

Turn `orders.py` into an `orders/` package:

```
app/
  orders/
    __init__.py        # re-exports the router; thin
    router.py          # FastAPI route handlers only (the HTTP layer)
    schemas.py         # Pydantic request/response models
    queries.py         # SQLAlchemy reads/writes (the data-access layer)
    discounts.py       # discount-calculation business logic (pure functions)
    service.py         # optional: orchestration that ties queries + discounts together
```

Map your current four chunks straight onto this:

- **Route handlers** → `router.py`. Keep these thin. Each handler parses input, calls into `service`/`queries`/`discounts`, and returns a response model. No SQLAlchemy expressions, no discount maths inline.
- **Pydantic models** → `schemas.py`. Request and response models live together here. This is the file an agent reads first to understand the shape of the API.
- **SQLAlchemy queries** → `queries.py`. Functions like `get_order(session, order_id)`, `list_orders(session, ...)`, `insert_order(session, ...)`. They take a session and primitives/ORM objects, return ORM objects or rows. No HTTP concepts (no `HTTPException`, no status codes) in here.
- **Discount logic** → `discounts.py`. This is your real business logic and the part most worth isolating. Make it **pure**: functions that take plain inputs (line items, a customer tier, coupon codes) and return a computed result, with no database or request objects in scope. Pure functions are the easiest thing in the world for an agent to reason about and to test.

`service.py` is optional. Add it only once a handler needs to do "load order, apply discount, persist, return" as a multi-step flow — that orchestration is awkward in the router and doesn't belong in either `queries` or `discounts`. If your handlers are currently simple, skip it and add it the day you feel the pain.

## Why this shape specifically

**It matches the dependency direction.** `router → service → (queries, discounts)`, and `schemas` is shared vocabulary everyone imports. Dependencies point one way, so an agent asked to "change the discount rule" opens `discounts.py` and touches nothing else. Asked to "add a field to the response," it opens `schemas.py`. The file name *is* the routing table for where work happens.

**It keeps the agent's context small and relevant.** A 250-line everything-file means any edit pulls the whole thing into the working set, including code irrelevant to the task. Smaller, single-purpose files let the agent (and you) load just `discounts.py` to change pricing without the SQLAlchemy and FastAPI noise. That's faster, cheaper, and less error-prone.

**Pure discount logic is independently testable.** Because `discounts.py` has no I/O, the agent can write and run table-driven unit tests against it without a database or a test client. This is where most of your bugs will live, so it's where you want the tightest test loop. (Your stated TDD preference lands cleanest here.)

**Layer boundaries prevent the classic leaks.** The two rules that earn their keep: no SQLAlchemy in `router.py`, and no FastAPI/`HTTPException` in `queries.py` or `discounts.py`. Keep those and the package stays legible as it grows.

## A couple of caveats

- **Don't over-split.** Four-to-five files is right for ~250 lines heading toward a few hundred. Resist one-file-per-class or a `models/` directory with five 15-line files — that just trades a too-big file for too much navigation. Split when a file has genuinely distinct responsibilities (you do) or crosses roughly 300–400 lines, not on principle.
- **`schemas.py` vs `models.py` naming.** If you already have SQLAlchemy ORM classes called "models" elsewhere, keep Pydantic in `schemas.py` to avoid the perennial models-means-two-things confusion. Consistent, unambiguous names help the agent pick the right file every time.
- **Migration is mechanical.** Move code into the new files, fix imports, and have `orders/__init__.py` re-export the router so whatever wires up your app (`include_router`) doesn't change. Do it in one commit so the diff is "moved, not rewritten" and easy to review. Run the tests before and after; behaviour should be identical.

## If you only do one thing

Pull the discount calculation out into a pure `discounts.py` with its own tests. That's the highest-value cut: it's the real logic, it's the most likely to change, and isolating it gives both you and the agent a clean, fast surface to work against. The router/schemas/queries split is the natural next step once that's done.
