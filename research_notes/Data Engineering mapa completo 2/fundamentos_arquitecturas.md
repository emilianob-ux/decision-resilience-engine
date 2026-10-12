# Data Engineering: fundamentos y arquitecturas de referencia, con verificación en fuentes primarias (a oct 2026)

Nota de método. Esta pasada (v2) leyó en texto completo, vía descarga y `pdftotext`, el paper CIDR 2021 del Lakehouse, el paper VLDB 2020 de Delta Lake, el paper VLDB 2015 del Dataflow Model, el paper VLDB 2020 de TiDB y el paper arXiv de Uber "Real-time Data Infrastructure at Uber". También leyó artículos de martinfowler.com (Dehghani, Fowler), el blog de Kleppmann, el post de Confluent sobre EOS, el blog de Flink sobre 2PC, la spec de Iceberg, la doc de Debezium, el blog de LinkedIn Engineering, el AWS Big Data Blog (Zalando) y páginas del Thoughtworks Radar. Convenciones: **[Fuente]** = afirmado por la URL citada; **[Inferencia]** = juicio del investigador; **[Secundaria]** = la fuente cita a un tercero y no se verificó el original. Cuando la herramienta de fetch resumió con un modelo pequeño, las cifras se contrastaron con el texto extraído del PDF, salvo indicación. No se pudo leer: Kreps original de nuevo (se reutiliza la lectura de la pasada 1), Gartner (de pago), DDIA 2ª ed. (solo metadatos), posts originales de Zalando y Intuit (404/error o solo resúmenes), blog de Netflix TechBlog (solo secundarias). Se hicieron unas 40 llamadas de búsqueda/fetch.

Cambios respecto a la pasada 1 (resumen para el redactor):
- Verificado con fuente primaria: tesis y cifras del paper Lakehouse; límites declarados de Delta Lake; la crítica de Akidau a Lambda; el límite de Kafka EOS; 2PC de Flink; spec de Iceberg; historial del Radar para data mesh y lakehouse; Uber no puede adoptar Kappa y creó "Kappa+"; LinkedIn 94%; Airbnb Riverbed eligió Lambda; Zalando 5.000 data products.
- Corregido: la cifra "8-12% de adopción" de mesh NO aparece en el abstract del arXiv 2606.08266 citado en la pasada 1; la cifra de 18% la atribuye Atlan (secundaria) a una encuesta de Gartner 2021. Ver sección 3.
- Medallion: sigue sin existir literatura empírica; se añadió crítica de practicantes (opinión).

---

## 1. Qué dicen las fuentes primarias (Kleppmann, Akidau, Kreps, Armbrust, Dehghani, Delta VLDB) y qué afirmaciones sostienen

### Takeaway
Cada fuente primaria sostiene una tesis acotada. Armbrust (CIDR 2021) es un argumento de posición con un benchmark de Databricks sobre su propio motor. Delta VLDB documenta con honestidad límites reales (transacciones por tabla, latencia de object store). Akidau define el modelo y critica Lambda por complejidad, no por incorrección. Dehghani es un modelo conceptual sin umbrales ni métricas de éxito.

### Cited Findings

**Lakehouse (Armbrust, Ghodsi, Xin, Zaharia, CIDR 2021)**
- [Fuente] Tesis: la arquitectura de data warehouse "se marchitará en los próximos años" y será reemplazada por el Lakehouse: formatos abiertos de acceso directo (Parquet), soporte de primera clase para ML/ciencia de datos y rendimiento de estado del arte. — [CIDR 2021 paper](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf)
- [Fuente] Problemas que atribuyen a la arquitectura de dos niveles (lake + warehouse): fiabilidad (mantener ambos consistentes es difícil y costoso), obsolescencia de datos (cargas al warehouse "frecuentemente toman días"), soporte limitado de analítica avanzada y costo total (ETL continuo, doble almacenamiento, lock-in). Citan una encuesta Dimensional Research/Fivetran: 86% de analistas usan datos desactualizados y 62% esperan a ingeniería varias veces al mes. — [CIDR 2021](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf)
- [Fuente] Definición: sistema de gestión de datos sobre almacenamiento barato y de acceso directo que ofrece ACID, versionado, auditoría, indexación, caché y optimización de consultas. La implementación se basa en una capa de metadatos sobre el object store. — [CIDR 2021](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf)
- [Fuente] Evidencia de rendimiento: TPC-DS a factor de escala 30.000, 99 consultas, clusters de 960 vCPU, contra cuatro warehouses cloud; Delta Engine (motor C++ de Databricks) "comparable o mejor a menor precio". Nota al pie: datos cacheados en SSD; con caché fría Delta Engine fue 18% más lento. Los competidores no se nombran. — [CIDR 2021](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf)
- [Fuente] Reconocen como problemas abiertos nuevos formatos de almacenamiento, estrategias de caché/layout y serverless. Sus afirmaciones finales son predicciones ("creemos que la industria convergerá"). — [CIDR 2021](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf)

**Delta Lake (Armbrust et al., VLDB 2020)**
- [Fuente] Desplegado en "miles de clientes de Databricks" que procesan "exabytes por día"; las instancias más grandes gestionan datasets de escala exabyte y miles de millones de objetos. Autoinforme del proveedor. — [VLDB 2020](https://www.vldb.org/pvldb/vol13/p3411-armbrust.pdf)
- [Fuente] Diseño: log de transacciones en el propio object store con escritura "put-if-absent", control de concurrencia optimista; escrituras serializables, lecturas con aislamiento de snapshot (o serializable si se ejecuta como transacción lectura-escritura). — [VLDB 2020](https://www.vldb.org/pvldb/vol13/p3411-armbrust.pdf)
- [Fuente] Límites declarados: (1) transacciones serializables solo dentro de una tabla (cada tabla tiene su log); (2) latencia de streaming limitada por el object store, "difícil lograr latencia de milisegundos", segundos aceptables; (3) sin índices secundarios (solo min/max por objeto); (4) tasa de commits limitada a "varias transacciones por segundo" porque la escritura a object store tarda decenas a cientos de ms. — [VLDB 2020](https://www.vldb.org/pvldb/vol13/p3411-armbrust.pdf)

**Dataflow Model (Akidau et al., VLDB 2015)**
- [Fuente] Propone un modelo unificado sobre datos no acotados y desordenados donde corrección, latencia y costo son ajustables; separa qué se calcula, dónde en tiempo de evento (ventanas), cuándo se emite (triggers/watermarks) y cómo se refinan resultados (modos de acumulación). Los watermarks suelen ser heurísticos (cota inferior de tiempos de evento procesados). — [VLDB 2015](https://www.vldb.org/pvldb/vol8/p1792-Akidau.pdf)
- [Fuente] Sobre Lambda: los sistemas Lambda "pueden lograr muchos de los requisitos pero fallan en simplicidad por tener que construir y mantener dos sistemas"; Summingbird mitiga la complejidad con una interfaz única pero "impone limitaciones". — [VLDB 2015](https://www.vldb.org/pvldb/vol8/p1792-Akidau.pdf)
- [Fuente] Anécdota de Google: un cliente de MillWheel ejecutaba streaming en modo de consistencia débil con un MapReduce nocturno "para generar la verdad"; "los usuarios dejaron de confiar en los resultados débilmente consistentes" y reimplementaron con consistencia fuerte. Motivación para unificar batch/streaming: un pipeline de log-join con implementación FlumeJava separada para backfills. — [VLDB 2015](https://www.vldb.org/pvldb/vol8/p1792-Akidau.pdf)

**Kreps (2014, "Questioning the Lambda Architecture")** — releído en la pasada 1, no re-leído aquí
- [Fuente] Problema central de Lambda: mantener la misma lógica en dos sistemas; Kappa: log retenido + segundo job que reprocesa y conmuta; su evidencia es LinkedIn/Samza; recomienda no usar ambos salvo necesidad. — [Kreps, O'Reilly](https://www.oreilly.com/radar/questioning-the-lambda-architecture/)

**Data mesh (Dehghani, martinfowler.com 2020)**
- [Fuente] Cuatro principios: propiedad de datos descentralizada orientada a dominio; datos como producto; infraestructura self-serve como plataforma; gobernanza federada computacional. Los declara "colectivamente necesarios y suficientes". Advierte que exige estructura organizacional, incentivos y arquitectura de apoyo, y que el equilibrio entre decisiones globales y locales es "un arte". — [Dehghani, principios](https://martinfowler.com/articles/data-mesh-principles.html)
- [Fuente] Diagnóstico del enfoque centralizado: tres generaciones (warehouse, lake, lake con streaming/cloud) que "sufren las características que causaron los fallos previas"; descomposición del pipeline "ortogonal al eje de cambio" (ingesta, preparación, servicio); ingenieros hiperespecializados sin conocimiento del dominio. — [Dehghani, monolito a mesh](https://martinfowler.com/articles/data-monolith-to-mesh.html)
- [Fuente] Caveats propios del autor: el modelo centralizado "puede funcionar para organizaciones con dominios simples y pocos casos de consumo"; no define umbral numérico; lakes/warehouses pasan a ser "nodos del mesh"; reconoce que "la adopción a escala empresarial aún tiene un largo camino" (2020, prácticas en "bolsillos"). — [Dehghani, monolito a mesh](https://martinfowler.com/articles/data-monolith-to-mesh.html)

**Kleppmann (DDIA y escritos)**
- [Fuente] DDIA 2ª ed. (Kleppmann y Riccomini) figura como publicada en febrero 2026, 650 páginas, conservando estructura y filosofía de la 1ª. — [O'Reilly](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/colophon01.html), resumida vía búsqueda (no se leyó el texto de la 2ª ed.)
- [Fuente, secundaria: resaltado de lector de la 1ª ed.] Exactly-once = organizar el cómputo para que el efecto final sea el mismo que sin fallos aunque haya reintentos; la idempotencia de extremo a extremo exige considerar todo el flujo de la petición y no basta con una transacción de base de datos. — [Goodreads highlight](https://www.goodreads.com/notes/34626431-designing-data-intensive-applications/146561796-charles-fonseca?page=11)
- [Fuente] "A Critique of the CAP Theorem": confusión sobre significado de CAP, definiciones inconsistentes/ambiguas, problemas en su formalización; discute la lectura "los sistemas eventualmente consistentes son más disponibles"; propone el marco "delay-sensitivity" (sensibilidad de la latencia de operaciones al retardo de red). — [Kleppmann 2015](https://martin.kleppmann.com/2015/09/17/critique-of-the-cap-theorem.html)

### Inferences
- [Inferencia] Armbrust 2021 es una fuente de posición y marketing técnico: sus afirmaciones de rendimiento provienen del proveedor sobre su motor propio, con cache en SSD. Delta VLDB es más fiable en limitaciones porque las enumera. El redactor debe presentar "warehouse se marchitará" como predicción, no hecho.
- [Inferencia] Los dos papers de Databricks convergen en un patrón: latencia de segundos y no de milisegundos, por lo que el lakehouse no sustituye a OLAP en tiempo real ni a stores operacionales.

### Gaps
- No se leyó el texto de DDIA 2ª ed.; cualquier afirmación de capítulo requiere el libro. No se verificó Streaming Systems (Akidau, Chernyak, Lax) más allá del paper de 2015.

---

## 2. Fundamentos con fuente primaria: exactly-once, CDC, schema evolution, CAP/PACELC, HTAP, partición

### Takeaway
Exactly-once es una garantía acotada a una frontera (Kafka-Kafka; Flink con sinks transaccionales) y cuesta rendimiento medible. CDC log-based entrega at-least-once con limitaciones de DDL. Iceberg resuelve schema evolution por ID de columna y concurrencia por intercambio atómico de metadatos. CAP es una herramienta de razonamiento discutida; PACELC es la extensión práctica.

### Cited Findings
- [Fuente] Kafka: el productor idempotente da exactly-once por partición (sin duplicados, sin pérdida, en orden) con impacto "despreciable" en throughput; las transacciones permiten escrituras atómicas multi-partición y commit de offsets en la misma transacción; consumidores `read_committed`. — [Confluent](https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/)
- [Fuente] Límite: la garantía de Kafka Streams es "dentro del alcance del procesamiento interno de Kafka Streams"; llamadas RPC a stores externos o lógica no determinista quedan fuera; para salir a sistemas externos se necesita un conector exactly-once. — [Confluent](https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/)
- [Fuente] Costo (benchmarks 2017, Kafka 0.11, mensajes de 1 KB, transacciones de 100 ms): -3% de throughput frente a `acks=all`; -20% frente a `acks=1` con 5 in-flight; Kafka Streams con commit de 100 ms pierde 15-30%; con commit de 30 s sin sobrecosto para mensajes de 1 KB o más. — [Confluent](https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/) (cifras antiguas; no revalidadas en 2026)
- [Fuente] Diseño KIP-98: idempotent producer con PID y números de secuencia, coordinador de transacciones, escrituras atómicas multi-partición. — [Conduktor KIP explorer](https://kafka-options-explorer.conduktor.io/kip/98/) y [wiki Apache](https://cwiki.apache.org/confluence/display/KAFKA/KIP-98+-+Exactly+Once+Delivery+and+Transactional+Messaging) (solo vía resultado de búsqueda)
- [Fuente] Flink 2PC: los checkpoints son el punto de coordinación; en pre-commit cada sink con escritura externa cierra su transacción abierta; al confirmar el JobManager que el checkpoint está completo, se hace commit. `TwoPhaseCommitSinkFunction` (Flink 1.4) con begin/preCommit/commit/abort. Condiciones: el sistema externo debe soportar transacciones; los commits deben acabar teniendo éxito y ser idempotentes; la salida solo es visible tras el commit (latencia de visibilidad). — [Flink blog](https://flink.apache.org/2018/02/28/an-overview-of-end-to-end-exactly-once-processing-in-apache-flink-with-apache-kafka-too/)
- [Fuente] Debezium (PostgreSQL): reanuda desde la última posición del WAL; pueden aparecer duplicados tras snapshot; modos de snapshot `initial`, `always`, `initial_only`, `no_data`, `when_needed`; plugins `pgoutput`/`decoderbufs`; "la decodificación lógica no soporta cambios DDL"; no soporta cambios de esquema durante un snapshot incremental; los cambios se publican al commit. — [Debezium docs](https://debezium.io/documentation/reference/stable/connectors/postgresql.html) (texto leído hasta 100k de 320k caracteres; no se leyeron TOAST ni crecimiento de replication slot)
- [Fuente] DBLog (Netflix): CDC basado en marcas de agua que intercala eventos del log de transacciones con SELECTs de tablas, sin locks; usado en producción por "decenas de microservicios". — [arXiv 2010.12597 vía resultado de búsqueda](https://www.arxiv.org/pdf/2010.12597)
- [Fuente] Iceberg: un intercambio atómico del archivo de metadatos "sienta la base del aislamiento serializable"; commit optimista con reintento; columnas seleccionadas por field ID (renombrar y reordenar es seguro); particionado por transformaciones (day, bucket) con filtros derivados automáticamente y particionado modificable; v1 tablas analíticas, v2 deletes de fila, v3 vectores de borrado, row lineage, `variant`, valores por defecto, cifrado; v4 en desarrollo. — [Iceberg spec](https://iceberg.apache.org/spec/)
- [Fuente] PACELC (Abadi, IEEE Computer 2012): si hay partición, disponibilidad vs consistencia; si no (else), latencia vs consistencia. Clasificación: Dynamo/Cassandra/Riak PA/EL; PNUTS PC/EL; MongoDB PA/EC según un resumen. — [Abadi PDF](https://cs.umd.edu/~abadi/papers/abadi-pacelc.pdf), [resumen ODBMS](https://www.odbms.org/2012/01/consistency-tradeoffs-in-modern-distributed-database-system-design/) (solo vía búsqueda)
- [Fuente] HTAP (TiDB, VLDB 2020): HTAP exige frescura y aislamiento; un estudio previo mostró que los sistemas en memoria co-ejecutando OLTP y OLAP degradan mucho (citan caídas de al menos 3x en HANA y 5x en HyPer). TiDB añade un rol "learner" de Raft que replica asíncronamente a un almacén columnar (TiFlash) sin participar en commit ni elección; en CH-benCHmark, aumentar clientes OLTP reduce el throughput OLAP como máximo 5%, mientras MemSQL cae más de 5x en throughput transaccional al crecer clientes analíticos. Retardo de replicación al learner: con 100 warehouses y 2 clientes analíticos más del 80% de las consultas toman menos de 100 ms, pero con 32 clientes menos del 50%. Autoevaluación de los autores (PingCAP). — [TiDB VLDB 2020](https://www.cs.purdue.edu/homes/csjgwang/CloudNativeDB/TiDBVLDB20.pdf)
- [Fuente] Zero-ETL (AWS): "conjunto de integraciones que minimiza la necesidad de construir pipelines ETL"; Aurora/RDS a Redshift, DynamoDB a SageMaker Lakehouse/Redshift/OpenSearch, etc.; "casi tiempo real" sin cifra de latencia ni lista de limitaciones en la página. — [AWS](https://aws.amazon.com/what-is/zero-etl/)
- [Fuente] Event-driven (Fowler 2017): cuatro patrones distintos (event notification, event-carried state transfer, event sourcing, CQRS); advierte que el problema central es "confundir los patrones"; cons: flujo implícito, copias de datos, replay problemático con dependencias externas, evolución del esquema de eventos. — [Fowler](https://martinfowler.com/articles/201701-event-driven.html)

### Inferences
- [Inferencia] "Exactly-once" extremo a extremo = límite transaccional + idempotencia en el último salto; el costo de latencia está en el intervalo de commit/checkpoint (Kafka 100 ms vs 30 s; Flink visible solo tras checkpoint).
- [Inferencia] Zero-ETL es un nombre para replicación CDC gestionada propietaria (acoplada al proveedor); no existe estándar abierto, y la página de AWS no cuantifica latencia.
- [Inferencia] Quedan sin fuente primaria en esta pasada: definición formal de OLTP/OLAP (Codd, Kimball), ETL vs ELT, Open Data Contract Standard, Dataflow en Beam; usar conocimiento de la pasada 1 como no verificado.

### Gaps
- Sin primaria: particionamiento/sharding (Dynamo, Spanner papers no leídos), consistency models (Jepsen/Viotti no leídos), sagas. Zero-ETL sin benchmarks independientes.

---

## 3. Evidencia documentada de adopción y fracaso: data mesh y lakehouse

### Takeaway
Para data mesh solo hay evidencia cualitativa: Thoughtworks lo pasó de Assess (2019) a Trial (2020-2022) y luego lo dejó fuera de la edición vigente, con advertencias crecientes sobre costos de integración; Gartner 2022 lo calificó "obsolescente antes del plateau". El caso cuantificado más sólido es Zalando (descrito sin la etiqueta "mesh" en AWS). Las cifras de adopción 8-12% de la pasada 1 no se pudieron verificar. Para lakehouse, la evidencia son papers del proveedor y un blip Trial del Radar de 2023.

### Cited Findings
**Data mesh**
- [Fuente] Historial del Radar: Assess (nov 2019, may 2020), Trial (oct 2020, oct 2021, mar 2022); hoy "no está en la edición actual" y no se re-revisa. Textos: may 2020 exige plataforma self-serve, cambio organizacional e incentivos; oct 2020 herramientas limitadas; oct 2021 fricción con tecnologías existentes y dominios que resisten tratar el dato como responsabilidad central; mar 2022 "altos costos de integración", adopción "confinada a partes de grandes organizaciones" y vendors que distraen del trabajo socio-organizacional. — [Thoughtworks Radar: data mesh](https://www.thoughtworks.com/radar/techniques/data-mesh)
- [Fuente, secundaria] Gartner Hype Cycle for Data Management 2022: data mesh en "innovation trigger", beneficio y penetración de mercado "bajos", predicción "obsolete before plateau" (junto con Information Stewardship Applications e iPaaS for data integration). — [Atlan](https://atlan.com/gartner-data-mesh), consistente con [Starburst](https://www.starburst.io/blog/data-mesh-what-happened/) y con el resultado de búsqueda sobre [Dataminded](https://www.dataminded.com/resources/the-state-of-data-products-in-2024). Críticas: un ex analista lo interpreta como promoción de data fabric; otra lectura dice que ignora implementaciones activas. No se pudo leer el informe de Gartner (de pago).
- [Fuente, secundaria] "Solo 18% de las organizaciones alcanzó la madurez de gobernanza necesaria" según una encuesta Gartner de 2021 reportada por Atlan. — [Atlan](https://atlan.com/gartner-data-mesh)
- [Fuente] Corrección: el arXiv 2606.08266 (citado en pasada 1 por "8-12%") en su abstract no da porcentajes ni cita a Gartner; dice que leyeron 64 fuentes, que "la tecnología avanzó, el historial organizacional apenas se movió" y que "las encuestas reportan altas tasas de fracaso" sin números. Las cifras 8-12% quedan **sin verificar**. — [arXiv abs](https://arxiv.org/abs/2606.08266) (solo abstract leído)
- [Fuente] Gartner Hype Cycle 2024: Data Product, Data Fabric y Active Metadata aparecen entre 32 tecnologías; el artículo de Denodo y una fuente secundaria sitúan data fabric cerca del trough; no se encontró la posición de data mesh en 2024+. — [Denodo](https://www.denodo.com/en/document/analyst-report/gartner-hype-cycle-data-management-2024), [datamanagementblog](https://www.datamanagementblog.com/my-reflections-on-the-gartner-hype-cycle-for-data-management-2024/)
- [Fuente] Estudio con 15 expertos (arXiv 2023): dificultad con gobernanza federada y con asumir responsabilidad de data products. — [arXiv 2302.01713](https://arxiv.org/abs/2302.01713) (pasada 1)
- [Fuente] Aprendizajes de equipos anónimos (datamesh-architecture.com): 3 sprints para el primer data product; equipos con objetivos de roadmap en conflicto; carga cognitiva; algunos data products pedidos pero sin uso; calidad aguas arriba incompleta; coste de Athena/Parquet/JSON. Un product owner dijo que los datos le permitieron rechazar "al menos la mitad" de peticiones de features poco rentables. Sin empresas nombradas, sin muestreo. — [datamesh-architecture.com](https://datamesh-architecture.com/real-world-learnings)
- [Fuente] Zalando: lago de más de 20 PB, más de 5.000 data products mantenidos por 350 equipos descentralizados, unos 6.000 usuarios mensuales (~80% de la plantilla), 27 mercados, 52 millones de clientes activos, GMV > 14.000 M EUR. El post de AWS no usa el término "data mesh". — [AWS Big Data Blog](https://aws.amazon.com/blogs/big-data/how-zalando-innovates-their-fast-serving-layer-by-migrating-to-amazon-redshift) Zalando se vincula a data mesh por una charla de Max Schultze y Arif Wider (ThoughtWorks) y diapositivas, no leídas aquí (SlideShare falló). Resultados de migración del serving layer a Redshift: 75% de consultas más rápidas, P90 -13%, P99 -23%, pico del lunes de 130 a 52 min, más de 19.000 horas de job ahorradas en 4 semanas (efecto de Redshift, no de mesh).
- [Fuente, secundaria] Intuit: el Chief Architect de la plataforma de datos, Tristan Baker, publicó "Intuit's Data Mesh Strategy" (Medium) y se inspiró en el artículo de 2019 de Dehghani; no se pudieron leer posts primarios ni métricas. — [resultados de búsqueda; Data Mesh Learning](https://datameshlearning.substack.com/p/data-mesh-newsletter-may-12-2021?open=false)
- [Fuente] Radar nov 2025 (vía rmoff): "Standalone data engineering teams" en Hold; data mesh no figura en la página listada. — [rmoff](https://rmoff.net/2025/11/05/tech-radar-nov-2025-data-blips) (el blip solo aparece por nombre, sin texto)

**Lakehouse**
- [Fuente] Radar: "Lakehouse architecture" Trial (abr 2023), fuera de la edición vigente; sugiere Delta Lake, Iceberg y Hudi, y que complementa data mesh. — [Thoughtworks Radar](https://www.thoughtworks.com/radar/techniques/lakehouse-architecture)
- [Fuente] Netflix: Iceberg nació en Netflix (2018) y hoy es proyecto top-level de Apache; reportes secundarios hablan de cientos de PB y ~1,5 millones de tablas Hive a migrar por capas de metadatos Iceberg sobre archivos existentes. — [Data Engineer Things (secundaria)](https://blog.dataengineerthings.org/i-spent-4-hours-learning-how-netflix-operates-apache-iceberg-at-scale-c93a9f94c539); no se encontró el TechBlog primario.
- [Fuente, contradictoria/vendor] Estado Delta vs Iceberg 2026: v3 de Iceberg con vectores de borrado; Databricks documenta soporte de Iceberg v3 en DBR 18.0+; fuentes discrepan sobre fecha de ratificación (mediados de 2025 vs Iceberg 1.11.0 el 19 mayo 2026) y sobre si UniForm y deletion vectors coexisten (Airbyte dice no; Databricks implica sí). — [Databricks docs](https://docs.databricks.com/iceberg/iceberg-v3), [Airbyte](https://airbyte.com/data-engineering-resources/iceberg-vs-delta-lake). Tratar como no resuelto.

### Inferences
- [Inferencia] La señal del Radar (Trial y luego retirado de la edición) combinada con el texto de 2022 sugiere que mesh se estabilizó como "idea parcialmente adoptada" y no como arquitectura de referencia general; esto es lectura, no afirmación de Thoughtworks.
- [Inferencia] Zalando es el único caso con volumen y equipos medibles, pero esa métrica de escala (5.000 data products, 350 equipos) es de producción, no de resultado de negocio; no hay evidencia causal de que mesh mejore tiempos de entrega.
- [Inferencia] El "fracaso" de mesh documentado es organizacional (capacidad de equipos, incentivos), consistente con las advertencias del propio Dehghani.

### Gaps
- Sin postmortems con nombre de una empresa que abandonó data mesh (la búsqueda solo arrojó comentarios generales). Sin cifras de adopción verificadas. Sin encuesta primaria de Gartner. Sin evidencia independiente de fracaso/éxito de lakehouse más allá de blips y vendors. Área de baja literatura.

---

## 4. Medallion: modos de fallo documentados fuera de material de vendor

### Takeaway
No hay estudios empíricos. Lo documentado es crítica de practicantes (opinión): reetiqueta del modelado Kimball, más almacenamiento y cómputo, silver cajón de sastre, golds divergentes, sin capa semántica. La fuente de vendor (Databricks) no lista desventajas.

### Cited Findings
- [Fuente, vendor] Definición de bronze/silver/gold: ver pasada 1 [Databricks glossary](https://www.databricks.com/glossary/medallion-architecture).
- [Fuente, opinión] Daniel Beach (Data Engineering Central) sostiene que medallion es Kimball renombrado, que tres capas requieren más almacenamiento y cómputo, que "Gold" es en realidad un data mart, y que la mención más temprana en Databricks que encontró es del 2 de junio de 2020. Recomienda modelar el lakehouse como un warehouse (hechos, dimensiones, marts). Un comentarista advierte contra organizar equipos por capa. No habla de latencia. — [Data Engineering Central](https://dataengineeringcentral.substack.com/p/medallion-architecture-truth-or-fiction)
- [Fuente, opinión agregada, sin métricas] Posts de practicantes enumeran: bronze sin esquema ni linaje, silver con enmascarado/dedup/enriquecimiento/reglas de negocio (frágil y lenta), proliferación de golds con definiciones divergentes ("metric drift"), cómputo impredecible por transformaciones repetidas y backfills, y "medallion describe estados de datos, no significado". Defensores: es una convención compartida y no una arquitectura completa. — [resultados de búsqueda; DevGenius](https://blog.devgenius.io/when-to-break-medallion-architectures-rules-and-what-you-re-actually-betting-on-0c606dfdd1dc) (de pago, no leído)
- [Fuente] Thoughtworks no tiene blip de medallion (búsqueda sin resultado); su blip de lakehouse no menciona medallion. — [Radar lakehouse](https://www.thoughtworks.com/radar/techniques/lakehouse-architecture)

### Inferences
- [Inferencia] La crítica de duplicación/costo es plausible pero no cuantificada en ninguna fuente; la de latencia (saltos materializados) es solo razonamiento. Los modos de fallo son de gobernanza y modelado, no del concepto.

### Gaps
- Cero evidencia cuantitativa de costo/latencia adicional por capa; área de baja literatura. No se leyó la guía de dbt Labs ni Kimball Group.

---

## 5. Lambda vs Kappa vs unificado: migraciones y casos reales con cifras

### Takeaway
Los casos documentados muestran tres rutas: (a) abandonar Lambda por código unificado (LinkedIn con Beam, -94% de tiempo de backfill); (b) no poder adoptar Kappa puro por costo de retención y crear un híbrido (Uber Kappa+); (c) elegir Lambda a conciencia por backfills y reconciliación (Airbnb Riverbed). Google (Akidau) documenta que un esquema Lambda con verdad nocturna perdió la confianza de usuarios.

### Cited Findings
- [Fuente] LinkedIn (marzo 2023): dos sistemas (batch y stream), dos bases de código, dos runtimes; con un pipeline unificado de Apache Beam (Samza y Spark runners) el backfill pasó de 7 horas a 25 minutos (-94%); como job de streaming consumía más de 5.000 GB-horas de memoria y casi 4.000 horas de CPU, y el batch unificado redujo ambos aproximadamente a la mitad; coste operativo reducido "11 veces" según el análisis de cost-to-serve; backfills sobre 900 millones de perfiles a 40.000 por segundo; Samza procesa 2 billones (trillion) de mensajes diarios. No dan cifra de reducción de tiempo de desarrollo. — [LinkedIn Engineering](https://www.linkedin.com/blog/engineering/data-streaming-processing/unified-streaming-and-batch-pipelines-at-linkedin-reducing-proc), resumen en [BigDATAwire](https://www.bigdatawire.com/2023/04/05/apache-beam-cuts-processing-time-94-for-linkedin) (la combinación de 94%, 50% y 11x proviene de dos medidas distintas; no mezclarlas)
- [Fuente] Uber (arXiv 2021): Lambda mantiene dos sistemas y genera problemas de consistencia; Kappa "requiere retención muy larga en Kafka y puede ser poco eficiente"; Uber limita la retención de Kafka a "unos pocos días" por escala y reemplazo de nodos, "por lo tanto no podemos adoptar Kappa". Solución con Flink en dos modos: SQL (misma consulta sobre Kafka y Hive, compilada a dos jobs, "similar a Lambda pero sin mantener dos jobs") y API "Kappa+", que reutiliza la lógica de streaming leyendo directamente datos archivados en Hive, resolviendo límites de entrada acotada, throttling del mayor throughput histórico y ajuste de memoria por datos desordenados. Escala: billones de mensajes y petabytes por día en Kafka (oct 2020). Los autores dicen que es un área "activa de investigación" y no hacen evaluación completa. — [Uber arXiv 2104.00087](https://arxiv.org/pdf/2104.00087)
- [Fuente] Uber Engineering también describe un "Kappa architecture" con un solo código (Spark Streaming) para backfills; el modo batch de Structured Streaming ignora ventanas por event time y watermarks y falla en backfills de varios días. — [Uber blog](https://eng.uber.com/kappa-architecture-data-stream-processing/) (solo vía resultado de búsqueda)
- [Fuente] Airbnb Riverbed: framework de vistas materializadas distribuidas con Lambda (Kafka online, Spark offline); 2,4 mil millones de eventos y 350 millones de documentos escritos por día; más de 50 vistas materializadas y más de 50 casos de uso intensivos en lectura; el artículo contrasta Kappa (más simple de mantener, más difícil para backfills y consistencia con eventos desordenados) y elige Lambda para backfill y reconciliación. — [InfoQ](https://www.infoq.com/news/2023/10/airbnb-riverbed-introduction)
- [Fuente] Shopify: adopción de Flink desde 2021; una prueba de concepto de joins con más de 10 TB de estado Flink y "100% de corrección"; mapa en vivo de BFCM rediseñado con Flink para más de 1,7 millones de comerciantes. Sin cifras comparativas Lambda/Kappa. — [Shopify Engineering](https://shopify.engineering/bfcm-live-map-2021-apache-flink-redesign), [Data Council](https://datacouncil.ai/talks/apache-flink-adoption-at-shopify) (resúmenes de charla)
- [Fuente] Google MillWheel/Dataflow: ver sección 1 (cliente con Lambda abandonó consistencia débil + MapReduce nocturno). — [VLDB 2015](https://www.vldb.org/pvldb/vol8/p1792-Akidau.pdf)
- [Fuente, pasada 1] Fresha (Current London 2026) sigue con Lambda por costo: tablas materializadas cada 20 min más vistas en consulta con CDC en vivo. — [Current 2026](https://current.confluent.io/post-conference-videos-26/lambda-architecture-in-2025-kafka-views-and-the-evolving-data-platform-ldn26)

### Inferences
- [Inferencia] Patrón común: nadie reporta Kappa "puro"; Uber lo rechaza por costo de retención y LinkedIn/Google unifican el código con el modelo (Beam/Dataflow) y mantienen dos modos de ejecución. El resultado práctico es "un código, dos ejecuciones" y no "un solo sistema".
- [Inferencia] Las cifras de LinkedIn (-94%) corresponden al coste del backfill ejecutado como batch en lugar de como streaming, no a un ahorro total de la plataforma; extrapolarlas a otras organizaciones es injustificado.

### Gaps
- Sin migraciones documentadas con coste total de propiedad antes/después en Netflix, Airbnb o Shopify. No se leyeron los posts originales de Uber ni el talk de Flink Forward sobre Kappa+. Sin benchmarks independientes.

---

## 6. Catálogo de arquitecturas: madurez, estándares y referencias (actualizado)

### Takeaway
Las arquitecturas son ejes distintos y combinables. Esta pasada verificó con fuente: Lambda/Kappa/Kappa+, lakehouse (CIDR), mesh (Dehghani, Radar), event-driven (Fowler), HTAP (TiDB), zero-ETL (AWS), data fabric (definición de Gartner vía secundaria), reverse ETL (solo vendors).

### Cited Findings
- [Fuente] Data fabric según Gartner (citado por vendors): "diseño de gestión de datos nuevo y en evolución" para pipelines de integración flexibles y reutilizables, basado en grafos de conocimiento, semántica y automatización con metadatos activos; "no es una sola herramienta"; en el Hype Cycle 2024 se sitúa cerca del valle de desilusión. — [TopQuadrant, resumen](https://topquadrant.com/blog/metadata-and-data-fabric), [Denodo](https://www.denodo.com/en/document/analyst-report/gartner-hype-cycle-data-management-2024). Definición contestada (metadato activo se usa con significados distintos según el analista).
- [Fuente] Reverse ETL: mueve datos transformados del warehouse a herramientas de negocio; se asocia al CDP composable; críticas (de vendors de CDP competidores): latencia batch (hourly a daily), duplicación de PII, no resuelve identidad ni decisión en tiempo real, riesgo de gobierno por escribir datos erróneos en sistemas operacionales. — [CDP.com](https://cdp.com/articles/reverse-etl-vs-cdp/), [Redpoint](https://www.redpointglobal.com/blog/composability-is-not-just-reverse-etl/). Fuentes con conflicto de interés; no hay estudio independiente.
- [Fuente] Confluent Tableflow materializa topics de Kafka como Iceberg/Delta con frescura ~5 min (pasada 1). — [Confluent docs](https://docs.confluent.io/cloud/current/topics/tableflow/overview.html)

### Tabla de síntesis (actualizada; columnas "Evidencia" y "Madurez" son [Inferencia] salvo celdas con enlace)

| Arquitectura | Evidencia leída | Cuándo usar | Cuándo no | Contras documentados | Madurez (est.) |
|---|---|---|---|---|---|
| Lambda | Kreps; Akidau; Uber; Airbnb Riverbed; LinkedIn | Backfill/reconciliación crítica; ya hay batch | Equipo pequeño; proyecto nuevo sin necesidad dual | Dos bases de código ([Kreps](https://www.oreilly.com/radar/questioning-the-lambda-architecture/)); confianza perdida si la verdad es nocturna ([VLDB 2015](https://www.vldb.org/pvldb/vol8/p1792-Akidau.pdf)) | Alta, en declive/nicho |
| Kappa | Kreps; Uber | Log retenido barato y equipo de streaming | Retención corta por costo/ops (Uber: días) | Retención larga, throughput ([Uber](https://arxiv.org/pdf/2104.00087)) | Media; rara en forma pura |
| Unificado (Beam/Dataflow, Kappa+) | Akidau; LinkedIn; Uber | Un código, ejecución batch o stream | Lógica muy específica de cada motor | Límites de la intersección de capacidades ([VLDB 2015](https://www.vldb.org/pvldb/vol8/p1792-Akidau.pdf)); bordes en backfills | Alta en grandes empresas |
| Warehouse / Lake | Armbrust CIDR (descripción de dos niveles) | BI estructurado / datos crudos baratos | Ver pasada 1 | Staleness, doble coste, reliability ([CIDR](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf)) | Muy alta |
| Lakehouse | CIDR 2021; Delta VLDB; Iceberg spec; Radar Trial 2023 | BI + ML en una capa abierta | Latencia sub-segundo, transacciones multi-tabla intensivas | Transacciones por tabla, ~pocos commits/s, sin índices secundarios ([VLDB 2020](https://www.vldb.org/pvldb/vol13/p3411-armbrust.pdf)) | Alta; catálogos aún en disputa |
| Medallion | Solo vendor y opinión | Convención de refinamiento | Casos de baja latencia | Ver sección 4 | Alta como convención |
| Data mesh | Dehghani; Radar; Gartner 2022; Zalando | Muchos dominios autónomos y plataforma madura | Pocos dominios, equipos sin capacidad | Costos de integración, adopción parcial ([Radar](https://www.thoughtworks.com/radar/techniques/data-mesh)) | Baja-media |
| Data fabric | Definición vía vendors | Metadatos activos sobre fuentes distribuidas | Cuando basta un warehouse central | Concepto difuso ([Gartner vía vendors](https://topquadrant.com/blog/metadata-and-data-fabric)) | Baja-media |
| Event-driven | Fowler | Desacople, integración | Consistencia fuerte multi-paso | Flujo implícito, replay, evolución de eventos ([Fowler](https://martinfowler.com/articles/201701-event-driven.html)) | Alta |
| Reverse ETL | Solo vendors | Activación de segmentos en SaaS | Cuando basta integración directa | Latencia batch, PII, gobierno | Media |
| Zero-ETL | AWS | Analítica casi en tiempo real sobre OLTP del mismo proveedor | Multi-cloud/neutralidad | Acoplamiento al proveedor [Inferencia] | Media (en crecimiento) |
| HTAP | TiDB VLDB | OLTP con analítica fresca en el mismo sistema | Cargas OLAP masivas y complejas | Contención si no hay aislamiento físico ([TiDB](https://www.cs.purdue.edu/homes/csjgwang/CloudNativeDB/TiDBVLDB20.pdf)) | Media; evidencia sobre todo del proveedor |

### Inferences
- [Inferencia] Estándares/referencias verificables hoy: spec de Iceberg (v3, v4 en desarrollo), protocolo Delta (paper VLDB), Debezium, Kafka KIP-98. No verificados: OpenLineage, Open Data Contract Standard, dbt (solo conocimiento general).

### Gaps
- Sin fuente primaria de data fabric (Gartner de pago), reverse ETL independiente, madurez de HTAP fuera de TiDB (SingleStore, Spanner, Aurora no leídos). Casos de Netflix, Airbnb, Shopify: sin cifras comparables primarias de mesh o medallion.
