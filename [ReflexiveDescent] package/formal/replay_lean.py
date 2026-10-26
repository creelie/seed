"""Replay selected modules with Lean's own kernel replay tool.

This is an environment-integrity check, not a separate proof assistant.
It checks the new declarations in each named module relative to its imports.
"""
from pathlib import Path
import os,subprocess,sys,json,time
sys.stdout.reconfigure(encoding='utf8');sys.stderr.reconfigure(encoding='utf8')
ROOT=Path(__file__).resolve().parent
PKGS=Path(r'D:\CLAUDE PAPERS\research-closure-2026-10-23\NavierStokesAndEuler\.lake\packages')
CHECKER=Path(r'C:\Users\user\.elan\toolchains\leanprover--lean4---v4.34.0-rc2\bin\leanchecker.exe')
env=os.environ.copy();env['LEAN_NUM_THREADS']='1'
env['LEAN_PATH']=os.pathsep.join([str(ROOT)]+[str(p/'.lake/build/lib/lean') for p in PKGS.iterdir() if p.is_dir()])
mods=sys.argv[1:] or ['DescentProducts','FiniteBases','FreeSumGeometry','CoordinateLattice',
    'FreeSumDepth','DepthGrowth','IntervalDescents','FiniteReflexive','Depth22Certificate',
    'FourDimensionalObstruction','PolarConvention']
start=time.monotonic()
print('Kernel replay: '+', '.join(mods),flush=True)
r=subprocess.run([str(CHECKER),'-v',*mods],cwd=ROOT,env=env,text=True,encoding='utf8',errors='replace',capture_output=True,timeout=900)
(ROOT/'kernel-replay.log').write_text(r.stdout+r.stderr,encoding='utf8')
report={'exit_code':r.returncode,'modules':mods,'wall_seconds':round(time.monotonic()-start,3),
        'scope':'Lean kernel replay of new module declarations relative to their imports; not an independent proof assistant'}
(ROOT/'kernel-replay.json').write_text(json.dumps(report,indent=2)+'\n')
print(r.stdout,end='');print(r.stderr,end='',file=sys.stderr);print(json.dumps(report))
raise SystemExit(r.returncode)
