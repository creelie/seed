"""Independent replay of depth certificates.

A certificate for a reflexive 4-polytope Delta is a list of cut vectors q_1, ..., q_k.  The replay
starts from the lattice points of Delta, keeps at step i the points x with <x,q_i> >= -1, checks
with PALP that their hull Gamma_i is reflexive and that it has exactly those lattice points, and
charges the step either the exact interval length ell[Gamma_i, Gamma_{i-1}] (when the
certificate marks it exact; recomputed here) or min(|Gamma_{i-1}|-|Gamma_i|,
|Gamma_i^*|-|Gamma_{i-1}^*|).  The certified bound is the total charge plus the pair bound
L(|Gamma_k|, |Gamma_k^*|).

  python3 verify_certs.py CERTS.jsonl[.gz] [T] [--legacy]
Each line is a JSON object with the vertices ('verts') and the cuts ('cuts', each [q, p, q*,
cost, exact] as written by hcert.py, or a bare vector q as written by farm_shard.py).

With --legacy the cut vectors are read as written by the first farm run (tag t50), whose
bcert.cuts paired each kept point set with the cut vector of the same position in the list
before the sets with fewer than six points were dropped.  The point sets and the bounds of
that run are right; only the recorded vectors are shifted, and the replay undoes the shift by
recomputing the same list exactly as the farm did."""
import sys, os, json, gzip
import numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import bcert, hcert

def legacy_cut(Vin,q):
    """the point set that the first farm run recorded under the vector q"""
    P,E=bcert.points_and_duals([Vin]); X=P[0]
    Q=bcert.lattice_points([(3*E[0]).tolist()])[0]
    G=X@Q.T; Q=Q[G.min(0)<=-2]; G=G[:,G.min(0)<=-2]
    H=G>=-1; n=H.sum(0); keep=n>=6; H=H[:,keep]
    for j in range(H.shape[1]):
        if tuple(int(t) for t in Q[j])==tuple(q): return X[H[:,j]]
    return None

def replay(V,cuts,legacy=False):
    P,E=bcert.points_and_duals([V]); X=P[0]; Vin=V
    pq=bcert.counts_safe([X.tolist()])[0]
    if pq is None: return None,'not reflexive'
    total=0
    for c in cuts:
        q=np.array(c[0] if isinstance(c[0],list) else c,dtype=np.int64)
        exact=bool(c[4]) if isinstance(c[0],list) else False
        if legacy:
            h=legacy_cut(Vin,q)
            if h is None: return None,'legacy vector not found'
        else: h=X[(X@q)>=-1]
        r=bcert.counts_safe([h.tolist()])[0]
        if r is None: return None,'cut not reflexive'
        if r[0]!=len(h): return None,'cut not closed'
        if exact:
            Dd=hcert.dual_pts(X); e,ex=hcert.ell(X,h,Dd,hcert.dual_pts(h))
            if not ex: return None,'interval not exact'
        else: e=min(pq[0]-r[0],r[1]-pq[1])
        if isinstance(c[0],list) and int(c[3])<e: return None,'cost understated'
        total+=e; X=h; pq=r; Vin=h.tolist()
    return total+bcert.Lpair.get(pq,bcert.BIG),'ok'

if __name__=='__main__':
    legacy='--legacy' in sys.argv; args=[a for a in sys.argv[1:] if a!='--legacy']
    f=args[0]; T=int(args[1]) if len(args)>1 else None
    op=gzip.open if f.endswith('.gz') else open
    n=bad=0; mx=0
    for line in op(f,'rt'):
        d=json.loads(line); b,msg=replay(d['verts'],d['cuts'],legacy); n+=1
        if b is None or (T is not None and b>T) or b>d['bound']:
            bad+=1; print('FAIL',n,msg,b,d.get('bound'),flush=True)
        else: mx=max(mx,b)
    print(n,'certificates replayed,',bad,'failures, largest bound',mx)
