"""Thin wrapper around PALP's poly.x (Kreuzer and Skarke): convex hulls, lattice points,
the interior-point test, reflexivity and GL(d,Z) normal forms of lattice polytopes.
Set PALP to the path of poly.x, or put poly.x in ./palp/."""
import os, subprocess
P=os.environ.get('PALP',os.path.join(os.path.dirname(os.path.abspath(__file__)),'palp','poly.x'))
def run_palp(inputs):
    """inputs: list of (d, list of points).  Returns list of dicts."""
    buf=[]
    for d,pts in inputs:
        buf.append(f"{d} {len(pts)}")
        for k in range(d): buf.append(' '.join(str(p[k]) for p in pts))
    out=subprocess.run([P,'-gIvpN'],input='\n'.join(buf)+'\n',capture_output=True,text=True).stdout
    res=[]; cur=None; lines=out.split('\n'); i=0
    def readmat(hdr):
        nonlocal i
        a,b=int(hdr[0]),int(hdr[1])
        if a<=b:
            d,n=a,b; rows=[list(map(int,lines[i+1+k].split())) for k in range(d)]; i+=1+d
            return [tuple(rows[r][c] for r in range(d)) for c in range(n)]
        n,d=a,b; rows=[list(map(int,lines[i+1+k].split())) for k in range(n)]; i+=1+n
        return [tuple(r) for r in rows]
    while i<len(lines):
        l=lines[i]
        if l.startswith('M:'):
            cur={'hdr':l,'ip':True,'refl':' N:' in l,'npts':int(l.split()[0][2:])}; res.append(cur); i+=1
        elif l.startswith('No IP'): cur['ip']=False; i+=1
        elif 'Points of P' in l: cur['pts']=readmat(l.split())
        elif 'Vertices of P' in l: cur['verts']=readmat(l.split())
        elif 'Normal form' in l: cur['nf']=readmat(l.split())
        else: i+=1
    assert len(res)==len(inputs),(len(res),len(inputs),out[:500])
    return res
def key(nf): return ';'.join(','.join(map(str,v)) for v in nf)
