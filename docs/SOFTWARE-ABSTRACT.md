# Zenodo software description draft

**Title:** patch-gap-hot-search: a synthetic HOT-searcher toy for the governance patch-gap

## 1. Artifact claim (one sentence)

This deposit is a Python, stdlib-only toy that **generates** a discovery rate \(R_d\) from a label-blind interface searcher on a Highly Optimized Tolerance (HOT) rule graph; the patch-gap \(G = R_d/R_p\) and the stocks \(S_\text{known}\), \(S_\text{active}\) are outputs, not fitted legal measurements.

## 2. Problem / scientific context

Paper concept DOI [10.5281/zenodo.21910874](https://doi.org/10.5281/zenodo.21910874) defines the governance patch-gap as a rate ratio and a stock, and maps legal open texture onto HOT / robust-yet-fragile design. \(G\) in that PDF is a definition, not a dynamical model; the §4.4 powers of ten are heuristics. This software exists so those qualitative distinctions can be *run*: a search process produces \(R_d\), a patcher produces \(R_p\), and \(G\) and \(S\) emerge. It does not estimate Congress, courts, or any statute book.

## 3. Contents

- `simulation/graph.py` — HOT generator (dense modules, planted interface penumbra) and same-size uniform-null control
- `simulation/dynamics.py` — counted \(R_d\), patcher, actor execution filters, two stocks; legislative acceleration is sticky
- `simulation/figures.py` — optional SVG snapshots (not load-bearing)
- `verify_patchgap_claims.py` — thin Monte Carlo gate for three toy claims
- `claim-manifest.json` — `cd-claim-gate/v1`
- `results/` — executed gate evidence from the recorded run
- `figures/` — five labeled SVGs (HOT vs null, \(G\) and \(S\), searcher rule, actors, limiters)

No paper PDF. No real legal corpus.

## 4. How to reproduce

- Environment: Python 3.10+ (3.8 likely fine). No third-party packages.
- Commands:

```text
python verify_patchgap_claims.py
# exit 0 iff the three toy claims hold

python -m simulation.figures
# optional; writes figures/*.svg
```

- Expected: `ALL CHECKS PASSED`; optional outer runner `verify_claim_project.py --project .` writes `results/claim_verify_meta.json`.

## 5. Relation to paper

Illustrates the paper’s §4.4 distinction that \(G\) can fall while \(S_\text{known}\) still rises, and that a searcher aimed at interfaces is not the same as a degree-greedy crawl of a robust core. Load-bearing legal argument, predictions, and named weaknesses stay in the PDF. Paper and software are **separate Zenodo concepts**; do not merge this zip with the paper record `21910874` / `21910875`.

## 6. Limitations / non-claims

- Not a measurement of legal \(G\), \(R_d\), or \(R_p\)
- Not support for the paper’s heuristic exponents
- Not a test that any statute is HOT (the generator *assumes* HOT structure)
- Not SocioHack, A1/VERITE, Rice/FLP, or an evaluation of any live bill
- Claim 2 is the stock identity made executable, not a new empirical law
- Claim 3 is an existence path under scenario knobs (sticky acceleration), not a legislature model

## 7. This software version (scientific delta)

**v0.1.1.** Five Tufte-leaning figures replace unlabeled snapshots: seed strips with axes; stacked \(G(t)\) and \(S(t)\) (no dual y-axis); spill vs degree-greedy; actor-class execution stocks; limiter 2×2. These can fail a paper sentence on this toy. Dynamics and gated claims are unchanged from v0.1.0.

## 8. Citation

Cite the paper concept DOI [10.5281/zenodo.21910874](https://doi.org/10.5281/zenodo.21910874) for the argument. Cite this software **concept** DOI [10.5281/zenodo.21918091](https://doi.org/10.5281/zenodo.21918091) for the runnable artifact (this zip: [10.5281/zenodo.21918637](https://doi.org/10.5281/zenodo.21918637)).
