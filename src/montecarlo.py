"""Monte Carlo sobre el DCF de Inditex (escenario Base como centro).

En vez de tres escenarios, se repite el DCF N veces sacando al azar las hipótesis inciertas dentro de rangos razonables
(todos los parámetros están en PARAMS y explicados en docs/Guia_del_modelo.md). Se obtiene una distribución del valor por
acción y la probabilidad de que supere el precio de mercado.

Salida: data/processed/montecarlo_resumen.csv, montecarlo_drivers.csv y los gráficos 10 y 11.
"""
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import dcf_model as M

ROOT = Path(__file__).resolve().parents[1]
N = 20000
SEED = 2026

# media, desviación típica (o mínimo, moda, máximo en la triangular) y límites para recortar valores extremos
PARAMS = dict(
    beta=dict(media=1.00, sd=0.10, lim=(0.60, 1.40)),                 # error típico de la regresión (0,08-0,10)
    erp=dict(media=0.054, sd=0.005, lim=(0.040, 0.070)),              # rango Damodaran 4,2-5,8 %
    rf=dict(media=0.0357, sd=0.003, lim=(0.025, 0.048)),              # movimiento habitual del bono a 10 años
    g=dict(minimo=0.020, moda=0.025, maximo=0.030),                   # inflación objetivo BCE y crecimiento nominal
    crec=dict(sd=0.012, lim=(-0.04, 0.04)),                           # desplazamiento fijo sobre el camino Base, todos los años
    margen=dict(sd=0.012, lim=(-0.04, 0.04)),
    capex=dict(sd=0.004, lim=(-0.01, 0.01)),
    corr_crec_margen=0.3,                                             # más ventas suele diluir costes fijos
    spread_minimo_wacc_g=0.02,                                        # seguridad: WACC - g nunca por debajo de 2 pp
)
BLUE, ORANGE = "#2a78d6", "#eb6834"
SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"


def simular() -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    P = PARAMS
    z = rng.standard_normal((N, 2))
    rho = P["corr_crec_margen"]
    z_margen = rho * z[:, 0] + np.sqrt(1 - rho ** 2) * z[:, 1]       # correlación mediante combinación lineal
    clip = lambda x, lim: np.clip(x, *lim)
    d = pd.DataFrame({
        "beta": clip(P["beta"]["media"] + P["beta"]["sd"] * rng.standard_normal(N), P["beta"]["lim"]),
        "erp": clip(P["erp"]["media"] + P["erp"]["sd"] * rng.standard_normal(N), P["erp"]["lim"]),
        "rf": clip(P["rf"]["media"] + P["rf"]["sd"] * rng.standard_normal(N), P["rf"]["lim"]),
        "g": rng.triangular(P["g"]["minimo"], P["g"]["moda"], P["g"]["maximo"], N),
        "crec": clip(P["crec"]["sd"] * z[:, 0], P["crec"]["lim"]),
        "margen": clip(P["margen"]["sd"] * z_margen, P["margen"]["lim"]),
        "capex": clip(P["capex"]["sd"] * rng.standard_normal(N), P["capex"]["lim"]),
    })
    base_esc = M.ESCENARIOS[2]
    base = M.datos_base()
    valores, ajustes = [], 0
    for r in d.itertuples(index=False):
        wacc = r.rf + r.beta * r.erp                                  # peso de la deuda 0: WACC = Ke
        g = r.g
        if wacc - g < P["spread_minimo_wacc_g"]:
            g, ajustes = wacc - P["spread_minimo_wacc_g"], ajustes + 1
        v = M.valorar(
            2, mercado=dict(rf=r.rf, beta=r.beta, erp=r.erp, g_terminal=g), base=base,
            overrides=dict(
                crecimiento=[x + r.crec for x in base_esc["crecimiento"]],
                margen_ebit=[x + r.margen for x in base_esc["margen_ebit"]],
                capex_pct=[x + r.capex for x in base_esc["capex_pct"]],
            ),
        )
        valores.append(v["por_accion_hoy"])
    d["valor"] = valores
    d.attrs["ajustes_g"] = ajustes
    return d


def resumir(d: pd.DataFrame) -> pd.DataFrame:
    v = d["valor"]
    precio = M.MERCADO["precio"]
    filas = {
        "simulaciones": len(v), "media": v.mean(), "desviacion_tipica": v.std(),
        "p5": v.quantile(.05), "p25": v.quantile(.25), "mediana": v.median(), "p75": v.quantile(.75), "p95": v.quantile(.95),
        "minimo": v.min(), "maximo": v.max(),
        "valor_base_determinista": M.valorar(2)["por_accion_hoy"], "precio_mercado": precio,
        "prob_supera_precio": float((v >= precio).mean()), "prob_inferior_30": float((v < 30).mean()),
        "prob_supera_50": float((v >= 50).mean()), "ajustes_g": d.attrs["ajustes_g"],
    }
    return pd.DataFrame({"metrica": list(filas), "valor": list(filas.values())})


def drivers(d: pd.DataFrame) -> pd.DataFrame:
    nombres = dict(erp="Prima de riesgo (ERP)", beta="Beta", crec="Crecimiento de ventas", margen="Margen EBIT",
                   g="Crecimiento a perpetuidad (g)", rf="Tipo libre de riesgo", capex="Capex")
    # Spearman = correlación de Pearson entre los rangos (así no hace falta scipy)
    rv = d["valor"].rank()
    c = {k: d[k].rank().corr(rv) for k in nombres}
    out = pd.DataFrame({"hipotesis": [nombres[k] for k in c], "correlacion_con_valor": list(c.values())})
    return out.reindex(out.correlacion_con_valor.abs().sort_values(ascending=False).index).reset_index(drop=True)


def estilo(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def graficos(d: pd.DataFrame, rs: pd.DataFrame, dr: pd.DataFrame):
    mpl.rcParams.update({"font.family": ["Segoe UI", "DejaVu Sans"], "savefig.dpi": 200})
    r = dict(zip(rs.metrica, rs.valor))
    es = lambda x, n=0: f"{x:.{n}f}".replace(".", ",")
    pct = r["prob_supera_precio"]

    fig, ax = plt.subplots(figsize=(10, 5.6))
    fig.patch.set_facecolor(SURFACE); ax.set_facecolor(SURFACE); estilo(ax)
    ax.grid(axis="y", color=GRID)
    ax.hist(d["valor"], bins=70, range=(20, 90), color=BLUE, zorder=3, rwidth=0.92)
    ax.axvspan(r["p5"], r["p95"], color=BLUE, alpha=0.08, zorder=1)
    ymax = ax.get_ylim()[1]
    ax.set_ylim(0, ymax * 1.25)                      # espacio libre arriba para las etiquetas, fuera de las barras
    top = ymax * 1.22
    ax.axvline(r["precio_mercado"], color=ORANGE, lw=2.2, zorder=4)
    ax.axvline(r["mediana"], color=INK, lw=1.6, zorder=4)
    ax.text(r["precio_mercado"] + 0.6, top, f"Precio\n{es(r['precio_mercado'], 2)} €", color=INK, fontsize=10.5, fontweight="bold", va="top")
    ax.text(r["mediana"] - 0.6, top, f"Mediana\n{es(r['mediana'], 1)} €", color=INK, fontsize=10.5, fontweight="bold", va="top", ha="right")
    ax.set_yticks([]); ax.set_xlim(20, 90)
    ax.set_xticks(range(20, 91, 10)); ax.set_xticklabels([f"{t} €" for t in range(20, 91, 10)], color=MUTED)
    fig.text(0.04, 0.95, f"Solo el {pct:.0%} de las simulaciones valora Inditex por encima del precio", fontsize=17, fontweight="bold", color=INK, ha="left", va="top")
    n_sim = f"{int(r['simulaciones']):,}".replace(",", ".")
    fig.text(0.04, 0.885, f"Valor por acción en {n_sim} simulaciones del DCF. Banda sombreada: 90 % de los casos, de {es(r['p5'])} € a {es(r['p95'])} €",
             fontsize=11.5, color=INK2, ha="left", va="top")
    fig.text(0.04, 0.025, "Fuente: modelo DCF propio (src/montecarlo.py). Rangos de las hipótesis basados en regresión de beta, Damodaran, BCE, consenso y Bankinter.", fontsize=8.5, color=MUTED, ha="left", va="bottom")
    fig.subplots_adjust(left=0.04, right=0.97, top=0.78, bottom=0.13)
    fig.savefig(ROOT / "informe" / "graficos" / "10_montecarlo_histograma.png", facecolor=SURFACE)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 4.8))
    fig.patch.set_facecolor(SURFACE); ax.set_facecolor(SURFACE); estilo(ax)
    ax.grid(axis="x", color=GRID)
    dd = dr.iloc[::-1].reset_index(drop=True)
    ax.barh(dd.index, dd.correlacion_con_valor, height=0.5, color=BLUE, zorder=3)
    ax.axvline(0, color=AXIS, lw=1)
    for i, x in enumerate(dd.correlacion_con_valor):
        ax.text(x + (0.015 if x >= 0 else -0.015), i, es(x, 2), va="center", ha="left" if x >= 0 else "right", fontsize=10, color=INK)
    ax.set_yticks(dd.index); ax.set_yticklabels(dd.hipotesis, color=INK2, fontsize=10.5)
    ax.set_xlim(-0.85, 0.85)
    fig.text(0.03, 0.94, "El crecimiento y el margen son las mayores fuentes de incertidumbre del valor", fontsize=16, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.03, 0.865, "Correlación (Spearman) entre cada hipótesis y el valor por acción. Si es negativa, cuanto mayor la hipótesis, menor el valor", fontsize=11.5, color=INK2, ha="left", va="top")
    fig.text(0.03, 0.02, "Fuente: simulación Monte Carlo propia (src/montecarlo.py).", fontsize=8.5, color=MUTED, ha="left", va="bottom")
    fig.subplots_adjust(left=0.30, right=0.97, top=0.76, bottom=0.12)
    fig.savefig(ROOT / "informe" / "graficos" / "11_montecarlo_drivers.png", facecolor=SURFACE)
    plt.close(fig)


def main():
    d = simular()
    rs, dr = resumir(d), drivers(d)
    pd.set_option("display.width", 160)
    print(rs.to_string(index=False, float_format=lambda x: f"{x:,.4f}"))
    print("\nCorrelación de cada hipótesis con el valor:\n", dr.round(3).to_string(index=False))
    out = ROOT / "data" / "processed"
    rs.to_csv(out / "montecarlo_resumen.csv", index=False, encoding="utf-8")
    dr.to_csv(out / "montecarlo_drivers.csv", index=False, encoding="utf-8")
    graficos(d, rs, dr)


if __name__ == "__main__":
    main()
