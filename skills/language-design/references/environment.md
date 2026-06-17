# Environment — scope chain implementation

The interpreter's `evaluate` loop lives in `SKILL.md`. This is the `Environment`
class it depends on: a lexically-scoped chain where each scope holds its own
bindings and falls back to its parent for lookups.

```typescript
class Environment {
  private values = new Map<string, Value>();
  private parent?: Environment;

  constructor(parent?: Environment) {
    this.parent = parent;
  }

  define(name: string, value: Value): void {
    this.values.set(name, value);
  }

  get(name: string): Value {
    if (this.values.has(name)) return this.values.get(name)!;
    if (this.parent) return this.parent.get(name);
    throw new RuntimeError(`Undefined variable: ${name}`);
  }

  // Assign to an existing binding, walking up the chain.
  // Unlike `define`, this fails if the variable was never declared.
  assign(name: string, value: Value): void {
    if (this.values.has(name)) {
      this.values.set(name, value);
      return;
    }
    if (this.parent) return this.parent.assign(name, value);
    throw new RuntimeError(`Undefined variable: ${name}`);
  }
}
```

## Scope chain notes

- A new `Environment(parent)` is created per block / function call; discard it on
  exit so bindings don't leak.
- `define` always writes to the current scope (shadowing is intentional);
  `assign` mutates the nearest enclosing binding.
- Closures capture by holding a reference to the defining environment, so keep
  parent scopes alive as long as a closure referencing them is reachable.
