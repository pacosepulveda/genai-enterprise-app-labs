# M06-P03 — Tool Calling & Enterprise Data

En esta práctica el asistente deja de limitarse a recuperar documentación y empieza a consultar datos empresariales estructurados mediante **tool calling real** con Bedrock Converse.

## Objetivos

- inspeccionar una base SQLite empresarial local y persistente;
- diferenciar conocimiento del modelo y datos obtenidos mediante herramientas;
- ejecutar tools Python de solo lectura sobre `data/enterprise.db`;
- observar `toolUse`, argumentos, resultados y segundo turno del modelo;
- comprobar cómo el LLM decide qué herramientas necesita;
- mantener una traza completa de tool calls y uso de tokens;
- evolucionar la superficie `Investigate`.

## Notebook

Abrir:

```text
labs/M06/P03/tool_calling_enterprise_data.ipynb
```

Kernel:

```text
Python (GenAI Course)
```

## Base de datos

La práctica usa:

```text
data/enterprise.db
```

El fichero se genera localmente con:

```bash
python scripts/init_database.py
```

La base contiene datos ficticios pero persistentes de:

```text
customers
services
contracts
service_status
incidents
```

No se permite SQL arbitrario generado por el LLM. Las herramientas usan consultas parametrizadas y una conexión SQLite de solo lectura.

## Tools disponibles

```text
get_service_status(service_name)
get_open_incidents(customer_name, service_name)
get_contract_sla(customer_name, service_name)
```

## Flujo

```text
pregunta
→ Bedrock Converse
→ toolUse
→ Python ejecuta una tool permitida
→ SQLite
→ toolResult
→ Bedrock Converse
→ respuesta final
```

## Integración

Después del notebook:

```bash
streamlit run app/Home.py
```

La página `Investigate` permite ejecutar el mismo flujo y abrir la caja para inspeccionar tools, argumentos y resultados.