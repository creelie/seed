"""The two candidate enumerations agree on a sample of 3D polytopes."""
import sys, json, random
import rhull, complete
p=json.load(open('data/poset3.json'))
keys=[k for k in p['covers'] if p['covers'][k]]
random.seed(1); ks=random.sample(keys,300)
def pts_of(k): return [tuple(map(int,v.split(','))) for v in k.split(';')]
bad=0
for k in ks:
    S=rhull.closure(pts_of(k)); F=rhull.facets(list(S))
    V,Dst,w=complete.dual_points_and_weights(S,F)
    a=sorted(complete.candidate_cuts(S,F,V,Dst,w,3)); b=complete.candidate_cuts_subsets(S,F,V,Dst,w,3)
    if a!=b: bad+=1
print('disagreements',bad,'of',len(ks))
