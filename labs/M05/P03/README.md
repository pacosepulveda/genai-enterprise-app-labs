# M05-P03 — Enterprise Document Analyzer

Práctica para ampliar `Analyze` desde incidencias breves hacia documentos empresariales generales.

## Objetivos

- analizar correos, tickets y políticas con el mismo modelo de Bedrock usado en el curso;
- producir salida estructurada y validada con Pydantic;
- clasificar tipo de documento y categoría;
- extraer entidades con evidencia textual;
- separar hechos, acciones solicitadas y recomendaciones del modelo;
- conservar fechas/plazos sin inventar información ausente;
- mostrar incertidumbres y necesidad de revisión humana;
- integrar esta capacidad en la página `Analyze` de Enterprise GenAI Assistant.

## Datos de ejemplo

Los documentos de prueba están en:

```text
data/documents/m05_document_samples.json
```

Incluyen:

- un correo sobre renovación de certificado TLS;
- un ticket de acceso a una aplicación;
- un extracto de política de manejo de información.

## Notebook

Abrir:

```text
labs/M05/P03/enterprise_document_analyzer.ipynb
```

Kernel:

```text
Python (GenAI Course)
```

## Evolución de Analyze

La aplicación distingue dos usos:

```text
Incidencia
→ hechos / hipótesis / acciones / evidencia visual

Documento empresarial
→ resumen / clasificación / entidades / acciones / incertidumbres
```

La salida del modelo no se acepta como texto libre: se valida contra un JSON Schema derivado de Pydantic.

## Criterio importante

`requested_actions` contiene únicamente acciones que aparecen explícitamente solicitadas en el documento.

`recommended_actions` contiene propuestas del modelo y se muestra por separado para no presentarlas como hechos originales.

## Qué tiene que hacer el alumno

1. Continúa en `curso-m05` y renueva AWS SSO si fuese necesario.
2. Abre `enterprise_document_analyzer.ipynb` con **Python (GenAI Course)** y ejecuta los tres tipos de documento de ejemplo.
3. Para cada caso, compara `requested_actions` con `recommended_actions` y comprueba que las propuestas del modelo no se presentan como solicitudes originales.
4. Revisa entidades, hechos, fechas/plazos e incertidumbres y busca cualquier dato que no aparezca en el documento fuente.
5. Arranca `streamlit run app/Home.py`, abre **Analyze → Enterprise Document** y prueba al menos uno de los documentos desde la interfaz.
6. Considera la práctica completada cuando puedes explicar cómo una salida estructurada permite tratar correos, tickets y políticas con el mismo pipeline sin convertir recomendaciones en hechos.
