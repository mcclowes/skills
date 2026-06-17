# Model an order's status lifecycle and events

We're modelling the lifecycle of an order in our API. Right now we have a single `status` string that can be `created`, `paid`, `payment_failed`, `shipped`, or `delivered`, and we fire a webhook on every change. But a failed payment can be retried, and the frontend keeps having to special-case `payment_failed` to know what to show the user and whether they can try again. How should we model and name the order's states and the events?
