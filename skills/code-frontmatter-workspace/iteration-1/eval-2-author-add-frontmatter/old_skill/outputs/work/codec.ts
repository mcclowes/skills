/**
 * ---
 * purpose: Base62 encode/decode for turning numeric link IDs into URL slugs
 * inputs:
 *   - n: number - non-negative integer to encode
 *   - slug: string - base62 string to decode
 * outputs:
 *   - string - base62 slug (encode)
 *   - number - decoded integer (decode)
 * related:
 *   - ./shortener.ts - encodes store IDs into slugs
 * ---
 */
const ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
const BASE = ALPHABET.length;

/** Encode a non-negative integer as a base62 string. */
export function encode(n: number): string {
  if (n < 0 || !Number.isInteger(n)) {
    throw new RangeError("encode expects a non-negative integer");
  }
  if (n === 0) return ALPHABET[0];
  let out = "";
  while (n > 0) {
    out = ALPHABET[n % BASE] + out;
    n = Math.floor(n / BASE);
  }
  return out;
}

/** Decode a base62 string back to an integer. */
export function decode(slug: string): number {
  let n = 0;
  for (const ch of slug) {
    const v = ALPHABET.indexOf(ch);
    if (v === -1) throw new RangeError(`invalid base62 character: ${ch}`);
    n = n * BASE + v;
  }
  return n;
}
