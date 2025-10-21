# ─────────────────────────────────────────────────────────────
else:
st.subheader("Forensic Solver (one missing input)")


missing = st.selectbox(
"Select the missing variable:",
["cost_of_equity", "cost_of_debt", "tax_rate", "equity_value", "debt_value"],
index=0
)


wacc_known = st.number_input("Known WACC (decimal, e.g., 0.0923)", min_value=0.0, max_value=5.0, value=0.0923, step=0.0001, format="%f")


# Inputs except the missing one
def maybe_input(label, key, default, minv=0.0, maxv=5.0):
if missing == key:
st.text_input(label, value="(missing)", disabled=True)
return None
else:
return st.number_input(label, min_value=minv, max_value=maxv, value=default, step=0.001, format="%f")


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
col1, col2 = st.columns(2)
col1.metric("Implied wE", f"{out['wE']:.4f}")
col2.metric("Implied wD", f"{out['wD']:.4f}")
with st.expander("Raw output"):
st.json(out)
# Gentle interpretive text
if not (0 <= out['wE'] <= 1):
st.warning("Implied equity weight is outside [0,1]. Inputs may be inconsistent.")
except Exception as e:
st.error(str(e))
