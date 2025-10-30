from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json


def write_protocol_lock(spec_obj, path: str | Path) -> str:
    """Persist the analysis plan and its plan_hash to a JSON file.

    Returns the plan hash.
    """
    if not hasattr(spec_obj, "plan_hash") or not callable(spec_obj.plan_hash):
        raise TypeError("spec_obj must provide a plan_hash() method.")
    payload = asdict(spec_obj)
    payload["plan_hash"] = spec_obj.plan_hash()
    path = Path(path)
    path.write_text(json.dumps(payload, indent=2))
    return payload["plan_hash"]