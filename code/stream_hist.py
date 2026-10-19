"""Histogram of (number of lattice points of Delta, number of lattice points of Delta^*) over
all 473,800,776 reflexive 4-polytopes of Kreuzer and Skarke, read from the Hugging Face
dataset calabi-yau-data/polytopes-4d (one parquet file per vertex count).  Files are
downloaded into $HF4D (default ./hf4d) and deleted after use unless KEEP=1.
Writes data/ks4_point_pairs.csv with one line per pair that occurs."""
import os, subprocess
import numpy as np
import pyarrow.parquet as pq
URL='https://huggingface.co/datasets/calabi-yau-data/polytopes-4d/resolve/main/polytopes-4d-{v}-vertices.parquet'
root=os.environ.get('HF4D','hf4d'); os.makedirs(root,exist_ok=True)
H=np.zeros((700,700),dtype=np.int64)
for v in [f'{n:02d}' for n in list(range(5,34))+[36]]:
    fn=os.path.join(root,f'polytopes-4d-{v}-vertices.parquet')
    if not os.path.exists(fn):
        subprocess.run(['curl','-sSL','--retry','5','-o',fn,URL.format(v=v)],check=True)
    f=pq.ParquetFile(fn)
    for rg in range(f.num_row_groups):
        t=f.read_row_group(rg,columns=['point_count','dual_point_count'])
        np.add.at(H,(t.column('point_count').to_numpy(),t.column('dual_point_count').to_numpy()),1)
    if os.environ.get('KEEP')!='1': os.remove(fn)
    print('vertices',v,'running total',int(H.sum()),flush=True)
a,b=np.nonzero(H)
with open('data/ks4_point_pairs.csv','w') as out:
    out.write('points,dual_points,count\n')
    for i,j in zip(a,b): out.write(f'{i},{j},{H[i,j]}\n')
print('done',int(H.sum()))
