# Parser — full recursive descent implementation

The core loop and key precedence levels live in `SKILL.md`. This is the complete
recursive-descent parser, showing every precedence level wired top to bottom.

```typescript
class Parser {
  private tokens: Token[];
  private current = 0;

  constructor(tokens: Token[]) {
    this.tokens = tokens;
  }

  parse(): Program {
    const statements: Stmt[] = [];
    while (!this.isAtEnd()) {
      statements.push(this.statement());
    }
    return { type: "Program", body: statements };
  }

  // --- Precedence climbing, lowest to highest ---

  private expression(): Expr {
    return this.pipe();
  }

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

  private comparison(): Expr {
    let left = this.term();
    while (this.match(TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE)) {
      const op = this.previous().type;
      const right = this.term();
      left = { type: "BinaryExpr", op, left, right };
    }
    return left;
  }

  private term(): Expr {
    let left = this.factor();
    while (this.match(TokenType.PLUS, TokenType.MINUS)) {
      const op = this.previous().type;
      const right = this.factor();
      left = { type: "BinaryExpr", op, left, right };
    }
    return left;
  }

  private factor(): Expr {
    let left = this.unary();
    while (this.match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT)) {
      const op = this.previous().type;
      const right = this.unary();
      left = { type: "BinaryExpr", op, left, right };
    }
    return left;
  }

  private unary(): Expr {
    if (this.match(TokenType.MINUS)) {
      const operand = this.unary();
      return { type: "UnaryExpr", op: TokenType.MINUS, operand };
    }
    return this.primary();
  }

  private primary(): Expr {
    if (this.match(TokenType.NUMBER)) {
      return { type: "NumberLiteral", value: Number(this.previous().value) };
    }
    if (this.match(TokenType.IDENT)) {
      return { type: "Identifier", name: this.previous().value };
    }
    if (this.match(TokenType.LPAREN)) {
      const expr = this.expression();
      this.consume(TokenType.RPAREN, "Expected ')' after expression");
      return expr;
    }
    throw new ParseError(`Unexpected token: ${this.peek().type}`, this.peek());
  }

  // --- Token cursor helpers ---

  private match(...types: TokenType[]): boolean {
    if (types.includes(this.peek().type)) {
      this.advance();
      return true;
    }
    return false;
  }

  private consume(type: TokenType, message: string): Token {
    if (this.peek().type === type) return this.advance();
    throw new ParseError(message, this.peek());
  }

  private advance(): Token {
    if (!this.isAtEnd()) this.current++;
    return this.previous();
  }

  private peek(): Token {
    return this.tokens[this.current];
  }

  private previous(): Token {
    return this.tokens[this.current - 1];
  }

  private isAtEnd(): boolean {
    return this.peek().type === TokenType.EOF;
  }
}
```
