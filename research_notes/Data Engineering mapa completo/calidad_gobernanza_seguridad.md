# Calidad, observabilidad, gobernanza, seguridad y cumplimiento en Data Engineering (estado a oct 2026)

Nota metodológica: investigación limitada (~12 llamadas). Las afirmaciones con enlace provienen de fuentes consultadas; lo marcado "[conocimiento previo, no verificado en esta sesión]" va en Inferencias y debe verificarse antes de citarse. Gran parte de la bibliografía de herramientas es de proveedores o afiliada: señalado donde aplica.

## 1. Cómo implementar borrado GDPR (art. 17) en lakehouses Iceberg/Delta

### Takeaway
Un DELETE lógico no borra bytes: en Delta hacen falta DELETE/MERGE + VACUUM (+ REORG ... APPLY (PURGE) si hay deletion vectors); en Iceberg DELETE + compactación (rewrite_data_files) + expire_snapshots + remove_orphan_files, en ese orden. Además hay que propagar a tablas derivadas, fuentes upstream (Kafka, ficheros), backups y cachés; la alternativa estructural es separar PII (tabla de identidad) o crypto-shredding.

### Cited Findings
- Delta (Databricks): lo más seguro es el borrado completo; si PII y no-PII están separadas por una clave no natural (p. ej. user_id) se pueden borrar solo columnas PII. Para borrados masivos se recomienda MERGE contra una tabla de control de solicitudes. — [Databricks GDPR/Delta](https://docs.databricks.com/aws/en/security/privacy/gdpr-delta)
- Delta retiene historial (incluidos registros borrados) 30 días por defecto; VACUUM elimina versiones antiguas de forma permanente. — [Databricks GDPR/Delta](https://docs.databricks.com/aws/en/security/privacy/gdpr-delta)
- Con deletion vectors habilitados hay que ejecutar además `REORG TABLE ... APPLY (PURGE)` para eliminar físicamente los registros; aplica a tablas Delta, materialized views y streaming tables. — [Databricks GDPR/Delta](https://docs.databricks.com/aws/en/security/privacy/gdpr-delta)
- Propagación downstream: materialized views procesan borrados de fuente pero requieren refresh y mantenimiento; streaming tables se rompen ante cambios no-append (usar skipChangeCommits o full refresh). Riesgo: un full refresh con fuente cuya retención ya expiró (ej. Kafka 7 días) puede perder datos. GDPR/CCPA alcanzan también a Kafka, ficheros y BBDD fuera de Delta. La ofuscación puede permitir reidentificación; a menudo hace falta borrado total. — [Databricks GDPR/Delta](https://docs.databricks.com/aws/en/security/privacy/gdpr-delta)
- Iceberg v3: un delete escribe un deletion vector (bitmap de posiciones en un fichero Puffin) y las filas siguen en el data file; las snapshots antiguas conservan los datos (history.expire.max-snapshot-age-ms por defecto 5 días); la compactación (rewrite_data_files) es el paso que reclama físicamente; luego expire_snapshots y finalmente remove_orphan_files (al final, para no perder ficheros retenidos por snapshots a expirar). — [Resumen vía búsqueda: Dremio](https://www.dremio.com/subsurface/apache-iceberg-and-the-right-to-be-forgotten/), [datalakehousehub](https://datalakehousehub.com/blog/gdpr-hard-deletes-on-iceberg), [AWS Prescriptive Guidance Iceberg v3](https://docs.aws.amazon.com/prescriptive-guidance/latest/apache-iceberg-on-aws/table-spec-v3.html)
- Iceberg v3 row lineage (_row_id, _last_updated_sequence_number) es tracking de cambios; AWS indica que el upgrade no hace backfill histórico. — [AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/apache-iceberg-on-aws/table-spec-v3.html)
- Dremio (proveedor) describe la inmutabilidad de Iceberg como opuesta al borrado por defecto y menciona crypto-shredding como vía para cubrir todas las copias. — [Dremio](https://www.dremio.com/subsurface/apache-iceberg-and-the-right-to-be-forgotten/)
- Criterio de identificabilidad: CJEU EDPS v SRB (C-413/23 P, 4 sep 2025) aclara que datos seudonimizados pueden no ser personales para un receptor que no puede reidentificar (resumen secundario; leer sentencia). EDPB Opinion 28/2024 (17 dic 2024): modelos de IA entrenados con datos personales no son siempre anónimos; evaluación caso a caso. — [IAPP](https://iapp.org/news/a/edpb-weighs-in-on-key-questions-on-personal-data-in-ai-models), [CMS](https://cms.law/en/bel/legal-updates/edpb-opinion-28-2024-key-takeaways-on-processing-personal-data-in-the-context-of-ai-models)

### Inferences
- Receta práctica (síntesis): (1) registro de solicitudes DSAR con SLA de 1 mes (plazo del art. 12 GDPR [conocimiento previo]); (2) diseñar para borrar: PII aislada en pocas tablas con clave subrogada, particionado/clustering por subject id para que el rewrite sea barato; (3) batch periódico (semanal/mensual) de borrados agrupados en lugar de uno a uno, porque cada borrado reescribe ficheros; (4) tras DELETE, ejecutar el pipeline de purga con retención de time-travel acortada para tablas con PII (o excluir PII del time travel); (5) propagar a silver/gold/feature stores/índices vectoriales/exports; (6) backups: política de expiración documentada (los reguladores suelen aceptar "put beyond use" con rotación, [conocimiento previo, verificar con DPO]); (7) evidencia auditable del borrado.
- Crypto-shredding (clave por sujeto en KMS, borrar la clave) evita reescrituras pero añade complejidad de gestión de claves y rendimiento; apropiado para PII en streams/logs inmutables o múltiples copias. [conocimiento previo parcialmente respaldado por Dremio]
- Conflicto con retención legal (fiscal, AML): el derecho al olvido tiene excepciones; el borrado debe ser selectivo por base legal.
- Conflicto de tensiones: tiempo de retención de snapshots corto reduce capacidad de rollback/WAP/auditoría; se necesita política diferenciada por clase de dato.

### Gaps
- No se consultaron las docs oficiales de Iceberg (maintenance, spec v3) ni de Delta/OSS (no Databricks) sobre VACUUM/UniForm; las fuentes de Iceberg son blogs de proveedores. Verificar orden y parámetros por motor/versión.
- No hay guía regulatoria específica (EDPB/ICO/CNIL) sobre si el borrado diferido por mantenimiento y backups cumple el art. 17; no encontrada.
- Interacción de deletion vectors v3 con row lineage y borrado físico: no verificada.

## 2. Contratos de datos: adopción real y trampas

### Takeaway
ODCS (Bitol, Linux Foundation AI & Data) es el estándar abierto de referencia con ecosistema (DataHub, Data Contract CLI); la adopción está limitada más por ownership/organización que por tecnología. Hay poca evidencia independiente cuantitativa.

### Cited Findings
- ODCS es un estándar YAML abierto y neutral mantenido por Bitol bajo LF AI & Data; v3 amplió el modelo de esquema (jerárquico, streaming, no estructurado) y añadió sección de soporte/canales; v3.1.0 añade relaciones entre propiedades, validación JSON Schema más estricta y SLAs ejecutables, compatible con v3.0. — [Bitol v3.1.0](https://bitol.io/bitol-announces-odcs-v3-1-0-stronger-smarter-and-stricter/), [DataHub ODCS](https://docs.datahub.com/docs/generated/ingestion/sources/odcs), [Data Contract CLI](https://docs.datacontract.com/docs/open-data-contract-standard.md)
- Un post de Substack menciona un RFC aprobado para ODCS v3.2 (2026-05-19) con bloque "context" para IA; no confirmado en página oficial. La graduación de Bitol en LF AI & Data solo aparece en un snippet de la home. — [Substack](https://dataintelligenceplatform.substack.com/p/odcs-32-and-odps-11-making-ai-smart), [Bitol](https://bitol.io/)
- Estudio BARC 2026 (patrocinado por Actian, 308 encuestados): retos "técnicos y organizativos" al escalar data products y contratos; contenido completo no accesible. — [BARC](https://barc.com/research/data-products-contracts-2026/)
- Tesis de Aalto (10 entrevistas, un solo caso): barreras = tensión autonomía local vs dirección central, protección de datos vs democratización, falta de claridad de roles/ownership. — [Aalto](https://aaltodoc.aalto.fi/items/9643d2ad-40ad-4cdb-a12d-792695ec30c1)
- Opinión de experto citada: acumular contratos sin SOPs fuertes crea deuda técnica y administrativa; la responsabilidad operativa debe seguir en productores y consumidores. — [CompleteAITraining](https://completeaitraining.com/news/data-contracts-gain-urgency-as-ai-exposes-weak-data/)

### Inferences
- Trampas habituales [conocimiento previo]: contratos escritos pero no ejecutados en CI (documentación muerta); productores sin incentivo; contratos sobre tablas internas en vez de interfaces estables; sobrecoste de versionado/breaking changes; confundir contrato con esquema (falta semántica, SLA, ownership). Mitigación: empezar por 5-10 interfaces críticas (eventos de dominio, tablas que alimentan finanzas/ML), enforcement en CI + en runtime (schema registry, tests dbt `contract: enforced`), y política de breaking change.
- Alternativas: dbt model contracts + versions, Protobuf/Avro + schema registry, Data Contract spec (datacontract.com) y ODCS convergiendo hacia ODCS.

### Gaps
- Sin datos independientes de tasa de adopción real; la cifra "61%" citada en prensa es de atribución confusa. No se verificó la especificación de Data Contract Specification ni su estado de deprecación frente a ODCS.

## 3. Calidad de datos: dimensiones, testing, anomalías, WAP

### Takeaway
Combinar tests deterministas en el pipeline (dbt tests/GX/Soda) con auditoría WAP en tablas críticas y monitorización estadística (Elementary/plataformas). WAP sobre ramas Iceberg es patrón consolidado a coste de latencia.

### Cited Findings
- WAP en Iceberg: escribir a una rama de staging, auditar, y hacer fast-forward a main si pasa; coste: latencia adicional. Configuración Spark: `write.wap.enabled`, rama por ejecución (Cloudera). Netflix audita sobre snapshot oculto. — [AWS Big Data blog](https://aws.amazon.com/blogs/big-data/build-write-audit-publish-pattern-with-apache-iceberg-branching-and-aws-glue-data-quality/), [Cloudera](https://community.cloudera.com/t5/Developer-Blogs/Iceberg-WAP-Failsafe-ETL-with-Iceberg-and-CDE/m-p/413008), [resumen Netflix](https://vutr.substack.com/p/how-does-netflix-ensure-the-data)
- Soda: núcleo open source (soda-core) + plataforma comercial, YAML/SodaCL; Great Expectations: framework Python open source con GX Cloud opcional; precios de comparativas (Soda Team $750/mes) de fuente de terceros. — [DataExpert comparación](https://www.dataexpert.io/blog/soda-vs-great-expectations-data-quality-tools)
- Elementary: observabilidad dbt-native, self-hosted o cloud; limitado a modelos dbt. — [Medium comparativa](https://medium.com/@aidelearning/data-observability-in-2026-monte-carlo-vs-great-expectations-vs-soda-a-data-engineers-honest-7c8cab1b68f1)

### Inferences
- Dimensiones estándar (DAMA): completitud, unicidad, validez, exactitud, consistencia, oportunidad (freshness), integridad [conocimiento previo]. Deequ: librería Spark/AWS, adecuada para volúmenes grandes en Spark. Circuit breaker: abortar el DAG aguas abajo ante fallo severo; severidad warn/error para evitar alert fatigue.
- Madurez: dbt tests y GX alta; WAP/branching media-alta (depende del catálogo: Nessie, Glue, Polaris, Snowflake/Databricks lo soportan en distinto grado, no verificado); anomaly detection ML es heterogénea y la calidad de las señales es difícil de evaluar sin pilotos.

### Gaps
- No se verificaron releases 2026 de GX/Soda/Elementary ni adquisiciones; Deequ y dbt unit tests sin fuente primaria.

## 4. Observabilidad: build vs buy, lineage, SLOs, FinOps

### Takeaway
Para equipos pequeños, open source (Elementary + OpenLineage/Marquez + alertas propias) basta; las plataformas (Monte Carlo, Bigeye) justifican coste con muchas fuentes/equipos y detección automática. Gran parte de la literatura es de proveedor.

### Cited Findings
- Una comparativa sitúa el cruce build/buy en torno a >20 ingenieros; otra dice que las herramientas son "apuestas distintas" sobre dónde gastar ingeniería, licencias y paciencia. Monte Carlo: consumo, seis cifras anuales en enterprise; Bigeye: auto-thresholding. Las plataformas gestionadas aún requieren ingeniería. — [Medium](https://medium.com/@aidelearning/data-observability-in-2026-monte-carlo-vs-great-expectations-vs-soda-a-data-engineers-honest-7c8cab1b68f1), [datadrivendaily](https://datadrivendaily.com/data-observability-tools-compared-a-guide-for-2026/)
- OpenLineage: estándar de eventos de lineage; Marquez es la implementación de referencia (eventos -> PostgreSQL, API de grafo, UI), con alcance deliberadamente solo lineage. Integraciones: Airflow (provider nativo desde 2.7), dbt, Spark, Flink, Dagster, GX. Column-level lineage es una facet del spec. Fuentes son blogs; gobernanza (LF AI & Data vs CNCF) conflictiva entre fuentes, LF AI & Data mejor respaldada. — [Adaltas](https://www.adaltas.com/en/2024/02/19/openlineage-introduction/), [pdpspectra](https://pdpspectra.com/blog/openlineage-column-level-lineage), [LF AI&Data](https://lf-aidata.atlassian.net/wiki/x/HwXJ)

### Inferences
- SLOs de datos [conocimiento previo]: freshness, volumen, tasa de éxito de contratos; definir SLI por producto de datos con error budget; SLA solo hacia consumidores externos.
- FinOps de datos: no se investigó con fuentes. Prácticas conocidas: tagging por equipo/producto, vistas de consumo (Snowflake ACCOUNT_USAGE, Databricks system tables), alertas de presupuesto, optimización de queries; herramientas: Select, Capital One Slingshot, Unravel [conocimiento previo, no verificado].

### Gaps
- Sin fuentes primarias sobre Monte Carlo/Bigeye (precios, capacidades), cost observability/FinOps, ni métricas de adopción de OpenLineage.

## 5. Gobernanza: catálogos, linaje, ownership, gobierno mínimo viable

### Takeaway
Catálogo: DataHub/OpenMetadata (OSS) si hay capacidad de ingeniería; Atlan (gestionado, mid-size); Collibra (regulado/enterprise); Unity Catalog por defecto en Databricks, no como catálogo global. Coste oculto del OSS: 0,25-1,0 FTE según un análisis. Fuentes muy sesgadas.

### Cited Findings
- DataHub: preferido por equipos con ingeniería, requiere operar infraestructura (Kafka según una fuente); OpenMetadata: calidad de datos y data contracts nativos y servidor MCP según su propia web, percibido como más joven; ambos Apache. Atlan recomendado para mid-size; Collibra para regulados, seis-siete cifras anuales; claims de Gartner/Forrester provienen de materiales del proveedor. Unity Catalog: embebido en plataforma. — [daily.dev](https://daily.dev/posts/openmetadata-vs-datahub-vs-amundsen-vs-commercial-2026--upeyjiiqu.md), [open-metadata.org](https://open-metadata.org/llms.txt), [pdpspectra](https://pdpspectra.com/blog/data-catalog-datahub-vs-atlan-vs-collibra), [datadrivendaily](https://datadrivendaily.com/data-catalog-tools-compared-the-2026-guide/)

### Inferences
- Gobierno mínimo viable (mid-size, síntesis propia): (1) inventario de data products/tablas críticas con owner nominal y tier; (2) catálogo ligero auto-ingestado (dbt docs/OpenMetadata) con descripciones en las top 20% tablas; (3) clasificación PII en origen + RBAC/masking por defecto; (4) contratos+tests+alertas en interfaces tier-1; (5) proceso DSAR y registro de tratamientos (RoPA); (6) revisión trimestral con un data council pequeño. Evitar comité pesado y plataforma antes de proceso.
- Master data/MDM (Reltio, Informatica, Semarchy, Profisee) y data mesh/products: no investigados; ODPS (Open Data Product Standard) de Bitol aparece mencionado en fuentes secundarias.
- Purview (Azure) y lineage a nivel columna en catálogos: no investigados con fuentes.

### Gaps
- Sin Gartner/Forrester primarios (paywall); sin pruebas independientes de OpenMetadata vs DataHub; Purview, MDM, DAMA-DMBOK no consultados.

## 6. Seguridad y cumplimiento (cifrado, acceso, PII, regulación)

### Takeaway
Regulación con fechas móviles: Data Act aplicable desde 12 sep 2025; AI Act con retraso de alto riesgo vía Digital Omnibus (acuerdo provisional, publicación final sin confirmar). Controles técnicos (RBAC/ABAC, masking, tokenización, KMS) son conocimiento estándar pero no fueron verificados con fuentes aquí.

### Cited Findings
- EU Data Act aplicable desde 12 sep 2025; normas de switching entre nubes vigentes; cargos de egress por cambio de proveedor deben eliminarse desde 12 ene 2027 (hasta entonces solo costes reales); uso multi-cloud paralelo permite egress a coste real. Una guía (sota.io) dice sep 2027, contradicho por la mayoría y no verificable. — [Travers Smith](https://www.traverssmith.com/knowledge/knowledge-container/the-data-acts-changes-to-cloud-services-contracts-tipping-the-scales-on-switching/), [Cooley](https://www.cooley.com/news/insight/2025/2025-09-08-paas-iaas-or-saas-be-aware-new-switching-rules-will-become-applicable-in-eu); contradice [sota.io](https://sota.io/blog/eu-data-act-2025-cloud-switching-rights-developer-guide)
- AI Act Digital Omnibus: acuerdo provisional 7 mayo 2026; alto riesgo Anexo III pasa a 2 dic 2027 y Anexo I a 2 ago 2028; Parlamento votó 16 jun 2026; adopción formal/OJ no confirmada en las fuentes. Transparencia art. 50 en gran parte en calendario original. — [Gibson Dunn](https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/), [Sidley](https://datamatters.sidley.com/2026/06/22/eu-lawmakers-reach-provisional-agreement-to-delay-key-eu-ai-act-obligations/)
- Seudonimización y anonimato: ver CJEU SRB y EDPB 28/2024 en sección 1.

### Inferences
- Controles [conocimiento previo, no verificado]: cifrado en reposo/tránsito con CMK y rotación; RBAC base + ABAC por etiquetas (Unity Catalog, Snowflake tags, Lake Formation LF-TBAC, Ranger); row/column-level security y dynamic masking; tokenización (vault vs format-preserving) para PCI; descubrimiento PII con Macie/Purview/Presidio/BigID; secretos en Vault/Secrets Manager con credenciales efímeras/OIDC; zero trust = identidad por workload, mínimo privilegio, segmentación. Marcos: GDPR, CCPA/CPRA, HIPAA (BAA, PHI), SOC 2 (evidencia de controles), PCI DSS 4.0 (alcance mínimo, tokenizar).
- Residencia de datos: regiones UE + controles de transferencia (SCC, Data Privacy Framework); AI Act relevante para gobernanza de datos de entrenamiento (art. 10) en alto riesgo, ahora con plazo posterior.

### Gaps
- Texto oficial de GDPR, Data Act y AI Act no leído directamente; HIPAA/PCI/SOC2/CCPA, ABAC/masking/tokenización y secretos sin fuentes en esta sesión; estado final del Omnibus (publicación OJ) sin confirmar.
