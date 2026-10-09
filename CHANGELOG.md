# Changelog

## v0.2.0 — 2026-10-09 — Gates

Zenodo version `10.5281/zenodo.23262639` (concept still `10.5281/zenodo.21918091`). Paper copy under `paper/` is the v1.2 source (`PAPER_PATCHGAP_DRAFT_v6.md`, paper version `10.5281/zenodo.23262565`).

Added (gates; v0.1 claims unchanged):

- `lean/`: Lean 4 core (no Mathlib) proofs of the paper's Section 4.3 stock algebra.
  `stock_rises_iff`, `stock_flat_iff`, `stock_grows_on_window`,
  `stock_nonincreasing_after`, `g_falls_while_stock_rises` (G 10 -> 3 while S rises).
  lean-proof-forge verdict VERIFIED: no sorry/admit, no native_decide, no local axioms,
  axioms within {propext, Classical.choice, Quot.sound}. Toolchain v4.15.0.
- `gates/check_regime_arithmetic.py` + `regime_numbers.json`: recomputes Section 4.4
  R_d and G from stated inputs; checks phrases verbatim against the paper. Fails on
  paper v4-PRE (filter of 10^2 gives ~1 gap/hour, not 1/week); passes on v5-PRE (10^4).
- `gates/check_searcher_sweep.py` + frozen specs: 3 searchers x 54 generator cells.
  v1 spec FAILED (spill 48/54 < 0.90) on a metric ceiling when budget > planted
  penumbra; kept as `results/searcher_sweep_v1_FAILED.json`. v2 spec (recall lift,
  frozen before its first run) passes: spill 54/54, degree control 49/54, random 54/54.
- `gates/check_sources.py` + `sources.json` + `predictions.json`: figure drift,
  retired phrasings, staleness (STALE after 120 days; fails with --strict), prediction
  ledger with deadlines.
- `run_all_gates.py`: one command for all gates.

## v0.1.1 — 2026-08-13 — Labeled figures

Replaced unlabeled snapshots with five Tufte-leaning SVGs (axes, ticks, base-rate
and \(G=1\) hairlines, seed strips, no dual y-axis). Added searcher-rule,
actor-class, and limiter small multiples that can fail a paper sentence on this
toy. Gate unchanged. Zenodo version `10.5281/zenodo.21918637` (concept still `10.5281/zenodo.21918091`).

## v0.1.0 — 2026-08-13 — First software mint

Zenodo software concept `10.5281/zenodo.21918091`, version `10.5281/zenodo.21918092`.
GitHub Release `v0.1.0`. File: `patch-gap-hot-search-v0.1.0.zip`.
Not the paper concept `10.5281/zenodo.21910874`.

## unreleased — 2026-08-13 — Public GitHub tree (no software DOI)

Pushed as `chokmah-me/patch-gap-hot-search`. Added `docs/SOFTWARE-ABSTRACT.md` (Zenodo draft, 8-part scholarly body). Paper v1.0 unchanged. Software concept still not opened.

## unreleased — 2026-08-12 — First companion scaffold

HOT vs uniform-null rule graphs, spill-ranked interface searcher, two-stock
dynamics, and a three-claim thin MC gate. First gate run showed a degree-heavy
rank picking HOT hubs (claim 1 gap −0.235); ranking was changed to neighborhood
spill. Acceleration was made sticky so a salience spike does not flicker off
when patches clear \(S_\text{active}\). No software DOI. Paper v1.0 is unchanged.
