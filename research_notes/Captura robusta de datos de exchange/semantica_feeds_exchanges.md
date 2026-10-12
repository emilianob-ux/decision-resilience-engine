# Semántica de entrega de datos y modos de fallo documentados de feeds de exchanges cripto (Binance primero; comparación con Coinbase, Kraken, OKX, Bybit) para un grabador de análisis/backtesting

Fecha de recuperación de todas las fuentes: 2026-10-12. Nota metodológica: las páginas se leyeron mediante un extractor que resume con un modelo pequeño; varias páginas del portal nuevo developers.binance.com (SPA) devolvieron solo la página de inicio, por lo que algunos detalles de streams de futuros (formato exacto de payload de aggTrade/kline/bookTicker de futuros, página de opciones) NO se pudieron leer y se listan en Gaps. Los datos de cambios (changelogs) se leyeron parcialmente (ver Gaps). Los GitHub issues se consultaron por la API pública de búsqueda de GitHub y por lectura de cada issue.

## 1. Tipos de stream de Binance y qué garantías ofrece cada uno (spot, USD-M, COIN-M, opciones)

### Takeaway
Binance documenta ids secuenciales útiles solo en trade (`t`), aggTrade (`a`, `f`, `l`) y depth diff (`U`, `u`, `pu` en futuros). Kline, bookTicker parcial/ticker, mark price y liquidaciones no tienen identificador de continuidad (o, en liquidaciones, el stream descarta eventos por diseño), así que la completitud no se puede probar solo con el stream. La documentación no promete entrega garantizada, ni orden entre streams, ni ausencia de duplicados.

### Cited Findings
- Spot: `<symbol>@trade` (real-time; campos trade id `t`, precio, cantidad, `T`, `m`), `<symbol>@aggTrade` (real-time; `a`, `f`, `l`), `<symbol>@kline_<interval>` (1000 ms para `1s`, 2000 ms para el resto; flag de cierre `x`), `<symbol>@bookTicker` (real-time; update id `u`), `<symbol>@depth<5|10|20>[@100ms]` (snapshot parcial con `lastUpdateId`; 1000 ms o 100 ms), `<symbol>@depth[@100ms]` (diff con `E`, `U`, `u`, `b`, `a`) — [Spot web-socket-streams.md](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/web-socket-streams.md)
- Spot aggTrade: "push trade information that is aggregated for a single taker order"; el campo `M` de trade/aggTrade está documentado solo como "Ignore" — [Spot web-socket-streams.md](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/web-socket-streams.md)
- Spot REST: "Trades that fill at the time, from the same taker order, with the same price will have the quantity aggregated" — [Spot rest-api.md](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/rest-api.md)
- Spot kline: variante UTC+8 (`<symbol>@kline_<interval>@+08:00`); los timestamps del payload siguen siendo Unix UTC — [Spot web-socket-streams.md](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/web-socket-streams.md)
- La página de streams de spot no hace promesas explícitas de entrega, ni sobre orden entre streams, ni sobre duplicados (el extractor lo confirma: "makes no explicit delivery guarantees"); el formato de combined stream es `{"stream":..., "data":...}` sin mención a orden de eventos — [Spot web-socket-streams.md](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/web-socket-streams.md)
- USD-M: streams listados: `!bookTicker`, `@depth@{speed}`, `@bookTicker`, `@depth{levels}@{speed}`, `@rpiDepth@500ms`, aggTrade, liquidaciones (individual y todo el mercado), mini/ticker, composite index, continuous kline, contract info, kline, mark price (individual y todo el mercado), multi-assets index, trading session — [USD-M websocket market streams](https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams)
- USD-M: desde el changelog de 2026-03-05 hay rutas separadas `/public` (alta frecuencia: depth, bookTicker), `/market` (datos regulares: p.ej. `@markPrice`) y `/private`; una conexión sin ruta solo recibe datos de Public (p. ej. `@depth` funciona, `@markPrice` no). El endpoint legacy se retiró el 2026-04-23 (changelog 2026-04-02) — [Connect USD-M](https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Connect); [Change Log derivados](https://developers.binance.com/docs/derivatives/change-log)
- USD-M mark price: `@markPrice` (3000 ms) o `@markPrice@1s` (1000 ms); payload incluye mark, index, estimated settle, funding rate y next funding time (resumen de resultado de búsqueda de la página oficial) — [Mark Price Stream USD-M](https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Mark-Price-Stream)
- USD-M liquidaciones `<symbol>@forceOrder` (1000 ms): "For each symbol, only the latest one liquidation order within 1000ms will be pushed as the snapshot. If no liquidation happens in the interval of 1000ms, no stream will be pushed" (cita vía resultado de búsqueda). El changelog de derivados registra el 2026-04-10 que el stream pasa de "latest" a "largest" liquidación en 1000 ms — [Liquidation Order Streams USD-M](https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Liquidation-Order-Streams); [Change Log derivados](https://developers.binance.com/docs/derivatives/change-log)
- COIN-M: aggTrade cada 100 ms; `!forceOrder@arr` un snapshot por símbolo por 1000 ms; depth diff 100 ms/500 ms; streams por par (`ps`, p. ej. BTCUSD); tras la integración CM/UM (changelog 2026-06-10, efectiva 2026-06-30) algunos streams "all market" cubren UM y CM y el payload incluye `st` (1=UM, 2=CM) — [COIN-M websocket market streams](https://developers.binance.com/docs/derivatives/coin-margined-futures/websocket-market-streams); [Change Log derivados](https://developers.binance.com/docs/derivatives/change-log)
- Cambios de semántica en futuros: 2025-11-18 las órdenes RPI se excluyen de depth y bookTicker; 2025-11-25 nuevo `@rpiDepth@500ms`; 2025-12-29 aggTrade añade campo `nq` y las trades RPI no se agregan — [Change Log derivados](https://developers.binance.com/docs/derivatives/change-log)
- Opciones: las páginas de streams de opciones no se pudieron leer (devolvieron la página de inicio). Un resultado de búsqueda indica que los docs antiguos de opciones usan ping 5 min / pong 15 min, diferente de futuros — [resultado de búsqueda sobre Connect](https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Connect) (dato secundario, no verificado en la página de opciones)
- Spot: nuevo stream `<symbol>@blockTrade` (2026-05-11) y `<symbol>@referencePrice` (2026-03-09); `!ticker@arr` retirado el 2026-03-26 — [Spot CHANGELOG](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/CHANGELOG.md)
- Binance retiró `!bookTicker` de spot (anunciado 2022-09-30, noviembre 2022) a favor de `<symbol>@bookTicker` — [Spot CHANGELOG (parte antigua)](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/CHANGELOG.md)
- Auditoría de datos spot aggTrade del 2022-04-12: "missing trades were recovered, and duplicate records were marked invalid (price and quantity set to '0', trade IDs set to -1)" (parafraseo del extractor) — [Spot CHANGELOG](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/CHANGELOG.md)
- Corrección 2022-05-23 de overflow de cantidades en depth (REST y streams `@depth`): se limitan al máximo en lugar de volverse negativas — [Spot CHANGELOG](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/CHANGELOG.md)
- Datos de un tercero (Tardis) sobre futuros: depth se registró a 100 ms hasta 2020-01-07 y luego `depth@0ms`; liquidaciones: "Only the latest liquidation per symbol is published in each 1000ms window, so intermediate liquidations are not captured"; `premiumIndex`, `openInterest`, ratios long/short son generados por polling REST y no provienen de WS — [Tardis Binance Futures](https://docs.tardis.dev/historical-data-details/binance-futures)

### Inferences
- Prueba de completitud por stream (inferencia a partir de los campos documentados):
  - trade: ids `t` consecutivos por símbolo permiten detectar huecos (un salto implica pérdida o filtrado); aggTrade: `a` consecutivo y rangos `f`..`l` contiguos entre eventos permiten detectar huecos y verificar contra REST. Es inferencia: la doc dice qué son los campos, pero no declara explícitamente que sean contiguos en el stream.
  - depth diff: `U`/`u` (spot) y `pu` (futuros) dan prueba de continuidad entre diffs (ver sección 2); el nivel de profundidad inicial solo se prueba con snapshot REST.
  - depth parcial (`depth5/10/20`), kline, bookTicker (su `u` es id de actualización de libro, no probado como contiguo en lo leído), mark price, ticker: sin prueba de completitud por el stream. Para klines la única verdad es REST (sección 7).
  - forceOrder: por diseño no completo (solo un evento por ventana de 1000 ms y por símbolo); no existe prueba de completitud posible desde WS.
- Ningún stream tiene "exactly-once" documentado; el diseño de grabación debe asumir at-most-once con posibles reordenamientos entre streams distintos (ver el reporte de skew `/public` vs `/market`, sección 5).
- Los cambios de Binance (retiro/renombrado de streams, cambio de semántica de liquidación de latest a largest, exclusión de RPI) significan que "el mismo nombre de stream" no garantiza la misma semántica en el tiempo; el grabador debería versionar el esquema/semántica con fecha.

### Gaps
- No se pudieron leer las páginas oficiales individuales de futuros (aggTrade, kline, bookTicker, Diff Book Depth, Partial Depth, Mark Price, Liquidation) ni las de opciones: el fetch devolvió solo la landing; los detalles vienen de resúmenes de búsqueda. Falta verificar en la fuente: campos exactos de kline de futuros y si bookTicker de futuros documenta `u` contiguo.
- No se encontró afirmación oficial de que los ids de aggTrade sean contiguos dentro del stream.
- No se leyó la sección de opciones de Binance (streams, límites, update ids).

## 2. Identificadores de secuencia y procedimiento oficial de libro local; cómo se detectan huecos

### Takeaway
Spot: snapshot REST + diffs con `U`/`u`; hueco si `U > localUpdateId + 1`. USD-M: además `pu` debe igualar el `u` previo. Estos son los únicos mecanismos oficiales de detección de huecos en Binance. Un libro sin huecos puede seguir siendo incorrecto (niveles fantasma), y los snapshots están limitados a 5000 niveles (spot).

### Cited Findings
- Procedimiento spot (resumen del extractor sobre la doc oficial): (1) abrir `@depth` y bufferizar, anotando la `U` del primer evento; (2) pedir snapshot REST (hasta 5000); (3) si `lastUpdateId` del snapshot es estrictamente menor que la `U` del primer evento bufferizado, pedir otro snapshot; (4) descartar eventos con `u <= lastUpdateId`; (5) fijar el libro al snapshot con id = `lastUpdateId`; (6) aplicar buffer y luego eventos en vivo. Regla por evento: si `u` < id local, ignorar; si `U` > id local + 1, se perdieron eventos, descartar el libro y reiniciar; cantidad 0 elimina el nivel; actualizar id local = `u`. Los snapshots tienen tope de 5000 niveles por lado, por lo que niveles más lejanos no aparecen hasta que cambien — [Spot web-socket-streams.md](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/web-socket-streams.md)
- Spot `GET /api/v3/depth`: límite por defecto 100, máx 5000; pesos 5 (1-100), 25 (101-500), 50 (501-1000), 250 (1001-5000); fuente "Memory" — [Spot rest-api.md](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/rest-api.md)
- Procedimiento USD-M: abrir `wss://fstream.binance.com/public/stream?streams=btcusdt@depth`; bufferizar; pedir `/fapi/v1/depth?limit=1000`; descartar eventos con `u` < `lastUpdateId`; el primer evento procesado debe cumplir `U <= lastUpdateId` y `u >= lastUpdateId`; cada evento siguiente debe tener `pu` igual al `u` del evento previo, si no reiniciar desde el paso 3; las cantidades son absolutas, no deltas; cantidad 0 elimina el nivel; un evento que elimina un nivel inexistente es normal — [How to manage a local order book correctly USD-M](https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/How-to-manage-a-local-order-book-correctly)
- La página de USD-M no define umbral temporal de obsolescencia/staleness; el único disparador de resincronización es la ruptura de secuencia — [mismo enlace anterior](https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/How-to-manage-a-local-order-book-correctly)
- Payload de diff USD-M incluye `E`, `T`, `U`, `u`, `pu`; velocidades 250 ms (por defecto), 500 ms, 100 ms; excluye órdenes RPI (resumen de búsqueda de la doc oficial) — [Diff Book Depth Streams USD-M](https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Diff-Book-Depth-Streams)
- Velocidad de diff depth SBE de spot: 50 ms -> 25 ms (2026-05-05) -> 20 ms (2026-08-04) — [Spot CHANGELOG](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/CHANGELOG.md)
- Evidencia comunitaria: un libro sin huecos de secuencia puede estar mal. En una prueba de 25,10 h con BTCUSDT (autor: mantenedor de UNICORN Binance Local Depth Cache, con herramienta propia, una sola ventana en mercado tranquilo, +/-1,88 %), un caché "ingenuo" que solo borra niveles con cantidad 0 terminó con 20.758 bids y 9.116 asks y solo 24,09 % de bids y 39,82 % de asks coincidían con REST; un caché podado a corredor de 1000 niveles coincidió 87,83 % / 91,74 % — [DEV Community, Zehentleitner](https://dev.to/oliverzehentleitner/your-binance-l2-order-book-can-be-gap-free-and-still-be-wrong-1kk8) (fuente secundaria, autoinformada)

### Inferences
- "Niveles fantasma": como los snapshots son de profundidad limitada y los diffs solo informan niveles que cambian, los niveles fuera de la ventana mantenida nunca reciben cantidad 0. Para un grabador que registra los diffs crudos, esto implica que la reconstrucción posterior debe acotar profundidad o validar contra snapshots periódicos (inferencia apoyada en la fuente secundaria anterior y en la nota de la doc sobre el tope de 5000).
- Los snapshots REST sirven como verificación periódica del libro reconstruido, pero un snapshot REST es una foto "Memory" sin garantía temporal exacta respecto del stream; usarlo solo vía el cálculo `lastUpdateId` vs `U`/`u`.
- Spot y futuros difieren: spot no tiene `pu`; la continuidad se prueba con `U <= prev_u + 1` (doc: error solo si `U > local+1`); futuros exige igualdad `pu == prev_u`. Binance spot: la doc no dice si `U == prev_u+1` siempre (el extractor afirma que "normally" lo es; no verificado literalmente).

### Gaps
- No se leyó la sección de opciones ni COIN-M del procedimiento de libro (se asume análogo a USD-M; no verificado).
- No se encontró documentación oficial sobre cuánto puede tardar un snapshot REST en ser "viejo" respecto al stream.

## 3. Qué NO está garantizado y causas de pérdida silenciosa de datos

### Takeaway
Hay varias vías documentadas de pérdida silenciosa: desconexión forzada por superar límites de mensajes entrantes, expiración a las 24 h, reinicios de infraestructura, streams que descartan eventos por diseño (liquidaciones), y clientes que tragan desconexiones anormales. Binance no documenta entrega garantizada ni replay tras reconexión.

### Cited Findings
- Spot: conexión válida 24 h; ping del servidor cada 20 s, desconexión si no hay pong en 1 min; máx 5 mensajes entrantes por segundo (incluye ping/pong y subscribe/unsubscribe) y superar el límite desconecta, con posible baneo de IP si se repite; máx 1024 streams por conexión; 300 intentos de conexión cada 5 min por IP — [Spot web-socket-streams.md](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/web-socket-streams.md)
- Spot: evento `serverShutdown` señala desconexión inminente (añadido 2026-05-06; el 2026-06-09 se eliminó el aviso fijo previo de 10 minutos); abrir nueva conexión cuanto antes — [Spot CHANGELOG](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/CHANGELOG.md)
- Spot: actualización de infraestructura de WebSocket Streams desde 2026-07-09 07:00 UTC (hasta ~1 hora) con posible desconexión: "your WebSocket connection may be disconnected; please reconnect" — [Spot CHANGELOG](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/CHANGELOG.md)
- USD-M: 24 h por conexión; ping cada 3 min, desconexión si no hay pong en 10 min; 10 mensajes entrantes por segundo; máx 1024 streams por conexión (subió de 200 a 1024 según changelog 2025-07-02); pongs no solicitados permitidos — [Connect USD-M](https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Connect); [Change Log derivados](https://developers.binance.com/docs/derivatives/change-log)
- USD-M: la página de Connect recomienda obtener estado de órdenes y posiciones por user data stream porque "REST data may lag during volatile markets" — [Connect USD-M](https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Connect)
- Fuentes de datos spot: Matching Engine, Memory, Database (de menor a mayor retraso potencial); "The API system is asynchronous, so some delay in the response is normal and expected" — [Spot rest-api.md](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/rest-api.md)
- Evidencia de clientes: `binance-connector-python` #548: una desconexión anormal (`CLOSE`/`ERROR`/EOF silencioso) "just breaks out of the detached receive_loop task and is swallowed"; el SDK solo reconecta por temporizador de 23 h o `serverShutdown`, no ante cierre anormal; se citan #293, #227 y #526 ("SUBSCRIBE ACKs succeed but no data frames arrive") — [issue #548](https://github.com/binance/binance-connector-python/issues/548). Cerrada el 2026-09-02 con API `on_connection`/reconnect
- `binance-connector-python` #258 (2023-09-18, cerrada 2025-07-18): "Connection to remote host was lost" tras 10 min a 1 día en stream aggTrade — [issue #258](https://github.com/binance/binance-connector-python/issues/258)
- `binance-connector-python` #528: reconexión al endpoint genérico `/stream` y duplicación del pool de conexiones en cada ciclo — [lista de issues](https://api.github.com/search/issues?q=repo:binance/binance-connector-python+is:issue+(websocket+OR+reconnect+OR+ping+OR+pong)&per_page=15) (solo título y resumen leídos)
- `python-binance` #948 (2021): "timed out waiting for pong" cierra el stream y los datos dejan de llegar; #526 (2020): no reconecta tras la caída; #917 (2021): fallo del keepalive del listen key detiene la reconexión — [búsqueda de issues python-binance](https://api.github.com/search/issues?q=repo:sammchardy/python-binance+is:issue+(reconnect+OR+missing+OR+out+of+order+OR+depth)+websocket&per_page=15) (solo resumen)
- `ccxt` #28466 (abierto, 2026-04-27): reporte de que `watch_order_book` de Binance spot se desvía de los precios reales tras 10-20 min; el mantenedor no pudo reproducirlo y explicó que con `checksum=true` un evento perdido lanza `ChecksumError` y re-descarga el snapshot; sin resolución — [issue #28466](https://github.com/ccxt/ccxt/issues/28466). Otros: ccxt #29586 (Go, `WatchBidsAsks` en Binance deja de entregar tras pocas actualizaciones) — [búsqueda ccxt](https://api.github.com/search/issues?q=repo:ccxt/ccxt+binance+watchOrderBook+(sequence+OR+nonce+OR+snapshot+OR+gap)&per_page=15)
- Skew entre endpoints tras la división de URL: `binance-connector-python` #564 (2026-09-07) reporta 500-2000 ms de desfase entre datos de libro (`/public`) y de trades/precios (`/market`) en períodos volátiles, frente a ~1 ms mediana / ~70 ms p99 antes; el autor aclara que son observaciones de operadores, no mediciones controladas; Binance no respondió y el contribuidor de Binance cerró el issue indicando que "cannot be resolved on our side" — [issue #564](https://github.com/binance/binance-connector-python/issues/564)
- Un colector comercial (Tardis) documenta que los mensajes de feeds se guardan sin modificar, que re-suscribe cada 24 h para obtener snapshots de libro y que esto crea "tiny gap" de ~300-3000 ms según el exchange; conexiones se reinician cuando falla la validación `U`/`u` — [Tardis Overview](https://docs.tardis.dev/historical-data-details/overview); [Tardis Binance](https://docs.tardis.dev/historical-data-details/binance)

### Inferences
- Pérdida silenciosa documentada o evidenciada: (a) mensajes de control que cuentan para el límite de 5/s (spot) o 10/s (futuros): un cliente que hace muchos subscribe/pong puede ser desconectado; (b) desconexión de 24 h y apagados de infraestructura: siempre hay un intervalo entre cierre y re-suscripción sin replay documentado; (c) clientes/SDK que no notifican caídas; (d) skew entre rutas `/public` y `/market` en futuros que rompe el orden cronológico por recepción; (e) liquidaciones con una sola fila por ventana de 1000 ms.
- Como no hay replay en WS, la prueba de integridad tras reconexión depende de rellenar desde REST (trades por `fromId`) y de reiniciar el libro (sección 2).
- La mención de "inter-endpoint skew" es evidencia de una sola fuente de la comunidad sin confirmación oficial; tratar como hipótesis.

### Gaps
- No se encontró un post-mortem oficial de Binance sobre degradación de WebSocket market data. La búsqueda sobre el 10-oct-2025 devolvió cobertura secundaria de un informe de Binance (publicado 2026-01-31) que reconoce degradación en transferencias internas, no en feeds de mercado; no se verificó en fuente primaria — [Bankless Times (secundaria)](https://www.banklesstimes.com/articles/2026/01/31/october-10-crypto-crash-binance-releases-post-mortem-findings/)
- No se leyó la página de límites de WS API (distinta de streams) ni documentación de listenKey.

## 4. Ciclo de vida de conexión, límites de tasa, baneos y diferencias REST vs WS

### Takeaway
Límites por IP en REST con pesos; 429 y 418 (baneos escalables 2 min a 3 días). Límites de WS por conexión distintos entre spot y futuros. Los valores cambian con frecuencia (p. ej. streams por conexión 200 -> 1024 en futuros en 2025).

### Cited Findings
- REST spot: límites basados en IP, no en API key; 429 al exceder, 418 si se continúa tras 429; `Retry-After` se envía con 418/429; baneos escalan "from 2 minutes to 3 days"; cabecera `X-MBX-USED-WEIGHT-(intervalNum)(intervalLetter)` — [Spot rest-api.md](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/rest-api.md)
- REST USD-M: mismos 429/418; límites actuales en `rateLimits` de `/fapi/v1/exchangeInfo` (RAW_REQUEST, REQUEST_WEIGHT, ORDER); 403 = WAF; 408 = timeout del backend; 503 "Unknown error ..." = estado de ejecución desconocido; -1008 = throttle de sistema; recvWindow por defecto 5000 ms — [General Info USD-M](https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info)
- Spot: timeout de 10 s de backend (-1007); hosts api1-api4 con "better performance but less stability"; solo datos de mercado: `data-api.binance.vision` y `wss://data-stream.binance.vision` (sin user data) — [Spot rest-api.md](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/rest-api.md); [legacy general info](https://developers.binance.com/legacy-docs/binance-spot-api-docs/rest-api/general-api-information)
- Spot: unidad de tiempo por defecto milisegundos; microsegundos con `timeUnit=MICROSECOND` en URL de WS o cabecera `X-MBX-TIME-UNIT:MICROSECOND` en REST (soporte anotado en el changelog el 2024-12-17) — [Spot web-socket-streams.md](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/web-socket-streams.md); [Spot CHANGELOG](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/CHANGELOG.md)
- Listen key / user data streams: no se leyó la documentación en esta investigación (ver Gaps). Evidencia comunitaria menor: python-binance #917 (fallo de keepalive de listen key detiene la reconexión).
- Comparación otros exchanges: Bybit: máx 500 conexiones por 5 min por dominio WS, ping cada 20 s recomendado, corte a los 10 min sin ping/pong o datos, desconexiones "at any time", reconectar cuanto antes; spot máx 10 args por request de suscripción — [Bybit WS connect](https://bybit-exchange.github.io/docs/v5/ws/connect). OKX: la conexión se corta si no hay suscripción o no se emiten datos en 30 s (enviar `ping` antes de N<30 s); máx 3 conexiones/s por IP y 480 requests de subscribe/unsubscribe/login por conexión por hora — [OKX docs-v5](https://www.okx.com/docs-v5/en/). Coinbase Exchange: debe enviarse `subscribe` en 5 s o el servidor desconecta; mensajes pueden perderse incluso sobre TCP — [Coinbase WS overview](https://docs.cdp.coinbase.com/exchange/websocket-feed/overview). Kraken v2: canal `heartbeat` ~1/s solo cuando no hay otras actualizaciones — [Kraken heartbeat](https://docs.kraken.com/api/docs/websocket-v2/heartbeat)
- OKX anuncia que desde 2026-10-31 el puerto 8443 deja de aceptar conexiones WebSocket (changelog) y que se enviará aviso 64008 60 s antes de una desconexión por actualización en el canal Business (2026-06-11) — [OKX changelog](https://www.okx.com/docs-v5/log_en/)

### Inferences
- Para un grabador de varios cientos de streams: distribuir en conexiones, no enviar mensajes de control innecesarios, y registrar los eventos de cierre/reconexión como metadatos propios (para marcar intervalos de datos no cubiertos).
- Dado que la lista de límites cambió al menos una vez en 2025 (200 -> 1024 en futuros), conviene registrar la fecha de lectura de límites en los metadatos de cada corrida.

### Gaps
- No se leyó: documentación de listenKey (spot/futuros), límites de WS API, página de límites oficial de spot con valor de peso por minuto (el extractor no confirmó "6000").
- No se verificó el límite de streams por conexión de COIN-M/opciones (la página COIN-M no lo mostró).

## 5. Semántica temporal: E, T, server time, unidades, microsegundos

### Takeaway
Binance usa milisegundos por defecto y ofrece microsegundos opcionales; los archivos de datos spot cambian a microsegundos desde 2025-01-01, lo que es una trampa para parsers.

### Cited Findings
- `E` = event time, `T` = trade time (en trades) / transaction time (diff USD-M incluye `E` y `T`); campo de diff USD-M `T` documentado en el payload de ejemplo — [Diff Book Depth Streams USD-M](https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Diff-Book-Depth-Streams) (resumen); spot trade incluye `T` trade time — [Spot web-socket-streams.md](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/web-socket-streams.md)
- Server time: `GET /api/v3/time` (peso 1, Memory) devuelve ms — [Spot rest-api.md](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/rest-api.md)
- USD-M: todos los campos de tiempo en milisegundos; datos devueltos en orden ascendente (más antiguo primero) — [General Info USD-M](https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info)
- Archivo público: timestamps spot en microsegundos desde 2025-01-01; datos anteriores y futuros en milisegundos (16 dígitos vs 13 en los ejemplos) — [binance-public-data README](https://raw.githubusercontent.com/binance/binance-public-data/master/README.md)
- Tardis: capturaba spot sin `timeUnit` hasta 2025-02-28 y desde entonces con `?timeUnit=microsecond`; sellos de recepción propios de 100 ns con reloj sincronizado — [Tardis Binance](https://docs.tardis.dev/historical-data-details/binance); [Tardis Overview](https://docs.tardis.dev/historical-data-details/overview)
- Bybit: `ts` = momento en que el sistema generó el dato, `cts` = timestamp del matching engine, correlacionable con `T` de trades públicos — [Bybit orderbook](https://bybit-exchange.github.io/docs/v5/websocket/public/orderbook)
- Kraken v2 book: `timestamp` RFC3339 con microsegundos — [Kraken book v2](https://docs.kraken.com/api/docs/websocket-v2/book)

### Inferences
- Un grabador debe guardar siempre: tiempo de recepción local (reloj sincronizado), `E`, `T`, y la unidad con la que se pidió el stream; no asumir que `E` sea monótono entre streams (evidencia de skew en sección 3).
- No encontré documentación que defina la precisión de sincronización del reloj de Binance ni la relación entre `E` y `T` más allá de los nombres.

### Gaps
- No se leyó la definición oficial literal de `E` vs `T` para cada stream de futuros.

## 6. Klines: finalización, revisiones y verdad en REST

### Takeaway
El stream de kline envía actualizaciones cada 1-2 s con flag de cierre `x`; REST klines (fuente Database) son la verdad de referencia pero hay reportes de huecos y de inconsistencias en el archivo.

### Cited Findings
- El stream spot de kline actualiza cada 1000 ms (`1s`) o 2000 ms (resto), con flag `x` "Is this kline closed?" — [Spot web-socket-streams.md](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/web-socket-streams.md)
- REST klines: peso 2, fuente Database, límite por defecto 500 y máx 1000; `startTime`/`endTime` siempre en UTC independientemente de `timeZone`; sin parámetros devuelve las más recientes; el campo final del array es "ignore" — [Spot rest-api.md](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/rest-api.md)
- `uiKlines`: mismos parámetros, datos "modified for candlestick chart presentation" — [Spot rest-api.md](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/rest-api.md)
- Archivo: actualización de klines del 2022-08-08 "fixing inconsistent data" — [binance-public-data README](https://raw.githubusercontent.com/binance/binance-public-data/master/README.md)
- Issue: en el archivo USD-M, agregar 5 velas de 1 m de mark price no coincide con la vela oficial de 5 m en 814 buckets BTCUSDT/ETHUSDT (2020-2025), y también en datos servidos por la API actual (comentario de usuario independiente, issue abierto sin respuesta) — [binance-public-data #483](https://github.com/binance/binance-public-data/issues/483)
- Issue: faltaba la vela BTCUSDT 1h de 2023-03-24 13:00 UTC, ausente también del archivo mensual — [binance-public-data #501](https://github.com/binance/binance-public-data/issues/501) (resumen de la búsqueda; abierto)
- Issue #365: decenas de huecos en klines de 1 s BTCUSDT 2017-2024 del archivo mensual — [binance-public-data #365](https://api.github.com/search/issues?q=repo:binance/binance-public-data+(missing+OR+duplicate+OR+wrong+OR+gap)&per_page=20) (resumen)

### Inferences
- Una vela del stream con `x=true` no está garantizada como definitiva respecto a REST; la doc leída no dice que sea inmutable ni que pueda revisarse. Se infiere que para análisis conviene tratar REST como referencia y marcar divergencias; no hay fuente que cuantifique revisiones.
- Velas ausentes no implican que el exchange no tuviera trades: en spot, una vela sin trades puede no existir (no confirmado por doc; ver Gaps).

### Gaps
- No encontré documentación oficial sobre revisión posterior de velas cerradas ni sobre el comportamiento de `x` si el stream pierde el último evento del intervalo.
- No se verificó si REST omite velas de intervalos sin trades.

## 7. Archivo histórico data.binance.vision y reconciliación

### Takeaway
El archivo oficial incluye checksums SHA256, pero los checksums solo prueban integridad de la descarga, no completitud. Hay múltiples issues abiertos sin respuesta oficial que reportan huecos, duplicados y un cambio silencioso de convención temporal.

### Cited Findings
- Contenido documentado en el README (extractor): aggTrades, klines, trades para SPOT, USD-M (`/fapi/v1`) y COIN-M (`/dapi/v1`); archivos diarios y mensuales; los diarios aparecen el día siguiente, los mensuales el primer lunes del mes siguiente; cada zip tiene `.CHECKSUM` (sha256sum) — [binance-public-data README](https://raw.githubusercontent.com/binance/binance-public-data/master/README.md)
- Los archivos pueden reemplazarse: el README mantiene un log de actualizaciones con rutas y checksums (2022-08-08 klines; 2022-04-21 aggTrades alineado con el cambio spot del 2022-04-12) — [binance-public-data README](https://raw.githubusercontent.com/binance/binance-public-data/master/README.md)
- Spot timestamps en microsegundos desde 2025-01-01 — [binance-public-data README](https://raw.githubusercontent.com/binance/binance-public-data/master/README.md)
- Intervalo mensual `1mo` en nombres de archivo (para sistemas de archivos que no distinguen mayúsculas) — [binance-public-data README](https://raw.githubusercontent.com/binance/binance-public-data/master/README.md)
- La lectura del README por el extractor no listó datasets como bookTicker, bookDepth, metrics, fundingRate, liquidationSnapshot, indexPriceKlines, pero los issues muestran que existen metrics, markPriceKlines, indexPriceKlines, BVOLIndex y bookDepth en el archivo — [issues lista](https://api.github.com/search/issues?q=repo:binance/binance-public-data+(missing+OR+duplicate+OR+wrong+OR+gap)&per_page=20); por tanto el README leído no cubre todos los datasets
- Issues (todos en github.com/binance/binance-public-data; estado a 2026-10-12 según la API de GitHub):
  - #203 (2022-12): aggTrades mensual BTCUSDT USD-M de septiembre 2022 con duplicados desde aggTradeId 1446230265; el checksum del zip coincide; Binance respondió "We're aware of the issue and are looking into it" (2022-12-21), sin arreglo visible — [#203](https://github.com/binance/binance-public-data/issues/203)
  - #378 (2024-12): huecos de ids en aggTrades BTCUSDT USD-M 2024-07-04; sin respuesta de Binance — [#378](https://github.com/binance/binance-public-data/issues/378)
  - #424 (2025-06): análisis de trades BTCUSDT perp 2020-2025: p. ej. 2022-02 con 2.295.328 ids faltantes (2,26 %), hueco mayor ~16,5 h; 2023-11 417.955 ids (0,51 %); discontinuidades de timestamp mayores de 1 min en varios meses; abril 2022 con duplicados; sin respuesta — [#424](https://github.com/binance/binance-public-data/issues/424) (análisis del reportante; la causa no está resuelta)
  - #353 (2024-09): ZILBTC spot aggTradeId duplicado en dos archivos feb/mar 2021 — [lista](https://api.github.com/search/issues?q=repo:binance/binance-public-data+(missing+OR+duplicate+OR+wrong+OR+gap)&per_page=20)
  - #458 (2026-02): en archivos de trades USD-M, cientos de símbolos sin trades el 2025-10-10 y otras fechas; la API muestra que existen; sin respuesta — [#458](https://github.com/binance/binance-public-data/issues/458)
  - #483 (2026-07): 603 minutos faltantes en markPriceKlines/indexPriceKlines 1m en seis símbolos (fechas 2020-01-19, 2020-12-17, 2022-07-12/13, 2024-08-12); la API devuelve `[]`; scripts de descarga oficiales recuperaron 0; reproducido por otro usuario — [#483](https://github.com/binance/binance-public-data/issues/483)
  - #484 y #503 (cerrados): huecos y duplicados en metrics/markPriceKlines (5 min) incluso con checksums válidos; #503: 285/288 registros de 5 min el 2023-09-12 — [lista](https://api.github.com/search/issues?q=repo:binance/binance-public-data+(missing+OR+duplicate+OR+wrong+OR+gap)&per_page=20)
  - #491 (2026-08): cambio no documentado el 2026-06-25 de la convención de `create_time` en metrics USD-M (fin de período -> inicio de período, +5 min), con fila `00:00:00` duplicada entre dos archivos diarios consecutivos; sin respuesta — [#491](https://github.com/binance/binance-public-data/issues/491)
  - #512 (2026-10-10): archivos diarios bookDepth BTCUSDT USD-M de 2026-10-07 y 2026-10-09 cubren solo parte del día UTC; #499: 21 archivos diarios consecutivos de BVOLIndex faltantes (2025-12-15 a 2026-01-04); #365, #370, #426, #457 (BTCUSD spot faltante antes de 2025-12-04), #287 (open interest) — [lista](https://api.github.com/search/issues?q=repo:binance/binance-public-data+(missing+OR+duplicate+OR+wrong+OR+gap)&per_page=20) (solo títulos y resúmenes)
- Pasivos del lado oficial: la auditoría de spot aggTrades 2022-04-12 admitió trades faltantes y duplicados corregidos (duplicados marcados con precio/cantidad 0 e id -1) — [Spot CHANGELOG](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/CHANGELOG.md)

### Inferences
- El archivo es útil como referencia para reconciliación de trades/klines, pero no es "verdad absoluta": la ausencia en el archivo no prueba ausencia en el exchange (issues #458, #483), y un trade presente en tu grabación y no en el archivo no implica error tuyo. Los ids de aggTrade/trade permiten reconciliar por id, no por tiempo.
- Un checksum válido solo prueba que el zip no se corrompió; varios issues muestran contenido con huecos y duplicados con checksums correctos (#203, #484).
- Un archivo diario puede reemplazarse; conviene guardar el checksum del archivo descargado y fecha de descarga.
- Metadatos de convención de tiempo cambiaron sin aviso (metrics, 2026-06-25) y spot cambió de ms a µs (2025-01-01): el parser debe detectar unidad por magnitud y registrar la convención.

### Gaps
- No se encontró documentación oficial sobre la latencia exacta de publicación más allá de "diarios al día siguiente; mensuales el primer lunes del mes siguiente".
- No hay respuesta oficial en la mayoría de los issues (solo #203 con reconocimiento); no se pudo establecer el estado de las correcciones.
- El README leído no documenta los datasets bookDepth, metrics, fundingRate, etc.; su formato y semántica no se verificaron en fuente primaria.

## 8. REST para backfill de trades y klines (límites, `fromId`)

### Takeaway
Endpoints de backfill existen pero con límites de 1000 filas por llamada y fuentes con posible retraso (Database). En futuros, la ventana de aggTrades por tiempo es limitada.

### Cited Findings
- Spot `GET /api/v3/trades` (peso 25, Memory, límite por defecto 500, máx 1000, sin `fromId`); `GET /api/v3/historicalTrades` (peso 25, Database, `fromId` opcional); `GET /api/v3/aggTrades` (peso 4, Database, `fromId`, `startTime` y `endTime` inclusivos, máx 1000) — [Spot rest-api.md](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/rest-api.md)
- Cambios previos: 2022-05-17 y 2022-02-24 `aggTrades` devuelve los elementos más antiguos cuando se dan `startTime` y `endTime`; el cambio sin fecha de 2022-12 retiró combinaciones de `fromId` con tiempos — [Spot CHANGELOG](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/CHANGELOG.md)
- Futuros: el changelog de derivados registra que el lookback de `aggTrades` pasa de 24 a 48 horas (efectivo 2026-08-13) y que `forceOrders` solo cubre 90 días — [Change Log derivados](https://developers.binance.com/docs/derivatives/change-log)
- Los datos en futuros se devuelven en orden ascendente — [General Info USD-M](https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info)
- Coinbase: para trades perdidos en el canal `matches` se recomienda usar `last_trade_id` del heartbeat para pedir los trades faltantes por REST — [Coinbase channels](https://docs.cdp.coinbase.com/exchange/websocket-feed/channels)

### Inferences
- Para backfill, el id es la clave de reconciliación; REST de trades por `fromId` en spot permite repaginar sin ambigüedad de tiempo. Para futuros, la ventana de 24-48 h de aggTrades por tiempo implica que un hueco de mayor antigüedad solo se cubre con el archivo público (con sus propios huecos).

### Gaps
- No se leyó la doc REST de futuros para `aggTrades`/`klines`/`trades` (semántica exacta de `fromId` y límites); solo se obtuvo la mención del changelog.
- No se verificó el rate limit de `historicalTrades` en futuros.

## 9. Símbolos: cambios, delistings, renombres, redenominaciones, mantenimiento

### Takeaway
Hay poca documentación formal de API sobre renombres; los cambios se anuncian por separado y rompen suscripciones. En Binance, COIN-M y USD-M se están fusionando y OKX migra pares USD a USDC.

### Cited Findings
- Binance retiró pares MATIC y listó POL spot el 2024-09-13 (Binance suspendió MATIC y abrió POL/USDT, POL/BTC, etc.); fuente secundaria de prensa, no el anuncio oficial — [The Block](https://www.theblock.co/post/316437/polygons-pol-token-surges-after-binance-listing-marking-end-of-matic-migration); [BeInCrypto vía TradingView](https://tr.tradingview.com/news/beincrypto%3A8720c8699094b%3A0-binance-lists-polygon-s-pol-token-price-impact)
- COIN-M/USD-M integración (changelog 2026-06-10, efectiva 2026-06-30) con stream `<pair>@indexPrice` de COIN-M cambiando el campo `i` por `s` y retirando `@indexPrice@1s` (cambio rompiente) — [Change Log derivados](https://developers.binance.com/docs/derivatives/change-log)
- Spot: nuevo valor `CANCEL_ONLY` en `symbolStatus` (SBE 3:5, 2026-07-01) — [Spot CHANGELOG](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/CHANGELOG.md)
- OKX: renombrado de contrato SPACEX Perpetual (2026-06-02) requiere re-suscribir con nuevo `instId`; migración de pares spot `Crypto-USD` a `Crypto-USDC` (2026-09-30) — [OKX changelog](https://www.okx.com/docs-v5/log_en/)
- ccxt #30814 (2026-10-12): reconstruir markets de forma no atómica puede enrutar mal updates de libro WS entre spot y perp con el mismo id — [ccxt #30814](https://api.github.com/search/issues?q=repo:ccxt/ccxt+binance+watchOrderBook+(sequence+OR+nonce+OR+snapshot+OR+gap)&per_page=15) (resumen)

### Inferences
- Un grabador debe guardar `exchangeInfo`/listas de símbolos con fecha y estado, y tratar el símbolo como clave con versión (símbolo + vigencia), porque el mismo nombre puede referirse a instrumentos distintos con el tiempo (inferencia; no hay fuente que lo afirme).

### Gaps
- No se encontró un anuncio oficial de Binance sobre renombres/redenominaciones leído en fuente primaria; ni un registro oficial de ventanas de mantenimiento de Binance para feeds de mercado.
- No se encontró página de estado oficial de Binance consultable para incidentes históricos.

## 10. Frecuencia de cambios de API y breaking changes

### Takeaway
Los cambios son frecuentes (alrededor de 3-4 entradas al mes en spot en 2026; varios cambios por mes en futuros), incluyendo campos nuevos, retiros y cambios de semántica.

### Cited Findings
- Spot CHANGELOG: 26 entradas del 2026-02-02 al 2026-09-18 (~3,5 por mes; marzo 2026 la más cargada con 6; agosto 2026 sin entradas) según el recuento del extractor — [Spot CHANGELOG](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/CHANGELOG.md)
- Futuros (derivados): ~9 entradas relevantes a streams/mercado en 2025 (julio-diciembre) y ~19 en 2026 (enero-septiembre) según recuento aproximado; ejemplos de cambios rompientes o de semántica: 2026-03-05 rutas nuevas, 2026-04-23 retiro de URL legacy, 2026-04-10 liquidación latest->largest, 2026-06-30 `i`->`s` en indexPrice COIN-M, 2025-11-18 exclusión de RPI en depth/bookTicker — [Change Log derivados](https://developers.binance.com/docs/derivatives/change-log)
- Spot: retiro de SBE 3:1 (2026-06-29) y de SBE 3:2 (2026-09-25); campos nuevos (`expiryReason`) — [Spot CHANGELOG](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/CHANGELOG.md)
- OKX: ~17 entradas relevantes a WS en 2025-03 a 2026-09; cambios rompientes incluidos: checksum fijado a 0 (2026-06-23), `books-elp` -> `books-rpi` (2026-07-28), puerto 8443 cerrado desde 2026-10-31, instruments channel con pushes incrementales (2026-09-30) — [OKX changelog](https://www.okx.com/docs-v5/log_en/)
- Bybit: cambios de frecuencia de push (spot Level 200 de 200 ms a 100 ms el 2026-03-19; Level 1000 de 300 ms a 200 ms 2025-11-25; ticker spot a 50 ms 2025-11-04) y eliminación del orderbook nivel 500 de futuros (2025-09-11) — [Bybit changelog v5](https://bybit-exchange.github.io/docs/changelog/v5)
- Binance Spot: en 2026 los cambios de cadencia de diff depth SBE fueron dos en 3 meses (50->25 ms, 25->20 ms) — [Spot CHANGELOG](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/CHANGELOG.md)

### Inferences
- Para 2026, la tasa de cambios es suficiente para exigir monitoreo de changelogs y guardar payloads crudos con versión de esquema; los recuentos por mes son aproximados (el extractor no leyó todo el changelog; ver Gaps).

### Gaps
- El changelog spot se leyó en dos partes (0-100000 y desde 100000); no se leyó el tramo de 2023-2025 (no hay entradas 2023-2024 en el segmento leído, pero el segmento puede no ser exhaustivo). El changelog de derivados solo se leyó hasta ~100000 de 153496 caracteres; el de OKX hasta ~100000 de 594452 (Bybit hasta ~100000 de 203833).

## 11. Otros exchanges: secuencias, snapshots, heartbeats y comprobaciones de integridad

### Takeaway
Coinbase ofrece números de secuencia por producto, canal `heartbeat` con `sequence` y `last_trade_id`, y reconoce que los mensajes pueden perderse; Kraken v2 ofrece checksum CRC32 de los 10 niveles superiores del libro (opcional); OKX ofrece `seqId`/`prevSeqId` y retiró el checksum en 2026-06-23; Bybit ofrece `u` y `seq`, con snapshot nuevo cuando hay problemas.

### Cited Findings
- Coinbase Exchange: números de secuencia crecientes de uno en uno por producto; "greater than one integer value from the previous number indicate that a message has been dropped"; número menor = fuera de orden; los servidores "can result in dropped messages"; se recomienda `level2` para sincronizar libro — [Coinbase WS overview](https://docs.cdp.coinbase.com/exchange/websocket-feed/overview)
- Coinbase `level2` "guarantees delivery of all updates" (snapshot + `l2update`, `size` es el total del nivel, "0" elimina); `level2_batch` cada 50 ms sin autenticación; `full` requiere autenticación y exige reconstrucción con snapshot REST, descartando mensajes con secuencia menor o igual; `matches`: "Messages can be dropped from this channel"; `heartbeat` por producto cada segundo con `sequence` y `last_trade_id`, que "can be used to verify that no messages were missed"; `ticker_batch` cada 5000 ms — [Coinbase channels](https://docs.cdp.coinbase.com/exchange/websocket-feed/channels)
- Coinbase: failover de `ws-direct` a `ws-feed`; tras reconectar hay que re-enviar `subscribe`; compresión permessage-deflate — [Coinbase WS overview](https://docs.cdp.coinbase.com/exchange/websocket-feed/overview)
- Kraken Spot WS v2 `book`: profundidades 10/25/100/500/1000, snapshot (por defecto true), checksum CRC32 de los 10 mejores niveles de bid y ask presente en snapshot y update, "Updates should always be processed in sequence", sin campo de número de secuencia descrito; `timestamp` RFC3339; "it is possible to have multiple updates to the same price level in a single update message" — [Kraken book v2](https://docs.kraken.com/api/docs/websocket-v2/book)
- Kraken checksum: se calcula tras aplicar todas las actualizaciones del mensaje; se trunca el libro a la profundidad suscrita tras cada update; validación opcional (cada update o periódica); la guía no dice qué hacer ante un desajuste — [Kraken checksum v2](https://docs.kraken.com/api/docs/guides/spot-ws-book-v2); [Kraken checksum guide](https://docs.kraken.com/exchange/guides/websockets/book-checksum-v2.md)
- Kraken heartbeat v2: ~1 por segundo solo cuando no hay otras actualizaciones; no lleva datos — [Kraken heartbeat](https://docs.kraken.com/api/docs/websocket-v2/heartbeat)
- OKX: snapshot con `prevSeqId = -1` y `seqId`; incremental con `prevSeqId` igual al `seqId` anterior; keepalive repite `seqId` con `prevSeqId == seqId`; tras mantenimiento un mensaje puede traer `seqId` menor que `prevSeqId` (reset) (resumen de búsqueda sobre la doc oficial; texto de la sección no leído en la página principal por truncamiento) — [OKX docs-v5](https://www.okx.com/docs-v5/en/); [OKX anuncio checksum](https://www.okx.com/en-us/help/okx-order-book-channels-checksum-field-deprecation)
- OKX: el campo `checksum` de `books`, `books-l2-tbt`, `books50-l2-tbt` queda fijo en 0 desde producción 2026-06-23 (demo 2026-06-02); `books5` y `bbo-tbt` nunca tuvieron checksum; se recomienda `seqId`/`prevSeqId` — [OKX anuncio checksum](https://www.okx.com/en-us/help/okx-order-book-channels-checksum-field-deprecation); [OKX changelog](https://www.okx.com/docs-v5/log_en/). Entrada 2025-07-08: trades channel añade `seqId`
- Evidencia comunitaria OKX: ccxt PR #30456 (2026-09): tras rechazo por nonce, el handler seguía modificando el libro eliminado — [ccxt #30456](https://api.github.com/search/issues?q=repo:ccxt/ccxt+binance+watchOrderBook+(sequence+OR+nonce+OR+snapshot+OR+gap)&per_page=15); proyectos de terceros que rompieron al fijarse el checksum a 0 (resultado de búsqueda, no verificado individualmente)
- Bybit orderbook: tras suscripción llega `snapshot` y luego `delta`; "If you receive a new snapshot message, you will have to reset your local orderbook"; `u`=1 indica snapshot por reinicio de servicio; nivel 1 de linear/inverse/spot solo envía snapshots y re-envía si no hay cambios en 3 s con el mismo `u`; `seq` (cross sequence) compara entre profundidades; frecuencias: L1 10 ms, L50 20 ms, L200 100 ms, L1000 200 ms (spot igual; opciones L25 20 ms, L100 100 ms; cifras de la página, con actualizaciones posteriores en el changelog) — [Bybit orderbook](https://bybit-exchange.github.io/docs/v5/websocket/public/orderbook)
- Bybit trades: `i` (trade id, string), `seq`, `T`, `ts`; un mensaje puede contener hasta 1024 trades y varios mensajes pueden compartir `seq`; sin promesas explícitas de entrega — [Bybit trade](https://bybit-exchange.github.io/docs/v5/websocket/public/trade)

### Inferences
- Pruebas de integridad por exchange (inferencia a partir de lo anterior):
  - Coinbase: mejor soporte de prueba (secuencia por producto + heartbeat con `last_trade_id` + level2 con entrega garantizada); `matches` sin garantía.
  - Kraken: integridad por checksum del top-10 (detecta divergencia de contenido, no huecos fuera del top-10); sin secuencia documentada en book.
  - OKX: continuidad por `prevSeqId`/`seqId` desde 2026-06-23 como única comprobación; el checksum ya no sirve; los libros de múltiples exchanges no son comparables entre sí.
  - Bybit: sin checksum; `u` y `seq` con resets explícitos; el snapshot reemplaza al libro.
  - Binance: `U`/`u`/`pu` con snapshot REST; sin checksum; sin heartbeat de datos.
- Ninguno de los exchanges comparados ofrece prueba criptográfica de completitud de trades; solo Coinbase (heartbeat `last_trade_id`) y Binance (ids de trade/aggTrade) permiten una verificación indirecta mediante ids.

### Gaps
- La sección de OKX "WS / Order book channel" no se pudo leer en la página (truncada) y la sección de trades/candles de OKX tampoco; los detalles de `seqId`/`prevSeqId` provienen de un resumen de búsqueda de la doc oficial.
- No se leyó el canal de velas (`confirm`) de OKX, ni la doc de klines de Bybit/Kraken/Coinbase.
- No se investigaron Coinbase Advanced Trade (distinto de Coinbase Exchange) ni canales de Kraken para trades (sin números de secuencia leídos).
- No se encontraron post-mortems oficiales de incidentes de feeds para Coinbase/Kraken/OKX/Bybit.

## 12. Qué dice la documentación sobre exactitud de datos y qué prueba de completitud existe

### Takeaway
Las docs oficiales leídas no ofrecen declaración de exactitud/completitud del feed ni SLA; las únicas garantías explícitas son el nivel2 de Coinbase y la continuidad de secuencias.

### Cited Findings
- Binance spot: sin promesa de entrega, sin mención de duplicados — [Spot web-socket-streams.md](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/web-socket-streams.md)
- Binance: "The API system is asynchronous, so some delay in the response is normal and expected" — [Spot rest-api.md](https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/rest-api.md)
- Coinbase: advierte explícitamente de mensajes perdidos y recomienda el canal con garantía — [Coinbase WS overview](https://docs.cdp.coinbase.com/exchange/websocket-feed/overview)
- Bybit trades: sin garantías explícitas — [Bybit trade](https://bybit-exchange.github.io/docs/v5/websocket/public/trade)
- Tardis (proveedor): almacena mensajes sin modificar, valida secuencias donde existen, reinicia conexiones ante gap y marca como `generated:true` los snapshots obtenidos por REST — [Tardis Overview](https://docs.tardis.dev/historical-data-details/overview); [Tardis Binance](https://docs.tardis.dev/historical-data-details/binance)
- CoinAPI publicó un incidente de huecos en OHLCV para Binance y otros exchanges APAC (feb. 2023) — [CoinAPI status](https://status.coinapi.io/history/2023/february/2rlrltw6r8dm9zlq-gaps-in-ohlcv-data-for-binance-and-a-few-smaller-apac-exchanges) (solo título visto; contenido no leído)

### Inferences
- Resumen de qué permite PROBAR completitud (a partir de lo anterior):
  - Prueba posible: Binance trade/aggTrade por ids (con REST como reconciliador), Binance depth diff por `U`/`u`/`pu`, Coinbase level2/heartbeat/sequence, OKX `seqId`/`prevSeqId` (books), Bybit `u` y reset por `u=1`, Kraken book checksum (solo de contenido top-10).
  - Sin prueba: Binance kline stream, bookTicker parcial, depth parcial, mark price, ticker, forceOrder (diseñado con pérdidas); Coinbase `matches` (sin garantía); streams de metrics/open interest generados por REST en proveedores.
- No hay sustituto para guardar los datos crudos con tiempo de recepción y registrar eventos de conexión.

### Gaps
- No hay SLA oficial leído de ningún exchange; no se encontró documento oficial de exactitud de datos de Binance.
- No se leyó el contenido del incidente de CoinAPI.
