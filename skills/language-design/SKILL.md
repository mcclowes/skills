---
name: language-design
# prettier-ignore
description: Use when designing or implementing a programming language, compiler, interpreter, tokenizer, or DSL (domain-specific language). Generates lexer and parser implementations, defines AST node structures using discriminated unions, and builds tree-walk interpreter/evaluator patterns with scoped environments. Use when building a grammar, writing a tokenizer, constructing a syntax tree, or wiring together a full source-to-result pipeline for a custom language.
---

# Language Design Patterns

## Quick Start

```
Source Code → Lexer → Tokens → Parser → AST → Interpreter → Result
```

> **Validation checkpoints:** After each stage, verify output before proceeding.
> - Lexer: feed a test string, inspect token stream for correct types/values.
> - Parser: print AST for a simple expression, confirm node shape matches type definitions.
> - Interpreter: evaluate a literal or binary expression before wiring up the full pipeline.

## Lexer Design

### Token Types

```typescript
enum TokenType {
  // Literals
  NUMBER, STRING, IDENTIFIER,

  // Keywords
  LET, IF, ELSE, RETURN,

  // Operators
  PLUS, MINUS, STAR, SLASH,
  PIPE,  // />

  // Delimiters
  LPAREN, RPAREN, LBRACE, RBRACE,

  // Special
  EOF, NEWLINE,
}
```

### Key Lexer Pattern (core loop)

```typescript
// Full implementation → references/lexer.md
class Lexer {
  private source: string;
  private pos = 0;
  private line = 1;
  private column = 1;

  nextToken(): Token {
    this.skipWhitespace();
    if (this.isAtEnd()) return this.makeToken(TokenType.EOF);
    const char = this.advance();
    if (this.isDigit(char)) return this.number();
    if (this.isAlpha(char)) return this.identifier();
    if (char === '"') return this.string();
    switch (char) {
      case '+': return this.makeToken(TokenType.PLUS);
      case '/':
        // Project-specific: /> is the pipe operator
        if (this.match('>')) return this.makeToken(TokenType.PIPE);
        return this.makeToken(TokenType.SLASH);
    }
    throw new LexerError(`Unexpected character: ${char}`, this.line, this.column);
  }
}
```

## Parser Design

### Precedence Table (project-specific ordering)

```
1. Ternary     ? :     (lowest)
2. Equality   == !=
3. Comparison < > <= >=
4. Term       + - ++
5. Factor     * / %
6. Pipe       />      ← custom: pipes value into next function
7. Unary      -
8. Call       fn()
9. Primary    literals  (highest)
```

### Recursive Descent (key precedence levels)

```typescript
// Full parser → references/parser.md
private expression(): Expr { return this.pipe(); }

private pipe(): Expr {
  let left = this.equality();
  while (this.match(TokenType.PIPE)) {
    const right = this.equality();
    left = { type: "PipeExpr", left, right };
  }
  return left;
}

private equality(): Expr {
  let left = this.comparison();
  while (this.match(TokenType.EQEQ, TokenType.NEQ)) {
    const op = this.previous().type;
    const right = this.comparison();
    left = { type: "BinaryExpr", op, left, right };
  }
  return left;
}
// Continue down precedence...
```

## AST Design

### Discriminated Unions

```typescript
type Expr =
  | { type: "NumberLiteral"; value: number; line: number }
  | { type: "StringLiteral"; value: string; line: number }
  | { type: "Identifier"; name: string; line: number }
  | { type: "BinaryExpr"; op: string; left: Expr; right: Expr; line: number }
  | { type: "PipeExpr"; left: Expr; right: Expr; line: number }
  | { type: "CallExpr"; callee: Expr; args: Expr[]; line: number };

type Stmt =
  | { type: "LetStmt"; name: string; value: Expr; line: number }
  | { type: "ExprStmt"; expression: Expr; line: number };
```

## Interpreter Design

### Tree-Walk Evaluator

```typescript
// Environment/scope implementation → references/environment.md
class Interpreter {
  private env = new Environment();

  evaluate(expr: Expr): Value {
    switch (expr.type) {
      case "NumberLiteral":
        return expr.value;
      case "BinaryExpr": {
        const left = this.evaluate(expr.left);
        const right = this.evaluate(expr.right);
        return this.applyOperator(expr.op, left, right);
      }
      case "PipeExpr": {
        // Project-specific: left value is passed as first arg to right fn
        const value = this.evaluate(expr.left);
        const fn = this.evaluate(expr.right);
        return this.call(fn, [value]);
      }
      case "Identifier":
        return this.env.get(expr.name);
    }
  }
}
```

## Reference Files

- [references/lexer.md](references/lexer.md) - Full Lexer class with helper methods
- [references/parser.md](references/parser.md) - Full Parser class with all precedence levels
- [references/environment.md](references/environment.md) - Environment/scope chain implementation
- [references/error-handling.md](references/error-handling.md) - Error recovery patterns
- [references/builtins.md](references/builtins.md) - Builtin function design
