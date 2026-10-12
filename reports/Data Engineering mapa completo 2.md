# El catálogo toma el mando en Data Engineering

**Conclusión central (estado a 12-oct-2026):** la ingeniería de datos dejó de decidirse por el motor de cómputo y pasó a decidirse en cuatro fronteras: el **formato de tabla abierto** (Iceberg como lengua franca de interoperabilidad, con Delta convergiendo hacia el mismo diseño), el **catálogo** (que pasa a coordinar commits, gobierno y credenciales), el **contrato y la propiedad del dato** (donde la evidencia sitúa la mayoría de los fallos) y un **mercado que se reempaqueta por fusiones**. Dos señales técnicas lo ilustran: Delta Lake está en la versión **4.4.1** (5-oct) y su protocolo ya delega en el catálogo la verdad sobre qué commit tuvo éxito ([delta.io](https://delta.io/blog/), [releases](https://github.com/delta-io/delta/releases)); Iceberg v4 propone que la ubicación de la tabla la suministre el catálogo y que cada commit toque un solo fichero ([spec](https://raw.githubusercontent.com/apache/iceberg/main/format/spec.md)). En procesamiento, Spark 4.2.0 (14-jul-2026), Flink 2.3.0 (25-jun-2026) y Kafka 4.3.x (mayo-junio 2026) consolidan un patrón de "un código, dos ejecuciones" más que la desaparición de Lambda ([Spark](https://spark.apache.org/news/index.html), [Flink](https://flink.apache.org/downloads/), [Kafka](https://kafka.apache.org/community/downloads/)). En regulación, el Reglamento (UE) 2026/1744 retrasó los sistemas de alto riesgo del AI Act (Anexo III a 2-dic-2027; Anexo I a 2-ago-2028), mientras la parte GDPR/datos del Digital Omnibus **no está acordada** ([Reg. 2026/1744](https://publications.europa.eu/resource/celex/32026R1744)). Esta segunda versión sustituye a la primera en todo lo que difiere: corrige 26 afirmaciones (sección 17), entre ellas siete centrales (Delta 5.0 no existe; DuckDB Labs–AWS sí está confirmado; ODCS v3.2.0 sí está publicada; Soda Core pasó a Elastic License 2.0; MetricFlow es Apache 2.0 desde oct-2025; Debezium 3.7.0.Final; IBM–Confluent cerrada), elimina dos cifras sin respaldo (8-12 % de adopción de data mesh; "~20 ingenieros" para build-vs-buy) y etiqueta cada tema con su nivel de evidencia. El mensaje operativo: elija formatos abiertos y SQL portable, trate el catálogo como pieza de control, ponga contratos ejecutables en las 5-10 interfaces críticas y no tome decisiones de coste con las cifras de lista de este informe, que están verificadas solo en parte.

## Índice

1. Convenciones de confianza, método y alcance
2. Fundamentos y conceptos clave
3. Arquitecturas: batch, streaming, Lambda, Kappa, lakehouse, medallion, mesh y otras
4. Pipelines, ingesta, transformación y orquestación
5. Almacenamiento: formatos de tabla, catálogos, formatos de fichero, warehouses y operación
6. Procesamiento batch y streaming
7. Modelado de datos y capa semántica
8. Calidad, observabilidad, lineage, contratos y gobernanza
9. Seguridad y compliance
10. Plataformas cloud, on-premise, híbrido, soberanía y América Latina
11. Stack moderno por categoría
12. Patrones avanzados, anti-patrones e incidentes públicos
13. Mejores prácticas de producción: checklists y runbooks
14. Escalabilidad, coste y mantenimiento
15. Evolución reciente 2023-2026, IA y rol del data engineer
16. Temas con poca literatura consolidada o en evolución rápida
17. Qué cambió respecto a la primera versión
18. Confianza y lo no verificado
19. Resumen ejecutivo
20. Referencias

## 1. Convenciones de confianza, método y alcance

Este informe sintetiza ocho cuadernos de investigación de una segunda pasada con verificación en fuentes primarias (papers, documentación y comunicados oficiales, textos legales leídos en el Diario Oficial) y el informe de la primera pasada, que se usa como base solo donde no contradice a la segunda. Etiquetas usadas en todo el texto: **[Fuente]** significa que la URL citada afirma lo escrito (puede ser de proveedor; se indica el sesgo); **[Práctica consolidada]** es conocimiento estable del oficio, no verificado contra una fuente de 2026 (referencias canónicas: *Designing Data-Intensive Applications* de Kleppmann y Riccomini, 2ª ed., y *Fundamentals of Data Engineering* de Reis y Housley); **[Inferencia]** es juicio del análisis, incluidos todos los umbrales y heurísticas; **[No verificado]** es una afirmación que circula pero no pudo contrastarse. Dos advertencias de método afectan a la lectura. Primera, las herramientas de lectura resumieron páginas con un modelo pequeño: las fechas de GitHub Releases aparecen sin año y el año (2026) se infiere por contexto; donde importa, se marca "año inferido". Segunda, la sección 9 es investigación técnica, **no asesoramiento legal**: valide con DPO o asesoría jurídica.

La fecha de referencia es el 12-oct-2026. Los precios de lista se citan solo cuando una página oficial los mostró; para BigQuery, Fabric, Databricks y la tarifa por crédito de Snowflake fuera de la tabla oficial, el informe dice explícitamente qué no está verificado (ver 5.6 y 10.1).

## 2. Fundamentos y conceptos clave

Esta sección mezcla [Práctica consolidada] con los resultados verificados de papers y documentación primaria. Cada fila sigue el esquema pedido: qué es, cuándo importa, límites, alternativas y madurez.

| Concepto | Esencia | Cuándo importa / trampa | Alternativas y madurez |
|---|---|---|---|
| OLTP vs OLAP | OLTP: transacciones cortas, filas, normalizado. OLAP: escaneos agregados, columnar | Zero-ETL y HTAP difuminan la frontera pero no la eliminan | Muy alta [Práctica consolidada] |
| ETL vs ELT | ELT domina con cómputo y almacenamiento desacoplados | ETL persiste para enmascarar PII antes de cargar, edge y streaming | Muy alta [Práctica consolidada] |
| Batch vs streaming | Datos acotados vs no acotados; en streaming importan event time, watermarks, triggers y estado | El modelo Dataflow separa qué, dónde (ventanas), cuándo (triggers) y cómo se refina el resultado ([Akidau, VLDB 2015](https://www.vldb.org/pvldb/vol8/p1792-Akidau.pdf)) | Alta |
| Idempotencia | Reejecutar produce el mismo estado: overwrite de partición, MERGE por clave | Base de reintentos y backfills; Airflow recomienda UPSERT en lugar de INSERT y tratar tareas como transacciones ([Airflow best practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)) | Alta |
| Exactly-once | Efecto final igual al de ejecución sin fallos, acotado a una frontera | Ver 2.1 | Alta dentro de la frontera |
| CDC | Log-based (WAL/binlog) vs consulta o trigger | Snapshot inicial, DDL, orden entre tablas, PII (ver 4.3) | Alta |
| Evolución de esquema | Iceberg identifica columnas por ID, lo que hace seguro renombrar y reordenar ([spec](https://iceberg.apache.org/spec/)) | Un contrato añade semántica, SLA y owner al esquema | Alta |
| CAP / PACELC | CAP discute partición; PACELC añade latencia vs consistencia sin partición ([Abadi](https://cs.umd.edu/~abadi/papers/abadi-pacelc.pdf)) | Kleppmann critica ambigüedades de CAP y propone "delay-sensitivity" ([2015](https://martin.kleppmann.com/2015/09/17/critique-of-the-cap-theorem.html)) | Herramienta de razonamiento, discutida |
| Particionamiento | Tiempo, hash, rango; transformaciones ocultas (Iceberg) o clustering (Delta) | Sobre-particionar genera ficheros pequeños | Alta |
| HTAP | OLTP y OLAP en un sistema | Exige aislamiento físico; en TiDB, réplica columnar asíncrona (learner de Raft) ([VLDB 2020](https://www.cs.purdue.edu/homes/csjgwang/CloudNativeDB/TiDBVLDB20.pdf)) | Media; evidencia sobre todo del proveedor |

### 2.1 Exactly-once: qué garantiza cada frontera

**[Fuente]** El productor idempotente de Kafka da exactly-once por partición (sin duplicados, sin pérdida, en orden) con impacto "despreciable"; las transacciones permiten escrituras atómicas multi-partición con commit de offsets en la misma transacción y consumidores `read_committed`. La garantía de Kafka Streams es "dentro del alcance del procesamiento interno": llamadas RPC a stores externos o lógica no determinista quedan fuera ([Confluent](https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/)). Los costes medidos en 2017 con Kafka 0.11 (mensajes de 1 KB, transacciones de 100 ms) fueron -3 % de throughput frente a `acks=all` y entre -15 % y -30 % en Kafka Streams con commit de 100 ms, sin sobrecoste con commit de 30 s; **son cifras antiguas, no revalidadas en 2026**. En Flink, los checkpoints son el punto de coordinación de un two-phase commit: el sink cierra su transacción en pre-commit y confirma cuando el JobManager declara completo el checkpoint; exige un sistema externo transaccional y commits idempotentes, y la salida solo es visible tras el commit, lo que fija la latencia de visibilidad ([Flink blog](https://flink.apache.org/2018/02/28/an-overview-of-end-to-end-exactly-once-processing-in-apache-flink-with-apache-kafka-too/)). La documentación actual de garantías añade que el Kafka sink es exactly-once con productores transaccionales, los file sinks también, y Elasticsearch/OpenSearch/Redis son at-least-once ([Flink guarantees](https://nightlies.apache.org/flink/flink-docs-stable/docs/connectors/datastream/guarantees/)). Uber ilustra el patrón extremo a extremo: incrusta el ID de checkpoint de Flink en los metadatos del commit de Hudi ([Uber](https://uber.com/blog/from-batch-to-streaming-accelerating-data-freshness-in-ubers-data-lake/)).

**[Inferencia]** "Exactly-once" extremo a extremo equivale a límite transaccional más idempotencia en el último salto. El coste de latencia vive en el intervalo de commit/checkpoint. Regla práctica: declare siempre la frontera ("exactly-once entre Kafka y Kafka", "effectively-once hacia Iceberg con ID de checkpoint") y nunca el eslogan.

### 2.2 Lo que los papers fundacionales sostienen (y lo que no)

| Fuente | Tesis acotada | Salvedad verificada |
|---|---|---|
| Armbrust et al., Lakehouse, CIDR 2021 ([paper](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf)) | La arquitectura de dos niveles (lake + warehouse) "se marchitará" ante formatos abiertos con ACID, ML de primera clase y rendimiento de estado del arte | Es una **predicción**; el benchmark (TPC-DS SF 30.000, 99 consultas, 960 vCPU) es de Databricks sobre su motor, con caché SSD; con caché fría Delta Engine fue 18 % más lento |
| Armbrust et al., Delta Lake, VLDB 2020 ([paper](https://www.vldb.org/pvldb/vol13/p3411-armbrust.pdf)) | Log de transacciones en el object store con put-if-absent y concurrencia optimista | Límites propios declarados: transacciones solo por tabla, latencia de segundos (no ms), sin índices secundarios, "varias transacciones por segundo" de tasa de commits |
| Akidau et al., Dataflow Model, VLDB 2015 ([paper](https://www.vldb.org/pvldb/vol8/p1792-Akidau.pdf)) | Modelo unificado con corrección, latencia y coste ajustables | Critica Lambda por **complejidad** (dos sistemas), no por incorrección; los watermarks suelen ser heurísticos |
| Kreps, Questioning the Lambda Architecture, 2014 ([O'Reilly](https://www.oreilly.com/radar/questioning-the-lambda-architecture/)) | Mantener la misma lógica en dos sistemas es el coste; Kappa = log retenido + segundo job que reprocesa y conmuta | Evidencia de LinkedIn/Samza (pasada 1) |
| Dehghani, Data Mesh, 2020 ([principios](https://martinfowler.com/articles/data-mesh-principles.html), [monolito a mesh](https://martinfowler.com/articles/data-monolith-to-mesh.html)) | Cuatro principios "colectivamente necesarios y suficientes" | Sin umbrales numéricos ni métricas de éxito; el autor reconoce que el modelo centralizado "puede funcionar" con dominios simples y pocos casos de consumo |

DDIA 2ª edición (Kleppmann y Riccomini) figura como publicada en febrero de 2026 con 650 páginas ([O'Reilly](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/colophon01.html)); no se leyó su texto, por lo que ninguna afirmación de capítulo se apoya en ella.

## 3. Arquitecturas: batch, streaming, Lambda, Kappa, lakehouse, medallion, mesh y otras

Las arquitecturas no compiten entre sí: ocupan ejes distintos (procesamiento, almacenamiento, layout, organización, integración) y se combinan. La pregunta útil pasó de "¿uno o dos pipelines?" a "¿qué frescura justifica el coste, por consumidor?". Esta sección documenta cada una con fuentes y cierra con la tabla comparativa (3.7) y un marco de decisión (3.8).

### 3.1 Lambda, Kappa y unificado: tres rutas documentadas

**Descripción y contexto.** Lambda mantiene una capa batch y otra de velocidad; Kappa elimina la batch conservando el log y reprocesando con un segundo job; la ruta "unificada" escribe una sola lógica con un modelo (Beam/Dataflow, Flink SQL) y la ejecuta en modo batch o streaming.

**Evidencia por caso (todas [Fuente], de empresa o paper de los propios autores):**

| Caso | Qué hicieron | Cifras | Lectura |
|---|---|---|---|
| LinkedIn, mar-2023 ([blog](https://www.linkedin.com/blog/engineering/data-streaming-processing/unified-streaming-and-batch-pipelines-at-linkedin-reducing-proc), [BigDATAwire](https://www.bigdatawire.com/2023/04/05/apache-beam-cuts-processing-time-94-for-linkedin)) | Abandonaron dos bases de código por un pipeline Apache Beam (runners Samza y Spark) | Backfill de 7 h a 25 min (-94 %); el batch unificado redujo memoria y CPU aproximadamente a la mitad frente al job de streaming; "11 veces" menos coste de servicio según su análisis | El -94 % es coste del **backfill como batch frente a como streaming**, no ahorro total de plataforma; no mezclar las tres cifras |
| Uber, arXiv 2021 ([paper](https://arxiv.org/pdf/2104.00087)) | Rechazan Kappa puro: limitan la retención de Kafka a "unos pocos días" y crean "Kappa+" en Flink, que relee datos archivados en Hive; además un modo SQL que compila la misma consulta a dos jobs | Billones de mensajes y petabytes por día (oct-2020) | Los autores lo califican de área "activa de investigación" |
| Airbnb Riverbed, 2023 ([InfoQ](https://www.infoq.com/news/2023/10/airbnb-riverbed-introduction)) | Eligen Lambda (Kafka online, Spark offline) por backfill y reconciliación | 2,4 mil millones de eventos y 350 millones de documentos/día; más de 50 vistas materializadas | Elección consciente, no deuda |
| Google, Dataflow Model ([paper](https://www.vldb.org/pvldb/vol8/p1792-Akidau.pdf)) | Un cliente de MillWheel con streaming débil + MapReduce nocturno "para generar la verdad" perdió la confianza de los usuarios y reimplementó con consistencia fuerte | n/d | Riesgo de confianza en el patrón "verdad nocturna" |
| Shopify ([ingeniería](https://shopify.engineering/bfcm-live-map-2021-apache-flink-redesign)) | Flink desde 2021; prueba de concepto de joins con más de 10 TB de estado | "100 % de corrección" en la prueba | Sin comparativa Lambda/Kappa |
| Fresha, Current London 2026 ([charla](https://current.confluent.io/post-conference-videos-26/lambda-architecture-in-2025-kafka-views-and-the-evolving-data-platform-ldn26)) | Siguen con Lambda por coste: tablas materializadas cada 20 min más vistas con CDC en vivo | n/d (pasada 1) | Charla de conferencia |

**[Inferencia]** Nadie reporta Kappa "puro": Uber lo descarta por coste de retención; LinkedIn y Google unifican el **código** y mantienen dos modos de ejecución. El resultado práctico es "un código, dos ejecuciones". Extrapolar el -94 % de LinkedIn a otras organizaciones no está justificado.

**Cuándo usar / cuándo no.** Lambda: backfill y reconciliación críticos, o batch ya existente al que se añade baja latencia; evitar en proyectos nuevos sin necesidad dual y con equipos pequeños. Kappa: log barato y largo, equipo de streaming; evitar si la retención está limitada por coste u operación (caso Uber). Unificado: lógica expresable en la intersección de capacidades; evitar con lógica muy específica por motor, ya que Akidau advierte que las capas como Summingbird "imponen limitaciones". **Madurez:** Lambda alta pero en declive/nicho; Kappa media y rara en forma pura; unificado alta en grandes empresas (síntesis en la tabla 3.7).

**Streaming hacia tablas abiertas.** Confluent Tableflow materializa topics de Kafka como tablas Iceberg o Delta con frescura de unos 5 minutos ([docs](https://docs.confluent.io/cloud/current/topics/tableflow/overview.html), pasada 1). Kai Waehner (con sesgo de proveedor) sostiene que los table formats refuerzan Kappa ([Waehner](https://www.kai-waehner.de/blog/tag/delta-lake/)). **[Inferencia]** el lakehouse unificado ofrece una sola capa con ACID y upserts a latencia de minutos; el sub-segundo exige Kafka/Flink o un OLAP en tiempo real delante.

### 3.2 Lakehouse

**Descripción.** Sistema de gestión de datos sobre almacenamiento barato de acceso directo con ACID, versionado, auditoría, indexación, caché y optimización de consultas, apoyado en una capa de metadatos sobre el object store ([CIDR 2021](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf)). El paper atribuye a la arquitectura de dos niveles problemas de fiabilidad, obsolescencia ("días" en las cargas al warehouse), analítica avanzada limitada y coste total; cita una encuesta Dimensional Research/Fivetran con 86 % de analistas usando datos desactualizados.

**Cuándo usar.** BI y ML sobre una capa abierta; multi-motor; volumen alto. **Cuándo no.** Latencia sub-segundo y transacciones multi-tabla intensivas (límites del propio paper de Delta). **Ventajas.** Formatos abiertos, una sola copia. **Limitaciones.** Mantenimiento (compactación, expiración), tasa de commits limitada por tabla, catálogos en disputa. **Alternativas.** Warehouse cloud con tablas Iceberg gestionadas; OLAP en tiempo real para serving. **Madurez:** alta y creciente; Thoughtworks lo situó en Trial en abril de 2023, sugiriendo Delta, Iceberg y Hudi, y hoy está fuera de la edición vigente ([Radar](https://www.thoughtworks.com/radar/techniques/lakehouse-architecture)). **Evidencia independiente de éxito/fracaso: inexistente** más allá de papers de proveedor y blips; Netflix creó Iceberg en 2018 y las cifras de escala (cientos de PB) provienen de reportes secundarios ([Data Engineer Things](https://blog.dataengineerthings.org/i-spent-4-hours-learning-how-netflix-operates-apache-iceberg-at-scale-c93a9f94c539)).

### 3.3 Medallion

**Descripción.** Convención de capas: bronze guarda el dato "tal cual" con metadatos de carga, silver lo conforma y deduplica, gold ofrece modelos de lectura por proyecto ([Databricks glossary](https://www.databricks.com/glossary/medallion-architecture), pasada 1; la página no lista desventajas). Es una convención, no una arquitectura completa ni un estándar.

**Críticas documentadas ([Fuente], opinión de practicantes, sin métricas).** Daniel Beach sostiene que es Kimball renombrado, que tres capas requieren más almacenamiento y cómputo, que "Gold" es en realidad un data mart y que la mención más temprana que halló en Databricks es del 2-jun-2020; recomienda modelar el lakehouse como un warehouse y un comentarista advierte contra organizar equipos por capa ([Data Engineering Central](https://dataengineeringcentral.substack.com/p/medallion-architecture-truth-or-fiction)). Otros posts enumeran silver convertido en cajón de sastre, proliferación de golds con definiciones divergentes ("metric drift"), cómputo impredecible por backfills y que "medallion describe estados de datos, no significado"; los defensores replican que es una convención compartida ([DevGenius](https://blog.devgenius.io/when-to-break-medallion-architectures-rules-and-what-you-re-actually-betting-on-0c606dfdd1dc), de pago, no leído). Thoughtworks no tiene blip de medallion.

**[Inferencia]** Los modos de fallo son de gobernanza y modelado, no del concepto; la crítica de coste y latencia es plausible pero **no está cuantificada en ninguna fuente**. Mapeo práctico: bronze = staging crudo con contrato en el borde; silver = integración (3NF o Data Vault opcional); gold = marts Kimball más capa semántica (ver sección 7). El mapeo con dbt (staging, intermediate, marts) es casi 1:1 ([dbt best practices](https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview)). **Madurez:** alta como convención; evidencia empírica: cero.

### 3.4 Data mesh

**Descripción.** Cuatro principios: propiedad descentralizada por dominio, datos como producto, plataforma self-serve y gobernanza federada computacional ([Dehghani](https://martinfowler.com/articles/data-mesh-principles.html)). Dehghani advierte que exige estructura organizacional, incentivos y arquitectura de soporte, y que el equilibrio global/local es "un arte".

**Evidencia de adopción (todas cualitativas):**
- Thoughtworks Radar: Assess (nov-2019, may-2020), Trial (oct-2020, oct-2021, mar-2022) y luego fuera de la edición vigente. Los textos escalan las advertencias: herramientas limitadas (2020), fricción con tecnologías existentes (2021), "altos costos de integración" y adopción "confinada a partes de grandes organizaciones" (2022) ([Radar](https://www.thoughtworks.com/radar/techniques/data-mesh)). El Radar de nov-2025 puso "Standalone data engineering teams" en Hold y data mesh no figura en la página listada ([rmoff](https://rmoff.net/2025/11/05/tech-radar-nov-2025-data-blips)).
- Gartner Hype Cycle 2022 la sitúa en "innovation trigger" con predicción "obsolete before plateau" (**vía fuente secundaria**; el informe es de pago) ([Atlan](https://atlan.com/gartner-data-mesh)). La cifra "solo 18 % alcanzó la madurez de gobernanza necesaria" (encuesta Gartner 2021) también es secundaria.
- Un estudio con 15 expertos halló dificultad con la gobernanza federada y con asumir responsabilidad de los data products ([arXiv 2302.01713](https://arxiv.org/abs/2302.01713)).
- Aprendizajes anónimos: 3 sprints para el primer data product, equipos con objetivos en conflicto, data products pedidos pero sin uso; sin empresas nombradas ni muestreo ([datamesh-architecture.com](https://datamesh-architecture.com/real-world-learnings)).
- Zalando es el único caso con escala medible: lago de más de 20 PB, más de 5.000 data products, 350 equipos descentralizados y unos 6.000 usuarios mensuales (~80 % de la plantilla); el post de AWS **no usa el término "data mesh"** y las mejoras que reporta (consultas 75 % más rápidas tras migrar el serving layer a Redshift) son efecto de Redshift, no de mesh ([AWS](https://aws.amazon.com/blogs/big-data/how-zalando-innovates-their-fast-serving-layer-by-migrating-to-amazon-redshift)).

**Corrección explícita.** La cifra "8-12 % de adopción" de la primera versión **no aparece** en el abstract del arXiv 2606.08266 que se citó (leyeron 64 fuentes y dicen que "las encuestas reportan altas tasas de fracaso" sin números) ([arXiv](https://arxiv.org/abs/2606.08266)). Queda **[No verificado]** y no debe usarse como hecho.

**Cuándo usar.** Muchos dominios autónomos con plataforma de datos madura y capacidad de producto. **Cuándo no.** Pocos dominios, equipos sin capacidad analítica local (Dehghani concede que el modelo central puede bastar). **Alternativas.** Plataforma central con contratos; pilotos de dos dominios como máximo (recomendación de Starburst, con sesgo de federación: [Starburst](https://www.starburst.io/blog/data-mesh-what-happened/)). **Madurez:** baja-media. **[Inferencia]** Lo documentado como fracaso es organizacional (capacidad, incentivos), coherente con las advertencias del propio autor; no hay postmortems con nombre de una empresa que lo abandonara.

### 3.5 Otras arquitecturas e integraciones

| Arquitectura | Descripción y evidencia | Cuándo usar / no | Contras documentados | Madurez |
|---|---|---|---|---|
| Data fabric | "Diseño de gestión de datos nuevo y en evolución" con grafos de conocimiento y metadatos activos; "no es una sola herramienta"; cerca del valle de desilusión en el Hype Cycle 2024 (definición vía proveedores) ([TopQuadrant](https://topquadrant.com/blog/metadata-and-data-fabric), [Denodo](https://www.denodo.com/en/document/analyst-report/gartner-hype-cycle-data-management-2024)) | Metadatos activos sobre fuentes distribuidas / basta un warehouse central | Concepto difuso, definición contestada | Baja-media |
| Event-driven | Fowler distingue cuatro patrones (event notification, event-carried state transfer, event sourcing, CQRS) y advierte que el problema central es confundirlos ([Fowler](https://martinfowler.com/articles/201701-event-driven.html)) | Desacople e integración / consistencia fuerte multi-paso | Flujo implícito, copias, replay con dependencias externas, evolución de esquema de eventos | Alta |
| Reverse ETL | Mueve datos transformados del warehouse a herramientas de negocio; asociado al CDP composable ([CDP.com](https://cdp.com/articles/reverse-etl-vs-cdp/), [Redpoint](https://www.redpointglobal.com/blog/composability-is-not-just-reverse-etl/)) | Activación de segmentos en SaaS / basta integración directa | Latencia batch, duplicación de PII, riesgo de escribir datos erróneos en sistemas operacionales; **fuentes con conflicto de interés** | Media |
| Zero-ETL | "Conjunto de integraciones que minimiza la necesidad de ETL" (Aurora/RDS a Redshift, DynamoDB a SageMaker Lakehouse, etc.), "casi tiempo real" sin cifra ni lista de limitaciones ([AWS](https://aws.amazon.com/what-is/zero-etl/)) | Analítica fresca sobre OLTP del mismo proveedor / multi-cloud | **[Inferencia]** replicación CDC gestionada y propietaria; acoplamiento al proveedor | Media, creciente |
| HTAP | TiDB aísla con réplica columnar asíncrona; en CH-benCHmark, más clientes OLTP reducen el throughput OLAP como máximo 5 %, mientras MemSQL cae más de 5x en el transaccional al crecer los analíticos; con 32 clientes analíticos menos del 50 % de las consultas ven retardo de réplica <100 ms ([TiDB VLDB 2020](https://www.cs.purdue.edu/homes/csjgwang/CloudNativeDB/TiDBVLDB20.pdf)) | OLTP con analítica fresca / OLAP masivo y complejo | Autoevaluación de PingCAP | Media |

### 3.6 Warehouse y lake clásicos

El warehouse acopla cómputo y almacenamiento propios y oculta el mantenimiento; el lake clásico ofrece objeto barato sin ACID por defecto y degenera en "swamp" sin gobierno [Práctica consolidada]. Ambos siguen siendo la base instalada; su convergencia en tablas Iceberg gestionadas se detalla en 5.6 y 10.

### 3.7 Tabla comparativa de arquitecturas

Columnas "Madurez" y "Cuándo" son [Inferencia] salvo celdas con enlace.

| Arquitectura | Eje | Evidencia leída | Cuándo usar | Cuándo no | Ventajas | Limitaciones / contras | Complejidad | Madurez |
|---|---|---|---|---|---|---|---|---|
| Batch | Procesamiento | [Práctica consolidada] | Horas de latencia, backfills | Decisiones en segundos | Simple, barato, reproducible | Latencia | Baja | Muy alta |
| Streaming | Procesamiento | Dataflow ([VLDB 2015](https://www.vldb.org/pvldb/vol8/p1792-Akidau.pdf)) | Fraude, alertas, apps con estado fresco | Equipos sin experiencia en estado y orden | Baja latencia | Estado, orden, operación | Alta | Alta |
| Lambda | Procesamiento | Kreps, Akidau, Uber, Airbnb, LinkedIn | Backfill/reconciliación crítica | Equipo pequeño; proyecto nuevo | Pragmático | Dos bases de código; confianza si la verdad es nocturna | Media-alta | Alta, nicho |
| Kappa | Procesamiento | Kreps, Uber | Log retenido barato y equipo de streaming | Retención corta por coste/ops | Una ruta de código | Retención larga, throughput ([Uber](https://arxiv.org/pdf/2104.00087)) | Alta | Media; rara pura |
| Unificado (Beam, Kappa+) | Procesamiento | Akidau, LinkedIn, Uber | Un código, dos ejecuciones | Lógica específica de motor | Un código | Intersección de capacidades; bordes en backfills | Media | Alta en grandes empresas |
| Warehouse | Almacenamiento | CIDR (descripción) | BI/SQL, equipos pequeños | ML sobre no estructurado masivo | Gobierno, SQL | Coste a escala, formatos propietarios | Baja | Muy alta |
| Lake | Almacenamiento | CIDR (descripción) | Crudo barato | Sin gobierno | Barato | Sin ACID, swamp | Media | Alta (legado) |
| Lakehouse | Almacenamiento | CIDR, Delta VLDB, spec Iceberg | BI + ML, multi-motor | Sub-segundo; multi-tabla intensivo | ACID, abierto | Transacciones por tabla, pocos commits/s ([VLDB 2020](https://www.vldb.org/pvldb/vol13/p3411-armbrust.pdf)) | Media-alta | Alta |
| Medallion | Layout | Solo vendor y opinión | Refinamiento progresivo | Latencia extrema | Linaje, reprocesos | Capas sobrecargadas, golds divergentes | Baja | Alta (convención) |
| Data mesh | Organización | Dehghani, Radar, Zalando | Muchos dominios autónomos y plataforma madura | Pocos dominios | Escala organizativa | Costes de integración, adopción parcial ([Radar](https://www.thoughtworks.com/radar/techniques/data-mesh)) | Muy alta (organizativa) | Baja-media |
| Data fabric | Metadatos | Definición vía proveedores | Fuentes distribuidas | Basta warehouse central | Acceso sin mover datos | Concepto difuso | Alta | Baja-media |
| Event-driven | Integración | Fowler | Desacople | Consistencia multi-paso | Desacople | Depuración, replay | Media-alta | Alta |
| Reverse ETL | Activación | Solo proveedores | Segmentos en SaaS | Integración directa suficiente | Cierra el ciclo | Latencia, PII | Baja-media | Media |
| Zero-ETL | Integración | AWS | Mismo proveedor | Multi-cloud | Sin pipeline propio | Acoplamiento | Baja | Media |
| HTAP | Almacenamiento | TiDB | OLTP + analítica fresca | OLAP masivo | Un sistema | Contención sin aislamiento físico | Alta | Media |

### 3.8 Marco de decisión de arquitectura

**[Inferencia]** (los umbrales son criterios del análisis, sin respaldo empírico):

| Contexto | Combinación recomendada | Riesgo a vigilar |
|---|---|---|
| 1-5 personas, <1 TB, latencia de horas | Warehouse cloud + ELT con dbt + orquestador gestionado | Sobre-ingeniería (15 herramientas para <1 TB) |
| 5-30 personas, varias fuentes, latencia de minutos | Lakehouse (Iceberg o Delta) con capas bronze/silver/gold, CDC a bronze, micro-batch | Mantenimiento de ficheros y catálogo |
| Segundos de latencia, casos operacionales | Event-driven con Kafka/Flink + OLAP en tiempo real para servir; tabla abierta para histórico | Coste de operar estado; DLQ y backfills |
| Muchos dominios autónomos y plataforma central estable | Mesh parcial: dominios propietarios de data products sobre plataforma común y contratos | Evidencia cualitativa; pilotos de dos dominios |
| Regulado, auditable | Capa de integración con historia (Data Vault o SCD2 + bitemporal), controles de acceso por tags | Coste de modelado; ver sección 7 |

**Regla de Kreps, aún vigente:** batch si no hay sensibilidad a la latencia, streaming si la hay, y no ambos salvo necesidad ([Kreps](https://www.oreilly.com/radar/questioning-the-lambda-architecture/)). Fije la latencia **por consumidor**, no por pipeline.

## 4. Pipelines, ingesta, transformación y orquestación

### 4.1 Orquestación: Airflow 3.x, Dagster, Prefect y las categorías vecinas

**Descripción.** Un orquestador programa, ordena y reintenta trabajo y, en los modelos orientados a assets, conoce el estado y el linaje de las tablas que produce. Hay tres modelos: *task-based* (Airflow), *asset-based* (Dagster; Airflow 3 y Prefect 3 se acercan) y *event-driven*.

**Estado verificado de Airflow ([release notes oficiales](https://airflow.apache.org/docs/apache-airflow/stable/release_notes.html), solo se leyeron los primeros 100k de 516k caracteres).**

| Versión | Fecha | Novedades relevantes |
|---|---|---|
| 3.0.0 | 22-abr-2025 | Task SDK / Execution API, Edge Executor, backfills en el scheduler, versionado de DAGs, UI React, `airflow.sdk` |
| 3.1.0 | 25-sep-2025 | Tareas human-in-the-loop, desacople del Task SDK, Deadline Alerts, Python 3.13 |
| 3.2.0 | 7-abr-2026 | Asset partitioning, despliegues multi-team, SQLAlchemy 2.0, Python 3.14 |
| 3.3.0 | 6-jul-2026 (3.3.2: 17-sep-2026) | Más asset partitioning, state store de tareas/assets, retry policies enchufables, Task SDKs Java y Go, bundle versioning al clear/rerun/backfill |

Los AIPs de 3.0 (AIP-65/66 versionado, AIP-72 Task Execution Interface, AIP-74/75 assets, AIP-78 backfills del scheduler, AIP-82 scheduling por eventos externos, AIP-83 fin de la unicidad de execution date) están en el [blog oficial](https://airflow.apache.org/blog/airflow-three-point-oh-is-here/). Las nubes gestionadas ya siguen la línea 3: MWAA ofrece 3.3.1 (disponible 1-sep-2026), 3.2.1, 3.0.6 y 2.11.x, **no soporta multi-team** y avisa el fin de soporte con 180 días ([AWS MWAA](https://docs.aws.amazon.com/mwaa/latest/userguide/airflow-versions.html)); Cloud Composer Gen 3 lista Airflow 3.1, 3.2 y 3.3 con soporte hasta 2027 ([Google Cloud](https://docs.cloud.google.com/composer/docs/composer-versions)). Dynamic task mapping: `max_map_length` por defecto 1024, el scheduler crea las copias justo antes de ejecutar y un mapa vacío marca la tarea SKIPPED ([docs](https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/dynamic-task-mapping.html)).

**Dagster y Prefect.** Dagster 1.13.26 (9-oct, año inferido 2026) hace que `dagster-dbt` ya no instale `dbt-core` por defecto ([releases](https://github.com/dagster-io/dagster/releases)); los backfills por partición generan N runs por defecto y `backfill_policy=single_run` ejecuta el rango en uno solo, lo que exige que el código opere sobre rangos ([docs](https://dagster.io/docs/guides/build/partitions-and-backfills/backfilling-data)). Prefect 3 identifica assets por URI con `@materialize`, infiere dependencias del grafo y emite eventos `prefect.asset.materialization.succeeded/failed` ([docs](https://docs.prefect.io/v3/concepts/assets)); se despliega con work pools (Docker, K8s, serverless) y workers con polling, o con push/managed pools sin worker a costa de compartir más información con Prefect Cloud ([docs](https://docs.prefect.io/v3/concepts/deployments)).

**Prefect–Dagster: anunciado, cierre NO confirmado.** El post de Dagster está fechado el 13-jul-2026; términos no divulgados; el OSS será "activamente desarrollado, no solo mantenido"; Dagster+ continúa con su marca y contratos; unos 40 empleados pasan a Prefect y **Nick Schrock deja el proyecto y la empresa** (la primera versión lo describía como asesor, lo que es incorrecto). La FAQ dice "esperamos que la transacción cierre en las próximas semanas", pero el banner de la página ya dice "Dagster is now part of Prefect" (inconsistencia no resuelta); el post de Prefect devolvió 404 ([blog](https://dagster.io/blog/prefect-is-acquiring-dagster), [FAQ](https://dagster.io/dagster-customer-faq)). Ninguna fuente leída confirma el cierre.

| Orquestador | Encaja cuando | Evitar cuando | Operación | Madurez |
|---|---|---|---|---|
| Airflow 3.x | Ecosistema máximo, heterogeneidad de tareas, parque Airflow existente | Si se exige lineage y particiones nativos como prioridad única | Scheduler + API server + DB + workers (más piezas) [Inferencia] | Muy alta |
| Dagster | Modelo de assets, particiones, checks, dbt-céntrico | Propiedad incierta tras la adquisición: no migrar solo por roadmap [Inferencia] | Dagster+ factura por materialización (blog secundario previo, **no verificado**) | Alta |
| Prefect 3 | Python ligero, despliegue híbrido, push pools | Necesidad de ecosistema de operadores de Airflow | El más liviano (fuente única secundaria de la pasada 1) | Alta |
| Argo Workflows | Contenedores en Kubernetes, ML y batch contenedorizado; proyecto CNCF graduado ([docs](https://argo-workflows.readthedocs.io/en/latest/)) | Orquestación centrada en tablas | CRD sobre K8s | Alta |
| Temporal | Lógica de negocio larga y durable: reproduce el Event History en otro worker y retoma ([docs](https://docs.temporal.io/evaluate/why-temporal)) | Pipelines de tablas; la página no detalla exactly-once | Servicio propio | Alta |
| Kestra | Declarativo y orientado a eventos ([docs](https://kestra.io/docs)) | — | Licencia y versión **no confirmadas** | Media |

**[Inferencia]** Con Airflow 3.2/3.3 (partitions, state store) y soporte en MWAA/Composer, el coste de quedarse en Airflow baja; subir de 2.x a 3 suele rendir más que migrar de orquestador. ADF, Databricks Workflows/Lakeflow Jobs y Mage no se investigaron con fuente primaria.

### 4.2 Transformación: dbt, SQLMesh y la consolidación

**Hechos de mercado verificados.**
- Fivetran anunció la compra de Tobiko Data (SQLMesh y SQLGlot) el 3-sep-2025, sin términos financieros ([Business Wire](https://www.businesswire.com/news/home/20250903275106/en/Fivetran-Acquires-Tobiko-Data-to-Power-the-Next-Generation-of-Advanced-AI-Ready-Data-Transformation)).
- La fusión Fivetran–dbt Labs se anunció el 13-oct-2025 y el comunicado de Fivetran del **1-jun-2026** declara la fusión completada: "all-stock", sin valoración publicada; George Fraser sigue como CEO y Tristan Handy es President. Ambas empresas son privadas, así que no existe presentación SEC que lo verifique; el comunicado original de oct-2025 no se encontró (404) ([Fivetran](https://www.fivetran.com/press/fivetran-dbt-labs-complete-merger-to-create-the-data-infrastructure-for-trusted-ai-agents), [Pulse 2.0](https://pulse2.com/fivetran-and-dbt-labs-complete-merger-to-build-trusted-ai-data-infrastructure/amp/)). Cifra de marketing: "más de 100.000 equipos de datos".
- SQLMesh: la Linux Foundation anunció el 25-mar-2026 que lo aloja; el repo declara "SQLMesh is a project of the Linux Foundation", licencia Apache 2.0 ([Linux Foundation](https://www.linuxfoundation.org/press/linux-foundation-welcomes-sqlmesh-project), vía resumen de búsqueda; [GitHub](https://github.com/TobikoData/sqlmesh)).
- dbt Core v2: primer alpha el 1-jun-2026, GA sin fecha; el runtime Rust, antes bajo ELv2, pasa a Apache 2.0 en el repo `dbt-core`; `dbt-fusion` queda archivado; migración con `dbt parse --use-v2-parser` y `dbt-autofix` ([dbt blog](https://docs.getdbt.com/blog/dbt-core-v2-is-here)).
- Licencias dbt: Core v1.x y dbt OSS v2, motor, adaptadores y spec en Apache 2.0; **MetricFlow Apache 2.0** (relicenciado oct-2025, antes BSL); el binario "dbt" completo y la extensión de VS Code bajo un "dbt Product Licensing Agreement" propietario ([FAQ de licencias](https://www.getdbt.com/licenses-faq)). Esto contradice la primera versión (Fusion bajo ELv2, MetricFlow BSL).
- "dbt State" (preview) sucede a la orquestación state-aware: hash en caché por modelo (código y datos) almacenado en Redis, funciona con Core, Fusion y orquestadores externos; la afirmación de "30 % o más" de ahorro es del proveedor ([Fivetran](https://www.fivetran.com/press/fivetran-dbt-labs-complete-merger-to-create-the-data-infrastructure-for-trusted-ai-agents), [dbt docs](https://docs.getdbt.com/docs/deploy/state-aware-about), solo snippet).

**dbt vs SQLMesh (diferencias técnicas verificadas).**

| Dimensión | SQLMesh | dbt |
|---|---|---|
| Entornos | Entornos virtuales: conjuntos de referencias a tablas versionadas por fingerprint; promover a prod suele ser un "Virtual Update" sin cómputo ([plans](https://sqlmesh.readthedocs.io/en/stable/concepts/plans/)) | CI con `state:modified+ --defer --state <artefactos de prod>` ([best practices](https://docs.getdbt.com/best-practices/best-practice-workflows)) |
| Categorías de cambio | breaking / non-breaking / forward-only | n/a |
| Incrementales | `INCREMENTAL_BY_TIME_RANGE` (intervalos faltantes, `lookback`), `BY_UNIQUE_KEY`, `BY_PARTITION` (no idempotente), SCD2, FULL, VIEW ([kinds](https://sqlmesh.readthedocs.io/en/stable/concepts/models/model_kinds/)) | `append`, `merge`, `delete+insert`, `insert_overwrite`, `microbatch` ([docs](https://docs.getdbt.com/docs/build/incremental-strategy)) |
| Backfill por intervalo | Estado propio de intervalos procesados | Microbatch: `event_time`, `begin`, `batch_size`, `lookback` por defecto 1, UTC, `dbt retry` solo para batches fallidos ([docs](https://docs.getdbt.com/docs/build/incremental-microbatch)) |
| SCD2 | Kinds SCD_TYPE_2 (restatement deshabilitado por defecto) | `snapshots`: estrategias `timestamp`/`check`, ignoran `--full-refresh`, "batch CDC" ([docs](https://docs.getdbt.com/docs/build/snapshots)) |
| Gobierno de proyecto | Linux Foundation | Fivetran (empresa fusionada) |

**[Inferencia]** SQLMesh rastrea intervalos procesados en su estado y no depende de `is_incremental()`; dbt microbatch aproxima esto por reloj y `lookback`. Un `merge` en dbt es SCD1 (sobrescribe) y no versiona historia. Criterio: dbt por defecto por ecosistema y contratación; SQLMesh si el dolor son entornos virtuales y backfills complejos. El riesgo estratégico es la concentración de T+EL+orquestación en un proveedor, mitigado por Core Apache 2.0 y SQLMesh bajo LF. Hay opinión de que Apache 2.0 no garantiza inversión de roadmap y que las novedades pueden aterrizar en Cloud/Fusion ([Nexla](https://nexla.com/blog/open-source-vs-saas-fivetran-dbt-merger/), snippet).

### 4.3 Ingesta y CDC

| Herramienta | Versión / estado verificado | Notas |
|---|---|---|
| Debezium | **3.7.0.Final (29-sep-2026)**: conectores incubating TiDB, Milvus, SQLite; CockroachDB sale de incubating; CLI oficial; JDBC sink con DLQ; breaking: se elimina Oracle 12 continuous mining y Cassandra 3. 3.6.3.Final (18-sep-2026, mantenimiento) ([releases](https://debezium.io/releases/), [post 3.7](https://debezium.io/blog/2026/09/29/debezium-3-7-final-released/)) | Reemplaza a la nota de la primera versión (3.6/3.7 Alpha de un agregador) |
| dlt | 1.31.0 (7-oct-2026), Apache 2.0 ([PyPI](https://pypi.org/project/dlt/)) | Code-first en Python |
| Airbyte | Plataforma 2.0 (14-oct-2025); 2.1 (3-abr-2026) solo vía snippet ([notas](https://docs.airbyte.com/release_notes/self-managed)) | Última versión y precios **no confirmados** |
| Flink CDC | Docs 3.7.0; pipelines YAML hacia Doris, StarRocks, Paimon, Iceberg, Hudi, Kafka ([docs](https://nightlies.apache.org/flink/flink-cdc-docs-stable/)) | |
| Snowflake Openflow | Basado en Apache NiFi; BYOC GA en AWS y SPCS GA en AWS y Azure según la página de producto; fechas GA no confirmadas ([docs](https://docs.snowflake.com/en/user-guide/data-integration/openflow/connectors/about-openflow-connectors)) | |
| Databricks Lakeflow Connect | Conectores CDC (MySQL, PostgreSQL, SQL Server), SaaS y archivos; estados de lanzamiento variados por conector ([docs](https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/)) | Databricks Asset Bundles pasó a llamarse "Declarative Automation Bundles" ([docs](https://docs.databricks.com/aws/en/dev-tools/bundles/)) |

**Semántica de Debezium/PostgreSQL ([docs](https://debezium.io/documentation/reference/stable/connectors/postgresql.html), leído hasta 100k de 320k caracteres).** Reanuda desde la última posición del WAL; pueden aparecer duplicados tras un snapshot; modos de snapshot `initial`, `always`, `initial_only`, `no_data`, `when_needed`; "la decodificación lógica no soporta cambios DDL"; no soporta cambios de esquema durante un snapshot incremental; los cambios se publican al commit. No se leyeron las secciones de TOAST ni de crecimiento del replication slot (riesgo operativo típico: [Práctica consolidada]). **DBLog** (Netflix) intercala eventos del log de transacciones con SELECTs mediante marcas de agua, sin locks ([arXiv 2010.12597](https://www.arxiv.org/pdf/2010.12597)). **Criterio:** CDC log-based cuando se necesitan baja latencia, deletes e histórico; incremental por cursor `updated_at` solo si la columna es fiable y se tolera latencia. Fivetran (pricing por MAR, conectores), Kafka Connect, ADF y los providers de Terraform no se investigaron.

### 4.4 Patrones de pipeline: idempotencia, backfills, datos tardíos, SCD

Las fuentes primarias coinciden: sobrescribir particiones o intervalos deterministas (no append), no leer "lo último disponible" sino la partición `data_interval_start`, evitar `now()` en cómputo crítico, no ejecutar DB/red/cómputo pesado en el código de nivel superior del DAG, y usar XCom solo para mensajes pequeños ([Airflow](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)). Beauchemin ("Functional Data Engineering", 2018) propone tareas puras que sobrescriben su partición de salida e inmutabilidad de particiones; **solo se conoce por resúmenes** (el artículo devolvió 403) ([Data Council](https://www.datacouncil.ai/functional-data-engineering-a-set-of-best-practices)). Los datos tardíos se tratan con `lookback` (dbt microbatch, SQLMesh) e `incremental_predicates` para acotar escaneos. Kimball Tipo 2 añade una fila por cambio con clave sustituta, fechas de vigencia e indicador de fila vigente ([Kimball](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/type-2/)).

**Runbook de backfill seguro [Inferencia, derivado de las fuentes anteriores]:**
1. Congelar y versionar el código (Airflow 3.3 versiona el bundle al hacer clear/rerun/backfill; Dagster usa particiones).
2. Verificar idempotencia: la tarea debe sobrescribir su partición o hacer MERGE por clave, nunca INSERT ciego.
3. Ejecutar en staging o rama (Iceberg branching, SQLMesh virtual environment) y auditar antes de publicar (WAP, ver 8.5).
4. Limitar concurrencia (`max_active_tis_per_dag`, `concurrent_batches`) para no saturar la fuente ni el catálogo.
5. En Dagster, usar `single_run` solo si el código opera sobre rangos; en dbt, `--event-time-start/--event-time-end` y `dbt retry` para fallos.
6. Verificar conteos y checksums frente a la fuente; publicar; compactar los ficheros pequeños que haya generado.
7. Registrar el backfill (rango, versión de código, responsable).

**Anti-patrones derivados (indirectos):** INSERT sin clave en tareas con reintento, `now()` en lógica, trabajo pesado en top-level, XCom con datos grandes, `merge` sin predicado sobre tablas enormes. Hay **cero post-mortems públicos** de backfills no idempotentes o de SCD2 a escala (área de baja literatura).

### 4.5 CI/CD y testing de datos

Slim CI de dbt: `dbt run/test -s state:modified+ --defer --state <artefactos>`; `--defer` resuelve refs no modificadas hacia producción; selectores `result:error/fail` para reruns y `source_status:fresher+` para reconstruir solo lo afectado; limitar datos en CI según `target.name`; definir `grants` en la config ([dbt](https://docs.getdbt.com/best-practices/best-practice-workflows)). Los unit tests de dbt (desde 1.8) se definen en YAML, solo para modelos SQL del proyecto, no para materialized views ni SQL recursivo, y se recomienda ejecutarlos en dev/CI ([dbt](https://docs.getdbt.com/docs/build/unit-tests)). **[Inferencia]** el virtual environment de SQLMesh es el análogo de blue/green a nivel de tabla. Sin fuente en esta pasada: data diff (Datafold/Recce), clones zero-copy, Terraform/OpenTofu y OpenLineage en Dagster/dbt/Spark.

## 5. Almacenamiento: formatos de tabla, catálogos, formatos de fichero, warehouses y operación

### 5.1 Iceberg: v3 adoptada, GA por motor muy desigual

**Estado de la especificación [Fuente].** v1 a v3 están adoptadas; v4 está "en desarrollo activo y no formalmente adoptada" ([spec](https://raw.githubusercontent.com/apache/iceberg/main/format/spec.md)). v2 añadió deletes a nivel de fila y números de secuencia; v3 añade tipos nuevos (timestamp con nanosegundos con/sin zona, `unknown`, `variant`, `geometry`, `geography`), valores por defecto de columna, transformaciones multi-argumento, row lineage, **deletion vectors binarios** y claves de cifrado de tabla. El esbozo de v4 incluye rutas relativas, `location` opcional (la da el catálogo), métricas en struct tipado `content_stats` y que ya no se permita escribir nuevos equality deletes; en el Iceberg Summit 2026 se presentaron árboles de metadatos adaptativos con commits de un fichero y column families (blog de proveedor, sin primaria ASF: [Snowflake](https://www.snowflake.com/en/blog/engineering/iceberg-summit-2026-recap-v4-spec/)).

**Versiones de la librería Java:** 1.10.0 (11-sep-2025; descrita por Google y Dremio como la versión que lleva v3 a GA con spec "cerrada", sin leer la nota oficial), 1.11.0 (20-may-2026: cifrado de manifest list, Flink 2.1, lectores Flink de row lineage), 1.12.0 (30-sep-2026, "Latest": endpoint REST de `unregister-table`, variant shredded en Flink, trabajo v4) ([releases](https://github.com/apache/iceberg/releases), [índice](https://iceberg.apache.org/releases/), [Google OSS](https://opensource.googleblog.com/2025/09/apache-iceberg-110-maturing-the-v3-spec-the-rest-api-and-google-contributions.html)).

**Resolución de la contradicción de la primera versión.** "Ratificada a mediados de 2025 / GA a mediados de 2026" mezcla tres cosas distintas: la **spec** (cerrada ~sep-2025 con la librería 1.10.0), el **soporte en la librería** y el **GA por producto**, que varía:

| Motor / plataforma | Estado de v3 (fuente) | Salvedades |
|---|---|---|
| Snowflake | **GA el 7-may-2026**: geography, geometry, nanosegundos, variant, unknown, defaults, deletion vectors, row lineage ([release note](https://docs.snowflake.com/en/release-notes/2026/other/2026-05-07-iceberg-v3-ga), [docs v3](https://docs.snowflake.com/en/user-guide/tables-iceberg-v3-specification-support)). Nota de prensa del 2-jun-2026 repite v3 GA y lectura/escritura bidireccional de motores externos sobre tablas gestionadas vía Horizon ([PR](https://www.snowflake.com/en/news/press-releases/snowflake-pioneers-new-open-framework-for-interoperable-enterprise-data-and-ai/)) | No soporta transformaciones multi-argumento ni claves de cifrado de tabla; el default sigue siendo v2 (`ICEBERG_VERSION = 3`); sin upgrade in-place v2→v3; escritura externa de tablas v3 gestionadas no GA según la release note (la nota de prensa de junio es más amplia: priorizar la release note) |
| AWS (EMR Spark 7.12+, Glue, S3 Tables, SageMaker notebooks) | Anuncio 26-nov-2025: **deletion vectors y row lineage** ([What's New](https://aws.amazon.com/about-aws/whats-new/2025/11/aws-apache-iceberg-v3-deletion-vectors-row-lineage), [Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/apache-iceberg-on-aws/table-spec-v3.html)) | **Athena: no soporta v3**; upgrade v2→v3 sin reescribir datos pero **de un solo sentido**; requiere merge-on-read; sin backfill histórico de row lineage; AWS usa "support", no etiqueta GA |
| Databricks | **Public Preview** en DBR 18.0+/18 LTS: DVs, VARIANT, row lineage ([docs](https://docs.databricks.com/aws/en/iceberg/iceberg-v3)) | No soporta defaults iniciales, `unknown`, nanosegundos ni transformaciones multi-argumento; upgrade irreversible; el estado "preview" viene de snippet y una página Azure decía Beta en DBR 17.3 (preferir la más nueva) |
| BigQuery / Lakehouse for Apache Iceberg | Deletion vectors binarios en **Preview** (11-jun-2026); DML/DDL sobre Iceberg en runtime catalog en Preview (25-jun-2026) ([release notes](https://docs.cloud.google.com/lakehouse/docs/release-notes)) | Sin entrada GA de v3 |
| Trino 483 | v3 **experimental**; UPDATE/DELETE/OPTIMIZE no soportados en v3; sin defaults ni cifrado ([docs](https://trino.io/docs/current/connector/iceberg.html)) | Starburst afirma soporte v3 en 476-e (proveedor, contradice parcialmente al upstream) |
| Spark / Flink OSS | Soporte en la librería (Flink: lectores de row lineage en 1.11, variant shredded en 1.12) | **Matriz oficial no verificada** (páginas de docs truncadas) |

**[Inferencia]** Un solo motor sin v3 en el camino de lectura (Athena, hoy) bloquea el upgrade, porque es unidireccional y cualquier lector no-v3 rompe. Antes de subir una tabla a v3: inventariar lectores, probar en copia, y tras el upgrade ejecutar compactación para consolidar delete files ([AWS PG](https://docs.aws.amazon.com/prescriptive-guidance/latest/apache-iceberg-on-aws/table-spec-v3.html)).

**Concurrencia y REST.** Un intercambio atómico del fichero de metadatos "sienta la base del aislamiento serializable", con commit optimista y reintento; el particionado es por transformaciones (day, bucket) con filtros derivados automáticamente y modificable sin reescritura ([spec](https://iceberg.apache.org/spec/)). El REST Catalog spec (OpenAPI 3.1.1) define config, namespaces, tablas (create/register/rename/staged), scan planning (`/plan`, `/tasks`), `transactions/commit`, funciones e `idempotency-key`; el endpoint OAuth2 `/oauth/tokens` está deprecado y se eliminará en Java 2.0 ([OpenAPI](https://github.com/apache/iceberg/blob/main/open-api/rest-catalog-open-api.yaml), parte truncada: vistas y credential vending no confirmados).

### 5.2 Delta Lake: 4.x, catalog-managed y la verificación de "Delta 5.0"

**Delta 5.0 no existe.** Ni delta.io ni GitHub la muestran; la última es **4.4.1 (5-oct-2026, año inferido)**. Línea de versiones ([releases](https://github.com/delta-io/delta/releases), [blog](https://delta.io/blog/)):

| Versión | Fecha | Contenido |
|---|---|---|
| 4.0.0 | blog 25-sep-2025 | Delta Connect, catalog-managed (preview), Variant (la fecha "09 Jun" que mostró el resumen de GitHub es incompatible con el blog: no fiable) |
| 4.0.1 | 16-ene-2026 | Renombra `catalogOwned-preview` a `catalogManaged` (breaking) |
| 4.1.0 | 26-feb-2026 | Spark 4.1, catalog-managed en preview |
| 4.2.0 | 16-abr-2026 | Variant GA, geospatial y collations en Kernel, conector Flink experimental |
| 4.3.0 | 18-jun-2026 | UC Delta REST API, UniForm Iceberg atómico e incremental |
| 4.4.0 | 20-ago-2026 | Spark 4.2, UC Delta API en Kernel y Flink, identity columns en DDL |
| 4.4.1 | 5-oct-2026 | Evita mantenimiento automático arriesgado en tablas catalog-managed; arregla snapshots incorrectos con S3A fast listing |

**Protocolo.** Reader v3 / writer v7 con *table features*: `deletionVectors`, `columnMapping`, `v2Checkpoint`, `domainMetadata`, `changeDataFeed`, `icebergCompatV1/V2/V3`, `catalogManaged` (el catálogo es fuente de verdad de qué commit tuvo éxito; exige in-commit timestamps y no admite acceso solo por filesystem), tablas clustered y Row Tracking ([PROTOCOL.md](https://raw.githubusercontent.com/delta-io/delta/master/PROTOCOL.md), mitad truncada; la mecánica Hilbert/z-order del clustering **no se confirmó**). **UniForm** genera metadatos Iceberg/Hudi de forma asíncrona tras cada commit con una sola copia de datos; los clientes Iceberg son solo lectura ([docs](https://docs.delta.io/latest/delta-uniform.html)); esa página dice requerir Hive Metastore e incompatibilidad con DVs, mientras la nota 4.3.0 sugiere evolución: tratar la página como posiblemente desfasada. **Liquid clustering** (Databricks) sustituye particionado y ZORDER, admite hasta 4 claves cambiables sin reescribir y `CLUSTER BY AUTO` con predictive optimization (DBR 15.4+) ([docs](https://docs.databricks.com/aws/en/delta/clustering)). Unity Catalog OSS 0.6.0 (20-ago) sube Iceberg a 1.11.0 y añade vistas SQL; 0.5.0 (18-jun) trae la UC Delta API ([releases](https://github.com/unitycatalog/unitycatalog/releases)). La extensión Delta/UC de DuckDB sale de experimental el 6-may-2026 y Delta Kernel Rust se integra en ClickHouse el 18-may-2026 ([delta.io](https://delta.io/blog/)).

**[Inferencia]** Delta (catalogManaged) e Iceberg v4 (`location` suministrada por el catálogo, commits de un fichero) convergen hacia "el catálogo coordina los commits"; el parche 4.4.1 indica que catalog-managed sigue madurando en producción.

### 5.3 Hudi, Paimon, DuckLake y comparación de formatos

| Formato | Estado verificado | Fortaleza | Limitación | Madurez |
|---|---|---|---|---|
| Hudi | 1.0.0 (dic-2024: table version 8, non-blocking concurrency control, índice secundario) ([blog](https://hudi.apache.org/blog/2024/12/16/announcing-hudi-1-0-0)); 1.1.1 (formato de tabla enchufable, Spark 4.0/Flink 2.0) ([1.1](https://hudi.apache.org/releases/release-1.1)); 1.2.x (tipos VECTOR/VARIANT/BLOB, lectura/escritura Lance solo Spark, Record-Level Index en Flink, table version 9) ([1.2](https://hudi.apache.org/releases/release-1.2), sin fecha) | Upserts por clave, indexación, table services | Casi 10x más lento en carga masiva en LHBench 2023 | Media-alta |
| Paimon | 2.0 estable, 2.2-SNAPSHOT en master; tablas PK con LSM, merge engines, changelog producers ([docs](https://paimon.apache.org/docs/master/)); OCC con reintento en conflicto de snapshot, en S3 necesita creación condicional o lock y se recomienda `write-only=true` más job de compactación dedicado ([concurrencia](https://paimon.apache.org/docs/master/concepts/concurrency-control/)) | Streaming con Flink | Menos motores | Media |
| DuckLake | **1.0 el 13-abr-2026** (confirmado en [duckdb.org/news](https://duckdb.org/news/)): metadatos en PostgreSQL/MySQL/SQLite/DuckDB, datos en Parquet, MIT, transacciones multi-tabla, compatibilidad hacia atrás garantizada ([ducklake.select](https://ducklake.select/)) | Simplicidad; metadatos SQL | Ecosistema pequeño | Emergente |
| XTable | ASF incubating; traduce metadatos entre Hudi, Delta e Iceberg ([sitio](https://xtable.apache.org/)) | Interoperabilidad sin migrar | No es formato nuevo | Incubating |

**Comparación académica.** CIDR 2023 ("Analyzing and Comparing Lakehouse Storage Systems", LHBench sobre EMR) halló a Hudi casi 10x más lento en carga masiva porque se optimiza para upserts; es de 2023, con versiones antiguas y autores vinculados a Databricks (sesgo potencial) ([CIDR](https://vldb.org/cidrdb/2023/analyzing-and-comparing-lakehouse-storage-systems.html), [LHBench](https://lhbench.cs.berkeley.edu/)); LST-Bench (SIGMOD 2024, Microsoft) es otra referencia ([MSR](https://www.microsoft.com/en-us/research/publication/lst-bench-benchmarking-log-structured-tables-in-the-cloud/)). **No hay benchmarks independientes 2025-26 ni cifras duras de cuota de mercado.**

**Layout de metadatos (documentado).** Iceberg: `metadata.json` → manifest list → manifests → data/delete files, con Puffin para estadísticas y DVs. Delta: `_delta_log` (JSON + checkpoints; `v2Checkpoint` con sidecars). Paimon: snapshots/manifests + LSM por bucket. DuckLake: tablas SQL.

**Señal de adopción.** "Iceberg ganó, importa el catálogo" proviene de fuentes con sesgo (autor ligado a Dremio: [AM Data Lakehouse](https://amdatalakehouse.substack.com/p/lakehouse-table-formats-in-2026-iceberg), [Cloudmagazin](https://www.cloudmagazin.com/fr/2026/07/01/iceberg-a-remporte-la-guerre-des-formats-maintenant-cest-le-catalogue-qui-compte/)). La señal más sólida es que Snowflake, AWS, Google, Databricks y Starburst publican soporte v3 de Iceberg, y que Thoughtworks puso Apache Iceberg en **Adopt** en el Radar vol. 34 (abr-2026) ([Radar](https://www.thoughtworks.com/radar)).

**Cuándo elegir (marco).** Iceberg: interoperabilidad multi-motor y neutralidad. Delta: base instalada en Databricks y Kernel/Flink; interop vía UniForm. Hudi: upserts de alta tasa por clave con table services. Paimon: streaming nativo en Flink. DuckLake: equipos pequeños y analítica local/embebida donde los metadatos en SQL simplifican. **[Inferencia]** no use un formato de nicho si el catálogo y los motores que necesita no lo soportan.

### 5.4 Catálogos

| Catálogo | Estado verificado | Notas |
|---|---|---|
| Apache Polaris | **TLP**, blog fechado 19-feb-2026 (publicación, no prueba la fecha del voto) ([blog](https://polaris.apache.org/blog/2026/02/19/apache-polaris-graduates-to-top-level-project/)); Gluten graduó en la misma tanda (5-mar-2026) | Implementación vendor-neutral de Iceberg REST; Dremio, Snowflake, Spark, Trino, Flink |
| Snowflake Open Catalog / Horizon | Open Catalog = Polaris gestionado; Snowflake recomienda Horizon a clientes nuevos y ya no permite crear la primera cuenta Open Catalog; facturación por requests prevista 1S-2026, **estado de cobro actual no verificado** ([docs](https://docs.snowflake.com/en/user-guide/opencatalog/overview)) | **[Inferencia]** prioriza su catálogo propietario |
| Unity Catalog (OSS / Databricks) | OSS 0.6.0 (ver 5.2); Databricks añade Iceberg gestionado (v3 en preview) | Donación a LF no confirmada en esta pasada |
| AWS Glue / S3 Tables / Lake Formation | Glue expone Iceberg REST y table maintenance con v3; S3 Tables hace mantenimiento automático ([S3 Tables](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables-maintenance-overview.html)) | Lake Formation: investigado en 9.8 y 8.6, no como catálogo |
| Apache Gravitino | **TLP** anunciado el 3-jun-2025 ([ASF](https://news.apache.org/foundation/entry/the-apache-software-foundation-announces-two-new-top-level-projects)); docs 1.3.1 enlazadas | Catálogo federado |
| Lakekeeper | Rust, Apache-2.0, credential vending y remote signing, OpenFGA (Cedar solo en edición comercial "Plus"); **no es ASF**, mantenido por Vakamo ([GitHub](https://github.com/lakekeeper/lakekeeper)) | Versión no obtenida |
| Nessie | Control de versiones "inspirado en Git", Iceberg REST, docs hasta 0.109.0 sin marca de deprecación ([sitio](https://projectnessie.org/)) | Actividad e inversión de Dremio **no verificadas** |
| BigQuery tables for Iceberg ("Lakehouse for Apache Iceberg", antes BigLake) | Datos en buckets del cliente; compactación, clustering, GC y refresco de metadatos facturados como DCU; sin renombrar/clonar/snapshots/MV/RLS ([docs](https://docs.cloud.google.com/bigquery/docs/iceberg-tables)) | |

Snowflake–Fabric/OneLake bidireccional GA el 30-ene-2026 ([release note](https://docs.snowflake.com/release-notes/2026/other/2026-01-30-iceberg-microsoft-fabric-bidirectional-data-access-ga)). **[Inferencia]** Polaris (Snowflake/Dremio), Unity (Databricks) y Glue/S3 Tables compiten por ser el catálogo REST de referencia; Lakekeeper y Gravitino cubren el segmento self-hosted/federado. Sin fuente primaria: Lake Formation en profundidad, detalle de Horizon, pertenencia de UC OSS a LF AI & Data.

### 5.5 Formatos de fichero

| Formato | Estado verificado ([Parquet blog](https://parquet.apache.org/blog/) salvo indicación) | Nota |
|---|---|---|
| Parquet | Variant (blog 27-feb-2026), tipos geoespaciales nativos (13-feb), estadísticas float con orden total IEEE 754 y conteo de NaN (29-may), parquet-format 2.13.0 (13-jun) y 2.14.0 (11-sep: INT96 cronológico, tipo lógico FILE, codificación ALP), blog ALP 22-sep ("compresión cercana a zstd, descompresión más rápida"), parquet-java 1.17.0 (13-ene) y 1.18.0 (11-ago) | Page index y bloom filters no cubiertos |
| Vortex | "Incubating", "a Series of LF Projects", donado por Spiral; claims "100x acceso aleatorio, 10-20x scans, 5x escrituras" **sin metodología** ([vortex.dev](https://vortex.dev/)) | Afiliación LF AI & Data no confirmada; un benchmark de Zilliz da ~2,4x en full scan (pasada 1) |
| Lance | Apache-2.0; formato de fichero + tabla + spec de catálogo para IA multimodal; búsqueda vectorial/FTS/SQL; claim 100x acceso aleatorio; paper VLDB 2025 ([lance.org](https://lance.org/)); Hudi 1.2 lo lee/escribe | Sin validación independiente |
| ORC, Avro, Arrow, Nimble | Sin fuente primaria en esta pasada | [Práctica consolidada]: Avro para filas/streaming con schema registry; ORC en Hive; Arrow para memoria e IPC |

Contrapunto de escepticismo sobre sustituir Parquet: [urandom.io](https://urandom.io/blog/2026-05-18-parquet-is-paying-a-cpu-tax-it-cant-afford) (blog personal, no re-leído). **[Inferencia]** Parquet seguirá siendo el contenedor por defecto de Iceberg, Delta, Hudi y DuckLake; ALP, Variant y geo aportan compresión y semi-estructurado sin cambiar el modelo de tablas.

### 5.6 Warehouses y OLAP: arquitectura y precios (solo lo verificado)

**Qué se pudo leer en páginas oficiales:**

| Plataforma | Precio verificado | Fuente |
|---|---|---|
| Snowflake | Crédito on-demand en AWS US East (N. Virginia): $2,00 Standard / $3,00 Enterprise / $4,00 Business Critical / $6,00 VPS; Europa (Dublín/Frankfurt) $2,60 / $3,90 / $5,20; almacenamiento on-demand $23/TB-mes en US East, desde $13,80 con capacidad | [Credit Consumption Table](https://www.snowflake.com/legal-files/CreditConsumptionTable.pdf) (leída con pdftotext), [opciones](https://www.snowflake.com/en/pricing-options/) |
| Redshift (us-east-1) | Serverless $0,375/RPU-hora; ra3.4xlarge $3,26/h (ejemplo); managed storage $0,024/GB-mes; Spectrum $5/TB escaneado | [AWS](https://aws.amazon.com/redshift/pricing/) |
| ClickHouse Cloud | Compute unit = 8 GiB RAM + 2 vCPU; Enterprise AWS us-east-1 $0,39030/unidad-hora y $25,30/TB-mes; escala a cero | [ClickHouse](https://clickhouse.com/pricing) |
| MotherDuck | Lite $0; Business $250/org-mes + uso; Pulse $0,60/CU-hora, Standard $2,40/h, Jumbo $4,80/h; almacenamiento $0,04/GB-mes comprimido | [MotherDuck](https://motherduck.com/product/pricing/) |
| S3 / S3 Tables | S3 Tables $0,0265/GB-mes (primeros 50 TB); PUT $0,005/1000, GET $0,0004/1000; monitorización $0,025/1000 objetos; compactación $0,002/1000 objetos + $0,005/GB; egress a internet: 100 GB/mes gratis, ejemplo $0,09/GB desde Irlanda | [AWS S3](https://aws.amazon.com/s3/pricing/) (región no indicada en el resumen) |
| AWS Glue | Optimización de tablas Iceberg $0,44/DPU-hora (por segundo, mínimo 1 min); catálogo con 1M objetos y 1M requests gratis, luego $1/100k objetos-mes | [AWS Glue](https://aws.amazon.com/glue/pricing/) |

**Lo que NO está verificado (decláralo en cualquier decisión):**
- **BigQuery:** la página oficial no se pudo leer. Un snippet de búsqueda indica on-demand $6,25/TiB con 1 TiB gratis y slot-hora PAYG de $0,06 (Enterprise), pero otra copia daba $0,04 (conflicto); el fetch directo devolvió cifras de memoria del modelo, **descartadas**. Una anécdota de la comunidad HTTP Archive corrobora $6,25/TiB como cifra de trabajo del mantenedor ([foro](https://discuss.httparchive.org/t/warning-14-000-bigquery-charge-in-2-hours/2715)), lo cual no sustituye a la página de precios.
- **Fabric:** SKUs F2 a F8192; las reservas de 1-3 años ahorran ~41 % frente a pay-as-you-go; la página mostró "$-" en los precios ([Azure](https://azure.microsoft.com/en-us/pricing/details/microsoft-fabric/)). No hay tarifa por CU verificada.
- **Databricks:** el DBU se define como medida normalizada con facturación por segundo; **no se obtuvo tarifa oficial por DBU**. Terceros dan ~0,70-1,00 USD/DBU para SQL Serverless en AWS, discrepantes ([Databricks](https://www.databricks.com/product/pricing), [CostBench](https://www.costbench.com/software/business-intelligence/databricks-sql/), [DoiT](https://www.doit.com/blog/databricks-pricing-explained-dbus-tiers-cost-control)).
- **Snowflake:** la tabla oficial cubre los créditos citados; precios de capacidad (ACV) y de otras regiones/nubes no se leyeron.

**OLAP/serving.** Pinot 1.5.1: ingestión real-time desde Kafka/Pulsar/Kinesis, upserts desde 0.6, multi-tenant; la página no menciona Iceberg/Delta ([pinot.apache.org](https://pinot.apache.org/)). StarRocks, Doris y Druid: **sin fuente primaria** (el fetch de StarRocks devolvió 404). **DuckDB:** 1.5.x hasta 1.5.6 (28-sep-2026); preview de v2.0 el 17-ago-2026 con protocolo "Quack" para lecturas/escrituras concurrentes multiproceso ([duckdb.org](https://duckdb.org/news/)). **DuckDB Labs–AWS: confirmado** por fuente primaria: el 26-ago-2026 DuckLabs (entidad "DuckLabs B.V.") anunció que se une a AWS como subsidiaria, cierre esperado a principios de sept-2026, términos no divulgados; DuckDB, DuckLake, Quack y las extensiones siguen MIT bajo la DuckDB Foundation, con un stakeholder advisory board ([duckdb.org](https://duckdb.org/2026/08/26/ducklabs-to-join-aws); corroboración: [SiliconANGLE](https://siliconangle.com/2026/08/26/aws-buys-ducklabs-to-bring-duckdbs-embeddable-analytics-to-more-enterprises/), [Channel Insider](https://www.channelinsider.com/channel-business/news-aws-acquires-ducklabs-duckdb/)). La primera versión la descartó por error; las cifras de descargas divergen entre fuentes (1M/día vs >3M).

**Comparación warehouse vs lakehouse [Inferencia].** El almacenamiento es parecido (Snowflake $23/TB-mes, Redshift RMS $24, ClickHouse $25,30, S3 Standard: precio **no verificado en esta pasada**, no recuperado de la página oficial); la diferencia está en cómputo, mantenimiento (Glue $0,44/DPU-h; compactación de S3 Tables) y egress. **No hay benchmark independiente reciente**: los de proveedores (Databricks 2021 "2,7x más rápido, 12x más barato" vs Snowflake, refutado; Fivetran 2022; Gigaom 2019 patrocinado) están disputados ([HPCwire](https://www.hpcwire.com/bigdatawire/2022/12/21/fivetran-benchmarks-five-cloud-data-warehouse/), [Databricks](https://www.databricks.com/de/blog/2021/11/15/snowflake-claims-similar-price-performance-to-databricks-but-not-so-fast.html), [Blocks&Files](https://blocksandfiles.com/2021/11/15/snowflake-rebuts-databricks-snowflake-performance-comparison/)). ClickBench lo mantiene ClickHouse ([ClickBench](https://benchmark.clickhouse.com/)). Para serving de baja latencia y alta concurrencia (Pinot, ClickHouse, StarRocks) frente a BI ad hoc en warehouse, la elección es por patrón de consulta; sin benchmark neutral no hay ranking defendible.

### 5.7 Operación del lakehouse: runbook de mantenimiento

**Qué dice la documentación oficial de Iceberg ([maintenance](https://raw.githubusercontent.com/apache/iceberg/main/docs/docs/maintenance.md)).** Recomendado: expirar snapshots; eliminar metadata antigua (`write.metadata.delete-after-commit.enabled`, por defecto false; `previous-versions-max` 100); borrar huérfanos (retención por defecto de 3 días; un intervalo corto puede corromper la tabla; operación lenta con muchos ficheros). Opcional: `rewriteDataFiles`, `rewriteManifests`, reescribir position deletes, `removeDanglingDeleteFiles` y estadísticas NDV (Puffin). Los procedimientos de Spark fijan `expire_snapshots` con `older_than` por defecto de 5 días y `retain_last` 1, `remove_orphan_files` con `dry_run`, y `rewrite_data_files` con `delete-file-threshold` ([spark-procedures](https://raw.githubusercontent.com/apache/iceberg/main/docs/docs/spark-procedures.md)). La evolución de particiones es solo de metadatos y los datos viejos conservan su layout ([evolution](https://raw.githubusercontent.com/apache/iceberg/main/docs/docs/evolution.md)). La documentación **no da guía sobre mantenimiento concurrente con escritores** más allá de la retención de huérfanos.

| Tarea | Frecuencia sugerida [Inferencia] | Precaución |
|---|---|---|
| Compactación (`rewrite_data_files`) | Continua o micro-lote en tablas de streaming; diaria en batch; objetivo ~256-512 MB (el ejemplo de AWS PG usa 512 MB) | Programarla fuera de la ventana de escrituras conflictivas; Paimon recomienda compactación dedicada |
| `expire_snapshots` | Diaria/semanal según la ventana de time travel | Recordar que time travel conserva datos borrados (GDPR, 9.3) |
| `remove_orphan_files` | Semanal/mensual con retención ≥ 3 días y mayor que la escritura más larga | Usar `dry_run` primero |
| `rewrite_manifests` | Ocasional, si el patrón de escritura no coincide con el de lectura | |
| Estadísticas NDV | Tras cargas grandes | |
| Monitorización | Tamaño medio de fichero vía tabla `files` (AWS PG lo sugiere) | |

**Escrituras condicionales en S3.** `If-None-Match` (solo `*`) e `If-Match` (ETag) en PutObject/CopyObject/CompleteMultipartUpload; 412 si falla la precondición, 409 en deletes concurrentes, el primero en terminar gana, requiere SigV4 ([AWS](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html)); fueron anunciadas en ago/nov-2024 sin coste extra (pasada 1). S3 Tables redujo la compactación hasta un 90 % desde jul-2025 ([What's New](https://aws.amazon.com/about-aws/whats-new/2025/07/amazon-s3-tables-reduce-compaction-costs), no re-leído); una anécdota de blog (Glue 1,32 USD vs S3 Tables 0,0875 USD en una semana) **no es generalizable**.

**Particionado vs clustering.** En Iceberg gestionado por Unity Catalog, las columnas de partición externas se traducen a claves de clustering y se descartan los bucket transforms ([Databricks](https://docs.databricks.com/aws/en/delta/clustering)). **[Inferencia]** el crecimiento de metadatos limita la tasa de commits: es la motivación de Iceberg v4 (commits de un fichero) y de DuckLake (metadatos en SQL). Los servicios gestionados (S3 Tables, Glue, BigQuery) facturan el mantenimiento. Sin fuentes: VACUUM/OPTIMIZE de Delta en docs oficiales y table services de Hudi.

## 6. Procesamiento batch y streaming

### 6.1 Estado verificado de versiones (a 12-oct-2026)

| Proyecto | Versiones y fechas | Fuente / salvedad |
|---|---|---|
| Spark | 4.0.0 (23-may-2025), 4.1.0 (16-dic-2025), 4.1.1 (9-ene-2026), 4.1.2 (21-may-2026), **4.2.0 (14-jul-2026)**, 4.1.3 y 4.0.4 (15-jul), 3.5.9 (16-jul). No figura Spark 4.3 | [Spark news](https://spark.apache.org/news/index.html) |
| Flink | 2.0.0 (24-mar-2025), 2.1.0 (31-jul-2025), 2.2.0 (4-dic-2025), **2.3.0 (25-jun-2026, "latest stable")**, parches 2.2.1 (15-may) y 2.1.3 (14-jun) | [Flink downloads](https://flink.apache.org/downloads/) (100k de 126k caracteres leídos) |
| Kafka | 4.0.0 (18-mar-2025), 4.1.0 (2-sep-2025), 4.2.0 (17-feb-2026), **4.3.0 (22-may-2026)**, 4.3.1 (25-jun), 4.2.2 (29-sep), 4.1.2 (17-mar) | [Kafka downloads](https://kafka.apache.org/community/downloads/), [blog](https://kafka.apache.org/blog). La página marca 4.3.1 como "latest" aunque 4.2.2 tiene fecha posterior; no resuelto |
| Trino | 483 (17-jul-2026), 482 (25-jun), 481 (11-may), 480 (24-mar), 479 (14-dic-2025) | [Trino releases](https://trino.io/docs/current/release.html) |
| Pulsar | 4.2.0 (24-mar-2026), 4.2.1 (23-abr), 4.2.2 (5-jun); LTS 4.0 sale de soporte activo el 21-oct-2026 y recibe solo parches de seguridad hasta 21-oct-2027 | [espejo de pruebas Apache](https://release-test.apache.org/api/cle/release/pulsar/4.2.0) y [endoflife.date](https://endoflife.date/apache-pulsar); no es pulsar.apache.org |
| Comet | **1.0.0 (7-ago-2026)** | [DataFusion blog](https://datafusion.apache.org/blog/2026/08/07/datafusion-comet-1.0.0) |
| Gluten | Top-level project el 5-mar-2026 | [ASF](https://news.apache.org/foundation/entry/the-apache-software-foundation-graduates-two-open-source-projects-from-incubator) |
| IBM–Confluent | **Cierre el 17-mar-2026**: US$31/acción en efectivo, EV ~US$11.000 M; la nota no dice si se mantiene la marca ni nada sobre la licencia OSS de Kafka | [IBM Newsroom](https://newsroom.ibm.com/2026-03-17-ibm-completes-acquisition-of-confluent,-making-real-time-data-the-engine-of-enterprise-ai-and-agents); anuncio 8-dic-2025, aprobación de accionistas 12-feb-2026 ([ChannelWeb](https://www.channelweb.co.uk/news-network/2026/ibm-completes-11bn-confluent-acquisition), secundaria; no se halló el 8-K) |

**[Inferencia]** Cadencia: Flink ~2 minors/año tras 2.0; Kafka ~3 minors/año. La ausencia de Spark 4.3 en la página sugiere que la Real-Time Mode con estado en OSS aún no salió; verificar antes de decidir. Sin releases verificados en esta pasada: Redpanda, Materialize, RisingWave, Polars.

### 6.2 Spark 4.x: Connect, Declarative Pipelines, Real-Time Mode, AQE y tuning

**Qué trae.** Spark 4.0: ANSI por defecto, VARIANT, Connect ([release](https://spark.apache.org/releases/spark-release-4-0-0.html), pasada 1). Real-Time Mode (RTM) en 4.1.0 soporta solo consultas **stateless** en OSS; las stateful (agregaciones, joins, `transformWithState`) están planificadas para 4.3; el trigger (5 min por defecto) es intervalo de checkpoint, no objetivo de latencia, y como todas las etapas corren simultáneamente los task slots deben ser ≥ total de tareas ([docs master](https://apache.googlesource.com/spark/+show/master/docs/streaming/real-time-mode.md), [Databricks](https://docs.databricks.com/aws/structured-streaming/real-time)). Databricks afirma p99 de un dígito de ms y una charla del Data+AI Summit habla de p99 <300 ms también con estado ([blog](https://www.databricks.com/fr/blog/introducing-real-time-mode-apache-sparktm-structured-streaming), [sesión](https://www.databricks.com/dataaisummit/session/real-time-mode-technical-deep-dive-how-we-built-sub-300-millisecond)); **es afirmación de producto, no de OSS**, y contradice el alcance de la doc 4.1. Spark 4.2.0 añade RTM trigger para PySpark, **Auto CDC SCD1** en Declarative Pipelines, stream-stream non-outer join en modo Update, join state format V4, nombrado de fuentes/sinks para evolucionar queries sin romper checkpoints, QUALIFY, cursores de SQL scripting, metric views y reparación automática de snapshots del state store ([release 4.2.0](https://spark.apache.org/releases/spark-release-4-2-0.html)).

**Tuning oficial (docs 4.2) ([SQL performance tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)):**

| Parámetro | Valor por defecto | Recomendación de la doc / práctica derivada |
|---|---|---|
| `spark.sql.shuffle.partitions` | 200 | Con AQE, fijar `initialPartitionNum` alto (p. ej. 2000) y dejar que AQE coalesce |
| AQE | activo desde 3.2 | Dejar por defecto |
| `coalescePartitions.advisoryPartitionSizeInBytes` | 64 MB | |
| `coalescePartitions.parallelismFirst` | true | La doc recomienda `false` en clústeres ocupados |
| `skewJoin.enabled` / `skewedPartitionFactor` / umbral | true / 5,0 / 256 MB | Preferir el skew join de AQE antes del salting manual (el salting sigue siendo necesario para agregaciones skewed [Práctica consolidada]) |
| `autoBroadcastJoinThreshold` / `broadcastTimeout` | 10 MB / 300 s | Hint BROADCAST para dimensiones >10 MB; AQE puede convertir SMJ en broadcast o shuffled hash join |

**Aceleración nativa.** Photon (propietario, solo Databricks): speedup promedio 3x frente al runtime anterior y hasta >10x en benchmark del propio proveedor ([paper SIGMOD 2022](https://www.databricks.com/wp-content/uploads/2022/07/Photon-A-Fast-Query-Engine-for-Lakehouse-Systems.pdf)). Comet 1.0.0: 244 commits de 23 contribuidores en ~6 semanas, semver, soporta Spark 3.4-4.1 (experimental 4.2), >400 expresiones, fallback por expresión, suite de >24.000 tests; **el post no da speedups propios** (remite a un TPC-DS de 3 TB en EKS de AWS Labs) y los benchmarks tempranos fueron modestos. Gluten descarga cómputo de la JVM a Velox o ClickHouse. **No existe evidencia independiente comparando Photon, Comet y Gluten.** Elección para OSS: Comet (Arrow/DataFusion, Rust) vs Gluten (Velox, C++) [Inferencia].

### 6.3 Flink 2.x

Flink 2.0 rompió compatibilidad (elimina DataSet, SourceFunction, Sink V1; sin garantía de compatibilidad de estado 1.x→2.x), desagregó el estado sobre DFS (ForSt) con ejecución asíncrona, añadió 7 operadores SQL stateful asíncronos (11 de 14 queries stateful de Nexmark lo soportan), Materialized Tables con integración Paimon, Java 17 por defecto y `config.yaml` ([anuncio](https://flink.apache.org/2025/03/24/apache-flink-2.0.0-a-new-era-of-real-time-data-processing/)). El paper VLDB 2025 contra Flink 1.20 reporta hasta -94 % de duración de checkpoint, hasta 49x en recuperación/rescale y hasta 50 % de ahorro de coste, con autores del equipo de desarrollo (Alibaba) ([VLDB 2025](https://www.vldb.org/pvldb/vol18/p4846-mei.pdf)). Flink 2.3 (25-jun-2026) trae PTFs `FROM_CHANGELOG`/`TO_CHANGELOG`, DDL de materialized tables, S3 nativo sin Hadoop/Presto, partición adaptativa opt-in (hasta ~3x de throughput bajo skew, según las notas de release), checkpointing durante la recuperación (opt-in) y un cambio de comportamiento: SinkUpsertMaterializer falla en planificación si la upsert key difiere de la PK del sink (requiere `ON CONFLICT`) ([release notes](https://nightlies.apache.org/flink/flink-docs-release-2.3/release-notes/flink-2.3/)). **[Inferencia]** migrar de 1.x a 2.x requiere reprocesar o re-bootstrapping de estado: planificarlo como proyecto, no como upgrade. Sin datos de adopción de ForSt fuera de Alibaba.

**Caso Uber IngestionNext** ([blog](https://uber.com/blog/from-batch-to-streaming-accelerating-data-freshness-in-ubers-data-lake/)): Kafka → Flink → Hudi reemplaza ingestión batch de Spark; frescura de horas/días a minutos; **-25 % de cómputo**; los small files de Parquet se mitigan con merge a nivel de row group (compactación 10x más rápida); skew por partición Kafka mitigado alineando paralelismo, cuotas por partición y autoscaling consciente de skew.

### 6.4 Kafka 4.x y alternativas

| Tema | Estado verificado | Fuente |
|---|---|---|
| Kafka 4.0 | Sin ZooKeeper (solo KRaft), KIP-848 GA, brokers en Java 17 | [Instaclustr](https://www.instaclustr.com/blog/kafka-4-0-unveiled-key-changes-and-how-they-impact-developers/) (pasada 1) |
| Kafka 4.2.0 (17-feb-2026) | **Share groups (colas, KIP-932) "production-ready"**; KIP-1071 Streams Rebalance Protocol GA con conjunto limitado; DLQ en handlers de excepciones (KIP-1034) | [anuncio](https://kafka.apache.org/blog/2026/02/17/apache-kafka-4.2.0-release-announcement/) |
| Kafka 4.3.0 (22-may-2026) | Cordoned log dirs (KIP-1066), límites de buffers de coordinadores, headers en state stores de Streams, aviso al usar el protocolo de rebalanceo clásico (KIP-1274), deprecación de `streams-scala` (KIP-1244, remoción en 5.0); 4.3.1 arregla una fuga de memoria nativa de RocksDB en Streams | [anuncio](https://kafka.apache.org/blog/2026/05/22/apache-kafka-4.3.0-release-announcement/), [blog](https://kafka.apache.org/blog) |
| Tiered storage (KIP-405) | Production-ready desde 3.9; KIP-950 permite deshabilitarlo por tópico | [KIP-405](https://cwiki.apache.org/confluence/display/KAFKA/KIP-405%3A+Kafka+Tiered+Storage), [KIP-950](https://cwiki.apache.org/confluence/display/KAFKA/KIP-950:++Tiered+Storage+Disablement) |
| Diskless (KIP-1150) | **Aceptado el 2-mar-2026** (9 binding, 5 non-binding); es un KIP "meta"; sub-KIPs 1163/1164/1165 en discusión; **no está en Kafka mainline**; única implementación: fork Inkless de Aiven | [Aiven](https://aiven.io/blog/kip-1150-accepted-and-the-road-ahead), [Instaclustr](https://www.instaclustr.com/support/documentation/announcements/apache-kafka/kafka-diskless-proposals-status-insights/) |
| WarpStream | Adquirido por Confluent el 9-sep-2024; descrito para cargas con latencia relajada en la nube del cliente | [Business Wire](https://www.businesswire.com/news/home/20240909282386/en/Confluent-Acquires-WarpStream-to-Advance-Next-Gen-BYOC-Data-Streaming) |
| AutoMQ | Apache 2.0, liderado por empresa (no ASF), según su propia comparativa | [AutoMQ](https://www.automq.com/blog/top-open-source-diskless-kafka-alternatives) (competidor, sesgo) |
| Redpanda | Jepsen (29-abr-2022, v21.10.1-21.11.2): escrituras duplicadas sin idempotencia, offsets inconsistentes, pérdida de escrituras transaccionales (corregidas en 21.11.15), pérdida de mensajes confirmados sin resolver al publicar. Ediciones Community/Enterprise con clave de licencia; Iceberg Topics requiere licencia enterprise | [Jepsen](https://jepsen.io/analyses/redpanda-21.10.1), [licencias](https://docs.redpanda.com/current/get-started/licensing/); la doc no menciona BSL (el dato BSL es [Práctica consolidada]) |
| Kafka vs Redpanda | Vanlightly (2023, 3x i3en.6xlarge): al límite del NVMe (~2 GB/s) Kafka ~1900 MB/s vs Redpanda ~1400 MB/s; el 1 GB/s de Redpanda se degrada con 50 productores, con claves y con TLS. Autor afiliado a Confluent | [Vanlightly](https://jack-vanlightly.com/blog/2023/5/15/kafka-vs-redpanda-performance-do-the-claims-add-up); **no hay benchmark independiente posterior a 2023** |

**[Inferencia]** Para costes dominados por tráfico inter-AZ y latencia relajada, el candidato es el modelo diskless/object storage (WarpStream, AutoMQ, Inkless); para Kafka OSS puro, esperar los sub-KIPs de KIP-1150 sin fecha. Con share groups GA, algunos casos de colas (RabbitMQ/SQS) podrían consolidarse en Kafka; es una madurez de febrero de 2026: validar con carga propia. La latencia de diskless "de cientos de ms a ~1-2 s p99" de la primera versión es **[No verificado]**.

### 6.5 Otros motores y árbol de decisión

- **Trino:** la ejecución tolerante a fallos está desactivada por defecto; `retry-policy` QUERY o TASK; TASK para batch grande y requiere exchange manager (S3/Azure/GCS/HDFS) con datos spooled cifrados; 4 reintentos por defecto; puede añadir latencia a queries cortas ([docs](https://trino.io/docs/current/admin/fault-tolerant-execution.html)).
- **Ray vs Daft:** Anyscale (proveedor de Ray) afirma que Ray Data fue ~30 % más rápido en promedio y ~3x en inferencia batch de imágenes en su reproducción del benchmark de Daft; Daft publicó el original y no se halló respuesta; el anuncio de integración con NVIDIA cuDF "80 % menor coste" es nota de prensa ([Anyscale](https://www.anyscale.com/blog/ray-data-daft-benchmarking-multimodal-ai-workloads), [HPCwire](https://www.hpcwire.com/bigdatawire/this-just-in/anyscale-cuts-multimodal-ai-data-processing-costs-by-80-with-nvidia-rtx-pro-4500-blackwell/)).
- **Migraciones Spark↔Flink:** no hay caso con números de Spark Structured Streaming a Flink. Hallazgos adyacentes: F5 Threat Stack pasó de Flink a Spark en EMR con coste de infraestructura ~10 % del clúster Flink ([F5](https://www.f5.com/company/blog/optimizing-threat-stacks-data-pipeline-with-apache-spark-and-amazon-emr)); Tencent migró gradualmente a Flink con estado de 40 TB ([ApacheCon](https://apachecon.com/acasia2022/sessions/streaming-1235.html)); una guía de Ksolves recomienda correr ambos motores 2-4 semanas ([Ksolves](https://www.ksolves.com/blog/big-data/spark/migrating-to-apache-flink)). Uber upgradeó Spark 2.4→3.3 en más de 2M de aplicaciones con >60 % de jobs con >10 % de mejora ([Uber](https://www.uber.com/blog/ubers-strategy-to-upgrading-2m-spark-jobs/), resumen de buscador).
- **Streaming DBs:** el claim de RisingWave (22/27 queries Nexmark vs Flink) y las comparaciones de Materialize son de proveedor ([RisingWave](https://risingwave.com/blog/best-apache-flink-alternatives-2026/)).

| Necesidad | Motor sugerido [Inferencia derivada de las fuentes] | Evitar si |
|---|---|---|
| Frescura de minutos hacia lakehouse | Flink o Spark a Hudi/Iceberg (Uber: -25 % de cómputo frente a batch) | El batch recomputa poco; añade small files y compactación |
| SLA sub-segundo stateless sobre Spark existente | Spark RTM (límites OSS) | Se necesita estado en OSS hoy |
| Estado grande + event time | Flink 2.x | No hay capacidad de operar el clúster |
| Lógica embebida en servicio JVM | Kafka Streams (4.3 sigue invirtiendo) | Fuentes no Kafka, estado enorme |
| SQL interactivo/federado | Trino (FTE solo para ETL batch) | |
| IA multimodal/GPU | Ray Data o Daft | |
| Volúmenes de un nodo (<~1 TB) | DuckDB o Polars | Alta concurrencia de escritura |

### 6.6 ¿Streaming real o batch frecuente?

El streaming se justifica cuando el retraso es caro (seguridad, fraude, obligaciones legales, decisiones automáticas) o el consumidor es una app o agente que necesita estado fresco. La estimación "solo 5-15 % de los datos requiere tiempo real genuino" proviene de una guía secundaria y es **[No verificado]** ([youngju.dev](https://www.youngju.dev/transcribe/culture/2026-04-15-streaming-vs-batch-redefined-complete-guide-flink-risingwave-materialize-cdc-streaming-sql-deep-dive-guide-2025.en)). **[Inferencia]** Heurística: ingesta CDC o de eventos continua y barata; transformación en micro-batch o incremental; streaming real solo para el subconjunto con SLA de segundos. El coste se desplaza a small files y compactación. Conceptos estables [Práctica consolidada]: event time vs processing time, watermarks como heurística de completitud, triggers y allowed lateness, dualidad stream-tabla y backpressure; la doc oficial de semantics de Kafka y de watermarks/2PC de Flink no se recuperó. Jepsen documenta que sin idempotencia los productores Kafka-compatibles pueden duplicar escrituras y que los rebalanceos pueden rebobinar posiciones dentro de una transacción ([Jepsen](https://jepsen.io/analyses/redpanda-21.10.1)).

## 7. Modelado de datos y capa semántica

### 7.1 Guías primarias: Kimball, Inmon, Data Vault, Anchor

**Kimball [Fuente: kimballgroup.com].** El índice oficial incluye grano; tablas de hechos de transacción, snapshot periódico, snapshot acumulativo, factless, agregadas y consolidadas; dimensiones degeneradas, role-playing, junk, snowflaked y outrigger; dimensiones conformadas, bus architecture, bus matrix, drilling across; SCD tipos 0 a 7; multivalued dimensions y bridge tables; late-arriving facts/dimensions; real-time fact tables; audit dimensions ([técnicas](https://www.kimballgroup.com/techniques/dimensional-modeling-techniques/)). El grano es el nivel de detalle de una fila de hechos, se declara primero, es "binding contract on the design", conviene atómico y "different grains must not be mixed in the same fact table" ([Grain](http://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/grain/)). La bus matrix cruza procesos de negocio (filas) con dimensiones (columnas), se implementa una fila a la vez ([Bus Matrix](http://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/enterprise-data-warehouse-bus-matrix)).

| SCD | Mecánica ([Design Tip 152](https://www.kimballgroup.com/2013/02/design-tip-152-slowly-changing-dimension-types-0-4-5-6-7/)) | Uso típico |
|---|---|---|
| 0 | Retiene el original | Atributos de fecha, claves durables |
| 1 | Sobrescribe | Correcciones sin historia |
| 2 | Nueva fila por cambio | Historia analítica |
| 3 | Nueva columna con valor previo | Un solo cambio previo |
| 4 | Mini-dimensión para atributos volátiles; el hecho guarda ambas claves | Atributos que cambian muy rápido |
| 5 | Tipo 4 + outrigger Tipo 1 con perfil actual | |
| 6 | Atributos Tipo 1 (actuales) dentro de una dimensión Tipo 2 | Historia y estado actual en una dimensión |
| 7 | El hecho lleva clave sustituta Tipo 2 y clave durable ligada a la fila actual | Ambos puntos de vista |

Bridge tables: el hecho apunta a una group key y el bridge tiene una fila por valor; con dimensiones Tipo 2 debe llevar fechas de vigencia y las consultas deben acotarse a un punto en el tiempo ([Kimball](http://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/multivalued-dimension-bridge-table)). Kimball desaconseja el snowflaking por comprensibilidad y rendimiento ([Snowflaked](http://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/snowflake-dimension)).

**Kimball vs Inmon (CIF).** Según el texto de Kimball Group (2004, **descripción de Kimball sobre CIF, no texto de Inmon**), CIF exige un EDW normalizado en 3NF antes de los marts dimensionales; Kimball sostiene que el dato atómico "must be dimensionally structured" y que la integración viene de dimensiones conformadas ([Kimball Group](https://decisionworks.com/2004/03/differences-of-opinion/)). La definición canónica de Inmon (subject-oriented, integrated, non-volatile, time-variant) se cita en fuentes que remiten a la 4ª ed. (2005); el año 1992 no se pudo verificar ([O'Reilly](https://www.oreilly.com/library/view/pentaho-solutions-business/9780470484326/ch06.html), snippet). Sin acceso a texto primario de Inmon.

**Data Vault 2.0.** Concebido por Linstedt (90s), liberado en 2000, DV2.0 en 2013; hubs (claves de negocio), links (relaciones, normalmente N:M), satellites (atributos append-only con historia), Raw Vault y Business Vault (PIT y bridge), típicamente alimentando marts en estrella; requiere arquitectos con experiencia y no está optimizado para consulta directa desde BI ([Wikipedia](https://en.wikipedia.org/wiki/Data_vault_modeling), secundaria con etiquetas de cita faltantes). Libros: Linstedt (2010); Linstedt y Olschimke (2015/2016) ([Elsevier](https://www.elsevier.com/books/catalog/isbn/9780128025109)). La Data Vault Alliance ofrece certificación CDVP2.1 y un programa de certificación de herramientas ([DVA](https://datavaultalliance.com/)). Los trade-offs (insert-only crece; satélites por fuente exigen consultas complejas; 3-5 fuentes estables pueden ir con estrella; hash keys pierden contra secuenciales en joins) provienen de proveedores que venden servicios DV/Snowflake ([WhereScape](https://www.wherescape.com/blog/data-vault-on-snowflake-guide/), [phData](https://www.phdata.io/blog/optimizing-snowflakes-performance-for-data-vault-modeling/)): **sin crítica independiente**. **Anchor modeling:** técnica abierta en 6NF (Anchors, Attributes, Ties, knots) desarrollada desde 2003 con la Universidad de Estocolmo ([ER09](https://www.anchormodeling.com/wp-content/uploads/2010/08/Anchor_Modeling_ER09_Presentation.pdf), snippet).

### 7.2 Modelado en columnar cloud: lo que dice la documentación

| Plataforma | Hecho verificado | Fuente |
|---|---|---|
| BigQuery | "Funciona mejor con datos desnormalizados"; nested/repeated (STRUCT, ARRAY) preservan relaciones; límite de 15 niveles de anidamiento | [docs](https://docs.cloud.google.com/bigquery/docs/nested-repeated) |
| Snowflake VARIANT | Usar VARIANT si no se sabe cómo se consultará; aplanar fechas/números en string o arrays mejora pruning; subcolumnarización hasta 200 elementos por partición; límite 128 MB sin comprimir | [docs](https://docs.snowflake.com/en/user-guide/semistructured-considerations) |
| Snowflake clustering | Solo tablas muy grandes (típicamente multi-TB), consultas selectivas, poco modificadas; cuesta créditos; 3-4 columnas máx. | [docs](https://docs.snowflake.com/en/user-guide/tables-clustering-keys) |
| Constraints | Snowflake estándar: PK/FK/UNIQUE no se imponen, NOT NULL y CHECK sí; hybrid tables imponen todos. Databricks: PK/FK informativos (GA desde DBR 15.2), UNIQUE en Public Preview (DBR 18.2+), NOT NULL y CHECK se imponen | [Snowflake](https://docs.snowflake.com/en/sql-reference/constraints-overview), [Databricks](https://docs.databricks.com/aws/en/tables/constraints) |

**[Inferencia]** Como PK/FK no se imponen en Snowflake ni Databricks, la unicidad del grano debe validarse con tests (por ejemplo `unique_combination_of_columns` de dbt_utils, no verificado en esta pasada). La preferencia por estrella frente a snowflake se justificaba por comprensibilidad y ETL, razones aún vigentes.

### 7.3 ¿OBT frente a estrella? La evidencia es de una sola fuente patrocinada

Existe **un solo benchmark con método declarado**: el blog de Fivetran (16-ago-2022) sobre un subset de TPC-DS (store_sales con 4 dimensiones; Redshift, Snowflake X-Large, BigQuery; caché desactivada) halló la OBT más rápida en 9 de 10 consultas en Redshift (25-30 % global), ~25 % en Snowflake pero con la estrella ganando en tres consultas, y ~49-50 % en BigQuery; en Redshift la OBT ocupó 60,3 GB frente a 29,8 GB. El autor reconoce no ser experto en BigQuery/Snowflake y no explica los resultados de Snowflake; el dataset y el blog son de Fivetran ([Fivetran](https://fivetran.com/blog/obt-star-schema)). Un segundo post (InterWorks, 12-mar-2024) da 40 s vs 77 s sin tamaño de datos ni warehouse (SQL Server PDW) y advierte que la tabla plana consume más disco, pierde la dimensión compartida como filtro en Tableau y es costosa de reconstruir ([InterWorks](https://interworks.com/blog/2024/03/12/comparing-query-performance-of-star-schemas-vs-flat-tables/)). **No hay benchmark oficial de Snowflake, BigQuery o Databricks ni estudio revisado por pares.** **[Inferencia]** El 25-50 % es indicativo para BI simple sobre un hecho y cuatro dimensiones; no cubre SCD, múltiples hechos ni el coste de reconstrucción. Mida con su carga.

### 7.4 Activity schema, streaming, CDC, bitemporalidad, evolución y contratos

- **Activity schema:** presentado en el blog de dbt (29-oct-2021) por Narrator: una tabla de serie temporal de 11 columnas que reemplaza hechos y dimensiones ([dbt](https://www.getdbt.com/blog/activity-schema-data-modeling-with-a-single-table)); solo hay fuentes del promotor y secundarias; no se pudo abrir la spec ni hay crítica independiente. **[Inferencia]** encaja en analítica de producto y journeys, no en finanzas o inventario con snapshots.
- **Capa mart en dbt:** marts "wide, rich" por entidad de negocio (staging → intermediate → marts) ([dbt](https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview)).
- **Delta Change Data Feed:** añade `_change_type` (insert, update_preimage, update_postimage, delete), `_commit_version`, `_commit_timestamp`; se activa con `delta.enableChangeDataFeed=true` y solo registra cambios posteriores a la activación ([docs](https://docs.delta.io/latest/delta-change-data-feed.html)).
- **Bitemporalidad:** valid time (cuándo es cierto en el mundo) y transaction time (cuándo lo registró la base); SQL:2011 añadió tablas de application-time, system-versioned y bitemporales ([Wikipedia](https://en.wikipedia.org/wiki/Temporal_database)). **[Inferencia]** SCD2 sola no distingue correcciones tardías.
- **Evolución de esquema en Iceberg:** add/drop/rename/widen/reorder son cambios de metadata; los IDs únicos evitan leer la columna equivocada ([docs](https://iceberg.apache.org/docs/latest/evolution/)).
- **Contratos de modelo dbt:** `contract.enforced: true` exige nombre y tipo de todas las columnas, verifica antes del build, cubre table/view/incremental (con `on_schema_change` append_new_columns o fail), no cubre Python models, materialized views, ephemeral, snapshots ni seeds; detecta cambios rompientes (quitar columna, cambiar tipo, quitar constraints desde 1.6, quitar modelo desde 1.9); valida forma, no contenido ([dbt](https://docs.getdbt.com/docs/mesh/govern/model-contracts)).
- **Modelo CDC [Inferencia]:** raw/bronze append-only de cambios → dimensión SCD2 o tabla de estado actual (equivale a un satélite de DV o snapshot SCD2).

### 7.5 Capas semánticas: cronología corregida

| Hito | Fecha | Fuente |
|---|---|---|
| MetricFlow pasa a Apache 2.0 (Coalesce 2025; esperan donarlo a una fundación) | **14-oct-2025** (no dic-2025) | [dbt blog](https://www.getdbt.com/blog/open-source-metricflow-governed-metrics); README: v0 a 0.140.0 AGPL, 0.150.0 a 0.208.2 BSL, ≥0.209.0 Apache 2.0 ([GitHub](https://github.com/dbt-labs/metricflow)) |
| OSI v1 publicada (Apache 2.0), vendor-neutral: datasets, métricas, dimensiones, relaciones, contextos | 27-ene-2026 | [Snowflake](https://www.snowflake.com/en/blog/open-semantic-interchanges-specs-finalized/) |
| Renombrado a **Apache Ossie (Incubating)** por colisión de acrónimo | ~10-jul-2026 (Dremio dice jun-2026; Snowflake publica 8-jul) | [Ossie](https://ossie.apache.org/updates/ossie-enters-apache-incubator/), [Dremio](https://www.dremio.com/blog/apache-ossie-the-open-semantic-interchange-joins-the-apache-incubator), [Snowflake](https://snowflake.com/en/blog/apache-ossie-open-semantic-interchange-incubator) |
| Snowflake Semantic Views: definir GA (Summit jun-2025); consultar GA en release 9.25 (25-28 ago-2025); Snowsight GA 2-oct-2025; compartir GA 4-nov-2025 | 2025 | [Summit](https://docs.snowflake.com/en/release-notes/2025/june-summit), [9.25](https://docs.snowflake.com/release-notes/2025/9_25) (algunas fechas por snippet) |
| Databricks Metric Views: Public Preview 29-may-2025; "Unity Catalog Business Semantics GA" 2-abr-2026; núcleo hacia Spark OSS (SPARK-54119, sin versión); materialización automática y creación por UI aún en Preview | 2025-2026 | [Databricks blog](https://www.databricks.com/blog/redefining-semantics-data-layer-future-bi-and-ai) |
| AtScale libera SML como estándar abierto (se une a OSI en ene-2026) | 10-sep-2024 | [Business Wire](https://www.businesswire.com/news/home/20240910415282/en) (snippet) |

Detalles: Ossie reporta 17 socios de lanzamiento y ahora más de 50 organizaciones, con grupos de trabajo Metric Language, Catalog y Ontology; el repo tiene spec JSON/YAML, conversores (dbt, GoodData, Polaris, Salesforce), licencia Apache-2.0 y su ROADMAP **no fija número de spec ni fecha de release**; "Incubating" no implica estabilidad ni endoso pleno de la ASF ([Ossie](https://ossie.apache.org/updates/ossie-enters-apache-incubator/), [ROADMAP](https://github.com/apache/ossie/blob/main/ROADMAP.md)). El dbt Semantic Layer gestionado requiere planes Starter, Enterprise o Enterprise+ ([dbt](https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl)). Cube Core: cubes y views en YAML o JS, pre-aggregations en Cube Store, APIs SQL/REST/GraphQL y MCP; la licencia no se verificó ([Cube](https://docs.cube.dev/docs/introduction)). LookML es independiente del dialecto ([Google](https://docs.cloud.google.com/looker/docs/what-is-lookml)). Atlan afirmó (sin verificar) que ningún producto soportaba aún import/export OSI.

**Text-to-SQL con grounding semántico.** dbt Labs (7-abr-2026; ACME Insurance, 15 tablas 3NF; 11 preguntas x 20 corridas): sin modelado extra text-to-SQL 64,5 % frente a Semantic Layer 72,7 %; con modelos adicionales generados por LLM el SL llega a 98,2-100 %; text-to-SQL sobre datos modelados 84,1-90,0 %. Caveats del post: un solo dataset, sin intervalos de confianza, el autor vende el producto ([dbt](https://docs.getdbt.com/blog/semantic-layer-vs-text-to-sql-2026)). **[Inferencia]** el mayor salto vino del modelado de datos, no solo de la capa semántica. Las cifras de Snowflake BIRD 57→78 %, Looker -66 % de errores y Strategy 88,2 % vs 100 % son de proveedores (solo snippets): no usarlas como evidencia independiente.

### 7.6 Marco de decisión de modelado [Inferencia, umbrales propios]

| Contexto | Recomendación |
|---|---|
| Equipo 1-5, <10 fuentes, un dominio | Staging → marts dimensionales (estrella, dimensiones conformadas, bus matrix); SCD2 solo donde la historia importa; capa semántica nativa o dbt/MetricFlow; evitar DV |
| Equipo mediano, varios dominios, fuentes cambiantes | Kimball con conformidad estricta + contratos dbt en las interfaces; capa de integración si los cambios de fuente rompen marts |
| Grande, muchas fuentes, M&A, regulado | Raw Vault + Business Vault + marts estrella; requiere automatización y formación; PIT/bridge para rendimiento |
| Alta volatilidad de esquema fuente | Iceberg/Delta, VARIANT/RECORD en raw, contrato en el borde de consumo |
| Reconstruir "lo que sabíamos entonces" | Modelado bitemporal |
| Producto/journeys | Tabla de eventos tipo activity schema; estrella para finanzas/inventario |
| BI con latencia crítica | OBT como materialización derivada, medida con carga propia |
| Agentes / text-to-SQL | Capa semántica gobernada + datos modelados + benchmark propio |

## 8. Calidad, observabilidad, lineage, contratos y gobernanza

### 8.1 Herramientas: versiones, licencias y estado

| Herramienta | Estado verificado (oct-2026) | Fuente |
|---|---|---|
| Great Expectations (GX Core) | 1.24.0 (7-oct, año inferido), Python 3.10-3.14; 1.23.2 corrige ruptura con SQLAlchemy 2.1; Apache-2.0; GX Cloud: Developer (gratis), Team, Enterprise sin precios públicos | [releases](https://github.com/great-expectations/great_expectations/releases), [PyPI](https://pypi.org/pypi/great-expectations/json), [pricing](https://greatexpectations.io/pricing) |
| **Soda Core** | PyPI 4.26.0 (6-oct-2026), licencia "Proprietary" en metadatos. **Cambio de Apache-2.0 a Elastic License 2.0** (cabecera "Oct 8, 2026", cuerpo "Published Jan 27, 2026": fecha ambigua): prohíbe ofrecerlo como servicio gestionado a terceros, eludir license keys y quitar avisos; uso interno/producción, forks y consultoría siguen permitidos. v4 = "motor de data quality y data contracts" con YAML de contrato (`soda contract verify`); paquetes `soda-{datasource}`; primer release público v4 = 4.0.5 (28-ene-2026), cambio rompiente de SodaCL a contratos | [PyPI](https://pypi.org/project/soda-core/), [blog](https://soda.io/blog/soda-core-license-update-moving-to-elastic-license), [LICENSE](https://github.com/sodadata/soda-core/blob/main/LICENSE), [README](https://github.com/sodadata/soda-core) |
| Soda Cloud | Free $0, Team $750/mes, Enterprise a medida | [pricing](https://www.soda.io/pricing) (proveedor) |
| Elementary | CLI Apache-2.0, 0.26.1 (11-oct-2026); trabaja con `dbt-data-reliability`; Cloud es la oferta comercial | [PyPI](https://pypi.org/project/elementary-data/) |
| Deequ | Apache-2.0; Maven 3.0.3-spark-3.5 (actualizado 2026-09-16); PyDeequ para Python | [Maven](https://repo1.maven.org/maven2/com/amazon/deequ/deequ/maven-metadata.xml) |
| Pandera | MIT (Union.ai); valida pandas, polars, pyspark, ibis, dask, modin, pyarrow | [docs](https://pandera.readthedocs.io/en/stable/) |
| DataHub | Apache-2.0; `acryl-datahub` 1.7.0.14 estable (29-sep); 1.8.0rc4/rc5 (8-oct, pre-release); LTS v1.6.0.3 (25-sep) con hardening de seguridad | [PyPI](https://pypi.org/project/acryl-datahub/), [releases](https://github.com/datahub-project/datahub/releases) |
| OpenMetadata | 2.0.5 (8-oct), 2.0.4, 2.0.3, 2.0.2 ("MCP tool consolidation"). Repo Apache-2.0, **pero** el paquete PyPI `openmetadata-ingestion` 2.0.5.0 declara "Collate Community License Agreement": contradicción no resuelta | [releases](https://github.com/open-metadata/OpenMetadata/releases), [PyPI](https://pypi.org/project/openmetadata-ingestion/) |
| OpenLineage | 1.53.0 (1-sep), 1.52.0, 1.51.0; facets explícitos, Spark 4.2, `dbt_model` facet; LF AI & Data "Graduate" | [releases](https://github.com/OpenLineage/OpenLineage/releases), [docs](https://openlineage.io/docs/) |
| Marquez | Implementación de referencia de OpenLineage (WeWork); la web no confirma gobernanza LF | [sitio](https://marquezproject.ai/) |
| **ODCS (Bitol)** | **v3.2.0 publicada** (tag 8-sep; año inferido 2026): bloque `context` para agentes de IA, synonyms, variables, tipos vector/map/enum, measures/dimensions, deprecation, 9 tipos de server nuevos (Iceberg, HANA, Teradata, Exasol, Actian), 5 RFCs compartidas con ODPS. v3.1.0 (8-dic-2025): relaciones (FK), estructura `team`, métricas de calidad. Bitol es proyecto de **incubación** de LF AI & Data (no "graduated") | [releases](https://github.com/bitol-io/open-data-contract-standard/releases), [tag](https://github.com/bitol-io/open-data-contract-standard/releases/tag/v3.2.0), [bitol.io](https://bitol.io/) |
| Data Contract Specification (datacontract.com) | **Deprecada**: migrar a ODCS; soportada hasta fin de 2026; última 1.2.1. Data Contract CLI (MIT, 1.2.4) soporta ODCS nativamente | [spec](https://github.com/datacontract/datacontract-specification), [CLI](https://github.com/datacontract/datacontract-cli) |
| PayPal | Abrió su plantilla (Apache-2.0) en mayo-2023; hoy el repo dice que "ha evolucionado y se llama ODCS" | [GitHub](https://github.com/paypal/data-contract-template) |

**[Inferencia]** La afirmación de la primera versión de que ODCS v3.2 "es solo un RFC" está obsoleta; sin embargo, bitol.io y su web de docs no mencionan v3.2 (cacheadas), así que **pinee la versión por tag**. Soda ya no es "open source" en sentido OSI para el core v4: para equipos que valoren OSI/Apache quedan GX Core y Elementary CLI. Riesgo de gobernanza: los dos catálogos OSS dependen de un proveedor comercial (DataHub Cloud, Collate); vigile licencias de paquetes (casos Soda y OpenMetadata).

### 8.2 Contratos de datos: mecanismos y evidencia de adopción

**Evidencia de adopción: débil y patrocinada.** El 61 % de "organizaciones usa contratos operativamente" proviene de un estudio BARC patrocinado por Actian (artículo del 21-abr-2026, >300 respondientes, sin metodología ni desglose publicados; la primera versión citaba 308); úsese solo con la etiqueta "encuesta patrocinada por proveedor" ([Actian](https://www.actian.com/blog/data-intelligence/barc-x-actian-research-data-products-enter-the-enterprise-roll-out-phase/)). Los casos de referencia están documentados como origen/arquitectura, no como resultados: GoCardless (Andrew Jones) pensó el problema en agosto de 2020, escribió en abril de 2021 y describió la implementación en diciembre de 2021 con un "consumer working group" ([AtScale podcast](https://www.atscale.com/podcast/data-contracts-with-andrew-jones/), [Bigeye](https://bigeye.com/the-observatory/andrew-jones-gocardless)); Convoy (Chad Sanderson) tuvo la plataforma interna "Chassis", solo en resúmenes de podcast; **no se halló caso de Netflix con resultados**. Una tesis de Aalto con 10 entrevistas señala roles y ownership poco claros ([Aalto](https://aaltodoc.aalto.fi/items/9643d2ad-40ad-4cdb-a12d-792695ec30c1)).

**Mecanismos de enforcement verificables.** dbt `contract: enforced` (ver 7.4); Schema Registry de Confluent: modo por defecto BACKWARD (no transitivo), siete modos (BACKWARD, BACKWARD_TRANSITIVE, FORWARD, FORWARD_TRANSITIVE, FULL, FULL_TRANSITIVE, NONE); backward = consumidores primero, forward = productores primero; para Protobuf se recomienda BACKWARD_TRANSITIVE ([Confluent](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html)). **[Inferencia]** BACKWARD no transitivo puede permitir una cadena de cambios que rompa consumidores antiguos: con retención larga o replay, use *_TRANSITIVE. El soporte de constraints depende de la plataforma (Postgres las aplica todas, Athena ninguna).

**Contratos eficaces [Inferencia]:** (1) esquema ejecutable en CI o registro, (2) semántica, SLA y owner (ODCS), (3) proceso de cambio con los consumidores. Trampas: contratos sin dueño productor, sin incentivos, sobre tablas internas, y confundirlos con esquema. Thoughtworks listó "Data contract CLI" en el Radar (detección de breaking changes en CI/CD); la posición exacta de "Data contracts" en el Radar es **inconsistente entre espejos** y no se confirmó.

### 8.3 Observabilidad: construir o comprar (sin la regla de "20 ingenieros")

**La heurística "~20 ingenieros" se descarta.** La única cifra numérica encontrada es una opinión de un post de Medium ("<15 construir, >20 comprar") sin metodología ([Medium](https://medium.com/@aidelearning/data-observability-in-2026-monte-carlo-vs-great-expectations-vs-soda-a-data-engineers-honest-7c8cab1b68f1)); las fuentes serias hablan de talento disponible, riesgo y TCO ([Acceldata](https://www.acceldata.io/blog/choosing-open-source-vs-paid-data-observability-solutions), [Bigeye](https://www.bigeye.com/blog/data-observability-build-or-buy), [Last9](https://last9.io/blog/build-vs-buy-observability-stack), todas de proveedor). **[Inferencia]** Criterio defendible: comprar cuando haya muchas fuentes y equipos y poca capacidad de plataforma; construir con OSS cuando el stack sea dbt-céntrico y exista ingeniería de plataforma; decidir por número de fuentes, equipos consumidores, coste de incidentes y FTE de operación, no por plantilla.

| Producto | Hecho verificado | Fuente |
|---|---|---|
| Monte Carlo | Créditos de consumo + monitores; tiers Start (hasta 10 usuarios, 1.000 monitores), Scale, Enterprise, Business Critical; precios "Request pricing"; 400+ clientes enterprise; ROI "375 %" de un estudio Forrester es cifra del proveedor, no verificada | [pricing](https://montecarlo.ai/pricing), [home](https://montecarlo.ai/) |
| Bigeye | Plataforma "AI Trust", MCP server, monitoring as code; sin precios | [bigeye.com](https://www.bigeye.com/) |
| Metaplane | Adquirida por Datadog (anunciado 23-abr-2025; términos no divulgados) | [TechCrunch](https://techcrunch.com/2025/04/23/datadog-acquires-ai-powered-observability-startup-metaplane) |
| Datadog Data Observability | Monitorización ML, lineage, jobs, coste de Spark/Databricks; sin precio ni estado GA/preview en la página | [docs](https://docs.datadoghq.com/data_observability/) |
| Anomalo | Agentes; SaaS o VPC del cliente; SOC2 Type II | [anomalo.com](https://www.anomalo.com/) |
| Catálogos comerciales | Estimaciones de terceros contradictorias: Atlan ~$25K-$150K/año; Alation ~$198K-$414K; Collibra ~$170K-$510K; negociado 15-40 % bajo lista. **Precios reales no públicos** | [CostBench](https://costbench.com/stats/data-catalog-pricing-2026/) |

La cifra de "0,25-1,0 FTE de coste oculto del OSS" de la primera versión sale de un análisis sesgado y queda **[No verificado]**. **[Inferencia]** Tras la compra de Metaplane y el giro de Monte Carlo/Bigeye hacia "AI trust/agents", el mercado converge hacia catálogo + observabilidad + gobernanza, con riesgo de lock-in.

### 8.4 Blueprint mínimo viable de gobernanza

**Marcos verificados.** DGI propone 10 componentes (Mission and Value; Beneficiaries; Data Products; Controls; Accountabilities; Decision Rights; Policy and Rules; Process, Tools and Communication; Data Work Program; Participants) y distingue "little g" (productos, catálogos, definiciones, metadatos, controles) de "Big G" (derechos de decisión, responsabilidades, políticas) ([DGI](https://datagovernance.com/the-dgi-data-governance-framework/)). DAMA habla de la 2ª edición del DMBOK y de un proyecto "DAMA-DMBOK 3.0" iniciado en 2025 sin fecha ([DAMA](https://dama.org/learning-resources/dama-data-management-body-of-knowledge-dmbok/)); la lista de 11 áreas no se confirmó en la página (conocimiento general). ISO 8000 e ISO/IEC 25012: las páginas de ISO dieron 403, sin verificar. DCAM no se consultó.

**Blueprint de siete pasos [Inferencia, mapeado a DGI/DAMA]:**
1. Charter de una página: misión, beneficiarios, alcance.
2. Roles y derechos de decisión: owner por dominio o data product, steward nominado, data council trimestral pequeño, RACI de cambios breaking.
3. Inventario de datos críticos (CDE) con tier y owner en el catálogo elegido.
4. Controles ejecutables: contratos ODCS o dbt, tests con Soda/GX en tier-1, severidades y runbooks.
5. Políticas: clasificación, retención, acceso (ABAC por tags), registro de excepciones.
6. Medición: % de activos tier-1 con owner, descripción y contrato; incidentes y MTTR; frescura frente a SLO.
7. Cadencia trimestral; evolucionar a MDM solo si hay entidades maestras duplicadas entre sistemas.

### 8.5 Catálogos y gobierno por plataforma

| Plataforma | Capacidad verificada | Fuente |
|---|---|---|
| Microsoft Purview | Data Map + Unified Catalog; el Unified Catalog factura por "activo gobernado" (ejemplo oficial: 200 activos = $100 por 30 días, ≈$0,50/activo/mes derivado; precios por región como "$-") | [Purview](https://learn.microsoft.com/en-us/purview/purview), [precios](https://azure.microsoft.com/en-us/pricing/details/purview/) |
| Google | Dataplex Universal Catalog **renombrado Knowledge Catalog el 10-abr-2026** (API/IAM sin cambios): discovery, lineage a nivel de columna, escaneos de calidad con ML, data products con SLA/contratos | [docs](https://docs.cloud.google.com/dataplex/docs/introduction) |
| Databricks Unity Catalog | RBAC/ABAC, row/column filters, lineage, monitoreo de calidad; habilitado por defecto para workspaces nuevos desde 8-nov-2023. UC OSS: Apache-2.0, proyecto sandbox de LF AI & Data | [Databricks](https://docs.databricks.com/aws/en/data-governance/unity-catalog/), [GitHub](https://github.com/unitycatalog/unitycatalog) |
| Snowflake | Data Metric Functions + expectations; anomaly detection solo de volumen y freshness; requiere Enterprise Edition; cómputo serverless facturado como "Data Quality Monitoring"; no soporta hybrid tables, streams ni shares | [docs](https://docs.snowflake.com/en/user-guide/data-quality-intro) |
| AWS Lake Formation | Permisos finos columna/fila/celda sobre Glue Data Catalog, LF-Tags (TBAC), ABAC, auditoría con CloudTrail; es control de acceso más que catálogo de negocio | [docs](https://docs.aws.amazon.com/lake-formation/latest/dg/what-is-lake-formation.html) |
| MDM | Gartner Magic Quadrant MDM 2026 (publicado 6-abr-2026) evaluó 20 proveedores; Reltio y Profisee afirman ser Leaders (material de proveedor); posicionamientos completos tras paywall | [Gartner](https://www.gartner.com/en/documents/7683461) |

### 8.6 Calidad por capas, WAP, SLOs y FinOps de datos

**Pirámide [Inferencia con soporte documental]:** contratos y esquema → tests deterministas (dbt, GX, Soda, Deequ, Pandera) → Write-Audit-Publish en tablas críticas → monitorización estadística de frescura, volumen y esquema. Las plataformas ya incluyen monitores básicos (Snowflake DMF, Dataplex, Unity, Datadog). **WAP:** la página de branching de Iceberg lista el caso "Audit Branch" pero su cuerpo no se recuperó ([Iceberg](https://iceberg.apache.org/docs/latest/branching/)); AWS documenta WAP con ramas Iceberg y Glue Data Quality ([AWS](https://aws.amazon.com/blogs/big-data/build-write-audit-publish-pattern-with-apache-iceberg-branching-and-aws-glue-data-quality/)); Nessie ofrece semántica tipo Git, Apache-2.0 ([GitHub](https://github.com/projectnessie/nessie)). Sin fuente primaria para WAP en Delta, lakeFS hooks ni WAP exacto en Iceberg.

**SLOs de datos [Inferencia]:** SLI = frescura, completitud de volumen, tasa de verificación de contrato; SLO por data product tier-1 con presupuesto de error. Sin fuente primaria de Google SRE aplicada a datos.

**FinOps de datos [Fuente]:** FOCUS (FinOps Foundation/Linux Foundation) va por la versión 1.4; Snowflake y Databricks generan v1.3 y AWS/Azure/GCP v1.2 ([FOCUS](https://focus.finops.org/)). Snowflake: atribución con object tags y query tags (TAG_REFERENCES, WAREHOUSE_METERING_HISTORY, QUERY_ATTRIBUTION_HISTORY); el coste por query excluye idle time y solo cubre cómputo de warehouse (no storage, transferencia ni serverless) ([docs](https://docs.snowflake.com/en/user-guide/cost-attributing)). Databricks: `system.billing.usage` con `custom_tags` y `usage_metadata`, correcciones por RETRACTION/RESTATEMENT, disponibilidad ~12 h ([docs](https://docs.databricks.com/aws/en/admin/system-tables/billing)). Herramientas de coste (Select, Slingshot, Unravel) no verificadas.

## 9. Seguridad y compliance

**Aviso: investigación técnica, no asesoramiento legal.** Los textos de reglamentos y sentencias se leyeron en el servidor de la Oficina de Publicaciones de la UE (CELEX), que sirve el mismo texto del Diario Oficial. Sin acceso primario: HHS.gov (403), texto completo de PCI DSS v4.0.1 (403), Trust Services Criteria de AICPA (requiere cuenta) y la casación Latombe C-703/25 P.

### 9.1 Seudonimización frente a anonimización

**[Fuente]** El Considerando 26 del GDPR dice que los datos seudonimizados atribuibles a una persona con información adicional son información sobre persona identificable, y que debe considerarse "todos los medios razonablemente probables" (singling out, por el responsable u otra persona) con factores objetivos de coste, tiempo y tecnología; el Art. 4(5) exige que la información adicional se mantenga por separado con medidas técnicas y organizativas; el Art. 25 cita la seudonimización como medida de privacy by design y exige que "por defecto" solo se traten los datos necesarios, incluida la accesibilidad; el Art. 32(1)(a) cita "la seudonimización y el cifrado" ([GDPR](https://publications.europa.eu/resource/celex/32016R0679)).

**TJUE, C-413/23 P (EDPS v SRB), 4-sep-2025 ([sentencia](https://publications.europa.eu/resource/celex/62023CJ0413), [comunicado 107/25](https://curia.europa.eu/site/upload/docs/application/pdf/2025-09/cp250107en.pdf)).** Anula la sentencia del Tribunal General y devuelve el asunto. Los datos seudonimizados "no deben considerarse, en todos los casos y para toda persona", datos personales, porque la seudonimización puede impedir que personas distintas del responsable identifiquen al interesado; pero si no se descarta que terceros tengan medios razonables (por ejemplo cruzar con otros datos), el interesado es identificable y los datos son personales. Para el deber de informar (Art. 15(1)(d) del Reg. 2018/1725, equivalente al Art. 13 GDPR), la identificabilidad se evalúa "en el momento de la recogida y desde el punto de vista del responsable". La sentencia aplica el Reg. 2018/1725 (instituciones UE), no el GDPR directamente.

**Orientación del EDPB.** WP216 (2014): "la seudonimización no es un método de anonimización"; una solución robusta debe resistir singling out, linkability e inferencia; k-anonymity no previene la inferencia ([WP216](https://ec.europa.eu/justice/article-29/documentation/opinion-recommendation/files/2014/wp216_en.pdf)). Guidelines 01/2025 sobre seudonimización (adoptadas 16-ene-2025 para consulta, cerrada 14-mar-2025; **no se halló versión final**): el dato seudonimizado sigue siendo personal incluso si la información adicional está en otras manos; introduce el "pseudonymisation domain" ([PDF](https://www.edpb.europa.eu/system/files/2025-01/edpb_guidelines_202501_pseudonymisation_en.pdf), [consulta](https://www.edpb.europa.eu/our-work-tools/documents/public-consultations/2025/guidelines-012025-pseudonymisation_en)). **Guidelines 02/2026 sobre anonimización**, v1.0, adoptadas el 7-jul-2026 para consulta pública (8-jul a 30-oct-2026): tres criterios (No Record Isolation, No Linkage, No Inference) y evaluación por entidad ("contextual") o enfoque "simplificado" más conservador ([PDF](https://www.edpb.europa.eu/system/files/2026-07/edpb_guidelines_202602_anonymisation_v1_en_0.pdf)). Opinion 28/2024 (modelos de IA; el PDF dice 17-dic-2024 y la web 18-dic): un modelo entrenado con datos personales no es anónimo en todos los casos; la probabilidad de extracción directa o por consulta debe ser "insignificante" ([PDF](https://www.edpb.europa.eu/system/files/2024-12/edpb_opinion_202428_ai-models_en.pdf)). Otros regímenes: CCPA exige que "deidentified" no permita inferir ni vincular, más tres compromisos del negocio ([CPPA](https://cppa.ca.gov/pdf/20260101_ccpa_statute.pdf)); LGPD Art. 12 excluye datos anonimizados salvo reversibilidad con "esfuerzos razonables" ([Lei 13.709](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)).

**[Inferencia] para pipelines.** Un `sha256(email)` sin clave, o una surrogate key cuyo mapeo existe en otra tabla, es seudonimización (dato personal) para el responsable: tratar esas tablas con retención, acceso y DSAR completos. Marcar datos como "anónimos" para un destinatario solo con análisis documentado por entidad y controles que impidan la reidentificación. SRB no autoriza compartir seudonimizados sin informar: la transparencia se fija en el origen. La Opinion 28/2024 exige documentar origen y base legal de datasets de entrenamiento. Pendiente: no se leyó la Joint Opinion 2/2026 EDPB-EDPS sobre el Digital Omnibus ni cómo 02/2026 trata hashing, tokenización o differential privacy en detalle.

### 9.2 Artículos GDPR que implementa un data engineer

| Artículo | Obligación | Traducción técnica [Inferencia] |
|---|---|---|
| 5(1)(c)(e), 5(2) | Minimización, limitación del almacenamiento, demostrar cumplimiento | TTL y purga física; evidencia auditable |
| 17 | Supresión "sin demora indebida" en seis supuestos, con excepciones | `erasure_ledger`, DELETE/MERGE, PURGE, expiración (ver 9.3) |
| 25(1)(2) | Privacy by design/default, incluida la accesibilidad | Deny-by-default: nuevas tablas con PII sin grants amplios |
| 28(3) | Contrato con el procesador: instrucciones documentadas, subencargados, asistencia DSAR, borrado o devolución al terminar, auditorías | Revisión de DPA y cláusula de borrado |
| 30(1) | RoPA con plazos previstos de supresión y descripción de medidas Art. 32 | `retention_policy` por dataset en el catálogo |
| 32(1) | Seudonimización y cifrado, resiliencia, capacidad de restaurar "a tiempo", pruebas regulares | Restore drills con RTO/RPO; registro de supresiones reaplicable tras restore |
| 33(1) | Notificar brechas en un máximo de 72 horas | Runbook de incidentes con contactos |
| 35(1) | DPIA para tratamientos de alto riesgo con nuevas tecnologías | DPIA para pipelines de perfilado o entrenamiento |
| 44, 46 | Transferencias: adecuación o garantías apropiadas | SCC + TIA, regionalización de datos y claves |

Fuente de la tabla: [GDPR](https://publications.europa.eu/resource/celex/32016R0679). Sin extraer textualmente: Arts. 6, 45, 47-49; guías de transferencias (Cap. V) y listas de DPIA no leídas.

### 9.3 Supresión en formatos inmutables: Delta, Iceberg, backups, crypto-shredding

**[Fuente]** Delta (Databricks): borrar primero en bronze con DELETE (individual) o MERGE contra tabla de control (masivo); propagar a silver/gold (las materialized views requieren refresh; streaming tables con `skipChangeCommits`); Delta retiene historial 30 días por defecto; ejecutar `VACUUM`; con deletion vectors "debe ejecutar también `REORG TABLE ... APPLY (PURGE)`" ([Databricks](https://docs.databricks.com/aws/en/security/privacy/gdpr-delta)). Iceberg: cada write/delete/compactación produce un snapshot que conserva datos; `expire_snapshots` borra snapshots y los ficheros que solo ellos necesitan (`older_than` 5 días y `retain_last` 1 por defecto); `remove_orphan_files` (3 días por defecto, `dry_run`); `rewrite_data_files` con `delete-file-threshold` ([Iceberg](https://raw.githubusercontent.com/apache/iceberg/main/docs/docs/spark-procedures.md)). La guía de proveedores de la primera versión (Dremio, datalakehousehub) coincide en el orden DELETE → compactación → `expire_snapshots` → `remove_orphan_files`.

**Reguladores.** El informe CEF 2025 del EDPB sobre supresión (10-feb-2026): "puede no ser aconsejable modificar o borrar información de los backups", pero entonces las organizaciones deben tener procedimientos para registrar solicitudes de supresión y aplicarlas en sistemas restaurados; muchos responsables carecían de procedimientos específicos; borrados incrementales a largo plazo dificultan demostrar "sin demora indebida"; recomienda estándares de borrado, verificar y poder demostrar el borrado, sustituir datos por cadenas aleatorias en backups; y el uso de anonimización como sustituto del borrado fue común, pero la seudonimización básica o el enmascaramiento parcial "no cumpliría los requisitos" ([EDPB CEF](https://www.edpb.europa.eu/system/files/2026-02/edpb_cef-report_2025_right-to-erasure_en.pdf)). El ICO británico acepta poner los backups "beyond use" aunque no puedan sobrescribirse de inmediato, y responder "sin demora indebida y como máximo en un mes" ([ICO](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/individual-rights/right-to-erasure/)). CCPA §1798.105(c) obliga a notificar a proveedores y terceros salvo que sea "imposible o suponga esfuerzo desproporcionado" ([CCPA](https://cppa.ca.gov/pdf/20260101_ccpa_statute.pdf)); LGPD Art. 18 IV reconoce anonimización, bloqueo o eliminación ([LGPD](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)); la Ley 25.326 argentina (Art. 16) fija 5 días hábiles para supresión o rectificación ([InfoLEG](https://servicios.infoleg.gob.ar/infolegInternet/anexos/60000-64999/64790/texact.htm)). AWS KMS con doble cifrado y XKS: revocar permanentemente la clave externa deja el texto cifrado "efectivamente crypto-shredded", aunque AWS advierte que la carga operativa y de disponibilidad supera el beneficio para la mayoría ([AWS](https://docs.aws.amazon.com/kms/latest/developerguide/keystore-external.html)).

**Runbook de supresión [Inferencia, no respaldado literalmente por los reguladores]:**
1. Registrar la solicitud en un `erasure_ledger` con identificador no reversible del sujeto y plazo (un mes del Art. 12 GDPR).
2. DELETE/MERGE en bronze y propagación a silver/gold, feature stores, índices vectoriales, cachés y exports.
3. PURGE/compactación (Delta: `REORG ... APPLY (PURGE)`; Iceberg: `rewrite_data_files`).
4. `VACUUM` o `expire_snapshots` + `remove_orphan_files` con SLA documentado (por ejemplo ≤30 días).
5. Backups con retención corta y rotación; reaplicar el ledger tras cualquier restore; documentar con el DPO.
6. Incluir time travel, clones, shallow clones y snapshots de warehouse en el alcance; Unity Catalog con filtros o máscaras no soporta time travel ni clones (9.8).
7. Mantener un tombstone del ID para evitar la re-ingesta desde fuentes upstream; logs de auditoría sin PII.
8. **Crypto-shredding por sujeto** (clave de datos por usuario/tenant, borrar la clave) es técnicamente sólido con envelope encryption por sujeto, pero **ningún regulador consultado lo avala ni lo rechaza**: documentarlo en RoPA y DPIA y no apoyarse en una clave maestra compartida.

Sin guía específica de CNIL o AEPD sobre lakehouses ni sobre crypto-shredding; time travel/Fail-safe de Snowflake y BigQuery (7 días) no verificados con documentación oficial.

### 9.4 Transferencias internacionales: EU-US Data Privacy Framework

La Decisión de ejecución (UE) 2023/1795 (10-jul-2023) sigue vigente; el Art. 45(3) GDPR exige revisión al menos cada cuatro años ([Decisión](https://publications.europa.eu/resource/celex/32023D1795)). El Tribunal General desestimó el 3-sep-2025 el recurso de anulación T-553/23 (Latombe): a la fecha de adopción EE. UU. garantizaba un nivel adecuado, con el DPRC independiente, y la Comisión puede suspender o derogar si cambia el marco ([comunicado 106/25](https://curia.europa.eu/jcms/upload/docs/application/pdf/2025-09/cp250106en.pdf)). Latombe presentó casación el 31-oct-2025 (C-703/25 P), reportada como pendiente hasta junio de 2026 en fuentes secundarias ([DOUE C/2025/6610](https://eur-lex.europa.eu/eli/C/2025/6610/oj/eng), [WilmerHale](https://www.wilmerhale.com/en/insights/blogs/wilmerhale-privacy-and-cybersecurity-law/20251201-european-court-of-justice-to-review-challenge-to-eu-us-data-privacy-framework)). **Formulación segura a oct-2026: válido, bajo recurso.** [Inferencia] Mantener SCC + transfer impact assessment y una arquitectura capaz de regionalizar datos y claves (HYOK/XKS) como contingencia; no se verificó el estado procesal en CURIA.

### 9.5 Normativa UE: Data Act, AI Act, Digital Omnibus, DORA, NIS2, CRA

| Norma | Hecho verificado | Matiz / corrección | Fuente |
|---|---|---|---|
| **Data Act** (Reg. 2023/2854) | Aplica desde 12-sep-2025. Art. 29: desde el **12-ene-2027** los proveedores de servicios de procesamiento de datos "no impondrán cargos de cambio" (incluye los de egress de cambio; entre 11-ene-2024 y 12-ene-2027 solo cargos que no superen los costes directos). Art. 34(2): en uso paralelo (multi-cloud) pueden cobrar egress "solo para repercutir los costes", sin excederlos. Art. 32: medidas contra acceso gubernamental internacional a datos no personales | **No es una prohibición general de egress**: solo cargos de cambio de proveedor; el tráfico normal y el uso paralelo siguen facturándose | [Reg. 2023/2854](https://publications.europa.eu/resource/celex/32023R2854) |
| **AI Act** (Reg. 2024/1689) | Texto original: aplica desde 2-ago-2026 (Art. 113) | Modificado por el Omnibus de IA | [Reg. 2024/1689](https://publications.europa.eu/resource/celex/32024R1689) |
| **Digital Omnibus on AI**, **Reglamento (UE) 2026/1744** (8-jul-2026; DOUE 24-jul-2026) | Alto riesgo Anexo III desde **2-dic-2027**; Anexo I desde **2-ago-2028**; nuevas prohibiciones desde 2-dic-2026; proveedores de IA generativa ya en mercado antes del 2-ago-2026 deben cumplir Art. 50(2) antes del 2-dic-2026; nuevo Art. 4a permite tratar categorías especiales de datos "en la medida estrictamente necesaria" para detectar y corregir sesgos; entra en vigor el tercer día tras su publicación | Sustituye el "acuerdo provisional sin publicación confirmada" de la primera versión | [Reg. 2026/1744](https://publications.europa.eu/resource/celex/32026R1744) |
| Digital Omnibus (parte GDPR/datos, COM(2025) 837) | Sin mandato del Consejo ni trílogos, Parlamento con >1.750 enmiendas; acuerdo realista no antes de 2027 (reportes secundarios hasta sep-2026) | **No acordado** | [Acompli](https://acompli.ie/news/digital-omnibus-gdpr-cookies-status-september-2026/) |
| AI Act Art. 10 | Gobernanza de datos de alto riesgo: origen y finalidad original, preparación (anotación, limpieza), examen de sesgos (10(2)(f)) y medidas de mitigación (10(2)(g)) | Usar el margen hasta 2027 para construir evidencia, no para posponer [Inferencia] | [Reg. 2024/1689](https://publications.europa.eu/resource/celex/32024R1689) |
| DORA (Reg. 2022/2554) | Aplica desde 17-ene-2025; Art. 9(4): política de seguridad, acceso limitado a lo necesario, autenticación fuerte y protección de claves con cifrado "basado en la clasificación de datos aprobada" | Solo si la entidad está en su ámbito (Art. 2) | [DORA](https://publications.europa.eu/resource/celex/32022R2554) |
| NIS2 (Dir. 2022/2555) | Art. 21(2): gestión de backups, cadena de suministro, vulnerabilidades, criptografía, control de acceso, MFA; transposición desde 18-oct-2024 | Aplica a entidades esenciales/importantes; si no, referencia de buenas prácticas | [NIS2](https://publications.europa.eu/resource/celex/32022L2555) |
| CRA (Reg. 2024/2847) | Aplica desde 11-dic-2027; Art. 14 desde 11-sep-2026; Anexo I Parte II(1): SBOM "en formato común y legible por máquina" para dependencias de primer nivel | Obliga a fabricantes de productos con elementos digitales, no a un pipeline interno | [CRA](https://publications.europa.eu/resource/celex/32024R2847) |

### 9.6 Sectoriales y estándares: HIPAA, PCI DSS, SOC 2, CCPA, ISO

- **HIPAA (45 CFR).** §164.514(b)(1) Expert Determination ("el riesgo es muy pequeño") y (b)(2) Safe Harbor con 18 tipos de identificadores (nombres, geografía menor a un estado, fechas salvo el año, teléfonos, correos, SSN, historia clínica, IPs, biométricos, imágenes faciales, cualquier código único, etc.) y sin "conocimiento real" de que pueda identificar; §164.312: ID único (required), cifrado en reposo y en tránsito (addressable), controles de auditoría para "registrar y examinar actividad" (standard) ([164.514](https://www.ecfr.gov/api/renderer/v1/content/enhanced/current/title-45?part=164&section=164.514), [164.312](https://www.ecfr.gov/api/renderer/v1/content/enhanced/current/title-45?part=164&section=164.312)). La guía del HHS no se pudo abrir.
- **PCI DSS.** El suplemento de tokenización del PCI SSC (agosto 2011, sobre PCI DSS 2.0) establece que "todos los elementos del sistema de tokenización, incluida la detokenización y el almacén de PAN, forman parte del CDE"; sistemas segmentados que solo almacenan tokens "pueden considerarse fuera del CDE"; si el comerciante puede recuperar el PAN, está en alcance ([PCI SSC](https://listings.pcisecuritystandards.org/documents/Tokenization_Guidelines_Info_Supplement.pdf)). En v4.0.1, 51 de los 64 requisitos nuevos eran "future-dated" y pasaron a obligatorios el 31-mar-2025 ([PCI SSC](https://blog.pcisecuritystandards.org/now-is-the-time-for-organizations-to-adopt-the-future-dated-requirements-of-pci-dss-v4-x), [v4.0.1](https://blog.pcisecuritystandards.org/just-published-pci-dss-v4-0-1)). No se leyó el texto de v4.0.1 ni existe un suplemento de tokenización específico para v4.x que se haya encontrado.
- **SOC 2.** Los Trust Services Criteria 2017 (puntos de enfoque revisados 2022) cubren seguridad, disponibilidad, integridad del procesamiento, confidencialidad y privacidad ([AICPA](https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022)); texto de CC6/CC7/CC8 no obtenido.
- **ISO.** ISO/IEC 27701:2025 (edición 2, oct-2025) es una norma independiente de sistema de gestión de privacidad, certificable sin ISO 27001; la edición 2019 figura retirada (14-oct-2025); ISO/IEC 27706:2025 define requisitos para certificadores ([ISO 27701](https://www.iso.org/standard/27701)).

**[Inferencia]** Lakehouse y PCI: tokenice el PAN en el borde (vault segmentado o proveedor) para que el lakehouse solo vea tokens no reversibles; solo así queda fuera del CDE, y debe demostrarse al QSA. SOC 2 y HIPAA piden evidencia: el CI/CD con aprobaciones y audit logs inmutables sirve como evidencia.

### 9.7 Controles técnicos

| Control | Hecho verificado | Fuente |
|---|---|---|
| Envelope encryption | Cifrar datos con una data key y cifrar esta bajo otra clave; las claves raíz de AWS KMS no salen sin cifrar de HSMs FIPS 140-3 nivel 3; BYOK con RSAES-OAEP | [AWS KMS](https://docs.aws.amazon.com/kms/latest/developerguide/kms-cryptography.html) |
| HYOK / XKS | AWS no puede crear, ver ni borrar la clave; XKS no soporta claves asimétricas, HMAC, material importado, rotación automática ni multi-región; "mayor riesgo de disponibilidad y latencia superará, para la mayoría, los beneficios" | [AWS XKS](https://docs.aws.amazon.com/kms/latest/developerguide/keystore-external.html) |
| Fabric / OneLake | Cifrado en reposo por defecto con claves de Microsoft u opción de claves del cliente; TLS 1.2 mínimo; private links; OneLake diagnostics | [Fabric](https://learn.microsoft.com/en-us/fabric/onelake/security/get-started-security) |
| Secretos dinámicos (Vault) | Credenciales por rol bajo demanda, TTL por defecto 1 h y máx. 24 h, usuario distinto por instancia, roles estáticos rotan cada 24 h | [Vault](https://developer.hashicorp.com/vault/docs/secrets/databases) |
| Workload identity (OIDC) | Los jobs de GitHub Actions obtienen un JWT por job validado por el proveedor cloud; evita credenciales de larga duración | [GitHub](https://docs.github.com/en/actions/concepts/security/openid-connect) |
| Red privada | PrivateLink conecta VPC con servicios sin internet gateway, NAT ni IP pública | [AWS](https://docs.aws.amazon.com/vpc/latest/privatelink/what-is-privatelink.html) |
| FPE | El segundo borrador de NIST SP 800-38G r1 (3-feb-2025) elimina FF3 y FF3-1 y deja FF1; versión final no verificada | [NIST](https://csrc.nist.gov/pubs/sp/800/38/g/r1/2pd) (vía buscador) |
| Desidentificación | NIST SP 800-188 (sep-2023): enfoque por riesgos, comité de revisión de divulgación; ciertas herramientas de masking no bastan | [NIST](https://csrc.nist.gov/pubs/sp/800/188/final) |
| Differential privacy | NIST SP 800-226 (mar-2025), "differential privacy pyramid" | [NIST](https://csrc.nist.gov/pubs/sp/800/226/final) |
| Zero trust | NIST SP 800-207 (ago-2020): sin confianza implícita por ubicación de red | [NIST](https://csrc.nist.gov/pubs/sp/800/207/final) |
| Supply chain | SLSA v1.0: pista Build con niveles 1-3; no cubre calidad del código ni confianza transitiva (la página remite a v1.2) | [SLSA](https://slsa.dev/spec/v1.0/about) |

**[Inferencia]** Capas recomendadas: TLS 1.2+ en tránsito; cifrado en reposo con CMK del cliente y rotación; envelope por tenant o sujeto si se necesita crypto-shredding; HYOK solo con requisito regulatorio explícito. FPE sigue siendo cifrado reversible (dato personal o CHD) y no reduce alcance PCI por sí solo. **Keyed hashing (HMAC) con la clave en KMS** es la forma práctica de seudonimizar IDs para joins: la clave es la "información adicional" del Art. 4(5). La privacidad diferencial exige presupuesto gobernado y no equivale a anonimización sin la evaluación EDPB 02/2026. Lockfiles con hashes, SBOM (CycloneDX/SPDX) por build y provenance SLSA. Sin fuente: Private Link de Azure, Private Service Connect/VPC-SC de GCP, Key Vault/GCP KMS, Secrets Manager, SPIFFE, NIST 800-53/800-57/800-218, descubrimiento de PII (Macie, DLP, Purview).

**Regímenes latinoamericanos.** Argentina: Ley 25.326, Art. 9 (medidas técnicas y organizativas) y Art. 12 (prohibida la transferencia a países sin nivel adecuado, con excepciones); reforma en el Congreso sin sanción confirmada ([abogados.com.ar](https://abogados.com.ar/nuevo-proyecto-de-ley-de-proteccion-de-datos-personales/39762)). Brasil: LGPD Arts. 33 y 46. México: nueva LFPDPPP publicada en el DOF el 20-mar-2025, con la Secretaría Anticorrupción y Buen Gobierno como autoridad tras la extinción del INAI, última reforma 14-nov-2025 ([Diputados](https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf), texto no leído).

### 9.8 Seguridad a nivel de fila y columna por plataforma

| Plataforma | Mecanismo | Limitaciones críticas para ingeniería | Fuente |
|---|---|---|---|
| Snowflake | Masking policies (dinámico y External Tokenization), basado en etiquetas; row access policies; requiere Enterprise Edition | Row access se evalúa antes que masking; una columna no puede estar en la firma de ambas; tablas de mapeo más lentas | [CLS](https://docs.snowflake.com/en/user-guide/security-column-intro), [RAP](https://docs.snowflake.com/en/user-guide/security-row-intro) |
| BigQuery | Masking sobre policy tags (SHA-256 determinista, hash con sal, email, últimos cuatro, nullify, rutina personalizada); row-level policies tipo WHERE | Hasta nueve data policies por tag; incompatible con `tabledata.list`, copy jobs, snapshots, wildcard tables; sin BI Engine; `CREATE OR REPLACE TABLE` elimina las políticas; sin poda de particiones por el filtro | [masking](https://docs.cloud.google.com/bigquery/docs/column-data-masking-intro), [RLS](https://docs.cloud.google.com/bigquery/docs/row-level-security-intro) |
| Databricks Unity Catalog | Row filters y column masks vía UDF; recomienda ABAC por governed tags; Runtime ≥12.2 LTS | No en vistas; no accesibles por Iceberg REST/Unity REST; no compartibles con Delta Sharing con filtros de tabla; sin acceso por ruta, **sin time travel ni clones**; restricciones en MERGE | [docs](https://docs.databricks.com/aws/en/data-governance/unity-catalog/filters-and-masks/) |
| Redshift | Dynamic data masking por RBAC con prioridades; RLS con políticas | AWS dejará de soportar UDFs Python **después del 30-jun-2026** (afecta masking basado en Python) | [DDM](https://docs.aws.amazon.com/redshift/latest/dg/t_ddm.html), [RLS](https://docs.aws.amazon.com/redshift/latest/dg/t_rls.html) |
| Fabric | DDM en Warehouse (default, email, random, partial); OneLake security con RLS/CLS en todos los motores | Admin/Member/Contributor ven datos sin máscara; DDM **no impide la inferencia** ("no usar DDM por sí solo"); motores externos en preview | [DDM](https://learn.microsoft.com/en-us/fabric/data-warehouse/dynamic-data-masking), [OneLake](https://learn.microsoft.com/en-us/fabric/onelake/security/get-started-security) |

**[Inferencia]** ABAC: Unity Catalog por tags gobernados, Snowflake por tag-based masking, BigQuery por policy tags; ReBAC (OpenFGA, Lakekeeper) sería una capa externa. El riesgo transversal es la copia sin control (exports, clones, snapshots, time travel, cachés), que sortea RLS y masking: aplique controles en la capa más baja posible y bloquee el acceso directo al storage. El masking dinámico es control de exposición, no anonimización ni borrado. No se verificó si ABAC de Unity es GA o preview, ni se consultó la clasificación de PII por plataforma.

### 9.9 Audit logging y mapa control-requisito

| Control en lakehouse/warehouse | Requisito que lo respalda | Implementación |
|---|---|---|
| Clasificación PII/tags en el catálogo | DORA 9(4)(d), GDPR 30 y 25 | Tags gobernados que disparan masking/ABAC |
| RBAC + RLS/CLS deny-by-default | GDPR 25(2), 32; HIPAA 164.312(a); DORA 9(4)(c) | Roles por dominio, revisión periódica |
| Masking dinámico | GDPR 25, 32 | Nunca única defensa |
| Seudonimización HMAC/token con clave en KMS | GDPR 4(5), 32(1)(a) | Clave separada, rotación |
| Tokenización de PAN en el borde | PCI (suplemento 2011) | El lakehouse solo ve tokens |
| Cifrado en reposo y tránsito, CMK/envelope | GDPR 32(1)(a); HIPAA 164.312; DORA 9(2); NIS2 21(2) | KMS + envelope por tenant; TLS ≥1.2 |
| Crypto-shredding | GDPR 17, 5(1)(e) (inferencia) | DEK por sujeto; documentar |
| Ledger de supresiones + PURGE/VACUUM/expire | GDPR 17(1), CEF 2025 | Jobs programados con verificación |
| Retención y borrado de backups | GDPR 5(1)(e), 17; ICO/EDPB | Retención corta, "beyond use", reaplicar ledger |
| Secretos dinámicos + OIDC | GDPR 32; NIS2 21(2); DORA 9(4) | Sin secretos en repos |
| Red privada | GDPR 32; DORA 9(4)(b) | Sin IP públicas |
| Audit logs inmutables | HIPAA 164.312(b); GDPR 5(2) | WORM, sin PII en claro |
| SBOM + pin de dependencias | NIS2 21(2); CRA Anexo I | Lockfiles, SLSA |
| Contratos de procesador | GDPR 28 | Cláusula de borrado o devolución |
| Residencia y llaves regionales | GDPR Cap. V, Data Act 32 | Regiones UE, SCC |

El CEF 2025 recomienda una "data deletion matrix" (tipo de dato × base legal × retención) y documentar en el RoPA las obligaciones legales de retención. Sin fuente primaria para NIST 800-53 (AU-2, AU-9) ni para retención recomendada de logs.

## 10. Plataformas cloud, on-premise, híbrido, soberanía y América Latina

### 10.1 Posicionamiento y modelos de precio: Databricks, Snowflake, BigQuery, Fabric, Redshift

Los cinco usan consumo medido (DBU, crédito, slot/TiB, CU, RPU), pero las páginas oficiales de Snowflake, Databricks, BigQuery y Fabric se renderizan con JavaScript y no devolvieron tarifas. **Lo verificado está en 5.6**; aquí solo se añaden los modelos. Databricks: DBU como medida normalizada, facturación por segundo, descuentos por compromiso (incluso multi-cloud), precios por región y nube; en Azure Databricks el precio lo fija Microsoft ([Databricks](https://www.databricks.com/product/pricing)). Snowflake: almacenamiento facturado mensual sobre promedio comprimido, on-demand o capacidad prepagada; ediciones Standard, Enterprise (multi-cluster, Time Travel extendido), Business Critical (Tri-Secret Secure, private connectivity, failover) y VPS ([Snowflake](https://www.snowflake.com/en/pricing-options/)). Fabric: reserva 1-3 años ≈41 % menos que PAYG; Autoscale Billing for Spark a tarifa PAYG sin descuento de reserva; OneLake por GB/mes con niveles hot/cool/cold; mirroring gratis hasta cierta capacidad (64 TB en F64); la facturación de red "próximamente" con ≥90 días de aviso ([Azure](https://azure.microsoft.com/en-us/pricing/details/microsoft-fabric/)). BigQuery Next '26 (22-abr-2026): "fluid scaling" GA con facturación por segundo y "hasta 34 % de ahorro"; claims de Google de consultas 35 % más rápidas y coste de procesamiento 40 % menor interanual son **afirmaciones de proveedor** ([Google](https://cloud.google.com/blog/products/data-analytics/unveiling-new-bigquery-capabilities-for-the-agentic-era)). Genie pasa a pago por uso el 8-jul-2026 (vía búsqueda sobre notas de versión) ([Databricks](https://docs.databricks.com/aws/en/release-notes/product/2026/june)).

**Synapse.** La página oficial de ciclo de vida lista Azure Synapse Analytics como "In Support" **sin fecha de retiro** (inicio 16-nov-2022; actualizada ene-2024); existe un "Fabric Migration Assistant" para pasar de dedicated SQL pool a Fabric Warehouse; Synapse Data Explorer se retiró el 7-oct-2025 ([Lifecycle](https://learn.microsoft.com/en-us/lifecycle/products/azure-synapse-analytics), [migración](https://learn.microsoft.com/en-us/fabric/data-warehouse/migration-synapse-dedicated-sql-pool-warehouse)). Los blogs que dicen "end-of-life" no tienen respaldo oficial: **no hay anuncio oficial de retiro total**.

**Lakebase.** Postgres serverless (tecnología Neon): cómputo sin estado + safekeepers + pageserver + object storage; scale-to-zero tras 5 min; ramas copy-on-write; el cómputo deja de facturarse al suspender pero el almacenamiento sigue; sin tarifas publicadas en las páginas leídas ([Databricks](https://docs.databricks.com/aws/en/oltp/projects/architecture)).

**Criterios de decisión [Inferencia]** (las unidades no son comparables 1:1: el DBU incluye o no la VM según SKU, el crédito de Snowflake incluye cómputo gestionado, el slot de BigQuery y la CU de Fabric difieren; el TCO exige POC con carga propia y precios contractuales):

| Plataforma | Elegir cuando | Riesgo principal |
|---|---|---|
| Databricks | Ingeniería, ML y streaming fuertes; un plano de gobierno (Unity) | Complejidad de costes; base Delta |
| Snowflake | SQL/BI, compartición, equipos analíticos con poca operación | Coste a escala; rebrands frecuentes |
| BigQuery | Ya en GCP, cargas ad hoc y serverless | Dependencia de GCP; falta de guardarraíles por defecto (12.1) |
| Fabric | Organización centrada en Microsoft (Power BI, Entra) | Modelo de capacidad (CU); madurez desigual entre workloads |
| AWS nativo (S3 Tables, Athena, EMR, Redshift) | Menor lock-in | Mayor esfuerzo de integración; Athena sin v3 |

### 10.2 Anuncios 2025-2026: qué está confirmado en fuente oficial

| Anuncio | Estado | Fuente |
|---|---|---|
| Databricks–Neon | Nota oficial del 14-may-2025 ("intent to acquire"; >80 % de las bases en Neon creadas por agentes de IA); Lakebase lanzado 11-jun-2025. La cifra de ~1.000 M USD **no figura** en la nota oficial: no verificada | [Neon](https://www.databricks.com/company/newsroom/press-releases/databricks-agrees-acquire-neon-help-developers-deliver-ai-systems), [Lakebase](https://www.databricks.com/company/newsroom/press-releases/databricks-launches-lakebase-new-class-operational-database-ai-apps) |
| LTAP | Anunciado 16-jun-2026; la nota dice "coming soon as part of Lakebase"; entradas de oct-2026 lo describen parcialmente operativo (Synced Tables) | [PR](https://www.databricks.com/company/newsroom/press-releases/databricks-launches-ltap-first-lake-transactionalanalytical), [blog](https://www.databricks.com/blog/lakebase-ltap-rethinking-database-storage) |
| Genie One | 16-jun-2026: Genie One, Agents y Code GA; App Builder y ZeroOps en private preview | [PR](https://www.databricks.com/company/newsroom/press-releases/databricks-launches-genie-one-all-new-agentic-coworker-every-team) |
| Unity AI Gateway GA / Governance Hub | 4-ago-2026 / 26-ago-2026 | [blog](https://www.databricks.com/blog/unity-ai-gateway-generally-available), [Governance Hub](https://www.databricks.com/blog/introducing-governance-hub-intelligent-account-level-governance-over-your-databricks-estate) |
| Mooncake, Lakehouse//RT, Panther, CustomerLake | Mooncake (1-oct-2025) solo respaldado por TechTarget; Lakehouse//RT solo por StorageNewsletter, aunque un blog oficial del VLDB 2026 menciona "LakehouseRT": **disponibilidad sin verificar** | [TechTarget](https://www.techtarget.com/data-technologies/news/366631950/Mooncake-acquisition-boosts-Databricks-database-capabilities), [StorageNewsletter](https://www.storagenewsletter.com/2026/06/26/data-ai-summit-2026-all-news), [VLDB](https://www.databricks.com/blog/building-ai-era-lakebase-streaming-and-lakehouse-innovations-vldb-2026) |
| Snowflake Summit 26 (1-4 jun 2026) | Iceberg v3 GA, Snowflake Storage for Iceberg Tables GA, Horizon bidireccional GA; control de acceso de motores externos, Scan Plan API, Connected Audit Access: private preview | [PR](https://www.snowflake.com/en/news/press-releases/snowflake-pioneers-new-open-framework-for-interoperable-enterprise-data-and-ai/) |
| Snowflake–AWS | Compromiso de 6.000 M USD a 5 años (27-may-2026), sin calendario | [PR](https://www.snowflake.com/en/news/press-releases/snowflake-expands-aws-collaboration-with-6b-commitment-to-accelerate-enterprise-agentic-ai-adoption/) |
| CoWork / CoCo / Horizon Context | Solo recaps de terceros y agendas de user groups: sin nota oficial detallada | [select.dev](https://select.dev/posts/snowflake-summit-2026-what-actually-shipped-and-what-it-means) |
| Snowflake–Crunchy Data | Blog oficial del acuerdo; precio ~250 M USD solo de TechCrunch (anónimo); Snowflake Postgres en preview con GA discrepante entre fuentes | [Snowflake](https://www.snowflake.com/en/blog/snowflake-postgres-enterprise-ai-database/) |
| Google Cloud Next '26 (22-abr) | Managed Iceberg (ex BigLake) GA; Iceberg REST catalog preview; Cross-cloud Lakehouse preview; federación de catálogos preview; replicación Spanner/AlloyDB/Cloud SQL→BigQuery GA; BigQuery remote MCP server GA; Data Engineering Agent GA | [Google](https://cloud.google.com/blog/products/data-analytics/unveiling-new-bigquery-capabilities-for-the-agentic-era) |
| Microsoft Build 2026 (2-jun) | Fabric IQ GA, Graph in Fabric GA, shortcuts a SharePoint/OneDrive GA, GPU acceleration en Warehouse early access, Azure HorizonDB preview | [Azure](https://azure.microsoft.com/en-us/blog/microsoft-build-2026-building-agentic-apps-with-microsoft-fabric-and-microsoft-databases/) |
| AWS re:Invent 2025 | Federación de catálogos en Glue, Redshift escribe en Iceberg, Iceberg V3 en EMR 7.12/Glue/S3 Tables, MWAA Serverless; claims de proveedor (EMR Serverless storage "hasta 20 % menos", MV Iceberg "hasta 8x") sin indicar GA o preview | [AWS](https://aws.amazon.com/blogs/big-data/aws-analytics-at-reinvent-2025-unifying-data-ai-and-governance-at-scale) |

Regla de redacción: use "GA" únicamente donde la nota oficial lo diga; el resto es "anunciado".

### 10.3 On-premise e híbrido: Kubernetes, object storage y MinIO

**MinIO Community Edition está oficialmente sin mantenimiento.** El repositorio muestra el banner "THIS REPOSITORY IS NO LONGER MAINTAINED" y fue **archivado por el propietario el 25-abr-2026** (solo lectura); licencia AGPLv3, edición comunitaria solo-fuente; el README remite a AIStor Free y AIStor Enterprise ([GitHub](https://github.com/minio/minio)). Cronología (secundaria): 24-may-2025 retirada de funciones de gestión de la consola comunitaria; oct-2025 sin binarios ni imágenes Docker; 3-dic-2025 modo mantenimiento; archivado y desarchivado en feb-2026; 25-abr-2026 archivado de nuevo ([It's FOSS](https://itsfoss.com/news/minio-moves-away-from-open-source/)). AIStor Free: $0, nodo único, licencia comercial no redistribuible, soporte comunitario; Enterprise por cotización (sin precio por TiB publicado) ([MinIO](https://www.min.io/pricing)). **[Inferencia]** MinIO CE ya no es base recomendable para instalaciones nuevas (sin parches de seguridad garantizados).

| Opción | Hecho verificado | Fuente |
|---|---|---|
| Ceph | Tentacle (v20); v20.2.3 el 5-ago-2026; Squid (v19.2.x) sigue recibiendo parches; mejoras de compatibilidad S3 de RGW | [docs](https://docs.ceph.com/en/latest/releases/tentacle/), [ceph.io](https://ceph.io/en/news/blog/2026/v20-2-3-tentacle-released/) |
| Rook | RGW vía `CephObjectStore`; guías comunitarias recomiendan ≥3 OSD | [FOSDEM](https://fosdem.org/2025/events/attachments/fosdem-2025-4862-declarative-object-storage-at-scale-integrating-rook-ceph-and-openstack/slides/236672/Declarati_nGa0HrT.pdf), [OneUptime](https://oneuptime.com/blog/post/2026-03-31-rook-object-storage-s3/markdown) |
| Apache Ozone | Object store/FS distribuido para analítica, petabytes y miles de millones de objetos, S3 nativo, integración con Hive, Spark, Impala | [Ozone](https://ozone.apache.org/) |
| Spark on Kubernetes (4.2) | Sin external shuffle service (usar shuffle tracking con dynamic allocation); Volcano y YuniKorn para gang scheduling; requiere K8s ≥1.34 | [docs](https://spark.apache.org/docs/latest/running-on-kubernetes.html) |
| Strimzi | CNCF incubating, versión 1.2.0; TLS/SCRAM/OAuth, rack awareness, GitOps | [Strimzi](https://strimzi.io/) |
| Flink Kubernetes Operator | Despliegue, upgrades con estado, rollbacks, autoscaler, blue/green | [docs](https://nightlies.apache.org/flink/flink-kubernetes-operator-docs-main/) |
| Appliances (Pure, VAST, Dell) | Marketing de partners de Dremio; Dell ECS/ObjectScale sin resultados; la ronda de VAST de 1.000 M USD a 30.000 M no verificada | [Dremio/Pure](https://www.dremio.com/partners/pure-storage/), [Dremio/VAST](https://www.dremio.com/blog/dremio-storage-infrastructure-partners/) |
| Trino/StarRocks | StarRocks reclama ~6,9x vs Trino en TPC-DS 1 TB (presentación de proveedor, ene-2026); caso Ksolves con "68 % menos infraestructura" (proveedor) | [Speaker Deck](https://speakerdeck.com/markosun/starrocks-introduction-for-iceberg-meetup-japan-number-4), [Ksolves](https://www.ksolves.com/case-studies/big-data/starrocks-iceberg-lakehouse-logistics-real-time-analytics) |

**[Inferencia]** Stack abierto típico: Iceberg + catálogo REST (Polaris, Unity, Nessie) + Trino/Spark/StarRocks + Strimzi y Flink en K8s + Ceph; Ozone si hay legado Hadoop; appliances si se acepta el lock-in de hardware. No se halló evidencia comparativa de TCO de este stack.

### 10.4 Hadoop legado y migración

El único caso con cifras es Indeed (caso de AWS, proveedor): lake de 101 PB, 18.000 datasets, 530 M de objetos S3, 190.000 consultas/día; lift-and-shift de Hadoop on-prem a AWS (S3, EMR, Glue, Athena) completado a mediados de 2023, luego Hive/ORC→Iceberg (finales de 2023) y S3 Tables con doble catálogo vía Glue; más de 1.000 h/año de mantenimiento evitadas, ahorro proyectado del 10 % anual y throughput de transacciones 10x. Lección: la compactación autogestionada consumía mucho esfuerzo ([AWS](https://aws.amazon.com/solutions/case-studies/indeed-s3-tables-case-study/)). Insider reportó "90 % menos coste de S3" en una charla de Subsurface 2023 (vía búsqueda, proveedor) ([Dremio](https://www.dremio.com/?p=11899)). Iceberg ofrece `snapshot`, `migrate` y `add_files` para Hive→Iceberg ([docs](https://iceberg.apache.org/docs/latest/hive-migration/), solo índice leído). Cloudera (8-abr-2026): LTS con soporte hasta 2032, Cloud Bursting y Lakehouse Optimizer (claims de 38 % más rápido y 36 % menos almacenamiento) ([StorageNewsletter](https://www.storagenewsletter.com/2026/04/10/cloudera-advances-hybrid-data-platform-with-long-term-stability-elastic-scale-and-open-data-interoperability/)); Iceberg GA en CDP Private Cloud desde 7.1.9 ([Cloudera](https://docs.cloudera.com/cdp-private-cloud/latest/release-summaries/topics/announcement-202309-719.html)). La afirmación de MinIO de que on-prem es más barato que la nube a ~5 PB es de proveedor, no verificada. **[Inferencia]** Patrón replicable: primero mover almacenamiento y cómputo, después cambiar el formato; basado en un único caso con patrocinador.

### 10.5 Soberanía, multi-cloud, egress y repatriación

- **AWS European Sovereign Cloud:** GA el 15-ene-2026 en Brandenburg, más de 90 servicios, inversión >7.800 M EUR, operada por residentes UE con metadatos de cliente en la UE; Local Zones soberanas planificadas en Bélgica, Países Bajos y Portugal ([Amazon](https://press.aboutamazon.com/aws/2026/1/aws-launches-aws-european-sovereign-cloud-and-announces-expansion-across-europe)).
- **Microsoft:** Sovereign Private Cloud sobre Azure Local (jun-2025), operaciones desconectadas GA (feb-2026), Azure Local hasta miles de nodos (27-abr-2026) ([blog](https://blogs.microsoft.com/blog/2026/04/27/microsoft-sovereign-private-cloud-scales-to-thousands-of-nodes-with-azure-local/)). **Google:** Data Boundary, S3NS/Thales (apunta a SecNumCloud), Distributed Cloud air-gapped ([Google](https://cloud.google.com/sovereign-cloud)). Proveedores UE: STACKIT, IONOS y OVHcloud con atestaciones BSI C5 (tipos discrepantes entre fuentes); **Gaia-X no certifica propiedad UE ni protección frente al CLOUD Act**, y en 2024 un tribunal de Ontario ordenó a OVHcloud entregar datos almacenados fuera de Canadá ([SoftwareSeni](https://www.softwareseni.com/the-european-sovereign-cloud-provider-landscape-in-2026-who-exists-and-what-they-offer/), secundaria; la tabla de precios de cómputo no verificada).
- **Egress.** Google eliminó los cargos de salida al abandonar la plataforma (salida completa en 60 días); AWS anunció un programa similar el 5-mar-2024 (requiere contactar a AWS); el EU Data Act fija cargos de cambio solo a coste desde 12-sep-2025 y prohibidos desde el 12-ene-2027 (ver 9.5) ([TechRadar](https://www.techradar.com/pro/aws-follows-google-cloud-drops-egress-fees-when-moving-data-out-of-its-system), [DCD](https://www.datacenterdynamics.com/en/news/google-axes-some-data-transfer-costs-in-preparation-for-eu-data-act/)). Egress ordinario: 100 GB/mes gratis en AWS y ejemplo de $0,09/GB desde Irlanda ([S3](https://aws.amazon.com/s3/pricing/)).
- **Repatriación.** 37signals: factura cloud >3,2 M USD/año; ~700.000 USD en servidores Dell ahorraron ~2 M/año; en S3, ~1,5 M USD/año y 18 PB en Pure Storage por 1,5 M USD, coste operativo <200.000 USD/año, ahorro ~1,3 M/año, y AWS condonó 250.000 USD de egress ([The Register](https://www.theregister.com/2025/05/09/37signals_cloud_repatriation_storage_savings), [DCD](https://www.datacenterdynamics.com/en/news/37signals-begins-exiting-aws-storage-service/)); cifras del propio DHH. **[Inferencia]** Es una empresa con cargas estables y equipo de operaciones propio: extrapolar a plataformas de datos con picos o IA exige cautela. "Soberano" depende del control operativo y jurisdiccional, no de pertenecer a Gaia-X.
- **FinOps Foundation:** fases Inform/Optimize/Operate, 6 principios, 4 dominios; actualización del framework del 20-mar-2026 ([FinOps](https://www.finops.org/framework/)).

### 10.6 América Latina

AWS opera São Paulo y México y anunció en mayo-2025 una región en Chile (3 AZ, ~4.000 M USD) para fines de 2026; el lanzamiento efectivo a oct-2026 **no está confirmado** ([AWS](https://aws.amazon.com/blogs/aws/coming-soon-aws-south-america-chile-region/)). Google Cloud tiene Querétaro (41.ª región, dic-2024), Santiago y São Paulo ([Google](https://cloud.google.com/blog/products/infrastructure/google-cloud-announces-41st-cloud-region-in-mexico)). Azure: Mexico Central (mayo-2024); Chile Central y Brazil South solo por un agregador ([cloudprice.net](https://cloudprice.net/gcp/regions/southamerica-west1)). Snowflake lanzó operaciones oficiales en Chile el 18-jun-2026 ([Snowflake](https://www.snowflake.com/en/news/press-releases/)). La cobertura por servicio (Fabric, Databricks, BigQuery, Redshift Serverless) y las regiones de Databricks y Snowflake en Brasil y México no se verificaron.

## 11. Stack moderno por categoría

El mercado se reempaqueta: ingestión y transformación (Fivetran + dbt Labs, con SQLMesh en la Linux Foundation), streaming (IBM + Confluent), orquestación (Prefect + Dagster, cierre no confirmado), plataforma + Postgres + IA (Databricks con Neon, Snowflake con Crunchy). Matt Turck redujo el mapa MAD 2025 de ~2.000 a ~1.150 logos (recorte deliberado), describe el MDS "desagregándose y ahora consolidándose" y señala el riesgo de burbuja ([MAD 2025](https://mattturck.com/mad2025/)); IBM–Confluent (~11.000 M USD), Salesforce–Informatica (~8.000 M USD) y ServiceNow–Moveworks (2.850 M USD) figuran allí.

| Categoría | Opciones maduras | Emergente o volátil | Criterio de elección | Nota de verificación |
|---|---|---|---|---|
| Ingesta y CDC | Fivetran, Debezium 3.7, Kafka Connect | Airbyte 2.x, dlt 1.31, Lakeflow Connect, Openflow, Flink CDC, zero-ETL nativo | CDC para baja latencia; mirroring nativo erosiona conectores genéricos | Versiones de 4.3 |
| Streaming y mensajería | Kafka 4.x (KRaft), Flink 2.x, Kafka Streams | Diskless (KIP-1150 aceptado, sin mainline), WarpStream, AutoMQ, RisingWave, Materialize, Redpanda | SLA de frescura y madurez del equipo | 6.4 |
| Almacenamiento | Object storage, Parquet, Iceberg, Delta | Iceberg v3/v4, DuckLake 1.0, Vortex, Lance | Interoperabilidad y catálogo | 5.1-5.5 |
| Catálogo de tablas | Unity, Glue/S3 Tables, Polaris (TLP) | Lakekeeper, Gravitino (TLP), Nessie (actividad no verificada) | Neutralidad vs integración | 5.4 |
| Motores | Spark 4.2, Snowflake, BigQuery, Databricks SQL, Trino | DuckDB (AWS), Polars, Comet 1.0, Gluten (TLP), Ray/Daft | Escala y concurrencia | 6.1 |
| OLAP en tiempo real | ClickHouse, Pinot, Druid, StarRocks | Lakehouse//RT (sin verificar) | Concurrencia y latencia de serving | Sin benchmark neutral |
| Transformación | dbt Core v1.x, Spark SQL | dbt Core v2 (alpha), Fusion, SQLMesh (LF), dbt State (preview) | Ecosistema vs entornos virtuales | 4.2 |
| Orquestación | Airflow 3.3, MWAA/Composer, Step Functions, ADF | Dagster/Prefect (cierre sin confirmar), Argo, Temporal, Kestra | Task vs asset vs evento | 4.1 |
| Calidad y observabilidad | dbt tests, GX Core, Elementary | Soda (ELv2), Monte Carlo, Bigeye, Metaplane (Datadog), OpenLineage/Marquez | Número de fuentes y equipos, coste de incidentes | 8.1, 8.3 |
| Contratos | dbt contracts, Schema Registry | ODCS v3.2.0, Data Contract CLI, ODPS | Enforcement en CI | 8.2 |
| Gobernanza y catálogo de negocio | Unity, Purview, Knowledge Catalog, DataHub, OpenMetadata, Atlan, Collibra | Catálogos con agentes y MCP | Capacidad de ingeniería y regulación | 8.5 |
| Capa semántica | dbt SL/MetricFlow (Apache 2.0), Cube, LookML | OSI / Apache Ossie, Snowflake Semantic Views, Databricks Metric Views | Agentes y métricas gobernadas | 7.5 |
| Activación | Reverse ETL (Census dentro de Fivetran) | Mercado fragmentado | Warehouse como fuente de verdad | 3.5 |
| Almacenamiento on-prem | Ceph/Rook, Ozone | AIStor (comercial), appliances | Operación vs lock-in | 10.3 |

Las áreas con poca consolidación observada (observabilidad, catálogo independiente, reverse ETL restante, calidad y contratos) lo son por ausencia de noticias de M&A encontradas, no por medición. Metaplane fue comprada por Datadog (abr-2025).

## 12. Patrones avanzados, anti-patrones e incidentes públicos

### 12.1 Incidentes públicos y modos de fallo

Los incidentes públicos permiten ordenar los modos de fallo por **cobertura de casos documentados**, no por frecuencia estadística. Los casos son de empresas con tráfico muy grande, pero los modos de fallo son genéricos.

| # | Modo de fallo | Caso primario | Hechos clave | Lección |
|---|---|---|---|---|
| 1 | Restauración/DR no probada y alertas silenciosas | GitLab, 31-ene-2017 ([postmortem](https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/)) | ~18 h de indisponibilidad; se borró el directorio del primario en lugar del secundario (~300 GB); fallaron todos los backups (pg_dump 9.2 contra BD 9.6, bucket S3 vacío, alertas por email rechazadas por DMARC); ~5.000 proyectos, ~5.000 comentarios y ~700 cuentas perdidos (estimaciones); restore lento por discos de ~60 Mbps | Asignar propiedad de la durabilidad, probar restauraciones, WAL archiving/PITR |
| 2 | Artefactos generados que se propagan sin validación | Cloudflare, 18-nov-2025 ([blog](https://blog.cloudflare.com/18-november-2025-outage/)) | Un cambio de permisos en ClickHouse duplicó columnas en la query del "feature file" de Bot Management; superó el límite de 200 features (se usaban ~60) y los proxies entraron en pánico → HTTP 5xx; se regeneraba cada 5 min; impacto principal resuelto 14:30 y total 17:06 UTC | Tratar la config generada internamente como input no confiable; kill switches globales; validar en la frontera (es un caso de "contrato" de datos) |
| 3 | Fail-open sin pruebas de sobrecarga | Cloudflare, 14-nov-2024 ([blog](https://blog.cloudflare.com/cloudflare-incident-on-november-14-2024-resulting-in-lost-logs/)) | ~3,5 h y ~55 % de logs de clientes perdidos; una config vacía activó un failsafe fail-open que intentó enviar logs de todos los clientes; Buftee pasó de ~1 M a ~40 M de buffers y, sin protecciones de sobrecarga configuradas, quedó inoperativo | Probar caminos de degradación; habilitar protecciones |
| 4 | Acoplamiento oculto entre dominios de fallo | Datadog, 8-mar-2023 ([blog](https://www.datadoghq.com/blog/2023-03-08-multiregion-infrastructure-connectivity-issue/)) | Una actualización automática de systemd (06:00-07:00 UTC) borró rutas de Cilium en varias regiones a la vez; primer servicio principal 16:44 UTC; todo operativo 9-mar 08:58; backfill histórico terminó 10-mar 06:25 | Las regiones "autónomas" compartían la ventana de actualización; priorizar live sobre histórico; los stores con metadatos por quórum se recuperaron más lento |
| 5 | Kafka: pérdida de redundancia y alertas ruidosas | Honeycomb, dic-2025 ([status](https://status.honeycomb.io/incidents/pjzh0mtqw3vt), informe preliminar) | Particiones sin líder, disco agotado, problemas de tiered storage; ingesta caída 6 h 23 min el 6-dic; SLOs con ~18 h de retraso; Activity Log perdió datos del 5-dic 20:23 al 9-dic 23:45 UTC; ~1,5 h en overload protection sin notarse | Ruido de alertas enmascara; consumidores "idle" parecen sanos; ensayar migraciones en pre-producción |
| 6 | Coste sin guardarraíles | BigQuery y Snowflake | HTTP Archive: ~14.000 USD en 2 h con un script Python (~2,5 PB a 6,25 USD/TiB, estimación del mantenedor) ([foro](https://discuss.httparchive.org/t/warning-14-000-bigquery-charge-in-2-hours/2715)); Mixmax: un proceso diario con funciones externas pasó de >24 h a <4 min al exportar/importar desde MongoDB; créditos de enero ≈ mitad de diciembre y otro -30 % en febrero ([Mixmax](https://www.mixmax.com/engineering/make-it-snow-efb88freducing-costs-in-snowflake)) | Límites por defecto; ver 12.3 |

Coralogix (jul-2019, ~10 % de logs procesados durante 6 h por reasignación de particiones) solo se conoce por resumen de búsqueda ([status](https://status.coralogix.com/incidents/b8vc1d0tttt3)). **Lagunas:** no hay post-mortems formales públicos de sobrecoste en Snowflake o Databricks con cifras (las anécdotas BigQuery de 5.000 y 15-18k USD se contradicen), ni de backfills no idempotentes ni de SCD2 a escala.

### 12.2 Patrones avanzados

| Patrón | Qué resuelve | Hechos verificados | Cuándo no |
|---|---|---|---|
| Outbox + CDC | Dual-write entre base transaccional y bus | El relay puede publicar duplicados, por lo que los consumidores deben ser idempotentes; es propenso a error (se puede olvidar escribir en el outbox) ([microservices.io](https://microservices.io/patterns/data/transactional-outbox.html)). Con Debezium: `aggregateid` como clave Kafka, UUID en header, el consumidor registra el UUID en la misma transacción; el ejemplo no cubre reintentos limitados, DLQ ni limpieza de la tabla ([Debezium](https://debezium.io/blog/2019/02/19/reliable-microservices-data-exchange-with-the-outbox-pattern/)) | Sin necesidad de integración orientada a eventos |
| Schema Registry | Contrato técnico en streaming | BACKWARD por defecto; Kafka Streams solo soporta tipos que incluyan BACKWARD ([Confluent](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html)) | Retención larga sin *_TRANSITIVE |
| Contratos de modelo | Forma en el límite productor-consumidor | Solo forma, no contenido (ver 7.4) | Como único control de calidad |
| Data sharing | Compartir sin copiar | Snowflake Open Data Sharing (Iceberg REST) en Public Preview solo admite como destino la región del proveedor; la ruta cross-region (Cross-Cloud Auto-Fulfillment) **replica los datos** y el proveedor paga egress, almacenamiento y cómputo ([Snowflake](https://docs.snowflake.com/en/user-guide/open-data-sharing), [auto-fulfillment](https://docs.snowflake.com/en/collaboration/use-auto-fulfillment-with-open-table-formats)) | Cross-region: no es "zero-copy" |
| WAP | Calidad en publicación | Iceberg branching "Audit Branch"; AWS Glue Data Quality; Nessie (ver 8.6) | Latencia crítica |
| Feature stores | Features online/offline | Databricks acordó comprar Tecton (ago-2025) para Agent Bricks; el precio ~900 M USD solo en un agregador, otras fuentes dicen no divulgado ([Perficient](https://blogs.perficient.com/databricks-acquires-tecton/)) | Estado de Feast: sin datos |
| SCD2, medallion, multi-tenancy (esquema por tenant vs RLS), DLQ, reverse ETL | | [Práctica consolidada]: sin fuente primaria en esta pasada (DLQ con límite de reintentos y alertas) | |

**[Inferencia]** Con la compra de Tecton, "feature store independiente" pierde peso. Thoughtworks Radar vol. 34 (abr-2026): Apache Iceberg en Adopt; Semantic layer, Docling y LangExtract en Trial; DuckLake, Agent Bricks, FalkorDB, "Context graph", "Role-based contextual isolation in RAG", "VLMs for end-to-end document parsing" y PageIndex en Assess; "MCP by default" en Caution; el radar usa anillos Adopt/Trial/Assess/Caution (sin Hold) ([Radar](https://www.thoughtworks.com/radar)).

### 12.3 Anti-patrones y errores comunes (ordenados por respaldo documental)

1. **Falta de propiedad y de contratos con roturas upstream silenciosas.** Reis 2026: sistemas legacy 25 %, falta de dirección 21 %, requisitos deficientes 19 %; en modelado, 59 % por presión de velocidad, 51 % por falta de ownership y solo 11 % dice que va bien (muestra autoseleccionada; titular dice 1.001 y cuerpo 1.101 respuestas, discrepancia sin explicar) ([Reis](https://joereis.substack.com/p/the-2026-state-of-data-engineering)).
2. **Artefactos generados sin validar y degradación sin probar** (incidentes 2 y 3 de 12.1).
3. **Restauración y DR no ensayados** (incidente 1).
4. **Costes sin guardarraíles:** `SELECT *`, scans sin partición, `LIMIT` creído como reductor (en tablas no clusterizadas **no** reduce los datos leídos), warehouses sobredimensionados u olvidados; el gasto que crece más que el dato sugiere duplicación y marts redundantes ([BigQuery](https://docs.cloud.google.com/bigquery/docs/best-practices-costs), [Revefi](https://www.revefi.com/blog/avoiding-snowflake-data-cost-pitfalls), proveedor).
5. **Ficheros pequeños y streaming innecesario:** se cita un overhead de Snowpipe de ~0,06 créditos por 1.000 ficheros y ficheros de 100-500 MB ([PointFive](https://www.pointfive.co/knowledge-base/inefficient-snowpipe-usage-due-to-small-file-ingestion)), sin contrastar con precios oficiales.
6. **Egress entre regiones o nubes** inadvertido.
7. **DAGs espagueti** con dependencias implícitas y backfills no idempotentes; INSERT sin clave con reintentos; `now()` en lógica.
8. **Over-engineering:** 15 herramientas para <1 TB [Inferencia].
9. **Medallion mal usado** (silver cajón de sastre, gold por consumidor); **mesh como reorganización sin plataforma**; **contratos sin enforcement**.
10. **Confiar en el masking como única defensa** (9.8) y **confundir seudonimización con anonimización** (9.1).

La encuesta de dbt Labs 2026 (proveedor) cita temas de costes que superan presupuestos, riesgo de alucinaciones y confianza; las cifras concretas de la primera versión (57 % más gasto en warehouse frente a 36 % más presupuesto; 71 % preocupado por alucinaciones; 72 % frente a 24 %) vienen de un resumen de búsqueda y **no se pudieron verificar** contra el original ([dbt Labs](https://www.getdbt.com/resources/state-of-analytics-engineering-2026-download)).

## 13. Mejores prácticas de producción: checklists y runbooks

Cada ítem remite al apartado que lo respalda; los checklists son [Inferencia] construida sobre fuentes primarias, salvo indicación.

### 13.1 Checklist de pipeline listo para producción

- [ ] Idempotente: overwrite de partición o MERGE por clave; sin `now()`; lee `data_interval_start` (4.4).
- [ ] Reintentos solo en tareas idempotentes; timeouts y límites de concurrencia; DLQ con límite de reintentos y alerta (12.2).
- [ ] Contrato en el borde (dbt `contract`, Schema Registry, ODCS fijado por tag) y política de breaking changes (8.2).
- [ ] Tests: unit tests de modelos en CI, tests deterministas de grano (unicidad, not null), frescura y volumen (7.2, 8.6).
- [ ] WAP o rama de auditoría en tablas tier-1 (8.6).
- [ ] Observabilidad: lineage (OpenLineage), frescura, volumen, esquema; alertas por frescura del asset antes que por duración de tarea.
- [ ] Runbook y on-call con SLO por data product tier-1 (8.6).
- [ ] Etiquetas de coste (tags/query tags/`custom_tags`) y alertas de presupuesto (8.6, 14).
- [ ] PII clasificada, acceso deny-by-default, borrado diseñado (9.3, 9.8).
- [ ] Credenciales dinámicas u OIDC; sin secretos en repos (9.7).
- [ ] Backups con restore drill documentado (12.1, 9.2).

### 13.2 Checklist de tabla Iceberg/Delta en producción

- [ ] Versión de formato decidida con inventario de lectores (Athena sin v3; upgrade unidireccional) (5.1).
- [ ] Compactación programada, `expire_snapshots`, `remove_orphan_files` con retención ≥ 3 días y mayor que la escritura más larga (5.7).
- [ ] Monitor de tamaño medio de fichero y de tasa de commits por tabla.
- [ ] Catálogo con credential vending y control de acceso; plan de salida si el catálogo es propietario (5.4).
- [ ] Retención de time travel alineada con política de supresión (9.3).
- [ ] En Delta catalog-managed, no activar mantenimiento automático sin probar (4.4.1 lo corrige) (5.2).

### 13.3 Runbook de incidente de calidad de datos

1. Detectar (frescura, volumen, esquema, contrato); clasificar severidad por tier.
2. Contener: pausar publicación y consumidores aguas abajo (circuit breaker); no sobrescribir con reintentos.
3. Diagnosticar con lineage (qué cambió aguas arriba: esquema, permisos, configuración generada).
4. Corregir y reprocesar con el runbook de backfill (4.4) sobre rama o staging.
5. Comunicar a consumidores y registrar el incidente (causa, MTTR, acción preventiva).
6. Si hay PII implicada: evaluar notificación de brecha en 72 h (Art. 33) con DPO (9.2).

### 13.4 Checklist de selección de plataforma

- [ ] POC con carga propia y precios contractuales (unidades no comparables) (10.1).
- [ ] Formatos abiertos y SQL portable; catálogo REST estándar.
- [ ] Residencia, cifrado con CMK y requisitos de transferencia (9.4, 9.7).
- [ ] Plan de egress y salida (Data Act desde 12-ene-2027, solo cargos de cambio) (9.5).
- [ ] Soporte del servicio en la región requerida (LatAm: verificar por servicio) (10.6).
- [ ] Riesgo de proveedor/M&A: no migrar por roadmap hasta ver releases posteriores a un cierre (4.1, 4.2).

### 13.5 Matriz de gobierno de cambios y de ownership

| Artefacto | Owner | Revisión de cambios | Evidencia |
|---|---|---|---|
| Data product tier-1 | Dominio productor | Consumer working group (patrón GoCardless) | Contrato versionado + resultados de verificación |
| Pipeline | Equipo de ingeniería | PR con CI y aprobación | Logs inmutables |
| Políticas de acceso | Data steward + seguridad | Revisión periódica | Auditoría de grants |
| Catálogo y glosario | Data council | Trimestral | % de activos con owner/descripción |

## 14. Escalabilidad, coste y mantenimiento

**Dónde está el coste.** Lakehouse: operación (compactación, expiración, catálogo, requests, egress). Warehouse: consumo opaco que se gobierna con tags, vistas de consumo (`ACCOUNT_USAGE`, system tables), apagado automático y presupuestos [Práctica consolidada]. Streaming: continuo frente a recomputo batch (Uber -25 % de cómputo) a cambio de small files y compactación (6.3). El metadato limita la tasa de commits (Delta VLDB: "varias transacciones por segundo" por tabla), lo que motiva commits de un fichero en Iceberg v4 y metadatos SQL en DuckLake (5.7).

**Cifras de coste con cautela.**

| Dato | Valor | Estado |
|---|---|---|
| Snowflake crédito AWS US East | $2/3/4/6 por edición; almacenamiento $23/TB-mes on-demand | Oficial (5.6) |
| Redshift Serverless | $0,375/RPU-h; managed storage $0,024/GB-mes | Oficial, ejemplos (5.6) |
| S3 Tables / Glue | $0,0265/GB-mes; compactación $0,002/1000 objetos + $0,005/GB; optimización Glue $0,44/DPU-h | Oficial (5.6) |
| BigQuery, Fabric, Databricks (tarifa por unidad) | — | **No verificado** |
| Ahorros FinOps de casos | Mixmax -50 % y luego -30 %; Capital One proyectó -27 % de cómputo y -43 % de tiempo de query (resumen de búsqueda) ([Capital One](https://www.capitalone.com/software/blog/snowflake-cost-optimization/)); ESO -60 % ([Snowflake](https://www.snowflake.com/blog/snowflakes-performance-optimizations-help-eso-reduce-costs-by-60)); Costco Travel -50 % ([Keebo](https://keebo.ai/wp-content/uploads/Costco-case-study.pdf)); Authentic -44 % ([casestudies.com](https://www.casestudies.com/company/espresso-ai/case-study/237-authentic-saves-44-on-snowflake-spend-with-espresso-ai)) | Autoinformados, sin metodología comparable ni importes en USD; órdenes de magnitud (30-60 %) solo para casos de partida muy ineficiente [Inferencia] |

**State of FinOps 2026** (solo fuentes secundarias): 98 % gestiona algún coste de IA (31 % en 2024, 63 % en 2025), 90 % gestiona SaaS, muestra ~1.100-1.192 profesionales y >83.000 M USD de gasto; "las ganancias fáciles ya se capturaron" ([nOps](https://www.nops.io/blog/state-of-finops-2026/), [Virtasant](https://virtasant.com/blog/state-of-finops-2026)). Reis 2026: equipos con modelado ad hoc dedican 38 % del tiempo a apagar fuegos frente a 19 % con modelos canónicos o semánticos (muestra autoseleccionada) ([Reis](https://joereis.substack.com/p/ai-is-here-but-the-hard-parts-havent)).

**Guardarraíles mínimos defendibles a partir de los incidentes [Inferencia]:** límite de bytes por query (`maximum bytes billed` en BigQuery hace fallar la query sin cargo si la estimación lo supera; dry run estima bytes; cuotas diarias por proyecto y usuario ([Google](https://docs.cloud.google.com/bigquery/docs/best-practices-costs))); statement timeout y límite de reintentos; auto-suspend con recordatorio al escalar; restore drills; límites de tamaño y validación de artefactos generados. Con facturación física en BigQuery, el time travel y el failsafe cuentan en el coste.

**Escalabilidad por componente.** Spark: AQE y skew join (6.2). Flink: estado desagregado reduce checkpoints y rescale según sus autores (6.3). Kafka: tiered storage production-ready desde 3.9; diskless sin mainline (6.4). Pequeña escala: DuckDB y Polars evitan clústeres. **Mantenimiento organizativo:** la escala pesa tanto como la técnica; la regla de "20 ingenieros" y la de "0,25-1,0 FTE" no están respaldadas y se descartan. Presión de coste 2026-27: cargas agénticas; el claim de MotherDuck de que los agentes ejecutan 29x más queries que humanos es especulación de proveedor, sin verificar.

## 15. Evolución reciente 2023-2026, IA y rol del data engineer

### 15.1 Cronología verificada

| Fecha | Hito | Fuente |
|---|---|---|
| 4-jun-2024 | Databricks anuncia la compra de Tabular (creadores de Iceberg) | [Databricks](https://www.databricks.com/company/newsroom/press-releases/databricks-agrees-acquire-tabular-company-founded-original-creators) (pasada 1) |
| 9-sep-2024 | Confluent compra WarpStream | [Business Wire](https://www.businesswire.com/news/home/20240909282386/en/Confluent-Acquires-WarpStream-to-Advance-Next-Gen-BYOC-Data-Streaming) |
| dic-2024 | Hudi 1.0 | [Hudi](https://hudi.apache.org/blog/2024/12/16/announcing-hudi-1-0-0) |
| mar-2025 | Flink 2.0; Kafka 4.0 (sin ZooKeeper) | 6.3, 6.4 |
| abr-2025 | Airflow 3.0 | 4.1 |
| 14-may-2025 | Databricks–Neon; Lakebase (11-jun) | 10.2 |
| sep-2025 | Delta 4.0; Iceberg 1.10 (v3 cerrada); Tobiko–Fivetran | 5.1, 5.2, 4.2 |
| 13-oct-2025 | Anuncio de la fusión Fivetran–dbt Labs; MetricFlow Apache 2.0 (14-oct) | 4.2, 7.5 |
| 26-nov-2025 | AWS: Iceberg v3 (DV y row lineage) | 5.1 |
| 8-dic-2025 | Anuncio IBM–Confluent | 6.1 |
| ene-2026 | OSI v1 (27-ene); Snowflake–Fabric bidireccional GA (30-ene); AWS Sovereign Cloud GA (15-ene) | 7.5, 5.4, 10.5 |
| feb-2026 | Kafka 4.2 (share groups); Polaris TLP (19-feb); DDIA 2ª ed. | 6.4, 5.4, 2 |
| mar-2026 | KIP-1150 aceptado (2-mar); Gluten TLP (5-mar); IBM cierra Confluent (17-mar); SQLMesh a LF (25-mar) | 6.4, 6.1, 4.2 |
| abr-2026 | DuckLake 1.0 (13-abr); Next '26 (22-abr); MinIO CE archivado (25-abr) | 5.3, 10.2, 10.3 |
| may-jun-2026 | Snowflake Iceberg v3 GA (7-may); Fivetran–dbt cierre (1-jun); dbt Core v2 alpha (1-jun); Airflow 3.3; Flink 2.3 (25-jun) | 5.1, 4.2, 6.1 |
| jul-ago-2026 | Prefect–Dagster anunciado (13-jul); Spark 4.2 (14-jul); Ossie (10-jul); Comet 1.0 (7-ago); DuckLabs–AWS (26-ago) | 4.1, 6.1, 7.5, 5.6 |
| sep-oct-2026 | Debezium 3.7 (29-sep); Iceberg 1.12 (30-sep); Delta 4.4.1 (5-oct); ODCS v3.2.0 (8-sep) | 4.3, 5.1, 5.2, 8.1 |

### 15.2 IA en data engineering: text-to-SQL, agentes, AI-ready data

| Benchmark | Resultado (oct-2026) | Salvedad | Fuente |
|---|---|---|---|
| Spider 2.0 original (nov-2024) | 21,3 % (mejor modelo de razonamiento de entonces con agente de código) frente a 91,2 % en Spider 1.0 y 73,0 % en BIRD; 632 tareas | Referencia histórica | [arXiv 2411.07763](https://arxiv.org/abs/2411.07763) |
| Spider 2.0-Snow | 96,70 (Genloop Sentinel Agent v2 Pro) | Autoinformado; esquemas empresariales | [Spider 2.0](https://spider2-sql.github.io/) |
| Spider 2.0-Lite | 76,23 (Tianqiong Data Agent) | | [Spider 2.0](https://spider2-sql.github.io/) |
| Spider 2.0-DBT | 65,6 máx. (SignalPilot); siguientes ≈39,7-60,29 | 68 tareas añadidas el 22-may-2025; etiquetar uso de tablas oráculo | [Spider 2.0](https://spider2-sql.github.io/) |
| BIRD | test 82,95 % (GrainSQL, 7-sep-2026, con conocimiento oráculo); dev 78,10 %; mejor single-model 80,04 %; humanos 92,96 % | | [BIRD](https://bird-bench.github.io/) |
| Snowflake Cortex Analyst | 90 %+ frente a 51 % de un modelo general con un solo prompt | Benchmark interno de 150 preguntas, tablas anchas pre-unidas | [Snowflake](https://www.snowflake.com/en/blog/engineering/cortex-analyst-text-to-sql-accuracy-bi/) |

**[Inferencia]** Un agente SQL de 90 %+ en un benchmark limpio no justifica autonomía sobre datos reales; Spider2-DBT (≤65,6 %) y Lite (≤76 %) sugieren que tareas de transformación y esquemas reales siguen fallando 25-35 % o más. Se requiere capa semántica, evaluación propia con gold queries, sandbox de solo lectura, límites de bytes y revisión humana en escrituras. Los leaderboards son autoinformados, con sistemas multi-agente y self-consistency costosos. Gartner (feb-2025) **predice** que hasta 2026 las organizaciones abandonarán el 60 % de proyectos de IA sin datos AI-ready (encuesta de 1.203 líderes, jul-2024; predicción, no hecho medido) ([Gartner](https://www.gartner.com/en/newsroom/press-releases/2025-02-26-lack-of-ai-ready-data-puts-ai-projects-at-risk), fetch directo 403). Radar vol. 34 pone "MCP by default" en Caution (agentes con permisos amplios y prompt injection; zero trust y mínimo privilegio).

**Vectores y no estructurados.** Benchmark de Timescale (proveedor; 50 M de vectores de 768 dimensiones, sin filtros, a 99 % de recall): Postgres+pgvector+pgvectorscale 471,57 QPS frente a Qdrant 41,47 QPS; Qdrant tiene menor latencia p99 (38,71 vs 74,60 ms); otra fuente discrepa en dimensiones ([Instaclustr](https://www.instaclustr.com/education/vector-database/pgvector-vs-qdrant-5-key-differences-and-how-to-choose/), [Tiger Data](https://dev.to/tigerdata/postgresql-vs-qdrant-for-vector-search-50m-embedding-benchmark-3hhe)). PostgreSQL lidera Stack Overflow 2025 por tercer año (47 % quiere usarlo, 66 % lo admira) ([Stack Overflow](https://stackoverflow.co/company/press/archive/stack-overflow-2025-developer-survey/)). **[Inferencia]** pgvector es el punto de partida razonable para <~50 M vectores si ya se opera Postgres; las bases vectoriales dedicadas se justifican por latencia y filtrado. Chunking, embeddings y evaluación RAG: sin fuentes primarias.

### 15.3 Rol del data engineer y encuestas

Reis 2026 (publicado 10-feb-2026; muestra autoseleccionada, sin ponderación): 82 % usa IA a diario o más; 64 % de organizaciones aún experimenta o la usa tácticamente; 42 % espera crecer el equipo frente a 7 % que espera reducirlo ([Reis](https://joereis.substack.com/p/the-2026-state-of-data-engineering)). Pulse (n=194): optimismo de carrera 71 %; el asistente de Anthropic 49 %, Copilot 16 %, ChatGPT 15 %, Cursor 7 %; 57 % dice escribir código mucho más rápido; narrativa "1 = 10" ([Reis pulse](https://joereis.substack.com/p/ai-is-here-but-the-hard-parts-havent)). Stack Overflow 2025: 84 % usa o planea usar IA (76 % en 2024), 46 % desconfía de la precisión frente a 33 % que confía, 31 % usa agentes ([Stack Overflow](https://survey.stackoverflow.co/2025/ai)). Radar de nov-2025: "Standalone data engineering teams" en Hold ([rmoff](https://rmoff.net/2025/11/05/tech-radar-nov-2025-data-blips)). **[Inferencia]** El rol se desplaza de escribir pipelines a plataforma, contratos, calidad, coste y contexto para agentes; el patrón repetido (Reis: ownership y requisitos; MAD: gobernanza; dbt: confianza; incidentes: validación en fronteras) apunta a proceso y propiedad como factor limitante. No hay datos de empleo ni salarios (Dice/LinkedIn).

## 16. Temas con poca literatura consolidada o en evolución rápida

| Tema | Por qué es frágil | Qué falta | Recomendación |
|---|---|---|---|
| Data mesh | Evidencia cualitativa; sin tasas de éxito | Postmortems con nombre, encuestas primarias, Gartner | Pilotos de dos dominios |
| Medallion | Cero estudios empíricos de coste/latencia | Medición por capa | Tratarlo como convención |
| Data fabric / reverse ETL | Definición difusa / fuentes con conflicto de interés | Estudios independientes | Decidir por caso |
| Contratos de datos | Estándar en movimiento (ODCS 3.2.0); adopción solo patrocinada | Encuesta independiente; resultados de PayPal/GoCardless/Netflix | Pinear versión; empezar con 5-10 interfaces |
| Iceberg v3/v4, Delta catalog-managed, catálogos REST | GA desigual; v4 en desarrollo | Matriz oficial Spark/Flink; Lake Formation/Horizon en detalle | Inventariar lectores antes de subir de versión |
| Capas semánticas (OSI/Ossie) | Incubación; sin versión fijada en ROADMAP | Interoperabilidad end-to-end | No apostar a un solo formato |
| Streaming lakehouse, diskless Kafka | KIP-1150 sin implementación mainline; latencias no verificadas | Benchmarks independientes | Esperar sub-KIPs o usar fork/servicio con validación propia |
| Vortex, Lance, DuckLake | Claims de proveedor | Benchmarks independientes | Parquet por defecto |
| Spark RTM con estado, Comet vs Gluten vs Photon | 4.3 sin publicar; sin comparativas independientes | Benchmarks | Medir con carga propia |
| Text-to-SQL y agentes | Leaderboards autoinformados | Coste por consulta, evaluación en producción | Gold queries propias y sandbox |
| RAG, vector data, feature stores | Sin fuentes primarias | Chunking, embeddings, evaluación | Las mismas exigencias de idempotencia, lineage y borrado (los índices vectoriales entran en la propagación GDPR) [Práctica consolidada] |
| FinOps de datos y de cargas agénticas | Casos autoinformados | Estudios independientes con USD | Guardarraíles por defecto |
| On-prem, Hadoop legado, K8s data platforms | Un solo caso con cifras (Indeed, patrocinado por AWS) | TCO neutral | POC; evitar MinIO CE en instalaciones nuevas |
| Soberanía y regulación | Fechas móviles (AI Act, Omnibus GDPR); DPF bajo recurso | Estado de C-703/25 P; Joint Opinion 2/2026 | Revisar con DPO cada trimestre |

## 17. Qué cambió respecto a la primera versión

| # | Afirmación de la primera versión | Corrección de la segunda pasada | Fuente |
|---|---|---|---|
| 1 | Una fuente apuntaba a un "Delta 5.0" similar a Iceberg v4 (sin corroborar) | **Delta 5.0 no existe**; la última es 4.4.1 (5-oct-2026) | [GitHub](https://github.com/delta-io/delta/releases), [delta.io](https://delta.io/blog/) |
| 2 | DuckDB Labs se une a AWS (descartado como resumen poco fiable) | **Confirmado** en duckdb.org (26-ago-2026); entidad "DuckLabs B.V."; MIT y DuckDB Foundation | [duckdb.org](https://duckdb.org/2026/08/26/ducklabs-to-join-aws) |
| 3 | Iceberg v3 con GA "discrepante" | Spec adoptada (cerrada ~sep-2025); GA por motor: Snowflake GA (7-may-2026); AWS DV + row lineage (nov-2025), Athena no; Databricks y BigQuery en preview; Trino experimental; v4 en desarrollo | 5.1 |
| 4 | ODCS v3.2 "solo un RFC" | **v3.2.0 publicada** (tag 8-sep; año inferido) | [releases](https://github.com/bitol-io/open-data-contract-standard/releases) |
| 5 | Soda con núcleo OSS (implícito Apache) | **Elastic License 2.0** (source-available, no OSI); v4 = contratos | [blog](https://soda.io/blog/soda-core-license-update-moving-to-elastic-license) |
| 6 | MetricFlow Apache 2.0 desde dic-2025, listado BSL en FAQ | Apache 2.0 desde **14-oct-2025**; el FAQ actual lo lista como Apache 2.0 | [dbt blog](https://www.getdbt.com/blog/open-source-metricflow-governed-metrics), [FAQ](https://www.getdbt.com/licenses-faq) |
| 7 | Fusion bajo ELv2; licencias repartidas entre ELv2, propietaria y BSL | Runtime Apache 2.0 en `dbt-core` v2 (alpha); binario completo bajo acuerdo propietario; ELv2 reemplazada | [dbt](https://docs.getdbt.com/blog/dbt-core-v2-is-here) |
| 8 | Debezium "3.6 y 3.7 alpha" (agregadores) | **3.7.0.Final (29-sep-2026)** | [Debezium](https://debezium.io/releases/) |
| 9 | Fusión Fivetran–dbt Labs: cierre a verificar | Cierre el 1-jun-2026 según el comunicado; empresas privadas, sin SEC | 4.2 |
| 10 | IBM–Confluent: cierre de fuente única | **Cerrada el 17-mar-2026** según nota de IBM; marca y licencia OSS sin pronunciamiento | [IBM](https://newsroom.ibm.com/2026-03-17-ibm-completes-acquisition-of-confluent,-making-real-time-data-the-engine-of-enterprise-ai-and-agents) |
| 11 | Prefect–Dagster "los fundadores pasan a asesores" | Schrock **deja el proyecto y la empresa**; ~40 empleados a Prefect; **cierre no confirmado** | [Dagster](https://dagster.io/blog/prefect-is-acquiring-dagster) |
| 12 | AI Act Omnibus: acuerdo provisional, publicación sin confirmar | **Reglamento (UE) 2026/1744**, DOUE 24-jul-2026; la parte GDPR/datos **no acordada** | [Reg. 2026/1744](https://publications.europa.eu/resource/celex/32026R1744) |
| 13 | Data Act: "cargos de egress por cambio... eliminarse" | Precisado: Art. 29, cargos de cambio prohibidos desde 12-ene-2027; no es una prohibición general de egress (Art. 34: uso paralelo a coste) | [Reg. 2023/2854](https://publications.europa.eu/resource/celex/32023R2854) |
| 14 | Data mesh: adopción 8-12 % | **No verificada**; el abstract citado no da porcentajes; el 18 % de Gartner es secundario | [arXiv](https://arxiv.org/abs/2606.08266) |
| 15 | Build-vs-buy de observabilidad en torno a ~20 ingenieros | **Descartada**: solo una opinión de Medium sin metodología | 8.3 |
| 16 | "0,25-1,0 FTE" de coste oculto de catálogo OSS | Sin respaldo; no verificado | 8.3 |
| 17 | MinIO/Ceph: licencias a verificar | MinIO CE **archivado el 25-abr-2026**, sin mantenimiento; AIStor Free con licencia comercial | [GitHub](https://github.com/minio/minio) |
| 18 | Synapse en EOL (blogs) | Estado "In Support" sin fecha de retiro oficial; solo retiros parciales | [Lifecycle](https://learn.microsoft.com/en-us/lifecycle/products/azure-synapse-analytics) |
| 19 | Spark RTM "~5 ms"; "verificar si 4.2 o 4.3 ya cubren RTM con estado" | OSS: RTM solo stateless en 4.1; stateful previsto para 4.3; 4.2.0 (14-jul-2026) solo añade el trigger para PySpark | [Spark](https://spark.apache.org/releases/spark-release-4-2-0.html) |
| 20 | Flink/Kafka versiones sin verificar | Flink 2.3.0 (25-jun-2026), Kafka 4.3.x, Spark 4.2.0, Comet 1.0.0, Trino 483 | 6.1 |
| 21 | CJEU SRB y EDPB 28/2024 vía resúmenes | Leídos en texto original; añadidos EDPB 02/2026 (anonimización) y CEF 2025 (supresión y backups) | 9.1, 9.3 |
| 22 | Precios por plataforma sin base | Verificados solo Snowflake (tabla oficial), Redshift, ClickHouse, MotherDuck, S3/Glue; BigQuery, Fabric y Databricks siguen sin tarifa verificada | 5.6 |
| 23 | OSI v0.1 | Spec v1 publicada el 27-ene-2026; renombrada Apache Ossie (incubación) | 7.5 |
| 24 | Neon ~1.000 M USD; Crunchy ~250 M USD | Neon: cifra no figura en la nota oficial; Crunchy: solo TechCrunch anónimo | 10.2 |
| 25 | Tecton "no verificado" | Compra acordada (ago-2025); precio ~900 M USD solo en un agregador | 12.2 |
| 26 | Incidentes y patrones citados genéricamente | Añadidos post-mortems primarios (GitLab, Cloudflare x2, Datadog, Honeycomb, Mixmax) | 12.1 |

## 18. Confianza y lo no verificado

| Afirmación | Estado | Motivo |
|---|---|---|
| Cierre de Prefect–Dagster | **No confirmado** | Solo anuncio del 13-jul-2026; FAQ dice "próximas semanas"; banner incoherente |
| Cierre Fivetran–dbt Labs (1-jun-2026) | Confirmado por comunicado de parte; sin registro regulatorio | Empresas privadas |
| Cierre IBM–Confluent (17-mar-2026) | Confirmado por nota de IBM; sin 8-K | Primaria corporativa |
| DuckLabs–AWS | Confirmado en duckdb.org | Cierre esperado a principios de sept-2026; cierre efectivo no verificado |
| Años de fechas de GitHub Releases (Delta, Iceberg 1.11/1.12, Dagster, GX, ODCS) | **Inferidos 2026** | La página no muestra año |
| Tarifas de BigQuery, Fabric y Databricks (DBU), y Snowflake fuera de la tabla oficial | **No verificado** | Páginas dinámicas; snippets discrepantes |
| Precio S3 Standard | **No verificado en esta pasada** | No recuperado |
| Cifras de adopción de data mesh (8-12 %, 18 %) | **No verificado** / secundaria | Ver 3.4 |
| Gartner Hype Cycle de data mesh 2022 | Secundaria | Informe de pago |
| Regla "~20 ingenieros", "0,25-1,0 FTE", "5-15 % tiempo real" | **Descartadas / no verificadas** | Opinión sin metodología |
| Umbrales de equipo (1-5, 5-30) y marcos de decisión | **[Inferencia]** | Criterios del análisis |
| 61 % de uso de contratos (BARC/Actian) | Patrocinada, metodología no divulgada | n>300 |
| Benchmarks: Flink 2.0 (-94 %, 49x), Photon (3x), Vortex/Lance (100x), RisingWave (22/27), Timescale vs Qdrant, Snowflake Cortex (90 %), StarRocks (6,9x) | Del proveedor o de los autores | Sin validación independiente |
| Spider 2.0 / BIRD | Autoinformados | Usos de oráculo no verificados |
| Estados GA/preview de Summit/Next/Build 2026; Lakehouse//RT, Mooncake, CoWork/CoCo | Anunciado; GA solo donde la nota oficial lo dice | Recaps de terceros |
| Licencia de OpenMetadata ingestion; Cube Core; Kestra; Lakekeeper versión | Contradictoria / no verificada | Repo vs PyPI |
| Estado de Dagster+ pricing por materialización; Prefect "más liviano" | Fuente secundaria única | Pasada 1 |
| Estado final de EDPB Guidelines 01/2025; casación C-703/25 P; Joint Opinion 2/2026 | Sin versión final / pendiente / no leída | |
| PCI DSS v4.0.1 numeración de requisitos; SOC 2 CC6-CC8; guía HHS | No leídos | 403 / cuenta AICPA |
| Spark Connect/Declarative Pipelines más allá de lo listado; ORC, Avro, Arrow, Nimble | No verificado | |
| Matriz oficial Spark/Flink para Iceberg v3; Lake Formation y Horizon en detalle | No verificado | Páginas truncadas |
| Disponibilidad de la región AWS Chile (fines de 2026) | No confirmada | |

## 19. Resumen ejecutivo

1. **Las arquitecturas son ejes, no rivales.** Combine un modo de procesamiento, un almacenamiento y un layout, y fije la latencia por consumidor. Nadie reporta Kappa puro: el patrón dominante es un código con dos ejecuciones; Lambda sobrevive donde el backfill y la reconciliación son críticos.
2. **El catálogo es el nuevo punto de control.** Iceberg v3 está adoptada con GA desigual (Snowflake GA; AWS parcial; Databricks y BigQuery en preview; Athena sin soporte), v4 sigue en desarrollo, Delta llega a 4.4.1 (sin "Delta 5.0") y ambos convergen hacia catálogos que coordinan commits. Diseñe con formatos abiertos y plan de salida del catálogo.
3. **El riesgo dominante es organizativo.** Ownership, requisitos aguas arriba y contratos explican más fallos que el motor; empiece por 5-10 interfaces críticas con contrato ejecutable en CI y fije ODCS por tag.
4. **Data mesh solo con plataforma madura y escala organizativa.** La evidencia es cualitativa y la cifra de adopción circulante no está verificada.
5. **El mercado se reempaqueta.** Fivetran+dbt Labs (cerrada), IBM+Confluent (cerrada), DuckLabs en AWS (confirmado) y Prefect+Dagster (cierre sin confirmar): minimice la exposición con SQL portable, formatos abiertos y licencias revisadas (Soda pasó a ELv2; MinIO CE está archivado).
6. **Las plataformas convergen** en Iceberg, Postgres integrado y agentes; elija por perfil de equipo, ecosistema, gobierno y coste real con POC, no por keynotes. Las tarifas de BigQuery, Fabric y Databricks de este informe **no están verificadas**.
7. **Calidad por capas:** contratos, tests deterministas, WAP en tablas críticas, observabilidad con OpenLineage y SLOs por data product. Construir o comprar se decide por fuentes, equipos y coste de incidentes, no por tamaño de plantilla.
8. **Cumplimiento por diseño:** un HMAC o un token no es anonimización; el borrado en un lakehouse exige DELETE, PURGE, expiración de snapshots y reaplicación del ledger tras restores; los reguladores aceptan backups "beyond use" con procedimientos. Calendario UE: Data Act (cargos de cambio prohibidos desde 12-ene-2027, no un fin general del egress), AI Act con Anexo III a 2-dic-2027 y Anexo I a 2-ago-2028 (Reg. 2026/1744), Omnibus GDPR sin acordar, DPF válido pero bajo recurso.
9. **Coste:** lo que más pesa es el mantenimiento del lakehouse, el full refresh, los ficheros pequeños y el egress; instale guardarraíles por defecto (límites de bytes, timeouts, auto-suspend) y use streaming solo donde el retraso cuesta dinero.
10. **Zonas inmaduras:** agentes y text-to-SQL (leaderboards autoinformados), capas de contexto, RAG y datos no estructurados, formatos nuevos (Vortex, Lance), diskless Kafka, FinOps agéntico y on-prem. Decida ahí con pilotos propios, no con literatura.

## 20. Referencias

Las referencias se agrupan por sección; los enlaces inline del cuerpo son la fuente de cada afirmación. Etiqueta: [P] primaria (proyecto, proveedor o texto oficial), [V] proveedor con sesgo, [S] secundaria o de opinión.

**Fundamentos y arquitecturas (2-3)**
- [P] Armbrust et al., Lakehouse, CIDR 2021: https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf
- [P] Armbrust et al., Delta Lake, VLDB 2020: https://www.vldb.org/pvldb/vol13/p3411-armbrust.pdf
- [P] Akidau et al., Dataflow Model, VLDB 2015: https://www.vldb.org/pvldb/vol8/p1792-Akidau.pdf
- [P] Kreps, Questioning the Lambda Architecture: https://www.oreilly.com/radar/questioning-the-lambda-architecture/
- [P] Dehghani: https://martinfowler.com/articles/data-mesh-principles.html ; https://martinfowler.com/articles/data-monolith-to-mesh.html
- [P] Fowler, event-driven: https://martinfowler.com/articles/201701-event-driven.html
- [P] Kleppmann, CAP: https://martin.kleppmann.com/2015/09/17/critique-of-the-cap-theorem.html ; Abadi PACELC: https://cs.umd.edu/~abadi/papers/abadi-pacelc.pdf
- [P] Confluent EOS: https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/ ; Flink 2PC: https://flink.apache.org/2018/02/28/an-overview-of-end-to-end-exactly-once-processing-in-apache-flink-with-apache-kafka-too/ ; Flink guarantees: https://nightlies.apache.org/flink/flink-docs-stable/docs/connectors/datastream/guarantees/
- [P] LinkedIn: https://www.linkedin.com/blog/engineering/data-streaming-processing/unified-streaming-and-batch-pipelines-at-linkedin-reducing-proc ; Uber Kappa+: https://arxiv.org/pdf/2104.00087 ; Uber IngestionNext: https://uber.com/blog/from-batch-to-streaming-accelerating-data-freshness-in-ubers-data-lake/ ; Airbnb Riverbed: https://www.infoq.com/news/2023/10/airbnb-riverbed-introduction ; Shopify: https://shopify.engineering/bfcm-live-map-2021-apache-flink-redesign
- [P] TiDB HTAP: https://www.cs.purdue.edu/homes/csjgwang/CloudNativeDB/TiDBVLDB20.pdf ; AWS zero-ETL: https://aws.amazon.com/what-is/zero-etl/
- [P/S] Thoughtworks Radar data mesh: https://www.thoughtworks.com/radar/techniques/data-mesh ; lakehouse: https://www.thoughtworks.com/radar/techniques/lakehouse-architecture ; vol. 34: https://www.thoughtworks.com/radar
- [S] Data mesh: https://atlan.com/gartner-data-mesh ; https://www.starburst.io/blog/data-mesh-what-happened/ ; https://arxiv.org/abs/2302.01713 ; https://arxiv.org/abs/2606.08266 ; https://datamesh-architecture.com/real-world-learnings ; Zalando: https://aws.amazon.com/blogs/big-data/how-zalando-innovates-their-fast-serving-layer-by-migrating-to-amazon-redshift
- [V/S] Medallion: https://www.databricks.com/glossary/medallion-architecture ; https://dataengineeringcentral.substack.com/p/medallion-architecture-truth-or-fiction ; Tableflow: https://docs.confluent.io/cloud/current/topics/tableflow/overview.html ; Fresha: https://current.confluent.io/post-conference-videos-26/lambda-architecture-in-2025-kafka-views-and-the-evolving-data-platform-ldn26

**Pipelines y orquestación (4)**
- [P] Airflow: https://airflow.apache.org/docs/apache-airflow/stable/release_notes.html ; https://airflow.apache.org/blog/airflow-three-point-oh-is-here/ ; https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html ; MWAA: https://docs.aws.amazon.com/mwaa/latest/userguide/airflow-versions.html ; Composer: https://docs.cloud.google.com/composer/docs/composer-versions
- [P] Dagster: https://github.com/dagster-io/dagster/releases ; https://dagster.io/blog/prefect-is-acquiring-dagster ; https://dagster.io/dagster-customer-faq ; Prefect: https://docs.prefect.io/v3/concepts/assets ; https://docs.prefect.io/v3/concepts/deployments
- [P] Argo: https://argo-workflows.readthedocs.io/en/latest/ ; Temporal: https://docs.temporal.io/evaluate/why-temporal ; Kestra: https://kestra.io/docs
- [P] Fivetran–Tobiko: https://www.businesswire.com/news/home/20250903275106/en/Fivetran-Acquires-Tobiko-Data-to-Power-the-Next-Generation-of-Advanced-AI-Ready-Data-Transformation ; Fivetran–dbt: https://www.fivetran.com/press/fivetran-dbt-labs-complete-merger-to-create-the-data-infrastructure-for-trusted-ai-agents ; SQLMesh LF: https://www.linuxfoundation.org/press/linux-foundation-welcomes-sqlmesh-project
- [P] dbt: https://docs.getdbt.com/blog/dbt-core-v2-is-here ; https://www.getdbt.com/licenses-faq ; https://docs.getdbt.com/docs/build/incremental-strategy ; https://docs.getdbt.com/docs/build/incremental-microbatch ; https://docs.getdbt.com/docs/build/snapshots ; https://docs.getdbt.com/best-practices/best-practice-workflows ; https://docs.getdbt.com/docs/build/unit-tests ; SQLMesh: https://sqlmesh.readthedocs.io/en/stable/concepts/plans/ ; https://sqlmesh.readthedocs.io/en/stable/concepts/models/model_kinds/
- [P] Debezium: https://debezium.io/releases/ ; https://debezium.io/blog/2026/09/29/debezium-3-7-final-released/ ; https://debezium.io/documentation/reference/stable/connectors/postgresql.html ; dlt: https://pypi.org/project/dlt/ ; Flink CDC: https://nightlies.apache.org/flink/flink-cdc-docs-stable/ ; Lakeflow Connect: https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/ ; Openflow: https://docs.snowflake.com/en/user-guide/data-integration/openflow/connectors/about-openflow-connectors ; DBLog: https://www.arxiv.org/pdf/2010.12597

**Almacenamiento (5)**
- [P] Iceberg: https://iceberg.apache.org/spec/ ; https://raw.githubusercontent.com/apache/iceberg/main/format/spec.md ; https://github.com/apache/iceberg/releases ; https://raw.githubusercontent.com/apache/iceberg/main/docs/docs/maintenance.md ; https://raw.githubusercontent.com/apache/iceberg/main/docs/docs/spark-procedures.md ; https://raw.githubusercontent.com/apache/iceberg/main/docs/docs/evolution.md ; REST: https://github.com/apache/iceberg/blob/main/open-api/rest-catalog-open-api.yaml
- [P] v3 por proveedor: https://docs.snowflake.com/en/release-notes/2026/other/2026-05-07-iceberg-v3-ga ; https://aws.amazon.com/about-aws/whats-new/2025/11/aws-apache-iceberg-v3-deletion-vectors-row-lineage ; https://docs.databricks.com/aws/en/iceberg/iceberg-v3 ; https://docs.cloud.google.com/lakehouse/docs/release-notes ; https://trino.io/docs/current/connector/iceberg.html
- [P] Delta: https://github.com/delta-io/delta/releases ; https://delta.io/blog/ ; https://raw.githubusercontent.com/delta-io/delta/master/PROTOCOL.md ; https://docs.delta.io/latest/delta-uniform.html ; https://docs.databricks.com/aws/en/delta/clustering ; https://github.com/unitycatalog/unitycatalog/releases
- [P] Hudi: https://hudi.apache.org/blog/2024/12/16/announcing-hudi-1-0-0 ; https://hudi.apache.org/releases/release-1.2 ; Paimon: https://paimon.apache.org/docs/master/ ; DuckLake: https://ducklake.select/ ; https://duckdb.org/news/ ; https://duckdb.org/2026/08/26/ducklabs-to-join-aws ; XTable: https://xtable.apache.org/
- [P/S] LHBench: https://vldb.org/cidrdb/2023/analyzing-and-comparing-lakehouse-storage-systems.html ; https://lhbench.cs.berkeley.edu/
- [P] Catálogos: https://polaris.apache.org/blog/2026/02/19/apache-polaris-graduates-to-top-level-project/ ; https://docs.snowflake.com/en/user-guide/opencatalog/overview ; https://github.com/lakekeeper/lakekeeper ; https://projectnessie.org/ ; https://gravitino.apache.org/ ; https://docs.cloud.google.com/bigquery/docs/iceberg-tables ; https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables-maintenance-overview.html
- [P] Parquet: https://parquet.apache.org/blog/ ; Lance: https://lance.org/ ; Vortex: https://vortex.dev/
- [P] Precios: https://www.snowflake.com/legal-files/CreditConsumptionTable.pdf ; https://aws.amazon.com/redshift/pricing/ ; https://clickhouse.com/pricing ; https://motherduck.com/product/pricing/ ; https://aws.amazon.com/s3/pricing/ ; https://aws.amazon.com/glue/pricing/ ; https://azure.microsoft.com/en-us/pricing/details/microsoft-fabric/
- [P] S3 conditional writes: https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html ; Pinot: https://pinot.apache.org/

**Procesamiento (6)**
- [P] https://spark.apache.org/news/index.html ; https://spark.apache.org/releases/spark-release-4-2-0.html ; https://spark.apache.org/docs/latest/sql-performance-tuning.html ; https://flink.apache.org/downloads/ ; https://flink.apache.org/2025/03/24/apache-flink-2.0.0-a-new-era-of-real-time-data-processing/ ; https://nightlies.apache.org/flink/flink-docs-release-2.3/release-notes/flink-2.3/ ; https://www.vldb.org/pvldb/vol18/p4846-mei.pdf ; https://kafka.apache.org/blog/2026/02/17/apache-kafka-4.2.0-release-announcement/ ; https://kafka.apache.org/blog/2026/05/22/apache-kafka-4.3.0-release-announcement/ ; https://trino.io/docs/current/release.html ; https://trino.io/docs/current/admin/fault-tolerant-execution.html ; https://datafusion.apache.org/blog/2026/08/07/datafusion-comet-1.0.0 ; https://newsroom.ibm.com/2026-03-17-ibm-completes-acquisition-of-confluent,-making-real-time-data-the-engine-of-enterprise-ai-and-agents ; https://jepsen.io/analyses/redpanda-21.10.1 ; https://cwiki.apache.org/confluence/display/KAFKA/KIP-405%3A+Kafka+Tiered+Storage
- [V/S] https://aiven.io/blog/kip-1150-accepted-and-the-road-ahead ; https://jack-vanlightly.com/blog/2023/5/15/kafka-vs-redpanda-performance-do-the-claims-add-up ; https://www.anyscale.com/blog/ray-data-daft-benchmarking-multimodal-ai-workloads ; https://www.databricks.com/wp-content/uploads/2022/07/Photon-A-Fast-Query-Engine-for-Lakehouse-Systems.pdf

**Modelado y semántica (7)**
- [P] Kimball: https://www.kimballgroup.com/techniques/dimensional-modeling-techniques/ ; https://www.kimballgroup.com/2013/02/design-tip-152-slowly-changing-dimension-types-0-4-5-6-7/ ; https://decisionworks.com/2004/03/differences-of-opinion/
- [P] Docs de plataforma: https://docs.cloud.google.com/bigquery/docs/nested-repeated ; https://docs.snowflake.com/en/user-guide/semistructured-considerations ; https://docs.snowflake.com/en/sql-reference/constraints-overview ; https://docs.databricks.com/aws/en/tables/constraints ; https://docs.delta.io/latest/delta-change-data-feed.html ; https://docs.getdbt.com/docs/mesh/govern/model-contracts
- [V/S] OBT: https://fivetran.com/blog/obt-star-schema ; https://interworks.com/blog/2024/03/12/comparing-query-performance-of-star-schemas-vs-flat-tables/ ; Data Vault: https://en.wikipedia.org/wiki/Data_vault_modeling ; https://datavaultalliance.com/
- [P/V] Semántica: https://www.getdbt.com/blog/open-source-metricflow-governed-metrics ; https://github.com/dbt-labs/metricflow ; https://www.snowflake.com/en/blog/open-semantic-interchanges-specs-finalized/ ; https://ossie.apache.org/updates/ossie-enters-apache-incubator/ ; https://github.com/apache/ossie/blob/main/ROADMAP.md ; https://docs.snowflake.com/en/user-guide/views-semantic/overview ; https://www.databricks.com/blog/redefining-semantics-data-layer-future-bi-and-ai ; https://docs.cube.dev/docs/introduction ; https://docs.getdbt.com/blog/semantic-layer-vs-text-to-sql-2026

**Calidad, observabilidad y gobernanza (8)**
- [P] https://github.com/great-expectations/great_expectations/releases ; https://pypi.org/project/soda-core/ ; https://soda.io/blog/soda-core-license-update-moving-to-elastic-license ; https://github.com/sodadata/soda-core/blob/main/LICENSE ; https://pypi.org/project/elementary-data/ ; https://github.com/awslabs/deequ ; https://pandera.readthedocs.io/en/stable/ ; https://pypi.org/project/acryl-datahub/ ; https://github.com/open-metadata/OpenMetadata/releases ; https://github.com/OpenLineage/OpenLineage/releases ; https://github.com/bitol-io/open-data-contract-standard/releases ; https://bitol.io/ ; https://github.com/datacontract/datacontract-specification ; https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html
- [P] Gobernanza: https://datagovernance.com/the-dgi-data-governance-framework/ ; https://dama.org/learning-resources/dama-data-management-body-of-knowledge-dmbok/ ; https://learn.microsoft.com/en-us/purview/purview ; https://docs.cloud.google.com/dataplex/docs/introduction ; https://docs.databricks.com/aws/en/data-governance/unity-catalog/ ; https://docs.snowflake.com/en/user-guide/data-quality-intro ; https://docs.aws.amazon.com/lake-formation/latest/dg/what-is-lake-formation.html ; https://focus.finops.org/ ; https://docs.snowflake.com/en/user-guide/cost-attributing ; https://docs.databricks.com/aws/en/admin/system-tables/billing
- [V/S] https://www.actian.com/blog/data-intelligence/barc-x-actian-research-data-products-enter-the-enterprise-roll-out-phase/ ; https://montecarlo.ai/pricing ; https://techcrunch.com/2025/04/23/datadog-acquires-ai-powered-observability-startup-metaplane ; https://costbench.com/stats/data-catalog-pricing-2026/ ; https://aaltodoc.aalto.fi/items/9643d2ad-40ad-4cdb-a12d-792695ec30c1

**Seguridad y compliance (9)**
- [P] GDPR: https://publications.europa.eu/resource/celex/32016R0679 ; SRB: https://publications.europa.eu/resource/celex/62023CJ0413 ; https://curia.europa.eu/site/upload/docs/application/pdf/2025-09/cp250107en.pdf ; WP216: https://ec.europa.eu/justice/article-29/documentation/opinion-recommendation/files/2014/wp216_en.pdf ; EDPB 01/2025: https://www.edpb.europa.eu/system/files/2025-01/edpb_guidelines_202501_pseudonymisation_en.pdf ; EDPB 02/2026: https://www.edpb.europa.eu/system/files/2026-07/edpb_guidelines_202602_anonymisation_v1_en_0.pdf ; EDPB 28/2024: https://www.edpb.europa.eu/system/files/2024-12/edpb_opinion_202428_ai-models_en.pdf ; EDPB CEF 2025: https://www.edpb.europa.eu/system/files/2026-02/edpb_cef-report_2025_right-to-erasure_en.pdf ; ICO: https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/individual-rights/right-to-erasure/
- [P] DPF: https://publications.europa.eu/resource/celex/32023D1795 ; https://curia.europa.eu/jcms/upload/docs/application/pdf/2025-09/cp250106en.pdf ; Data Act: https://publications.europa.eu/resource/celex/32023R2854 ; AI Act: https://publications.europa.eu/resource/celex/32024R1689 ; Omnibus IA: https://publications.europa.eu/resource/celex/32026R1744 ; DORA: https://publications.europa.eu/resource/celex/32022R2554 ; NIS2: https://publications.europa.eu/resource/celex/32022L2555 ; CRA: https://publications.europa.eu/resource/celex/32024R2847
- [P] CCPA: https://cppa.ca.gov/pdf/20260101_ccpa_statute.pdf ; LGPD: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm ; Ley 25.326: https://servicios.infoleg.gob.ar/infolegInternet/anexos/60000-64999/64790/texact.htm ; HIPAA: https://www.ecfr.gov/api/renderer/v1/content/enhanced/current/title-45?part=164&section=164.514 ; PCI: https://listings.pcisecuritystandards.org/documents/Tokenization_Guidelines_Info_Supplement.pdf ; ISO 27701: https://www.iso.org/standard/27701
- [P] Controles: https://docs.aws.amazon.com/kms/latest/developerguide/kms-cryptography.html ; https://docs.aws.amazon.com/kms/latest/developerguide/keystore-external.html ; https://developer.hashicorp.com/vault/docs/secrets/databases ; https://docs.github.com/en/actions/concepts/security/openid-connect ; https://csrc.nist.gov/pubs/sp/800/188/final ; https://csrc.nist.gov/pubs/sp/800/226/final ; https://csrc.nist.gov/pubs/sp/800/207/final ; https://slsa.dev/spec/v1.0/about ; Databricks GDPR: https://docs.databricks.com/aws/en/security/privacy/gdpr-delta
- [P] RLS/masking: https://docs.snowflake.com/en/user-guide/security-column-intro ; https://docs.snowflake.com/en/user-guide/security-row-intro ; https://docs.cloud.google.com/bigquery/docs/column-data-masking-intro ; https://docs.cloud.google.com/bigquery/docs/row-level-security-intro ; https://docs.databricks.com/aws/en/data-governance/unity-catalog/filters-and-masks/ ; https://docs.aws.amazon.com/redshift/latest/dg/t_ddm.html ; https://learn.microsoft.com/en-us/fabric/data-warehouse/dynamic-data-masking ; https://learn.microsoft.com/en-us/fabric/onelake/security/get-started-security
- [S] https://acompli.ie/news/digital-omnibus-gdpr-cookies-status-september-2026/ ; https://www.wilmerhale.com/en/insights/blogs/wilmerhale-privacy-and-cybersecurity-law/20251201-european-court-of-justice-to-review-challenge-to-eu-us-data-privacy-framework

**Plataformas, soberanía y tendencias (10-15)**
- [P/V] https://www.databricks.com/product/pricing ; https://www.snowflake.com/en/pricing-options/ ; https://cloud.google.com/blog/products/data-analytics/unveiling-new-bigquery-capabilities-for-the-agentic-era ; https://azure.microsoft.com/en-us/blog/microsoft-build-2026-building-agentic-apps-with-microsoft-fabric-and-microsoft-databases/ ; https://www.snowflake.com/en/news/press-releases/snowflake-pioneers-new-open-framework-for-interoperable-enterprise-data-and-ai/ ; https://www.databricks.com/company/newsroom/press-releases/databricks-launches-ltap-first-lake-transactionalanalytical ; https://learn.microsoft.com/en-us/lifecycle/products/azure-synapse-analytics ; https://aws.amazon.com/blogs/big-data/aws-analytics-at-reinvent-2025-unifying-data-ai-and-governance-at-scale
- [P] On-prem y soberanía: https://github.com/minio/minio ; https://www.min.io/pricing ; https://docs.ceph.com/en/latest/releases/tentacle/ ; https://ozone.apache.org/ ; https://spark.apache.org/docs/latest/running-on-kubernetes.html ; https://strimzi.io/ ; https://press.aboutamazon.com/aws/2026/1/aws-launches-aws-european-sovereign-cloud-and-announces-expansion-across-europe ; https://cloud.google.com/sovereign-cloud ; https://aws.amazon.com/solutions/case-studies/indeed-s3-tables-case-study/ ; https://www.finops.org/framework/
- [S] https://www.theregister.com/2025/05/09/37signals_cloud_repatriation_storage_savings ; https://www.softwareseni.com/the-european-sovereign-cloud-provider-landscape-in-2026-who-exists-and-what-they-offer/ ; https://itsfoss.com/news/minio-moves-away-from-open-source/
- [P/S] Incidentes: https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/ ; https://blog.cloudflare.com/18-november-2025-outage/ ; https://blog.cloudflare.com/cloudflare-incident-on-november-14-2024-resulting-in-lost-logs/ ; https://www.datadoghq.com/blog/2023-03-08-multiregion-infrastructure-connectivity-issue/ ; https://status.honeycomb.io/incidents/pjzh0mtqw3vt ; https://www.mixmax.com/engineering/make-it-snow-efb88freducing-costs-in-snowflake ; https://discuss.httparchive.org/t/warning-14-000-bigquery-charge-in-2-hours/2715 ; https://microservices.io/patterns/data/transactional-outbox.html ; https://debezium.io/blog/2019/02/19/reliable-microservices-data-exchange-with-the-outbox-pattern/ ; https://docs.cloud.google.com/bigquery/docs/best-practices-costs
- [S] Encuestas y mercado: https://joereis.substack.com/p/the-2026-state-of-data-engineering ; https://joereis.substack.com/p/ai-is-here-but-the-hard-parts-havent ; https://mattturck.com/mad2025/ ; https://survey.stackoverflow.co/2025/ai ; https://www.getdbt.com/resources/state-of-analytics-engineering-2026-download ; https://www.nops.io/blog/state-of-finops-2026/ ; https://spider2-sql.github.io/ ; https://bird-bench.github.io/ ; https://arxiv.org/abs/2411.07763 ; https://www.gartner.com/en/newsroom/press-releases/2025-02-26-lack-of-ai-ready-data-puts-ai-projects-at-risk
- Bibliografía canónica no leída en texto completo: Kleppmann y Riccomini, *Designing Data-Intensive Applications*, 2ª ed. (2026); Reis y Housley, *Fundamentals of Data Engineering* (2022); Kimball y Ross, *The Data Warehouse Toolkit*, 3ª ed.; Linstedt y Olschimke (2015/2016); Akidau, Chernyak y Lax, *Streaming Systems*.
