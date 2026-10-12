# Data Engineering: cloud/on-prem, ecosistema (modern data stack), patrones/anti-patrones, coste y tendencias 2023-2026 (estado a oct 2026)

Nota metodológica: ~18 búsquedas web (resúmenes de búsqueda, mayormente fuentes secundarias; no se hizo fetch de páginas primarias). Todo lo citado lleva fuente; lo que viene de conocimiento general (sin verificar en esta sesión) se marca como [NO VERIFICADO] y se concentra en "Inferences" y "Gaps". Muchas fuentes son vendor-biased (Databricks, Snowflake, MotherDuck, Revefi, dbt Labs); se señala en cada caso.

## 1. Databricks vs Snowflake vs BigQuery vs Fabric: posicionamiento y criterios de decisión

### Takeaway
Las cuatro plataformas convergen hacia el mismo diseño: tablas abiertas Iceberg + catálogo gobernado + Postgres/OLTP integrado + capa de agentes de IA. La diferenciación pasa de "motor de consulta" a gobernanza/contexto para agentes, integración con el ecosistema del hiperescalador y modelo de coste. La elección se decide más por perfil de equipo (SQL/BI vs ingeniería/ML), ecosistema cloud existente y gobernanza que por rendimiento puro.

### Cited Findings
- Databricks compró Neon (Postgres serverless) en mayo de 2025; su tecnología sustenta Lakebase (Postgres gestionado con autoscaling, scale-to-zero, branching, PITR). Un solo medio cita ~1.000 M USD — [TechTarget](https://www.techtarget.com/data-technologies/news/366631950/Mooncake-acquisition-boosts-Databricks-database-capabilities), [Medium/datalex](https://medium.com/datalex/from-lakehouse-to-lakebase-why-databricks-buying-neon-changes-everything-ba4c1bcfa148)
- Databricks adquirió Mooncake Labs (1-oct-2025), extensión Postgres que refleja tablas a Iceberg sin ETL; términos no divulgados — [TechTarget](https://www.techtarget.com/data-technologies/news/366631950/Mooncake-acquisition-boosts-Databricks-database-capabilities)
- Data+AI Summit 2026 (15-18 jun, SF): Genie One (GA, "coworker" agéntico para negocio, 50+ apps), Genie Ontology (preview), LTAP (Lake Transactional + Analytical Processing), Lakehouse//RT (BI en milisegundos), Global Unity Catalog, Unity AI Gateway, Databricks Storage Ecosystem, CustomerLake, acuerdo para adquirir Panther — [Flexera recap](https://www.flexera.com/blog/perspectives/databricks-data-ai-summit-2026-recap-genie-one-ltap-lakehouse-rt-and-every-major-launche/), [StorageNewsletter](https://www.storagenewsletter.com/2026/06/26/data-ai-summit-2026-all-news). Recaps de terceros; fechas de disponibilidad sin verificar.
- Snowflake anunció la compra de Crunchy Data (jun 2025, ~250 M USD según fuente anónima de TechCrunch, Snowflake no comentó) para Snowflake Postgres; lectura como respuesta a Neon — [TechCrunch](https://www.techcrunch.com/2025/06/02/snowflake-to-acquire-database-startup-crunchy-data/), [AIM Research](https://aimresearch.co/?p=16024)
- Snowflake Summit 2026 (jun, SF): Snowflake Intelligence renombrado CoWork, Cortex Code → CoCo (extensiones Excel, VS Code, Claude Code), Horizon Context (capa de contexto de negocio), Datastream, Adaptive Compute, Openflow, Cortex AISQL, Iceberg v3 GA con almacenamiento gestionado y Polaris bidireccional, Agent Identity y AI-SPM, adquisiciones Natoma y Observe, compromiso de 6.000 M USD/5 años con AWS — [Revefi](https://www.revefi.com/blog/key-takeaways-snowflake-summit-2026), [Towards AI](https://pub.towardsai.net/snowflake-summit-2026-what-actually-shipped-and-what-it-means-for-the-people-who-build-on-it-502b95acf82a), [Medium](https://medium.com/@saurabh.kr/snowflake-summit-2026-what-to-build-on-what-to-watch-065ec28f73c5). Fuentes discrepan en conteo de anuncios y tema; Revefi es vendor.
- Google Cloud Next '26: marco "Agentic Data Cloud" (BigQuery + AlloyDB + Spanner + Bigtable + Spark gestionado); cross-cloud lakehouse (consulta de Iceberg en S3 sin egress vía interconexión, según análisis alemán); Knowledge Catalog; federación de catálogos externos (Glue, Databricks, Snowflake, SAP, Salesforce) en preview; BigQuery Remote MCP Server y ADK toolset — [Nand Research](https://nand-research.com/google-cloud-next-2026-enterprise-ai-enters-production/), [G-gen](https://blog.g-gen.co.jp/entry/next-26-whats-new-in-bigquery), [Cloudmagazin](https://www.cloudmagazin.com/2026/05/03/google-agentic-data-cloud-bigquery-lakehouse-databricks-dach-2026/). Secundarias; estado GA/preview sin verificar.
- Microsoft Fabric (Ignite nov-2025 y primeros meses 2026): OneLake security con permisos ReadWrite por carpeta, mirroring de Cosmos DB GA, Oracle y BigQuery en preview, surge protection y herramienta de overage de capacidad (preview Q1-2026), etiquetas de sensibilidad por defecto GA — [Fabric blog](https://blog.fabric.microsoft.com/en-au/blog/whats-new-in-onelake-and-the-fabric-platform-more-sources-security-and-capacity-tooling), [McCoy Partners](https://mccoy-partners.com/en/updates/microsoft-fabric-feature-spotlight-2026-q1). No hallé cobertura de Ignite 2026.
- AWS re:Invent 2025: >18 anuncios de analytics con Iceberg como eje; SageMaker Unified Studio con onboarding de un clic basado en IAM, Airflow serverless; S3 Tables adoptó el estándar Iceberg REST catalog (mar-2025) — [AWS Big Data Blog](https://aws.amazon.com/blogs/big-data/aws-analytics-at-reinvent-2025-unifying-data-ai-and-governance-at-scale), [Futurum](https://futurumgroup.com/insights/aws-leverages-s3-and-next-generation-of-sagemaker-during-pi-day-2025/), [Constellation](https://www.constellationr.com/blog-news/amazon-web-services-evolves-sagemaker-unified-data-platform-centered-ai)

### Inferences
- Patrón común 2025-26: los tres independientes/hiperescalares compran o integran Postgres (Neon, Crunchy, AlloyDB) para cubrir OLTP + agentes; "lakehouse + base transaccional" es la nueva frontera de rebundling.
- Criterios de decisión (síntesis propia, [NO VERIFICADO] como tabla oficial): Databricks cuando hay fuerte carga de ingeniería/ML/streaming y se quiere un único plano de gobernanza (Unity); Snowflake cuando predomina SQL/BI, data sharing y equipos analíticos con poca ops; BigQuery si ya se está en GCP, con cargas ad hoc/serverless y datos de marketing/GA; Fabric si la organización es Microsoft-céntrica (Power BI, M365, Entra) y acepta el modelo de capacidades (CU) — con riesgo de madurez desigual entre workloads. AWS "nativo" (S3 Tables + Athena/EMR/Redshift/SageMaker) suele ser la opción de menor lock-in pero mayor esfuerzo de integración.
- Los roadmaps casi idénticos (agente de negocio, capa de contexto/ontología, coding agent) hacen que el criterio relevante sea coste/gobernanza real, no features de keynote.

### Gaps
- No se verificó con fuentes primarias el estado GA/preview de ningún anuncio de 2026, ni benchmarks independientes de rendimiento/coste (TPC-DS, etc.). Los benchmarks publicados por vendors no son comparables.
- No hallé información sobre cuotas de mercado actuales ni precios comparativos fiables.

## 2. Modern data stack realista en 2026 tras la consolidación

### Takeaway
La pila se está re-empaquetando: ingestión+transformación (Fivetran+dbt), plataforma+Postgres+IA (Databricks/Snowflake), streaming (IBM+Confluent) y orquestación (Prefect+Dagster). Quedan piezas poco consolidadas (observabilidad, catálogo, reverse ETL/activación, BI semántica) y un contrapeso "small data" (DuckDB/DuckLake/Postgres).

### Cited Findings
- Fivetran y dbt Labs acordaron fusión all-stock el 13-oct-2025 (CEO George Fraser; Tristan Handy presidente; ~600 M USD ARR combinado); posteriormente se completó (TechTarget, fecha de cierre no confirmada). Compromiso de mantener dbt Core con su licencia. Fivetran ya había comprado Census (reverse ETL) y Tobiko Data (SQLMesh) en 2025 — [dbt Labs](https://www.getdbt.com/blog/dbt-labs-and-fivetran-sign-definitive-agreement-to-merge), [TechTarget](https://www.techtarget.com/searchdatamanagement/news/366643590/Fivetran-DBT-Labs-complete-merger-to-form-data-layer-for-AI), [Peliqan](https://peliqan.io/blog/dbt-fivetran-merger-explained/)
- IBM acordó comprar Confluent por ~11.000 M USD (31 USD/acción, anunciado 8-dic-2025); incluye Kafka, WarpStream y Flink gestionado; cierre sujeto a aprobaciones (no confirmé si cerró) — [Constellation](https://www.constellationr.com/blog-news/insights/ibm-buys-confluent-11-billion-heres-what-big-blue-gets), [SD Times](https://sdtimes.com/data/ibm-to-acquire-confluent-for-11-billion/). Opinión crítica (Lenses.io, competidor): la adopción de Flink de Confluent será lenta.
- Prefect adquirió Dagster Labs (anunciado ~13-14 jul-2026, términos no divulgados); Dagster mantiene nombre, licencia OSS y roadmap; Dagster afirma que no se obliga a migrar a clientes — [Dagster FAQ](https://dagster.io/dagster-customer-faq), [Pulse2](https://pulse2.com/prefect-acquiring-dagster-labs/amp/). Escepticismo en un digest comunitario (comentario, no hecho).
- Matt Turck MAD: en 2024 el mapa tenía 2.011 logos (1.416 en 2023) y la consolidación "no había llegado aún"; existe edición 2025 (nov-2025) pero no pude leer su análisis — [MAD 2024](https://mattturck.com/mad2024/), [MAD 2025 PDF](https://mattturck.com/landscape/mad2025.pdf)
- DuckDB/MotherDuck: tesis "small data" y agentes; DuckLake 1.0 (catálogo en base SQL, más simple que Iceberg/Delta) — afirmaciones del propio vendor (MotherDuck, incl. "agentes ejecutan 29x más queries que humanos"); un blog tercero reporta subida de precios de MotherDuck (sin anuncio, verificar) — [MotherDuck](https://motherduck.com/videos/duckdb-agent-moment-jordan-tigani/), [tasrieit](https://tasrieit.com/blog/motherduck-pricing-change-2026), [Sacra](https://sacra.com/chat/h/d224bb78-414a-420a-a3a9-d8f7d4cc8a80/)
- Catálogos/formatos: Iceberg v3 (deletion vectors, variant, row lineage, geo) descrito como GA en las principales plataformas en 1S-2026, pero hay discrepancia (otra fuente dice Databricks en public preview); AWS Glue aún sin crear tablas v3 vía REST CreateTable según una fuente; Polaris (donado a Apache) y Unity (implementa Iceberg REST, integra Glue) compiten como punto de convergencia — [Substack AM Data Lakehouse](https://amdatalakehouse.substack.com/p/the-state-of-apache-iceberg-catalogs), [Data Lakehouse Hub](https://datalakehousehub.com/blog/iceberg-market-2026), [Cloudmagazin](https://www.cloudmagazin.com/en/2026/07/01/iceberg-won-the-format-war-now-the-catalog-counts/)

### Inferences
- Pila "realista 2026" [síntesis propia, NO VERIFICADO como estándar]: ingestión (Fivetran/Airbyte/CDC Debezium/Flink o mirroring nativo zero-ETL) → almacenamiento Iceberg/Delta en object store → motor (Databricks/Snowflake/BigQuery/Trino/DuckDB) → dbt/SQLMesh → orquestación (Airflow/Dagster-Prefect/servicios nativos) → semántica/BI → agentes. Cada hiperescalar ofrece mirroring/zero-ETL que erosiona el valor de los conectores genéricos.
- Riesgo de lock-in de "roll-up": precios y roadmap de dbt Core/Cloud, Dagster y Confluent bajo nuevo dueño. Mitigar con formatos abiertos y SQL portable.
- Poca consolidación todavía (señalar): observabilidad de datos, catálogo/gobierno independiente, BI/capa semántica, reverse ETL (Census absorbido; resto fragmentado), data quality/contracts. Solo inferencia desde la ausencia de noticias de M&A encontradas, no medido.

### Gaps
- No hallé el análisis de MAD 2025 ni cifras de logos 2025/26.
- No verifiqué otras operaciones relevantes (p. ej. adquisiciones de Databricks como Tabular/MosaicML/Tecton/Neon: solo Neon y Mooncake confirmados aquí; Tecton no hallado — [NO VERIFICADO] y no debe afirmarse). Tampoco estado de Airbyte, Astronomer, Atlan/Alation/Collibra, Monte Carlo, Looker/Tableau/Sigma.

## 3. Plataformas on-prem/híbrido, multi-cloud y soberanía

### Takeaway
La soberanía se está materializando como oferta de hiperescalares (AWS European Sovereign Cloud) y como federación de catálogos entre nubes; la evidencia recopilada sobre Kubernetes/MinIO/Ceph/Cloudera/migración Hadoop es insuficiente.

### Cited Findings
- AWS European Sovereign Cloud GA el 15-ene-2026: región independiente en Brandenburg (eusc-de-east-1), Local Zones soberanas en Bélgica, Países Bajos y Portugal, inversión de 7.800 M EUR a largo plazo (nota: un agregador da fecha jul-2026, contradicha por AWS y otros medios) — [AWS press](https://press.aboutamazon.com/aws/2026/1/aws-launches-aws-european-sovereign-cloud-and-announces-expansion-across-europe), [W.Media](https://w.media/aws-launches-european-sovereign-cloud/); TechRadar sugiere que puede frenar la "geopatriación" — [TechRadar](https://www.techradar.com/pro/aws-brings-sovereign-cloud-to-europe-you-can-pause-your-geopatriation-plans-for-now)
- Interoperabilidad multi-cloud: BigQuery cross-cloud lakehouse y federación de catálogos (ver §1); Databricks "Global Unity Catalog" cross-región/cloud (§1).

### Inferences
- [NO VERIFICADO, conocimiento general] On-prem: Kubernetes + Spark/Trino/Flink + Iceberg sobre MinIO/Ceph es viable pero exige equipo de plataforma; Cloudera (CDP Private Cloud) y migraciones desde Hadoop se orientan a lakehouse Iceberg; el coste oculto está en operar el almacenamiento y la seguridad. Licencias de MinIO/Ceph y cambios recientes de MinIO (edición comunitaria) deben verificarse antes de decidir.
- "Sovereign" ≠ ausencia de jurisdicción extranjera: depende del control operativo y legal; revisar caso a caso (opinión, no cubierta por fuente aquí).

### Gaps
- No se buscaron/encontraron fuentes sobre Cloudera, MinIO, Ceph, Hadoop legacy, Kubernetes data platforms, Azure/GCP sovereign. Requiere investigación adicional.

## 4. Patrones, anti-patrones y errores comunes (incidentes y sobrecostes)

### Takeaway
La evidencia citada apunta a que los problemas dominantes son organizativos (propiedad, requisitos, presión por velocidad) y de coste operativo (archivos pequeños, full refresh, egress), no de tecnología. El listado de patrones/anti-patrones del encargo proviene mayormente de conocimiento general y no se pudo respaldar con fuentes en esta sesión.

### Cited Findings
- Encuesta State of Data Engineering 2026 (Joe Reis, 1.101 respuestas, muestra comunitaria no aleatoria): cuellos de botella = deuda técnica/legacy 25%, falta de dirección de liderazgo 21%, requisitos/upstream deficientes 19%; en modelado, 59% "presión por ir rápido" y 51% "falta de ownership"; solo 11% dice que el modelado va bien — [Reis](https://joereis.substack.com/p/the-2026-state-of-data-engineering), [Reis](https://joereis.substack.com/p/ai-is-here-but-the-hard-parts-havent)
- dbt Labs State of Analytics Engineering 2026 (vendor): 57% reporta más gasto en warehouse/cómputo vs 36% más presupuesto de equipo; 71% preocupado por datos alucinados que lleguen a stakeholders; 72% prioriza código asistido por IA pero solo 24% gestión de pipelines asistida (testing/observabilidad/calidad) — [dbt Labs](https://www.getdbt.com/resources/state-of-analytics-engineering-2026-download) (vía resumen de búsqueda)
- Snowpipe cobra overhead por archivo (~0,06 créditos/1.000 archivos) y se recomiendan archivos comprimidos de 100-500 MB; transferencias entre regiones/nubes generan cargos que pasan desapercibidos; picos tras deploys sugieren regresiones, scans amplios y full refresh por defecto; gasto que crece más que el dato sugiere duplicación, schedule creep y marts redundantes — [PointFive](https://www.pointfive.co/knowledge-base/inefficient-snowpipe-usage-due-to-small-file-ingestion), [Revefi](https://www.revefi.com/blog/avoiding-snowflake-data-cost-pitfalls), [Coalesce](https://coalesce.io/data-insights/snowflake-cost-optimization-a-practical-engineering-guide-to-reducing-snowflake-costs/). Fuentes vendor/tooling; cifras sin verificar contra precios oficiales.
- Databricks FinOps: etiquetado/asignación de costes, apagado automático de clusters inactivos, alertas de presupuesto — [Xebia](https://xebia.com/blog/databricks-finops-optimization-strategies/) (genérico).
- Datadog (vendor): 95% preocupado por el impacto de coste/rendimiento de la IA en infraestructura compartida — [Datadog](https://www.datadoghq.com/ja/resources/ai-age-data-engineering-market-survey/) (resumen gated).

### Inferences
- Ranking provisional [juicio propio, NO medido] por frecuencia de incidentes/coste: (1) falta de ownership y de data contracts → roturas upstream silenciosas; (2) full refresh/SELECT * / scans sin partición/clustering y warehouses sobredimensionados o siempre encendidos; (3) archivos pequeños y micro-batches/streaming innecesario; (4) egress cross-region/cloud; (5) DAGs espagueti con dependencias implícitas y backfills no idempotentes; (6) over-engineering (stack de 15 herramientas para <1 TB). El cluster 1 sí lo respaldan las encuestas; el resto es experiencia práctica.
- Patrones (CDC + outbox, event sourcing, data products, WAP — write-audit-publish, medallion, feature stores, backfills idempotentes por partición, multi-tenancy, schema registry): [NO VERIFICADO en esta sesión]. Puntos senior: outbox evita dual-write; WAP con branching Iceberg/Nessie/lakeFS o Delta clones; medallion es convención de capas, no arquitectura (riesgo de copias redundantes); feature stores pierden peso frente a tablas gobernadas + online serving; schema registry es la base técnica de data contracts en streaming.

### Gaps
- Sin fuente sobre post-mortems públicos reales para rankear anti-patrones por incidente; el ranking es opinión.
- Sin cifras de sobrecoste agregadas ni estudios de FinOps independientes (FinOps Foundation no consultada).

## 5. Tendencias 2023-2026: IA en data engineering, rol del data engineer, calidad y producción

### Takeaway
La IA ya es herramienta diaria (82% de encuestados) pero la adopción organizativa va rezagada y los límites siguen siendo datos, requisitos y gobierno. Text-to-SQL empresarial sigue siendo poco fiable sin capa semántica/contexto, de ahí la carrera por "context layers" (Horizon Context, Genie Ontology, Knowledge Catalog).

### Cited Findings
- 82% usa IA a diario o más; 64% de las organizaciones aún experimenta o la usa tácticamente; 42% espera crecer el equipo, 7% reducirse — [Reis 2026](https://joereis.substack.com/p/the-2026-state-of-data-engineering) (muestra comunitaria)
- Spider 2.0 (workflows SQL empresariales reales, 632 tareas, esquemas ~812 columnas): modelos que rinden ~91% en Spider 1.0 y 73% en BIRD resuelven solo ~17-21% en la versión original del paper (o1-preview); el fallo principal es el schema linking. Sin datos 2026 de modelos nuevos — [arXiv 2411.07763](https://www.arxiv.org/pdf/2411.07763), [revisión](https://themoonlight.io/review/spider-20-evaluating-language-models-on-real-world-enterprise-text-to-sql-workflows). El 90% de precisión "es inútil" es opinión: [ascii.co.uk](https://ascii.co.uk/news/article/news-20260118-3e9e9dee/spider-20-exposes-text-to-sql-accuracy-crisis-in-enterprise)
- Agentes sobre datos: MCP servers (BigQuery Remote MCP, CoCo con extensión Claude Code), agent identity/AI-SPM en Snowflake, Unity AI Gateway (§1). Thoughtworks Radar vol. 34 (abr-2026) enfatiza fundamentos de ingeniería frente a "cognitive debt"; no pude leer las entradas sobre data contracts/MCP — [Thoughtworks PDF](https://www.thoughtworks.com/content/dam/thoughtworks/documents/radar/2026/04/tr_technology_radar_vol_34_en.pdf)
- Streaming: IBM-Confluent (11.000 M USD) y Flink gestionado como pieza central (§2); Snowflake Datastream/Openflow y Databricks Lakehouse//RT como "streaming simplificado" dentro de la plataforma (§1).

### Inferences
- Rol del data engineer [juicio propio]: se desplaza de "escribir pipelines" a plataforma, contratos, calidad, coste y curación de contexto para agentes; los agentes de código aceleran el scaffolding pero la dbt Labs muestra el hueco en testing/observabilidad automatizados (24% vs 72%).
- Áreas de baja consolidación a vigilar (hype alto, estándares inmaduros): capas de contexto/ontología para agentes (3 definiciones propietarias distintas), vector data/RAG pipelines (no cubierto por fuentes aquí), unstructured data processing, evaluación de agentes, observabilidad LLM, catálogos para IA. Alta probabilidad de más M&A y cambios de nombre (p. ej. rebrands de Snowflake en un año).
- Presión de costes: la encuesta dbt (57% más gasto en cómputo) + mayor consumo por agentes (claim vendor de MotherDuck) sugiere que 2026-27 será de FinOps para cargas agénticas [especulación].
- Buenas prácticas productivas [NO VERIFICADO]: tests de datos en CI (dbt tests/unit tests, Great Expectations/Soda), data contracts en el PR, CI/CD con entornos efímeros/branching, observabilidad por freshness/volumen/schema/lineage, runbooks y on-call con SLOs por data product, documentación generada pero revisada.

### Gaps
- Sin fuentes sobre vector databases/pgvector/RAG pipelines, unstructured data, adopción real de data contracts, plataforma-engineering, ni cifras de empleo/salarios del rol.
- No se pudo leer el Fundamentals of Data Engineering, a16z ni las entradas concretas del Tech Radar.
- Sin comprobación primaria de ningún anuncio de Summit 2026; tratar nombres de producto y disponibilidad como provisionales.
