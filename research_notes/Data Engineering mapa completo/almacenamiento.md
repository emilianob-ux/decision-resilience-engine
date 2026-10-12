# Capas y formatos de almacenamiento de datos (estado a oct-2026)

Nota metodológica: ~11 llamadas de búsqueda/fetch. Casi todas las fuentes son blogs de proveedores o agregadores; los hallazgos "Cited" llevan enlace y sesgo señalado. Lo marcado "[conocimiento previo]" proviene del entrenamiento del autor, NO fue verificado en esta sesión y está en Inferences/Gaps para que el redactor lo trate como no citado. Un fetch de duckdb.org/history devolvió una afirmación incoherente (dijo que DuckDB v1.0.0 es "la última versión"), lo que sugiere que el resumidor de WebFetch es poco fiable; las fechas de ese fetch deben verificarse.

## 1. Guerra de formatos Iceberg vs Delta vs Hudi vs Paimon (2025-2026) y convergencia de catálogos

### Takeaway
Narrativa dominante en 2026: Iceberg ganó como formato de interoperabilidad y la disputa se desplazó al catálogo (Polaris TLP, REST catalog, Unity). Delta sigue evolucionando (catalog-managed tables, Variant GA) y Hudi/Paimon quedan como nichos (upserts/streaming). Gran parte de la evidencia es de blogs de proveedores.

### Cited Findings
- Visión 2026: la industria se ha asentado mayoritariamente en Iceberg para interoperabilidad; todas las nubes grandes ofrecen Iceberg gestionado; Snowflake y Databricks lo leen/escriben nativamente; los formatos nunca se fusionaron del todo — [Substack AM Data Lakehouse](https://amdatalakehouse.substack.com/p/lakehouse-table-formats-in-2026-iceberg) (autor afiliado a Dremio; sesgo pro-Iceberg). Titular afín "Iceberg ganó la guerra de formatos, ahora importa el catálogo" — [Cloudmagazin](https://www.cloudmagazin.com/fr/2026/07/01/iceberg-a-remporte-la-guerre-des-formats-maintenant-cest-le-catalogue-qui-compte/).
- Iceberg v3: añade deletion vectors, tipo variant, row lineage y tipos geoespaciales (releases 1.10–1.11 hasta mayo 2026); las fuentes discrepan sobre fecha (ratificado mediados 2025 vs GA mediados 2026). Snowflake habría declarado v3 GA en mayo 2026, Databricks en Public Preview, S3 Tables también lo soporta — [Cloudmagazin](https://www.cloudmagazin.com/fr/2026/07/01/iceberg-a-remporte-la-guerre-des-formats-maintenant-cest-le-catalogue-qui-compte/), [Iceberg Lakehouse blog](https://iceberglakehouse.com/posts/table-formats-2026-breakdown/). Última versión Java de Iceberg vista en docs: 1.12.0 — [iceberg.apache.org](https://iceberg.apache.org/spec/).
- Iceberg v4 (en diseño, no ratificado a jul-ago 2026): adaptive metadata tree, commits de un solo fichero, stats de contenido, rutas relativas; punto abierto: partition tuple y updates por columna — [Snowflake, Iceberg Summit 2026](https://www.snowflake.com/en/blog/engineering/iceberg-summit-2026-recap-v4-spec/), [Estado v4 jul-2026](https://datalakehousehub.com/blog/iceberg-v4-state-july-2026/). Afirmación de que Databricks propondría Delta 5.0 con la misma estructura: sin corroboración (no usar como hecho).
- Databricks anunció la compra de Tabular (creadores de Iceberg: Ryan Blue, Daniel Weeks, Jason Reid) el 4-jun-2024; plan: UniForm a corto plazo, estándar común a largo (años) — [Databricks PR](https://www.databricks.com/company/newsroom/press-releases/databricks-agrees-acquire-tabular-company-founded-original-creators), [Blocks&Files](https://blocksandfiles.com/2024/06/05/databricks-buys-tabular-to-win-the-iceberg-war/).
- Delta: 4.0 (sep-2025) con catalog-managed tables en preview y Variant; catalog-managed tables formalizadas en 4.1.0; Variant GA en 4.2; la 4.4.0 añade soporte Spark 4.2 y mayor integración con UC Delta API — [delta.io 4.0](https://delta.io/blog/2025-09-25-delta-lake-40/), [Delta 4.2.0](https://github.com/delta-io/delta/releases/tag/v4.2.0), [Delta 4.4.0](https://newreleases.io/project/github/delta-io/delta/release/v4.4.0), [Delta Kernel + UC Delta APIs (ago-2026)](https://delta.io/blog/2026-08-20-simplifying-your-open-lakehouse-with-the-delta-kernel-and-the-uc-delta-apis).
- Leer Delta desde Trino/Dremio/Snowflake pasa por capas de compatibilidad (UniForm, manifests) funcionales pero "de segunda clase" — [Substack AM](https://amdatalakehouse.substack.com/p/lakehouse-table-formats-in-2026-iceberg) (sesgo).
- Hudi 1.0.0 (dic-2024): table version 8, non-blocking concurrency control, secondary index, lectura/escritura en v6 y upgrade automático — [Hudi blog](https://hudi.apache.org/blog/2024/12/16/announcing-hudi-1-0-0). Hudi se describe centrado en upserts incrementales rápidos; Paimon nació en Flink/Alibaba (2022) como tabla con semántica de streaming — [tech-insider](https://tech-insider.org/apache-iceberg-vs-delta-lake-vs-hudi-2026/) (fuente débil).
- Apache Polaris (co-creado por Snowflake y Dremio, donado a ASF ago-2024) se graduó a TLP el 19-feb-2026; implementación vendor-neutral de la Iceberg REST Catalog spec; ~100 contribuidores, 6 releases en incubación; Polaris 1.4 en abril 2026 (multi-tenancy) — [Polaris blog](https://polaris.apache.org/blog/2026/02/19/apache-polaris-graduates-to-top-level-project/), [Fivetran](https://www.fivetran.com/blog/the-impact-of-apache-polaris-graduating-to-top-level-apache-project), [Snowflake](https://www.snowflake.com/en/engineering-blog/apache-polaris-1-4-release/).
- DuckLake 1.0 (13-abr-2026): metadatos en base SQL en vez de ficheros en object storage, extensión DuckDB, small updates en catálogo, sorting/partitioning mejorado — [duckdb.org/history](https://duckdb.org/history), [InfoQ vía búsqueda](https://thenote.app/post/en/ducklake-1-0-data-lake-format-with-sql-catalog-metadata-g2l2rkqece).
- Interop Snowflake-Fabric/OneLake bidireccional Iceberg GA (30-ene-2026) — [Snowflake release notes](https://docs.snowflake.com/release-notes/2026/other/2026-01-30-iceberg-microsoft-fabric-bidirectional-data-access-ga).

### Inferences
- "Iceberg ganó" es cierto en cuanto a lectura multi-motor y soporte de proveedores, pero Delta mantiene la mayor base instalada en Databricks; la convergencia real es Iceberg REST + catálogo gestionado (Unity/Polaris/Glue/S3 Tables) con Delta/UniForm como puente.
- El catálogo es el nuevo punto de control/lock-in (gobierno, credential vending, commits coordinados); Delta catalog-managed commits e Iceberg v4 apuntan a convergir en "el catálogo coordina commits".
- DuckLake es una contra-tesis (metadatos en SQL ACID) que ataca el problema de metadata/small files, pero con ecosistema aún pequeño.

### Gaps
- No se obtuvieron fuentes primarias sobre Paimon 1.x ni cuota de mercado real (cifras de adopción). Estado actual de Nessie, Lakekeeper, XTable (Apache incubating) y Unity Catalog OSS: sin resultados verificables. [conocimiento previo, no verificado: Lakekeeper = catálogo REST Iceberg en Rust; Nessie = catálogo con versionado tipo Git; XTable = traducción de metadatos entre Iceberg/Delta/Hudi sin reescribir datos; Unity Catalog OSS donado a LF en 2024; Glue soporta Iceberg REST endpoint.]
- Ratificación exacta de Iceberg v3 y el estado de soporte por motor requieren verificar en spec/release notes oficiales.

## 2. Warehouse vs lakehouse: decisión y modelo de costes

### Takeaway
Las fronteras se difuminan: los warehouses (Snowflake, BigQuery, Fabric) leen/escriben Iceberg en almacenamiento del cliente y los lakehouses añaden gobierno y SQL. Decide por cargas, gobierno, madurez del equipo y coste de mantenimiento, no por el formato.

### Cited Findings
- Snowflake y Microsoft Fabric/OneLake: tablas Iceberg gestionadas por Snowflake almacenadas en OneLake, una sola copia, GA ene-2026 — [Fabric blog](https://blog.fabric.microsoft.com/en-us/blog/microsoft-onelake-and-snowflake-interoperability-is-now-generally-available?ft=All).
- BigLake for Iceberg (BigQuery) con datos en buckets del cliente: reportado como GA solo por agregador — [checkthat.ai](https://checkthat.ai/answers/what-are-the-best-data-lake-solutions) (baja fiabilidad; verificar).
- Coste S3 Tables: desde 1-jul-2025 los fees de compactación bajaron hasta 90% (por objeto -50%; por byte -90% binpack, -80% sort/z-order); estrategias binpack/sort/z-order — [AWS What's New](https://aws.amazon.com/about-aws/whats-new/2025/07/amazon-s3-tables-reduce-compaction-costs). Anécdota de un blog: mantenimiento en 7 días, Glue $1.32 (549 ficheros) vs S3 Tables $0.0875 (74 ficheros); una sola carga, no generalizable — [Medium/dataengineerthings](https://blog.dataengineerthings.org/amazon-s3-tables-vs-the-glue-optimizer-glue-cost-me-15x-more-in-iceberg-maintenance-b27a6c52beb0).

### Inferences
- Modelo de coste: warehouse = cómputo+almacenamiento acoplado/gestionado, mantenimiento incluido, opaco; lakehouse = almacenamiento barato en objeto + cómputo elegido + coste oculto de operar mantenimiento (compactación, expiración, catálogo) y requests/egress.
- Regla práctica: warehouse para BI/SQL con equipo pequeño; lakehouse para multi-motor, ML/streaming, volumen grande, evitar lock-in; híbrido Iceberg compartido es el patrón en alza.

### Gaps
- Sin datos verificados de precios actuales de Snowflake, BigQuery, Redshift, Synapse/Fabric ni benchmarks neutrales (TPC-DS de proveedor tienen sesgo). Nada específico sobre Redshift 2026. [conocimiento previo, no verificado: Synapse dedicated pools en transición hacia Fabric Warehouse; BigQuery cobra por bytes escaneados u slots; Redshift Serverless por RPU.]

## 3. Operativa: small files, compactación, metadata, snapshots, GC, ACID en object stores

### Takeaway
El coste real del lakehouse es el mantenimiento. Las primitivas de ACID en S3 maduraron (conditional writes), los servicios gestionados (S3 Tables) automatizan compactación, y Iceberg v4/DuckLake atacan el crecimiento de metadatos.

### Cited Findings
- S3 soporta conditional writes (If-None-Match, If-Match con ETag), sin coste extra, en todas las regiones (ago y nov 2024) — [AWS](https://aws.amazon.com/about-aws/whats-new/2024/08/amazon-s3-conditional-writes), [AWS nov-2024](https://aws.amazon.com/about-aws/whats-new/2024/11/amazon-s3-functionality-conditional-writes).
- Motivación de Iceberg v4: cada commit reescribe varios artefactos (dos escalan con la tabla); commits de un fichero para escrituras de baja latencia — [Snowflake](https://www.snowflake.com/en/blog/engineering/iceberg-summit-2026-recap-v4-spec/).
- Hudi 1.0 NBCC permite múltiples escritores de streaming sin resolución de conflictos — [Hudi](https://hudi.apache.org/blog/2024/12/16/announcing-hudi-1-0-0).
- Compactación gestionada (S3 Tables) y estrategias sort/z-order — ver sección 2.

### Inferences
- [Con base en práctica común, no citado] Checklist: compactación periódica (binpack, objetivo ~128-512 MB), sort/z-order o liquid clustering según patrón, expire_snapshots, remove_orphan_files, rewrite_manifests, límites de retención para time travel, y vigilar la tasa de commits por tabla en streaming.
- Deletion vectors (Iceberg v3, Delta) reducen coste de escrituras de update/delete frente a copy-on-write.

### Gaps
- Sin fuentes sobre liquid clustering de Databricks, partition evolution/hidden partitioning, ni detalles de GC en esta sesión. [conocimiento previo: Delta liquid clustering reemplaza particionado+ZORDER; Iceberg tiene partition evolution; VACUUM en Delta, remove_orphan_files en Iceberg.]

## 4. Formatos de fichero: Parquet, ORC, Avro, Arrow, Lance, Vortex

### Takeaway
Parquet sigue siendo el estándar de facto; Vortex y Lance atacan acceso aleatorio, GPU y cargas de IA/multimodales, con cifras de proveedores aún sin validación independiente.

### Cited Findings
- Vortex: columnar extensible, separa tipos lógicos de layout físico, interoperable zero-copy con Arrow, compresión en cascada basada en BtrBlocks; donado a LF AI & Data (ago-2025 según una fuente; la web del proyecto cita "LF Projects, LLC") — [Zilliz FAQ](https://zilliz.com/ai-faq/vortex-file-format), [vortex.dev](https://vortex.dev).
- Cifras del proyecto: 100x lectura aleatoria y 10-20x scans vs Parquet; benchmark de Zilliz independiente-ish: ~2.4x en full scan y menos tráfico S3 — [Zilliz Lance vs Vortex](https://zilliz.com/ai-faq/lance-vs-vortex). Contrapunto: "Parquet no está muerto" — [urandom.io](https://urandom.io/blog/2026-05-18-parquet-is-paying-a-cpu-tax-it-cant-afford).
- Lance: proyecto independiente orientado a IA/vectores; a fines de 2025 se evaluaba donación a una fundación — [Zilliz](https://zilliz.com/ai-faq/lance-vs-vortex).

### Inferences
- [Conocimiento previo] Parquet (analítica columnar, estándar), ORC (ecosistema Hive), Avro (fila, streaming/schema registry), Arrow (memoria/IPC/Flight, no persistencia primaria). Para tablas Iceberg/Delta lo pragmático es Parquet; Lance/Vortex para vector/multimodal o acceso aleatorio, con riesgo de madurez/ecosistema.

### Gaps
- Sin fuente para ORC/Avro/Arrow/Parquet v2-nuevas encodings; foundation exacta de Vortex y Lance sin confirmar; sin benchmarks independientes.

## 5. Motores OLAP y embebido (ClickHouse, Druid, Pinot, StarRocks, DuckDB/MotherDuck) y vector/feature stores

### Takeaway
Pinot: servir a usuarios con alta concurrencia; Druid: streaming/series temporales; StarRocks: joins/BI y lakehouse; ClickHouse: propósito general rápido. DuckDB cubre el nodo único/embebido y con DuckLake empuja a lakehouse ligero.

### Cited Findings
- Segmentación anterior de OLAP; ClickHouse con joins mejorados (reordenación, runtime filters, spill) pero prefiere esquemas desnormalizados; StarRocks soporta Iceberg/Hive nativamente y protocolo MySQL; Pinot con star-tree index para <100 ms a alta QPS; Druid integra Iceberg/Delta — [StarTree](https://startree.ai/blog/a-tale-of-three-real-time-olap-databases), [Tinybird](https://www.tinybird.co/blog/md/best-database-for-olap), [Estuary](https://estuary.dev/blog/real-time-olap-databases/). Fuentes con conflicto de interés (competidores); no se hallaron benchmarks neutrales de Iceberg 2026.
- DuckDB 1.0 en jun-2024 (estabilidad) — [duckdb.org](https://duckdb.org/2024/06/03/announcing-duckdb-100). DuckLake 1.0 abr-2026 (ver sección 1). Afirmación de que DuckDB Labs se une a AWS (26-ago-2026) proviene de una sola página resumida por WebFetch poco fiable: NO verificada.

### Inferences
- DuckDB: ETL/exploración local, CI, datos de hasta cientos de GB-pocos TB en un nodo, lector de Parquet/Iceberg en S3; MotherDuck añade el modelo híbrido. No para alta concurrencia multiusuario de escritura.

### Gaps
- Sin fuentes sobre MotherDuck, ni vector stores/feature stores (Lance, pgvector, Feast, etc.) en esta sesión; sin madurez/estándares formales (Parquet/Arrow son estándares de facto; Iceberg REST es spec abierta). Requiere búsqueda adicional.
