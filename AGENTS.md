# AGENTS.md — patch-gap-hot-search

Software companion that generates \(R_d\) from a budgeted HOT-graph searcher. Do not simulate \(G\). \(G\) and the stocks are outputs. Python 3.10+, stdlib only.

## Commands

```powershell
python verify_patchgap_claims.py
python -m simulation.figures
python run_all_gates.py --paper paper/PAPER_PATCHGAP_DRAFT_v6.md
```

`verify_patchgap_claims.py` exit 0 iff the three gated claims hold. Figures are labeled SVGs, not load-bearing.

## Work rules

- Not a measurement of legal \(G\), \(R_d\), or \(R_p\).
- Paper §4.4 powers of ten stay heuristics.
- Claim 1 failure challenges this generator+searcher pair, not a legislature.

## Pointers

- `README.md` — gated claims and non-claims
- `claim-manifest.json` — computational-claim-gate
- `docs/SOFTWARE-ABSTRACT.md` — Zenodo body
- `ZENODO.md` — software concept vs version
