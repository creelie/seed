import json,sys,random,time
from palp import run_palp, key
import rhull, complete
p=json.load(open('data/poset3.json'))
keys=[k for k in p['covers'] if p['covers'][k]]
lo,hi=int(sys.argv[1]),int(sys.argv[2]); ks=keys[lo:hi]
def pts_of(k): return [tuple(map(int,v.split(','))) for v in k.split(';')]
R=run_palp([(3,pts_of(k)) for k in ks])
ok=0;t=time.time();tot=dict(ncand=0,nonrefl=0)
for k,ri in zip(ks,R):
    S=frozenset(ri['pts']); F=rhull.facets(list(S)); st={}
    cv=complete.covers(S,F,st)
    rr=run_palp([(3,sorted(c)) for c in cv]) if cv else []
    got={key(x['nf']) for x in rr}
    ok+=got==set(p['covers'][k]); tot['ncand']+=st['ncand']; tot['nonrefl']+=st['nonrefl']
    if got!=set(p['covers'][k]): print('MISMATCH',k,len(got),len(p['covers'][k]),flush=True)
print('ok',ok,'of',len(ks),tot,'secs',round(time.time()-t,1))
