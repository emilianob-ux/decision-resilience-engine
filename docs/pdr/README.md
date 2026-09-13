# Paquete PDR — Decision Resilience Engine

**Sistema:** Decision Resilience Engine (DRE)  
**Versión PDR:** 1.0 · **Revisión:** lista para comité de ingeniería  
**Baseline:** especificaciones ecosystem v1.5–v1.8  

Este directorio contiene un **Preliminary Design Review (PDR)** en archivos independientes.

> **Qué es y qué no es.** Es un *ejercicio de ingeniería de sistemas* escrito por
> una sola persona: aplicar a un proyecto propio el formato de revisión (matriz
> de trazabilidad, ICD, registro de riesgos con RPN, plan de V&V, checklist
> Go/No-Go) que se usa en equipos grandes. **No hubo comité, ni aprobadores, ni
> firmas**: las tablas de roles del archivo `05` son la plantilla del formato,
> no un registro de aprobaciones reales. El estado real del código está en
> [DRE_IMPLEMENTATION_STATUS.md](../DRE_IMPLEMENTATION_STATUS.md) y en
> [`../../AUDIT.md`](../../AUDIT.md); la columna "Estado" de la matriz FR/NFR
> dice **Diseñado**, no **Implementado**, y eso es literal.

## Archivos

| Archivo | Descripción |
|---------|-------------|
| [01_Requirements_Traceability_Matrix.md](01_Requirements_Traceability_Matrix.md) | Matriz de trazabilidad FR/NFR → componentes y verificación. |
| [02_Interface_Contracts_ICD.md](02_Interface_Contracts_ICD.md) | Contratos de interfaz (ICD), payloads Pydantic y errores tipados. |
| [03_Risk_Register.md](03_Risk_Register.md) | Registro de riesgos, RPN, mitigaciones y owners. |
| [04_VV_Plan.md](04_VV_Plan.md) | Plan de verificación y validación (unitario → auditoría). |
| [05_PDR_Review_Checklist.md](05_PDR_Review_Checklist.md) | Checklist Go/No-Go, open issues, firmas. |

## Arquitectura técnica ampliada

Fundamentos matemáticos, diagramas Mermaid y stack de implementación: [**DRE_TECHNICAL_ARCHITECTURE.md**](../DRE_TECHNICAL_ARCHITECTURE.md) (v1.1, alineado con specs v1.5–v1.8).

## Relación con este repositorio (`decision-resilience-engine`)

- **`decision-resilience-engine`** (repo): núcleo de especificación e implementación **DRE**; el codigo **`dre/`** se ejecuta desde clon local / CI (no wheel PyPI).
- **MAT** en este repo = implementación del **simulador / medición** en dominio futuros compuesto (SQLite, métricas `p_ruin`, walk-forward, rejillas de señales), disponible como modulos en la wheel PyPI.
- Integración: el runner MAT actúa como **comando de medición** dentro del pipeline DRE (patrón “measurement.command”).

## Uso sugerido

1. Revisar los cinco archivos del PDR en orden numérico.
2. Cruzar con [DRE_TECHNICAL_ARCHITECTURE.md](../DRE_TECHNICAL_ARCHITECTURE.md) para diagramas y complejidades.
3. Archivar como `PDR_v1.0_APPROVED` tras firma de checklist `05`.
4. Avanzar a **CDR (Critical Design Review)** con diseño detallado por componente.
