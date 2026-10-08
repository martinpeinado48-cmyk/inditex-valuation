"""Calidad contable de Inditex: Altman Z'' (riesgo de dificultades financieras) y Beneish M-score (indicios de manipulación).

Son herramientas de CRIBADO: señalan dónde mirar con más lupa, no prueban nada.

Altman Z'' (empresas no industriales):  Z'' = 6,56·X1 + 3,26·X2 + 6,72·X3 + 1,05·X4
    X1 = (activo corriente - pasivo corriente) / activo total
    X2 = beneficios acumulados / activo total
    X3 = EBIT / activo total
    X4 = patrimonio neto contable / pasivo total
    Zonas: > 2,6 segura · 1,1 - 2,6 gris · < 1,1 riesgo

Beneish M (8 variables, año t frente a t-1):
    M = -4,84 + 0,920·DSRI + 0,528·GMI + 0,404·AQI + 0,892·SGI + 0,115·DEPI - 0,172·SGAI + 4,679·TATA - 0,327·LVGI
    Umbral habitual: -1,78 (algunos usan -2,22, más estricto). M por encima del umbral = se parece a empresas que maquillaron cuentas.

Adaptaciones a Inditex (documentadas en docs/Guia_del_modelo.md):
    - SG&A = gastos de explotación (personal + alquileres + otros operativos); Inditex no desglosa SG&A.
    - PPE = inmovilizado material + derecho de uso (las tiendas arrendadas).
    - Pasivo con coste del LVGI = pasivo corriente + deuda financiera a largo + arrendamiento a largo.
    - TATA = (resultado neto - flujo de explotación) / activo total.
    - AQI usa activo corriente + PPE (no se separan inversiones financieras no corrientes).

Salida: data/processed/calidad_contable_*.csv y los gráficos 12 y 13.
"""
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# Ganancias acumuladas al cierre de cada ejercicio (M EUR): columna «Ganancias acumuladas» de la fila «Saldo a 31 de enero»
# del Estado de cambios en el patrimonio consolidado de las cuentas anuales (ejercicio N cierra el 31/01/N+1).
GANANCIAS_ACUMULADAS = {2020: 14703, 2021: 15462, 2022: 16460, 2023: 17991, 2024: 18994, 2025: 19825}

BLUE, ORANGE = "#2a78d6", "#eb6834"
SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"


def cargar() -> pd.DataFrame:
    w = pd.read_csv(ROOT / "data" / "processed" / "inditex_financials.csv", index_col=0)
    w.index = w.index.astype(int)
    w["ganancias_acumuladas"] = pd.Series(GANANCIAS_ACUMULADAS)
    return w


def altman(w: pd.DataFrame) -> pd.DataFrame:
    ta = w.total_activo
    x = pd.DataFrame({
        "X1_circulante_activo": (w.activo_corriente - w.pasivo_corriente) / ta,
        "X2_acumulados_activo": w.ganancias_acumuladas / ta,
        "X3_ebit_activo": w.ebit / ta,
        "X4_patrimonio_pasivo": w.patrimonio_neto / (ta - w.patrimonio_neto),
    })
    x["Z2"] = 6.56 * x.X1_circulante_activo + 3.26 * x.X2_acumulados_activo + 6.72 * x.X3_ebit_activo + 1.05 * x.X4_patrimonio_pasivo
    x["zona"] = pd.cut(x.Z2, [-99, 1.1, 2.6, 999], labels=["riesgo", "gris", "segura"]).astype(str)
    return x


def beneish(w: pd.DataFrame) -> pd.DataFrame:
    ventas = w.ventas
    margen_bruto = (w.ventas + w.coste_mercancia) / ventas           # coste de la mercancía viene en negativo
    ppe = w.inmovilizado_material + w.derecho_uso
    dep = -w.amortizaciones
    sga = -w.gastos_explotacion
    deuda = w.pasivo_corriente + w.deuda_financiera_lp + w.arrendamiento_lp
    ta = w.total_activo
    ind = pd.DataFrame(index=w.index)
    ind["DSRI"] = (w.deudores / ventas) / (w.deudores / ventas).shift(1)
    ind["GMI"] = margen_bruto.shift(1) / margen_bruto
    ind["AQI"] = (1 - (w.activo_corriente + ppe) / ta) / (1 - (w.activo_corriente + ppe) / ta).shift(1)
    ind["SGI"] = ventas / ventas.shift(1)
    ind["DEPI"] = (dep / (dep + ppe)).shift(1) / (dep / (dep + ppe))
    ind["SGAI"] = (sga / ventas) / (sga / ventas).shift(1)
    ind["LVGI"] = (deuda / ta) / (deuda / ta).shift(1)
    ind["TATA"] = (w.resultado_neto - w.flujo_explotacion) / ta
    coef = dict(DSRI=0.920, GMI=0.528, AQI=0.404, SGI=0.892, DEPI=0.115, SGAI=-0.172, TATA=4.679, LVGI=-0.327)
    contrib = pd.DataFrame({k: ind[k] * c for k, c in coef.items()})
    ind["M"] = -4.84 + contrib.sum(axis=1)
    # Control NIIF 16: el flujo de explotación no resta los pagos de alquiler (van a financiación) y eso favorece el TATA.
    # Se recalcula M restando esos pagos del flujo de explotación (pago_arrendamientos viene en negativo).
    tata_aj = (w.resultado_neto - (w.flujo_explotacion + w.pago_arrendamientos)) / ta
    ind["M_ajustado_NIIF16"] = ind.M + 4.679 * (tata_aj - ind.TATA)
    ind = ind.dropna()
    contrib = contrib.loc[ind.index]
    ind["alerta_-1.78"] = ind.M > -1.78
    ind["alerta_-2.22"] = ind.M > -2.22
    return ind, contrib


def estilo(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    ax.grid(axis="y", color=GRID)


def graficos(a: pd.DataFrame, m: pd.DataFrame):
    mpl.rcParams.update({"font.family": ["Segoe UI", "DejaVu Sans"], "savefig.dpi": 200})
    es = lambda v, n=1: f"{v:.{n}f}".replace(".", ",")

    fig, ax = plt.subplots(figsize=(10, 5.2))
    fig.patch.set_facecolor(SURFACE); ax.set_facecolor(SURFACE); estilo(ax)
    x = a.index.tolist()
    ax.plot(x, a.Z2, color=BLUE, lw=2, solid_capstyle="round", zorder=3)
    ax.plot(x, a.Z2, "o", color=BLUE, markersize=9, markeredgecolor=SURFACE, markeredgewidth=2, zorder=4)
    for xi, v in zip(x, a.Z2):
        ax.text(xi, v + 0.5, es(v), ha="center", va="bottom", fontsize=10.5, color=INK, fontweight="bold")
    for nivel, txt in ((2.6, "Zona segura: por encima de 2,6"), (1.1, "Zona de riesgo: por debajo de 1,1")):
        ax.axhline(nivel, color=MUTED, lw=1, zorder=2)
        ax.text(x[0] - 0.25, nivel + 0.2, txt, fontsize=9.5, color=INK2, va="bottom")
    ax.set_xticks(x); ax.set_xlim(x[0] - 0.3, x[-1] + 0.3)
    ax.set_ylim(0, max(a.Z2) * 1.2)
    fig.text(0.05, 0.94, f"El Z'' de Altman de Inditex ({es(a.Z2.min())}-{es(a.Z2.max())}) queda muy por encima de la zona segura", fontsize=16.5, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.05, 0.865, "Altman Z'' (versión para empresas no industriales), ejercicios 2020-2025", fontsize=11.5, color=INK2, ha="left", va="top")
    fig.text(0.05, 0.02, "Fuente: cuentas anuales consolidadas de Inditex. Elaboración propia. Herramienta de cribado, no una prueba.", fontsize=8.5, color=MUTED, ha="left", va="bottom")
    fig.subplots_adjust(left=0.06, right=0.97, top=0.76, bottom=0.12)
    fig.savefig(ROOT / "informe" / "graficos" / "12_altman.png", facecolor=SURFACE)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5.2))
    fig.patch.set_facecolor(SURFACE); ax.set_facecolor(SURFACE); estilo(ax)
    x = m.index.tolist()
    for serie, color, nombre, dy in ((m.M, BLUE, "M-score", -0.09), (m.M_ajustado_NIIF16, ORANGE, "M ajustado NIIF 16", 0.09)):
        ax.plot(x, serie, color=color, lw=2, solid_capstyle="round", zorder=3, label=nombre)
        ax.plot(x, serie, "o", color=color, markersize=9, markeredgecolor=SURFACE, markeredgewidth=2, zorder=4)
        # Etiqueta selectiva: solo el último año; el resto está en el CSV
        ax.text(x[-1], serie.iloc[-1] + dy, es(serie.iloc[-1], 2), ha="center", va="bottom" if dy > 0 else "top", fontsize=10.5, color=INK, fontweight="bold")
    for nivel, txt in ((-1.78, "Umbral de alerta −1,78"), (-2.22, "Umbral estricto −2,22")):
        ax.axhline(nivel, color=MUTED, lw=1.2, zorder=2)
        ax.text(x[-1] + 0.45, nivel + 0.03, txt, fontsize=9.5, color=INK2, va="bottom", ha="right")
    ax.set_xticks(x)
    ax.set_ylim(-3.4, -1.5)
    ax.set_xlim(x[0] - 0.4, x[-1] + 0.5)
    ax.legend(loc="lower left", frameon=False, ncol=2, fontsize=10, labelcolor=INK2)
    bajo = int((m.M_ajustado_NIIF16.max() <= -2.22))
    titulo = ("Beneish: Inditex queda bajo los umbrales de alerta, también ajustando por NIIF 16"
              if bajo and (m.M <= -2.22).all() else "Beneish: el M-score de Inditex roza o supera algún umbral de alerta")
    fig.text(0.05, 0.94, titulo, fontsize=15.5, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.05, 0.865, "Beneish M-score por ejercicio. Por encima de un umbral = se parece a empresas que maquillaron cuentas; más abajo = más tranquilizador", fontsize=11, color=INK2, ha="left", va="top")
    fig.text(0.05, 0.02, "Fuente: cuentas anuales consolidadas de Inditex. Elaboración propia. Herramienta de cribado, no una prueba.", fontsize=8.5, color=MUTED, ha="left", va="bottom")
    fig.subplots_adjust(left=0.06, right=0.97, top=0.76, bottom=0.12)
    fig.savefig(ROOT / "informe" / "graficos" / "13_beneish.png", facecolor=SURFACE)
    plt.close(fig)


def main():
    pd.set_option("display.width", 200)
    w = cargar()
    a = altman(w)
    m, contrib = beneish(w)
    print("ALTMAN Z'':\n", a.round(3).to_string())
    print("\nBENEISH:\n", m.round(3).to_string())
    print("\nContribución de cada variable a M (incluye el término -4,84 aparte):\n", contrib.round(3).to_string())
    out = ROOT / "data" / "processed"
    a.to_csv(out / "calidad_contable_altman.csv", encoding="utf-8")
    m.to_csv(out / "calidad_contable_beneish.csv", encoding="utf-8")
    contrib.to_csv(out / "calidad_contable_beneish_contribuciones.csv", encoding="utf-8")
    graficos(a, m)


if __name__ == "__main__":
    main()
