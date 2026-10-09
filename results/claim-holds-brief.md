# Claim-holds brief — patch-gap-hot-search

## Status

**Verified** (thin MC, this host, 2026-08-13). Not a software mint. Not a measurement of legal \(G\).

## Claims

| id | command | exit | notes |
|----|---------|------|-------|
| patchgap-hot-searcher | `python verify_patchgap_claims.py` | 0 | HOT mean share 0.957 vs null 0.212 (gap 0.745, n=20, budget=20); 350 Rd>Rp steps S_known nondecreasing (10 runs); 10/10 limiter runs G-drop + rising S_known |

Outer runner: `computational-claim-gate` `verify_claim_project.py --project .` → `ok=True` (309 ms).

## Seeds / env / platform

- Master seed: `20260812`
- Host: Windows, pwsh; `python` on PATH (3.14)
- Timestamp: `2026-08-13T02:18:12.240256+00:00` (`results/claim_verify_meta.json`)

## Not checked here

- Legal \(G\), \(R_d\), \(R_p\), or §4.4 powers of ten
- SocioHack, A1/VERITE, any live corpus or bill
- Rice / FLP / attestation; Lean
- Figure SVGs (optional snapshots, not gated)
- Software Zenodo concept (not opened)

## Evidence

- `results/claim_verify_meta.json`
- `results/claim_verify_out.txt`
- `results/verify_patchgap_last.json`

## Residual risk

The HOT concentration result is a property of this generator + spill ranking pair. A different searcher (degree-greedy) picks robust hubs and **fails** claim 1 — that failure was observed in the first gate run and is why ranking is spill, not degree. Sticky legislative acceleration is a modeling choice (ECRA-style, not a one-step flicker). Parameters are scenario knobs.

No mint, push, or announce from this gate.


## v0.2 addendum (2026-10-09, Linux, Python 3.14, Lean 4.15.0 core)

| gate | result | evidence |
|------|--------|----------|
| searcher sweep v1 | FAIL 48/54 spill cells (ceiling artifact) | `results/searcher_sweep_v1_FAILED.json` |
| searcher sweep v2 | pass: spill 54/54, degree 49/54, random 54/54 | `results/searcher_sweep_v2.json` |
| regime arithmetic | pass on v6; fails on v4-PRE | stdout |
| sources/predictions | pass on v6 | stdout |
| Lean stock algebra | VERIFIED, 5 declarations | `lean/results/lean_verify_meta.json` |

Lean was run against a locally linked toolchain (`lean-4.15.0`, same release as
`leanprover/lean4:v4.15.0`) because the session's egress policy blocked
release.lean-lang.org; the committed `lean-toolchain` names the official release.

Residual risk added in v0.2: degree-greedy finds planted bridges when bridges touch
three modules in sparse modules (5/54 cells), so the paper's searcher dependence is
itself generator-dependent. The paper (v5-PRE Section 4.5) now says so.
