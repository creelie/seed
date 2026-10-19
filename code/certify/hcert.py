"""Second-stage cut certificates for the polytopes left above T by bcert.py.

The cuts are those of bcert.py (q a lattice point of 3 Delta* outside Delta*), but the cost of a
cut is the exact length of the shortest maximal chain in the interval [Gamma, Delta] of the
reflexive poset when the smaller side of the difference has at most CAP points, and the crude
bound min(|Delta|-|Gamma|, |Gamma*|-|Delta*|) otherwise.  Every maximal chain in the interval
consists of covers, so delta(Delta) <= ell[Gamma, Delta] + delta(Gamma).  The intermediate
reflexive polytopes are the closed reflexive sets Gamma u S with S inside Delta minus Gamma, or,
on the dual side, Delta* u S with S inside Gamma* minus Delta*; the shortest maximal chain is
found by breadth-first search over the Hasse diagram of these sets.  A beam search keeps the
best few partial chains at each step, scored by cost so far plus the pair bound L."""
import itertools, os, sys
import numpy as np
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
import bcert
L=bcert.Lpair; BIG=bcert.BIG
CAP=12

def dual_pts(X):
    P,E=bcert.points_and_duals([X.tolist()])
    return bcert.lattice_points([E[0].tolist()])[0]

def interval_length(base,extra,cap=CAP):
    """shortest maximal chain from the closed reflexive set base to base u extra, or None"""
    c=len(extra)
    if c<=1: return c
    if c>cap: return None
    subs=[s for r in range(1,c) for s in itertools.combinations(range(c),r)]
    sets=[np.vstack([base,extra[list(s)]]).tolist() for s in subs]
    res=bcert.counts_safe(sets)
    valid=[frozenset()]+[frozenset(s) for s,r,X in zip(subs,res,sets) if r is not None and r[0]==len(X)]
    full=frozenset(range(c)); valid=sorted(set(valid+[full]),key=len)
    dist={frozenset():0}; frontier=[frozenset()]
    while frontier:
        nxt=[]
        for A in frontier:
            sup=[B for B in valid if A<B]
            for B in sup:
                if any(C<B for C in sup): continue
                if B not in dist: dist[B]=dist[A]+1; nxt.append(B)
        if full in dist: return dist[full]
        frontier=nxt
    return None

def ell(Xd,Xg,Dd,Dg,cap=CAP):
    """(cost, exact): interval length between Gamma (points Xg, dual points Dg) and Delta"""
    sd=set(map(tuple,Xd.tolist())); sg=set(map(tuple,Xg.tolist()))
    a=len(sd)-len(sg); b=len(Dg)-len(Dd); crude=min(a,b)
    if crude<=1: return crude,True
    if a<=b: r=interval_length(Xg,np.array(sorted(sd-sg)),cap)
    else: r=interval_length(Dd,np.array(sorted(set(map(tuple,Dg.tolist()))-set(map(tuple,Dd.tolist())))),cap)
    return (r,True) if r is not None else (crude,False)

def options(X,full=False):
    """dual points of X and the reflexive cuts (counts, points, q).  With full=True the cut
    vectors q also run over the region of Proposition (cuts): q tight on four independent points
    of X with nvol conv(X* u q) at most 3528 (complete.py), which is needed for thin simplices
    whose 3 Delta* has no useful lattice point."""
    P,E=bcert.points_and_duals([X.tolist()])
    Dd=bcert.lattice_points([E[0].tolist()])[0]
    Q3=bcert.lattice_points([(3*E[0]).tolist()])[0]
    if full:
        import rhull, complete
        Xt=[tuple(int(a) for a in x) for x in X.tolist()]
        F=rhull.facets(Xt); V,Dst,w=complete.dual_points_and_weights(frozenset(Xt),F)
        qs=set(map(tuple,Q3.tolist()))|set(complete.candidate_cuts(frozenset(Xt),F,V,Dst,w,4))
        Q3=np.array(sorted(qs),dtype=np.int64)
    C=bcert.cuts(X,Q3)
    res=bcert.counts_safe([h.tolist() for h,_ in C])
    return Dd,[(r,h,qv) for (h,qv),r in zip(C,res) if r is not None]

def certify(V,T,beam=3,maxsteps=40,tries=30,full=False):
    """returns (bound, [(q, points, dual points, cost, exact), ...])"""
    P,E=bcert.points_and_duals([V]); X0=P[0]
    c0=bcert.counts_safe([X0.tolist()])[0]
    states=[(0,X0,c0,[])]; best=(L.get(c0,BIG),[]); seen=set()
    for s in range(maxsteps):
        nxt=[]
        for cost,X,pq,path in states:
            if L.get(pq,BIG)==0: continue
            Dd,opts=options(X,full)
            pick=sorted(opts,key=lambda o:L.get(o[0],BIG))[:tries]
            pick+=sorted(opts,key=lambda o:min(pq[0]-o[0][0],o[0][1]-pq[1]))[:tries]
            for r,h,qv in pick:
                k=tuple(sorted(map(tuple,h.tolist())))
                if k in seen: continue
                seen.add(k)
                e,ex=ell(X,h,Dd,dual_pts(h))
                c2=cost+e; path2=path+[(list(qv),int(r[0]),int(r[1]),int(e),bool(ex))]
                if c2+L.get(r,BIG)<best[0]: best=(c2+L.get(r,BIG),path2)
                nxt.append((c2+L.get(r,BIG),c2,h,r,path2))
        if best[0]<=T or not nxt: break
        nxt.sort(key=lambda o:(o[0],o[1]))
        states=[(c2,h,r,path) for sc,c2,h,r,path in nxt[:beam]]
    return best

def certify_escalate(V,T,full=False):
    """beam 3, then wider searches, until the bound is at most T"""
    best=None
    for beam,tries in ((3,30),(8,60),(16,120)):
        b=certify(V,T,beam=beam,tries=tries,full=full)
        if best is None or b[0]<best[0]: best=b
        if best[0]<=T: break
    return best
