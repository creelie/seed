"""Run the pinned local Lean/Mathlib without modifying the reused package tree."""
from pathlib import Path
import os, subprocess, sys, json, hashlib
sys.stdout.reconfigure(encoding='utf8')
sys.stderr.reconfigure(encoding='utf8')
ROOT=Path(__file__).resolve().parent
PKGS=Path(r'D:\CLAUDE PAPERS\research-closure-2026-10-23\NavierStokesAndEuler\.lake\packages')
LEAN=Path(r'C:\Users\user\.elan\toolchains\leanprover--lean4---v4.34.0-rc2\bin\lean.exe')
env=os.environ.copy()
env['LEAN_PATH']=os.pathsep.join([str(ROOT)]+[str(p/'.lake/build/lib/lean') for p in PKGS.iterdir() if p.is_dir()])
module_order=['DescentProducts','FiniteBases','FreeSumGeometry','CoordinateLattice',
 'FreeSumDepth','DepthGrowth','IntervalDescents','FiniteReflexive','Depth22Certificate',
 'FourDimensionalObstruction','PolarConvention','ReflexiveDescentFormal','AxiomsAudit']
targets=sys.argv[1:] or [m+'.lean' for m in module_order]
for arg in targets:
    p=ROOT/arg
    print('Checking '+arg,flush=True)
    result=subprocess.run([str(LEAN),'-M','6144','-o',str(p.with_suffix('.olean')),str(p)],cwd=ROOT,env=env,text=True,encoding='utf8',errors='replace',capture_output=True,timeout=600)
    print(result.stdout,end='');print(result.stderr,end='',file=sys.stderr)
    (ROOT/(p.stem+'.log')).write_text(result.stdout+result.stderr,encoding='utf8')
    if result.returncode:raise SystemExit(result.returncode)
