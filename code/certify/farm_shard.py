"""One job of the certificate farm: certify every reflexive 4-polytope of some row groups of the
Kreuzer-Skarke list (the Hugging Face copy calabi-yau-data/polytopes-4d) whose pair bound L
exceeds T, by chains of cuts (bcert.py).

  python3 farm_shard.py GROUPS T NPROC BUDGET OUTDIR
GROUPS is a comma-separated list file:rowgroup, e.g. 13:0,13:1.  Polytopes left above T by the
fast search are searched again with every cut at each step.  For each row group the job writes
OUTDIR/summary-F-R.json (counts, largest bound, histogram, the polytopes left above T) and
OUTDIR/certs-F-R.jsonl.gz (one line [row, bound, cut vectors] per certified polytope).
BUDGET is in seconds; a row group not finished in time is marked done=false."""
import sys, os, json, gzip, time, csv
from multiprocessing import Pool
import numpy as np, fsspec, pyarrow.parquet as pq, pyarrow.compute as pc, pyarrow as pa
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import bcert
URL='https://huggingface.co/datasets/calabi-yau-data/polytopes-4d/resolve/main/polytopes-4d-{v}-vertices.parquet'
CH=40
SECOND=1800   # seconds per row group for the second, exhaustive search

def work(args):
    T,full,items=args
    if full: res=bcert.certify_chunk([(V,p,q) for _,V,p,q in items],T,batch=10**6,maxsteps=80)
    else: res=bcert.certify_chunk([(V,p,q) for _,V,p,q in items],T)
    return [(r,b,[list(x[3]) for x in pth[1:]],V,p,q) for (r,V,p,q),(b,pth) in zip(items,res)]

def read_group(v,rg,T):
    for a in range(6):
        try:
            with fsspec.open(URL.format(v=v),'rb',block_size=1<<23) as fh:
                t=pq.ParquetFile(fh).read_row_group(rg,columns=['vertices','point_count','dual_point_count'])
            break
        except Exception as e:
            print('read retry',v,rg,repr(e),flush=True); time.sleep(20*(a+1))
    else: raise RuntimeError('cannot read %s:%d'%(v,rg))
    p=t.column('point_count').to_numpy().astype(np.int64); q=t.column('dual_point_count').to_numpy().astype(np.int64)
    L=LT[p,q]
    rows=np.nonzero(L>T)[0]
    V=t.column('vertices').take(pa.array(rows)).to_pylist()
    items=[(int(r),V[k],int(p[r]),int(q[r])) for k,r in enumerate(rows)]
    items.sort(key=lambda x:-LT[x[2],x[3]])
    return len(p),items

LT=np.full((1200,1200),bcert.BIG,dtype=np.int64)
for (a,b),l in bcert.Lpair.items(): LT[a,b]=l

if __name__=='__main__':
    groups=[(g.split(':')[0],int(g.split(':')[1])) for g in sys.argv[1].split(',') if g]
    T=int(sys.argv[2]); nproc=int(sys.argv[3]); budget=float(sys.argv[4]); out=sys.argv[5]
    os.makedirs(out,exist_ok=True); t0=time.time()
    pool=Pool(nproc)
    if True:
        for v,rg in groups:
            t1=time.time(); nrows,items=read_group(v,rg,T)
            chunks=[(T,False,items[i:i+CH]) for i in range(0,len(items),CH)]
            hist={}; mx=0; ndone=0; left=[]; done=True
            with gzip.open(os.path.join(out,f'certs-{v}-{rg}.jsonl.gz'),'wt') as fh:
                for res in pool.imap_unordered(work,chunks):
                    for r,b,cut,V,p,q in res:
                        if b>T: left.append((r,V,p,q,b,cut)); continue
                        fh.write(json.dumps([r,b,cut])+'\n'); hist[b]=hist.get(b,0)+1; mx=max(mx,b); ndone+=1
                    if time.time()-t0>budget: done=False; pool.terminate(); break
                if done and left:
                    t2=time.time(); first={x[0]:x for x in left}; again=[(T,True,[x[:4] for x in left[i:i+4]]) for i in range(0,len(left),4)]; left=[]; seen=0
                    for res in pool.imap(work,again):
                        seen+=1
                        for r,b,cut,V,p,q in res:
                            if b>T: left.append(dict(row=r,bound=b,cuts=cut,verts=V,points=p,dual_points=q)); continue
                            fh.write(json.dumps([r,b,cut])+'\n'); hist[b]=hist.get(b,0)+1; mx=max(mx,b); ndone+=1
                        if time.time()-t2>SECOND or time.time()-t0>budget: break
                    for c in again[seen:]:
                        left+=[dict(row=r,bound=first[r][4],cuts=first[r][5],verts=V,points=p,dual_points=q) for r,V,p,q in c[2]]
                    if seen<len(again): pool.terminate(); pool=Pool(nproc)
                else: left=[dict(row=r,bound=b,cuts=cut,verts=V,points=p,dual_points=q) for r,V,p,q,b,cut in left]
            s=dict(file=v,rowgroup=rg,T=T,rows=nrows,todo=len(items),certified=ndone,max=mx,
                   hist={str(k):hist[k] for k in sorted(hist)},left=left,done=done,secs=round(time.time()-t1,1))
            json.dump(s,open(os.path.join(out,f'summary-{v}-{rg}.json'),'w'))
            print(json.dumps({k:s[k] for k in ('file','rowgroup','rows','todo','certified','max','done','secs')}),
                  'left',len(left),flush=True)
            if not done: break
    pool.terminate()
