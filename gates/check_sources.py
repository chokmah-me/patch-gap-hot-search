#!/usr/bin/env python3
"""Gate: empirical figures and prediction statuses have not drifted.

1. Every registered figure phrase appears verbatim in the paper.
2. No retired phrasing reappears.
3. Every figure was retrieved within max_age_days of --today; older ones
   print STALE (fail only with --strict, so a re-check is forced before mint).
4. The predictions ledger is well-formed; open predictions past deadline
   fail; each prediction's status phrase appears in the paper.

Exit 0 iff all non-warning checks pass. Stdlib only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", required=True)
    ap.add_argument("--today", default=dt.date.today().isoformat())
    ap.add_argument("--strict", action="store_true", help="treat STALE as failure")
    a = ap.parse_args()
    text = Path(a.paper).read_text(encoding="utf-8")
    today = dt.date.fromisoformat(a.today)
    src = json.loads((HERE / "sources.json").read_text(encoding="utf-8"))
    pred = json.loads((HERE / "predictions.json").read_text(encoding="utf-8"))
    fails, warns = [], []

    for f in src["figures"]:
        if f["phrase"] not in text:
            fails.append(f"figure {f['id']}: phrase missing from paper: {f['phrase']!r}")
        age = (today - dt.date.fromisoformat(f["retrieved"])).days
        if age > src["max_age_days"]:
            warns.append(f"STALE figure {f['id']}: retrieved {age} days ago ({f['source']}); re-check before mint")
        if f"[{f['ref']}]" not in text.split("## References")[0] and f"][{f['ref']}]" not in text:
            fails.append(f"figure {f['id']}: reference [{f['ref']}] never cited in body")
    for r in src["retired"]:
        if r["phrase"] in text:
            fails.append(f"retired phrasing present: {r['phrase']!r} ({r['why']})")

    ok_status = set(pred["statuses"])
    for p in pred["predictions"]:
        if p["status"] not in ok_status:
            fails.append(f"{p['id']}: bad status {p['status']!r}")
        if p["status"] == "open" and today > dt.date.fromisoformat(p["deadline"]):
            fails.append(f"{p['id']}: deadline {p['deadline']} passed with status open; resolve it")
        if p["paper_status_phrase"] not in text:
            fails.append(f"{p['id']}: status phrase missing from paper")
        for e in p["evidence"]:
            if not (e.get("url", "").startswith("http") and e.get("date")):
                fails.append(f"{p['id']}: evidence entry lacks url or date: {e}")

    print(f"OK:   {len(src['figures'])} figures, {len(src['retired'])} retired phrasings, "
          f"{len(pred['predictions'])} predictions checked against {a.paper}")
    for w in warns:
        print("WARN: " + w)
    if a.strict:
        fails += warns
    for f in fails:
        print("FAIL: " + f, file=sys.stderr)
    print("ALL CHECKS PASSED" if not fails else f"{len(fails)} CHECK(S) FAILED")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
