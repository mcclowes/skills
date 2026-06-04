# View endpoints vs data endpoints

Guidance for the most consequential structural choice in an API: whether an endpoint exists to **render a view** or to **expose a resource**. These are different jobs, and the same underlying data deserves a different contract depending on which job it's doing. Read this when designing read endpoints, deciding what to include in a payload, choosing a pagination style, or untangling an API where the frontend is doing too much stitching — or where "the data API" has quietly filled up with UI-specific fields.

## Contents

- [Two jobs, not one](#two-jobs-not-one)
- [The squeeze: what happens when you only build one](#the-squeeze-what-happens-when-you-only-build-one)
- [What actually changes between them](#what-actually-changes-between-them)
- [Pagination is the clearest example](#pagination-is-the-clearest-example)
- [Ownership and change cadence](#ownership-and-change-cadence)
- [How they coexist](#how-they-coexist)
- [Where you've seen this before](#where-youve-seen-this-before)
- [The rule](#the-rule)

## Two jobs, not one

A **view endpoint** exists to drive a specific screen or component. Its job is to hand the frontend exactly what that view needs to render, in roughly the shape it needs it. A **data endpoint** (resource endpoint) exists to expose a canonical entity in the domain. Its job is to represent that entity faithfully, regardless of who's asking or why.

These pull in opposite directions, and that's the whole point:

| | **View / presentation endpoint** | **Data / resource endpoint** |
|---|---|---|
| Job to be done | Render a screen or component | Expose a canonical entity |
| Coupled to | The UI — changes when the screen changes | The domain model — stable, slow-moving |
| Shape | Aggregated, denormalised — several entities packaged for one view | Normalised, single-entity |
| Richness | Derived, computed, and formatted display fields; labels; summaries | Raw canonical values |
| Pagination | For humans: page numbers, totals, jump-to-page | For throughput: cursors, streaming |
| Typical owner | The frontend team — they know what the screen needs | The platform/domain team |
| Change cadence | Fast — tracks product/design | Slow — tracks the domain |

Trying to make one endpoint serve both jobs is the source of a surprising amount of API pain. The two jobs want different shapes, different richness, different pagination, and different rates of change. A contract optimised for one is actively wrong for the other.

## The squeeze: what happens when you only build one

Pick one kind of endpoint and the other job doesn't disappear — it leaks somewhere worse.

**Only data endpoints → the frontend stitches.** The client fetches `/customers/123`, then `/customers/123/invoices`, then each invoice's line items, then formats currency and dates, computes a total, and assembles the card the designer drew. This is chatty (N+1 round trips), slow on real networks, and pushes domain logic — what "overdue" means, how a total is computed — into the client, where it duplicates across web, iOS, and Android and drifts out of sync.

**Only "data" endpoints that try to help → coupling by accretion.** To spare the frontend, someone adds `displayName`, `formattedTotal`, `statusLabel`, `isOverdue` to the canonical `/invoices/{id}` resource. It works. Then the screen changes, the fields are wrong, and now you can't change a screen without a release of the platform API — and every other consumer of that "canonical" entity is carrying fields that only ever made sense for one view. The resource is secretly a view wearing a resource's name.

Naming the two jobs up front is what lets each stay honest: the view endpoint is *allowed* to be UI-shaped and change fast, precisely because the resource endpoint next to it stays canonical and stable.

## What actually changes between them

- **Aggregation.** A view endpoint freely combines disparate entities — customer + recent invoices + outstanding balance + next action — into one neatly packaged payload, because that's one screen. A data endpoint returns one entity and links/IDs to the rest, leaving composition to the caller.
- **Derived and formatted fields.** View payloads carry computed and presentation-ready values: a `statusLabel` of "Overdue by 3 days", money pre-formatted or accompanied by display hints, sorted/grouped collections. Data payloads carry raw canonical values (`status`, minor-unit amounts, ISO timestamps) and let the consumer derive the rest.
- **Selectivity.** A view returns the fields the screen shows and omits the rest. A resource returns the entity's representation; trimming it per-caller is the consumer's concern (sparse fieldsets, expansion), not a bespoke shape.
- **Read vs write.** View endpoints are overwhelmingly *reads*. Mutations should still go to resource endpoints with clear semantics — don't invent a write path bolted onto a screen-shaped read. (When a view needs to trigger an action, it calls the same resource mutation everything else does.)

## Pagination is the clearest example

Pagination isn't a separate topic — it's where the view/data split becomes concrete, and where database efficiency forces the choice into the open.

- **Cursor-based pagination is usually the more efficient choice.** It pages by a stable key (`WHERE id > :cursor LIMIT n`) instead of `OFFSET`, so cost doesn't grow as you page deeper, and it's stable under inserts. For data endpoints, bulk export, and infinite-scroll feeds, it's the right default and perfectly usable.
- **But cursors don't suit every UI.** A screen that shows "page 3 of 47", lets the user jump to page 40, or displays a total count needs **offset/page-number pagination** — and that means accepting the database cost (counting the full set, scanning to a deep offset) *because it's a presentation requirement*, not an oversight.

So the pagination style falls out of the job: cursor when throughput and efficiency dominate (data), offset/page-number when human navigation dominates (view). The honest version of "how should I paginate?" is "what is this endpoint *for*?" If you're paying for offset semantics on an endpoint nobody navigates by page, you're paying the database tax for nothing; if you're forcing cursors onto a screen that needs page numbers, you've made the UI impossible to spare a query.

## Ownership and change cadence

The split is also an org boundary. View contracts are best owned by the people who own the screens — they change with the product, and coupling them to the frontend's release cycle is a feature, not a leak. Resource contracts are owned by the domain/platform team and should change slowly and additively, because everything depends on them. Keeping the two apart means a fast-moving product team can reshape a view endpoint freely without filing a change against the slow, widely-depended-on canonical API.

## How they coexist

This isn't "build two parallel APIs and duplicate everything." A view endpoint is usually a thin composition layer *over* the resource endpoints or domain services — it reads canonical data and reshapes it for one screen. The resource layer stays the single source of truth; the view layer is a presentation concern stacked on top, free to be denormalised because it owns nothing canonical. Writes collapse back to the resource layer, so there's one place state actually changes.

## Where you've seen this before

The distinction has well-trodden names worth knowing, so you can borrow the reasoning without reinventing it:

- **Backend-for-frontend (BFF)** — a presentation API per client (web, mobile), shaped for that client's screens. This is the view layer, made explicit and owned by the frontend.
- **GraphQL** — its whole appeal is letting the client shape its own view from a canonical graph, collapsing the view/data tension into one endpoint by pushing shaping to query time. (Same trade-off, different mechanism: you've moved the coupling into the query.)
- **CQRS / read models** — separating the write model (canonical, normalised) from read models (denormalised, view-shaped) is this same split at the persistence layer.

You don't need any of these technologies to apply the idea. You need to decide, per endpoint, which job it's doing — and refuse to let one endpoint do both.

## The rule

Decide what each read endpoint is *for* before you decide its shape. If it renders a screen, let it be screen-shaped: aggregate, derive, format, paginate for humans, and let the frontend team own it as it changes. If it represents an entity, keep it canonical: normalised, raw, stable, paginated for throughput, owned by the domain. The mistake is never "I built a view endpoint" or "I built a data endpoint" — it's building one and quietly asking it to be both.
