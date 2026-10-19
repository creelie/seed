"""Exact covering depth of a reflexive polytope by breadth-first descent through complete covers.
depth(P) = least k such that some chain of k covers from P ends at a polytope with no cover."""
import sys, json, time
from palp import run_palp, key
import rhull, complete

def nf_keys(sets,d):
    R=run_palp([(d,sorted(s)) for s in sets])
    return [key(r['nf']) for r in R]

def exact_depth(pts,maxlevel=60,verbose=True):
    S=rhull.closure(pts); d=len(next(iter(S)))
    k0=nf_keys([S],d)[0]
    frontier={k0:S}; seen={k0}; level=0; ncov=0
    while level<maxlevel:
        nxt={}
        for k,S in frontier.items():
            F=rhull.facets(list(S))
            cv=complete.covers(S,F); ncov+=1
            if not cv:
                return level,{'minimal':sorted(S),'covers_computed':ncov,'seen':len(seen)}
            ks=nf_keys(cv,d)
            for kk,c in zip(ks,cv):
                if kk not in seen: seen.add(kk); nxt[kk]=c
        level+=1; frontier=nxt
        if verbose: print(' level',level,'frontier',len(frontier),'seen',len(seen),'covers',ncov,flush=True)
    return None,{'seen':len(seen)}

if __name__=='__main__':
    steps=json.load(open(sys.argv[1])); i=int(sys.argv[2])
    P=[tuple(x) for x in steps[i]]
    t=time.time(); dep,info=exact_depth(P)
    print('polytope',i,'points',len(P),'exact depth',dep,info.get('seen'),'secs',round(time.time()-t,1))
    json.dump({'index':i,'points':len(P),'depth':dep,'info':info},open(f'data/depth_{len(P)}.json','w'))
