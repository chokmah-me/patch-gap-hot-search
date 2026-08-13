"""Synthetic rule graphs: HOT (planted interface penumbra) vs uniform-null.

No real statute text. Nodes are toy rules. The searcher never sees the
penumbra label; it ranks by neighborhood *spill* (how evenly neighbors
sit in more than one module). That is the §5.2 cross-reference signal,
not a degree-greedy crawl of the well-specified core.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from random import Random


@dataclass(frozen=True)
class RuleGraph:
    n_core: int
    n_penumbra: int
    n_modules: int
    modules: tuple[int, ...]
    is_penumbra: tuple[bool, ...]
    adj: tuple[frozenset[int], ...]
    kind: str

    @property
    def n(self) -> int:
        return self.n_core + self.n_penumbra

    @property
    def n_edges(self) -> int:
        return sum(len(nbrs) for nbrs in self.adj) // 2

    def degree(self, i: int) -> int:
        return len(self.adj[i])

    def neighbor_modules(self, i: int) -> set[int]:
        return {self.modules[j] for j in self.adj[i]}


def _undirected(n: int, edge_set: set[tuple[int, int]]) -> tuple[frozenset[int], ...]:
    buckets: list[set[int]] = [set() for _ in range(n)]
    for a, b in edge_set:
        if a == b:
            continue
        buckets[a].add(b)
        buckets[b].add(a)
    return tuple(frozenset(s) for s in buckets)


def _core_slices(n_core: int, n_modules: int) -> list[list[int]]:
    sizes = [n_core // n_modules] * n_modules
    for i in range(n_core % n_modules):
        sizes[i] += 1
    out: list[list[int]] = []
    start = 0
    for sz in sizes:
        out.append(list(range(start, start + sz)))
        start += sz
    return out


def generate_hot(
    rng: Random,
    *,
    n_core: int = 80,
    n_penumbra: int = 20,
    n_modules: int = 8,
    p_intra: float = 0.45,
    bridges_per_penumbra: int = 2,
    stubs_per_module: int = 2,
) -> RuleGraph:
    """Modules are dense cores. Penumbra nodes are planted as cross-module bridges.

    Common-case disputes stay inside a module (HOT tolerance). Residual
    open-texture lives on the interfaces — the RYF boundary.
    """
    if n_modules < 2:
        raise ValueError("n_modules must be >= 2")
    if n_core < n_modules:
        raise ValueError("need at least one core node per module")
    if bridges_per_penumbra < 2:
        raise ValueError("penumbra must touch at least two modules")

    n = n_core + n_penumbra
    slices = _core_slices(n_core, n_modules)
    modules = [0] * n
    is_penumbra = [False] * n
    for m, nodes in enumerate(slices):
        for i in nodes:
            modules[i] = m

    edges: set[tuple[int, int]] = set()
    for nodes in slices:
        for a_i, a in enumerate(nodes):
            for b in nodes[a_i + 1 :]:
                if rng.random() < p_intra:
                    edges.add((a, b) if a < b else (b, a))

    # Penumbra ids sit after the core block. Home module is assigned for
    # bookkeeping; edges go to hubs in `bridges_per_penumbra` distinct modules.
    for k in range(n_penumbra):
        p = n_core + k
        is_penumbra[p] = True
        home = k % n_modules
        modules[p] = home
        others = [m for m in range(n_modules) if m != home]
        rng.shuffle(others)
        touch = [home] + others[: bridges_per_penumbra - 1]
        for m in touch:
            hubs = list(slices[m])
            rng.shuffle(hubs)
            for h in hubs[:stubs_per_module]:
                a, b = (p, h) if p < h else (h, p)
                edges.add((a, b))

    return RuleGraph(
        n_core=n_core,
        n_penumbra=n_penumbra,
        n_modules=n_modules,
        modules=tuple(modules),
        is_penumbra=tuple(is_penumbra),
        adj=_undirected(n, edges),
        kind="hot",
    )


def generate_null(
    rng: Random,
    *,
    n_core: int = 80,
    n_penumbra: int = 20,
    n_modules: int = 8,
    n_edges: int,
) -> RuleGraph:
    """Same size and edge count; random edges; penumbra labels assigned at random.

    Module ids are still striped by index so an interface score is defined.
    Labels are independent of that structure.
    """
    n = n_core + n_penumbra
    if n_edges < 0:
        raise ValueError("n_edges must be >= 0")
    max_edges = n * (n - 1) // 2
    n_edges = min(n_edges, max_edges)

    modules = tuple(i % n_modules for i in range(n))
    labels = [False] * n
    chosen = list(range(n))
    rng.shuffle(chosen)
    for i in chosen[:n_penumbra]:
        labels[i] = True

    edges: set[tuple[int, int]] = set()
    # Rejection sampling is fine at these sizes; fall back to shuffle of all
    # pairs only if we somehow stall (dense graphs).
    stall = 0
    while len(edges) < n_edges:
        a = rng.randrange(n)
        b = rng.randrange(n)
        if a == b:
            stall += 1
            if stall > 10_000:
                break
            continue
        edge = (a, b) if a < b else (b, a)
        if edge in edges:
            stall += 1
            if stall > 10_000:
                break
            continue
        edges.add(edge)
        stall = 0

    if len(edges) < n_edges:
        all_pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if (i, j) not in edges]
        rng.shuffle(all_pairs)
        for e in all_pairs[: n_edges - len(edges)]:
            edges.add(e)

    return RuleGraph(
        n_core=n_core,
        n_penumbra=n_penumbra,
        n_modules=n_modules,
        modules=modules,
        is_penumbra=tuple(labels),
        adj=_undirected(n, edges),
        kind="null",
    )


def interface_score(g: RuleGraph, i: int) -> tuple[float, int, int]:
    """Spill, then n_modules touched, then a small degree tie-break.

    Spill is 1 − (largest neighbor-module share). Robust HOT hubs have
    high degree but almost all neighbors inside one module, so spill is
    low. Planted bridges split their few edges across modules, so spill
    is high. The searcher does not see the penumbra label.
    """
    nbrs = g.adj[i]
    if not nbrs:
        return (0.0, 0, 0)
    counts = Counter(g.modules[j] for j in nbrs)
    majority = max(counts.values())
    spill = 1.0 - majority / len(nbrs)
    return (spill, len(counts), len(nbrs))


def search_order(g: RuleGraph) -> list[int]:
    """Budgeted combinatorial ranking: high spill first. Not an LLM."""
    return sorted(range(g.n), key=lambda i: interface_score(g, i), reverse=True)


def penumbra_share(g: RuleGraph, ranked: list[int], budget: int) -> float:
    if budget <= 0:
        return 0.0
    picked = ranked[: min(budget, len(ranked))]
    if not picked:
        return 0.0
    return sum(1 for i in picked if g.is_penumbra[i]) / len(picked)
