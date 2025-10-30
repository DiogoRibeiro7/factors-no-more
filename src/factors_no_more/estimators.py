from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np
import pandas as pd
import statsmodels.api as sm


@dataclass(frozen=True)
class BinaryATEInputs:
    """Inputs for binary-treatment ATE estimators.

    Args:
        y_col: Outcome column (numeric).
        a_col: Binary treatment column (0/1).
        z_cols: Prespecified confounders used in the propensity/outcome models.
    """
    y_col: str
    a_col: str
    z_cols: Tuple[str, ...]


def _check_binary(a: np.ndarray) -> None:
    u = np.unique(a)
    if u.size > 2 or not np.all(np.isin(u, [0, 1])):
        raise ValueError("Treatment must be binary {0,1} after preprocessing.")


def fit_adjusted_effect(df: pd.DataFrame, spec) -> Tuple[float, Tuple[float, float]]:
    """Adjusted regression effect for one prespecified exposure (Table-2 safe).

    For logistic: returns log-odds coefficient and 95% CI for the exposure.
    For linear: returns slope and 95% CI.

    Notes:
        - Only the prespecified exposure's effect is returned.
        - No stepwise variable selection is performed here.
    """
    from factors_no_more.causal_spec import CausalSpec  # local import to avoid cycles
    if not isinstance(spec, CausalSpec):
        raise TypeError("spec must be a CausalSpec instance.")

    cols = (spec.outcome, spec.exposure, *spec.adjusters)
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"Missing columns: {missing}")

    dfx = df[list(cols)].dropna(axis=0, how="any")
    y = dfx[spec.outcome].to_numpy()
    X = dfx[[spec.exposure, *spec.adjusters]]
    X = sm.add_constant(X, has_constant="add")  # add intercept if absent

    if spec.model == "logistic":
        model = sm.Logit(y, X)
    elif spec.model == "linear":
        model = sm.OLS(y, X)
    else:
        raise ValueError(f"Unsupported model family: {spec.model!r}")

    res = model.fit(disp=False)
    coef = float(res.params[spec.exposure])
    ci_low, ci_high = map(float, res.conf_int().loc[spec.exposure])
    return coef, (ci_low, ci_high)


def ipw_ate(df: pd.DataFrame, spec: BinaryATEInputs) -> Tuple[float, float]:
    """Inverse Probability Weighting (stabilized) for ATE.

    Returns:
        ate: Average treatment effect.
        se:  Robust standard error (sandwich via influence-function approximation).
    """
    cols = (spec.y_col, spec.a_col, *spec.z_cols)
    if any(c not in df.columns for c in cols):
        missing = [c for c in cols if c not in df.columns]
        raise KeyError(f"Missing columns: {missing}")

    d = df[list(cols)].dropna()
    y = d[spec.y_col].to_numpy(dtype=float)
    a = d[spec.a_col].to_numpy(dtype=float)
    _check_binary(a)

    Z = sm.add_constant(d[list(spec.z_cols)], has_constant="add")
    ps = sm.Logit(a, Z).fit(disp=False).predict(Z)
    eps = 1e-6
    ps = np.clip(ps, eps, 1 - eps)

    pA = float(a.mean())
    w = np.where(a == 1, pA / ps, (1 - pA) / (1 - ps))

    y1 = (w * a * y).sum() / (w * a).sum()
    y0 = (w * (1 - a) * y).sum() / (w * (1 - a)).sum()
    ate = float(y1 - y0)

    EwA = float((w * a).mean())
    Ew0 = float((w * (1 - a)).mean())
    infl = w * ((a * (y - y1)) / (EwA + eps) - ((1 - a) * (y - y0)) / (Ew0 + eps))
    se = float(np.sqrt(np.var(infl, ddof=1) / len(infl)))
    return ate, se


def aipw_ate(df: pd.DataFrame, spec: BinaryATEInputs) -> Tuple[float, float]:
    """Augmented IPW (doubly robust) for ATE."""
    cols = (spec.y_col, spec.a_col, *spec.z_cols)
    d = df[list(cols)].dropna()
    y = d[spec.y_col].to_numpy(dtype=float)
    a = d[spec.a_col].to_numpy(dtype=float)
    _check_binary(a)

    Z = sm.add_constant(d[list(spec.z_cols)], has_constant="add")
    ps = sm.Logit(a, Z).fit(disp=False).predict(Z)
    eps = 1e-6
    ps = np.clip(ps, eps, 1 - eps)

    X1 = sm.add_constant(pd.concat([pd.Series(1, index=d.index, name="A"), d[list(spec.z_cols)]], axis=1), has_constant="add")
    X0 = sm.add_constant(pd.concat([pd.Series(0, index=d.index, name="A"), d[list(spec.z_cols)]], axis=1), has_constant="add")
    X = sm.add_constant(pd.concat([d[[spec.a_col]], d[list(spec.z_cols)]], axis=1), has_constant="add")

    yhat = sm.OLS(y, X).fit(disp=False).predict(X)
    mu1 = sm.OLS(y, X1).fit(disp=False).predict(X1)
    mu0 = sm.OLS(y, X0).fit(disp=False).predict(X0)

    term1 = mu1 - mu0
    term2 = a * (y - mu1) / ps
    term3 = (1 - a) * (y - mu0) / (1 - ps)
    psi = term1 + term2 - term3

    ate = float(np.mean(psi))
    se = float(np.sqrt(np.var(psi, ddof=1) / len(psi)))
    return ate, se