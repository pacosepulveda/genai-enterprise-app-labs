# M06-P04 — LangGraph Enterprise Workflow

## Objetivo

Convertir la investigación de M06-P03 en un workflow empresarial explícito y observable con LangGraph.

El caso combina tres capacidades que ya existen en la aplicación:

1. **Datos empresariales estructurados** mediante tools read-only sobre `enterprise.db`.
2. **Conocimiento operativo** recuperado desde el corpus RAG.
3. **Generación con LLM** para producir un briefing y un borrador de comunicación.

La novedad es que ahora estas capacidades se coordinan con **estado, nodos, routing y aprobación humana**.

## Escenario

Asteria Retail reporta fallos de autenticación en Managed VPN. El workflow debe:

- consultar incidentes abiertos, estado del servicio y SLA;
- recuperar guía operativa relevante;
- construir un briefing basado en evidencia;
- aplicar una regla de negocio determinista;
- detenerse si el caso requiere revisión humana;
- permitir que una persona apruebe o rechace el borrador antes de finalizar.

## Flujo

```text
START
  ↓
collect_enterprise_data
  ↓
retrieve_operational_guidance
  ↓
build_incident_brief
  ↓
¿P1 o servicio degradado?
  ├─ no → finalize → END
  └─ sí
       ↓
   human_review
       ⏸ interrupt()
       ↓ Command(resume=...)
   finalize
       ↓
      END
```

## Utilidad empresarial

El objetivo no es crear un “agente autónomo” que actúe sin control. El valor está en reducir el tiempo necesario para reunir contexto disperso y presentar a un responsable humano un paquete de decisión coherente:

```text
datos operativos + contrato + runbook + síntesis + trazabilidad
```

El workflow **no envía mensajes ni modifica sistemas**. Prepara un borrador y exige aprobación humana en situaciones sensibles.

## Controles

- tools empresariales en modo read-only;
- sin SQL arbitrario;
- routing de aprobación calculado por la aplicación, no por el LLM;
- `interrupt()` de LangGraph para detener el workflow;
- `Command(resume=...)` para reanudarlo con la decisión humana;
- `InMemorySaver` solo para laboratorio; en producción se usaría persistencia durable;
- no se afirma incumplimiento de SLA porque la base solo contiene el objetivo contractual, no el tiempo real de respuesta.

## Archivos

- `langgraph_enterprise_workflow.ipynb`
- `src/enterprise_genai/workflow.py`
- `app/pages/4_Investigate.py`

## Resultado esperado

Para el caso por defecto, el workflow debería encontrar:

- incidente `INC-1043`, severidad P1;
- Managed VPN en estado `degraded`;
- SLA P1 de 30 minutos para Asteria Retail;
- documentación VPN relevante;
- un briefing y un borrador de actualización;
- una pausa real de LangGraph esperando aprobación humana.

Después de aprobar o rechazar, el mismo thread del workflow continúa desde el checkpoint y finaliza.

## Qué tiene que hacer el alumno

1. Continúa en `curso-m06` y asegúrate de que AWS SSO está activo.
2. Abre `langgraph_enterprise_workflow.ipynb` con **Python (GenAI Course)**.
3. Ejecuta el workflow hasta la interrupción y comprueba que aparece `Interrumpido: True`, `brief_ready` y una timeline que termina en `build_incident_brief`.
4. Antes de aprobar, revisa los datos empresariales, las fuentes RAG, el briefing, las acciones y las incertidumbres. Busca afirmaciones plausibles que no estén respaldadas.
5. Edita el borrador si es necesario y reanuda **el mismo `thread_id`** con la decisión humana; no vuelvas a lanzar la investigación desde cero.
6. Comprueba que el estado final incluye `human_review_approved` o `human_review_rejected` y `finalize`.
7. Arranca Streamlit, abre **Investigate → Workflow LangGraph (M06-P04)** y repite el recorrido visual: datos → RAG → briefing → pausa → revisión → reanudación.
8. Debes poder explicar qué son estado, nodo, edge, routing, checkpoint, `interrupt()` y `Command(resume=...)`, y por qué la regla de aprobación la controla la aplicación.
