# Short pitch — Decision Resilience Engine

Material listo para copiar y pegar. Todo lo que dice acá está respaldado por código
en este repo; nada de esto vende alfa de trading.

---

## Pitch de 15 segundos

**ES**
> Construí un motor de decisiones que no miente sobre su estado: cada transición
> queda en una bitácora append-only, reejecutar un run no duplica nada, y cualquier
> run se retoma exacto desde su último checkpoint. Corre en tres segundos con un
> comando.

**EN**
> I built a decision engine that doesn't lie about its own state: every transition
> lands in an append-only ledger, re-running is idempotent, and any run resumes
> exactly from its last checkpoint. One command, three seconds.

---

## Pitch de 60 segundos

**ES**

> Un pipeline que corre por horas y se cae a la mitad deja tres preguntas sin
> responder: en qué estado quedó, si puedo reejecutarlo sin duplicar trabajo, y si
> puedo demostrar después por qué decidió lo que decidió. La respuesta habitual son
> logs sueltos y un reinicio desde cero.
>
> El Decision Resilience Engine es mi respuesta a esas tres preguntas, construida en
> chico. La máquina de estados vive en una tabla de 21 transiciones: una transición
> no declarada lanza una excepción en vez de caer a un default. Cada transición
> escribe un evento de auditoría y un checkpoint en SQLite. La idempotencia se define
> por el par `(run_id, data_hash)`: reenviar el mismo run no duplica nada, y el mismo
> `run_id` con otros datos devuelve un HTTP 409 tipado con instrucciones de
> recuperación, en vez de sobrescribir en silencio.
>
> Lo que más me interesa mostrar no es el motor, es cómo lo verifico. Los tests no
> chequean que el camino feliz termine bien: chequean que la bitácora esté encadenada,
> que el `resume` devuelva el contexto idéntico campo por campo, y que la máquina de
> estados no tenga estados inalcanzables — validada como grafo. Hay un test que falla
> si la documentación de contratos se desincroniza del código.
>
> Encima del motor hay un laboratorio cuantitativo de backtesting que se conecta como
> comando de medición. Es el banco de pruebas, no el producto: no vendo estrategias,
> vendo sistemas que se pueden auditar.
>
> Y el repo incluye una auditoría que lo critica: qué está implementado, qué está solo
> diseñado, y dónde el documento de arquitectura prometía más de lo que el código
> entrega.

**EN**

> A pipeline that runs for hours and dies halfway leaves three questions unanswered:
> what state was it in, can I re-run it without duplicating work, and can I prove
> afterwards why it decided what it decided. The usual answer is scattered logs and a
> restart from zero.
>
> The Decision Resilience Engine is my answer to those three, built small. The state
> machine is a table of 21 transitions: an undeclared transition raises instead of
> falling through to a default. Every transition writes one audit event and one
> checkpoint to SQLite. Idempotency is keyed on `(run_id, data_hash)`: resubmitting a
> run duplicates nothing, and the same `run_id` with different data returns a typed
> HTTP 409 with recovery instructions rather than silently overwriting.
>
> What I care about showing isn't the engine — it's how I verify it. The tests don't
> check that the happy path ends well: they check that the audit log is *chained*,
> that `resume` returns the identical context field by field, and that the FSM has no
> unreachable states, validated as a graph. One test fails if the contract
> documentation drifts from the code.
>
> On top of it sits a quantitative backtesting lab wired in as a measurement command.
> That's the bench, not the product: I'm not selling strategies, I'm selling systems
> that can be audited.
>
> And the repo ships an audit that criticizes itself: what's implemented, what's only
> designed, and where the architecture document promised more than the code delivers.

---

## 5 bullets para LinkedIn / CV

Redactados para que cada uno sea verificable abriendo el repo.

- Diseñé e implementé un motor de orquestación con **máquina de estados en tabla
  (21 transiciones, 16 estados)** donde una transición no declarada falla fuerte en
  lugar de degradar a un estado por defecto.
- Implementé **gobernanza append-only sobre SQLite** con idempotencia por
  `(run_id, data_hash)` y error tipado HTTP 409 ante colisión, más **checkpoint por
  transición** con `resume` verificado campo por campo contra el contexto original.
- Escribí **tests de invariantes, no de humo**: bitácora encadenada, resume idéntico,
  y la FSM validada como grafo (sin estados inalcanzables, un solo estado absorbente).
- Cerré la deriva entre documentación y código con un **test que falla si el ICD deja
  de ser copia literal de los contratos Pydantic**, más guardas de CI contra diagramas
  Mermaid que no renderizan y contra regresiones del entrypoint de la demo.
- Construí un **laboratorio de backtesting reproducible** (futuros BTC/ETH, funding,
  ventanas deslizantes, validación walk-forward con `--holdout-frac`) integrado al
  motor como *measurement command*, con dataset sintético generado por script y seeds
  explícitos.

---

## 3 preguntas de entrevista y las respuestas honestas

### 1. "¿Esto está en producción? ¿Cuántos usuarios tiene?"

**No, y no tiene usuarios.** Es un repo de portfolio con cero estrellas y un solo
autor. La API no tiene autenticación, escucha en `127.0.0.1` y es un servidor de
desarrollo; el backend Redis nunca corrió contra un Redis real, solo contra
`fakeredis`; y los SLAs de latencia que aparecen en el documento de arquitectura
nunca se midieron.

Lo que sí puedo defender es el criterio: las decisiones de diseño —FSM en tabla,
idempotencia por `(run_id, data_hash)` en vez de timestamp, resume verificado campo
por campo— son las mismas que tomaría en un sistema con tráfico, y están testeadas.
El repo tiene un `AUDIT.md` donde yo mismo marco qué es MVP y qué es diseño, con una
tabla de "diseñado pero no implementado".

### 2. "El documento de arquitectura habla de copulas, KDE con FFT y DoWhy. ¿Dónde está ese código?"

**No existe, y es la crítica correcta.** Ese documento es un diseño objetivo, no un
reporte de estado, y durante un tiempo no lo decía en ningún lado visible — la única
aclaración estaba al final del archivo, en cursiva. Hoy tiene un banner al inicio
que enumera qué no está implementado.

Lo que hay es deliberadamente *lite* y está nombrado así: `forecasting` es un test
de Kolmogórov–Smirnov contra una normal ajustada (el propio código devuelve
`kind: "univariate_gaussian_proxy"`); `causal` es solapamiento de histogramas 1-D
con un gate en 0.6, que no es inferencia causal y no calcula ningún ATE. Escribir
"proxy" donde es un proxy me parece más defendible que implementar mal una copula
para poder decir la palabra.

La versión larga: el riesgo de un documento de diseño ambicioso es que se lea como
inventario. La mitigación que elegí fue un mapa componente → archivo → test, y una
sección de brechas conocidas que incluye cosas incómodas, como que el *append-only*
del ledger es una convención del código y no una garantía de la base de datos.

### 3. "¿Cuál es la debilidad más grande del repo hoy?"

**Dos, y las tengo priorizadas.**

La primera: `compound_optimize_runner.py` y `scripts/optimize_signal_grid.py` suman
unas 1370 líneas —la mitad del repo— y **no tienen tests unitarios**. La única
cobertura es un smoke de CI que verifica que el JSON de salida tenga dos claves. Es
el P1-5 del `AUDIT.md`, con el plan escrito: tests sobre las funciones puras
(`ema`, `sma`, `calc_indicators`) y una propiedad de `sim_window`.

La segunda: cuatro componentes —`backprop`, `drift`, `override` y el propio puente
al laboratorio MAT— existen, están testeados aisladamente, y **ningún recorrido del
pipeline los invoca**. Son bibliotecas correctas, no partes del motor en ejecución.
La FSM declara las ramas `BACKPROP` y `ESCALATED`, pero los dos caminos implementados
van siempre por `STRESS_PASS`. El arreglo está identificado (P2-4): un tercer
recorrido que ejercite el fallo de stress e incremente `iteration_count`, que hoy es
otro campo del contrato que nunca cambia de valor.

---

## Cómo no vender esto

Tres cosas que **no** digo de este repo, y por qué:

| No decir | Por qué |
|---|---|
| "Sistema de trading" o cualquier cosa con alfa | El MAT mide probabilidad de ruina sobre datos sintéticos; la corrida por defecto da `p_win_terminal = 0.0`. Vender alfa acá es mentir y además es fácil de desmentir. |
| "Enterprise-grade", "production-ready", "AI-powered" | Sin auth, sin usuarios, sin métricas de latencia. El primer revisor que abra `dre/api/app.py` lo nota en treinta segundos. |
| "Motor de inferencia causal" | Son 25 líneas de solapamiento de histogramas. El nombre del archivo ya es generoso. |
