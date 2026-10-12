# Seguridad de datos y cumplimiento regulatorio en Data Engineering (estado a oct 2026)

**AVISO: estas notas son investigación técnica, no asesoramiento legal.** Las citas provienen de textos primarios (EUR-Lex/Cellar, CURIA, EDPB, eCFR, leyes nacionales, documentación oficial de proveedores) leídos directamente; las secciones "Inferencias" son interpretación propia y deben validarse con asesoría legal/DPO. Fecha de corte: 12-oct-2026.

**Nota de método.** EUR-Lex (HTML/PDF) bloqueó las descargas automáticas (HTTP 202 de WAF). Los textos de reglamentos/sentencias se leyeron desde el servidor de la Oficina de Publicaciones (`https://publications.europa.eu/resource/celex/<CELEX>`), que sirve el mismo texto del Diario Oficial; abajo se cita esa URL (equivale a `https://eur-lex.europa.eu/eli/...`). Sin acceso primario (marcado en Gaps): HHS.gov (403), texto completo de PCI DSS v4.0.1 (403), texto de los Trust Services Criteria de AICPA (requiere cuenta), Latombe C-703/25 P (solo fuentes secundarias).

**Cambios clave vs. pasada anterior (`calidad_gobernanza_seguridad.md`)**
- "Omnibus: acuerdo provisional, publicación sin confirmar" → **REEMPLAZADO**: Reglamento (UE) 2026/1744 publicado en DOUE el 24-jul-2026 (ver §5).
- SRB y Opinion 28/2024 ya leídos desde sentencia/PDF original, no resúmenes de estudios jurídicos (ver §1, §2).
- Nuevo hallazgo: **EDPB Guidelines 02/2026 sobre anonimización** (adoptadas 7-jul-2026 para consulta pública hasta 30-oct-2026) y **informe CEF 2025 sobre derecho de supresión** (10-feb-2026), con orientación explícita sobre backups.
- HIPAA, PCI, SOC 2, CCPA, ABAC, masking, tokenización, secretos: ahora con fuentes (ver secciones).

---

## 1. Seudonimización vs. anonimización: GDPR Rec. 26, WP216, CJEU SRB (C-413/23 P), EDPB Guidelines 01/2025 y 02/2026

### Takeaway
Los datos seudonimizados siguen siendo personales para quien puede reatribuirlos; el TJUE (4-sep-2025) añadió que pueden dejar de serlo *para un destinatario que no tiene medios razonables de reidentificar*, pero que las obligaciones del responsable (p. ej. informar de destinatarios) se evalúan desde su perspectiva y al momento de la recolección. Para un data engineer: un hash/token no es anonimización, y "anónimo" es una afirmación por-entidad que hay que poder demostrar (EDPB 02/2026 en consulta).

### Cited Findings
- GDPR Rec. 26: los datos seudonimizados "which could be attributed to a natural person by the use of additional information should be considered to be information on an identifiable natural person"; para valorar identificabilidad se consideran "all the means reasonably likely to be used, such as singling out, either by the controller or by another person", con factores objetivos (coste, tiempo, tecnología disponible); los principios no aplican a información anónima. — [Reglamento (UE) 2016/679, Rec. 26 (Cellar)](https://publications.europa.eu/resource/celex/32016R0679)
- GDPR Art. 4(5): seudonimización = tratamiento de modo que los datos "can no longer be attributed to a specific data subject without the use of additional information, provided that such additional information is kept separately and is subject to technical and organisational measures". — [GDPR Art. 4(5)](https://publications.europa.eu/resource/celex/32016R0679)
- Art. 25(1) cita la seudonimización como ejemplo de medida de protección de datos desde el diseño; Art. 25(2) exige que "by default" solo se traten los datos necesarios, incluyendo "accessibility" (no accesibles a un número indefinido de personas sin intervención). Art. 32(1)(a) cita "the pseudonymisation and encryption of personal data". — [GDPR Arts. 25 y 32](https://publications.europa.eu/resource/celex/32016R0679)
- TJUE, sentencia 4-sep-2025, C-413/23 P (EDPS v SRB), Primera Sala, ECLI:EU:C:2025:645: anula la sentencia del Tribunal General (T-557/20) y devuelve el asunto (dispositivo: anular, devolver, reservar costas). — [Sentencia, texto en Cellar](https://publications.europa.eu/resource/celex/62023CJ0413)
- Holding (apdos. 85-86): los datos seudonimizados "must not be regarded as constituting, in all cases and for every person, personal data" porque la seudonimización "may, depending on the circumstances of the case, effectively prevent persons other than the controller from identifying the data subject". Pero si no se puede descartar que terceros tengan medios razonables (p. ej. cruce con otros datos), el interesado es identificable "as regards both that transfer and any subsequent processing" y los datos son personales. — [Sentencia C-413/23 P](https://publications.europa.eu/resource/celex/62023CJ0413); resumen oficial del Tribunal: [Comunicado de prensa 107/25](https://curia.europa.eu/site/upload/docs/application/pdf/2025-09/cp250107en.pdf)
- Holding sobre deber de informar (apdo. 111): para el Art. 15(1)(d) Reg. 2018/1725 (equivalente a Art. 13 GDPR), "the identifiable nature of the data subject must be assessed at the time of collection of the data and from the point of view of the controller". Así, el deber de informar de destinatarios aplica aunque, tras seudonimizar, los datos no fueran personales para el destinatario (Deloitte). — [Sentencia C-413/23 P](https://publications.europa.eu/resource/celex/62023CJ0413); [Comunicado 107/25](https://curia.europa.eu/site/upload/docs/application/pdf/2025-09/cp250107en.pdf)
- Además, el Tribunal declaró que las opiniones personales están "necessarily closely linked" a su autor (no hace falta analizar contenido/finalidad/efecto en ese caso). — [Comunicado 107/25](https://curia.europa.eu/site/upload/docs/application/pdf/2025-09/cp250107en.pdf)
- La sentencia trabaja con el Reg. 2018/1725 (instituciones UE), no el GDPR directamente; el análisis se apoya en jurisprudencia GDPR y en el Rec. 16 equivalente. — [Sentencia C-413/23 P](https://publications.europa.eu/resource/celex/62023CJ0413)
- WP29 Opinion 05/2014 (WP216): "pseudonymisation is not a method of anonymisation. It merely reduces the linkability of a dataset with the original identity of a data subject, and is accordingly a useful security measure"; una solución robusta debe resistir tres riesgos: singling out, linkability, inference; k-anonymity no previene ataques de inferencia; l-diversity amplía k-anonymity; evalúa differential privacy dentro de las técnicas de aleatorización y describe fallos (consultas múltiples). — [WP216 (ec.europa.eu)](https://ec.europa.eu/justice/article-29/documentation/opinion-recommendation/files/2014/wp216_en.pdf)
- EDPB Guidelines 01/2025 on Pseudonymisation (adoptadas 16-ene-2025, versión para consulta): "Pseudonymised data, which could be attributed to a natural person by the use of additional information, is to be considered information on an identifiable natural person… This statement also holds true if pseudonymised data and additional information are not in the hands of the same person"; si se borra toda la información adicional, solo es anónimo si se cumplen las condiciones de anonimato; introduce el "pseudonymisation domain" (contexto en que se quiere evitar la atribución); no hay obligación general de seudonimizar (Rec. 28). — [EDPB Guidelines 01/2025 (PDF)](https://www.edpb.europa.eu/system/files/2025-01/edpb_guidelines_202501_pseudonymisation_en.pdf)
- Estado Guidelines 01/2025: la página de consulta figura "Closed for feedback" (17-ene a 14-mar-2025); no encontré versión final adoptada; la búsqueda indica que EDPB/EDPS señalaron en feb-2026 que preparan una actualización. — [Página de consulta EDPB](https://www.edpb.europa.eu/our-work-tools/documents/public-consultations/2025/guidelines-012025-pseudonymisation_en); [Joint Opinion 2/2026](https://www.edpb.europa.eu/system/files/2026-02/edpb_edps_jointopinion_202602_digitalomnibus_en.pdf) (solo vista en resultados de búsqueda, no leída)
- **EDPB Guidelines 02/2026 on Anonymisation**, v1.0, adoptadas 7-jul-2026 "for public consultation" (consulta 8-jul a 30-oct-2026 según la página EDPB). Marco con tres criterios: *No Record Isolation, No Linkage, No Inference*; la anonimidad se evalúa desde la perspectiva de cada entidad relevante (enfoque "contextual") o con un enfoque "simplificado" más conservador; "means" incluye medios accesibles solo vía terceros. — [EDPB Guidelines 02/2026 (PDF)](https://www.edpb.europa.eu/system/files/2026-07/edpb_guidelines_202602_anonymisation_v1_en_0.pdf); [Resultado de búsqueda con fechas de consulta](https://www.edpb.europa.eu/public-consultations/guidelines-on-anonymisation_en)
- EDPB Opinion 28/2024 (modelos de IA), Art. 64(2) a petición de la autoridad irlandesa: un modelo entrenado con datos personales no es anónimo en todos los casos; para serlo, la probabilidad de extracción directa (incl. probabilística) y la de obtener datos personales mediante consultas debe ser "insignificant" considerando "all the means reasonably likely to be used"; evaluación caso a caso por las autoridades. Legítimo interés: test en tres pasos (interés, necesidad, ponderación). Tres escenarios de tratamiento ilícito en desarrollo: (1) mismo responsable despliega el modelo con datos retenidos → depende del caso; (2) otro responsable despliega → debe haber evaluado, como accountability, que el modelo no se desarrolló con tratamiento ilícito; (3) modelo anonimizado después → GDPR no aplica a la operación posterior del modelo. — [EDPB Opinion 28/2024 (PDF)](https://www.edpb.europa.eu/system/files/2024-12/edpb_opinion_202428_ai-models_en.pdf)
- Discrepancia de fecha: el PDF dice "Adopted on 17 December 2024"; la página del EDPB indica 18-dic-2024. — [PDF](https://www.edpb.europa.eu/system/files/2024-12/edpb_opinion_202428_ai-models_en.pdf); [página EDPB](https://www.edpb.europa.eu/our-work-tools/our-documents/opinion-board-art-64/opinion-282024-certain-data-protection-aspects_en)
- CCPA: "deidentified" exige que la información no pueda razonablemente usarse para inferir o vincular a un consumidor Y que el negocio (1) tome medidas razonables, (2) se comprometa públicamente a no reidentificar, (3) obligue contractualmente a receptores. "Pseudonymize" definido de forma análoga a GDPR. — [CCPA texto 2026 (CPPA)](https://cppa.ca.gov/pdf/20260101_ccpa_statute.pdf)
- LGPD Brasil Art. 12: datos anonimizados no son personales salvo que el proceso sea reversible con medios propios o "com esforços razoáveis", evaluado con costo y tiempo. — [Lei 13.709/2018](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)

### Inferencias
- Para pipelines: un `sha256(email)` sin sal/clave o un surrogate key cuyo mapeo existe en otra tabla es seudonimización (dato personal) a efectos del responsable; tratar las tablas "seudonimizadas" como datos personales con retención, acceso y DSAR completos. Marcarlas como "anónimas" para un destinatario solo con análisis documentado por entidad (EDPB 02/2026) y controles contractuales/técnicos que impidan reidentificación.
- SRB no habilita compartir seudonimizados sin informar: el deber de transparencia se fija en el origen. Importa para data sharing/marketplaces y para entregar datos a procesadores/analistas.
- Opinion 28/2024 es relevante para pipelines de entrenamiento: documentar origen y base legal del dataset (también por la Art. 10 AI Act).

### Gaps
- No se leyó la versión final de la Guidelines 01/2025 (no existe según lo encontrado) ni se verificó cómo EDPB 02/2026 trata hashing/tokenización/differential privacy en detalle (solo extracto y resumen ejecutivo).
- No se leyó el texto de la Joint Opinion 2/2026 EDPB-EDPS sobre el Digital Omnibus.

---

## 2. Principios y artículos GDPR que implementa un data engineer (Arts. 5, 6, 17, 25, 28, 30, 32, 33, 35)

### Takeaway
La traducción técnica: minimización y limitación de almacenamiento (Art. 5), privacy by design/default (Art. 25), seguridad "apropiada al riesgo" incl. cifrado y seudonimización (Art. 32), registro de tratamientos con plazos de supresión (Art. 30), contratos con procesadores (Art. 28) y DPIA para tratamientos de alto riesgo (Art. 35). Ninguno prescribe una tecnología concreta: se exige "state of the art" proporcional al riesgo.

### Cited Findings
- Art. 5(1): licitud/transparencia, limitación de finalidad, minimización, exactitud, limitación del almacenamiento ("no longer than is necessary"), integridad y confidencialidad ("appropriate security… protection against unauthorised or unlawful processing and against accidental loss, destruction or damage"); Art. 5(2): el responsable debe "be able to demonstrate compliance". — [GDPR Art. 5](https://publications.europa.eu/resource/celex/32016R0679)
- Art. 17(1): supresión "without undue delay" en seis supuestos (finalidad cumplida, retiro de consentimiento, oposición, tratamiento ilícito, obligación legal, servicios de la sociedad de la información a menores); 17(2): si los datos se hicieron públicos, "reasonable steps, including technical measures" para informar a otros responsables; 17(3): excepciones (libertad de expresión, obligación legal, salud pública, archivo/investigación/estadística, defensa de reclamaciones). — [GDPR Art. 17](https://publications.europa.eu/resource/celex/32016R0679)
- Art. 28(3): contrato con el procesador debe fijar tratamiento solo bajo instrucciones documentadas (incl. transferencias), confidencialidad del personal, medidas del Art. 32, subencargados con autorización, asistencia para derechos ARCO/DSAR, asistencia Arts. 32-36, "deletes or returns all the personal data" al terminar y borra copias, y auditorías. — [GDPR Art. 28](https://publications.europa.eu/resource/celex/32016R0679)
- Art. 30(1): el registro (RoPA) incluye finalidades, categorías de datos/sujetos, destinatarios, transferencias a terceros países, "where possible, the envisaged time limits for erasure" y "general description" de medidas Art. 32. — [GDPR Art. 30](https://publications.europa.eu/resource/celex/32016R0679)
- Art. 32(1): "state of the art, costs of implementation…" ; incluye (a) seudonimización y cifrado, (b) confidencialidad, integridad, disponibilidad y resiliencia, (c) capacidad de restaurar la disponibilidad "in a timely manner", (d) proceso de prueba y evaluación regular. Art. 32(4): quien accede actúa solo bajo instrucciones. — [GDPR Art. 32](https://publications.europa.eu/resource/celex/32016R0679)
- Art. 33(1): notificar brechas a la autoridad "not later than 72 hours" tras tener conocimiento, salvo que sea improbable que suponga riesgo. — [GDPR Art. 33](https://publications.europa.eu/resource/celex/32016R0679)
- Art. 35(1): DPIA previa cuando el tratamiento "in particular using new technologies" probablemente entrañe alto riesgo; 35(3)(a) incluye evaluación sistemática y extensiva basada en tratamiento automatizado/perfilado. — [GDPR Art. 35](https://publications.europa.eu/resource/celex/32016R0679)
- Transferencias: Art. 44 (principio general, incl. transferencias ulteriores); Art. 46(1)-(2): sin decisión de adecuación, garantías apropiadas (BCR, cláusulas tipo, etc.) con derechos exigibles y recursos efectivos. — [GDPR Arts. 44 y 46](https://publications.europa.eu/resource/celex/32016R0679)
- Arts. 45 (adecuación) y 49 (excepciones) no se extrajeron textualmente; los Arts. 6, 47 y 48-49 no fueron citados con texto en esta pasada (ver Gaps).

### Inferencias
- Mapeo Art. 30(1)(f) → catálogo con `retention_policy` por dataset y job de expiración; Art. 5(1)(e) → TTL/lifecycle + purga física (ver §3).
- Art. 25(2) "accessibility" → deny-by-default en el catálogo: nuevas tablas con PII se crean sin grants a roles amplios.
- Art. 32(1)(c) + backups: ensayar restauración (RTO/RPO) y mantener un registro de supresiones reaplicable tras restore (ver §3).

### Gaps
- Texto literal de Arts. 6, 45, 47, 48, 49 no extraído; EDPB Guidelines sobre transferencias (Cap. V) no leídas.
- No se revisó guía de autoridades sobre DPIA (lista del Art. 35(4)).

---

## 3. Supresión (Art. 17) en formatos inmutables: Delta, Iceberg, crypto-shredding, backups; guía de reguladores

### Takeaway
Borrar lógicamente no es borrar físicamente: en Delta hay que combinar DELETE/MERGE + `REORG TABLE … APPLY (PURGE)` (si hay deletion vectors) + VACUUM; en Iceberg, DELETE crea delete files y snapshots que retienen datos hasta `expire_snapshots`/compactación/`remove_orphan_files`. Los reguladores (EDPB CEF 2025, ICO) aceptan que los backups no se modifiquen de inmediato si se ponen "beyond use" y hay un calendario de rotación y procedimiento para reaplicar supresiones tras una restauración.

### Cited Findings
- Databricks (guía GDPR/CCPA sobre Delta): lo más seguro es el borrado completo; borrar primero en bronze con DELETE (individual) o MERGE contra una tabla de control (masivo); propagar a silver/gold (materialized views requieren refresh y mantenimiento; streaming tables con `skipChangeCommits`); Delta retiene historial incl. registros borrados 30 días por defecto; usar Predictive Optimization/mantenimiento de pipelines o ejecutar `VACUUM` ("permanently remove previous versions"); con deletion vectors "you must also run `REORG TABLE ... APPLY (PURGE)`" para eliminar físicamente. — [Databricks: GDPR y CCPA en Delta Lake](https://docs.databricks.com/aws/en/security/privacy/gdpr-delta)
- Iceberg: cada write/update/delete/compactación produce un snapshot que conserva datos para aislamiento y time travel; `expire_snapshots` elimina snapshots antiguos y los data files que solo ellos requieren (`older_than` por defecto 5 días, `retain_last` por defecto 1); `remove_orphan_files` borra archivos no referenciados (por defecto, creados hace >3 días; admite `dry_run`); `rewrite_data_files` tiene opción `delete-file-threshold` (mínimo de deletes asociados a un data file para reescribirlo); existe `rewrite_position_delete_files`. — [Iceberg Spark procedures (fuente docs en GitHub)](https://raw.githubusercontent.com/apache/iceberg/main/docs/docs/spark-procedures.md)
- AWS KMS External Key Store: con doble cifrado, si se revoca permanentemente el acceso a la clave externa "any ciphertext remaining in AWS is effectively crypto-shredded"; AWS advierte que XKS implica carga operativa y riesgo de disponibilidad que "for most customers" supera el beneficio. — [AWS KMS XKS](https://docs.aws.amazon.com/kms/latest/developerguide/keystore-external.html)
- **EDPB CEF 2025 sobre supresión** (informe adoptado 10-feb-2026): "Depending on the technical settings and risks, it might not always be advisable to modify or delete information from back-ups. But, in that case, organisations should have appropriate procedures to keep track of erasure requests and comply with them on restored systems, as much as possible"; la mitad de las autoridades respondientes planteó preocupaciones; muchos responsables no tenían procedimientos específicos y dependían de borrado automático por retención; una autoridad señaló que borrados incrementales a lo largo de períodos largos dificultan concluir que se cumple "without undue delay" (Art. 17(1)); recomendaciones: seguir estándares establecidos de borrado y destrucción, y "verify that erasure has been carried out and be able to demonstrate such erasure"; buenas prácticas: sustituir datos a borrar por cadenas aleatorias en backups; herramientas que extraen datos y los trasladan a un sistema inaccesible para empleados y se borran/anonimizan después (borrado definitivo un mes después en el ejemplo). EDPB "may consider" más guía sobre backups y el significado de "without undue delay". — [EDPB CEF 2025 right to erasure report (PDF)](https://www.edpb.europa.eu/system/files/2026-02/edpb_cef-report_2025_right-to-erasure_en.pdf)
- Mismo informe, Issue 7: práctica común de usar anonimización como sustituto del borrado; varias autoridades vieron solo seudonimización básica o enmascaramiento parcial, que "would not fulfil the requirements of the GDPR regarding deletion"; el EDPB trabaja en guías de anonimización a la luz de SRB (hoy: Guidelines 02/2026 en consulta). — [EDPB CEF 2025 report](https://www.edpb.europa.eu/system/files/2026-02/edpb_cef-report_2025_right-to-erasure_en.pdf)
- ICO (Reino Unido): para backups "the key issue is to put the backup data 'beyond use', even if it cannot be immediately overwritten"; no usar para otros fines; permanecen hasta ser reemplazados según calendario; informar claramente a los individuos qué pasa con backups; responder "without undue delay and at the latest within one month". — [ICO: Right to erasure](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/individual-rights/right-to-erasure/)
- CCPA §1798.105(c): el negocio debe borrar de sus registros, notificar a service providers/contractors y a terceros a quienes vendió o compartió datos "unless this proves impossible or involves disproportionate effort"; puede mantener un registro confidencial de solicitudes de borrado para evitar re-venta. — [CCPA texto 2026](https://cppa.ca.gov/pdf/20260101_ccpa_statute.pdf)
- LGPD Art. 18 IV: derecho a "anonimização, bloqueio ou eliminação" de datos innecesarios o tratados en desconformidad. — [LGPD](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
- Ley 25.326 (Argentina) Art. 16: supresión/rectificación en plazo máximo de 5 días hábiles tras el reclamo, con acción de hábeas data si se incumple. — [Ley 25.326 (InfoLEG)](https://servicios.infoleg.gob.ar/infolegInternet/anexos/60000-64999/64790/texact.htm)

### Inferencias (no respaldadas literalmente por los reguladores)
- Patrón recomendado: (1) tabla de solicitudes de supresión (`erasure_ledger`) con hash/ID no reversible del sujeto; (2) DELETE/MERGE en todas las capas; (3) PURGE/compactación; (4) `VACUUM` o `expire_snapshots` + `remove_orphan_files` con SLA documentado (p. ej. ≤30 días); (5) backups con retención corta y rotación, más re-aplicación del ledger tras cualquier restore; (6) logs/auditoría sin PII o con pseudónimos.
- Crypto-shredding por sujeto (clave de datos por usuario/tenant en KMS, borrar la clave) es técnicamente sólido para datos y backups que usan envelope encryption por sujeto, pero ningún regulador consultado lo avala o rechaza expresamente: documentarlo en el RoPA y DPIA y no basarse en una clave maestra compartida. El informe CEF solo menciona sustituir por cadenas aleatorias y mover a sistemas inaccesibles.
- Time travel y clones/shallow clones/snapshots de warehouse son copias a incluir en el alcance del borrado; Unity Catalog con filtros/masks no soporta time travel ni clones (ver §8), un factor a considerar.
- Mantener un `tombstone` del ID para impedir re-ingesta desde fuentes upstream.

### Gaps
- No encontré guía específica de CNIL ni AEPD sobre Delta/Iceberg/lakehouse; ninguna sobre crypto-shredding. (Se buscó vía EDPB/ICO; CNIL/AEPD no se consultaron directamente.)
- No verifiqué en doc oficial de Delta Lake (delta.io) los detalles de VACUUM/deletion vectors fuera de la página de Databricks.
- Snowflake Time Travel/Fail-safe y BigQuery time travel (7 días) no se verificaron con documentación oficial en esta pasada.

---

## 4. Transferencias internacionales: EU-US Data Privacy Framework (estado oct-2026)

### Takeaway
La decisión de adecuación (UE) 2023/1795 sigue vigente. El Tribunal General la confirmó el 3-sep-2025 (T-553/23 Latombe); hay recurso de casación pendiente (C-703/25 P, presentado 31-oct-2025) sin sentencia encontrada. No eliminar de los contratos las SCC como plan B.

### Cited Findings
- Decisión de ejecución (UE) 2023/1795 de la Comisión, 10-jul-2023; Art. 3: la Comisión "shall continuously monitor" el marco legal estadounidense; considerando 211: primera revisión al año y luego periodicidad según resultado; Art. 45(3) GDPR exige revisión periódica "at least every four years" (nota 410 de la decisión). — [Decisión 2023/1795 (Cellar)](https://publications.europa.eu/resource/celex/32023D1795)
- Tribunal General, 3-sep-2025, T-553/23 Latombe v Commission: desestima la acción de anulación; concluye que a la fecha de adopción EE. UU. garantizaba nivel adecuado; el DPRC tiene salvaguardas de independencia; la recolección masiva no requiere autorización previa independiente, basta control judicial ex post (según Schrems II). Comisión puede suspender/modificar/derogar si cambia el marco legal. — [Comunicado de prensa 106/25](https://curia.europa.eu/jcms/upload/docs/application/pdf/2025-09/cp250106en.pdf) (leído vía descarga local)
- Recurso: Latombe presentó casación el 31-oct-2025, asunto C-703/25 P; reportes secundarios hasta junio de 2026 lo dan por pendiente. — [Diario Oficial C/2025/6610 (listado en búsqueda)](https://eur-lex.europa.eu/eli/C/2025/6610/oj/eng); [WilmerHale](https://www.wilmerhale.com/en/insights/blogs/wilmerhale-privacy-and-cybersecurity-law/20251201-european-court-of-justice-to-review-challenge-to-eu-us-data-privacy-framework) (secundaria)

### Inferencias
- "Status oct-2026: válido, bajo recurso" es la formulación segura. Riesgo de invalidación futura (Schrems III) no nulo; mantener SCC + transfer impact assessment y arquitectura capaz de regionalizar datos y claves (HYOK/XKS) para escenarios de contingencia.

### Gaps
- No verifiqué en CURIA el estado procesal de C-703/25 P ni la conclusión de la segunda revisión de la Comisión; no pude obtener la lista oficial dataprivacyframework.gov (página sin contenido útil).

---

## 5. Normativa UE de datos/IA/ciber: Data Act, AI Act + Digital Omnibus, DORA, NIS2, CRA

### Takeaway
(a) Data Act: aplica desde 12-sep-2025; la eliminación de cargos por cambio de proveedor (switching charges, incl. egress de cambio) es del 12-ene-2027 (Art. 29(1)), no una eliminación general del egress: en uso paralelo multi-cloud (Art. 34) se pueden cobrar egress a coste. (b) AI Act: el Reglamento (UE) 2026/1744 (Digital Omnibus on AI) fue publicado el 24-jul-2026 y retrasa high-risk Anexo III al 2-dic-2027 y Anexo I al 2-ago-2028. (c) La parte GDPR/datos del Digital Omnibus NO está acordada.

### Cited Findings
**Data Act (Reg. 2023/2854)**
- Art. 50: aplica desde 12-sep-2025; Art. 3(1) (diseño de productos conectados) para productos puestos en el mercado después de 12-sep-2026; Capítulo IV (cláusulas abusivas) a contratos celebrados tras 12-sep-2025 y desde 12-sep-2027 a ciertos contratos anteriores (indefinidos o con vencimiento ≥10 años desde 11-ene-2024). — [Reg. (UE) 2023/2854 Art. 50 (Cellar)](https://publications.europa.eu/resource/celex/32023R2854)
- Art. 29: "From 12 January 2027, providers of data processing services shall not impose any switching charges on the customer for the switching process"; del 11-ene-2024 al 12-ene-2027 solo cargos reducidos que no excedan los costes directos. Art. 2(35)-(36): "switching charges" incluyen "data egress charges" (tasas de transferencia para extraer datos a otro proveedor u on-premises). Art. 34(2): en uso paralelo de servicios, el proveedor "may impose data egress charges, but only for the purpose of passing on egress costs incurred, without exceeding such costs". — [Reg. 2023/2854 Arts. 29, 34 y definiciones](https://publications.europa.eu/resource/celex/32023R2854)
- Art. 32(1): los proveedores de servicios de procesamiento de datos deben adoptar medidas técnicas, organizativas y legales para evitar el acceso gubernamental internacional o transferencia de datos no personales en conflicto con el derecho UE. — [Reg. 2023/2854 Art. 32](https://publications.europa.eu/resource/celex/32023R2854)

**AI Act (Reg. 2024/1689) y Digital Omnibus on AI (Reg. 2026/1744)**
- Texto original Art. 113: aplica desde 2-ago-2026, con Capítulos I-II desde 2-feb-2025, ciertos capítulos desde 2-ago-2025 y Art. 6(1) desde 2-ago-2027. — [Reg. 2024/1689 Art. 113](https://publications.europa.eu/resource/celex/32024R1689)
- Reglamento (UE) 2026/1744 del 8-jul-2026, DOUE L 24.7.2026, "Digital Omnibus on AI": reemplaza Art. 113(c): Capítulo III Secciones 1-3 aplican desde **2-dic-2027** para sistemas de alto riesgo del Art. 6(2)/Anexo III y desde **2-ago-2028** para Art. 6(1)/Anexo I; ciertas prohibiciones nuevas (Art. 5(1) puntos (ba),(bb), 5(1a),(1b)) desde 2-dic-2026; proveedores con sistemas generativos ya en mercado antes del 2-ago-2026 deben cumplir Art. 50(2) antes del 2-dic-2026; entra en vigor el tercer día tras su publicación (Art. 4). — [Reg. (UE) 2026/1744 (Cellar)](https://publications.europa.eu/resource/celex/32026R1744)
- Nuevo Art. 4a AI Act: proveedores (y ampliado a otros) pueden tratar categorías especiales de datos "to the extent strictly necessary" para detección/corrección de sesgos, con condiciones (p. ej. que no pueda lograrse con datos sintéticos o anonimizados, y limitaciones técnicas a la reutilización). — [Reg. 2026/1744, art. 4a](https://publications.europa.eu/resource/celex/32026R1744)
- Art. 10 AI Act (gobernanza de datos para sistemas de alto riesgo): prácticas sobre origen de datos y finalidad original si son personales, preparación (anotación, limpieza, agregación), examen de sesgos (10(2)(f)) y medidas para detectar/mitigarlos (10(2)(g)). — [Reg. 2024/1689 Art. 10](https://publications.europa.eu/resource/celex/32024R1689)

**Digital Omnibus (parte GDPR/datos, COM(2025) 837)**
- Según reportes secundarios (hasta mediados de septiembre 2026): sin mandato del Consejo, sin trílogos, Parlamento (ITRE/LIBE) con >1.750 enmiendas; acuerdo realista no antes de 2027. — [Acompli (secundaria)](https://acompli.ie/news/digital-omnibus-gdpr-cookies-status-september-2026/)

**DORA, NIS2, CRA**
- DORA (Reg. 2022/2554) aplica desde 17-ene-2025; Art. 9(4): política de seguridad de la información, gestión de red, políticas que limiten acceso físico/lógico a lo necesario, autenticación fuerte y "protection measures of cryptographic keys whereby data is encrypted based on results of approved data classification and ICT risk assessment processes". — [DORA Arts. 9 y 64](https://publications.europa.eu/resource/celex/32022R2554)
- NIS2 (Dir. 2022/2555) Art. 21(2): medidas mínimas incl. continuidad (gestión de backups), seguridad de la cadena de suministro, seguridad en adquisición/desarrollo/mantenimiento con gestión de vulnerabilidades, criptografía/cifrado, control de acceso, MFA; transposición debía aplicarse desde 18-oct-2024. — [NIS2 Arts. 21 y 41](https://publications.europa.eu/resource/celex/32022L2555)
- CRA (Reg. 2024/2847): aplica desde 11-dic-2027, con Art. 14 (notificaciones) desde 11-sep-2026 y Capítulo IV desde 11-jun-2026; Anexo I Parte II(1): los fabricantes deben elaborar un SBOM "in a commonly used and machine-readable format covering at the very least the top-level dependencies". — [Reg. 2024/2847 (Cellar)](https://publications.europa.eu/resource/celex/32024R2847)

### Inferencias
- La afirmación "enero 2027 sin egress" debe matizarse: aplica a cambio de proveedor (switching) y bajo el Reglamento solo a proveedores de servicios de procesamiento de datos (cloud/PaaS/SaaS) frente a clientes UE; tráfico normal/uso paralelo sigue facturándose (al coste en uso paralelo). Verificar con el proveedor cómo implementa Art. 29.
- Para equipos de datos en UE fuera de finanzas: DORA/NIS2 solo si la entidad está en su ámbito (DORA Art. 2; NIS2 entidades esenciales/importantes). Si no, son referencia de buenas prácticas.
- El AI Act "high-risk" para datos de entrenamiento pasa a 2-dic-2027 (Anexo III), pero la preparación (lineage, calidad, sesgos) lleva tiempo: usar el margen para construir evidencia, no para posponer.

### Gaps
- No verifiqué el estado de la propuesta Digital Omnibus que modifica el Data Act (la parte "datos" vs. "AI") ni otros cambios a Data Act post-2025.
- No leí el texto completo de DORA RTS (gestión de claves) ni de la implementación de NIS2 en un Estado miembro concreto.
- Fuente oficial de OEIL para el procedimiento 2025/0360(COD) no consultada (solo secundarias).

---

## 6. Sectoriales EEUU/estándares: HIPAA, PCI DSS 4.x, SOC 2, CCPA/CPRA, ISO 27001/27701

### Takeaway
HIPAA: dos métodos de desidentificación (Expert Determination y Safe Harbor con 18 identificadores) y controles técnicos (cifrado "addressable", logging obligatorio). PCI DSS: la tokenización reduce alcance solo si el PAN no es recuperable y los sistemas están segmentados; la tokenización/detokenización queda dentro del CDE. SOC 2: criterios de servicio de confianza de AICPA (texto no accesible). CCPA: borrado + definición estricta de "deidentified".

### Cited Findings
**HIPAA (45 CFR)**
- §164.514(b)(1) Expert Determination: persona con conocimiento y experiencia en principios estadísticos y científicos determina que "the risk is very small" de identificar a un individuo, y documenta métodos y resultados. §164.514(b)(2) Safe Harbor: eliminar 18 tipos de identificadores del individuo o de familiares/empleadores/hogar (nombres; subdivisiones geográficas menores a un estado; todos los elementos de fechas excepto año; teléfonos; fax; correos; SSN; historia clínica; beneficiario; cuentas; licencias; vehículos; dispositivos; URLs; IPs; biométricos; imágenes faciales; cualquier otro código único) y no tener "actual knowledge" de que la información podría identificar. §164.514(c): código de re-identificación no derivado de información del individuo y sin divulgar el mecanismo. — [45 CFR 164.514 (eCFR)](https://www.ecfr.gov/api/renderer/v1/content/enhanced/current/title-45?part=164&section=164.514)
- §164.312: control de acceso (ID único: required; cifrado/descifrado: addressable), controles de auditoría (registrar y examinar actividad: standard), integridad (mecanismo de autenticación de ePHI: addressable), seguridad de transmisión (cifrado: addressable). — [45 CFR 164.312 (eCFR)](https://www.ecfr.gov/api/renderer/v1/content/enhanced/current/title-45?part=164&section=164.312)
- La guía del HHS sobre desidentificación no se pudo abrir (403).

**PCI DSS**
- Tokenization Guidelines (PCI SSC, agosto 2011, suplemento informativo sobre PCI DSS 2.0): "All elements of the tokenization system and process, including de-tokenization and PAN storage, are considered part of the cardholder data environment (CDE) and are therefore in scope"; sistemas segmentados que solo almacenan tokens "may be considered outside of the CDE and possibly out of scope"; si el comerciante puede recuperar el PAN, su entorno está en alcance; el alcance de tokens reversibles basados en cifrado seguía bajo evaluación. — [PCI SSC Tokenization Guidelines (PDF)](https://listings.pcisecuritystandards.org/documents/Tokenization_Guidelines_Info_Supplement.pdf)
- PCI DSS v4.0.1: 51 de los 64 requisitos nuevos eran "future-dated" y pasaron a ser obligatorios el 31-mar-2025; v4.0.1 es revisión limitada que no cambia esa fecha; 6.4.3 y 11.6.1 (scripts de páginas de pago) incluidos. — [PCI SSC blog: future-dated requirements](https://blog.pcisecuritystandards.org/now-is-the-time-for-organizations-to-adopt-the-future-dated-requirements-of-pci-dss-v4-x); [PCI SSC blog v4.0.1](https://blog.pcisecuritystandards.org/just-published-pci-dss-v4-0-1)
- Req. 3.5.1.2: cifrado a nivel de disco/partición solo para medios extraíbles o, en no extraíbles, el PAN debe además volverse ilegible con otro mecanismo (según el resumen de cambios v3.2.1→v4.0). — [PCI DSS v3.2.1→v4.0 Summary of Changes](https://listings.pcisecuritystandards.org/documents/PCI-DSS-v3-2-1-to-v4-0-Summary-of-Changes-r1.pdf) (vista en resultados de búsqueda)

**SOC 2**
- Los Trust Services Criteria 2017 (puntos de enfoque revisados 2022) cubren seguridad, disponibilidad, integridad del procesamiento, confidencialidad y privacidad; los establece el ASEC de AICPA para compromisos de atestación. — [AICPA TSC (página de descarga)](https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022)

**CCPA/CPRA**
- §1798.105: derecho de supresión y obligaciones en cascada (ver §3); "Deidentified" y "Pseudonymize" (ver §1). — [CCPA texto vigente 1-ene-2026 (CPPA)](https://cppa.ca.gov/pdf/20260101_ccpa_statute.pdf)

**ISO**
- ISO/IEC 27701:2025 (edición 2, 2025-10) es una norma independiente de sistema de gestión de información de privacidad (PIMS), certificable sin ISO 27001; la edición 2019 figura retirada (2025-10-14); ISO/IEC 27706:2025 define requisitos para entes certificadores PIMS. — [ISO 27701:2025](https://www.iso.org/standard/27701); [ISO 27701:2019](https://www.iso.org/standard/71670.html)
- El informe CEF cita ISO/IEC 27001 como buena práctica de gestión (no como obligación). — [EDPB CEF 2025 report](https://www.edpb.europa.eu/system/files/2026-02/edpb_cef-report_2025_right-to-erasure_en.pdf)

### Inferencias
- En un lakehouse: tokenizar PAN en el borde (vault de tokens segmentado/PCI-validado o proveedor) y que el lakehouse solo vea tokens no reversibles; así el lakehouse queda fuera del CDE solo si la segmentación y la imposibilidad de recuperar PAN se demuestran al QSA. Ver cifrado "format-preserving" en §7.
- SOC 2 y HIPAA piden evidencia (logs, revisiones de acceso, gestión de cambios): el pipeline CI/CD con aprobaciones y audit logs inmutables sirve de evidencia; no verifiqué el texto de CC6/CC7/CC8.

### Gaps
- No pude leer el texto de PCI DSS v4.0.1 (403), por lo que no cito numeración exacta de 3.4/3.5/3.6/8.x/10.x ni las definiciones de alcance de 4.0.1. Tampoco existe un suplemento de tokenización PCI SSC específico para v4.x que haya encontrado (el de 2011 es el vigente en el sitio).
- Texto de CC6.1, CC7.2, CC8.1, C1.2 y P-series de SOC 2 no obtenido (requiere cuenta AICPA).
- Guías HHS (desidentificación, Security Rule cloud) no accesibles; usé eCFR.
- CPRA regs (11 CCR §7000+) no leídas.

---

## 7. Controles técnicos: cifrado, KMS/BYOK/HYOK, IAM/ABAC, secretos, tokenización/FPE, differential privacy, red, supply chain, zero trust

### Takeaway
Los textos legales piden "state of the art" y "appropriate to the risk"; las especificaciones concretas viven en NIST y en la documentación de proveedores. Lo verificado: envelope encryption/XKS en AWS KMS, credenciales dinámicas en Vault, OIDC en GitHub Actions, PrivateLink, FF1 como único modo FPE en el segundo draft de NIST SP 800-38G r1, y SP 800-226 para differential privacy.

### Cited Findings
- Envelope encryption (AWS KMS): "encrypting plaintext data with a data key, and then encrypting the data key under another key"; las claves raíz nunca salen sin cifrar de HSMs FIPS 140-3 Nivel 3; beneficios: guardar la clave de datos cifrada junto al dato, re-cifrar solo claves de datos, combinar algoritmos; el AWS Encryption SDK ofrece envelope encryption del lado del cliente; permite importar material de clave propio (BYOK) cifrado con RSAES-OAEP. — [AWS KMS cryptography essentials](https://docs.aws.amazon.com/kms/latest/developerguide/kms-cryptography.html)
- HYOK/XKS: la clave y operaciones criptográficas viven en un gestor de claves externo bajo control del cliente; AWS no puede crear/ver/borrar las claves; revocar el acceso temporalmente bloquea el descifrado y revocar permanente deja el texto cifrado irrecuperable; XKS no soporta claves asimétricas, HMAC, material importado, rotación automática ni claves multi-región; AWS advierte que "greater risk to availability and latency will, for most customers, exceed the perceived security benefits". — [AWS KMS External Key Stores](https://docs.aws.amazon.com/kms/latest/developerguide/keystore-external.html)
- Fabric/OneLake: cifrado en reposo por defecto con claves gestionadas por Microsoft y opción de claves gestionadas por el cliente (workspaces); TLS 1.2 mínimo y TLS 1.3 cuando es posible; tráfico entre servicios por la red global de Microsoft; private links; OneLake diagnostics para auditar acceso a datos. — [Fabric: Data security overview](https://learn.microsoft.com/en-us/fabric/onelake/security/get-started-security)
- Secretos dinámicos (Vault): el motor de bases de datos genera credenciales bajo demanda por rol; TTL por defecto 1 h y máx. 24 h; cada instancia obtiene su propio usuario (trazabilidad); revocación al expirar el lease; roles estáticos rotan contraseña cada 24 h por defecto; advertencia de no asignar credenciales root a un rol estático. — [Vault database secrets engine](https://developer.hashicorp.com/vault/docs/secrets/databases)
- Workload identity (OIDC): los jobs de GitHub Actions obtienen un JWT por job (claims `sub`, `aud`, `repository`, `ref`, etc.) y el proveedor cloud lo valida contra condiciones de confianza del rol, devolviendo un token de acceso de vida corta; evita guardar credenciales cloud de larga duración como secretos. — [GitHub Docs: OpenID Connect](https://docs.github.com/en/actions/concepts/security/openid-connect)
- Aislamiento de red: AWS PrivateLink conecta VPC con servicios "as if they were in your VPC" sin internet gateway, NAT ni IP pública, controlando los endpoints alcanzables. — [AWS PrivateLink](https://docs.aws.amazon.com/vpc/latest/privatelink/what-is-privatelink.html)
- FPE: según resultados de búsqueda del sitio NIST, el segundo borrador público de SP 800-38G Rev. 1 (3-feb-2025) elimina FF3 y FF3-1 (debilidad en el tweak, Beyne) y deja FF1 como único modo; no encontré una versión final. — [NIST SP 800-38G r1 (2pd)](https://csrc.nist.gov/pubs/sp/800/38/g/r1/2pd) y [versión 2019 retirada](https://csrc.nist.gov/pubs/sp/800/38/g/r1/ipd) (vistas en resultados de búsqueda; no leídas completas)
- Desidentificación: NIST SP 800-188 (final, sep-2023): enfoque por objetivos y riesgos, modelos de compartición (datos desidentificados/sintéticos, interfaz de consulta, enclave protegido), recomienda comité de revisión de divulgación y estudios de reidentificación; advierte que ciertas herramientas de masking no bastan para desidentificación. — [NIST SP 800-188](https://csrc.nist.gov/pubs/sp/800/188/final)
- Differential privacy: NIST SP 800-226 (final, marzo 2025) "Guidelines for Evaluating Differential Privacy Guarantees" con "differential privacy pyramid" y "privacy hazards". — [NIST SP 800-226](https://csrc.nist.gov/pubs/sp/800/226/final)
- WP216 sobre DP: DP no cambia los datos originales y exige llevar registro de consultas para limitar inferencia y vinculación. — [WP216](https://ec.europa.eu/justice/article-29/documentation/opinion-recommendation/files/2014/wp216_en.pdf)
- Zero trust: NIST SP 800-207 (ago-2020) define arquitectura donde no hay confianza implícita por ubicación de red; autenticación y autorización de sujeto y dispositivo ocurren antes de abrir una sesión. — [NIST SP 800-207](https://csrc.nist.gov/pubs/sp/800/207/final)
- Supply chain: SLSA v1.0 define una pista "Build" con niveles 1-3 y no cubre calidad del código, productores maliciosos ni confianza transitiva en dependencias (la página consultada está marcada como retirada y remite a v1.2). — [SLSA v1.0](https://slsa.dev/spec/v1.0/about)
- SBOM: definición legal en CRA Art. 3(39) ("formal record containing details and supply chain relationships of components") y requisito Anexo I Parte II(1). — [CRA](https://publications.europa.eu/resource/celex/32024R2847)
- Residencia/soberanía: Data Act Art. 32 (acceso gubernamental no personal) y GDPR Cap. V; ver §4-§5.
- Argentina Ley 25.326 Art. 9: medidas técnicas y organizativas para "garantizar la seguridad y confidencialidad", detectar desviaciones; Art. 12: prohibida la transferencia a países sin nivel adecuado, con excepciones; LGPD Art. 46: medidas "aptas a proteger" de accesos no autorizados y situaciones accidentales o ilícitas; LGPD Art. 33: transferencia internacional solo con adecuación o garantías (cláusulas contractuales, normas globales, sellos). — [Ley 25.326](https://servicios.infoleg.gob.ar/infolegInternet/anexos/60000-64999/64790/texact.htm); [LGPD](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
- México: nueva LFPDPPP publicada en el DOF el 20-mar-2025, con la Secretaría Anticorrupción y Buen Gobierno como autoridad (tras la extinción del INAI); última reforma 14-nov-2025. — [Cámara de Diputados: LFPDPPP](https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf) (datos de resultados de búsqueda; texto no leído); [comunicado Diputados](https://comunicacionsocial.diputados.gob.mx/index.php/notas/publica-dof-decreto-de-nuevas-leyes-secundarias-de-transparencia-y-proteccion-de-datos-personales)
- Argentina: reforma de la Ley 25.326 en el Congreso (proyecto AAIP y proyecto Rossi 3397-D-2026) sin sanción confirmada. — [abogados.com.ar](https://abogados.com.ar/nuevo-proyecto-de-ley-de-proteccion-de-datos-personales/39762) (secundaria)

### Inferencias
- Capas de cifrado recomendadas: TLS 1.2+ en tránsito (HIPAA §164.312(e), DORA Art. 9(2)); cifrado en reposo con CMK del cliente y rotación; envelope por tenant/sujeto cuando se necesite crypto-shredding; HYOK/XKS solo con requisito regulatorio/soberanía explícito por su coste de disponibilidad.
- FPE (FF1) sirve para mantener formato (PAN, DNI/CUIL) en sistemas legados, pero sigue siendo cifrado reversible = dato personal/CHD; en PCI no reduce alcance por sí solo (el suplemento de 2011 dejaba en evaluación los tokens basados en cifrado).
- Keyed hashing (HMAC) con clave en KMS es la forma práctica de pseudonimizar IDs para joins; la clave es la "información adicional" del Art. 4(5) y debe custodiarse separada.
- DP en analítica: usar solo con presupuesto de privacidad gobernado; no equivale a "anonimización" automática sin la evaluación EDPB 02/2026.
- Dependencias: pin con lockfiles/hashes, SBOM (CycloneDX/SPDX) por build y provenance SLSA; CRA aplica a fabricantes de productos con elementos digitales, no obliga directamente a un pipeline interno.

### Gaps
- Sin fuente primaria para: Azure Private Link, GCP Private Service Connect/VPC-SC, Azure Key Vault/GCP KMS (BYOK/EKM), AWS Secrets Manager, SPIFFE/Workload Identity Federation de GCP/Azure, NIST SP 800-53 rev5 (SC-28, AU, AC-3), NIST SP 800-57, PII discovery (Macie/DLP/Purview/Unity Catalog classification), OWASP/OpenSSF scorecards, SPDX/CycloneDX specs, NIST SSDF 800-218.
- Estado final del SP 800-38G r1 no verificado en la página oficial (solo vía buscador).

---

## 8. Seguridad a nivel de fila/columna y masking por plataforma (docs oficiales)

### Takeaway
Todas las plataformas ofrecen RLS/CLS/masking nativo, pero con distintas limitaciones críticas para ingeniería: masking en Snowflake y Redshift se evalúa por rol/política; BigQuery lo liga a policy tags; Databricks UC usa UDFs (filtros/máscaras) o ABAC por tags gobernados y limita time travel/clones; Fabric ofrece DDM en Warehouse y OneLake security (RLS/CLS) aplicado a todos los motores de Fabric. Todos los proveedores advierten que masking no impide inferencia.

### Cited Findings
**Snowflake**
- Column-level security = masking policies (Dynamic Data Masking y External Tokenization); política: un tipo de dato, condiciones, funciones; condiciones con `CURRENT_ROLE`, `INVOKER_ROLE`, `IS_ROLE_IN_SESSION` o tabla de entitlements; masking basado en etiquetas (policy asignada directamente a la columna tiene precedencia); por defecto el propietario del objeto no puede quitar la política ni ver la columna; requiere Enterprise Edition o superior. — [Snowflake: Column-level Security](https://docs.snowflake.com/en/user-guide/security-column-intro)
- Row access policies: objeto de esquema; controla filas en SELECT y las que UPDATE/DELETE/MERGE pueden tocar; se evalúa con el rol del propietario de la política; patrón de tabla de mapeo (más lento; recomiendan función memoizable); si hay row access y masking, se evalúa primero la row access; una columna no puede estar en la firma de ambas políticas; requiere Enterprise Edition. — [Snowflake: Row access policies](https://docs.snowflake.com/en/user-guide/security-row-intro)

**BigQuery**
- Masking dinámico con data policies sobre policy tags: reglas (hash SHA-256 determinista, hash aleatorio con sal, email mask, first/last four, date year, default, nullify, rutina personalizada); roles `bigquerydatapolicy.maskedReader` y Data Catalog Fine-Grained Reader; límites: hasta nueve data policies por policy tag; incompatible con `tabledata.list`, copy jobs, snapshots y wildcard tables; no aceleración BI Engine; el caching puede devolver datos brevemente tras revocar acceso. — [BigQuery: dynamic data masking](https://docs.cloud.google.com/bigquery/docs/column-data-masking-intro)
- Row-level access policies: filtro tipo WHERE por lista de grantees; quien no está en ninguna política no ve filas; no compatible con SQL legacy, JSON columns, wildcard tables ni Storage Read API con subquery; `CREATE OR REPLACE TABLE` o `WRITE_TRUNCATE` eliminan las políticas implícitamente (TRUNCATE no); no hay poda de particiones por el filtro; el masking se aplica encima de RLS. — [BigQuery: row-level security](https://docs.cloud.google.com/bigquery/docs/row-level-security-intro)

**Databricks Unity Catalog**
- Row filters (UDF SQL, `ALTER TABLE … SET ROW FILTER`) y column masks (`SET MASK`); recomiendan ABAC (políticas a nivel catálogo/esquema por governed tags) para consistencia; requiere Runtime ≥12.2 LTS; limitaciones: no en vistas, no accesibles por Iceberg REST/Unity REST APIs, no compartibles vía Delta Sharing/OpenSharing con filtros a nivel de tabla, sin acceso por ruta, sin time travel, sin deep/shallow clones, restricciones en MERGE. — [Databricks: row filters and column masks](https://docs.databricks.com/aws/en/data-governance/unity-catalog/filters-and-masks/)

**Amazon Redshift**
- Dynamic data masking: políticas de enmascaramiento por usuario/rol (RBAC), múltiples políticas por columna con prioridades, hash con UDF (SQL, Python o Lambda) para permitir joins, masking condicional a nivel celda; el RLS usa políticas con expresiones y recomienda políticas simples (las tablas de lookup añaden coste). — [Redshift DDM](https://docs.aws.amazon.com/redshift/latest/dg/t_ddm.html); [Redshift RLS](https://docs.aws.amazon.com/redshift/latest/dg/t_rls.html)
- Nota de plataforma: AWS dejará de soportar UDFs Python en Redshift después del 30-jun-2026 (afecta funciones de masking basadas en Python). — [Redshift DDM](https://docs.aws.amazon.com/redshift/latest/dg/t_ddm.html)

**Microsoft Fabric**
- Warehouse/SQL endpoint: DDM con funciones default, email, random y partial; roles Admin/Member/Contributor ven datos sin máscara; `UNMASK` para ver; advertencia: DDM no impide inferencia por consultas (ejemplo con `WHERE Salary > 99999 AND Salary < 100001`); "Don't use dynamic data masking alone to fully secure sensitive data". — [Fabric: Dynamic Data Masking](https://learn.microsoft.com/en-us/fabric/data-warehouse/dynamic-data-masking)
- OneLake security: roles de acceso a datos (solo roles Grant) con RLS/CLS a nivel de tabla, aplicados en todos los motores de Fabric; afectan a Viewers/Read (Admin, Member y Contributor ya tienen acceso a los datos); motores externos autorizados en preview; roles asignados a identidades Entra; shortcuts heredan según roles del lakehouse origen. — [Fabric: OneLake data security overview](https://learn.microsoft.com/en-us/fabric/onelake/security/get-started-security)

### Inferencias
- ABAC/ReBAC: UC soporta ABAC por tags gobernados; Snowflake lo implementa con tag-based masking + role/entitlement; BigQuery con policy tags (jerarquía). ReBAC (relaciones tipo Zanzibar/OpenFGA) no figura en estas docs: sería una capa externa de entitlements (tabla de mapeo + RLS).
- Riesgo transversal: copia de datos sin control (exports, clones, snapshots, time travel, caches) sortea RLS/masking; la regla es aplicar controles en la capa más baja posible y bloquear ruta de acceso directa a storage.
- El masking dinámico es un control de exposición, no de anonimización: no cumple Art. 17 (borrado) ni Rec. 26 (ver CEF 2025 Issue 7).

### Gaps
- No verifiqué si UC ABAC es GA o preview al 2026 (la página no indicó estado en el extracto); ni límites de edición/precio.
- No consulté docs de Fabric RLS/CLS en Warehouse ni Snowflake tag-based masking en detalle.
- No consulté Google Cloud DLP/Sensitive Data Protection, AWS Macie, Purview, Snowflake classification ni Databricks classification para descubrimiento de PII.

---

## 9. Audit logging, descubrimiento/clasificación de PII, gobernanza (síntesis con referencias legales)

### Takeaway
Las normas piden evidencia y trazabilidad (HIPAA audit controls, GDPR accountability Art. 5(2) y Art. 30, DORA/NIS2 gestión de TIC), pero no un formato de log; la clasificación de datos es premisa explícita en DORA Art. 9(4)(d) para decidir el cifrado.

### Cited Findings
- HIPAA §164.312(b): mecanismos que "record and examine activity" en sistemas con ePHI. — [45 CFR 164.312](https://www.ecfr.gov/api/renderer/v1/content/enhanced/current/title-45?part=164&section=164.312)
- DORA Art. 9(4)(d): cifrado "based on results of approved data classification and ICT risk assessment processes". — [DORA](https://publications.europa.eu/resource/celex/32022R2554)
- GDPR Art. 30 y 5(2) (ver §2). Fabric: OneLake diagnostics para accesos y Fabric audit log para cambios de roles/sharing. — [Fabric](https://learn.microsoft.com/en-us/fabric/onelake/security/get-started-security)
- Informe CEF 2025: mejores prácticas incluyen "data deletion matrix" (tipo de dato × base legal × retención) y documentar en el RoPA obligaciones legales de retención. — [EDPB CEF 2025](https://www.edpb.europa.eu/system/files/2026-02/edpb_cef-report_2025_right-to-erasure_en.pdf)

### Inferencias
- Mapa control → requisito (síntesis propia): ver tabla.

| Control en lakehouse/warehouse | Requisito que lo respalda | Implementación |
|---|---|---|
| Clasificación PII/tags en el catálogo | DORA 9(4)(d), GDPR Art. 30, Art. 25 | Tags gobernados (UC, policy tags, Snowflake tags) que disparan masking/ABAC |
| RBAC + RLS/CLS deny-by-default | GDPR 25(2), 32; HIPAA 164.312(a); DORA 9(4)(c) | Roles por dominio, filtros por tabla/ABAC, revisión periódica |
| Masking dinámico | GDPR 25, 32 (seudonimización) | Políticas por rol; nunca única defensa (Fabric/DDM advierten inferencia) |
| Seudonimización con HMAC/token y clave en KMS | GDPR 4(5), 32(1)(a), Rec. 28 | Clave separada, rotación; tabla de mapeo en dominio aislado |
| Tokenización de PAN en el borde | PCI (suplemento 2011) | Lakehouse solo tokens; tokenizador en CDE segmentado |
| Cifrado en reposo/tránsito, CMK/envelope | GDPR 32(1)(a); HIPAA 164.312(a)(e); DORA 9(2); NIS2 21(2)(h) | KMS + envelope por tenant; TLS≥1.2 |
| Crypto-shredding por sujeto | GDPR 17, 5(1)(e) (inferencia) | DEK por sujeto/tenant; borrar DEK; documentarlo |
| Ledger de supresiones + PURGE/VACUUM/expire_snapshots | GDPR 17(1), CEF 2025 | Jobs programados + verificación auditada |
| Retención y borrado de backups | GDPR 5(1)(e), 17, ICO/EDPB | Retención corta, "beyond use", reaplicar ledger tras restore |
| Secretos dinámicos + OIDC sin claves largas | GDPR 32; NIS2 21(2)(i)(j); DORA 9(4)(d) | Vault/IAM roles/OIDC; sin secretos en repos |
| Red privada (PrivateLink/endpoints) | GDPR 32; DORA 9(4)(b) | Sin IP públicas, políticas de endpoint |
| Audit logs inmutables | HIPAA 164.312(b); GDPR 5(2) | Logs de acceso a datos en bucket WORM, sin PII en claro |
| SBOM + pin de dependencias + provenance | NIS2 21(2)(d)(e); CRA Anexo I | Lockfiles, SBOM por build, SLSA |
| Contratos de procesador, subencargados | GDPR 28 | Revisión DPA, cláusula de borrado/devolución |
| Residencia y llaves regionales | GDPR Cap. V, Data Act 32 | Regiones UE, SCC, HYOK solo si hace falta |

### Gaps
- No se verificaron las referencias NIST SP 800-53 (AU-2, AU-9) ni guías de logging; no hay fuente primaria para retención recomendada de logs de auditoría.

---

## Resumen del estado de verificación (oct-2026)

| Ítem | Estado verificado | Fuente primaria |
|---|---|---|
| Data Act | Aplica 12-sep-2025; switching charges prohibidos desde 12-ene-2027 (Art. 29); egress en uso paralelo a coste (Art. 34) | [Reg. 2023/2854](https://publications.europa.eu/resource/celex/32023R2854) |
| AI Act high-risk | Anexo III: 2-dic-2027; Anexo I: 2-ago-2028 (Reg. 2026/1744, DOUE 24-jul-2026) | [Reg. 2026/1744](https://publications.europa.eu/resource/celex/32026R1744) |
| Digital Omnibus (GDPR/datos) | No acordado (fuentes secundarias hasta sep-2026) | [Acompli](https://acompli.ie/news/digital-omnibus-gdpr-cookies-status-september-2026/) |
| DPF | Decisión vigente; T-553/23 desestimado 3-sep-2025; casación C-703/25 P pendiente | [Comunicado 106/25](https://curia.europa.eu/jcms/upload/docs/application/pdf/2025-09/cp250106en.pdf); [Decisión 2023/1795](https://publications.europa.eu/resource/celex/32023D1795) |
| CJEU SRB C-413/23 P | Leído en texto original (sentencia 4-sep-2025) | [Sentencia](https://publications.europa.eu/resource/celex/62023CJ0413) |
| EDPB Opinion 28/2024 | Leído en PDF original (17/18-dic-2024) | [PDF](https://www.edpb.europa.eu/system/files/2024-12/edpb_opinion_202428_ai-models_en.pdf) |
| EDPB Guidelines 01/2025 | Versión de consulta; sin versión final encontrada | [PDF](https://www.edpb.europa.eu/system/files/2025-01/edpb_guidelines_202501_pseudonymisation_en.pdf) |
| EDPB Guidelines 02/2026 anonimización | Adoptadas para consulta 7-jul-2026; consulta hasta 30-oct-2026 | [PDF](https://www.edpb.europa.eu/system/files/2026-07/edpb_guidelines_202602_anonymisation_v1_en_0.pdf) |
