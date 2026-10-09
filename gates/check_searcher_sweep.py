#!/usr/bin/env python3
"""Gate: frozen perturbation sweep over searcher x generator knobs.

Reads gates/searcher_sweep_frozen.json (written before any run), executes
every cell, writes a survival map to results/searcher_sweep.json, and exits
0 iff each frozen criterion holds on its required fraction of cells. No cell
is dropped: a cell that errors is recorded and counts as a failure.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path
from random import Random

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from simulation.graph import (  # noqa: E402
    generate_hot, generate_null, penumbra_share, search_order,
)


def order_for(g, searcher: str, rng: Random) -> list[int]:
    if searcher == "spill":
        return search_order(g)
    if searcher == "degree":
        return sorted(range(g.n), key=lambda i: (g.degree(i), -i), reverse=True)
    if searcher == "random":
        idx = list(range(g.n)); rng.shuffle(idx); return idx
    raise ValueError(searcher)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default=str(Path(__file__).parent / "searcher_sweep_frozen_v2.json"))
    spec_path = Path(ap.parse_args().spec)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    recall = spec.get("metric") == "recall_lift"
    ax = spec["axes"]
    rng0 = Random(spec["master_seed"])
    cells = []
    for s, npen, br, pin, bud in itertools.product(
        ax["searcher"], ax["n_penumbra"], ax["bridges_per_penumbra"], ax["p_intra"], ax["budget"]
    ):
        cell = {"searcher": s, "n_penumbra": npen, "bridges": br, "p_intra": pin, "budget": bud}
        try:
            hs, ns = [], []
            for _ in range(spec["n_seeds_per_cell"]):
                gh = generate_hot(Random(rng0.randrange(2**31)), n_penumbra=npen,
                                  bridges_per_penumbra=br, p_intra=pin)
                gn = generate_null(Random(rng0.randrange(2**31)), n_penumbra=npen, n_edges=gh.n_edges)
                r = Random(rng0.randrange(2**31))
                a = penumbra_share(gh, order_for(gh, s, r), bud)
                b = penumbra_share(gn, order_for(gn, s, r), bud)
                if recall:  # share * picked / reachable = hits / min(budget, n_pen)
                    k = min(bud, gh.n) / min(bud, npen)
                    a, b = a * k, b * k
                hs.append(a)
                ns.append(b)
            cell["hot"] = sum(hs) / len(hs)
            cell["null"] = sum(ns) / len(ns)
            cell["gap"] = cell["hot"] - cell["null"]
        except Exception as e:  # recorded, never dropped
            cell["error"] = repr(e)
        cells.append(cell)

    tests = {
        "gap >= 0.20": lambda g: g >= 0.20,
        "gap < 0.20": lambda g: g < 0.20,
        "abs(gap) < 0.15": lambda g: abs(g) < 0.15,
    }
    ok_all = True
    summary = {}
    for name, c in spec["criteria"].items():
        sel = [x for x in cells if x["searcher"] == c["searcher"]]
        passed = [x for x in sel if "gap" in x and tests[c["test"]](x["gap"])]
        frac = len(passed) / len(sel)
        good = frac >= c["min_cell_fraction"]
        ok_all &= good
        fails = [x for x in sel if x not in passed]
        summary[name] = {"cells": len(sel), "passed": len(passed), "fraction": frac,
                         "required": c["min_cell_fraction"], "ok": good,
                         "failing_cells": fails}
        print(("OK:   " if good else "FAIL: ") +
              f"{name}: {len(passed)}/{len(sel)} cells ({frac:.2f}) satisfy {c['test']} "
              f"[need {c['min_cell_fraction']:.2f}]")
        for x in fails[:6]:
            print(f"        failing cell: {x}")

    out = ROOT / "results" / (spec_path.stem.replace("_frozen", "") + ".json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"spec": spec, "summary": summary, "cells": cells}, indent=2) + "\n", encoding="utf-8")
    print("ALL CHECKS PASSED" if ok_all else "SWEEP FAILED")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
