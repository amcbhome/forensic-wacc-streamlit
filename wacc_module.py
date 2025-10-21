# -*- coding: utf-8 -*-
"""
WACC Module
──────────────────────────────────────────────
Provides two main functions:
1. calculate_wacc()  → forward calculation
2. solve_missing()   → forensic back-solver
"""

from typing import Dict, Optional


# ──────────────────────────────────────────────
# Utility: compute capital weights
# ──────────────────────────────────────────────
def _weights(E: float, D: float):
    """Return (wE, wD) given equity and debt values."""
    if E is None or D is None:
        raise ValueError("Equity (E) and Debt (D) must be provided.")
    if E < 0 or D < 0:
        raise ValueError("Equity and Debt must be non-negative.")
    total = E + D
    if total == 0:
        raise ValueError("E + D cannot be zero.")
    wE = E / total
    wD = 1 - wE
    return wE, wD


# ──────────────────────────────────────────────
# Forward computation
# ──────────────────────────────────────────────
def calculate_wacc(equity_value: float,
                   debt_value: float,
                   cost_of_equity: float,
                   cost_of_debt: float,
                   tax_rate: float) -> Dict:
    """
    Compute Weighted Average Cost of Capital (WACC).

    Parameters
    ----------
    equity_value : float
        Market value of equity.
    debt_value : float
        Market value of debt.
    cost_of_equity : float
        Cost of equity (decimal form, e.g. 0.10 for 10%).
    cost_of_debt : float
        Cost of debt (decimal form, e.g. 0.06 for 6%).
    tax_rate : float
        Corporate tax rate (decimal, e.g. 0.25 for 25%).

    Returns
    -------
    dict
        Structured result with weights and WACC (decimal).
    """
    wE, wD = _weights(equity_value, debt_value)
    if not (0 <= tax_rate <= 1):
        raise ValueError("Tax rate must be within [0, 1].")

    wacc = wE * cost_of_equity + wD * cost_of_debt * (1 - tax_rate)

    return {
        "equity_value": equity_value,
        "debt_value": debt_value,
        "cost_of_equity": cost_of_equity,
        "cost_of_debt": cost_of_debt,
        "tax_rate": tax_rate,
        "equity_weight": wE,
        "debt_weight": wD,
        "wacc": wacc,
    }


# ──────────────────────────────────────────────
# Forensic solver
# ──────────────────────────────────────────────
def solve_missing(*,
                  wacc: float,
                  equity_value: Optional[float],
                  debt_value: Optional[float],
                  cost_of_equity: Optional[float],
                  cost_of_debt: Optional[float],
                  tax_rate: Optional[float]) -> Dict:
    """
    Solve for the single missing variable in the WACC formula.

    Provide WACC (decimal) and EXACTLY four of:
      equity_value (E), debt_value (D),
      cost_of_equity (Ke), cost_of_debt (Kd), tax_rate (T)

    Returns
    -------
    dict
        {"missing": variable, "value": solved_value,
         "wE": equity_weight, "wD": debt_weight}
    """
    params = {
        "equity_value": equity_value,
        "debt_value": debt_value,
        "cost_of_equity": cost_of_equity,
        "cost_of_debt": cost_of_debt,
        "tax_rate": tax_rate,
    }

    missing = [k for k, v in params.items() if v is None]
    if len(missing) != 1:
        raise ValueError("Provide exactly four inputs (one missing).")
    miss = missing[0]

    # Cost of equity (Ke)
    if miss == "cost_of_equity":
        wE, wD = _weights(equity_value, debt_value)
        if wE == 0:
            raise ValueError("Cannot solve Ke when equity weight is zero.")
        Ke = (wacc - wD * cost_of_debt * (1 - tax_rate)) / wE
        return {"missing": miss, "value": Ke, "wE": wE, "wD": wD}

    # Cost of debt (Kd)
    if miss == "cost_of_debt":
        wE, wD = _weights(equity_value, debt_value)
        denom = wD * (1 - tax_rate)
        if denom == 0:
            raise ValueError("Cannot solve Kd: denominator zero (check D and T).")
        Kd = (wacc - wE * cost_of_equity) / denom
        return {"missing": miss, "value": Kd, "wE": wE, "wD": wD}

    # Tax rate (T)
    if miss == "tax_rate":
        wE, wD = _weights(equity_value, debt_value)
        denom = wD * cost_of_debt
        if denom == 0:
            raise ValueError("Cannot solve T: denominator zero (check D and Kd).")
        T = 1 - (wacc - wE * cost_of_equity) / denom
        return {"missing": miss, "value": T, "wE": wE, "wD": wD}

    # Equity or Debt value
    if miss in ("equity_value", "debt_value"):
        A = cost_of_equity
        B = cost_of_debt * (1 - tax_rate)
        denom = A - B
        if denom == 0:
            raise ValueError("Cannot infer weights: Ke == Kd*(1-T).")
        wE = (wacc - B) / denom
        if not (0 <= wE <= 1):
            raise ValueError(f"Inconsistent inputs: implied wE={wE:.4f} not in [0,1].")
        wD = 1 - wE

        if miss == "equity_value":
            if debt_value is None:
                raise ValueError("To solve E, provide D.")
            if wD == 0:
                raise ValueError("Debt weight zero; E not identifiable.")
            E = (wE / wD) * debt_value
            return {"missing": miss, "value": E, "wE": wE, "wD": wD}

        if miss == "debt_value":
            if equity_value is None:
                raise ValueError("To solve D, provide E.")
            if wE == 0:
                raise ValueError("Equity weight zero; D not identifiable.")
            D = (wD / wE) * equity_value
            return {"missing": miss, "value": D, "wE": wE, "wD": wD}

    raise ValueError("Unexpected solver state.")


# ──────────────────────────────────────────────
# Display helper
# ──────────────────────────────────────────────
def format_percent(x: float, decimals: int = 6) -> str:
    """Return a formatted percentage string with six decimal places."""
    return f"{x * 100:.6f}%"

