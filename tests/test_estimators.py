from __future__ import annotations

import numpy as np
import pandas as pd

from factors_no_more.causal_spec import CausalSpec
from factors_no_more.estimators import BinaryATEInputs, fit_adjusted_effect, ipw_ate, aipw_ate


def make_toy(n: int = 5000, seed: int = 1) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    age = rng.normal(50, 10, n)
    sex = rng.integers(0, 2, n)
    smoke = rng.integers(0, 2, n)
    # Treatment depends on Z
    pA = 1 / (1 + np.exp(-( -2 + 0.02 * age + 0.5 * sex + 0.7 * smoke )))
    A = rng.binomial(1, pA)
    # Outcome depends on A and Z (linear-Gaussian)
    Y = 2.0 * A + 0.05 * age + 0.2 * sex + 0.3 * smoke + rng.normal(0, 1, n)
    return pd.DataFrame(dict(Y=Y, A=A, age=age, sex=sex, smoking=smoke))


def test_fit_adjusted_effect_runs():
    df = make_toy()
    spec = CausalSpec("A", "Y", ("age", "sex", "smoking"), model="linear")
    coef, ci = fit_adjusted_effect(df, spec)
    assert np.isfinite(coef)
    assert np.isfinite(ci[0]) and np.isfinite(ci[1]) and ci[0] < ci[1]


def test_ipw_and_aipw_close():
    df = make_toy()
    spec = BinaryATEInputs("Y", "A", ("age", "sex", "smoking"))
    ate_ipw, se_ipw = ipw_ate(df, spec)
    ate_aipw, se_aipw = aipw_ate(df, spec)
    # Both should be close to the true effect ~ 2.0
    assert abs(ate_ipw - 2.0) < 0.3
    assert abs(ate_aipw - 2.0) < 0.25