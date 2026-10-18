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
