# Data pipelines, ingesta y orquestación (estado a oct 2026)

Nota de método: ~15 llamadas de búsqueda/fetch. Los hechos con URL fueron verificados en fuentes (primarias cuando se indica; varias son secundarias/agregadores). Lo marcado "[no verificado / conocimiento previo]" proviene de conocimiento de entrenamiento y NO tiene fuente en esta sesión; el redactor debe tratarlo como hipótesis. Mercado muy volátil: M&A y versiones cambian mes a mes.

## 1. Airflow vs Dagster vs Prefect: trade-offs reales y qué cambió con Airflow 3

### Takeaway
Airflow 3.0 (abr 2025) cerró las brechas históricas (versionado de DAGs, arquitectura Task SDK/API server, assets, backfills en scheduler, UI React), acercándolo al modelo asset-based de Dagster, pero conserva el mayor footprint operativo. Dagster = mejor modelo de assets/lineage/particiones; Prefect = más ligero y flexible para workflows dinámicos. En jul 2026 se anunció que Prefect adquiere Dagster Labs (riesgo de roadmap a vigilar).

### Cited Findings
- Airflow 3.0 salió en abril 2025; introduce Task Execution API + API server separado para ejecución remota y aislamiento de tareas (AIP-72); los autores importan de `airflow.sdk` (@dag, @task, DAG); se planearon SDKs de otros lenguajes, empezando por Go — [Airflow blog](https://airflow.apache.org/blog/airflow-three-point-oh-is-here/), [resumen](https://thedatacanal.substack.com/p/airflow-30-dag-versioning-multi-language)
- DAG versioning (AIP-65/66): cada run termina con la versión con la que empezó; la UI enlaza runs con estructura, código y logs; fue la feature más pedida en la encuesta anual — [Airflow blog](https://airflow.apache.org/blog/airflow-three-point-oh-is-here/)
- Backfills ahora corren dentro del scheduler, lanzables desde UI/API (AIP-78); Datasets pasan a Assets (AIP-74) con sintaxis por decorador (AIP-75); asset watchers para scheduling event-driven, con SQS como ejemplo (AIP-82) — [Airflow blog](https://airflow.apache.org/blog/airflow-three-point-oh-is-here/)
- UI reescrita en React sobre APIs FastAPI (AIP-84); Flask AppBuilder pasa a provider separado (AIP-79); CLI dividida con `airflowctl` (AIP-81); AIP-83 elimina la unicidad de execution date en DAG runs (permite DAGs sin data interval, p.ej. inferencia) — [Airflow blog](https://airflow.apache.org/blog/airflow-three-point-oh-is-here/)
- Edge Executor GA (AIP-69); upgrade requiere Airflow >=2.7 y Python 3.9–3.12 — [resumen búsqueda sobre release notes](https://airflow.apache.org/docs/apache-airflow/3.0.0/release_notes.html)
- A oct 2026 Airflow está en la línea 3.3: asset partitioning llegó en 3.2; un task/asset state store en 3.3 (fuente secundaria, blog de Alex Merced) — [datalakehousehub](https://datalakehousehub.com/blog/orchestration-in-2026/)
- Mismo artículo: Dagster = lineage a nivel tabla, particiones, checks, dbt model->asset; "todo debe encajar en el modelo de assets", reestructurar pipelines existentes toma semanas a meses; freshness policies GA en 2026 y Components GA en Dagster 1.13; pricing hosted pasó a por-materialización en 2026. Prefect 3: `@flow`/`@task`, event stream, automations, assets opcionales vía `@materialize` (2025); el más liviano de operar. Airflow: ecosistema más grande, pero mayor footprint (scheduler, API server, DB, workers, triggerer) — [datalakehousehub](https://datalakehousehub.com/blog/orchestration-in-2026/) (fuente única, sin citas externas: tratar con cautela)
- Prefect anunció el 13 jul 2026 un acuerdo para adquirir Dagster Labs; Dagster/Dagster+ mantienen nombre, licencia OSS y roadmap; Schrock y Hunt pasan a asesores tras el cierre; algunos elementos de Dagster se incorporarán a Prefect; sin precio ni fecha de cierre publicados — [Dagster blog](https://dagster.io/blog/prefect-is-acquiring-dagster), [Dagster FAQ](https://dagster.io/dagster-customer-faq), [Pulse 2.0](https://pulse2.com/prefect-acquiring-dagster-labs/)
- Astronomer (parte interesada) posiciona Dagster como opción para equipos greenfield centrados en dbt, y Airflow con OpenLineage integrado — [Astronomer](https://www.astronomer.io/airflow/astro-vs-dagster/)

### Inferences
- Airflow 3 reduce el principal argumento de migrar a Dagster (assets, event-driven, versionado), pero no cambia el costo operativo; para estacks dbt-céntricos nuevos Dagster sigue siendo más ergonómico. Para orgs con parque Airflow grande, upgrade 2.x->3 suele ser mejor ROI que migrar.
- La consolidación Prefect+Dagster sugiere: no apostar por una migración a Dagster basada solo en roadmap hasta ver 2-3 releases post-cierre; Dagster OSS conserva licencia.
- [no verificado / conocimiento previo] Otras categorías: Argo Workflows (K8s-native, YAML, bueno para ML/batch contenedorizado), Temporal (durable execution, para workflows de larga duración y lógica de negocio, no tablas), cloud-native (MWAA, Cloud Composer, Step Functions, ADF, Databricks Workflows/Lakeflow Jobs). Regla: task-based (Airflow/Prefect) para heterogeneidad y operaciones; asset-based (Dagster, Airflow assets) cuando importa el estado de datos, lineage y backfill por partición; event-driven (SQS/Kafka triggers, Prefect automations) para latencia baja, a costa de observabilidad de dependencias (el artículo de datalakehousehub lo señala igualmente).

### Gaps
- No se verificaron fuentes primarias de release notes de Airflow 3.1/3.2/3.3 ni la lista exacta de breaking changes de 3.0 (remoción de acceso directo a la metadata DB desde tareas, execution_date, SubDAGs): conocimiento previo, no confirmado aquí.
- Sin datos primarios sobre Argo, Temporal, Dagster Components, Prefect 3 releases, ni benchmarks de adopción (encuestas).
- Estado de cierre de la adquisición Prefect-Dagster no confirmado.

## 2. dbt vs SQLMesh; fusión dbt Labs/Fivetran; dbt Fusion engine

### Takeaway
Fivetran compró Tobiko (SQLMesh/SQLGlot) en sep 2025, anunció la fusión con dbt Labs el 13 oct 2025 y la cerró el 1 jun 2026; donó SQLMesh a la Linux Foundation (mar 2026). dbt Core v2 (alpha, jun 2026) abre bajo Apache 2.0 el runtime de Fusion; Fusion CLI/plataforma mantiene ELv2 y código propietario. Fusion es GA en la plataforma dbt para Snowflake; otros adapters en preview.

### Cited Findings
- Fivetran adquirió Tobiko Data (SQLMesh, SQLGlot) el 3 sep 2025 — [Orchestra](https://orchestra.substack.com/p/fivetran-acquires-sqlmesh-consolidation), [DataGravity](https://www.datagravity.dev/p/fivetran-acquires-tobiko-data-to)
- Fusión Fivetran + dbt Labs: all-stock, anunciada 13 oct 2025, completada 1 jun 2026 (comunicado conjunto); George Fraser CEO, Tristan Handy President; "más de 100.000 equipos de datos" (cifra de marketing) — [Fivetran press](https://www.fivetran.com/press/fivetran-dbt-labs-complete-merger-to-create-the-data-infrastructure-for-trusted-ai-agents), [Pulse 2.0](https://pulse2.com/fivetran-and-dbt-labs-complete-merger-to-build-trusted-ai-data-infrastructure/amp/)
- Fivetran donó SQLMesh a la Linux Foundation (mar 2026), gobernanza neutral — [The New Stack](https://thenewstack.io/fivetran-donates-sqlmesh-lf/), [OpenSource For You](https://www.opensourceforu.com/2026/03/sqlmesh-goes-open-source-neutral-to-power-modern-data-stacks/). Opinión escéptica sobre inversión sostenida (canibalización) — [smallbigdata](https://smallbigdata.substack.com/p/sqlmesh-dbt-and-fivetran-whats-next)
- dbt Core v2: primer alpha publicado 1 jun 2026, Apache 2.0; el runtime que estaba bajo ELv2 en Fusion pasó a Apache 2.0; "termina la división de dos motores"; Fusion es binario Rust precompilado con código propietario (linter SQL), algunas features gratis, otras con login o pago; novedades: parse mucho más rápido, spec estricta, artifacts en Parquet consultables con DuckDB, adapters con ADBC/Arrow, instalación sin venv; ruta de migración: dbt v1.12 -> `dbt parse --use-v2-parser`; dbt-autofix; v1.x sigue disponible — [dbt blog](https://docs.getdbt.com/blog/dbt-core-v2-is-here)
- Licencias: Fusion (v2.x) bajo ELv2 (prohíbe ofrecer servicio gestionado competidor); plataforma dbt (Orchestrator, Studio, Canvas, Catalog) propietaria; MetricFlow bajo BSL — [dbt licensing FAQ](https://www.getdbt.com/licenses-faq), [blog de licencia](https://www.getdbt.com/blog/new-code-new-license-understanding-the-new-license-for-the-dbt-fusion-engine)
- Fusion: beta pública 28 may 2025; "dbt v2 está GA para la plataforma dbt" (docs); GA para proyectos en Snowflake, preview en otros adapters; panel de readiness con despliegue por fases; requisitos: resolver deprecaciones, paquetes compatibles, jobs activos en últimos 7 días — [dbt readiness](https://docs.getdbt.com/docs/dbt/dbt-readiness.md), [Fusion releases](https://docs.getdbt.com/docs/fusion/fusion-releases). Builds `2.0.0-preview.212` aún en agosto 2026 (la etiqueta CLI sigue preview)
- Fivetran + dbt mencionan "dbt State" (procesar solo activos cambiados) mostrado en Snowflake Summit 2026 — [Pulse 2.0](https://pulse2.com/fivetran-and-dbt-labs-complete-merger-to-build-trusted-ai-data-infrastructure/amp/) (solo fuente secundaria)

### Inferences
- Contradicción aparente: docs dicen "GA" y versión sigue "preview" -> GA parece referirse al servicio en la plataforma (Snowflake), no al CLI/OSS de todos los adapters. Verificar antes de decidir.
- Riesgo estratégico: el stack T+EL+orquestación (dbt Cloud/Fivetran) se concentra en un vendor; el Core Apache 2.0 y SQLMesh en LF mitigan lock-in, pero features premium (linter, state-aware) quedan detrás de login/pago.
- [no verificado / conocimiento previo] Diferencias dbt vs SQLMesh: SQLMesh tiene virtual data environments, plan/apply con diff de impacto, state propio, column-level lineage nativo, Python models, scheduler incremental por intervalos (menos fragilidad que `is_incremental`), tests unitarios; dbt gana en ecosistema, paquetes, contratación y herramientas. Con SQLMesh en LF y dbt v2 incorporando ideas (state-aware), elegir dbt por defecto; SQLMesh si el dolor es entornos/backfills/incrementales complejos. Dataform (BigQuery/GCP), Spark/Databricks (Lakeflow declarative pipelines) como alternativas por plataforma.

### Gaps
- No hay roadmap/contribuidores post-donación de SQLMesh en fuentes primarias.
- Sin detalle de adapters soportados en dbt v2 ni de qué es "dbt State" en fuente primaria.
- Sin comparativa técnica independiente dbt vs SQLMesh en esta sesión.

## 3. Patrones de diseño: cargas idempotentes, datos tardíos, backfills, incrementales

### Takeaway
No se obtuvieron fuentes citables específicas; sólo las capacidades de plataforma (backfills gestionados en Airflow 3, versionado, particiones en Dagster) están respaldadas. El resto es conocimiento previo.

### Cited Findings
- Airflow 3 mueve backfills al scheduler, con control desde UI/API y diagnóstico — [Airflow blog](https://airflow.apache.org/blog/airflow-three-point-oh-is-here/)
- AIP-83 permite DAG runs sin data interval único; asset partitioning en Airflow 3.2 — [Airflow blog](https://airflow.apache.org/blog/airflow-three-point-oh-is-here/), [datalakehousehub](https://datalakehousehub.com/blog/orchestration-in-2026/)
- Dagster: particiones y asset checks como primitivas de primera clase — [datalakehousehub](https://datalakehousehub.com/blog/orchestration-in-2026/)

### Inferences
- [no verificado / conocimiento previo] Patrones estándar (Fundamentals of Data Engineering, Kimball): (a) idempotencia = overwrite por partición (`INSERT OVERWRITE`/delete+insert por ventana) o MERGE con clave natural; evitar append ciego; (b) tiempos lógicos (data interval) no `now()`; (c) datos tardíos: ventana de reprocesamiento (lookback N días) + watermarks por event time vs. ingestion time, tablas bi-temporales; (d) backfill: particionado por intervalo, concurrencia limitada, escribir a staging y swap, aislar compute del run diario; (e) incremental dbt: `merge`/`insert_overwrite`/microbatch (dbt 1.9+), cuidado con `full_refresh` y schema drift; (f) retries con backoff solo si tarea idempotente; SLAs: alertar por frescura del asset (freshness) más que por duración de task; (g) contratos de datos y tests en el borde (dbt contracts, Great Expectations/Soda).
- Asset-based + particiones reduce el costo cognitivo de backfills frente a task-based con fechas.

### Gaps
- Sin fuentes citables para estos patrones en esta sesión; recomiendo que el redactor los cite a Fundamentals of Data Engineering (Reis & Housley) y docs de dbt (incremental models/microbatch), no verificados aquí.

## 4. Consolidación de herramientas de ingesta 2023-2026 (incl. CDC, ELT gestionado, streaming)

### Takeaway
Consolidación fuerte: Fivetran (Census y Tobiko en 2025, dbt Labs en jun 2026) forma un stack ingest+transform+reverse ETL+lake; plataformas (Databricks Lakeflow Connect, Snowflake) absorben ingesta gestionada; Airbyte (OSS, Iceberg) y dlt (código, Python, amigable a agentes IA) cubren el lado abierto; Debezium domina CDC OSS.

### Cited Findings
- Fivetran compró Census y Tobiko Data en 2025 y completó la fusión con dbt Labs; ofrece ingesta, transformación y data lake gestionado; reputación de mayor cobertura de conectores y mejor CDC en DB operacionales — [datalakehousehub ingestion](https://datalakehousehub.com/blog/lakehouse-ingestion-tools/) (secundaria)
- Airbyte: plataforma OSS de conectores con Iceberg como destino de primera clase; dlt: opción code-first Python, creciente uso con agentes IA; Debezium y Kafka Connect Iceberg sink para CDC/streaming donde batch no encaja — [datalakehousehub ingestion](https://datalakehousehub.com/blog/lakehouse-ingestion-tools/)
- Databricks Lakeflow Connect: conectores gestionados SaaS y DB, gobernados por Unity Catalog, sobre serverless y DLT; mezcla de GA/Preview/Beta (parte contenido de vendor) — [Databricks docs](https://docs.databricks.com/aws/ingestion/lakeflow-connect)
- Debezium: línea 3.6 GA, 3.6.2.Final (sep 2026) con snapshots incrementales en réplicas read-only de PostgreSQL; 3.7.0.Alpha2 (13 ago 2026) con conector TiDB incubating y dead-letter/retry en JDBC sink — [API Evangelist](https://blogs.apievangelist.com/blogs/debezium-2026-09-01-debezium-3-6-2-final-released/), [mentions](https://theconsensus.dev/projects/quarkus/mentions.html) (agregadores generados con IA; confirmar en debezium.io)

### Inferences
- Tendencia: ingesta pasa de producto standalone a feature de plataforma (Databricks, Snowflake Openflow [no verificado]) y a bundle de vendor (Fivetran+dbt). Presión de precios en MAR-based; OSS/código (dlt, Airbyte) para costo y control.
- [no verificado / conocimiento previo] Estándares: OpenLineage (spec de lineage; provider `apache-airflow-providers-openlineage` integrado, ver abajo), formatos abiertos Iceberg/Delta, Debezium como estándar de facto CDC log-based, Kafka/Connect para streaming; criterios CDC: usar cuando necesitas bajo latencia/deletes/histórico; batch incremental por cursor si tolera latencia y la tabla tiene `updated_at` fiable.

### Gaps
- Estado actual de Snowflake Openflow, Airbyte (versión/pricing 2026), dlt (versión, dltHub Cloud), Estuary/Redpanda Connect, Fivetran pricing: no hallados.
- Sin cifras de mercado ni adquisiciones adicionales verificadas (p.ej. otras M&A de 2023-2026).

## 5. Estándares, CI/CD, testing, DataOps, IaC, OpenLineage

### Takeaway
OpenLineage está integrado en Airflow; el resto del material (CI/CD, testing, IaC) quedó sin fuentes y es conocimiento previo.

### Cited Findings
- `apache-airflow-providers-openlineage` viene con Airflow desde 2.7, emite eventos por DAG/tarea con facets de schema, column lineage, calidad y SQL; versión 2.7.2 ajustó compatibilidad con Airflow 3.1.0 (2.7.3 en oct 2025) — [Atlan](https://atlan.com/connect/airflow-openlineage/), [changelog provider](https://airflow.apache.org/docs/apache-airflow-providers-openlineage/2.7.3/commits.html)
- El steering committee de OpenLineage incluye Airflow, Snowflake, dbt, Microsoft (fuente secundaria) — [Atlan](https://atlan.com/know/ai-agent/data-for-ai/airflow-openlineage-for-ai/)
- dbt Core v2 publica artifacts en Parquet y migra con dbt-autofix y `--use-v2-parser` — [dbt blog](https://docs.getdbt.com/blog/dbt-core-v2-is-here)
- dbt platform: slim/readiness basado en jobs recientes; `static_analysis: strict` en desarrollo y `baseline` en deploy — [dbt readiness](https://docs.getdbt.com/docs/dbt/dbt-readiness.md)

### Inferences
- [no verificado / conocimiento previo] CI/CD de datos: entornos efímeros por PR (clones zero-copy Snowflake/Databricks, o virtual environments de SQLMesh), `dbt build --select state:modified+ --defer`, tests unitarios de modelos, data diff (Datafold/Recce), linting (sqlfluff), contratos; IaC: Terraform/OpenTofu/Pulumi para warehouse, conectores (providers de Fivetran/Airbyte), Databricks Asset Bundles; DAG tests en Airflow (DagBag import tests); observabilidad: Monte Carlo/Elementary. Confirmar antes de publicar.

### Gaps
- Sin fuentes sobre CI/CD, IaC, testing de pipelines, DataOps; sin verificación de soporte OpenLineage en Dagster, dbt, Spark, Prefect.
