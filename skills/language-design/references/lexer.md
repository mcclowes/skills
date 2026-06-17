# Lexer — full implementation with helper methods

The core `nextToken` dispatch loop lives in `SKILL.md`. This fleshes out the
helper methods it calls — character classification, the per-token scanners, and
the cursor primitives.

```typescript
class Lexer {
  private source: string;
  private pos = 0;
  private line = 1;
  private column = 1;
  private tokenStart = 0;

  constructor(source: string) {
    this.source = source;
  }

  nextToken(): Token {
    this.skipWhitespace();
    this.tokenStart = this.pos;

    if (this.isAtEnd()) return this.makeToken(TokenType.EOF);

    const char = this.advance();

    if (this.isDigit(char)) return this.number();
    if (this.isAlpha(char)) return this.identifier();
    if (char === '"') return this.string();

    switch (char) {
      case '+': return this.makeToken(TokenType.PLUS);
      case '-': return this.makeToken(TokenType.MINUS);
      case '*': return this.makeToken(TokenType.STAR);
      case '/':
        // Project-specific: /> is the pipe operator
        if (this.match('>')) return this.makeToken(TokenType.PIPE);
        return this.makeToken(TokenType.SLASH);
    }

    throw new LexerError(`Unexpected character: ${char}`, this.line, this.column);
  }

  // --- Token scanners ---

  private number(): Token {
    while (this.isDigit(this.peek())) this.advance();
    if (this.peek() === "." && this.isDigit(this.peekNext())) {
      this.advance(); // consume the '.'
      while (this.isDigit(this.peek())) this.advance();
    }
    return this.makeToken(TokenType.NUMBER);
  }

  private identifier(): Token {
    while (this.isAlphaNumeric(this.peek())) this.advance();
    const text = this.source.slice(this.tokenStart, this.pos);
    return this.makeToken(KEYWORDS[text] ?? TokenType.IDENT);
  }

  private string(): Token {
    while (this.peek() !== '"' && !this.isAtEnd()) {
      if (this.peek() === "\n") this.line++;
      this.advance();
    }
    if (this.isAtEnd()) {
      throw new LexerError("Unterminated string", this.line, this.column);
    }
    this.advance(); // closing quote
    return this.makeToken(TokenType.STRING);
  }

  // --- Character classification ---

  private isDigit(c: string): boolean {
    return c >= "0" && c <= "9";
  }

  private isAlpha(c: string): boolean {
    return (c >= "a" && c <= "z") || (c >= "A" && c <= "Z") || c === "_";
  }

  private isAlphaNumeric(c: string): boolean {
    return this.isAlpha(c) || this.isDigit(c);
  }

  // --- Cursor primitives ---

  private skipWhitespace(): void {
    while (!this.isAtEnd()) {
      const c = this.peek();
      if (c === " " || c === "\t" || c === "\r") {
        this.advance();
      } else if (c === "\n") {
        this.line++;
        this.column = 1;
        this.advance();
      } else {
        break;
      }
    }
  }

  private advance(): string {
    const c = this.source[this.pos++];
    this.column++;
    return c;
  }

  private match(expected: string): boolean {
    if (this.isAtEnd() || this.source[this.pos] !== expected) return false;
    this.pos++;
    this.column++;
    return true;
  }

  private peek(): string {
    return this.isAtEnd() ? "\0" : this.source[this.pos];
  }

  private peekNext(): string {
    return this.pos + 1 >= this.source.length ? "\0" : this.source[this.pos + 1];
  }

  private isAtEnd(): boolean {
    return this.pos >= this.source.length;
  }

  private makeToken(type: TokenType): Token {
    return {
      type,
      value: this.source.slice(this.tokenStart, this.pos),
      line: this.line,
      column: this.column,
    };
  }
}
```
