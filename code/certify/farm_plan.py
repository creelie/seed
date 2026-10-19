"""Matrix of the certificate farm, read by .github/workflows/farm.yml.
queue.json gives the threshold T, the number of row groups per job and optionally an explicit
list of groups (file:rowgroup); by default every row group of the Kreuzer-Skarke list is used,
with the small files of fewer than a million polytopes put together in one job."""
import json, os
here=os.path.dirname(os.path.abspath(__file__))
Q=json.load(open(os.path.join(here,'queue.json')))
RG=json.load(open(os.path.join(here,'rowgroups.json')))
per=Q.get('per_job',2)
if Q.get('groups'):
    G=Q['groups']; jobs=[','.join(G[i:i+per]) for i in range(0,len(G),per)]
else:
    small=[f'{v}:0' for v,s in RG.items() if len(s)==1]
    jobs=[','.join(small)]
    for v,s in RG.items():
        if len(s)==1: continue
        g=[f'{v}:{r}' for r in range(len(s))]
        jobs+=[','.join(g[i:i+per]) for i in range(0,len(g),per)]
part=Q.get('part')
if part is not None: jobs=jobs[part*256:(part+1)*256]
print('jobs='+json.dumps([{'k':k,'g':g} for k,g in enumerate(jobs)]))
print('T='+str(Q['T']))
print('tag='+Q['tag'])
