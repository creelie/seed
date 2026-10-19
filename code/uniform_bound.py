"""Theorem B: the explicit uniform bound for the covering depth over the whole list.
For every reflexive Delta, depth(Delta) <= min(|Delta| - 6, 680 - |Delta^*|): each cover step
adds at least one lattice point of Delta and removes at least one of Delta^*, a minimal
polytope has at least 6 points, and no reflexive 4-polytope has more than 680 points."""
import csv, sys
rows=[(int(r['points']),int(r['dual_points']),int(r['count'])) for r in csv.DictReader(open(sys.argv[1] if len(sys.argv)>1 else 'data/ks4_point_pairs.csv'))]
fails=0; passes=0
def check(name,ok):
    global fails, passes
    print(('PASS ' if ok else 'FAIL ')+name)
    if ok: passes+=1
    else: fails+=1
N=sum(c for a,b,c in rows)
check('total is 473,800,776',N==473800776)
check('point counts lie in [6,680]',min(a for a,b,c in rows)==6 and max(a for a,b,c in rows)==680)
pairs={(a,b):c for a,b,c in rows}
check('mirror symmetry: count(a,b)=count(b,a)',all(pairs.get((b,a))==c for (a,b),c in pairs.items()))
bound=lambda a,b:min(a-6,680-b)
M=max(bound(a,b) for a,b,c in rows)
check('maximum of the bound is 654',M==654)
arg=[(a,b,c) for a,b,c in rows if bound(a,b)==M]
check('attained only at (680,26), one polytope',arg==[(680,26,1)])
for X in [20,30,40,50,60,80,100,150,200,300,400,500,600]:
    print(f'  polytopes with bound > {X}: {sum(c for a,b,c in rows if bound(a,b)>X)}')
print(f'{passes} checks passed, {fails} failed')
