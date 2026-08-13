#!/usr/bin/env python3
"""Computational claim gate for patch-gap-hot-search.

Load-bearing *toy* claims (thin MC). Not measurements of any legal system.

  1. HOT concentration: interface searcher recovers planted penumbra more
     under the HOT generator than under a same-size uniform-null graph.
  2. Stock identity: on every step with counted R_d > R_p, S_known does
     not fall (definition made executable).
  3. Limiter qualitative: legislative acceleration can drop G while
     S_known is still rising.

Non-claims: legal G, SocioHack, A1/VERITE, Rice/FLP, any live bill,
§4.4 powers of ten.

Exit 0 iff all checks pass. Prints why each check fails.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from random import Random

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from simulation.dynamics import DynamicsConfig, run_episode  # noqa: E402
from simulation.graph import generate_hot, generate_null, penumbra_share, search_order  # noqa: E402

MASTER_SEED = 20260812
N_SEEDS = 20
BUDGET = 20
# HOT should beat null by a wide structural margin; 0.20 is the floor, not a fit.
MIN_SHARE_GAP = 0.20
# Null share should stay near the label base rate (~0.20), not collapse to 0
# in a way that would make the gap trivial for the wrong reason.
NULL_SHARE_MAX = 0.45
N_DYN = 10
RESULTS = ROOT / "results"


def _fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise AssertionError(msg)


def _ok(msg: str) -> None:
    print(f"OK:   {msg}")


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else float("nan")


def check_hot_concentration() -> dict:
    rng = Random(MASTER_SEED)
    hot_shares: list[float] = []
    null_shares: list[float] = []
    for k in range(N_SEEDS):
        gh = generate_hot(Random(rng.randrange(2**31)))
        gn = generate_null(Random(rng.randrange(2**31)), n_edges=gh.n_edges)
        if gh.n != gn.n:
            _fail(f"seed {k}: size mismatch HOT n={gh.n} null n={gn.n}")
        if gh.n_edges != gn.n_edges:
            _fail(f"seed {k}: edge mismatch HOT {gh.n_edges} null {gn.n_edges}")
        sh = penumbra_share(gh, search_order(gh), BUDGET)
        sn = penumbra_share(gn, search_order(gn), BUDGET)
        hot_shares.append(sh)
        null_shares.append(sn)

    mh, mn = _mean(hot_shares), _mean(null_shares)
    gap = mh - mn
    if math.isnan(mh) or math.isnan(mn):
        _fail("empty share samples")
    if mn > NULL_SHARE_MAX:
        _fail(
            f"null penumbra share {mn:.3f} > {NULL_SHARE_MAX} "
            f"(interface score leaking labels?)"
        )
    if gap < MIN_SHARE_GAP:
        _fail(
            f"HOT−null penumbra-share gap {gap:.3f} < {MIN_SHARE_GAP} "
            f"(HOT mean {mh:.3f}, null mean {mn:.3f}, n={N_SEEDS})"
        )
    _ok(
        f"HOT concentration: mean share HOT={mh:.3f} null={mn:.3f} "
        f"gap={gap:.3f} (n={N_SEEDS}, budget={BUDGET})"
    )
    return {
        "n_seeds": N_SEEDS,
        "budget": BUDGET,
        "hot_mean": mh,
        "null_mean": mn,
        "gap": gap,
        "hot_shares": hot_shares,
        "null_shares": null_shares,
    }


def check_stock_identity() -> dict:
    rng = Random(MASTER_SEED + 1)
    violations = 0
    steps_checked = 0
    for k in range(N_DYN):
        g = generate_hot(Random(rng.randrange(2**31)))
        ep = run_episode(g, DynamicsConfig(accelerate=False, actor="corporate"))
        prev = 0
        for t, (rd, rp, sk) in enumerate(zip(ep.rd, ep.rp, ep.s_known)):
            if sk < 0:
                _fail(f"run {k} t={t}: S_known={sk} < 0")
            if rd > rp:
                steps_checked += 1
                if sk < prev:
                    violations += 1
                    _fail(
                        f"run {k} t={t}: Rd={rd} > Rp={rp} but "
                        f"S_known {sk} < previous {prev}"
                    )
            prev = sk
    if steps_checked < 5:
        _fail(f"stock identity: only {steps_checked} Rd>Rp steps (need a real path)")
    _ok(f"stock identity: {steps_checked} Rd>Rp steps, S_known nondecreasing ({N_DYN} runs)")
    return {"runs": N_DYN, "rd_gt_rp_steps": steps_checked, "violations": violations}


def check_limiter_qualitative() -> dict:
    rng = Random(MASTER_SEED + 2)
    triggered = 0
    success = 0
    details = []
    for k in range(N_DYN):
        g = generate_hot(Random(rng.randrange(2**31)))
        ep = run_episode(g, DynamicsConfig(accelerate=True, actor="agent"))
        if ep.t_accel is None:
            details.append({"run": k, "triggered": False})
            continue
        triggered += 1
        t0 = ep.t_accel
        g0 = ep.g_finite(t0)
        # If Rp was 0 at onset, take the next finite G as the reference peak.
        t_ref = t0
        if g0 is None:
            for t in range(t0, len(ep.g)):
                if ep.g_finite(t) is not None:
                    t_ref = t
                    g0 = ep.g_finite(t)
                    break
        if g0 is None:
            details.append({"run": k, "triggered": True, "reason": "no finite G after onset"})
            continue
        dropped = False
        rose = False
        t_drop = None
        t_rise = None
        for t in range(t_ref + 1, len(ep.g)):
            gt = ep.g_finite(t)
            if gt is not None and gt < g0:
                dropped = True
                t_drop = t
            if ep.s_known[t] > ep.s_known[t_ref]:
                rose = True
                t_rise = t
            if dropped and rose:
                break
        if dropped and rose:
            success += 1
            details.append(
                {
                    "run": k,
                    "triggered": True,
                    "ok": True,
                    "t_accel": t0,
                    "g_ref": g0,
                    "t_drop": t_drop,
                    "t_rise": t_rise,
                }
            )
        else:
            details.append(
                {
                    "run": k,
                    "triggered": True,
                    "ok": False,
                    "g_dropped": dropped,
                    "s_rose": rose,
                    "t_accel": t0,
                    "g_ref": g0,
                }
            )

    if triggered < 8:
        _fail(f"acceleration triggered in {triggered}/{N_DYN} runs (need ≥8)")
    if success < 8:
        _fail(
            f"G-drop with S_known still rising in {success}/{N_DYN} runs "
            f"(need ≥8; triggered={triggered})"
        )
    _ok(
        f"limiter qualitative: {success}/{N_DYN} runs show G drop + rising S_known "
        f"(triggered={triggered})"
    )
    return {"runs": N_DYN, "triggered": triggered, "success": success, "details": details}


def main() -> int:
    report = {
        "seed": MASTER_SEED,
        "claims": {},
    }
    try:
        report["claims"]["hot-concentration"] = check_hot_concentration()
        report["claims"]["stock-identity"] = check_stock_identity()
        report["claims"]["limiter-qualitative"] = check_limiter_qualitative()
    except AssertionError:
        RESULTS.mkdir(parents=True, exist_ok=True)
        (RESULTS / "verify_patchgap_last.json").write_text(
            json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
        return 1

    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "verify_patchgap_last.json").write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
