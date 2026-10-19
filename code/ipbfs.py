"""BFS over GL(d,Z)-classes of IP lattice polytopes obtained from a list of reflexive polytopes
by successively dropping vertices (Kreuzer-Skarke style).  Uses PALP poly.x for hulls,
IP test and normal forms.  Records: classes (normal form -> data), vertex-drop edges."""
import sys, json, subprocess, os
from palp import run_palp, key
if __name__=='__main__':
    polys=json.load(open(sys.argv[1])); out=sys.argv[2]
    d=len(polys[0]['verts'][0])
    classes={}; edges=[]  # edges: (parent key, child key)
    r0=run_palp([(d,[tuple(v) for v in p['verts']]) for p in polys])
    frontier=[]
    for r in r0:
        k=key(r['nf'])
        if k not in classes:
            classes[k]={'refl':r['refl'],'npts':r['npts'],'nv':len(r['verts']),'pts':r['pts'],'verts':r['verts']}; frontier.append(k)
    print('level0 classes',len(classes),flush=True)
    level=0
    while frontier:
        level+=1
        inputs=[]; parents=[]
        for k in frontier:
            c=classes[k]; pts=c['pts']; vs=set(c['verts'])
            for v in vs:
                child=[p for p in pts if p!=v]
                if len(child)<d+1: continue
                inputs.append((d,child)); parents.append(k)
        new=[]
        B=20000
        for s in range(0,len(inputs),B):
            res=run_palp(inputs[s:s+B])
            for pk,r in zip(parents[s:s+B],res):
                if not r['ip']: continue
                k=key(r['nf']); edges.append((pk,k))
                if k not in classes:
                    classes[k]={'refl':r['refl'],'npts':r['npts'],'nv':len(r['verts']),'pts':r['pts'],'verts':r['verts']}; new.append(k)
        print('level',level,'inputs',len(inputs),'new classes',len(new),'total',len(classes),'edges',len(edges),flush=True)
        frontier=new
    json.dump({'classes':classes,'edges':edges},open(out,'w'))
