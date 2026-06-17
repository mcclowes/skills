# Model a 3DS challenge pause in payment state

We have a payments API and we're adding 3D Secure. When a charge needs the cardholder to complete a 3DS challenge, the payment pauses until they do it. I was going to add a `requires_action` status (copying Stripe) and have the frontend check for it to know when to pop the challenge. The status field is currently an enum: `pending`, `succeeded`, `failed`. How should I model the 3DS-pause state and tell the frontend to show the challenge?
