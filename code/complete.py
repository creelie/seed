"""Complete lower covers of a reflexive polytope (any dimension d >= 2).

Candidates q for cuts: lattice points outside Delta^* with
   sum_v w_v * max(1, -<v,q>) <= VMAX,   w_v = nvol(conv(0, facet of Delta^* dual to v)),
(the left side is nvol(conv(Delta^* u {q})), which lies in Gamma^* for a cover Gamma whose
dual has q as a vertex; nvol(Gamma^*) <= VMAX by Balletti-Kasprzyk-Nill, Cor. 1.2 for d = 4,
and by the finite lists for d = 2, 3), and such that <x,q> = -1 holds on d affinely
independent lattice points x of Delta (q is a vertex of Gamma^*, so this is a facet of Gamma).
"""
import sys, math, itertools
import numpy as np
from scipy.spatial import ConvexHull
from scipy.optimize import linprog
import rhull
VMAX={2:9,3:72,4:3528}

def dual_points_and_weights(S,F):
    d=len(F[0][0])
    V=rhull.vertices(S,F)
    A=np.array([a for a,c in F],dtype=np.int64)
    box=[(int(A[:,i].min()),int(A[:,i].max())) for i in range(d)]
    Dst=rhull.lattice_points_H([(v,-1) for v in V],box)
    Y=np.array(Dst,dtype=np.int64)
    w={}
    for v in V:
        fp=Y[(Y@np.array(v))==-1]
        pts=np.vstack([fp,np.zeros((1,d),dtype=np.int64)]).astype(float)
        vol=ConvexHull(pts).volume*math.factorial(d)
        w[v]=int(round(vol))
    return V,set(Dst),w

def candidate_cuts(S,F,V,Dst,w,d):
    Vm=VMAX[d]; W=sum(w.values())
    Vv=np.array(V,dtype=np.int64); wv=np.array([w[v] for v in V],dtype=np.int64)
    # region R': -<v,q> <= (Vm-W+w_v)/w_v
    A_ub=-Vv.astype(float); b_ub=np.array([(Vm-W+w[v])/w[v] for v in V])
    box=[]
    for i in range(d):
        c=np.zeros(d); c[i]=1
        lo=linprog(c,A_ub=A_ub,b_ub=b_ub,bounds=[(None,None)]*d).fun
        hi=-linprog(-c,A_ub=A_ub,b_ub=b_ub,bounds=[(None,None)]*d).fun
        box.append((math.floor(lo-1e-9),math.ceil(hi+1e-9)))
    X=np.array(sorted(S),dtype=np.int64)
    out=[]
    ranges=[np.arange(lo,hi+1) for lo,hi in box]
    # chunk over the first d-2 coordinates, so that each chunk is a plane of the box
    grids=np.meshgrid(*ranges[d-2:],indexing='ij'); tail=np.stack([g.ravel() for g in grids],axis=1)
    for head in itertools.product(*ranges[:d-2]):
        Q=np.hstack([np.tile(np.array(head,dtype=np.int64),(len(tail),1)),tail])
        Q=Q[np.all(-(Q@Vv.T)<=b_ub+1e-9,axis=1)]
        if len(Q)==0: continue
        P=-(Q@Vv.T)
        ok=(np.maximum(P,1)@wv<=Vm)&(P.max(axis=1)>=2)
        Q=Q[ok]
        if len(Q)==0: continue
        H=(X@Q.T==-1)
        cnt=H.sum(axis=0)
        for j in np.nonzero(cnt>=d)[0]:
            fp=X[H[:,j]]
            if np.linalg.matrix_rank((fp[1:]-fp[0]).astype(float))==d-1:
                out.append(tuple(int(t) for t in Q[j]))
    return out

def candidate_cuts_subsets(S,F,V,Dst,w,d,chunk=200000):
    """Same candidate set, enumerated through the facet condition: q is the unique solution of
    <x_i,q> = -1 for d linearly independent lattice points x_i of Delta."""
    Vm=VMAX[d]
    Vv=np.array(V,dtype=np.int64); wv=np.array([w[v] for v in V],dtype=np.int64)
    X=np.array(sorted(x for x in S if any(x)),dtype=np.int64)
    out=set()
    it=itertools.combinations(range(len(X)),d)
    while True:
        idx=np.array(list(itertools.islice(it,chunk)),dtype=np.int64)
        if len(idx)==0: break
        M=X[idx].astype(float)
        det=np.linalg.det(M)
        ok=np.abs(det)>0.5
        M=M[ok]; idx=idx[ok]
        if len(M)==0: continue
        q=np.linalg.solve(M,-np.ones((len(M),d,1)))[...,0]
        qi=np.rint(q).astype(np.int64)
        good=np.all(np.abs(q-qi)<1e-6,axis=1)
        qi=qi[good]; idx=idx[good]
        exact=np.all(np.einsum('mij,mj->mi',X[idx],qi)==-1,axis=1)
        qi=qi[exact]
        if len(qi)==0: continue
        P=-(qi@Vv.T)
        keep=(np.maximum(P,1)@wv<=Vm)&(P.max(axis=1)>=2)
        for t in qi[keep]: out.add(tuple(int(u) for u in t))
    return sorted(out)

def covers(S,F,stats=None,method='auto'):
    d=len(F[0][0])
    V,Dst,w=dual_points_and_weights(S,F)
    n=len(S)-1
    if method=='subsets' or (method=='auto' and d>=4 and math.comb(n,d)<=3*10**7):
        cands=candidate_cuts_subsets(S,F,V,Dst,w,d)
    else:
        cands=candidate_cuts(S,F,V,Dst,w,d)
    found=set(); memo={}; nonrefl=0
    for q in cands:
        H=[x for x in S if sum(a*b for a,b in zip(x,q))>=-1]
        if len(H)<d+1: continue
        r=rhull.Tinf(rhull.closure(H))
        if r is None: continue
        Q,FQ=r
        if rhull.is_reflexive(FQ): found.add(Q)
        else:
            nonrefl+=1
            found|=rhull.max_reflexive_subpolytopes(Q,memo)
    if stats is not None: stats.update(ncand=len(cands),nonrefl=nonrefl)
    return rhull._maximal(found)
