"""Merge the summaries of a full replay (replay_shard.py) into results/<tag>/replay.json: the
number of polytopes above T, how many carry an accepted certificate, the largest replayed bound,
the row groups not reported, and every polytope left uncovered."""
import sys, os, json, glob
art,dst=sys.argv[1],sys.argv[2]; os.makedirs(dst,exist_ok=True)
S=[json.load(open(f)) for f in sorted(glob.glob(os.path.join(art,'**','rsummary-*.json'),recursive=True))]
RG=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'rowgroups.json')))
seen={(s['file'],s['rowgroup']) for s in S}
missing=[f'{v}:{r}' for v,sz in RG.items() for r in range(len(sz)) if (v,r) not in seen]
unc=[dict(file=s['file'],rowgroup=s['rowgroup'],**u) for s in S for u in s['uncovered']]
out=dict(T=S[0]['T'] if S else None,rowgroups=len(S),rows=sum(s['rows'] for s in S),
         above=sum(s['above'] for s in S),covered=sum(s['covered'] for s in S),
         max=max([s['max'] for s in S],default=0),missing=missing,uncovered=unc,
         secs=round(sum(s['secs'] for s in S)))
json.dump(out,open(os.path.join(dst,'replay.json'),'w'),indent=1)
print(json.dumps({k:out[k] for k in ('T','rowgroups','rows','above','covered','max')}),
      'missing',len(missing),'uncovered',len(unc))
