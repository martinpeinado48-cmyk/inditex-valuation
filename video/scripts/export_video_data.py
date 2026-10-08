"""Exporta a JSON los datos reales del modelo para el vídeo de Remotion (video/src/data/modelData.json).

Reutiliza src/dcf_model.py y src/montecarlo.py del repositorio (misma semilla: reproduce las 20.000 simulaciones).
Uso, desde la raíz del repositorio:  python video/scripts/export_video_data.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]  # video/scripts/ -> raíz del repositorio
sys.path.insert(0, str(ROOT / "src"))
import dcf_model as M  # noqa: E402
import montecarlo as MC  # noqa: E402

out = {}

# Histórico de ventas y EBIT (millones de euros)
fin = pd.read_csv(ROOT / "data" / "processed" / "inditex_financials.csv", index_col=0)
out["historico"] = [dict(year=int(y), ventas=float(r.ventas), ebit=float(r.ebit)) for y, r in fin.iterrows()]

# Escenarios y flujo de caja libre del caso Base
esc = {}
for k, nombre in ((1, "low"), (2, "base"), (3, "high")):
    r = M.valorar(k)
    esc[nombre] = dict(valor=r["por_accion_hoy"], wacc=r["wacc"], peso_vt=r["peso_vt"])
    if k == 2:
        out["base_filas"] = [dict(year=f["año"], ventas=f["ventas"], ebit=f["ebit"], fcff=f["fcff"]) for f in r["filas"]]
out["escenarios"] = esc

# Monte Carlo (misma semilla que montecarlo.py: reproduce exactamente las 20.000 simulaciones)
d = MC.simular()
v = d["valor"].to_numpy()
rs = MC.resumir(d)
res = dict(zip(rs.metrica, rs.valor))
lo, hi, nb = 20.0, 90.0, 56
counts, edges = np.histogram(v, bins=nb, range=(lo, hi))
out["montecarlo"] = dict(
    n=int(res["simulaciones"]), mediana=res["mediana"], p5=res["p5"], p95=res["p95"],
    prob_supera=res["prob_supera_precio"], precio=res["precio_mercado"],
    bin_lo=lo, bin_hi=hi, counts=counts.tolist(),
    muestra=[round(float(x), 2) for x in v[:400]],
)

# Comparables
comp = pd.read_csv(ROOT / "data" / "processed" / "comparables_valor_implicito.csv")
out["comparables_nombres"] = comp.empresa.tolist()
out["comparables"] = [dict(nombre=r.empresa, per=float(r.per_forward), ev_ebitda=float(r.ev_ebitda)) for r in comp.itertuples()]
out["comparables_mediana"] = dict(per=float(comp.valor_per.median()), ev_ebitda=float(comp.valor_ev_ebitda.median()))

# Calidad contable
alt = pd.read_csv(ROOT / "data" / "processed" / "calidad_contable_altman.csv")
ben = pd.read_csv(ROOT / "data" / "processed" / "calidad_contable_beneish.csv")
out["altman"] = dict(min=float(alt.Z2.min()), max=float(alt.Z2.max()), serie=[round(float(x), 2) for x in alt.Z2])
out["beneish"] = dict(min=float(ben.M.min()), max=float(ben.M.max()), serie=[round(float(x), 2) for x in ben.M])

dest = ROOT / "video" / "src" / "data"
dest.mkdir(parents=True, exist_ok=True)
(dest / "modelData.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print("OK ->", dest / "modelData.json")
print(json.dumps({k: out[k] for k in ("escenarios", "comparables_mediana", "altman", "beneish")}, indent=1))
print({k: out["montecarlo"][k] for k in ("n", "mediana", "p5", "p95", "prob_supera")})
print([ (f["year"], round(f["fcff"])) for f in out["base_filas"]])
print([(h["year"], h["ventas"], h["ebit"]) for h in out["historico"]])
