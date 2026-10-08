"""Beta de Inditex por regresión: rentabilidades de la acción frente a un índice de mercado.

beta = pendiente de la regresión  r_acción = alfa + beta · r_índice + error
(equivale a covarianza(acción, índice) / varianza(índice))

Se calcula con varios índices y periodos para ver si el resultado es estable.
Datos: Yahoo Finance (cierres ajustados por dividendos). Salida: data/market/beta_inditex.csv
"""
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "market"
HEADERS = {"User-Agent": "Mozilla/5.0"}
INDICES = {"EURO STOXX 50": "^STOXX50E", "STOXX Europe 600": "^STOXX", "IBEX 35": "^IBEX", "MSCI World (ETF URTH)": "URTH"}


def descargar(simbolo: str, intervalo: str, rango: str = "5y") -> pd.Series:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{simbolo}"
    r = requests.get(url, params={"range": rango, "interval": intervalo}, headers=HEADERS, timeout=30)
    r.raise_for_status()
    res = r.json()["chart"]["result"][0]
    precios = res["indicators"].get("adjclose", [{}])[0].get("adjclose") or res["indicators"]["quote"][0]["close"]
    idx = pd.to_datetime(res["timestamp"], unit="s").normalize()
    s = pd.Series(precios, index=idx, name=simbolo, dtype=float).dropna()
    return s[~s.index.duplicated(keep="last")]


def beta(r_acc: pd.Series, r_idx: pd.Series) -> dict:
    d = pd.concat([r_acc, r_idx], axis=1, join="inner").dropna()
    d.columns = ["a", "m"]
    n = len(d)
    cov = np.cov(d.a, d.m, ddof=1)
    b = cov[0, 1] / cov[1, 1]
    alfa = d.a.mean() - b * d.m.mean()
    resid = d.a - (alfa + b * d.m)
    se = np.sqrt(resid.var(ddof=2) / ((d.m - d.m.mean()) ** 2).sum())
    r2 = np.corrcoef(d.a, d.m)[0, 1] ** 2
    return dict(n=n, beta=b, error_tipico=se, ic95_bajo=b - 1.96 * se, ic95_alto=b + 1.96 * se, r2=r2,
                beta_ajustada_blume=0.67 * b + 0.33)


def main():
    filas = []
    precios = {}
    for intervalo, etiqueta in (("1wk", "semanal"), ("1mo", "mensual")):
        acc = descargar("ITX.MC", intervalo)
        precios[("ITX.MC", etiqueta)] = acc
        for nombre, simbolo in INDICES.items():
            try:
                idx = descargar(simbolo, intervalo)
            except Exception as e:  # algún símbolo puede no estar disponible
                print(f"AVISO {nombre} ({simbolo}) {etiqueta}: {e}")
                continue
            precios[(simbolo, etiqueta)] = idx
            ra, ri = acc.pct_change().dropna(), idx.pct_change().dropna()
            for periodo, desde in (("5 años", None), ("2 años", pd.Timestamp.today() - pd.DateOffset(years=2))):
                a, i = (ra, ri) if desde is None else (ra[ra.index >= desde], ri[ri.index >= desde])
                filas.append(dict(indice=nombre, frecuencia=etiqueta, periodo=periodo, **beta(a, i)))
    res = pd.DataFrame(filas)
    OUT.mkdir(parents=True, exist_ok=True)
    res.to_csv(OUT / "beta_inditex.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 200)
    print(res.round(3).to_string(index=False))
    return res


if __name__ == "__main__":
    main()
