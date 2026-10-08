"""Cuánto pesa cada hipótesis en el valor por acción (escenario Base) y qué descuenta el mercado.

1. Tornado: se cambia una hipótesis cada vez entre un valor bajo y uno alto y se mide el valor por acción.
2. Paquetes coherentes de coste del capital (rf + beta x ERP).
3. DCF inverso: qué WACC o qué crecimiento perpetuo hacen que el valor sea igual al precio de mercado.
4. Escenario "tipo consenso": ventas y EBIT que publican los analistas hasta 2029E con el mismo coste del capital.
"""
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

import dcf_model as M

ROOT = Path(__file__).resolve().parents[1]
GRAF = ROOT / "informe" / "graficos"
PRECIO = M.MERCADO["precio"]
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"


def valor(mercado=None, overrides=None, escenario=2):
    return M.valorar(escenario, mercado=mercado, overrides=overrides)["por_accion_hoy"]


def desplazar(lista, delta):
    return [x + delta for x in lista]


def tornado():
    base = M.ESCENARIOS[2]
    v0 = valor()
    casos = [  # etiqueta, (bajo, alto) como funciones que devuelven (mercado, overrides)
        ("Prima de riesgo (ERP): 4,2 % ↔ 5,8 %", dict(erp=0.042), dict(erp=0.058), None, None),
        ("Beta: 0,8 ↔ 1,1", dict(beta=0.8), dict(beta=1.1), None, None),
        ("Tipo libre de riesgo: 3,57 % ↔ 4,11 %", dict(rf=0.0357), dict(rf=0.0411), None, None),
        ("Crecimiento a perpetuidad: 2,0 % ↔ 3,0 %", dict(g_terminal=0.02), dict(g_terminal=0.03), None, None),
        ("Margen EBIT: ±1,5 pp todos los años", None, None,
         dict(margen_ebit=desplazar(base["margen_ebit"], +0.015)), dict(margen_ebit=desplazar(base["margen_ebit"], -0.015))),
        ("Crecimiento de ventas: ±1 pp todos los años", None, None,
         dict(crecimiento=desplazar(base["crecimiento"], +0.01)), dict(crecimiento=desplazar(base["crecimiento"], -0.01))),
        ("Capex: ±0,5 pp de ventas todos los años", None, None,
         dict(capex_pct=desplazar(base["capex_pct"], -0.005)), dict(capex_pct=desplazar(base["capex_pct"], +0.005))),
    ]
    filas = []
    for etq, m_lo, m_hi, o_hi, o_lo in casos:
        if m_lo is not None:   # hipótesis de mercado: "bajo" = valor numérico bajo del parámetro
            a, b = valor(mercado=m_lo), valor(mercado=m_hi)
        else:                  # hipótesis operativas: "alto" = mejor para el valor
            a, b = valor(overrides=o_lo), valor(overrides=o_hi)
        filas.append(dict(hipotesis=etq, valor_a=a, valor_b=b, minimo=min(a, b), maximo=max(a, b), amplitud=abs(a - b)))
    df = pd.DataFrame(filas).sort_values("amplitud", ascending=False).reset_index(drop=True)
    return v0, df


def paquetes():
    cs = [
        ("Actual (propuesta inicial)", dict(rf=0.0411, beta=0.90, erp=0.050)),
        ("A. Académico coherente: Bund, ERP ponderada, beta 1,0", dict(rf=0.0357, beta=1.00, erp=0.054)),
        ("B. Bund, ERP de mercado maduro, beta 0,9 (Investing)", dict(rf=0.0357, beta=0.90, erp=0.0417)),
        ("C. Bono español, ERP España (Damodaran), beta 1,0", dict(rf=0.0411, beta=1.00, erp=0.0578)),
        ("D. Bund, ERP 5,0 %, beta del sector (0,8)", dict(rf=0.0357, beta=0.80, erp=0.050)),
    ]
    filas = []
    for nombre, p in cs:
        ke = p["rf"] + p["beta"] * p["erp"]
        filas.append(dict(paquete=nombre, **p, ke=ke, **{f"valor_{M.ESCENARIOS[k]['nombre'].lower()}": valor(mercado=p, escenario=k) for k in (1, 2, 3)}))
    return pd.DataFrame(filas)


def biseccion(f, lo, hi, objetivo, it=60):
    flo = f(lo) - objetivo
    for _ in range(it):
        mid = (lo + hi) / 2
        fm = f(mid) - objetivo
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return (lo + hi) / 2


def dcf_inverso():
    w0 = M.wacc(M.MERCADO)
    # WACC implícito: se fuerza ke = rf con beta 0
    wacc_imp = biseccion(lambda r: valor(mercado=dict(rf=r, beta=0.0, erp=0.0)), 0.05, 0.12, PRECIO)
    g_imp = biseccion(lambda g: valor(mercado=dict(g_terminal=g)), 0.0, w0 - 0.004, PRECIO)
    base = M.ESCENARIOS[2]["crecimiento"]
    delta = biseccion(lambda d: valor(overrides=dict(crecimiento=desplazar(base, d))), -0.02, 0.05, PRECIO)
    return dict(wacc_base=w0, wacc_implicito=wacc_imp, g_implicito=g_imp, extra_crecimiento_pp=delta)


def consenso():
    # Consenso (Bolsamanía, 31/08/2026). Se asume que "2027e" = ejercicio que acaba el 31/01/2027 (= FY2026E aquí),
    # porque 42.727 M€ es +7,2 % sobre las ventas de 39.864 M€ del último ejercicio cerrado.
    ventas = [39864, 42727, 45862, 49068, 53086]
    ebit = [7997, 8733, 9522, 10344, 11446]
    crec = [ventas[i + 1] / ventas[i] - 1 for i in range(4)]
    marg = [ebit[i + 1] / ventas[i + 1] for i in range(4)]
    cola_c = [0.065, 0.060, 0.050, 0.040, 0.035, 0.030]
    crec_full = crec + cola_c
    marg_full = marg + [marg[-1]] * 6
    return dict(crecimiento=crec_full, margen_ebit=marg_full), crec, marg


def figuras(v0, df):
    mpl.rcParams.update({"font.family": ["Segoe UI", "DejaVu Sans"], "savefig.dpi": 200})
    fig, ax = plt.subplots(figsize=(10, 5.6))
    fig.patch.set_facecolor(SURFACE); ax.set_facecolor(SURFACE)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(AXIS); ax.grid(axis="x", color=GRID); ax.set_axisbelow(True); ax.tick_params(length=0)
    d = df.iloc[::-1].reset_index(drop=True)
    ax.barh(d.index, d.maximo - d.minimo, left=d.minimo, height=0.5, color=BLUE, zorder=3)
    ax.axvline(v0, color=INK, lw=1.5, zorder=4)
    ax.axvline(PRECIO, color=ORANGE, lw=2, zorder=4)
    ax.set_yticks(d.index); ax.set_yticklabels(d.hipotesis, color=INK2, fontsize=10)
    for i, r in d.iterrows():
        ax.text(r.minimo - 0.4, i, f"{r.minimo:.0f} €".replace(".", ","), ha="right", va="center", fontsize=10, color=INK)
        ax.text(r.maximo + 0.4, i, f"{r.maximo:.0f} €".replace(".", ","), ha="left", va="center", fontsize=10, color=INK)
    ax.set_xlim(22, 78); ax.set_xticks([30, 40, 50, 60, 70]); ax.set_xticklabels([f"{t} €" for t in (30, 40, 50, 60, 70)])
    ax.text(v0, len(d) - 0.35, f"Base {v0:.1f} €".replace(".", ","), ha="center", va="bottom", fontsize=10, color=INK, fontweight="bold")
    ax.text(PRECIO, len(d) - 0.35, f"Precio {PRECIO:.2f} €".replace(".", ","), ha="center", va="bottom", fontsize=10, color=INK, fontweight="bold")
    fig.text(0.03, 0.95, "El coste del capital pesa más que cualquier hipótesis operativa", fontsize=17, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.03, 0.885, "Valor por acción (escenario Base) al cambiar una hipótesis cada vez entre el extremo bajo y el alto", fontsize=11.5, color=INK2, ha="left", va="top")
    fig.text(0.03, 0.025, "Fuente: modelo DCF propio (src/dcf_model.py). Elaboración propia.", fontsize=8.5, color=MUTED, ha="left", va="bottom")
    fig.subplots_adjust(left=0.36, right=0.96, top=0.78, bottom=0.12)
    fig.savefig(GRAF / "07_tornado_hipotesis.png", facecolor=SURFACE)
    plt.close(fig)

    # Betas
    b = pd.read_csv(ROOT / "data" / "market" / "beta_inditex.csv").dropna(subset=["beta"])
    b = b[b.periodo == "5 años"].copy()
    b["etq"] = b.indice + " · " + b.frecuencia
    b = b.sort_values("beta").reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(10, 5.0))
    fig.patch.set_facecolor(SURFACE); ax.set_facecolor(SURFACE)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(AXIS); ax.grid(axis="x", color=GRID); ax.set_axisbelow(True); ax.tick_params(length=0)
    ax.hlines(b.index, b.ic95_bajo, b.ic95_alto, color=BLUE, lw=2, zorder=3)
    ax.plot(b.beta, b.index, "o", color=BLUE, markersize=9, markeredgecolor=SURFACE, markeredgewidth=2, zorder=4)
    for ref, col, txt in ((0.90, ORANGE, "Investing.com 0,90"), (0.79, AQUA, "Sector (Damodaran) 0,79")):
        ax.axvline(ref, color=col, lw=2, zorder=2)
    ax.text(0.90, len(b) - 0.35, "Investing.com 0,90", color=INK2, fontsize=9.5, ha="left", va="bottom")
    ax.text(0.79, len(b) - 0.35, "Sector 0,79", color=INK2, fontsize=9.5, ha="right", va="bottom")
    ax.set_yticks(b.index); ax.set_yticklabels(b.etq, color=INK2, fontsize=10)
    for i, r in b.iterrows():
        ax.text(r.ic95_alto + 0.03, i, f"{r.beta:.2f}".replace(".", ","), va="center", fontsize=10, color=INK, fontweight="bold")
    ax.set_xlim(0.5, 2.0)
    fig.text(0.03, 0.94, "La beta de Inditex por regresión ronda 1,0-1,2, por encima del 0,90 publicado", fontsize=16, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.03, 0.865, "Beta a 5 años con intervalo de confianza del 95 % según índice y frecuencia de los datos", fontsize=11.5, color=INK2, ha="left", va="top")
    fig.text(0.03, 0.02, "Fuente: Yahoo Finance (cierres ajustados), Investing.com, Damodaran (ene-2026). Elaboración propia.", fontsize=8.5, color=MUTED, ha="left", va="bottom")
    fig.subplots_adjust(left=0.27, right=0.96, top=0.74, bottom=0.12)
    fig.savefig(GRAF / "08_beta_inditex.png", facecolor=SURFACE)
    plt.close(fig)


def main():
    pd.set_option("display.width", 220); pd.set_option("display.max_colwidth", 70)
    v0, df = tornado()
    print(f"Valor base: {v0:.2f} €  | precio {PRECIO:.2f} €\n")
    print(df.round(2).to_string(index=False))
    pq = paquetes()
    print("\nPaquetes de coste del capital:")
    print(pq.round(4).to_string(index=False))
    inv = dcf_inverso()
    print("\nDCF inverso (escenario Base):", {k: round(v, 4) for k, v in inv.items()})
    ov, crec, marg = consenso()
    print("\nConsenso -> crecimiento", [round(x, 3) for x in crec], "margen EBIT", [round(x, 3) for x in marg])
    for nombre, p in (("Ke actual 8,61 %", {}), ("Paquete A", dict(rf=0.0357, beta=1.0, erp=0.054)),
                      ("Paquete B", dict(rf=0.0357, beta=0.9, erp=0.0417)), ("Paquete D", dict(rf=0.0357, beta=0.8, erp=0.05))):
        print(f"  Operativo tipo consenso + {nombre}: {valor(mercado=p, overrides=ov):.2f} €")
    df.to_csv(ROOT / "data" / "processed" / "hipotesis_tornado.csv", index=False, encoding="utf-8")
    pq.to_csv(ROOT / "data" / "processed" / "hipotesis_paquetes_ke.csv", index=False, encoding="utf-8")
    figuras(v0, df)


if __name__ == "__main__":
    main()
