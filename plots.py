from __future__ import annotations
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def mass_vs_radius_figure(out: dict, final_radii_m: tuple[float, float]) -> go.Figure:
    r_mm = out["mass_vs_radius"]["r_mm"]
    m1, m2 = out["mass_vs_radius"]["mass_g"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=r_mm, y=m1, mode="lines", name="Plane 1"))
    fig.add_trace(go.Scatter(x=r_mm, y=m2, mode="lines", name="Plane 2"))

    fig.add_vline(x=final_radii_m[0] * 1000.0, line_dash="dash", opacity=0.6)
    fig.add_vline(x=final_radii_m[1] * 1000.0, line_dash="dash", opacity=0.6)

    fig.update_layout(
        title="Required correction mass vs radius",
        xaxis_title="Radius (mm)",
        yaxis_title="Required mass (g)",
        hovermode="x",
        template="plotly_white",
    )
    fig.update_xaxes(range=[0, 75])
    return fig


def residual_vs_angle_figure(out: dict) -> go.Figure:
    angles = out["mass_vs_angle"]["angles_deg"]
    resid = out["mass_vs_angle"]["residual_kgm"]
    a_opt = out["mass_vs_angle"]["opt_angle_deg"]
    r_fix = out["mass_vs_angle"]["fixed_radius_m"]
    m_opt = out["mass_vs_angle"]["opt_mass_g"]

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,     
        vertical_spacing=0.10,
        subplot_titles=(
            f"Plane 1 @ r = {r_fix*1000:.0f} mm (mass fixed: {m_opt[0]:.2f} g)",
            f"Plane 2 @ r = {r_fix*1000:.0f} mm (mass fixed: {m_opt[1]:.2f} g)",
        ),
    )

    fig.add_trace(
        go.Scatter(x=angles, y=resid[0], mode="lines", name="Residual P1"), row=1, col=1
    )
    fig.add_vline(x=a_opt[0], line_dash="dash", opacity=0.6, row=1, col=1)

    fig.add_trace(
        go.Scatter(x=angles, y=resid[1], mode="lines", name="Residual P2"), row=2, col=1
    )
    fig.add_vline(x=a_opt[1], line_dash="dash", opacity=0.6, row=2, col=1)

    fig.update_layout(
        title="Residual if same mass used at all angles (fixed radius)",
        xaxis_title="Angle (deg)",
        xaxis2_title="Angle (deg)",
        yaxis_title="|Residual| (kg·m)",
        yaxis2_title="|Residual| (kg·m)",
        hovermode="x",
        template="plotly_white",
        showlegend=False,
    )
    return fig
