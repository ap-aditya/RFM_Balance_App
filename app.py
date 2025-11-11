from __future__ import annotations
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from rfm_core import balance_rfm_core
from plots import mass_vs_radius_figure, residual_vs_angle_figure

st.set_page_config(
    page_title="RFM Balance — Two-Plane",
    page_icon="🛠️",
    layout="wide",
)


def default_df(rows=1):
    return pd.DataFrame({"Amplitude": [0.0] * rows, "Phase_deg": [0.0] * rows})


st.markdown(
    """
    <style>
    /* General */
    .small-note {
        opacity: 0.75; 
        font-size: 0.9rem;
    }
    
    /* Result Metric Cards */
    .metric-card {
        border: 1px solid #dee2e6; /* Lighter border */
        border-radius: 12px; 
        padding: 16px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04);
        transition: box-shadow 0.3s ease-in-out;
    }
    .metric-card:hover {
        box-shadow: 0 6px 12px rgba(0,0,0,0.08);
    }
    
    /* Data Editor Headers */
    [data-testid="stDataEditor"] > div > div > div > div > div[data-testid="stMarkdownContainer"] {
        font-weight: 600;
        font-size: 1.05rem;
    }
    
    /* Main container for data editors */
    .data-entry-container {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1rem 1rem 0.5rem 1rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        border-right: 1px solid #e0e0e0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("RFM Balance — Two-Plane")
st.caption("Compute two-plane balancing via Response Function Matrix (RFM).")


with st.sidebar:
    st.header("Trials")
    col1, col2 = st.columns(2)
    with col1:
        t1_mass = st.number_input("Plane 1 Mass (g)", value=0.0, step=0.01)
        t1_angle = st.number_input("Plane 1 Angle (deg)", value=0.0, step=0.1)
        t1_radius = st.number_input("Plane 1 Radius (m)", value=0.05, step=0.001, min_value=1e-6)
    with col2:
        t2_mass = st.number_input("Plane 2 Mass (g)", value=0.0, step=0.01)
        t2_angle = st.number_input("Plane 2 Angle (deg)", value=0.0, step=0.1)
        t2_radius = st.number_input("Plane 2 Radius (m)", value=0.05, step=0.001, min_value=1e-6)

    st.divider()
    st.header("Options")
    use_final = st.checkbox("Specify final radii (else use trial radii)", value=False)
    colf1, colf2 = st.columns(2)
    with colf1:
        final_r1 = st.number_input("Final radius P1 (m)", value=t1_radius, step=0.001, disabled=not use_final)
    with colf2:
        final_r2 = st.number_input("Final radius P2 (m)", value=t2_radius, step=0.001, disabled=not use_final)

    fix_radius = st.number_input("Fixed radius for angle plot (m)", value=0.05, step=0.001, min_value=1e-6)
    
    add_180_deg = st.checkbox("Add 180° to final angles (Opposite to rotation)", value=True)
    
    show_R = st.checkbox("Show Mass vs Radius plot", value=True)
    show_A = st.checkbox("Show Residual vs Angle plot", value=True)

st.subheader("Sensor Readings")
st.markdown('<span class="small-note">Each table is M×2: Amplitude, Phase (deg). Use consistent units for amplitude across runs.</span>', unsafe_allow_html=True)


st.markdown('<div class="data-entry-container">', unsafe_allow_html=True)
c0, c1, c2 = st.columns(3)
with c0:
    st.markdown("**R0 — Baseline**")
    R0_df = st.data_editor(default_df(1), key="R0", num_rows="dynamic", width='stretch')
with c1:
    st.markdown("**R1 — Trial on Plane 1**")
    R1_df = st.data_editor(default_df(1), key="R1", num_rows="dynamic", width='stretch')
with c2:
    st.markdown("**R2 — Trial on Plane 2**")
    R2_df = st.data_editor(default_df(1), key="R2", num_rows="dynamic", width='stretch')
st.markdown('</div>', unsafe_allow_html=True)


st.divider()
compute = st.button("Compute Balance", type="primary")

def _coerce(A: pd.DataFrame, table_name: str) -> np.ndarray:
    """Validate and convert dataframe to numpy array."""
    if A is None or A.empty:
        raise ValueError(f"Table {table_name} is empty")
    if not {"Amplitude", "Phase_deg"}.issubset(A.columns):
        raise ValueError(f"Table {table_name} must have columns: Amplitude, Phase_deg")
    
    if A.isnull().values.any():
        raise ValueError(f"Table {table_name} must not contain empty/null cells. Please fill all values.")
    
    try:
        arr = A[["Amplitude", "Phase_deg"]].astype(float).to_numpy()
    except ValueError as e:
        raise ValueError(f"Invalid non-numeric data found in {table_name}: {e}")
        
    arr[:, 1] = np.mod(arr[:, 1], 360.0)
    return arr

if compute:
    try:
        R0 = _coerce(R0_df, "R0")
        R1 = _coerce(R1_df, "R1")
        R2 = _coerce(R2_df, "R2")

        if R0.shape != R1.shape or R0.shape != R2.shape:
            raise ValueError(f"R0, R1, R2 must have the same shape (got {R0.shape}, {R1.shape}, {R2.shape})")
        if R0.shape[0] < 1:
            raise ValueError("At least one sensor row (M>=1) is required")

        trial1 = {"mass_g": float(t1_mass), "angle_deg": float(t1_angle), "radius_m": float(t1_radius)}
        trial2 = {"mass_g": float(t2_mass), "angle_deg": float(t2_angle), "radius_m": float(t2_radius)}
        final_radii_m = (float(final_r1), float(final_r2)) if use_final else (t1_radius, t2_radius)

        out = balance_rfm_core(
            R0, R1, R2, trial1, trial2,
            final_radii_m=final_radii_m,
            fix_radius_m=float(fix_radius),
            opp_to_rotation=add_180_deg, 
        )

        st.subheader("Results")
        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label=f"Plane 1 @ r = {final_radii_m[0]:.3f} m",
                value=f"{out['mass_g_at_final'][0]:.2f} g",
                delta=f"{out['angle_deg'][0]:.1f}°",
                delta_color="normal",
            )
            st.markdown('</div>', unsafe_allow_html=True)
        with cc2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label=f"Plane 2 @ r = {final_radii_m[1]:.3f} m",
                value=f"{out['mass_g_at_final'][1]:.2f} g",
                delta=f"{out['angle_deg'][1]:.1f}°",
                delta_color="normal",
            )
            st.markdown('</div>', unsafe_allow_html=True)

        tabs = st.tabs(["📈 Plots", "🧮 Matrices / Details", "📝 Summary"])

        with tabs[0]:
            if not show_R and not show_A:
                st.info("Plots are hidden. Please enable them in the sidebar Options.")
            if show_R:
                figR = mass_vs_radius_figure(out, final_radii_m)
                st.plotly_chart(figR, use_container_width=True)
            if show_A:
                figA = residual_vs_angle_figure(out)
                st.plotly_chart(figA, use_container_width=True)

        with tabs[1]:
            H = out["H"]; r0 = out["r0"]; bc = out["bc_kgm"]
            def cformat(z): return f"{z.real:.6e} + {z.imag:.6e}j"
            lines = ["H (M x 2, complex):"]
            for i in range(H.shape[0]):
                lines.append(f"  row {i+1}: [ {cformat(H[i,0])} , {cformat(H[i,1])} ]")
            lines.append("\nr0 (M x 1, complex):")
            for i in range(r0.shape[0]):
                lines.append(f"  {i+1}: {cformat(r0[i])}")
            lines.append("\nbc (2 x 1, complex kg·m):")
            lines.append(f"  b1: {cformat(bc[0])}")
            lines.append(f"  b2: {cformat(bc[1])}")
            st.code("\n".join(lines), language="text")

        with tabs[2]:
            st.code(out["summary"], language="text")

    except Exception as e:
        st.error(f"{type(e).__name__}: {e}")
else:
    st.info("Enter readings in R0 / R1 / R2, set trial parameters, then click **Compute Balance**.")