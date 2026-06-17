# Design a payouts endpoint error response

I'm building a POST /api/v1/payouts endpoint in our Next.js app. It can fail in a few ways: the user's connected bank token has expired, the requested amount exceeds their daily payout limit, and sometimes our payment provider (a vendor called Sequra) rejects it with its own error code. Design the JSON error response body the API should return for these cases.
