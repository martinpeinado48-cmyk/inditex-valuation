"""DCF de Inditex: implementación de referencia en Python.

Sirve para dos cosas: (1) comprobar que el modelo de Excel calcula lo mismo y
(2) reutilizar la lógica en el Monte Carlo y en los gráficos.

Enfoque (arrendamientos como coste operativo, "pre-NIIF 16"):
    FCFF = EBITDA - pagos por arrendamiento - impuestos - capex - aumento de circulante
    Impuestos = tipo x (EBIT - interés de arrendamientos)
    Valor de la empresa = VA(FCFF) + VA(valor terminal de Gordon)
    Valor del equity = valor de la empresa + posición financiera neta (sin restar arrendamientos)

Importes en millones de euros. Fecha del balance de partida: 31/07/2026.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

YEARS = list(range(2026, 2036))  # FY2026E ... FY2035E (el ejercicio N termina el 31/01/N+1)

# --- Hipótesis de mercado (ver data/market/datos_mercado_2026-10-07.csv) -------------------------
MERCADO = dict(
    fecha_valoracion=date(2026, 10, 7),
    fecha_balance=date(2026, 7, 31),
    meses_restantes_2026=6,
    precio=54.38,
    acciones=3115.921539,          # millones
    rf=0.0357,      # bono alemán a 10 años (30/09/2026). Decisión de Martín 2026-10-07 (bono español: 4,11 %)
    beta=1.00,      # regresión propia semanal 5 años (0,95-1,08); Investing.com 0,90; sector 0,79
    erp=0.054,      # Damodaran mercado maduro 4,17 % + riesgo-país ponderado por ventas (estimación propia)
    kd=0.045,
    peso_deuda=0.0,
    tipo_impositivo=0.225,
    g_terminal=0.025,
    efectivo=4361.0,
    inv_temporales=6038.0,
    deuda_financiera=1.0,
    otros_activos=0.0,
    minoritarios=0.0,
)

# --- Parámetros operativos comunes a los tres escenarios -------------------------------------------
OPERATIVOS = dict(
    da_pct=0.082,          # amortizaciones / ventas (2025: 3.270 / 39.864 = 8,2 %)
    arrend_pct=0.046,      # pagos por arrendamiento / ventas (2025: 1.834 / 39.864 = 4,6 %)
    arrend_int_pct=0.005,  # interés de arrendamientos / ventas (2025: 215 / 39.864 = 0,5 %)
    nwc_pct=-0.085,        # (existencias + deudores - acreedores) / ventas (media 2020-25 ≈ -8,6 %)
)

# --- Escenarios: 1 = Bajo, 2 = Base, 3 = Alto -----------------------------------------------------------
ESCENARIOS = {
    1: dict(
        nombre="Bajo",
        crecimiento=[0.050, 0.045, 0.040, 0.035, 0.030, 0.030, 0.028, 0.026, 0.025, 0.025],
        margen_ebit=[0.200, 0.195, 0.190, 0.185, 0.180, 0.180, 0.180, 0.180, 0.180, 0.180],
        capex_pct=[0.058, 0.058, 0.056, 0.055, 0.055, 0.055, 0.055, 0.055, 0.055, 0.055],
    ),
    2: dict(
        nombre="Base",
        crecimiento=[0.075, 0.070, 0.065, 0.060, 0.055, 0.050, 0.045, 0.040, 0.035, 0.030],
        margen_ebit=[0.200] * 10,
        capex_pct=[0.058, 0.056, 0.054, 0.052, 0.050, 0.050, 0.050, 0.050, 0.050, 0.050],
    ),
    3: dict(
        nombre="Alto",
        crecimiento=[0.090, 0.085, 0.080, 0.070, 0.065, 0.060, 0.050, 0.045, 0.040, 0.035],
        margen_ebit=[0.205, 0.208, 0.211, 0.214, 0.217, 0.220, 0.220, 0.220, 0.220, 0.220],
        capex_pct=[0.058, 0.054, 0.050, 0.048, 0.045, 0.045, 0.045, 0.045, 0.045, 0.045],
    ),
}


def datos_base() -> dict:
    """Saldos del ejercicio 2025 (último cerrado) para arrancar la proyección."""
    w = pd.read_csv(ROOT / "data" / "processed" / "inditex_financials.csv", index_col=0)
    u = w.loc[2025]
    return dict(ventas=float(u.ventas), nwc=float(u.existencias + u.deudores - u.acreedores))


def wacc(m: dict) -> float:
    ke = m["rf"] + m["beta"] * m["erp"]
    return ke * (1 - m["peso_deuda"]) + m["kd"] * (1 - m["tipo_impositivo"]) * m["peso_deuda"]


def valorar(escenario: int = 2, mercado: dict | None = None, operativos: dict | None = None,
            overrides: dict | None = None, base: dict | None = None) -> dict:
    """Devuelve el detalle año a año y la valoración. `overrides` permite sustituir listas del escenario."""
    m = {**MERCADO, **(mercado or {})}
    op = {**OPERATIVOS, **(operativos or {})}
    esc = deepcopy(ESCENARIOS[escenario])
    esc.update(overrides or {})
    b = base or datos_base()

    stub = m["meses_restantes_2026"] / 12
    w = wacc(m)
    g = m["g_terminal"]

    filas = []
    ventas_ant, nwc_ant = b["ventas"], b["nwc"]
    for i, año in enumerate(YEARS):
        ventas = ventas_ant * (1 + esc["crecimiento"][i])
        ebit = ventas * esc["margen_ebit"][i]
        da = ventas * op["da_pct"]
        ebitda = ebit + da
        pagos_arrend = -ventas * op["arrend_pct"]
        int_arrend = ventas * op["arrend_int_pct"]
        impuestos = -m["tipo_impositivo"] * max(ebit - int_arrend, 0)
        capex = -ventas * esc["capex_pct"][i]
        nwc = ventas * op["nwc_pct"]
        var_nwc = nwc_ant - nwc                      # negativo si el circulante aumenta (sale caja)
        fcff = ebitda + pagos_arrend + impuestos + capex + var_nwc
        fraccion = stub if i == 0 else 1.0
        t = stub / 2 if i == 0 else (stub + 0.5 if i == 1 else filas[-1]["t"] + 1)
        factor = (1 + w) ** -t
        filas.append(dict(año=año, ventas=ventas, crecimiento=esc["crecimiento"][i], ebit=ebit,
                          margen_ebit=esc["margen_ebit"][i], da=da, ebitda=ebitda,
                          pagos_arrend=pagos_arrend, int_arrend=int_arrend, impuestos=impuestos,
                          capex=capex, nwc=nwc, var_nwc=var_nwc, fcff=fcff, fraccion=fraccion,
                          fcff_valorado=fcff * fraccion, t=t, factor=factor, va=fcff * fraccion * factor))
        ventas_ant, nwc_ant = ventas, nwc

    va_explicito = sum(f["va"] for f in filas)
    ultimo = filas[-1]
    vt = ultimo["fcff"] * (1 + g) / (w - g)
    va_vt = vt * ultimo["factor"]            # convención de mitad de periodo: se descuenta con el factor del último flujo
    ev = va_explicito + va_vt
    pfn = m["efectivo"] + m["inv_temporales"] - m["deuda_financiera"]
    equity = ev + pfn + m["otros_activos"] - m["minoritarios"]
    por_accion_balance = equity / m["acciones"]
    dias = (m["fecha_valoracion"] - m["fecha_balance"]).days
    por_accion_hoy = por_accion_balance * (1 + w) ** (dias / 365)
    return dict(filas=filas, wacc=w, g=g, va_explicito=va_explicito, vt=vt, va_vt=va_vt, ev=ev, pfn=pfn,
                equity=equity, por_accion_balance=por_accion_balance, por_accion_hoy=por_accion_hoy,
                upside=por_accion_hoy / m["precio"] - 1, peso_vt=va_vt / ev, dias=dias, mercado=m)


if __name__ == "__main__":
    for k in (1, 2, 3):
        r = valorar(k)
        print(f"{ESCENARIOS[k]['nombre']:<5} WACC {r['wacc']:.2%} | EV {r['ev']:>9,.0f} | equity {r['equity']:>9,.0f} | "
              f"€/acción hoy {r['por_accion_hoy']:>6.2f} | vs precio {r['upside']:+.1%} | VT/EV {r['peso_vt']:.0%}")
