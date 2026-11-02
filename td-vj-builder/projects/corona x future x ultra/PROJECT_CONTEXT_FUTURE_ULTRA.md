# PROJECT_CONTEXT — Future + Ultra 2026

> Documento de transferencia de contexto para Claude / Claude Code. Estado: 15 de octubre de 2026. Distingue decisiones confirmadas, propuestas y pendientes.

## Identidad y responsable

- **Estudio / marca comercial:** El Taller de Piyamas.
- **Responsable creativo y técnico:** Sebastián Díaz.
- **No usar Equipo Abierto** como identidad comercial de este proyecto.

## Objetivo

Desarrollar y operar un sistema audiovisual **generativo y audio-reactivo en tiempo real** para dos festivales de música electrónica: **Future Festival (7–8 de noviembre de 2026; montaje previsto el 6)** y **Ultra (13 de noviembre de 2026; montaje previsto el 13)**. Las fechas proceden de la información discutida y deben reconfirmarse con producción.

El sistema se implementará en **TouchDesigner**, con **Claude Code** como apoyo para programar, iterar y documentar. No se plantea entregar únicamente animaciones pre-renderizadas.

## Superficies / contenido

1. **Pantalla central:** visuales generativos originales y audio-reactivos.
2. **Pantallas laterales:** integrar assets de marca suministrados por el cliente y procesarlos con efectos en tiempo real, preservando legibilidad.
3. **Truss / asteras:** posibilidad exploratoria de video mapping; **no está confirmado** como alcance definitivo.

Dirección estética inicial: **techno industrial**, geometría abstracta, interferencia, distorsión, texturas metálicas, feedback y alto contraste. No hay renders definitivos ni moodboard aprobado.

## Arquitectura técnica propuesta (no implementada aún)

- `Audio Engine`: captura y análisis de señal; bandas graves, medias y agudas, energía, transitorios y smoothing.
- `Visual Engine`: escenas generativas modulares, preferentemente GPU/GLSL cuando convenga.
- `FX Engine`: distorsión, feedback, glitch y modulaciones.
- `Brand Layer`: assets de marca independientes de los efectos.
- `Control Interface`: escenas, presets, intensidad, sensibilidad, bypass y recuperación rápida.
- `Output Manager`: composición y mapeo hacia las superficies LED.

**Principio de diseño:** un solo motor visual reutilizable para ambos festivales, con composiciones y configuraciones de salida adaptables. No asumir que cada superficie exige una salida física independiente.

## Equipo y operación

- Sebastián **proporcionará una sola laptop** con varias salidas de video y se contempla operación durante los festivales.
- Falta validar modelo, GPU, VRAM, adaptadores, licencia TouchDesigner, número de salidas simultáneas y resoluciones.
- Falta confirmar quién suministra procesadores LED, distribución de señales, cableado y audio de entrada.
- Se requiere prueba de rendimiento a la resolución real y plan de contingencia, especialmente por operar con una sola computadora.
- Hay un compromiso personal de Sebastián con el aniversario de **Punto Ácido** que podría coincidir; alternativas: pagar a alguien para cubrir ese compromiso o delegar la operación del festival. Es una decisión interna, no un concepto a exponer al cliente.

## Alcance económico discutido

**Cotización de referencia acordada en la conversación:** **$85,000 MXN + IVA** (total aritmético con IVA del 16%: **$98,600 MXN**), bajo El Taller de Piyamas.

Desglose interno preliminar, no necesariamente para mostrar al cliente:

| Concepto | MXN |
|---|---:|
| Concepto creativo y moodboard | 5,000 |
| Desarrollo generativo TouchDesigner | 25,000 |
| Audio-reactividad y adaptación de pantallas | 12,000 |
| Pruebas y optimización | 5,000 |
| Renta de laptop para ambos festivales | 8,000 |
| Operación técnica (5 jornadas estimadas) | 22,500 |
| Adaptación entre festivales | 5,000 |
| **Total** | **82,500** |

**Nota:** El desglose suma $82,500; los $2,500 restantes hasta la cotización comercial de $85,000 pueden tratarse como margen de contingencia / coordinación. No confundir ambos importes.

- Se discutió un precio de salida de $85,000, con posibilidad de negociar alrededor de $75,000 **solo si se reduce el alcance**.
- Viáticos, traslados, hospedaje, alimentación, hardware LED, procesadores y cambios importantes de alcance: fuera del monto salvo acuerdo explícito.
- Operación estimada en cinco jornadas: **confirmar** con horarios y montaje reales.
- Como antecedente comercial, Sebastián recuerda Casa Bacardí en torno a $30,000 para una etapa de desarrollo; otras cifras mencionadas durante la conversación no han sido verificadas documentalmente. No usarlas como hechos firmes.
- Condiciones de pago propuestas: 70% de anticipo y 30% antes del primer montaje; **no consta aceptación del cliente**.

## Estado y pendientes

**Confirmado por Sebastián:** tiempo real, TouchDesigner, Claude Code, una laptop con varias salidas, equipo propio, operación contemplada, identidad El Taller de Piyamas.

**Pendiente de recibir / validar:**

- Renders, plano de escenario, dimensiones y **pixel map** de todas las superficies.
- Resoluciones, frecuencia de refresco, cantidad de señales, procesadores LED y rutas de distribución.
- Especificaciones de la laptop y capacidad de salida simultánea.
- Tipo de señal de audio (interfaz, línea, canal, nivel), ubicación FOH y latencia aceptable.
- Assets y lineamientos de marca; cantidad de escenas y presets.
- Confirmación de mapping en truss / asteras.
- Horarios de montaje, pruebas, operación y desmontaje de ambos festivales.
- Logística y ciudad de cada festival; traslados y hospedaje.
- Quién operará cada fecha y cobertura de Punto Ácido.
- Aprobación de presupuesto, facturación, IVA y condiciones comerciales.

## Plan de desarrollo sugerido

1. **MVP:** capturar audio y generar una composición visual con tres bandas, smoothing, controles de sensibilidad e intensidad.
2. **Motor visual:** crear escenas y efectos reutilizables; separar generación, procesamiento y composición.
3. **Control en vivo:** presets, selección de escenas, bypass y fallback.
4. **Salidas:** simular pantallas con resoluciones de prueba; migrar al pixel map real cuando llegue.
5. **Integración y QA:** medir FPS, uso GPU/VRAM, estabilidad prolongada, recuperación de fallos y pruebas con audio real.

## Instrucciones para Claude Code

Actúa como desarrollador senior de TouchDesigner, Python, GLSL y sistemas audiovisuales para shows en vivo. Lee este archivo como fuente de contexto, pero no supongas que las propuestas están aprobadas o implementadas. Antes de escribir un parche complejo:

1. Resume arquitectura de componentes/nodos y dependencias.
2. Señala supuestos y riesgos de la laptop con múltiples salidas.
3. Propón un MVP ejecutable, verificable y medible.
4. Implementa por módulos, documenta parámetros y prueba cada etapa.
5. No inventes renders, pixel maps, especificaciones de equipo ni entregables pactados.

**Primera tarea recomendada:** diseñar el grafo de TouchDesigner para un MVP de audio-reactividad de tres bandas con una escena generativa y una interfaz mínima de control.
