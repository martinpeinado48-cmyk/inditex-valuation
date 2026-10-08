"""Normaliza statements_long.csv a una tabla ancha (una fila por ejercicio) y valida
identidades contables. Salida: data/processed/inditex_financials.csv

Ejercicio N = año fiscal que termina el 31 de enero de N+1 (convencion de Inditex).
Importes en millones de euros. Una partida ausente o '-' en el PDF se trata como 0.
"""
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "processed" / "statements_long.csv"
OUT = ROOT / "data" / "processed" / "inditex_financials.csv"

# (estado, seccion o None, regex sobre la etiqueta en minusculas) -> nombre canonico
ITEMS = {
    # Cuenta de resultados
    "ventas": ("pyg", None, r"^ventas$"),
    "coste_mercancia": ("pyg", None, r"^coste de la mercancía$"),
    "margen_bruto": ("pyg", None, r"^margen bruto$"),
    "gastos_explotacion": ("pyg", None, r"^gastos de explotación$"),
    "otras_pyg": ("pyg", None, r"^otras pérdidas y ganancias netas$"),
    "ebitda": ("pyg", None, r"^resultado operativo \(ebitda\)$"),
    # Solo aparece en 2022 (-231 M EUR, efecto excepcional de la salida de Rusia).
    "otros_resultados": ("pyg", None, r"^otros resultados$"),
    "amortizaciones": ("pyg", None, r"^amortizaciones y depreciaciones$"),
    "ebit": ("pyg", None, r"^resultados de explotación \(ebit\)$"),
    "resultados_financieros": ("pyg", None, r"^resultados financieros$"),
    "puesta_equivalencia": ("pyg", None, r"^resultados (?:por puesta en equivalencia|de inversiones contabilizadas)"),
    "bai": ("pyg", None, r"^resultados antes de impuestos"),
    "impuesto_beneficios": ("pyg", None, r"^impuesto sobre beneficios$"),
    "resultado_neto": ("pyg", None, r"^resultado neto del ejercicio$"),
    "bpa": ("pyg", None, r"^beneficio por acción"),
    # Balance
    "activo_no_corriente": ("balance", None, r"^activos no corrientes$"),
    "derecho_uso": ("balance", None, r"^derecho de uso$"),
    "intangibles": ("balance", None, r"^otros activos intangibles$"),
    "fondo_comercio": ("balance", None, r"^fondo de comercio$"),
    "inmovilizado_material": ("balance", None, r"^inmovilizado material$"),
    "activo_corriente": ("balance", None, r"^activos corrientes$"),
    "existencias": ("balance", None, r"^existencias$"),
    "deudores": ("balance", None, r"^deudores$"),
    "inv_financieras_temporales": ("balance", None, r"^inversiones financieras temporales$"),
    "efectivo": ("balance", None, r"^efectivo y equivalentes$"),
    "total_activo": ("balance", None, r"^total activo$"),
    "patrimonio_neto": ("balance", None, r"^patrimonio neto$"),
    "pasivo_no_corriente": ("balance", None, r"^pasivos no corrientes$"),
    "deuda_financiera_lp": ("balance", "PASIVOS NO CORRIENTES", r"^deuda financiera$"),
    "arrendamiento_lp": ("balance", None, r"^pasivo por arrendamiento a largo plazo$"),
    "pasivo_corriente": ("balance", None, r"^pasivos corrientes$"),
    "deuda_financiera_cp": ("balance", "PASIVOS CORRIENTES", r"^deuda financiera$"),
    "arrendamiento_cp": ("balance", None, r"^pasivo por arrendamiento a corto plazo$"),
    "acreedores": ("balance", None, r"^acreedores$"),
    "total_pasivo_patrimonio": ("balance", None, r"^total pasivo y patrimonio neto$"),
    # Flujos de efectivo
    "flujo_explotacion": ("flujos", None, r"^flujos derivados de las actividades de explotación$"),
    "gasto_fin_arrendamiento": ("flujos", None, r"^gasto financiero por arrendamiento$"),
    "capex_intangible": ("flujos", None, r"^pagos por inversiones en inmovilizado intangible$"),
    "capex_material": ("flujos", None, r"^pagos por inversiones en inmovilizado material$"),
    "flujo_inversion": ("flujos", None, r"^flujos derivados de actividades de inversión$"),
    "pago_arrendamientos": ("flujos", None, r"^pagos por arrendamiento renta fija$"),
    "dividendos": ("flujos", None, r"^dividendos$"),
    "flujo_financiacion": ("flujos", None, r"^flujos empleados en actividades de financiación$"),
    "efecto_tipo_cambio": ("flujos", None, r"^efectos de las variaciones en los tipos de cambio"),
}


def load() -> pd.DataFrame:
    df = pd.read_csv(SRC)
    df["fy"] = df["pdf"].str.extract(r"FY(\d{4})").astype(int)
    df.loc[df["col"] == "prior", "fy"] -= 1
    df["section"] = df["section"].fillna("")
    # Preferimos el dato 'current' del PDF de cada ejercicio; el comparativo solo cubre 2020.
    return df[(df["col"] == "current") | (df["fy"] == 2020)]


def build(df: pd.DataFrame) -> pd.DataFrame:
    out = {}
    for name, (stmt, section, pattern) in ITEMS.items():
        sub = df[df["statement"] == stmt]
        if section is not None:
            sub = sub[sub["section"] == section]
        sub = sub[sub["label"].str.lower().str.contains(pattern, regex=True)]
        out[name] = sub.drop_duplicates("fy").set_index("fy")["value"]
    wide = pd.DataFrame(out).sort_index()
    # Partidas que el PDF omite o muestra como '-' cuando son cero.
    for col in ("otros_resultados", "deuda_financiera_lp"):
        wide[col] = wide[col].fillna(0)
    return wide


def checks(w: pd.DataFrame) -> pd.DataFrame:
    z = w.fillna(0)
    res = pd.DataFrame(index=w.index)
    res["activo=pasivo+PN"] = z.total_activo - z.total_pasivo_patrimonio
    res["PN+PNC+PC=total"] = z.patrimonio_neto + z.pasivo_no_corriente + z.pasivo_corriente - z.total_pasivo_patrimonio
    res["ANC+AC=total"] = z.activo_no_corriente + z.activo_corriente - z.total_activo
    res["ventas-coste=margen"] = z.ventas + z.coste_mercancia - z.margen_bruto
    res["EBITDA-D&A=EBIT"] = z.ebitda + z.otros_resultados + z.amortizaciones - z.ebit
    res["EBIT+fin+pe=BAI"] = z.ebit + z.resultados_financieros + z.puesta_equivalencia - z.bai
    res["BAI+imp=neto"] = z.bai + z.impuesto_beneficios - z.resultado_neto
    # Variacion de caja = flujos operativos + inversion + financiacion + efecto tipo de cambio;
    # comparamos con la variacion del saldo de efectivo del balance.
    flujos = z.flujo_explotacion + z.flujo_inversion + z.flujo_financiacion + z.efecto_tipo_cambio
    res["Δcaja flujos vs balance"] = flujos - z.efectivo.diff().fillna(flujos)
    return res


def main():
    wide = build(load())
    wide.index.name = "ejercicio"
    wide.to_csv(OUT, encoding="utf-8")
    print(f"{wide.shape[0]} ejercicios x {wide.shape[1]} partidas -> {OUT}\n")
    missing = wide.isna().sum()
    print("Partidas con huecos (NaN):\n", missing[missing > 0].to_string() or "ninguna", "\n")
    print("Chequeos (deben ser ~0; tolerancia de redondeo +-3):")
    print(checks(wide).to_string())


if __name__ == "__main__":
    main()
