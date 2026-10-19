# The reflexive polygons and their reflexive descents, computed from scratch.
#
# A lattice polygon with the origin as its only interior lattice point has its
# other lattice points q_1, ..., q_n on the boundary, in counterclockwise order,
# with det(q_i, q_{i+1}) = 1.  Then q_{i+1} = t_i q_i - q_{i-1} with t_i <= 2
# (convexity), and the sequence closes after one turn.  Enumerating these
# sequences gives every such polygon.  Polygons are identified up to GL(2,Z)
# by a normal form; covers are the maximal reflexive proper subpolygons,
# found by trying every subset of the boundary points.
#
# Checks against Table II of the paper: sixteen polygons, and for each the
# number of lattice points, the number of covers up to equivalence, the
# transition depth and the length of a longest descent; D_2 = 5, attained only
# by the ten-point triangle; every cover drops exactly one lattice point; every
# polygon with at least six points contains an r-minimal polygon with five.

const Pt = Tuple{Int,Int}
det2(a::Pt, b::Pt) = a[1]*b[2] - a[2]*b[1]

passes = 0; fails = 0
function check(ok::Bool, what::String)
    global passes, fails
    println(ok ? "PASS " : "FAIL ", what)
    ok ? (passes += 1) : (fails += 1)
end

# --- convex hull and lattice points ---------------------------------------
cross(o::Pt, a::Pt, b::Pt) = (a[1]-o[1])*(b[2]-o[2]) - (a[2]-o[2])*(b[1]-o[1])
function hull(P::Vector{Pt})
    S = sort(unique(P))
    length(S) <= 2 && return S
    lower = Pt[]; upper = Pt[]
    for p in S
        while length(lower) >= 2 && cross(lower[end-1], lower[end], p) <= 0; pop!(lower); end
        push!(lower, p)
    end
    for p in reverse(S)
        while length(upper) >= 2 && cross(upper[end-1], upper[end], p) <= 0; pop!(upper); end
        push!(upper, p)
    end
    return vcat(lower[1:end-1], upper[1:end-1])      # counterclockwise vertices
end

# lattice points of conv(P) and the number of them in the interior
function latpoints(P::Vector{Pt})
    H = hull(P)
    n = length(H)
    n < 3 && return (Pt[], 0)
    xs = [p[1] for p in H]; ys = [p[2] for p in H]
    pts = Pt[]; inner = 0
    for x in minimum(xs):maximum(xs), y in minimum(ys):maximum(ys)
        s = [cross(H[i], H[mod1(i+1, n)], (x, y)) for i in 1:n]
        if all(>=(0), s)
            push!(pts, (x, y))
            all(>(0), s) && (inner += 1)
        end
    end
    return (sort(pts), inner)
end

# a polygon (as its set of lattice points) is reflexive when the origin is its
# only interior lattice point and every edge is at lattice distance one
function reflexive(pts::Vector{Pt})
    H = hull(pts)
    length(H) < 3 && return false
    n = length(H)
    for i in 1:n
        a, b = H[i], H[mod1(i+1, n)]
        g = gcd(b[1]-a[1], b[2]-a[2])
        det2(a, b) == g || return false            # edge at height 1 from the origin
    end
    lp, inner = latpoints(pts)
    return inner == 1 && (0, 0) in lp && lp == sort(pts)
end

# --- normal form under GL(2,Z) ---------------------------------------------
# two consecutive boundary points p, q have det(p,q) = 1, so an element of
# GL(2,Z) is fixed by the images of p and q; we take every image in a box and
# the least sorted vertex list.  The set of images inside the box is the same
# for every member of a class, so the result is a normal form.
const B = 4
function normalform(pts::Vector{Pt})
    H = hull(pts)
    bd = sort([x for x in pts if x != (0, 0)], by = x -> atan(x[2], x[1]))
    p, q = bd[1], bd[2]
    @assert det2(p, q) == 1
    best = nothing
    for a1 in -B:B, a2 in -B:B, b1 in -B:B, b2 in -B:B
        d = a1*b2 - a2*b1
        abs(d) == 1 || continue
        # g with g p = a, g q = b:  g = [a b] [p q]^{-1}, [p q]^{-1} = [q2 -q1; -p2 p1]
        g11 = a1*q[2] - b1*p[2]; g12 = -a1*q[1] + b1*p[1]
        g21 = a2*q[2] - b2*p[2]; g22 = -a2*q[1] + b2*p[1]
        img = sort([(g11*v[1] + g12*v[2], g21*v[1] + g22*v[2]) for v in H])
        all(v -> abs(v[1]) <= B && abs(v[2]) <= B, img) || continue
        if best === nothing || img < best; best = img; end
    end
    return best
end

# --- enumeration of the boundary sequences ----------------------------------
function enumerate_polygons()
    found = Dict{Vector{Pt},Vector{Pt}}()
    q1 = (1, 0); q2 = (0, 1)                    # any unimodular pair maps to this one
    function dfs(seq::Vector{Pt})
        length(seq) > 12 && return
        prev, cur = seq[end-1], seq[end]
        for t in -12:2
            nxt = (t*cur[1] - prev[1], t*cur[2] - prev[2])
            if nxt == q1
                # closing: convexity at q1 and q2 as well
                t1 = (q2[1] + cur[1]) ÷ q1[1]   # q2 = t1 q1 - cur  (q1 = (1,0))
                (q2[2] + cur[2]) == 0 || continue  # second coordinate of t1 q1 - cur must match
                t1 <= 2 || continue
                # the turn number: angles must add up to one full turn
                wind = 0.0
                s = vcat(seq, [q1])
                for i in 1:length(s)-1
                    wind += atan(det2(s[i], s[i+1]), s[i][1]*s[i+1][1] + s[i][2]*s[i+1][2])
                end
                abs(wind - 2pi) < 1e-9 || continue
                pts = vcat([(0, 0)], seq)
                reflexive(pts) || continue
                nf = normalform(pts)
                found[nf] = sort(pts)
            else
                # keep turning counterclockwise, less than one full turn
                det2(cur, nxt) == 1 || continue
                ang = 0.0
                s = vcat(seq, [nxt])
                for i in 1:length(s)-1
                    ang += atan(det2(s[i], s[i+1]), s[i][1]*s[i+1][1] + s[i][2]*s[i+1][2])
                end
                ang < 2pi - 1e-9 || continue
                dfs(vcat(seq, [nxt]))
            end
        end
    end
    dfs([q1, q2])
    return found
end

classes = enumerate_polygons()
check(length(classes) == 16, "there are sixteen reflexive polygons up to GL(2,Z)")

# --- covers, depth and height ------------------------------------------------
function reflexive_subpolygons(pts::Vector{Pt})
    bd = [x for x in pts if x != (0, 0)]
    out = Vector{Vector{Pt}}()
    for mask in 1:(2^length(bd) - 2)
        S = vcat([(0, 0)], [bd[i] for i in 1:length(bd) if (mask >> (i-1)) & 1 == 1])
        length(S) >= 4 || continue
        lp, _ = latpoints(S)
        lp == sort(S) || continue
        reflexive(lp) && push!(out, lp)
    end
    return out
end

function covers(pts::Vector{Pt})
    subs = reflexive_subpolygons(pts)
    return [G for G in subs if !any(H -> length(H) > length(G) && issubset(G, H), subs)]
end

depthmemo = Dict{Vector{Pt},Tuple{Int,Int}}()
function depth_height(pts::Vector{Pt})
    nf = normalform(pts)
    haskey(depthmemo, nf) && return depthmemo[nf]
    cv = covers(pts)
    r = isempty(cv) ? (0, 0) :
        (1 + minimum(depth_height(G)[1] for G in cv), 1 + maximum(depth_height(G)[2] for G in cv))
    depthmemo[nf] = r
    return r
end

table = Dict{Vector{Pt},NTuple{4,Int}}()
onepoint = true
for (nf, pts) in classes
    cv = covers(pts)
    global onepoint
    all(G -> length(G) == length(pts) - 1, cv) || (onepoint = false)
    c = length(unique(normalform(G) for G in cv))
    d, h = depth_height(pts)
    table[nf] = (length(pts), c, d, h)
end
check(onepoint, "every cover of a reflexive polygon drops exactly one lattice point")

# Table II of the paper: vertices, |Delta|, c, delta, h
paper = [
    ([(-2,-3), (1,0), (1,3)], 10, 1, 5, 6),
    ([(-2,1), (0,1), (1,-2), (1,0)], 9, 2, 4, 5),
    ([(-1,-2), (-1,0), (1,0), (1,2)], 9, 1, 4, 5),
    ([(-3,-2), (1,0), (1,2)], 9, 1, 4, 5),
    ([(-1,-2), (-1,1), (0,1), (1,0)], 8, 3, 3, 4),
    ([(-1,-1), (-1,1), (0,1), (1,-1), (1,0)], 8, 3, 3, 4),
    ([(-3,-2), (0,1), (1,0)], 7, 1, 2, 3),
    ([(-1,-1), (-1,1), (0,-1), (0,1), (1,0)], 7, 2, 2, 3),
    ([(-2,1), (0,-1), (0,1), (1,0)], 7, 2, 2, 3),
    ([(-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0)], 7, 1, 2, 3),
    ([(-1,-1), (-1,1), (0,1), (1,0)], 6, 2, 1, 2),
    ([(-1,0), (0,-1), (0,1), (1,0), (1,1)], 6, 2, 1, 2),
    ([(-1,0), (0,1), (1,-1), (1,0)], 5, 1, 1, 1),
    ([(-2,-1), (0,1), (1,0)], 5, 0, 0, 0),
    ([(-1,0), (0,-1), (0,1), (1,0)], 5, 0, 0, 0),
    ([(-1,-1), (0,1), (1,0)], 4, 0, 0, 0),
]
ok = true; seen = Set{Vector{Pt}}()
for (verts, n, c, d, h) in paper
    global ok
    lp, _ = latpoints(verts)
    nf = normalform(lp)
    push!(seen, nf)
    if !haskey(table, nf) || table[nf] != (n, c, d, h)
        println("  mismatch for ", verts, ": computed ", get(table, nf, nothing), ", paper ", (n, c, d, h))
        ok = false
    end
end
check(ok && length(seen) == 16, "Table II: points, covers, depth and height of all sixteen polygons")

maxd = maximum(v[3] for v in values(table))
argmax_d = [k for (k, v) in table if v[3] == maxd]
check(maxd == 5 && length(argmax_d) == 1 && table[argmax_d[1]][1] == 10,
      "D_2 = 5, attained only by the ten-point triangle")
check(maximum(v[4] for v in values(table)) == 6, "the longest descent of a reflexive polygon has 6 steps")
check(all(v -> v[4] - v[3] <= 1, values(table)),
      "shortest and longest descents of a polygon differ by at most one")
check(count(v -> v[2] == 0, values(table)) == 3, "three polygons are r-minimal")

# every polygon with at least six points contains an r-minimal polygon with five points
fives = true
for (nf, pts) in classes
    global fives
    length(pts) >= 6 || continue
    subs = reflexive_subpolygons(pts)
    any(G -> length(G) == 5 && isempty(covers(G)), subs) || (fives = false)
end
check(fives, "every polygon with at least six points contains a five-point r-minimal polygon")
# Proposition: delta(Delta) = |Delta| - m(Delta), m the largest number of lattice
# points of an r-minimal polygon inside Delta; the longest descent likewise ends
# at an r-minimal polygon with the fewest points
formula = true
for (nf, pts) in classes
    global formula
    subs = vcat([pts], reflexive_subpolygons(pts))
    ends = [length(G) for G in subs if isempty(covers(G))]
    (table[nf][3] == length(pts) - maximum(ends) && table[nf][4] == length(pts) - minimum(ends)) ||
        (formula = false)
end
check(formula, "delta(Delta) = |Delta| - m(Delta) and h(Delta) = |Delta| - (fewest points of an r-minimal subpolygon)")

println("polygons.jl: $passes passed, $fails failed")
exit(fails == 0 ? 0 : 1)
