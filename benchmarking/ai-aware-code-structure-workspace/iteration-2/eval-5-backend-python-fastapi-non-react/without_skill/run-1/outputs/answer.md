# Structuring your growing `orders.py`

Short version: split it into a small **package** organised by concern, not one big file. Right now you have four distinct responsibilities (HTTP routing, schemas, persistence, business logic) glued together, and they change for different reasons and at different rates. Separating them gives you smaller, single-purpose files that an agent (or a human) can load, understand, and edit without dragging in everything else.

## Recommended layout

Turn `orders.py` into an `orders/` package:

```
app/
  orders/
    __init__.py
    router.py        # FastAPI route handlers only — thin
    schemas.py       # Pydantic request/response models
    models.py        # SQLAlchemy ORM models (Order, OrderLine, ...)
    repository.py    # DB queries / data access
    service.py       # orchestration: ties repo + discounts together
    discounts.py     # pure discount-calculation business logic
    dependencies.py  # FastAPI dependencies (get_db, current_user, etc.) — only if you have them
```

If you'd rather not make a package yet, the same split works as sibling modules (`orders_router.py`, `orders_schemas.py`, …), but a package keeps the namespace clean and signals "this is one feature." At ~250 lines you're right at the point where the package pays off.

## What goes where, and why

**`router.py` — the HTTP layer.** Route handlers, status codes, dependency injection, turning exceptions into HTTP responses. Each handler should read like a table of contents: validate input (Pydantic does this), call a service function, return a response model. No SQLAlchemy, no discount math here. When a handler is more than ~10 lines, the logic underneath it probably wants to move to `service.py`.

**`schemas.py` — the API contract.** Your Pydantic `OrderCreate`, `OrderRead`, etc. Keeping these separate from the ORM models is the important one — conflating "shape of the HTTP payload" with "shape of the database row" is a common trap that bites you the moment the two need to diverge (computed fields, hiding internal columns, versioning the API). They're genuinely different concerns.

**`models.py` — the ORM.** SQLAlchemy table definitions. Separate file because they're imported by migrations and other features, and you don't want a circular dependency dragging the router in.

**`repository.py` — data access.** The actual queries (`session.execute(select(Order)...)`). Isolating these means the rest of the code talks to orders through named functions like `get_order_by_id(session, id)` rather than inline query expressions. This is the single biggest win for working in the file: queries are the part an agent most often gets subtly wrong, and pinning them behind a small, named surface makes them easy to find, test, and change.

**`discounts.py` — the business logic.** This is your most valuable code and it should be the easiest to reason about. Make it **pure functions**: take primitives/dataclasses in, return a result out, no database session, no request object. That makes it trivially unit-testable (and testable in isolation is exactly where an agent can move fast and verify itself). This is the chunk most likely to keep growing, so give it room.

**`service.py` — orchestration.** The glue: "load the order via the repository, run the discount calc, persist the result." It's where a use-case lives end to end, so it's the natural place to start reading when you want to understand *what an endpoint does*. Keeps the router thin and keeps `discounts.py` pure.

## Why this helps an agent specifically

- **Bounded context per file.** Claude can open `discounts.py` and have everything relevant to a discount change in front of it, without 200 lines of routing and ORM noise competing for attention. Smaller, single-purpose files mean less irrelevant context loaded and fewer chances to edit the wrong thing.
- **Predictable file names.** "Add a route" → `router.py`. "Change the discount rule" → `discounts.py`. "New query" → `repository.py`. The mapping from intent to file is obvious, so the agent navigates by name instead of grepping.
- **Clean seams for tests.** Pure `discounts.py` and a thin `repository.py` are each independently testable, which fits your TDD preference and lets the agent write a focused test next to the change.
- **Stable import graph.** `router → service → repository → models` and `service → discounts` flows one direction. No cycles, so moving or editing one layer doesn't ripple.

## A couple of cautions

- **Don't over-shard.** Six small files for one feature is right; sixteen is not. Keep everything for *orders* inside the `orders/` package. Don't hoist things into some global `services/` or `schemas/` directory yet — co-locating by feature beats organising by layer at the top level until you have several features sharing code.
- **Sequence it.** Pull out `discounts.py` first (it's pure, lowest risk, highest clarity gain), then `schemas.py`, then `repository.py`/`models.py`, and let `router.py`/`service.py` fall out of what's left. Move one concern at a time and keep tests green between steps.
- **Re-export if anything imports `orders` directly.** If other modules do `from app.orders import router`, expose it from `__init__.py` so the refactor doesn't break call sites.

If discounts later grows into several pricing rules, `discounts.py` can itself become a `discounts/` subpackage — but don't pre-build that; let it earn the split.
