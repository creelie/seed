"""Batched cut certificates for the depth of reflexive 4-polytopes, with a threshold T.

For reflexive Gamma inside reflexive Delta every maximal chain of reflexive polytopes between
them consists of covers and has length at most min(|Delta|-|Gamma|, |Gamma*|-|Delta*|), so
delta(Delta) <= that number + delta(Gamma) <= that number + L(Gamma), with L the pair bound.
A cut keeps the lattice points x of Delta with <x,q> >= -1 for a lattice point q of
3 Delta* outside Delta*; PALP decides reflexivity and counts the dual points.
Polytopes are processed in chunks so that each PALP call serves many of them."""
import sys, os, subprocess, csv, json, time
import numpy as np
HERE=os.path.dirname(os.path.abspath(__file__))
PALP=os.environ.get('PALP',os.path.join(HERE,'palp','poly.x'))
Lpair={}
for r in csv.DictReader(open(os.path.join(HERE,'..','data','pair_chain.csv'))):
    Lpair[(int(r['points']),int(r['dual_points']))]=int(r['L'])
BIG=10**6

def _palp(inputs,flags):
    buf=[]
    for P in inputs:
        buf.append(f"{len(P)} 4"); buf.extend(' '.join(map(str,p)) for p in P)
    return subprocess.run([PALP,flags],input='\n'.join(buf)+'\n',capture_output=True,text=True).stdout

def _blocks(out,tag):
    """matrices following header lines that contain tag, as int arrays n x 4"""
    L=out.split('\n'); res=[]; i=0
    while i<len(L):
        if tag in L[i]:
            a,b=map(int,L[i].split()[:2])
            rows=[list(map(int,L[i+1+k].split())) for k in range(a)]
            M=np.array(rows,dtype=np.int64)
            res.append(M.T if (a<=b and a==4 and b!=4) else M); i+=1+a
        else: i+=1
    return res

def points_and_duals(polys):
    """for reflexive polytopes given by vertex lists: (points n x 4, dual vertices m x 4)"""
    out=_palp(polys,'-fpe')
    P=_blocks(out,'Points of P'); E=_blocks(out,'Equations of P')
    assert len(P)==len(polys)==len(E),(len(P),len(E),len(polys))
    return P,E

def lattice_points(polys):
    out=_palp(polys,'-fp'); P=_blocks(out,'Points of P'); assert len(P)==len(polys); return P

def counts(sets):
    out=_palp(sets,'-fgI'); res=[]
    for l in out.split('\n'):
        if l.startswith('M:'):
            t=l.split(); res.append((int(t[0][2:]),int(t[2][2:])) if t[2].startswith('N:') else None)
    return res

def counts_safe(sets):
    if not sets: return []
    c=counts(sets)
    if len(c)==len(sets): return c
    if len(sets)==1: return [None]
    h=len(sets)//2; return counts_safe(sets[:h])+counts_safe(sets[h:])

def cuts(X,Q):
    """distinct full-dimensional cut point sets, smallest first"""
    G=X@Q.T
    Q=Q[G.min(0)<=-2]; G=G[:,G.min(0)<=-2]
    H=G>=-1; n=H.sum(0); keep=n>=6; H=H[:,keep]; n=n[keep]; Q=Q[keep]
    if H.shape[1]==0: return []
    pk=np.packbits(H,axis=0).T.copy()
    _,idx=np.unique(pk.view(np.dtype((np.void,pk.shape[1]))).ravel(),return_index=True)
    idx=idx[np.argsort(n[idx],kind='stable')]
    out=[]
    for j in idx:
        h=X[H[:,j]]
        if np.linalg.matrix_rank((h[1:]-h[0]).astype(float))==4: out.append((h,tuple(int(t) for t in Q[j])))
    return out

def certify_chunk(polys,T,batch=48,maxsteps=40):
    """polys: list of (vertex list, p, q).  Returns list of (bound, path)."""
    n=len(polys); bound=[None]*n; path=[[(p,q,0)] for _,p,q in polys]
    st=[]
    for i,(V,p,q) in enumerate(polys):
        L=Lpair.get((p,q),BIG); bound[i]=L
        st.append(dict(V=V,p=p,q=q,cost=0,done=L<=T))
    for step in range(maxsteps):
        act=[i for i in range(n) if not st[i]['done']]
        if not act: break
        P,E=points_and_duals([st[i]['V'] for i in act])
        Q3=lattice_points([(3*E[k]).tolist() for k in range(len(act))])
        C={i:cuts(P[k],Q3[k]) for k,i in enumerate(act)}
        best={i:None for i in act}; pos={i:0 for i in act}; open_=set(act)
        while open_:
            sets=[];own=[]
            for i in sorted(open_):
                c=C[i][pos[i]:pos[i]+batch]; pos[i]+=batch
                sets+=c; own+=[i]*len(c)
            res=counts_safe([s.tolist() for s,_ in sets])
            for (s,qv),i,r in zip(sets,own,res):
                if r is None: continue
                p2,q2=r; s_=st[i]; sc=min(s_['p']-p2,q2-s_['q'])+Lpair.get((p2,q2),BIG)
                if best[i] is None or sc<best[i][0]: best[i]=(sc,s,p2,q2,qv)
            for i in list(open_):
                if (best[i] and st[i]['cost']+best[i][0]<=T) or pos[i]>=len(C[i]): open_.discard(i)
        for i in act:
            s_=st[i]
            if best[i] is None: s_['done']=True; continue
            sc,S,p2,q2,qv=best[i]; s_['cost']+=min(s_['p']-p2,q2-s_['q'])
            s_['p'],s_['q']=p2,q2; s_['V']=S.tolist()
            path[i].append((p2,q2,s_['cost'],qv))
            bound[i]=min(bound[i],s_['cost']+Lpair.get((p2,q2),BIG))
            if bound[i]<=T or Lpair.get((p2,q2),BIG)==0: s_['done']=True
    return list(zip(bound,path))
