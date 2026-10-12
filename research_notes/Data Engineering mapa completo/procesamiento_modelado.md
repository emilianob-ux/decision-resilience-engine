# Procesamiento de datos (batch y streaming) y modelado de datos

Fecha de corte: oct 2026. Metodología: ~12 búsquedas web (snippets, sin fetch profundo de páginas). Convención: "Cited Findings" = respaldado por fuente; "Inferences" = mezcla de inferencia y conocimiento de fondo del investigador (NO verificado en esta sesión; marcado como [BG] cuando es conocimiento previo, [VOLÁTIL] cuando es de rápida evolución). El redactor debe tratar [BG] como hipótesis a contrastar.

## 1. Spark vs Flink vs Kafka Streams vs streaming databases: criterios de decisión

### Takeaway
No hay ganador universal: Kafka Streams = librería embebida para lógica simple sobre Kafka en servicios Java; Flink = estado grande y lógica event-time compleja con equipo que opere un clúster; Materialize/RisingWave = vistas SQL frescas servidas a apps (sobre todo CDC); Spark = plataforma batch/lakehouse que ahora (4.1) empieza a cubrir baja latencia con Real-Time Mode, aún limitado a consultas sin estado. Gran parte de la comparación pública es de vendors (RisingWave, Tinybird): sesgo.

### Cited Findings
- Kafka Streams es una librería (no clúster): la topología corre dentro del proceso de la app, se escala añadiendo instancias; costos operativos: rebalanceo de state stores en deploys, standby replicas, lag, replay de estado tras bugs — [RisingWave: Kafka Streams vs RisingWave 2026](https://risingwave.com/blog/kafka-streams-vs-risingwave-2026) (vendor)
- Flink: recomendado para lógica compleja event-driven con flexibilidad Java; "poderoso pero caro de operar" — [RisingWave: Choosing between RisingWave, Materialize, Flink](https://risingwave.com/blog/choosing-risingwave-materialize-flink-data-stack) (vendor)
- Materialize: consistencia strict-serializable (joins sobre CDC reflejan el estado exacto de la fuente en cada instante), solo cloud, licencia source-available (BSL), consistencia correcta pero memory-bound — [RisingWave vs Materialize](https://risingwave.com/blog/risingwave-vs-materialize-comparison/) (vendor competidor)
- RisingWave: SQL-nativo, compatible con protocolo PostgreSQL, escalado elástico sobre object storage; afirma superar a Flink en 22/27 queries Nexmark (benchmark propio, sin verificar independiente) — [RisingWave Flink alternatives 2026](https://risingwave.com/blog/best-apache-flink-alternatives-2026/)
- Un pipeline que solo escribe a topics Kafka no puede ser consultado directamente por un agente/app; una streaming DB con interfaz Postgres sí — [RisingWave](https://risingwave.com/blog/kafka-streams-vs-risingwave-2026)
- Flink 2.0: estado desagregado (ForSt, LSM sobre DFS con disco local como caché) + runtime de ejecución asíncrona; paper VLDB 2025 reporta vs Flink 1.20 (Nexmark y carga productiva): hasta -94% duración de checkpoint, hasta 49x recuperación/rescale más rápido, hasta 50% ahorro de costo — [VLDB 2025 Mei et al.](https://www.vldb.org/pvldb/vol18/p4846-mei.pdf). Latencia objeto ~23 ms vs NVMe ~68 µs, ocultada por el Asynchronous Execution Controller (análisis de blog, no del paper) — [blog](https://mohakchugh.is-a.dev/blog/flink-disaggregated-state-forst-async-execution)
- Spark 4.0: ANSI mode por defecto, tipo VARIANT, Spark Connect con alta paridad con Classic, cliente Python ligero pyspark-client (1.5 MB), tarball con Connect habilitado por defecto, config `spark.api.mode`, cliente Swift — [Spark 4.0.0 release](https://spark.apache.org/releases/spark-release-4-0-0.html); [Databricks blog](https://www.databricks.com/blog/introducing-apache-spark-40)
- Spark 4.1: Real-Time Mode (RTM) en Structured Streaming + Spark Declarative Pipelines (SDP). Docs OSS: 4.1 solo soporta consultas stateless (proyecciones, filtros, unions, stream-static joins); agregaciones, dedupe, stream-stream joins y `transformWithState` planificados "desde Spark 4.3". Databricks (vendor) afirma latencias de ~5 ms. Discrepancia de versión (4.1 vs 4.1.1) no resuelta — [Spark docs RTM](https://apache.googlesource.com/spark/+show/master/docs/streaming/real-time-mode.md); [Databricks RTM](https://www.databricks.com/product/data-engineering/spark-real-time-mode); [Databricks Spark 4.1](https://www.databricks.com/blog/introducing-apache-sparkr-41)
- Contexto corporativo: IBM anunció compra de Confluent (~US$11B, US$31/acción) el 8-dic-2025; un único source indica cierre el 17-mar-2026 (no confirmado por 2ª fuente); Confluent seguirá como marca distinta; Kafka sigue siendo OSS — [Confluent blog](https://confluent.io/blog/ibm-to-acquire-confluent); [SD Times](https://sdtimes.com/data/ibm-to-acquire-confluent-for-11-billion/); [Nucleus](https://nucleusresearch.com/research/single/ibm-announces-intent-to-acquire-confluent/)

### Inferences
- Árbol de decisión sugerido: (1) ¿Necesita <1 s con estado grande, event-time, CEP, joins complejos? -> Flink. (2) ¿Lógica por-evento en microservicio Java ya sobre Kafka, estado moderado? -> Kafka Streams. (3) ¿El consumidor es una app/analista que consulta una vista fresca por SQL, con CDC como fuente? -> Materialize/RisingWave. (4) ¿Ya hay lakehouse Spark y SLA de minutos? -> Structured Streaming micro-batch / SDP, sin nuevo motor. RTM en Spark aún no cubre casos con estado (a oct-2026 [VOLÁTIL]: verificar si 4.2/4.3 lo añadió).
- Flink 2.0 con estado en objeto reduce el principal argumento operativo contra Flink (checkpoints/rescale lentos con estado de TB), pero los números son del equipo autor del paper (Alibaba/Ververica) [inferencia].
- [BG] Otros: Beam es capa de portabilidad (runners Dataflow/Flink/Spark), su valor real depende de Dataflow; Arroyo, Bytewax, ksqlDB (en declive relativo; Confluent prioriza Flink), Decodable aparecen en comparativas; Pulsar tiene tracción menor que Kafka; Redpanda = API Kafka en C++/Seastar sin JVM, licencia BSL. Sin verificar aquí.
- [BG] Exactly-once: Flink = checkpoints Chandy-Lamport + 2PC en sinks; Kafka Streams = transacciones Kafka (EOS v2); Spark = checkpoint + sinks idempotentes. "Exactly-once" end-to-end exige sink transaccional o idempotente.

### Gaps
- Sin fuentes independientes (no vendor) con benchmarks Flink vs Spark vs Kafka Streams vs RisingWave.
- No se verificó estado de Pulsar, Redpanda, Beam, Ray, Trino/Presto en 2026.
- No se confirmó la fecha de GA de Flink 2.0 ni el último Flink (2.1/2.2) ni Kafka 4.1/4.2.
- Qué versión de Spark (4.2/4.3) lleva RTM stateful a oct-2026.

## 2. ¿Cuándo se justifica streaming real vs micro-batch/batch frecuente?

### Takeaway
Streaming real se justifica cuando el costo del retraso es alto (seguridad, fraude, obligaciones legales, decisiones operativas automáticas) o cuando el consumidor es una app/agente que necesita estado fresco; en el resto, batch frecuente (15-60 min) o micro-batch suele bastar con mucha menos complejidad operativa.

### Cited Findings
- Una guía (secundaria, en coreano) estima que solo 5-15% de los datos requieren tiempo real real y enmarca la decisión por "costo del retraso" — [youngju.dev](https://www.youngju.dev/transcribe/culture/2026-04-15-streaming-vs-batch-redefined-complete-guide-flink-risingwave-materialize-cdc-streaming-sql-deep-dive-guide-2025.en) (cifra no verificada, fuente débil)
- Fuentes vendor sugieren que si un dashboard o refresh batch cada 15-60 min cumple, streaming puede no justificarse; muchos equipos reevalúan la complejidad operativa para trabajo que SQL resuelve — [RisingWave](https://risingwave.com/blog/apache-flink-alternatives-sql-teams)
- Kafka 4.0: ZooKeeper eliminado (solo KRaft), KIP-848 (nuevo protocolo de rebalanceo de consumidores) GA, colas (KIP-932, share groups) en early access; requiere pasar por 3.9.x antes; Java 17 brokers / 11 clientes — [Instaclustr](https://www.instaclustr.com/blog/kafka-4-0-unveiled-key-changes-and-how-they-impact-developers/); [2 Minute Streaming](https://blog.2minutestreaming.com/p/apache-kafka-4-0-release)
- KIP-1150 (Diskless Topics) aceptado el 2-mar-2026 (9 binding, 5 non-binding); topics opt-in que escriben a object storage, diseño leaderless; propuesto por Aiven abr-2025 — [Aiven](https://aiven.io/blog/kip-1150-accepted-and-the-road-ahead). WarpStream adquirido por Confluent el 9-sep-2024 y hoy dentro de IBM; competidor (AutoMQ) cuestiona independencia — [AutoMQ](https://www.automq.com/blog/warpstream-after-confluent-acquisition-what-changed) (sesgado); [WarpStream](https://www.warpstream.com/llms.txt) (sesgado)
- DataFusion Comet 1.0.0 (primer estable) reportado 7-ago-2026; Gluten graduó a top-level en mar-2026; Comet vs Gluten: Gluten soporta Velox y ClickHouse (Velox más usado), Comet se enfoca solo en DataFusion — [Comet vs Gluten](https://datafusion.apache.org/comet/gluten_comparison.html) (mantenido por Comet); [Dremio](https://www.dremio.com/newsroom/apache-elevates-open-source-projects-gluten-and-polaris-to-top-level-status/); [datalakehousehub](https://datalakehousehub.com/blog/datafusion-comet-1-spark-iceberg)
- DuckDB 1.4.0 LTS (16-sep-2025): cifrado, MERGE, escrituras Iceberg; soporte comunitario LTS hasta 2026-09-16 (ya vencido; 1.4.5 existe); DuckDB 1.5.x en 2026 con DuckLake v0.4, GEOMETRY y VARIANT; v2.0 esperado "este otoño" — [DuckDB 1.4](https://duckdb.org/2025/09/16/announcing-duckdb-140), [MotherDuck jul-2026](https://motherduck.com/blog/duckdb-ecosystem-newsletter-july-2026/). Polars: motor streaming estabilizado y sink Iceberg en 2026 (fuentes secundarias) — [datalakehousehub](https://datalakehousehub.com/blog/2026-05-duckdb-polars-iceberg/)

### Inferences
- Heurística: elegir latencia por consumidor, no por pipeline. Capas: ingesta CDC/eventos continua (barata en Kafka/diskless) + transformación en micro-batch/incremental (Spark SDP, dbt incremental, Iceberg/Delta/Hudi) + streaming real solo para el subconjunto con SLA de segundos.
- Streaming lakehouse (Flink/Spark -> Iceberg/Paimon/Hudi) hoy da frescura de 1-5 min con semántica de tabla; suele ser el término medio que evita operar estado complejo [BG; Paimon/Fluss no verificados aquí].
- Diskless/WarpStream-like: intercambia latencia (cientos de ms a ~1-2 s p99) por costo (sin tráfico inter-AZ) [BG]; apto para logs/telemetría/CDC analítico, no para trading o RPC de baja latencia.
- Para single-node/medio (<~1 TB), DuckDB/Polars reemplazan Spark con menor costo; Spark+Photon/Velox/Comet siguen para escala y gobierno multi-tenant [BG].
- Conceptos (Akidau/Kleppmann) [BG, estables]: event time vs processing time; watermarks = heurística de completitud; triggers + allowed lateness + retractions/acumulación; ventanas tumbling/sliding/session; dualidad stream-tabla (changelog <-> tabla); backpressure vía buffers acotados/credit-based (Flink) o lag (Kafka).
- Tuning Spark [BG]: AQE (skew join, coalesce de particiones), `spark.sql.shuffle.partitions`, salting para skew, broadcast joins, formatos columnar + particionado/clustering (liquid clustering/Z-order), evitar small files, memoria off-heap con motores nativos.

### Gaps
- No hay evidencia citada de Photon (propietario Databricks), Trino/Presto, Ray, Pulsar, Redpanda.
- Latencias reales de diskless Kafka no verificadas.
- No se encontraron casos Uber/Netflix recientes (no buscados).

## 3. Kimball vs Data Vault vs OBT en warehouses cloud columnares

### Takeaway
Kimball (star schema) sigue siendo el default para capa de consumo; Data Vault 2.0 se justifica en integración multi-fuente con cambio frecuente, auditoría y carga paralela (con un mart Kimball encima); OBT es una optimización de entrega para casos concretos, sin fuentes sólidas encontradas. La evidencia es blogs/vendors, no benchmarks.

### Cited Findings
- Data Vault separa entidades de negocio, relaciones y datos descriptivos, facilitando expansión; prioriza escalabilidad de carga sobre velocidad de consulta, por lo que el rendimiento se resuelve en una capa de reporting — [VaultSpeed](https://www.vaultspeed.com/blog/a-robust-foundation-for-data-products) (vendor DV)
- Argumento a favor: gobernanza, auditoría, ingesta paralela; en contra: complejidad de consulta — [datadriven.io](https://datadriven.io/data-vault-interview-questions)
- Whitepaper LTIMindtree (dic-2025): DV 2.0 apto para Snowflake/Databricks pero adopción cauta por complejidad/overhead; Kimball "fundacional" pero rezagado — [LTIM PDF](https://www.ltm.com/content/dam/ltimcorporatewebsite/uploads/2025/12/Data-Vault-2.0.pdf) (vendor)
- La mayoría de warehouses analíticos de empresas tech omiten DV y usan Kimball; los star schemas pueden romperse con fuentes cambiantes — [DataVidhya](https://datavidhya.com/learn/data-modeling-and-warehouse/modern-approaches/data-vault/)

### Inferences
- [BG] Kimball: hechos (grano declarado, aditivos/semi/no aditivos) + dimensiones conformadas, bus matrix; SCD tipo 1 (sobrescribe), 2 (versionado con vigencia — default para historia), 3 (columna previa), 4 (mini-dimensión/historial), 6 (híbrido 1+2+3), 7. En columnar cloud, joins baratos y storage barato hacen viables SCD2 y snapshots.
- [BG] Inmon (CIF): EDW normalizado 3NF corporativo + data marts; hoy se usa como "capa core/silver normalizada"; menor adopción como metodología explícita.
- [BG] Data Vault 2.0: hubs (claves de negocio), links (relaciones), satellites (atributos con historia), hashkeys, load-date, record source; Business Vault (reglas), PIT/bridge tables para rendimiento. Cuándo: muchas fuentes, M&A, auditoría regulada, equipos grandes con automatización (VaultSpeed, dbt packages). Cuándo no: equipo chico, pocas fuentes, un dominio: sobre-ingeniería (más joins, más tablas).
- [BG] OBT: tabla ancha desnormalizada precalculada; pros: simplicidad para BI/ML, sin joins, ideal en columnar con compresión; contras: duplicación/refresh costoso, dificultad con relaciones many-to-many y cambios de dimensión, gobierno de métricas disperso, ancho excesivo. Buen "serving layer" derivada de un modelo star, no modelo primario.
- [BG] Activity schema: una sola tabla de eventos (actividad por cliente/entidad) con convenciones; buen ajuste para analítica de producto/journeys; adopción de nicho, ligada a Narrator; madurez baja-media.
- Recomendación práctica [inferencia]: medallion (raw/bronze -> integrado -> consumo); DV opcional en integración, Kimball en consumo, OBT/wide tables como vistas materializadas para casos de rendimiento o ML features; semantic layer encima para métricas.
- [BG] Lakehouse: Iceberg/Delta/Hudi con particionado oculto/liquid clustering, evolución de esquema, SCD2 vía MERGE; data contracts (ODCS/Open Data Contract Standard, schema registry con compatibilidad, tests en CI) para estabilizar fronteras productor-consumidor.

### Gaps
- Sin fuente sobre OBT ni Activity schema (búsqueda no devolvió contenido).
- Sin benchmarks de rendimiento Kimball vs DV vs OBT en Snowflake/BigQuery/Databricks.
- Sin fuentes primarias de Kimball Group (Kimball Techniques) o Linstedt en esta sesión.
- Data contracts: no investigados con fuentes.

## 4. Semantic layer: estado del arte 2025-2026

### Takeaway
2026 es el año de la estandarización: Open Semantic Interchange (OSI) nació en ene-2026 (Snowflake, dbt Labs, Databricks, Salesforce, etc.) y en jul-2026 migró a la Apache Incubator como Apache Ossie; MetricFlow (motor del dbt Semantic Layer) pasaría a Apache 2.0 (dic-2025, fuente agregadora); dbt Labs se fusionó con Fivetran. Cube Core sigue como semantic layer OSS para serving de alta concurrencia/API.

### Cited Findings
- OSI v0.1: lanzado 27-ene-2026 por Snowflake como repo Apache 2.0; modelo vendor-neutral de datasets, métricas, dimensiones, relaciones, contextos; dbt Labs, Databricks, Salesforce participaron en la spec inicial; Denodo se unió mar-2026 — [Snowflake blog](https://www.snowflake.com/en/blog/open-semantic-interchanges-specs-finalized/); [dbt blog](https://www.getdbt.com/blog/the-osi-spec-updates); [Denodo](https://denodo.com/en/press-release/2026-03-24/denodo-joins-snowflake-and-industry-leaders-advance-data-and-ai-interoperability-through-open)
- OSI pasó a Apache Incubator como "Apache Ossie" (anuncio 10-jul-2026); formato YAML declarativo para métricas, dimensiones y joins; hay actualización comunitaria abr-2026 — [Apache Ossie](https://ossie.apache.org/); [update abr-2026](https://ossie.apache.org/updates/osi-april-2026-community-update/)
- Fivetran y dbt Labs: fusión all-stock anunciada oct-2025; una fuente dice cierre 1-jun-2026; incertidumbre sobre el futuro del Semantic Layer — [PrivSource](https://www.privsource.com/acquisitions/deal/fivetran-and-dbt-labs-to-merge-in-an-all-stock-deal-EMSy57); [Plushcap dbt oct-2025](https://www.plushcap.com/companies/dbt/blog/summaries/2025/10)
- MetricFlow movido a Apache 2.0 en dic-2025 y alineado con OSI (fuente secundaria, confirmar con dbt Labs) — [Cube vs dbt SL vs MetricFlow 2026](https://querio.ai/articles/cube-vs-dbt-semantic-layer-vs-metricflow-update)
- Cube Core (Apache 2.0) lee modelos dbt y añade caching, seguridad multi-tenant, múltiples interfaces; comparativas: dbt SL para gobierno de métricas centrado en dbt, Cube para APIs/embedded/baja latencia — [Cube](https://cube.dev/articles/dbt-semantic-layer-alternatives-2026) (vendor); [Querio](https://querio.ai/articles/cube-vs-dbt-semantic-layer-vs-metricflow-update)

### Inferences
- [BG] Otras opciones: AtScale (universal semantic layer comercial, MDX/DAX/SQL), Snowflake Semantic Views, Databricks Unity Catalog Metric Views, LookML (Looker), Power BI semantic models; las plataformas están incorporando semantic layers nativos, lo que presiona a los independientes. Verificar.
- Motor de la tendencia: los LLM/agentes de analítica (text-to-SQL) exigen definiciones de métricas gobernadas; un semantic layer reduce alucinaciones [BG, plausible].
- Riesgo: la estandarización OSI/Ossie está en fase temprana (v0.1, incubación); el interchange puede perder expresividad frente a formatos nativos. Madurez: dbt SL/Cube/LookML = producción; OSI/Ossie = emergente.

### Gaps
- No se verificó el anuncio primario de MetricFlow Apache 2.0, ni el roadmap post-fusión Fivetran-dbt.
- Sin detalle sobre AtScale, Snowflake Semantic Views, Databricks Metric Views.
- No se confirmó versión actual de la spec Ossie posterior a v0.1.

## 5. Catálogo por tecnología (descripción / cuándo / pros-contras / alternativas / madurez)

### Takeaway
Tabla compacta; solo lo marcado con fuente está verificado, el resto es [BG] y debe tratarse como hipótesis.

### Cited Findings
- Spark 4.x: ver sección 1 (ANSI, VARIANT, Connect, RTM, SDP). Madurez: GA, estándar de facto batch.
- Motores nativos: Gluten (top-level mar-2026, Velox/ClickHouse), Comet 1.0 (ago-2026, DataFusion) — ver sección 2. Photon es propietario de Databricks (no verificado aquí).
- Kafka 4.x (KRaft, KIP-848 GA, colas early access en 4.0), Diskless KIP-1150 aceptado (implementación pendiente [BG]) — secciones 2.
- Flink 2.0 (estado desagregado) — sección 1.
- DuckDB 1.4 LTS / 1.5, DuckLake, Polars streaming — sección 2.
- Streaming DBs: Materialize (BSL, cloud), RisingWave (Postgres-compatible, OSS) — sección 1.

### Inferences
- [BG] Kafka Streams: librería JVM, estado en RocksDB + changelog topics; EOS; sin clúster extra; limitada a Kafka como fuente/sink. Madurez alta.
- [BG] Redpanda: broker compatible Kafka, C++, tiered storage, BSL; Pulsar: separación compute/storage (BookKeeper), multi-tenancy, geo-replicación; adopción menor. Beam: modelo unificado, portabilidad; Ray: cómputo distribuido Python/ML (Ray Data para ingesta/inferencia, no para SQL clásico); Trino/Presto: SQL federado interactivo sobre lakehouse, no ETL pesado con tolerancia a fallos salvo modo FTE.
- [BG] Tiered storage Kafka (KIP-405): GA desde 3.9; offload de segmentos fríos a objeto. Verificar.

### Gaps
- Todo lo [BG] de esta sección sin verificar con fuentes en esta sesión; priorizar verificación de: Flink 2.x releases, Kafka tiered storage GA, Photon, Trino FTE, Ray, Pulsar, Redpanda licensing, Activity schema, Data Vault 2.0 (Linstedt), Kimball Group.
