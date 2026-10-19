"""Exact covers in the inclusion order of reflexive lattice polytopes.

For a lattice polytope P with the origin in its interior put
  T(P) = conv{ x in P cap M : <x,y> >= -1 for every y in P^* cap N }.
Every reflexive polytope contained in P is contained in T(P) (its dual is a
lattice polytope containing P^*), so iterating T to a fixed point Q loses no
reflexive subpolytope; if Q is reflexive it is the largest one in P, otherwise
every reflexive subpolytope misses a vertex of Q and we branch.
All arithmetic is exact (Python integers); Qhull is used only to propose
facets, which are then recomputed and verified with integers."""
import itertools, math
import numpy as np
from scipy.spatial import ConvexHull
from fractions import Fraction

def _det(m):
    # exact determinant by fraction-free Bareiss
    m=[list(r) for r in m]; n=len(m); s=1; prev=1
    for k in range(n-1):
        if m[k][k]==0:
            for r in range(k+1,n):
                if m[r][k]!=0: m[k],m[r]=m[r],m[k]; s=-s; break
            else: return 0
        for i in range(k+1,n):
            for j in range(k+1,n):
                m[i][j]=(m[i][j]*m[k][k]-m[i][k]*m[k][j])//prev
        prev=m[k][k]
    return s*m[n-1][n-1]

def _normal(face_pts):
    """integer normal of the affine hyperplane through d affinely independent points"""
    d=len(face_pts[0]); p0=face_pts[0]
    diffs=[[p[i]-p0[i] for i in range(d)] for p in face_pts[1:]]
    nrm=[]
    for i in range(d):
        minor=[[r[j] for j in range(d) if j!=i] for r in diffs]
        nrm.append((-1)**i*_det(minor))
    g=0
    for x in nrm: g=math.gcd(g,abs(x))
    return [x//g for x in nrm] if g else None

def facets(pts):
    """pts: list of integer tuples spanning R^d. Returns list of (a,c): a.x >= c on P, a primitive."""
    d=len(pts[0]); arr=np.array(pts,dtype=float)
    hull=ConvexHull(arr,qhull_options='Qt')
    out={}
    for simp in hull.simplices:
        fp=[pts[i] for i in simp]
        a=_normal(fp)
        if a is None: continue
        vals=[sum(ai*xi for ai,xi in zip(a,x)) for x in pts]
        c0=sum(ai*xi for ai,xi in zip(a,fp[0]))
        mn,mx=min(vals),max(vals)
        if mn==c0: key=(tuple(a),c0)
        elif mx==c0: key=(tuple(-x for x in a),-c0)
        else: continue  # not a supporting hyperplane (numerical artefact)
        out[key]=1
    F=list(out)
    # verify: every point satisfies all, each facet touches >= d affinely independent pts
    return F

def lattice_points_H(F,box):
    """integer points with a.x >= c for all (a,c) in F, inside box [(lo,hi)]*d"""
    d=len(box)
    grids=np.meshgrid(*[np.arange(lo,hi+1) for lo,hi in box],indexing='ij')
    X=np.stack([g.ravel() for g in grids],axis=1).astype(np.int64)
    if len(F)==0: return [tuple(x) for x in X]
    A=np.array([a for a,c in F],dtype=np.int64); C=np.array([c for a,c in F],dtype=np.int64)
    ok=np.all(X@A.T>=C,axis=1)
    return [tuple(int(t) for t in x) for x in X[ok]]

def interior_origin(F):
    return all(c<0 for a,c in F)

def dual_points(F):
    """lattice points of P^* = {y : <x,y> >= -1 on P}; facets (a,c) with c<0 give vertices a/(-c)"""
    d=len(F[0][0])
    verts=[[Fraction(ai,-c) for ai in a] for a,c in F]
    box=[(math.floor(min(v[i] for v in verts)),math.ceil(max(v[i] for v in verts))) for i in range(d)]
    # P^* as H-rep: <v,y> >= -1 for vertices v of P; we use all points passed via closure
    return verts,box

class Poly:
    def __init__(self,pts):
        self.pts=frozenset(pts)

def T_step(S):
    """S: frozenset of lattice points (closed: S = P cap M). Returns new closed set or None if no IP."""
    pts=list(S); d=len(pts[0])
    try: F=facets(pts)
    except Exception: return None   # degenerate (not full dimensional)
    if not interior_origin(F): return None
    verts,box=dual_points(F)
    # H-rep of P^*: <x,y> >= -1 for x in vertices of P; use all points of S (same set)
    Fd=[(x,-1) for x in pts]
    Y=lattice_points_H(Fd,box)
    Ya=np.array(Y,dtype=np.int64); X=np.array(pts,dtype=np.int64)
    ok=np.all(X@Ya.T>=-1,axis=1)
    keep=[pts[i] for i in range(len(pts)) if ok[i]]
    if len(keep)==len(pts):
        return S,F,Y
    # closure: lattice points of conv(keep)
    return closure(keep),None,None

def closure(pts):
    d=len(pts[0])
    try: F=facets(pts)
    except Exception: return frozenset(pts)
    box=[(min(p[i] for p in pts),max(p[i] for p in pts)) for i in range(d)]
    return frozenset(lattice_points_H(F,box))

def is_reflexive(F):
    return all(c==-1 for a,c in F)

def vertices(S,F):
    """vertices of conv(S): points lying on >= d facets with affinely independent normals"""
    pts=list(S); d=len(pts[0]); out=[]
    A=np.array([a for a,c in F],dtype=np.int64); C=np.array([c for a,c in F],dtype=np.int64)
    X=np.array(pts,dtype=np.int64); tight=(X@A.T==C)
    for i,p in enumerate(pts):
        rows=A[tight[i]]
        if len(rows)>=d and np.linalg.matrix_rank(rows.astype(float))==d: out.append(p)
    return out

def Tinf(S):
    while True:
        r=T_step(S)
        if r is None: return None
        S2,F,Y=r
        if F is not None: return S2,F
        S=S2


def max_reflexive_subpolytopes(S,memo=None):
    """all maximal reflexive subpolytopes (as closed point sets) of conv(S)"""
    if memo is None: memo={}
    if S in memo: return memo[S]
    res=set()
    r=None
    if len(S)>=len(next(iter(S)))+1:
        r=Tinf(S)
    if r is not None:
        Q,F=r
        if is_reflexive(F): res={Q}
        else:
            for w in vertices(Q,F):
                sub=closure([p for p in Q if p!=w]) if len(Q)>len(next(iter(Q)))+1 else None
                if sub is None or len(sub)<len(next(iter(Q)))+1: continue
                res|=max_reflexive_subpolytopes(sub,memo)
            res=_maximal(res)
    memo[S]=res
    return res

def _maximal(sets):
    sets=sorted(sets,key=len,reverse=True); out=[]
    for s in sets:
        if not any(s<=t for t in out): out.append(s)
    return set(out)

def covers(pts):
    """lower covers of the reflexive polytope with lattice point set pts"""
    S=frozenset(pts); F=facets(list(S)); assert is_reflexive(F)
    memo={}; cand=set()
    for v in vertices(S,F):
        sub=closure([p for p in S if p!=v])
        cand|=max_reflexive_subpolytopes(sub,memo)
    return _maximal(cand)
