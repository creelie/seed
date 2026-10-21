"""One job of the second stage of the certificate farm: the polytopes of results/SRC/left.json
with index congruent to K modulo N are certified by hcert.py.

  python3 hcert_shard.py LEFT K N T NPROC OUT [MEM_GB SECS]
writes OUT/hsummary-K.json (counts, histogram, polytopes still above T) and OUT/hcerts-K.jsonl
(one line per polytope: file, rowgroup, row, bound, and the cuts with their costs).

With MEM_GB and SECS each worker is limited to MEM_GB of address space and each polytope to SECS
seconds; a polytope that exceeds either keeps its first-stage bound, is listed under "hard" in
the summary and stays among the polytopes above T, so one expensive polytope cannot take the
whole runner down."""
import sys, os, json, time, signal, resource
from multiprocessing import Pool
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import hcert

class Budget(Exception): pass

def _alarm(*_): raise Budget()

def init(mem_gb):
    signal.signal(signal.SIGALRM,_alarm)
    if mem_gb:
        lim=int(mem_gb*2**30); resource.setrlimit(resource.RLIMIT_AS,(lim,lim))

def certify(T,d):
    b,path=hcert.certify_escalate(d['verts'],T)
    if b>T:
        # thin polytopes whose 3 Delta* has no useful lattice point need the full set of cuts
        b2,path2=hcert.certify_escalate(d['verts'],T,full=True)
        if b2<b: b,path=b2,path2
    return b,path

def work(args):
    T,d,secs=args; t=time.time()
    if not secs: return d,*certify(T,d),round(time.time()-t,1),False
    signal.alarm(secs)
    try:
        b,path=certify(T,d); hard=False
    except Exception as e:
        b,path,hard=d['bound'],None,type(e).__name__
    finally:
        signal.alarm(0)
    return d,b,path,round(time.time()-t,1),hard

if __name__=='__main__':
    left,K,N,T,nproc,out=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]),sys.argv[6]
    mem_gb=float(sys.argv[7]) if len(sys.argv)>7 else 0; secs=int(sys.argv[8]) if len(sys.argv)>8 else 0
    os.makedirs(out,exist_ok=True)
    items=[d for i,d in enumerate(json.load(open(left))) if i%N==K]
    hist={}; still=[]; hard=[]; n=0; t0=time.time()
    with open(os.path.join(out,f'hcerts-{K}.jsonl'),'w') as fh, Pool(nproc,init,(mem_gb,),maxtasksperchild=1 if mem_gb else None) as pool:
        for d,b,path,dt,why in pool.imap_unordered(work,[(T,d,secs) for d in items]):
            if why: hard.append(dict(file=d['file'],rowgroup=d['rowgroup'],row=d['row'],reason=why))
            else: fh.write(json.dumps(dict(file=d['file'],rowgroup=d['rowgroup'],row=d['row'],bound=b,cuts=path))+'\n')
            hist[b]=hist.get(b,0)+1; n+=1
            if b>T: still.append(dict(d,bound=b,cuts=path))
            print(d['file'],d['rowgroup'],d['row'],d['bound'],'->',b,dt,why or '',flush=True)
    s=dict(K=K,N=N,T=T,items=len(items),certified=n-len(still),max=max(hist,default=0),
           hist={str(k):hist[k] for k in sorted(hist)},left=still,hard=hard,secs=round(time.time()-t0,1))
    json.dump(s,open(os.path.join(out,f'hsummary-{K}.json'),'w'))
    print(json.dumps({k:s[k] for k in ('K','items','certified','max','secs')}),'left',len(still),'hard',len(hard),flush=True)
