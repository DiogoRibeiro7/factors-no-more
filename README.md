# factors-no-more

[![CI](https://github.com/your-org/factors-no-more/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/factors-no-more/actions/workflows/ci.yml) [![Docs](https://github.com/your-org/factors-no-more/actions/workflows/pages.yml/badge.svg)](https://github.com/your-org/factors-no-more/actions/workflows/pages.yml) [![codecov](https://codecov.io/gh/your-org/factors-no-more/branch/main/graph/badge.svg)](https://codecov.io/gh/your-org/factors-no-more) [![Semantic Release](https://img.shields.io/badge/semantic--release-angular-blue)](https://github.com/python-semantic-release/python-semantic-release)

Guardrails and minimal estimators that **operationalize** the guidance in *BMJ Medicine 2025;4:e001375*:
avoid “factors associated with ...” shotgun screening; prespecify a **causal target** and **adjustment set**;
separate prediction from causation; handle multiplicity; provide bias demos.

> This library enforces process and provides small, typed utilities. It is not a silver bullet.

## Install
```bash
poetry add factors-no-more
# or from source:
poetry install
```

## Quick start

```python
from factors_no_more.causal_spec import CausalSpec
from factors_no_more.estimators import fit_adjusted_effect
from factors_no_more.guards import validate_against_factors_associated_pattern

spec = CausalSpec(
    exposure="A",
    outcome="Y",
    adjusters=("age", "sex", "smoking"),
    model="logistic",
    estimand="ATE",
)

validate_against_factors_associated_pattern(["A"], spec)
coef, (lo, hi) = fit_adjusted_effect(df, spec)  # typed effect with 95% CI
print(coef, lo, hi)
```

### Binary-treatment ATE
```python
from factors_no_more.estimators import BinaryATEInputs, ipw_ate, aipw_ate

spec = BinaryATEInputs(y_col="Y", a_col="A", z_cols=("age", "sex", "smoking"))
ate, se = ipw_ate(df, spec)
print("IPW ATE:", ate, "SE:", se)
```

### Multiplicity control
```python
from factors_no_more.multiplicity import bonferroni_adjust, benjamini_hochberg
adj_p, alpha_bonf = bonferroni_adjust([0.01, 0.2, 0.04])
adj_p_bh, reject = benjamini_hochberg([0.01, 0.2, 0.04], alpha=0.05)
```

### Protocol lock
```python
from factors_no_more.protocol import write_protocol_lock
hash_ = write_protocol_lock(spec, "analysis_plan.json")
print(hash_)
```

### Bias demos
```python
from factors_no_more.simulators import simulate_collider, simulate_mediator
dat = simulate_collider(n=100000, seed=1)
```

## Design principles
- **No stepwise** or shotgun screening.
- **One target at a time**: report the effect for the prespecified exposure only.
- **Causal vs prediction**: don’t mix. Choose the path and language accordingly.
- **Reproducibility**: lock and hash the plan.
- **Typed**: strict mypy + ruff + tests.

## Development
```bash
poetry install
poetry run ruff check .
poetry run mypy src
poetry run pytest
```

## License
MIT