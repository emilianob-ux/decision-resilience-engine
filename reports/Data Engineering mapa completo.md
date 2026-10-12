# Data Engineering en 2026: mapa que ordena el caos

**Conclusión central:** en octubre de 2026 la ingeniería de datos ha dejado de ser una carrera por herramientas y se ha convertido en una disciplina de fronteras: formatos de tabla abiertos (Iceberg como lingua franca de interoperabilidad), catálogos como nuevo punto de control, contratos y ownership como principal factor de éxito, y un mercado que se reempaqueta por fusiones y adquisiciones. La evidencia disponible indica que los fallos dominantes son organizativos (deuda técnica 25%, falta de dirección 21%, requisitos upstream deficientes 19% en la encuesta de Joe Reis, muestra comunitaria no aleatoria) y de coste operativo, no de motor de cómputo ([Reis 2026](https://joereis.substack.com/p/the-2026-state-of-data-engineering)). Las arquitecturas ya no compiten entre sí, sino que son ejes ortogonales: procesamiento (batch/streaming/Lambda/Kappa), almacenamiento (warehouse/lake/lakehouse), layout (medallion) y organización (mesh). La pregunta práctica pasó de "¿uno o dos pipelines?" a "¿qué SLA de frescura justifica el coste de streaming?". Las plataformas (Databricks, Snowflake, BigQuery, Fabric) convergen en tablas Iceberg, catálogo gobernado, Postgres integrado y agentes de IA. Este informe sigue el encargo (fundamentos a tendencias) y separa en cada tema lo respaldado por fuente de lo que es práctica consolidada; las secciones 15 y 16 listan explícitamente lo volátil y lo no verificado. Fecha de corte: octubre de 2026.

## Índice

1. Convenciones de confianza y alcance
2. Fundamentos y conceptos clave
3. Arquitecturas: batch, streaming, Lambda, Kappa, medallion, lakehouse, mesh, fabric
4. Pipelines, ingesta y orquestación
5. Almacenamiento: warehouses, lakes, lakehouses y formatos
6. Procesamiento batch y streaming
7. Modelado de datos y capa semántica
8. Calidad, observabilidad y gobernanza
9. Seguridad y compliance
10. Plataformas cloud, on-premise, híbrido y soberanía
11. Stack moderno por categoría
12. Patrones avanzados, anti-patrones y errores comunes
13. Mejores prácticas de producción
14. Escalabilidad, coste y mantenimiento
15. Evolución reciente 2023-2026 y temas de poca literatura o evolución rápida
16. Nivel de confianza: lo no verificado
17. Resumen ejecutivo
18. Referencias

## 1. Convenciones de confianza y alcance

Los hallazgos con enlace provienen de páginas leídas por los investigadores; muchos son blogs de proveedores, agregadores o resúmenes de búsqueda. Uso tres etiquetas: **[Fuente]** (respaldado con enlace, a veces con sesgo señalado), **[Práctica consolidada]** (conocimiento general estable, no verificado contra fuentes de 2026; contrastar con *Designing Data-Intensive Applications* de Kleppmann y *Fundamentals of Data Engineering* de Reis y Housley) y **[No verificado]** (afirmación puntual, a menudo una fecha o cifra de fuente única). Los umbrales numéricos de tamaño de equipo o de datos son heurísticas del análisis, no datos medidos.

## 2. Fundamentos y conceptos clave

Esta sección es casi enteramente [Práctica consolidada]; las referencias canónicas son Kleppmann (DDIA), Reis y Housley (FoDE) y el modelo Dataflow de Akidau.

| Concepto | Esencia | Cuándo importa / trampa |
|---|---|---|
| OLTP vs OLAP | OLTP: transacciones cortas, filas, normalizado. OLAP: escaneos agregados, columnar, desnormalizado | HTAP y zero-ETL difuminan la frontera; sigue siendo la decisión base de diseño |
| ETL vs ELT | ELT domina con cómputo y almacenamiento desacoplados (SQL/dbt en el warehouse) | ETL persiste para enmascarar PII antes de cargar, edge y streaming |
| Batch vs streaming | Datos acotados vs no acotados; en streaming importan event time, watermarks, triggers y estado | Streaming también implica backfill y reprocesamiento |
| Idempotencia | Reejecutar produce el mismo estado: MERGE por clave natural, overwrite de partición, claves deterministas | Base de reintentos y backfills seguros |
| Exactly-once | En la práctica "effectively-once": at-least-once más idempotencia o transacciones | Kafka (productor idempotente más transacciones) y Flink (checkpoints más 2PC) lo garantizan dentro de su frontera, no hacia sistemas externos sin sink transaccional o idempotente |
| CDC | Log-based (Debezium; binlog/WAL) vs por consulta o trigger | Reto: snapshot inicial, DDL, orden entre tablas, PII |
| Schema evolution y contratos | Compatibilidad backward/forward/full con schema registry (Avro/Protobuf); Iceberg evoluciona columnas por id | Un contrato es más que un esquema: añade semántica, SLA y owner |
| CAP/PACELC | CAP solo aplica ante partición; PACELC añade latencia vs consistencia en operación normal | S3 es fuertemente consistente desde 2020; los table formats usan commit atómico optimista |
| Particionamiento | Tiempo, hash o rango; evitar sobre-particionar (archivos pequeños) | Iceberg hidden partitioning y Delta liquid clustering reducen el acoplamiento query-layout |

Dos fundamentos tienen respaldo directo. Primero, Kreps argumenta que el log de entrada inmutable (Kafka) es la columna vertebral del reprocesamiento ([Kreps, O'Reilly](https://www.oreilly.com/radar/questioning-the-lambda-architecture/)). Segundo, Dehghani plantea la "gobernanza computacional federada" con estándares globales automatizados como equivalente de contratos entre dominios ([Dehghani](https://martinfowler.com/articles/data-mesh-principles.html)). Sobre contratos, el estándar abierto de referencia es el Open Data Contract Standard (ODCS) de Bitol bajo LF AI & Data, cuya v3.1.0 añade relaciones entre propiedades, validación JSON Schema más estricta y SLAs ejecutables ([Bitol](https://bitol.io/bitol-announces-odcs-v3-1-0-stronger-smarter-and-stricter/)).

## 3. Arquitecturas: ejes distintos, no rivales

### Lambda, Kappa y lakehouse unificado

Kreps (2014) identificó el coste real de Lambda: implementar las mismas transformaciones en un sistema batch y otro de streaming, mantenerlas sincronizadas y operar dos sistemas distribuidos; las capas de abstracción como Summingbird solo exponen la intersección de capacidades ([Kreps](https://www.oreilly.com/radar/questioning-the-lambda-architecture/)). Su Kappa conserva el log (retención igual a la ventana de reprocesamiento), lanza un segundo job desde el inicio al cambiar el código y conmuta al alcanzarlo, con unos 2x de almacenamiento de salida temporal; su evidencia es de LinkedIn con Samza. Kreps aconseja batch si no hay sensibilidad a latencia, streaming si la hay, y no ambos salvo necesidad.

En 2025-26 el debate se desplazó a streaming más table formats abiertos, donde batch y streaming escriben las mismas tablas. Confluent Tableflow materializa topics Kafka como tablas Iceberg o Delta con frescura de unos 5 minutos y publicación a catálogos (Glue, Unity, Polaris, Snowflake Open Catalog); Delta solo con almacenamiento propio, y no está disponible en Confluent Platform ([Confluent docs](https://docs.confluent.io/cloud/current/topics/tableflow/overview.html)). Kai Waehner (comentarista con sesgo de vendor) sostiene que los table formats refuerzan Kappa ([Waehner](https://www.kai-waehner.de/blog/tag/delta-lake/)); como contrapunto, Fresha afirmó en Current London 2026 que "Lambda no está muerto": materializan tablas cada 20 minutos y fusionan eventos CDC en vivo vía vistas, por coste ([Current 2026](https://current.confluent.io/post-conference-videos-26/lambda-architecture-in-2025-kafka-views-and-the-evolving-data-platform-ldn26)). Un blog personal describe el patrón "unificado sobre lakehouse" (Flink más Iceberg) y califica Kappa de "teóricamente simple, prácticamente difícil" ([youngju.dev](https://www.youngju.dev/blog/culture/2026-04-15-streaming-vs-batch-redefined-complete-guide-flink-risingwave-materialize-cdc-streaming-sql-deep-dive-guide-2025.en)).

Mi lectura: el lakehouse unificado ofrece una sola capa de almacenamiento con ACID y upserts, pero con latencia de minutos, no sub-segundo; para sub-segundo hace falta Kafka/Flink o un OLAP en tiempo real delante. No existen benchmarks independientes ni casos cuantificados que comparen costes de Lambda, Kappa y lakehouse; la evidencia es opinión o vendor.

### Medallion

Medallion es una convención de capas, no un estándar formal. Bronze guarda el dato "tal cual" con metadatos de carga para CDC, auditoría y reproceso; Silver lo conforma, limpia y deduplica (limpieza "just-enough", modelos 3NF o Data Vault); Gold ofrece modelos desnormalizados de lectura por proyecto (Kimball, marts) ([Databricks](https://www.databricks.com/glossary/medallion-architecture)). La página oficial no lista desventajas. Los modos de fallo son inferencia mía, sin literatura empírica: silver convertido en cajón de sastre, proliferación de golds con métricas divergentes sin capa semántica, latencia y coste de tres saltos materializados, ambigüedad sobre dónde aplicar PII y bronze sin contrato. El mapeo con dbt (staging, intermediate, marts) es casi 1:1.

### Data mesh

Data mesh (Dehghani, 2019) tiene cuatro principios: propiedad por dominio, datos como producto, plataforma self-serve y gobernanza federada computacional, declarados "colectivamente necesarios y suficientes" ([Dehghani](https://martinfowler.com/articles/data-mesh-principles.html)). La evidencia es cualitativa. Un estudio de 15 entrevistas a expertos halló dificultad para pasar a gobernanza federada, asumir responsabilidad de data products y entender el concepto ([arXiv 2302.01713](https://arxiv.org/abs/2302.01713)). Starburst (vendor con sesgo a federación) atribuye los fallos a ownership solapado, falta de skills en dominios, catálogos degradados y rollouts big-bang, y recomienda pilotos de máximo dos dominios y plataforma como producto ([Starburst](https://www.starburst.io/blog/data-mesh-what-happened/)). Cifras de adopción (8-12%) circulan por citas secundarias de Gartner sin verificar con la fuente original ([arXiv 2606.08266](https://arxiv.org/pdf/2606.08266)). **No hay literatura consolidada con tasas de éxito medidas: tema de evidencia pobre.** Encaja en organizaciones grandes con dominios autónomos y plataforma madura; no en equipos pequeños o de un dominio dominante.

### Tabla comparativa de arquitecturas

Madurez y umbrales son estimaciones del análisis, a validar.

| Arquitectura | Eje | Cuándo usar | Cuándo no | Ventajas | Limitaciones | Madurez |
|---|---|---|---|---|---|---|
| Batch | Procesamiento | Horas de latencia, reportes, backfills | Decisiones en segundos | Simple, barato, reproducible | Latencia | Muy alta |
| Streaming | Procesamiento | Fraude, alertas, personalización | Equipos sin experiencia en estado y orden | Baja latencia | Complejidad operativa y de estado | Alta |
| Lambda | Procesamiento | Ya existe batch y se añade baja latencia | Proyectos nuevos sin necesidad dual | Pragmático | Lógica duplicada | Alta, nicho |
| Kappa | Procesamiento | Eventos como fuente de verdad, equipo de streaming | Reprocesos masivos baratos con batch | Una ruta de código | Retención y coste, difícil en la práctica | Media-alta |
| Data warehouse | Almacenamiento | BI/SQL, equipos pequeños | ML sobre no estructurado a gran escala | Gobierno, rendimiento SQL | Coste a escala, formatos propietarios | Muy alta |
| Data lake | Almacenamiento | Crudo y semiestructurado barato | Sin gobierno (swamp) | Barato, flexible | Sin ACID por defecto | Alta (legado) |
| Lakehouse | Almacenamiento | BI y ML en una capa, formatos abiertos | Latencia sub-segundo | ACID, abierto | Compaction, catálogo, fragmentación | Alta, creciente |
| Medallion | Layout | Refinamiento progresivo | Latencia extrema | Linaje, reprocesos | Capas sobrecargadas | Alta (convención) |
| Data mesh | Organización | Muchos dominios autónomos | Organizaciones pequeñas | Escala organizativa | Cambio cultural, gobernanza difícil | Baja-media, evidencia escasa |
| Data fabric | Metadatos/integración | Datos distribuidos con virtualización | Basta un warehouse central | Acceso sin mover datos | Concepto difuso, marketing | Baja-media |
| Event-driven | Integración | Sistemas desacoplados | Consistencia fuerte multi-paso sin sagas | Desacople | Depuración, orden, evolución de esquema | Alta |
| Reverse ETL | Activación | Warehouse como fuente de segmentos | Basta integración directa | Cierra el ciclo analítico-operacional | Calidad, coste por filas | Media |

### Qué elegir según contexto (heurística del análisis)

Con equipo de 1-5 personas, menos de ~1 TB y latencia de horas, basta un warehouse cloud más ELT con dbt y orquestador. Con 5-30 personas, múltiples fuentes y latencia de minutos, un lakehouse con medallion, CDC a bronze y micro-batch. Con latencia de segundos y casos operacionales, arquitectura event-driven con Flink/Kafka y OLAP en tiempo real para servir. Solo con muchos ingenieros y dominios autónomos (>30-50) tiene sentido considerar mesh, y antes conviene probar plataforma central más contratos.

## 4. Pipelines, ingesta y orquestación

### Orquestación: Airflow 3, Dagster y Prefect

Airflow 3.0 (abril 2025) introdujo una Task Execution API con API server separado (AIP-72), versionado de DAGs (AIP-65/66, la feature más pedida en su encuesta), backfills dentro del scheduler lanzables desde UI/API (AIP-78), Datasets convertidos en Assets (AIP-74/75), asset watchers para scheduling event-driven (AIP-82), UI React sobre FastAPI y la eliminación de la unicidad de execution date (AIP-83), que permite DAGs sin data interval como inferencia ([Airflow blog](https://airflow.apache.org/blog/airflow-three-point-oh-is-here/)). Una fuente secundaria sitúa Airflow en la línea 3.3 a octubre de 2026, con asset partitioning en 3.2 ([datalakehousehub](https://datalakehousehub.com/blog/orchestration-in-2026/)); no se verificaron las release notes primarias.

Según la misma fuente única, Dagster destaca en lineage a nivel de tabla, particiones y checks, y "todo debe encajar en el modelo de assets"; Prefect 3 es el más liviano de operar; Airflow tiene el ecosistema más grande y el mayor footprint (scheduler, API server, base de datos, workers, triggerer). Tratar con cautela. Astronomer, parte interesada, posiciona Dagster para greenfield centrado en dbt ([Astronomer](https://www.astronomer.io/airflow/astro-vs-dagster/)).

**Prefect y Dagster:** Dagster Labs anunció el 13 de julio de 2026 que Prefect la adquiere; Dagster mantiene nombre, licencia OSS y roadmap, y los fundadores pasan a asesores tras el cierre, sin precio ni fecha de cierre publicados ([Dagster blog](https://dagster.io/blog/prefect-is-acquiring-dagster), [FAQ](https://dagster.io/dagster-customer-faq)). El estado de cierre no está confirmado. Mi recomendación: no migrar a Dagster basándose solo en roadmap hasta ver dos o tres releases posteriores al cierre; para un parque Airflow grande, subir de 2.x a 3 suele rendir más que migrar.

Alternativas [Práctica consolidada, no verificada en sesión]: Argo Workflows (nativo de Kubernetes, ML y batch contenedorizado), Temporal (durable execution para lógica de larga duración, no para tablas), y servicios nativos (MWAA, Cloud Composer, Step Functions, ADF, Databricks Workflows). Regla: task-based para heterogeneidad, asset-based cuando importan estado, lineage y backfill por partición, event-driven para baja latencia a costa de visibilidad de dependencias.

### Transformación: dbt, SQLMesh y la consolidación

Fivetran compró Tobiko Data (SQLMesh, SQLGlot) el 3 de septiembre de 2025 ([Orchestra](https://orchestra.substack.com/p/fivetran-acquires-sqlmesh-consolidation)). La fusión all-stock con dbt Labs se anunció el 13 de octubre de 2025 y, según el comunicado conjunto, se completó el 1 de junio de 2026 ([Fivetran](https://www.fivetran.com/press/fivetran-dbt-labs-complete-merger-to-create-the-data-infrastructure-for-trusted-ai-agents)); otra fuente (TechTarget) no confirma la fecha de cierre, por lo que conviene verificarla. SQLMesh fue donado a la Linux Foundation en marzo de 2026 ([The New Stack](https://thenewstack.io/fivetran-donates-sqlmesh-lf/)), con opiniones escépticas sobre inversión sostenida por canibalización ([smallbigdata](https://smallbigdata.substack.com/p/sqlmesh-dbt-and-fivetran-whats-next)).

Según el blog de dbt, dbt Core v2 tuvo su primer alpha el 1 de junio de 2026 y abre bajo Apache 2.0 el runtime que estaba bajo ELv2 en Fusion; Fusion es un binario Rust con código propietario (por ejemplo el linter SQL), con funciones gratuitas, tras login o de pago; hay ruta de migración con `dbt parse --use-v2-parser` y dbt-autofix ([dbt blog](https://docs.getdbt.com/blog/dbt-core-v2-is-here)). Las licencias se reparten entre ELv2 (Fusion), propietaria (plataforma) y BSL (MetricFlow según el FAQ) ([licencias dbt](https://www.getdbt.com/licenses-faq)). Fusion es GA en la plataforma para proyectos en Snowflake y preview en otros adapters, mientras las builds CLI seguían etiquetadas `preview` en agosto de 2026 ([dbt readiness](https://docs.getdbt.com/docs/dbt/dbt-readiness.md)). La lectura prudente es que "GA" se refiere al servicio, no al CLI de todos los adapters.

Mi criterio: dbt por defecto por ecosistema y contratación; SQLMesh si el dolor son entornos virtuales, backfills y modelos incrementales complejos (virtual environments, plan/apply, scheduler por intervalos [Práctica consolidada]); Dataform o Lakeflow declarative pipelines como alternativas por plataforma. El riesgo estratégico es la concentración de T+EL+orquestación en un vendor, mitigado por Core con licencia Apache y SQLMesh bajo LF.

### Ingesta y CDC

La ingesta pasa de producto autónomo a función de plataforma. Fivetran (que además compró Census, reverse ETL) tiene fama de mayor cobertura de conectores y mejor CDC en bases operacionales ([datalakehousehub](https://datalakehousehub.com/blog/lakehouse-ingestion-tools/), fuente secundaria). Airbyte (OSS, Iceberg como destino) y dlt (Python, code-first) cubren el lado abierto; Databricks Lakeflow Connect ofrece conectores gestionados gobernados por Unity Catalog con mezcla de GA, Preview y Beta ([Databricks docs](https://docs.databricks.com/aws/ingestion/lakeflow-connect)). Debezium es el estándar de facto de CDC log-based [Práctica consolidada]; fuentes agregadoras (generadas con IA) citan la línea 3.6 y una 3.7 alpha, pero **las versiones de Debezium no están verificadas contra debezium.io**. Criterio práctico: CDC cuando se necesita baja latencia, deletes e histórico; incremental por cursor `updated_at` si la tabla es fiable y se tolera latencia.

### Patrones de pipeline

Estos patrones son [Práctica consolidada] (FoDE, Kimball, docs de dbt): idempotencia por overwrite de partición o MERGE con clave natural, evitar append ciego; tiempos lógicos (data interval) en vez de `now()`; datos tardíos con ventana de lookback y distinción entre event time e ingestion time; backfills particionados con concurrencia limitada, escritos a staging y con swap; incrementales dbt (`merge`, `insert_overwrite`, microbatch desde 1.9) con cuidado ante schema drift; reintentos solo en tareas idempotentes; alertar por frescura del asset antes que por duración de tarea. Lo respaldado por fuente es la capacidad de plataforma: backfills gestionados y versionado en Airflow 3, particiones y checks de primera clase en Dagster.

### CI/CD, IaC y DataOps

[Práctica consolidada, no verificada]: entornos efímeros por PR (clones zero-copy o virtual environments), `dbt build --select state:modified+ --defer`, tests unitarios de modelos, data diff, linting con sqlfluff, Terraform/OpenTofu/Pulumi y Databricks Asset Bundles para infraestructura. Respaldado: el provider OpenLineage viene con Airflow desde la 2.7 y emite facets de schema, column lineage, calidad y SQL ([Atlan](https://atlan.com/connect/airflow-openlineage/)).

## 5. Almacenamiento: warehouses, lakes, lakehouses y formatos

### La guerra de formatos se mudó al catálogo

La narrativa dominante en 2026 es que Iceberg ganó como formato de interoperabilidad y que ahora importa el catálogo ([Cloudmagazin](https://www.cloudmagazin.com/fr/2026/07/01/iceberg-a-remporte-la-guerre-des-formats-maintenant-cest-le-catalogue-qui-compte/)); la fuente principal que lo desarrolla está afiliada a Dremio y es pro-Iceberg ([AM Data Lakehouse](https://amdatalakehouse.substack.com/p/lakehouse-table-formats-in-2026-iceberg)). Delta mantiene la mayor base instalada en Databricks y sigue evolucionando: la 4.0 (septiembre 2025) con catalog-managed tables en preview y Variant, formalizadas en 4.1 y con Variant GA en 4.2 ([delta.io](https://delta.io/blog/2025-09-25-delta-lake-40/), [Delta 4.2.0](https://github.com/delta-io/delta/releases/tag/v4.2.0)). Leer Delta desde otros motores pasa por capas de compatibilidad (UniForm), descritas como "de segunda clase" por una fuente sesgada.

Iceberg v3 aporta deletion vectors, tipo variant, row lineage y tipos geoespaciales; **las fuentes discrepan en cuándo es GA**: se reporta GA en Snowflake (mayo 2026) y Public Preview en Databricks ([Cloudmagazin](https://www.cloudmagazin.com/fr/2026/07/01/iceberg-a-remporte-la-guerre-des-formats-maintenant-cest-le-catalogue-qui-compte/), [Iceberg Lakehouse](https://iceberglakehouse.com/posts/table-formats-2026-breakdown/)). Iceberg v4 está en diseño y no ratificado a jul-ago 2026: árbol de metadatos adaptativo, commits de un solo fichero y rutas relativas ([Snowflake](https://www.snowflake.com/en/blog/engineering/iceberg-summit-2026-recap-v4-spec/)). Una afirmación de que Databricks propondría "Delta 5.0" con la misma estructura carece de corroboración y no debe tomarse como hecho.

Hitos de gobernanza: Databricks anunció la compra de Tabular (creadores de Iceberg) el 4 de junio de 2024 ([Databricks](https://www.databricks.com/company/newsroom/press-releases/databricks-agrees-acquire-tabular-company-founded-original-creators)); Apache Polaris, implementación vendor-neutral de la Iceberg REST Catalog spec, se graduó a Top-Level Project el 19 de febrero de 2026 ([Polaris](https://polaris.apache.org/blog/2026/02/19/apache-polaris-graduates-to-top-level-project/)); Hudi 1.0 (diciembre 2024) añadió non-blocking concurrency control e índice secundario ([Hudi](https://hudi.apache.org/blog/2024/12/16/announcing-hudi-1-0-0)); DuckLake 1.0 (13 abril 2026) guarda los metadatos en una base SQL en lugar de ficheros ([duckdb.org](https://duckdb.org/history)). Inferencia: el catálogo es el nuevo punto de control y de lock-in (gobierno, credential vending, commits coordinados), y Delta catalog-managed e Iceberg v4 convergen hacia "el catálogo coordina los commits". DuckLake es una contra-tesis atractiva con ecosistema aún pequeño. Paimon (nacido en Flink/Alibaba) y Hudi quedan como nichos de streaming y upserts; no hay cifras verificadas de cuota de mercado.

| Formato de tabla | Fortaleza | Limitación | Madurez |
|---|---|---|---|
| Iceberg | Spec abierta, multi-motor, REST catalog | Mantenimiento y fragmentación de catálogos; v3/v4 en movimiento | Alta |
| Delta | Integración con Databricks, evolución rápida | Interop externa vía UniForm | Alta |
| Hudi | Upserts incrementales, NBCC | Ecosistema menor | Media-alta |
| Paimon | Semántica de streaming (Flink) | Sin fuentes primarias verificadas | Media |
| DuckLake | Metadatos SQL ACID, simplicidad | Ecosistema pequeño | Emergente |

### Warehouse vs lakehouse

Las fronteras se difuminan: Snowflake y Fabric/OneLake comparten tablas Iceberg con una sola copia (GA el 30 de enero de 2026) ([Fabric blog](https://blog.fabric.microsoft.com/en-us/blog/microsoft-onelake-and-snowflake-interoperability-is-now-generally-available?ft=All)). El modelo de coste difiere: el warehouse acopla cómputo y almacenamiento y oculta el mantenimiento; el lakehouse usa objeto barato y cómputo a elección, pero traslada el mantenimiento (compactación, expiración, catálogo) y requests/egress al equipo [inferencia]. Regla: warehouse para BI/SQL con equipo pequeño; lakehouse para multi-motor, ML/streaming y volumen alto; Iceberg compartido como híbrido en alza. No hay precios verificados ni benchmarks neutrales.

### Operativa del lakehouse

El coste real está en el mantenimiento. S3 admite escrituras condicionales (If-None-Match/If-Match) desde 2024, base para commits ACID sin coordinador ([AWS](https://aws.amazon.com/about-aws/whats-new/2024/08/amazon-s3-conditional-writes)); S3 Tables redujo desde el 1 de julio de 2025 los costes de compactación hasta un 90% ([AWS](https://aws.amazon.com/about-aws/whats-new/2025/07/amazon-s3-tables-reduce-compaction-costs)). Una anécdota de blog (Glue 1,32 USD vs S3 Tables 0,0875 USD en una semana de mantenimiento) no es generalizable. Checklist [Práctica consolidada]: compactación periódica (objetivo ~128-512 MB), sort/z-order o liquid clustering, `expire_snapshots`, `remove_orphan_files`, `rewrite_manifests`, límites de retención de time travel y vigilancia de la tasa de commits por tabla en streaming. Los deletion vectors abaratan updates frente a copy-on-write.

### Formatos de fichero

Parquet sigue siendo el estándar de facto; Avro para filas y streaming con schema registry; ORC en el ecosistema Hive; Arrow para memoria e IPC [Práctica consolidada]. Vortex (columnar extensible, interoperable con Arrow) y Lance (orientado a IA y vectores) atacan acceso aleatorio y cargas multimodales. Las cifras del proyecto Vortex (100x en lectura aleatoria, 10-20x en scans) contrastan con un benchmark de Zilliz de ~2,4x en full scan ([Zilliz](https://zilliz.com/ai-faq/lance-vs-vortex)), y existe la postura contraria de que Parquet no está muerto ([urandom.io](https://urandom.io/blog/2026-05-18-parquet-is-paying-a-cpu-tax-it-cant-afford)). Sin validación independiente; la fundación exacta de ambos proyectos no está confirmada.

### OLAP y motores embebidos

Pinot sirve a usuarios con alta concurrencia (star-tree index, <100 ms), Druid encaja en streaming y series temporales, StarRocks en joins/BI y lakehouse, y ClickHouse como propósito general rápido, aunque prefiere esquemas desnormalizados; las fuentes son competidores entre sí ([StarTree](https://startree.ai/blog/a-tale-of-three-real-time-olap-databases), [Tinybird](https://www.tinybird.co/blog/md/best-database-for-olap)). DuckDB alcanzó 1.0 en junio de 2024 ([duckdb.org](https://duckdb.org/2024/06/03/announcing-duckdb-100)) y 1.4 LTS en septiembre de 2025 con MERGE, cifrado y escrituras Iceberg ([DuckDB 1.4](https://duckdb.org/2025/09/16/announcing-duckdb-140)). Cubre ETL local, CI y datos de cientos de GB a pocos TB en un nodo; no sirve para alta concurrencia de escritura multiusuario. **No verificado:** un resumen automático afirmó que DuckDB Labs se une a AWS (26 de agosto de 2026); el mismo método produjo un error evidente en otra página, así que no se debe usar.

Feature stores y vector stores (Feast, pgvector, Lance) no se cubrieron con fuentes; ver sección 15.

## 6. Procesamiento batch y streaming

### Cómo elegir motor

No hay ganador universal. La comparación pública es mayormente de vendors (RisingWave, Tinybird), con sesgo.

| Motor | Encaja cuando | Evitar cuando | Nota |
|---|---|---|---|
| Kafka Streams | Lógica por evento en microservicio Java sobre Kafka, estado moderado | Fuentes no Kafka, estado enorme | Librería, no clúster; coste: rebalanceo de state stores y replay de estado ([RisingWave](https://risingwave.com/blog/kafka-streams-vs-risingwave-2026), vendor) |
| Flink | Estado grande, event-time complejo, CEP, joins complejos, <1 s | Equipo sin capacidad de operar clúster | "Poderoso pero caro de operar" (vendor competidor) |
| Materialize / RisingWave | Vistas SQL frescas servidas a apps, CDC como fuente | Transformaciones muy custom | Materialize: strict-serializable, cloud, BSL; RisingWave compatible con PostgreSQL; su benchmark Nexmark (22/27 queries vs Flink) es propio y sin verificar |
| Spark Structured Streaming / SDP | Ya hay lakehouse Spark y SLA de minutos | Latencia de ms con estado | 4.1: Real-Time Mode solo para consultas stateless; agregaciones, dedupe y stream-stream joins previstos "desde 4.3" ([Spark docs](https://apache.googlesource.com/spark/+show/master/docs/streaming/real-time-mode.md)) |

Flink 2.0 desagrega el estado (ForSt, LSM sobre sistema de ficheros distribuido) con ejecución asíncrona; el paper VLDB 2025 reporta hasta -94% en duración de checkpoint, hasta 49x en recuperación y rescale y hasta 50% de ahorro frente a Flink 1.20 ([VLDB 2025](https://www.vldb.org/pvldb/vol18/p4846-mei.pdf)). Son cifras de los autores del sistema. Spark 4.0 trajo ANSI mode por defecto, tipo VARIANT y Spark Connect con alta paridad ([Spark 4.0](https://spark.apache.org/releases/spark-release-4-0-0.html)); a octubre de 2026 conviene verificar si 4.2 o 4.3 ya cubren RTM con estado. Kafka 4.0 eliminó ZooKeeper (solo KRaft), dejó GA el protocolo de rebalanceo KIP-848 y trajo colas (KIP-932) en early access ([Instaclustr](https://www.instaclustr.com/blog/kafka-4-0-unveiled-key-changes-and-how-they-impact-developers/)); KIP-1150 (Diskless Topics, escritura a object storage) fue aceptado el 2 de marzo de 2026, con implementación pendiente ([Aiven](https://aiven.io/blog/kip-1150-accepted-and-the-road-ahead)).

Corporativo: IBM anunció la compra de Confluent por unos 11.000 M USD (31 USD por acción) el 8 de diciembre de 2025 ([Confluent](https://confluent.io/blog/ibm-to-acquire-confluent)). **Una sola fuente indica cierre el 17 de marzo de 2026, sin confirmar por segunda fuente; no usar como hecho.** WarpStream fue adquirida por Confluent el 9 de septiembre de 2024 ([AutoMQ](https://www.automq.com/blog/warpstream-after-confluent-acquisition-what-changed), fuente competidora).

### ¿Streaming real o batch frecuente?

El streaming se justifica cuando el coste del retraso es alto (seguridad, fraude, obligaciones legales, decisiones automáticas) o cuando el consumidor es una app o agente que necesita estado fresco. Una guía secundaria estima que solo 5-15% de los datos requieren tiempo real genuino, cifra débil y sin verificar ([youngju.dev](https://www.youngju.dev/transcribe/culture/2026-04-15-streaming-vs-batch-redefined-complete-guide-flink-risingwave-materialize-cdc-streaming-sql-deep-dive-guide-2025.en)). Heurística recomendada: fijar la latencia por consumidor, no por pipeline, con ingesta CDC o de eventos continua y barata, transformación en micro-batch o incremental, y streaming real solo para el subconjunto con SLA de segundos. El streaming lakehouse (Flink o Spark hacia Iceberg, Hudi o Paimon) da frescura de 1-5 minutos con semántica de tabla.

Motores nativos: Gluten se graduó a top-level en marzo de 2026 y DataFusion Comet reportó su 1.0.0 estable el 7 de agosto de 2026 ([Dremio](https://www.dremio.com/newsroom/apache-elevates-open-source-projects-gluten-and-polaris-to-top-level-status/), [datalakehousehub](https://datalakehousehub.com/blog/datafusion-comet-1-spark-iceberg)). Para volúmenes de un nodo (<~1 TB), DuckDB y Polars sustituyen a Spark con menor coste [inferencia]. Beam, Pulsar, Redpanda, ksqlDB, Trino/Presto y Ray se mencionan solo desde conocimiento general (Beam como capa de portabilidad, Redpanda compatible con Kafka y en BSL, Trino para SQL federado interactivo) y no se verificaron en 2026. Conceptos estables de Akidau/Kleppmann [Práctica consolidada]: event time vs processing time, watermarks como heurística de completitud, triggers con allowed lateness, dualidad stream-tabla y backpressure.

## 7. Modelado de datos y capa semántica

Kimball (star schema) sigue siendo el default de la capa de consumo; Data Vault 2.0 se justifica en integración multi-fuente con cambio frecuente, auditoría y carga paralela, con un mart Kimball encima; OBT (one big table) es una optimización de entrega, no un modelo primario. La evidencia para esto es de vendors y blogs, no benchmarks. Data Vault prioriza escalabilidad de carga sobre velocidad de consulta, por lo que el rendimiento se resuelve en una capa de reporting ([VaultSpeed](https://www.vaultspeed.com/blog/a-robust-foundation-for-data-products), vendor DV); la mayoría de warehouses de empresas tech omite DV y usa Kimball ([DataVidhya](https://datavidhya.com/learn/data-modeling-and-warehouse/modern-approaches/data-vault/)). La encuesta de Reis muestra que **solo 11% considera que su modelado va bien**, con presión por ir rápido (59%) y falta de ownership (51%) como causas ([Reis](https://joereis.substack.com/p/ai-is-here-but-the-hard-parts-havent)).

| Enfoque | Cuándo | Cuándo no | Pros | Contras | Madurez |
|---|---|---|---|---|---|
| Kimball (star) | Capa de consumo, BI | Fuentes muy cambiantes sin capa de integración | Simple de consultar, ecosistema | Se rompe con cambios de fuente | Muy alta |
| Inmon (3NF) | Core corporativo normalizado | Equipos pequeños | Integración sólida | Menor adopción explícita hoy | Alta |
| Data Vault 2.0 | Muchas fuentes, M&A, auditoría regulada, automatización | Equipo chico, pocas fuentes | Carga paralela, auditoría | Más joins y tablas | Media-alta |
| OBT / wide tables | Serving para BI, features de ML | Relaciones many-to-many, dimensiones cambiantes | Sin joins, comprime bien en columnar | Duplicación, refresh costoso | Alta como técnica |
| Activity schema | Analítica de producto y journeys | General | Una tabla de eventos | Adopción de nicho (ligada a Narrator) | Baja-media |

Los detalles de Kimball (grano declarado, bus matrix, SCD tipos 1, 2, 3, 4, 6, 7; SCD2 viable en columnar cloud) y de Data Vault (hubs, links, satellites, hashkeys, PIT/bridge) son [Práctica consolidada]. Recomendación práctica: medallion con integración opcional en Data Vault, Kimball en consumo, OBT como vista materializada para rendimiento o features y capa semántica encima. No se hallaron fuentes sobre OBT ni Activity schema, ni benchmarks de rendimiento entre enfoques.

### Capa semántica

2026 es el año de la estandarización. Open Semantic Interchange (OSI) v0.1 se lanzó el 27 de enero de 2026 como repo Apache 2.0 impulsado por Snowflake, con dbt Labs, Databricks y Salesforce en la spec inicial ([Snowflake](https://www.snowflake.com/en/blog/open-semantic-interchanges-specs-finalized/)), y pasó a la Apache Incubator como "Apache Ossie" (anuncio del 10 de julio de 2026) ([Ossie](https://ossie.apache.org/)). Fuentes agregadoras indican que MetricFlow pasó a Apache 2.0 en diciembre de 2025, pero **no se confirmó con dbt Labs** (y el FAQ de licencias lo listaba como BSL). Cube Core (Apache 2.0) cubre serving de alta concurrencia y APIs ([Cube](https://cube.dev/articles/dbt-semantic-layer-alternatives-2026), vendor). Los semantic layers nativos de plataforma (Snowflake Semantic Views, Databricks Metric Views, LookML, Power BI) presionan a los independientes [Práctica consolidada, verificar]. El motor de la tendencia es que los agentes de analítica necesitan métricas gobernadas: en Spider 2.0 (632 tareas empresariales reales) modelos que rinden ~91% en Spider 1.0 resuelven solo ~17-21% en el paper original ([arXiv 2411.07763](https://www.arxiv.org/pdf/2411.07763)); no hay datos 2026 de modelos más nuevos. Madurez: dbt SL, Cube y LookML en producción; OSI/Ossie emergente y en v0.1, con riesgo de perder expresividad frente a formatos nativos.

## 8. Calidad, observabilidad y gobernanza

### Calidad de datos

Combinar tests deterministas en el pipeline (dbt tests, Great Expectations, Soda) con auditoría Write-Audit-Publish (WAP) en tablas críticas y monitorización estadística. WAP sobre ramas Iceberg escribe en una rama de staging, audita y hace fast-forward a main si pasa, a coste de latencia; AWS y Cloudera documentan la configuración y Netflix audita sobre un snapshot oculto ([AWS](https://aws.amazon.com/blogs/big-data/build-write-audit-publish-pattern-with-apache-iceberg-branching-and-aws-glue-data-quality/), [Cloudera](https://community.cloudera.com/t5/Developer-Blogs/Iceberg-WAP-Failsafe-ETL-with-Iceberg-and-CDE/m-p/413008)). Soda tiene núcleo OSS y plataforma comercial, Great Expectations es framework Python con GX Cloud opcional y Elementary es observabilidad dbt-native limitada a modelos dbt ([DataExpert](https://www.dataexpert.io/blog/soda-vs-great-expectations-data-quality-tools), [comparativa](https://medium.com/@aidelearning/data-observability-in-2026-monte-carlo-vs-great-expectations-vs-soda-a-data-engineers-honest-7c8cab1b68f1)). Dimensiones DAMA [Práctica consolidada]: completitud, unicidad, validez, exactitud, consistencia, frescura, integridad; circuit breakers con severidad warn/error para evitar fatiga de alertas; Deequ para volúmenes grandes en Spark.

### Contratos de datos

ODCS es el estándar abierto de referencia, con soporte en DataHub y Data Contract CLI ([DataHub](https://docs.datahub.com/docs/generated/ingestion/sources/odcs)). Un post menciona un RFC aprobado para ODCS v3.2 (19 de mayo de 2026) con bloque de contexto para IA, no confirmado en la página oficial. La adopción se frena por ownership y organización más que por tecnología: una tesis de Aalto (10 entrevistas, un caso) señala tensión autonomía local vs dirección central y falta de claridad de roles ([Aalto](https://aaltodoc.aalto.fi/items/9643d2ad-40ad-4cdb-a12d-792695ec30c1)); un estudio BARC 2026 patrocinado por Actian (308 encuestados) habla de retos técnicos y organizativos al escalar ([BARC](https://barc.com/research/data-products-contracts-2026/)). No hay datos independientes de tasa de adopción. Trampas [Práctica consolidada]: contratos no ejecutados en CI (documentación muerta), productores sin incentivo, contratos sobre tablas internas, confundir contrato con esquema. Mitigación: empezar por 5-10 interfaces críticas, enforcement en CI y runtime (schema registry, `contract: enforced` de dbt) y política de breaking changes.

### Observabilidad y lineage

El cruce build/buy se sitúa en torno a >20 ingenieros según una comparativa; para equipos pequeños basta Elementary más OpenLineage/Marquez con alertas propias, y las plataformas (Monte Carlo, Bigeye) se justifican con muchas fuentes y equipos, con costes de seis cifras anuales en enterprise ([datadrivendaily](https://datadrivendaily.com/data-observability-tools-compared-a-guide-for-2026/)); todo es literatura de proveedor. OpenLineage es el estándar de eventos de lineage y Marquez su implementación de referencia, con integraciones en Airflow, dbt, Spark, Flink, Dagster y GX ([Adaltas](https://www.adaltas.com/en/2024/02/19/openlineage-introduction/)); la gobernanza de la fundación (LF AI & Data vs CNCF) es contradictoria entre fuentes, con LF AI & Data mejor respaldada. SLOs de datos [Práctica consolidada]: SLI de frescura, volumen y éxito de contratos por data product con error budget. La observabilidad de coste (FinOps) no se investigó con fuentes.

### Gobernanza y catálogos

DataHub y OpenMetadata (ambos Apache) requieren capacidad de ingeniería (DataHub necesita operar infraestructura incluyendo Kafka según una fuente); Atlan se recomienda para mid-size, Collibra para regulados, y Unity Catalog es el catálogo por defecto en Databricks, no un catálogo global ([daily.dev](https://daily.dev/posts/openmetadata-vs-datahub-vs-amundsen-vs-commercial-2026--upeyjiiqu.md), [pdpspectra](https://pdpspectra.com/blog/data-catalog-datahub-vs-atlan-vs-collibra)). Un análisis estima el coste oculto del OSS en 0,25-1,0 FTE; las fuentes están muy sesgadas y las citas de Gartner/Forrester vienen de materiales de proveedor. Gobierno mínimo viable (síntesis propia): inventario de tablas críticas con owner y tier; catálogo auto-ingestado con descripciones en el 20% principal; clasificación PII en origen con RBAC y masking por defecto; contratos, tests y alertas en interfaces tier-1; proceso DSAR y registro de tratamientos; revisión trimestral con un data council pequeño. MDM, Purview y DAMA-DMBOK no se investigaron.

## 9. Seguridad y compliance

### Borrado GDPR en lakehouses

Un DELETE lógico no borra bytes. En Delta hace falta DELETE o MERGE más VACUUM, y `REORG TABLE ... APPLY (PURGE)` si hay deletion vectors; el historial se retiene 30 días por defecto ([Databricks](https://docs.databricks.com/aws/en/security/privacy/gdpr-delta)). En Iceberg el orden es DELETE, compactación (`rewrite_data_files`), `expire_snapshots` y finalmente `remove_orphan_files`, con retención de snapshots de 5 días por defecto ([Dremio](https://www.dremio.com/subsurface/apache-iceberg-and-the-right-to-be-forgotten/), [datalakehousehub](https://datalakehousehub.com/blog/gdpr-hard-deletes-on-iceberg), [AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/apache-iceberg-on-aws/table-spec-v3.html)); estas fuentes de Iceberg son blogs de proveedores, así que verificar orden y parámetros en la documentación oficial por motor. Hay que propagar el borrado a tablas derivadas, fuentes (Kafka, ficheros), backups y cachés; un full refresh con fuente cuya retención expiró puede perder datos, y la ofuscación puede permitir reidentificación. Receta [síntesis propia]: registro DSAR con el plazo de un mes del art. 12; PII aislada con clave subrogada y clustering por subject id; borrados en lotes periódicos; retención de time-travel acortada para tablas con PII; propagación a silver/gold, feature stores e índices vectoriales; política de expiración de backups acordada con el DPO; evidencia auditable. Crypto-shredding (clave por sujeto en KMS) evita reescrituras pero añade gestión de claves. El derecho al olvido tiene excepciones (fiscal, AML).

Criterio de identificabilidad: el TJUE en EDPS v SRB (C-413/23 P, 4 de septiembre de 2025) aclara que datos seudonimizados pueden no ser personales para un receptor que no puede reidentificar (resumen secundario; leer la sentencia), y la Opinión 28/2024 del EDPB (17 de diciembre de 2024) establece que los modelos de IA entrenados con datos personales no son siempre anónimos ([IAPP](https://iapp.org/news/a/edpb-weighs-in-on-key-questions-on-personal-data-in-ai-models), [CMS](https://cms.law/en/bel/legal-updates/edpb-opinion-28-2024-key-takeaways-on-processing-personal-data-in-the-context-of-ai-models)).

### Regulación con fechas móviles

El Data Act de la UE es aplicable desde el 12 de septiembre de 2025; los cargos de egress por cambio de proveedor deben eliminarse desde el 12 de enero de 2027 (hasta entonces, solo costes reales); una guía que dice septiembre de 2027 está contradicha por la mayoría ([Travers Smith](https://www.traverssmith.com/knowledge/knowledge-container/the-data-acts-changes-to-cloud-services-contracts-tipping-the-scales-on-switching/), [Cooley](https://www.cooley.com/news/insight/2025/2025-09-08-paas-iaas-or-saas-be-aware-new-switching-rules-will-become-applicable-in-eu)). **AI Act:** el acuerdo provisional del Digital Omnibus (7 de mayo de 2026) retrasaría los sistemas de alto riesgo del Anexo III al 2 de diciembre de 2027 y los del Anexo I al 2 de agosto de 2028; el Parlamento votó el 16 de junio de 2026, pero la adopción formal y publicación en el Diario Oficial **no están confirmadas** en las fuentes ([Gibson Dunn](https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/), [Sidley](https://datamatters.sidley.com/2026/06/22/eu-lawmakers-reach-provisional-agreement-to-delay-key-eu-ai-act-obligations/)). Tratar estas fechas como provisionales y validar con asesoría legal.

### Controles técnicos [Práctica consolidada, no verificada en sesión]

Cifrado en reposo y tránsito con claves gestionadas por el cliente y rotación; RBAC base más ABAC por etiquetas (Unity Catalog, tags de Snowflake, Lake Formation LF-TBAC, Ranger); seguridad a nivel de fila y columna con masking dinámico; tokenización (vault o format-preserving) para PCI; descubrimiento de PII (Macie, Purview, Presidio, BigID); secretos en Vault o Secrets Manager con credenciales efímeras y OIDC; zero trust con identidad por workload y mínimo privilegio. Marcos: GDPR, CCPA/CPRA, HIPAA (BAA), SOC 2, PCI DSS 4.0. Residencia de datos con regiones UE y controles de transferencia (SCC, Data Privacy Framework). Los textos oficiales de GDPR, Data Act y AI Act no fueron leídos directamente.

## 10. Plataformas cloud, on-premise, híbrido y soberanía

### Las cuatro plataformas convergen

Databricks, Snowflake, BigQuery y Fabric apuntan al mismo diseño: tablas Iceberg abiertas, catálogo gobernado, Postgres/OLTP integrado y capa de agentes. Databricks compró Neon (mayo 2025), base de Lakebase (Postgres gestionado con autoscaling y branching), y Mooncake Labs (1 de octubre de 2025) ([TechTarget](https://www.techtarget.com/data-technologies/news/366631950/Mooncake-acquisition-boosts-Databricks-database-capabilities)); Snowflake anunció Crunchy Data en junio de 2025 ([TechCrunch](https://www.techcrunch.com/2025/06/02/snowflake-to-acquire-database-startup-crunchy-data/)). Los precios citados (~1.000 M USD por Neon, ~250 M USD por Crunchy) proceden de fuentes únicas o anónimas. Los keynotes de 2026 (Data+AI Summit del 15 al 18 de junio, Snowflake Summit, Google Cloud Next '26) anunciaron capas de contexto y agentes con nombres propietarios distintos: Genie One y Genie Ontology, Horizon Context y CoWork, Knowledge Catalog ([Flexera](https://www.flexera.com/blog/perspectives/databricks-data-ai-summit-2026-recap-genie-one-ltap-lakehouse-rt-and-every-major-launche/), [Revefi](https://www.revefi.com/blog/key-takeaways-snowflake-summit-2026), [Nand Research](https://nand-research.com/google-cloud-next-2026-enterprise-ai-enters-production/)). Son recaps de terceros o de vendor, con estado GA/preview sin verificar: **tratar nombres y disponibilidad como provisionales**. En AWS, re:Invent 2025 puso Iceberg en el centro y S3 Tables adoptó la Iceberg REST catalog spec en marzo de 2025 ([AWS Big Data](https://aws.amazon.com/blogs/big-data/aws-analytics-at-reinvent-2025-unifying-data-ai-and-governance-at-scale)). En Fabric destacan OneLake security y mirroring ([Fabric blog](https://blog.fabric.microsoft.com/en-au/blog/whats-new-in-onelake-and-the-fabric-platform-more-sources-security-and-capacity-tooling)).

Criterios de decisión (síntesis propia, no verificada como tabla oficial):

| Plataforma | Elegir cuando | Riesgo principal |
|---|---|---|
| Databricks | Fuerte ingeniería, ML y streaming; un plano de gobernanza (Unity) | Complejidad de costes; base Delta |
| Snowflake | SQL/BI, data sharing, equipos analíticos con poca ops | Coste a escala; rebrands frecuentes |
| BigQuery | Ya en GCP, cargas ad hoc y serverless | Dependencia de ecosistema GCP |
| Fabric | Organización centrada en Microsoft (Power BI, Entra) | Modelo de capacidad (CU); madurez desigual entre workloads |
| AWS nativo (S3 Tables, Athena, EMR, Redshift) | Menor lock-in | Mayor esfuerzo de integración |

Como los roadmaps son casi idénticos, el criterio relevante es coste y gobierno reales, no features de keynote. No hay benchmarks independientes ni cuotas de mercado verificadas.

### On-premise, híbrido y soberanía

La evidencia aquí es la más débil del informe. Verificado: AWS European Sovereign Cloud salió GA el 15 de enero de 2026 con región independiente en Brandenburg y una inversión de 7.800 M EUR ([AWS](https://press.aboutamazon.com/aws/2026/1/aws-launches-aws-european-sovereign-cloud-and-announces-expansion-across-europe)); un agregador que da fecha de julio de 2026 está contradicho. Lo demás es [Práctica consolidada, no verificada en 2026]: Kubernetes con Spark, Trino o Flink e Iceberg sobre MinIO o Ceph es viable pero exige equipo de plataforma; Cloudera (CDP Private Cloud) y las migraciones desde Hadoop se orientan a lakehouse Iceberg; Hadoop/HDFS/YARN/Hive son legado, y Hive Metastore persiste como catálogo; el coste oculto está en operar almacenamiento y seguridad; las licencias de MinIO y Ceph han cambiado y deben verificarse. "Soberano" no equivale a ausencia de jurisdicción extranjera: depende del control operativo y legal. Los EU Data Act switching rules (sección 9) refuerzan la portabilidad.

## 11. Stack moderno por categoría

Mercado en re-empaquetado: ingestión y transformación (Fivetran más dbt), plataforma más Postgres e IA (Databricks, Snowflake), streaming (IBM más Confluent) y orquestación (Prefect más Dagster). Matt Turck contaba 2.011 logos en el mapa MAD 2024 frente a 1.416 en 2023 y decía que la consolidación aún no había llegado ([MAD 2024](https://mattturck.com/mad2024/)). Prioricé criterios sobre listas.

| Categoría | Opciones maduras | Emergente o volátil | Criterio de elección |
|---|---|---|---|
| Ingesta y CDC | Fivetran, Debezium, Kafka Connect | Airbyte, dlt, Lakeflow Connect, mirroring/zero-ETL nativo | CDC para baja latencia; mirroring nativo erosiona conectores genéricos |
| Streaming/mensajería | Kafka (KRaft), Flink, Kafka Streams | Diskless Kafka, RisingWave, Materialize, Redpanda | SLA de frescura y madurez del equipo |
| Almacenamiento | Object storage, Parquet, Iceberg, Delta | Iceberg v3/v4, DuckLake, Vortex, Lance | Interoperabilidad y catálogo |
| Catálogo de tablas | Unity, Glue, Polaris | REST catalogs, Lakekeeper, Nessie (no verificados) | Neutralidad vs integración |
| Motores | Spark, Snowflake, BigQuery, Databricks SQL, Trino | DuckDB, Polars, Comet, Gluten | Escala y concurrencia |
| OLAP en tiempo real | ClickHouse, Pinot, Druid, StarRocks | Lakehouse//RT | Concurrencia y latencia de serving |
| Transformación | dbt, Spark SQL | dbt Fusion/Core v2, SQLMesh (LF) | Ecosistema vs entornos virtuales |
| Orquestación | Airflow 3, cloud-native | Dagster/Prefect (en fusión), Argo, Temporal | Task vs asset vs evento |
| Calidad y observabilidad | dbt tests, GX, Soda, Elementary | Monte Carlo, Bigeye, OpenLineage/Marquez | Build vs buy en torno a 20 ingenieros |
| Gobernanza | Unity, DataHub, OpenMetadata, Atlan, Collibra | Contratos ODCS, ODPS | Capacidad de ingeniería y regulación |
| Capa semántica | dbt SL, Cube, LookML | OSI/Ossie | Agentes y métricas gobernadas |
| Activación | Reverse ETL (Census dentro de Fivetran) | Mercado fragmentado | Warehouse como fuente de verdad |

Las áreas con poca consolidación observada (observabilidad, catálogo independiente, BI/semántica, reverse ETL restante, calidad y contratos) lo son por ausencia de noticias de M&A encontradas, no por medición.

## 12. Patrones avanzados, anti-patrones y errores comunes

### Patrones [Práctica consolidada, no verificada en sesión]

El patrón **outbox** evita el dual-write entre base transaccional y bus de eventos; CDC más outbox es la base de integración event-driven. **Event sourcing** hace del log la fuente de verdad (Kappa). **WAP** con ramas Iceberg, Nessie, lakeFS o clones Delta cierra la calidad en publicación. **Data products** con contrato, owner y SLA, **schema registry** como base técnica de contratos en streaming, **backfills idempotentes por partición** y **multi-tenancy** con aislamiento por tags y políticas. Los feature stores pierden peso frente a tablas gobernadas con serving online. Medallion es una convención de capas, no una arquitectura completa.

### Anti-patrones y errores comunes

El ranking siguiente es juicio propio sin medición; solo el primer grupo tiene respaldo en encuestas.

1. **Falta de ownership y de contratos**, con roturas upstream silenciosas: 51% reporta falta de ownership en modelado y 19% requisitos upstream deficientes ([Reis](https://joereis.substack.com/p/the-2026-state-of-data-engineering)).
2. **Full refresh por defecto, `SELECT *`, scans sin partición ni clustering, warehouses sobredimensionados o siempre encendidos.** El gasto que crece más que el dato sugiere duplicación, schedule creep y marts redundantes ([Revefi](https://www.revefi.com/blog/avoiding-snowflake-data-cost-pitfalls), vendor).
3. **Archivos pequeños y streaming innecesario.** Snowpipe cobra overhead por archivo (~0,06 créditos por 1.000 archivos) y se recomiendan ficheros comprimidos de 100-500 MB ([PointFive](https://www.pointfive.co/knowledge-base/inefficient-snowpipe-usage-due-to-small-file-ingestion)); cifras sin contrastar con precios oficiales.
4. **Egress entre regiones o nubes** que pasa desapercibido.
5. **DAGs espagueti** con dependencias implícitas y backfills no idempotentes.
6. **Over-engineering:** un stack de 15 herramientas para menos de 1 TB.
7. Medallion mal usado (silver sobrecargado, gold por consumidor), mesh como reorganización sin plataforma, contratos sin enforcement.

La encuesta de dbt Labs (vendor) añade que 57% reporta más gasto en warehouse y cómputo frente a 36% con más presupuesto de equipo, y 71% teme que datos alucinados lleguen a stakeholders ([dbt Labs](https://www.getdbt.com/resources/state-of-analytics-engineering-2026-download), vía resumen de búsqueda).

## 13. Mejores prácticas de producción

Las siguientes son [Práctica consolidada] y coinciden con lo que las fuentes sugieren: tests de datos en CI (dbt tests y unit tests, GX o Soda) y contrato validado en el PR; entornos efímeros o branching por cambio; observabilidad por frescura, volumen, schema y lineage con OpenLineage; runbooks y on-call con SLOs por data product; pipelines idempotentes con orquestación por intervalo lógico; WAP en tablas tier-1; PII aislada y borrado diseñado desde el principio; etiquetado de costes por equipo y producto con alertas de presupuesto; formatos abiertos y SQL portable para mitigar lock-in; documentación generada pero revisada. Un matiz de la encuesta de dbt: 72% prioriza código asistido por IA frente a solo 24% gestión de pipelines asistida (testing, observabilidad, calidad), lo que apunta a un hueco en la automatización de la calidad.

## 14. Escalabilidad, coste y mantenimiento

El coste del lakehouse es de operación: compactación, expiración de snapshots y catálogo, con servicios gestionados (S3 Tables) que bajan el mantenimiento y commits de un fichero (Iceberg v4) o metadatos SQL (DuckLake) que atacan el crecimiento de metadatos. El coste del warehouse es de consumo opaco: gobernarlo exige tags, vistas de consumo (ACCOUNT_USAGE, system tables), apagado automático y presupuestos [Práctica consolidada] ([Xebia](https://xebia.com/blog/databricks-finops-optimization-strategies/), genérico). En streaming, el diskless Kafka cambia latencia (cientos de ms a ~1-2 s p99, no verificado) por ahorro de tráfico inter-AZ. Flink 2.0 reduce el coste de checkpoints y rescale con estado en objeto, según los propios autores. En escala pequeña, DuckDB y Polars evitan clústeres. La escala organizativa pesa tanto como la técnica: el cruce build/buy de observabilidad en ~20 ingenieros y el coste de 0,25-1,0 FTE por catálogo OSS son órdenes de magnitud de fuentes con sesgo. La presión de coste de 2026-27 probablemente vendrá de cargas agénticas (claim vendor de MotherDuck de que los agentes ejecutan 29x más queries que humanos; especulación, sin verificar).

## 15. Evolución reciente 2023-2026 y temas de poca literatura o evolución rápida

Ejes de evolución respaldados por fuentes: la consolidación (Tabular 2024, Fivetran–Census/Tobiko/dbt 2025-26, IBM–Confluent 2025, Prefect–Dagster 2026), la maduración de Iceberg (v3, REST catalog, Polaris TLP, S3 Tables), la llegada de las bases Postgres a las plataformas de datos y la irrupción de agentes y capas de contexto. En IA, 82% de los encuestados de Reis usa IA a diario, pero 64% de las organizaciones aún experimenta o la usa tácticamente, y 42% espera crecer el equipo frente a 7% que espera reducirse ([Reis](https://joereis.substack.com/p/the-2026-state-of-data-engineering)). Mi lectura: el rol del data engineer se desplaza de escribir pipelines a plataforma, contratos, calidad, coste y curación de contexto; el Radar de Thoughtworks vol. 34 (abril 2026) enfatiza los fundamentos de ingeniería frente a la "deuda cognitiva" ([Thoughtworks](https://www.thoughtworks.com/content/dam/thoughtworks/documents/radar/2026/04/tr_technology_radar_vol_34_en.pdf)).

### Temas con poca literatura consolidada o en evolución rápida

- **Data mesh:** evidencia cualitativa y de vendor; sin tasas de éxito medidas.
- **Data fabric:** concepto difuso; sin fuentes leídas.
- **Data contracts:** estándar en movimiento (ODCS v3.1, RFC v3.2 sin confirmar) y sin datos de adopción.
- **Catálogos Iceberg y convergencia Delta/Iceberg:** Iceberg v3 GA según plataforma discrepante; v4 sin ratificar; REST catalogs, Lakekeeper, Nessie y XTable sin verificar.
- **Capas de contexto y ontología para agentes:** tres definiciones propietarias distintas; Ossie/OSI en v0.1.
- **RAG, vector data, feature stores y procesamiento de datos no estructurados:** no cubiertos por fuentes; [Práctica consolidada] básica: pipelines de chunking, embedding e indexado con las mismas exigencias de idempotencia, linaje y borrado (los índices vectoriales deben entrar en la propagación GDPR), pgvector o bases vectoriales gestionadas según escala, y evaluación de calidad de retrieval como equivalente de los tests de datos. Sin literatura consolidada de arquitectura de referencia.
- **Evaluación de agentes y observabilidad LLM:** inmaduro.
- **Streaming lakehouse y Diskless Kafka:** diseños aceptados, implementación y latencias reales sin verificar.
- **Formatos Vortex y Lance, y DuckLake:** cifras de proveedor sin validación independiente.
- **FinOps de datos y de cargas agénticas:** sin estudios independientes.
- **On-prem, Hadoop legado y Kubernetes data platforms:** sin fuentes de 2026.

## 16. Nivel de confianza: lo no verificado

Las siguientes afirmaciones circulan en las fuentes pero **no deben tomarse como hechos establecidos**:

| Afirmación | Estado |
|---|---|
| Cierre de Prefect–Dagster | Anunciado el 13 de julio de 2026; sin precio ni fecha de cierre; cierre no confirmado |
| Cierre de Fivetran–dbt Labs el 1 de junio de 2026 | Según comunicado conjunto; otra fuente no confirma la fecha. Verificar |
| Cierre de IBM–Confluent (17 de marzo de 2026) | Fuente única; sin segunda confirmación |
| DuckDB Labs se une a AWS (26 de agosto de 2026) | Proviene de un resumen automático poco fiable; descartar |
| Delta 5.0 con estructura similar a Iceberg v4 | Sin corroboración |
| Versiones de Debezium 3.6 y 3.7 | Agregadores generados con IA; confirmar en debezium.io |
| Fechas de GA de Iceberg v3 por plataforma | Fuentes discrepantes (Snowflake GA vs Databricks preview) |
| MetricFlow bajo Apache 2.0 (dic. 2025) | Fuente secundaria; el FAQ de licencias lo listaba como BSL |
| "dbt State" | Solo fuente secundaria |
| Fusion "GA" | GA en la plataforma (Snowflake); CLI aún en preview |
| Fechas del AI Act Omnibus | Acuerdo provisional; adopción formal no confirmada |
| Precios de adquisición (Neon ~1.000 M USD, Crunchy ~250 M USD) | Fuente única o anónima |
| Estado GA de anuncios de Summit y Next 2026 | Recaps de terceros o vendor |
| Cifras de adopción de data mesh (8-12%) | Citas secundarias de Gartner |
| Benchmarks de Flink 2.0, RisingWave, Vortex y Spark RTM (~5 ms) | De los propios autores o vendors |
| Umbrales de equipo y escala (1-5, 5-30, 30-50; 20 ingenieros; 0,25-1,0 FTE) | Heurísticas, no datos medidos |

Limitaciones del conjunto: ninguna cifra de cuota de mercado, precios actuales de plataformas ni benchmarks neutrales; no se leyeron los textos oficiales de GDPR, Data Act y AI Act; no se consultaron Kimball Group ni Linstedt en fuentes primarias; las secciones de fundamentos, patrones, buenas prácticas, seguridad técnica y on-prem se apoyan en práctica consolidada, no en fuentes de 2026.

## 17. Resumen ejecutivo

1. **Las arquitecturas son ejes, no rivales.** Combine un modo de procesamiento, un almacenamiento y un layout. Fije la latencia por consumidor: la regla de Kreps (batch si no hay sensibilidad, streaming si la hay, no ambos salvo necesidad) sigue vigente, pero el lakehouse unificado con frescura de 1-5 minutos es el término medio dominante.
2. **El catálogo es el nuevo campo de batalla.** Iceberg domina la interoperabilidad (v3 en despliegue, v4 en diseño), Delta es fuerte dentro de Databricks, y el control se desplaza a catálogos REST (Polaris, Unity, Glue). Diseñe con formatos abiertos y minimice el lock-in en catálogo.
3. **El riesgo principal es organizativo.** Ownership, requisitos upstream y contratos explican más fallos que el motor elegido; empiece con 5-10 interfaces críticas con contrato ejecutable en CI.
4. **Data mesh solo con escala organizativa y plataforma madura.** La evidencia es cualitativa; pilotos de dos dominios como máximo.
5. **El mercado se reempaqueta.** Fivetran más dbt (más SQLMesh en la Linux Foundation), IBM–Confluent y Prefect–Dagster: mitigue con SQL portable, formatos abiertos y no migre por roadmap hasta ver releases posteriores a los cierres.
6. **Las plataformas convergen** en Iceberg, Postgres integrado y agentes; elija por perfil de equipo, ecosistema cloud, gobernanza y coste real, no por features de keynote.
7. **Calidad por capas:** tests deterministas, WAP en tablas críticas, observabilidad con OpenLineage y SLOs por data product; build en equipos pequeños, buy cuando crece el número de fuentes y equipos.
8. **Cumplimiento por diseño:** el borrado GDPR en lakehouse requiere compactación, expiración y purga físicas, y propagación a derivadas, backups e índices vectoriales; las fechas del AI Act son provisionales.
9. **Coste:** lo que más pesa es el mantenimiento del lakehouse, full refresh, archivos pequeños y egress; el streaming solo donde el retraso cuesta dinero.
10. **Zonas inmaduras:** capas de contexto para agentes, RAG y datos no estructurados, contratos, FinOps agéntico y on-prem; decida ahí con pilotos y no con literatura.

## 18. Referencias

Fuentes citadas (el nivel de sesgo se indica en el cuerpo del informe).

**Arquitecturas y fundamentos**
- Kreps, Questioning the Lambda Architecture: https://www.oreilly.com/radar/questioning-the-lambda-architecture/
- Confluent Tableflow: https://docs.confluent.io/cloud/current/topics/tableflow/overview.html
- Waehner: https://www.kai-waehner.de/blog/tag/delta-lake/
- Current London 2026 (Fresha): https://current.confluent.io/post-conference-videos-26/lambda-architecture-in-2025-kafka-views-and-the-evolving-data-platform-ldn26
- youngju.dev: https://www.youngju.dev/blog/culture/2026-04-15-streaming-vs-batch-redefined-complete-guide-flink-risingwave-materialize-cdc-streaming-sql-deep-dive-guide-2025.en
- Databricks, Medallion: https://www.databricks.com/glossary/medallion-architecture
- Dehghani, Data Mesh Principles: https://martinfowler.com/articles/data-mesh-principles.html
- Entrevistas data mesh: https://arxiv.org/abs/2302.01713
- Starburst: https://www.starburst.io/blog/data-mesh-what-happened/
- arXiv 2606.08266: https://arxiv.org/pdf/2606.08266
- Bibliografía canónica [no leída en sesión]: Kleppmann, *Designing Data-Intensive Applications*; Reis y Housley, *Fundamentals of Data Engineering* (2022); Armbrust et al., "Lakehouse" (CIDR 2021).

**Pipelines y orquestación**
- Airflow 3.0: https://airflow.apache.org/blog/airflow-three-point-oh-is-here/
- datalakehousehub, orquestación 2026: https://datalakehousehub.com/blog/orchestration-in-2026/
- Dagster–Prefect: https://dagster.io/blog/prefect-is-acquiring-dagster ; https://dagster.io/dagster-customer-faq
- Astronomer: https://www.astronomer.io/airflow/astro-vs-dagster/
- Fivetran–Tobiko: https://orchestra.substack.com/p/fivetran-acquires-sqlmesh-consolidation
- Fivetran–dbt Labs: https://www.fivetran.com/press/fivetran-dbt-labs-complete-merger-to-create-the-data-infrastructure-for-trusted-ai-agents
- SQLMesh a LF: https://thenewstack.io/fivetran-donates-sqlmesh-lf/ ; https://smallbigdata.substack.com/p/sqlmesh-dbt-and-fivetran-whats-next
- dbt Core v2: https://docs.getdbt.com/blog/dbt-core-v2-is-here ; https://docs.getdbt.com/docs/dbt/dbt-readiness.md ; https://www.getdbt.com/licenses-faq
- Ingesta: https://datalakehousehub.com/blog/lakehouse-ingestion-tools/ ; https://docs.databricks.com/aws/ingestion/lakeflow-connect
- OpenLineage en Airflow: https://atlan.com/connect/airflow-openlineage/

**Almacenamiento**
- https://amdatalakehouse.substack.com/p/lakehouse-table-formats-in-2026-iceberg
- https://www.cloudmagazin.com/fr/2026/07/01/iceberg-a-remporte-la-guerre-des-formats-maintenant-cest-le-catalogue-qui-compte/
- https://iceberglakehouse.com/posts/table-formats-2026-breakdown/
- https://www.snowflake.com/en/blog/engineering/iceberg-summit-2026-recap-v4-spec/
- https://www.databricks.com/company/newsroom/press-releases/databricks-agrees-acquire-tabular-company-founded-original-creators
- https://delta.io/blog/2025-09-25-delta-lake-40/ ; https://github.com/delta-io/delta/releases/tag/v4.2.0
- https://hudi.apache.org/blog/2024/12/16/announcing-hudi-1-0-0
- https://polaris.apache.org/blog/2026/02/19/apache-polaris-graduates-to-top-level-project/
- https://duckdb.org/history ; https://duckdb.org/2024/06/03/announcing-duckdb-100 ; https://duckdb.org/2025/09/16/announcing-duckdb-140
- https://blog.fabric.microsoft.com/en-us/blog/microsoft-onelake-and-snowflake-interoperability-is-now-generally-available?ft=All
- https://aws.amazon.com/about-aws/whats-new/2024/08/amazon-s3-conditional-writes ; https://aws.amazon.com/about-aws/whats-new/2025/07/amazon-s3-tables-reduce-compaction-costs
- https://zilliz.com/ai-faq/lance-vs-vortex ; https://urandom.io/blog/2026-05-18-parquet-is-paying-a-cpu-tax-it-cant-afford
- https://startree.ai/blog/a-tale-of-three-real-time-olap-databases ; https://www.tinybird.co/blog/md/best-database-for-olap

**Procesamiento y modelado**
- https://risingwave.com/blog/kafka-streams-vs-risingwave-2026
- https://www.vldb.org/pvldb/vol18/p4846-mei.pdf
- https://spark.apache.org/releases/spark-release-4-0-0.html ; https://apache.googlesource.com/spark/+show/master/docs/streaming/real-time-mode.md
- https://www.instaclustr.com/blog/kafka-4-0-unveiled-key-changes-and-how-they-impact-developers/ ; https://aiven.io/blog/kip-1150-accepted-and-the-road-ahead
- https://confluent.io/blog/ibm-to-acquire-confluent ; https://www.automq.com/blog/warpstream-after-confluent-acquisition-what-changed
- https://www.dremio.com/newsroom/apache-elevates-open-source-projects-gluten-and-polaris-to-top-level-status/ ; https://datalakehousehub.com/blog/datafusion-comet-1-spark-iceberg
- https://www.vaultspeed.com/blog/a-robust-foundation-for-data-products ; https://datavidhya.com/learn/data-modeling-and-warehouse/modern-approaches/data-vault/
- https://www.snowflake.com/en/blog/open-semantic-interchanges-specs-finalized/ ; https://ossie.apache.org/ ; https://cube.dev/articles/dbt-semantic-layer-alternatives-2026
- https://www.arxiv.org/pdf/2411.07763

**Calidad, gobernanza y seguridad**
- https://docs.databricks.com/aws/en/security/privacy/gdpr-delta
- https://www.dremio.com/subsurface/apache-iceberg-and-the-right-to-be-forgotten/ ; https://datalakehousehub.com/blog/gdpr-hard-deletes-on-iceberg ; https://docs.aws.amazon.com/prescriptive-guidance/latest/apache-iceberg-on-aws/table-spec-v3.html
- https://iapp.org/news/a/edpb-weighs-in-on-key-questions-on-personal-data-in-ai-models ; https://cms.law/en/bel/legal-updates/edpb-opinion-28-2024-key-takeaways-on-processing-personal-data-in-the-context-of-ai-models
- https://bitol.io/bitol-announces-odcs-v3-1-0-stronger-smarter-and-stricter/ ; https://docs.datahub.com/docs/generated/ingestion/sources/odcs ; https://barc.com/research/data-products-contracts-2026/ ; https://aaltodoc.aalto.fi/items/9643d2ad-40ad-4cdb-a12d-792695ec30c1
- https://aws.amazon.com/blogs/big-data/build-write-audit-publish-pattern-with-apache-iceberg-branching-and-aws-glue-data-quality/ ; https://community.cloudera.com/t5/Developer-Blogs/Iceberg-WAP-Failsafe-ETL-with-Iceberg-and-CDE/m-p/413008
- https://www.dataexpert.io/blog/soda-vs-great-expectations-data-quality-tools ; https://medium.com/@aidelearning/data-observability-in-2026-monte-carlo-vs-great-expectations-vs-soda-a-data-engineers-honest-7c8cab1b68f1 ; https://datadrivendaily.com/data-observability-tools-compared-a-guide-for-2026/
- https://www.adaltas.com/en/2024/02/19/openlineage-introduction/
- https://daily.dev/posts/openmetadata-vs-datahub-vs-amundsen-vs-commercial-2026--upeyjiiqu.md ; https://pdpspectra.com/blog/data-catalog-datahub-vs-atlan-vs-collibra
- https://www.traverssmith.com/knowledge/knowledge-container/the-data-acts-changes-to-cloud-services-contracts-tipping-the-scales-on-switching/ ; https://www.cooley.com/news/insight/2025/2025-09-08-paas-iaas-or-saas-be-aware-new-switching-rules-will-become-applicable-in-eu
- https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/ ; https://datamatters.sidley.com/2026/06/22/eu-lawmakers-reach-provisional-agreement-to-delay-key-eu-ai-act-obligations/

**Plataformas, ecosistema y tendencias**
- https://www.techtarget.com/data-technologies/news/366631950/Mooncake-acquisition-boosts-Databricks-database-capabilities
- https://www.techcrunch.com/2025/06/02/snowflake-to-acquire-database-startup-crunchy-data/
- https://www.flexera.com/blog/perspectives/databricks-data-ai-summit-2026-recap-genie-one-ltap-lakehouse-rt-and-every-major-launche/ ; https://www.revefi.com/blog/key-takeaways-snowflake-summit-2026 ; https://nand-research.com/google-cloud-next-2026-enterprise-ai-enters-production/
- https://blog.fabric.microsoft.com/en-au/blog/whats-new-in-onelake-and-the-fabric-platform-more-sources-security-and-capacity-tooling
- https://aws.amazon.com/blogs/big-data/aws-analytics-at-reinvent-2025-unifying-data-ai-and-governance-at-scale
- https://press.aboutamazon.com/aws/2026/1/aws-launches-aws-european-sovereign-cloud-and-announces-expansion-across-europe
- https://mattturck.com/mad2024/
- https://joereis.substack.com/p/the-2026-state-of-data-engineering ; https://joereis.substack.com/p/ai-is-here-but-the-hard-parts-havent
- https://www.getdbt.com/resources/state-of-analytics-engineering-2026-download
- https://www.pointfive.co/knowledge-base/inefficient-snowpipe-usage-due-to-small-file-ingestion ; https://www.revefi.com/blog/avoiding-snowflake-data-cost-pitfalls ; https://xebia.com/blog/databricks-finops-optimization-strategies/
- https://www.thoughtworks.com/content/dam/thoughtworks/documents/radar/2026/04/tr_technology_radar_vol_34_en.pdf
