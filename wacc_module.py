# ─────────────────────────────────────────────────────────────
Ke = (wacc - wD * cost_of_debt * (1 - tax_rate)) / wE
return {"missing": miss, "value": Ke, "wE": wE, "wD": wD}


if miss == "cost_of_debt":
wE, wD = _weights(equity_value, debt_value)
denom = wD * (1 - tax_rate)
if denom == 0:
raise ValueError("Denominator zero: cannot solve Kd (check T and D).")
Kd = (wacc - wE * cost_of_equity) / denom
return {"missing": miss, "value": Kd, "wE": wE, "wD": wD}


if miss == "tax_rate":
wE, wD = _weights(equity_value, debt_value)
denom = wD * cost_of_debt
if denom == 0:
raise ValueError("Denominator zero: cannot solve T (check D and Kd).")
T = 1 - (wacc - wE * cost_of_equity) / denom
return {"missing": miss, "value": T, "wE": wE, "wD": wD}


# Missing E or D: infer weights from linear form first
if miss in ("equity_value", "debt_value"):
A = cost_of_equity
B = cost_of_debt * (1 - tax_rate)
denom = (A - B)
if denom == 0:
raise ValueError("Cannot infer weights when Ke == Kd*(1-T).")
wE = (wacc - B) / denom
if not (0 <= wE <= 1):
raise ValueError(f"Inconsistent inputs: implied equity weight {wE:.4f} not in [0,1].")
wD = 1 - wE


if miss == "equity_value":
if debt_value is None:
raise ValueError("To solve E, provide D.")
if wD == 0:
raise ValueError("Debt weight is zero; E not identifiable from D.")
E = (wE / wD) * debt_value
return {"missing": miss, "value": E, "wE": wE, "wD": wD}


if miss == "debt_value":
if equity_value is None:
raise ValueError("To solve D, provide E.")
if wE == 0:
raise ValueError("Equity weight is zero; D not identifiable from E.")
D = (wD / wE) * equity_value
return {"missing": miss, "value": D, "wE": wE, "wD": wD}


raise ValueError("Unexpected state.")




def format_percent(x: float, decimals: int = 2) -> str:
return f"{round(x*100, decimals)}%"