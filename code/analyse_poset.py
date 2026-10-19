import json, sys
from collections import defaultdict
D=json.load(open(sys.argv[1])); C=D['classes']; E=D['edges']
keys=list(C); idx={k:i for i,k in enumerate(keys)}
refl=[C[k]['refl'] for k in keys]; npts=[C[k]['npts'] for k in keys]
rk=[i for i in range(len(keys)) if refl[i]]; rpos={i:j for j,i in enumerate(rk)}
ch=defaultdict(set)
for a,b in E:
    if a!=b: ch[idx[a]].add(idx[b])
# reachable reflexive set as bitmask; process nodes by increasing npts (children have fewer points)
order=sorted(range(len(keys)),key=lambda i:npts[i])
R=[0]*len(keys)
for i in order:
    m=0
    for j in ch[i]:
        m|=R[j]
        if refl[j]: m|=1<<rpos[j]
    R[i]=m
# covers and depth among reflexive classes
depth={}; height={}; covers={}
for i in sorted(rk,key=lambda i:npts[i]):
    m=R[i]; below=[rk[b] for b in range(len(rk)) if m>>b&1]
    sub=0
    for j in below: sub|=R[j]
    cov=[j for j in below if not (sub>>rpos[j]&1)]
    covers[i]=cov
    depth[i]=0 if not cov else 1+min(depth[j] for j in cov)
    height[i]=0 if not cov else 1+max(height[j] for j in cov)
mins=[i for i in rk if not covers[i]]
maxs=[] if len(sys.argv)>3 else [i for i in rk if not any((R[j]>>rpos[i]&1) for j in rk)]
print('IP classes',len(keys),'reflexive',len(rk))
print('minimal reflexive',len(mins),'maximal reflexive',len(maxs))
from collections import Counter
print('depth distribution',sorted(Counter(depth.values()).items()))
print('height distribution',sorted(Counter(height.values()).items()))
print('max depth D3 =',max(depth.values()),'max height =',max(height.values()))
print('cover count distribution', sorted(Counter(len(covers[i]) for i in rk).items())[:30])
deep=[i for i in rk if depth[i]==max(depth.values())]
for i in deep[:10]: print('deep',keys[i],npts[i],C[keys[i]]['nv'])
print('minimal elements:'); 
for i in mins: print(' ',keys[i],'npts',npts[i],'nv',C[keys[i]]['nv'])
json.dump({'depth':{keys[i]:depth[i] for i in rk},'height':{keys[i]:height[i] for i in rk},'covers':{keys[i]:[keys[j] for j in covers[i]] for i in rk},'mins':[keys[i] for i in mins],'maxs':[keys[i] for i in maxs]},open(sys.argv[2],"w"))
