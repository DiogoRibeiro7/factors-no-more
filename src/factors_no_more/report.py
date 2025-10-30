from __future__ import annotations

from math import sqrt


def effect_markdown(exposure: str, estimand: str, estimate: float, se: float) -> str:
    """Render a minimal, single-target effect report in Markdown."""
    z = 1.96
    lo, hi = estimate - z * se, estimate + z * se
    return (
        f"### Effect of **{exposure}**\n"
        f"- Estimand: {estimand}\n"
        f"- Estimate: {estimate:.4f}\n"
        f"- 95% CI: [{lo:.4f}, {hi:.4f}]\n"
        f"- SE: {se:.4f}\n\n"
        "_Note: Effect is reported only for the prespecified exposure; "
        "mutual-adjustment coefficients for other variables are not presented as findings._"
    )