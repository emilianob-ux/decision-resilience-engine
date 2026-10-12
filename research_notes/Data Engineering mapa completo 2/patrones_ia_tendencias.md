# Data Engineering: patrones avanzados, anti-patrones con incidentes públicos, buenas prácticas, coste/FinOps, IA y tendencias 2023-2026 (estado a oct 2026, verificación primaria)

Nota metodológica: ~43 llamadas de búsqueda/fetch. Se hizo fetch de páginas primarias cuando fue posible (postmortems de GitLab, Datadog, Cloudflare x2, Honeycomb; leaderboards Spider2/BIRD; Thoughtworks Radar; Reis; MAD 2025; docs de Confluent, dbt, BigQuery, microservices.io, Debezium). No logré acceder a: Gartner (403), pgvector.org (503), informe completo dbt 2026 (solo resumen), Iceberg branching (truncado), Delta Sharing docs, informe FinOps Foundation (solo secundarias). Estas lagunas se marcan en "Gaps". Convención: "Inferences" = juicio propio; lo que no está en Cited Findings no está verificado.

## 1. ¿Qué incidentes/post-mortems públicos ilustran los principales modos de fallo y de coste en pipelines de datos?

### Takeaway
Hay post-mortems primarios sólidos para cuatro modos de fallo: (a) backups/restauración nunca probados (GitLab), (b) fail-open + protecciones de sobrecarga sin configurar en pipelines de logs (Cloudflare 2024), (c) cambio de metadatos/permisos que corrompe un artefacto de datos generado y propagado sin validación (Cloudflare 2025), (d) acoplamiento oculto entre regiones y clusters Kafka que degradan sin alerta eficaz (Datadog, Honeycomb). Para sobrecoste (BigQuery SELECT *, Snowflake) solo hay anécdotas de usuarios y contenido de vendors, no post-mortems formales de empresas; el único caso con números de ingeniería es Mixmax.

### Cited Findings
**Durabilidad / backups**
- GitLab (31-ene-2017): ~18 h de indisponibilidad; un ingeniero borró el directorio de datos del primario en lugar del secundario (~300 GB). Todos los mecanismos de backup fallaron: pg_dump 9.2 contra una BD 9.6 (bucket S3 vacío), alertas por email rechazadas por falta de DMARC, sin snapshots Azure en los servidores de BD, LVM snapshots no pensados para DR. Se perdieron ~5.000 proyectos, ~5.000 comentarios y ~700 cuentas (estimaciones). Lecciones: asignar propiedad de la durabilidad y probar restauraciones; alertas de backup en Prometheus; WAL archiving/PITR; la restauración tardó ~18 h por discos lentos (~60 Mbps) de staging — [GitLab postmortem](https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/)

**Pipeline de logs / telemetría**
- Cloudflare (14-nov-2024): ~3,5 h y ~55 % de los logs destinados a clientes se perdieron. Un bug en la generación de configuración produjo una config vacía para Logfwdr; se revirtió en <5 min, pero activó un failsafe "fail open" (diseñado cuando el tráfico era mucho menor) que intentó enviar logs de todos los clientes; Buftee pasó de ~1 M a ~40 M de buffers y, al no tener configuradas sus protecciones de sobrecarga, quedó inoperativo. Causas de fondo: el camino fail-open no se probaba a nivel de sistema y las protecciones de Buftee nunca se habilitaron. Remediación: alertas, arreglar el generador de config con tests, y pruebas regulares de sobrecarga en cascada — [Cloudflare](https://blog.cloudflare.com/cloudflare-incident-on-november-14-2024-resulting-in-lost-logs/)
- Cloudflare (18-nov-2025): un cambio de permisos en ClickHouse (11:05 UTC) hizo que la query que genera el "feature file" de Bot Management devolviera columnas duplicadas de la BD `r0` (la query no filtraba por nombre de base de datos). El fichero se duplicó, superó el límite de 200 features (se usaban ~60) y los proxies entraron en pánico → HTTP 5xx; se generaba cada 5 min y fue intermitente al inicio. Resuelto a las 14:30 (impacto principal) y 17:06 (total). Remediación: tratar ficheros de config generados internamente como input no confiable, kill switches globales — [Cloudflare](https://blog.cloudflare.com/18-november-2025-outage/)
- Datadog (8-mar-2023): una actualización automática de systemd (ventana 06:00-07:00 UTC activa en un canal de seguridad heredado de la imagen base) borró rutas gestionadas por Cilium en múltiples regiones a la vez. Primer servicio principal operativo 16:44 UTC; todo operativo 9-mar 08:58; backfill de datos históricos completado 10-mar 06:25. Lecciones: regiones "autónomas" acopladas indirectamente por la ventana de actualización; prioridad live > histórico; los stores con metadatos por quórum se recuperaron más lento que los shardeados estáticamente — [Datadog](https://www.datadoghq.com/blog/2023-03-08-multiregion-infrastructure-connectivity-issue/)

**Kafka**
- Honeycomb, cluster Kafka EU (5-17-dic-2025, informe preliminar): pérdida crítica de redundancia dejó particiones sin líder; agotamiento de disco, problemas de tiered storage y daño en particiones internas de metadatos; el control plane dejó de aceptar cambios y se migró a un cluster nuevo. Ingesta caída 6 h 23 min el 6-dic; SLOs con ~18 h de retraso; Activity Log perdió datos del 5-dic 20:23 al 9-dic 23:45 UTC; ~0,23 % de datasets no podían ingerir en el pico. Lecciones del propio informe: el ruido de alertas enmascaró el problema (~1,5 h en overload protection sin notarse), consumidores "idle" aparentaban salud, los arreglos de emergencia (desactivar tiered storage) tuvieron efectos inesperados, y ensayar la migración en pre-producción limitó el daño — [Honeycomb status](https://status.honeycomb.io/incidents/pjzh0mtqw3vt)
- Coralogix (jul-2019): reasignación de particiones Kafka bloqueó E/S de disco por líder sesgado y parámetro de throttling mal calculado; tras reinicio los brokers rebalancearon continuamente (bug conocido de Kafka 1.0.0); ~10 % de logs procesados durante 6 h, sin pérdida final y con retraso de hasta 1,5 h — solo vía resumen de búsqueda, no leí el original: [resultado de búsqueda sobre Coralogix](https://status.coralogix.com/incidents/b8vc1d0tttt3)

**Coste (BigQuery / Snowflake)**
- HTTP Archive forum: un usuario recibió una factura de ~14.000 USD en 2 h al ejecutar un script Python (los clientes oficiales no muestran el coste como la UI); el mantenedor estimó ~2,5 PB a 6,25 USD/TiB; se añadió advertencia al FAQ; los controles de coste solo pueden imponerse en el proyecto del usuario; no consta si hubo reembolso — [HTTP Archive](https://discuss.httparchive.org/t/warning-14-000-bigquery-charge-in-2-hours/2715)
- Docs oficiales BigQuery: en tablas no clusterizadas LIMIT no reduce los datos leídos; `maximum bytes billed` hace fallar la query sin cargo si la estimación lo supera; dry run estima bytes; cuotas diarias personalizadas por proyecto/usuario — [Google Cloud docs](https://docs.cloud.google.com/bigquery/docs/best-practices-costs); las cuotas se reinician a medianoche hora del Pacífico y no pueden ejecutarse queries sobre la cuota — [Google cost-controls vía búsqueda](https://docs.cloud.google.com/bigquery/cost-controls?authuser=0) (solo snippet)
- Otras anécdotas BigQuery (5.000 USD por una query; 15-18k USD en Solana) provienen de prensa/blogs y se contradicen entre sí en cifras; no hay post-mortem de Google — [searchengineworld](https://www.searchengineworld.com/when-a-single-query-costs-5000-a-devs-nightmare-with-google-clouds-bigquery)
- Mixmax (Snowflake, ingeniería, dic-2022): un proceso diario con funciones externas (3 checks por usuario) tardaba >24 h y se bloqueaba a sí mismo; subir el cluster ayudó 2 días y luego se olvidó, apareciendo en la factura de diciembre. Los datos ya estaban en MongoDB; export/import diario bajó el proceso de >24 h a <4 min. Resultado: créditos de enero ≈ mitad de diciembre, febrero otro −30 % vs enero, tiempo medio de query 1,85→0,37 — [Mixmax](https://www.mixmax.com/engineering/make-it-snow-efb88freducing-costs-in-snowflake)
- Búsqueda de "runaway query" en Snowflake: solo contenido de vendors (Select.dev, Yuki, nOps) sin caso con nombre y cifra verificable; ejemplos de "29 % más créditos con <2 % más queries" son hipotéticos — [búsqueda](https://yukidata.com/content/catching-weekend-snowflake-cost-overruns-before-they-hit)

**Patrón idempotencia/duplicados (docs primarias)**
- Outbox: el relay puede publicar duplicados (p. ej. cae tras publicar y antes de registrar), por lo que los consumidores deben ser idempotentes; drawback: es propenso a error (se puede olvidar escribir en el outbox) — [microservices.io](https://microservices.io/patterns/data/transactional-outbox.html)
- Debezium: outbox + CDC log-based; `aggregateid` como clave Kafka para orden por agregado; UUID en header para detectar duplicados; el consumidor registra el UUID en la misma transacción que el cambio; el ejemplo NO cubre reintentos limitados ni DLQ ni limpieza de la tabla de mensajes — [Debezium](https://debezium.io/blog/2019/02/19/reliable-microservices-data-exchange-with-the-outbox-pattern/)

### Inferences
- Ranking sustentado en fuentes (sustituye al ranking de opinión): (1) restauración/DR no probada y alertas silenciosas (GitLab); (2) artefactos de datos/config generados que se propagan sin validación ni límite (Cloudflare 2025, 2024); (3) caminos de degradación/fail-open sin pruebas de sobrecarga (Cloudflare 2024); (4) acoplamiento oculto entre dominios de fallo y recuperación lenta de stores con quórum (Datadog, Honeycomb); (5) cost blowups por falta de guardarraíles por defecto (BigQuery sin `maximum_bytes_billed`, cluster Snowflake olvidado). Es un ranking por cobertura de casos documentados, no por frecuencia estadística.
- Los casos son de empresas con tráfico muy grande (Cloudflare, Datadog): su transferibilidad a equipos de datos medianos es un juicio, pero los modos de fallo (validar artefactos, probar restore, alertas de consumidores) son genéricos.
- Cloudflare 2025 es un incidente de pipeline de datos de configuración (ClickHouse → fichero → proxy), no un fallo de analítica; sirve como ejemplo de "data contract/validación en la frontera".

### Gaps
- Sin post-mortems formales públicos de sobrecoste en Snowflake/Databricks con cifras; las anécdotas BigQuery son de usuarios, con cifras discrepantes y sin reembolso confirmado.
- No leí originales de Coralogix; sin post-mortem de Kafka por misconfig de retención con pérdida de datos.
- No hallé post-mortems públicos de backfills/replays no idempotentes ni de SCD2 a escala (área de baja literatura pública).

## 2. Patrones avanzados verificados (outbox, CDC, WAP, schema registry, contratos, sharing, feature stores)

### Takeaway
Se pudieron verificar con fuentes primarias outbox/idempotencia, compatibilidad de schema registry y el alcance real (solo forma) de los contratos de dbt. WAP, SCD2, medallion, multi-tenancy, DLQ, reverse ETL y la mayoría del data sharing quedan sin verificación primaria en esta pasada. El sharing "zero-copy" tiene matices: cross-region implica copia.

### Cited Findings
- Schema Registry (Confluent): default BACKWARD (no transitivo; compara solo con la última versión). BACKWARD → actualizar consumidores antes que productores; FORWARD → productores primero; FULL → independiente; NONE sin garantías; Kafka Streams solo soporta tipos que incluyan BACKWARD (actualizar Streams antes que productores) — [Confluent docs](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html)
- dbt model contracts: fijan nombres de columnas, tipos y constraints, y fallan el build si no coinciden; NO validan contenido (para eso, data tests); no soportan Python models, materialized views, ephemeral, sources, seeds ni snapshots; en algunas plataformas `not_null`/`check` solo se aplican tras construir; incremental exige `on_schema_change: append_new_columns|fail`; detecta cambios rompientes (borrar columna, cambiar tipo; borrar modelo con contrato desde v1.9) — [dbt docs](https://docs.getdbt.com/docs/mesh/govern/model-contracts)
- Snowflake Open Data Sharing (Iceberg REST, consultas sobre datos vivos sin copia): en Public Preview solo se soporta como región destino la región del proveedor; el camino cross-region/cross-cloud es Cross-Cloud Auto-Fulfillment, que replica los datos como tabla Iceberg gestionada en la región destino y el proveedor paga egress, almacenamiento y cómputo (es decir, una copia) — [Snowflake docs](https://docs.snowflake.com/en/user-guide/open-data-sharing), [Snowflake auto-fulfillment](https://docs.snowflake.com/en/collaboration/use-auto-fulfillment-with-open-table-formats). Estado preview/GA mezclado en fuentes; verificar.
- Databricks acordó adquirir Tecton (ago-2025) para integrarlo con Agent Bricks (serving online); precio ~900 M USD solo en un agregador, otras fuentes dicen no divulgado — [Perficient](https://blogs.perficient.com/databricks-acquires-tecton/), [Dealroom](https://ai-startups.dealroom.co/news/feed/databricks-acquires-tecton-for-900m). Esto corrige el [NO VERIFICADO] de la nota previa sobre Tecton. Estado de Feast: sin datos.
- Thoughtworks Radar vol. 34 (abr-2026): Apache Iceberg en Adopt; Semantic layer en Trial; Docling y LangExtract en Trial; DuckLake, Databricks Agent Bricks, FalkorDB, "Context graph", "Role-based contextual isolation in RAG", "VLMs for end-to-end document parsing" y PageIndex en Assess; "MCP by default" en Caution; sin entradas de data contracts ni text-to-SQL como blips de este volumen; el radar usa anillos Adopt/Trial/Assess/Caution (sin "Hold") — [Thoughtworks Radar](https://www.thoughtworks.com/radar). Una entrada anterior "Data contract CLI" existe en el radar (anillo no visible en snippet) y menciona detección de breaking changes entre versiones en CI/CD — [Thoughtworks](https://www.thoughtworks.com/en-br/radar/tools/data-contract-cli)
- Iceberg branching: el índice de la página lista un caso "Audit Branch" (base de WAP), pero no pude leer el texto — [Iceberg docs](https://iceberg.apache.org/docs/latest/branching/)

### Inferences
- Los contratos de dbt cubren solo el "shape" en el límite productor-consumidor del warehouse; para contratos en streaming el equivalente técnico es el schema registry (BACKWARD/FULL) + CI. Inferido de los dos docs anteriores.
- La compatibilidad por defecto BACKWARD no transitiva puede permitir una cadena de cambios que rompan a consumidores antiguos; para retención larga/replay se recomienda *_TRANSITIVE [inferencia a partir de la definición documentada].
- Con la compra de Tecton, "feature store independiente" pierde peso; Databricks FS/Tecton pasa a integrarse en la plataforma de agentes (inferencia).
- WAP, SCD2, medallion (convención de capas), multi-tenancy (esquema/tenant vs. RLS), DLQ (con límite de reintentos y alertas) y reverse ETL son conocimiento general no verificado aquí.

### Gaps
- Sin fuentes primarias para: WAP (Iceberg/Delta/lakeFS/Nessie), SCD2 a escala, medallion, DLQ, replay/backfill, reverse ETL, Delta Sharing, Iceberg REST sharing (parcial), Feast vigente, data mesh/data products.
- No pude leer el contenido íntegro de Radar vol. 33 ni de las entradas "data product" o "data contracts" en vol. 33-34.

## 3. Mejores prácticas de producción, FinOps y escalabilidad/coste con cifras

### Takeaway
Los guardarraíles de coste existen como controles de plataforma (BigQuery: maximum bytes billed, cuotas diarias, dry run), pero su ausencia por defecto es la causa raíz de los casos conocidos. Los casos cuantificados de FinOps de datos son escasos y mayormente de vendors; el mejor dato de ingeniería independiente es Mixmax. SRE de datos (SLOs, on-call, runbooks) no tiene fuentes primarias en esta pasada.

### Cited Findings
- Controles BigQuery (ver §1): `maximum bytes billed`, dry run, cuotas diarias por proyecto/usuario; LIMIT no reduce bytes en tablas no clusterizadas; el modelo de facturación de almacenamiento lógico vs físico se define por dataset y no afecta al rendimiento; con facturación física, el time travel y failsafe cuentan en coste — [Google Cloud docs](https://docs.cloud.google.com/bigquery/docs/best-practices-costs)
- Casos cuantificados Snowflake: Mixmax (ver §1: −50 % mes a mes, luego −30 %, query media 5x más rápida) — [Mixmax](https://www.mixmax.com/engineering/make-it-snow-efb88freducing-costs-in-snowflake); Capital One proyectó −27 % de cómputo y −43 % de tiempo de query (resumen de búsqueda, no leí original) — [Capital One](https://www.capitalone.com/software/blog/snowflake-cost-optimization/); ESO −60 % (post de Snowflake, vendor) — [Snowflake blog](https://www.snowflake.com/blog/snowflakes-performance-optimizations-help-eso-reduce-costs-by-60); Costco Travel −50 % (Keebo, vendor) — [Keebo PDF](https://keebo.ai/wp-content/uploads/Costco-case-study.pdf); Authentic −44 % (Espresso AI, vendor) — [casestudies.com](https://www.casestudies.com/company/espresso-ai/case-study/237-authentic-saves-44-on-snowflake-spend-with-espresso-ai). Cifras autoinformadas; sin metodología comparable ni importes en USD.
- State of FinOps 2026 (FinOps Foundation; solo fuentes secundarias): 98 % gestiona algún coste de IA (31 % en 2024, 63 % en 2025); 90 % gestiona SaaS; 78 % de las funciones FinOps reportan a CTO/CIO; muestra ~1.100-1.192 profesionales y >83.000 M USD gasto; "las ganancias fáciles ya se capturaron" — [nOps](https://www.nops.io/blog/state-of-finops-2026/), [Virtasant](https://virtasant.com/blog/state-of-finops-2026). El informe original no se leyó.
- dbt State of Analytics Engineering 2026: temas "Infrastructure costs are outrunning budgets", hallucination risk, trust; la página de descarga no contiene cifras — [dbt Labs](https://www.getdbt.com/resources/state-of-analytics-engineering-2026-download). Cifras de la nota previa (57 % más gasto en warehouse vs 36 % más presupuesto; 71 % preocupado por alucinaciones; 72 % vs 24 %) provienen de un resumen de búsqueda y NO pude verificarlas contra el original en esta pasada.
- Reis 2026 (pulse): equipos con modelado ad-hoc reportan 38 % de tiempo apagando fuegos vs 19 % con modelos canónicos/semánticos; muestra auto-seleccionada — [Reis](https://joereis.substack.com/p/ai-is-here-but-the-hard-parts-havent)

### Inferences
- Guardarraíles mínimos defendibles a partir de los incidentes: límite de bytes por query y cuota diaria por usuario/servicio, statement timeout y límite de reintentos, auto-suspend/escalado a la baja con recordatorio, restore drills periódicos, límites de tamaño y validación de artefactos generados.
- FinOps de datos: la ausencia de estudios independientes con USD sugiere sesgo de publicación hacia el vendor; usar las cifras como órdenes de magnitud (30-60 %) solo para casos de partida muy ineficiente.
- SRE para datos (SLOs de freshness/volumen, on-call, runbooks, pirámide de tests, entornos) es conocimiento general NO VERIFICADO aquí.

### Gaps
- Sin FinOps Foundation primario, sin precios oficiales de Snowflake/Databricks verificados, sin casos de spot/autoscaling/caching con cifras, sin literatura sobre SLOs para data products ni testing pyramid en datos.

## 4. IA en data engineering: text-to-SQL, agentes, MCP, AI-ready data, semantic layers

### Takeaway
Los benchmarks de agentes SQL han subido muchísimo (Spider 2.0-Snow ~96,7 %, BIRD test ~83 %), pero Spider 2.0-Lite (~76 %) y sobre todo Spider 2.0-DBT (65,6 % máx.) siguen lejos de fiable, y los resultados de producción dependen de la capa semántica/contexto. Las cifras de "90 %+" de Snowflake o Genie son internas de vendors.

### Cited Findings
- Spider 2.0 original (arXiv 2411.07763, nov-2024): 632 tareas; mejor resultado entonces o1-preview con agente de código 21,3 % vs 91,2 % en Spider 1.0 y 73,0 % en BIRD — [arXiv](https://arxiv.org/abs/2411.07763)
- Leaderboard Spider 2.0 (consultado oct-2026; sin fechas por entrada): Snow: Genloop Sentinel Agent v2 Pro 96,70; Native mini 96,53; QUVI-3 + Gemini-3-pro-preview 94,15. Lite: Tianqiong Data Agent + GLM 5.2 76,23; DecisionX 74,95. DBT: SignalPilot Agent 65,6; Databao Agent 60,29; los siguientes con GPT-5/5.4 ≈ 39,7-41,2. Spider2-DBT se añadió el 22-may-2025 (68 tareas); las puntuaciones "pueden cambiar" y el uso de tablas oráculo debe etiquetarse — [Spider 2.0](https://spider2-sql.github.io/)
- Leaderboard BIRD (oct-2026): mejor test 82,95 % (GrainSQL, Purdue, 7-sep-2026, con conocimiento oráculo); mejor dev 78,10 % (DataGallery, Huawei, 22-ago-2026); mejor single-model con self-consistency Gemini-SQL2 80,04 % test (3-jun-2026); rendimiento humano 92,96 % — [BIRD](https://bird-bench.github.io/)
- Snowflake Cortex Analyst (blog de Snowflake, benchmark interno de 150 preguntas, tablas anchas pre-unidas): 90 %+ vs 51 % de GPT-4o con un solo prompt; evaluación con precisión/recall de columnas y gold queries marcadas por humanos — [Snowflake](https://www.snowflake.com/en/blog/engineering/cortex-analyst-text-to-sql-accuracy-bi/)
- Resumen de búsqueda (secundario) de un paper arXiv de 2026 sobre capas semánticas y otros estudios de vendors: mejoras con capa semántica (p. ej. Genie 53 % → 80 % → 100 % en 15 preguntas; dbt Labs 90-100 % vs 84-90 %, según Atlan) — muestras pequeñas, de vendor — [arXiv 2604.25149](https://arxiv.org/pdf/2604.25149), [Atlan](https://atlan.com/know/snowflake/cortex-analyst-vs-text-to-sql/)
- Gartner (feb-2025): hasta 2026 las organizaciones abandonarán el 60 % de los proyectos de IA sin datos AI-ready; 63 % no tiene o no sabe si tiene prácticas adecuadas; encuesta a 1.203 líderes de gestión de datos (jul-2024) — [Gartner vía búsqueda](https://www.gartner.com/en/newsroom/press-releases/2025-02-26-lack-of-ai-ready-data-puts-ai-projects-at-risk) (fetch directo dio 403; es una predicción, no un hecho medido)
- Uso de IA: Reis 2026 (n=1.101): 82 % usa IA a diario o más; en pulse (n=194) Claude 49 %, Copilot 16 %, ChatGPT 15 %, Cursor 7 %; 57 % dice escribir código mucho más rápido (el autor duda de que llegue a producción); 49 % cree que modelado y capas semánticas serán lo más importante en 2027 — [Reis pulse](https://joereis.substack.com/p/ai-is-here-but-the-hard-parts-havent); Stack Overflow 2025: 84 % usa o planea usar IA (76 % en 2024), 46 % desconfía de la precisión vs 33 % que confía; 31 % usa agentes en el trabajo — [Stack Overflow](https://survey.stackoverflow.co/2025/ai)
- Thoughtworks Radar vol. 34: "MCP by default" en Caution; Semantic layer en Trial; Docling/LangExtract en Trial; temas de agentes con permisos amplios y prompt injection (zero trust, mínimo privilegio) — [Thoughtworks Radar](https://www.thoughtworks.com/radar)
- Plataformas lanzaron MCP servers (BigQuery Remote MCP, CoCo, etc.) — ver nota previa; secundarias.

### Inferences
- Implicación para producción: un agente SQL de 90 %+ en un benchmark limpio no justifica autonomía sobre datos reales; Spider2-DBT (≤65,6 %) y Lite (≤76 %) sugieren que tareas de transformación y esquemas reales siguen fallando 25-35+ % de las veces. Se requiere capa semántica, evaluación propia con gold queries, sandbox de solo lectura, límites de bytes y revisión humana en escrituras.
- Los leaderboards son autoinformados y con sistemas multi-agente/self-consistency costosos; no son comparables a un modelo único ni a la latencia/coste de producción (inferencia; BIRD sí separa pista single-model).
- Discrepancia a notar: Snowflake mide con tablas anchas pre-unidas (fácil) mientras Spider2 usa esquemas empresariales grandes; los números no son comparables.

### Gaps
- Sin fecha por entrada en Spider2; sin verificar metodología de los líderes (¿oráculo?). Sin cifras de coste por consulta de agentes. Sin datos primarios sobre coding agents en pipelines (más allá de encuestas) ni sobre MCP en data platforms (solo el radar y notas previas).

## 5. Datos no estructurados, vector/RAG, Postgres/DuckDB y arquitectura (streaming-lakehouse)

### Takeaway
La literatura verificable es escasa: el Radar vol. 34 muestra qué herramientas de parsing/RAG se consideran emergentes (Docling, LangExtract en Trial; VLM para parsing, PageIndex en Assess), y hay un benchmark de vendor pgvectorscale vs Qdrant. Postgres lidera en Stack Overflow. El resto es inferencia.

### Cited Findings
- Benchmark Timescale (vendor, 50 M vectores, 768 dim, AWS r6id.4xlarge, sin filtros): a 99 % recall, Postgres+pgvector+pgvectorscale 471,57 QPS vs Qdrant 41,47 QPS; Qdrant menor latencia p99 (38,71 vs 74,60 ms) y mejor índice; otra fuente discrepa en dimensiones (1536) — [Instaclustr](https://www.instaclustr.com/education/vector-database/pgvector-vs-qdrant-5-key-differences-and-how-to-choose/), [Tiger Data](https://dev.to/tigerdata/postgresql-vs-qdrant-for-vector-search-50m-embedding-benchmark-3hhe)
- Stack Overflow 2025: PostgreSQL primero por tercer año (47 % quiere usarlo, 66 % admirado) — [Stack Overflow press](https://stackoverflow.co/company/press/archive/stack-overflow-2025-developer-survey/). Cifras de DuckDB/pgvector del survey no verificadas.
- Radar vol. 34 (ver §2 y §4): Docling y LangExtract Trial; PageIndex, VLM end-to-end para parsing de documentos, aislamiento contextual por rol en RAG, context graph, FalkorDB, Graphiti, DuckLake Assess/Trial — [Thoughtworks](https://www.thoughtworks.com/radar)
- Databricks compró Neon (Postgres) y Mooncake; Snowflake compró Crunchy Data — nota previa (secundarias) — [TechTarget](https://www.techtarget.com/data-technologies/news/366631950/Mooncake-acquisition-boosts-Databricks-database-capabilities)
- IBM–Confluent ~11.000 M USD, Salesforce–Informatica ~8.000 M USD, ServiceNow–Moveworks 2.850 M USD (MAD 2025) — [MAD 2025](https://mattturck.com/mad2025/)

### Inferences
- Dado el benchmark (vendor, sin filtros) y el liderazgo de Postgres, pgvector es el punto de partida razonable para <~50 M vectores si el equipo ya opera Postgres; las bases vectoriales dedicadas se justifican por latencia/filtrado. No generalizable.
- RAG evaluation, chunking y embeddings: no hay fuentes primarias aquí; el Radar sugiere que parsing de documentos es un área en movimiento rápido (blips en Assess).

### Gaps
- Sin fuentes sobre chunking/embeddings/evaluación RAG (Ragas, etc.), vector search nativo de lakehouse (Databricks/Snowflake), DuckDB adoption en cifras, streaming-lakehouse (Paimon, Iceberg streaming), pgvector docs oficiales (503).

## 6. Rol del data engineer, encuestas y panorama de mercado (Reis, dbt, MAD, Radar, Stack Overflow)

### Takeaway
Reis 2026 y MAD 2025 son verificados con primaria: los cuellos de botella son organizativos, la IA es uso diario, y el mercado se consolida con megaofertas selectivas. No hay datos duros de empleo/salarios (Dice/LinkedIn) ni de platform engineering.

### Cited Findings
- Reis 2026 (publicado 10-feb-2026; titular dice 1.001 y cuerpo 1.101 respuestas — discrepancia no explicada; muestra auto-seleccionada de su comunidad; sin metodología de ponderación): bottlenecks: sistemas legacy 25 %, falta de dirección del liderazgo 21 %, requisitos deficientes 19 %; modelado: presión por ir rápido 59 %, falta de ownership 51 %, solo 11 % dice que va bien; 82 % usa IA a diario o más, 64 % de organizaciones aún experimenta o la usa tácticamente; 42 % espera crecer el equipo vs 7 % reducirlo — [Reis](https://joereis.substack.com/p/the-2026-state-of-data-engineering). Contratos de datos, roles y herramientas: no aparecen en la página.
- Reis pulse (n=194): optimismo de carrera 71 %; narrativa "1 = 10" (una persona con IA equivale a 4-10) y presión directiva por mayor velocidad con equipos menores — [Reis pulse](https://joereis.substack.com/p/ai-is-here-but-the-hard-parts-havent)
- MAD 2025 (Turck, 11ª edición): logos de ~2.000+ a ~1.150 (recorte deliberado); nuevas secciones agent stack y local AI; MDS "desagregándose y ahora consolidándose" (dbt+Fivetran); datos e infraestructura de IA convergen en un plano de control con gobernanza, lineage y evaluación; megaofertas raras por integración y antitrust; riesgo de burbuja (acuerdos circulares); energía como restricción — [MAD 2025](https://mattturck.com/mad2025/)
- dbt State of Analytics Engineering 2026: temas (IA embebida, gobernanza rezagada, confianza, alucinaciones, costes que superan presupuesto, el cuello de botella se ha movido) — sin cifras en la página — [dbt Labs](https://www.getdbt.com/resources/state-of-analytics-engineering-2026-download)
- Stack Overflow 2025: ver §4/§5 — [Stack Overflow](https://survey.stackoverflow.co/2025/ai)

### Inferences
- Rol: de construir pipelines a plataforma, contratos, calidad, coste y contexto para agentes; las cifras de "1 = 10" son percepción de una comunidad auto-seleccionada, no evidencia de productividad de producción.
- El patrón repetido (Reis: ownership y requisitos; MAD: gobernanza; dbt: confianza; incidentes: validación en fronteras) apunta a que el factor limitante es proceso/propiedad, no motor.

### Gaps
- Sin datos Dice/LinkedIn/Data Engineering Weekly; sin platform engineering para datos; sin adopción medida de data contracts; sin informe completo de dbt 2026 ni distribución de roles de Reis.
- Radar vol. 33 no leído.
