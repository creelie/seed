"""Figures of the paper.  Run from paper/figures/src:  python3 make_figures.py
Reads ../../../code/data and writes flattened 256-colour PNGs into paper/figures."""
import json, os, sys, csv, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly
from matplotlib.colors import LogNorm, ListedColormap
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
DATA = os.path.join(HERE, '..', '..', '..', 'code', 'data')
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['DejaVu Serif'], 'mathtext.fontset': 'dejavuserif',
                     'font.size': 9, 'axes.linewidth': 0.7, 'xtick.major.width': 0.6, 'ytick.major.width': 0.6})
DEPTHCOL = ['#1b3a5c', '#2a6f97', '#3f9c8f', '#8cbf5a', '#e0b23a', '#d0583a']

def save(fig, name, width_px=1600):
    w_in = fig.get_size_inches()[0]
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=width_px / w_in, facecolor='white')
    plt.close(fig)
    im = Image.open(p).convert('RGB')
    im = im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(p, optimize=True)
    print('wrote', p, Image.open(p).size)

def pts_of(k): return [tuple(map(int, v.split(','))) for v in k.split(';')]

def hull_order(V):
    c = np.mean(np.array(V, float), axis=0)
    return sorted(V, key=lambda p: math.atan2(p[1] - c[1], p[0] - c[0]))

def reduce2(V):
    best=None
    for a in range(-3,4):
        for b in range(-3,4):
            for c in range(-3,4):
                for d in range(-3,4):
                    if abs(a*d-b*c)!=1: continue
                    W=[(a*x+b*y,c*x+d*y) for x,y in V]
                    W=[(x-0,y-0) for x,y in W]
                    key=(max(max(abs(x),abs(y)) for x,y in W), sum(x*x+y*y for x,y in W), -sum(y for x,y in W))
                    if best is None or key<best[0]: best=(key,W)
    return best[1]

def lattice_in(V):
    V = hull_order(V); P = np.array(V)
    out = []
    for x in range(P[:, 0].min(), P[:, 0].max() + 1):
        for y in range(P[:, 1].min(), P[:, 1].max() + 1):
            ok = True
            for i in range(len(V)):
                a, b = V[i], V[(i + 1) % len(V)]
                if (b[0] - a[0]) * (y - a[1]) - (b[1] - a[1]) * (x - a[0]) < 0: ok = False; break
            if ok: out.append((x, y))
    return out

# ---------------------------------------------------------------- Hasse diagram, d = 2
def fig_hasse2():
    P = json.load(open(os.path.join(DATA, 'poset2.json')))
    rows = {10: ['1,0;1,3;-2,-3'],
            9: ['1,0;1,2;-1,-2;-1,0', '1,0;0,1;-2,1;1,-2', '1,0;1,2;-3,-2'],
            8: ['1,0;0,1;-1,1;1,-1;-1,-1', '1,0;0,1;-1,1;-1,-2'],
            7: ['1,0;0,1;1,-1;-1,1;0,-1;-1,0', '1,0;0,1;0,-1;-1,1;-1,-1', '1,0;0,1;0,-1;-2,1', '1,0;0,1;-3,-2'],
            6: ['1,0;0,1;0,-1;-1,0;1,1', '1,0;0,1;-1,-1;-1,1'],
            5: ['1,0;0,1;0,-1;-1,0', '1,0;-1,0;0,1;1,-1', '1,0;0,1;-2,-1'],
            4: ['1,0;0,1;-1,-1']}
    pos = {}
    for n, ks in rows.items():
        for i, k in enumerate(ks):
            pos[k] = ((i - (len(ks) - 1) / 2) * 2.35, (n - 4) * 2.05)
    fig, ax = plt.subplots(figsize=(3.4, 4.6))
    for k, cv in P['covers'].items():
        for c in cv:
            (x0, y0), (x1, y1) = pos[k], pos[c]
            ax.plot([x0, x1], [y0, y1], color='#9a9a9a', lw=0.8, zorder=1)
    for k, (x, y) in pos.items():
        V = reduce2(pts_of(k)); d = P['depth'][k]
        Vc = np.array(V, float); s = 0.72 / max(1.0, np.linalg.norm(Vc, axis=1).max())
        circ = plt.Circle((x, y), 0.86, facecolor='white', edgecolor=DEPTHCOL[d],
                          lw=2.0 if not P['covers'][k] else 1.1, zorder=2)
        ax.add_patch(circ)
        H = np.array(hull_order(V), float) * s + [x, y]
        ax.add_patch(MPoly(H, closed=True, facecolor=DEPTHCOL[d], alpha=0.35, edgecolor=DEPTHCOL[d], lw=0.8, zorder=3))
        L = np.array(lattice_in(V), float) * s + [x, y]
        ax.scatter(L[:, 0], L[:, 1], s=2.2, color='black', zorder=4, linewidths=0)
        ax.text(x + 0.98, y + 0.62, str(d), fontsize=7, color=DEPTHCOL[d], ha='center', va='center', zorder=5,
                fontweight='bold')
    for n in rows:
        ax.text(-4.75, (n - 4) * 2.05, f'{n}', fontsize=7.5, ha='center', va='center', color='#444444')
    ax.text(-4.75, 6 * 2.05 + 1.15, 'points', fontsize=7.5, ha='center', color='#444444')
    ax.set_xlim(-5.3, 4.9); ax.set_ylim(-1.1, 13.6); ax.set_aspect('equal'); ax.axis('off')
    fig.tight_layout(pad=0.1)
    save(fig, 'fig_hasse2.png', 1100)

# ---------------------------------------------------------------- the cut lemma in the plane
def fig_cut():
    fig, axs = plt.subplots(1, 2, figsize=(3.4, 1.85))
    D = [(-1, -1), (2, -1), (-1, 2)]; q = (-1, 0)
    ax = axs[0]
    ax.add_patch(MPoly(np.array(D), closed=True, facecolor='#d9e6f2', edgecolor='#1b3a5c', lw=1.0))
    G = [(-1, -1), (1, -1), (1, 0), (-1, 2)]
    ax.add_patch(MPoly(np.array(G), closed=True, facecolor='#3f9c8f', alpha=0.45, edgecolor='#2a6f97', lw=1.0))
    ax.plot([1, 1], [-1.6, 2.4], color='#d0583a', lw=1.0, ls='--')
    for p in lattice_in(D):
        ax.plot(*p, 'o', ms=2.6, color='black' if p != (2, -1) else '#d0583a')
    ax.text(1.12, 2.0, r'$\langle x,q\rangle=-1$', fontsize=6.5, color='#d0583a')
    ax.text(-0.85, -0.55, r'$\Gamma$', fontsize=8, color='#1b3a5c')
    ax.text(1.55, -0.75, r'$\Delta$', fontsize=8, color='#1b3a5c')
    ax.set_xlim(-1.6, 2.6); ax.set_ylim(-1.6, 2.6); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(r'$M_\mathbb{R}$', fontsize=8, pad=1)
    ax = axs[1]
    Ds = [(0, 1), (1, 0), (-1, -1)]; Gs = [(0, 1), (1, 0), (-1, -1), (-1, 0)]
    ax.add_patch(MPoly(np.array(hull_order(Gs)), closed=True, facecolor='#3f9c8f', alpha=0.45, edgecolor='#2a6f97', lw=1.0))
    ax.add_patch(MPoly(np.array(Ds), closed=True, facecolor='#d9e6f2', edgecolor='#1b3a5c', lw=1.0))
    for x in range(-2, 3):
        for y in range(-2, 3):
            ax.plot(x, y, 'o', ms=1.2, color='#bbbbbb')
    for p in [(0, 1), (1, 0), (-1, -1), (0, 0)]:
        ax.plot(*p, 'o', ms=2.6, color='black')
    ax.plot(*q, 'o', ms=3.2, color='#d0583a')
    ax.text(-1.55, 0.15, r'$q$', fontsize=8, color='#d0583a')
    ax.text(0.25, 0.05, r'$\Delta^*$', fontsize=7.5, color='#1b3a5c')
    ax.text(-1.0, 0.6, r'$\Gamma^*$', fontsize=7.5, color='#2a6f97')
    ax.set_xlim(-2.2, 2.2); ax.set_ylim(-2.2, 2.2); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(r'$N_\mathbb{R}$', fontsize=8, pad=1)
    fig.tight_layout(pad=0.2)
    save(fig, 'fig_cut.png', 1300)

# ---------------------------------------------------------------- point pairs of the four-dimensional list
def fig_pairs():
    H = np.zeros((700, 700)); Lb = {}
    for r in csv.DictReader(open(os.path.join(DATA, 'pair_chain.csv'))):
        p, q = int(r['points']), int(r['dual_points'])
        H[p, q] = int(r['count']); Lb[(p, q)] = int(r['L'])
    ch = json.load(open(os.path.join(DATA, 'pair_chain_witness.json')))
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.9), gridspec_kw={'width_ratios': [1.15, 1]})
    ax = axs[0]
    Hm = np.ma.masked_where(H == 0, H)
    im = ax.imshow(Hm.T, origin='lower', norm=LogNorm(vmin=1, vmax=H.max()), cmap='viridis',
                   extent=(-0.5, 699.5, -0.5, 699.5), interpolation='nearest')
    cx = [c[0] for c in ch]; cy = [c[1] for c in ch]
    ax.step(cx, cy, where='post', color='#d0583a', lw=0.9)
    ax.plot([521], [22], 'o', ms=3, color='#d0583a')
    ax.plot([680], [26], 's', ms=3, color='white', mec='#d0583a', mew=0.8)
    mid = ch[len(ch) // 2]
    ax.annotate('longest pair chain\n(348 steps)', xy=(mid[0], mid[1]), xytext=(390, 470), fontsize=7.5,
                color='#d0583a', arrowprops=dict(arrowstyle='-', color='#d0583a', lw=0.6))
    ax.annotate(r'$\Delta_{680}$', xy=(676, 32), xytext=(600, 150), fontsize=8, color='#d0583a',
                arrowprops=dict(arrowstyle='-', color='#d0583a', lw=0.6))
    ax.set_xlim(0, 700); ax.set_ylim(0, 700)
    ax.set_xlabel(r'lattice points of $\Delta$'); ax.set_ylabel(r'lattice points of $\Delta^*$')
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.02); cb.set_label('polytopes', fontsize=8)
    cb.ax.tick_params(labelsize=7)
    ax = axs[1]
    a, b = np.nonzero(H)
    w = H[a, b].astype(np.int64)
    for vals, col, lab in ((np.minimum(a - 6, 680 - b), '#9aa7b4', 'min bound'),
                           (np.array([Lb[(x, y)] for x, y in zip(a, b)]), '#1b3a5c', 'pair bound')):
        cnt = np.zeros(656, dtype=np.int64); np.add.at(cnt, vals, w)
        tail = cnt[::-1].cumsum()[::-1]
        m = tail > 0
        ax.semilogy(np.arange(656)[m], tail[m], color=col, lw=1.2, label=lab)
    ax.axvline(348, color='#d0583a', lw=0.6, ls='--'); ax.axvline(654, color='#cccccc', lw=0.6, ls='--')
    ax.set_xlabel('bound on the length of a descent')
    ax.set_ylabel('polytopes with at least this bound')
    ax.legend(fontsize=7.5, frameon=False, loc='upper right', borderaxespad=0.2)
    ax.set_xlim(0, 670)
    fig.tight_layout(pad=0.3)
    save(fig, 'fig_pairs.png', 1600)

# ---------------------------------------------------------------- depths in dimension three
def fig_depth3():
    P = json.load(open(os.path.join(DATA, 'poset3.json')))
    import itertools
    sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'code'))
    dep = P['depth']; hei = P['height']
    hist = np.bincount(list(dep.values()))
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.4))
    ax = axs[0]
    ax.bar(np.arange(len(hist)), hist, color=[DEPTHCOL[min(5, i // 2)] for i in range(len(hist))], width=0.8)
    for i, h in enumerate(hist):
        ax.text(i, h + 12, str(h), ha='center', fontsize=6.5)
    ax.set_xlabel('transition depth'); ax.set_ylabel('reflexive 3-polytopes'); ax.set_xticks(range(len(hist)))
    ax.set_ylim(0, hist.max() * 1.12)
    ax = axs[1]
    D = np.array([dep[k] for k in dep]); Hh = np.array([hei[k] for k in dep])
    M = np.zeros((D.max() + 1, Hh.max() + 1))
    np.add.at(M, (D, Hh), 1)
    Mm = np.ma.masked_where(M == 0, M)
    im = ax.imshow(Mm.T, origin='lower', aspect='auto', cmap='viridis', norm=LogNorm(vmin=1, vmax=M.max()),
                   extent=(-0.5, D.max() + 0.5, -0.5, Hh.max() + 0.5), interpolation='nearest')
    ax.plot([0, D.max()], [0, D.max()], color='#d0583a', lw=0.7, ls='--')
    ax.set_xlabel('shortest descent (depth)'); ax.set_ylabel('longest descent (height)')
    cb = fig.colorbar(im, ax=ax, fraction=0.05, pad=0.02); cb.set_label('polytopes', fontsize=8); cb.ax.tick_params(labelsize=7)
    fig.tight_layout(pad=0.3)
    save(fig, 'fig_depth3.png', 1600)

# ---------------------------------------------------------------- the descent of the largest polytope
def fig_chain680():
    sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'code'))
    import rhull
    ch = json.load(open(os.path.join(DATA, 'chain680.json')))
    n = []; nd = []
    for S in ch:
        S = frozenset(tuple(x) for x in S); F = rhull.facets(list(S))
        A = np.array([a for a, c in F]); box = [(int(A[:, i].min()), int(A[:, i].max())) for i in range(4)]
        n.append(len(S)); nd.append(len(rhull.lattice_points_H([(v, -1) for v in rhull.vertices(S, F)], box)))
    json.dump({'points': n, 'dual_points': nd}, open(os.path.join(DATA, 'chain680_counts.json'), 'w'))
    k = np.arange(len(n))
    fig, ax = plt.subplots(figsize=(3.4, 2.35))
    ax.semilogy(k, n, 'o-', ms=2.6, lw=1.0, color='#1b3a5c', label=r'$|\Gamma_i\cap M|$')
    ax.semilogy(k, nd, 's-', ms=2.4, lw=1.0, color='#d0583a', label=r'$|\Gamma_i^*\cap N|$')
    c22 = descent22()[0]
    ax.semilogy(range(10, 33), [len(rhull.closure(V)) for _, V in c22], ls=(0, (2, 1.5)), lw=1.1,
                color='#3f9c8f', label='shortest from step 10: dual')
    ax.semilogy([32], [15], 'D', ms=3.4, color='#3f9c8f', label='its r-minimal end, 15 points')
    ax.semilogy([32], [288], 'D', ms=3.4, color='#3f9c8f', mfc='white')
    ax.annotate('22 steps', xy=(25, 120), xytext=(16.5, 330), fontsize=7, color='#3f9c8f',
                arrowprops=dict(arrowstyle='-', color='#3f9c8f', lw=0.6))
    ax.axvline(10, color='#cccccc', lw=0.6, zorder=0)
    ax.text(4.5, 900, 'climb', fontsize=7, ha='center', color='#444444')
    ax.text(24, 900, 'complete covers', fontsize=7, ha='center', color='#444444')
    ax.set_xlabel('step $i$'); ax.set_ylabel('lattice points'); ax.set_ylim(2.5, 2000); ax.set_xlim(-1, 39)
    ax.legend(fontsize=6.5, frameon=False, loc='lower left')
    fig.tight_layout(pad=0.3)
    save(fig, 'fig_chain680.png', 1300)
    return n, nd

def descent22():
    """Shortest descents of P_1 and P_2 from data/depth22.json.gz: lists of (points, dual points)."""
    import gzip
    sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'code'))
    import rhull
    D = json.load(gzip.open(os.path.join(DATA, 'depth22.json.gz'), 'rt')); N = D['nodes']
    out = []
    for r in D['roots']:
        i, d, ch = r, 22, []
        while True:
            S = frozenset(tuple(x) for x in N[i]['points']); F = rhull.facets(list(S))
            ch.append((S, [a for a, c in F]))
            if d == 0: break
            i = [c for c in N[i]['covers'] if N[c]['exact'] == d - 1][0]; d -= 1
        out.append(ch)
    return out

def fig_depth22():
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'code'))
    import rhull
    fig = plt.figure(figsize=(7.0, 3.1))
    ax = fig.add_subplot(1, 2, 1, projection='3d')
    proj = lambda x: (x[0] + 0.35 * x[2], x[1] - 0.75 * x[2])
    Q = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (-4, -2, -1)]
    col = {8: '#d0583a', 4: '#e0b23a', 2: '#3f9c8f', 1: '#2a6f97', 0: '#1b3a5c'}
    columns = [((-4, -2, -1), 8), ((-2, -1, 0), 4), ((-1, 0, 0), 2), ((0, 0, 0), 1),
               ((1, 0, 0), 0), ((0, 1, 0), 0), ((0, 0, 1), 0)]
    s = 0.25
    for a in range(4):
        for b in range(a + 1, 4):
            pa, pb = proj(Q[a]), proj(Q[b])
            ax.plot([pa[0], pb[0]], [pa[1], pb[1]], [0, 0], color='#888888', lw=0.7)
    top, bot = proj(Q[3]), proj(Q[3])
    for v in Q[:3]:
        pv = proj(v)
        for h in (8, -8):
            ax.plot([pv[0], top[0]], [pv[1], top[1]], [0, s * h], color='#1b3a5c', lw=0.8, alpha=0.8)
    ax.plot([top[0]] * 2, [top[1]] * 2, [-8 * s, 8 * s], color='#d0583a', lw=1.4)
    for x, h in columns:
        px = proj(x)
        ts = range(-h, h + 1)
        ax.scatter([px[0]] * len(ts), [px[1]] * len(ts), [s * t for t in ts], s=9, color=col[h],
                   depthshade=False, zorder=5)
    ax.text(top[0] - 0.5, top[1], 8 * s + 0.3, r'$u+8e_4$', fontsize=7)
    ax.text(top[0] - 0.5, top[1], -8 * s - 0.55, r'$u-8e_4$', fontsize=7)
    for v, lab, dz in zip(Q[:3], (r'$e_1$', r'$e_2$', r'$e_3$'), (0.12, 0.12, -0.45)):
        pv = proj(v); ax.text(pv[0] + 0.2, pv[1], dz, lab, fontsize=7)
    pu = proj(Q[3]); ax.text(pu[0] + 0.25, pu[1], -0.42, r'$u$', fontsize=7)
    ax.quiver(1.6, 1.4, -1.6, 0, 0, 1.2, color='#555555', lw=0.7, arrow_length_ratio=0.18)
    ax.text(1.75, 1.4, -0.6, r'$x_4$', fontsize=7, color='#555555')
    ax.set_axis_off()
    ax.view_init(elev=14, azim=-58)
    ax.set_box_aspect((1.25, 1.0, 1.25))
    ax.set_title('(a) $P_1$: columns of heights $8,4,2,1,0$', fontsize=8, pad=-2)
    ax2 = fig.add_subplot(1, 2, 2)
    styles = (('#1b3a5c', 'o', '$P_1$'), ('#d0583a', 's', '$P_2$'))
    for ch, (c, m, lab) in zip(descent22(), styles):
        n = [len(S) for S, _ in ch]
        nd = [len(rhull.closure(V)) for _, V in ch]
        k = np.arange(len(n))
        ax2.semilogy(k, n, m + '-', ms=2.6, lw=1.0, color=c, label=lab + ': points')
        ax2.semilogy(k, nd, m + '--', ms=2.4, lw=1.0, color=c, mfc='white', label=lab + ': dual points')
    ax2.semilogy([22], [15], 'D', ms=4, color='#3f9c8f')
    ax2.annotate('r-minimal, 15 points', xy=(22, 15), xytext=(10.5, 9.0), fontsize=7, color='#3f9c8f',
                 arrowprops=dict(arrowstyle='-', color='#3f9c8f', lw=0.6))
    ax2.set_xlabel('step'); ax2.set_ylabel('lattice points'); ax2.set_xlim(-1, 23.5); ax2.set_ylim(7, 450)
    ax2.legend(fontsize=6.5, frameon=False, loc='upper left', ncol=1)
    ax2.set_title('(b) shortest descents', fontsize=8)
    fig.tight_layout(pad=0.4, w_pad=1.2)
    save(fig, 'fig_depth22.png', 1600)

if __name__ == '__main__':
    which = sys.argv[1:] or ['hasse2', 'cut', 'pairs', 'depth3', 'chain680', 'depth22']
    for w in which: globals()['fig_' + w]()
