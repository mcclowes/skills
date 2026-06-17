import sys


def main():
    data = sys.stdin.buffer.read().split()
    # data[0] = N, data[1] = T, data[2..] = S_1..S_N
    n = int(data[0])
    t = data[1]
    L = len(t)

    # threshold count array: cntB[v] = number of j with g(S_j) == v
    cntB = [0] * (L + 2)
    A = [0] * n

    strings = data[2:2 + n]

    for i in range(n):
        s = strings[i]

        # f(s): longest prefix of T that is a subsequence of s
        p = 0
        for ch in s:
            if p < L and ch == t[p]:
                p += 1
        A[i] = p

        # g(s): longest suffix of T that is a subsequence of s
        q = 0
        # scan s from the right, match T from the end
        for idx in range(len(s) - 1, -1, -1):
            if q < L and s[idx] == t[L - 1 - q]:
                q += 1
        cntB[q] += 1

    # suffixB[v] = number of j with g(S_j) >= v
    suffixB = [0] * (L + 2)
    for v in range(L, -1, -1):
        suffixB[v] = suffixB[v + 1] + cntB[v]

    ans = 0
    for i in range(n):
        need = L - A[i]
        if need < 0:
            need = 0
        ans += suffixB[need]

    sys.stdout.write(str(ans) + "\n")


main()
