# is_sorted — plan

Verdict: invariant + subtle duplicate rule. Plan first (briefly).

## Data & invariants
- Input: list of non-negative integers.
- Output: bool.
- "Sorted ascending" = each element ≤ next (non-strict, since duplicates allowed at all).
- Duplicate rule: "more than 1 duplicate of the same number" → more than 2 occurrences
  of any single value ⇒ False. (Examples: [1,2,2,3,3,4] True (each appears ≤2 times);
  [1,2,2,2,3,4] False (2 appears 3 times)).

## Control flow
- ascending check: for i from 1 to n-1: if lst[i] < lst[i-1] → return False
- duplicate check: count occurrences of each value; if any count > 2 → return False
- else → return True

## Edge cases
- empty list      → no pair fails, no count > 2 → True
- single element  → True
- equal adjacent within limit ([2,2]) → allowed by non-strict compare, count 2 ≤ 2
- triple ([2,2,2]) → count 3 > 2 → False (and order ok, so dup rule is what catches it)

## Interface contract
- Pure; does not mutate input; returns bool.
