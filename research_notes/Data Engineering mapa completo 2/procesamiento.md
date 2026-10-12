# Procesamiento batch y streaming: verificación con fuentes primarias (corte oct-2026)

Metodología: ~45 llamadas de búsqueda/fetch. Convención: "Cited Findings" = respaldado por la URL citada; "Inferences" = inferencia o conocimiento de fondo [BG] no verificado en esta sesión. Aviso: WebFetch resume con un modelo pequeño; los datos clave provienen de páginas primarias (spark.apache.org, flink.apache.org, kafka.apache.org, newsroom.ibm.com, jepsen.io, uber.com), pero algunas páginas largas se leyeron solo parcialmente. Las secciones de modelado quedan fuera de alcance.

## 1. Estado verificado de versiones y fechas (Spark, Flink, Kafka, Trino, Pulsar, IBM–Confluent)

### Takeaway
Spark está en 4.2.0 (14-jul-2026); Flink en 2.3.0 (25-jun-2026); Kafka en la línea 4.3 (4.3.0 22-may-2026) y 4.2.2 (29-sep-2026); Trino 483 (17-jul-2026). IBM cerró la compra de Confluent el 17-mar-2026, confirmado por nota de prensa IBM (primaria) y varias secundarias. No existe Spark 4.3 publicado a la fecha de la página de noticias consultada.

### Cited Findings
- Spark: 4.0.0 (23-may-2025), 4.1.0 (16-dic-2025), 4.1.1 (9-ene-2026), 4.1.2 (21-may-2026), 4.2.0 (14-jul-2026), 4.1.3 y 4.0.4 (15-jul-2026), 3.5.9 (16-jul-2026). La página no lista 4.3 — [Spark news](https://spark.apache.org/news/index.html)
- Flink: 2.0.0 (24-mar-2025), 2.1.0 (31-jul-2025), 2.2.0 (4-dic-2025), 2.3.0 (25-jun-2026, "latest stable"), parches 2.2.1 (15-may-2026), 2.1.3 (14-jun-2026) — [Flink downloads](https://flink.apache.org/downloads/) (se leyeron 100k de 126k caracteres)
- Kafka: 4.0.0 (18-mar-2025), 4.1.0 (2-sep-2025; el blog indica 4-sep), 4.2.0 (17-feb-2026), 4.3.0 (22-may-2026), 4.3.1 (25-jun-2026), 4.2.2 (29-sep-2026), 4.1.2 (17-mar-2026). La página marca 4.3.1 como "latest" aunque 4.2.2 tiene fecha posterior (la herramienta advirtió que podría ser error de la página; no resuelto) — [Kafka downloads](https://kafka.apache.org/community/downloads/); [Kafka blog](https://kafka.apache.org/blog)
- IBM completó la adquisición de Confluent el 17-mar-2026: US$31/acción en efectivo, EV ~US$11B; la nota IBM no dice si la marca Confluent se mantiene ni nada sobre la licencia/desarrollo OSS de Kafka — [IBM Newsroom](https://newsroom.ibm.com/2026-03-17-ibm-completes-acquisition-of-confluent,-making-real-time-data-the-engine-of-enterprise-ai-and-agents). Anuncio 8-dic-2025, aprobación de accionistas 12-feb-2026, baja de Nasdaq 16-mar — [ChannelWeb](https://www.channelweb.co.uk/news-network/2026/ibm-completes-11bn-confluent-acquisition) (secundaria; no se encontró el 8-K/SEC filing directamente)
- Trino: 483 (17-jul-2026), 482 (25-jun-2026), 481 (11-may-2026), 480 (24-mar-2026), 479 (14-dic-2025) — [Trino releases](https://trino.io/docs/current/release.html)
- Pulsar: 4.2.0 el 24-mar-2026, 4.2.1 el 23-abr, 4.2.2 el 5-jun (API de releases Apache, espejo de pruebas); LTS 4.0 sale de soporte activo el 21-oct-2026 y recibe solo parches de seguridad hasta 21-oct-2027 (endoflife.date y artículo; política: LTS cada 18 meses) — [release API](https://release-test.apache.org/api/cle/release/pulsar/4.2.0); [endoflife.date](https://endoflife.date/apache-pulsar)
- Gluten graduó a TLP el 5-mar-2026 (ASF, junto a Polaris) — [ASF news](https://news.apache.org/foundation/entry/the-apache-software-foundation-graduates-two-open-source-projects-from-incubator); [Dremio newsroom](https://www.dremio.com/newsroom/apache-elevates-open-source-projects-gluten-and-polaris-to-top-level-status/)

### Inferences
- Los parches 4.2.2 (29-sep) de Kafka y la ausencia de 4.3 en Spark sugieren que Spark 4.3 (RTM con estado según docs) aún no salió a oct-2026; verificar en spark.apache.org antes de publicar.
- Cadencia Flink ~ 2 minors/año tras 2.0; Kafka ~ 3 minors/año (4.1 sep-25, 4.2 feb-26, 4.3 may-26) [inferido de las fechas].

### Gaps
- No se encontró el 8-K/SEC de cierre IBM–Confluent; solo nota de prensa IBM (primaria corporativa) y prensa.
- Fecha de salida de Pulsar 4.2 viene de un espejo de pruebas de Apache, no de pulsar.apache.org.
- Sin releases de Redpanda, Materialize, RisingWave, Polars, DuckDB verificados en esta pasada (DuckDB/Polars: ver notas previas, secundarias).

## 2. Spark 4.x: Connect, Declarative Pipelines, Real-Time Mode, AQE y tuning oficial

### Takeaway
Spark 4.1 introdujo Real-Time Mode (solo stateless en OSS 4.1; stateful planificado para 4.3 según docs); 4.2 añade Auto CDC SCD1 en Declarative Pipelines, QUALIFY, mejoras de stream-stream join. El tuning oficial recomienda AQE con coalesce y skew join por defecto, y fijar un número inicial grande de particiones de shuffle.

### Cited Findings
- Spark 4.0: ANSI por defecto, VARIANT, Connect, pyspark-client — [Spark 4.0.0 release](https://spark.apache.org/releases/spark-release-4-0-0.html) (de notas previas; no re-leído)
- RTM en Spark 4.1.0 soporta solo consultas stateless; stateful (agregaciones, joins, transformWithState) planificado para 4.3; la duración del trigger (5 min por defecto) es intervalo de checkpoint, no objetivo de latencia; todas las etapas corren simultáneamente, por lo que los task slots deben ser >= total de tareas — [Spark docs RTM (master, googlesource)](https://apache.googlesource.com/spark/+show/master/docs/streaming/real-time-mode.md); [Databricks docs RTM](https://docs.databricks.com/aws/structured-streaming/real-time)
- Latencia RTM: Databricks afirma p99 de un dígito de ms y una charla del Data+AI Summit habla de p99 <300 ms también para consultas con estado; esto contradice el alcance stateless-only de la doc OSS 4.1 (la afirmación es de producto Databricks, no OSS) — [Databricks blog](https://www.databricks.com/fr/blog/introducing-real-time-mode-apache-sparktm-structured-streaming); [DAIS session](https://www.databricks.com/dataaisummit/session/real-time-mode-technical-deep-dive-how-we-built-sub-300-millisecond)
- Spark 4.2.0 (notas oficiales): RTM trigger para PySpark (SPARK-54660, única mención de RTM); Auto CDC SCD Tipo 1 en Declarative Pipelines (SPARK-56249) con APIs Python y Connect; stream-stream non-outer join en modo Update; join state format V4; nombrado de fuentes/sinks (`.name()`, `IDENTIFIED BY`) para evolucionar queries sin romper checkpoints; QUALIFY; SQL scripting cursors; metric views; reparación automática de snapshots del state store; GetStatus en Connect — [Spark 4.2.0 release](https://spark.apache.org/releases/spark-release-4-2-0.html)
- Tuning oficial (docs 4.2): `spark.sql.shuffle.partitions`=200; AQE activo por defecto (desde 3.2); `coalescePartitions.enabled`=true; `advisoryPartitionSizeInBytes`=64 MB; `coalescePartitions.parallelismFirst`=true (la doc recomienda ponerlo en false en clústeres ocupados); `initialPartitionNum` no definido (recomendación: ponerlo alto, p. ej. 2000, y dejar que AQE coalesce); `skewJoin.enabled`=true, `skewedPartitionFactor`=5.0, `skewedPartitionThresholdInBytes`=256 MB; `autoBroadcastJoinThreshold`=10 MB, `broadcastTimeout`=300 s, hint BROADCAST fuerza broadcast; AQE puede convertir SMJ en broadcast o shuffled hash join (`maxShuffledHashJoinLocalMapThreshold`) — [Spark SQL performance tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)
- Photon: motor vectorizado en C++ integrado con el memory manager de Spark; paper SIGMOD 2022 (Best Industry Paper) reporta speedup promedio 3x vs Databricks Runtime anterior y hasta >10x (benchmark del propio vendor) — [Photon paper PDF](https://www.databricks.com/wp-content/uploads/2022/07/Photon-A-Fast-Query-Engine-for-Lakehouse-Systems.pdf); [BigDATAwire](https://www.bigdatawire.com/2022/06/30/databricks-scores-acm-sigmod-awards-for-spark-and-photon)
- Comet 1.0.0 (7-ago-2026, blog oficial DataFusion): 244 commits de 23 contribuidores en ~6 semanas desde 0.17.0; semver desde 1.0; soporta Spark 3.4–4.1 (experimental 4.2) y ANSI; >400 expresiones Spark; los 4 operadores de join, ventanas, shuffle nativo; fallback por-expresión vía codegen dispatch (antes caía el subárbol entero); corre la suite de tests de Spark (>24.000 tests) y fuzzing; el post no da speedups propios y remite a un TPC-DS 3 TB en EKS de AWS Labs ("significant speedups"); benchmarks tempranos fueron modestos — [Comet 1.0.0](https://datafusion.apache.org/blog/2026/08/07/datafusion-comet-1.0.0)
- Comet donado a DataFusion en mar-2024; 0.1.0 con 13 operadores y 106 expresiones — mismo post.
- Gluten: plugin que descarga cómputo de la JVM a motores nativos (Velox, ClickHouse) — [ASF news](https://news.apache.org/foundation/entry/the-apache-software-foundation-graduates-two-open-source-projects-from-incubator)

### Inferences
- Para oct-2026 la RTM stateful en OSS depende de Spark 4.3 (no publicado según la página de noticias); la afirmación de Databricks sobre stateful probablemente aplica a su runtime. Tratar como no equivalente.
- Comet, Gluten/Velox y Photon compiten en el mismo nicho (aceleración nativa de Spark); Photon es propietario (no se puede usar fuera de Databricks); para OSS la elección es Comet (Arrow/DataFusion, Rust) vs Gluten (Velox, C++). Evidencia independiente de rendimiento comparado: no encontrada.
- Receta práctica derivada de la doc: dejar AQE por defecto, subir `initialPartitionNum`, `parallelismFirst=false` en clústeres compartidos, usar hint BROADCAST para dimensiones >10 MB, y el skew join de AQE antes de salting manual (el salting sigue siendo necesario para agregaciones skewed y para joins no-SMJ [BG]).

### Gaps
- No se pudo abrir la página de notas de Spark 4.1.0 ni la doc 4.1.1 de RTM (404); datos 4.1 vienen de la doc master y notas previas.
- Sin benchmarks independientes de Gluten/Velox vs Comet vs Photon.
- Estado de Spark Connect y Declarative Pipelines en 4.2 más allá de lo listado: no verificado.

## 3. Flink 2.x

### Takeaway
Flink 2.0 (mar-2025) rompió compatibilidad (elimina DataSet, SourceFunction, Sink V1; sin compatibilidad de estado 1.x->2.x) e introdujo estado desagregado ForSt con ejecución asíncrona; 2.3 (jun-2026) añade partición adaptativa bajo skew, PTFs de changelog y mejoras de materialized tables.

### Cited Findings
- Flink 2.0: estado desagregado sobre DFS (ForSt), modelo de ejecución asíncrona, 7 operadores SQL stateful async (`table.exec.async-state.enabled`; 11 de 14 queries stateful de Nexmark lo soportan), Materialized Tables con integración Paimon, Java 17 por defecto/21 soportado, `config.yaml` reemplaza `flink-conf.yaml`, estado 1.x/2.x no garantizado compatible — [Flink 2.0.0 announcement](https://flink.apache.org/2025/03/24/apache-flink-2.0.0-a-new-era-of-real-time-data-processing/)
- Paper VLDB 2025 (vs Flink 1.20): hasta -94% duración de checkpoint, hasta 49x recuperación/rescale, hasta 50% ahorro de costo; autores son del equipo de desarrollo (Alibaba) — [VLDB 2025](https://www.vldb.org/pvldb/vol18/p4846-mei.pdf)
- Flink 2.3: PTFs `FROM_CHANGELOG`/`TO_CHANGELOG`; DDL de materialized tables (ALTER ADD/MODIFY/DROP, `START_MODE`); S3 nativo (AWS SDK v2, sin Hadoop/Presto); adaptive partition selection opt-in (hasta ~3x throughput bajo skew, cifra de las notas); capa "Applications"; checkpointing durante recovery (opt-in); cambio de comportamiento: SinkUpsertMaterializer falla en planificación si la upsert key difiere de la PK del sink (requiere `ON CONFLICT`); buffer de watermark alignment — [Flink 2.3 release notes](https://nightlies.apache.org/flink/flink-docs-release-2.3/release-notes/flink-2.3/)
- Semántica de garantías: el exactly-once de estado requiere que la fuente participe en snapshots; end-to-end requiere sink que participe en checkpoints; Kafka sink exactly-once con productores transaccionales; Elasticsearch/OpenSearch/Redis at-least-once; file sinks exactly-once — [Flink guarantees](https://nightlies.apache.org/flink/flink-docs-stable/docs/connectors/datastream/guarantees/) (la página no menciona 2PC explícitamente)
- Caso Uber IngestionNext: ingestión Kafka -> Flink -> Hudi reemplaza batch Spark; frescura de horas/días a minutos; -25% de cómputo; small files de Parquet mitigados con merge a nivel row-group (10x más rápido en compactación); problemas de skew por partición Kafka (mitigados con paralelismo alineado a particiones, cuotas por partición, autoscaling consciente de skew); sincronización checkpoint Flink/commit Hudi incrustando checkpoint IDs en metadata de commit — [Uber blog](https://uber.com/blog/from-batch-to-streaming-accelerating-data-freshness-in-ubers-data-lake/)

### Inferences
- [BG] 2PC de Flink: el sink pre-commitea en el checkpoint barrier y commitea al notificarse el checkpoint completado; esto no se confirmó en la doc consultada. El caso Uber (commit Hudi atado a checkpoint ID) ilustra el patrón.
- La ruptura 1.x->2.x implica que migrar requiere reprocesar estado o re-bootstrapping; planificar como proyecto, no upgrade.

### Gaps
- Estado de adopción real de ForSt en producción fuera de Alibaba: no encontrado. Notas de 2.1 y 2.2 no leídas.
- Paimon/Fluss: solo mención en 2.0; no investigado a fondo.

## 4. Kafka 4.x, KRaft, KIP-848, tiered storage, diskless, Streams, Redpanda, Pulsar, WarpStream, AutoMQ

### Takeaway
Kafka 4.2 declaró share groups (colas, KIP-932) listos para producción y 4.2 llevó el Streams Rebalance Protocol (KIP-1071) a GA con funciones limitadas. Tiered storage (KIP-405) está production-ready desde 3.9. Diskless (KIP-1150) está aceptado pero no hay implementación en Apache Kafka (solo fork Inkless de Aiven). Redpanda tiene un Jepsen de 2022 con bugs serios luego corregidos; no hay benchmark independiente reciente.

### Cited Findings
- Kafka 4.2.0: "Kafka Queues (Share Groups) is now production-ready" (KIP-932, más KIP-1222 RENEW, KIP-1206, KIP-1224, KIP-1226); KIP-1071 Streams Rebalance Protocol GA con conjunto limitado; DLQ en handlers de excepciones (KIP-1034) — [Kafka 4.2.0 announcement](https://kafka.apache.org/blog/2026/02/17/apache-kafka-4.2.0-release-announcement/)
- Kafka 4.3.0: cordoned log dirs (KIP-1066), límites de buffers de coordinadores, métricas de uso de retención, headers en state stores de Streams (KIP-1271/1285), KIP-1274 avisa cuando se usa el protocolo de rebalanceo clásico; deprecación del módulo streams-scala (KIP-1244, remoción en 5.0) y de `group.coordinator.rebalance.protocols` — [Kafka 4.3.0 announcement](https://kafka.apache.org/blog/2026/05/22/apache-kafka-4.3.0-release-announcement/)
- Kafka 4.3.1 incluye fix de una fuga de memoria nativa de RocksDB en Streams — [Kafka blog](https://kafka.apache.org/blog)
- Kafka 4.0: sin ZooKeeper (solo KRaft), KIP-848 GA, Java 17 brokers — [Instaclustr](https://www.instaclustr.com/blog/kafka-4-0-unveiled-key-changes-and-how-they-impact-developers/); [2 Minute Streaming](https://blog.2minutestreaming.com/p/apache-kafka-4-0-release) (de notas previas)
- Tiered storage KIP-405: página del KIP la marca production-ready desde Kafka 3.9; motivación: retención desacoplada de discos locales, recuperación/rebalanceo más rápido; KIP-950 permite deshabilitarlo por tópico (3.9) — [KIP-405](https://cwiki.apache.org/confluence/display/KAFKA/KIP-405%3A+Kafka+Tiered+Storage); [KIP-950](https://cwiki.apache.org/confluence/display/KAFKA/KIP-950:++Tiered+Storage+Disablement)
- KIP-1150 (Diskless Topics) aceptado el 2-mar-2026 (9 binding, 5 non-binding); es un KIP "meta" direccional; sub-KIPs 1163/1164/1165 aún en discusión; no está en Kafka mainline; única implementación en ejecución: fork Inkless de Aiven — [Aiven](https://aiven.io/blog/kip-1150-accepted-and-the-road-ahead); [Instaclustr](https://www.instaclustr.com/support/documentation/announcements/apache-kafka/kafka-diskless-proposals-status-insights/) (secundaria)
- WarpStream adquirido por Confluent el 9-sep-2024; Confluent lo describe para cargas grandes con requisitos de latencia relajados, en la nube del cliente — [BusinessWire](https://www.businesswire.com/news/home/20240909282386/en/Confluent-Acquires-WarpStream-to-Advance-Next-Gen-BYOC-Data-Streaming)
- AutoMQ: open source bajo Apache 2.0, liderado por empresa (no proyecto ASF) según su propia comparativa — [AutoMQ](https://www.automq.com/blog/top-open-source-diskless-kafka-alternatives) (competidor, sesgo)
- Redpanda: Jepsen (29-abr-2022, versiones 21.10.1–21.11.2) halló escrituras duplicadas por defecto sin idempotencia, offsets inconsistentes, lecturas abortadas/pérdida de escrituras transaccionales (corregidas en 21.11.15) y pérdida de mensajes confirmados sin resolver al publicar; no halló problemas por clock skew — [Jepsen Redpanda](https://jepsen.io/analyses/redpanda-21.10.1). Es un reporte antiguo; no hay Jepsen más reciente encontrado.
- Redpanda licensing: ediciones Community y Enterprise con clave de licencia; Iceberg Topics requiere licencia enterprise; desde 24.3 no se puede actualizar con features enterprise sin licencia válida; 25.3 trae cambios incompatibles de esquema Iceberg — [Redpanda licensing](https://docs.redpanda.com/current/get-started/licensing/); [Iceberg topics](https://docs.redpanda.com/streaming/25.3/manage/iceberg/about-iceberg-topics/). La doc no menciona BSL (el dato BSL es [BG]).
- Kafka vs Redpanda: serie de Jack Vanlightly (2023) con OpenMessaging Benchmark en 3x i3en.6xlarge: el resultado de 1 GB/s de Redpanda se degrada con 50 productores, con claves de registro y con TLS; al límite del NVMe (~2 GB/s) Kafka ~1900 MB/s vs Redpanda ~1400 MB/s; degradación en corridas >12 h. Autor afiliado a Confluent (según resumen secundario no verificado) — [Vanlightly](https://jack-vanlightly.com/blog/2023/5/15/kafka-vs-redpanda-performance-do-the-claims-add-up). Benchmark original de Redpanda (vendor): 4x m5n.8xlarge, Kafka 3.2.0, Redpanda 22.2.2.
- Pulsar: ver sección 1 (4.2 en mar-2026; LTS 4.0 fin de soporte activo oct-2026).

### Inferences
- Para cargas con latencia relajada y costo inter-AZ dominante, diskless/object-storage (WarpStream, AutoMQ, Inkless) es el candidato; para Kafka OSS puro, esperar sub-KIPs de KIP-1150 (no hay fecha).
- Con share groups GA, algunos casos de colas (RabbitMQ/SQS) podrían consolidarse en Kafka; madurez reciente (feb-2026), validar con carga propia.
- Evidencia independiente Kafka vs Redpanda reciente (post-2023) no existe en lo encontrado; toda comparación debe marcarse como vendor.

### Gaps
- No se verificó Kafka Streams EOS v2 en doc oficial (la página de documentación devolvió solo redirect) ni Schema Registry/Connect más allá de 4.3.
- Redpanda: licencia BSL, releases 25.x/26.x, y posible adquisición: sin verificar. Pulsar: sin benchmarks ni adopción verificada.
- WarpStream/AutoMQ: sin benchmarks de latencia independientes.

## 5. Trino/Presto, Ray/Daft, DuckDB/Polars, streaming DBs, benchmarks independientes

### Takeaway
Trino sigue con releases frecuentes (483 jul-2026) y ofrece ejecución tolerante a fallos opt-in para batch. Ray vs Daft: la evidencia disponible es de vendors en disputa. No se encontró un benchmark independiente y reciente que compare los motores; ClickBench está mantenido por ClickHouse.

### Cited Findings
- Trino FTE: desactivado por defecto; `retry-policy` = QUERY o TASK; TASK para batch grande y requiere exchange manager (S3/Azure/GCS/HDFS) con datos spooled cifrados; no todos los conectores lo soportan (Iceberg, Delta, Hive, BigQuery, etc. sí); 4 reintentos por defecto; puede añadir latencia en queries cortas — [Trino FTE docs](https://trino.io/docs/current/admin/fault-tolerant-execution.html)
- Ray vs Daft: Anyscale (vendor de Ray) afirma que Ray Data fue ~30% más rápido en promedio y ~3x en inferencia batch de imágenes en su reproducción del benchmark de Daft (Flotilla vs Ray Data vs EMR Spark); Daft publicó el benchmark original; no se encontró respuesta de Daft. Anyscale anunció en mar-2026 integración con NVIDIA cuDF con "80% menor costo" (nota de prensa) — [Anyscale blog](https://www.anyscale.com/blog/ray-data-daft-benchmarking-multimodal-ai-workloads); [HPCwire](https://www.hpcwire.com/bigdatawire/this-just-in/anyscale-cuts-multimodal-ai-data-processing-costs-by-80-with-nvidia-rtx-pro-4500-blackwell/)
- ClickBench: benchmark analítico con filtros por hardware, tuning y almacenamiento; repositorio ClickHouse/ClickBench; la página no declara mantenedor ni metodología en el texto leído — [ClickBench](https://benchmark.clickhouse.com/)
- Spark->Flink: no se encontró caso con números de Spark Structured Streaming a Flink. Hallazgos adyacentes: F5 Threat Stack pasó de Flink a Spark en EMR con costo de infraestructura ~10% del clúster Flink (blog F5); Tencent migró gradualmente de Spark Streaming a Flink con estado de 40 TB (charla ApacheCon 2022, sin cifras de costo); guía Ksolves (jun-2026, no es caso) recomienda correr ambos motores 2-4 semanas — [F5](https://www.f5.com/company/blog/optimizing-threat-stacks-data-pipeline-with-apache-spark-and-amazon-emr); [ApacheCon](https://apachecon.com/acasia2022/sessions/streaming-1235.html); [Ksolves](https://www.ksolves.com/blog/big-data/spark/migrating-to-apache-flink)
- Uber: upgrade Spark 2.4->3.3 de 2M+ apps: >60% de jobs con >10% mejora, ~50% menos runtime/recursos — [Uber](https://www.uber.com/blog/ubers-strategy-to-upgrading-2m-spark-jobs/) (resumen de buscador, no leído completo)
- Claims de RisingWave (22/27 Nexmark vs Flink), Materialize y comparaciones de streaming DBs: ver notas previas, todas vendor — [RisingWave](https://risingwave.com/blog/best-apache-flink-alternatives-2026/)

### Inferences
- Árbol de decisión (derivado de las fuentes): frescura en minutos hacia lakehouse -> Flink/Spark a Hudi/Iceberg (caso Uber: -25% cómputo vs batch); SLA sub-segundo stateless sobre Spark ya existente -> RTM (con límites); estado grande + event-time -> Flink 2.x; lógica embebida en servicio -> Kafka Streams (4.3 sigue invirtiendo: KIP-1071, headers en stores); SQL interactivo/federado -> Trino (FTE solo si se quiere ETL batch); IA multimodal/GPU -> Ray Data/Daft.
- Los costos de streaming "continuo" se ahorran respecto a batch si el batch recomputa grandes ventanas (caso Uber); pero el costo se desplaza a small files y compactación.
- Cualquier cifra de speedup de un motor sobre otro en estas notas es de vendor o paper de los propios autores; el redactor debe presentarlas como tal.

### Gaps
- Sin Nexmark/TPC-DS independientes recientes (Flink vs Spark vs RisingWave; Spark vs Trino vs DuckDB). ClickBench es de ClickHouse; no se pudo ver la lista de motores ni resultados.
- Sin verificar: Polars/DuckDB releases 2026 (solo secundarias en notas previas), Materialize/RisingWave versiones, Beam/Dataflow, Starburst/Athena, Presto, caso Netflix/Pinterest/Stripe/Shopify.
- Cálculos de dimensionamiento y costo de clúster: no hay fuentes primarias recopiladas; usar guías de proveedor.

## 6. Semántica de streaming (resumen y límites de verificación)

### Takeaway
Solo se verificaron con fuente las garantías de conectores de Flink y puntos de Kafka/Spark; los conceptos (event time, watermarks, ventanas, dualidad stream-tabla, backpressure) quedan como conocimiento de fondo.

### Cited Findings
- Spark 4.2 añade stream-stream non-outer join en modo Update y state format V4; el watermark/estado se gestiona vía state store con checksums y reparación de snapshots — [Spark 4.2.0 release](https://spark.apache.org/releases/spark-release-4-2-0.html)
- Flink 2.3: PTFs ahora manejan late data; buffer en watermark alignment (por defecto 3) — [Flink 2.3 notes](https://nightlies.apache.org/flink/flink-docs-release-2.3/release-notes/flink-2.3/)
- Uber: end-to-end exactly-once efectivo exige alinear el offset del checkpoint con el commit del sink (Hudi) — [Uber](https://uber.com/blog/from-batch-to-streaming-accelerating-data-freshness-in-ubers-data-lake/)
- Jepsen documenta que sin idempotencia habilitada los productores Kafka-compatibles pueden duplicar escrituras, y que los rebalanceos pueden rebobinar posiciones dentro de una transacción — [Jepsen Redpanda](https://jepsen.io/analyses/redpanda-21.10.1)

### Inferences
- [BG, no verificado] Definiciones de Akidau (Dataflow Model), Kafka EOS (productor idempotente + transacciones + `read_committed`; Streams `exactly_once_v2`), backpressure credit-based de Flink, ventanas y allowed lateness: no se pudieron confirmar en la doc oficial en esta sesión.

### Gaps
- Doc oficial de Kafka (semantics) y de Flink (watermarks, 2PC sink) no recuperadas; el redactor debe citar la doc o marcar como conocimiento general.
