# AUDIT — `decision-resilience-engine`

Auditoría de repositorio con criterio de *staff engineer* + *staff product designer*,
hecha sobre el código real, no sobre los documentos. Todo lo que se afirma acá se
verificó ejecutando algo: los comandos y su salida están citados.

**Fecha:** 2026-09-13 · **Commit base:** `59ee36c` · **Entorno:** Python 3.11.15, Linux

**Convención de madurez usada en todo el informe:**

| Etiqueta | Significa |
|---|---|
| **Implementado** | Hay código y hay test que lo ejecuta. |
| **Documentado** | Hay especificación escrita, sin código. |
| **Planificado** | Aparece como backlog o "siguiente oleada". |
| **Overclaim** | El texto público sugiere más madurez que el código. |

---

## A1. Qué es esto, en una frase honesta

**Para un recruiter:**
> Un motor de decisiones que deja rastro auditable de cada paso y puede retomarse
> exactamente donde quedó, más un laboratorio de backtesting cuantitativo que se
> usa como banco de medición.

**Para un staff engineer:**
> Un orquestador con FSM explícita (21 transiciones en tabla, transición no
> declarada ⇒ excepción), un ledger SQLite append-only con idempotencia por
> `(run_id, data_hash)` y colisión tipada como HTTP 409, checkpoints por transición
> con `resume` fiel al contexto, y contratos Pydantic verificados contra su propia
> documentación por un test. Encima de eso, un backtester de futuros BTC/ETH con
> walk-forward que se invoca como *measurement command* por subproceso.

**Qué NO es** (matar expectativas infladas antes de que las mate un entrevistador):

- **No es un motor de trading ni una estrategia con alfa.** El MAT mide
  probabilidades de ruina sobre un dataset sintético; la corrida por defecto da
  `p_win_terminal = 0.0` y `p_ruin = 0.73`. Es un instrumento de medición, no un
  resultado que vender.
- **No es el sistema de `DRE_TECHNICAL_ARCHITECTURE.md`.** Ese documento describe
  KDE con FFT, copulas, programación estocástica en dos etapas, DoWhy y un ledger
  con evidencia de manipulación. **Nada de eso está implementado.**
- **No es producción.** La API no tiene autenticación ni rate limiting; el Redis
  solo se probó contra `fakeredis`; nunca se midió ninguno de los SLAs de latencia
  que promete §7 del doc técnico.
- **No es un proyecto de equipo.** El paquete PDR tiene tablas de firmas para
  "Chief Architect", "Engineering Manager" y "Compliance Officer". No hubo comité.

---

## A2. Mapa real vs. mapa documentado

Columna "Brecha" = distancia entre lo que promete el texto público y lo que hace el código.

| Componente | Prometido en docs | Implementado en código | Evidencia | Brecha |
|---|---|---|---|---|
| **FSM del orquestador** | Máquina de estados completa, `O(1)`, "async I/O", sub-ms | Tabla `dict[(estado, evento)] → estado` con 21 transiciones, síncrona | `dre/orchestrator/fsm.py:9-31`; `tests/test_dre_invariants.py::test_i5_*` | **Baja.** El diagrama §5.2 coincide con el código. Lo de `asyncio` es aspiracional. |
| **Orquestación** | Router por modo de ejecución (FAST/STANDARD/DEEP_AUDIT), reintentos, `iteration_count` | Dos recorridos secuenciales fijos; `execution_mode` **hardcodeado a `STANDARD`**; `iteration_count` siempre 0 | `dre/orchestrator/engine.py:62,107`; `grep iteration_count dre/` → solo `=0` | **Alta.** No hay ruteo. Los tres modos existen en el enum y no cambian nada. |
| **Governance SQLite** | Ledger inmutable, "tamper evidence: UPDATE/DELETE rechazado y logueado como `AUDIT_VIOLATION`" | 3 tablas, solo `INSERT`, idempotencia y colisión reales | `dre/governance/sqlite_store.py`; `tests/test_dre_invariants.py::test_i3_*` | **Media.** La idempotencia y la colisión son de verdad. La *evidencia de manipulación* **no existe**: nada impide un `UPDATE` manual sobre el archivo. |
| **Checkpoints / resume** | "Redis TTL 72h", "Checkpoints TTL 24h", restore ante fallo | Checkpoint por transición en SQLite; `resume_latest` reconstruye el contexto **exacto** | `engine.py:47-53`; `test_i4_resume_reconstructs_the_same_context` | **Media.** El resume funciona y está probado campo por campo. Los TTL y la política de expiración no existen. |
| **Redis** | Estado volátil distribuido, locking, TTL 72h | `RedisContextStore` (get/save/delete + TTL opcional), probado solo con `fakeredis`; el pipeline usa memoria | `dre/storage/redis_store.py`; `tests/test_dre_storage.py` | **Media.** La interfaz está bien separada, pero nunca corrió contra un Redis real ni se usa por defecto. |
| **API HTTP** | "REST/gRPC ready", FastAPI + asyncio | 3 endpoints, validación Pydantic, 409 tipado, 422 y 404 correctos | `dre/api/app.py`; `tests/test_dre_api.py` (7 tests) | **Baja** en lo que hace; **alta** en lo que falta: sin auth, sin gRPC, servidor de desarrollo. |
| **Coherence** | `DataCoherenceEngineer`, validación de integridad | Chequea que `data_hash` empiece con `sha256:` y que el modo sea válido. 8 líneas. | `dre/skills/coherence.py` | **Alta.** El nombre del componente promete mucho más que un chequeo de prefijo. |
| **Forecasting** | KDE+FFT, selección de familia (Normal/LogNormal/Gamma/Beta/t), Anderson–Darling, updating bayesiano, copulas, ADF/KPSS | Media, desvío, CV y **un test KS contra la normal ajustada** | `dre/skills/forecasting.py` (33 líneas) | **Muy alta → OVERCLAIM.** El campo `kind` del propio código dice `univariate_gaussian_proxy`, que es honesto; el documento de arquitectura, no. |
| **Stress LP** | ≥50 escenarios, colas históricas p95/p99, muestreo por copulas, Latin Hypercube | `linprog` HiGHS sobre una lista de Δ en el RHS **provista por el llamador**; devuelve `infeasibility_rate` y `min_slack_global` | `dre/skills/stress.py`; el pipeline le pasa 3 y 2 escenarios (`engine.py:89,148`) | **Alta.** Las métricas son las del contrato, pero **no hay generación de escenarios** y el pipeline usa 3, no 50. |
| **Backprop** | Árbol de reformulación (buffer / estocástico en 2 etapas / relajación con penalidad), máx. 2 iteraciones | Relajación LP con timeout por hilo que devuelve `FEASIBLE/INFEASIBLE/TIMEOUT` | `dre/skills/backprop.py` | **Muy alta.** **No reformula nada.** El único consumidor es un test; el pipeline no lo llama. |
| **Drift** | PSI con ventanas deslizantes con estado, Sherman–Morrison–Woodbury, regla de 3 corridas, umbrales por banda | Dos funciones puras: PSI por histograma y norma Frobenius | `dre/skills/drift.py` | **Alta.** Las métricas están; la lógica operativa (umbrales, persistencia, alertas) no. Ningún estado del pipeline las invoca. |
| **Causal** | Jerarquía de 3 niveles, ATE con intervalos, refutación con placebo, DoWhy/CausalML, CATE | Solapamiento de histogramas 1-D + gate en 0.6 | `dre/skills/causal.py` (25 líneas) | **Muy alta → OVERCLAIM.** No calcula ningún efecto causal. Es un chequeo de solapamiento de distribuciones. |
| **Override** | Sandbox de 50 iteraciones, `expiry_utc`, rollback automático, log de intentos | Función pura que clasifica ΔKPI en 3 bandas | `dre/skills/override.py` (14 líneas) | **Muy alta.** Están los umbrales, no el protocolo. Ningún estado del pipeline la llama. |
| **Puente DRE→MAT** | "measurement.command" integrado al pipeline | `subprocess` → `compound_optimize_runner.py`, parsea stdout | `dre/measurement/mat_runner.py` | **Media.** El puente existe y anda, pero **el pipeline DRE nunca lo invoca**: hoy solo lo llama un test. |
| **Runners MAT** | Backtest compuesto con funding, ventanas deslizantes, walk-forward, rejilla de señales | Todo eso existe y corre | `compound_optimize_runner.py` (678 líneas), `scripts/optimize_signal_grid.py` (690) | **Baja** funcionalmente, **alta** en pruebas: 1368 líneas con **cero tests unitarios**; solo un *smoke* de CI que verifica que el JSON tiene dos claves. |

**Resumen del mapa:** el eje DRE (FSM + governance + checkpoints + API + contratos)
es real y verificable. Los seis *skills* son proxies honestos en el código y
sobrevendidos en el documento de arquitectura. Cuatro de los seis
(`backprop`, `drift`, `override`, y el propio puente MAT) **no los llama ningún
recorrido del pipeline**: existen y se testean aisladamente.

---

## A3. Fortalezas que sí sirven para venderte

Esto es lo que un staff engineer reconoce como criterio, no como volumen de código.

1. **Idempotencia y colisión como decisión de diseño, no como accidente.**
   `write_run` devuelve `inserted` / `already_existed` y levanta `RunIdCollisionError`
   con un payload de recuperación cuando el mismo `run_id` llega con otro
   `data_hash`. Se sirve como HTTP 409 con cuerpo tipado. Reejecutar un run no
   duplica nada; reejecutarlo con otros datos **no se permite en silencio**.
   *Evidencia:* `bash scripts/demo_dre.sh` pasos 4 y 5; `tests/test_dre_invariants.py`.

2. **FSM en tabla, con falla explícita.** Las transiciones son datos, no `if`s
   desparramados. Una transición no declarada lanza `FSMError` en vez de caer a un
   estado por defecto. Eso es lo que permite testear la FSM como grafo (estados
   inalcanzables, estados absorbentes) sin ejecutarla.

3. **Checkpoints con resume verificado campo por campo.** El test no compara el
   estado final, compara `model_dump(mode="json")` completo del contexto guardado
   contra el devuelto. Es la diferencia entre "el resume anda" y "el resume no
   miente".

4. **Contratos que no pueden derivar de la documentación.** El ICD dice espejar
   `dre/contracts/`; un test (`test_docs_contract.py::test_d2_*`) verifica que los
   snippets sean el archivo **verbatim**. Si cambia el código y no el doc, falla CI.

5. **Separación limpia de capas.** `ContextStore` como ABC con dos backends,
   *skills* como funciones puras sin estado, governance detrás de una clase, API
   como fábrica (`create_app`) que recibe la ruta de la DB. Se puede testear todo
   sin levantar nada.

6. **Reproducibilidad real.** Dataset sintético generado por script (24 500 barras
   en 0.3 s), seeds explícitos en cada corrida, CI en dos versiones de Python,
   `ruff` + `ruff format` + pre-commit, y un contrato de métricas versionado
   (`optimization/contract.json` + `ce-optimize-spec.yaml`).

7. **Specs escritas antes del código, con tabúes explícitos.**
   `docs/specs/2026-04-27-surfer-compound-win-requirements.md` define requisitos
   con IDs, un gate walk-forward, y una lista de *tabúes anti curve-fitting*
   ("no añadir ventanas de MA distintas de las del cóctel"). El gate R8 se terminó
   implementando como `--holdout-frac`. **Esa trazabilidad requisito → flag es el
   activo de portfolio más fuerte del repo** y estaba borrado del árbol de trabajo.

8. **Disclaimer de research presente y correcto**, más `SECURITY.md` con alcance
   acotado y MIT limpio.

---

## A4. Riesgos y deudas

### Confianza / claims

- **R1 (crítico).** El documento de arquitectura se lee como un reporte de estado.
  Un lector técnico que abra `DRE_TECHNICAL_ARCHITECTURE.md` primero y `dre/skills/`
  después concluye que el repo exagera. La única línea que lo aclaraba estaba al
  **final** del archivo, en cursiva. *(Corregido: ver P0-4.)*
- **R2.** `docs/pdr/05` tiene una tabla de firmas con cuatro roles para un repo de
  una persona. Sin marco, parece *cosplay* corporativo; con marco, es un ejercicio
  de ingeniería de sistemas defendible. *(Corregido: ver P0-5.)*
- **R3.** `forecasting`, `causal` y `override` tienen nombres de componentes
  empresariales sobre 25–35 líneas de estadística básica. El código es honesto
  (`univariate_gaussian_proxy`); el índice de docs no lo era.

### Código

- **R4.** `compound_optimize_runner.py` (678 líneas) y `scripts/optimize_signal_grid.py`
  (690) **no tienen tests unitarios**. La única cobertura es un *smoke* de CI que
  verifica que el JSON de salida tiene dos claves. Es la mitad del repo en líneas.
- **R5.** Cuatro *skills* (`backprop`, `drift`, `override`) y el puente MAT no los
  invoca ningún recorrido del pipeline. Son bibliotecas testeadas, no partes del
  motor. El README los listaba como si fueran el motor.
- **R6.** `ExecutionContext.checkpoint_refs` está declarado y siempre vacío. Un
  contrato con un campo que nunca se llena es, en pequeño, exactamente lo que este
  repo dice combatir.
- **R7.** `compound_optimize_runner.py` busca una DB en `../BOTS TRADING/data/candles.db`,
  una carpeta privada de la máquina del autor, en 4 archivos. Filtra el layout local
  a un repo público y confunde a cualquiera que clone.

### CI / build

- **R8 (crítico, latente).** `requirements-dev.txt` pineaba `ruff>=0.9,<1` y CI
  corre `ruff format --check .`. El formateador de `ruff` **cambia entre versiones
  menores**: con `ruff 0.9.10` el check falla por `compound_optimize_runner.py`;
  con `ruff 0.16.7` falla por `docs/pdr/02_Interface_Contracts_ICD.md`. CI estaba
  verde el 2026-05-06 y hoy fallaría, sin que nadie tocara una línea de código.
  Además `.pre-commit-config.yaml` apuntaba a `v0.15.12`, una tercera versión.
  *(Corregido: ver P0-2.)*
- **R9.** El paso "Compile check" usa `compileall`, que **no ejecuta imports**: por
  eso CI nunca detectó que el quickstart del README estaba roto (ver P0-1).

### Packaging

- **R10.** El paquete se llamaba `decision-resilience-engine` y **excluía `dre/` de
  la wheel**: `pip install decision-resilience-engine` entregaba únicamente los
  módulos MAT. El paquete no contenía aquello que le da el nombre.
  *(Corregido: ver P1-3.)*
- **R11.** `import dre` fallaba con `ModuleNotFoundError: fastapi` porque
  `dre/__init__.py` importaba `create_app` en forma ansiosa. El motor no debería
  exigir un servidor HTTP. *(Corregido: ver P1-3.)*
- **R12.** El README lideraba con `pip install sistema-optimizacion-mat` (nombre
  viejo, versión 0.2.0 en PyPI) y con un badge "pendiente" del nombre nuevo, que
  **no existe en PyPI** (`GET /pypi/decision-resilience-engine/json` → 404). Tres
  párrafos de instalación antes de mostrar qué hace el proyecto.
  *(Corregido: ver P0-3.)*

### DX / demo

- **R13 (crítico).** `python scripts/run_dre_api.py` —el comando estrella del
  README, el que abre la demo de 60 segundos— **fallaba siempre**:
  `ModuleNotFoundError: No module named 'dre'`. Python pone `scripts/` al frente de
  `sys.path`, no la raíz del repo, y `dre/` no estaba instalado. Los otros tres
  wrappers de `scripts/` sí hacían el `sys.path.insert`; este lo omitía.
  *(Corregido: ver P0-1.)*
- **R14.** El ledger del demo (`data/dre_governance.sqlite`) **no estaba en
  `.gitignore`** (solo `data/*.db`): correr la demo dejaba un artefacto binario
  listo para commitear. *(Corregido.)*
- **R15.** La demo eran seis bloques de `curl` en el README que el lector tenía que
  ejecutar a mano, en dos terminales, y que no mostraban la propiedad interesante
  (idempotencia, colisión, bitácora). *(Corregido: ver P0-6.)*

### Documentación / presentación

- **R16 (crítico).** **Dos de los tres diagramas Mermaid** del documento de
  arquitectura **no renderizan en GitHub**: paréntesis sin comillas dentro de
  etiquetas `[...]` y `\n` literal. GitHub muestra "Unable to render rich display".
  Los diagramas son lo primero que mira un lector técnico. *(Corregido: ver P0-7.)*
- **R17.** `docs/README.md` era un cajón: listaba tres documentos de *marketing*
  (`LAUNCH_KIT`, `OUTREACH_EXECUTION`, `LAUNCH_DAY_CHECKLIST`) al mismo nivel que
  la arquitectura. Un hiring manager que ve un plan de 7 días para "maximizar
  stars" en el índice de documentación del proyecto lee promoción, no ingeniería.
  *(Corregido: movidos a `docs/internal/`.)*
- **R18.** Esos mismos documentos enlazan a un release `v0.3.0` **en borrador** y a
  un proyecto de PyPI que no existe. Links rotos en el material de difusión.
- **R19.** El commit `362dff1` borró `docs/specs/` y `docs/brainstorms/` —278
  líneas de specs con requisitos y trazabilidad— por ser "no necesarios para
  correr el proyecto". Correcto para un usuario, **equivocado para un portfolio**:
  era la mejor evidencia de criterio del repo. *(Corregido: restaurados desde
  historia, con mojibake reparado.)*
- **R20.** `README.md` y `CHANGELOG.md` empezaban con BOM UTF-8 (ya había roto
  `python -m build` una vez, según el CHANGELOG 0.3.0); `data/__init__.py` tenía un
  carácter de reemplazo U+FFFD. *(Corregido.)*

---

## A5. Primera impresión de un extraño en 60 segundos

Simulación honesta de las tres audiencias abriendo el repo **antes** de esta auditoría.

**(A) Recruiter no técnico — se pierde a los 15 segundos.**
Lee "Framework de investigacion y ejecucion centrado en resiliencia y gobernanza de
decisiones (DRE), con MAT como puente de medicion cuantitativa secundario (futuros
BTC/ETH)". Son 27 palabras, cuatro siglas y ningún sustantivo concreto. No sabe si
es un producto, una librería o una tesis. Ve "futuros BTC/ETH" y archiva mentalmente
"cripto". **Cierra.**

**(B) Hiring manager / staff engineer — llega a los 90 segundos y encuentra fricción.**
Los badges están bien (CI verde, licencia, Python). Pero el tercer bloque del README
es instalación desde PyPI con **dos** nombres de paquete y una explicación de por qué
uno está "pendiente": eso responde una pregunta que nadie hizo todavía. Si intenta la
demo, el primer comando falla con `ModuleNotFoundError`. Si abre el documento de
arquitectura en su lugar, ve dos diagramas rotos y después promesas de copulas y
DoWhy que no encuentra en `dre/skills/`. **Se va con la sensación de que el repo
promete más de lo que entrega**, que es exactamente lo contrario de lo que el repo
intenta demostrar.

**(C) Quant / researcher que clona — es el que mejor la pasa.**
`bootstrap_synthetic_candles_db.py` corre en 0.3 s, `pytest` da verde, el runner MAT
escupe JSON con walk-forward en 0.3 s. Todo eso funciona. Pero abandona el DRE
porque el servidor no arranca, y no encuentra un solo test que cubra las 1368 líneas
del motor MAT que acaba de correr.

**Qué cierra la pestaña, en orden:** (1) el primer comando de la demo falla;
(2) el título no dice qué problema resuelve; (3) la distancia entre el documento de
arquitectura y `dre/skills/`.

---

## A6. Scorecard (1–10)

Nota **antes** → **después** de los cambios de esta auditoría.

| Dimensión | Antes | Después | Justificación |
|---|:---:|:---:|---|
| **Claridad de propuesta** | 3 | 8 | Antes: 27 palabras con cuatro siglas y sin problema enunciado; dos productos mezclados en el primer párrafo. Ahora: problema en una línea, DRE y MAT separados con quickstarts distintos. |
| **Honestidad de claims** | 4 | 9 | Antes: el doc técnico prometía KDE+FFT, copulas y DoWhy con 33 líneas de `scipy.stats` detrás, y el PDR simulaba un comité. Ahora: banner de alcance en el doc de diseño, tabla implementado/documentado/no implementado, y sufijo *lite* donde corresponde. |
| **Calidad del README** | 4 | 8 | Antes: instalación PyPI con dos nombres antes de explicar qué hace; demo a mano en dos terminales. Ahora: gancho, demo de un comando verificada, tabla "hoy vs roadmap", PyPI degradado a nota al pie. |
| **Arquitectura real** | 7 | 7 | Sin cambios de arquitectura, y no hacía falta: FSM en tabla, capas separadas, `ContextStore` como ABC, API como fábrica. Pierde puntos porque cuatro skills no los invoca el pipeline y `execution_mode` es decorativo. |
| **Tests / CI** | 5 | 8 | Antes: 30 tests, casi todos de humo; CI con formateador sin pinear (rojo latente); 1368 líneas de MAT sin tests. Ahora: 48 tests con invariantes reales (idempotencia, append-only encadenado, resume exacto, FSM como grafo), guardas anti-deriva de docs, y `ruff` pineado. El MAT **sigue sin tests unitarios** (P1-5, pendiente). |
| **DX / demo** | 2 | 9 | Antes: el comando principal fallaba siempre. Ahora: `bash scripts/demo_dre.sh` corre en ~2.2 s y muestra las tres propiedades del motor, con un test que verifica que el entrypoint sigue importando. |
| **Empaquetado** | 3 | 8 | Antes: el paquete llamado `decision-resilience-engine` no contenía `dre/`, e `import dre` exigía FastAPI. Ahora: la wheel incluye el motor, la API es un extra opcional, verificado instalando la wheel en un venv limpio. Sigue sin publicar bajo el nombre nuevo (decisión del autor). |
| **Narrativa de autor** | 2 | 8 | Antes: cero. Tres documentos de campaña de difusión en el índice de docs y ninguna línea sobre por qué existe el repo o qué decisiones defiende su autor. Ahora: sección "Por qué existe este repo", specs de diseño restauradas como evidencia de criterio, marketing movido a `docs/internal/`. |

**Promedio: 3.8 → 8.1.** La nota que no se movió (arquitectura real) es la correcta:
esta auditoría no reescribió el producto, corrigió lo que impedía verlo.

---

## Backlog priorizado

**P0** = rompe confianza o rompe la demo · **P1** = calidad visible · **P2** = deseable.

### P0 — implementados en esta auditoría

| # | Problema | Por qué importa para portfolio | Archivos | Cambio | Esf. | Riesgo |
|---|---|---|---|---|:---:|:---:|
| **P0-1** | `python scripts/run_dre_api.py` → `ModuleNotFoundError: No module named 'dre'`. El comando estrella del README nunca funcionó. | Es lo primero que ejecuta un evaluador. Si falla, todo lo demás da igual. | `scripts/run_dre_api.py` | `sys.path.insert` de la raíz del repo, igual que los otros tres wrappers de `scripts/`, con comentario que explica por qué. | S | Bajo |
| **P0-2** | CI rojo latente: `ruff>=0.9,<1` + `ruff format --check .`. Tres versiones distintas entre CI, pre-commit y pyproject. | Un badge de CI en rojo por una release de terceros destruye más credibilidad que la que construye el badge en verde. | `requirements-dev.txt`, `pyproject.toml`, `.pre-commit-config.yaml` | Pin exacto `ruff==0.16.7` en los tres lugares (tag verificado en `ruff-pre-commit`). | S | Bajo |
| **P0-3** | README lidera con instalación PyPI de dos nombres, uno inexistente (404). | Responde una pregunta que el lector todavía no se hizo, y la primera impresión es "confusión de nombres". | `README.md`, `README.en.md` | PyPI degradado a nota al pie; el camino recomendado es clonar. | S | Bajo |
| **P0-4** | El doc de arquitectura se lee como reporte de estado. | Es la fuente principal de *overclaim* del repo. | `docs/DRE_TECHNICAL_ARCHITECTURE.md` | Banner al inicio: qué **no** está implementado, con enlace al mapa real. | S | Bajo |
| **P0-5** | Paquete PDR con tablas de firmas de 4 roles para un repo de una persona. | Sin marco parece inventado; con marco es un ejercicio defendible y hasta un plus. | `docs/pdr/README.md`, `docs/pdr/05_*.md` | Nota "qué es y qué no es": ejercicio de ingeniería de sistemas, sin comité ni firmas. | S | Bajo |
| **P0-6** | La demo eran 6 bloques de `curl` manuales en dos terminales. | La demo es el argumento; tiene que correr sola y mostrar la propiedad interesante. | `scripts/demo_dre.sh` (nuevo) | Un comando: levanta la API, camino feliz, resume, idempotencia, colisión 409 y volcado de la bitácora con las 9 transiciones. ~2.2 s. | M | Bajo |
| **P0-7** | 2 de 3 diagramas Mermaid no renderizan en GitHub. | El diagrama es lo primero que mira un staff engineer. Roto = descuido. | `docs/DRE_TECHNICAL_ARCHITECTURE.md` | Etiquetas entrecomilladas y `<br/>` en vez de `\n`. Validado con `mermaid@11`: 3/3 parsean. | S | Bajo |
| **P0-8** | BOM UTF-8 en `README.md` y `CHANGELOG.md`; U+FFFD en `data/__init__.py`; ledger de la demo fuera de `.gitignore`. | Detalles que un revisor lee como falta de cuidado. | varios | Limpieza de encoding + `data/*.sqlite` ignorado. | S | Bajo |

### P1 — implementados en esta auditoría

| # | Problema | Por qué importa para portfolio | Archivos | Cambio | Esf. | Riesgo |
|---|---|---|---|---|:---:|:---:|
| **P1-1** | Tests de humo, no de invariantes: verificaban que el camino feliz termina en `MONITORING`, no que el motor cumpla sus promesas. | Las invariantes **son** el argumento del repo. Sin tests, son marketing. | `tests/test_dre_invariants.py` (nuevo) | 8 tests: idempotencia sin fila duplicada, colisión tipada, bitácora append-only **encadenada** (el `state_after` de cada evento es el `state_before` del siguiente), resume idéntico campo por campo, y la FSM validada como grafo. | M | Bajo |
| **P1-2** | La documentación podía derivar del código sin que nada fallara. | Un ICD que miente es peor que no tener ICD. | `tests/test_docs_contract.py` (nuevo), `docs/pdr/02_*.md` | ICD reescrito como espejo **verbatim** de `dre/contracts/`, con tabla de diferencias deliberadas vs. el borrador v1.0; test que falla si divergen. Más guardas Mermaid y del entrypoint del README. | M | Bajo |
| **P1-3** | El paquete `decision-resilience-engine` no contenía `dre/`; `import dre` exigía FastAPI. | "El paquete no incluye aquello que le da el nombre" es una pregunta incómoda garantizada en una entrevista. | `pyproject.toml`, `MANIFEST.in`, `dre/__init__.py` | La wheel incluye `dre*`; `pydantic`/`scipy` pasan a dependencias base; FastAPI/uvicorn quedan en el extra `[api]`; `create_app` con import perezoso (PEP 562). Verificado instalando la wheel en un venv limpio. | M | Medio |
| **P1-4** | Cobertura de contrato incompleta en la API. | 422/404 correctos es lo que separa un endpoint de un prototipo. | `tests/test_dre_api.py` | +4 tests: `run_id` malformado → 422, variante desconocida → 422, resume inexistente → 404 (no 500), camino `intervention`. | S | Bajo |
| **P1-6** | Índice de docs como cajón, con marketing al mismo nivel que arquitectura. | Un plan para "maximizar stars" en el índice técnico lee promoción. | `docs/README.md`, `docs/internal/` | Índice de 30 s con columna "leé esto si…"; marketing movido a `docs/internal/` con `git mv` (historia intacta). | S | Bajo |
| **P1-7** | Specs de diseño borradas del árbol de trabajo. | Eran la mejor evidencia de criterio del repo. | `docs/specs/` | Restauradas desde `362dff1^`, mojibake reparado, enlazadas desde el índice. | S | Bajo |
| **P1-8** | `forecasting`/`causal`/`stress`/`backprop` presentados con nombres de componentes empresariales. | Nombrar *lite* lo que es *lite* convierte un overclaim en una señal de honestidad. | `docs/DRE_IMPLEMENTATION_STATUS.md` | Reescrito: alcance real por componente, tabla "diseñado pero no implementado" y brechas conocidas del MVP. | M | Bajo |

### P1 — pendiente (no implementado)

| # | Problema | Por qué importa | Archivos | Cambio propuesto | Esf. | Riesgo |
|---|---|---|---|---|:---:|:---:|
| **P1-5** | `compound_optimize_runner.py` (678 líneas) y `scripts/optimize_signal_grid.py` (690) **sin tests unitarios**. | Es la mitad del repo en líneas y el único *asset* medible del MAT. Un quant lo va a preguntar. | `tests/test_mat_runner.py` (nuevo) | Tests de unidad sobre las funciones puras: `ema`/`sma` contra valores calculados a mano, `calc_indicators` con series construidas, y una propiedad de `sim_window` (equity nunca baja de `kill` sin marcar ruina). No hace falta tocar el runner. | L | Medio — obliga a entender 678 líneas de código compacto. |

### P2 — deseable, no implementado

| # | Problema | Cambio propuesto | Esf. |
|---|---|---|:---:|
| **P2-1** | `ExecutionContext.checkpoint_refs` declarado y siempre vacío. | Poblarlo con el id que devuelve `save_checkpoint` (el contexto persistido no puede contener su propia referencia; documentar esa asimetría) **o** quitarlo del contrato. Hoy está documentado como brecha en el ICD §2.2. | S |
| **P2-2** | El *append-only* es una convención del código, no de la base. | `CREATE TRIGGER` en SQLite que aborte `UPDATE`/`DELETE` sobre `dre_run_registry` y `dre_audit_log`. Convierte una promesa del README en una garantía del motor y es **la mejora de señal técnica más alta que queda**. | M |
| **P2-3** | Ruta a `../BOTS TRADING/data/candles.db` en 4 archivos. | Reemplazar por la variable de entorno `COMPOUND_OPT_DB` (que ya existe) y borrar el fallback al repo hermano. | S |
| **P2-4** | `backprop`, `drift` y `override` no los llama ningún recorrido del pipeline. | Un tercer recorrido `simulate_stress_failure` que ejercite `STRESS_BACKPROP → BACKPROP → ESCALATED` e incremente `iteration_count`. Cerraría la brecha entre la FSM declarada y la ejercitada. | M |
| **P2-5** | `RedisContextStore` solo probado con `fakeredis`. | Job opcional de CI con el servicio `redis:7` y los mismos tests contra el cliente real. | M |
| **P2-6** | `execution_mode` decorativo. | O implementar un `ExecutionModeRouter` mínimo (FAST saltea stress), o reducir el enum a `STANDARD` y documentar el resto como roadmap. | M |
| **P2-7** | Sin `CITATION.cff` (existía y se borró en `362dff1`). | Restaurarlo: es barato y ayuda si alguien académico cita el repo. | S |
| **P2-8** | CI no valida que los diagramas Mermaid parseen de verdad. | El test actual detecta las dos clases de error conocidas por regex. Un job opcional con `@mermaid-js/mermaid-cli` daría validación real. | M |
| **P2-9** | Release `v0.3.0` en borrador y enlazado como público desde `docs/internal/`. | Publicar el release o corregir los enlaces. | S |

---

## Cómo se verificó todo esto

```bash
# Entorno
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

ruff check .                    # All checks passed
ruff format --check .           # 84 files already formatted
pytest tests/ -q                # 48 passed
python scripts/bootstrap_synthetic_candles_db.py   # 24500 barras, 0.3 s
bash scripts/demo_dre.sh        # 9 transiciones, 1 run, HTTP 409, ~2.2 s
python -m build && twine check --strict dist/*     # PASSED (wheel + sdist)
```

Los diagramas Mermaid se validaron con `mermaid@11` bajo `jsdom`, parseando cada
bloque ` ```mermaid ` del repo: **3/3 OK** después del arreglo (2/3 fallaban antes).
La ausencia del paquete en PyPI se verificó con
`GET https://pypi.org/pypi/decision-resilience-engine/json` → **404**.

---

## Higiene de GitHub — texto listo para pegar

Esto no se puede cambiar desde un commit: hay que pegarlo en la UI del repo.

### About (descripción de una línea)

Texto decidido, para pegar en **Settings → About → Description**:

```
Auditable, idempotent, resumable decision engine. MAT is the measurement bench, not the product.
```

**Website:** dejar vacío hasta publicar en PyPI.

### Topics (8)

Lista decidida, para pegar en **Settings → About → Topics**:

```
python  fastapi  decision-engine  orchestration  governance  reproducibility  quantitative-finance  research
```

### Social preview (Settings → Social preview)

Imagen 1280×640. No hace falta diseño: fondo oscuro liso, tipografía monoespaciada,
tres bloques de texto.

```
        DECISION RESILIENCE ENGINE

   append-only ledger · idempotent runs · checkpoint resume

   $ bash scripts/demo_dre.sh
   > runs = 1   audit events = 18   checkpoints = 18
   > HTTP 409  RUN_ID_COLLISION
```

La línea de terminal es el activo: es una captura real de la demo y comunica en un
vistazo que el repo **corre**. Se genera con una captura de terminal sobre fondo
oscuro; no hace falta nada más elaborado.

### Release v0.3.0

Está **en borrador** (`published_at: null`) pero `docs/internal/LAUNCH_KIT.md` lo
enlaza como público. Publicarlo o corregir los enlaces (P2-9).

### Plantillas e issues

Agregadas en esta auditoría:

- `.github/ISSUE_TEMPLATE/claim_challenge.md` — "un claim no se sostiene". Es
  coherente con la tesis del repo: invita a que lo auditen.
- `.github/ISSUE_TEMPLATE/bug_report.md` y `feature_request.md`.
- `CONTRIBUTING.md` **que dice la verdad**: repo de una persona, no busco PRs
  grandes, lo que sí quiero son desafíos a los claims. Es más creíble —y más útil—
  que un CONTRIBUTING genérico que simula una comunidad que no existe.
