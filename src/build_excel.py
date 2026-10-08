"""Construye excel/Inditex_Valoracion.xlsx con fórmulas vivas (openpyxl).

Hojas: Resumen · Hipótesis · Histórico · DCF · Sensibilidad
Convenciones: azul = dato o hipótesis (se edita) · negro = fórmula · verde = enlace a otra hoja ·
              celda amarilla = hipótesis clave que el autor debe decidir.
La tabla de escenarios del Resumen es una foto estática (valores calculados con src/dcf_model.py).
"""
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L

import comparables as CP
import dcf_model as M

import sys

ROOT = Path(__file__).resolve().parents[1]
# Ruta de salida opcional como primer argumento (útil si el libro está abierto en Excel y bloqueado)
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "excel" / "Inditex_Valoracion.xlsx"

BLUE, BLACK, GREEN = "0000FF", "000000", "008000"
YELLOW = PatternFill("solid", fgColor="FFFF00")
HEADER_FILL = PatternFill("solid", fgColor="1F3864")
SECTION_FILL = PatternFill("solid", fgColor="D9E1F2")
THIN = Side(style="thin", color="999999")

F_M = '#,##0;(#,##0);"-"'
F_M1 = '#,##0.0;(#,##0.0);"-"'
F_PCT = '0.0%;(0.0%);"-"'
F_PCT2 = '0.00%;(0.00%);"-"'
F_X = '0.0"x"'
F_EUR = '#,##0.00 "€";(#,##0.00 "€");"-"'
F_DATE = "dd/mm/yyyy"
F_NUM2 = "0.00"

ws_names = dict(res="Resumen", hip="Hipótesis", his="Histórico", dcf="DCF", sen="Sensibilidad", comp="Comparables")
Q = {k: f"'{v}'" for k, v in ws_names.items()}   # nombres entre comillas para las fórmulas
COLS = [L(c) for c in range(4, 14)]               # D..M = 2026E..2035E


def font(color=BLACK, bold=False, italic=False, size=10):
    return Font(name="Arial", size=size, bold=bold, italic=italic, color=color)


def put(ws, ref, value, kind="calc", fmt=None, bold=False, fill=None, align=None, italic=False):
    c = ws[ref]
    c.value = value
    color = {"input": BLUE, "calc": BLACK, "link": GREEN, "label": BLACK, "note": "595959"}[kind]
    c.font = font(color, bold=bold, italic=italic or kind == "note")
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    if align:
        c.alignment = Alignment(horizontal=align, vertical="center", wrap_text=False)
    return c


def titulo(ws, texto, sub=None):
    put(ws, "A1", texto, "label", bold=True)
    ws["A1"].font = font(BLACK, bold=True, size=14)
    if sub:
        put(ws, "A2", sub, "note")


def seccion(ws, fila, texto, hasta=14):
    for col in range(1, hasta + 1):
        ws.cell(row=fila, column=col).fill = SECTION_FILL
    put(ws, f"A{fila}", texto, "label", bold=True, fill=SECTION_FILL)


def cabecera_años(ws, fila, primero="2025A", col_primero="C"):
    put(ws, f"{col_primero}{fila}", primero, "label", bold=True, align="right")
    for i, col in enumerate(COLS):
        put(ws, f"{col}{fila}", f"{M.YEARS[i]}E", "label", bold=True, align="right")
    for col in range(1, 14):
        c = ws.cell(row=fila, column=col)
        c.border = Border(bottom=THIN)


# =============================================================================================
def hoja_historico(wb):
    ws = wb.create_sheet(ws_names["his"])
    titulo(ws, "Histórico de Inditex (2020-2025)",
           "Fuente: cuentas anuales consolidadas de Inditex (inditex.com), extraídas con src/extract_statements.py. "
           "M€. El ejercicio N termina el 31/01/N+1.")
    w = pd.read_csv(ROOT / "data" / "processed" / "inditex_financials.csv", index_col=0)
    años = [2020, 2021, 2022, 2023, 2024, 2025]
    hc = [L(3 + i) for i in range(6)]  # C..H
    for c, a in zip(hc, años):
        put(ws, f"{c}4", str(a), "label", bold=True, align="right")
    for col in range(1, 9):
        ws.cell(row=4, column=col).border = Border(bottom=THIN)

    filas = [  # fila, etiqueta, columna del CSV, signo
        (5, "Ventas", "ventas"), (6, "Coste de la mercancía", "coste_mercancia"),
        (7, "Margen bruto", "margen_bruto"), (8, "EBITDA", "ebitda"),
        (9, "Amortizaciones y depreciaciones", "amortizaciones"), (10, "EBIT", "ebit"),
        (11, "Resultado antes de impuestos (BAI)", "bai"), (12, "Impuesto sobre beneficios", "impuesto_beneficios"),
        (13, "Resultado neto", "resultado_neto"),
        (15, "Existencias", "existencias"), (16, "Deudores", "deudores"), (17, "Acreedores", "acreedores"),
        (19, "Efectivo y equivalentes", "efectivo"), (20, "Inversiones financieras temporales", "inv_financieras_temporales"),
        (22, "Pasivo por arrendamiento a largo plazo", "arrendamiento_lp"),
        (23, "Pasivo por arrendamiento a corto plazo", "arrendamiento_cp"),
        (24, "Patrimonio neto", "patrimonio_neto"), (25, "Total activo", "total_activo"),
        (27, "Flujo de explotación (CFO)", "flujo_explotacion"),
        (28, "Capex en inmovilizado material", "capex_material"),
        (29, "Capex en inmovilizado intangible", "capex_intangible"),
        (30, "Pagos por arrendamiento (renta fija)", "pago_arrendamientos"),
        (31, "Gasto financiero por arrendamiento", "gasto_fin_arrendamiento"),
        (32, "Dividendos pagados", "dividendos"),
    ]
    for fila, etiqueta, col in filas:
        put(ws, f"A{fila}", etiqueta, "label")
        for c, a in zip(hc, años):
            put(ws, f"{c}{fila}", float(w.loc[a, col]), "input", F_M)
    # deuda financiera = lp + cp (valor)
    put(ws, "A21", "Deuda financiera (corriente + no corriente)", "label")
    for c, a in zip(hc, años):
        put(ws, f"{c}21", float(w.loc[a, "deuda_financiera_lp"] + w.loc[a, "deuda_financiera_cp"]), "input", F_M)
    put(ws, "A18", "Circulante operativo (existencias + deudores − acreedores)", "label", bold=True)
    for c in hc:
        put(ws, f"{c}18", f"={c}15+{c}16-{c}17", "calc", F_M, bold=True)
    put(ws, "A14", "Balance (cierre de ejercicio)", "label", bold=True)
    put(ws, "A26", "Flujos de caja", "label", bold=True)

    seccion(ws, 34, "Ratios (fórmulas)", hasta=8)
    ratios = [
        (35, "Crecimiento de ventas", lambda c, p: f"={c}5/{p}5-1" if p else None, F_PCT),
        (36, "Margen bruto", lambda c, p: f"={c}7/{c}5", F_PCT),
        (37, "Margen EBITDA", lambda c, p: f"={c}8/{c}5", F_PCT),
        (38, "Margen EBIT", lambda c, p: f"={c}10/{c}5", F_PCT),
        (39, "Margen neto", lambda c, p: f"={c}13/{c}5", F_PCT),
        (40, "Tipo impositivo efectivo", lambda c, p: f"=-{c}12/{c}11", F_PCT),
        (41, "Amortizaciones / ventas", lambda c, p: f"=-{c}9/{c}5", F_PCT),
        (42, "Pagos por arrendamiento / ventas", lambda c, p: f"=-{c}30/{c}5", F_PCT),
        (43, "Interés de arrendamientos / ventas", lambda c, p: f"={c}31/{c}5", F_PCT2),
        (44, "Circulante operativo / ventas", lambda c, p: f"={c}18/{c}5", F_PCT),
        (45, "Capex / ventas", lambda c, p: f"=-({c}28+{c}29)/{c}5", F_PCT),
        (46, "FCF tras arrendamientos (CFO − capex − arrendamientos)", lambda c, p: f"={c}27+{c}28+{c}29+{c}30", F_M),
        (47, "Posición financiera neta (caja + inversiones − deuda)", lambda c, p: f"={c}19+{c}20-{c}21", F_M),
    ]
    for fila, etiqueta, fn, fmt in ratios:
        put(ws, f"A{fila}", etiqueta, "label")
        for i, c in enumerate(hc):
            f = fn(c, hc[i - 1] if i else None)
            if f:
                put(ws, f"{c}{fila}", f, "calc", fmt)
    ws.column_dimensions["A"].width = 58
    ws.column_dimensions["B"].width = 3
    for c in hc:
        ws.column_dimensions[c].width = 12
    ws.freeze_panes = "C5"
    return ws


def hoja_hipotesis(wb):
    ws = wb.create_sheet(ws_names["hip"])
    m, op = M.MERCADO, M.OPERATIVOS
    titulo(ws, "Hipótesis del modelo",
           "Azul = dato/hipótesis que puedes editar · Amarillo = decisión clave · Negro = fórmula · Verde = enlace a otra hoja. M€ salvo indicación.")

    seccion(ws, 4, "1. Fechas y mercado")
    filas = [
        (5, "Fecha de valoración (precio de mercado)", m["fecha_valoracion"], "input", F_DATE, "Fecha de la cotización usada"),
        (6, "Fecha del balance de partida", m["fecha_balance"], "input", F_DATE, "Último balance publicado: 1S2026 (31/07/2026)"),
        (7, "Meses del ejercicio 2026 que quedan tras el balance", m["meses_restantes_2026"], "input", "0",
         "El ejercicio 2026 acaba el 31/01/2027"),
        (8, "Fracción del año 2026E que se valora", "=B7/12", "calc", F_NUM2,
         "Simplificación: se valora la mitad del flujo anual de 2026E (ignora la estacionalidad)"),
        (9, "Precio de la acción (€)", m["precio"], "input", F_EUR, "es.investing.com, 07/10/2026. Cotiza con derecho a dividendo hasta el 29/10/2026"),
        (10, "Número de acciones (millones)", m["acciones"], "input", "#,##0.0", "Resultados 1S2026 de Inditex"),
        (11, "Capitalización bursátil (M€)", "=B9*B10", "calc", F_M, None),
        (12, "Días entre el balance y la fecha de valoración", "=B5-B6", "calc", "0", None),
    ]
    for fila, et, val, kind, fmt, nota in filas:
        put(ws, f"A{fila}", et, "label")
        put(ws, f"B{fila}", val, kind, fmt)
        if nota:
            put(ws, f"D{fila}", nota, "note")

    seccion(ws, 14, "2. Tasa de descuento y crecimiento a perpetuidad")
    filas = [
        (15, "Tipo libre de riesgo (rf)", m["rf"], "input", F_PCT2, "DECISIÓN DE MARTÍN (07/10/2026): bono alemán a 10 años, cierre 30/09/2026 (datosmacro). El bono español está en 4,11 %", True),
        (16, "Beta", m["beta"], "input", F_NUM2, "DECISIÓN DE MARTÍN. Regresión propia semanal a 5 años: 0,95-1,08 según índice (src/beta.py). Investing.com 0,90; sector (Damodaran) 0,79", True),
        (17, "Prima de riesgo de mercado (ERP)", m["erp"], "input", F_PCT2, "DECISIÓN DE MARTÍN. Mercado maduro 4,17 % (Damodaran, jul-2026) + riesgo-país ponderado por ventas de Inditex (estimación propia). España: 5,78 %", True),
        (18, "Coste de los recursos propios (Ke = rf + beta × ERP)", "=B15+B16*B17", "calc", F_PCT2, "CAPM", False),
        (19, "Coste de la deuda antes de impuestos", m["kd"], "input", F_PCT2, "Irrelevante con peso de deuda 0 %", False),
        (20, "Peso de la deuda D/(D+E)", m["peso_deuda"], "input", F_PCT, "Inditex no tiene deuda financiera relevante (caja neta)", False),
        (21, "Tipo impositivo", m["tipo_impositivo"], "input", F_PCT, "Efectivo 2021-25 ≈ 22 %; 1S2026: 22,5 %", False),
        (22, "WACC", "=B18*(1-B20)+B19*(1-B21)*B20", "calc", F_PCT2, "Los arrendamientos se tratan como coste operativo, no como deuda", False),
        (23, "Crecimiento a perpetuidad (g)", m["g_terminal"], "input", F_PCT2, "DECISIÓN DE MARTÍN. Entre la inflación objetivo del BCE (2 %) y el crecimiento nominal esperado; menor que rf", True),
    ]
    for fila, et, val, kind, fmt, nota, clave in filas:
        put(ws, f"A{fila}", et, "label", bold=(fila in (18, 22)))
        put(ws, f"B{fila}", val, kind, fmt, bold=(fila in (18, 22)), fill=YELLOW if clave else None)
        put(ws, f"D{fila}", nota, "note")

    seccion(ws, 25, "3. Balance de partida (31/07/2026)")
    filas = [
        (26, "Efectivo y equivalentes", m["efectivo"], "input", F_M, "Resultados 1S2026"),
        (27, "Inversiones financieras temporales", m["inv_temporales"], "input", F_M, "Resultados 1S2026"),
        (28, "Deuda financiera", m["deuda_financiera"], "input", F_M, "Resultados 1S2026 (solo corriente)"),
        (29, "Posición financiera neta", "=B26+B27-B28", "calc", F_M, "Coincide con los 10.398 M€ que publica Inditex"),
        (30, "Otros activos no operativos", m["otros_activos"], "input", F_M, "0 por prudencia: no se suman las inversiones por puesta en equivalencia (≈500 M€)"),
        (31, "Intereses minoritarios", m["minoritarios"], "input", F_M, "Inditex no tiene minoritarios relevantes"),
        (32, "Pasivos por arrendamiento (informativo, no se resta)", 6197.0, "input", F_M,
         "4.549 + 1.648. No se restan porque el alquiler ya está dentro del flujo de caja (FCFF)"),
    ]
    for fila, et, val, kind, fmt, nota in filas:
        put(ws, f"A{fila}", et, "label", bold=(fila == 29))
        put(ws, f"B{fila}", val, kind, fmt, bold=(fila == 29))
        put(ws, f"D{fila}", nota, "note")

    seccion(ws, 34, "4. Parámetros operativos (iguales en todos los escenarios)")
    put(ws, "C34", "2025A", "label", bold=True, align="right", fill=SECTION_FILL)
    his = Q["his"]
    filas = [
        (35, "Amortizaciones / ventas", op["da_pct"], f"={his}!H41", "Se mantiene el nivel de 2025"),
        (36, "Pagos por arrendamiento / ventas", op["arrend_pct"], f"={his}!H42", "Se mantiene el nivel de 2025"),
        (37, "Interés de arrendamientos / ventas", op["arrend_int_pct"], f"={his}!H43", "Solo se usa para calcular el impuesto"),
        (38, "Circulante operativo / ventas", op["nwc_pct"], f"={his}!H44", "Media 2020-25 ≈ −8,6 %; al ser negativo, crecer libera caja"),
    ]
    for fila, et, val, ref, nota in filas:
        put(ws, f"A{fila}", et, "label")
        put(ws, f"B{fila}", val, "input", F_PCT2 if fila == 37 else F_PCT)
        put(ws, f"C{fila}", ref, "link", F_PCT2 if fila == 37 else F_PCT)
        put(ws, f"D{fila}", nota, "note")

    seccion(ws, 40, "5. Escenarios (cambia el selector)")
    put(ws, "A41", "Escenario activo (1 = Bajo, 2 = Base, 3 = Alto)", "label", bold=True)
    put(ws, "B41", 2, "input", "0", bold=True, fill=YELLOW, align="center")
    put(ws, "C41", '=CHOOSE(B41,"Bajo","Base","Alto")', "calc", bold=True)
    put(ws, "D41", "Las tres filas de cada bloque son hipótesis tuyas; la fila «Activo» es la que usa el modelo", "note")

    bloques = [
        (43, "Crecimiento de ventas", "crecimiento", F_PCT, "Bajo: la mitad del ritmo actual · Base: 7,5 % en 2026E (1S2026: +7,6 % reportado) con convergencia lineal al 3 % · Alto: mantiene ≈9 % (ritmo a tipo constante)"),
        (49, "Margen EBIT", "margen_ebit", F_PCT, "Base: se mantiene en 20 % (2025: 20,1 %; 1S2026: 19,5 %) · Bajo: cae a 18 % · Alto: sube a 22 %"),
        (55, "Capex / ventas", "capex_pct", F_PCT, "2026E: guía de Inditex ≈2.300 M€ ordinarios + 200 M€ extraordinarios ≈ 5,8 % · después se normaliza a 4,5-5,5 % según escenario"),
    ]
    for fila, nombre, clave, fmt, nota in bloques:
        put(ws, f"A{fila}", nombre, "label", bold=True)
        cabecera_años(ws, fila, "")
        for k in (1, 2, 3):
            r = fila + k
            put(ws, f"A{r}", f"   {M.ESCENARIOS[k]['nombre']}", "label")
            for i, col in enumerate(COLS):
                put(ws, f"{col}{r}", M.ESCENARIOS[k][clave][i], "input", fmt)
        r = fila + 4
        put(ws, f"A{r}", "   Activo", "label", bold=True)
        for col in COLS:
            put(ws, f"{col}{r}", f"=CHOOSE($B$41,{col}{fila+1},{col}{fila+2},{col}{fila+3})", "calc", fmt, bold=True)
        put(ws, f"N{fila}", nota, "note")
    ws.column_dimensions["A"].width = 56
    ws.column_dimensions["B"].width = 12
    ws.column_dimensions["C"].width = 10
    for col in COLS:
        ws.column_dimensions[col].width = 10
    ws.freeze_panes = "B4"
    return ws


def hoja_dcf(wb):
    ws = wb.create_sheet(ws_names["dcf"])
    hip, his = Q["hip"], Q["his"]
    titulo(ws, "DCF · flujo de caja libre de la empresa (FCFF)")
    # ROUND en vez de TEXT: los códigos de formato de TEXT dependen del idioma de Excel
    put(ws, "A2", f'="Escenario: "&{hip}!C41&"  ·  WACC "&ROUND({hip}!B22*100,2)&" %  ·  g "&ROUND({hip}!B23*100,2)&" %"', "note")
    put(ws, "A4", "M€", "label", bold=True)
    cabecera_años(ws, 4)

    def fila(r, et, c_formula, d_formula, fmt=F_M, kind_c="link", kind_d="calc", bold=False):
        put(ws, f"A{r}", et, "label", bold=bold)
        if c_formula:
            put(ws, f"C{r}", c_formula, kind_c, fmt, bold=bold)
        for i, col in enumerate(COLS):
            prev = L(3 + i)
            put(ws, f"{col}{r}", d_formula(col, prev, i), kind_d, fmt, bold=bold)

    fila(5, "Ventas", f"={his}!H5", lambda c, p, i: f"={p}5*(1+{c}6)", bold=True)
    fila(6, "   Crecimiento", f"={his}!H35", lambda c, p, i: f"={hip}!{c}47", F_PCT, kind_d="link")
    fila(7, "   Margen EBIT", f"={his}!H38", lambda c, p, i: f"={hip}!{c}53", F_PCT, kind_d="link")
    fila(8, "EBIT", f"={his}!H10", lambda c, p, i: f"={c}5*{c}7")
    fila(9, "Amortizaciones", f"=-{his}!H9", lambda c, p, i: f"={c}5*{hip}!$B$35")
    fila(10, "EBITDA", f"={his}!H8", lambda c, p, i: f"={c}8+{c}9", bold=True)
    fila(11, "(−) Pagos por arrendamiento", f"={his}!H30", lambda c, p, i: f"=-{c}5*{hip}!$B$36")
    fila(12, "   Memo: interés de arrendamientos", f"={his}!H31", lambda c, p, i: f"={c}5*{hip}!$B$37")
    fila(13, "(−) Impuestos sobre EBIT − interés de arrend.", None, lambda c, p, i: f"=-{hip}!$B$21*MAX({c}8-{c}12,0)")
    fila(14, "(−) Capex", f"={his}!H28+{his}!H29", lambda c, p, i: f"=-{c}5*{hip}!{c}59")
    fila(15, "   Memo: saldo de circulante operativo", f"={his}!H18", lambda c, p, i: f"={c}5*{hip}!$B$38")
    fila(16, "(−) Aumento / (+) disminución del circulante", None, lambda c, p, i: f"={p}15-{c}15")
    fila(17, "FCFF (flujo de caja libre de la empresa)", None, lambda c, p, i: f"={c}10+{c}11+{c}13+{c}14+{c}16", bold=True)
    put(ws, "A18", "   Memo: FCF 2025A tras arrendamientos (reportado, no comparable 1:1)", "note")
    put(ws, "C18", f"={his}!H46", "link", F_M)

    put(ws, "A20", "Fracción del año que se valora", "label")
    put(ws, "A21", "FCFF a valorar", "label")
    put(ws, "A22", "Tiempo de descuento (años desde 31/07/2026, mitad de periodo)", "label")
    put(ws, "A23", "Factor de descuento", "label")
    put(ws, "A24", "Valor actual del FCFF", "label", bold=True)
    for i, col in enumerate(COLS):
        put(ws, f"{col}20", f"={hip}!B8" if i == 0 else 1, "link" if i == 0 else "input", F_NUM2)
        put(ws, f"{col}21", f"={col}17*{col}20", "calc", F_M)
        if i == 0:
            put(ws, f"{col}22", f"={hip}!B8/2", "calc", F_NUM2)
        elif i == 1:
            put(ws, f"{col}22", f"={hip}!B8+0.5", "calc", F_NUM2)
        else:
            put(ws, f"{col}22", f"={L(3 + i)}22+1", "calc", F_NUM2)
        put(ws, f"{col}23", f"=1/(1+{hip}!$B$22)^{col}22", "calc", "0.0000")
        put(ws, f"{col}24", f"={col}21*{col}23", "calc", F_M, bold=True)

    seccion(ws, 26, "Valoración", hasta=13)
    val = [
        (27, "Suma del valor actual de los FCFF (2026E-2035E)", "=SUM(D24:M24)", F_M, False),
        (28, "FCFF del último año explícito (2035E)", "=M17", F_M, False),
        (29, "Valor terminal (Gordon: FCFF × (1+g) / (WACC − g))", f"=C28*(1+{hip}!B23)/({hip}!B22-{hip}!B23)", F_M, False),
        (30, "Factor de descuento del valor terminal", "=M23", "0.0000", False),
        (31, "Valor actual del valor terminal", "=C29*C30", F_M, False),
        (32, "Valor de la empresa (EV)", "=C27+C31", F_M, True),
        (33, "(+) Posición financiera neta", f"={hip}!B29", F_M, False),
        (34, "(+) Otros activos no operativos", f"={hip}!B30", F_M, False),
        (35, "(−) Intereses minoritarios", f"=-{hip}!B31", F_M, False),
        (36, "Valor del capital (equity) a 31/07/2026", "=SUM(C32:C35)", F_M, True),
        (37, "Acciones (millones)", f"={hip}!B10", "#,##0.0", False),
        (38, "Valor por acción a 31/07/2026", "=C36/C37", F_EUR, False),
        (39, "Factor para actualizar hasta la fecha de valoración", f"=(1+{hip}!B22)^({hip}!B12/365)", "0.0000", False),
        (40, "VALOR POR ACCIÓN HOY", "=C38*C39", F_EUR, True),
        (41, "Precio de mercado", f"={hip}!B9", F_EUR, False),
        (42, "Potencial frente al precio de mercado", "=C40/C41-1", F_PCT, True),
    ]
    for r, et, f, fmt, bold in val:
        put(ws, f"A{r}", et, "label", bold=bold)
        kind = "link" if f.startswith(f"={hip}!") and f.count("!") == 1 and not any(ch in f[1:] for ch in "+-*/(") else "calc"
        put(ws, f"C{r}", f, kind, fmt, bold=bold)
    ws["C40"].fill = YELLOW

    seccion(ws, 44, "Controles de sensatez", hasta=13)
    ctr = [
        (45, "Valor terminal / valor de la empresa", "=C31/C32", F_PCT),
        (46, "EV / EBITDA tras arrendamientos 2026E (implícito)", "=C32/(D10+D11)", F_X),
        (47, "Valor terminal / EBITDA tras arrendamientos 2035E (múltiplo de salida implícito)", "=C29/(M10+M11)", F_X),
        (48, "EV de mercado / EBITDA tras arrendamientos 2026E", f"=({hip}!B11-{hip}!B29-{hip}!B30+{hip}!B31)/(D10+D11)", F_X),
    ]
    for r, et, f, fmt in ctr:
        put(ws, f"A{r}", et, "label")
        put(ws, f"C{r}", f, "calc", fmt)
    put(ws, "A49", "g menor que rf", "label")
    put(ws, "C49", f'=IF({hip}!B23<{hip}!B15,"OK","REVISAR")', "calc", align="right")
    put(ws, "A50", "WACC mayor que g", "label")
    put(ws, "C50", f'=IF({hip}!B22>{hip}!B23,"OK","REVISAR")', "calc", align="right")

    ws.column_dimensions["A"].width = 66
    ws.column_dimensions["B"].width = 2
    for c in ["C"] + COLS:
        ws.column_dimensions[c].width = 11
    ws.freeze_panes = "C5"

    ch = BarChart()
    ch.type = "col"
    ch.title = "FCFF proyectado (M€)"
    ch.y_axis.title = None
    ch.add_data(Reference(ws, min_col=4, max_col=13, min_row=17), from_rows=True, titles_from_data=False)
    ch.set_categories(Reference(ws, min_col=4, max_col=13, min_row=4))
    ch.legend = None
    ch.height, ch.width = 7.5, 18
    ch.series[0].graphicalProperties.solidFill = "2A78D6"
    ch.y_axis.delete = False
    ch.x_axis.delete = False
    ws.add_chart(ch, "F26")
    return ws


def hoja_sensibilidad(wb):
    ws = wb.create_sheet(ws_names["sen"])
    hip, dcf = Q["hip"], Q["dcf"]
    titulo(ws, "Sensibilidad del valor por acción",
           "Cada celda recalcula la valoración con otro WACC y otro g, manteniendo el escenario activo. Verde = por encima del precio de mercado; rojo = por debajo.")
    put(ws, "A4", "Paso del WACC", "label")
    put(ws, "B4", 0.005, "input", F_PCT2)
    put(ws, "A5", "Paso de g", "label")
    put(ws, "B5", 0.005, "input", F_PCT2)

    def tabla(fila0, titulo_t, como_upside):
        put(ws, f"A{fila0}", titulo_t, "label", bold=True)
        put(ws, f"A{fila0+1}", "WACC ↓  ·  g →", "note")
        for j in range(5):
            put(ws, f"{L(2 + j)}{fila0+1}", f"={hip}!$B$23+({j}-2)*$B$5", "calc", F_PCT2, bold=True, align="right")
        for i in range(7):
            r = fila0 + 2 + i
            put(ws, f"A{r}", f"={hip}!$B$22+({i}-3)*$B$4", "calc", F_PCT2, bold=True, align="right")
            for j in range(5):
                col = L(2 + j)
                w_, g_ = f"$A{r}", f"{col}${fila0+1}"
                core = (f"((SUMPRODUCT({dcf}!$D$21:$M$21,(1+{w_})^(-{dcf}!$D$22:$M$22))"
                        f"+{dcf}!$M$17*(1+{g_})/({w_}-{g_})*(1+{w_})^(-{dcf}!$M$22)"
                        f"+{hip}!$B$29+{hip}!$B$30-{hip}!$B$31)/{hip}!$B$10*(1+{w_})^({hip}!$B$12/365))")
                if como_upside:
                    put(ws, f"{col}{r}", f"={core}/{hip}!$B$9-1", "calc", F_PCT)
                else:
                    put(ws, f"{col}{r}", f"={core}", "calc", F_EUR)
        rng = f"B{fila0+2}:F{fila0+8}"
        if como_upside:
            ws.conditional_formatting.add(rng, CellIsRule(operator="greaterThanOrEqual", formula=["0"], fill=PatternFill("solid", bgColor="C6EFCE")))
            ws.conditional_formatting.add(rng, CellIsRule(operator="lessThan", formula=["0"], fill=PatternFill("solid", bgColor="FFC7CE")))
        else:
            ws.conditional_formatting.add(rng, CellIsRule(operator="greaterThanOrEqual", formula=[f"{hip}!$B$9"], fill=PatternFill("solid", bgColor="C6EFCE")))
            ws.conditional_formatting.add(rng, CellIsRule(operator="lessThan", formula=[f"{hip}!$B$9"], fill=PatternFill("solid", bgColor="FFC7CE")))

    tabla(7, "Valor por acción hoy (€)", False)
    tabla(18, "Potencial frente al precio de mercado", True)
    put(ws, "A29", "Control: la celda central de la primera tabla debe coincidir con el valor del DCF", "note")
    put(ws, "A30", "Diferencia (debe ser 0)", "label")
    put(ws, "B30", f"=ROUND(D12-{dcf}!C40,6)", "calc", "0.000000")
    ws.column_dimensions["A"].width = 24
    for j in range(5):
        ws.column_dimensions[L(2 + j)].width = 12
    return ws


def hoja_comparables(wb):
    ws = wb.create_sheet(ws_names["comp"])
    hip, res = Q["hip"], Q["res"]
    titulo(ws, "Valoración por comparables",
           "¿Qué valdría Inditex si el mercado la valorase como a H&M, Fast Retailing o Next? Datos de una sola fuente (Yahoo Finance) y la misma fecha.")
    c = pd.read_csv(ROOT / "data" / "market" / "comparables_2026-10-07.csv")

    seccion(ws, 4, "1. Múltiplos de mercado (Yahoo Finance, 07/10/2026)", hasta=8)
    cab = ["Empresa", "P/E trailing", "P/E forward", "EV/EBITDA", "Margen operativo (%)", "ROE (%)", "Crec. ventas trim. (%)", "Beta Yahoo 5a"]
    for j, h in enumerate(cab):
        put(ws, f"{L(1 + j)}5", h, "label", bold=True, align="right" if j else None)
        ws.cell(row=5, column=1 + j).border = Border(bottom=THIN)
    campos = ["per_trailing", "per_forward", "ev_ebitda", "margen_operativo_pct", "roe_pct", "crec_ventas_trim_yoy_pct", "beta_5a_mensual"]
    for i, (_, f) in enumerate(c.iterrows()):
        r = 6 + i
        put(ws, f"A{r}", f.empresa, "label", bold=(i == 0))
        for j, campo in enumerate(campos):
            fmt = F_X if campo in ("per_trailing", "per_forward", "ev_ebitda") else "0.0" if campo != "beta_5a_mensual" else F_NUM2
            put(ws, f"{L(2 + j)}{r}", float(f[campo]), "input", fmt)
    for r, et, fn in ((10, "Mediana de los comparables", "MEDIAN"), (11, "Media de los comparables", "AVERAGE")):
        put(ws, f"A{r}", et, "label", bold=True)
        for j in range(3):
            col = L(2 + j)
            put(ws, f"{col}{r}", f"={fn}({col}7:{col}9)", "calc", F_X, bold=True)
        for j in range(3, 7):
            col = L(2 + j)
            put(ws, f"{col}{r}", f"={fn}({col}7:{col}9)", "calc", "0.0")
    put(ws, "A12", "Inditex frente a la mediana (prima + / descuento −)", "label")
    for j in range(3):
        col = L(2 + j)
        put(ws, f"{col}12", f"={col}6/{col}10-1", "calc", F_PCT)

    seccion(ws, 14, "2. Datos de Inditex para aplicar los múltiplos", hasta=8)
    datos = [
        (15, "EBITDA de los últimos 12 meses (M€)", CP.EBITDA_TTM, "input", F_M, "Ejercicio 2025 (11.267) − 1S2025 (5.114) + 1S2026 (5.513). Resultados oficiales de Inditex"),
        (16, "BPA forward de Inditex (€)", "=B20/C6", "calc", F_NUM2, "Precio ÷ P/E forward de Yahoo: el beneficio por acción que está implícito en ese múltiplo"),
        (17, "Pasivos por arrendamiento (M€)", f"={hip}!B32", "link", F_M, "Se restan porque el EV de Yahoo incluye los alquileres como deuda"),
        (18, "Posición financiera neta (M€)", f"={hip}!B29", "link", F_M, "Caja + inversiones temporales − deuda financiera (31/07/2026)"),
        (19, "Acciones (millones)", f"={hip}!B10", "link", "#,##0.0", None),
        (20, "Precio de mercado (€)", f"={hip}!B9", "link", F_EUR, None),
    ]
    for r, et, v, kind, fmt, nota in datos:
        put(ws, f"A{r}", et, "label")
        put(ws, f"B{r}", v, kind, fmt)
        if nota:
            put(ws, f"D{r}", nota, "note")

    seccion(ws, 22, "3. Valor por acción de Inditex si se valorase como cada comparable (€)", hasta=8)
    put(ws, "B23", "Por P/E forward", "label", bold=True, align="right")
    put(ws, "C23", "Por EV/EBITDA", "label", bold=True, align="right")
    for k in range(3):
        r, rm = 24 + k, 7 + k
        put(ws, f"A{r}", f"=A{rm}", "calc")
        put(ws, f"B{r}", f"=C{rm}*$B$16", "calc", F_EUR)
        put(ws, f"C{r}", f"=(D{rm}*$B$15-$B$17+$B$18)/$B$19", "calc", F_EUR)
    for r, et, fn in ((27, "Mínimo", "MIN"), (28, "Mediana", "MEDIAN"), (29, "Media", "AVERAGE"), (30, "Máximo", "MAX")):
        put(ws, f"A{r}", et, "label", bold=(r == 28))
        for col in "BC":
            put(ws, f"{col}{r}", f"={fn}({col}24:{col}26)", "calc", F_EUR, bold=(r == 28))
    put(ws, "A31", "Media sin Fast Retailing (crecimiento ≈22 %)", "label")
    for col in "BC":
        put(ws, f"{col}31", f"=AVERAGE({col}24,{col}26)", "calc", F_EUR)
    put(ws, "A32", "Control: el múltiplo propio de Inditex aplicado a Inditex", "label")
    put(ws, "B32", "=C6*$B$16", "calc", F_EUR)
    put(ws, "C32", "=(D6*$B$15-$B$17+$B$18)/$B$19", "calc", F_EUR)
    put(ws, "A33", "   Diferencia frente al precio de mercado", "label")
    put(ws, "B33", "=B32/$B$20-1", "calc", F_PCT)
    put(ws, "C33", "=C32/$B$20-1", "calc", F_PCT)
    put(ws, "D33", "La diferencia en EV/EBITDA viene de cómo Yahoo define el EBITDA de Inditex (≈11.900 M€ frente a los 11.666 M€ de aquí)", "note")

    seccion(ws, 35, "4. Campo de fútbol: rangos de valor por acción (€)", hasta=8)
    for j, h in enumerate(["Método", "Mínimo", "Máximo", "Amplitud", "Valor central"]):
        put(ws, f"{L(1 + j)}36", h, "label", bold=True, align="right" if j else None)
        ws.cell(row=36, column=1 + j).border = Border(bottom=THIN)
    filas = [
        (37, "DCF (escenarios Bajo - Alto)", f"={res}!C17", f"={res}!C19", f"={res}!C18", "link"),
        (38, "Comparables: P/E forward", "=B27", "=B30", "=B28", "calc"),
        (39, "Comparables: EV/EBITDA", "=C27", "=C30", "=C28", "calc"),
        (40, "Precio objetivo de analistas", CP.OBJETIVO_ANALISTAS[0], CP.OBJETIVO_ANALISTAS[1], CP.OBJETIVO_ANALISTAS[2], "input"),
        (41, "Rango de cotización 52 semanas", CP.RANGO_52S[0], CP.RANGO_52S[1], None, "input"),
    ]
    for r, et, lo, hi, cen, kind in filas:
        put(ws, f"A{r}", et, "label")
        put(ws, f"B{r}", lo, kind, F_EUR)
        put(ws, f"C{r}", hi, kind, F_EUR)
        put(ws, f"D{r}", f"=C{r}-B{r}", "calc", F_EUR)
        if cen is not None:
            put(ws, f"E{r}", cen, kind, F_EUR)
    put(ws, "A42", "Precio de mercado", "label", bold=True)
    put(ws, "B42", "=B20", "calc", F_EUR, bold=True)
    put(ws, "D42", "Analistas: 24 analistas, Bolsamanía 31/08/2026. 52 semanas: Yahoo Finance 07/10/2026. DCF: foto estática de la hoja Resumen.", "note")

    ch = BarChart()
    ch.type = "bar"
    ch.grouping = "stacked"
    ch.overlap = 100
    ch.title = "Rangos de valor por acción (€)"
    ch.add_data(Reference(ws, min_col=2, min_row=36, max_row=41), titles_from_data=True)
    ch.add_data(Reference(ws, min_col=4, min_row=36, max_row=41), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=1, min_row=37, max_row=41))
    ch.series[0].graphicalProperties.noFill = True
    ch.series[0].graphicalProperties.line.noFill = True
    ch.series[1].graphicalProperties.solidFill = "2A78D6"
    ch.legend = None
    ch.height, ch.width = 8.5, 18
    ch.y_axis.scaling.min = 20
    ch.y_axis.scaling.max = 90
    ch.x_axis.scaling.orientation = "maxMin"
    ch.title.overlay = False
    ch.y_axis.delete = False
    ch.x_axis.delete = False
    ws.add_chart(ch, "A45")
    ws.column_dimensions["A"].width = 54
    for col in "BCDH":
        ws.column_dimensions[col].width = 16
    for col in "EFG":
        ws.column_dimensions[col].width = 24   # títulos largos: margen operativo, crecimiento de ventas
    return ws


def hoja_resumen(wb, resultados):
    ws = wb.create_sheet(ws_names["res"], 0)
    hip, dcf = Q["hip"], Q["dcf"]
    titulo(ws, "Inditex · Valoración por descuento de flujos (DCF)",
           "Proyecto de finanzas de Martín Peinado Miraflores · Modelo con hipótesis propias, uso formativo; no es una recomendación de inversión.")
    seccion(ws, 4, "Resultado del escenario activo (se actualiza solo)", hasta=8)
    filas = [
        (5, "Escenario activo", f"={hip}!C41", None),
        (6, "WACC", f"={hip}!B22", F_PCT2),
        (7, "Crecimiento a perpetuidad (g)", f"={hip}!B23", F_PCT2),
        (8, "Valor de la empresa (M€)", f"={dcf}!C32", F_M),
        (9, "Valor del capital (M€)", f"={dcf}!C36", F_M),
        (10, "Valor por acción hoy (€)", f"={dcf}!C40", F_EUR),
        (11, "Precio de mercado (€)", f"={hip}!B9", F_EUR),
        (12, "Potencial frente al precio", f"={dcf}!C42", F_PCT),
        (13, "Valor terminal / valor de la empresa", f"={dcf}!C45", F_PCT),
    ]
    for r, et, f, fmt in filas:
        put(ws, f"A{r}", et, "label", bold=(r in (10, 12)))
        put(ws, f"B{r}", f, "link", fmt, bold=(r in (10, 12)), align="right")

    seccion(ws, 15, "Los tres escenarios (foto estática, calculada con Python y verificada contra este Excel)", hasta=8)
    for j, h in enumerate(["Escenario", "WACC", "Valor por acción (€)", "Potencial vs precio", "Valor empresa (M€)", "VT / EV"]):
        put(ws, f"{L(1 + j)}16", h, "label", bold=True, align="right" if j else None)
        ws.cell(row=16, column=1 + j).border = Border(bottom=THIN)
    for k, r in zip((1, 2, 3), (17, 18, 19)):
        x = resultados[k]
        put(ws, f"A{r}", M.ESCENARIOS[k]["nombre"], "label")
        put(ws, f"B{r}", x["wacc"], "input", F_PCT2)
        put(ws, f"C{r}", x["por_accion_hoy"], "input", F_EUR)
        put(ws, f"D{r}", x["upside"], "input", F_PCT)
        put(ws, f"E{r}", x["ev"], "input", F_M)
        put(ws, f"F{r}", x["peso_vt"], "input", F_PCT)
    put(ws, "A20", "Precio de mercado", "label")
    put(ws, "C20", f"={hip}!B9", "link", F_EUR)
    put(ws, "A21", "Para reproducir cada fila: cambia el selector de la hoja Hipótesis (celda B41). La foto no se actualiza sola.", "note")

    seccion(ws, 23, "Cómo leer este libro", hasta=8)
    guia = [
        "Hipótesis: todas las entradas del modelo, con su fuente. Es la única hoja que hay que tocar.",
        "Histórico: cuentas de Inditex 2020-2025 y ratios calculados con fórmulas.",
        "DCF: proyección a 10 años del flujo de caja libre, valor terminal y valor por acción.",
        "Sensibilidad: cómo cambia el valor con el WACC y el crecimiento a perpetuidad.",
        "Comparables: qué valdría Inditex valorada como H&M, Fast Retailing o Next, y gráfico con todos los métodos.",
        "Colores: azul = dato o hipótesis editable · negro = fórmula · verde = enlace a otra hoja · amarillo = decisión clave.",
    ]
    for i, t in enumerate(guia):
        put(ws, f"A{24 + i}", t, "label")

    seccion(ws, 30, "Cómo está planteado (y qué no hace)", hasta=8)
    notas = [
        "Los pagos por arrendamiento (alquiler de tiendas) se restan del flujo de caja como un coste operativo; por eso no se restan después como deuda.",
        "Se valora a 31/07/2026 (último balance, 1S2026) y se actualiza hasta el 07/10/2026. El precio incluye el dividendo de 0,875 € que se paga el 02/11/2026.",
        "El 2026E se valora solo en su segunda mitad, tomando la mitad del flujo anual (ignora la estacionalidad).",
        "No incluye análisis de comparables ni de riesgos específicos (divisa, geopolítica). La prima de riesgo ponderada por ventas es una estimación propia.",
        "Con estas hipótesis, el precio de mercado equivale a un coste del capital de ≈7,5 % frente al 8,97 % del modelo: la diferencia con el consenso de analistas está sobre todo en la tasa de descuento.",
    ]
    for i, t in enumerate(notas):
        put(ws, f"A{31 + i}", t, "label")

    mc_csv = ROOT / "data" / "processed" / "montecarlo_resumen.csv"
    if mc_csv.exists():
        mc = dict(pd.read_csv(mc_csv).values)
        seccion(ws, 38, "Monte Carlo (foto estática: 20.000 simulaciones con src/montecarlo.py)", hasta=8)
        bloque = [
            ("Mediana del valor por acción (€)", mc["mediana"], F_EUR),
            ("Media (€)", mc["media"], F_EUR),
            ("Percentil 5 (€): solo un 5 % de los casos vale menos", mc["p5"], F_EUR),
            ("Percentil 95 (€): solo un 5 % de los casos vale más", mc["p95"], F_EUR),
            ("Probabilidad de que el valor supere el precio de mercado", mc["prob_supera_precio"], F_PCT),
            ("Probabilidad de que el valor supere 50 €", mc["prob_supera_50"], F_PCT),
        ]
        for i, (et, v, fmt) in enumerate(bloque):
            put(ws, f"A{39 + i}", et, "label", bold=(i == 4))
            put(ws, f"B{39 + i}", float(v), "input", fmt, bold=(i == 4))
        put(ws, "A45", "Las hipótesis varían dentro de rangos razonables (beta ±0,10, prima de riesgo ±0,5 pp, crecimiento y margen ±1,2 pp, etc.). Ver docs/Guia_del_modelo.md. No se actualiza sola.", "note")

    alt_csv = ROOT / "data" / "processed" / "calidad_contable_altman.csv"
    ben_csv = ROOT / "data" / "processed" / "calidad_contable_beneish.csv"
    if alt_csv.exists() and ben_csv.exists():
        alt = pd.read_csv(alt_csv, index_col=0)
        ben = pd.read_csv(ben_csv, index_col=0)
        seccion(ws, 47, "Calidad contable (foto estática, src/calidad_contable.py): herramientas de cribado, no una prueba", hasta=8)
        for j, h in enumerate(["Ejercicio", "Altman Z'' (>2,6 segura)", "Beneish M (alerta > −1,78)", "Beneish M ajustado NIIF 16"]):
            put(ws, f"{L(1 + j)}48", h, "label", bold=True, align="right" if j else None)
            ws.cell(row=48, column=1 + j).border = Border(bottom=THIN)
        for i, año in enumerate(alt.index):
            r = 49 + i
            put(ws, f"A{r}", str(año), "label")
            put(ws, f"B{r}", float(alt.loc[año, "Z2"]), "input", F_NUM2)
            if año in ben.index:
                put(ws, f"C{r}", float(ben.loc[año, "M"]), "input", F_NUM2)
                put(ws, f"D{r}", float(ben.loc[año, "M_ajustado_NIIF16"]), "input", F_NUM2)
        put(ws, f"A{49 + len(alt)}", "Beneish necesita el año anterior, por eso empieza en 2021. El ajuste NIIF 16 resta los pagos de alquiler al flujo de explotación. No se actualiza sola.", "note")

    ch = BarChart()
    ch.type = "col"
    ch.title = "Valor por acción: escenarios frente al precio de mercado (€)"
    ch.add_data(Reference(ws, min_col=3, min_row=16, max_row=20), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=1, min_row=17, max_row=20))
    ch.legend = None
    ch.height, ch.width = 7.5, 16
    ch.y_axis.scaling.min = 0
    ch.y_axis.scaling.max = 70       # margen para que el título no pise las etiquetas
    ch.title.overlay = False
    ch.series[0].graphicalProperties.solidFill = "2A78D6"
    ch.dataLabels = DataLabelList()
    ch.dataLabels.showVal = True
    ch.dataLabels.showSerName = False
    ch.dataLabels.showCatName = False
    ch.dataLabels.showLegendKey = False
    ch.dataLabels.showPercent = False
    ch.y_axis.delete = False
    ch.x_axis.delete = False
    ws.add_chart(ch, "H4")
    ws.column_dimensions["A"].width = 40
    for c in "BCDEF":
        ws.column_dimensions[c].width = 18
    return ws


def main():
    resultados = {k: M.valorar(k) for k in (1, 2, 3)}
    wb = Workbook()
    wb.remove(wb.active)
    hoja_historico(wb)
    hoja_hipotesis(wb)
    hoja_dcf(wb)
    hoja_sensibilidad(wb)
    hoja_comparables(wb)
    hoja_resumen(wb, resultados)
    wb._sheets = [wb[ws_names[k]] for k in ("res", "hip", "his", "dcf", "sen", "comp")]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    print("guardado", OUT)


if __name__ == "__main__":
    main()
