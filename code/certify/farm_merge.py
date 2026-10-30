"""Merge the per-row-group summaries of a farm run (farm_shard.py) into results/<tag>:
summary.json (totals, the largest bound, the histogram, row groups not finished) and left.json
(the polytopes still above the threshold, with their vertices).  A row group split into slices
k/n counts as seen when all n slices are present, and its rows are counted once."""
import sys, os, json, glob
art,dst=sys.argv[1],sys.argv[2]; os.makedirs(dst,exist_ok=True)
S=[json.load(open(f)) for f in sorted(glob.glob(os.path.join(art,'**','summary-*.json'),recursive=True))]
hist={}; left=[]; undone=[]
for s in S:
    for k,v in s['hist'].items(): hist[k]=hist.get(k,0)+v
    for d in s['left']: left.append(dict(file=s['file'],rowgroup=s['rowgroup'],**d))
    sl=s.get('slice')
    if not s['done']: undone.append(f"{s['file']}:{s['rowgroup']}"+(f"/{sl[0]}/{sl[1]}" if sl else ''))
RG=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'rowgroups.json')))
slices={}
for s in S:
    if s.get('slice'): slices.setdefault((s['file'],s['rowgroup']),set()).add(tuple(s['slice']))
seen={(s['file'],s['rowgroup']) for s in S if not s.get('slice')}
seen|={g for g,ks in slices.items() if len({k for k,n in ks})==max(n for k,n in ks)}
missing=[f'{v}:{r}' for v,sz in RG.items() for r in range(len(sz)) if (v,r) not in seen]
T=S[0]['T'] if S else None
out=dict(T=T,rowgroups=len(S),rows=sum(s['rows'] for s in S if not s.get('slice') or s['slice'][0]==0),todo=sum(s['todo'] for s in S),
         certified=sum(s['certified'] for s in S),max=max([s['max'] for s in S],default=0),
         left=len(left),max_left=max([d['bound'] or 0 for d in left],default=0),
         hist={k:hist[k] for k in sorted(hist,key=int)},undone=undone,missing=missing,
         secs=round(sum(s['secs'] for s in S)))
json.dump(out,open(os.path.join(dst,'summary.json'),'w'),indent=1)
json.dump(left,open(os.path.join(dst,'left.json'),'w'))
print(json.dumps({k:out[k] for k in ('T','rowgroups','rows','todo','certified','max','left','max_left')}))
print('undone',len(undone),'missing',len(missing))
