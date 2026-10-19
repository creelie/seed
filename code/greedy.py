"""Greedy certified cover chains in any dimension (upper bounds for covering depth).
A step: pick a cut q (lattice point outside Delta^*), Gamma = Tinf(H_q) reflexive,
then climb: for q' in Gamma^* minus Delta^*, R = Tinf(H_q') contains Gamma; if R is a
strictly larger reflexive polytope replace Gamma by R. Stop when no q' enlarges Gamma:
then Gamma is a lower cover of Delta (proof in the paper)."""
import sys, itertools, json, time
import numpy as np
import rhull

def dual_lattice(S,F):
    # F reflexive: dual vertices are the normals a (c=-1)
    A=np.array([a for a,c in F],dtype=np.int64)
    d=A.shape[1]
    box=[(int(A[:,i].min()),int(A[:,i].max())) for i in range(d)]
    X=np.array(list(S),dtype=np.int64)
    V=rhull.vertices(S,F)
    return set(rhull.lattice_points_H([(v,-1) for v in V],box)), V

def cut(S,q):
    X=[x for x in S if sum(a*b for a,b in zip(x,q))>=-1]
    d=len(q)
    if len(X)<d+1: return None
    r=rhull.Tinf(rhull.closure(X))
    return r

class Stalled(Exception): pass

def climb(S,Dstar,G,FG):
    while True:
        Gd,_=dual_lattice(G,FG)
        grew=False
        for q in Gd-Dstar:
            r=cut(S,q)
            if r is None: raise Stalled('cut lost IP')
            R,FR=r
            if R==G: continue
            if not rhull.is_reflexive(FR): raise Stalled('nonreflexive above')
            if len(R)>len(G) and G<=R:
                G,FG=R,FR; grew=True; break
        if not grew: return G,FG

def candidates(S,F,Dstar,V,gmax):
    A=np.array([a for a,c in F],dtype=np.int64); d=A.shape[1]
    box=[(int(A[:,i].min())-gmax,int(A[:,i].max())+gmax) for i in range(d)]
    grids=np.meshgrid(*[np.arange(lo,hi+1) for lo,hi in box],indexing='ij')
    Q=np.stack([g.ravel() for g in grids],axis=1)
    Vv=np.array(V,dtype=np.int64)
    g=(-(Q@Vv.T)).max(axis=1)
    sel=(g>=2)&(g<=gmax)
    return [tuple(int(t) for t in q) for q in Q[sel]]

def one_step(S,F,gmax=3,mode='small'):
    Dstar,V=dual_lattice(S,F)
    best=None
    seen=set()
    for q in candidates(S,F,Dstar,V,gmax):
        r=cut(S,q)
        if r is None: continue
        G,FG=r
        if not rhull.is_reflexive(FG) or G in seen: continue
        seen.add(G)
        if best is None or len(G)<len(best[0]): best=(G,FG)
    if best is None: return None
    return climb(S,Dstar,*best)

def chain(pts,gmax=3,verbose=True):
    S=rhull.closure(pts); F=rhull.facets(list(S)); assert rhull.is_reflexive(F)
    out=[len(S)]; steps=[sorted(S)]
    while True:
        r=one_step(S,F,gmax)
        if r is None: break
        S,F=r; out.append(len(S)); steps.append(sorted(S))
        if verbose: print(' step',len(out)-1,len(S),flush=True)
    chain.steps=steps
    return out

if __name__=='__main__':
    V=json.loads(sys.argv[1])
    t=time.time(); c=chain([tuple(v) for v in V])
    print('chain',c,'length',len(c)-1,'secs',round(time.time()-t,1))
    if len(sys.argv)>2: json.dump(chain.steps,open(sys.argv[2],'w'))
