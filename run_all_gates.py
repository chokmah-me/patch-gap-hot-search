#!/usr/bin/env python3
"""Run every gate for patch-gap-hot-search v0.2.

  python run_all_gates.py --paper path/to/PAPER_PATCHGAP_DRAFT_v6.md [--lean]

Gates:
  1. verify_patchgap_claims.py        toy MC claims (v0.1, unchanged)
  2. gates/check_searcher_sweep.py    frozen perturbation sweep (v2 spec)
  3. gates/check_regime_arithmetic.py Section 4.4 arithmetic vs paper text
  4. gates/check_sources.py           figure/prediction drift vs paper text
  5. (--lean) lean-proof-forge verify on lean/ (needs elan + lake)
Exit 0 iff all selected gates pass.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(name: str, cmd: list[str], cwd: Path = ROOT) -> bool:
    print(f"\n=== {name}\n$ {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=cwd)
    print(f"--- {name}: {'PASS' if r.returncode == 0 else 'FAIL'}")
    return r.returncode == 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", required=True)
    ap.add_argument("--lean", action="store_true")
    ap.add_argument("--lean-verifier", default="verify_lean_project.py",
                    help="path to lean-proof-forge scripts/verify_lean_project.py")
    a = ap.parse_args()
    py = sys.executable
    ok = [
        run("toy claims", [py, "verify_patchgap_claims.py"]),
        run("searcher sweep", [py, "gates/check_searcher_sweep.py"]),
        run("regime arithmetic", [py, "gates/check_regime_arithmetic.py", "--paper", a.paper]),
        run("sources and predictions", [py, "gates/check_sources.py", "--paper", a.paper]),
    ]
    if a.lean:
        ok.append(run("lean stock algebra", [py, a.lean_verifier, "--project", "lean"]))
    print("\nALL GATES PASSED" if all(ok) else f"\n{ok.count(False)} GATE(S) FAILED")
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
