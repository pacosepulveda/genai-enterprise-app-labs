# Criterios de diseño de las prácticas

Estos criterios son requisitos del curso, no recomendaciones opcionales.

1. **IA real por defecto.** Bedrock se usa de verdad para LLM, embeddings y generación cuando la práctica lo requiere.
2. **El alumno no escribe código por rutina.** El código se entrega preparado, comentado y ejecutable. El alumno lee, ejecuta, inspecciona y modifica pequeñas partes deliberadas.
3. **Escribir código debe tener una razón didáctica.** Los huecos de implementación se reservan para casos donde escribir unas pocas líneas ayuda a comprender el concepto.
4. **Cada práctica produce algo observable.** Una predicción, una visualización, una respuesta, una imagen, un retrieval, una traza o una métrica.
5. **Interfaz adecuada al concepto.** Jupyter para experimentar, Streamlit para interactuar/visualizar y CLI para ejecutar o inspeccionar cuando aporta conocimiento.
6. **La GUI también explica.** Retrieval, chunks, structured output, tool calls, estado de LangGraph y métricas deben hacerse visibles cuando sea útil.
7. **CLI sin fricción innecesaria.** Codespaces instala dependencias, prepara datos y ofrece tareas de VS Code para operaciones repetitivas.
8. **Ruta principal accesible.** Un alumno con poca experiencia en desarrollo debe poder completar la práctica siguiendo la guía.
9. **Ampliación para perfiles avanzados.** Los retos opcionales profundizan sin bloquear la ruta principal.
10. **Problema antes que patrón.** Primero se observa la limitación; después se introduce Pydantic, LangChain, LangGraph, evaluación o un control de seguridad.
11. **Abstracciones transparentes.** Siempre que sea posible se puede abrir la caja para ver prompts, contexto, documentos recuperados, tool calls y estado.
12. **Realista, no production-ready.** El prototipo se parece a una aplicación empresarial sin introducir infraestructura que no sea necesaria para aprender GenAI.
13. **Mocks solo con justificación explícita.** Los servicios de IA no se simulan. Los sistemas corporativos inexistentes se representan con datos/servicios locales reales.
14. **Los tests sirven al producto.** Se prueban componentes cuando la prueba ayuda a comprender fiabilidad, evaluación o regresión; pasar tests no es el objetivo principal de una práctica.
