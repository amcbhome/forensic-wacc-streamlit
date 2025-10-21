# -*- coding: utf-8 -*-
import streamlit as st
from wacc_module import calculate_wacc, solve_missing, format_percent

# ──────────────────────────────────────────────
# Streamlit page setup
# ──────────────────────────────────────────────
st.set_page_config(page_title="Forensic WACC Solver", layout="centered")
st.title("Forensic WACC Solver")
st.caption("Back-solve missing inputs from the WACC formula — a teaching demo for forensic accounting.")

# Display the formula
with st.expander("Formula & Notation", expanded=False):
    st.latex(r"""
    \text{WACC} = w_E K_E + w_D K_D (1 - T),\quad
    w_E = \frac{E}{E + D},\; w_D = 1 - w_E
    """)

# ──────────────────────────────────────────────
# Mode selection: Forward vs Forensic
# ──────────────────────────────────────────────
mode = st.radio("Choose mode:", ["Forward (compute WACC)", "Forensic (solve missing)"])

st.divider()

# ──────────────────────────────────────────────
# Mode 1: Forward calculation
# ──────────────────────────────────────────────
if mode == "Forward (compute WACC)":
    st.subheader("Forward WACC Calculator")

    col1, col2 = st.columns(2)
    with col1:
        E = st.number_input("Equity value (E)", min_value=0.0, value=12000.0, step=100.0)
        Ke = st.number_input("Cost of equity (Ke, decimal)", min_value=0.0, max_value=5.0,
                             value=0.10, step=0.005, format="%f")
        T = st.number_input("Tax rate (T, decimal)", min_value=0.0, max_value=1.0,
                            value=0.25, step=0.01, format="%f")
    with col2:
        D = st.number_input("Debt value (D)", min_value=0.0, value=2000.0, step=100.0)
        Kd = st.number_input("Cost of debt (Kd, decimal)", min_value=0.0, max_value=5.0,
                             value=0.067, step=0.005, format="%f")

    if st.button("Calculate WACC", type="primary"):
        try:
            res = calculate_wacc(E, D, Ke, Kd, T)
            colA, colB, colC = st.columns(3)
            colA.metric("Equity weight (wE)", f"{res['equity_weight']:.4f}")
            colB.metric("Debt weight (wD)", f"{res['debt_weight']:.4f}")
            colC.metric("WACC", format_percent(res['wacc']))
            with st.expander("Calculation details"):
                st.json(res)
        except Exception as e:
            st.error(str(e))

# ──────────────────────────────────────────────
# Mode 2: Forensic (solve missing input)
# ──────────────────────────────────────────────
else:
    st.subheader("Forensic Solver (find missing input)")

    missing = st.selectbox(
        "Select the missing variable:",
        ["cost_of_equity", "cost_of_debt", "tax_rate", "equity_value", "debt_value"],
        index=0
    )

    wacc_known = st.number_input("Known WACC (decimal, e.g. 0.0923)",
                                 min_value=0.0, max_value=5.0,
                                 value=0.0923, step=0.0001, format="%f")

    # Helper for conditional inputs
    def maybe_input(label, key, default, minv=0.0, maxv=5.0):
        if missing == key:
            st.text_input(label, value="(missing)", disabled=True)
            return None
        else:
            return st.number_input(label, min_value=minv, max_value=maxv,
                                   value=default, step=0.001, format="%f")

    # Collect inputs
    E = maybe_input("Equity value (E)", "equity_value", 12000.0, 0.0, 1e12)
    D = maybe_input("Debt value (D)", "debt_value", 2000.0, 0.0, 1e12)
    Ke = maybe_input("Cost of equity (Ke, decimal)", "cost_of_equity", 0.10, 0.0, 5.0)
    Kd = maybe_input("Cost of debt (Kd, decimal)", "cost_of_debt", 0.067, 0.0, 5.0)
    T = maybe_input("Tax rate (T, decimal)", "tax_rate", 0.25, 0.0, 1.0)

    if st.button("Solve missing value", type="primary"):
        kwargs = dict(wacc=wacc_known, equity_value=E, debt_value=D,
                      cost_of_equity=Ke, cost_of_debt=Kd, tax_rate=T)
        try:
            out = solve_missing(**kwargs)
            st.success(f"Solved {out['missing']}: {out['value']:.6f}")
            c1, c2 = st.columns(2)
            c1.metric("Implied wE", f"{out['wE']:.4f}")
            c2.metric("Implied wD", f"{out['wD']:.4f}")
            with st.expander("Solver details"):
                st.json(out)
            if not (0 <= out['wE'] <= 1):
                st.warning("Implied equity weight is outside [0,1]; inputs may be inconsistent.")
        except Exception as e:
            st.error(str(e))

