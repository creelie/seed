"""One job of the full replay of the certificate farm: for the row groups of index congruent to K
modulo N, every polytope of the Kreuzer-Skarke list whose pair bound exceeds T must carry a
certificate that verify_certs.replay accepts with bound at most T.

  python3 replay_shard.py ART K N T NPROC OUT
ART holds the artifacts of the first-stage runs, one directory <tag>-<job> each with the files
certs-F-R[-k].jsonl.gz written by farm_shard.py; the run tagged t50 recorded shifted cut vectors
and is replayed with legacy=True.  The second-stage certificates are read from
results/*/certs.jsonl.gz.  For each polytope the certificates are tried in the order of their
recorded bounds until one replays to at most T.  The job writes OUT/rsummary-F-R.json for each of
its row groups: the number of polytopes above T, how many are covered, the largest replayed
bound, and the polytopes with no accepted certificate (with the reasons of the failed ones)."""
import sys, os, json, glob, gzip, re, time
from multiprocessing import Pool
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import farm_shard, verify_certs, replay_fast

LEGACY={'t50'}
CH=200
TRUNCATED=[]

def lines(f):
    """the complete lines of a gzip file; a file cut off by a killed job yields the lines before
    the cut and is recorded in TRUNCATED.  Polytopes whose certificate is lost this way are not
    covered by it, so a cut can only add to the list of uncovered polytopes."""
    try:
        with gzip.open(f,'rt') as g:
            for line in g:
                if line.endswith('\n'): yield line
    except (EOFError,OSError,__import__('zlib').error):
        TRUNCATED.append(f)

def stage1(art,v,rg):
    """certificates of the first stage for row group v:rg, as row -> [(bound, cuts, legacy)]"""
    C={}
    for f in glob.glob(os.path.join(art,'*',f'certs-{v}-{rg}.jsonl.gz'))+glob.glob(os.path.join(art,'*',f'certs-{v}-{rg}-*.jsonl.gz')):
        tag=os.path.basename(os.path.dirname(f)).rsplit('-',1)[0]
        for line in lines(f):
            r,b,cuts=json.loads(line); C.setdefault(r,[]).append((b,cuts,tag in LEGACY))
    return C

def stage2(results):
    """second-stage certificates, as (file, rowgroup) -> row -> [(bound, cuts, False)]"""
    C={}
    for f in sorted(glob.glob(os.path.join(results,'*','certs.jsonl.gz'))):
        for line in lines(f):
            d=json.loads(line)
            if not d.get('cuts'): continue
            C.setdefault((d['file'],d['rowgroup']),{}).setdefault(d['row'],[]).append((d['bound'],d['cuts'],False))
    return C

def work(args):
    T,items=args
    return replay_fast.replay_chunk(T,items)

def work_single(args):
    T,items=args; out=[]
    for r,V,cands in items:
        why=[]
        for b,cuts,legacy in sorted(cands,key=lambda c:c[0]):
            if b>T: continue
            try: got,msg=verify_certs.replay(V,cuts,legacy)
            except Exception as e: got,msg=None,type(e).__name__
            if got is not None and got<=T and got<=b: out.append((r,got,None)); break
            why.append(msg if got is None else f'replayed {got} > {min(b,T)}')
        else: out.append((r,None,why or ['no certificate']))
    return out

if __name__=='__main__':
    art,K,N,T,nproc,out=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]),sys.argv[6]
    os.makedirs(out,exist_ok=True)
    here=os.path.dirname(os.path.abspath(__file__))
    RG=json.load(open(os.path.join(here,'rowgroups.json')))
    groups=[(v,r) for v,sz in RG.items() for r in range(len(sz))]
    S2=stage2(os.path.join(here,'results')); S2T=list(TRUNCATED)
    with Pool(nproc) as pool:
        for i,(v,rg) in enumerate(groups):
            if i%N!=K: continue
            t0=time.time(); nrows,items=farm_shard.read_group(v,rg,T)
            TRUNCATED.clear(); C=stage1(art,v,rg); C2=S2.get((v,rg),{})
            work_items=[(r,V,C.get(r,[])+C2.get(r,[])) for r,V,p,q in items]
            chunks=[(T,work_items[j:j+CH]) for j in range(0,len(work_items),CH)]
            covered=0; mx=0; bad=[]; hist={}
            for res in pool.imap_unordered(work,chunks):
                for r,got,why in res:
                    if got is None: bad.append(dict(row=r,why=why))
                    else: covered+=1; mx=max(mx,got); hist[got]=hist.get(got,0)+1
            s=dict(file=v,rowgroup=rg,T=T,rows=nrows,above=len(items),covered=covered,max=mx,
                   uncovered=bad,hist=hist,truncated=sorted(set(TRUNCATED+S2T)),secs=round(time.time()-t0,1))
            json.dump(s,open(os.path.join(out,f'rsummary-{v}-{rg}.json'),'w'))
            print(json.dumps({k:s[k] for k in ('file','rowgroup','rows','above','covered','max','secs')}),
                  'uncovered',len(bad),flush=True)
