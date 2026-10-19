// The largest reflexive 4-polytope Delta_680 and its dual, checked from the
// vertices alone with exact integer arithmetic.
//
//   Delta_680 = conv{(-1,-1,-1,-1), (83,-1,-1,-1), (-1,6,-1,-1), (-1,-1,2,-1), (-1,-1,-1,1)}
//
// Checks: the facet normals are e1,...,e4 and (-1,-12,-28,-42), each at height
// -1 (so the polytope is reflexive); it has 680 lattice points; they are the
// monomials of degree 84 in P(1,1,12,28,42) shifted by (1,1,1,1); the dual
// has 26 lattice points; the normalised volumes are 3528 = 2*42^2 and 84; the
// weights divided by their sum are 1/2, 1/3, 1/7, 1/84, 1/84.  Also the end
// simplex of the descent of Table III: 9 lattice points, reflexive, dual with
// 201 points.
#include <array>
#include <cstdio>
#include <cstdlib>
#include <numeric>
#include <set>
#include <vector>

using V4 = std::array<long long, 4>;
static int passes = 0, fails = 0;
static void check(bool ok, const char* what) {
    std::printf("%s %s\n", ok ? "PASS" : "FAIL", what);
    (ok ? passes : fails)++;
}

static long long dot(const V4& a, const V4& b) {
    long long s = 0;
    for (int i = 0; i < 4; i++) s += a[i] * b[i];
    return s;
}

static long long det4(std::array<V4, 4> m) {
    // fraction-free Gaussian elimination (Bareiss)
    long long sign = 1, prev = 1;
    for (int k = 0; k < 4; k++) {
        if (m[k][k] == 0) {
            int r = k + 1;
            while (r < 4 && m[r][k] == 0) r++;
            if (r == 4) return 0;
            std::swap(m[k], m[r]);
            sign = -sign;
        }
        for (int i = k + 1; i < 4; i++)
            for (int j = k + 1; j < 4; j++)
                m[i][j] = (m[k][k] * m[i][j] - m[i][k] * m[k][j]) / prev;
        prev = m[k][k];
    }
    return sign * m[3][3];
}

// normalised volume of a 4-simplex = |det(v1-v0, ..., v4-v0)|
static long long nvol(const std::vector<V4>& v) {
    std::array<V4, 4> m;
    for (int i = 0; i < 4; i++)
        for (int j = 0; j < 4; j++) m[i][j] = v[i + 1][j] - v[0][j];
    return std::llabs(det4(m));
}

// facet normals of a 4-simplex: for each vertex, the hyperplane through the other four,
// scaled to a primitive integer normal a with <a,x> >= c on the simplex
struct Facet { V4 a; long long c; };
static std::vector<Facet> simplex_facets(const std::vector<V4>& v) {
    std::vector<Facet> F;
    for (int omit = 0; omit < 5; omit++) {
        std::vector<V4> w;
        for (int i = 0; i < 5; i++) if (i != omit) w.push_back(v[i]);
        // normal by cofactors of the 3x4 matrix of edge vectors
        std::array<V4, 3> e;
        for (int i = 0; i < 3; i++)
            for (int j = 0; j < 4; j++) e[i][j] = w[i + 1][j] - w[0][j];
        V4 a;
        for (int col = 0; col < 4; col++) {
            std::array<V4, 4> m{};
            m[0] = V4{0, 0, 0, 0};
            m[0][col] = 1;
            for (int i = 0; i < 3; i++) m[i + 1] = e[i];
            a[col] = det4(m);
        }
        long long g = 0;
        for (long long t : a) g = std::gcd(g, std::llabs(t));
        for (auto& t : a) t /= g;
        long long c = dot(a, w[0]);
        if (dot(a, v[omit]) < c) { for (auto& t : a) t = -t; c = -c; }
        F.push_back({a, c});
    }
    return F;
}

static std::vector<V4> points_in(const std::vector<Facet>& F, const std::vector<V4>& verts) {
    V4 lo, hi;
    for (int i = 0; i < 4; i++) {
        lo[i] = hi[i] = verts[0][i];
        for (auto& v : verts) { lo[i] = std::min(lo[i], v[i]); hi[i] = std::max(hi[i], v[i]); }
    }
    std::vector<V4> out;
    V4 x;
    for (x[0] = lo[0]; x[0] <= hi[0]; x[0]++)
        for (x[1] = lo[1]; x[1] <= hi[1]; x[1]++)
            for (x[2] = lo[2]; x[2] <= hi[2]; x[2]++)
                for (x[3] = lo[3]; x[3] <= hi[3]; x[3]++) {
                    bool in = true;
                    for (auto& f : F) if (dot(f.a, x) < f.c) { in = false; break; }
                    if (in) out.push_back(x);
                }
    return out;
}

// lattice points y of the dual {y : <v,y> >= -1 for every vertex v}; the dual of a
// reflexive simplex is the simplex spanned by its facet normals
static std::vector<V4> dual_points(const std::vector<Facet>& F, const std::vector<V4>& verts) {
    std::vector<V4> dv;
    for (auto& f : F) dv.push_back(f.a);
    std::vector<Facet> H;
    for (auto& v : verts) H.push_back({v, -1});
    return points_in(H, dv);
}

static bool reflexive(const std::vector<Facet>& F) {
    for (auto& f : F) if (f.c != -1) return false;
    return true;
}

int main() {
    std::vector<V4> D = {V4{-1, -1, -1, -1}, V4{83, -1, -1, -1}, V4{-1, 6, -1, -1},
                         V4{-1, -1, 2, -1}, V4{-1, -1, -1, 1}};
    auto F = simplex_facets(D);
    std::set<V4> normals;
    for (auto& f : F) normals.insert(f.a);
    std::set<V4> want = {V4{1, 0, 0, 0}, V4{0, 1, 0, 0}, V4{0, 0, 1, 0}, V4{0, 0, 0, 1},
                         V4{-1, -12, -28, -42}};
    check(normals == want, "facet normals of Delta_680 are e1, e2, e3, e4 and (-1,-12,-28,-42)");
    check(reflexive(F), "every facet of Delta_680 is at height -1 (reflexive)");

    auto P = points_in(F, D);
    check(P.size() == 680, "Delta_680 has 680 lattice points");

    // monomials of degree 84 in P(1,1,12,28,42): (u0,...,u4) >= 0 with
    // u0 + u1 + 12 u2 + 28 u3 + 42 u4 = 84; the point is (u1,u2,u3,u4) - (1,1,1,1)
    std::set<V4> mono;
    for (long long u4 = 0; 42 * u4 <= 84; u4++)
        for (long long u3 = 0; 28 * u3 + 42 * u4 <= 84; u3++)
            for (long long u2 = 0; 12 * u2 + 28 * u3 + 42 * u4 <= 84; u2++)
                for (long long u1 = 0; u1 + 12 * u2 + 28 * u3 + 42 * u4 <= 84; u1++)
                    mono.insert(V4{u1 - 1, u2 - 1, u3 - 1, u4 - 1});
    std::set<V4> Ps(P.begin(), P.end());
    check(mono.size() == 680 && mono == Ps,
          "the lattice points are the monomials of degree 84 in P(1,1,12,28,42), shifted");

    auto Q = dual_points(F, D);
    check(Q.size() == 26, "the dual of Delta_680 has 26 lattice points");

    long long vol = nvol(D);
    std::vector<V4> Dd;
    for (auto& f : F) Dd.push_back(f.a);
    long long dvol = nvol(Dd);
    check(vol == 3528 && vol == 2 * 42 * 42, "normalised volume of Delta_680 is 3528 = 2*42^2");
    check(dvol == 84 && dvol == 1 + 1 + 12 + 28 + 42, "normalised volume of the dual is 84 = 1+1+12+28+42");

    // weights over their sum: 42/84, 28/84, 12/84, 1/84, 1/84 = 1/2, 1/3, 1/7, 1/84, 1/84
    long long w[5] = {42, 28, 12, 1, 1};
    long long s = 0;
    for (long long t : w) s += t;
    check(s == 84 && 84 % 42 == 0 && 84 / 42 == 2 && 84 / 28 == 3 && 84 / 12 == 7,
          "weights over their sum are 1/2, 1/3, 1/7, 1/84, 1/84");
    // 1/2 + 1/3 + 1/7 + 1/42 = 1, i.e. 21 + 14 + 6 + 1 = 42
    check(21 + 14 + 6 + 1 == 42, "1/2 + 1/3 + 1/7 + 1/42 = 1");

    // the end of the descent, Gamma_38
    std::vector<V4> E = {V4{-1, -1, -1, 1}, V4{-1, -1, 2, -1}, V4{-1, 0, 1, -1},
                         V4{-1, 6, -1, -1}, V4{1, 0, 0, 0}};
    auto FE = simplex_facets(E);
    auto PE = points_in(FE, E);
    auto QE = dual_points(FE, E);
    check(reflexive(FE), "the end simplex Gamma_38 is reflexive");
    check(PE.size() == 9, "Gamma_38 has 9 lattice points");
    check(QE.size() == 201, "the dual of Gamma_38 has 201 lattice points");
    bool inside = true;
    for (auto& x : PE) if (!Ps.count(x)) inside = false;
    check(inside, "Gamma_38 lies inside Delta_680");

    std::printf("delta680.cpp: %d passed, %d failed\n", passes, fails);
    return fails ? 1 : 0;
}
