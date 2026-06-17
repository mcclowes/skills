# Unify error handling across REST responses and webhooks

Our REST API returns errors one way but our webhooks deliver failures in a totally different shape, and our React frontend has to special-case both. How should we make error handling consistent across responses and webhooks, and how would we consume the unified shape in the frontend?
