"""Certified partial descents for the polytopes whose pair-chain bound exceeds a target T.

For each polytope Delta of the input file with L(|Delta|,|Delta^*|) > T (L from pair_chain.py),
take certified covers Delta > Gamma_1 > ... > Gamma_s with greedy.one_step (each step is a cover by
the climbing lemma) until s + L(|Gamma_s|,|Gamma_s^*|) <= T.  Every reflexive descent of Gamma_s has
length at most L(|Gamma_s|,|Gamma_s^*|), so Delta has a reflexive descent of length at most T.
If the greedy step finds no cut, complete.covers supplies all covers and the smallest is taken.

Usage: python3 certify_top.py T input.json nproc [out.jsonl]
Output: one JSON line per polytope (index, counts, dual counts, bound reached, seconds)."""
import sys, os, json, time, csv
from multiprocessing import Pool
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
import rhull, greedy, complete

L = {}
with open(os.path.join(here, 'data', 'pair_chain.csv')) as f:
    r = csv.reader(f); next(r)
    for a in r: L[(int(a[0]), int(a[1]))] = int(a[3])

def certify(verts, T):
    S = rhull.closure([tuple(v) for v in verts]); F = rhull.facets(list(S))
    assert rhull.is_reflexive(F)
    Dst, _ = greedy.dual_lattice(S, F)
    counts = [len(S)]; duals = [len(Dst)]; how = []
    while len(how) + L[(len(S), len(Dst))] > T:
        r = greedy.one_step(S, F, 3)
        if r is not None:
            S, F = r; how.append('climb')
        else:
            cv = complete.covers(S, F)
            if not cv: break
            S = min(cv, key=len); F = rhull.facets(list(S)); how.append('complete')
        Dst, _ = greedy.dual_lattice(S, F)
        counts.append(len(S)); duals.append(len(Dst))
    return counts, duals, how, len(how) + L[(len(S), len(Dst))], sorted(S)

def work(arg):
    i, p, T = arg; t = time.time()
    try:
        counts, duals, how, reached, end = certify(p['verts'], T)
        return dict(i=i, points=p['points'], dual_points=p['dual_points'], h11=p['h11'], h12=p['h12'],
                    L=L[(p['points'], p['dual_points'])], counts=counts, duals=duals, how=how,
                    reached=reached, ok=reached <= T, end=end, secs=round(time.time() - t, 2))
    except Exception as e:
        return dict(i=i, points=p['points'], dual_points=p['dual_points'], error=repr(e), ok=False)

if __name__ == '__main__':
    T = int(sys.argv[1]); P = json.load(open(sys.argv[2])); nproc = int(sys.argv[3])
    out = sys.argv[4] if len(sys.argv) > 4 else f'certify_{T}.jsonl'
    P = [p for p in P if L[(p['points'], p['dual_points'])] > T]
    P.sort(key=lambda p: (-L[(p['points'], p['dual_points'])], json.dumps(p['verts'])))
    done = set()
    if os.path.exists(out):
        for l in open(out): done.add(json.loads(l)['i'])
    todo = [(i, p, T) for i, p in enumerate(P) if i not in done]
    print('targets', len(P), 'to do', len(todo), flush=True)
    with Pool(nproc) as pool, open(out, 'a') as fh:
        for r in pool.imap_unordered(work, todo, chunksize=1):
            fh.write(json.dumps(r) + '\n'); fh.flush()
            print(r['i'], r['points'], r.get('L'), r.get('counts'), r.get('reached'), r.get('secs'),
                  r.get('error', ''), flush=True)
