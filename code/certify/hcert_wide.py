"""Last pass of the second stage: the polytopes that hcert_shard.py could not finish within its
memory limit.  The beam search of hcert.py is run with wider beams, (3,30) up to (256,1600) and
up to 80 steps, using only the cuts of 3 Delta*; a polytope still above T is then searched with
the full set of cuts (complete.candidate_cuts, enumerated one plane of the box at a time).

  python3 hcert_wide.py LEFT T NPROC MEM_GB OUT
writes OUT/certs.jsonl (vertices, bound and cuts of every polytope certified at T, in the format
read by verify_certs.py) and OUT/summary.json."""
import sys, os, json, time, resource
from multiprocessing import Pool
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import hcert

WIDE=((3,30),(8,60),(16,120),(32,240),(64,400),(128,800),(256,1600))

def init(mem_gb):
    lim=int(mem_gb*2**30); resource.setrlimit(resource.RLIMIT_AS,(lim,lim))

def work(args):
    T,d=args; t=time.time(); best=None
    try:
        for full in (False,True):
            for beam,tries in (WIDE if not full else WIDE[:4]):
                b=hcert.certify(d['verts'],T,beam=beam,tries=tries,maxsteps=80,full=full)
                if best is None or b[0]<best[0]: best=b
                if best[0]<=T: return d,best,round(time.time()-t),''
        return d,best,round(time.time()-t),''
    except Exception as e:
        return d,best,round(time.time()-t),type(e).__name__

if __name__=='__main__':
    left,T,nproc,mem_gb,out=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),float(sys.argv[4]),sys.argv[5]
    os.makedirs(out,exist_ok=True); L=json.load(open(left)); still=[]; hist={}
    with Pool(nproc,init,(mem_gb,),maxtasksperchild=1) as pool, open(os.path.join(out,'certs.jsonl'),'w') as fh:
        for d,b,dt,why in pool.imap_unordered(work,[(T,d) for d in L]):
            bound=b[0] if b else d['bound']
            print(d['file'],d['rowgroup'],d['row'],d['bound'],'->',bound,dt,why,flush=True)
            if bound<=T:
                fh.write(json.dumps(dict(file=d['file'],rowgroup=d['rowgroup'],row=d['row'],verts=d['verts'],bound=bound,cuts=b[1]))+'\n')
                hist[bound]=hist.get(bound,0)+1
            else: still.append(dict(d,bound=bound,reason=why))
    s=dict(T=T,items=len(L),certified=len(L)-len(still),max=max(hist,default=0),
           hist={str(k):hist[k] for k in sorted(hist)},left=still)
    json.dump(s,open(os.path.join(out,'summary.json'),'w'),indent=1)
    print(json.dumps({k:s[k] for k in ('T','items','certified','max')}),'left',len(still))
