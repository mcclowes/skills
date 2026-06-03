# Auth: security schemes are discrete contracts

Guidance for how an API presents authentication to its consumers. Read this when documenting auth, designing how clients authenticate, reviewing an API where "how do I authenticate this call?" is ambiguous, or mapping endpoints to credentials. This is about the *contract* a consumer reasons about, not the cryptography.

## The principle

A security scheme is a discrete contract: a named way of proving who you are, with its own rules, and **each endpoint maps to exactly one of them.** The common failure is treating auth as a single undifferentiated blob — "just send the auth header" — when an API actually has several distinct schemes that a consumer must tell apart to call it correctly.

Two things must be true for auth to be legible:

1. **Each scheme is named and described as its own thing**, even when two schemes happen to share an implementation under the hood.
2. **Every endpoint declares which scheme it requires** — one, specifically, not "auth, somehow."

When either is missing, the consumer reverse-engineers the rules from 401s.

## Don't conflate the credential's mechanics with the scheme

A credential has an *implementation* (how the bytes are transmitted) and a *scheme* (the contract the consumer reasons about). These are different layers, and collapsing them is a real source of confusion.

**Example — Codat.** The relationship between "an API key" and the `Authorization` header was left ambiguous: the header was `Authorization: Basic {base64-encoded api key}`. Mechanically, the API key *is* the thing you base64-encode into a Basic header. But the docs never made the mapping explicit, so consumers couldn't tell whether "API key auth" and "Basic auth" were one scheme or two, or how to turn the key they were given into the header the API wanted. The fix isn't cryptographic — it's a one-line contract: *"Authenticate with your API key as HTTP Basic: `Authorization: Basic base64(apiKey + ':')`."* Name the scheme, state the transform, and the ambiguity evaporates.

The lesson: describe the scheme from the consumer's side (what they have, what they send), and make the relationship between the credential they were issued and the header they transmit explicit. "It's obvious once you know" is not documentation.

## Functionally distinct schemes can share an implementation

The mirror-image trap: two schemes that are technically the *same* mechanism but are *functionally different* to the consumer, and must be treated as distinct.

**Example — Weavr stepped-up tokens.** A token can be "stepped up" (elevated after an additional verification — say SCA). Implementation-wise, the stepped-up token and the ordinary token are technically the same kind of token. But functionally, to the user, they are **different schemes**: some endpoints accept the ordinary token, sensitive ones require a stepped-up token, and an endpoint correlates with one *or* the other — not both. The fact that they're the same bytes under the hood is an implementation detail the consumer should never have to reason about. What the consumer needs is: *this endpoint requires a stepped-up token; that one accepts a standard token.*

The lesson: scheme identity is defined by the contract, not the mechanism. If two credentials grant access to different sets of endpoints, or one is required where the other is rejected, they are different schemes — name and document them as such, regardless of how alike they look in the implementation.

## Model it explicitly

This discipline already has a home in tooling — most people just don't use it. OpenAPI's named `securitySchemes` plus per-operation `security` requirements model exactly this: define each scheme once, then have every endpoint declare which it needs. Use it. The payoff for the consumer is that the contract becomes legible from the spec alone — they can see, per endpoint, precisely which credential to present, instead of discovering it through trial, error, and support tickets.

## The rule

Treat each way of authenticating as a discrete, named scheme with its own contract. Make every endpoint say which one it requires. Keep the consumer-facing scheme separate from its implementation: explain how an issued credential becomes a transmitted header (don't leave it implied), and split credentials that grant different access into different schemes even when they're the same mechanism underneath. Auth is legible when a consumer can answer "what do I send to call *this* endpoint?" from the docs, not from a 401.
