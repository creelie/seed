"""Independent check of a cover chain: each next polytope must be among the complete covers
of the previous one, and the last polytope must have no cover (r-minimal)."""
import sys, json, time
import rhull, complete
steps=json.load(open(sys.argv[1])); lo=int(sys.argv[2]); hi=int(sys.argv[3])
for i in range(lo,hi):
    t=time.time()
    S=frozenset(tuple(x) for x in steps[i]); F=rhull.facets(list(S))
    cv=complete.covers(S,F)
    if i+1<len(steps):
        nxt=frozenset(tuple(x) for x in steps[i+1])
        ok=any(frozenset(c)==nxt for c in cv)
        print('step',i,len(S),'->',len(nxt),'is cover',ok,'ncovers',len(cv),'secs',round(time.time()-t,1),flush=True)
    else:
        print('last',i,len(S),'ncovers',len(cv),'minimal',len(cv)==0,flush=True)
