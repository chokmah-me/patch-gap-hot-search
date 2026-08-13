"""Stdlib SVG snapshots. Not load-bearing. Gate does not depend on these files."""

from __future__ import annotations

from pathlib import Path
from random import Random

from .dynamics import DynamicsConfig, run_episode
from .graph import generate_hot, generate_null, penumbra_share, search_order

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"

W, H = 720, 360
PAD = 48


def _polyline(xs: list[float], ys: list[float], xmin, xmax, ymin, ymax, color: str) -> str:
    if not xs:
        return ""
    def sx(x: float) -> float:
        return PAD + (W - 2 * PAD) * (x - xmin) / (xmax - xmin or 1)
    def sy(y: float) -> float:
        return H - PAD - (H - 2 * PAD) * (y - ymin) / (ymax - ymin or 1)
    pts = " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in zip(xs, ys))
    return f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{pts}"/>'


def _svg(body: str, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">\n'
        f'<rect width="100%" height="100%" fill="#fff"/>\n'
        f'<text x="{PAD}" y="24" font-family="system-ui,sans-serif" font-size="14">{title}</text>\n'
        f"{body}\n</svg>\n"
    )


def write_hot_vs_null(path: Path, n_seeds: int = 20, budget: int = 20) -> None:
    rng = Random(20260812)
    hot, null = [], []
    for s in range(n_seeds):
        gh = generate_hot(Random(rng.randrange(2**31)))
        gn = generate_null(Random(rng.randrange(2**31)), n_edges=gh.n_edges)
        hot.append(penumbra_share(gh, search_order(gh), budget))
        null.append(penumbra_share(gn, search_order(gn), budget))
    # Bar pair of means
    mh = sum(hot) / len(hot)
    mn = sum(null) / len(null)
    y0 = H - PAD
    hmax = H - 2 * PAD
    bh = hmax * mh
    bn = hmax * mn
    body = (
        f'<rect x="180" y="{y0 - bh:.1f}" width="120" height="{bh:.1f}" fill="#1d4ed8"/>\n'
        f'<rect x="400" y="{y0 - bn:.1f}" width="120" height="{bn:.1f}" fill="#6b7280"/>\n'
        f'<text x="180" y="{H - 16}" font-family="system-ui,sans-serif" font-size="12">'
        f"HOT mean {mh:.2f}</text>\n"
        f'<text x="400" y="{H - 16}" font-family="system-ui,sans-serif" font-size="12">'
        f"null mean {mn:.2f}</text>\n"
        f'<text x="{PAD}" y="{H - 8}" font-family="system-ui,sans-serif" font-size="10" fill="#666">'
        f"penumbra share of top-{budget} interface-ranked nodes, {n_seeds} seeds</text>"
    )
    path.write_text(_svg(body, "Claim 1 snapshot — HOT vs uniform-null (not a legal measurement)"), encoding="utf-8")


def write_g_drops_s_rises(path: Path) -> None:
    g = generate_hot(Random(20260812))
    ep = run_episode(g, DynamicsConfig(accelerate=True, actor="agent"))
    xs = list(range(len(ep.s_known)))
    smax = max(ep.s_known + [1])
    # Finite G only
    g_vals = []
    for t, val in enumerate(ep.g):
        if ep.rp[t] > 0 and val != float("inf"):
            g_vals.append(val)
        else:
            g_vals.append(None)
    finite = [v for v in g_vals if v is not None]
    gmax = max(finite + [1.0])
    s_line = _polyline(
        [float(x) for x in xs],
        [float(v) for v in ep.s_known],
        0,
        max(xs),
        0,
        smax,
        "#111827",
    )
    gx = [float(t) for t, v in enumerate(g_vals) if v is not None]
    gy = [float(v) for v in g_vals if v is not None]
    g_line = _polyline(gx, gy, 0, max(xs), 0, gmax, "#b45309")
    mark = ""
    if ep.t_accel is not None:
        x = PAD + (W - 2 * PAD) * ep.t_accel / (max(xs) or 1)
        mark = (
            f'<line x1="{x:.1f}" y1="{PAD}" x2="{x:.1f}" y2="{H - PAD}" '
            f'stroke="#dc2626" stroke-dasharray="4 3"/>'
        )
    body = (
        f"{s_line}\n{g_line}\n{mark}\n"
        f'<text x="{PAD}" y="{H - 12}" font-family="system-ui,sans-serif" font-size="10" fill="#666">'
        f"black = S_known (left-scaled) · amber = G = Rd/Rp where Rp&gt;0 · dashed = acceleration onset</text>"
    )
    path.write_text(
        _svg(body, "Claim 3 snapshot — G can fall while S_known still rises (scenario knobs)"),
        encoding="utf-8",
    )


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    write_hot_vs_null(FIG / "hot-vs-null-share.svg")
    write_g_drops_s_rises(FIG / "g-drops-s-rises.svg")
    print(f"wrote {FIG / 'hot-vs-null-share.svg'}")
    print(f"wrote {FIG / 'g-drops-s-rises.svg'}")


if __name__ == "__main__":
    main()
