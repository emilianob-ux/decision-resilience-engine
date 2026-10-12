# Revisión humana y tasas de error en captura/registro de datos; limpieza manual de datos

Convenciones: "Hallazgos citados" = afirmaciones leídas en la fuente (resumen/abstract o texto completo, indicado). "Inferencias" = cálculo o razonamiento mío, no afirmado por la fuente. Unidad estándar: errores por 10,000 campos (1% = 100 por 10,000). Fecha de las notas: 2026-10-12. Donde solo vi el abstract lo indico ("solo abstract"); donde leí texto completo/PDF lo indico ("texto completo").

---

## 1. Tasas de error medidas por método de captura; ¿vale la pena la doble digitación frente a entrada simple con validaciones?

### Takeaway
La evidencia consistente: la entrada simple ronda 0.3% de campos (~29-37 por 10,000 en meta-análisis; 15-22 por 10,000 en ensayos con CRF), la doble digitación independiente ~0.14% (~14 por 10,000, rango 4-33), la abstracción desde historia clínica (source-to-database) ~6.6% (rango 0.7%-27.8%), y OCR/escaneo ~0.7% con 2 órdenes de magnitud de variabilidad. La revisión visual casi no mejora la entrada simple; la doble digitación sí. La ganancia absoluta de la doble digitación es pequeña cuando la entrada simple ya es buena (CAST: 22 vs 15 por 10,000, P=0.09; CHART: 15 por 10,000, no la usaron), por lo que su valor depende de cuánto cuesta un error y de si los chequeos de rango/lógica atrapan los errores relevantes.

### Cited Findings

**Meta-análisis y síntesis**
- Revisión sistemática/meta-análisis (93 artículos, 1978-2008): tasas de error de 2 a 2,784 por 10,000 campos. Pooled: abstracción de historia clínica (MRA) 6.57% (IC95% 5.51-7.72; rango 70-2,784 por 10,000); escaneo óptico (OMR/OCR) 0.74% (0.21-1.60; rango 2-358); entrada simple 0.29% (0.24-0.35; rango 4-650); doble digitación 0.14% (0.08-0.20; rango 4-33). Hay heterogeneidad en los cuatro métodos. Los autores señalan que la variabilidad del OCR depende de limpieza de datos, verificación visual posterior, entrenamiento en letra y compatibilidad formulario-software, y que la variabilidad de la entrada simple se explica por subtipos de entrada. (texto completo del preprint) — [Garza et al., Int J Med Inform 2025, doi:10.1016/j.ijmedinf.2024.105749](https://doi.org/10.1016/j.ijmedinf.2024.105749); [texto en PMC10775420](https://pmc.ncbi.nlm.nih.gov/articles/PMC10775420/)
- El mismo estudio señala que otros reportaron tasas de OCR hasta 3 veces mayores que la digitación manual por teclado, y que usó la tasa informada o, si solo había tasa normalizada, asumió denominador 10,000. (texto completo) — [PMC10775420](https://pmc.ncbi.nlm.nih.gov/articles/PMC10775420/)
- Revisión previa de la propia literatura (Nahm 2008): 42 artículos con tasas source-to-database (principalmente registros) con promedio 976 errores por 10,000 campos; 19 artículos con comparación CRF-to-base de datos con promedio 14 por 10,000. El estudio NIDA CTN midió 14.3 por 10,000 en su primer año con EDC y atribuye la baja tasa a la ausencia de abstracción de historia clínica; en ensayos en papel con doble digitación auditados CRF-to-base obtuvo 3.4, 0 y 3.7 por 10,000. (texto completo) — [Nahm, Pieper, Cunningham, PLoS ONE 2008, PMC2516178](https://pmc.ncbi.nlm.nih.gov/articles/PMC2516178/)

**Estudios primarios, entrada simple vs doble**
- CAST (Reynolds-Haertle & McBride 1992): experimento cruzado aleatorizado en centros clínicos; 42,278 campos comparados con formulario en papel. Tasa global 19 por 10,000; entrada simple 22 y doble 15 por 10,000 (P=0.09, regresión de Poisson). La doble digitación tomó 37% más tiempo (~90 min extra por mes por clínica). (solo abstract) — [PubMed 1334820](https://pubmed.ncbi.nlm.nih.gov/1334820/)
- CHART (Gibson et al. 1994): se re-digitaron datos de 44 pacientes por un segundo data manager y se compararon. Tasa combinada de ambas entradas 14 por 10,000 (IC95% 10-19); entrada inicial sola 15 por 10,000 (9.5-22); tasa de errores "vitales/importantes" 2.5 por 10,000 (0.68-6.4). Conclusión: no usan doble digitación en CHART. (solo abstract) — [PubMed 7851109](https://pubmed.ncbi.nlm.nih.gov/7851109/)
- Day, Fayers & Harvey 1998: simulación con errores de dígito en presión arterial; los chequeos de rango simples detectan los errores que más afectan estimación, significancia y potencia; los errores no detectables por rango, aunque posiblemente numerosos, tuvieron poca importancia en las conclusiones. Doble digitación y análisis exploratorio detectan cosas distintas (la doble digitación solo asegura fidelidad CRF-base; el análisis exploratorio cuestiona la plausibilidad); proponen que el análisis exploratorio sea siempre obligatorio. (solo abstract) — [PubMed 9492966](https://pubmed.ncbi.nlm.nih.gov/9492966/)
- Zhang & Hu 1998 "Single or double data entry: considerations based on a simple binomial model" (modelo binomial): solo localicé el título/DOI, sin abstract accesible. — [PubMed 9492969](https://pubmed.ncbi.nlm.nih.gov/9492969/)
- Paulsen et al. 2012 (200 pacientes, cuestionarios de resultados reportados por el paciente, EpiData Entry): doble digitación 0.046 errores por 1,000 campos (IC95% 0.001-0.258) vs entrada simple 0.370 por 1,000 (0.160-0.729), p=0.020; OMR sin diferencia estadística con doble digitación (0.046 por 1,000); ICR (carácter manuscrito) 6.734 por 1,000 (0.817-24.113) sin diferencia con simple ni doble. Conclusión: el procesamiento automático es alternativa válida a doble digitación en formularios altamente estructurados (casillas, códigos numéricos, sin fechas). (texto completo) — [PMC3320865](https://pmc.ncbi.nlm.nih.gov/articles/PMC3320865/)
- Goldberg, Niemierko & Turchin 2008 (bases de datos de investigación en un centro): tasas detectadas por doble digitación de 2.3% a 26.9%; errores por digitación y por mala interpretación del documento original; la detección por violación de restricciones (constraint) subestima significativamente la tasa total y las alarmas integradas previenen solo una fracción; muchos errores no son aleatorios (agrupados). (solo abstract) — [PMC2656002](https://pmc.ncbi.nlm.nih.gov/articles/PMC2656002/)
- Mauri et al. 2008 (6,446 historias; un solo digitador): el "control doble ciego" del data manager no mejoró la fiabilidad; las entradas al final de la hoja de captura tuvieron más errores; el control electrónico fue estadísticamente más efectivo que la búsqueda manual en historias seleccionadas al azar. Concluyen que el control doble ciego es un costo evitable. (solo abstract) — [PMC2596166](https://pmc.ncbi.nlm.nih.gov/articles/PMC2596166/)
- Atkinson 2012 cita errores de transferencia de datos de hasta 26.9% (de Goldberg) y propone un método para estimar el nivel de confianza sobre el número de errores introducidos tras doble digitación. (solo abstract) — [PubMed 22985318](https://pubmed.ncbi.nlm.nih.gov/22985318/)

**Revisión visual / leer en voz alta vs doble digitación**
- Kawado et al. 2003 (Registro Japonés de Trasplante Renal; 560 CRF, 104,720 campos): la entrada simple tuvo 358 errores (0.34% por campo). Tasa de detección de errores: doble digitación por operador distinto 88.3%; doble digitación por el mismo operador 69.0%; lectura en voz alta (RA) con operador distinto 59.5%; RA con el mismo operador 39.9% (diferencias significativas, p<0.001). Tiempo total: DDE 74.8 h vs RA 57.9 h. (solo abstract) — [PubMed 14500053](https://pubmed.ncbi.nlm.nih.gov/14500053/)
- Barchard & Pace 2011 (195 estudiantes asignados al azar a doble digitación, chequeo visual o entrada simple; 30 hojas con seis tipos de dato): el chequeo visual dejó "2958% más errores" que la doble digitación (cifra tal cual aparece en el abstract del artículo) y no fue significativamente mejor que la entrada simple; 66% de los participantes en chequeo visual obtuvo un alfa de Cronbach incorrecto, a veces con error mayor a .40. (abstract del artículo en PDF) — [doi:10.1016/j.chb.2011.04.004](https://doi.org/10.1016/j.chb.2011.04.004); [copia del abstract](https://online210.psych.wisc.edu/wp-content/uploads/PSY-210_Unit_Materials/PSY-210_Unit05_Materials/Barchard_abstract_CHB_2011.pdf)
- Barchard et al. 2020 (412 estudiantes; errores introducidos deliberadamente en 20 hojas): la doble digitación fue significativa y sustancialmente más precisa que visual, lectura en voz alta con compañero y lectura en voz alta en solitario; pero quienes cometieron errores en doble digitación hicieron coincidir las dos entradas, a veces introduciendo errores nuevos; sugieren que la conciliación debe apuntar a la hoja original (no a la otra entrada), idealmente con una tercera persona. La lectura en voz alta en solitario fue más rápida que doble digitación pero menos precisa, y a veces mejor que la revisión visual en un tipo de dato. (solo abstract) — [PubMed 30859478](https://pubmed.ncbi.nlm.nih.gov/30859478/)
- Büchele et al. 2005 "Single vs. double data entry" (Epidemiology, carta): solo localicé cita y DOI, no el contenido. — [PubMed 15613958](https://pubmed.ncbi.nlm.nih.gov/15613958/)

**Alternativa basada en muestreo**
- King & Lashley 2000 proponen reemplazar el paso de verificación de la doble digitación por la verificación de una muestra de registros de la base de entrada simple mediante un plan de muestreo continuo (control estadístico de calidad), con ventajas: lo puede hacer el personal de captura, se puede calcular el costo/tiempo y la ganancia de calidad, y el plan se puede construir para alcanzar metas de calidad. (solo abstract) — [PubMed 10715507](https://pubmed.ncbi.nlm.nih.gov/10715507/)
- Juul (Universidad de Aarhus, guía "Take Good Care of Your Data") recomienda doble digitación de todo o parte de los datos con EpiData, razonamiento costo-beneficio (barato en un ensayo de 50+50 pacientes; en una encuesta de 10,000 cuestionarios puede no justificarse para todos), y da un ejemplo: segunda digitación de 1,000 de 10,000 cuestionarios; 5% de cuestionarios con alguna discrepancia; un operador tenía 25% de error vs 0-0.3% del resto, y se re-digitaron todos los suyos. (texto completo) — [takecare.pdf](http://www.epidata.dk/php/downloadc.php?file=takecare.pdf)
- EpiData (hilos de la lista de usuarios, no el manual oficial): se crea una copia en blanco ("Prepare Double Entry"), se re-digita y se compara con "Validate Duplicate Files"; hasta tres campos pueden usarse para emparejar registros por clave; sin campo clave se emparejan por número de registro (depende del orden). Fuente de baja autoridad (foros). — [lista EpiData](https://lists.umanitoba.ca/archives/list/epidata-list@lists.umanitoba.ca/thread/UIRFQ2VPT772MYO5S7ETQKGNS4A2TRMF)

**Revisión de 100% vs muestra (verificación contra fuente)**
- Tudur Smith et al. 2012 (ensayo oncológico): comparación de 100% SDV vs sin SDV vs monitoreo central; discrepancias sin patrón sistemático y efecto despreciable sobre la sobrevida global (HR 1.18 con 100% SDV, 1.18 sin SDV); mayor diferencia en el resultado subjetivo "respuesta objetiva" (OR 1.67 vs 2.45), atribuida a diferencias en lectura de tomografías. SDV fue costoso. (solo abstract) — [PMC3520949](https://pmc.ncbi.nlm.nih.gov/articles/PMC3520949/)
- I-SPY COVID (Abbasi et al. 2025): SDV retrospectivo sobre 23% de los eCRF (333 de 1,111 pacientes) cambió 0.36% (1,234/340,532) de los campos; no cambió el tipo de desenlace; costo 61,073 horas-persona y US$6.1 M. (solo abstract) — [PMC12572212](https://pmc.ncbi.nlm.nih.gov/articles/PMC12572212/)
- Yamada et al. 2021 (11 sujetos, 5,617 datos; 19.7% críticos): tasa de error en datos críticos detectada por monitoreo en sitio con 100% SDV 7.6%, por monitoreo remoto basado en riesgo 7.6%, por revisión de data managers 3.9%. (solo abstract) — [PubMed 33258688](https://pubmed.ncbi.nlm.nih.gov/33258688/)
- Houston et al. 2018: revisión de 15 publicaciones sobre métodos de auditoría SDV: proporción auditada de 3% a 100%, frecuencia de 6 a 24 meses, métodos de clasificación y cálculo de error inconsistentes, sin método uniforme de "mejor práctica"; errores de transcripción y personal inexperto como causas principales; auditorías repetidas con el mismo conjunto de datos mostraron ~40% de mejora en exactitud/completitud. (solo abstract) — [PubMed 29783038](https://pubmed.ncbi.nlm.nih.gov/29783038/)
- Houston et al. 2021 (encuesta en Australia/NZ, 441 estudios): 55% aplicó SDV; quienes no hicieron 100% incluyeron 1-25% de los puntos de dato. (solo abstract) — [PubMed 33503495](https://pubmed.ncbi.nlm.nih.gov/33503495/)

**Estándares de la industria (BPO)**
- No encontré un estándar publicado independiente. Fuentes comerciales mencionan objetivos contractuales de 98% a 99.95% (campo vs carácter), advierten que "key-verify/double punching" a veces cubre solo campos seleccionados y que el SLA debe indicar cobertura y métrica. Fuente de baja calidad (blog de proveedor); usar solo como contexto. — [Invensis](https://www.invensis.net/data-entry/tips-to-improve-data-quality); [Outsource Accelerator](https://www.outsourceaccelerator.com/glossary/data-entry/)

### Inferences
- Pasar de entrada simple a doble reduce el error a ~la mitad (0.29% → 0.14% en el pooled; 22 → 15 por 10,000 en CAST; 0.370 → 0.046 por 1,000 en Paulsen), pero el beneficio absoluto es de ~7-15 errores por 10,000 campos en contextos con entrada simple "buena". La doble digitación tiene más sentido en campos críticos, volumen moderado, o digitadores/formularios con tasa de error alta (la tasa por operador del ejemplo Juul sugiere medir por operador antes de decidir).
- Las dos técnicas son complementarias, no sustitutas (Day 1998; Goldberg 2008): doble digitación captura errores de transcripción con valores plausibles (que los chequeos de rango no ven); los chequeos de rango/lógica captan valores imposibles, incluidos errores presentes en el documento fuente. Una política defendible es validación en línea para todo + doble digitación (o muestreo con escalamiento) para campos críticos.
- El patrón "revisión visual ≈ entrada simple" (Barchard 2011) y "lectura en voz alta con compañero < DDE" (Kawado) es consistente en dos diseños distintos (estudiantes aleatorizados, y CRF reales con errores detectados); pero Barchard son estudiantes con datos de laboratorio, no personal profesional.
- La mayor parte del error total viene de pasos previos a la digitación (abstracción de historia clínica 6.6% vs 0.14-0.29%); mejorar la digitación no corrige eso.

### Gaps
- No pude acceder a los textos completos de Reynolds-Haertle 1992, Gibson 1994, Kawado 2003, Day 1998, Zhang & Hu 1998, Büchele 2005 (solo abstracts/títulos): faltan detalles de diseño (p. ej., cómo se definió el campo, tipos de error).
- "Hong 2013" (doble vs simple, costo-efectividad), "Helms 2001" y "Houston 2019" no los localicé con las búsquedas realizadas (Europe PMC y web); no los incluyo. Nahm 2012 (capítulo de Clinical Research Informatics, doi 10.1007/978-1-84882-448-5_10) se identificó pero no pude leerlo; sus datos se reflejan indirectamente en Nahm 2008 y Garza 2025.
- No hay análisis de costo-efectividad formal con costo por error evitado en lo que leí; solo tiempo (+37% CAST; 74.8 h vs 57.9 h Kawado).
- El pooled de Garza cubre 1978-2008; no hay actualización a 2026 de las tasas por método.

---

## 2. Cómo diseñar un plan de muestreo defendible para verificar datos capturados

### Takeaway
Definir primero la métrica (errores / campos inspeccionados, por 10,000 campos, con numerador y denominador documentados), luego la meta (aceptable por tipo de campo: GCDMP/SCDM cita 0-10 por 10,000 en críticos y 20-100 en no críticos; 50 por 10,000 global como "popular"), y luego dimensionar la muestra con aritmética binomial o con tablas AQL (ISO 2859-1). Las reglas "√N+1" y "10%" son prácticas comunes pero no estadísticamente derivadas; para una afirmación defendible conviene el tamaño de muestra por nivel de confianza o por plan de aceptación con riesgos declarados.

### Cited Findings
- Definición y cálculo: tasa de error = errores detectados / campos inspeccionados; se expresa por 10,000 campos: p. ej., DEMOG 10 errores en 100 campos = 1,000 por 10,000; VITALS 20 en 400 campos = 500 por 10,000. Deben documentarse numerador y denominador (¿contar campos derivados?, ¿mes y año de una fecha derivada son 1 o 2 errores?, ¿campos por defecto o poblados automáticamente?); dos proveedores con 10 errores cada uno pueden diferir por factor 2 solo por la definición del denominador (ejemplo de 50,000 campos). La documentación debe permitir recrear el muestreo y el cálculo. (texto completo) — [SCDM, Measuring Data Quality, J Soc Clin Data Manag 2023, doi:10.47912/jscdm.329](https://scdm.org/wp-content/uploads/2024/07/Measuring-Data-Quality.pdf)
- Tamaño de muestra: "mejor práctica" es un tamaño estadísticamente apropiado por inspección, documentado con el equipo del estudio; dos reglas comunes son √N + 1 de la población y 10% de la población. (texto completo) — [SCDM 2023](https://scdm.org/wp-content/uploads/2024/07/Measuring-Data-Quality.pdf)
- Nivel aceptable: no hay estándar de la industria; definiciones populares: 50 por 10,000 global; 0-10 por 10,000 en variables críticas y 20-100 por 10,000 en no críticas. Las regulaciones no fijan mínimos; cada organización define el suyo. El error es menos importante en campos no críticos. (texto completo) — [SCDM 2023](https://scdm.org/wp-content/uploads/2024/07/Measuring-Data-Quality.pdf)
- La experiencia de auditoría (DCRI) sugiere que una serie de auditorías pequeñas durante el estudio logra mayor calidad que una sola auditoría grande al cierre (según resumen de la búsqueda; no leí la fuente primaria). — [Springer, DIA J](https://link.springer.com/article/10.1177/216847900604000403)
- ISO 2859-1 (muestreo por atributos, inspección normal): nivel general II es el predeterminado; lote 3,201-10,000 con nivel II da código L, muestra de 200 unidades. Ejemplo comercial: AQL 2.5% mayor y 4.0% menor con Ac=10 y 14 respectivamente para n=200 (valores del ejemplo del sitio, no la tabla oficial). Fuente secundaria (sitio de inspección de calidad); la tabla completa no estaba en texto. — [qualityinspection.org](https://qualityinspection.org/aql-2-5-samples); catálogo de la norma: [iteh ISO 2859-1:1989](https://iteh.es/catalog/standards/iso/f35f3cb7-1dad-4f15-b7a1-d2a43010790a/iso-2859-1-1989)
- Plan de aceptación con aceptación cero: n ≥ log(α)/log(1-p_L) (aprox. regla de 3: n ≈ 3/p para α=0.05). (preprint arXiv, derivación para estudios piloto) — [arXiv 1707.00222](https://arxiv.org/pdf/1707.00222)
- Plan de muestreo continuo (Dodge-type): verificación de muestra de registros de la base de entrada simple con parámetros para metas de calidad; ejemplos de parámetros en el artículo (no los vi). — [King & Lashley 2000](https://pubmed.ncbi.nlm.nih.gov/10715507/)
- Los estudios de auditoría usan proporciones entre 3% y 100% de los datos y definiciones inconsistentes de error. — [Houston 2018](https://pubmed.ncbi.nlm.nih.gov/29783038/)
- El control de calidad continuo con capacitación formal en abstracción mantuvo error de 1% (denominador todos los campos, optimista) a 3% (campos poblados, conservador), con descenso de 0.51 puntos porcentuales por cada evento de QC adicional. Reportar ambos denominadores es una buena práctica. (solo abstract) — [Garza et al. 2022, BMC Med Res Methodol, PMC9380367](https://pmc.ncbi.nlm.nih.gov/articles/PMC9380367/)
- Selección selectiva: en edición estadística oficial, la edición selectiva prioriza registros con errores influyentes mediante una puntuación de relevancia; la macro-edición ahorra 35-80% de verificación manual vs micro-edición (Statistics Sweden); el "over-editing" dedica esfuerzo a errores sin impacto en cifras publicadas. (según resultados de búsqueda; no leí los documentos completos) — [CBS Países Bajos](https://www.cbs.nl/-/media/imported/documents/2008/51/2008-18-x10-pub.pdf)

### Inferences (cálculos propios, aritmética binomial, no provienen de las fuentes; verificables)

Fórmulas:
- Estimación de tasa p con margen ±e al 95% (aprox. normal): n = 1.96² · p(1−p) / e². Ejemplos: p=0.5% ± 0.2% → n ≈ 4,778 campos; p=1% ± 0.5% → ≈ 1,522 campos; p=6.5% ± 2% → ≈ 584 campos. Es campos, no registros.
- Aceptación cero con confianza C de que la tasa real es ≤ p (cuota de tolerancia, LTPD): n = ln(1−C)/ln(1−p). Tabla (campos sin errores requeridos):

| tolerancia p (por 10,000) | C=90% | C=95% | C=99% |
|---|---|---|---|
| 100 (1%) | 230 | 299 | 459 |
| 50 (0.5%) | 460 | 598 | 919 |
| 10 (0.1%) | 2,302 | 2,995 | 4,603 |
| 5 (0.05%) | 4,605 | 5,990 | 9,209 |

- Límite superior Clopper-Pearson unilateral 95% (por 10,000 campos): 0 errores en 3,000 campos → ≤ 9.98; 0 en 10,000 → ≤ 3.0; 2 en 10,000 → ≤ 6.29; 3 en 10,000 → ≤ 7.75; 15 en 10,000 → ≤ 23.09.
- Curva OC del plan ISO código L (n=200, Ac=10, valores binomiales; se aplica a unidades defectuosas, p. ej., registros con ≥1 error): probabilidad de aceptar con 2.5% defectuosos 0.987; 5% 0.583; 8% 0.069; 10% 0.008. Con n=200, c=0: 0.5% → 0.367; 1% → 0.134; 2% → 0.018.

Lectura práctica y reglas de escalamiento propuestas (diseño mío, no de una fuente):
1. Unidad de muestreo: registros (clúster) y campos dentro; los errores dentro de un mismo registro u operador están correlacionados (Goldberg: errores agrupados; Juul: un operador con 25%), así que el IC por campos es optimista; estratificar por operador, sitio, tipo de formulario y criticidad.
2. Estratos: críticos (aceptación cero o ≤ 10 por 10,000, muestra mayor, hasta 100%/doble digitación) y no críticos (20-100 por 10,000, muestra menor).
3. Escalamiento análogo a la "severidad" de ISO 2859 (normal → reforzada → reducida): si una auditoría supera el umbral, ampliar la muestra del lote/operador (o 100%) y re-entrenar; tras N lotes consecutivos aceptados, reducir muestreo; regla de reconocer causa raíz (formulario, entrenamiento) en lugar de solo corregir hallazgos (Houston 2018 muestra mejora ~40% con auditorías repetidas).
4. Declarar riesgos α/β, p aceptable, p rechazable, denominador y forma de contar errores antes de ver los datos; documentarlo como pide el SCDM.
5. Aplicar 100% donde un error cambia la decisión: Tudur Smith e I-SPY sugieren que la verificación total contra fuente aporta poco en desenlaces objetivos, pero sí en desenlaces subjetivos (respuesta objetiva) o seguridad (2 AE adicionales en I-SPY).

### Gaps
- No obtuve las tablas oficiales ISO 2859-1/ANSI Z1.4 (de pago); solo fuentes secundarias para letra de código L (n=200 para lote 3,201-10,000, nivel II). Los valores Ac/Re por AQL deben verificarse en la norma.
- No localicé una fuente primaria para la regla √N+1 más allá de SCDM; no hay justificación estadística en lo leído.
- No encontré un estudio que valide empíricamente reglas de escalamiento para auditorías de captura de datos.
- La norma ISO 2859-1 tiene edición vigente que no pude verificar (un resultado secundario mencionó una edición 2026; no confirmado).

---

## 3. Auditorías fuente-a-base de datos: cómo calcular la tasa por campo / por 10,000 campos; duplicado de abstracción, reconciliación y supervisión

### Takeaway
La auditoría se define comparando valores de la base con el documento fuente (o con el CRF) y contando discrepancias sobre campos inspeccionados; hay que separar etapas (fuente→CRF vs CRF→base) porque el error se concentra en la abstracción. Para registros/revisión de historias, la abstracción duplicada independiente mide acuerdo (kappa, % acuerdo) que complementa la tasa de error.

### Cited Findings
- Fórmula, ejemplo y ambigüedades del conteo: ver sección 2 (SCDM 2023). — [SCDM](https://scdm.org/wp-content/uploads/2024/07/Measuring-Data-Quality.pdf)
- Auditorías CRF-a-base "identifican errores adicionales introducidos en el procesamiento" y no evalúan errores de transcripción fuente→CRF, medición o registro; las auditorías fuente-a-base sí; el promedio publicado CRF-base fue 14 por 10,000 y fuente-base 976 por 10,000. — [Nahm 2008](https://pmc.ncbi.nlm.nih.gov/articles/PMC2516178/)
- Meta-análisis: ver sección 1; se calculó la tasa con errores / campos inspeccionados, o con denominador 10,000 cuando solo había tasa normalizada, y se agruparon fuente-a-base y fuente-a-CRF como "MRA". — [Garza 2025 (PMC10775420)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10775420/)
- Confiabilidad de abstracción (Mi et al. 2013, 75 historias de reemplazo total de rodilla, un cirujano y dos coordinadores): kappa cirujano-coordinador 0.59-1 (un coordinador) y 0.49-1 (otro); % acuerdo 82-100% y 70-100%; intra-evaluador kappa 0.66-1 (97-100% acuerdo); entre coordinadores kappa 0.49-1 (76-100%). Fiabilidad excelente para información de baja complejidad técnica y moderada a buena para la más compleja. (solo abstract) — [PMC3684546](https://pmc.ncbi.nlm.nih.gov/articles/PMC3684546/)
- Gianinazzi et al. 2015 (cáncer infantil, 9 clínicas): segunda abstracción independiente; intra-evaluador (154 historias) kappa 0.6-0.8 y acuerdo 75-95%; inter-evaluador (70 historias) kappa 0.70-0.83 y acuerdo 86-100%; se observaron efectos de aprendizaje en todas las variables. (solo abstract) — [PMC4441480](https://pmc.ncbi.nlm.nih.gov/articles/PMC4441480/)
- Arts et al. 2002: marco de procedimientos de calidad de datos en registros médicos, dividido en centrales y locales, y en prevención, detección de datos imperfectos y causas, y acciones/correcciones. (solo abstract) — [PubMed 12386111](https://pubmed.ncbi.nlm.nih.gov/12386111/)
- Weiskopf & Weng 2013: cinco dimensiones (completitud, corrección, concordancia, plausibilidad, vigencia) y siete métodos de evaluación (comparación con estándar de oro, acuerdo entre elementos de datos, acuerdo entre fuentes, comparación de distribuciones, chequeos de validez, revisión de logs, presencia de elementos); poca consistencia entre estudios. (solo abstract) — [PMC3555312](https://pmc.ncbi.nlm.nih.gov/articles/PMC3555312/)
- URECA (Rho, estudio multicéntrico de asma): doble digitación entre sitio y centro coordinador por rondas; el sistema genera informe de discrepancias, el personal del centro compara con el documento fuente y re-digita si es necesario, y bloquea la base de esa ronda; las tasas por formulario sirven para identificar formularios complejos y se rediseñaron formularios; tasas de formularios de 4.65% a 0.00% a lo largo de rondas (ejemplo "Respiratory and Allergy Symptoms"). (póster) — [Rho poster](https://www.rhoworld.com/wp-content/uploads/Double_Data_Entry_Quality_Control_in_URECA_Urban_Environment_and_Childhood_Asthma.pdf)
- Conciliación en transferencias: validar procesos y reconciliar para asegurar integridad en transferencia/migración de datos y evitar pérdida o modificaciones no intencionadas (ICH E6(R3) 4.2.5). El alcance de la verificación de datos transcritos manualmente debe considerar la criticidad (4.2.1(a)). (texto completo) — [ICH E6(R3)](https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf)
- Supervisión por operador: Juul recomienda registrar el ID del operador para detectar al digitador con error elevado. — [takecare.pdf](http://www.epidata.dk/php/downloadc.php?file=takecare.pdf)

### Inferences
- Un informe de auditoría defendible debe reportar: población de campos, regla de selección de la muestra, definición de error (con clasificación por criticidad), numerador, denominador (todos vs poblados), tasa e IC, y causas.
- La abstracción duplicada con kappa es útil para variables subjetivas/complejas; para variables objetivas conviene % de acuerdo o tasa de error contra estándar de oro (los kappa bajos con alto % acuerdo pueden deberse a prevalencia extrema; esto es conocimiento estadístico general, no de las fuentes).
- No encontré un estudio de verificación por supervisores ("spot-checks") con cifras; la evidencia disponible es de auditorías QC y monitoreo (Houston, Garza 2022, Tudur Smith).

### Gaps
- No hay (en lo hallado) estudios cuantitativos de "spot-checks" de supervisores aislados ni de conciliación documentada como intervención.
- Tasas de error por campo en abstracción duplicada comparadas directamente con tasas fuente-a-base en la misma muestra: no localizadas.

---

## 4. Tipología de errores de captura humana y contramedidas de proceso (no tecnológicas)

### Takeaway
Los errores no son solo teclazos: incluyen malinterpretación del documento, desplazamiento de valores a campos vecinos, preferencia por dígitos (terminal digit), y errores sistemáticos de operador o formulario. Las contramedidas de proceso con evidencia: diseño de formularios, entrenamiento y control de calidad continuo, reducción de pasos de transcripción, minimizar interrupciones, medir por operador y retroalimentar.

### Cited Findings

**Tipología (fuentes)**
- Sustitución, omisión, inserción, transposición: en mecanografía de texto, Grudin 1983 (novatos: sustitución 75% de errores, transposición 4%, omisión 4%, inserción 9%; expertos con perfiles variables: p. ej., inserción 75% en un experto, sustitución 69% en otro; transposición 3-11%). Es mecanografía de texto en inglés, no captura de datos numéricos, pero es la base de la tipología. (texto completo) — [Grudin 1983](https://gwern.net/doc/design/typography/1983-grudin.pdf)
- Errores por mala interpretación del documento original y errores agrupados en "clusters especiales y cognitivos"; las restricciones integradas a la base detectan solo una fracción. (solo abstract) — [Goldberg 2008](https://pmc.ncbi.nlm.nih.gov/articles/PMC2656002/)
- Errores por desplazar el valor correcto a la variable vecina: al encontrar un error, revisar las variables vecinas porque son de alto riesgo; recomienda no calcular nada antes de la captura (registrar fechas, no edades) y codificar texto antes. (texto completo) — [Juul](http://www.epidata.dk/php/downloadc.php?file=takecare.pdf)
- Posición en la hoja de captura: más errores hacia el final de la hoja. (solo abstract) — [Mauri 2008](https://pmc.ncbi.nlm.nih.gov/articles/PMC2596166/)
- Preferencia terminal de dígito: con medición manual de presión arterial, 32.8% de los dígitos terminales de la sistólica eran 0 (esperado 20% porque se instruyó registrar al par más cercano); tras pasar a medición automatizada bajó a 12.4% (esperado 10%), y la presión sistólica media estimada subió 5.09 mm Hg (IC95% 4.98-5.19); 1,541,227 mediciones en 11 clínicas. (solo abstract) — [Kottke et al. 2022, JAMA Netw Open](https://pmc.ncbi.nlm.nih.gov/articles/PMC9434355/)
- Errores de fecha como prioridad: en limpieza, los errores de fecha, sexo faltante o mal especificado, duplicados y resultados biológicamente imposibles son errores prioritarios; los errores de fecha contaminan variables derivadas. (texto completo) — [Van den Broeck 2005](https://pmc.ncbi.nlm.nih.gov/articles/PMC1198040/)
- En el SDV, errores de transcripción y personal inexperto fueron la fuente principal de error reportada. — [Houston 2018](https://pubmed.ncbi.nlm.nih.gov/29783038/)
- Tipos de datos y precisión del método: el método de verificación se desempeñó distinto según el tipo de dato (lectura en voz alta solitaria mejor que visual en un tipo). — [Barchard 2020](https://pubmed.ncbi.nlm.nih.gov/30859478/)

**Factores humanos**
- Interrupciones: cada interrupción se asoció a +12.7% de errores clínicos en administración de medicamentos (98 enfermeras, 4,271 medicaciones); con 3 interrupciones, tasa de error clínico 38.9% vs 25.3% sin interrupciones. (solo abstract; contexto clínico, no captura de datos) — [Westbrook 2010](https://pubmed.ncbi.nlm.nih.gov/20421552/)
- En médicos de urgencias (observación directa): errores de prescripción aumentaron con interrupción (RR 2.82; IC95% 1.23-6.49) y multitarea (RR 1.86; 1.35-2.56); dormir por debajo del promedio RR 16.44 (4.84-55.81); la memoria de trabajo fue protectora; carga de trabajo sin efecto. (solo abstract; contexto clínico) — [Westbrook 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC6204927/)
- Diseño de formulario: formularios con demasiados detalles en una página aumentan las discrepancias. Fuente secundaria vía búsqueda (no leída). — [PMC4170533](https://pmc.ncbi.nlm.nih.gov/articles/PMC4170533/)
- Capacitación y QC continuo: ver Garza 2022 (−0.51 puntos porcentuales por evento de QC) y Houston 2018 (~40% de mejora en auditorías repetidas). — [PMC9380367](https://pmc.ncbi.nlm.nih.gov/articles/PMC9380367/)
- Formularios: el rediseño de formularios identificados por altas tasas de error redujo estas tasas a lo largo del tiempo en URECA. — [Rho poster](https://www.rhoworld.com/wp-content/uploads/Double_Data_Entry_Quality_Control_in_URECA_Urban_Environment_and_Childhood_Asthma.pdf)
- ICH E6(R3) 2.12.2: evitar pasos de transcripción innecesarios entre el registro fuente y la herramienta de adquisición de datos. — [ICH E6(R3)](https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf)
- Efectos en análisis: un solo error de captura puede convertir una correlación moderada en cero o una prueba t significativa en no significativa (Barchard & Pace 2011). — [doi](https://doi.org/10.1016/j.chb.2011.04.004)

### Inferences
- No hallé estudios de captura de datos que midan fatiga o carga de trabajo directamente; extrapolo desde estudios clínicos (Westbrook) con cautela: es plausible que interrupciones y falta de sueño aumenten errores de captura, pero no está demostrado en datos de digitación en lo que leí.
- Contramedidas de proceso derivadas: (a) minimizar transcripciones y recodificar antes, (b) registrar el ID del operador y medir tasa por operador, (c) formularios cortos con campos en el orden del documento fuente y unidades/formatos de fecha fijos, (d) separar al verificador del digitador (Kawado: mismo operador detecta menos), (e) conciliar contra el original y por una tercera persona (Barchard 2020), (f) permitir bloques sin interrupciones y limitar sesiones largas (inferencia), (g) vigilar preferencia terminal de dígito con histogramas de dígitos finales como indicador de calidad de medición, (h) lectura de instrumento digital en vez de manual cuando sea posible (Kottke).
- Errores de unidades, formato de fecha (DD/MM vs MM/DD) y valores por defecto: no hallé fuentes cuantitativas específicas en esta búsqueda; son categorías habituales pero no las respaldo con cifras.

### Gaps
- Sin fuentes cuantitativas sobre errores de unidades, formato de fecha, valores por defecto o fatiga en digitación de datos de investigación.
- Grudin es mecanografía de texto de 1983: los porcentajes no se pueden trasladar directamente a captura numérica.
- No leí la fuente completa de diseño de formularios (PMC4170533); es afirmación de resultado de búsqueda.

---

## 5. Metodología de limpieza de datos: detección, diagnóstico y edición

### Takeaway
Van den Broeck et al. (2005) definen limpieza como un ciclo repetible de cribado (screening), diagnóstico y edición, con un plan previo y registro de cada decisión. La edición excesiva y la corrección sin documentación son riesgos explícitos en la literatura.

### Cited Findings
- Definición: "proceso de detectar, diagnosticar y editar datos defectuosos". Ciclo de tres etapas, repetido; puede iniciarse en tres puntos; los errores pueden ocurrir en cualquier etapa del flujo de datos, incluso durante la limpieza. (texto completo) — [Van den Broeck et al., PLoS Med 2005;2(10):e267, doi:10.1371/journal.pmed.0020267, PMID 16138788](https://pmc.ncbi.nlm.nih.gov/articles/PMC1198040/)
- Screening: cuatro tipos de anomalías (datos faltantes o en exceso; valores atípicos e inconsistencias; patrones inusuales en la distribución conjunta; resultados inesperados del análisis); expectativas predefinidas (rangos, distribuciones, relaciones); métodos: doble digitación, chequeos de rango y consistencia, diagramas de caja, dispersión, tabulaciones cruzadas, detección estadística de atípicos; los inliers erróneos se estiman examinando o re-midiendo una muestra. (texto completo) — [PMC1198040](https://pmc.ncbi.nlm.nih.gov/articles/PMC1198040/)
- Diagnóstico: cada punto sospechoso se clasifica como erróneo, extremo verdadero, normal verdadero o idiopático; cortes blandos (activan cribado) vs duros (diagnóstico inmediato); rastrear el valor en el flujo de datos, revisar variables relacionadas, consultar al personal o re-medir. El diagnóstico es laborioso y su costo suele subestimarse. (texto completo) — [PMC1198040](https://pmc.ncbi.nlm.nih.gov/articles/PMC1198040/)
- Edición: corregir, eliminar o dejar sin cambio; los valores imposibles no se dejan: se corrigen si se encuentra el valor correcto y si no se eliminan; los extremos verdaderos suelen permanecer; las exclusiones post hoc se reportan; hacer análisis con y sin atípicos/imputación; retroalimentar al protocolo y capacitación. (texto completo) — [PMC1198040](https://pmc.ncbi.nlm.nih.gov/articles/PMC1198040/)
- Faltantes: reglas predefinidas de manejo; los códigos sustitutos (p. ej., 999) deben corregirse antes del análisis; la imputación debe justificarse. (texto completo) — [PMC1198040](https://pmc.ncbi.nlm.nih.gov/articles/PMC1198040/)
- Documentación: el protocolo debe incluir plan de limpieza (presupuesto, personal, expectativas, procedimientos, reglas de decisión); cada dato debe tener registro de banderas, diagnósticos, tipo de edición, fechas y personal; el reporte debe describir tipos y tasas de error, tasas de eliminación/corrección. El artículo no usa el término "audit trail" pero describe el equivalente (según la lectura). Observa que rara vez se reportan métodos de limpieza o tasas de error en la literatura médica. (texto completo) — [PMC1198040](https://pmc.ncbi.nlm.nih.gov/articles/PMC1198040/)
- Datos inconsistentes: dos principios (recodificar todo lo inconsistente a faltante, o juzgar con otra información); cualquiera sea la decisión, debe documentarse por escrito. (texto completo) — [Juul](http://www.epidata.dk/php/downloadc.php?file=takecare.pdf)
- Estadística oficial: edición selectiva y macroedición para evitar sobre-edición; costos de edición/imputación de 20%-40% de recursos de institutos de estadística (según resultados de búsqueda, sin leer documento primario). — [CBS](https://www.cbs.nl/-/media/imported/documents/2008/51/2008-18-x10-pub.pdf); [UNECE/Statistics Sweden resultados](https://cros.ec.europa.eu/group/30/files/1184/download)
- Resultados de la detección: chequeos de rango atrapan los errores que más afectan la inferencia (Day 1998), pero subestiman la tasa total (Goldberg 2008); el control electrónico fue más efectivo que revisar historias al azar a mano en el estudio de Mauri. — ver sección 1.

### Inferences
- Una secuencia defendible: (1) plan de limpieza antes del análisis con reglas duras/blandas por variable; (2) cribado automatizado y manual por listados impresos de valores sospechosos y de vecinos; (3) diagnóstico contra el documento original; (4) edición con justificación; (5) re-cribado hasta convergencia; (6) reporte de tasas.
- Esfuerzo proporcional a sensibilidad del análisis a atípicos y faltantes (Van den Broeck), y a criticidad del campo (SCDM/ICH).

### Gaps
- No hay estudios comparativos de efectividad de métodos de limpieza distintos de la simulación de Day 1998; no leí otras guías de edición (UNECE) completas.

---

## 6. Cómo corregir errores sin destruir la pista de auditoría

### Takeaway
Principio normativo estable: la corrección debe ser atribuible, fechada, justificada, apoyada en la fuente, y no debe oscurecer el valor original; las correcciones se hacen por un proceso controlado (no editando "en la ventana de datos").

### Cited Findings
- ICH E6(R3) (Step 4, 2025): 2.12.2 "Los cambios a registros fuente deben ser trazables, no deben oscurecer la entrada original y deben explicarse si es necesario (vía audit trail)"; 2.12.6 los cambios en datos reportados deben ser trazables, explicados y no oscurecer la entrada original; 4.2.4 corregir errores que puedan afectar la fiabilidad de los resultados, atribuidos a la persona/sistema, justificados y respaldados por registros fuente cercanos a la entrada original, en forma oportuna; definición de audit trail: muestra actividades, entrada inicial y cambios, por quién, cuándo y, si aplica, por qué; en sistemas computarizados seguro, generado por computadora y con sello de tiempo; 4.2.2(b) no deshabilitar audit trails. (texto completo, parafraseado) — [ICH E6(R3)](https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf)
- ICH E6(R3), sección del patrocinador sobre datos (ítem "(j)"; no verifiqué el número de sección padre): el patrocinador debe permitir la corrección de errores, incluidos datos ingresados por participantes, justificadas y respaldadas por registros fuente cercanos a la entrada original. (texto completo) — [ICH E6(R3)](https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf)
- 21 CFR 11.10(e): los cambios de registro "no deben oscurecer información registrada previamente" y la documentación de audit trail se conserva tanto tiempo como el registro. (confirmado por fuentes secundarias que reproducen el texto; no pude abrir eCFR directamente) — [Creighton, 21 CFR Part 11](https://www.creighton.edu/fileadmin/user/ResearchCompliance/IRB/Policies_and_Procedures/InfoEd_21CFRPart11.pdf); [AVEVA docs](https://docs.aveva.com/bundle/batch-management/page/1508746.html)
- Registros en papel (guía ICH previa, hospedada por Nova): una sola línea sobre el dato incorrecto, fecha, iniciales y explicación; no oscurecer el original. (fuente secundaria) — [Nova SE](https://cms.nova.edu/ocr/forms/ICH%20Guidelines%20for%20Source%20Documents%20and%20Records.pdf)
- Juul: no corregir directamente en la ventana de datos ("el riesgo de corregir la variable o caso equivocado es alto" y "la pista de auditoría se rompe"); hacer correcciones en un archivo de comandos que genera una nueva versión, con bitácora (log book) y conservar la salida de la fusión como documentación; imprimir listados de valores sospechosos y escribir en ellos las correcciones tras ir al documento original. (texto completo) — [takecare.pdf](http://www.epidata.dk/php/downloadc.php?file=takecare.pdf)
- Van den Broeck: registro por dato de banderas, diagnósticos, tipo de edición, fechas y personal; archivar datos con justificación de cambios en cada etapa. — [PMC1198040](https://pmc.ncbi.nlm.nih.gov/articles/PMC1198040/)
- Barchard 2020: en doble digitación la resolución de discrepancias debe apuntar al documento original (no a igualar las dos entradas). — [PubMed 30859478](https://pubmed.ncbi.nlm.nih.gov/30859478/)

### Inferences
- Registro mínimo de cada corrección: identificador del registro/campo, valor anterior, valor nuevo, motivo (código + texto), evidencia fuente consultada, quién, cuándo, quién aprobó; los hallazgos sin evidencia fuente se marcan como "idiopáticos" y se mantiene el valor original, con bandera. (síntesis mía de ICH E6(R3) y Van den Broeck.)
- No sobrescribir: mantener el valor original y la versión editada (versionado), y distinguir correcciones de transcripción (fidelidad al documento) de correcciones de contenido (que requieren consulta al origen del dato).

### Gaps
- No pude leer el texto de 21 CFR 11.10(e) directamente en eCFR (redirigido); se apoya en copias secundarias.
- No revisé guías específicas de NIH/NIHR sobre correcciones ni normas ISO 8000/ISO 14155; podrían complementar.

---

## Resumen de calidad de fuentes
- Alta: ICH E6(R3) (texto completo), Van den Broeck 2005 (texto completo), SCDM 2023 (texto completo), Nahm 2008 (texto completo), Garza 2025/preprint (texto completo), Paulsen 2012 (texto completo), Juul (texto completo).
- Media (solo abstract de revistas indexadas): Kawado, Reynolds-Haertle, Gibson, Day, Barchard (2011 y 2020), Goldberg, Mauri, Tudur Smith, Abbasi, Yamada, Houston, Mi, Gianinazzi, Kottke, Westbrook.
- Baja o secundaria: ISO 2859 vía sitios de inspección, 21 CFR 11 vía copias, BPO vía blogs, EpiData vía foro.
- Discrepancia a notar: los resúmenes de búsqueda intermedios sugerían que "2958%" de Barchard 2011 era un error tipográfico; el abstract del artículo en PDF lo muestra tal cual. Otro estudio del mismo grupo (póster de UNLV) menciona "28 veces menos errores" para doble digitación; es una cifra de póster no revisada por pares.
