"""Merge the second-stage summaries (hcert_shard.py) into results/<tag>: summary.json (totals,
the largest bound, the histogram, shards missing) and left.json (polytopes still above T)
together with certs.jsonl.gz (all second-stage certificates)."""
import sys, os, json, glob, gzip
art,dst,n=sys.argv[1],sys.argv[2],int(sys.argv[3]); os.makedirs(dst,exist_ok=True)
S=[json.load(open(f)) for f in sorted(glob.glob(os.path.join(art,'**','hsummary-*.json'),recursive=True))]
hist={}; left=[]
for s in S:
    for k,v in s['hist'].items(): hist[k]=hist.get(k,0)+v
    left+=s['left']
with gzip.open(os.path.join(dst,'certs.jsonl.gz'),'wt') as fh:
    for f in sorted(glob.glob(os.path.join(art,'**','hcerts-*.jsonl'),recursive=True)):
        fh.write(open(f).read())
out=dict(T=S[0]['T'] if S else None,shards=len(S),missing=sorted(set(range(n))-{s['K'] for s in S}),
         items=sum(s['items'] for s in S),certified=sum(s['certified'] for s in S),
         max=max([s['max'] for s in S],default=0),left=len(left),
         hist={k:hist[k] for k in sorted(hist,key=int)},secs=round(sum(s['secs'] for s in S)))
json.dump(out,open(os.path.join(dst,'summary.json'),'w'),indent=1)
json.dump(left,open(os.path.join(dst,'left.json'),'w'))
print(json.dumps({k:out[k] for k in ('T','shards','items','certified','max','left')}),'missing',out['missing'])
