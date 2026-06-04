# Laying out a growing FastAPI route module

Short version: at 250 lines and one coherent domain (orders), you don't need to shatter this into the canonical `routers/`, `schemas/`, `crud/`, `services/` four-file pile yet. The instinct to split by *type of code* (models here, queries there, logic elsewhere) is the wrong cut for an AI-assisted codebase. Split by *whether a piece can be understood on its own*, and only when a piece earns it.

## Why not the textbook split

The standard FastAPI tutorial layout separates everything by layer: Pydantic models in `schemas.py`, SQLAlchemy queries in `crud.py`, handlers in `routers/orders.py`, logic in `services.py`. For a four-file orders feature that reads cleanly to a *human* — you glance between siblings without thinking.

An agent doesn't glance. It works with the file in front of it and is genuinely reluctant to go open the other three. So if your route handler lives in one file but its request model is in `schemas.py` and the discount logic is in `services.py`, an agent editing the handler is working from a partial picture: it'll confidently change a field, or mis-shape a call into the discount function, because it never opened the sibling that defines the contract. A handler and the request/response model it uses are changed together constantly and each needs the other to make sense — that's exactly the code you want co-located, not scattered across layers.

## What I'd actually do

**Keep the route handlers and their Pydantic models together.** These are tightly coupled — you almost never touch one without the other, and the model *is* the handler's contract. Co-locating them removes the cross-file lookup an agent is most likely to skip. This is the highest-value decision here.

**Pull the discount-calculation logic into its own module — because it passes the isolation test, not because it's "a separate concern."** The right test isn't "is this business logic vs. routing?" It's: *can this be understood in isolation?* Discount math is a great candidate: it takes plain inputs (line items, totals, a coupon, maybe a customer tier) and returns a number or a priced result. No request context, no DB session, no framework. An agent can open `discounts.py`, see pure functions with clear signatures, and work on them with almost zero external context. It's also where the gnarly, test-worthy logic lives, so giving it a real interface (`calculate_discount(...)`) pays off twice — the call site reads it and knows enough to proceed without reading the internals.

That gives you roughly:

```
orders/
  __init__.py
  routes.py      # handlers + their Pydantic request/response models
  discounts.py   # pure discount logic — no FastAPI, no DB
  queries.py     # only if the SQLAlchemy access earns it (see below)
```

(A flat `orders_routes.py` + `orders_discounts.py` is equally fine if you're not package-minded yet. Don't over-build the folder.)

## The SQLAlchemy queries — judgement call

This is the one I'd *not* split reflexively. Ask whether your queries stand alone. Two cases:

- **Thin, inline-ish queries** (a `select`, a `get`, a simple filter) woven into the handlers: leave them in `routes.py`. Extracting them into `queries.py` produces a file of one-liners that only make sense once you've read the handler that calls them — you've created a cross-file lookup the agent won't perform, for no isolation benefit.
- **Chunky, reusable query logic** (multi-join reporting, query objects reused across handlers, anything you'd unit-test on its own): that *does* pass the isolation test — give it `queries.py` with named functions like `get_orders_for_customer(session, customer_id)`. The handler then reads the call site and knows enough to proceed.

Start with them inline. Promote to `queries.py` only when a query gets reused or grows its own complexity.

## On the 250-line worry

250 lines covering one cohesive feature is *not* too big — that worry is the human-era "if it doesn't fit on a screen, split it" reflex, which was calibrated for scrolling, not for agents. Agents handle a few hundred lines of coherent code fine; cohesion beats line count. The thing that degrades agent quality isn't raw length, it's low signal-to-noise — several unrelated concerns crammed together. So split when the *concerns* diverge (which the discount extraction handles), not when the line count crosses an arbitrary bar. The real ceiling is around ~300 lines; past that, signal-to-noise genuinely drops and you split for that reason.

## The reach-for-an-abstraction move

Before splitting anything else later, prefer extracting a well-named function or class over relocating code into a new file. A split only moves code; an abstraction like `calculate_discount()` or `OrderRepository.get_for_customer()` actually *reduces* the context needed to work at the call site, because it hides its implementation behind an interface. The discount extraction above is exactly this — a real abstraction, not just a file move — which is why it's worth doing now while the query split mostly isn't.

## Summary

| Piece | Recommendation | Why |
|---|---|---|
| Route handlers + Pydantic models | **Co-locate** in `routes.py` | Always changed together; the model is the handler's contract |
| Discount logic | **Extract** to `discounts.py` | Pure, stands alone, testable — real abstraction |
| Simple SQLAlchemy queries | **Keep inline** for now | Splitting makes one-liners that only make sense with the caller |
| Reusable/complex queries | **Extract** to `queries.py` | Passes the isolation test; reused across handlers |
| The 250-line count itself | **Not a reason to split** | Cohesion beats line count until ~300 |

Net: you go from one 250-line file to two or three files where each one can be read and edited without opening the others. That self-containment — not layer purity — is what makes the module pleasant for Claude to work in.
