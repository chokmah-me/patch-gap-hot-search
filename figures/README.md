# Figures

Regenerate: `python -m simulation.figures` from the repo root. Stdlib only. The claim gate does **not** read these files.

Every chart is a toy. Axes are labeled. Dual y-scales are forbidden. Source line on each SVG: not a legal measurement.

| File | Paper sentence | What would fail it on this toy |
|------|----------------|--------------------------------|
| [fig1-hot-vs-null.svg](fig1-hot-vs-null.svg) | HOT concentrates recoverability at planted penumbra | HOT cloud sits on the 0.20 base rate |
| [fig2-g-and-s.svg](fig2-g-and-s.svg) | \(G\) can fall while \(S_\text{known}\) still rises | After acceleration, \(S\) falls whenever \(G\) falls |
| [fig3-searcher-rule.svg](fig3-searcher-rule.svg) | The attack surface is the interface, not the high-volume core | Degree-greedy recovers penumbra as well as spill |
| [fig4-actors.svg](fig4-actors.svg) | Discovery ≠ execution; actor class matters | The three \(S_\text{active}\) paths coincide |
| [fig5-limiters.svg](fig5-limiters.svg) | Does \(G\) fall below 1 fast enough for \(S\) to stabilize? | Every cell plateaus, or none ever has \(G>1\) then \(G\le 1\) |

No figure of the paper’s \(G \approx 10^2\) heuristics.
