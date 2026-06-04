# Laying out a growing `orders.py` for effective AI-assisted work

Short version: split it into a small package by *responsibility*, not by arbitrary line count. The four things you listed (route handlers, Pydantic schemas, SQLAlchemy queries, discount logic) are already four distinct concerns. Give each one a file. That's the layout that makes Claude — and you — most effective, because each file has a single, predictable job and changes stay local.

## Recommended layout

Turn the single module into a package:

```
app/
  orders/
    __init__.py        # re-exports the router; thin public surface
    router.py          # FastAPI route handlers only (HTTP concerns)
    schemas.py         # Pydantic request/response models
    repository.py      # SQLAlchemy queries (data access)
    discounts.py       # discount-calculation business logic (pure)
    service.py         # orchestration: ties repository + discounts together
```

If you'd rather not introduce a package yet, the same split works as sibling modules: `orders_router.py`, `orders_schemas.py`, `orders_repository.py`, `orders_discounts.py`, `orders_service.py`. The package is cleaner once you have more than ~3 files, and it scales when `users`, `products`, etc. get the same treatment.

### What goes where

- **`schemas.py`** — Pydantic models for requests and responses. These are the contract. Pulling them out first is the highest-leverage move: they're referenced everywhere, they're easy to read in isolation, and an agent editing an endpoint can load just this file to see the shapes.
- **`repository.py`** — every SQLAlchemy query, exposed as plain functions like `get_order(session, order_id)`, `list_orders_for_customer(...)`, `insert_order(...)`. No HTTP, no Pydantic. This is the layer you'll most want to mock in tests and the one most likely to grow.
- **`discounts.py`** — the discount math as **pure functions** that take plain inputs (amounts, customer tier, line items) and return results. No database, no request objects. Pure logic is the easiest thing in the world for both a human and an LLM to reason about and test, and it's where bugs with real money consequences live, so isolating it pays off twice.
- **`service.py`** — the orchestration layer. A handler calls `service.create_order(...)`, which validates, calls `discounts` to compute totals, calls `repository` to persist, and returns a domain result. This is optional at 250 lines but I'd add it now: it's the seam that keeps `router.py` thin and keeps business rules out of HTTP code.
- **`router.py`** — just the FastAPI handlers: parse the request (Pydantic), call the service, shape the response, handle HTTP status codes and errors. Each handler should read like a table of contents.
- **`__init__.py`** — re-export the router (`from .router import router`) so the rest of the app imports `from app.orders import router` and doesn't care about the internal split.

## Why this shape specifically helps an AI agent

1. **Predictable file names mean targeted reads.** When Claude needs to change discount rules, it opens `discounts.py` and nothing else. It doesn't have to load 250 lines of mixed concerns to find the 30 that matter, and it won't accidentally edit a query while touching pricing. Smaller, single-purpose files mean less context burned and fewer unintended changes.
2. **Clear boundaries constrain the blast radius.** A change to a SQL query can't silently alter your response schema if they live in different files with an explicit interface between them. The agent gets the same guardrails you do.
3. **Pure logic is testable in isolation.** `discounts.py` with no I/O can be exercised by fast unit tests an agent can write and run without spinning up a database or the app. That tight loop is exactly where TDD shines.
4. **The layering is conventional.** router → service → repository, plus schemas and pure-logic modules, is a pattern that appears constantly in well-structured FastAPI codebases. An agent recognises it and slots new code into the right place by default.

## Don't over-split

Resist the urge to explode this into fifteen files. Four to six modules for a feature this size is right. Splitting `discounts.py` into one-function-per-file, or separating "create" and "list" handlers into different router files, adds navigation cost without buying clarity. The heuristic: split when a file holds **two genuinely different responsibilities** or when it gets large enough that you scroll to find things (very roughly past a few hundred lines). 250 lines split four ways lands each file comfortably under that.

## Suggested order of execution (low-risk, incremental)

1. Extract `schemas.py` — pure move, no logic change, immediately makes the rest readable.
2. Extract `repository.py` — move the queries behind plain functions.
3. Extract `discounts.py` — move the calculation to pure functions; **write tests as you go**, since you now can.
4. Introduce `service.py` and thin out `router.py` to just call it.
5. Add `__init__.py` re-export and fix imports.

Do each step as its own commit so the diff stays reviewable and you can bisect if something breaks. After step 3 you'll already feel most of the benefit; 4 and 5 are polish that pays off as the feature keeps growing.

One thing worth confirming before you start: if your discount logic currently reaches into the database (e.g. loading promo rules mid-calculation), decide whether those lookups belong in `repository.py` with the results *passed into* the pure discount functions. Keeping `discounts.py` free of I/O is what makes it cheap to test, so it's worth the small bit of plumbing.
