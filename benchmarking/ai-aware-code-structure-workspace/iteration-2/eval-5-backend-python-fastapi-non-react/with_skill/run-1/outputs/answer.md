# Laying out a growing FastAPI route module for AI-assisted work

Short version: at 250 lines you don't have a problem yet, and the reflex to shatter it into the canonical `routes/ models/ schemas/ crud/ services/` tree is the wrong move for a single feature. Split along **one** boundary that genuinely stands on its own — the discount logic — and leave the rest co-located. Here's the reasoning.

## Don't apply the "one file per concern" reflex here

The instinct is to mirror the four things you listed into four files:

```
orders/
  router.py     # handlers
  schemas.py    # Pydantic models
  crud.py       # SQLAlchemy queries
  service.py    # discount logic
```

This *looks* tidy, but think about how Claude actually works in it. When an agent is editing a handler in `router.py`, it needs the request/response shape and the query signature to make a correct change. AI tools are stubbornly reluctant to go open sibling files — they work confidently from what's in front of them. So a handler that calls `get_orders_for_user(...)` and returns an `OrderResponse` defined two files over is exactly the setup that produces a plausible-looking edit that's wrong because the agent never checked the actual field names or the query's return type.

For a feature this size, the handlers, their Pydantic schemas, and the queries they call are **tightly coupled** — you change them together, and each needs the others for context. The test isn't "is this a separate concern?" (they obviously are). It's: **can this concern be understood in isolation?** A handler can't be understood without its schema and its query. So co-locating those three beats splitting them.

## The discount logic is the real split

The one piece that passes the isolation test is the discount calculation. Good business logic is the classic case of something that stands alone: inputs in, a number out, no request objects, no DB session, no framework. An agent can open `discounts.py`, see a function like `calculate_discount(order, customer) -> Decimal`, and work on it correctly with zero external context. That's a *real abstraction* — a named interface that hides its internals — not just relocated code. The handler reads `discount = calculate_discount(order, customer)` at the call site and knows everything it needs.

That move also helps in the other direction: the discount rules are probably where the actual complexity and churn live, and where you'll want unit tests that never touch HTTP or a database. Pulling them out makes that trivial.

## Recommended layout

```
orders/
  __init__.py
  routes.py       # handlers + the Pydantic models + the SQLAlchemy queries
  discounts.py    # pure discount-calculation logic, framework-free
  test_discounts.py
```

Or, if you'd rather not make a package yet, just two flat modules: `orders.py` (now ~200 lines, handlers + schemas + queries) and `discounts.py` (the extracted logic). Both are fine.

Concretely, in `discounts.py`:

```python
# discounts.py — no FastAPI, no SQLAlchemy session, no request objects
from decimal import Decimal

def calculate_discount(subtotal: Decimal, customer_tier: str, coupon: Coupon | None) -> Decimal:
    ...
```

Keep its inputs as plain values / domain objects, not `Request` or a DB session. The moment this file imports FastAPI or needs a live session, it has stopped being independently understandable and the boundary has leaked.

## On the schemas and queries specifically

You might be tempted to peel the Pydantic models into `schemas.py` anyway because "models go in schemas." Resist it at this size. Those models are read and edited almost exclusively alongside the handlers that produce and consume them; separating them just creates the cross-file lookup the agent skips. Same for the SQLAlchemy queries here — if they're a handful of query functions used only by these routes, they belong next to the routes. (Note: your shared **ORM table definitions** — the `Order` mapped class etc. — usually already live in a central `models/` module shared across features. That's fine and unrelated; I'm talking about the per-route query *functions* and the request/response *schemas*.)

## When to split further

Raise your size threshold past the old "fits on a screen" rule — that was calibrated for human scrolling. Agents handle a few hundred lines well. Let `routes.py` grow as long as it stays one coherent concern. Revisit when:

- it crosses **~300–400 lines** and signal-to-noise starts dropping, or
- a second clearly-isolable concern emerges (e.g. a tax or shipping calculator, an external payment integration, a notification side-effect) — extract each the same way you extracted discounts: as a framework-free module with a clean interface.

At that point, splitting schemas into their own file can also start to pay off, because there'll be enough of them that they're a concern in their own right. But split because signal-to-noise demands it, not by reflex.

## Summary

- **Extract `discounts.py` now** — it's pure, isolatable, testable, and the highest-value move.
- **Keep handlers + schemas + queries together** in one module — they're coupled and each needs the others, so splitting them just multiplies the lookups Claude won't do.
- **Let that module grow** to a few hundred lines while it stays coherent; split again only when a new standalone concern appears or signal-to-noise drops.
- **Prefer a clean function interface over a new file** whenever you're tempted to split for tidiness alone.
