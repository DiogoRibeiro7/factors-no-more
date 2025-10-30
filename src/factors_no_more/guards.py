from __future__ import annotations

from typing import Iterable, Sequence

class FactorsAssociatedGuard(Exception):
    """Raised when a 'factors associated with' pattern is detected."""


FORBIDDEN_KEYWORDS: Sequence[str] = ("stepwise", "forward_selection", "backward_elimination")


def validate_against_factors_associated_pattern(
    candidate_exposures: Iterable[str],
    spec,
) -> None:
    """Fail if multiple primary exposures are screened in one model.

    This function enforces analyzing **one prespecified exposure** at a time.
    It should be called at the start of an analysis to catch shotgun screening.

    Raises:
        FactorsAssociatedGuard: if multiple exposures are provided.
        ValueError: if the spec exposure is not among candidates.
    """
    cand = set(candidate_exposures)
    if len(cand) > 1:
        raise FactorsAssociatedGuard(
            "Multiple primary exposures detected. Analyze each exposure with its own "
            "prespecified adjustment set. Stepwise/shotgun screening is disallowed."
        )
    if not cand:
        raise ValueError("No candidate exposures provided.")
    if getattr(spec, "exposure", None) not in cand:
        raise ValueError("Spec exposure not in candidate exposures.")


def forbid_stepwise(config_text: str) -> None:
    """Raise if a config/script hints at stepwise selection.

    Useful in CI pre-flight checks.
    """
    lower = config_text.lower()
    if any(k in lower for k in FORBIDDEN_KEYWORDS):
        raise RuntimeError("Stepwise variable selection is disallowed by protocol.")