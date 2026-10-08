"""Gráficos del informe en PDF, en español e inglés (sin título dentro de la imagen: el título va en el pie de figura).

Todos los datos salen de los mismos módulos y CSV del proyecto; solo cambian los textos.
Salida: informe/report_assets/es/*.png e informe/report_assets/en/*.png
"""
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import calidad_contable as CC
import comparables as CP
import dcf_model as M
import hipotesis_analisis as HA
import montecarlo as MC

ROOT = Path(__file__).resolve().parents[1]
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
W = 6.85  # ancho útil de una página A4 con márgenes de 18 mm, en pulgadas

T = {
    "es": dict(
        dcf="DCF (Bajo - Alto)", pe="Comparables: P/E forward", ev="Comparables: EV/EBITDA", an="Precio objetivo de analistas",
        r52="Cotización 52 semanas", base="Base", mediana="mediana", media="media", precio="Precio",
        ventas="Ventas (miles de millones de €)", cc="a t.c.", ebitda="EBITDA", ebit="EBIT", neto="Neto",
        mediana_mc="Mediana", banda="90 % de los casos",
        tornado=dict(erp="Prima de riesgo: 4,2 % - 5,8 %", beta="Beta: 0,8 - 1,1", rf="Tipo libre de riesgo: 3,57 % - 4,11 %",
                     g="Crecimiento perpetuo: 2,0 % - 3,0 %", margen="Margen EBIT: ±1,5 pp", crec="Crecimiento de ventas: ±1 pp",
                     capex="Capex: ±0,5 pp de ventas"),
        base_tornado="Base", altman="Altman Z'' (zona segura > 2,6)", beneish="Beneish M (alerta > −1,78)", seguro="Zona segura 2,6",
        riesgo="Zona de riesgo 1,1", um="Umbral de alerta −1,78", ue="Umbral estricto −2,22", m="M-score", maj="M ajustado NIIF 16",
        dec=","),
    "en": dict(
        dcf="DCF (Low - High)", pe="Peers: forward P/E", ev="Peers: EV/EBITDA", an="Analysts' price target",
        r52="52-week trading range", base="Base", mediana="median", media="mean", precio="Price",
        ventas="Sales (EUR billion)", cc="const. FX", ebitda="EBITDA", ebit="EBIT", neto="Net",
        mediana_mc="Median", banda="90 % of runs",
        tornado=dict(erp="Equity risk premium: 4.2 % - 5.8 %", beta="Beta: 0.8 - 1.1", rf="Risk-free rate: 3.57 % - 4.11 %",
                     g="Perpetual growth: 2.0 % - 3.0 %", margen="EBIT margin: ±1.5 pp", crec="Sales growth: ±1 pp",
                     capex="Capex: ±0.5 pp of sales"),
        base_tornado="Base", altman="Altman Z'' (safe zone > 2.6)", beneish="Beneish M (alert > −1.78)", seguro="Safe zone 2.6",
        riesgo="Risk zone 1.1", um="Alert threshold −1.78", ue="Strict threshold −2.22", m="M-score", maj="M adjusted for IFRS 16",
        dec="."),
}


def fmt(x, d=0, lang="es"):
    s = f"{x:.{d}f}"
    return s.replace(".", ",") if lang == "es" else s


def base_axes(figsize, ncols=1):
    mpl.rcParams.update({"font.family": ["Segoe UI", "DejaVu Sans"], "savefig.dpi": 220, "font.size": 8.5})
    fig, axes = plt.subplots(1, ncols, figsize=figsize)
    fig.patch.set_facecolor(SURFACE)
    axs = np.atleast_1d(axes)
    for ax in axs:
        ax.set_facecolor(SURFACE)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.spines["bottom"].set_color(AXIS)
        ax.tick_params(length=0, labelsize=8.5, colors=MUTED)
        ax.set_axisbelow(True)
    return fig, axs


def guardar(fig, lang, nombre):
    out = ROOT / "informe" / "report_assets" / lang
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / nombre, facecolor=SURFACE)
    plt.close(fig)


def fig_football(lang):
    t = T[lang]
    peers, _ = CP.valores_implicitos()
    rs = CP.resumen(peers)
    dcf = {k: M.valorar(k)["por_accion_hoy"] for k in (1, 2, 3)}
    filas = [(t["dcf"], dcf[1], dcf[3], dcf[2], t["base"]), (t["pe"], rs.loc[0, "minimo"], rs.loc[0, "maximo"], rs.loc[0, "mediana"], t["mediana"]),
             (t["ev"], rs.loc[1, "minimo"], rs.loc[1, "maximo"], rs.loc[1, "mediana"], t["mediana"]),
             (t["an"], CP.OBJETIVO_ANALISTAS[0], CP.OBJETIVO_ANALISTAS[1], CP.OBJETIVO_ANALISTAS[2], t["media"]),
             (t["r52"], CP.RANGO_52S[0], CP.RANGO_52S[1], None, None)]
    fig, (ax,) = base_axes((W, 3.1))
    ax.grid(axis="x", color=GRID)
    for i, (et, lo, hi, mar, txt) in enumerate(reversed(filas)):
        ax.barh(i, hi - lo, left=lo, height=0.46, color=BLUE, zorder=3)
        caja = dict(facecolor=SURFACE, edgecolor="none", pad=0.8)   # fondo para que la línea del precio no tache la etiqueta
        ax.text(lo - 0.8, i, f"{lo:.0f} €", ha="right", va="center", fontsize=8.5, color=INK, zorder=6, bbox=caja)
        ax.text(hi + 0.8, i, f"{hi:.0f} €", ha="left", va="center", fontsize=8.5, color=INK, zorder=6, bbox=caja)
        if mar is not None:
            ax.plot(mar, i, "o", color=INK, markersize=7, markeredgecolor=SURFACE, markeredgewidth=1.5, zorder=5)
            ax.text(mar, i + 0.34, f"{txt} {mar:.0f} €", ha="center", va="bottom", fontsize=7.5, color=INK2)
    ax.axvline(CP.PRECIO, color=ORANGE, lw=1.8, zorder=4)
    ax.text(CP.PRECIO, len(filas) - 0.35, f"{t['precio']} {fmt(CP.PRECIO, 2, lang)} €", ha="center", va="bottom", fontsize=8.5, color=INK, fontweight="bold")
    ax.set_yticks(range(len(filas))); ax.set_yticklabels([f[0] for f in reversed(filas)], color=INK2, fontsize=8.5)
    ax.set_xlim(20, 90); ax.set_xticks(range(30, 90, 10)); ax.set_xticklabels([f"{x} €" for x in range(30, 90, 10)])
    fig.subplots_adjust(left=0.30, right=0.97, top=0.9, bottom=0.1)
    guardar(fig, lang, "campo_futbol.png")


def fig_negocio(lang):
    t = T[lang]
    r = pd.read_csv(ROOT / "data" / "processed" / "inditex_ratios.csv", index_col=0)
    r.index = r.index.astype(int)
    fig, (a1, a2) = base_axes((W, 2.9), 2)
    x = r.index.values
    a1.bar(x, r.ventas_mm, width=0.55, color=BLUE, zorder=3)
    for xi, v in zip(x, r.ventas_mm):
        a1.text(xi, v + 0.8, fmt(v, 1, lang), ha="center", va="bottom", fontsize=8, color=INK, fontweight="bold")
    a1.set_xticks(x)
    etq = []
    for año, c in zip(x, r.crec_ventas):
        s = str(año)
        if not np.isnan(c):
            s += f"\n{'+' if c >= 0 else ''}{fmt(c, 1, lang)} %"
        if año == 2025:
            s += f"\n(+{fmt(7.0, 1, lang)} % {t['cc']})"
        etq.append(s)
    a1.set_xticklabels(etq, color=INK2, fontsize=7.5)
    a1.set_ylim(0, 47); a1.set_yticks([0, 10, 20, 30, 40]); a1.grid(axis="y", color=GRID)
    a1.set_title(t["ventas"], fontsize=8.5, color=INK2, loc="left")
    cols = [(t["ebitda"], r.margen_ebitda, BLUE), (t["ebit"], r.margen_ebit, ORANGE), (t["neto"], r.margen_neto, AQUA)]
    for nombre, s, c in cols:
        a2.plot(x, s.values, color=c, lw=2, solid_capstyle="round", zorder=3, label=nombre)
        a2.plot(x[-1], s.values[-1], "o", color=c, markersize=6.5, markeredgecolor=SURFACE, markeredgewidth=1.5, zorder=4)
        a2.annotate(f"{fmt(s.values[-1], 1, lang)} %", (x[-1], s.values[-1]), xytext=(7, 0), textcoords="offset points", va="center", fontsize=8, color=INK2, annotation_clip=False)
    a2.set_xticks(x); a2.set_xlim(x[0] - 0.2, x[-1] + 0.2)
    a2.set_ylim(0, 40); a2.set_yticks([0, 10, 20, 30]); a2.set_yticklabels([f"{v} %" for v in (0, 10, 20, 30)]); a2.grid(axis="y", color=GRID)
    a2.legend(loc="upper left", frameon=False, ncol=3, fontsize=8, labelcolor=INK2)
    a2.set_title("%", fontsize=8.5, color=INK2, loc="left")
    fig.subplots_adjust(left=0.07, right=0.93, top=0.9, bottom=0.2, wspace=0.28)
    guardar(fig, lang, "negocio.png")


def fig_tornado(lang):
    t = T[lang]
    v0, df = HA.tornado()
    clave = {"Prima de riesgo": "erp", "Beta": "beta", "Tipo libre": "rf", "Crecimiento a perpetuidad": "g", "Margen EBIT": "margen",
             "Crecimiento de ventas": "crec", "Capex": "capex"}
    df = df.copy()
    df["k"] = [next(v for k, v in clave.items() if h.startswith(k)) for h in df.hipotesis]
    d = df.iloc[::-1].reset_index(drop=True)
    fig, (ax,) = base_axes((W, 2.9))
    ax.grid(axis="x", color=GRID)
    ax.barh(d.index, d.maximo - d.minimo, left=d.minimo, height=0.5, color=BLUE, zorder=3)
    ax.axvline(v0, color=INK, lw=1.4, zorder=4)
    ax.axvline(CP.PRECIO, color=ORANGE, lw=1.8, zorder=4)
    for i, rw in d.iterrows():
        ax.text(rw.minimo - 0.4, i, f"{rw.minimo:.0f} €", ha="right", va="center", fontsize=8, color=INK)
        ax.text(rw.maximo + 0.4, i, f"{rw.maximo:.0f} €", ha="left", va="center", fontsize=8, color=INK)
    ax.set_yticks(d.index); ax.set_yticklabels([t["tornado"][k] for k in d.k], color=INK2, fontsize=8.2)
    ax.set_xlim(26, 62); ax.set_xticks([30, 40, 50, 60]); ax.set_xticklabels([f"{x} €" for x in (30, 40, 50, 60)])
    ax.text(v0, len(d) - 0.35, f"{t['base']} {fmt(v0, 1, lang)} €", ha="right", va="bottom", fontsize=8, color=INK, fontweight="bold")
    ax.text(CP.PRECIO, len(d) - 0.35, f"{t['precio']} {fmt(CP.PRECIO, 2, lang)} €", ha="left", va="bottom", fontsize=8, color=INK, fontweight="bold")
    fig.subplots_adjust(left=0.38, right=0.97, top=0.9, bottom=0.1)
    guardar(fig, lang, "tornado.png")


def fig_montecarlo(lang, d, rs):
    t = T[lang]
    r = dict(zip(rs.metrica, rs.valor))
    fig, (ax,) = base_axes((W, 2.8))
    ax.grid(axis="y", color=GRID)
    ax.hist(d["valor"], bins=70, range=(20, 90), color=BLUE, zorder=3, rwidth=0.92)
    ax.axvspan(r["p5"], r["p95"], color=BLUE, alpha=0.08, zorder=1)
    ymax = ax.get_ylim()[1]
    ax.set_ylim(0, ymax * 1.3)
    top = ymax * 1.25
    ax.axvline(r["precio_mercado"], color=ORANGE, lw=1.8, zorder=4)
    ax.axvline(r["mediana"], color=INK, lw=1.4, zorder=4)
    ax.text(r["precio_mercado"] + 0.6, top, f"{t['precio']}\n{fmt(r['precio_mercado'], 2, lang)} €", fontsize=8.2, color=INK, fontweight="bold", va="top")
    ax.text(r["mediana"] - 0.6, top, f"{t['mediana_mc']}\n{fmt(r['mediana'], 1, lang)} €", fontsize=8.2, color=INK, fontweight="bold", va="top", ha="right")
    ax.text(r["p95"] + 1.5, ymax * 0.55, f"{t['banda']}:\n{fmt(r['p5'], 0, lang)} € - {fmt(r['p95'], 0, lang)} €", fontsize=8, color=INK2, va="center")
    ax.set_yticks([]); ax.set_xlim(20, 90)
    ax.set_xticks(range(20, 91, 10)); ax.set_xticklabels([f"{x} €" for x in range(20, 91, 10)])
    fig.subplots_adjust(left=0.03, right=0.97, top=0.95, bottom=0.12)
    guardar(fig, lang, "montecarlo.png")


def fig_calidad(lang):
    t = T[lang]
    w = CC.cargar()
    a = CC.altman(w)
    m, _ = CC.beneish(w)
    fig, (a1, a2) = base_axes((W, 2.7), 2)
    x = a.index.tolist()
    a1.grid(axis="y", color=GRID)
    a1.plot(x, a.Z2, color=BLUE, lw=2, solid_capstyle="round", zorder=3)
    a1.plot(x, a.Z2, "o", color=BLUE, markersize=6.5, markeredgecolor=SURFACE, markeredgewidth=1.5, zorder=4)
    a1.text(x[-1], a.Z2.iloc[-1] + 0.4, fmt(a.Z2.iloc[-1], 1, lang), ha="center", va="bottom", fontsize=8.5, color=INK, fontweight="bold")
    for nivel, txt in ((2.6, t["seguro"]), (1.1, t["riesgo"])):
        a1.axhline(nivel, color=MUTED, lw=1, zorder=2)
        a1.text(x[0] - 0.2, nivel + 0.15, txt, fontsize=7.5, color=INK2, va="bottom")
    a1.set_xticks(x); a1.set_ylim(0, 7.5); a1.set_xlim(x[0] - 0.3, x[-1] + 0.4)
    a1.set_title(t["altman"], fontsize=8.5, color=INK2, loc="left")
    x2 = m.index.tolist()
    a2.grid(axis="y", color=GRID)
    for serie, c, nombre, dy in ((m.M, BLUE, t["m"], -0.1), (m.M_ajustado_NIIF16, ORANGE, t["maj"], 0.1)):
        a2.plot(x2, serie, color=c, lw=2, solid_capstyle="round", zorder=3, label=nombre)
        a2.plot(x2, serie, "o", color=c, markersize=6.5, markeredgecolor=SURFACE, markeredgewidth=1.5, zorder=4)
        a2.text(x2[-1], serie.iloc[-1] + dy, fmt(serie.iloc[-1], 2, lang), ha="center", va="bottom" if dy > 0 else "top", fontsize=8.2, color=INK, fontweight="bold")
    for nivel, txt in ((-1.78, t["um"]), (-2.22, t["ue"])):
        a2.axhline(nivel, color=MUTED, lw=1, zorder=2)
        a2.text(x2[-1] + 0.4, nivel + 0.03, txt, fontsize=7.5, color=INK2, va="bottom", ha="right")
    a2.set_xticks(x2); a2.set_ylim(-3.5, -1.4); a2.set_xlim(x2[0] - 0.3, x2[-1] + 0.4)
    a2.legend(loc="lower left", frameon=False, fontsize=7.5, labelcolor=INK2, ncol=2)
    a2.set_title(t["beneish"], fontsize=8.5, color=INK2, loc="left")
    fig.subplots_adjust(left=0.06, right=0.97, top=0.88, bottom=0.12, wspace=0.18)
    guardar(fig, lang, "calidad.png")


def main():
    d = MC.simular()
    rs = MC.resumir(d)
    for lang in ("es", "en"):
        fig_football(lang)
        fig_negocio(lang)
        fig_tornado(lang)
        fig_montecarlo(lang, d, rs)
        fig_calidad(lang)
        print("gráficos", lang, "ok")


if __name__ == "__main__":
    main()
