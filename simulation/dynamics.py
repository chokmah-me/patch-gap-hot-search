"""Stock-flow episode: searcher produces R_d; patcher produces R_p; G and S emerge.

S_known is known-but-unpatched finds. S_active is the executed subset.
Actor class only changes execution speed — not what the searcher can see.

All rates are scenario knobs. They are not measurements of any legislature.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .graph import RuleGraph, search_order

ActorClass = Literal["corporate", "state", "agent"]

# Execution: delay (steps after discovery) and fraction of unpatched finds
# that become active once the delay elapses. Corporate is slow and filtered;
# unsupervised agents are fast and have no principal.
ACTOR_EXEC: dict[ActorClass, tuple[int, float]] = {
    "corporate": (4, 0.20),
    "state": (3, 0.30),
    "agent": (1, 0.65),
}


@dataclass(frozen=True)
class DynamicsConfig:
    steps: int = 40
    base_rd: float = 7.0
    gamma: float = 0.04  # diminishing returns: cost rises with cumulative finds
    base_rp: int = 1
    accel_rp: int = 3
    salience: int = 5  # S_active threshold for legislative acceleration
    accelerate: bool = True
    actor: ActorClass = "agent"


@dataclass
class Episode:
    kind: str
    actor: ActorClass
    accelerate: bool
    rd: list[int] = field(default_factory=list)
    rp: list[int] = field(default_factory=list)
    s_known: list[int] = field(default_factory=list)
    s_active: list[int] = field(default_factory=list)
    g: list[float] = field(default_factory=list)
    accel_on: list[bool] = field(default_factory=list)
    t_accel: int | None = None

    def g_finite(self, t: int) -> float | None:
        if t < 0 or t >= len(self.rp):
            return None
        if self.rp[t] <= 0:
            return None
        return self.rd[t] / self.rp[t]


def _find_budget(base_rd: float, gamma: float, n_found: int, remaining: int) -> int:
    """Finite corpus + diminishing returns. Counted R_d, not an assumed constant."""
    if remaining <= 0:
        return 0
    raw = base_rd / (1.0 + gamma * n_found)
    return max(0, min(remaining, int(round(raw))))


def run_episode(g: RuleGraph, cfg: DynamicsConfig) -> Episode:
    order = search_order(g)
    found: list[int] = []
    unpatched: dict[int, int] = {}  # node -> discovery time
    executed: set[int] = set()
    delay, exec_frac = ACTOR_EXEC[cfg.actor]

    ep = Episode(kind=g.kind, actor=cfg.actor, accelerate=cfg.accelerate)
    s_known = 0
    triggered = False

    for t in range(cfg.steps):
        remaining = [i for i in order if i not in found]
        n_new = _find_budget(cfg.base_rd, cfg.gamma, len(found), len(remaining))
        new_nodes = remaining[:n_new]
        rd = len(new_nodes)
        for i in new_nodes:
            found.append(i)
            unpatched[i] = t

        # Execution of already-known unpatched finds (after actor delay).
        eligible = [i for i, t0 in unpatched.items() if i not in executed and t - t0 >= delay]
        n_exec = int(round(exec_frac * len(eligible)))
        # Deterministic subset: highest interface rank among eligible.
        rank = {node: r for r, node in enumerate(order)}
        eligible.sort(key=lambda i: rank[i])
        for i in eligible[:n_exec]:
            executed.add(i)
        s_active = len(executed)

        # Acceleration is sticky: a salience spike speeds the patcher for
        # the rest of the episode (ECRA-style, not a one-step flicker).
        if cfg.accelerate and s_active >= cfg.salience and not triggered:
            ep.t_accel = t
            triggered = True
        accel = bool(cfg.accelerate and triggered)
        rp_cap = cfg.accel_rp if accel else cfg.base_rp
        rp = min(rp_cap, s_known + rd)

        # Stock update after simultaneous discover + patch.
        s_known = s_known + rd - rp

        # Patches close the oldest unpatched finds (human queue).
        if rp:
            oldest = sorted(unpatched, key=lambda i: (unpatched[i], i))[:rp]
            for i in oldest:
                unpatched.pop(i, None)
                executed.discard(i)
            s_active = len(executed)

        if rp > 0:
            g_t = rd / rp
        else:
            g_t = float("inf") if rd > 0 else 0.0

        ep.rd.append(rd)
        ep.rp.append(rp)
        ep.s_known.append(s_known)
        ep.s_active.append(s_active)
        ep.g.append(g_t)
        ep.accel_on.append(accel)

    return ep
