# Ingesta, orquestación y transformación de datos: verificación con fuentes primarias (estado a 12-oct-2026)

Método: ~42 búsquedas/fetch. "Primaria" = docs/blog/comunicado del propio vendor o proyecto. Los resúmenes de WebFetch vienen de un modelo pequeño: las cifras puntuales (fechas, versiones) deben re-verificarse antes de publicar. Lo marcado [INFERENCIA] es mío, no de una fuente. Lo que no encontré está en Gaps.

## 1. Verificación de afirmaciones de M&A y licencias

### Takeaway
Confirmadas con fuente primaria: Fivetran adquirió Tobiko (3 sep 2025), la fusión Fivetran–dbt Labs se anunció el 13 oct 2025 y cerró el 1 jun 2026, SQLMesh fue contribuido a la Linux Foundation (25 mar 2026), y dbt Core v2 alpha (1 jun 2026) open-sourcea el runtime Fusion bajo Apache 2.0. La adquisición de Dagster por Prefect (anuncio 13 jul 2026) está confirmada como anuncio, pero NO se verificó el cierre; la propia FAQ de Dagster dice "cerrará en las próximas semanas". Corrección a notas previas: Schrock sale de la empresa (no "asesor"), y Fusion/dbt v2 sigue en alpha para el Core.

### Cited Findings
- Fivetran anunció la compra de Tobiko Data (SQLMesh y SQLGlot) el 3 sep 2025; sin términos financieros; fue su segunda adquisición de 2025 tras Census — [Business Wire](https://www.businesswire.com/news/home/20250903275106/en/Fivetran-Acquires-Tobiko-Data-to-Power-the-Next-Generation-of-Advanced-AI-Ready-Data-Transformation), [Fivetran press](https://www.fivetran.com/press/fivetran-acquires-tobiko-data-to-power-the-next-generation-of-advanced-ai-ready-data-transformation)
- Comunicado de Fivetran fechado 1 jun 2026: fusión con dbt Labs completada; "all-stock", sin valoración publicada; George Fraser sigue como CEO, Tristan Handy es President; afirma "más de 100.000 equipos de datos" (cifra de marketing); la fusión se anunció el 13 oct 2025 — [Fivetran press](https://www.fivetran.com/press/fivetran-dbt-labs-complete-merger-to-create-the-data-infrastructure-for-trusted-ai-agents). No se encontró el comunicado original de oct 2025 (la URL probada dio 404); la fecha 13 oct 2025 la dan el comunicado de cierre y [Pulse 2.0](https://pulse2.com/fivetran-and-dbt-labs-complete-merger-to-build-trusted-ai-data-infrastructure/amp/). Ambas son compañías privadas: no hay presentación SEC consultable que verifique el cierre.
- El mismo comunicado menciona "dbt State (preview)": capa de caché que construye solo modelos cambiados, con afirmación de vendor de "30% o más" de ahorro de infraestructura; "dbt Wizard (beta)" y "Agents Schema" — [Fivetran press](https://www.fivetran.com/press/fivetran-dbt-labs-complete-merger-to-create-the-data-infrastructure-for-trusted-ai-agents)
- SQLMesh: la Linux Foundation anunció el 25 mar 2026 (KubeCon EU) que aloja SQLMesh, contribuido por Fivetran; gobernanza de comunidad abierta; miembros fundadores Benzinga, CloudKitchens, Harness, Infinite Lambda, Jump AI, Minerva; código sigue en GitHub — [Linux Foundation](https://www.linuxfoundation.org/press/linux-foundation-welcomes-sqlmesh-project) (vía resumen de búsqueda; la página LF no se abrió completa), [Fivetran press](https://www.fivetran.com/press/fivetran-contributes-sqlmesh-to-the-linux-foundation-to-advance-open-data-infrastructure). El repo ahora está en la org `SQLMesh` de GitHub, README: "SQLMesh is a project of the Linux Foundation", licencia Apache 2.0 — [GitHub](https://github.com/TobikoData/sqlmesh) (redirige a SQLMesh/sqlmesh)
- dbt Core v2.0: primer alpha el 1 jun 2026; GA sin fecha ("alpha today"); runtime Rust antes ELv2 ahora Apache 2.0 en repo `dbt-core`; repo `dbt-fusion` archivado; `dbt-fusion-private` retiene código propietario; el binario Fusion es gratuito con algunas features tras login gratuito o cuenta paga; v1.12 (beta en el post) es el paso recomendado previo; migración con `dbt parse --use-v2-parser` y `dbt-autofix`; v1.x sigue disponible — [dbt blog](https://docs.getdbt.com/blog/dbt-core-v2-is-here)
- Tabla de licencias de dbt: Core v1.x Apache 2.0; dbt OSS (subconjunto v2) Apache 2.0; código del motor Apache 2.0; adaptadores y spec Apache 2.0; MetricFlow Apache 2.0 (relicenciado oct 2025, antes BSL); el binario "dbt" completo bajo "dbt Product Licensing Agreement"; extensión VS Code bajo ese acuerdo; plataforma dbt comercial — [dbt licenses FAQ](https://www.getdbt.com/licenses-faq). Esto CONTRADICE la nota previa ("Fusion bajo ELv2, MetricFlow BSL"): ELv2 quedó reemplazada para el binario por un acuerdo propietario, y MetricFlow ya es Apache 2.0.
- dbt State sucede a "state-aware orchestration" (SAO): SAO estaba disponible para Enterprise/Enterprise+ con motor Fusion; los usuarios de SAO antes del 1 jun 2026 pueden seguir; trial de dbt State extendido hasta el 1 sep 2026; dbt State funciona con Core, Fusion, plataforma dbt y orquestadores externos; mecanismo: hash cacheado (código y datos) por modelo, almacenado en Redis; mutuamente excluyente con SAO — [dbt docs, búsqueda](https://docs.getdbt.com/docs/deploy/state-aware-about) (solo snippet de resultados; las páginas SAO se etiquetan Beta/Private preview de forma inconsistente)
- Prefect–Dagster: post de Dagster fechado 13 jul 2026; términos no divulgados; la licencia no se trata; el OSS será "activamente desarrollado, no solo mantenido"; Dagster+ continúa con su marca y contratos; unos 40 empleados de Dagster pasan a Prefect; Nick Schrock deja el proyecto y la empresa — [Dagster blog](https://dagster.io/blog/prefect-is-acquiring-dagster). La FAQ: "esperamos que la transacción cierre en las próximas semanas", sin planes de fusionar Dagster en Prefect, precios y contratos sin cambios, pero el banner de la página dice "Dagster is now part of Prefect" (inconsistencia) — [Dagster FAQ](https://dagster.io/dagster-customer-faq). Intento de leer un post de Prefect: 404 — [Prefect](https://www.prefect.io/blog/prefect-acquires-dagster)
- Opinión (no oficial): la promesa de Apache 2.0 no garantiza inversión de roadmap; las features nuevas pueden aterrizar en Cloud/Fusion — [Nexla](https://nexla.com/blog/open-source-vs-saas-fivetran-dbt-merger/) (vía snippet)

### Inferences
- [INFERENCIA] Para Prefect–Dagster, tratar el cierre como "anunciado, no confirmado cerrado" a oct 2026; el cierre no aparece en ninguna fuente que leí.
- [INFERENCIA] "Fusion GA" de notas previas debe tratarse con cuidado: el Core v2 es alpha; cualquier GA se refiere a la plataforma dbt (no re-verificado en esta pasada).

### Gaps
- Comunicado original de la fusión (oct 2025) y cualquier registro regulatorio: no encontrados (empresas privadas).
- Estado actual (oct 2026) de Core v2: no verifiqué si salió beta/GA tras el alpha de junio.
- Cierre de Prefect–Dagster y comunicado oficial de Prefect: no encontrados.

## 2. Airflow 3.x vs Dagster vs Prefect

### Takeaway
Airflow 3 cerró brechas (versionado, assets, event-driven, backfills en scheduler, SDK por lenguaje) pero conserva más componentes operativos; Dagster tiene el modelo de assets y particiones más maduro; Prefect modela assets de forma ligera y se despliega con work pools/workers. Versiones: Airflow 3.3.2 (17 sep 2026), Dagster 1.13.26 (9 oct 2026).

### Cited Findings
- Release notes oficiales de Airflow: 3.0.0 (2025-04-22; última listada 3.0.6, 2025-08-29): Task SDK/Execution API, Edge Executor, backfills del scheduler, versionado DAG, UI React, `airflow.sdk`. 3.1.0 (2025-09-25; 3.1.8, 2026-03-11): tareas human-in-the-loop, desacople del Task SDK para upgrades independientes, Deadline Alerts, Python 3.13. 3.2.0 (2026-04-07; 3.2.2, 2026-05-29): asset partitioning, despliegues multi-team, callbacks sincrónicos de deadlines, SQLAlchemy 2.0, Python 3.14. 3.3.0 (2026-07-06; 3.3.2, 2026-09-17): más asset partitioning, state store de tareas/assets, retry policies enchufables, Task SDKs Java y Go, bundle versioning al clear/rerun/backfill — [Airflow release notes](https://airflow.apache.org/docs/apache-airflow/stable/release_notes.html) (solo se leyeron los primeros 100k de 516k caracteres)
- AIPs de 3.0 (blog oficial): AIP-38 UI, AIP-65 historial/versionado de DAGs, AIP-66 DAG bundles, AIP-69 Edge Executor, AIP-72 Task Execution Interface, AIP-74/75 assets, AIP-78 backfills del scheduler, AIP-79 FAB fuera del core, AIP-81 CLI vía API (`airflowctl`), AIP-82 scheduling por eventos externos (SQS), AIP-83 elimina unicidad de execution date, AIP-84 API UI FastAPI. El blog no lista breaking changes ni requisitos — [Airflow blog](https://airflow.apache.org/blog/airflow-three-point-oh-is-here/)
- Dynamic task mapping en Airflow: `expand()`/`partial()`, el scheduler crea las copias justo antes de ejecutar; `max_map_length` por defecto 1024; `max_active_tis_per_dag` limita concurrencia; mapa vacío marca la tarea SKIPPED — [Airflow docs](https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/dynamic-task-mapping.html)
- Dagster: releases 1.13.17 (7 ago) a 1.13.26 (9 oct, marcada Latest); la 1.13.26 cambia que `dagster-dbt` ya no instala `dbt-core` por defecto — [Dagster GitHub releases](https://github.com/dagster-io/dagster/releases) (la página no muestra año; inferido 2026). Backfills por partición: por defecto N particiones = N runs; `backfill_policy=single_run` ejecuta el rango en un solo run (el código debe operar sobre rangos) — [Dagster docs](https://dagster.io/docs/guides/build/partitions-and-backfills/backfilling-data)
- Prefect 3: assets identificados por URI, `@materialize`, dependencias inferidas del grafo o `asset_deps`, estado verde/rojo/gris según la última materialización, eventos `prefect.asset.materialization.succeeded/failed` — [Prefect docs](https://docs.prefect.io/v3/concepts/assets). Despliegue: deployments `flow/nombre`, work pools (Docker, K8s, serverless), workers que hacen polling para pools híbridos, push/managed pools sin worker (a cambio de compartir más información con Prefect Cloud), `concurrency_limit` con ENQUEUE o CANCEL_NEW — [Prefect docs](https://docs.prefect.io/v3/concepts/deployments)
- Nubes gestionadas: MWAA ofrece 3.3.1 (disponible 1 sep 2026), 3.2.1, 3.0.6 y 2.11.x; no soporta multi-team; compromete mínimo 3 minor versions y avisa EoS con 180 días — [AWS MWAA](https://docs.aws.amazon.com/mwaa/latest/userguide/airflow-versions.html). Cloud Composer (Gen 3) lista Airflow 3.1, 3.2 y 3.3 con soporte hasta 2027 — [Google Cloud](https://docs.cloud.google.com/composer/docs/composer-versions)
- Airflow Best Practices: tratar tareas como transacciones; usar UPSERT en vez de INSERT; leer una partición específica (data_interval_start), "nunca leer el último dato disponible"; no usar `now()` en cómputo crítico; sin DB/red/cómputo pesado en top-level code; XCom solo para mensajes pequeños; tests de carga de DAG — [Airflow docs](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)

### Inferences
- [INFERENCIA] Operación: Airflow = scheduler + API server + DB + workers (según blog/arquitectura); Prefect ofrece opción sin worker (push/managed) y es el más liviano; Dagster+ pricing por materialización (del blog secundario previo, no re-verificado).
- [INFERENCIA] Con Airflow 3.2/3.3 (partitions, state store) y soporte en MWAA/Composer, el costo de quedarse en Airflow baja; migrar a Dagster se justifica por lineage/particiones nativos, ahora con incertidumbre de propiedad.

### Gaps
- Comparativa primaria de Dagster (Components, freshness, pricing de Dagster+), DAG versioning de Dagster/Prefect, y costos operativos medidos: no hallados. Las afirmaciones de la nota previa basadas en datalakehousehub (freshness GA, Components GA en 1.13, pricing) siguen sin fuente primaria.
- ADF, Databricks Workflows/Lakeflow Jobs, Mage: no investigados con fuente primaria en esta pasada (solo Lakeflow Connect crea un job por schedule de pipeline).

## 3. Argo Workflows, Temporal, Kestra

### Takeaway
Son categorías distintas de Airflow/Dagster: Argo = ejecución de contenedores en Kubernetes; Temporal = ejecución durable de código; Kestra = plataforma declarativa orientada a eventos.

### Cited Findings
- Argo Workflows: motor open source container-native para jobs paralelos en Kubernetes, implementado como CRD; pasos como contenedores en secuencia o DAG; artefactos (S3, GCS, Azure Blob, Git, HTTP); cron workflows; proyecto graduado de CNCF — [Argo docs](https://argo-workflows.readthedocs.io/en/latest/)
- Temporal: la ejecución durable corre hasta completarse pese a caídas; otro Worker reproduce el Event History y retoma en la misma línea; reintentos/backoff/timeouts por configuración; timers durables; ejecuciones ancladas a la versión de código con la que iniciaron — [Temporal docs](https://docs.temporal.io/evaluate/why-temporal). La página no detalla garantías como exactly-once.
- Kestra: plataforma open source de orquestación, declarativa y orientada a eventos; la página de docs lista versión 2.0 y no nombra licencia — [Kestra docs](https://kestra.io/docs)

### Inferences
- [INFERENCIA] Temporal/Argo encajan en lógica de negocio larga y ML/batch contenedorizado respectivamente; no son orquestadores centrados en tablas.

### Gaps
- Mage, benchmarks y adopción: no investigados. Licencia de Kestra y versión exacta: no confirmadas.

## 4. dbt vs SQLMesh (diferencias técnicas) y estrategias incrementales

### Takeaway
SQLMesh usa entornos virtuales (referencias a tablas versionadas por fingerprint) y planes con categorías de cambio; dbt usa `state:modified + --defer` para CI y estrategias incrementales por adaptador, con microbatch (UTC, `lookback`, backfill por `--event-time-*`) como el análogo más cercano a los intervalos de SQLMesh.

### Cited Findings
- SQLMesh planes: diferencia entre estado local y entorno destino (`prod` por defecto); cada cambio crea una variante (snapshot con fingerprint) con tabla física propia; un entorno es un conjunto de referencias; promover a prod suele ser un "Virtual Update" sin cómputo extra si no hay huecos; categorías breaking (backfill del modelo y downstream), non-breaking (solo el modelo) y forward-only (sin backfill, reusa tabla); backfill en dev con `--start/--end`; incremental by unique key y SCD2 no se backfillean en rangos parciales — [SQLMesh plans](https://sqlmesh.readthedocs.io/en/stable/concepts/plans/)
- SQLMesh model kinds: INCREMENTAL_BY_TIME_RANGE (procesa intervalos faltantes, requiere `time_column`, filtra la salida para no pisar registros ajenos, `lookback` para datos tardíos, debe ser idempotente), INCREMENTAL_BY_UNIQUE_KEY (upsert; no detecta duplicados), INCREMENTAL_BY_PARTITION (no idempotente), INCREMENTAL_UNMANAGED, FULL, SCD_TYPE_2_BY_TIME/BY_COLUMN (restatement deshabilitado por defecto por riesgo de pérdida de datos), VIEW (default), SEED, EXTERNAL, MANAGED — [SQLMesh model kinds](https://sqlmesh.readthedocs.io/en/stable/concepts/models/model_kinds/)
- dbt estrategias incrementales: `append` (sin dedup), `merge` (upsert por `unique_key`, `merge_update_columns`, `incremental_predicates` para limitar el escaneo), `delete+insert` (útil si la clave no es única; menos eficiente), `insert_overwrite` (reemplaza particiones), `microbatch`; Databricks y Snowflake muestran las cinco; estrategias custom vía macro `get_incremental_<X>_sql` (no soportadas en BigQuery/Spark) — [dbt docs](https://docs.getdbt.com/docs/build/incremental-strategy)
- dbt microbatch: requiere `event_time`, `begin`, `batch_size` (hour/day/month/year); `lookback` por defecto 1 para datos tardíos; `concurrent_batches`; cada batch es una unidad idempotente; backfill con `dbt run --event-time-start ... --event-time-end ...`; `dbt retry` reprocesa solo batches fallidos; todo se interpreta en UTC; implementación por adaptador (Postgres merge; Redshift/Snowflake delete+insert; BigQuery/Spark insert_overwrite; Databricks replace_where) — [dbt microbatch](https://docs.getdbt.com/docs/build/incremental-microbatch)
- dbt snapshots (SCD2): estrategias `timestamp` (recomendada) y `check`; columnas `dbt_valid_from/to`; `hard_deletes` ignore/invalidate/new_record; ignoran `--full-refresh`; son "batch CDC" que solo captura cambios cuando corren; configuración YAML desde v1.9 — [dbt snapshots](https://docs.getdbt.com/docs/build/snapshots). Kimball Tipo 2: nueva fila por cambio, clave sustituta, columnas fecha efectiva/expiración e indicador de fila vigente — [Kimball Group](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/type-2/)
- Licencias: SQLMesh Apache 2.0 y proyecto de la Linux Foundation ([GitHub](https://github.com/TobikoData/sqlmesh)); dbt Core v1.x y OSS v2 Apache 2.0, binario completo bajo acuerdo propietario ([dbt licenses FAQ](https://www.getdbt.com/licenses-faq))

### Inferences
- [INFERENCIA] Diferencia clave: SQLMesh rastrea intervalos procesados en su estado (no depende de `is_incremental()`); dbt microbatch aproxima esto pero determina batches por reloj y `lookback`, sin estado de intervalos propio (según las docs leídas, que no mencionan un estado de intervalos).
- [INFERENCIA] dbt State (preview) apunta a cerrar la brecha de "no reconstruir lo no cambiado", pero es capa de plataforma/vendor.

### Gaps
- Testing comparado (unit tests de dbt vs `sqlmesh test`), column-level lineage de SQLMesh, Dataform y SQLMesh-con-dbt-project: sin fuente leída. Release/roadmap de SQLMesh tras la donación: no hallados.

## 5. Patrones de diseño: idempotencia, backfills, datos tardíos, SCD

### Takeaway
Las fuentes primarias coinciden: sobrescribir particiones/intervalos determinísticos (no append), no leer "lo último", usar tiempo lógico, y reprocesar con ventana `lookback` para datos tardíos.

### Cited Findings
- Beauchemin, "Functional Data Engineering" (ene 2018): tareas puras que sobrescriben su partición de salida completa; particiones inmutables; sin particiones nativas, usar tablas separadas con vistas o delete+insert por parámetros de la tarea (el DELETE puede ser costoso) — conocido solo vía resumen de búsqueda de [Medium](https://maximebeauchemin.medium.com/functional-data-engineering-a-modern-paradigm-for-batch-data-processing-2327ec32c42a) y [Data Council](https://www.datacouncil.ai/functional-data-engineering-a-set-of-best-practices) (el artículo devolvió 403; no leído completo)
- Airflow: tareas como transacciones, UPSERT, partición por `data_interval_start`, evitar `now()` — [Airflow best practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- dbt: `lookback` (microbatch) y `incremental_predicates` para datos tardíos y escaneos acotados; SCD2 vía snapshots; `merge` es SCD1 (sobrescribe) y no versiona historia — [dbt strategies](https://docs.getdbt.com/docs/build/incremental-strategy), [microbatch](https://docs.getdbt.com/docs/build/incremental-microbatch)
- SQLMesh: lookback por intervalos; restatement parcial solo para time-range — [SQLMesh kinds](https://sqlmesh.readthedocs.io/en/stable/concepts/models/model_kinds/)
- Backfills: Airflow 3 los ejecuta en el scheduler (AIP-78) y 3.3 versiona el bundle al hacer clear/rerun/backfill ([release notes](https://airflow.apache.org/docs/apache-airflow/stable/release_notes.html)); Dagster por partición con `single_run` ([docs](https://dagster.io/docs/guides/build/partitions-and-backfills/backfilling-data))

### Inferences
- [INFERENCIA] Anti-patrones documentados indirectamente: INSERT sin clave en tareas con reintento, `now()` en lógica, trabajo pesado en top-level, XCom con datos grandes, `merge` sin predicado sobre tablas enormes.

### Gaps
- Fundamentals of Data Engineering y Kimball sobre late-arriving facts/SCD híbridos: no leídos. Anti-patrones de DAG más allá de las best practices de Airflow: sin fuente. SLAs: solo se sabe de Deadline Alerts en Airflow 3.1; detalles no leídos.

## 6. Ingesta: Debezium, Airbyte, dlt, Flink CDC, Openflow, Lakeflow Connect

### Takeaway
Versiones verificadas: Debezium 3.7.0.Final (29 sep 2026), dlt 1.31.0 (7 oct 2026), Flink CDC docs 3.7.0. Airbyte: plataforma 2.0 (14 oct 2025) y 2.1 (3 abr 2026, solo vía snippet); no pude confirmar versión más reciente.

### Cited Findings
- Debezium 3.7.0.Final el 29 sep 2026: conectores incubating TiDB, Milvus, SQLite; CockroachDB sale de incubating; CLI oficial; Platform con alertas y OIDC; PyDebeziumAI; mejoras Oracle/MySQL/Postgres/MongoDB; JDBC sink con DLQ; breaking: se elimina Oracle 12 continuous mining y Cassandra 3. 3.6.3.Final el 18 sep 2026 (mantenimiento) — [Debezium releases](https://debezium.io/releases/), [3.7 post](https://debezium.io/blog/2026/09/29/debezium-3-7-final-released/), [blog](https://debezium.io/blog/). Esto REEMPLAZA la nota previa (3.6.2/3.7 Alpha, de un agregador).
- dlt 1.31.0, 7 oct 2026, Apache 2.0 — [PyPI](https://pypi.org/project/dlt/)
- Airbyte: 2.0 liberada el 14 oct 2025 (índice de GitHub); 2.1 el 3 abr 2026 según release notes self-managed (leído solo vía snippet de búsqueda) — [Airbyte release notes](https://docs.airbyte.com/release_notes/self-managed). Análisis de roadmap de terceros, no oficial: [Ksolves](https://www.ksolves.com/blog/big-data/airbyte-roadmap)
- Flink CDC: herramienta de integración de datos en tiempo real/batch con YAML; docs v3.7.0; conectores pipeline (MySQL, Oracle, Postgres, SQL Server, Paimon, Fluss, Kafka, Doris, StarRocks, Iceberg, Hudi…) — [Flink CDC docs](https://nightlies.apache.org/flink/flink-cdc-docs-stable/)
- Snowflake Openflow: construido sobre Apache NiFi; conectores son flow definitions de NiFi versionados; BYOC GA en AWS y despliegue SPCS GA en AWS y Azure según la página de producto; fechas GA no confirmadas — [Snowflake docs/producto vía búsqueda](https://docs.snowflake.com/en/user-guide/data-integration/openflow/connectors/about-openflow-connectors)
- Databricks Lakeflow Connect: conectores CDC (MySQL, PostgreSQL, SQL Server), SaaS (Salesforce, HubSpot, Workday…), archivos (Google Drive, SharePoint), basados en consulta y streaming; estados de lanzamiento variados por conector; los pipelines se crean como job por schedule; gateway y staging en conectores de BD — [Databricks docs](https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/)
- Databricks "Declarative Automation Bundles" (antes Databricks Asset Bundles): proyectos como código en YAML que despliegan Lakeflow Jobs, pipelines, dashboards, etc. como unidad a un target; CLI ≥ v0.218.0; integración con CI/CD — [Databricks docs](https://docs.databricks.com/aws/en/dev-tools/bundles/)

### Inferences
- [INFERENCIA] El renombre de DABs sugiere que material antiguo con el nombre previo está desactualizado.

### Gaps
- Fivetran (pricing MAR, conectores), Kafka Connect, ADF, Terraform providers (Fivetran/Airbyte): no investigados. Airbyte 2.1 y pricing: no confirmados en fuente leída completa. Openflow: fechas GA y precios no verificados.

## 7. CI/CD y testing para datos

### Takeaway
La fuente primaria cubre Slim CI de dbt y la evolución a dbt State; no se cubrieron data diff, blue/green ni Terraform.

### Cited Findings
- Slim CI: `dbt run/test -s state:modified+ --defer --state <artifacts prod>`; `--defer` resuelve refs no modificados hacia producción; selectores `result:error/fail` para reruns; `source_status:fresher+` para reconstruir solo lo afectado por fuentes más frescas; limitar datos en CI según `target.name`; definir `grants` en config — [dbt best practices CI](https://docs.getdbt.com/best-practices/best-practice-workflows)
- dbt State / SAO ver sección 1. SQLMesh: los entornos virtuales permiten promover por intercambio de referencias ([SQLMesh plans](https://sqlmesh.readthedocs.io/en/stable/concepts/plans/))
- Airflow: tratar DAGs como código de producción, tests de carga y unitarios, entorno de staging parametrizado — [Airflow best practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- DABs para IaC en Databricks (ver sección 6)

### Inferences
- [INFERENCIA] El patrón de virtual environments de SQLMesh es el análogo de "blue/green" a nivel de tabla, sin copiar datos cuando no hay cambio de lógica.

### Gaps
- Data diff (Datafold/Recce), clones zero-copy, Terraform/OpenTofu, DataOps como disciplina, OpenLineage en Dagster/dbt/Spark: sin fuente en esta pasada (la nota previa solo cita el provider OpenLineage de Airflow vía Atlan, secundaria).
