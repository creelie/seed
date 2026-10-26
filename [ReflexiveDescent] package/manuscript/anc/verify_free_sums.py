"""Exact integer checks, no third-party dependencies and no floating hulls.

Two independently implemented polygon enumerators establish the finite base
cases. The geometric free-sum theorem is proved in the accompanying text;
the product-graph calculation is only a separate combinatorial control.
"""
from pathlib import Path
from itertools import combinations, product
from collections import Counter
from math import gcd, comb, factorial
import json

ROOT=Path(__file__).resolve().parent
ORIGIN=(0,0)
TPTS=tuple((x,y) for x,y in product(range(-1,3),repeat=2) if x+y<=1)
BPTS=((-1,-1),(-1,0),(0,-1),(0,0),(0,1),(1,0))

def cross(a,b,p):
    return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])

def hull(points):
    points=sorted(set(points))
    if len(points)<3:return None
    low=[];high=[]
    for p in points:
        while len(low)>1 and cross(low[-2],low[-1],p)<=0:low.pop()
        low.append(p)
    for p in reversed(points):
        while len(high)>1 and cross(high[-2],high[-1],p)<=0:high.pop()
        high.append(p)
    result=tuple(low[:-1]+high[:-1])
    return result if len(result)>2 else None

def inside(poly,p,strict=False):
    return all(cross(a,b,p)>(0 if strict else -1)
               for a,b in zip(poly,poly[1:]+poly[:1]))

def reflexive(poly):
    return all(cross(a,b,ORIGIN)==gcd(abs(b[0]-a[0]),abs(b[1]-a[1]))
               for a,b in zip(poly,poly[1:]+poly[:1]))

def hull_enumeration(points):
    boundary=tuple(p for p in points if p!=ORIGIN);polys={}
    for mask in range(1<<len(boundary)):
        h=hull(p for i,p in enumerate(boundary) if mask>>i&1)
        if h is None or not inside(h,ORIGIN,True):continue
        assert reflexive(h)
        closed=frozenset(p for p in points if inside(h,p))
        key=sum(1<<i for i,p in enumerate(boundary) if p in closed)
        polys[key]=h
    return boundary,polys

def support_enumeration(points):
    """Check closed subsets via all supporting directed pairs; no hull call."""
    boundary=tuple(p for p in points if p!=ORIGIN);valid=[]
    for mask in range(1<<len(boundary)):
        selected=[p for i,p in enumerate(boundary) if mask>>i&1]
        if not any(cross(a,b,c)!=0 for a,b,c in combinations(selected,3)):continue
        edges=[(a,b) for a in selected for b in selected if a!=b
               and all(cross(a,b,c)>=0 for c in selected)]
        if not edges:continue
        if any(cross(a,b,ORIGIN)!=gcd(abs(b[0]-a[0]),abs(b[1]-a[1]))
               for a,b in edges):continue
        if any(all(cross(a,b,p)>=0 for a,b in edges) for i,p in enumerate(boundary)
               if not(mask>>i&1)):continue
        valid.append(mask)
    return valid

def certificate(points):
    boundary,polys=hull_enumeration(points);masks=sorted(polys)
    assert masks==support_enumeration(points)
    rows={}
    for mask in masks:
        lower=[q for q in masks if q!=mask and q&mask==q]
        covers=[q for q in lower if not any(q!=p and q&p==q for p in lower)]
        profile=Counter({0:1}) if not covers else Counter()
        for q in covers:
            for length,count in rows[q]['profile'].items():profile[length+1]+=count
        rows[mask]={'mask':mask,'vertices':polys[mask],
          'points':[ORIGIN]+[p for i,p in enumerate(boundary) if mask>>i&1],
          'covers':covers,'depth':min(profile),'height':max(profile),
          'profile':dict(sorted(profile.items()))}
    root=(1<<len(boundary))-1
    return {'boundary_point_order':boundary,'subsets_checked':1<<len(boundary),
      'root':root,'root_data':rows[root],'nodes':[rows[m] for m in masks]}

def main():
    T=certificate(TPTS);B=certificate(BPTS)
    assert len(T['nodes'])==79
    assert (T['root_data']['depth'],T['root_data']['height'])==(5,6)
    assert (B['root_data']['depth'],B['root_data']['height'])==(1,2)
    for c in [T,B]:
        lookup={x['mask']:x for x in c['nodes']}
        assert all(len(x['points'])-len(lookup[y]['points'])==1
                   for x in c['nodes'] for y in x['covers'])
    # A 4D check with explicit inequalities, unrelated to polygon hull code.
    gauge=lambda x,y:max(-x,-y,x+y)
    four={p for p in product(range(-1,3),repeat=4) if gauge(*p[:2])+gauge(*p[2:])<=1}
    expected={p+(0,0) for p in TPTS}|{(0,0)+p for p in TPTS}
    assert four==expected and len(four)==19
    # Compute shortest and longest paths on the Cartesian cover graph.
    lookup={x['mask']:x for x in T['nodes']};dp={}
    pairs=sorted(product(lookup,repeat=2),key=lambda ab:ab[0]+ab[1])
    for a,b in pairs:
        neighbors=[(x,b) for x in lookup[a]['covers']]+[(a,y) for y in lookup[b]['covers']]
        dp[a,b]=(0,0) if not neighbors else (1+min(dp[n][0] for n in neighbors),1+max(dp[n][1] for n in neighbors))
    assert dp[T['root'],T['root']]==(10,12)
    assert len(dp)==79**2
    c5=T['root_data']['profile'][5];c6=T['root_data']['profile'][6]
    assert c5>0 and c6>0
    report={'triangle_subsets_checked':512,'triangle_reflexive_subpolytopes':79,
      'triangle_depth':5,'triangle_height':6,'triangle_chain_profile':T['root_data']['profile'],
      'pentagon_subsets_checked':32,'pentagon_reflexive_subpolytopes':len(B['nodes']),
      'pentagon_depth':1,'pentagon_height':2,'pentagon_chain_profile':B['root_data']['profile'],
      'independent_enumerators_agree':True,'four_dimensional_lattice_points':19,
      'product_graph_nodes':len(dp),'product_root_depth':10,'product_root_height':12,
      'triangle_minimal_masks':[x['mask'] for x in T['nodes'] if not x['covers']],
      'triangle_depth_histogram':dict(sorted(Counter(x['depth'] for x in T['nodes']).items())),
      'method':'two exact integer enumerators; no floating point, external database or imported certificate',
      'sharp_D4_determined':False,'new_Lean_formalization':False}
    (ROOT/'triangle-certificate.json').write_text(json.dumps(T,indent=2)+'\n',encoding='utf8',newline='\n')
    (ROOT/'pentagon-certificate.json').write_text(json.dumps(B,indent=2)+'\n',encoding='utf8',newline='\n')
    (ROOT/'free-sum-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
