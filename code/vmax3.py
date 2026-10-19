import json,sys,math
from palp import run_palp
import numpy as np
from scipy.spatial import ConvexHull
p=json.load(open('data/poset3.json'))
keys=list(p['depth'])
def pts_of(k): return [tuple(map(int,v.split(','))) for v in k.split(';')]
R=run_palp([(3,pts_of(k)) for k in keys])
vols=[round(ConvexHull(np.array(r['verts'],float)).volume*6) for r in R]
print('n',len(vols),'max nvol',max(vols))
