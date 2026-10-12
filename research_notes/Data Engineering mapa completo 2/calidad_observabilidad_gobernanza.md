# Calidad, observabilidad, lineage, catálogos y gobernanza de datos (verificado con fuentes primarias, oct 2026)

Convenciones: [P] = fuente primaria (repo/doc oficial/PyPI); [V] = documento de proveedor (sesgo comercial); [T] = tercero/secundario; "inferencia" = juicio propio. Fechas de GitHub Releases aparecen sin año en la página; el año se infiere por contexto (hoy = 2026-10-12) y se marca. El acceso a la API de GitHub estaba bloqueado en la sesión, por eso se usaron páginas HTML de releases y PyPI/Maven.

## 1. Versiones, estado y licencias actuales (GX, Soda, Elementary, Deequ, DataHub, OpenMetadata, OpenLineage, ODCS)

### Takeaway
Todos siguen activos con releases de sep-oct 2026. Hallazgos que cambian el mapa previo: (a) Soda Core pasó de Apache-2.0 a Elastic License 2.0 (source-available, no OSI) y v4 es "data contracts" por defecto; (b) ODCS v3.2.0 SÍ está publicada (tag en GitHub, 8 sep), el "RFC" del pase previo ya está resuelto; (c) hay una discrepancia de licencia en OpenMetadata (repo Apache-2.0 vs. paquete PyPI "Collate Community License").

### Cited Findings
- **Great Expectations (GX Core)**: última 1.24.0 (07 oct; año inferido 2026), soporta Python 3.10-3.14; 1.23.2 (28 sep) corrige ruptura con SQLAlchemy 2.1 (publicado 2026-09-24). Licencia Apache-2.0 (PyPI). GX Cloud: opciones Developer (gratis), Team y Enterprise; la página oficial no publica precios. — [GitHub releases](https://github.com/great-expectations/great_expectations/releases) [P], [PyPI JSON](https://pypi.org/pypi/great-expectations/json) [P], [GX pricing](https://greatexpectations.io/pricing) [P]
- **Soda Core**: PyPI muestra 4.26.0 publicado 6 oct 2026, licencia "Proprietary" en los metadatos. El blog oficial anuncia cambio de Apache-2.0 a **Elastic License 2.0** (cabecera dice "Oct 8, 2026", cuerpo "Published Jan 27, 2026": fecha ambigua): prohíbe ofrecerlo como servicio gestionado a terceros, eludir license keys y quitar avisos; uso interno/producción, forks y consultoría siguen permitidos. El README de v4 lo define como "motor de verificación de data quality y data contracts" con YAML de contrato (`soda contract verify`); paquetes renombrados `soda-{datasource}` (v3 era `soda-core-{datasource}`, rama v3 separada). Release notes: primer release público de v4 = 4.0.5 (28 ene 2026), cambio rompiente de SodaCL/checks a contratos. La licencia exacta del código de v4 no figura en el blog (afecta "a Soda Core"); el LICENSE en main es ELv2. — [PyPI soda-core](https://pypi.org/project/soda-core/) [P], [blog licencia](https://soda.io/blog/soda-core-license-update-moving-to-elastic-license) [P/V], [GitHub LICENSE](https://github.com/sodadata/soda-core/blob/main/LICENSE) [P], [README](https://github.com/sodadata/soda-core) [P], [release notes (vía búsqueda)](https://docs.soda.io/soda-v4/release-notes/soda-core-release-notes) [P]
- **Soda Cloud precios**: Free $0/mes (SPUs gratuitas, sin tope numérico publicado), Team $750/mes (contratos colaborativos, no-code, SSO, RBAC, audit logs), Enterprise a medida. — [Soda pricing](https://www.soda.io/pricing) [V]
- **Elementary**: CLI open source Apache-2.0, última 0.26.1 (11 oct 2026); trabaja junto al paquete dbt `dbt-data-reliability`; Elementary Cloud es la oferta comercial (ML monitors, lineage columnar, catálogo). — [PyPI](https://pypi.org/project/elementary-data/) [P], [GitHub](https://github.com/elementary-data/elementary) [P/V]
- **Deequ**: Apache-2.0; librería Spark "unit tests for data"; Maven Central muestra 3.0.3-spark-3.5 (lastUpdated 2026-09-16), historial 2.0.x -> 3.0.x; README (desactualizado) dice 2.x soporta Spark 3.1-3.5 y 2.1+ requiere Java 11; PyDeequ es la interfaz Python. — [Maven metadata](https://repo1.maven.org/maven2/com/amazon/deequ/deequ/maven-metadata.xml) [P], [GitHub](https://github.com/awslabs/deequ) [P]
- **Pandera**: MIT, proyecto de Union.ai (mantenedor Niels Bantilan); valida pandas, polars, pyspark, ibis, dask, modin, pyarrow; banner de la versión 0.34.0. — [Pandera docs](https://pandera.readthedocs.io/en/stable/) [P]
- **DataHub**: Apache-2.0; PyPI `acryl-datahub` 1.7.0.14 estable (29 sep 2026); GitHub: v1.8.0rc4/rc5 (08 oct, pre-release) y parche LTS v1.6.0.3 (25 sep) centrado en hardening de seguridad (requiere Python 3.11, CVEs). — [PyPI](https://pypi.org/project/acryl-datahub/) [P], [LICENSE](https://github.com/datahub-project/datahub/blob/master/LICENSE) [P], [releases](https://github.com/datahub-project/datahub/releases) [P]
- **OpenMetadata**: 2.0.5 (08 oct), 2.0.4 (06 oct), 2.0.3 (30 sep), 2.0.2 (16 sep; "MCP tool consolidation", arreglos de data contracts). README y LICENSE del repo: Apache-2.0; Collate (empresa comercial) vende capacidades gestionadas. PERO PyPI `openmetadata-ingestion` 2.0.5.0 declara "Collate Community License Agreement". Contradicción no resuelta; una reseña de terceros sugiere que componentes IA nuevos van bajo licencia Collate, sin confirmar. — [releases](https://github.com/open-metadata/OpenMetadata/releases) [P], [GitHub](https://github.com/open-metadata/OpenMetadata) [P], [PyPI ingestion](https://pypi.org/project/openmetadata-ingestion/) [P], [búsqueda](https://www.modern-datatools.com/tools/openmetadata) [T]
- **OpenLineage**: 1.53.0 (01 sep), 1.52.0 (23 jul), 1.51.0 (09 jul); novedades: facets explícitos de lineage, Spark 4.2, `dbt_model` facet, soporte Unity Catalog OSS en Spark 4.0, Datadog FedRAMP. Docs: proyecto LF AI & Data "Graduate", modelo Run/Job/Dataset + facets. — [releases](https://github.com/OpenLineage/OpenLineage/releases) [P], [docs](https://openlineage.io/docs/) [P]
- **Marquez**: implementación de referencia de OpenLineage (servidor, API de lineage, UI); open-sourced por WeWork; la web no confirma gobernanza LF. — [marquezproject.ai](https://marquezproject.ai/) [P]
- **ODCS (Bitol)**: GitHub Releases lista v3.2.0 como "Latest" (08 sep, 16:13, autor jgperrin; año no mostrado, inferido 2026 porque v3.1.0 fue 08 dic 2025 y un post del 2 jun 2026 la describía "en progreso"). Highlights: bloque `context` para agentes IA, synonyms, variables, tipos vector/map/enum, measures/dimensions, deprecation, 9 nuevos tipos de server (Iceberg, HANA, Teradata, Exasol, Actian), 5 RFCs compartidas con ODPS. v3.1.0: relaciones (FK), nueva estructura `team`, métricas de calidad, tipos timestamp/time. v3.0.0 (20 oct 2024 inferido): Support y Servers. — [Releases](https://github.com/bitol-io/open-data-contract-standard/releases) [P], [tag v3.2.0](https://github.com/bitol-io/open-data-contract-standard/releases/tag/v3.2.0) [P], [post jgp.ai 2026-06-02](https://jgp.ai/2026/06/02/odcs-v3-2-and-odps-v1-1-making-ai-smart-about-your-data/) [T/autor del release]
- **Bitol / LF**: la home de Bitol se describe como "Linux Foundation AI & Data Incubation project" (no "graduated"; página "Last updated 2025-12-07"). — [bitol.io](https://bitol.io/) [P]
- **Data Contract Specification (datacontract.com) está DEPRECADA**: "we deprecate the Data Contract Specification", migrar a ODCS; soportada en Data Contract CLI y Entropy Data hasta fin de 2026; última versión 1.2.1. Data Contract CLI: MIT, soporta ODCS nativamente; comandos lint/test/changelog/breaking, exports (avro, dbt, jsonschema, sodacl, sql, terraform...). — [datacontract-specification](https://github.com/datacontract/datacontract-specification) [P], [CLI](https://github.com/datacontract/datacontract-cli) [P], [PyPI](https://pypi.org/pypi/datacontract-cli/json) [P] (versión 1.2.4, MIT)
- **PayPal -> ODCS**: PayPal abrió su plantilla (Apache-2.0) en mayo 2023; hoy el repo declara que "ha evolucionado y se llama ODCS". — [paypal/data-contract-template](https://github.com/paypal/data-contract-template) [P]

### Inferences
- Resolución ODCS: la afirmación del pase previo ("v3.2 es solo un RFC") es obsoleta; el estado correcto es v3.2.0 publicada. Sin embargo, la home de Bitol y la web de docs no mencionan v3.2 (cacheadas/desfasadas), así que conviene pinear versión por tag. El año de la release se infiere, no está en la página.
- Soda ya no es "open source" en sentido OSI para el core v4: para equipos que valoren OSI/Apache, GX Core y Elementary CLI son las opciones restantes; ELv2 solo restringe revender como servicio.
- Riesgo de gobernanza: los dos catálogos OSS dependen de un proveedor comercial (Acryl/DataHub Cloud, Collate); vigilar licencias de paquetes (caso Soda y la discrepancia de OpenMetadata).

### Gaps
- No se pudo verificar fecha exacta (año) de los releases de GitHub ni la licencia efectiva del subpaquete de OpenMetadata. No se leyó la versión estable de DataHub en GitHub (solo rc y LTS); PyPI de GX no entregó fecha de 1.24.0 (se usó GitHub). Versión actual de dbt-core no consultada.

## 2. Evidencia documentada de adopción de data contracts y trampas

### Takeaway
La evidencia cuantitativa es débil y patrocinada: la cifra más citada (61%) viene de un estudio BARC patrocinado por Actian sin metodología publicada en el artículo. Los casos "de referencia" (PayPal, GoCardless) están documentados como origen/arquitectura, no como resultados medidos; no encontré evidencia primaria de Netflix ni Convoy con resultados.

### Cited Findings
- BARC x Actian (artículo del 21 abr 2026): "61% de organizaciones encuestadas usa data contracts operativamente, en varios dominios o en proyectos concretos"; muestra ">300 respondientes" data leaders de varios sectores/regiones; sin desglose por rol/tamaño, sin fecha de campo ni redacción de preguntas; patrocinador Actian publica el artículo. Un resultado de búsqueda menciona otro estudio Drexel-Precisely (505 líderes) con la misma cifra, atribución dudosa. — [Actian](https://www.actian.com/blog/data-intelligence/barc-x-actian-research-data-products-enter-the-enterprise-roll-out-phase/) [V], [búsqueda](https://completeaitraining.com/news/data-contracts-gain-urgency-as-ai-exposes-weak-data/) [T]
- GoCardless (Andrew Jones): empezó a pensar en el problema en agosto 2020, escribió públicamente en abril 2021 y describió la implementación en diciembre 2021; usó un "consumer working group" (data scientists/ingenieros que revisan casos críticos y definen cambios); resumen secundario: priorizar comunicación sobre rigidez y dar incentivos. Libro "Driving Data Quality with Data Contracts" (Jones, Kevin Hu). Posts originales de GoCardless no recuperados. — [AtScale podcast](https://www.atscale.com/podcast/data-contracts-with-andrew-jones/) [T], [Bigeye interview](https://bigeye.com/the-observatory/andrew-jones-gocardless) [V]
- Convoy (Chad Sanderson): plataforma interna "Chassis" como fuente de verdad de eventos/entidades/relaciones; solo resúmenes de podcast, sin resultados cuantitativos. — [podbay](https://podbay.fm/p/1481793207/e/1686888000) [T]
- Netflix: no encontré caso documentado de data contracts con resultados (búsquedas devolvieron casos de negocio genéricos). Tratar cualquier afirmación como no verificada.
- Thoughtworks Radar: el blip OpenMetadata está en Assess (Vol. oct 2022, ya fuera del Radar actual). La ubicación de "Data contracts and observability" en un espejo de terceros aparece como Trial y como Assess en versiones distintas: no confirmada. — [Thoughtworks OpenMetadata](https://www.thoughtworks.com/radar/platforms/openmetadata) [P], [espejo](https://rubinlake.com/en/technology-radar/data-platforms-and-mlops/data-contracts-observability) [T]
- Mecanismos de enforcement verificables: dbt `contract: enforced` valida nombres/tipos en build y marca breaking changes (columna eliminada, tipo cambiado, constraint quitada v1.6+, modelo contractual eliminado v1.9+); solo modelos SQL table/incremental/view; el soporte de constraints depende de la plataforma (Postgres las aplica todas, Athena ninguna). — [dbt model contracts](https://docs.getdbt.com/docs/mesh/govern/model-contracts) [P]
- Schema Registry (Confluent): modo por defecto BACKWARD (no transitivo); 7 modos (BACKWARD, BACKWARD_TRANSITIVE, FORWARD, FORWARD_TRANSITIVE, FULL, FULL_TRANSITIVE, NONE); orden de upgrade: backward = consumidores primero, forward = productores primero; para Protobuf se recomienda BACKWARD_TRANSITIVE; JSON Schema depende de modelo abierto/cerrado. — [Confluent docs](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html) [P]
- Pitfalls ya citados (Aalto, tesis con 10 entrevistas; roles/ownership poco claros) del pase previo: [Aalto](https://aaltodoc.aalto.fi/items/9643d2ad-40ad-4cdb-a12d-792695ec30c1) [T]

### Inferences
- Los contratos eficaces combinan (1) esquema ejecutable en CI/registro (dbt contract, schema registry), (2) semántica/SLA/owner (ODCS), (3) proceso de cambio con consumidores. Trampas probables (inferencia, apoyada en GoCardless y Aalto): contratos sin dueño productor, sin incentivos, sobre tablas internas, y confundirlos con esquema.
- Usar el 61% solo con la etiqueta "encuesta patrocinada por proveedor, n>300, metodología no divulgada".

### Gaps
- Informe completo BARC no accedido; no hay encuesta independiente con metodología; sin resultados medidos de PayPal/GoCardless/Convoy/Netflix.

## 3. Open source vs comercial en observabilidad y catálogos; heurística "~20 ingenieros"

### Takeaway
La regla "~20 ingenieros" no tiene respaldo: la única cifra encontrada es una opinión de un post de Medium ("<15 construir, >20 comprar") sin metodología; las fuentes serias hablan de talento disponible, riesgo y TCO. Recomiendo descartarla o presentarla solo como opinión. Los precios de Monte Carlo/Bigeye/Atlan/Collibra/Alation no son públicos; solo existen estimaciones de terceros contradictorias.

### Cited Findings
- Búsqueda sobre build vs buy: única regla numérica = post de Medium (<15 build / >20 buy) sin metodología; Acceldata: decisión por talento, riesgo, TCO (vendor); Bigeye: "Build if you must, buy if you can" (vendor); Last9: llegar al 80% lleva semanas, el resto es lo caro. — [Medium](https://medium.com/@aidelearning/data-observability-in-2026-monte-carlo-vs-great-expectations-vs-soda-a-data-engineers-honest-7c8cab1b68f1) [T], [Acceldata](https://www.acceldata.io/blog/choosing-open-source-vs-paid-data-observability-solutions) [V], [Bigeye](https://www.bigeye.com/blog/data-observability-build-or-buy) [V], [Last9](https://last9.io/blog/build-vs-buy-observability-stack) [V]
- **Monte Carlo**: modelo de créditos de consumo + monitores; tiers Start (hasta 10 usuarios, 1.000 monitores, 10k llamadas API/día), Scale (SSO, SCIM, 50k), Enterprise (multi-workspace, chargebacks, 100k), Business Critical (instancia dedicada, DR regional); precios: "Request pricing". Se posiciona como "Agent Trust Platform for Data + AI Observability", 400+ clientes enterprise; ROI "375%" de un estudio Forrester (cifra del proveedor, no verificada). — [pricing](https://montecarlo.ai/pricing) [V], [home](https://montecarlo.ai/) [V]
- **Bigeye**: plataforma "AI Trust" (metadata, lineage, observabilidad, sensibilidad, gobernanza, MCP server, monitoring as code); sin precios publicados. — [bigeye.com](https://www.bigeye.com/) [V]
- **Metaplane**: adquirida por Datadog (anunciado 23 abr 2025; términos no divulgados; seguirá como "Metaplane by Datadog"); planes con tier gratis, precio por uso; column-level lineage, CI/CD de datos. — [TechCrunch](https://techcrunch.com/2025/04/23/datadog-acquires-ai-powered-observability-startup-metaplane) [T], [Metaplane](https://www.metaplane.dev/) [V]
- **Datadog Data Observability** (docs): quality monitoring ML, lineage, jobs monitoring, cost y performance de Spark/Databricks, catálogo, CI/CD; warehouses Snowflake, Databricks, BigQuery; sin precio ni estado GA/preview en la página. — [Datadog docs](https://docs.datadoghq.com/data_observability/) [V]
- **Anomalo**: "autonomous data system" con agentes (Table Observability, Data Quality...), despliegue SaaS o en VPC del cliente, SOC2 Type II; la web no especifica ML no supervisado. — [anomalo.com](https://www.anomalo.com/) [V]
- Estimaciones de precios catálogos (terceros, contradictorias): Atlan ~$25K-$150K/año; Alation ~$198K-$414K/año; Collibra ~$170K-$510K/año; negociado 15-40% bajo lista. Los datos por usuario/mes del mismo sitio se consideran poco fiables. — [CostBench](https://costbench.com/stats/data-catalog-pricing-2026/) [T]
- Elementary Cloud vs CLI; Soda ELv2 + cloud; GX Cloud: ver sección 1.

### Inferences
- Criterio de decisión más defendible (inferencia): comprar cuando haya muchas fuentes/equipos y poca capacidad de plataforma; construir/OSS cuando el stack sea dbt-céntrico y haya ingeniería de plataforma. El umbral de personas no se sostiene; usar número de fuentes, equipos consumidores, coste de incidentes y FTE de operación.
- Tras la compra de Metaplane por Datadog y el giro de Monte Carlo/Bigeye a "AI trust/agents", el mercado converge con catálogo+observabilidad+gobernanza; riesgo de lock-in.

### Gaps
- Precios reales de MC/Bigeye/Atlan/Collibra/Alation (no publicados); sin Gartner/Forrester primarios (paywall); no verifiqué la cifra Forrester 375%.

## 4. Blueprint mínimo viable de gobernanza (DAMA, DGI, equivalentes)

### Takeaway
DGI propone 10 componentes y separa "little g" (productos de datos, catálogos, definiciones, metadatos, controles) de "Big G" (derechos de decisión, responsabilidades, políticas). Un MVP práctico = quien decide + qué se gobierna + controles ejecutables, empezando por datos críticos.

### Cited Findings
- DGI Framework: 10 componentes: Mission and Value; Beneficiaries; Data Products; Controls; Accountabilities; Decision Rights; Policy and Rules; Process, Tools and Communication; Data Work Program; Participants. Outputs "little g": data products, catálogos, definiciones, metadatos, controles, checkpoints, mediciones; "Big G": decision rights, accountabilities, policies. Una Oficina de Gobierno de Datos impulsa el programa. — [DGI](https://datagovernance.com/the-dgi-data-governance-framework/) [P]
- DAMA-DMBOK: la web de DAMA habla de la 2ª edición, y de un proyecto "DAMA-DMBOK 3.0" iniciado en 2025 como "evergreening"; sin fecha de lanzamiento. La página no enumera las áreas de conocimiento (la lista de 11 áreas no se confirmó aquí). — [DAMA](https://dama.org/learning-resources/dama-data-management-body-of-knowledge-dmbok/) [P]
- Microsoft Purview: portfolio unificado (seguridad, gobernanza, cumplimiento); gobernanza = Data Map + Unified Catalog; el Unified Catalog factura por "activo gobernado" (solo activos vinculados a data products, CDEs o calidad; ejemplo oficial: 200 activos = $100 por 30 días, ≈$0,50/activo/mes derivado; los precios por región aparecen como "$-" en la fuente). Precio de Data Map y calidad no obtenido. — [Purview overview](https://learn.microsoft.com/en-us/purview/purview) [P], [pricing](https://azure.microsoft.com/en-us/pricing/details/purview/) [P]
- Dataplex Universal Catalog fue renombrado **Knowledge Catalog** el 10 abr 2026 (API/IAM sin cambios): discovery, lineage a nivel de columna, data quality con escaneos ML (outliers y frescura), profiling, data products con SLA/contratos/owners, glosario. — [Google Cloud](https://docs.cloud.google.com/dataplex/docs/introduction) [P]
- Unity Catalog (Databricks): gobernanza unificada con RBAC/ABAC, row/column filters, lineage, monitoreo de calidad con perfiles y alertas; habilitado por defecto para workspaces nuevos desde 8 nov 2023. UC OSS: Apache-2.0, proyecto sandbox de LF AI & Data; APIs compatibles con Hive metastore e Iceberg REST. — [Databricks docs](https://docs.databricks.com/aws/en/data-governance/unity-catalog/) [P], [GitHub UC](https://github.com/unitycatalog/unitycatalog) [P]
- Snowflake (Horizon/Data Quality): Data Metric Functions + expectations; anomaly detection solo para volumen y freshness; requiere Enterprise Edition; cómputo serverless facturado como "Data Quality Monitoring"; no soporta hybrid tables/streams/shares. — [Snowflake docs](https://docs.snowflake.com/en/user-guide/data-quality-intro) [P]
- AWS Lake Formation: permisos finos a nivel columna/fila/celda sobre Glue Data Catalog, LF-Tags (TBAC) y ABAC, auditoría con CloudTrail, catálogos federados (Redshift, S3 Tables), compatibilidad con Iceberg REST. Lake Formation es control de acceso más que catálogo de negocio. — [AWS docs](https://docs.aws.amazon.com/lake-formation/latest/dg/what-is-lake-formation.html) [P]
- MDM: el Magic Quadrant de Gartner MDM 2026 (publicado 6 abr 2026) evaluó 20 proveedores; Reltio y Profisee afirman ser Leaders (material de proveedor); Informatica figura como "Salesforce (Informatica)"; Semarchy aparece en la lista; posicionamientos completos tras paywall. — [Gartner abstract](https://www.gartner.com/en/documents/7683461) [P/paywall], [Profisee](https://profisee.com/resources/2026-gartner-magic-quadrant-for-master-data-management-solutions/) [V], [Reltio](https://www.reltio.com/?p=27221) [V]
- Estándares de calidad (ISO 8000, ISO/IEC 25012): las páginas de ISO devolvieron 403; no verificados primariamente en esta pasada.

### Inferences
Blueprint (inferencia propia; mapea a componentes DGI y a DAMA "Data Governance"/"Metadata"/"Data Quality"):
1. Charter de 1 página: misión, beneficiarios, alcance (DGI 1-2).
2. Roles y decision rights: owner por dominio/data product, steward nominado, data council trimestral pequeño (DGI 5-6, 10); RACI de cambios breaking.
3. Inventario de datos críticos (CDEs) con tier y owner, en el catálogo elegido (DataHub/OpenMetadata/Unity/Purview/Knowledge Catalog según plataforma).
4. Controles ejecutables: contratos ODCS o dbt contracts + tests/Soda/GX en tier-1; severidades y runbooks (DGI "Controls").
5. Políticas: clasificación, retención, acceso (ABAC/tags), registro de excepciones (DGI 7).
6. Medición: % activos tier-1 con owner/descripción/contrato; incidentes y MTTR; frescura vs SLO.
7. Cadencia: revisión trimestral; evolucionar a MDM solo si hay entidades maestras duplicadas entre sistemas (clientes, productos).

### Gaps
- No se verificó la lista de 11 áreas DMBOK (conocimiento general: gobernanza, arquitectura, modelado, almacenamiento, seguridad, integración, documentos, master/reference data, DW/BI, metadatos, calidad); DCAM (EDM Council) no consultado; ISO 8000/25012 sin fuente primaria; ni Collibra/Atlan/Alation docs primarios.

## 5. Calidad, testing, WAP, anomalías y SLOs (soporte técnico)

### Takeaway
Pirámide: contratos/esquema -> tests deterministas (dbt, GX, Soda, Deequ, Pandera) -> WAP en tablas críticas -> monitorización estadística (frescura/volumen/esquema). Las plataformas cloud ya incluyen monitores básicos (Snowflake DMF, Dataplex, Unity, Datadog).

### Cited Findings
- dbt unit tests: introducidos en dbt 1.8; definidos en YAML bajo `models/`; formatos dict/csv/sql; solo modelos SQL del proyecto actual; no para materialized views ni recursive SQL; se recomienda ejecutarlos solo en dev/CI; en 1.11+ se pueden excluir de producción. — [dbt docs](https://docs.getdbt.com/docs/build/unit-tests) [P]
- WAP en Iceberg: la página de branching existe (casos de uso "Audit Branch"), pero el cuerpo no se recuperó; WAP con ramas/AWS Glue Data Quality ver pase previo. — [Iceberg branching](https://iceberg.apache.org/docs/latest/branching/) [P], [AWS blog](https://aws.amazon.com/blogs/big-data/build-write-audit-publish-pattern-with-apache-iceberg-branching-and-aws-glue-data-quality/) [V]
- Nessie: "Transactional Catalog for Data Lakes with Git-like semantics", Apache-2.0. — [GitHub](https://github.com/projectnessie/nessie) [P]
- Snowflake y Dataplex ofrecen anomaly detection integrado (ver sección 4). Sobre el volumen de Deequ: uso en Spark a gran escala (descripción oficial).
- FOCUS (FinOps): especificación abierta de FinOps Foundation/Linux Foundation, versión 1.4; generadores: Snowflake y Databricks en v1.3, AWS/Azure/GCP en v1.2. — [FOCUS](https://focus.finops.org/) [P]
- FinOps de datos, Snowflake: atribución con object tags (warehouses/usuarios) y query tags; vistas TAG_REFERENCES, WAREHOUSE_METERING_HISTORY, QUERY_ATTRIBUTION_HISTORY; limitaciones: el coste por query excluye idle time y solo cubre cómputo de warehouse (no storage, transferencia, serverless). — [Snowflake docs](https://docs.snowflake.com/en/user-guide/cost-attributing) [P]
- FinOps Databricks: `system.billing.usage` con `custom_tags`, `usage_metadata` (job_id, warehouse_id), correcciones vía RETRACTION/RESTATEMENT; disponibilidad ~12 h. — [Databricks docs](https://docs.databricks.com/aws/en/admin/system-tables/billing) [P]
- Datadog añade Cost and performance para Spark/Databricks. — [Datadog](https://docs.datadoghq.com/data_observability/) [V]

### Inferences
- SLOs de datos (inferencia): SLI = frescura, completitud de volumen, tasa de verificación de contrato; SLO por data product tier-1 con error budget. Sin fuente primaria de Google SRE aplicada a datos en esta pasada.
- Herramientas de coste (Select, Slingshot, Unravel) no verificadas.

### Gaps
- Sin fuente primaria para Delta (constraints, CHECK), lakeFS hooks (la URL redirigió), Iceberg WAP exacto, Great Expectations vs Soda comparativa independiente, Elementary features detalladas, y ejemplos de SLO de datos.
