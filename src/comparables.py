"""Valoración por comparables: qué valdría Inditex si el mercado la valorase como a H&M, Fast Retailing o Next.

Dos métodos (mismos datos que la hoja «Comparables» del Excel):

1. P/E forward:  valor = P/E forward del comparable x BPA forward de Inditex
2. EV/EBITDA:    el EV de Yahoo incluye los alquileres como deuda (y el EBITDA es antes de alquileres, NIIF 16), así que
                 valor del capital = múltiplo x EBITDA - pasivos por arrendamiento + posición financiera neta

Salida: data/processed/comparables_valor_implicito.csv y el gráfico informe/graficos/09_campo_de_futbol.png
"""
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import dcf_model as M

ROOT = Path(__file__).resolve().parents[1]

# Inditex, últimos 12 meses a 31/07/2026 = ejercicio 2025 - 1S2025 + 1S2026 (cuentas y resultados oficiales, M EUR)
EBITDA_TTM = 11267 - 5114 + 5513
ARRENDAMIENTOS = 4549 + 1648          # 31/07/2026
PFN = M.MERCADO["efectivo"] + M.MERCADO["inv_temporales"] - M.MERCADO["deuda_financiera"]
PRECIO, ACCIONES = M.MERCADO["precio"], M.MERCADO["acciones"]

# Otras referencias para el campo de fútbol (€ por acción)
RANGO_52S = (46.07, 59.42)             # Yahoo Finance, 07/10/2026
OBJETIVO_ANALISTAS = (41.50, 65.00, 59.54)   # mínimo, máximo, media; 24 analistas, Bolsamanía 31/08/2026


def valores_implicitos() -> tuple[pd.DataFrame, float]:
    c = pd.read_csv(ROOT / "data" / "market" / "comparables_2026-10-07.csv")
    ino = c[c.empresa == "Inditex"].iloc[0]
    peers = c[c.empresa != "Inditex"].copy()
    bpa_fwd = PRECIO / ino.per_forward           # BPA forward implícito en el P/E forward de Yahoo
    peers["valor_per"] = peers.per_forward * bpa_fwd
    peers["valor_ev_ebitda"] = (peers.ev_ebitda * EBITDA_TTM - ARRENDAMIENTOS + PFN) / ACCIONES
    return peers, bpa_fwd


def resumen(peers: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for col, nombre in (("valor_per", "P/E forward"), ("valor_ev_ebitda", "EV/EBITDA")):
        v = peers[col]
        sin_fr = peers[peers.empresa != "Fast Retailing"][col]
        filas.append(dict(metodo=nombre, minimo=v.min(), mediana=v.median(), media=v.mean(), maximo=v.max(),
                          media_sin_fast_retailing=sin_fr.mean()))
    return pd.DataFrame(filas)


def campo_de_futbol(rs: pd.DataFrame):
    dcf = {k: M.valorar(k)["por_accion_hoy"] for k in (1, 2, 3)}
    filas = [  # etiqueta, bajo, alto, marcador, texto del marcador
        ("DCF (escenarios Bajo - Alto)", dcf[1], dcf[3], dcf[2], "Base"),
        ("Comparables: P/E forward", rs.loc[0, "minimo"], rs.loc[0, "maximo"], rs.loc[0, "mediana"], "mediana"),
        ("Comparables: EV/EBITDA", rs.loc[1, "minimo"], rs.loc[1, "maximo"], rs.loc[1, "mediana"], "mediana"),
        ("Precio objetivo de analistas", OBJETIVO_ANALISTAS[0], OBJETIVO_ANALISTAS[1], OBJETIVO_ANALISTAS[2], "media"),
        ("Rango de cotización 52 semanas", RANGO_52S[0], RANGO_52S[1], None, None),
    ]
    BLUE, ORANGE = "#2a78d6", "#eb6834"
    SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
    mpl.rcParams.update({"font.family": ["Segoe UI", "DejaVu Sans"], "savefig.dpi": 200})
    es = lambda x: f"{x:.0f} €"
    fig, ax = plt.subplots(figsize=(10, 5.6))
    fig.patch.set_facecolor(SURFACE); ax.set_facecolor(SURFACE)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(AXIS); ax.grid(axis="x", color=GRID); ax.set_axisbelow(True); ax.tick_params(length=0)
    for i, (et, lo, hi, marca, txt) in enumerate(reversed(filas)):
        ax.barh(i, hi - lo, left=lo, height=0.46, color=BLUE, zorder=3)
        ax.text(lo - 0.8, i, es(lo), ha="right", va="center", fontsize=10, color=INK)
        ax.text(hi + 0.8, i, es(hi), ha="left", va="center", fontsize=10, color=INK)
        if marca is not None:
            ax.plot(marca, i, "o", color=INK, markersize=9, markeredgecolor=SURFACE, markeredgewidth=2, zorder=5)
            ax.text(marca, i + 0.36, f"{txt} {marca:.0f} €", ha="center", va="bottom", fontsize=9, color=INK2)
    ax.axvline(PRECIO, color=ORANGE, lw=2, zorder=4)
    ax.text(PRECIO, len(filas) - 0.3, f"Precio {PRECIO:.2f} €".replace(".", ","), ha="center", va="bottom", fontsize=10, color=INK, fontweight="bold")
    ax.set_yticks(range(len(filas))); ax.set_yticklabels([f[0] for f in reversed(filas)], color=INK2, fontsize=10.5)
    ax.set_xlim(20, 90); ax.set_xticks([30, 40, 50, 60, 70, 80]); ax.set_xticklabels([f"{t} €" for t in (30, 40, 50, 60, 70, 80)])
    fig.text(0.03, 0.95, "Cada método cuenta una parte de la historia sobre el valor de Inditex", fontsize=17, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.03, 0.885, "Valor por acción (€) según DCF, comparables, analistas y cotización. Punto = valor central", fontsize=11.5, color=INK2, ha="left", va="top")
    fig.text(0.03, 0.025, "Fuente: modelo DCF propio; Yahoo Finance (7/10/2026); Bolsamanía (consenso, 31/08/2026). Fast Retailing (crecimiento ≈22 %) ensancha el rango de comparables.",
             fontsize=8, color=MUTED, ha="left", va="bottom")
    fig.subplots_adjust(left=0.30, right=0.96, top=0.78, bottom=0.12)
    fig.savefig(ROOT / "informe" / "graficos" / "09_campo_de_futbol.png", facecolor=SURFACE)
    plt.close(fig)


def main():
    pd.set_option("display.width", 200)
    peers, bpa = valores_implicitos()
    print(f"BPA forward de Inditex (precio / P/E forward): {bpa:.3f} €  |  EBITDA 12 meses: {EBITDA_TTM:,} M€  |  alquileres {ARRENDAMIENTOS:,}  |  PFN {PFN:,.0f}")
    print(peers[["empresa", "per_forward", "ev_ebitda", "valor_per", "valor_ev_ebitda"]].round(2).to_string(index=False))
    rs = resumen(peers)
    print("\nResumen (€ por acción):\n", rs.round(2).to_string(index=False))
    # Control: el múltiplo EV/EBITDA propio de Inditex con mi EBITDA debería reproducir el precio
    ino = pd.read_csv(ROOT / "data" / "market" / "comparables_2026-10-07.csv").query("empresa == 'Inditex'").iloc[0]
    ctrl = (ino.ev_ebitda * EBITDA_TTM - ARRENDAMIENTOS + PFN) / ACCIONES
    print(f"\nControl EV/EBITDA propio: {ctrl:.2f} € frente al precio {PRECIO} € ({ctrl / PRECIO - 1:+.1%})")
    out = peers[["empresa", "per_forward", "ev_ebitda", "valor_per", "valor_ev_ebitda"]]
    out.to_csv(ROOT / "data" / "processed" / "comparables_valor_implicito.csv", index=False, encoding="utf-8")
    campo_de_futbol(rs)


if __name__ == "__main__":
    main()
