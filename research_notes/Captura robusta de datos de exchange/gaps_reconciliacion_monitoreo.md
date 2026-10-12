# Gaps, reconciliación y monitoreo estadístico para captura automatizada en tiempo real

Nota de método: ~40 llamadas de búsqueda/fetch (oct 2026). Leídos completos: working paper "Aggregate Confusion in Crypto Market Data" (PDF SEC, texto extraído), documentación Binance (klines, aggTrades, data.binance.vision, WS API), Coinbase (heartbeat), Kraken (checksum), NIST e-Handbook (EWMA, CUSUM, atributos). Bloqueados (HTTP 403): Alexander & Dakos (Sussex/SSRN/ResearchGate/T&F), Vidal-Tomás (ScienceDirect), página INFORMS de Schwenkler et al. Lo que se afirma sobre ellos viene solo de abstracts/resultados de búsqueda y está marcado. Regla: "Hallazgos citados" = fuente; "Inferencias" = mías; "Gaps" = literatura delgada o no verificado.

---

## 1. ¿Cómo decidir si un intervalo silencioso es "cero real" o un gap de captura? (taxonomía, ledger, heartbeat, modelos de tasa)

### Takeaway
No encontré ningún test publicado y validado específicamente para distinguir "cero real" de "gap de captura" en cripto; lo documentado son (a) señales de continuidad provistas por el exchange (IDs de trade, sequence, heartbeat, checksum) que convierten gaps desconocidos en conocidos, y (b) modelos de proceso puntual (Poisson/Hawkes/ACD con ajuste diurno) que sirven para marcar silencios implausibles. La combinación es una inferencia de diseño, no un método con evidencia de validación.

### Cited Findings
**Señales de continuidad del lado de la fuente (convierten "gap desconocido" en "gap conocido")**
- Binance: los klines vienen con campos "Number of trades", "Taker buy base asset volume", "Quote asset volume" (campos 5, 7, 8, 9, 10) y se identifican por open time; la página no describe cómo se derivan los klines de los trades — [Binance Spot REST market data](https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints)
- Binance aggTrades expone aggregate tradeId (a), first tradeId (f) y last tradeId (l); trades con mismo taker order y precio se agregan. Un salto en `a` o en el rango f–l entre mensajes consecutivos es una ruptura de secuencia verificable — [Binance REST](https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints); [Binance WS streams](https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams)
- Binance diff depth: cada evento trae U (primer update ID) y u (último), "necesarios para verificar continuidad" — [Binance WS streams](https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams)
- Binance WS API: toda conexión es válida 24 h (desconexión esperada; evento `serverShutdown` antes), el servidor envía ping cada 20 s y desconecta si no hay pong en ~1 min; 300 intentos de conexión/5 min/IP; bans por 429/418 de 2 min a 3 días. Es decir, hay cortes de origen conocido y programado (fuente "source-side") y causas de desconexión inducidas por el cliente (recorder-side) — [Binance WS API general info](https://developers.binance.com/docs/binance-spot-api-docs/websocket-api/general-api-information)
- Coinbase: el canal `heartbeat` emite un mensaje por segundo y producto con `sequence` y `last_trade_id` "para verificar que no se perdieron mensajes"; el canal matches puede perder mensajes y se aconseja rastrear last_trade_id vía heartbeat y recuperar trades faltantes por REST; el canal level2 está diseñado para garantizar entrega — [Coinbase WebSocket channels](https://docs.cdp.coinbase.com/exchange/websocket-feed/channels)
- Kraken book v2: cada snapshot/update lleva `checksum` CRC32 sobre top 10 bids/asks; confirma que el libro local está "correctamente sincronizado"; "updates should always be processed in sequence"; la página no define el procedimiento ante mismatch — [Kraken book](https://docs.kraken.com/api/docs/websocket-v2/book); [Kraken checksum guide](https://docs.kraken.com/api/docs/guides/spot-ws-book-v2/)
- Binance data.binance.vision: archivos diarios (disponibles al día siguiente) y mensuales (primer lunes del mes siguiente), cada zip con archivo `.CHECKSUM` (SHA256); timestamps spot en microsegundos desde 2025-01-01; archivos "pueden ser reemplazados tras encontrar problemas" (actualizaciones 2022-04-21 aggTrades y 2022-08-08 klines "inconsistent data"); la página NO documenta gaps ni cómo se manejan períodos faltantes — [binance-public-data](https://github.com/binance/binance-public-data)
- Cambio de unidad de timestamp (ms→µs) es un ejemplo de "payload corrompido/malinterpretado" por el parser — [binance-public-data](https://github.com/binance/binance-public-data); [Binance WS API](https://developers.binance.com/docs/binance-spot-api-docs/websocket-api/general-api-information) (parámetro timeUnit=MICROSECOND)

**Modelos de tasa de llegada**
- Hawkes en finanzas: revisión de Bacry, Mastromatteo, Muzy (procesos puntuales multivariados; aplicaciones a volatilidad desde transacciones, estabilidad, ejecución, libro completo) — [arXiv:1502.04592](https://arxiv.org/abs/1502.04592) (solo abstract leído)
- Características estilizadas citadas en un capítulo: llegadas irregulares, más actividad cerca de apertura/cierre, clustering, auto/cross-excitación; ARIMA/GARCH de intervalo fijo ajustan mal — [Viens & Baron, Hawkes processes HF](https://www.stt.msu.edu/~viens/publications/11_hawkes.pdf) (vía resumen de búsqueda, no leído completo)
- Sornette, Wehrli, Wheatley (2020): el branching ratio de Hawkes varía con la hora; estimaciones sobre ventanas de días con baseline constante pueden llegar a 0.3 → la elección del baseline importa — [SFI 20-39](https://www.sfi.ch/en/publications/n-20-39-scale-time-and-asset-dependence-of-hawkes-process-estimates-on-high-frequency-price-changes) (resumen de búsqueda)
- Hawkes aplicado a trades de BTC en Binance: [arXiv:2006.02460](https://arxiv.org/pdf/2006.02460), [arXiv:2402.04740](https://arxiv.org/pdf/2402.04740) (julio 2022, BTC-USD/ETH-USD), [arXiv:2401.09361](https://arxiv.org/html/2401.09361v3); muestras cortas (en un caso ~media hora) → ilustrativas, no validación de detección de silencio. Índice de reflexividad Bitcoin: [IDEAS EJF 28(7)](https://ideas.repec.org/a/taf/eurjfi/v28y2022i7p784-799.html)
- Modelos de duración ACD (Engle & Russell 1998, Econometrica 66(5):1127–1162) con ajuste diurno — [paquete ACDm, referencia a la fuente](https://cran.r-universe.dev/ACDm/doc/manual.html) (no leí el paper original)
- Brownlees & Gallo (2006, CSDA 51(4):2232–2245): en un ACD, ticks erróneos acortan duraciones y alteran autocorrelación; coeficientes y diagnósticos "considerablemente alterados" sin limpieza → datos defectuosos sesgan directamente los modelos de llegada que se usarían para detectar silencios — [RePEc/Florence WP](https://econpapers.repec.org/paper/fireconom/wp2006_5f03.htm)

**Cero real vs. faltante en datos de mercado (literatura general)**
- Una búsqueda no halló un test formal publicado para distinguir intervalos sin trades de observaciones faltantes; sí documenta: tratar intervalos vacíos como retorno cero o como no disponible cambia volatilidad/saltos (subestima volatilidad, marca retornos pequeños como saltos); duraciones cero pueden ser artefactos de timestamps idénticos; splits de transacciones causan ~63% de ceros en una muestra de DJIA; vendors a veces omiten la barra cuando no hubo trades en vez de rellenar con cero — resultados agregados en la búsqueda: [Hawkes cojumps](https://arxiv.org/pdf/1301.6141), [foro EODHD](https://forum.eodhd.com/t/missing-data-due-to-no-transaction-occurs/926) (foro; baja calidad), [gfk-cfs 10_19](https://gfk-cfs.de/media//10_19.pdf). Cifras de 63% no verificadas en la fuente primaria.
- Marco de datos faltantes: Rubin (1976), Biometrika 63(3):581–592, DOI 10.1093/biomet/63.3.581: condiciones (missing-at-random, observed-at-random, parámetros distintos) bajo las cuales se puede ignorar el mecanismo de faltantes — [Harvard DASH](https://dash.harvard.edu/entities/publication/73120378-8764-6bd4-e053-0100007fdf3b); [ETS 1975](https://www.ets.org/research/policy_research_reports/publications/report/1975/hrri.html). La atribución literal de MCAR/MAR/MNAR a ese paper no pude confirmarla.

**SPC aplicable a conteos/tasas de gaps**
- NIST: gráficos de atributos c (conteo de no-conformidades) y u (por unidad) — [NIST 6.3.3](https://itl.nist.gov/div898/handbook/pmc/section3/pmc33.htm) (límites y supuesto Poisson no aparecen en lo recuperado)
- EWMA: EWMA_t = λY_t + (1−λ)EWMA_{t−1}; λ=0.2–0.3 sugerido (Hunter 1986), k=3 o tablas de Lucas & Saccucci (1990); supone independencia y normalidad; λ=1 equivale a Shewhart; apto para derivas pequeñas; requiere datos históricos en control (fase 1) — [NIST EWMA](https://itl.nist.gov/div898/handbook/pmc/section3/pmc324.htm)
- CUSUM: mejor que Shewhart para cambios ≲2σ; forma tabular S_hi/S_lo reiniciadas a cero; k=δσ/2, h≈4–5σ de regla práctica — [NIST CUSUM](https://itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm)

### Inferences
- Taxonomía operativa propuesta (mía): (1) gap conocido = ruptura de ID/sequence/heartbeat faltante; (2) gap desconocido = solo detectable estadísticamente (sin IDs, p.ej. streams sin secuencia); (3) silencio de fuente (mantenimiento, halt, exchange sin matching) vs. (4) outage del recorder (proceso caído, desconexión no recuperada); (5) pérdida parcial (mensajes sueltos); (6) duplicados (replay tras reconexión; deduplicables por trade ID); (7) out-of-order; (8) late arrival; (9) payload corrupto (unidad errónea, campo nulo, checksum mismatch).
- Un "cero real" solo es afirmable si el recorder estuvo vivo y suscrito en todo el intervalo (ledger de cobertura + heartbeat contiguo) Y la continuidad de IDs entre el último trade antes y el primero después es contigua (ID_siguiente = ID_último+1). Esa es la prueba más fuerte, porque es determinista; los p-values de tasa son solo para streams sin IDs.
- Para el test estadístico: condicionar al estrato hora-del-día/día-de-semana, calcular P(N=0 | λ̂(t)) = exp(−∫λ) bajo Poisson no homogéneo (conservador porque el clustering de Hawkes fatigaría la cola: con auto-excitación hay más silencios largos que Poisson, así que un Poisson sobre-alarma); preferible usar la distribución empírica de duraciones por estrato y calibrar el umbral con los gaps ya confirmados por IDs (etiquetas "verdad" gratuitas). Múltiples contrastes (muchos símbolos × intervalos) requieren control de falsos descubrimientos.
- El ledger debe ser de intervalos [inicio, fin) con estado (CUBIERTO / NO_CUBIERTO / DESCONOCIDO) y razón; "sin filas" nunca debe significar cobertura.

### Gaps
- No hallé estudios que midan tasas de falsos positivos/negativos de un detector de "silencio implausible" en cripto. Tampoco hay validación publicada de Hawkes como detector de gaps.
- No leí completos Bacry et al., Engle & Russell ni Sornette et al.; solo abstracts/resúmenes.
- La documentación Binance sobre gestión de order book (reglas exactas de resincronización por U/u) no se recuperó (página truncada). Tampoco hay docs de Kraken sobre acción ante checksum mismatch.
- Docs Tardis.dev sobre calidad/gaps: el índice no contenía detalles; no verificado.

---

## 2. Registro de conexión, marcado y cuarentena, backfill y procedencia

### Takeaway
Las fuentes primarias respaldan que existen mecanismos de detección (secuencia, heartbeat, REST de recuperación) y recomiendan recuperar vía REST lo perdido; las políticas de "flag, never fill", etiquetado de procedencia y esquema de metadata no están respaldadas por literatura específica y son recomendaciones de diseño (inferencias).

### Cited Findings
- Coinbase: recuperar trades faltantes por REST usando last_trade_id del heartbeat; para level3, bufferizar mensajes, tomar snapshot REST y descartar los de sequence ≤ snapshot — [Coinbase channels](https://docs.cdp.coinbase.com/exchange/websocket-feed/channels)
- Binance: REST aggTrades admite `fromId`/`startTime`/`endTime` y historicalTrades `fromId`, o sea, backfill posible por ID — [Binance REST](https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints)
- Binance Vision son archivos oficiales reemplazables (versión corregida posible) → un backfill desde archivo debe registrar fecha de descarga/CHECKSUM — [binance-public-data](https://github.com/binance/binance-public-data)
- Patrón de bounding de la ventana perdida: guardar último slot visto antes de desconectar y comparar con el primero tras reconectar (ejemplo Solana, no cripto-CEX) — [Helius reconnects](https://www.helius.dev/docs/parsed-streams/guides/handling-reconnects)
- Un post de blog señala que los endpoints WS estándar no emiten alertas de datos faltantes, el recorder debe verificar continuidad por sí mismo — [DEV Community](https://dev.to/kels180/fix-websocket-tick-data-gaps-for-crypto-market-feeds-production-python-implementation-nb7) (fuente débil, blog)
- Efecto de tratar intervalos vacíos como cero vs. NA sobre volatilidad/saltos (ver sección 1) respalda "no rellenar con ceros" — [arXiv 1301.6141 vía búsqueda](https://arxiv.org/pdf/1301.6141)

### Inferences
- Registro de conexión como metadata (por conexión): connect/disconnect/reconnect timestamps (reloj local y, si existe, del servidor), mensajes de ack de suscripción, último ID/sequence visto, motivo del cierre (24 h programado, ping timeout, error de red, ban 418/429, `serverShutdown`), contador de reintentos y backoff. Los motivos de la doc Binance (24 h, 20 s ping, 300 conn/5 min) dan el vocabulario de causas esperadas, útiles para clasificar un outage como "benigno programado" vs. anómalo.
- Política: marcar (flag) y poner en cuarentena el intervalo; nunca forward-fill ni interpolar trades (un trade es un evento discreto, no una muestra de un proceso continuo; rellenar crea trades inexistentes, volumen cero falso y retornos cero que sesgan volatilidad a la baja — consistente con el hallazgo de subestimación de volatilidad citado arriba). Para agregados tipo OHLC, un intervalo con cobertura parcial debe llevar su % de cobertura, no un valor "completado".
- Backfill: cada registro lleva `provenance` (live | rest_backfill | vendor_archive | exchange_archive), timestamp de captura, fuente exacta/versión/checksum, y estado de verificación; los registros backfilleados se mantienen separables y no se mezclan silenciosamente; si hay disparidad live vs. backfill, ambos se conservan.
- Duplicados tras reconexión: deduplicar por (símbolo, trade ID); late arrival/out-of-order: conservar tiempo de recepción además de tiempo de evento.

### Gaps
- No encontré literatura revisada por pares sobre políticas de cuarentena/etiquetado de procedencia específicas de datos de mercado cripto; esto es práctica de ingeniería sin fuente académica recuperada.
- Límites de retención de REST (cuánto atrás se puede backfillear) no verificados aquí.

---

## 3. Diseños de reconciliación y matriz diagnóstica (conteos, volumen/notional, hash, multi-fuente)

### Takeaway
Existen campos oficiales utilizables como objetivos de reconciliación (number of trades, volume, quote volume, taker buy volume en klines; CHECKSUM por archivo; checksums de libro), pero no encontré tolerancias publicadas para comparar trades propios con klines oficiales; las tolerancias deben calibrarse empíricamente. La evidencia cuantificada de discrepancia entre agregadores es fuerte (sección 5).

### Cited Findings
- Campos de kline utilizables como control: Volume, Quote asset volume, Number of trades, Taker buy base volume, Taker buy quote volume, más OHLC — [Binance REST](https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints); [binance-public-data](https://github.com/binance/binance-public-data)
- Binance aggTrades colapsa trades individuales: por lo tanto "number of trades" del kline corresponde a trades (no a filas aggTrade) según la semántica de f/l; la doc no lo afirma explícitamente para klines — [Binance REST](https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints) (la equivalencia es inferencia)
- Hash por partición: data.binance.vision publica SHA256 por zip (`.CHECKSUM`), permite verificar integridad de la descarga, no completitud de lo que Binance publicó — [binance-public-data](https://github.com/binance/binance-public-data)
- Kraken/Coinbase: checksum CRC32 top-10 niveles (Kraken) y secuencia (Coinbase) como verificación de sincronización de libro — [Kraken](https://docs.kraken.com/api/docs/guides/spot-ws-book-v2/); [Coinbase](https://docs.cdp.coinbase.com/exchange/websocket-feed/channels)
- Archivos oficiales cambian: correcciones 2022 (klines "inconsistent data") → la reconciliación contra archivo debe versionarse — [binance-public-data](https://github.com/binance/binance-public-data)
- Cleaning-effects: datos erróneos distorsionan modelos aguas abajo — [Brownlees & Gallo](https://econpapers.repec.org/paper/fireconom/wp2006_5f03.htm)

### Inferences (matriz diagnóstica propuesta; ninguna celda tiene tolerancia publicada)
| Chequeo | Detecta bien | Detecta mal / ciega |
|---|---|---|
| Continuidad de trade ID / aggTrade a,f,l | pérdida parcial, outage con huecos de ID, duplicados, out-of-order | trades que el exchange nunca emitió; fallo total de suscripción con IDs que continúan tras backfill |
| Σ qty recorder vs kline Volume (por minuto) | pérdida parcial, outage, payload con qty corrupto | compensación de errores (duplicados + pérdidas); trades con qty correcta pero timestamp mal asignado a otro minuto (solo se ve en bordes) |
| Conteo de trades vs kline "number of trades" | pérdida y duplicados (si el conteo es por trade) | diferencias por agregación aggTrade vs trade |
| Σ quote qty / notional vs Quote asset volume | corrupción de precio o cantidad | ídem |
| Taker buy volume vs Σ qty con isBuyerMaker=false | corrupción del flag lado-agresor (invierte signo sin cambiar volumen total) | nada sobre gaps si el volumen total reconcilia |
| OHLC recalculado vs kline | pérdida de trades extremos (high/low), trades de apertura/cierre | gaps en el interior que no tocan extremos |
| Hash/CHECKSUM de partición | corrupción en transferencia/almacenamiento; deriva entre copias | completitud de la fuente |
- Los chequeos de volumen/conteo se hacen por intervalo; benignos esperables: diferencias de redondeo decimal, diferencia de frontera de minuto por reloj, correcciones post-hoc del archivo oficial, desfase entre REST kline y stream. Tolerancia sugerida: exactitud (diferencia cero a precisión decimal) debería ser el objetivo para spot de un único exchange, y toda diferencia no nula se clasifica por patrón; esto es hipótesis a validar con muestras, no estándar publicado.
- Interpretación de desacuerdos multi-fuente (dos recorders, vendor vs propio, live vs archivo): clasificar por patrón: A tiene un subconjunto de B (pérdida en A), conjuntos disjuntos por tiempo (outages distintos), mismos IDs con distinto valor (corrupción/versión), cluster temporal tras reconexiones (storms), diferencia sistemática de escala (unidad/decimales), desacuerdo que escala con volumen (saturación/backpressure del recorder). Union de ambos recorders reduce pérdida solo si fallos son independientes (no en eventos del lado de la fuente).
- Cadencia: continuidad de IDs en línea; reconciliación de volumen/conteo cuando la vela oficial se cierra (REST) y de nuevo contra archivo diario/mensual oficial (disponible día+1 / primer lunes del mes siguiente) para detectar revisiones.

### Gaps
- No hallé tolerancias documentadas por exchanges ni por vendors para reconciliar trades vs klines. No hay documentación oficial de Binance sobre si el "number of trades" del kline cuenta trades o aggTrades.
- No pude acceder a documentación de data-quality reports de Kaiko/CoinAPI/Tardis para citar prácticas de vendors.

---

## 4. Monitoreo estadístico (SPC), patrones de fallo y medición de sesgo por gaps

### Takeaway
Las herramientas SPC (Shewhart/c-u, EWMA, CUSUM) están bien documentadas por NIST, pero no hay literatura recuperada que las aplique a recorders de mercado; sobre el sesgo inducido por gaps en datos cripto no encontré estudios cuantificados. El marco de referencia es la teoría de datos faltantes (Rubin).

### Cited Findings
- Parámetros y límites de EWMA/CUSUM/c/u: ver sección 1 — [NIST EWMA](https://itl.nist.gov/div898/handbook/pmc/section3/pmc324.htm); [NIST CUSUM](https://itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm); [NIST atributos](https://itl.nist.gov/div898/handbook/pmc/section3/pmc33.htm)
- El supuesto de independencia/normalidad en EWMA y la necesidad de Fase 1 con datos en control — [NIST EWMA](https://itl.nist.gov/div898/handbook/pmc/section3/pmc324.htm)
- Heterogeneidad temporal en calidad de datos agregados: el "Aggregate Confusion Index" (fracción diaria de datos descartados) varió de 4.8% a 22% y estuvo generalmente más bajo desde 2023; se correlaciona con retorno/volatilidad de mercado y actividad on-chain — [Schwenkler, Shah, Yang (PDF SEC)](https://www.sec.gov/file/cryptodata-sec-102525)
- En ese mismo estudio, las discrepancias entre vendors son más frecuentes para monedas grandes (listadas en muchos exchanges) que para pequeñas, y se concentran cuando el precio fluctúa cerca de su valor medio — [Schwenkler et al.](https://www.sec.gov/file/cryptodata-sec-102525)
- Rubin 1976 como marco: ignorar el mecanismo de faltantes solo es válido bajo condiciones específicas — [Harvard DASH](https://dash.harvard.edu/entities/publication/73120378-8764-6bd4-e053-0100007fdf3b)
- Sesgo por limpieza/ruido sobre estimación de modelos de duración — [Brownlees & Gallo](https://econpapers.repec.org/paper/fireconom/wp2006_5f03.htm)

### Inferences
- Monitoreo recomendado: serie por hora de (tasa de gaps conocidos, latencia recepción–evento, % mensajes duplicados, retraso del heartbeat) → c/u-chart para conteos de gaps, EWMA (λ≈0.2) para deriva de latencia, CUSUM para cambio pequeño y sostenido en la tasa de desconexiones. Cuidado: los conteos de gaps están autocorrelacionados y con estacionalidad; los supuestos NIST (iid, normal) se violan, por lo que los límites deben calibrarse con estratos o con datos históricos limpios.
- Análisis de patrones de fallo: tabular incidencia de gaps vs. deciles de volatilidad realizada y volumen, hora del día, ventanas de mantenimiento, y "tormentas de reconexión" (varios reintentos en poco tiempo, vinculados a límites de conexión de Binance). Lo esperable (hipótesis): los recorders fallan más en picos de actividad (backpressure) → los gaps no son MCAR sino MNAR o MAR dependiente de volumen/volatilidad.
- Medición del sesgo: (i) comparar distribución de volatilidad/volumen de intervalos con gap vs. sin gap; (ii) modelo de propensión de faltante (logit de gap sobre volumen, volatilidad, hora) y ponderación inversa; (iii) métricas ponderadas por cobertura; (iv) análisis de sensibilidad: recalcular estadísticos del backtest bajo escenarios de relleno extremo (cero / cota superior) y reportar rango; (v) reporte estratificado por régimen.

### Gaps
- No hallé estudios cuantificados de sesgo por gaps de captura en cripto (ni en tick data de acciones) con deciles de volatilidad; literatura delgada. El único análisis cuantificado cercano es el impacto de discrepancias entre vendors sobre retornos y portafolios (sección 5), que no es lo mismo que gaps.
- No hay referencias recuperadas de change-point detection ni de anomaly detection sobre distribuciones de latencia de recorders.

---

## 5. Calidad, puertas de liberación y aceptación; evidencia de discrepancias entre vendors y exchanges

### Takeaway
La evidencia cuantificada más sólida es Schwenkler, Shah & Yang (Management Science, 2025): discrepancias muy grandes entre 8 agregadores, sobre todo en volumen. Alexander & Dakos (2020) y Makarov & Schoar (2020) son relevantes pero solo pude verificar sus abstracts vía terceros; ninguno cuantifica completitud de recorders.

### Cited Findings
**Schwenkler, Shah, Yang — "Aggregate Confusion in Crypto Market Data"** (Management Science, DOI [10.1287/mnsc.2025.00611](https://pubsonline.informs.org/doi/10.1287/mnsc.2025.00611); texto leído en [working paper PDF](https://www.sec.gov/file/cryptodata-sec-102525))
- Ocho proveedores (CoinCap, CoinGecko, CoinMarketCap, Coinpaprika, CryptoCompare, Live Coin Watch, Messari, Santiment), nov 2018 – oct 2024; apéndice con 20 vendors.
- Hasta 21% de las monedas de un proveedor con cambios de ID no divulgados (Coinpaprika; 4% Messari); un mismo ID para monedas distintas en 16% de la muestra de CoinGecko.
- De 3,379,576 entradas proveedor-moneda-día de volumen global, solo 30.4% caen en ±5% de la mediana entre proveedores; en casi 70% de las instancias el volumen diario se desvía >5% de la mediana; correlación de volúmenes tan baja como 27% (CryptoCompare vs. varios).
- Divergencias de precio de cierre de hasta factores 10^6 (Coinpaprika) o 10^−9 (CoinGecko, CoinCap) respecto a la mediana.
- Retornos y volatilidades calculados con distintos proveedores están "efectivamente incorrelacionados" sin filtrar outliers; con filtrado de 1% extremo las correlaciones suben a 61% (retornos) y 50% (volatilidades históricas).
- Portafolios: carteras long-short pueden tener solo 11–14% de solapamiento con la basada en mediana; diferencias de rendimiento de hasta 2.8%/año (mercado, Live Coin Watch), 10.8%/año (tamaño, CoinGecko), 9.8%/año (momentum).
- Tasa de descarte promedio (algoritmo de agregación) y nota: CoinGecko 26.8% (C), Messari 12.6% (B+), Live Coin Watch 7.7% (A−), Coinpaprika 4.5% (A), CoinMarketCap 3.5% (A), Santiment 3.3% (A) (CoinCap y CryptoCompare: ver figura 13 del PDF, no extraído aquí).
- Volumen entre exchanges de cola pesada (ley de potencias con varianza infinita); los 10 mayores exchanges ≈55% del volumen global. Selección de exchanges por proveedor explica gran parte de la discrepancia; el modelo estructural estima tasas de mislabeling de 0.1% (CoinGecko) a 0.7% (Live Coin Watch) y mismatch de 0.3% a 1% (CryptoCompare); el control de wash trading no resulta un factor significativo en su estimación.
- Algoritmo de agregación con tolerancias (tol2=10% en market-cap clustering, tol3=2% en close price) descarta 8.2% + 1.9% de instancias en etapas 2 y 3 y deja 72,830 (2.6%) entradas finales tras otro filtro (ver PDF, líneas ~1175–1185); el grading usa la tasa de descarte.

**Alexander & Dakos** — Quantitative Finance 20(2):173–188 (2020); SSRN [3382828](https://doi.org/10.2139/ssrn.3382828) (bloqueado; abstracts vía búsqueda)
- Menos de la mitad de los estudios sobre cripto publicados desde principios de 2017 usan datos correctos — [Sussex figshare (registro)](https://sussex.figshare.com/articles/journal_contribution/A_critical_investigation_of_cryptocurrency_data_and_analysis/23470910)
- Betas de mercado de bitcoin varían con la fuente/índice; time-stamping incorrecto prolongado en algunos sitios de ranking que afecta CRIX; datos de algunos exchanges requieren ajuste por inestabilidad de tether; recomiendan datos de exchanges con negociación real o bases con una sola divisa fiat; observan que CoinMarketCap usa volumen inferido (según papers citantes, no verificado en el original) — resumen de búsqueda; [resultado de búsqueda](https://doi.org/10.2139/ssrn.3382828)
- Contrapunto: Vidal-Tomás (2022) sostiene que CoinMarketCap es fiable para investigación — [ScienceDirect S1057521922000369](https://www.sciencedirect.com/science/article/abs/pii/S1057521922000369) (abstract no accesible; vía búsqueda)

**Makarov & Schoar** — "Trading and Arbitrage in Cryptocurrency Markets", J. Financial Economics 135(2):293–319 (2020), datos trade-level de 34 exchanges en 19 países
- Precios de bitcoin divergen entre exchanges por horas, a veces días/semanas; las desviaciones son mucho mayores entre países que dentro de un país; componente común explica ~80% de los retornos (85% en WP) — [LSE Research Online](https://researchonline.lse.ac.uk/id/eprint/118909); [Harvard Law corpgov](https://corpgov.law.harvard.edu/2019/09/21/trading-and-arbitrage-in-cryptocurrency-markets)
- Relevancia: desacuerdo entre exchanges no es automáticamente "error de datos"; puede ser divergencia económica real, por lo que la reconciliación multi-exchange de precios necesita tolerancias que no confundan arbitraje con corrupción (inferencia).

**Volumen inflado (contexto)**
- Bitwise (2019, 81 exchanges, 4 días) afirmó que ~95% del volumen reportado era cuestionable; la metodología fue disputada; Messari lanzó "Real 10" — [FXStreet](https://www.fxstreet.com/cryptocurrencies/news/only-10-out-of-85-cryptocurrency-exchanges-do-not-lie-about-their-trading-volumes-bitwise-201905271406); [The Block](https://theblock.co/news/ecosystems/2019-03-26-messari-rolls-out-real-10-volume-metrics-after-study-reveals-95-of-bitcoin-trading-volumes-are-fake-17249). Fuentes secundarias de prensa.

### Inferences
- Para reconciliación contra "oficial", usar el propio exchange (API/archivo del mismo venue) y no agregadores: la evidencia muestra que los agregadores difieren entre sí por mucho más que cualquier tolerancia razonable de un recorder, sobre todo en volumen.
- Escala de lo que no cuantifica ningún estudio: los rangos de Schwenkler et al. miden discrepancia entre agregadores (selección de exchange, mislabeling), no pérdida de un recorder propio; no deben usarse como línea base de tolerancia para un recorder de un solo venue.
- Puertas de liberación ("apto para backtest") propuestas (mías, sin respaldo normativo): cobertura mínima por intervalo y por estrato (volatilidad/volumen), 0 gaps desconocidos no resueltos en el período, reconciliación de volumen/conteo contra archivo oficial dentro de tolerancia calibrada, ausencia de dups/out-of-order sin resolver, informe de sensibilidad. Aceptación: muestreo estratificado (incluyendo días de alta volatilidad y de mantenimiento, no solo aleatorio) comparado con archivos oficiales versionados; con el esquema de metadata por intervalo: cobertura %, lista de gaps (con causa y método de detección), fuente/procedencia, estado de verificación, versión de archivo oficial contrastado, nivel de confianza.

### Gaps
- No pude leer el texto completo de Alexander & Dakos ni de Vidal-Tomás (403); sus cifras exactas no están verificadas. No identifiqué otros estudios revisados por pares que comparen completitud de recorders propios vs. archivo oficial; la literatura sobre completitud de recorders (vs. consistencia de agregadores) parece delgada.
- No hay estándar publicado de "fit for backtest" para datos cripto; los criterios arriba son diseño propio.
- No verifiqué literatura sobre Kaiko/CoinAPI/Amberdata (reportes de calidad de vendors) ni estudios de wash trading (Cong et al., Aloosh & Li, Amiram et al.) más allá de su mención en Schwenkler et al.
