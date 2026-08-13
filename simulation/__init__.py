"""HOT searcher toy for the governance patch-gap paper (companion, not the PDF)."""

from .graph import RuleGraph, generate_hot, generate_null, search_order, penumbra_share
from .dynamics import ActorClass, DynamicsConfig, Episode, run_episode

__all__ = [
    "RuleGraph",
    "generate_hot",
    "generate_null",
    "search_order",
    "penumbra_share",
    "ActorClass",
    "DynamicsConfig",
    "Episode",
    "run_episode",
]
