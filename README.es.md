# Inditex: valoración y calidad contable

Proyecto de finanzas corporativas de **Martín Peinado Miraflores** (estudiante de Administración y Dirección de Empresas, Universidad Complutense de Madrid).
🇬🇧 [English version](README.md)

> **Proyecto educativo. No es asesoramiento de inversión.** Todas las hipótesis son del autor; los datos de terceros se conservan con su fuente y fecha. Cifras a **7 de octubre de 2026**.

📄 **Informe de 4 páginas (PDF):** [Español](informe/Inditex_Informe_ES.pdf) · [English](informe/Inditex_Report_EN.pdf)

## Qué hace este proyecto

1. **Extrae** las cuentas anuales consolidadas de Inditex (ejercicios 2020-2025) desde los PDF oficiales a un conjunto de datos limpio, validado con identidades contables (el balance cuadra, EBITDA → EBIT → resultado neto, y los flujos de caja explican la variación de caja del balance).
2. **Analiza ratios** (márgenes, ROIC/ROE, circulante, caja frente a dividendos) en un cuaderno de Jupyter.
3. **Valora la empresa por DCF** en Excel (fórmulas vivas, tres escenarios, tabla de sensibilidad) y con una **réplica en Python que coincide con el Excel al céntimo**.
4. **Contrasta el resultado** con múltiplos de comparables (H&M, Fast Retailing, Next), una simulación **Monte Carlo** (20.000 repeticiones) y dos pruebas de calidad contable: **Altman Z''** y **Beneish M-score**.

## Resultados principales (precio de la acción: 54,38 €)

| Método | Valor por acción |
|---|---|
| DCF, escenarios Bajo / **Base** / Alto | 32,73 € / **42,87 €** / 51,75 € |
| Múltiplos de comparables, mediana (P/E forward · EV/EBITDA) | 44,9 € · 42,2 € |
| Monte Carlo: mediana y 90 % de los casos | 43,0 €, entre 32,9 € y 57,3 € |
| Probabilidad de que el valor supere el precio | **8,9 %** |
| Precio objetivo del consenso de analistas (24 analistas) | 59,54 € (rango 41,50-65,00 €) |
| Altman Z'' 2020-2025 (zona segura: por encima de 2,6) | de 4,6 a 6,0 |
| Beneish M 2021-2025 (alerta: por encima de −1,78) | de −2,74 a −2,95 (de −2,49 a −2,70 ajustado por NIIF 16) |

**Conclusión.** Con los flujos del escenario Base, el precio actual equivale a un coste del capital de **≈7,5 %**, frente al **8,97 %** que usa el modelo. Buena parte de la diferencia con los precios objetivo de los analistas está en la **tasa de descuento**, no en las previsiones operativas: con las ventas y márgenes del consenso pero el coste del capital de este modelo, el valor es de ≈47,8 €. Las pruebas de calidad contable no muestran señales de alerta (son herramientas de cribado, no una prueba).

![Campo de fútbol: DCF, múltiplos de comparables, analistas y rango de cotización](informe/graficos/09_campo_de_futbol.png)

![Distribución Monte Carlo del valor por acción](informe/graficos/10_montecarlo_histograma.png)

## El método en resumen

- **Coste del capital 8,97 %:** tipo libre de riesgo 3,57 % (bono alemán a 10 años) + beta 1,0 (regresión propia, 0,95-1,08 según el índice) × prima de riesgo 5,4 % (mercado maduro de Damodaran, 4,17 %, más riesgo-país ponderado por las ventas de Inditex: **estimación propia**). Crecimiento a perpetuidad 2,5 %.
- **Alquileres (NIIF 16):** el alquiler se trata como coste operativo en el flujo de caja libre, así que los pasivos por arrendamiento *no* se restan otra vez en el puente al valor del capital.
- **Fecha de valoración** 31 de julio de 2026 (último balance publicado, primer semestre de 2026), actualizada hasta la fecha del precio. Descuento a mitad de periodo, proyección explícita a 10 años y valor terminal de Gordon (≈58 % del valor de la empresa).
- **Escenarios** de crecimiento de ventas, margen EBIT y capex, contrastados con la guía de la compañía, el consenso de analistas y los informes de brokers.

Una explicación paso a paso de cada dato y de cada celda del modelo de Excel está en [`docs/Guia_del_modelo.md`](docs/Guia_del_modelo.md).

## Estructura del repositorio

```
excel/Inditex_Valoracion.xlsx      Modelo: Resumen, Hipótesis, Histórico, DCF, Sensibilidad, Comparables
notebooks/01_analisis_ratios.ipynb Análisis de ratios con gráficos
src/
  extract_statements.py            PDF -> tabla de estados financieros
  build_dataset.py                 Normaliza partidas y valida identidades contables
  dcf_model.py                     DCF en Python (comprueba el Excel; lo reutiliza el Monte Carlo)
  beta.py                          Regresión de la beta frente a índices europeos (datos de Yahoo Finance)
  hipotesis_analisis.py            Gráfico tornado, paquetes de coste del capital, DCF inverso
  comparables.py                   Valoración por múltiplos y campo de fútbol
  montecarlo.py                    Monte Carlo de 20.000 repeticiones sobre el DCF
  calidad_contable.py              Altman Z'' y Beneish M-score
  build_excel.py                   Construye el libro de Excel con fórmulas
  limpiar_metadatos_excel.py       Quita del .xlsx los metadatos del equipo
  report_charts.py                 Gráficos del informe en español e inglés
  build_report.py                  Genera los informes en PDF (plantilla HTML + Microsoft Edge sin ventana)
data/market/                       Datos de mercado y múltiplos, cada uno con fuente y fecha
data/processed/                    Datos limpios y resultados del modelo
informe/                           Informes en PDF (ES/EN) y gráficos (graficos/, report_assets/)
docs/Guia_del_modelo.md            Guía completa del modelo
```

## Cómo reproducirlo

Requiere Python 3.12.

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

1. Descarga las cuentas anuales consolidadas de Inditex (ejercicios 2021-2025) desde la [página de relación con inversores](https://www.inditex.com/itxcomweb/ad/es/inversores/informacion-financiera) y guárdalas en `data/raw/` como `CCAA_consolidadas_FY2021.pdf` … `CCAA_consolidadas_FY2025.pdf`. (Los PDF no están en este repositorio.)
2. Ejecuta el proceso desde la raíz del proyecto:

```bash
python src/extract_statements.py
python src/build_dataset.py
python src/dcf_model.py
python src/comparables.py
python src/montecarlo.py
python src/calidad_contable.py
python src/report_charts.py
python src/build_report.py      # necesita Microsoft Edge; escribe los dos PDF en informe/
```

`src/beta.py` y `src/hipotesis_analisis.py` necesitan conexión a internet (Yahoo Finance). Excel recalcula el libro al abrirlo; `src/build_excel.py` lo regenera desde Python.

## Fuentes de datos y límites

- **Fuentes:** cuentas anuales y resultados consolidados de Inditex (inditex.com); Yahoo Finance e Investing.com (precios, múltiplos, betas); datosmacro (rentabilidad de bonos); Damodaran (primas de riesgo, betas sectoriales); proyecciones del BCE; Bolsamanía y Bankinter (consenso e informes). Cada dato de `data/market/` lleva su fuente y fecha.
- **Límites:** el primer semestre del ejercicio 2026 se valora como la mitad del flujo anual (ignora la estacionalidad); solo tres comparables, con ejercicios fiscales distintos (sin calendarizar); las etiquetas del consenso se interpretaron como ejercicios que terminan en enero; las probabilidades del Monte Carlo dependen de los rangos elegidos para cada hipótesis; el Altman y el Beneish se diseñaron con otras empresas y otra época.

## Autor y licencia

Martín Peinado Miraflores, Administración y Dirección de Empresas, Universidad Complutense de Madrid.
Publicado bajo la [licencia MIT](LICENSE). Los datos de terceros siguen sujetos a los términos de sus fuentes originales.
