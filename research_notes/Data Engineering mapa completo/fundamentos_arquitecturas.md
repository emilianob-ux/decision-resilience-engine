# Data Engineering: fundamentos y arquitecturas de referencia (a oct 2026)

Nota de método: la sesión tuvo ~9 llamadas de búsqueda/fetch. Los hechos con enlace provienen de páginas leídas en esta sesión. Todo lo marcado "[conocimiento general, no verificado en sesión]" viene de formación previa del investigador (libros, papers, docs conocidos) y NO se re-verificó contra fuentes actuales; el redactor debe tratarlo como hipótesis a contrastar. No se pudo acceder a engineering.linkedin.com (404) ni se consultaron blogs de Uber/Netflix/Airbnb.

## 1. Lambda vs Kappa vs lakehouse unificado: trade-offs reales hoy

### Takeaway
Kreps (2014) planteó Kappa como alternativa a Lambda por el costo de mantener lógica duplicada en dos sistemas; en 2025-26 la discusión se desplazó a "streaming + formatos de tabla abiertos (Iceberg/Delta)" donde batch y streaming escriben/leen las mismas tablas. Lambda sigue en uso por costo/pragmatismo; Kappa puro es "simple en teoría, difícil en la práctica". La evidencia disponible es mayormente de opinión/vendor, no benchmarks.

### Cited Findings
- Kreps: el problema central de Lambda es implementar las mismas transformaciones en un sistema batch y en uno de streaming y mantenerlas sincronizadas; operar y depurar dos sistemas distribuidos es costoso; los frameworks de abstracción (Summingbird) solo exponen la intersección de capacidades — [Kreps, Questioning the Lambda Architecture](https://www.oreilly.com/radar/questioning-the-lambda-architecture/)
- Kappa según Kreps: conservar el log de entrada (Kafka, retención = ventana de reprocesamiento); al cambiar el código, lanzar un segundo job desde el inicio del log hacia una tabla nueva y conmutar al alcanzarla; ~2x almacenamiento de salida temporal; su evidencia es de LinkedIn con Samza — [Kreps](https://www.oreilly.com/radar/questioning-the-lambda-architecture/)
- Kreps reconoce que Lambda "resuelve un problema importante" (batch que no da baja latencia + stream que no reprocesa) y lo llama un "estado temporal" por limitaciones de herramientas; recomienda batch si no hay sensibilidad a latencia, stream si la hay, y no ambos "salvo que sea imprescindible" — [Kreps](https://www.oreilly.com/radar/questioning-the-lambda-architecture/)
- Confluent Tableflow materializa topics de Kafka como tablas Iceberg o Delta (schematización, evolución de esquema, CDC, publicación a catálogo), frescura ~5 min, catálogos Glue/Unity/Polaris/Snowflake Open Catalog; Delta solo con storage propio; no disponible en Confluent Platform — [Confluent docs](https://docs.confluent.io/cloud/current/topics/tableflow/overview.html)
- Kai Waehner (comentarista centrado en Kafka, con sesgo de vendor) sostiene que un único pipeline en tiempo real encaja mejor que las capas batch+RT de Lambda y que los table formats abiertos refuerzan Kappa — [Waehner blog](https://www.kai-waehner.de/blog/tag/delta-lake/)
- Contrapunto: charla de Fresha en Confluent Current London 2026 afirma "Lambda no está muerto": materializan tablas cada 20 min y fusionan eventos CDC en vivo vía vistas en consulta, como compromiso de costo — [Current 2026](https://current.confluent.io/post-conference-videos-26/lambda-architecture-in-2025-kafka-views-and-the-evolving-data-platform-ldn26)
- Blog personal (no revisado por pares) describe el patrón 2025 "unificado sobre lakehouse" (Flink + Iceberg, batch y streaming escriben a las mismas tablas), recomienda Iceberg para proyectos nuevos y Delta si el entorno es Databricks, y nota que Kappa es "teóricamente simple, prácticamente difícil" — [youngju.dev](https://www.youngju.dev/blog/culture/2026-04-15-streaming-vs-batch-redefined-complete-guide-flink-risingwave-materialize-cdc-streaming-sql-deep-dive-guide-2025.en)

### Inferences
- Trade-off real hoy: Lambda = dos rutas de código pero madurez y costo controlable (batch barato + capa de baja latencia acotada); Kappa = una ruta de código pero exige log retenido/tiered storage, reprocesos costosos, estado grande y habilidad en streaming; lakehouse unificado = una sola capa de almacenamiento (ACID, time travel, upserts) con latencia de minutos, NO sub-segundo; para sub-segundo se sigue necesitando Kafka/Flink o un OLAP en tiempo real (Pinot/Druid/ClickHouse) delante.
- La convergencia (Tableflow, Flink+Iceberg, Spark Structured Streaming/ Delta, Snowflake Dynamic Tables) sugiere que la pregunta pasó de "dos pipelines vs uno" a "qué SLA de frescura justifica el costo de streaming"; con frescura >=1-5 min la opción lakehouse con micro-batch suele dominar.
- [conocimiento general, no verificado en sesión] Costes ocultos del lakehouse streaming: archivos pequeños y compaction, commits frecuentes en Iceberg/Delta, conflictos de concurrencia, GC de snapshots; el paper CIDR 2021 "Lakehouse" (Armbrust et al.) y la spec Iceberg son las referencias base.

### Gaps
- No se hallaron benchmarks independientes ni estudios de caso cuantificados (Uber, Netflix, Airbnb, LinkedIn) comparando costos Lambda/Kappa/lakehouse; las fuentes son opinión o vendor.
- Estado 2026 de Delta vs Iceberg (UniForm, convergencia de catálogos, Iceberg v3) no verificado.

## 2. Medallion en la práctica y dónde falla

### Takeaway
Medallion (bronze/silver/gold) es una convención de capas de calidad progresiva popularizada por Databricks; es un patrón de organización, no un estándar formal. Falla sobre todo por mal uso (silver sobrecargado, gold por consumidor, copias redundantes), no por el concepto; la propia fuente oficial casi no lista desventajas.

### Cited Findings
- Bronze: datos "tal cual" de la fuente + metadatos (fecha de carga, id de proceso), para CDC rápido, archivo histórico, linaje, auditoría y reprocesamiento sin releer la fuente — [Databricks glossary](https://www.databricks.com/glossary/medallion-architecture)
- Silver: datos conformados/limpiados/deduplicados, "vista empresarial" de entidades clave; guía: limpieza "just-enough" en ELT, priorizar velocidad de ingesta, diferir reglas complejas a Gold; modelos 3NF o Data Vault — [Databricks glossary](https://www.databricks.com/glossary/medallion-architecture)
- Gold: modelos desnormalizados, de lectura optimizada, por proyecto (Kimball star schemas, data marts Inmon); reglas finales de calidad — [Databricks glossary](https://www.databricks.com/glossary/medallion-architecture)
- La página oficial no enumera desventajas explícitas y dice que es compatible con data mesh — [Databricks glossary](https://www.databricks.com/glossary/medallion-architecture)

### Inferences
- Modos de fallo plausibles (del investigador, sin fuente en sesión): (1) silver se convierte en cajón de sastre con lógica de negocio, rompiendo la guía "just-enough"; (2) proliferación de golds por equipo con definiciones de métricas divergentes (falta capa semántica); (3) latencia y costo acumulados por 3 saltos materializados, mal ajustados a casos casi-tiempo-real; (4) ambigüedad sobre dónde aplicar PII/gobierno; (5) tratarlo como arquitectura completa cuando es solo layout de datos (no resuelve ownership, contratos ni orquestación); (6) bronze sin contrato de esquema que rompe aguas abajo con cada cambio de la fuente.
- Alternativas/complementos: staging/intermediate/marts de dbt (mapeo casi 1:1), Data Vault + marts, capa semántica/metrics layer, "data products" por dominio.

### Gaps
- No hay literatura empírica sobre tasas de fallo de medallion; los modos de fallo anteriores no están respaldados por fuentes leídas. Buscar posts de dbt Labs, Kimball Group, o críticas de practicantes.

## 3. Data mesh: realidad de adopción, críticas, evidencia (literatura consolidada escasa, señalado)

### Takeaway
Data mesh (Dehghani, 2019) es sobre todo un cambio sociotécnico; la evidencia disponible es cualitativa (entrevistas, blogs de vendors) y apunta a que los fracasos son organizacionales. Las ideas "data as a product" y "platform as a product" se adoptan selectivamente, a menudo sin la etiqueta. NO existe literatura consolidada con tasas de éxito/fracaso medidas: marcar como área pobremente documentada.

### Cited Findings
- Cuatro principios: propiedad descentralizada por dominio; datos como producto; plataforma de datos self-serve; gobernanza computacional federada; Dehghani los declara "colectivamente necesarios y suficientes"; prerrequisitos: arquitectura que desacople dominios, roles de data product owner/developer, plataforma que oculte la complejidad, incentivos y estándares globales automatizados — [Dehghani en martinfowler.com](https://martinfowler.com/articles/data-mesh-principles.html)
- Estudio de 15 entrevistas a expertos (arXiv 2023): dificultad para pasar a gobernanza federada, para asumir responsabilidad de data products y para entender el concepto; buenas prácticas: unidad de coordinación transversal, monitorear uso de data products, quick wins, equipos pequeños dedicados — [arXiv 2302.01713](https://arxiv.org/abs/2302.01713)
- Starburst (vendor, sesgo a federación): Gartner Hype Cycle 2022 lo ubicó como "obsoleto antes del plateau"; fallos citados: fronteras de ownership solapadas, falta de skills de data engineering en dominios, catálogos que se degradan (~200 resultados para "revenue", ilustrativo), estándares divergentes, plataformas mínimas que colapsan con excepciones, rollouts big-bang; sobrevive: ownership selectivo (grandes empresas con unidades de negocio independientes), platform-as-product, data-as-product, pilotos de máximo 2 dominios, híbrido con federación; no aporta tasas de adopción — [Starburst](https://www.starburst.io/blog/data-mesh-what-happened/)
- Cifras de adopción (8-12% de uso; 18% con madurez de gobernanza suficiente) aparecen en un paper arXiv vía citas secundarias de Gartner; no verificadas con la fuente original — [arXiv 2606.08266](https://arxiv.org/pdf/2606.08266). Fuentes de blog atribuyen fracasos a falta de gestión del cambio y ROI lento — [ProfitOptics 2024](https://www.profitoptics.com/blog/data-mesh-cant-win-without-a-massive-cultural-shift)

### Inferences
- Encaja: organizaciones grandes con dominios de negocio autónomos, equipos con capacidad de ingeniería en dominios, y plataforma central madura. No encaja: <~100-200 personas de ingeniería, un solo dominio dominante, o equipo de datos central pequeño ya suficiente.
- Crítica estructural: el costo de coordinación y duplicación de capacidades puede superar al cuello de botella central que pretendía resolver; el gran riesgo es "mesh" como reorganización sin plataforma ni incentivos.
- [conocimiento general, no verificado] Casos públicos habitualmente citados: Zalando, Netflix (Data Mesh en plataforma de CDC/Studio), Intuit, JPMorgan; no se verificaron en sesión.

### Gaps
- Sin casos de éxito/fracaso verificados con métricas; sin encuestas primarias; Gartner original no consultado. Data fabric (Gartner) también sin fuentes leídas.

## 4. Qué arquitectura según escala, tamaño de equipo y latencia

### Takeaway
Elegir por (a) SLA de frescura real, (b) tamaño/madurez del equipo, (c) número de dominios/consumidores. Las fuentes leídas respaldan solo partes (latencia: Kreps; organización: mesh); el resto es síntesis del investigador.

### Cited Findings
- Regla de Kreps: batch si no hay sensibilidad a latencia, streaming si la hay, evitar ambos salvo necesidad — [Kreps](https://www.oreilly.com/radar/questioning-the-lambda-architecture/)
- Recomendación de pilotos pequeños (<=2 dominios) y plataforma como producto para mesh — [Starburst](https://www.starburst.io/blog/data-mesh-what-happened/)
- Frescura de ~5 min alcanzable con Kafka→Iceberg gestionado — [Confluent Tableflow](https://docs.confluent.io/cloud/current/topics/tableflow/overview.html)

### Inferences (heurística del investigador; validar)
- Equipo 1-5, datos <1 TB, latencia horas: warehouse cloud (Snowflake/BigQuery/Redshift/Databricks SQL) + ELT con dbt + orquestador; sin streaming ni mesh.
- Equipo 5-30, múltiples fuentes, ML/semi-estructurado, latencia minutos: lakehouse (Iceberg/Delta) + medallion, CDC a bronze, micro-batch.
- Latencia segundos y casos operacionales (fraude, personalización): arquitectura event-driven + Flink/Kafka Streams, OLAP en tiempo real para servir; considerar Kappa solo con equipo de streaming experimentado.
- >30-50 ingenieros de datos y muchos dominios autónomos: considerar mesh/data products con plataforma y contratos; antes, probar plataforma central + contratos.
- Reverse ETL cuando el warehouse es fuente de verdad de segmentos/scores para SaaS operacionales.

### Gaps
- Umbrales numéricos de escala/equipo son heurísticos, sin fuente.

## 5. Conceptos fundamentales (referencia densa)

### Takeaway
Base conceptual estable; se cita lo leído y el resto se marca como conocimiento general no verificado en sesión. Referencias canónicas: Kleppmann, *Designing Data-Intensive Applications* (2ª ed. 2025-26); Reis & Housley, *Fundamentals of Data Engineering* (2022).

### Cited Findings
- Kafka/log como columna del procesamiento de eventos y reprocesamiento inmutable — [Kreps](https://www.oreilly.com/radar/questioning-the-lambda-architecture/)
- Tableflow ilustra schema evolution y CDC materializados automáticamente desde registro de esquemas (Avro/Protobuf/JSON Schema) — [Confluent docs](https://docs.confluent.io/cloud/current/topics/tableflow/overview.html)
- "Federated computational governance" y estándares globales automatizados como equivalente de contratos entre dominios — [Dehghani](https://martinfowler.com/articles/data-mesh-principles.html)

### Inferences [conocimiento general, no verificado en sesión]
- OLTP vs OLAP: OLTP = transacciones cortas, filas, normalizado, baja latencia punto; OLAP = escaneos agregados, columnar, desnormalizado. HTAP/zero-ETL difuminan la frontera.
- ETL vs ELT: ELT domina con cómputo/almacenamiento cloud desacoplado (transformar en el warehouse con SQL/dbt); ETL persiste por privacidad (enmascarar antes de cargar), volumen/edge, y streaming.
- Idempotencia: reejecutar produce el mismo estado; técnicas: MERGE/upsert por clave natural, overwrite de partición, claves deterministas, deduplicación por id de evento, escrituras atómicas (commit de tabla).
- Exactly-once: en la práctica "effectively-once" = at-least-once + idempotencia o transacciones; Kafka (productor idempotente + transacciones) y Flink (checkpoints + two-phase commit sink) garantizan exactly-once dentro de su frontera, no extremo a extremo hacia sistemas externos sin sink transaccional/idempotente.
- CDC: log-based (Debezium; binlog/WAL) vs query/trigger; maneja deletes y orden; retos: snapshot inicial, DDL, ordenamiento entre tablas, PII.
- Schema evolution: compatibilidad backward/forward/full; Schema Registry; formatos Avro/Protobuf; table formats con evolución de columnas por id (Iceberg).
- Data contracts: acuerdo explícito productor-consumidor (esquema, semántica, SLA, calidad, propietario) aplicado en CI y runtime; estándares emergentes: Open Data Contract Standard (Bitol/Linux Foundation), datacontract.com; muy dinámico y mal documentado en producción.
- Batch vs streaming: bounded vs unbounded; Dataflow model (event time, watermarks, triggers); streaming también implica reprocesamiento/backfill y estado.
- CAP/consistencia: CAP solo aplica ante partición (elegir C o A); PACELC añade latencia vs consistencia en operación normal; consistencia eventual en lakes con object storage ya es fuerte en S3 desde 2020; table formats usan commit atómico optimista.
- Particionamiento: por tiempo/clave hash/rango; evitar sobre-particionar (archivos pequeños); Iceberg hidden partitioning y Delta liquid clustering reducen acoplamiento de queries al layout; en streaming, claves de partición determinan orden y paralelismo.

### Gaps
- Todo lo anterior carece de URLs verificadas en esta sesión; el redactor debe contrastar con DDIA, FoDE y docs oficiales (Kafka, Flink, Iceberg, Debezium, ODCS).

## 6. Catálogo de arquitecturas y tabla comparativa

### Takeaway
Las arquitecturas no son mutuamente excluyentes: son ejes distintos (modo de procesamiento: batch/streaming/Lambda/Kappa; almacenamiento: warehouse/lake/lakehouse; organización: mesh/fabric; layout: medallion; integración: event-driven/reverse ETL).

### Cited Findings
- Lambda/Kappa: ver sección 1. Medallion: ver sección 2. Mesh: ver sección 3.
- Medallion declarado compatible con mesh — [Databricks glossary](https://www.databricks.com/glossary/medallion-architecture)
- Híbrido mesh + federación estilo data fabric (Trino) presentado como camino práctico por un vendor — [Starburst](https://www.starburst.io/blog/data-mesh-what-happened/)

### Inferences (tabla de síntesis del investigador; madurez y trade-offs por validar)

| Arquitectura | Eje | Cuándo usar | Cuándo no | Pros | Contras | Madurez (est.) |
|---|---|---|---|---|---|---|
| Batch | Procesamiento | Latencia horas, reportes, backfills | Decisiones en segundos | Simple, barato, reproducible | Latencia alta | Muy alta |
| Streaming | Procesamiento | Fraude, alertas, personalización | Equipos sin experiencia en estado/ordenamiento | Baja latencia | Complejidad operacional, estado, reproceso | Alta |
| Lambda | Procesamiento | Ya hay batch y se añade baja latencia | Proyectos nuevos sin necesidad dual | Pragmático, robusto | Lógica duplicada (Kreps) | Alta, en declive/nicho |
| Kappa | Procesamiento | Eventos como fuente de verdad, equipo de streaming | Reprocesos masivos baratos con batch; retención larga costosa | Una ruta de código | Log retenido/costo, difícil en práctica | Media-alta |
| Data warehouse | Almacenamiento | BI/SQL estructurado, equipos pequeños | ML sobre no estructurado a gran escala, lock-in | Gobernanza, rendimiento SQL | Costo a escala, formatos propietarios | Muy alta |
| Data lake | Almacenamiento | Datos crudos/semiestructurados baratos | Sin gobierno ("data swamp") | Barato, flexible | Sin ACID/gobierno por defecto | Alta (legado) |
| Lakehouse | Almacenamiento | BI+ML en una capa, formatos abiertos | Latencia sub-segundo; equipos mínimos que cubre un DW | ACID, abierto, un almacenamiento | Operación de compaction/catálogo, fragmentación de catálogos | Alta y creciendo |
| Medallion | Layout | Refinamiento progresivo de calidad | Casos de baja latencia extrema | Linaje, reprocesos, convención común | Capas sobrecargadas, costo de copias | Alta (convención) |
| Data mesh | Organización | Muchos dominios autónomos, plataforma madura | Organizaciones pequeñas/centralizadas | Escala organizacional, ownership | Cambio cultural, gobernanza difícil | Baja-media; evidencia escasa |
| Data fabric | Integración/metadata | Datos distribuidos con virtualización y metadata activa | Cuando basta un warehouse central | Acceso unificado sin mover datos | Concepto difuso, mucho marketing | Baja-media; mal definido |
| Event-driven | Integración | Sistemas desacoplados, tiempo real | Consistencia fuerte multi-paso sin sagas | Desacople, escalabilidad | Depuración, ordenamiento, evolución de esquema | Alta |
| Reverse ETL | Activación | Llevar datos del warehouse a SaaS operacionales | Cuando basta integración directa de la app | Cierra el ciclo analítico-operacional | Calidad/latencia, costo por filas, solapamiento con CDP | Media |

- Alternativas/estándares [conocimiento general, no verificado]: Iceberg (spec abierta, Apache), Delta (Linux Foundation), Hudi; Kafka protocol; OpenLineage; dbt; Open Data Contract Standard; Gartner Hype Cycle para data mesh/fabric.

### Gaps
- Madurez y "estándares" por arquitectura no verificados con fuentes primarias; data fabric, reverse ETL y event-driven no se investigaron en esta sesión (sin fuentes leídas). Zonas rápidas y mal documentadas: data contracts, data mesh, catálogos Iceberg (REST/Polaris/Unity), streaming lakehouse.
