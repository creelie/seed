"""One job of the second stage of the certificate farm: the polytopes of results/SRC/left.json
with index congruent to K modulo N are certified by hcert.py.

  python3 hcert_shard.py LEFT K N T NPROC OUT
writes OUT/hsummary-K.json (counts, histogram, polytopes still above T) and OUT/hcerts-K.jsonl
(one line per polytope: file, rowgroup, row, bound, and the cuts with their costs)."""
import sys, os, json, time
from multiprocessing import Pool
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import hcert

def work(args):
    T,d=args; t=time.time()
    b,path=hcert.certify_escalate(d['verts'],T)
    if b>T:
        # thin polytopes whose 3 Delta* has no useful lattice point need the full set of cuts
        b2,path2=hcert.certify_escalate(d['verts'],T,full=True)
        if b2<b: b,path=b2,path2
    return d,b,path,round(time.time()-t,1)

if __name__=='__main__':
    left,K,N,T,nproc,out=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]),sys.argv[6]
    os.makedirs(out,exist_ok=True)
    items=[d for i,d in enumerate(json.load(open(left))) if i%N==K]
    hist={}; still=[]; n=0; t0=time.time()
    with open(os.path.join(out,f'hcerts-{K}.jsonl'),'w') as fh, Pool(nproc) as pool:
        for d,b,path,secs in pool.imap_unordered(work,[(T,d) for d in items]):
            fh.write(json.dumps(dict(file=d['file'],rowgroup=d['rowgroup'],row=d['row'],bound=b,cuts=path))+'\n')
            hist[b]=hist.get(b,0)+1; n+=1
            if b>T: still.append(dict(d,bound=b,cuts=path))
            print(d['file'],d['rowgroup'],d['row'],d['bound'],'->',b,secs,flush=True)
    s=dict(K=K,N=N,T=T,items=len(items),certified=n-len(still),max=max(hist,default=0),
           hist={str(k):hist[k] for k in sorted(hist)},left=still,secs=round(time.time()-t0,1))
    json.dump(s,open(os.path.join(out,f'hsummary-{K}.json'),'w'))
    print(json.dumps({k:s[k] for k in ('K','items','certified','max','secs')}),'left',len(still),flush=True)
