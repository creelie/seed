"""Failure-driven loop on the Anaxia engine (creelie/eBLLM, package `ebllm`).

A round tries one strategy.  Its checks are real computations or proofs with named sources;
the engine turns each failed check into a playbook bullet, and the round records the change
of strategy that the failure calls for.  The next round runs the changed strategy.  The
release label of every target comes only from the engine's release algebra.
"""
from __future__ import annotations

import json, time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from ebllm.engine import Engine, Proposal
from ebllm.ledger import contract_report
from ebllm.obligations import ObligationGraph
from ebllm.package import ConjecturePackage
from ebllm.playbook import Bullet
from ebllm.release import emit, blocking_factors


@dataclass
class Check:
    name: str                       # obligation name
    kind: str                       # lemma, construction, computation, literature, ...
    run: Callable[[], dict]         # returns {"ok": bool, "evidence": str}
    verifier: str = ""              # what discharges it


@dataclass
class Round:
    strategy: str
    checks: List[Check]
    change: str = ""                # the modification made when this round fails
    bridges: List[tuple] = field(default_factory=list)


@dataclass
class Target:
    name: str
    package: ConjecturePackage
    root: str
    rounds: List[Round]
    conditions: List[str] = field(default_factory=list)   # named unproved inputs, if any
    model_ok: bool = True


def run_target(t: Target, factors: Dict[str, int]) -> dict:
    g = ObligationGraph()
    g.add(t.root, kind="theorem")
    eng = Engine(package=t.package, graph=g, verifiers=dict(factors), root=t.root)
    log = []
    for i, r in enumerate(t.rounds, 1):
        t0 = time.time()
        results = {}
        obligations = [dict(name=c.name, kind=c.kind, verifier=c.verifier) for c in r.checks]
        for c in r.checks:
            out = c.run()
            results[c.name] = out
        prop = Proposal(obligations=obligations,
                        checks={c.name: (1 if results[c.name]["ok"] else 0) for c in r.checks},
                        bridges=r.bridges,
                        model_ok=t.model_ok and i == len(t.rounds) and all(o['ok'] for o in results.values()))
        failed = [n for n, o in results.items() if not o["ok"]]
        if failed and r.change:
            prop.lessons.append(Bullet(f"{t.name}:change-{i}", gate="strategy",
                                       claim=r.change, status="UNK", source=f"round {i}"))
        rec = eng.step(i, prop)
        log.append(dict(round=i, strategy=r.strategy, secs=round(time.time() - t0, 1),
                        checks={n: o for n, o in results.items()},
                        failed=failed, change=r.change if failed else "",
                        label=rec["label"], blocking=rec["blocking"]))
    certified = g.releasable(t.root)
    f = dict(factors)
    if not certified:
        f["proof"] = 0
    label = emit(f, conditions=t.conditions, model_ok=t.model_ok and certified)
    return dict(target=t.name, label=label.value, blocking=blocking_factors(f),
                certified_root=certified, rounds=log,
                report=contract_report(eng), ledger=eng.ledger.records)


def write_outputs(results: List[dict], prefix: str) -> None:
    json.dump([{k: v for k, v in r.items() if k != "report"} for r in results],
              open(f"{prefix}_ledger.json", "w"), indent=2, default=str)
    with open(f"{prefix}_reports.md", "w") as fh:
        for r in results:
            fh.write(r["report"] + "\n")
    lines = []
    for r in results:
        lines.append(f"## {r['target']}\n")
        lines.append("| Round | Strategy | Failed checks | Change made | Label after round |")
        lines.append("|---|---|---|---|---|")
        for x in r["rounds"]:
            lines.append(f"| {x['round']} | {x['strategy']} | {', '.join(x['failed']) or 'none'} | "
                         f"{x['change'] or '-'} | {x['label']} |")
        lines.append("")
        for x in r["rounds"]:
            for n, o in x["checks"].items():
                lines.append(f"- round {x['round']}, `{n}`: {'pass' if o['ok'] else 'FAIL'}. {o['evidence']}")
        lines.append(f"\nFinal label: **{r['label']}**; blocking factors: {', '.join(r['blocking']) or 'none'}.\n")
    open(f"{prefix}_loop.md", "w").write("\n".join(lines) + "\n")
