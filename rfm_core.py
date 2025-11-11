from __future__ import annotations
from typing import Dict, Any, Tuple
import numpy as np


def _to_complex(Aphi: np.ndarray) -> np.ndarray:
    """[Amp, Phase_deg] -> complex phasor."""
    amp = Aphi[:, 0].astype(float)
    phase_deg = Aphi[:, 1].astype(float)
    return amp * np.exp(1j * np.deg2rad(phase_deg))


def _ang_deg(z: np.ndarray) -> np.ndarray:
    """Angle in degrees in [0, 360)."""
    ang = np.degrees(np.angle(z))
    return np.mod(ang, 360.0)


def balance_rfm_core(
    R0: np.ndarray,
    R1: np.ndarray,
    R2: np.ndarray,
    trial1: Dict[str, float],
    trial2: Dict[str, float],
    *,
    final_radii_m: Tuple[float, float] | None = None,
    fix_radius_m: float = 0.050,
    opp_to_rotation: bool = False,
) -> Dict[str, Any]:
    """Python port of MATLAB balance_rfm_core."""
    opp_to_rotation= not opp_to_rotation  # Invert logic to match MATLAB version
    if R0.shape != R1.shape or R0.shape != R2.shape:
        raise ValueError("R0, R1, R2 must have the same shape (M x 2)")
    if R0.shape[1] != 2:
        raise ValueError("R* must have 2 columns: [Amplitude, Phase_deg]")
    if R0.shape[0] < 1:
        raise ValueError("At least one sensor row (M>=1) is required")

    # Options
    if final_radii_m is None:
        final_radii = np.array([trial1["radius_m"], trial2["radius_m"]], dtype=float)
    else:
        final_radii = np.asarray(final_radii_m, dtype=float).reshape(2)
    
    if np.any(final_radii <= 0):
        raise ValueError("final_radii_m must be > 0")
    if fix_radius_m <= 0:
        raise ValueError("fix_radius_m must be > 0")

    # Complex responses
    r0 = _to_complex(np.asarray(R0, dtype=float))
    r1 = _to_complex(np.asarray(R1, dtype=float))
    r2 = _to_complex(np.asarray(R2, dtype=float))

    # Trial unbalance phasors (kg·m)
    U1 = (trial1["mass_g"] / 1000.0) * trial1["radius_m"] * np.exp(
        1j * np.deg2rad(trial1["angle_deg"])
    )
    U2 = (trial2["mass_g"] / 1000.0) * trial2["radius_m"] * np.exp(
        1j * np.deg2rad(trial2["angle_deg"])
    )
    if abs(U1) == 0 or abs(U2) == 0:
        if trial1["mass_g"] == 0 or trial2["mass_g"] == 0:
             raise ValueError("Trial masses must be non-zero.")
        if trial1["radius_m"] == 0 or trial2["radius_m"] == 0:
             raise ValueError("Trial radii must be non-zero.")
        raise ValueError("Trial unbalance (mass * radius) must be non-zero.")


    # Response Function Matrix (M x 2 complex)
    H_col1 = (r1 - r0) / U1
    H_col2 = (r2 - r0) / U2
    H = np.column_stack((H_col1, H_col2))
    
    if np.all(np.abs(H_col1) < 1e-15) or np.all(np.abs(H_col2) < 1e-15):
        raise ValueError("One or both trial runs had no measurable effect. Check R1/R2 data.")

    # bc = -H \ r0  (least squares)
    try:
        bc, *_ = np.linalg.lstsq(H, -r0, rcond=None)  # (2,)
    except np.linalg.LinAlgError as e:
        raise ValueError(f"Linear algebra error during solve: {e}. Check data for linear dependencies.")

    # Final masses & angles
    m_final = np.array([abs(bc[0]) / final_radii[0], abs(bc[1]) / final_radii[1]]) * 1000.0
    a_final = _ang_deg(bc)
    
    # --- LOGIC IS HERE ---
    if opp_to_rotation:
        a_final = np.mod(a_final + 180.0, 360.0)

    # Mass vs Radius (0.1–75 mm)
    r_mm = np.linspace(0.1, 75.0, 750)
    r_m = r_mm / 1000.0
    m1_vs_r = (abs(bc[0]) / r_m) * 1000.0
    m2_vs_r = (abs(bc[1]) / r_m) * 1000.0

    # Mass vs Angle (fixed radius) + residual
    t = -bc
    r_fix = fix_radius_m
    angles = np.arange(0, 360)
    ejth = np.exp(1j * np.deg2rad(angles))
    m_opt_g = (np.abs(t) / r_fix) * 1000.0
    a_opt = _ang_deg(t)
    
    if opp_to_rotation:
        a_opt = np.mod(a_opt + 180.0, 360.0)
        
    mass_vs_angle_g = np.zeros((2, angles.size))
    resid_vs_angle = np.zeros((2, angles.size))
    for p in range(2):
        Mfixed = (m_opt_g[p] / 1000.0) * r_fix
        ucurve = Mfixed * ejth
        res = np.abs(t[p] - ucurve)
        mass_vs_angle_g[p, :] = m_opt_g[p]
        resid_vs_angle[p, :] = res

    summary = (
        "Two-plane RFM balancing\n"
        f"Final radii (m): [{final_radii[0]:.3f}  {final_radii[1]:.3f}]\n"
        f"Plane 1 -> {m_final[0]:.2f} g @ {a_final[0]:.1f}°\n"
        f"Plane 2 -> {m_final[1]:.2f} g @ {a_final[1]:.1f}°\n"
    )

    return {
        "H": H,
        "r0": r0,
        "bc_kgm": bc,
        "mass_g_at_final": m_final,
        "angle_deg": a_final, # This value depends on opp_to_rotation
        "mass_vs_radius": {"r_mm": r_mm, "mass_g": np.vstack([m1_vs_r, m2_vs_r])},
        "mass_vs_angle": {
            "angles_deg": angles,
            "mass_g_fixed": mass_vs_angle_g,
            "residual_kgm": resid_vs_angle,
            "opt_mass_g": m_opt_g,
            "opt_angle_deg": a_opt, # This value depends on opp_to_rotation
            "fixed_radius_m": r_fix,
        },
        "summary": summary,
    }