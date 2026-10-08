"""Genera el informe en PDF (español e inglés) a partir de una plantilla HTML y Microsoft Edge en modo headless.

Uso:  python src/report_charts.py   (genera los gráficos)
      python src/build_report.py    (genera informe/Inditex_Informe_ES.pdf e informe/Inditex_Report_EN.pdf)
Las cifras son las de los CSV y modelos del proyecto a 7 de octubre de 2026.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "informe" / "report_assets"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
REPO = "github.com/martinpeinado48-cmyk/inditex-valuation"

CSS = """
@page { size: A4; margin: 15mm 16mm 17mm 16mm;
  @bottom-left { content: "Inditex · Martín Peinado Miraflores"; font: 7.5pt 'Segoe UI', Arial, sans-serif; color: #898781; }
  @bottom-right { content: counter(page) " / " counter(pages); font: 7.5pt 'Segoe UI', Arial, sans-serif; color: #898781; } }
* { box-sizing: border-box; }
body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 9pt; line-height: 1.42; color: #0b0b0b; margin: 0; }
h1 { font-size: 21pt; line-height: 1.12; margin: 0 0 3pt 0; letter-spacing: -0.2pt; }
.sub { font-size: 10.5pt; color: #52514e; margin: 0 0 6pt 0; }
.meta { font-size: 8pt; color: #52514e; margin: 0 0 6pt 0; }
.aviso { font-size: 7.6pt; color: #52514e; border-top: 0.6pt solid #c3c2b7; border-bottom: 0.6pt solid #c3c2b7; padding: 3pt 0; margin: 0 0 9pt 0; }
h2 { font-size: 11.5pt; margin: 11pt 0 4pt 0; padding-bottom: 2pt; border-bottom: 1.2pt solid #2a78d6; break-after: avoid; }
p { margin: 0 0 5pt 0; text-align: left; }
ul { margin: 0 0 5pt 0; padding-left: 13pt; } li { margin-bottom: 2.5pt; }
.conclusion { background: #eef4fd; border-left: 3pt solid #2a78d6; padding: 6pt 9pt; margin: 0 0 8pt 0; font-size: 9.4pt; }
.kpis { display: flex; gap: 6pt; margin: 0 0 8pt 0; }
.kpi { flex: 1; border: 0.6pt solid #c3c2b7; padding: 5pt 7pt; background: #fcfcfb; }
.kpi .v { font-size: 15pt; font-weight: 600; color: #0b0b0b; line-height: 1.15; }
.kpi .l { font-size: 7.6pt; color: #52514e; }
table { border-collapse: collapse; width: 100%; margin: 3pt 0 6pt 0; font-size: 8.3pt; }
th { text-align: left; font-weight: 600; border-bottom: 0.9pt solid #0b0b0b; padding: 2.5pt 4pt; color: #0b0b0b; }
td { border-bottom: 0.5pt solid #e1e0d9; padding: 2.5pt 4pt; vertical-align: top; }
td.n, th.n { text-align: right; white-space: nowrap; }
tr.dest td { font-weight: 600; background: #f4f7fc; }
figure { margin: 4pt 0 6pt 0; break-inside: avoid; }
figure img { width: 100%; display: block; }
figcaption { font-size: 7.8pt; color: #52514e; margin-top: 2pt; }
.cols { display: flex; gap: 12pt; } .cols > div { flex: 1; }
.small { font-size: 7.8pt; color: #52514e; }
.pb { break-before: page; }
"""

TXT = {
    "es": dict(
        lang="es", titulo="Inditex: valoración y calidad contable",
        sub="Valoración por DCF, contraste con múltiplos, simulación Monte Carlo y pruebas de calidad contable",
        meta="Martín Peinado Miraflores · Grado en Administración y Dirección de Empresas, Universidad Complutense de Madrid · 8 de octubre de 2026 (datos a 7 de octubre de 2026)",
        aviso="<b>Proyecto educativo. No es asesoramiento de inversión.</b> Las hipótesis son del autor; los datos de terceros se citan con su fuente. El ejercicio N termina el 31 de enero de N+1.",
        conclusion="<b>Conclusión.</b> Con las hipótesis de este análisis, Inditex vale <b>42,9 € por acción</b> (rango de escenarios 32,7-51,7 €) frente a un precio de <b>54,38 €</b>. Los múltiplos de comparables (mediana 42-45 €) apuntan en la misma dirección y solo el 8,9 % de 20.000 simulaciones supera el precio. La diferencia con los precios objetivo de los analistas (media 59,5 €) se explica sobre todo por la <b>tasa de descuento</b>: el precio actual equivale a un coste del capital de ≈7,5 %, frente al 8,97 % de este modelo. Es un negocio excelente (ROIC ≈40 %, caja neta ≈10.400 M€, sin señales de alerta contable): la cuestión no es su calidad, sino cuánto se paga por ella.",
        kpis=[("42,9 €", "Valor por acción, DCF Base (32,7-51,7 €)"), ("54,38 €", "Precio de mercado, 7 oct. 2026"),
              ("42-45 €", "Comparables: mediana de P/E y EV/EBITDA"), ("8,9 %", "Probabilidad de que el valor supere el precio (Monte Carlo)")],
        h_met="Resumen de métodos", th_met=["Método", "Valor por acción", "Rango"],
        met=[("DCF: escenarios Bajo / Base / Alto", "32,7 / <b>42,9</b> / 51,7 €", "—"), ("Comparables: P/E forward (mediana)", "44,9 €", "36,7-79,4 €"),
             ("Comparables: EV/EBITDA (mediana)", "42,2 €", "30,3-76,9 €"), ("Monte Carlo (mediana)", "43,0 €", "32,9-57,3 € (90 % de los casos)"),
             ("Precio objetivo de 24 analistas (media)", "59,5 €", "41,5-65,0 €")],
        fig1="Figura 1. Valor por acción según cada método frente al precio de mercado (campo de fútbol). Punto = valor central.",
        h1="1. El negocio: rentable, con mucha caja y creciendo",
        b1=["Ventas de <b>39.864 M€</b> en el ejercicio 2025 (+3,2 % reportado; <b>+7,0 % a tipo de cambio constante</b>). El primer semestre de 2026 crece un +7,6 % (+9,2 % a tipo constante).",
            "Márgenes en máximos: EBIT del <b>20,1 %</b> (15,4 % en 2021) y neto del 15,6 %. ROIC del 40 % y ROE del 30 %.",
            "Balance muy sólido: caja e inversiones por 10.960 M€, casi sin deuda financiera y un ciclo de caja de −99 días (los proveedores financian el circulante).",
            "La inversión se ha duplicado (de 1.415 M€ en 2022 a 2.712 M€ en 2025) y la compañía guía ≈2.500 M€ para 2026. Los dividendos superan al flujo libre por su política de dividendos extraordinarios (payout ordinario del 60 %)."],
        fig2="Figura 2. Ventas (miles de millones de €, con su variación anual) y márgenes sobre ventas, ejercicios 2020-2025.",
        h2="2. El modelo de valoración por DCF",
        p2="Se proyecta el flujo de caja libre de la empresa a 10 años (ejercicios 2026-2035) y se descuenta a 31 de julio de 2026, la fecha del último balance publicado, con un valor terminal de Gordon. El alquiler de las tiendas se trata como coste operativo, de modo que no se resta de nuevo como deuda (NIIF 16).",
        th_h=["Hipótesis", "Valor", "Fundamento"],
        hip=[("Tipo libre de riesgo", "3,57 %", "Bono alemán a 10 años (30/09/2026)"),
             ("Beta", "1,0", "Regresión propia semanal a 5 años: 0,95-1,08 según el índice"),
             ("Prima de riesgo (ERP)", "5,4 %", "Damodaran: mercado maduro 4,17 % más riesgo-país ponderado por ventas (estimación propia)"),
             ("Coste del capital (WACC)", "<b>8,97 %</b>", "Sin deuda financiera relevante: WACC = coste de los recursos propios"),
             ("Crecimiento perpetuo (g)", "2,5 %", "Entre el objetivo de inflación del BCE (2 %) y el crecimiento nominal esperado"),
             ("Ventas, escenario Base", "+7,5 % (2026E) a +3 % (2035E)", "1S2026 +7,6 %; guía de espacio bruto ≈+5 %"),
             ("Margen EBIT, escenario Base", "20 %", "2025: 20,1 %; consenso hasta 21,6 %; Bankinter prevé estabilidad"),
             ("Capex, escenario Base", "5,8 % a 5,0 % de ventas", "Guía 2026: ≈2.300 M€ ordinarios + 200 M€ extraordinarios")],
        p2b="<b>Del flujo al valor por acción:</b> valor de la empresa 121.063 M€ (el valor terminal es el 58 %) + caja neta 10.398 M€ = valor del capital 131.461 M€, es decir 42,19 € por acción a 31 de julio y <b>42,87 €</b> actualizado a 7 de octubre.",
        h3="3. Qué mueve el resultado",
        p3="El valor es mucho más sensible al coste del capital que a las hipótesis operativas: la prima de riesgo (41-52 €) y la beta (40-51 €) mueven el resultado más que ±1 punto de crecimiento de ventas (40-46 €) o ±1,5 puntos de margen (40-46 €). La beta de 1,0 sale de una regresión propia; el 0,90 que publica Investing.com o el 0,79 del sector darían valores más altos.",
        fig3="Figura 3. Valor por acción (escenario Base) al cambiar una hipótesis cada vez entre su extremo bajo y alto.",
        h4="4. Contraste con el mercado",
        p4a="<b>Comparables.</b> H&M, Fast Retailing y Next, con datos de una sola fuente (Yahoo Finance, 7 de octubre de 2026). Inditex cotiza con una prima del 21 % sobre la mediana de P/E forward (24,6x frente a 20,3x), razonable por su crecimiento (9 % frente al 0,3 % de H&M) y su caja neta. La mediana (42-45 €) coincide con el DCF; la media (50-54 €) sube porque incluye a Fast Retailing, que crece ≈22 %.",
        p4b="<b>Analistas.</b> Precio objetivo medio de 59,5 € (24 analistas, 41,5-65,0 €). Con sus ventas y márgenes pero el coste del capital de este modelo el valor sería ≈47,8 €, y con un coste del 7,3 % ≈63 €: la discrepancia es sobre todo de tasa de descuento.",
        p4c="<b>Monte Carlo.</b> 20.000 simulaciones del DCF variando beta, prima de riesgo, tipo libre de riesgo, g, crecimiento, margen y capex dentro de rangos razonables: mediana 43,0 €, el 90 % de los casos entre 32,9 € y 57,3 €, y un <b>8,9 %</b> de probabilidad de superar el precio. Esas probabilidades dependen de los rangos elegidos, que son estimaciones propias.",
        fig4="Figura 4. Distribución del valor por acción en 20.000 simulaciones. Banda sombreada: 90 % de los casos.",
        h_inv="5. Qué tendría que ocurrir para justificar el precio",
        p_inv="Un DCF inverso (¿qué hipótesis igualan el valor al precio de 54,38 €?) señala tres caminos, cada uno por sí solo: (i) un coste del capital de ≈7,5 % en lugar de 8,97 %; (ii) un crecimiento de ventas ≈3,1 puntos superior cada año al escenario Base; o (iii) cumplir el consenso de ventas y márgenes (EBIT hasta el 21,6 %) con un coste del capital de ≈8,1 %. Ninguno es imposible, pero cada uno exige ser optimista en algo que este análisis trata con prudencia: el precio actual descuenta un buen resultado con poco margen para decepciones.",
        h5="6. Calidad contable: Altman y Beneish",
        p5="El <b>Altman Z''</b> (riesgo de dificultades financieras) sale entre 4,6 y 6,0 en 2020-2025, muy por encima del umbral de zona segura (2,6). El <b>Beneish M</b> (indicios de manipulación del beneficio) está entre −2,74 y −2,95 en 2021-2025, por debajo de los umbrales de alerta (−1,78 y −2,22), y entre −2,49 y −2,70 tras ajustar por la NIIF 16, que infla el flujo de caja de explotación. La señal clave es que Inditex genera más caja que beneficio contable. Son herramientas de cribado, no una prueba: que Inditex salga tranquila era lo esperable, y el valor del ejercicio es aplicarlas e interpretar sus límites.",
        fig5="Figura 5. Altman Z'' (izquierda) y Beneish M-score (derecha) de Inditex.",
        h6="7. Límites",
        b6=["Las hipótesis y los rangos son estimaciones propias (en especial la prima de riesgo ponderada por ventas, los escenarios y el Monte Carlo); un DCF devuelve un rango, no un número exacto, y el valor terminal supone el 58 % del valor.",
            "El segundo semestre de 2026 se valora como la mitad del flujo anual, lo que ignora la estacionalidad de la caja.",
            "Solo tres comparables, con ejercicios fiscales y países distintos. Las etiquetas del consenso de analistas se interpretaron como ejercicios que terminan en enero.",
            "El Altman y el Beneish se diseñaron con otras empresas y otra época."],
        fuentes=f"<b>Fuentes:</b> cuentas anuales y resultados de Inditex (inditex.com); Yahoo Finance; Investing.com; datosmacro; Damodaran; BCE; Bolsamanía; Bankinter. Código, datos y modelo de Excel con cada cifra y su fuente: {REPO}.",
        salida="Inditex_Informe_ES.pdf"),
    "en": dict(
        lang="en", titulo="Inditex: valuation and accounting quality",
        sub="DCF valuation, cross-check with peer multiples, Monte Carlo simulation and accounting-quality screens",
        meta="Martín Peinado Miraflores · BA in Business Administration, Universidad Complutense de Madrid · 8 October 2026 (data as of 7 October 2026)",
        aviso="<b>Educational project. Not investment advice.</b> All hypotheses are the author's; third-party data is cited with its source. Fiscal year N ends on 31 January N+1.",
        conclusion="<b>Bottom line.</b> On the assumptions of this analysis, Inditex is worth <b>€42.9 per share</b> (scenario range €32.7-51.7) against a market price of <b>€54.38</b>. Peer multiples (median €42-45) point the same way, and only 8.9 % of 20,000 simulations exceed the price. The gap to analysts' price targets (mean €59.5) is mostly the <b>discount rate</b>: today's price implies a cost of capital of about 7.5 %, versus 8.97 % in this model. This is an excellent business (ROIC ≈40 %, net cash ≈€10.4 bn, no accounting red flags): the question is not its quality, but how much is paid for it.",
        kpis=[("€42.9", "Value per share, DCF Base (€32.7-51.7)"), ("€54.38", "Market price, 7 Oct 2026"),
              ("€42-45", "Peer multiples: median of P/E and EV/EBITDA"), ("8.9 %", "Probability that value exceeds the price (Monte Carlo)")],
        h_met="Summary of methods", th_met=["Method", "Value per share", "Range"],
        met=[("DCF: Low / Base / High scenarios", "€32.7 / <b>€42.9</b> / €51.7", "—"), ("Peers: forward P/E (median)", "€44.9", "€36.7-79.4"),
             ("Peers: EV/EBITDA (median)", "€42.2", "€30.3-76.9"), ("Monte Carlo (median)", "€43.0", "€32.9-57.3 (90 % of runs)"),
             ("Price target of 24 analysts (mean)", "€59.5", "€41.5-65.0")],
        fig1="Figure 1. Value per share by method against the market price (football field). Dot = central value.",
        h1="1. The business: profitable, cash-rich and growing",
        b1=["Sales of <b>€39,864 m</b> in fiscal 2025 (+3.2 % reported; <b>+7.0 % at constant currency</b>). The first half of fiscal 2026 grew +7.6 % (+9.2 % at constant currency).",
            "Margins at record highs: EBIT margin <b>20.1 %</b> (15.4 % in 2021) and net margin 15.6 %. ROIC 40 % and ROE 30 %.",
            "Very strong balance sheet: €10,960 m of cash and investments, almost no financial debt and a cash conversion cycle of −99 days (suppliers fund working capital).",
            "Capex has doubled (from €1,415 m in 2022 to €2,712 m in 2025) and the company guides about €2,500 m for 2026. Dividends exceed free cash flow because of its extraordinary-dividend policy (60 % ordinary payout)."],
        fig2="Figure 2. Sales (EUR billion, with annual change) and margins on sales, fiscal years 2020-2025.",
        h2="2. The DCF valuation model",
        p2="The free cash flow to the firm is projected for 10 years (fiscal 2026-2035) and discounted to 31 July 2026, the date of the latest published balance sheet, with a Gordon terminal value. Store rent is treated as an operating cost, so it is not deducted again as debt (IFRS 16).",
        th_h=["Assumption", "Value", "Basis"],
        hip=[("Risk-free rate", "3.57 %", "10-year German Bund (30/09/2026)"),
             ("Beta", "1.0", "Own weekly 5-year regression: 0.95-1.08 depending on the index"),
             ("Equity risk premium (ERP)", "5.4 %", "Damodaran: mature market 4.17 % plus country risk weighted by sales (author's estimate)"),
             ("Cost of capital (WACC)", "<b>8.97 %</b>", "No relevant financial debt: WACC = cost of equity"),
             ("Perpetual growth (g)", "2.5 %", "Between the ECB inflation target (2 %) and expected nominal growth"),
             ("Sales, Base scenario", "+7.5 % (2026E) to +3 % (2035E)", "H1 2026 +7.6 %; gross space guidance ≈+5 %"),
             ("EBIT margin, Base scenario", "20 %", "2025: 20.1 %; consensus up to 21.6 %; Bankinter expects stability"),
             ("Capex, Base scenario", "5.8 % to 5.0 % of sales", "2026 guidance: ≈€2,300 m ordinary + €200 m extraordinary")],
        p2b="<b>From cash flow to value per share:</b> enterprise value €121,063 m (the terminal value is 58 %) + net cash €10,398 m = equity value €131,461 m, i.e. €42.19 per share at 31 July and <b>€42.87</b> rolled forward to 7 October.",
        h3="3. What drives the result",
        p3="The value is far more sensitive to the cost of capital than to operating assumptions: the equity risk premium (€41-52) and beta (€40-51) move the result more than ±1 point of sales growth (€40-46) or ±1.5 points of margin (€40-46). The beta of 1.0 comes from an own regression; the 0.90 published by Investing.com or the 0.79 sector beta would give higher values.",
        fig3="Figure 3. Value per share (Base scenario) when changing one assumption at a time between its low and high end.",
        h4="4. Cross-check with the market",
        p4a="<b>Peer multiples.</b> H&M, Fast Retailing and Next, from a single source (Yahoo Finance, 7 October 2026). Inditex trades at a 21 % premium to the peer median forward P/E (24.6x vs 20.3x), reasonable given its growth (9 % vs 0.3 % at H&M) and net cash. The median (€42-45) matches the DCF; the mean (€50-54) is higher because it includes Fast Retailing, which grows ≈22 %.",
        p4b="<b>Analysts.</b> Mean price target €59.5 (24 analysts, €41.5-65.0). With their sales and margins but this model's cost of capital the value would be ≈€47.8, and at a 7.3 % cost of capital ≈€63: the discrepancy is mostly the discount rate.",
        p4c="<b>Monte Carlo.</b> 20,000 simulations of the DCF varying beta, equity risk premium, risk-free rate, g, growth, margin and capex within reasonable ranges: median €43.0, 90 % of runs between €32.9 and €57.3, and an <b>8.9 %</b> probability of exceeding the price. These probabilities depend on the ranges chosen, which are the author's estimates.",
        fig4="Figure 4. Distribution of value per share across 20,000 simulations. Shaded band: 90 % of runs.",
        h_inv="5. What would have to happen to justify the price",
        p_inv="A reverse DCF (which assumptions make the value equal to the €54.38 price?) points to three alternative paths, each on its own: (i) a cost of capital of about 7.5 % instead of 8.97 %; (ii) sales growth about 3.1 points higher every year than in the Base scenario; or (iii) delivering the analysts' consensus sales and margins (EBIT up to 21.6 %) with a cost of capital of about 8.1 %. None is impossible, but each requires being optimistic about something this analysis treats prudently: today's price already discounts a good outcome with little room for disappointment.",
        h5="6. Accounting quality: Altman and Beneish",
        p5="The <b>Altman Z''</b> (financial distress risk) is between 4.6 and 6.0 in 2020-2025, far above the safe-zone threshold (2.6). The <b>Beneish M</b> (signs of earnings manipulation) is between −2.74 and −2.95 in 2021-2025, below the alert thresholds (−1.78 and −2.22), and between −2.49 and −2.70 after adjusting for IFRS 16, which inflates operating cash flow. The key signal is that Inditex generates more cash than accounting profit. These are screening tools, not proof: a clean result for Inditex was expected, and the point of the exercise is to apply them and interpret their limits.",
        fig5="Figure 5. Inditex Altman Z'' (left) and Beneish M-score (right).",
        h6="7. Limitations",
        b6=["Assumptions and ranges are the author's estimates (in particular the sales-weighted risk premium, the scenarios and the Monte Carlo); a DCF returns a range, not an exact number, and the terminal value is 58 % of the total.",
            "The second half of fiscal 2026 is valued as half of the annual cash flow, which ignores cash seasonality.",
            "Only three peers, with different fiscal calendars and countries. Analyst-consensus labels were interpreted as fiscal years ending in January.",
            "Altman and Beneish were designed on other companies and another era."],
        fuentes=f"<b>Sources:</b> Inditex annual accounts and results (inditex.com); Yahoo Finance; Investing.com; datosmacro; Damodaran; ECB; Bolsamanía; Bankinter. Code, data and the Excel model with every figure and its source: {REPO}.",
        salida="Inditex_Report_EN.pdf"),
}


def html(t: dict) -> str:
    lang = t["lang"]
    img = lambda n: (ASSETS / lang / n).as_uri()
    kpis = "".join(f'<div class="kpi"><div class="v">{v}</div><div class="l">{l}</div></div>' for v, l in t["kpis"])
    met = "".join(f"<tr><td>{a}</td><td class='n'>{b}</td><td class='n'>{c}</td></tr>" for a, b, c in t["met"])
    th_met = "".join(f"<th{' class=n' if i else ''}>{h}</th>" for i, h in enumerate(t["th_met"]))
    hip = "".join(f"<tr{' class=dest' if '8,97' in b or '8.97' in b else ''}><td>{a}</td><td class='n'>{b}</td><td>{c}</td></tr>" for a, b, c in t["hip"])
    th_h = "".join(f"<th{' class=n' if i == 1 else ''}>{h}</th>" for i, h in enumerate(t["th_h"]))
    b1 = "".join(f"<li>{x}</li>" for x in t["b1"])
    b6 = "".join(f"<li>{x}</li>" for x in t["b6"])
    fig = lambda n, cap: f'<figure><img src="{img(n)}"><figcaption>{cap}</figcaption></figure>'
    return f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>{t['titulo']}</title><style>{CSS}</style></head><body>
<h1>{t['titulo']}</h1><p class="sub">{t['sub']}</p><p class="meta">{t['meta']}</p><p class="aviso">{t['aviso']}</p>
<div class="conclusion">{t['conclusion']}</div>
<div class="kpis">{kpis}</div>
<table><tr>{th_met}</tr>{met}</table>
{fig('campo_futbol.png', t['fig1'])}

<h2>{t['h1']}</h2><ul>{b1}</ul>{fig('negocio.png', t['fig2'])}
<h2>{t['h2']}</h2><p>{t['p2']}</p>
<table><tr>{th_h}</tr>{hip}</table><p>{t['p2b']}</p>

<h2>{t['h3']}</h2><p>{t['p3']}</p>{fig('tornado.png', t['fig3'])}
<h2>{t['h4']}</h2><p>{t['p4a']}</p><p>{t['p4b']}</p><p>{t['p4c']}</p>{fig('montecarlo.png', t['fig4'])}
<h2>{t['h_inv']}</h2><p>{t['p_inv']}</p>

<h2>{t['h5']}</h2><p>{t['p5']}</p>{fig('calidad.png', t['fig5'])}
<h2>{t['h6']}</h2><ul>{b6}</ul>
<p class="small">{t['fuentes']}</p>
</body></html>"""


def build(lang: str) -> Path:
    t = TXT[lang]
    out = ROOT / "informe" / t["salida"]
    tmp = Path(tempfile.gettempdir()) / f"informe_{lang}.html"
    tmp.write_text(html(t), encoding="utf-8")
    cmd = [EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf-no-header",
           f"--print-to-pdf={out}", tmp.as_uri()]
    subprocess.run(cmd, check=True, timeout=120, capture_output=True)
    return out


if __name__ == "__main__":
    for lang in (sys.argv[1:] or ["es", "en"]):
        print(build(lang))
