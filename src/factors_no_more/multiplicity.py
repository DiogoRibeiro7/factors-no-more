from __future__ import annotations

from typing import Iterable, Tuple
import numpy as np


def false_positive_probability(n_tests: int, alpha: float = 0.05) -> float:
    """Probability of ≥1 false positive under global null: 1 - (1 - alpha)^n."""
    if n_tests < 0:
        raise ValueError("n_tests must be non-negative.")
    if not (0 < alpha < 1):
        raise ValueError("alpha must be in (0,1).") 
    return 1.0 - (1.0 - alpha) ** n_tests


def bonferroni_adjust(pvals: Iterable[float], alpha: float = 0.05) -> Tuple[np.ndarray, float]:
    """Bonferroni correction for FWER control.

    Returns:
        adjusted_pvals: np.ndarray of adjusted p-values.
        adjusted_alpha: the Bonferroni alpha threshold (alpha / m).
    """
    p = np.asarray(list(pvals), dtype=float)
    if p.ndim != 1 or p.size == 0:
        raise ValueError("pvals must be a non-empty 1D iterable of floats.")
    if not (0 < alpha < 1):
        raise ValueError("alpha must be in (0,1).") 
    m = p.size
    return np.minimum(p * m, 1.0), alpha / m


def benjamini_hochberg(pvals: Iterable[float], alpha: float = 0.05):
    """Benjamini–Hochberg procedure for FDR control.

    Returns:
        adjusted_pvals: np.ndarray of BH-adjusted p-values.
        reject_mask: boolean np.ndarray indicating which hypotheses are rejected.
    """
    p = np.asarray(list(pvals), dtype=float)
    if p.ndim != 1 or p.size == 0:
        raise ValueError("pvals must be a non-empty 1D iterable of floats.")
    if not (0 < alpha < 1):
        raise ValueError("alpha must be in (0,1).") 

    m = p.size
    order = np.argsort(p)
    ranks = np.arange(1, m + 1, dtype=float)
    p_sorted = p[order]

    # Standard BH adjusted p-values with monotonicity enforcement
    bh_vals = (p_sorted * m) / ranks
    # cumulative min in reverse to ensure non-decreasing adjusted p-values
    bh_adj = np.minimum.accumulate(bh_vals[::-1])[::-1]
    adjusted = np.empty_like(p_sorted)
    adjusted[:] = np.clip(bh_adj, 0.0, 1.0)

    result = np.empty_like(p)
    result[order] = adjusted

    reject = result <= alpha
    return result, reject