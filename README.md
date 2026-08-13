# patch-gap-hot-search

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21918091.svg)](https://doi.org/10.5281/zenodo.21918091)

Companion **software** for

> Daniyel Yaacov Bilar. *The Governance Patch-Gap: Machine-Speed Exploit Discovery Against Human-Speed Legal Repair* (v1.0). Zenodo. [10.5281/zenodo.21910874](https://doi.org/10.5281/zenodo.21910874) (concept); [10.5281/zenodo.21910875](https://doi.org/10.5281/zenodo.21910875) (PDF).

**Do not simulate \(G\).** This toy generates \(R_d\) from a budgeted interface searcher on a HOT-designed rule graph. \(G = R_d / R_p\) and the stocks \(S_\text{known}\), \(S_\text{active}\) are *outputs*.

The paper repo (`https://github.com/chokmah-me/patch-gap`) is paper-only. This tree is a separate software companion (`https://github.com/chokmah-me/patch-gap-hot-search`).

- Software **concept** DOI (always latest zip): [10.5281/zenodo.21918091](https://doi.org/10.5281/zenodo.21918091)
- Software **version** DOI (v0.1.1): [10.5281/zenodo.21918637](https://doi.org/10.5281/zenodo.21918637)

Zenodo body: [`docs/SOFTWARE-ABSTRACT.md`](docs/SOFTWARE-ABSTRACT.md).

## What is claimed / not claimed

**Gated claims** (`verify_patchgap_claims.py`):

1. **HOT concentration.** An interface searcher (neighborhood spill — it never sees the penumbra label) recovers planted penumbra more under the HOT generator than under a same-size, same-edge-count uniform-null graph.
2. **Stock identity.** While counted \(R_d > R_p\), \(S_\text{known}\) does not fall. The paper’s definition, made executable — not a new empirical law.
3. **Limiter qualitative.** Legislative acceleration (higher \(R_p\) after \(S_\text{active}\) crosses a salience knob) can drop \(G\) while \(S_\text{known}\) is still rising.

**Non-claims.**

- Not a measurement of legal \(G\), \(R_d\), or \(R_p\).
- Not SocioHack, not A1/VERITE, not a tax-code or CFR search.
- Not a proof that courts instantiate Rice, FLP, or attestation bounds.
- Not an evaluation of any live bill.
- Paper §4.4 powers of ten stay heuristics.

If claim 1 fails, the HOT mapping in the paper is *computationally* challenged on this toy — that is a real falsifier for the generator+searcher pair, not for any legislature.

## Reproduce

Python 3.10+ (3.8 likely fine). Stdlib only.

```text
python verify_patchgap_claims.py
# exit 0 iff the three claims hold

python -m simulation.figures
# labeled SVGs under figures/ — not load-bearing
```

Outer gate (same command via manifest):

```text
python path\to\computational-claim-gate\scripts\verify_claim_project.py --project .
```

## Layout

| Path | Role |
|------|------|
| `simulation/graph.py` | HOT vs uniform-null generators; interface ranking |
| `simulation/dynamics.py` | Counted \(R_d\), patcher, actor execution, two stocks |
| `simulation/figures.py` | Tufte-leaning SVG grammar (stdlib) |
| `verify_patchgap_claims.py` | Thin MC claim gate |
| `claim-manifest.json` | `cd-claim-gate/v1` |
| `results/` | Gate evidence |
| `figures/` | Five labeled charts — see [`figures/README.md`](figures/README.md) |

## Parameters

Graph sizes, search budget, patch rates, and the salience threshold are **scenario knobs**. They are not estimates of Congress, courts, or any agency.

Actor classes only change execution latency and the fraction of known finds that become active: corporate (slow, filtered), state (medium), unsupervised agent (fast, no principal). Discovery ranking is the same for all three.

## Citation

Cite the paper for the argument. Cite this software concept for the runnable toy.

Bilar, D. Y. (2026). *The Governance Patch-Gap: Machine-Speed Exploit Discovery Against Human-Speed Legal Repair* (v1.0). Zenodo. https://doi.org/10.5281/zenodo.21910874

Bilar, D. Y. (2026). *patch-gap-hot-search: a synthetic HOT-searcher toy for the governance patch-gap* (v0.1.1). Zenodo. https://doi.org/10.5281/zenodo.21918091 (concept); https://doi.org/10.5281/zenodo.21918637 (this zip)

License: MIT (this code). The paper is CC BY 4.0.
