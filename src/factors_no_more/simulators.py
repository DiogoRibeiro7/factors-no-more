from __future__ import annotations

from typing import Dict
import numpy as np


def simulate_collider(n: int = 50_000, seed: int = 0) -> Dict[str, np.ndarray]:
    """Generate A -> S <- Y (collider S). Conditioning on S induces spurious A–Y associations."""
    rng = np.random.default_rng(seed)
    A = rng.normal(0, 1, n)
    Y = rng.normal(0, 1, n)
    S = 0.8 * A + 0.8 * Y + rng.normal(0, 1, n)
    return {"A": A, "Y": Y, "S": S}


def simulate_mediator(n: int = 50_000, seed: int = 0) -> Dict[str, np.ndarray]:
    """Generate A -> M -> Y. Adjusting for M over-adjusts the total effect of A on Y."""
    rng = np.random.default_rng(seed)
    A = rng.normal(0, 1, n)
    M = 0.8 * A + rng.normal(0, 1, n)
    Y = 0.8 * M + rng.normal(0, 1, n)
    return {"A": A, "M": M, "Y": Y}