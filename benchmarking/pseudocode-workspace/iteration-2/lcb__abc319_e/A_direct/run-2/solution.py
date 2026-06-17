import sys


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    x = int(data[idx]); idx += 1
    y = int(data[idx]); idx += 1

    buses = []
    for _ in range(n - 1):
        p = int(data[idx]); idx += 1
        t = int(data[idx]); idx += 1
        buses.append((p, t))

    L = 840  # lcm(1..8)

    # For each residue r mod L of the time when arriving at bus stop 1,
    # precompute total extra time (relative to r... actually compute final
    # arrival time at bus stop N) given arrival time at stop 1 = r + k*L.
    # Since all P divide L, the offset pattern is periodic with period L.
    # arrive[r] = time of arrival at stop N if arrived at stop 1 at time r.
    arrive = list(range(L))
    for p, t in buses:
        for r in range(L):
            cur = arrive[r]
            # wait for next multiple of p >= cur
            rem = cur % p
            if rem != 0:
                cur += p - rem
            cur += t
            arrive[r] = cur
    # Now arrive[r] - r gives the constant additive delta for arriving at
    # stop 1 at any time congruent to r mod L (since arrive[r] is monotone
    # in the residue class and the bus schedule depends only on time mod p,
    # and p | L). delta[r] = arrive[r] - r works because increasing arrival
    # by multiples of L shifts all departures by the same multiple of L.
    delta = [arrive[r] - r for r in range(L)]

    q = int(data[idx]); idx += 1
    out = []
    for _ in range(q):
        qi = int(data[idx]); idx += 1
        t1 = qi + x  # arrival at bus stop 1
        ans = t1 + delta[t1 % L] + y
        out.append(str(ans))

    sys.stdout.write("\n".join(out) + "\n")


main()
