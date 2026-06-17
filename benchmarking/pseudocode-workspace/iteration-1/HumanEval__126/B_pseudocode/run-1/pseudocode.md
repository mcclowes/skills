# is_sorted

Verdict: small but has a subtle rule (the "more than 1 duplicate of same number" clause combined with sorted check). Planning the core.

## Data & invariants
- Input: list of non-negative integers, possibly empty.
- Output: bool.
- "Sorted ascending" = each element >= previous (non-strict, since duplicates are allowed up to a point).
- Duplicate rule: if any value appears 3+ times ("more than 1 duplicate" = more than one extra copy = count >= 3), return False. A value appearing exactly twice is fine.

## Control flow
```
ascending? = for i from 1 to n-1: lst[i] >= lst[i-1]   (all true)
counts = frequency of each value
no-triples? = every count <= 2
return ascending? AND no-triples?
```

## Edge cases & failure modes
- empty list      -> ascending vacuously true, no counts -> True
- single element  -> ascending vacuously true -> True
- [1,2,2,3,3,4]   -> sorted, max count 2 -> True
- [1,2,2,2,3,4]   -> value 2 appears 3 times -> False
- [1,3,2,...]     -> not ascending -> False
- non-adjacent dup like [1,2,1] -> not ascending caught first; also count rule independent of adjacency.

## Interface contract
- Pure; input not mutated; returns bool.
