# Modelado de datos y capas semánticas (verificación con fuentes primarias, oct-2026)

Convenciones: "Cited" = leído con WebFetch en la página citada (salvo que se marque "[snippet de búsqueda]", es decir, no abrí la página completa). "Inferencia" = mío. Idioma: español. Fecha de referencia: 2026-10-12.

## 1. Guía primaria (Kimball, Inmon, Linstedt) y qué dicen los independientes sobre columnar cloud

### Takeaway
Las definiciones de Kimball (grano, hechos, dimensiones conformadas, bus matrix, SCD 0-7, bridge) están verificadas contra kimballgroup.com. Inmon (CIF) y Data Vault se verificaron sólo parcialmente: Kimball describe a CIF en su propio texto; para Data Vault no pude abrir fuente primaria de Linstedt (sólo Data Vault Alliance, Wikipedia y vendors). Sobre trade-offs en motores columnares cloud la evidencia es mayormente de vendors/consultoras.

### Cited Findings
**Kimball (primario: Kimball Dimensional Modeling Techniques, derivado de The Data Warehouse Toolkit 3ª ed.)**
- El índice oficial de técnicas incluye: grano; transaction / periodic snapshot / accumulating snapshot / factless / aggregate / consolidated fact tables; conformed facts; degenerate, role-playing, junk, snowflaked y outrigger dimensions; conformed dimensions, shrunken rollup, drilling across, bus architecture y bus matrix; SCD tipos 0 a 7; multivalued dimensions y bridge tables; late-arriving facts/dimensions; real-time fact tables; audit dimensions — [Kimball techniques](https://www.kimballgroup.com/techniques/dimensional-modeling-techniques/)
- Grano = nivel de detalle que representa una fila de la tabla de hechos; se declara primero y es "binding contract on the design"; recomendar grano atómico; "different grains must not be mixed in the same fact table" — [Kimball: Grain](http://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/grain/)
- Bus matrix: filas = procesos de negocio, columnas = dimensiones; celda marcada = la dimensión aplica; leer columnas revela dónde conformar; sirve para priorizar proyectos (se implementa una fila a la vez); la "detailed implementation bus matrix" documenta grano y hechos por tabla — [Kimball: Bus Matrix](http://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/enterprise-data-warehouse-bus-matrix)
- SCD (Design Tip #152): Tipo 0 retiene el original (típico de atributos de dimensión fecha y claves durables); Tipo 1 sobrescribe; Tipo 2 nueva fila; Tipo 3 nueva columna con valor previo; Tipo 4 mini-dimensión para atributos volátiles (la tabla de hechos guarda ambas claves); Tipo 5 = Tipo 4 + outrigger Tipo 1 con perfil actual sobrescrito en la dimensión base; Tipo 6 = atributos Tipo 1 (actuales, sobrescritos en todas las filas de la misma clave durable) dentro de una dimensión Tipo 2; Tipo 7 = la tabla de hechos lleva dos FK: surrogate key Tipo 2 (histórico) y clave durable ligada a la fila actual — [Kimball Design Tip 152](https://www.kimballgroup.com/2013/02/design-tip-152-slowly-changing-dimension-types-0-4-5-6-7/)
- Bridge tables: cuando una dimensión toma varios valores por fila de hecho (p. ej. diagnósticos múltiples), el hecho apunta a una group key y el bridge tiene una fila por valor; si se apoya en dimensiones Tipo 2 debe incluir fechas de vigencia/expiración y la consulta debe acotarse a un punto en el tiempo — [Kimball: Multivalued dimensions and bridge tables](http://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/multivalued-dimension-bridge-table). (La página no trata weighting factors; no los cito.)
- Snowflaking: Kimball recomienda no hacerlo; normalizar jerarquías en tablas enlazadas es difícil de entender para usuarios y puede degradar rendimiento; una dimensión aplanada guarda la misma información — [Kimball: Snowflaked dimensions](http://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/snowflake-dimension). Design Tip #105 (Margy Ross, 2008): ahorro de espacio del snowflake "negligible" frente al costo de ETL y complejidad [snippet de búsqueda; página no abierta] — [Kimball DT 105 vía búsqueda](https://www.kimballgroup.com/2008/09/)
- Kimball vs CIF (texto de Kimball Group, 2004): CIF exige un EDW normalizado (3NF) antes de los marts dimensionales; Kimball sostiene que el dato atómico "must be dimensionally structured", que la integración viene de dimensiones conformadas ("Normalization alone doesn't begin to address the common data keys and labels required for integration") y que el almacenamiento duplicado (normalizado + dimensional) "is unwarranted"; el híbrido es viable pero costoso — [Kimball Group, "Differences of Opinion"](https://decisionworks.com/2004/03/differences-of-opinion/). Nota: es la descripción de Kimball sobre CIF, no texto de Inmon.

**Inmon**
- Definición canónica: colección subject-oriented, integrated, non-volatile, time-variant en apoyo de decisiones; las fuentes que encontré citan la 4ª ed. (Wiley, 2005), no la 1ª (1992); el año 1992 no se pudo verificar — [snippet de búsqueda, O'Reilly/otros](https://www.oreilly.com/library/view/pentaho-solutions-business/9780470484326/ch06.html)
- Sin acceso a texto primario de Inmon (libros). Hub-and-spoke con marts dependientes y EDW 3NF proviene de resúmenes secundarios — [TDAN](https://tdan.com/?p=29330)

**Data Vault 2.0**
- Historia: Linstedt lo concibió en los 90, lo liberó en 2000 (dominio público), explicó reglas en 5 artículos en The Data Administration Newsletter; DV2.0 (2013) añade NoSQL/semi-estructurado y mejores prácticas. Hubs = claves de negocio únicas; links = relaciones (normalmente N:M) con grano definido por las claves de hub; satellites = atributos descriptivos append-only con historia; Raw Vault (fiel a la fuente) y Business Vault (reglas de negocio + estructuras de apoyo como PIT y bridge); típicamente alimenta marts estrella; Wikipedia anota que requiere arquitectos con experiencia y que no está optimizado para consulta directa desde BI — [Wikipedia: Data vault modeling](https://en.wikipedia.org/wiki/Data_vault_modeling) (secundaria, con etiquetas de citas faltantes)
- Libros de referencia: Linstedt, Super Charge Your Data Warehouse (2010); Linstedt & Olschimke, Building a Scalable Data Warehouse with Data Vault 2.0 (Morgan Kaufmann/Elsevier, 2015/2016); Hultgren (2012) — [Wikipedia](https://en.wikipedia.org/wiki/Data_vault_modeling); [Elsevier](https://www.elsevier.com/books/catalog/isbn/9780128025109)
- Data Vault Alliance: ofrece certificación CDVP2.1 (DVAUniversity, "designed by Dan Linstedt") y un programa de certificación de herramientas desde 2021 que verifica generación de DML/DDL "100% compliant"; su home no define el método — [datavaultalliance.com](https://datavaultalliance.com/)
- Contra/trade-offs (vendors/consultoras, no independientes): insert-only crece mucho; satélites por fuente exigen consultas complejas para combinar; equipos con 3-5 fuentes estables pueden estar mejor con estrella; PIT tablas se presentan como "fact table" sobre satélites para simplificar; hash keys pierden contra claves secuenciales en joins pero se argumenta que otros beneficios compensan — [WhereScape](https://www.wherescape.com/blog/data-vault-on-snowflake-guide/); [phData](https://www.phdata.io/blog/optimizing-snowflakes-performance-for-data-vault-modeling/) (ambos venden servicios DV/Snowflake)

**Anchor modeling**
- Técnica abierta basada en sexta forma normal (6NF), desarrollada desde 2003 entre industria sueca y Stockholm University; mejor paper de ER'09; 3 tipos de tabla (Anchors, Attributes, Ties) más knots; "6NF puts each non-key attribute in a separate relation"; hay un documento sobre bitemporalidad — [anchormodeling.com (resultados de búsqueda)](https://www.anchormodeling.com/wp-content/uploads/2010/08/Anchor_Modeling_ER09_Presentation.pdf); [bitemporal](https://www.anchormodeling.com/wp-content/uploads/2011/05/Anchor-Modeling-with-Bitemporal-Data.pdf) [snippets; no abrí los PDF]

**Columnar cloud: documentación oficial**
- BigQuery: "performs best when your data is denormalized"; nested/repeated (RECORD/STRUCT, ARRAY) preservan relaciones sin el costo de un esquema normalizado; límite de 15 niveles de anidamiento; sin benchmarks cuantificados en la página — [BigQuery docs](https://docs.cloud.google.com/bigquery/docs/nested-repeated)
- Snowflake VARIANT: guardar en VARIANT si no se sabe cómo se consultará; aplanar a columnas si hay fechas/números como string o arrays (mejora pruning y almacenamiento); subcolumnarización hasta 200 elementos por partición por defecto; no se extraen elementos con JSON null o tipos múltiples; límite 128 MB sin comprimir — [Snowflake docs](https://docs.snowflake.com/en/user-guide/semistructured-considerations)
- Snowflake clustering: sólo tablas muy grandes (típicamente multi-TB), consultas selectivas, tablas poco modificadas; cuesta créditos y almacenamiento; 3-4 columnas máx. — [Snowflake docs](https://docs.snowflake.com/en/user-guide/tables-clustering-keys)
- Constraints: en tablas estándar de Snowflake PK/FK/UNIQUE no se imponen, NOT NULL y CHECK sí; en hybrid tables todos se imponen — [Snowflake docs](https://docs.snowflake.com/en/sql-reference/constraints-overview). En Databricks PK/FK son informativos (GA desde DBR 15.2), UNIQUE en Public Preview (DBR 18.2+), NOT NULL y CHECK se imponen; los informativos "might improve performance" vía optimizaciones — [Databricks docs](https://docs.databricks.com/aws/en/tables/constraints). No encontré en esas páginas qué hace RELY.

### Inferences
- Ninguna fuente primaria de Kimball dice nada sobre motores columnares; la preferencia por estrella frente a snowflake se justificaba por comprensibilidad y ETL, razones que siguen vigentes aunque el costo de joins haya bajado. (Inferencia.)
- Dado que PK/FK no se imponen en Snowflake/Databricks, la unicidad del grano debe validarse con tests (ver sección 6). (Inferencia a partir de la doc de constraints.)
- Data Vault es defendible como capa de integración/auditoría, pero la narrativa a su favor en cloud viene de quienes lo venden; tratarla como no verificada de forma independiente. (Inferencia.)

### Gaps
- Sin fuente primaria de Linstedt (blog/libro) ni de Inmon; sin crítica independiente de Data Vault (p. ej. de practicantes sin venta de servicios).
- Design Tip 105 sólo vía snippet. Sin definiciones textuales de Kimball para fact table types, junk, role-playing, degenerate, conformed dimension (sólo el índice oficial y las páginas arriba); las defino por conocimiento general en la sección de Inferencias de los otros apartados.
- Sin fuente sobre PIT/bridge de DV más allá de menciones de vendors.

## 2. ¿Evidencia cuantitativa OBT vs estrella? (con nota de patrocinio)

### Takeaway
Existe un solo benchmark con método declarado (Fivetran blog, 2022, TPC-DS subset): OBT 25-50% más rápido según warehouse, con resultados mixtos en Snowflake y storage 3x en Redshift. Un segundo post (InterWorks, 2024) da 40 s vs 77 s sin tamaño ni warehouse. Ninguno es auditado ni independiente de un vendor; no hay estudio revisado por pares.

### Cited Findings
- Fivetran (M. Kaminsky, 16-ago-2022): subset de TPC-DS "100" (5 tablas: store_sales, date_dim, store, household_demographics, customer_address), OBT = store_sales con LEFT JOIN a 4 dimensiones; Redshift (dc2.large x1 y dc2.8xlarge x3), Snowflake X-Large, BigQuery default; cache desactivado. Resultados: Redshift OBT más rápida en 9/10 queries, 25-30% global; Snowflake ~25% global pero la estrella ganó en queries 3, 4 y 7; BigQuery ~49-50%. Storage Redshift: store_sales 29.8 GB, OBT 60.3 GB; total de ~30 GB a >90 GB. El autor dice que no es experto en internals de BigQuery/Snowflake, no explica los resultados de Snowflake, y la nota de "excluir compilación" es inconsistente entre warehouses — [Fivetran blog](https://fivetran.com/blog/obt-star-schema). Patrocinio: publicado en blog de Fivetran, dataset aportado por Fivetran, con CTAs; sin declaración formal de conflicto.
- InterWorks (M. Oldroyd, 12-mar-2024): tabla plana 40 s vs estrella 77 s ("nearly twice as fast"); cliente en SQL Server PDW; sin tamaño de datos ni warehouse; advierte que benchmarking riguroso es difícil, que la tabla plana consume más disco (compresión en Snowflake lo reduce), pierde dimensión compartida como filtro en Tableau y cuesta reconstruirla con datos que cambian — [InterWorks](https://interworks.com/blog/2024/03/12/comparing-query-performance-of-star-schemas-vs-flat-tables/). InterWorks es consultora/partner de Snowflake y Tableau [conocimiento general, no verificado en página].
- No hay benchmark oficial de Snowflake/BigQuery/Databricks que compare ambos modelos (búsqueda sin resultados).

### Inferences
- La diferencia de 25-50% es indicativa para consultas BI simples sobre 1 hecho y 4 dimensiones; no cubre actualización de dimensiones (SCD), múltiples hechos ni costo de reconstrucción de la OBT.
- Costo real de OBT = rematerialización + 2-3x storage (en Redshift sin compresión óptima) vs ahorro de joins; sólo medir con la carga propia.

### Gaps
- Sin cifras de costo ($) comparadas; sin benchmark en Databricks/Iceberg; sin estudio independiente.

## 3. Activity Schema, OBT como patrón, 3NF, estrella vs snowflake

### Takeaway
Activity Schema tiene sólo fuentes de su promotor (Narrator/Elsamadisi, dbt blog 2021) y secundarias; no hay especificación formal independiente verificada. OBT es una práctica, no un estándar con referencia primaria.

### Cited Findings
- Activity Schema: presentado en el blog de dbt (29-oct-2021, Daniel Poppy; presenta Ahmed Elsamadisi): modela "a customer doing an activity over time", una sola tabla de serie temporal con 11 columnas y sin JSON, que reemplaza hechos y dimensiones — [dbt blog](https://www.getdbt.com/blog/activity-schema-data-modeling-with-a-single-table). Resumen secundario: columnas activity_id, ts, entity, entity_id, activity; algunos comentan que sirve poco más allá de analítica de producto — [DataVidhya](https://datavidhya.com/learn/data-modeling/modern-approaches/activity-schema/) (secundaria, peso bajo). Origen en Narrator — [Data Engineering Podcast ep. 234](https://www.dataengineeringpodcast.com/narrator-exploratory-analytics-episode-234)
- Capa mart en dbt: dbt recomienda marts "wide, rich" por entidad de negocio (staging -> intermediate -> marts) — [dbt best practices](https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview)
- OBT: ver sección 2 (única evidencia). 3NF: parte de CIF (sección 1).

### Inferences
- Activity Schema = modelo de eventos estilo "event stream table"; encaja con product analytics/journeys, no con finanzas o inventario con balances y snapshots (donde Kimball ofrece periodic/accumulating snapshots). Inferencia.

### Gaps
- No pude abrir el repo/spec de Activity Schema (activityschema.com / GitHub) ni crítica independiente; estado de mantenimiento desconocido.

## 4. Streaming, CDC, bitemporal, schema evolution, data contracts, naming, grain testing

### Takeaway
Las piezas verificadas: Delta CDF (columnas _change_type etc.), semántica bitemporal (valid time vs transaction time; SQL:2011), Iceberg schema evolution con column IDs, contratos de modelo dbt y sus límites. Test de grano y convenciones de nombre: parcialmente verificado.

### Cited Findings
- Delta Change Data Feed: agrega `_change_type` (insert, update_preimage, update_postimage, delete), `_commit_version`, `_commit_timestamp`; se activa con `delta.enableChangeDataFeed=true`; sólo registra cambios posteriores a la activación; renombrar/borrar columnas (cambios no aditivos) con column mapping restringen lecturas según versión — [Delta docs](https://docs.delta.io/latest/delta-change-data-feed.html)
- Bitemporalidad: valid time (cuándo es cierto en el mundo) y transaction time (cuándo lo registró la BD); SQL:2011 añadió tablas de application-time, system-versioned y bitemporales; Snodgrass propuso extensiones temporales en 1992 (TSQL2, 1994) — [Wikipedia: Temporal database](https://en.wikipedia.org/wiki/Temporal_database)
- Iceberg: add/drop/rename/update(widen)/reorder son cambios de metadata sin reescribir archivos; column IDs únicos evitan leer la columna equivocada; evolución de particiones sin reescribir (datos viejos conservan su spec) — [Iceberg docs](https://iceberg.apache.org/docs/latest/evolution/)
- dbt model contracts: `contract.enforced: true` exige nombre y data_type de todas las columnas; verificación previa al build; soporta table, view (sin constraints) e incremental (con on_schema_change append_new_columns/fail); no soporta Python models, materialized view, ephemeral, snapshots, seeds; cambios rompientes: quitar columna, cambiar tipo, quitar constraints (v1.6+), quitar modelo (v1.9+); los contratos validan forma y los data tests validan contenido; PK/FK/unique suelen ser sólo metadata en warehouses cloud — [dbt docs](https://docs.getdbt.com/docs/mesh/govern/model-contracts)
- Naming: dbt usa prefijo `stg_` en staging y marts nombrados por entidad (customers, orders); la página overview no menciona `fct_`/`dim_` — [dbt docs](https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview)
- Kimball: Late arriving facts/dimensions, audit dimension y real-time fact tables existen como técnicas oficiales — [Kimball techniques](https://www.kimballgroup.com/techniques/dimensional-modeling-techniques/)

### Inferences
- Modelo de CDC: raw/bronze append-only de cambios (log) -> dimensión SCD2 / tabla current-state. Equivale a satélite de DV o snapshot SCD2. Inferencia.
- Test de grano: con constraints no impuestas, usar test de unicidad sobre la combinación de claves del grano (p. ej. unique_combination_of_columns de dbt_utils; no verificado en esta sesión) + not_null; contrato dbt para forma. Inferencia.

### Gaps
- No verifiqué Debezium, Kafka compacted topics, Flink changelog semantics, ni SCD2 snapshots de dbt (docs). Sin fuente sobre convenciones fct_/dim_ de Kimball (no las define). Sin fuente primaria sobre "data contracts" como estándar (ODCS/Bitol) en esta sesión.

## 5. Capas semánticas: estado verificado, fechas y licencias

### Takeaway
Cronología verificada con fuentes primarias, corrigiendo las notas previas: MetricFlow pasó a Apache 2.0 el 14-oct-2025 (no dic-2025); OSI v1 se publicó el 27-ene-2026 y el proyecto se renombró Apache Ossie (Incubating) hacia 10-jul-2026; Snowflake Semantic Views GA en 2025; Databricks Metric Views GA el 2-abr-2026 (con partes en Preview).

### Cited Findings
**Cronología OSI / Apache Ossie**
- Repositorio abierto nov-2025 según el post de Ossie; 17 socios de lanzamiento, ahora >50 organizaciones; contribuyentes: Snowflake, Dremio, Salesforce, Databricks, dbt Labs, RelationalAI, GoodData, Honeydew; grupos de trabajo Metric Language, Catalog, Ontology; >100 commits y 35 PR fusionados en ese post — [Apache Ossie: updates (10-jul-2026, J. Klahr)](https://ossie.apache.org/updates/ossie-enters-apache-incubator/)
- 27-ene-2026: Snowflake anuncia la primera versión de la spec OSI (Apache 2.0): modelo vendor-neutral y extensible de datasets, métricas, dimensiones, relaciones y contextos; nuevos miembros AtScale, Coalesce, Collate, Credible, Databricks, JetBrains, Lightdash, Qlik; existentes incluyen Cube, dbt Labs, Salesforce, ThoughtSpot, etc. — [Snowflake blog](https://www.snowflake.com/en/blog/open-semantic-interchanges-specs-finalized/)
- Renombre por colisión de acrónimo con otros proyectos open source "OSI"; spec sin cambios; incubación ASF (gobernanza con listas públicas, votos, committership por mérito). Fecha de aceptación: Dremio dice jun-2026; Snowflake lo publica el 8-jul-2026; la página de Ossie el 10-jul-2026 — [Apache Ossie](https://ossie.apache.org/updates/ossie-enters-apache-incubator/); [Dremio vía búsqueda](https://www.dremio.com/blog/apache-ossie-the-open-semantic-interchange-joins-the-apache-incubator); [Snowflake](https://snowflake.com/en/blog/apache-ossie-open-semantic-interchange-incubator) (fechas discrepantes, ver Gaps)
- "Incubating" no implica completitud o estabilidad ni endoso pleno de la ASF (aviso estándar en el post) — [Apache Ossie](https://ossie.apache.org/updates/ossie-enters-apache-incubator/)
- Repo apache/ossie: spec JSON/YAML con schema legible por máquina, conversores (dbt, GoodData, Polaris, Salesforce), ejemplo TPC-DS, licencia Apache-2.0, ~2.4k estrellas, 52 issues y 66 PR abiertos — [GitHub apache/ossie](https://github.com/open-semantic-interchange/OSI) (redirige). ROADMAP: sin número de spec ni fecha de release; issue #102 propone versionado semántico y releases Git; conversores adicionales listados: Snowflake Cortex Analyst YAML, OrionBelt, Microsoft Power BI/Fabric (TMSL); funciones futuras: lenguaje de consulta semántica, jerarquías y tiempo, metadata para IA — [ROADMAP.md](https://github.com/apache/ossie/blob/main/ROADMAP.md)
- Un tercero (Atlan, 2026) afirma que ningún producto soportaba aún import/export OSI; no verificado — [Atlan vía búsqueda](https://atlan.com/know/ai-agent/semantic-layer/unity-catalog-semantic-layer.md)

**dbt Semantic Layer / MetricFlow**
- 14-oct-2025 (Coalesce 2025): dbt Labs anuncia MetricFlow "fully available under an Apache 2.0 license" (código de definición de métricas, SQL multi-dialecto, formato de metadatos); alineado con OSI; esperan donarlo a una fundación (no ocurrió en ese post) — [dbt blog](https://www.getdbt.com/blog/open-source-metricflow-governed-metrics)
- README del repo: v0 a 0.140.0 AGPL; 0.150.0 a 0.208.2 BSL; >=0.209.0 Apache 2.0 — [GitHub dbt-labs/metricflow](https://github.com/dbt-labs/metricflow). Conclusión: la afirmación "Apache 2.0" del agregador es correcta pero la fecha correcta es oct-2025; ver [Querio](https://querio.ai/articles/cube-vs-dbt-semantic-layer-vs-metricflow-update) (secundario, dic-2025 es erróneo).
- El dbt Semantic Layer (servicio gestionado, APIs, control de acceso, integración MCP) requiere planes dbt Starter, Enterprise o Enterprise+ — [dbt docs](https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl)
- Fusión Fivetran-dbt Labs: anunciada 13-oct-2025, cerrada 1-jun-2026 según comunicado de Fivetran; dbt Core v2.0 alpha abre el runtime Fusion con Apache 2.0 [snippet de búsqueda] — [Fivetran press](https://www.fivetran.com/press/fivetran-dbt-labs-complete-merger-to-create-the-data-infrastructure-for-trusted-ai-agents)

**Cube**
- Cube Core es la base open source; modelo con cubes (medidas, dimensiones, joins) y views, en YAML o JavaScript; pre-aggregations en Cube Store; APIs SQL (compatible Postgres con función MEASURE), REST, GraphQL, Meta API; MCP server y Chat API; los modelos portan entre Core y plataforma; la página no especifica licencia — [Cube docs](https://docs.cube.dev/docs/introduction)

**LookML (Looker)**
- Lenguaje de dependencias, independiente del dialecto, DRY; archivos model (explores, joins con sql_on) y view (dimension, dimension_group, measure); el generador SQL de Looker traduce consultas de Explore — [Google Cloud docs](https://docs.cloud.google.com/looker/docs/what-is-lookml)

**AtScale**
- 10-sep-2024: AtScale libera SML (Semantic Modeling Language) como estándar abierto: métricas, dimensiones, jerarquías, medidas semi-aditivas, many-to-many, composición/herencia; repo con modelos TPC-DS/AdventureWorks/Snowplow, SDK y CLI — [AtScale / BusinessWire vía búsqueda](https://www.businesswire.com/news/home/20240910415282/en) (snippet; la página devolvió 403). AtScale se unió a OSI en la actualización del 27-ene-2026 (Snowflake blog arriba). Arquitectura detallada (MDX/DAX/SQL, virtualización) no verificada: la página del producto dio 404.

**Snowflake Semantic Views**
- Objeto de esquema con tablas lógicas, facts, métricas, dimensiones, relaciones; DDL CREATE/ALTER/DESCRIBE/DROP SEMANTIC VIEW; vistas SEMANTIC_VIEWS etc. en INFORMATION_SCHEMA; Cortex Analyst y Cortex Agents las usan; YAML y Autopilot — [Snowflake docs](https://docs.snowflake.com/en/user-guide/views-semantic/overview)
- Estados: Summit 2-5 jun-2025: definir semantic views = GA, consultar (cláusula SEMANTIC_VIEW) = Preview — [Release notes](https://docs.snowflake.com/en/release-notes/2025/june-summit); consulta GA en release 9.25 (25-28 ago-2025), Snowsight GA 2-oct-2025, compartir GA 4-nov-2025, relationship paths en Preview mar-2026 [snippets de búsqueda] — [Release notes 9.25](https://docs.snowflake.com/release-notes/2025/9_25)

**Databricks Metric Views**
- Public Preview 29-may-2025 (requiere DBR 16.4+ o canal Preview) [snippet de búsqueda] — [Release notes may-2025](https://docs.databricks.com/aws/release-notes/product/2025/may)
- 2-abr-2026: "Unity Catalog Business Semantics is now GA"; implementación núcleo de Metric Views en camino a Apache Spark OSS (SPARK-54119, sin versión de Spark); soporte en Unity Catalog OSS v0.5 "coming soon"; materialización automática y creación por UI aún en Preview; mayoría de integraciones sólo lectura; Databricks participa en Apache Ossie — [Databricks blog](https://www.databricks.com/blog/redefining-semantics-data-layer-future-bi-and-ai)
- Concepto: separar definición de medidas de las dimensiones; consultas con función MEASURE; YAML v1.1 requiere DBR 17.2+ y añade metadata semántica (sinónimos, formatos) [snippets] — [Databricks docs](https://docs.databricks.com/aws/en/metric-views/); [YAML ref](https://docs.databricks.com/gcp/en/business-semantics/metric-views/yaml-reference)

**Text-to-SQL con grounding semántico**
- dbt Labs (7-abr-2026, J. Ganz y B. Perigaud): dataset ACME Insurance (data.world, 15 tablas 3NF), 11 preguntas x 20 corridas; sin modelado extra, text-to-SQL 64.5% (Sonnet 4.6 y GPT-5.3 Codex) vs Semantic Layer 72.7%; en preguntas sin saltos extra SL 100% vs 51-62%; en preguntas con demasiados saltos SL 0% vs hasta 100%; con modelos adicionales generados por LLM: SL 98.2% (Sonnet 4.6) y 100% (GPT-5.3); text-to-SQL sobre datos modelados 90.0% y 84.1%. Caveats del propio post: text-to-SQL recibió el esquema entero (optimista para casos grandes), un único dataset, sin intervalos de confianza, autor vende el producto; código abierto en dbt-labs/dbt-llm-sl-bench — [dbt blog](https://docs.getdbt.com/blog/semantic-layer-vs-text-to-sql-2026)
- Otras cifras (Snowflake BIRD 57% a 78%, Looker -66% errores, Strategy 88.2% vs 100%) son de vendors y sólo vi snippets; no citar como evidencia independiente — [búsqueda](https://docs.getdbt.com/blog/semantic-layer-vs-text-to-sql-2026?version=2)

### Inferences
- La convergencia es real pero joven: OSI/Ossie tiene spec v1 (ene-2026) y está en incubación sin versión fijada en el ROADMAP; los conversores existen, pero la interoperabilidad end-to-end entre motores no está verificada.
- El resultado del benchmark dbt sugiere que un semantic layer ayuda en lo que modela y falla en lo que no cubre; el mayor salto vino del modelado de datos (90%/84% text-to-SQL sobre datos modelados), no sólo de la capa semántica. (Inferencia sobre las cifras citadas.)
- Elegir semantic layer nativo de plataforma (Snowflake/Databricks) reduce piezas pero ata la definición al motor; dbt/Cube/AtScale son neutrales respecto al warehouse; Ossie reduciría la fricción de migración si madura. (Inferencia.)

### Gaps
- Fecha exacta de aceptación en la Incubadora (jun vs jul-2026): fuentes discrepan; no se verificó en el sitio de la ASF/lista general.
- Versión actual de la spec Ossie: no encontrada (ROADMAP no la da).
- Licencia de Cube Core (no verificada en esta sesión), AtScale GA/precios y arquitectura, GA exacto de Snowflake "query" (snippet), fecha de GA de Metric Views en notas de Databricks (el blog de abril 2026 es la fuente), estado de Metric Views en Spark upstream.
- Sin benchmark independiente de text-to-SQL con/sin capa semántica.

## 6. Marco de decisión (inferencia, basado en lo verificado arriba)

### Takeaway
No hay un estudio que valide umbrales; el marco es una síntesis razonada de las fuentes. Regla general: estrella (Kimball) para consumo; DV sólo con muchas fuentes volátiles o exigencia de auditoría y automatización; OBT como capa derivada medida; capa semántica sobre el modelo, nativa si la plataforma es única.

### Cited Findings
(Se apoya en hallazgos de las secciones 1-5. No hay hallazgos nuevos aquí.)

### Inferences
| Contexto | Recomendación |
|---|---|
| Equipo chico (1-5), pocas fuentes (<10), dominio único | Staging -> marts dimensionales (estrella, dimensiones conformadas, bus matrix); SCD2 sólo donde la historia importa; semantic layer nativo o dbt/MetricFlow. Evitar DV (WhereScape reconoce que 3-5 fuentes estables pueden ir con estrella) |
| Equipo mediano, múltiples dominios, fuentes cambiantes | Kimball con conformidad estricta + contratos dbt en las interfaces; considerar capa de integración si cambios de fuente rompen marts |
| Grande, muchas fuentes, M&A, regulado/auditable | Raw Vault (hub/link/sat) + Business Vault + marts estrella; requiere automatización (tooling certificado por DVA) y entrenamiento; PIT/bridge para rendimiento |
| Volatilidad alta de esquema fuente | Formatos con evolución segura (Iceberg/Delta), VARIANT/RECORD en raw, contrato en el borde de consumo |
| Regulatorio (reconstruir "lo que sabíamos entonces") | Modelado bitemporal (valid + transaction time); SCD2 sola no distingue correcciones tardías |
| Producto/journeys con eventos | Activity-style event table puede servir; verificar fit; mantener estrella para finanzas/inventario |
| BI con latencia crítica | OBT derivada como tabla/materialización, medir con carga propia (sección 2) |
| Agentes/text-to-SQL | Capa semántica gobernada (MetricFlow, Snowflake SV, Databricks MV, Cube) + datos modelados; validar con un benchmark propio |

### Gaps
- Umbrales (número de fuentes, tamaño de equipo) son criterios míos, sin fuente.
