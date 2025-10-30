## Getting Started

```python
from factors_no_more.causal_spec import CausalSpec
from factors_no_more.estimators import fit_adjusted_effect
spec = CausalSpec(exposure='A', outcome='Y', adjusters=('age','sex','smoking'), model='linear')
coef, (lo, hi) = fit_adjusted_effect(df, spec)
```
