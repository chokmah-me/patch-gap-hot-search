#!/usr/bin/env python3
"""Gate: Section 4.4 regime arithmetic is internally consistent.

Recomputes R_d from (raw flags per hour) x (hours per year) / 10^(filter),
and G = R_d / R_p, then checks each against the value the paper states,
within the manifest's log10 tolerance. With --paper, also checks that every
registered phrase appears verbatim in the draft (catches silent drift between
the manifest and the text).

Exit 0 iff every check passes. Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(HERE / "regime_numbers.json"))
    ap.add_argument("--paper", help="path to the paper draft (.md)")
    a = ap.parse_args()
    m = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
    tol = m["tolerance_log10"]
    hpy = m["hours_per_year"]
    text = Path(a.paper).read_text(encoding="utf-8") if a.paper else None
    fails: list[str] = []

    for r in m["regimes"]:
        rid = r["id"]
        if text is not None:
            for ph in r["phrases"]:
                if ph not in text:
                    fails.append(f"{rid}: phrase not in paper: {ph!r}")
        if "raw_flags_per_hour" in r:
            for label, h in hpy.items():
                rd = r["raw_flags_per_hour"] * h / 10 ** r["filter_reduction_log10"]
                d = math.log10(rd / r["stated_rd_per_year"])
                needed = math.log10(r["raw_flags_per_hour"] * h / r["stated_rd_per_year"])
                msg = (f"{rid} [{label} year, {h} h]: recomputed R_d={rd:g}/yr vs "
                       f"stated {r['stated_rd_per_year']:g}/yr (off by 10^{d:.2f}); "
                       f"filter needed for stated R_d = 10^{needed:.2f}")
                (fails.append if abs(d) > tol else print)(("" if abs(d) > tol else "OK:   ") + msg)
            rd_used = r["stated_rd_per_year"]
        else:
            rd_used = r["rd_per_year"]
        g = rd_used / r["rp_per_year"]
        dg = math.log10(g / r["stated_G"])
        msg = f"{rid}: G = {rd_used:g}/{r['rp_per_year']:g} = {g:g} vs stated {r['stated_G']:g}"
        if abs(dg) > tol:
            fails.append(msg)
        else:
            print("OK:   " + msg)

    for f in fails:
        print("FAIL: " + f, file=sys.stderr)
    print("ALL CHECKS PASSED" if not fails else f"{len(fails)} CHECK(S) FAILED")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
