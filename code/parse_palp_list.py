import sys, json
# parse PALP ascii list: header "d n  M:.. N:.. ..." then d rows of n ints (vertices as columns)
def parse(path):
    polys=[]
    with open(path) as f:
        lines=[l for l in f if l.strip()]
    i=0
    while i<len(lines):
        h=lines[i].split(); i+=1
        a,b=int(h[0]),int(h[1])
        if a<b: d,n=a,b; rows=[list(map(int,lines[i+k].split())) for k in range(d)]; i+=d
        else: n,d=a,b; rows=[list(map(int,lines[i+k].split())) for k in range(n)]; i+=n; rows=[list(c) for c in zip(*rows)]
        verts=[tuple(rows[r][c] for r in range(d)) for c in range(n)]
        polys.append({'header':' '.join(h),'verts':verts})
    return polys
if __name__=='__main__':
    p=parse(sys.argv[1]); print(len(p)); json.dump(p,open(sys.argv[2],'w'))
