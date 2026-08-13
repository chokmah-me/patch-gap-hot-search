"""Tufte-leaning SVG figures. Stdlib only. Not load-bearing for the claim gate."""

from __future__ import annotations

from pathlib import Path
from random import Random
from xml.sax.saxutils import escape

from .dynamics import DynamicsConfig, run_episode
from .graph import RuleGraph, generate_hot, generate_null, penumbra_share, search_order

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"

FONT = "Georgia, 'Times New Roman', serif"
INK = "#222222"
MUTED = "#777777"
RULE = "#b0b0b0"
ACCENT = "#a34a12"
MASTER = 20260812
NOTE = "Toy. Scenario knobs. Not a measurement of any legal system."


def degree_order(g: RuleGraph) -> list[int]:
    """Degree-greedy rank — the searcher that recovered HOT hubs, not bridges."""
    return sorted(range(g.n), key=lambda i: (g.degree(i), i), reverse=True)


class Frame:
    def __init__(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        xmin: float,
        xmax: float,
        ymin: float,
        ymax: float,
    ) -> None:
        self.x, self.y, self.w, self.h = x, y, w, h
        self.xmin, self.xmax = xmin, xmax
        self.ymin, self.ymax = ymin, ymax

    def px(self, v: float) -> float:
        return self.x + self.w * (v - self.xmin) / (self.xmax - self.xmin or 1)

    def py(self, v: float) -> float:
        return self.y + self.h * (1 - (v - self.ymin) / (self.ymax - self.ymin or 1))

    def axes(
        self,
        xticks: list[float],
        yticks: list[float],
        xlabel: str,
        ylabel: str,
        xfmt: str = "{:g}",
        yfmt: str = "{:g}",
        xticklabels: list[str] | None = None,
        show_xlabels: bool = True,
    ) -> str:
        x0, y0 = self.x, self.y + self.h
        x1, y1 = self.x + self.w, self.y
        parts = [
            f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y0:.1f}" '
            f'stroke="{INK}" stroke-width="0.8"/>',
            f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x0:.1f}" y2="{y1:.1f}" '
            f'stroke="{INK}" stroke-width="0.8"/>',
        ]
        for i, t in enumerate(xticks):
            px = self.px(t)
            parts.append(
                f'<line x1="{px:.1f}" y1="{y0:.1f}" x2="{px:.1f}" y2="{y0 + 4:.1f}" '
                f'stroke="{INK}" stroke-width="0.7"/>'
            )
            if show_xlabels:
                lab = xticklabels[i] if xticklabels is not None else xfmt.format(t)
                parts.append(
                    f'<text x="{px:.1f}" y="{y0 + 15:.1f}" text-anchor="middle" '
                    f'font-family="{FONT}" font-size="10" fill="{INK}">{escape(lab)}</text>'
                )
        for t in yticks:
            py = self.py(t)
            parts.append(
                f'<line x1="{x0:.1f}" y1="{py:.1f}" x2="{x0 - 4:.1f}" y2="{py:.1f}" '
                f'stroke="{INK}" stroke-width="0.7"/>'
            )
            parts.append(
                f'<text x="{x0 - 7:.1f}" y="{py + 3.5:.1f}" text-anchor="end" '
                f'font-family="{FONT}" font-size="10" fill="{INK}">{yfmt.format(t)}</text>'
            )
        parts.append(
            f'<text x="{self.x + self.w / 2:.1f}" y="{y0 + 30:.1f}" text-anchor="middle" '
            f'font-family="{FONT}" font-size="11" fill="{INK}">{escape(xlabel)}</text>'
        )
        cx, cy = self.x - 42, self.y + self.h / 2
        parts.append(
            f'<text x="{cx:.1f}" y="{cy:.1f}" text-anchor="middle" '
            f'font-family="{FONT}" font-size="11" fill="{INK}" '
            f'transform="rotate(-90 {cx:.1f} {cy:.1f})">{escape(ylabel)}</text>'
        )
        return "\n".join(parts)

    def hline(self, y: float, label: str = "", dash: str = "2 2") -> str:
        y0, y1 = self.y, self.y + self.h
        py = min(max(self.py(y), y0), y1)
        bits = [
            f'<line x1="{self.x:.1f}" y1="{py:.1f}" x2="{self.x + self.w:.1f}" '
            f'y2="{py:.1f}" stroke="{MUTED}" stroke-width="0.6" stroke-dasharray="{dash}"/>'
        ]
        if label:
            bits.append(
                f'<text x="{self.x + self.w + 4:.1f}" y="{py + 3:.1f}" '
                f'font-family="{FONT}" font-size="9" fill="{MUTED}">{escape(label)}</text>'
            )
        return "\n".join(bits)

    def vline(self, x: float, label: str = "") -> str:
        px = self.px(x)
        bits = [
            f'<line x1="{px:.1f}" y1="{self.y:.1f}" x2="{px:.1f}" '
            f'y2="{self.y + self.h:.1f}" stroke="{MUTED}" stroke-width="0.6" '
            f'stroke-dasharray="2 2"/>'
        ]
        if label:
            bits.append(
                f'<text x="{px + 3:.1f}" y="{self.y + 11:.1f}" '
                f'font-family="{FONT}" font-size="9" fill="{MUTED}">{escape(label)}</text>'
            )
        return "\n".join(bits)

    def polyline(self, xs: list[float], ys: list[float], color: str = INK, width: float = 1.2) -> str:
        pts = " ".join(f"{self.px(x):.1f},{self.py(y):.1f}" for x, y in zip(xs, ys))
        return (
            f'<polyline fill="none" stroke="{color}" stroke-width="{width}" '
            f'stroke-linejoin="round" stroke-linecap="round" points="{pts}"/>'
        )

    def dots(self, xs: list[float], ys: list[float], color: str = INK, r: float = 2.2) -> str:
        return "\n".join(
            f'<circle cx="{self.px(x):.1f}" cy="{self.py(y):.1f}" r="{r}" '
            f'fill="{color}" fill-opacity="0.85"/>'
            for x, y in zip(xs, ys)
        )

    def htick(self, x: float, y: float, half: float, color: str = INK) -> str:
        return (
            f'<line x1="{self.px(x - half):.1f}" y1="{self.py(y):.1f}" '
            f'x2="{self.px(x + half):.1f}" y2="{self.py(y):.1f}" '
            f'stroke="{color}" stroke-width="1.6"/>'
        )


def _svg(w: float, h: float, title: str, body: str, source: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
        f'viewBox="0 0 {w:.0f} {h:.0f}">\n'
        f'<rect width="100%" height="100%" fill="#fff"/>\n'
        f'<text x="28" y="26" font-family="{FONT}" font-size="13.5" fill="{INK}">'
        f"{escape(title)}</text>\n"
        f"{body}\n"
        f'<text x="28" y="{h - 10:.1f}" font-family="{FONT}" font-size="9" fill="{MUTED}">'
        f"{escape(source)}</text>\n"
        f"</svg>\n"
    )


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else float("nan")


def _nice_ticks(lo: float, hi: float, n: int = 5) -> list[float]:
    if hi <= lo:
        return [lo]
    span = hi - lo
    step = span / max(n - 1, 1)
    # prefer 1-2-5
    mag = 10 ** (len(str(int(step))) - 1) if step >= 1 else 10 ** (-2)
    for m in (1, 2, 5, 10):
        cand = m * mag
        if cand >= step * 0.6:
            step = cand
            break
    start = int(lo / step) * step
    out = []
    v = start
    while v <= hi + step * 0.01:
        if v >= lo - step * 0.01:
            out.append(round(v, 6))
        v += step
    if out and out[0] > lo + 1e-9:
        out.insert(0, lo)
    if out and out[-1] < hi - 1e-9:
        out.append(hi)
    return out


def write_fig1(path: Path, n_seeds: int = 20, budget: int = 20) -> None:
    rng = Random(MASTER)
    hot, null = [], []
    for _ in range(n_seeds):
        gh = generate_hot(Random(rng.randrange(2**31)))
        gn = generate_null(Random(rng.randrange(2**31)), n_edges=gh.n_edges)
        hot.append(penumbra_share(gh, search_order(gh), budget))
        null.append(penumbra_share(gn, search_order(gn), budget))
    j = Random(MASTER + 1)
    hx = [0.0 + j.uniform(-0.12, 0.12) for _ in hot]
    nx = [1.0 + j.uniform(-0.12, 0.12) for _ in null]
    fr = Frame(80, 48, 520, 280, -0.45, 1.45, 0, 1)
    body = "\n".join(
        [
            fr.axes(
                [0, 1],
                [0, 0.2, 0.4, 0.6, 0.8, 1.0],
                "",
                "penumbra share of top-20 finds",
                xticklabels=["HOT generator", "uniform-null"],
            ),
            fr.hline(0.20, "label base rate 0.20"),
            fr.dots(hx, hot, INK),
            fr.dots(nx, null, MUTED),
            fr.htick(0.0, _mean(hot), 0.16, ACCENT),
            fr.htick(1.0, _mean(null), 0.16, ACCENT),
            f'<text x="{fr.px(0) + 18:.1f}" y="{fr.py(_mean(hot)) - 6:.1f}" '
            f'font-family="{FONT}" font-size="10" fill="{ACCENT}">mean {_mean(hot):.2f}</text>',
            f'<text x="{fr.px(1) + 18:.1f}" y="{fr.py(_mean(null)) - 6:.1f}" '
            f'font-family="{FONT}" font-size="10" fill="{ACCENT}">mean {_mean(null):.2f}</text>',
        ]
    )
    path.write_text(
        _svg(
            700,
            390,
            "Interface search recovers planted penumbra on HOT graphs, not on random labels",
            body,
            f"{NOTE}  n = {n_seeds} paired seeds.  Searcher never sees the penumbra label.  "
            f"Accent bar = mean.",
        ),
        encoding="utf-8",
    )


def write_fig2(path: Path) -> None:
    g = generate_hot(Random(MASTER))
    ep = run_episode(g, DynamicsConfig(accelerate=True, actor="agent"))
    xs = [float(t) for t in range(len(ep.s_known))]
    g_y = [ep.g[t] if ep.rp[t] > 0 and ep.g[t] != float("inf") else 0.0 for t in range(len(ep.g))]
    gmax = max(g_y + [1.0])
    smax = max(ep.s_known + [1])
    top = Frame(72, 46, 560, 150, 0, max(xs), 0, gmax * 1.05)
    bot = Frame(72, 230, 560, 150, 0, max(xs), 0, smax * 1.08)
    xt = [0, 10, 20, 30, 39]
    t_acc = ep.t_accel if ep.t_accel is not None else -1
    body = "\n".join(
        [
            top.axes(xt, [0, 2, 4, 6], "", "G = Rd / Rp", show_xlabels=False),
            top.hline(1.0, "G = 1"),
            top.polyline(xs, g_y, ACCENT, 1.3),
            (top.vline(float(t_acc), "acceleration") if t_acc >= 0 else ""),
            bot.axes(xt, [0, 5, 10, 15], "time step", "S known (count)"),
            bot.polyline(xs, [float(v) for v in ep.s_known], INK, 1.3),
            (bot.vline(float(t_acc)) if t_acc >= 0 else ""),
        ]
    )
    path.write_text(
        _svg(
            700,
            430,
            "G can fall after a salience spike while the known-unpatched stock still rises",
            body,
            f"{NOTE}  One HOT episode, actor = unsupervised agent, sticky acceleration.  "
            f"Shared time axis; not a dual-scale overlay.",
        ),
        encoding="utf-8",
    )


def write_fig3(path: Path, n_seeds: int = 20, budget: int = 20) -> None:
    rng = Random(MASTER)
    spill, deg = [], []
    for _ in range(n_seeds):
        gh = generate_hot(Random(rng.randrange(2**31)))
        spill.append(penumbra_share(gh, search_order(gh), budget))
        deg.append(penumbra_share(gh, degree_order(gh), budget))
    j = Random(MASTER + 3)
    sx = [0.0 + j.uniform(-0.12, 0.12) for _ in spill]
    dx = [1.0 + j.uniform(-0.12, 0.12) for _ in deg]
    fr = Frame(80, 48, 520, 280, -0.45, 1.45, 0, 1)
    body = "\n".join(
        [
            fr.axes(
                [0, 1],
                [0, 0.2, 0.4, 0.6, 0.8, 1.0],
                "",
                "penumbra share of top-20 finds",
                xticklabels=["spill rank", "degree-greedy"],
            ),
            fr.hline(0.20, "label base rate 0.20"),
            fr.dots(sx, spill, INK),
            fr.dots(dx, deg, MUTED),
            fr.htick(0.0, _mean(spill), 0.16, ACCENT),
            fr.htick(1.0, _mean(deg), 0.16, ACCENT),
            f'<text x="{fr.px(0) + 18:.1f}" y="{fr.py(_mean(spill)) - 6:.1f}" '
            f'font-family="{FONT}" font-size="10" fill="{ACCENT}">mean {_mean(spill):.2f}</text>',
            f'<text x="{fr.px(1) + 18:.1f}" y="{fr.py(_mean(deg)) - 6:.1f}" '
            f'font-family="{FONT}" font-size="10" fill="{ACCENT}">mean {_mean(deg):.2f}</text>',
        ]
    )
    path.write_text(
        _svg(
            700,
            390,
            "On the same HOT graphs, degree-greedy finds the robust core; spill finds the bridge",
            body,
            f"{NOTE}  Paired ranks on identical graphs, n = {n_seeds}.  "
            f"Degree-greedy was the first failed gate run.",
        ),
        encoding="utf-8",
    )


def write_fig4(path: Path) -> None:
    g = generate_hot(Random(MASTER))
    actors = ("corporate", "state", "agent")
    labels = {
        "corporate": "corporate (slow, filtered)",
        "state": "state (medium)",
        "agent": "unsupervised agent",
    }
    eps = {
        a: run_episode(g, DynamicsConfig(accelerate=True, actor=a))  # type: ignore[arg-type]
        for a in actors
    }
    smax = max(max(ep.s_known + ep.s_active) for ep in eps.values())
    xs = [float(t) for t in range(len(eps["corporate"].s_known))]
    xt = [0, 20, 39]
    panels = []
    for i, a in enumerate(actors):
        fr = Frame(70 + i * 210, 56, 175, 240, 0, max(xs), 0, smax * 1.08)
        ep = eps[a]
        panels.append(
            "\n".join(
                [
                    f'<text x="{fr.x + fr.w / 2:.1f}" y="{fr.y - 10:.1f}" text-anchor="middle" '
                    f'font-family="{FONT}" font-size="11" fill="{INK}">{escape(labels[a])}</text>',
                    fr.axes(
                        xt,
                        _nice_ticks(0, smax, 4),
                        "time step",
                        "stock (count)" if i == 0 else "",
                    ),
                    fr.polyline(xs, [float(v) for v in ep.s_known], INK, 1.2),
                    fr.polyline(xs, [float(v) for v in ep.s_active], ACCENT, 1.2),
                    (
                        f'<text x="{fr.x + 8:.1f}" y="{fr.y + 12:.1f}" '
                        f'font-family="{FONT}" font-size="9" fill="{INK}">known</text>\n'
                        f'<text x="{fr.x + 8:.1f}" y="{fr.y + 24:.1f}" '
                        f'font-family="{FONT}" font-size="9" fill="{ACCENT}">active</text>'
                        if i == 0
                        else ""
                    ),
                ]
            )
        )
    path.write_text(
        _svg(
            720,
            360,
            "Same discoveries; execution stock depends on who acts",
            "\n".join(panels),
            f"{NOTE}  One HOT graph, three actor filters.  Discovery ranking is identical.  "
            f"Shared y scale.",
        ),
        encoding="utf-8",
    )


def _last_g_above_one(ep) -> int | None:
    last = None
    for t, val in enumerate(ep.g):
        if ep.rp[t] > 0 and val != float("inf") and val > 1:
            last = t
    return last


def write_fig5(path: Path) -> None:
    g = generate_hot(Random(MASTER))
    cells = [
        (0.0, False, "no diminishing returns", "no acceleration"),
        (0.0, True, "no diminishing returns", "sticky acceleration"),
        (0.04, False, "diminishing returns", "no acceleration"),
        (0.04, True, "diminishing returns", "sticky acceleration"),
    ]
    eps = []
    smax = 1
    for gamma, acc, _, _ in cells:
        ep = run_episode(g, DynamicsConfig(gamma=gamma, accelerate=acc, actor="agent"))
        eps.append(ep)
        smax = max(smax, max(ep.s_known))
    xs = [float(t) for t in range(len(eps[0].s_known))]
    xt = [0, 20, 39]
    panels = []
    for i, ((gamma, acc, rlab, clab), ep) in enumerate(zip(cells, eps)):
        col, row = i % 2, i // 2
        fr = Frame(78 + col * 300, 58 + row * 195, 240, 145, 0, max(xs), 0, smax * 1.08)
        last = _last_g_above_one(ep)
        extra = ""
        if last is not None:
            extra = fr.vline(float(last), f"G>1 until t={last}")
        panels.append(
            "\n".join(
                [
                    f'<text x="{fr.x + fr.w / 2:.1f}" y="{fr.y - 12:.1f}" text-anchor="middle" '
                    f'font-family="{FONT}" font-size="10.5" fill="{INK}">'
                    f"{escape(rlab)} · {escape(clab)}</text>",
                    fr.axes(
                        xt,
                        _nice_ticks(0, smax, 4),
                        "time step" if row == 1 else "",
                        "S known" if col == 0 else "",
                    ),
                    fr.polyline(xs, [float(v) for v in ep.s_known], INK, 1.2),
                    extra,
                ]
            )
        )
    path.write_text(
        _svg(
            700,
            500,
            "Whether S stabilizes depends on which limiter is on — the paper’s open question, on this toy",
            "\n".join(panels),
            f"{NOTE}  One HOT graph, actor = agent.  Vertical hairline = last step with G > 1.  "
            f"If every cell plateaus, or none ever crosses G = 1, the limiter story fails here.",
        ),
        encoding="utf-8",
    )


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    # retire the unlabeled snapshots
    for stale in ("hot-vs-null-share.svg", "g-drops-s-rises.svg"):
        p = FIG / stale
        if p.exists():
            p.unlink()
    write_fig1(FIG / "fig1-hot-vs-null.svg")
    write_fig2(FIG / "fig2-g-and-s.svg")
    write_fig3(FIG / "fig3-searcher-rule.svg")
    write_fig4(FIG / "fig4-actors.svg")
    write_fig5(FIG / "fig5-limiters.svg")
    for name in (
        "fig1-hot-vs-null.svg",
        "fig2-g-and-s.svg",
        "fig3-searcher-rule.svg",
        "fig4-actors.svg",
        "fig5-limiters.svg",
    ):
        print(f"wrote {FIG / name}")


if __name__ == "__main__":
    main()
