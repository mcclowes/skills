# Organising the orders module

Short version: don't reflexively shatter a 250-line file into five tidy little ones. Split along boundaries where each resulting file can be understood on its own, and reach for a real abstraction before you reach for a new file. The discount logic is the one piece that clearly earns its own home; the rest depends on how coupled it is.

## The thing to optimise for

When Claude (or any agent) works in this module, it tends to operate on the file that's open and is reluctant to go spelunking through siblings. So the failure mode you're designing against isn't "this file is long" — it's "Claude edits a handler confidently but breaks something because the request model or the query it depends on lives in a file it never opened."

That means the goal isn't maximum separation. It's making each file self-sufficient enough that an edit inside it doesn't silently depend on three other files.

## What I'd actually do

**1. Pull the discount logic out — into a function/module, not just a file.**

This is the highest-value move and it's not really about line count. Discount calculation is pure domain logic: orders/amounts in, a number out, no DB session, no request object. That's the textbook case of "can be understood in isolation." Give it a real interface:

```
orders/
  discounts.py     # calculate_discount(...) -> Decimal, plus rules/constants
```

The win is that the abstraction *reduces* the context needed elsewhere. At the call site in your handler, `calculate_discount(order, customer)` is self-explanatory — Claude doesn't need to read the internals to use it correctly, and it can work on the discount rules in `discounts.py` without dragging in routing or ORM concerns. That's strictly better than leaving 60 lines of branching arithmetic inline in a route handler, where it's noise every time someone works on the endpoint. Co-locate its tests right next to it (`test_discounts.py`) — pure logic is the easiest thing to test in isolation and the most valuable to lock down.

**2. Keep the handlers and their Pydantic models together.**

Resist the urge to make a `schemas.py` purely on principle. The request/response models are tightly coupled to the handlers — you almost always change them in the same edit, and a handler is hard to understand without seeing the shape of what it receives and returns. If the models live in a sibling file, you've created exactly the cross-file lookup the agent skips: it'll edit a handler and guess at the response shape. Co-locating them means Claude sees the whole request → handler → response story in one screen.

The common exception: if a model is genuinely shared across multiple route modules (a `Money` type, a paginated-list wrapper), promote *that one* to a shared `schemas/` location. Shared-ness is a real reason to extract; "models are a different kind of thing" is not.

**3. Decide the queries by how coupled they are — this is the real judgement call.**

Two reasonable layouts depending on your codebase:

- *If the queries are thin* (a couple of `select(Order).where(...)` lines per handler), leave them in the handler. Splitting them into a `repository.py` just doubles the lookups for no isolation benefit — the handler becomes meaningless without the query and vice versa.
- *If the queries are chunky or reused* (multi-join loaders, filtering/pagination, the same fetch used by three handlers), extract a `repository.py` / `queries.py` with named functions like `get_order_with_items(session, order_id)`. Same logic as the discount extraction: a named function with a clear signature is an abstraction the handler can call without reading the SQL. The test is whether someone can understand `repository.py` without the routes open — for data access functions, usually yes.

If you're unsure, leave them inline. It's cheaper to extract later than to glue back two files that only make sense together.

## Where I'd land

For a 250-line module that's still growing, a pragmatic shape:

```
orders/
  __init__.py
  routes.py        # handlers + their Pydantic request/response models
  discounts.py     # pure discount logic + constants (extract now)
  repository.py    # SQLAlchemy queries — only if they're non-trivial or shared
  test_discounts.py
  test_routes.py
```

Notice `routes.py` deliberately stays the biggest file, holding handlers + models + thin queries together. Don't panic about it sitting at 150–200 lines. The old "split anything that doesn't fit on a screen" rule was calibrated for human scrolling; agents handle a few hundred lines of *coherent* code fine. Cohesion beats line count until roughly the ~300-line mark, where signal-to-noise genuinely starts to drop — at that point split by sub-resource or concern, not by reflex.

## The rule of thumb to keep

Before extracting any piece, ask: **can this be understood and edited without opening the file it came from?**

- Discount logic — yes. Extract it.
- Non-trivial/shared queries — usually yes. Extract them.
- Pydantic models — no, they ride with the handlers. Keep them.
- A handler with its query inlined — fine as is until the file gets genuinely large.

Split where each side stands alone; co-locate where they don't. That keeps every file a complete picture for whoever opens it next — including Claude.
