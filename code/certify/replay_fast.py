"""Batched replay of depth certificates, with the same acceptance rule as verify_certs.replay.

verify_certs.replay checks one certificate with one PALP call per cut.  Here the certificates of
a whole chunk of polytopes are replayed step by step, and each step makes one PALP call for all
of them: the point set kept by the cut must be the set of lattice points of a reflexive polytope
(PALP counts its points and its dual points), and the step is charged
min(|Gamma_{i-1}|-|Gamma_i|, |Gamma_i^*|-|Gamma_{i-1}^*|).  Certificates with an exact interval
step are passed to verify_certs.replay unchanged, and so is every certificate whose first try
here fails, so that the batched path can only accept what the single replay accepts.

  replay_chunk(T, items) -> [(row, bound or None, reasons)]
with items a list of (row, vertices, [(recorded bound, cuts, legacy)])."""
import numpy as np
import bcert, verify_certs

def _legacy_sets(states):
    """the point sets that the first farm run recorded under the current vectors"""
    P,E=bcert.points_and_duals([s['V'] for s in states])
    Q3=bcert.lattice_points([(3*E[k]).tolist() for k in range(len(states))])
    out=[]
    for s,X,Q in zip(states,P,Q3):
        q=tuple(int(t) for t in s['cuts'][s['i']])
        G=X@Q.T; m=G.min(0)<=-2; Q=Q[m]; G=G[:,m]
        H=G>=-1; keep=H.sum(0)>=6; H=H[:,keep]; Q=Q[keep]
        h=None
        for j in range(H.shape[1]):
            if tuple(int(t) for t in Q[j])==q: h=X[H[:,j]]; break
        out.append(h)
    return out

def replay_chunk(T,items):
    res={}; first={}; slow=[]
    for r,V,cands in items:
        c=sorted((x for x in cands if x[0]<=T),key=lambda x:x[0])
        if not c: res[r]=(None,['no certificate']); continue
        b,cuts,leg=c[0]
        if any(isinstance(t[0],list) and bool(t[4]) for t in cuts if isinstance(t,list) and t and isinstance(t[0],list)):
            slow.append((r,V,c)); continue
        vec=[t[0] if (isinstance(t,list) and t and isinstance(t[0],list)) else t for t in cuts]
        cost=[int(t[3]) if (isinstance(t,list) and t and isinstance(t[0],list)) else None for t in cuts]
        first[r]=dict(r=r,V=V,b=b,cuts=vec,cost=cost,leg=leg,i=0,total=0,c=c)
    st=list(first.values())
    if st:
        P,_=bcert.points_and_duals([s['V'] for s in st])
        pq=bcert.counts_safe([X.tolist() for X in P])
        live=[]
        for s,X,x in zip(st,P,pq):
            if x is None: s['fail']='not reflexive'; continue
            s['X']=X; s['pq']=x; s['V']=X.tolist(); live.append(s)
        while live:
            leg=[s for s in live if s['leg']]
            L=dict(zip(map(id,leg),_legacy_sets(leg))) if leg else {}
            hs=[]
            for s in live:
                if s['leg']: h=L[id(s)]
                else:
                    q=np.array(s['cuts'][s['i']],dtype=np.int64); h=s['X'][(s['X']@q)>=-1]
                hs.append(h)
            ok=[(s,h) for s,h in zip(live,hs) if h is not None]
            for s,h in zip(live,hs):
                if h is None: s['fail']='legacy vector not found'
            cnt=bcert.counts_safe([h.tolist() for _,h in ok])
            nxt=[]
            for (s,h),x in zip(ok,cnt):
                if x is None: s['fail']='cut not reflexive'; continue
                if x[0]!=len(h): s['fail']='cut not closed'; continue
                e=min(s['pq'][0]-x[0],x[1]-s['pq'][1])
                if s['cost'][s['i']] is not None and s['cost'][s['i']]<e: s['fail']='cost understated'; continue
                s['total']+=e; s['X']=h; s['pq']=x; s['V']=h.tolist(); s['i']+=1
                if s['i']==len(s['cuts']): s['got']=s['total']+bcert.Lpair.get(tuple(x),bcert.BIG)
                else: nxt.append(s)
            live=nxt
        for s in st:
            g=s.get('got')
            if g is not None and g<=T and g<=s['b']: res[s['r']]=(g,None)
            else: slow.append((s['r'],None,s['c']))
    Vof={r:V for r,V,_ in items}
    for r,V,c in slow:
        V=Vof[r]; why=[]
        for b,cuts,legacy in c:
            try: got,msg=verify_certs.replay(V,cuts,legacy)
            except Exception as e: got,msg=None,type(e).__name__
            if got is not None and got<=T and got<=b: res[r]=(got,None); break
            why.append(msg if got is None else f'replayed {got} > {min(b,T)}')
        else: res[r]=(None,why or ['no certificate'])
    return [(r,)+res[r] for r,_,_ in items]
