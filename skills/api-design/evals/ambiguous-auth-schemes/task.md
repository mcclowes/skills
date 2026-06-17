# Present ambiguous auth schemes clearly

Our API docs just say 'authenticate with your API key in the Authorization header'. Internally we have a normal access token and a 'stepped-up' token (after the user does an extra verification) that's required for sensitive endpoints like moving money — but it's technically the same token type. Integrators keep getting confused about what to send where. How should we present auth?
