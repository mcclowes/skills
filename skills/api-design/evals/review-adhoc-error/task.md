# Review and improve an ad-hoc error response

Can you review the error response our API currently returns and suggest improvements? Right now for a failed auth it returns:

```json
{ "error": "Unauthorized", "code": 401, "msg": "token bad" }
```

We want something more consistent and developer-friendly across all our endpoints.
