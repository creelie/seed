"""Balanced-tree representation for efficient kernel reduction of the graph."""
from pathlib import Path
import gzip,json,hashlib
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'data/depth22.json.gz'
d=json.loads(gzip.decompress(SOURCE.read_bytes()));nodes=d['nodes'];N=len(nodes)
assert N==5592 and d['roots']==[0,1]
def tree(a,b):
    if b-a==1:
        row=nodes[a]
        return '.leaf ⟨'+str(row['bound'])+',['+','.join(map(str,row['covers'] or []))+']⟩'
    m=(a+b)//2
    return f'.branch {m-a} ({tree(a,m)}) ({tree(m,b)})'
def path(r):
    out=[r]
    while nodes[r]['exact']>0:
        r=next(j for j in nodes[r]['covers'] if nodes[j]['exact']==nodes[r]['exact']-1)
        out.append(r)
    assert len(out)==23 and nodes[r]['covers']==[]
    return out
s='''import FiniteBases

/-! Kernel verification of the complete STORED finite graph, not of the
geometric completeness of its cover lists. Null lists at zero-bound
frontier nodes are empty in this graph; the lower certificate uses only
positive-bound lists. A balanced tree makes all indexed reads logarithmic.
No native_decide, admitted proof or custom axiom is used. -/

set_option maxRecDepth 1000000
set_option maxHeartbeats 0

namespace ReflexiveDescent.Depth22

structure Info where
  lower : Nat
  edges : List Nat
inductive Tree where
  | leaf : Info → Tree
  | branch : Nat → Tree → Tree → Tree

def lookup : Tree → Nat → Info
  | .leaf row, _ => row
  | .branch split left right, i =>
    if i<split then lookup left i else lookup right (i-split)

def checkNode (N : Nat) (root : Tree) (row : Info) : Bool :=
  row.edges.all (fun j => decide (j<N ∧ row.lower ≤ (lookup root j).lower+1)) &&
    decide (row.lower=0 ∨ row.edges≠[])

def checkTree (N : Nat) (root : Tree) : Tree → Bool
  | .leaf row => checkNode N root row
  | .branch _ left right => checkTree N root left && checkTree N root right

theorem checkTree_sound (N : Nat) (root t : Tree) (h : checkTree N root t = true)
    (i : Nat) : checkNode N root (lookup t i) = true := by
  induction t generalizing i with
  | leaf row => exact h
  | branch k left right ihL ihR =>
    have hh : checkTree N root left=true ∧ checkTree N root right=true := by simpa [checkTree] using h
    simp only [lookup]
    split
    · exact ihL hh.1 _
    · exact ihR hh.2 _

theorem checkNode_sound (N : Nat) (root : Tree) (row : Info)
    (h : checkNode N root row=true) :
    (∀ j ∈ row.edges, j<N ∧ row.lower ≤ (lookup root j).lower+1) ∧
      (row.lower=0 ∨ row.edges≠[]) := by
  simpa [checkNode,List.all_eq_true] using h

def data : Tree :=
'''+tree(0,N)+'''

abbrev Node := Fin 5592
def bound (i : Node) : Nat := (lookup data i.val).lower
def cover (i j : Node) : Prop := j.val ∈ (lookup data i.val).edges
instance (i j : Node) : Decidable (cover i j) :=
  inferInstanceAs (Decidable (j.val ∈ (lookup data i.val).edges))

theorem certificate_checked : checkTree 5592 data data=true := by decide +kernel

theorem certificate_sound (i : Node) :
    (∀ j ∈ (lookup data i.val).edges, j<5592 ∧
      bound i ≤ (lookup data j).lower+1) ∧
    (bound i=0 ∨ (lookup data i.val).edges≠[]) :=
  checkNode_sound 5592 data _ (checkTree_sound 5592 data data certificate_checked i.val)

theorem positive_successor (i : Node) (hi : 0 < bound i) : ∃ j, cover i j := by
  have hh := certificate_sound i
  have hn : (lookup data i.val).edges≠[] := hh.2.resolve_left (Nat.ne_of_gt hi)
  obtain ⟨j,hj⟩ := List.exists_mem_of_ne_nil _ hn
  refine ⟨⟨j,(hh.1 j hj).1⟩,hj⟩

theorem edge_bound {i j : Node} (h : cover i j) : bound i ≤ bound j+1 :=
  ((certificate_sound i).1 j.val h).2

theorem graph_lower_bound {i : Node} {k : Nat} (h : Descent cover i k) : bound i ≤ k := by
  apply lower_certificate bound ?_ (fun _ _ h => edge_bound h) h
  intro x ht
  by_contra hne
  obtain ⟨y,hy⟩ := positive_successor x (Nat.pos_of_ne_zero hne)
  exact ht y hy

'''
paths=[path(r) for r in d['roots']]
for r,p in zip(d['roots'],paths):
    s+=f'theorem terminal_{r} : (lookup data {p[-1]}).edges = [] := by decide +kernel\n'
    s+=f'theorem path_{r} : Descent cover (⟨{r},by decide⟩ : Node) 22 := by\n'
    for k,i in enumerate(p[:-1]):
        s+=f'  apply Descent.step _ (⟨{p[k+1]},by decide⟩ : Node) {21-k} (by decide +kernel)\n'
    s+=f'  apply Descent.stop\n  intro y hy\n  change y.val ∈ (lookup data {p[-1]}).edges at hy\n  rw [terminal_{r}] at hy\n  exact List.not_mem_nil hy\n'
    s+=f'theorem root_{r}_shortest : Shortest cover (⟨{r},by decide⟩ : Node) 22 := by\n'
    s+=f'  refine ⟨path_{r},?_⟩\n  intro k hk\n  have hh := graph_lower_bound hk\n  have hb : bound (⟨{r},by decide⟩ : Node) = 22 := by decide +kernel\n  simpa only [hb] using hh\n\n'
s+='end ReflexiveDescent.Depth22\n\n'
s+='\n'.join('#print axioms ReflexiveDescent.Depth22.'+t for t in ['certificate_checked','graph_lower_bound','root_0_shortest','root_1_shortest'])+'\n'
(ROOT/'Depth22Certificate.lean').write_text(s,encoding='utf8',newline='\n')
(ROOT/'depth22-source.json').write_text(json.dumps({'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'nodes':N,'edges':sum(len(n['covers'] or []) for n in nodes),'positive_bound_nodes':sum(n['bound']>0 for n in nodes),'paths':paths,'representation':'balanced binary tree','scope':'stored finite graph only; no geometric cover-completeness proof'},indent=2)+'\n')
print('Generated balanced-tree graph certificate',N,'nodes')
