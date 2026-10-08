# Guía del modelo: qué hace cada dato y por qué

Guía para entender el proyecto de valoración de Inditex de principio a fin. Las cifras son las del **7 de octubre de 2026** con las hipótesis decididas ese día. Importes en millones de euros (M€) salvo indicación.

> **La idea en una frase:** el valor de Inditex es la caja libre que generará en el futuro, traída al presente con una tasa que refleja el riesgo, más la caja que ya tiene.

Cada dato del modelo hace una de tres cosas:

- **A. Punto de partida:** de dónde arrancamos (datos históricos).
- **B. Predecir la caja futura:** crecimiento, margen, inversión, circulante.
- **C. Fijar la tasa de descuento:** cuánto riesgo exige el inversor.

---

## 1. Mapa del proyecto

```
cuentas anuales (PDF) ──► tabla limpia ──► ratios ──► hipótesis ──► DCF ──► valor por acción
   data/raw             data/processed   notebooks    Excel: Hipótesis   Excel: DCF   Excel: Resumen
                                                                          ▲
                                          data/market (precio, tipos, beta, consenso)
```

| Carpeta | Qué contiene |
|---|---|
| `data/raw/` | PDF y Excel oficiales de Inditex tal como se descargaron |
| `data/processed/` | Tablas limpias: histórico, ratios, resultados de sensibilidad |
| `data/market/` | Datos de mercado con fuente y fecha, y la beta calculada |
| `src/` | Scripts de Python (ver sección 6) |
| `notebooks/` | Análisis de ratios con gráficos |
| `excel/` | El modelo de valoración |
| `informe/graficos/` | Gráficos para LinkedIn e informe |

---

## 2. Paso 1: datos históricos (hoja *Histórico*)

**De dónde salen:** de las cuentas anuales consolidadas oficiales de Inditex (inditex.com), ejercicios 2020-2025. Un script extrae las tres cuentas (resultados, balance, flujos de caja) y otro las normaliza.

**Cómo sé que están bien:** comprobaciones automáticas. El balance cuadra (activo = pasivo + patrimonio), EBITDA − amortizaciones = EBIT, EBIT + resultados financieros = BAI, la variación de caja de los flujos coincide con la del balance, y las cifras coinciden con el Excel resumen oficial de Inditex. Todas pasan con ±1 M€ de redondeo.

**Convención:** el ejercicio N termina el 31 de enero de N+1. El «2025» de Inditex es febrero de 2025 a enero de 2026.

| Dato (2025) | Valor | Para qué lo uso |
|---|---|---|
| Ventas | 39.864 | Base de la proyección: ventas 2026E = 39.864 × (1 + crecimiento) |
| EBIT | 7.997 (20,1 %) | Beneficio operativo; su % sobre ventas orienta la hipótesis de margen |
| Amortizaciones | 3.270 (8,2 % de ventas) | Para pasar de EBIT a EBITDA |
| Impuestos / BAI | 22,4 % | Referencia para el tipo impositivo futuro (22,5 %) |
| Pagos por arrendamiento | 1.834 (4,6 %) | Alquiler de tiendas: un coste real que se resta de la caja |
| Interés de arrendamientos | 215 (0,5 %) | Solo para calcular el impuesto |
| Capex (inversión) | 2.712 (6,8 %) | Salida de caja cada año |
| Existencias + deudores − acreedores | −3.854 (−9,7 %) | Circulante: al ser negativo, crecer libera caja |
| Caja + inversiones temporales − deuda | 10.958 | La caja ya existente (en el modelo se usa la del 31/07/2026) |
| CFO, dividendos, patrimonio, total activo | | Solo ratios y contexto. **No entran en el DCF** |

---

## 3. Paso 2: ratios (cuaderno `01_analisis_ratios.ipynb`)

Sirven para **entender el negocio** antes de predecirlo. No alimentan directamente el DCF, pero justifican las hipótesis.

- **Márgenes** (bruto, EBITDA, EBIT, neto): qué parte de cada euro vendido se queda como beneficio.
- **ROE y ROIC:** cuánto rinde el dinero invertido. El ROIC trata los arrendamientos como financiación y descuenta la caja.
- **Días de inventario, cobro y pago:** cómo gestiona el circulante.
- **Caja, FCF y dividendos:** cuánto genera, cuánto invierte y cuánto reparte.

Hallazgos y correcciones: el crecimiento reportado de 2025 (+3,2 %) estaba distorsionado por la divisa (a tipo constante fue +7,0 %), y los dividendos superiores al flujo libre responden a la política de dividendos extraordinarios, no a tensión financiera.

---

## 4. Paso 3: hipótesis (hoja *Hipótesis*)

### 4.1 Datos de mercado
Precio (54,38 €) y número de acciones (3.115,9 M). **No intervienen en el valor.** Sirven para dividir el valor entre las acciones y compararlo con el precio.

### 4.2 Coste del capital

**Qué es:** la rentabilidad mínima que exigiría un inversor para poner su dinero en Inditex en lugar de en otra cosa. Se usa para descontar los flujos futuros: cuanto más alta, menos valen hoy.

**Fórmula (CAPM):** `Ke = rf + beta × ERP`

| Pieza | Valor | Qué es | Decisión y fuente |
|---|---|---|---|
| rf (tipo libre de riesgo) | 3,57 % | Lo que se gana sin riesgo | Bono alemán a 10 años (30/09/2026). El español está en 4,11 %, pero incluye riesgo de España |
| beta | 1,0 | Cuánto se mueve la acción frente al mercado | Regresión propia semanal a 5 años: 0,95-1,08 según el índice. Investing.com 0,90; sector (Damodaran) 0,79 |
| ERP (prima de riesgo) | 5,4 % | Extra que exige la bolsa frente al activo sin riesgo | Damodaran mercado maduro 4,17 % + riesgo-país ponderado por ventas (estimación propia). España: 5,78 % |
| **Ke** | **8,97 %** | | 3,57 % + 1,0 × 5,4 % |

Como Inditex casi no tiene deuda, **WACC = Ke = 8,97 %**.

### 4.3 Crecimiento a perpetuidad (g = 2,5 %)
Ritmo al que crece la empresa para siempre a partir de 2035. Debe ser menor que el tipo libre de riesgo y razonable frente al crecimiento nominal de la economía. El BCE prevé inflación del 2,1 % en 2028 con un objetivo del 2 %.

### 4.4 Balance de partida (31/07/2026)
Se parte del último balance publicado (primer semestre de 2026). Caja neta = 4.361 + 6.038 − 1 = **10.398**. Se suma al final porque es dinero que ya existe. **No se restan los arrendamientos (6.197)** porque su coste ya está dentro del flujo de caja.

### 4.5 Parámetros operativos (comunes a los tres escenarios)
Amortizaciones 8,2 %, alquileres 4,6 %, interés de alquileres 0,5 % y circulante −8,5 % de las ventas, basados en el histórico.

### 4.6 Escenarios
Tres juegos de crecimiento, margen EBIT y capex por año. El selector (celda B41: 1 Bajo, 2 Base, 3 Alto) elige cuál usa el modelo, mediante la fila «Activo».

| | Crecimiento de ventas | Margen EBIT | Capex / ventas |
|---|---|---|---|
| Bajo | 5 % bajando a 2,5 % | 20 % bajando a 18 % | 5,8 % → 5,5 % |
| **Base** | **7,5 % bajando a 3 %** | **20 % constante** | **5,8 % → 5,0 %** |
| Alto | 9 % bajando a 3,5 % | 20,5 % subiendo a 22 % | 5,8 % → 4,5 % |

Contraste con el mercado: el consenso de 24 analistas (31/08/2026) prevé ventas de 42.727 M€ en el ejercicio 2026 hasta 53.086 M€ en 2029 y EBIT del 20,4 % al 21,6 %. Bankinter (10/09/2026) espera márgenes estables. Inditex guía 2.300 + 200 M€ de inversión, espacio bruto +5 % y efecto divisa del −1 %.

---

## 5. Paso 4: el DCF (hoja *DCF*)

### 5.1 La caja libre de cada año (FCFF), con 2026E como ejemplo

| Fila | Cálculo | 2026E |
|---|---|---|
| Ventas | 39.864 × (1 + 7,5 %) | 42.854 |
| EBIT | ventas × 20 % | 8.571 |
| Amortizaciones | ventas × 8,2 % | 3.514 |
| **EBITDA** | EBIT + amortizaciones | 12.085 |
| (−) Pagos por arrendamiento | ventas × 4,6 % | −1.971 |
| (−) Impuestos | 22,5 % × (EBIT − interés de alquileres 214) | −1.880 |
| (−) Capex | ventas × 5,8 % | −2.486 |
| (−) Aumento de circulante | saldo −3.643 frente a −3.854 el año anterior | −211 |
| **FCFF** | suma de las filas anteriores | **5.536** |

**Por qué el alquiler se resta aquí:** es un coste real de operar las tiendas, así que se trata como gasto operativo. Por eso no se resta de nuevo como deuda en el puente final; sería contarlo dos veces.

**Por qué el circulante resta 211:** el circulante de Inditex es negativo (los proveedores financian el negocio). Si el saldo negativo se reduce, sale caja; si crece en negativo, entra caja.

### 5.2 Descontar al presente

1. **Fracción del año:** se valora desde el 31/07/2026, así que de 2026E solo cuenta la segunda mitad: 5.536 × 0,5 = **2.768**.
2. **Tiempo de descuento (mitad de periodo):** la caja llega a lo largo del año, no el 31 de diciembre. 2026E: 0,25 años; 2027E: 1,0; 2028E: 2,0; … 2035E: 9,0.
3. **Factor de descuento:** 1 / (1 + WACC)^t. Para 2026E: 1 / 1,0897^0,25 = **0,9788**.
4. **Valor actual:** 2.768 × 0,9788 = **2.709**.

Se repite para 2027E-2035E. La suma de los diez valores actuales es **50.816**.

### 5.3 Valor terminal (lo que vale después de 2035)

`VT = FCFF 2035 × (1 + g) / (WACC − g) = 9.607 × 1,025 / (8,97 % − 2,5 %) = 152.191`

Descontado con el factor del último año (0,4616): **70.247**.

### 5.4 Del valor de la empresa al valor por acción

| Concepto | Importe |
|---|---|
| Suma del valor actual de los flujos | 50.816 |
| (+) Valor actual del valor terminal | 70.247 |
| **Valor de la empresa (EV)** | **121.063** |
| (+) Caja neta a 31/07/2026 | 10.398 |
| **Valor del capital (equity)** | **131.461** |
| ÷ Acciones (millones) | 3.115,9 |
| Valor por acción a 31/07/2026 | 42,19 € |
| × Actualización de 68 días hasta el 07/10 (1,0897^(68/365) = 1,0162) | |
| **Valor por acción hoy** | **42,87 €** |

El valor terminal es el 58 % del valor de la empresa. Por eso el coste del capital y g pesan tanto.

### 5.5 Controles de sensatez (parte baja de la hoja)
- Valor terminal / EV.
- EV / EBITDA tras alquileres implícito frente al del mercado.
- g < rf y WACC > g (si no, la fórmula del valor terminal no tiene sentido).

---

## 5b. Valoración por comparables (hoja *Comparables*)

**La idea.** El DCF valora Inditex por lo que *creemos* que generará. Los comparables miran lo que el mercado *paga* hoy por empresas parecidas. Si ambas respuestas se parecen, la valoración es más creíble.

**Los datos.** Cuatro empresas (Inditex, H&M, Fast Retailing, Next) de **una sola fuente**, Yahoo Finance, el 07/10/2026, para que las definiciones sean las mismas:

| | P/E forward | EV/EBITDA | Margen operativo | Crec. ventas trim. |
|---|---|---|---|---|
| Inditex | 24,6x | 13,5x | 18,9 % | 9,1 % |
| H&M | 20,3x | 7,7x | 10,7 % | 0,3 % |
| Fast Retailing | 36,0x | 20,2x | 21,0 % | 22,2 % |
| Next | 16,6x | 10,9x | 17,7 % | 9,6 % |

- **P/E forward:** precio entre el beneficio por acción esperado. «Se paga X veces el beneficio del próximo año.»
- **EV/EBITDA:** valor de la empresa entre su EBITDA. «Se paga X veces lo que genera antes de amortizar.»

**Qué se hace con ellos.** Se pregunta: ¿cuánto valdría Inditex si se valorase al mismo múltiplo que cada comparable?

1. **Por P/E forward:** valor por acción = P/E del comparable × beneficio por acción forward de Inditex (2,21 €, que es el precio entre su propio P/E forward).
2. **Por EV/EBITDA:** valor de la empresa = múltiplo × EBITDA de Inditex de los últimos 12 meses (11.666 M€). Como el EV de Yahoo incluye los alquileres como deuda, para llegar al valor del capital se **resta** el pasivo por arrendamiento (6.197) y se **suma** la caja neta (10.398). Después se divide entre las acciones.

| Si Inditex se valorase como… | Por P/E | Por EV/EBITDA |
|---|---|---|
| H&M | 44,9 € | 30,3 € |
| Next | 36,7 € | 42,2 € |
| Fast Retailing | 79,4 € | 76,9 € |
| **Mediana** | **44,9 €** | **42,2 €** |
| Media | 53,7 € | 49,8 € |
| Media sin Fast Retailing | 40,8 € | 36,2 € |

**Control.** Aplicando a Inditex su *propio* múltiplo EV/EBITDA (13,5x) con mi EBITDA, sale 51,9 € frente al precio de 54,38 € (−4,5 %). La diferencia viene de que Yahoo define el EBITDA de Inditex algo distinto (≈11.900 M€ frente a 11.666 M€).

**Cómo leerlo.** Inditex cotiza con una prima del ≈21 % sobre la mediana de P/E forward de sus comparables, y es razonable: crece al 9 % (H&M al 0,3 %), tiene mejor margen que H&M y caja neta. H&M tiende a *infravalorar* Inditex y Fast Retailing (crece al 22 %, empresa japonesa) a *sobrevalorarla*, y por eso el rango es tan ancho.

**El campo de fútbol** (gráfico `09_campo_de_futbol.png` y sección 4 de la hoja) pone en una misma escala los rangos de valor de todos los métodos: DCF, comparables por P/E, comparables por EV/EBITDA, precio objetivo de analistas y rango de cotización de 52 semanas.

---

## 5c. Monte Carlo (`src/montecarlo.py`)

**La idea.** El modelo da tres futuros (Bajo, Base, Alto). El Monte Carlo repite el DCF **20.000 veces**, cada vez con valores al azar de las hipótesis inciertas, y devuelve una distribución de valores posibles. Permite responder: *¿qué probabilidad hay de que el valor supere el precio actual?*

**Qué varía y por qué ese rango:**

| Hipótesis | Centro | Variación | Origen |
|---|---|---|---|
| Beta | 1,0 | ±0,10 (desviación típica) | Error típico de la regresión (0,08-0,10) |
| Prima de riesgo | 5,4 % | ±0,5 pp | Rango Damodaran 4,2-5,8 % |
| Tipo libre de riesgo | 3,57 % | ±0,3 pp | Movimiento habitual del bono a 10 años |
| g | 2,5 % | de 2,0 a 3,0 % (triangular) | Inflación objetivo BCE y crecimiento nominal |
| Crecimiento de ventas | camino Base | ±1,2 pp todos los años | Distancia entre los escenarios |
| Margen EBIT | 20 % | ±1,2 pp | Bankinter (estable) frente a consenso (21,6 %) |
| Capex | camino Base | ±0,4 pp de ventas | Poco peso en el tornado |

El crecimiento y el margen van **correlacionados** (0,3): más ventas suelen diluir costes fijos. Los valores extremos se recortan a límites razonables y se garantiza WACC − g ≥ 2 pp. La semilla es fija (2026), así que el resultado es reproducible.

**Resultado (20.000 simulaciones):**

| | Valor por acción |
|---|---|
| Mediana | 43,0 € (casi igual que el DCF Base, 42,9 €: buena señal de coherencia) |
| Media | 43,8 € |
| Percentil 5 – Percentil 95 | 32,9 € – 57,3 € (el 90 % de los casos) |
| **Probabilidad de superar el precio (54,38 €)** | **8,9 %** |
| Probabilidad de superar 50 € | 19,1 % |

**Qué hipótesis explican más la dispersión** (correlación de rangos con el valor): crecimiento de ventas 0,62, margen EBIT 0,49, beta −0,43, prima de riesgo −0,40, tipo libre de riesgo −0,24, capex −0,15, g 0,10.

**Matiz importante.** Esto no contradice el gráfico tornado, que ponía la prima de riesgo y la beta por delante. Cuánto pesa una hipótesis depende de *cuánto la dejamos variar*: en el tornado la prima iba de 4,2 a 5,8 % (±0,8 pp) y aquí su desviación es de 0,5 pp, mientras que el crecimiento varía ±1,2 pp. **Las probabilidades dependen de los rangos elegidos**, que son estimaciones propias: son una forma ordenada de expresar la incertidumbre, no una medida objetiva del riesgo.

---

## 5d. Calidad contable: Altman y Beneish (`src/calidad_contable.py`)

Dos modelos de **cribado**: señalan dónde mirar con más lupa, no prueban nada.

### Altman Z'' (¿riesgo de dificultades financieras?)

`Z'' = 6,56·X1 + 3,26·X2 + 6,72·X3 + 1,05·X4` (versión para empresas no industriales)

| X | Qué mide | Cálculo con Inditex |
|---|---|---|
| X1 | Liquidez | (activo corriente − pasivo corriente) / activo total |
| X2 | Rentabilidad acumulada | ganancias acumuladas / activo total (del estado de cambios en el patrimonio) |
| X3 | Rentabilidad operativa | EBIT / activo total |
| X4 | Colchón frente a deudas | patrimonio neto contable / pasivo total |

Zonas: **> 2,6 segura**, 1,1-2,6 gris, < 1,1 riesgo. **Resultado: 4,6 (2020) a 6,0 (2023); 5,7 en 2025**, más del doble del umbral. Es esperable: Inditex tiene caja neta, casi no tiene deuda financiera y es muy rentable.

### Beneish M-score (¿indicios de maquillaje de cuentas?)

Compara cada año con el anterior mediante ocho índices (DSRI, GMI, AQI, SGI, DEPI, SGAI, LVGI y TATA) y los combina en `M = −4,84 + 0,920·DSRI + 0,528·GMI + 0,404·AQI + 0,892·SGI + 0,115·DEPI − 0,172·SGAI + 4,679·TATA − 0,327·LVGI`. Si M supera **−1,78** (o −2,22, más estricto) la empresa se parece a las que manipularon sus cuentas.

**Resultado: M entre −2,74 y −2,95 en 2021-2025 (−2,79 en 2025): por debajo de los dos umbrales todos los años.**

- **El componente más importante es TATA** (devengos: beneficio que no se convierte en caja). Es negativo en Inditex (−0,08 a −0,12): genera más caja que beneficio contable, la mejor señal posible.
- **2021:** las ventas crecieron un 36 % tras la pandemia (SGI = 1,36, que suma 1,21 a M). Aun así M fue −2,88, porque otros índices compensaron: los deudores bajaron en relación con las ventas (DSRI 0,87) y TATA fue muy negativo.

**Adaptaciones a Inditex.** Inditex no desglosa gastos generales (SG&A), así que se usan los gastos de explotación. El derecho de uso de las tiendas se suma al inmovilizado material. El pasivo con coste incluye el arrendamiento a largo plazo. Los devengos son (resultado neto − flujo de explotación) / activo total.

**Control NIIF 16.** El flujo de explotación de Inditex no resta los pagos de alquiler (van a financiación), lo que **infla** la caja y favorece el TATA. Recalculando M restando esos pagos, sale entre **−2,49 y −2,70**: sigue por debajo de los dos umbrales. Es el resultado que conviene citar, porque no depende de ese sesgo.

**Límites.** El Altman se diseñó con empresas industriales de los años 60; el circulante negativo y los alquileres de Inditex deforman algunos ratios. El Beneish se calibró sobre empresas que luego fueron sancionadas, y empresas muy distintas de Inditex pueden dar falsos positivos o negativos. **Que Inditex salga tranquila era lo esperable**: el valor del ejercicio es mostrar que se sabe aplicar la herramienta e interpretar sus límites, no descubrir un fraude.

---

## 6. El resto del Excel y el Python

**Hoja Sensibilidad.** Recalcula el valor por acción con otros WACC y g (el escenario activo se mantiene). La celda central debe coincidir con el DCF; una celda de control lo comprueba.

**Hoja Resumen.** Muestra el resultado vivo del escenario activo y una **foto estática** de los tres escenarios (no se actualiza sola).

**Colores del Excel.** Azul = dato o hipótesis editable · negro = fórmula · verde = enlace a otra hoja · amarillo = decisión del autor.

| Script (`src/`) | Qué hace |
|---|---|
| `extract_statements.py` | Lee los PDF y extrae balance, resultados y flujos |
| `build_dataset.py` | Normaliza nombres de partidas, valida identidades contables y guarda `inditex_financials.csv` |
| `dcf_model.py` | **El mismo DCF en Python.** Comprueba el Excel al céntimo y se reutilizará en el Monte Carlo |
| `beta.py` | Regresión de la rentabilidad de Inditex frente a índices (Euro Stoxx 50, STOXX 600, IBEX) |
| `comparables.py` | Calcula qué valdría Inditex al múltiplo de H&M, Fast Retailing y Next, y dibuja el campo de fútbol |
| `montecarlo.py` | 20.000 simulaciones del DCF con las hipótesis inciertas; probabilidad de superar el precio |
| `calidad_contable.py` | Altman Z'' y Beneish M-score de Inditex, con control por NIIF 16 |
| `report_charts.py` | Gráficos del informe en español e inglés (sin título dentro de la imagen) |
| `build_report.py` | Genera los dos informes en PDF a partir de una plantilla HTML y Microsoft Edge sin ventana |
| `hipotesis_analisis.py` | Cambia una hipótesis cada vez (gráfico tornado), calcula paquetes de coste del capital y el DCF inverso |
| `build_excel.py` | Construye el Excel con fórmulas |

---

## 7. Lo que revela el modelo

- **Resultado (Base): 42,87 € frente a 54,38 €** de precio. Rango de escenarios: 32,73 € a 51,75 €.
- **El coste del capital pesa más que cualquier hipótesis operativa:** prima de riesgo (41-52 €) y beta (40-51 €) mueven más el valor que ±1 pp de crecimiento (40-46 €) o ±1,5 pp de margen (40-46 €).
- **DCF inverso:** con los flujos del escenario Base, el precio equivale a un coste del capital de ≈7,5 % (frente al 8,97 %), o a +3,1 pp de crecimiento de ventas cada año sobre el escenario Base; con las ventas y márgenes del consenso, el precio exigiría un coste del capital de ≈8,1 %.
- **Los comparables dan una historia parecida:** la mediana de los comparables (H&M, Next, Fast Retailing) da 42-45 € por acción, casi igual que el DCF Base (42,9 €), mientras que la media (50-54 €) se acerca al precio porque incluye a Fast Retailing.
- **Monte Carlo:** mediana 43,0 € (coherente con el DCF Base), 90 % de los casos entre 32,9 € y 57,3 €, y solo un **8,9 %** de probabilidad de que el valor supere el precio actual.
- **Calidad contable:** Altman Z'' de 4,6 a 6,0 (zona segura, > 2,6) y Beneish M de −2,7 a −2,9, por debajo de los umbrales de alerta también tras ajustar por NIIF 16. Sin señales de alarma, como era de esperar.
- **La diferencia con los analistas es sobre todo la tasa de descuento:** con ventas y márgenes del consenso y el coste del capital de este modelo, el valor es ≈47,8 €; con un coste del 7,3 % saldría ≈63 €.

---

## 8. Simplificaciones y límites

1. De 2026E solo se valora la segunda mitad como la mitad del flujo anual; ignora la estacionalidad de la caja.
2. Los arrendamientos se tratan como coste operativo («pre-NIIF 16»). Es una aproximación estándar, no la única.
3. Los tres escenarios y la prima de riesgo del 5,4 % (ponderación por regiones con medias supuestas) son estimaciones propias.
4. Las etiquetas del consenso («2027e») se interpretan como el ejercicio que termina en enero de 2027; no se ha podido confirmar con la fuente.
5. La beta depende del índice y de la frecuencia; el error típico es de ≈0,08-0,10.
6. El valor terminal supone más de la mitad del valor.
7. Un DCF produce un **rango**, no un número exacto.
8. Los comparables son solo tres empresas, con ejercicios fiscales distintos (no calendarizados) y países distintos. Las definiciones de EBITDA de Yahoo no coinciden exactamente con las de cada compañía.
9. Las probabilidades del Monte Carlo dependen de los rangos que se eligen para cada hipótesis (estimaciones propias); no son una medida objetiva del riesgo.
10. Altman y Beneish son herramientas de cribado diseñadas con otras empresas y otra época; sirven para señalar dónde mirar, no como prueba.

---

## 9. Cómo usar y modificar el modelo

**Cambiar de escenario:** hoja *Hipótesis*, celda B41 (1, 2 o 3).

**Cambiar una hipótesis:** edita solo las celdas **azules** de la hoja *Hipótesis*. Todo lo demás se recalcula.

**Regenerar el Excel desde Python:**
```
python src/build_excel.py [ruta_de_salida]
```
Después hay que abrirlo en Excel y guardarlo, para que se almacenen los valores calculados. Si el libro ya está abierto en Excel está bloqueado: pasa una ruta distinta.

**Comprobar que Excel y Python coinciden:**
```
python src/dcf_model.py
```
Los tres valores por acción (escenarios Bajo, Base y Alto) deben coincidir con los del Excel.

---

## 10. Glosario

| Término | Significado sencillo |
|---|---|
| **EBITDA** | Beneficio operativo antes de amortizaciones, intereses e impuestos |
| **EBIT** | EBITDA menos amortizaciones: beneficio de la actividad |
| **Amortización** | Reparto del coste de un activo (tiendas, tecnología) entre los años que se usa |
| **Capex** | Inversión en tiendas, logística y tecnología |
| **Circulante** | Existencias + deudores − acreedores: el dinero atrapado (o financiado) en el día a día |
| **FCFF** | Flujo de caja libre de la empresa: caja que genera tras pagar costes, impuestos e inversión |
| **WACC** | Coste medio del capital: la tasa de descuento |
| **CAPM** | Modelo que estima el coste de los recursos propios: rf + beta × ERP |
| **Beta** | Sensibilidad de la acción al mercado (1 = se mueve igual) |
| **ERP** | Prima de riesgo de mercado: rentabilidad extra que exige la bolsa frente a lo seguro |
| **Valor terminal** | Valor de todos los flujos después del último año proyectado |
| **EV (valor de la empresa)** | Valor del negocio operativo, antes de sumar la caja |
| **Equity (valor del capital)** | EV + caja neta: lo que pertenece a los accionistas |
| **NIIF 16** | Norma contable que lleva los alquileres al balance como deuda y a amortización |
| **DCF inverso** | Calcular qué hipótesis justifican el precio de mercado actual |
| **Tornado** | Gráfico que ordena las hipótesis por cuánto mueven el valor |
| **Múltiplo** | Cuántas veces se paga una magnitud de la empresa (beneficio, EBITDA) |
| **P/E (PER)** | Precio de la acción entre el beneficio por acción. «Forward» usa el beneficio esperado |
| **EV/EBITDA** | Valor de la empresa entre su EBITDA |
| **Comparables** | Empresas parecidas cuyos múltiplos sirven de referencia |
| **Campo de fútbol** | Gráfico que pone en una escala los rangos de valor de varios métodos |
| **Monte Carlo** | Repetir un cálculo miles de veces con valores al azar para ver la distribución de resultados |
| **Percentil** | El percentil 5 es el valor por debajo del cual queda el 5 % de los casos |
| **Altman Z'' / Beneish M** | Puntuaciones de cribado: riesgo financiero y posibles manipulaciones contables |
| **Devengos (TATA)** | Parte del beneficio contable que no se ha convertido en caja |
