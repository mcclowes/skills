# API design

Opinionated patterns for designing developer-friendly HTTP APIs: error/warning handling, resource state and events, read-endpoint structure and pagination, and authentication.

## Structure

- `SKILL.md` - Main skill instructions: principles, the `issues` pattern, the status/event/issue split, view-vs-data endpoints, auth schemes, and design rules
- `references/error-handling.md` - Full field-by-field reference for the `issues` array
- `references/event-status-design.md` - Modelling and naming a resource's lifecycle: states, events, and the status/event/issue split
- `references/view-vs-data-endpoints.md` - View (screen-shaped/BFF) vs data (canonical resource) endpoints, and pagination (cursor vs offset)
- `references/auth-schemes.md` - Treating security schemes as discrete, named contracts
- `references/consuming-in-react.md` - TypeScript types and React/SDK consumption examples

## Usage

This skill is automatically discovered by Claude when relevant to the task.
