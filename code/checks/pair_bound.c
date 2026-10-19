/* Pair bound for reflexive 4-polytopes, by a direct quadratic search.
 *
 * Input: data/ks4_point_pairs.csv with lines "points,dual_points,count", the
 * joint distribution of |Delta| and |Delta*| over the Kreuzer-Skarke list.
 *
 * L(p,q) is the length of a longest chain (p,q) = (p0,q0), (p1,q1), ..., (pk,qk)
 * of realised pairs with p strictly decreasing and q strictly increasing.  Here
 * it is computed by comparing every pair with every other pair, with no data
 * structure, independently of the Fenwick-tree program pair_chain.py.
 *
 * Checks: the total 473,800,776 and the 71,870 pairs; the symmetry of the
 * distribution under duality; the maxima 654 of the simple bound and 348 of
 * the pair bound, each at a single polytope; L(680,26) = 347; the counts of
 * Table I.  Exit status 0 when every check passes.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct { int p, q; long long c; int L; } Pair;

static int by_p(const void *a, const void *b) {
    const Pair *x = a, *y = b;
    if (x->p != y->p) return x->p - y->p;
    return y->q - x->q;
}

static int fails = 0, passes = 0;
static void check(int ok, const char *what) {
    printf("%s %s\n", ok ? "PASS" : "FAIL", what);
    if (ok) passes++; else fails++;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "data/ks4_point_pairs.csv";
    FILE *f = fopen(path, "r");
    if (!f) { perror(path); return 2; }
    char line[256];
    int n = 0, cap = 1 << 17;
    Pair *P = malloc(sizeof(Pair) * cap);
    if (!fgets(line, sizeof line, f)) return 2;          /* header */
    while (fgets(line, sizeof line, f)) {
        Pair r; r.L = 0;
        if (sscanf(line, "%d,%d,%lld", &r.p, &r.q, &r.c) != 3) continue;
        P[n++] = r;
    }
    fclose(f);

    long long total = 0;
    for (int i = 0; i < n; i++) total += P[i].c;
    check(n == 71870, "71,870 realised pairs (|Delta|, |Delta*|)");
    check(total == 473800776LL, "473,800,776 polytopes in the list");

    /* symmetry under duality: count(p,q) = count(q,p) */
    static long long C[700][700];
    memset(C, 0, sizeof C);
    for (int i = 0; i < n; i++) C[P[i].p][P[i].q] = P[i].c;
    int sym = 1;
    for (int i = 0; i < n; i++) if (C[P[i].q][P[i].p] != P[i].c) sym = 0;
    check(sym, "the distribution is symmetric under duality");

    /* longest chains, quadratic search */
    qsort(P, n, sizeof(Pair), by_p);
    for (int i = 0; i < n; i++) {
        int best = -1;
        for (int j = 0; j < i; j++)
            if (P[j].p < P[i].p && P[j].q > P[i].q && P[j].L > best) best = P[j].L;
        P[i].L = best + 1;
    }

    int maxL = 0, maxS = 0;
    for (int i = 0; i < n; i++) {
        int s = P[i].p - 6 < 680 - P[i].q ? P[i].p - 6 : 680 - P[i].q;
        if (P[i].L > maxL) maxL = P[i].L;
        if (s > maxS) maxS = s;
    }
    long long atL = 0, atS = 0; int Lp = 0, Lq = 0, Sp = 0, Sq = 0, L680 = -1;
    for (int i = 0; i < n; i++) {
        int s = P[i].p - 6 < 680 - P[i].q ? P[i].p - 6 : 680 - P[i].q;
        if (P[i].L == maxL) { atL += P[i].c; Lp = P[i].p; Lq = P[i].q; }
        if (s == maxS) { atS += P[i].c; Sp = P[i].p; Sq = P[i].q; }
        if (P[i].p == 680 && P[i].q == 26) L680 = P[i].L;
    }
    check(maxS == 654 && atS == 1 && Sp == 680 && Sq == 26,
          "simple bound: maximum 654, attained only at (680,26) by one polytope");
    check(maxL == 348 && atL == 1 && Lp == 521 && Lq == 22,
          "pair bound: maximum 348, attained only at (521,22) by one polytope");
    check(L680 == 347, "pair bound of the largest polytope: L(680,26) = 347");

    /* Table I */
    const int X[10] = {100, 150, 200, 250, 300, 320, 340, 348, 500, 654};
    const long long wantS[10] = {7159636, 893324, 136519, 30306, 7755, 4763, 2705, 2197, 39, 0};
    const long long wantL[10] = {6838181, 825559, 117767, 23814, 3556, 1028, 106, 0, 0, 0};
    int tab = 1;
    for (int k = 0; k < 10; k++) {
        long long a = 0, b = 0;
        for (int i = 0; i < n; i++) {
            int s = P[i].p - 6 < 680 - P[i].q ? P[i].p - 6 : 680 - P[i].q;
            if (s > X[k]) a += P[i].c;
            if (P[i].L > X[k]) b += P[i].c;
        }
        printf("  bound exceeds %3d: simple %9lld  pair %9lld\n", X[k], a, b);
        if (a != wantS[k] || b != wantL[k]) tab = 0;
    }
    check(tab, "Table I: counts of polytopes whose bounds exceed 100, ..., 654");

    /* the pair bound never exceeds the simple bound */
    int dom = 1;
    for (int i = 0; i < n; i++) {
        int s = P[i].p - 6 < 680 - P[i].q ? P[i].p - 6 : 680 - P[i].q;
        if (P[i].L > s) dom = 0;
    }
    check(dom, "L(p,q) <= min(p-6, 680-q) for every pair");

    printf("pair_bound.c: %d passed, %d failed\n", passes, fails);
    return fails ? 1 : 0;
}
