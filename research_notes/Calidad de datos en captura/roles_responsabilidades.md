# Roles responsables de validar la calidad de datos en captura/recolección (por contexto)

Nota de método: fecha de corte oct-2026. Se leyeron completos o por secciones, vía pdftotext, ICH E6(R3) final, ICH E9, DHS8 Supervisor Manual, SCDM CCDM Handbook 2026, SCDM Topic Brief CDM Role Evolution, Documento de las Américas (OPS). Varias fuentes (DMBOK2, ISO 8000-150, GCDMP, SCDM Competency Framework, NAACCR, ESS QAF, AAPOR texto completo) NO se pudieron leer en texto íntegro (de pago, 403/404 o resumen parcial); se marcan como brechas. Etiquetas: "Fuente" = afirmado por la URL citada; "Inferencia" = síntesis mía.

## 1. ¿Quién es formalmente responsable de la calidad de datos en captura en cada contexto y qué dicen las normas?

### Takeaway
En ensayos clínicos la responsabilidad formal está explícita y dividida: el investigador responde por exactitud, integridad, legibilidad y oportunidad de lo que se reporta en el CRF; el patrocinador (sponsor) responde por el sistema de calidad, el control de calidad (monitoreo y data management son "las principales actividades de QC"), la validación de herramientas y la decisión de qué pasos hacen los datos "suficientemente buenos" para analizar. En encuestas oficiales/sociales la responsabilidad recae en el organismo ejecutor y, operativamente, en el supervisor de campo; en negocio, en data owner/steward (gobierno de datos). No existe un estándar equivalente a E6 para registros ni vigilancia que nombre roles; ahí la asignación es por práctica/contrato (brecha).

### Cited Findings

**Ensayos clínicos (ICH E6(R3), versión final Step 4, enero 2025)**
- Investigador: "debe asegurar la integridad de los datos bajo su responsabilidad, independientemente del medio" (2.12.1). — [ICH E6(R3)](https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf)
- 2.12.5: el investigador debe asegurar "accuracy, completeness, legibility and timeliness" de los datos reportados al sponsor en las herramientas de adquisición (p. ej. CRF) y otros reportes (p. ej. SAE), y debe revisar y avalar (endorse) los datos en hitos importantes acordados con el sponsor (p. ej. análisis interino). — [ICH E6(R3)](https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf)
- 2.12.2: registros fuente deben ser atribuibles, legibles, contemporáneos, originales, exactos y completos (ALCOA+); el investigador define qué es registro fuente y método de captura antes de iniciar; evitar pasos de transcripción innecesarios. 2.12.6: datos reportados consistentes con la fuente o discrepancias explicadas; correcciones trazables que no oculten la entrada original. — [ICH E6(R3)](https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf)
- 2.12.3: el investigador es responsable de la revisión oportuna de los datos, incluidos datos de fuentes externas (laboratorio central, imágenes, ePRO) que afecten elegibilidad, tratamiento o seguridad. — [ICH E6(R3)](https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf)
- 2.3.1: el investigador puede delegar actividades pero "retiene la responsabilidad última" y debe supervisar a los delegados de modo proporcional a la importancia de los datos; 2.3.3 exige registro de delegación. — [ICH E6(R3)](https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf)
- Sponsor 3.16.1: asegura integridad y confidencialidad; aplica QC a las etapas relevantes del manejo de datos, enfocándose en datos de mayor criticidad; pre-especifica en el protocolo qué datos y cómo (con diagrama de flujo en un documento como el data management plan); herramientas de adquisición "fit for purpose", validadas antes de uso; no debe cambiar datos ingresados por el investigador salvo justificación, acuerdo previo y documentación; no debe tener control exclusivo de los datos del DAT (para evitar cambios indetectables); debe determinar los pasos de data management previos al análisis y documentarlos (p); restringir acceso de edición antes de entregar datos para el análisis final/desenmascaramiento (r). — [ICH E6(R3)](https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf)
- 3.11.3: "Within clinical trials, monitoring and data management processes are the main quality control activities"; 3.11.4: el monitoreo puede hacerse con métodos y personas de distintos roles (p. ej. data scientist, monitoreo centralizado) pero por personas no involucradas en la conducción clínica en el sitio monitoreado. 3.11.1-3.11.2: QA y auditoría son basadas en riesgo y proporcionales. — [ICH E6(R3)](https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf)
- 3.4: el sponsor debe usar personas calificadas para tareas asignadas (biostatisticians, data scientists/data managers, auditors, monitors). Principio 5.1: investigadores, trial coordinators, monitores, auditores y bioestadísticos calificados por educación, formación y experiencia. — [ICH E6(R3)](https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf)
- Sección 4 (Data Governance, dirigida a "investigators and sponsors"): 4.2.1 captura: la extensión de la verificación de transcripción manual depende de la criticidad; metadatos acompañan los datos; considerar validaciones automáticas en el punto de captura "según el riesgo". 4.2.3 revisión de datos y metadatos planificada y basada en riesgo. 4.2.4 correcciones atribuidas, justificadas y apoyadas en fuente. — [ICH E6(R3)](https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf)
- Glosario E6(R3): "Data integrity" = grado en que los datos son atribuibles, legibles, contemporáneos, originales, exactos, completos, seguros y confiables, de modo que sean "fit for purpose". — [ICH E6(R3)](https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf)
- Versión en español de referencia regional: Documento de las Américas (OPS/Red PARF, basado en ICH E6(R1)): 5.9.1 "el investigador deberá asegurarse que los datos reportados al patrocinador en los formularios de datos (FRC) ... sean exactos, legibles, estén completos y en el tiempo requerido"; 5.9.2 consistencia con documentos fuente; 6.18.1 el monitoreo verifica que los datos sean "completos, exactos y verificables de los documentos fuente"; 6.18.2 el patrocinador designa monitores calificados; 6.1.3 control de calidad en cada etapa del manejo de datos; 6.4.1 patrocinador emplea individuos idóneos (bioestadísticos, etc.). — [Documento de las Américas (PDF e-legis-ar)](https://e-legis-ar.msal.gov.ar/htdocs/legisalud/migration/pdf/7283.pdf)

**Estadística / bioestadística en ensayos**
- ICH E9: "la responsabilidad de todo el trabajo estadístico ... recae en un estadístico apropiadamente calificado"; el "Trial Statistician" se define como quien es responsable de los aspectos estadísticos del ensayo; el protocolo debe ser aprobado por el personal responsable incluido el estadístico. E9 excluye explícitamente principios de data management y monitoreo ("covered in other ICH guidelines"). — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)
- E9 5.8: la credibilidad de los resultados depende de la calidad y validez de métodos y software de data management (entrada, almacenamiento, verificación, corrección, recuperación); data management debe basarse en SOPs; el sponsor debe restringir acceso al código de tratamiento durante la limpieza de la base. — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)
- E9 (blind review): revisión ciega entre el fin del ensayo y el desenmascaramiento cubre exclusión de sujetos/datos de los conjuntos de análisis, outliers, etc.; las decisiones se documentan; estadísticos del análisis interino no cegado no deben participar en la revisión ciega. — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)
- E6(R3) 4.2.6: "datos de calidad suficiente" para análisis interino/final deben definirse y lograrse con procesos de captura, verificación, validación, revisión y rectificación; actividades de finalización (reconciliación, codificación médica, desviaciones) confirmadas y documentadas según procedimientos pre-especificados; extracción de datos y determinación de conjuntos de análisis conforme al plan estadístico planificado. E6(R3) NO nombra quién firma el "database lock". — [ICH E6(R3)](https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf)
- Comentario (secundario) de que E9 no discute el proceso de database lock ni quiénes firman; en protocolos reales firman típicamente el biometrician responsable y el project manager clínico, o el head statistician. — [ASA community blog (Zink)](https://community.amstat.org/blogs/richard-zink/2016/04/12/good-analytical-practice-or-what-the-medical-product-industry-gets-right) y ejemplos de SAP/protocolos ClinicalTrials.gov, p. ej. [SAP NCT04530136](https://cdn.clinicaltrials.gov/large-docs/36/NCT04530136/SAP_001.pdf)

**Rol CDM según SCDM**
- SCDM: el Clinical Data Manager es "responsable del ciclo de vida del dato clínico desde la recolección hasta la entrega para análisis estadístico"; se enfoca en recolección, flujo de datos e integridad ("ensuring data is managed the right way"); actividades comunes: ciclo de vida de herramientas de recolección y estándares, flujo extremo a extremo, revisión y conciliación de datos, gestión de datos de terceros y proveedores, gestión de proyecto y documentación. Clinical Data Scientist añade riesgo, significado y valor del dato ("credible and reliable"). SCDM cita al CDM como "central steward of clinical data quality". — [SCDM Topic Brief CDM Role Evolution (PDF)](https://scdm.org/wp-content/uploads/2024/03/SCDM-Topic-Brief-The-CDM-Role-Evolution-FINAL.pdf)
- La certificación SCDM (desde 2004) define 70 competencias en 8 dominios (85% en Design, Project Management, Data Processing, Programming); GCDMP publicado en 2000 con 28 capítulos. — mismo Topic Brief.

**Encuestas (trabajo de campo)**
- DHS8 Supervisor Manual (2024): supervisores son "el vínculo principal entre la recolección en campo y la oficina central" y "responsables de asegurar la calidad y el éxito del trabajo de campo"; "controlar la calidad de la recolección es la función más importante del supervisor": observar entrevistas, revisar completitud, re-entrevistas (al menos una por conglomerado, opcional según encuesta), revisar Field Check Tables, reunión diaria con entrevistadores, escalar a un coordinador de campo. — [DHS8 Supervisor Manual](https://dhsprogram.com/pubs/pdf/DHSM2/DHS8-Supervisor-Manual-EN-15Oct2024.pdf)
- AAPOR Best Practices: "los controles deben hacerse en cada paso del ciclo de vida de la encuesta"; métodos: observación de entrevistadores, re-entrevistas y monitoreo de paradatos; verificar que la información de cuestionarios se edite y codifique con exactitud. (La página no usa los términos "supervisión" ni "validación"; resumen por herramienta de fetch, no leído íntegro.) — [AAPOR Best Practices](https://aapor.org/standards-and-ethics/best-practices/)
- Nota secundaria: llamadas de validación a 10-25% de encuestados, supervisor-entrevistador como factor continuo de calidad (no AAPOR, material de capacitación y enciclopedia SAGE). — [SAGE quality control](https://sk.sagepub.com/ency/edvol/embed/survey/chpt/quality-control); [SAGE supervisor ratio](https://sk.sagepub.com/ency/edvol/embed/survey/chpt/supervisortointerviewer-ratio)
- Detección de falsificación por entrevistadores (paradatos, GPS): [Statistical Journal of the IAOS 2016](https://content.iospress.com/articles/statistical-journal-of-the-iaos/sji1014)

**Estadística oficial**
- GSBPM: la validación de estructura empieza en 4.3 (Run collection), la de contenido en 5.3 "Review and validate"; edición/imputación en 5.4; reglas de validación se especifican en 2.5. El texto consultado no asigna roles. — [CROS Eurostat: Validation and GSBPM](https://cros.ec.europa.eu/book-page/validation-and-gsbpm)
- ESS QAF: indicador de exactitud y fiabilidad "source data, intermediate results and statistical outputs are regularly assessed and validated"; la responsabilidad institucional es de Eurostat, los NSI y otras autoridades nacionales. No se asigna a un cargo concreto. — [Eurostat QAF](https://ec.europa.eu/eurostat/web/quality/european-quality-standards/quality-assurance-framework)
- INEGI describe captura, codificación y validación de datos individuales como parte de preparar la base y que la validación corrige omisiones, incongruencias, etc.; la fase de captación la planean direcciones/subdirecciones y la ejecutan direcciones regionales y coordinaciones estatales. — [INEGI RNM 1146](https://www.inegi.org.mx/rnm/index.php/catalog/1146) y [RNM 811](https://www.inegi.org.mx/rnm/index.php/catalog/811)
- Ejemplo histórico (Panamá 1990, censo): separa "crítica" y "codificación"; un supervisor general lleva avance y supervisores de control de calidad de la revisión controlan crítica y codificación. — [manual censo Panamá 1990 (IPUMS)](https://users.pop.umn.edu/~rmccaa/ipumsla/panama\1990\pa90manucrco.pdf) (URL con backslashes tal como la devolvió la búsqueda; no abierta por mí, citada vía resumen de búsqueda).

**Vigilancia en salud pública**
- CDC (MMWR RR-13, 2001): la calidad de datos se evalúa por completitud y validez; la guía va dirigida a profesionales de salud pública, proveedores de datos y usuarios en niveles local/estatal/federal; no hallé desglose de quién hace qué. — [CDC MMWR RR-50(13)](https://www.cdc.gov/mmwr/PDF/rr/rr5013.pdf) (vía resumen de búsqueda, no leído íntegro); [ejemplo de evaluación NJ](https://cste.confex.com/cste/2015/webprogram/Paper5180.html)

**Registros (cáncer)**
- Descripciones de empleadores (secundarias): el abstractor/registrador captura datos de tumores según reglas de codificación y estadificación (CoC, registros estatales), aplica edits hasta "cero errores" antes de enviar, y el control de calidad (auditorías, re-abstracting, estudios de confiabilidad) lo asigna al gestor del registro; en programas CoC los abstractores deben tener CTR o aprobarlo en plazo. — [UM System JD](https://www.umsystem.edu/hr/job-descriptions/5132c); [FCDS memo 2011](https://fcds.med.miami.edu/memos/2011_09memo.pdf); [St. Joseph posting](https://careers.sjchs.org/jobs/1814344-certified-tumor-registrar)

**Negocio / gobierno de datos**
- DMBOK2 (vía wiki gubernamental canadiense que cita pp. 76-77): "Data Stewards manage data assets on behalf of others and in the best interests of the organization"; tipos: Chief, Executive, Enterprise, Business, Technical y Coordinating stewards; "Data Owners are Business Data Stewards who have approval authority for decisions about data within their domain"; Technical Data Stewards incluyen DBAs, integradores de datos y Data Quality Analysts. — [GCcollab Data Steward](https://wiki.gccollab.ca/Data_Steward)
- Guía CDMP (secundaria): el owner tiene responsabilidad de negocio y autoridad de decisión/financiamiento; el steward ejecuta operativamente; el custodian es rol técnico de almacenamiento, transporte y protección. — [open-exam-prep CDMP 2.4](https://open-exam-prep.com/study-guides/cdmp/data-governance-b/data-stewardship); [datamanagement.wiki data custodian](https://datamanagement.wiki/_export/xhtml/role/data_custodian)
- ISO 8000-150:2022 trata de establecer roles y responsabilidades adecuados para gestión de calidad de datos, con marco y modelo funcional; no cubre modelos de procesos (8000-61), evaluación/certificación ni madurez (8000-62/64). Lista de roles concretos no leída (norma de pago). — [catálogo SCC](https://scc-ccn.ca/standardsdb/standards/8179505); [ISO](https://www.iso.org/standard/80753.html) (403 al fetch)

### Matriz RACI por fase (INFERENCIA, construida desde las fuentes anteriores; no existe en ninguna fuente como tabla única)
R = ejecuta; A = rinde cuentas (uno solo); C = consultado; I = informado. Contexto base: ensayo clínico. Variaciones por contexto debajo.

| Actividad / fase | PI (investigador) | Coord. estudio / capturista | Sponsor (patrocinador) | CDM / Data Mgmt Lead | Programador BD | CRA / Monitor | Bioestadístico | Codificador médico | QA/Auditor |
|---|---|---|---|---|---|---|---|---|---|
| Diseño: definir datos críticos, CRF/eCRF, DMP, plan de validación | C | C | A | R | R (build/UAT) | C | C (R para SAP y variables) | C | I/C (revisión de procesos) |
| Captura: entrada fiel a la fuente, oportuna | A | R | I | I | – | I | – | – | – |
| Captura: verificación SDV/SDR y monitoreo centralizado | I | C | A (delega) | C | – | R | C | – | – |
| Limpieza: queries, conciliación (SAE, lab, ePRO), revisión de datos | A (responde queries) | R (responde) | A para el proceso | R (emite/gestiona) | R (listados/checks) | R (hallazgos de sitio) | C | R (MedDRA/WHODrug) | I |
| Revisión ciega y decisiones sobre conjuntos de análisis | C | – | A | C | – | C | R | – | I |
| Bloqueo (lock) y endoso final | A (avala datos de su sitio, E6(R3) 2.12.5) | – | A (decisión de lock) | R | R (ejecuta) | C | C/aprobador | C | I |
| Análisis | I | – | A | C (entrega datasets) | C | – | R | – | I/C |
| QA/auditoría del sistema | C | I | A (sistema de calidad) | C | C | C | C | – | R |

Notas: (a) E6(R3) dice que el sponsor "determina los pasos" (3.16.1(p)) y que el investigador "avala" datos en hitos; no define un firmante único del lock, por eso "A" compartido es inferencia: en la práctica se documenta en SOP/DMP/SAP del sponsor. (b) Cuando el sponsor delega a una CRO, la responsabilidad sigue en el sponsor (E6(R3) 3.6.4/3.6.9 sobre oversight de proveedores, leído parcialmente).

Variaciones por contexto (INFERENCIA):
- Observacional/epidemiológico (cohortes, ensayos pragmáticos): PI/jefe de estudio es A; el rol CDM puede ser un "data manager" del centro coordinador; no aplica E6 salvo estudios intervencionales. No hallé estándar rector equivalente a E6 (brecha).
- Vigilancia: A = autoridad sanitaria que opera el sistema; R de captura = notificador/establecimiento; revisión = epidemiólogo/analista del nivel local o estatal.
- Encuestas oficiales: A = unidad responsable de la encuesta (director del proyecto); R captura = entrevistador/capturista; R control en campo = supervisor; R validación/edición = equipo de procesamiento y metodólogo; el estadístico/analista no "bloquea" formalmente en la fuente.
- Registro: A = director/gestor del registro; R = abstractor + QC del registro central.
- Negocio: A = data owner del dominio; R = data steward (reglas, definiciones) y data quality analyst (perfilado, medición); custodian R de la infraestructura.

### Inferences
- La asignación "clínica" más precisa viene de E6(R3): investigador = exactitud en la fuente y en el CRF; sponsor = sistema, QC y declaración de calidad suficiente del dataset. Eso corrige el uso común de "el data manager es responsable de la calidad": el CDM ejecuta los procesos del sponsor, no sustituye la responsabilidad del investigador sobre el dato en origen.
- En captura propiamente dicha, la línea entre prevención (diseño del instrumento y del flujo, validaciones en el punto de captura) y detección (queries, monitoreo) es lo que distingue al CDM (prevención y limpieza) del monitor (detección en sitio) y del supervisor de campo (detección en encuestas).

### Gaps
- Texto de DMBOK2 (definiciones primarias de steward/owner/custodian) y de ISO 8000-150 (lista de roles) no leídos; solo vía fuentes secundarias.
- GCDMP: no se obtuvo texto de capítulos de roles; SCDM Competency Framework: la página no lista roles.
- No se halló descripción oficial INEGI/DANE/IBGE de "supervisor de captura" ni "capturista" (solo contexto de procesamiento).
- NAACCR (404) y CDC RR-13 no leídos íntegramente; sin norma equivalente a E6 para registros y vigilancia.
- E6(R3) no define "database lock" ni su firmante.

## 2. Distinciones precisas: Data Quality Analyst, Data Steward, Data Manager (CDM) y Supervisor de captura; roles restantes, confusiones y terminología

### Takeaway
Son cuatro familias distintas: (1) gobierno de datos corporativo (owner, steward, custodian, DQ analyst), (2) gestión de datos clínicos (CDM, programador, codificador, líder DM), (3) operaciones de campo/captura (capturista, supervisor, coordinador), (4) garantes independientes (CRA/monitor, QA/auditor, bioestadístico, PI). Los mismos nombres ("data manager", "data steward", "data coordinator") cambian de significado entre sectores; en español agrava la ambigüedad "administrador/gestor/custodio de datos".

### Cited Findings

**Definiciones por rol (con fuente)**
- Data Owner: en DMBOK2 es un business steward con autoridad de aprobación sobre decisiones de su dominio. — [GCcollab](https://wiki.gccollab.ca/Data_Steward)
- Data Steward: SME que gestiona activos de datos en nombre de otros; define elementos de datos y reglas de negocio; no es dueño, asiste al owner; monitorea calidad, corrige problemas emergentes, implementa planes de mejora. — [GCcollab](https://wiki.gccollab.ca/Data_Steward); [datamanagement.wiki steward](https://datamanagement.wiki/role/data_steward)
- Data Custodian: rol técnico de almacenamiento/transporte/protección; títulos comunes DBA, modelador, ETL developer; (distinto de steward: custodian ve estructuras y entorno técnico, steward ve contenido y reglas). — [datamanagement.wiki custodian](https://datamanagement.wiki/_export/xhtml/role/data_custodian) (DMBOK2 incluye DBAs bajo "Technical Data Steward", ver [GCcollab](https://wiki.gccollab.ca/Data_Steward); es decir DMBOK2 y wikis divergen).
- Data Quality Analyst (ofertas de empleo, evidencia secundaria): perfilado, escritura de reglas de calidad para CDEs, detección de anomalías y análisis de causa raíz, en colaboración con stewards que validan definiciones y umbrales; steward aprueba reglas. — [Insight Global](https://insightglobal.com/jobs/find_a_job/florida/jupiter/sr-data-quality-analyst/job-553504/); [Built In](https://builtin.com/job/data-quality-analyst/7436624); [Aegon](https://www.aegon.com/careers/vacancies/netherlands/hague/investments/data-quality-analyst); [EWSolutions](https://www.ewsolutions.com/essential-guide-to-the-data-quality-analyst-skills-and-career-path/)
- Clinical Data Manager: ver sección 1 (SCDM Topic Brief). — [SCDM](https://scdm.org/wp-content/uploads/2024/03/SCDM-Topic-Brief-The-CDM-Role-Evolution-FINAL.pdf)
- Supervisor de campo (encuestas): ver DHS8 (calidad de campo como función principal; selecciona re-mediciones; revisa field check tables; opera como enlace con la oficina central). Aclaración: en DHS7 y anteriores el rol se llamaba "Supervisor/Editor", es decir combinaba supervisión y edición de cuestionarios. — [DHS8](https://dhsprogram.com/pubs/pdf/DHSM2/DHS8-Supervisor-Manual-EN-15Oct2024.pdf); [DHS7 Supervisor Editor Manual](https://www.dhsprogram.com/pubs/pdf/DHSM2/DHS7-Supervisor-Editor-Manual-EN-02May2017-DHSM2.pdf)
- Monitor/CRA: monitoreo verifica derechos y seguridad, y que "los datos reportados estén completos, sean exactos y verificables a partir de los documentos fuente" (Documento de las Américas 6.18.1); E6(R3) 3.11.4 incluye SDR, SDV, analítica de datos y visitas; los monitores no deben estar involucrados en la conducción clínica en el sitio monitoreado. — [Documento de las Américas](https://e-legis-ar.msal.gov.ar/htdocs/legisalud/migration/pdf/7283.pdf); [ICH E6(R3)](https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf)
- QA/Auditor: QA basada en riesgo; auditorías proporcionales; auditores calificados (E6(R3) 3.11.1, 3.11.2, 3.11.2.1). QC ≠ QA: QC son las actividades operativas (monitoreo, data management), QA la verificación independiente del sistema. — [ICH E6(R3)](https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf)
- Study coordinator: E6(R3) menciona "trial coordinators" como cualificados (principio 5.1) y la delegación por el investigador (2.3); no define el rol con detalle en el texto leído. — [ICH E6(R3)](https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf)
- Codificador médico: E6(R3) 4.2.6(b) incluye "medical coding" entre las actividades de finalización de datos antes del análisis; SCDM lista "Medical Coding" entre buenas prácticas CDM. — [ICH E6(R3)](https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf); [SCDM Topic Brief](https://scdm.org/wp-content/uploads/2024/03/SCDM-Topic-Brief-The-CDM-Role-Evolution-FINAL.pdf)
- Programador de BD: dominio "Programming" es uno de los 4 dominios centrales de la certificación CDM (competencias de build/validación de la base), dentro del perfil CDM. — [SCDM Topic Brief](https://scdm.org/wp-content/uploads/2024/03/SCDM-Topic-Brief-The-CDM-Role-Evolution-FINAL.pdf)
- Registry data abstractor / CTR (ahora ODS según un resumen secundario): ver sección 1. — [open-exam-prep NCRA](https://open-exam-prep.com/study-guides/ncra-ods-c/exam-overview-profession/ctr-to-ods-evolution) (verificar en ncra-usa.org)
- Survey methodologist: sin fuente primaria obtenida; el rol aparece en prácticas AAPOR de diseño/chequeo en cada paso del ciclo (ver sección 1). — [AAPOR](https://aapor.org/standards-and-ethics/best-practices/)
- Data Management Lead / Data Coordinator: no hallé definición normativa; SCDM menciona que los CDM asumen cada vez más gestión de proyectos y "Clinical Data Scientist". — [SCDM Topic Brief](https://scdm.org/wp-content/uploads/2024/03/SCDM-Topic-Brief-The-CDM-Role-Evolution-FINAL.pdf); [búsqueda GCDMP/ofertas](https://xtalks.com/job/senior-clinical-data-manager-usa/)

**Terminología: inconsistencias documentadas**
- SCDM llama al CDM "central steward of clinical data quality" (uso coloquial de "steward") mientras DMBOK2 usa "Data Steward" como rol de gobierno con reglas de negocio; no son el mismo puesto. — [SCDM](https://scdm.org/wp-content/uploads/2024/03/SCDM-Topic-Brief-The-CDM-Role-Evolution-FINAL.pdf); [GCcollab](https://wiki.gccollab.ca/Data_Steward)
- Una guía lista nueve tipos de steward incluyendo Executive Sponsor y Data Owner, que no coincide con el modelo de 4 tipos citado de DMBOK2; las fuentes divergen también en el alcance del custodian. — resultados de búsqueda: [open-exam-prep DMBOK 1.3](https://open-exam-prep.com/study-guides/cdmp/exam-overview-dmbok/data-management-organization)
- El mismo DQ Analyst figura en DMBOK2 como un tipo de technical steward (vía GCcollab) pero en ofertas de empleo como rol separado. — [GCcollab](https://wiki.gccollab.ca/Data_Steward); ofertas arriba.
- "SCDM" significa tanto la Society como "Senior Clinical Data Manager" en ofertas. — [Xtalks](https://xtalks.com/job/senior-clinical-data-manager-usa/)
- DHS: "Supervisor/Editor" (ediciones antiguas) vs "Supervisor" (DHS8) con CAPI. — enlaces DHS arriba.
- En estudios clínicos "monitor" ≠ "monitor" de seguridad (IDMC/CIMD = comité independiente de monitoreo de datos, distinto del monitor del sitio). — [Documento de las Américas](https://e-legis-ar.msal.gov.ar/htdocs/legisalud/migration/pdf/7283.pdf)
- Credencial: tumor registrar CTR vs ODS (renombrado 2024 según resumen secundario, no verificado en NCRA). — ver arriba.

**Uso en español / Latinoamérica**
- La traducción regional oficial de E6 (Documento de las Américas, OPS) usa FRC/CRF "formulario de reporte de casos", "patrocinador", "monitor", "bioestadísticos", "manejo de datos", "custodia de registros", "CIMD"; no usa "data manager" ni "gestor de datos clínicos" como cargo en los pasajes leídos (6.5 titula "Administración del Estudio, Manejo de Datos y Custodia de Registros"). — [Documento de las Américas](https://e-legis-ar.msal.gov.ar/htdocs/legisalud/migration/pdf/7283.pdf)
- INEGI y censos latinoamericanos: tareas "captura, codificación, validación/crítica"; la "crítica" (revisión de cuestionarios) y el "crítico" son términos regionales para lo que DHS llama field editing/edit. — [INEGI RNM 1146](https://www.inegi.org.mx/rnm/index.php/catalog/1146); [Panamá 1990](https://users.pop.umn.edu/~rmccaa/ipumsla/panama\1990\pa90manucrco.pdf)

### Inferences (no respaldadas literalmente por una fuente)
- Diferenciación operativa en una línea cada una:
  - Data Steward: define y aprueba significado, reglas y umbrales de un dominio; es el "quién decide qué es correcto". No mide ni limpia por sí solo.
  - Data Quality Analyst: mide, perfila y diagnostica contra esas reglas; reporta y propone causa raíz; no tiene autoridad de aprobar la definición.
  - Data Owner: A del dominio y de la política; no opera la limpieza.
  - Data Custodian: protege y opera infraestructura; no es responsable del significado del dato (en DMBOK2 cae dentro de technical steward).
  - Data Manager / CDM: gestiona el ciclo del dato de un estudio específico (diseño de CRF, DMP, limpieza, conciliación, lock); combina funciones que en negocio se dividen entre steward, DQ analyst y proyectos de TI. Es el más cercano a "estudio" en vez de "dominio".
  - Supervisor de captura/campo: controla en tiempo real el proceso humano de captura (observación, re-entrevista, revisión de completitud), con autoridad sobre el personal de campo; no define reglas del dato ni libera la base. En estadística oficial el análogo de edición/validación masiva pertenece a procesamiento, no al supervisor.
  - Capturista (data entry operator): transcribe de papel; debería ser R de fidelidad a la fuente, no A de calidad. Fuente primaria específica no hallada.
- Traslape: DQ analyst↔CDM (revisión de datos), steward↔CDM (definición de CRF/estándares, aunque CDISC/CDASH no se consultó), supervisor de campo↔monitor CRA (ambos verifican la fuente; difiere en que el CRA verifica documentos fuente de sitios independientes y el supervisor gestiona a su propio equipo).
- Conflicto de interés: E6(R3) separa a monitores del sitio monitoreado; DHS pone al supervisor dentro del equipo que recolecta; por eso las re-entrevistas dependen de procedimientos para evitar autocontrol.
- Términos en español recomendados para el informe (propuesta mía): data steward = "custodio/administrador de datos" solo con aclaración (la palabra "custodio" choca con data custodian); preferir "responsable de dominio (steward)" y "custodio técnico (custodian)".

### Gaps
- Sin fuente primaria para: Data Coordinator, Data Management Lead, Survey Methodologist, capturista, supervisor de captura (término exacto en español) y programador de BD como rol aparte.
- CDISC (CDASH/SDTM roles) no consultado.
- No se verificó ningún uso oficial de "gestor de datos clínicos" en AEMPS/ANMAT/COFEPRIS.

## 3. Rol del bioestadístico y del PI al declarar los datos listos para análisis

### Takeaway
El PI avala (endorses) la exactitud y completitud de los datos de su sitio en hitos acordados y resuelve queries; el sponsor decide cuándo el dataset es de calidad suficiente y documenta los pasos; el bioestadístico es responsable de lo estadístico (SAP, revisión ciega, conjuntos de análisis, impacto de los datos faltantes/desviaciones) pero ni E6(R3) ni E9 le atribuyen explícitamente el "lock".

### Cited Findings
- PI: revisa y avala datos reportados en hitos (E6(R3) 2.12.5; sponsor solicita endoso 3.16.1(o)). — [ICH E6(R3)](https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf)
- Sponsor determina los pasos de DM antes del análisis (según propósito: IDMC, interino, final), los documenta, y para interinos gestiona el acceso/cambio de datos según los pasos cumplidos; antes del análisis final/desenmascaramiento restringe el acceso de edición. — [ICH E6(R3) 3.16.1(p)(q)(r)](https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf)
- Sección 4 menciona como proceso clave "data finalisation prior to analysis, unblinding, allocation to analysis data sets" y roles/acceso a información no cegada definidos y documentados (plan de DM, SAP). — [ICH E6(R3) sec. 4, 4.1.2](https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf)
- Estadístico: responsable de lo estadístico; revisión ciega de datos antes de abrir el ciego; decisiones de exclusión, outliers, transformaciones; SAP finalizado en o cerca de la revisión ciega; "once data validation is complete, the analysis should proceed according to the pre-defined plans". — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)
- Ejemplos de práctica real: revisión ciega firmada por biometrician y project manager; confirmación escrita de lock por head statistician. — [SAP NCT04530136](https://cdn.clinicaltrials.gov/large-docs/36/NCT04530136/SAP_001.pdf) y [comentario ASA](https://community.amstat.org/blogs/richard-zink/2016/04/12/good-analytical-practice-or-what-the-medical-product-industry-gets-right) (nota: son documentos de estudios individuales, no norma).

### Inferences
- "Declarar datos listos" es una decisión colectiva documentada (DM + estadístico + clínico + QA de proceso), con el sponsor como A; el PI avala su sitio, no la base global. En estudios sin sponsor industrial (académicos), el PI/jefe de estudio suele asumir también el rol de sponsor (inferencia; no verificada en fuente).
- Fuera de ensayos (encuestas, vigilancia) no encontré norma que dé al estadístico poder de veto; suele ser el director del proyecto.

### Gaps
- Texto de SOPs modelo de lock (SCDM GCDMP "Database Lock") no accesible.
- Roles de firma en estudios académicos y observacionales: sin fuente.

## 4. Competencias, certificaciones y trayectorias

### Takeaway
Cada ecosistema tiene su credencial: CCDA/CCDM/CCDS (SCDM) para datos clínicos, CCRC/CCRA (ACRP) y CCRP (SoCRA) para coordinación/monitoreo, CDMP (DAMA) para gobierno de datos, CQE (ASQ) para calidad, CTR/ODS (NCRA) para registros. Casi todas exigen años de experiencia, no un título específico.

### Cited Findings
- CCDM (SCDM): elegibilidad = bachelor + 2 años full-time CDM, o associate + 3 años, o 4+ años sin título (o equivalente part-time); recertificación: 1,8 CEU en 3 años. — [SCDM CCDM Handbook 2026](https://scdm.org/wp-content/uploads/2026/07/SCDM-CCDM-certification-handbook-26.pdf)
- CCDA: nivel de entrada (menos de 2 años de experiencia, según resumen de búsqueda); CCDS: bachelor + 6 años, associate + 9, o 10+ años sin título. (Resumen del buscador sobre manual SCDM; CCDA/CCDS no verificados en el texto completo.) — [SCDM certification](https://scdm.org/certification); [CCDA Study Guide 2025](https://scdm.org/wp-content/uploads/2025/05/SCDM_CCDA_ExamStudyGuide.pdf)
- SCDM: competencias de certificación en 8 dominios (Design, Project Management, Data Processing, Programming, Testing, Training, Personnel Management, Review); habilidades blandas: detalle, pensamiento lógico, adaptabilidad, comunicación, investigar tendencias de datos, trabajo interfuncional; conocimientos: GCP, SDLC, auditoría, estadística básica, modelos/terminologías médicas. — [SCDM Topic Brief](https://scdm.org/wp-content/uploads/2024/03/SCDM-Topic-Brief-The-CDM-Role-Evolution-FINAL.pdf)
- Trayectoria: SCDM propone transición de Clinical Data Manager a Clinical Data Scientist (riesgo, vigilancia de proveedores, revisión centralizada de datos). — mismo Topic Brief.
- CDMP (DAMA): Associate (DMF ≥60%, sin experiencia), Practitioner (DMF + 2 exámenes de especialidad ≥70%, "ideal para 2-10 años"), Master (≥80%, mínimo 10 años y revisión de CV); exámenes de especialidad incluyen data quality y data governance; renovación anual con CPD. — [DAMA CDMP](https://www.dama.org/cdmp)
- ACRP: CCRC y CCRA requieren 3.000 horas de experiencia verificable (puede dispensarse hasta 1.500). SoCRA CCRP: 2 años full-time en los últimos 5 (o 1 año con título en investigación clínica). Fuentes secundarias; confirmar en los sitios. — [CASRAI](https://casrai.org/compare/acrp-vs-socra-certification); [IntuitionLabs](https://intuitionlabs.ai/articles/acrp-vs-socra-certification)
- ASQ CQE: 8 años de experiencia (3 en toma de decisiones), con exenciones por educación; acreditado ANAB/ISO 17024. — [ASQ CQE](https://asq.org/cert/quality-engineer); [Umbrex](https://umbrex.com/resources/professional-credentials-directory/cqe/)
- CTR (NCRA): 3 rutas de elegibilidad (grado asociado acreditado + práctica; 60 créditos + certificado + práctica; 60 créditos con anatomía/fisiología + 1.950 horas de experiencia en registro); 20 horas de CE para mantener; posible renombre a ODS (2024). Fuentes secundarias. — [open-exam-prep NCRA](https://open-exam-prep.com/study-guides/ncra-ods-c/exam-overview-profession/ctr-to-ods-evolution); [CTR eligibility chart](https://www.swtc.edu/uploadedpdfs/academic/health-occupations/CTR-Eligibility-Chart-Summer-2022.pdf)

### Inferences
- Para analistas de calidad de datos en negocio no existe una certificación específica dominante; CDMP con especialidad en data quality es la más cercana. Para supervisor/capturista de campo no hay credencial profesional estandarizada hallada (la formación es del propio proyecto, p. ej. capacitación DHS).
- Trayectorias típicas (inferencia desde las ofertas y SCDM): coordinador/capturista → CDA/CDM → senior CDM/DM lead → clinical data scientist/head of DM; en negocio: DQ analyst → steward/coordinating steward → data governance lead.

### Gaps
- IAIDQ/IQCP: sin resultados verificables (programa posiblemente descontinuado o rebautizado como IQ International; no confirmado).
- Certificaciones latinoamericanas equivalentes (p. ej. de CONACYT, ANMAT) no investigadas.
- Salarios y demanda: fuera de alcance y sin datos.
