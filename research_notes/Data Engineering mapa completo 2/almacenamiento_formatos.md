# Formatos de tabla abiertos, catálogos, formatos de fichero, operaciones y motores/warehouses (estado a oct-2026, verificación con fuentes primarias)

Nota metodológica: ~60 llamadas search/fetch. WebFetch usa un resumidor pequeño: las cifras se citan tal como las devolvió; donde la página llegó truncada o el resumen es inconsistente, se indica. Las fechas de GitHub Releases salen sin año en el resumen (se deduce 2026 por contexto: marcado "[año inferido]"). Lo no verificable va en Gaps. Hoy = 2026-10-12.

## 1. Iceberg v3: capacidades exactas, estado oficial y GA por motor (resolver afirmaciones contradictorias)

### Takeaway
La spec v3 está adoptada (v1–v3 adoptadas; v4 "en desarrollo activo, no adoptada formalmente"). Lo "contradictorio" de la pasada previa se explica por mezclar tres cosas: spec cerrada (2025), soporte en la librería Java (1.10.0, sep-2025) y GA por producto, que varía mucho: Snowflake GA (7-may-2026); AWS (Glue/EMR/S3 Tables, Spark) anunciado nov-2025 solo para deletion vectors y row lineage; Databricks Public Preview; BigQuery/Lakehouse Preview; Trino "experimental" sin DML; Athena NO soporta v3 según AWS.

### Cited Findings
- Contenido de v3 según la spec: tipos nuevos (timestamp nanosegundos con/sin zona, unknown, variant, geometry, geography), valores por defecto de columna, transformaciones multi-argumento para partición/orden, row lineage, deletion vectors binarios y claves de cifrado de tabla. v2 añadió deletes a nivel de fila, números de secuencia, etc. — [Iceberg spec](https://iceberg.apache.org/spec/) (leído vía raw [spec.md](https://raw.githubusercontent.com/apache/iceberg/main/format/spec.md)).
- Spec: v4 "en desarrollo activo y no formalmente adoptada"; esbozo v4: rutas relativas, `location` opcional (lo da el catálogo), métricas en struct tipado `content_stats`, ya no se permite escribir nuevos equality deletes — [spec.md](https://raw.githubusercontent.com/apache/iceberg/main/format/spec.md).
- Propuestas v4 presentadas en Iceberg Summit 2026: árboles de metadatos adaptativos con commits de un fichero, rutas relativas, column families, estadísticas extensibles; el artículo no dice que estén adoptadas — [Snowflake Engineering](https://www.snowflake.com/en/blog/engineering/iceberg-summit-2026-recap-v4-spec/) (blog de proveedor, sin primaria ASF).
- Versiones Java: 1.12.0 (30 sep [año inferido 2026], "Latest"; REST: endpoint unregister-table; lectores ORC de row lineage; variant shredded en Flink; trabajo v4: manifests Parquet/Avro en V4, relativización de rutas); 1.11.0 (20 may [2026]; cifrado de manifest list, Flink 2.1, lectores Flink de row lineage); 1.10.0 (11 sep [2025]) — [GitHub releases](https://github.com/apache/iceberg/releases) ; [releases index](https://iceberg.apache.org/releases/).
- 1.10.0 descrito como la versión que lleva v3 a "GA" y spec v3 "cerrada" — [Google Open Source Blog](https://opensource.googleblog.com/2025/09/apache-iceberg-110-maturing-the-v3-spec-the-rest-api-and-google-contributions.html) y [Dremio](https://www.dremio.com/blog/whats-new-in-apache-iceberg-1-10-0-and-what-comes-next/) (resultados de búsqueda; no se leyó la nota oficial de release 1.10.0 — secundario/vendor).
- Snowflake: v3 GA el 7-may-2026; soporta geography, geometry, nanosegundos, variant, unknown, defaults, deletion vectors, row lineage; NO soporta transformaciones multi-argumento ni claves de cifrado de tabla; default sigue siendo v2 (`ICEBERG_VERSION = 3`); sin upgrade in-place v2→v3; lectura externa de tablas v3 gestionadas vía Horizon Iceberg REST es GA, escritura externa no — [release note](https://docs.snowflake.com/en/release-notes/2026/other/2026-05-07-iceberg-v3-ga), [docs v3](https://docs.snowflake.com/en/user-guide/tables-iceberg-v3-specification-support) (la página de docs en sí no declara GA; la fuente del GA es la release note vía snippet de búsqueda).
- AWS: anuncio 26-nov-2025 de deletion vectors y row lineage v3 en EMR Spark 7.12+, Glue, SageMaker Unified Studio notebooks, S3 Tables y Glue Data Catalog (incl. Iceberg REST y table maintenance); Athena (Trino) = "No"; upgrade v2→v3 sin reescribir datos y de un solo sentido; requiere merge-on-read para DVs; sin backfill histórico de row lineage — [AWS What's New](https://aws.amazon.com/about-aws/whats-new/2025/11/aws-apache-iceberg-v3-deletion-vectors-row-lineage), [AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/apache-iceberg-on-aws/table-spec-v3.html). Nota: el soporte AWS es solo DV + row lineage (no variant/geo documentados en esa tabla) y "con Apache Spark".
- Databricks: v3 en Public Preview, requiere DBR 18.0+/18 LTS; DVs, VARIANT, row lineage (obligatorio en v3); no soporta initial defaults, tipo unknown, timestamps de nanosegundos ni transformaciones multi-argumento; upgrade irreversible — [Databricks docs](https://docs.databricks.com/aws/en/iceberg/iceberg-v3) (la página no declara explícitamente "preview"; el estado "Public Preview" viene de snippet de búsqueda; una página Azure decía Beta en DBR 17.3 — conflicto, preferir la más nueva).
- BigQuery / "Lakehouse for Apache Iceberg" (antes BigLake): V3 con Binary Deletion Vectors en Preview (11-jun-2026); escrituras DML/DDL de BigQuery sobre Iceberg en runtime catalog en Preview (25-jun-2026); sin entrada GA de v3 en las notas — [Release notes Google](https://docs.cloud.google.com/lakehouse/docs/release-notes), [doc BDV](https://docs.cloud.google.com/lakehouse/docs/use-iceberg-v3-binary-deletion-vectors).
- Trino 483 (docs): "Iceberg spec v1 y v2; el soporte de format version 3 es experimental"; UPDATE/DELETE/OPTIMIZE no soportados en v3; sin defaults ni cifrado; VARIANT solo en v3 — [Trino docs](https://trino.io/docs/current/connector/iceberg.html). Starburst (distribución comercial) afirma soporte v3 en 476-e — [Starburst](https://www.starburst.io/blog/iceberg-v3/) (vendor; contradice parcialmente al upstream).
- Spark y Flink: el soporte v3 se menciona en notas Iceberg (Flink readers de row lineage en 1.11; variant shredded en Flink 1.12), pero las páginas de docs de Spark/Flink recuperadas llegaron truncadas y no confirmaron estado — ver Gaps.
- REST Catalog spec: OpenAPI 3.1.1, `info.version` 0.0.1; endpoints config, namespaces, tables (create/register/rename/staged), scan planning (`/plan`, `/tasks`), `transactions/commit`, funciones, `idempotency-key` (lifetime ej. PT30M); OAuth2 `/oauth/tokens` deprecado y a eliminar en Java 2.0 — [rest-catalog-open-api.yaml](https://github.com/apache/iceberg/blob/main/open-api/rest-catalog-open-api.yaml) (parte truncada: vistas y credential vending no confirmados).

### Inferences
- Tabla de verdad práctica de "GA v3 por motor" (oct-2026): GA claro = Snowflake (con salvedades), Spark/Glue/EMR/S3 Tables (para DV+lineage; AWS usa el término "support", no etiqueta "GA" en las páginas leídas). Preview = Databricks, BigQuery. Experimental/parcial = Trino upstream, Athena no. Flink/Spark OSS: soporte en lib Java desde 1.10–1.12 pero sin verificar matriz.
- Un solo motor sin v3 (Athena) en el camino de lectura bloquea el upgrade, porque es unidireccional: cualquier lector no-v3 rompe.
- Resolución de la contradicción: "v3 ratificada mediados 2025 / GA mediados 2026" mezcla spec (cerrada ~sep-2025 con 1.10.0) y GA de Snowflake (may-2026).

### Gaps
- Nota oficial de release de Iceberg 1.10.0 y matriz oficial de Spark/Flink para v3 no obtenidas (páginas truncadas).
- Estado GA de Dremio, Redshift, Fabric, Glue como "GA" explícito no verificado más allá de la página AWS.
- Credential vending/views en la spec REST no confirmados (truncado).

## 2. Delta Lake: protocolo, 4.x, UniForm, catalog-managed, DVs, liquid clustering; verificación "Delta 5.0"

### Takeaway
No existe Delta 5.0: la última es 4.4.1 (5 oct [2026]); 4.3.0 (18 jun) y 4.4.0 (20 ago) integran la UC Delta API. La afirmación de "Delta 5.0" de la pasada previa queda REFUTADA (ausencia en delta.io y GitHub).

### Cited Findings
- Releases: 4.4.1 (5 oct; evita mantenimiento automático arriesgado en tablas catalog-managed, arregla snapshots incorrectos con S3A fast listing); 4.4.0 (20 ago; Spark 4.2, UC Delta API en Kernel y Flink, identity columns en DDL); 4.3.0 (18 jun; UC Delta REST API, UniForm Iceberg atómico e incremental); 4.2.0 (16 abr; Variant GA, geospatial y collations en Kernel, conector Flink experimental); 4.1.0 (26 feb; Spark 4.1, catalog-managed en preview, habilitar DV/column mapping sin conflictos); 4.0.1 (16 ene; renombra `catalogOwned-preview`→`catalogManaged`, breaking); 4.0.0 (blog del 25-sep-2025: Delta Connect, catalog-managed preview, Variant) — [GitHub releases](https://github.com/delta-io/delta/releases), [delta.io/blog](https://delta.io/blog/). Anomalía: el resumen mostraba 4.0.0 con "09 Jun", incompatible con el blog del 25-sep-2025; fecha de GitHub no fiable aquí. Ninguna fuente muestra 5.0.
- Protocolo: reader v3/writer v7 con table features; `deletionVectors`, `columnMapping`, `v2Checkpoint`, `domainMetadata`, `changeDataFeed`, `icebergCompatV1/V2/V3`, `catalogManaged` (el catálogo es fuente de verdad de qué commit tuvo éxito; exige in-commit timestamps y no admite acceso solo por filesystem), Clustered Table (`clusteringProvider` p.ej. "liquid"), Row Tracking, Variant — [PROTOCOL.md](https://raw.githubusercontent.com/delta-io/delta/master/PROTOCOL.md) (mitad truncada; mecánica Hilbert/z-order de clustering NO confirmada).
- Catalog-managed commits (blog 2-feb-2026) hacen de Unity Catalog fuente de verdad del estado de tabla — [delta.io blog](https://delta.io/blog/); UC Delta API: "superficie REST versionada, intent-based, atómica" en Unity Catalog 0.5 (blog 3-jul-2026) — mismo listado.
- UniForm: genera metadatos Iceberg/Hudi de forma asíncrona tras cada commit Delta con una sola copia de datos; clientes Iceberg/Hudi son solo-lectura; no compatible con DV (docs doc) — [docs.delta.io UniForm](https://docs.delta.io/latest/delta-uniform.html). Conflicto/obsolescencia: esa página exige Hive Metastore y dice incompatible con DV, mientras que `REORG ... UPGRADE UNIFORM` y `icebergCompat` posteriores y la nota 4.3.0 (conversión atómica incremental) sugieren evolución; tratar la página como posiblemente desfasada.
- Liquid clustering (Databricks): sustituye particionado y ZORDER, no combinable con ellos; hasta 4 claves; claves cambiables sin reescribir; `CLUSTER BY AUTO` con predictive optimization (UC managed, DBR 15.4+); convertir tablas con `REPLACE PARTITIONED BY WITH CLUSTER BY` (DBR 18.1+); en Iceberg gestionado: Public Preview en DBR 16.4+ — [Databricks docs](https://docs.databricks.com/aws/en/delta/clustering).
- Unity Catalog OSS: 0.6.0 (20 ago; sube Iceberg a 1.11.0, vistas SQL, métricas, tokens con expiración 24 h por defecto, ruptura), 0.5.0 (18 jun; UC Delta API), 0.4.x (feb–abr; credenciales AWS, Variant, fix CVE-2026-27478) — [GitHub releases](https://github.com/unitycatalog/unitycatalog/releases). Donación a LF (2024): no confirmada en esta pasada.
- DuckDB: extensiones Delta y UC salen de experimental (6-may-2026); Delta Kernel Rust integrado en ClickHouse (18-may-2026) — [delta.io/blog](https://delta.io/blog/).

### Inferences
- Delta converge hacia "catálogo coordina commits" (catalogManaged), igual que Iceberg v4 (`location` suministrada por catálogo, commits de un fichero): ambos mueven el punto de verdad al catálogo.
- 4.4.1 (arreglo de S3A listing y staged commits no ratificados) indica que catalog-managed sigue madurando en producción.

### Gaps
- Mecánica interna de liquid clustering OSS (Delta) y estado GA de catalog-managed OSS (4.1 decía "preview"): sin primaria posterior.
- Protocolo de `icebergCompatV3` y row tracking: sección truncada.

## 3. Hudi 1.x, Paimon, DuckLake y diferencias documentadas entre formatos; señales de adopción

### Takeaway
Cada formato optimiza un caso: Iceberg (interoperabilidad/snapshots, árbol de metadatos), Delta (log transaccional + catalog-managed), Hudi (upserts por clave, indexación, table services), Paimon (LSM para streaming Flink), DuckLake (metadatos en BD SQL). Las métricas de adopción real son débiles/no verificadas.

### Cited Findings
- Hudi 1.0.0 (dic-2024): table version 8, non-blocking concurrency control, índice secundario — [Hudi blog](https://hudi.apache.org/blog/2024/12/16/announcing-hudi-1-0-0). Hudi 1.1.1: framework de table format enchufable, Spark 4.0/Flink 2.0, record index particionado, lock provider basado en storage, payloads deprecados por merge modes — [release 1.1](https://hudi.apache.org/releases/release-1.1). Hudi 1.2.0/1.2.1: tipos VECTOR/VARIANT/BLOB, lectura/escritura de formato Lance (solo Spark), Record-Level Index en Flink, lock provider Azure, table version 9 — [release 1.2](https://hudi.apache.org/releases/release-1.2) (sin fecha en la página).
- Paimon: "Data Lake Platform" batch+streaming+IA multimodal; 2.0 marcada stable, 2.2-SNAPSHOT master; tablas PK con LSM, merge engines y changelog producers; integraciones StarRocks, Doris, Hive, Trino, Presto — [Paimon docs](https://paimon.apache.org/docs/master/). Concurrencia: OCC con snapshots atómicos; conflicto de snapshot → reintento; conflicto de ficheros en compactación → rechazo; en object stores sin rename atómico se necesita creación condicional o lock (Hive/JDBC); recomienda `write-only=true` en escritores y job de compactación dedicado — [Paimon concurrency control](https://paimon.apache.org/docs/master/concepts/concurrency-control/).
- DuckLake 1.0 (13-abr-2026): metadatos en PostgreSQL/MySQL/SQLite/DuckDB, datos en Parquet, MIT, compatibilidad hacia atrás garantizada, transacciones multi-tabla — [ducklake.select](https://ducklake.select/), [duckdb.org news](https://duckdb.org/news/) (confirma "DuckLake v1.0 ... Reaches Production-Readiness", 2026-04-13). Fecha CONFIRMADA.
- Comparación académica: CIDR 2023 "Analyzing and Comparing Lakehouse Storage Systems" (LHBench, TPC-DS en EMR): Hudi casi 10x más lento en carga masiva porque se optimiza para upserts por clave — [CIDR 2023](https://vldb.org/cidrdb/2023/analyzing-and-comparing-lakehouse-storage-systems.html), [LHBench](https://lhbench.cs.berkeley.edu/). Es de 2023 (versiones antiguas); autores vinculados a Databricks (Zaharia, Das) — sesgo potencial. Otro: LST-Bench (SIGMOD 2024, Microsoft) — [Microsoft Research](https://www.microsoft.com/en-us/research/publication/lst-bench-benchmarking-log-structured-tables-in-the-cloud/).
- Layout de metadatos (documentado): Iceberg = metadata.json → manifest list → manifests → data/delete files, con Puffin para stats/DV; Delta = `_delta_log` (JSON + checkpoints, v2Checkpoint con sidecars); Paimon = snapshots/manifests + LSM por bucket; DuckLake = tablas SQL — [Iceberg spec](https://iceberg.apache.org/spec/), [Delta PROTOCOL](https://raw.githubusercontent.com/delta-io/delta/master/PROTOCOL.md), [Paimon docs](https://paimon.apache.org/docs/master/), [DuckLake](https://ducklake.select/) (Hudi timeline/metadata table: no re-leído).
- Señal de adopción (débil): "Iceberg ganó, importa el catálogo" — [Cloudmagazin](https://www.cloudmagazin.com/fr/2026/07/01/iceberg-a-remporte-la-guerre-des-formats-maintenant-cest-le-catalogue-qui-compte/), [AM Data Lakehouse](https://amdatalakehouse.substack.com/p/lakehouse-table-formats-in-2026-iceberg) (autor ligado a Dremio, sesgo). Señal más sólida: todos los grandes proveedores analizados (Snowflake, AWS, Google, Databricks, Starburst) publican soporte v3 de Iceberg; Hudi 1.2 añade Lance; Delta añade UniForm hacia Iceberg.

### Inferences
- MoR/CoW: Iceberg v3 (DV, MoR) y Delta (DV) convergen en deletion vectors; Hudi (MoR/CoW nativo, record index) y Paimon (LSM) siguen siendo más fuertes para upserts de alta tasa por clave y streaming, a costa de menos motores. [MoR/CoW de Hudi no re-verificado en esta pasada.]
- Concurrencia: Iceberg/Delta OCC a nivel de tabla con conflicto en commit; Hudi 1.0 NBCC y Paimon OCC con compactación dedicada reducen conflictos en streaming multi-escritor.

### Gaps
- Cuota de mercado/adopción con datos duros (descargas, encuestas): no encontrada con fuente primaria.
- Benchmarks independientes actuales (2025–26) entre formatos: no hallados; LHBench es de 2023.
- Streaming ingestion de Iceberg (Flink sink) y detalles MoR/CoW de Hudi no verificados con docs.

## 4. Catálogos: Polaris, Unity (OSS/Databricks), Glue/S3 Tables/Lake Formation, Lakekeeper, Nessie, Gravitino, Snowflake Horizon/Open Catalog, BigLake

### Takeaway
Verificado: Polaris es TLP (19-feb-2026); Gravitino es TLP (3-jun-2025); XTable sigue incubating; Lakekeeper no es ASF (mantenido por Vakamo); Nessie sin señales de abandono en su web. El catálogo se convierte en eje de gobierno y de commits.

### Cited Findings
- Apache Polaris: graduado a TLP; blog fechado 19-feb-2026 (no prueba la fecha del voto de la junta); implementación vendor-neutral de Iceberg REST; motores nombrados: Dremio, Snowflake, Spark, Trino, Flink — [Polaris blog](https://polaris.apache.org/blog/2026/02/19/apache-polaris-graduates-to-top-level-project/). Fecha CONFIRMADA como publicación.
- Snowflake Open Catalog = servicio gestionado de Polaris; Snowflake recomienda Horizon Catalog a nuevos clientes y ya no permite crear la primera cuenta Open Catalog; gratis durante GA con facturación por requests REST prevista para 1S-2026 (estado actual de cobro no verificado); credential vending por defecto — [Snowflake docs](https://docs.snowflake.com/en/user-guide/opencatalog/overview).
- Apache Gravitino: TLP anunciado por la ASF el 3-jun-2025 (entró a incubación jun-2024), 1.0.0 en 2025; docs 1.3.1 enlazadas en el sitio — [Gravitino blog (búsqueda)](https://gravitino.apache.org/blog/gravitino-top-level-project), [ASF news](https://news.apache.org/foundation/entry/the-apache-software-foundation-announces-two-new-top-level-projects), [sitio](https://gravitino.apache.org/).
- Lakekeeper: catálogo REST Iceberg en Rust, Apache-2.0, basado en iceberg-rust; credential vending y remote signing (S3, ADLS, OneLake, GCS), autorización OpenFGA (Cedar solo en edición comercial "Plus"), Postgres, OIDC; mantenido por Vakamo; no es proyecto ASF — [GitHub](https://github.com/lakekeeper/lakekeeper) (no se obtuvo versión).
- Nessie: control de versiones "inspirado en Git", Iceberg REST, docs hasta 0.109.0, sin marca de deprecación en la página — [projectnessie.org](https://projectnessie.org/) (sin fechas; no se verificó el nivel de actividad ni si Dremio sigue invirtiendo).
- XTable: ASF incubating (antes OneTable); traduce metadatos entre Hudi, Delta e Iceberg (no es formato nuevo); Paimon solo como ejemplo futuro; sin versión en la página — [xtable.apache.org](https://xtable.apache.org/).
- Unity Catalog OSS: ver sección 2; Databricks Unity Catalog añade Iceberg gestionado (v3 en preview) y liquid clustering — [Databricks docs](https://docs.databricks.com/aws/en/iceberg/iceberg-v3).
- AWS: Glue Data Catalog expone Iceberg REST y table maintenance con v3; S3 Tables hace mantenimiento automático por defecto (compactación, gestión de snapshots a nivel tabla; eliminación de ficheros no referenciados a nivel bucket) y permite expiración de registros — [S3 Tables maintenance](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables-maintenance-overview.html), [AWS PG](https://docs.aws.amazon.com/prescriptive-guidance/latest/apache-iceberg-on-aws/table-spec-v3.html). Lake Formation: NO investigado en profundidad (ver Gaps).
- Google: BigQuery tables for Apache Iceberg (antes "BigLake tables for Apache Iceberg"): datos en buckets del cliente; compactación, clustering, GC y refresco de metadatos facturados como cómputo DCU; consultas con precio on-demand o slots; sin renombrar/clonar/snapshots/MV/RLS — [BigQuery docs](https://docs.cloud.google.com/bigquery/docs/iceberg-tables). Renombre a "Lakehouse for Apache Iceberg" visible en [release notes](https://docs.cloud.google.com/lakehouse/docs/release-notes). BigLake metastore como tal: no verificado.
- Snowflake–Fabric/OneLake bidireccional GA (30-ene-2026) — [Snowflake release notes](https://docs.snowflake.com/release-notes/2026/other/2026-01-30-iceberg-microsoft-fabric-bidirectional-data-access-ga).

### Inferences
- Polaris (Snowflake/Dremio), Unity (Databricks, UC Delta API) y Glue/S3 Tables (AWS) compiten por ser el catálogo REST de referencia; Lakekeeper y Gravitino cubren el segmento self-hosted/federado.
- El hecho de que Snowflake restrinja nuevas cuentas Open Catalog a favor de Horizon sugiere priorizar su catálogo propietario sobre Polaris gestionado (inferencia a partir de la doc).

### Gaps
- Lake Formation, Horizon Catalog detallado, versiones de Lakekeeper y Nessie, pertenencia de Unity Catalog OSS a LF AI & Data: sin fuente primaria obtenida.

## 5. Formatos de fichero: Parquet, ORC, Avro, Arrow, Lance, Vortex, Nimble

### Takeaway
Parquet evoluciona activamente en 2026 (Variant, geoespacial, ALP, estadísticas float). Lance y Vortex son alternativas con claims de proveedor sin validación independiente; Lance ya entra en Hudi 1.2.

### Cited Findings
- Parquet 2026: Variant (blog 27-feb), tipos geoespaciales nativos (13-feb), estadísticas float con orden total IEEE 754 y conteo de NaN (29-may), parquet-format 2.13.0 (13-jun), 2.14.0 (11-sep: INT96 ordenado cronológicamente, tipo lógico FILE, codificación ALP), blog ALP 22-sep ("compresión cercana a zstd, descompresión más rápida"), parquet-java 1.17.0 (13-ene), 1.18.0 (11-ago), 1.18.1 (4-ago, orden de la página) — [Parquet blog](https://parquet.apache.org/blog/). Page index y bloom filters: no cubiertos por esa página (ver Gaps).
- Vortex: "Incubating", "a Series of LF Projects, LLC", donado por Spiral; claims "100x acceso aleatorio, 10–20x scans, 5x escrituras" sin metodología en la página — [vortex.dev](https://vortex.dev/). Afiliación LF AI & Data NO confirmada.
- Lance: Apache-2.0, formato de fichero + tabla + spec de catálogo para IA multimodal; búsqueda vectorial/FTS/SQL; claim 100x acceso aleatorio vs Parquet; descrito en paper VLDB 2025; integra Spark, Ray, Trino, DuckDB y catálogos Polaris/UC/Gravitino/HMS — [lance.org](https://lance.org/). Hudi 1.2 lee/escribe Lance (Spark) — [Hudi 1.2](https://hudi.apache.org/releases/release-1.2).
- Contrapunto de escepticismo sobre sustituir Parquet — [urandom.io](https://urandom.io/blog/2026-05-18-parquet-is-paying-a-cpu-tax-it-cant-afford) (blog personal, no re-leído en esta pasada).

### Inferences
- Parquet seguirá siendo el contenedor por defecto de Iceberg/Delta/Hudi/DuckLake; la ventaja de ALP, Variant y geo es sobre todo de compresión y semi-estructurado, sin cambiar el modelo de tablas. [Inferido]

### Gaps
- ORC, Avro, Arrow, Nimble: sin fuente primaria en esta pasada (solo conocimiento previo, no citable). Page index, bloom filters y nuevas encodings de Parquet (más allá de ALP) sin verificar.
- Benchmarks independientes de Vortex/Lance: no hallados.

## 6. Operación: runbook (compactación, expiración, huérfanos, manifests), particionado vs clustering, concurrencia, automatización y costes

### Takeaway
Programar: compactación (según tasa de commits), expiración de snapshots (regular), eliminación de huérfanos (menos frecuente, con retención > duración de la escritura más larga), rewrite de manifests solo si el patrón de escritura no coincide con el de lectura. Los servicios gestionados (S3 Tables, Glue, BigQuery) facturan este mantenimiento.

### Cited Findings
- Mantenimiento Iceberg (docs oficiales): recomendado = expirar snapshots, eliminar metadata antigua (`write.metadata.delete-after-commit.enabled`, por defecto false; `previous-versions-max` 100), borrar huérfanos (retención por defecto 3 días; intervalo corto puede corromper la tabla; comparación por strings de ruta; operación lenta con muchos ficheros); opcional = `rewriteDataFiles`, `rewriteManifests`, reescribir position deletes, `removeDanglingDeleteFiles`, estadísticas NDV/particiones (Puffin); docs no dan guía sobre concurrencia con escritores más allá de la retención de huérfanos — [Iceberg maintenance (raw)](https://raw.githubusercontent.com/apache/iceberg/main/docs/docs/maintenance.md).
- Partition evolution: cambio de spec solo metadatos; datos viejos conservan layout; se planifica por spec; hidden partitioning; evolución de schema sin reescribir (IDs de columna) y de sort order — [Iceberg evolution (raw)](https://raw.githubusercontent.com/apache/iceberg/main/docs/docs/evolution.md).
- Clustering vs partición: ver liquid clustering en sección 2 (Databricks); en Iceberg gestionado por UC las columnas de partición externas se traducen a claves de clustering y se descartan bucket transforms — [Databricks docs](https://docs.databricks.com/aws/en/delta/clustering).
- S3 conditional writes: `If-None-Match` (solo `*`) e `If-Match` (ETag) en PutObject/CopyObject/CompleteMultipartUpload; 412 si falla la precondición; 409 en deletes concurrentes; el primero en terminar gana; requiere SigV4 — [AWS S3 docs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html). Anuncios de ago/nov-2024 (sin coste extra) en [AWS](https://aws.amazon.com/about-aws/whats-new/2024/08/amazon-s3-conditional-writes), [AWS nov](https://aws.amazon.com/about-aws/whats-new/2024/11/amazon-s3-functionality-conditional-writes) (de la pasada previa; no re-leídos).
- Paimon en S3: necesita creación condicional o lock; recomienda compactación dedicada — [Paimon](https://paimon.apache.org/docs/master/concepts/concurrency-control/).
- Costes: S3 Tables $0.0265/GB-mes (primeros 50 TB), PUT $0.005/1000, GET $0.0004/1000, monitorización $0.025/1000 objetos, compactación $0.002/1000 objetos + $0.005/GB — [AWS S3 pricing](https://aws.amazon.com/s3/pricing/) (región no indicada en el resumen; la rebaja del 90% de jul-2025 está en [AWS What's New](https://aws.amazon.com/about-aws/whats-new/2025/07/amazon-s3-tables-reduce-compaction-costs), no re-leída). Glue: optimización de tablas Iceberg $0.44/DPU-hora (facturación por segundo, mínimo 1 min); catálogo 1M objetos y 1M requests gratis, luego $1/100k objetos-mes — [AWS Glue pricing](https://aws.amazon.com/glue/pricing/) (precios de snapshot retention/huérfanos no listados por separado). BigQuery Iceberg: mantenimiento facturado como DCU — [BigQuery docs](https://docs.cloud.google.com/bigquery/docs/iceberg-tables).
- Delta: 4.4.1 evita mantenimiento automático arriesgado en tablas catalog-managed — [GitHub releases](https://github.com/delta-io/delta/releases).
- UniForm/Iceberg v3: tras upgrade v2→v3 ejecutar compactación para consolidar delete files; DVs requieren merge-on-read — [AWS PG](https://docs.aws.amazon.com/prescriptive-guidance/latest/apache-iceberg-on-aws/table-spec-v3.html).

### Inferences
- Runbook propuesto (no citado, criterio de ingeniería): compactación continua o por micro-lotes en tablas de streaming y diaria en batch con objetivo ~256–512 MB (AWS PG menciona 512 MB en su ejemplo); expire_snapshots diario/semanal acorde a la ventana de time travel; huérfanos semanal/mensual con retención ≥ 3 días; rewrite_manifests ocasional; stats NDV tras cargas grandes; monitorizar tamaño medio de ficheros vía tabla `files` (AWS PG lo sugiere).
- Metadata growth es el límite de la tasa de commits: motivación de v4 (commits de un fichero) y de DuckLake (metadatos en SQL).

### Gaps
- Costes reales comparados (Glue vs S3 Tables) solo hay una anécdota de blog (pasada previa); sin benchmark neutral.
- Guía oficial de ejecutar mantenimiento concurrente con escritores en Iceberg: no encontrada.
- Delta VACUUM/OPTIMIZE docs y Hudi table services (cleaning/clustering) no leídos.

## 7. OLAP/serving y warehouses: arquitectura y modelos de precio oficiales

### Takeaway
Precios oficiales verificados: Snowflake (créditos), Redshift, ClickHouse Cloud, MotherDuck. BigQuery y Fabric NO se pudieron verificar desde la página oficial (renderizado/truncado). Sin benchmark independiente fiable.

### Cited Findings
- Snowflake (tabla oficial de consumo): crédito on-demand AWS US East (N. Virginia) = $2.00 Standard / $3.00 Enterprise / $4.00 Business Critical / $6.00 VPS; Europa Dublín/Frankfurt $2.60/$3.90/$5.20; almacenamiento estándar on-demand $23/TB-mes en US East, desde $13.80 con capacidad (tiers por ACV) — [Credit Consumption Table (PDF)](https://www.snowflake.com/legal-files/CreditConsumptionTable.pdf) (leído con pdftotext). Modelo: cómputo y almacenamiento facturados por separado; ediciones — [Snowflake pricing](https://www.snowflake.com/en/pricing-options/).
- Redshift (us-east-1 N. Virginia): Serverless $0.375/RPU-hora; ra3.4xlarge $3.26/h (ejemplo); managed storage $0.024/GB-mes; Spectrum $5/TB escaneado — [AWS Redshift pricing](https://aws.amazon.com/redshift/pricing/).
- ClickHouse Cloud: planes Basic/Scale/Enterprise; compute unit = 8 GiB RAM + 2 vCPU; Enterprise AWS us-east-1 $0.39030 por unidad-hora y $25.30/TB-mes almacenamiento; cómputo por minuto, escala a cero; $300 en créditos — [ClickHouse pricing](https://clickhouse.com/pricing).
- MotherDuck: Lite $0; Business $250/org-mes + uso; Pulse $0.60/CU-hora, Standard $2.40/h, Jumbo $4.80/h; almacenamiento $0.04/GB-mes comprimido — [MotherDuck pricing](https://motherduck.com/product/pricing/).
- BigQuery: página oficial no recuperable; búsqueda indica on-demand $6.25/TiB con 1 TiB gratis y slot-hora PAYG $0.06 (Enterprise, con compromisos a $0.054/$0.048), mientras otra copia daba $0.04 — conflicto — [BigQuery pricing](https://cloud.google.com/bigquery/pricing) (valores de snippet de búsqueda, NO verificados en la página). El fetch directo devolvió cifras de memoria del modelo, descartadas.
- Fabric: reservas 1–3 años ahorran ~41% frente a pay-as-you-go; SKUs F2–F8192; la página mostró "$-" en los precios; OneLake con capas hot/cool/cold — [Azure Fabric pricing](https://azure.microsoft.com/en-us/pricing/details/microsoft-fabric/). Synapse dedicated pools→Fabric Warehouse: no verificado.
- Pinot 1.5.1: OLAP real-time con ingestión Kafka/Pulsar/Kinesis y upserts desde 0.6, multi-tenant; la página no menciona Iceberg/Delta — [pinot.apache.org](https://pinot.apache.org/). ClickHouse: Delta Kernel Rust integrado (mayo-2026) — [delta.io](https://delta.io/blog/). StarRocks/Doris/Druid: sin fuente primaria (el fetch de StarRocks devolvió 404).
- DuckDB: 1.5.x hasta 1.5.6 (28-sep-2026); preview de v2.0 el 17-ago-2026 con protocolo "Quack" y lecturas/escrituras concurrentes multiproceso — [duckdb.org/news](https://duckdb.org/news/), [AWS/DuckLabs](https://duckdb.org/2026/08/26/ducklabs-to-join-aws).
- Verificación DuckDB Labs/AWS: CONFIRMADA por fuente primaria. El 26-ago-2026 DuckLabs anunció que se une a AWS como subsidiaria; cierre esperado a principios de sept-2026; términos no divulgados; DuckDB, DuckLake, Quack y extensiones siguen MIT bajo la DuckDB Foundation, con un stakeholder advisory board — [duckdb.org](https://duckdb.org/2026/08/26/ducklabs-to-join-aws); cobertura corroborante: [SiliconANGLE](https://siliconangle.com/2026/08/26/aws-buys-ducklabs-to-bring-duckdbs-embeddable-analytics-to-more-enterprises/), [Channel Insider](https://www.channelinsider.com/channel-business/news-aws-acquires-ducklabs-duckdb/). Detalle: la entidad se llama "DuckLabs B.V.", no "DuckDB Labs". Cifras de descargas divergen entre fuentes (1M/día vs >3M).

### Inferences
- Comparativa de coste (derivable, no medida): warehouse = cómputo (crédito/RPU/slot) + almacenamiento propio ($23/TB-mes Snowflake, $24/TB Redshift RMS, $25.30 ClickHouse) frente a lakehouse = S3 (~$0.023/GB-mes; precio S3 Standard no recuperado en esta pasada) + cómputo elegido + mantenimiento (Glue $0.44/DPU-h; S3 Tables compactación). El almacenamiento es parecido; la diferencia está en cómputo, mantenimiento y egress.
- Para "serving" de baja latencia y alta concurrencia (Pinot/ClickHouse/StarRocks) vs "warehouse" para BI ad-hoc: la elección es por patrón de consulta; sin benchmark neutral no hay ranking defendible.

### Gaps
- Precios oficiales de BigQuery y Fabric, y S3 Standard: no verificados.
- Arquitectura y docs oficiales de Druid, Doris, StarRocks: no obtenidos.
- Benchmarks independientes warehouse vs lakehouse (patrocinio): no se encontró ninguno fiable en esta pasada; los de proveedores (TPC-DS) no se usaron.
- Verificaciones solicitadas: Delta 5.0 = no existe (sección 2); Polaris TLP = confirmado 19-feb-2026 (sección 4); DuckLake 1.0 = 13-abr-2026 confirmado (sección 3); DuckDB/AWS = confirmado (sección 7).
