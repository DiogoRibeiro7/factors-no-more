from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Tuple
import hashlib

Estimand = Literal["ATE", "ATT", "ATC"]
ModelFamily = Literal["linear", "logistic"]


@dataclass(frozen=True)
class CausalSpec:
    """Minimal causal specification for a single prespecified exposure.

    Args:
        exposure: Name of the exposure variable (A).
        outcome: Name of the outcome variable (Y).
        adjusters: Tuple of prespecified confounders (Z), based on a DAG/protocol.
        model: Model family for outcome regression ('linear' for continuous Y,
            'logistic' for binary Y).
        estimand: Target estimand. Currently used for reporting only.

    Notes:
        - This class encodes the discipline to prespecify exposure/outcome/adjusters.
        - No stepwise selection is permitted downstream.
    """

    exposure: str
    outcome: str
    adjusters: Tuple[str, ...]
    model: ModelFamily = "logistic"
    estimand: Estimand = "ATE"

    def plan_hash(self) -> str:
        """Return a stable SHA-256 hash of the analysis plan."""
        payload = f"{self.exposure}|{self.outcome}|{self.adjusters}|{self.model}|{self.estimand}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()