from __future__ import annotations
import numpy as np


def coerce_table(table: list[dict]) -> np.ndarray:
    """Dash DataTable rows -> (M,2) float array."""
    if not table:
        raise ValueError("Table is empty")
    amps, phases = [], []
    for i, row in enumerate(table):
        try:
            a = float(row.get("Amplitude", ""))
            p = float(row.get("Phase_deg", ""))
        except Exception as e:
            raise ValueError(f"Row {i+1}: non-numeric value") from e
        amps.append(a)
        phases.append(p)
    A = np.column_stack([amps, np.mod(phases, 360.0)])
    return A


def validate_trials(trial: dict, label: str):
    for key in ("mass_g", "angle_deg", "radius_m"):
        if key not in trial:
            raise ValueError(f"{label}: missing {key}")
        try:
            float(trial[key])
        except Exception as e:
            raise ValueError(f"{label}: {key} must be numeric") from e
    if float(trial["radius_m"]) <= 0:
        raise ValueError(f"{label}: radius_m must be > 0")
    if float(trial["mass_g"]) <= 0:
        raise ValueError(f"{label}: mass_g must be > 0")
