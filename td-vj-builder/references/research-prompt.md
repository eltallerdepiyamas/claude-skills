# Prompt de investigación de proyecto

Este es el prompt que el usuario corre en Claude o ChatGPT (con búsqueda web) para
investigar un artista/show y producir el brief `.md` que este skill consume. Está
afinado para que el research entregue los efectos **ya pensados en el contrato de
5 slots por rol**, de modo que el skill no tenga que adivinar. El research es 100%
dirección creativa; la plomería de TouchDesigner la hace el skill.

Entrega este archivo al usuario cuando pida "el prompt de research" o cuando no tenga
un brief. El usuario rellena `[ARTISTA]`, `[FESTIVAL/VENUE]`, `[FECHA]`, `[HORARIO]`.

---

```
Actúa como director de visuales e investigador para un show en vivo. Voy a hacer
VJing con cámara en vivo en TouchDesigner y necesito que investigues al artista y
me entregues un brief en Markdown que luego cargo en mi herramienta de construcción.

ARTISTA / SHOW: [ARTISTA] — [FESTIVAL o VENUE], [FECHA], [HORARIO si lo sabes]

Investiga fuentes públicas verificables (biografía oficial, videoclips, arte de
giras, entrevistas, line-up del festival) y dedúce la dirección visual. NO inventes
datos; si algo no se puede verificar, márcalo como inferencia.

Mi sistema NO hace full-screen visuals genéricos. Hace tres cosas:
  1. VISUALES generativos (fondos/contenido, pueden ser audio-reactivos)
  2. EFECTOS DE CÁMARA sobre video en vivo (la cara y el cuerpo deben seguir legibles)
  3. LAYOUTS de múltiples cámaras (modos de vista cuando uso 2+ cámaras)

Entrégame UN archivo Markdown con EXACTAMENTE estas secciones y nada más:

# PROYECTO: [ARTISTA]

## 1. Meta del show
- Fecha, venue, horario, duración estimada
- Luz ambiente (diurno/nocturno/interior) y qué implica para legibilidad
- Tono emocional en 3-5 palabras

## 2. Dirección visual
- Paleta (colores concretos en hex o nombre)
- 4-8 referencias estéticas (de qué época/video/arte salen) y qué extraer de cada una
- Qué EVITAR

## 3. Contexto de cámara
- ¿Cuántas cámaras se esperan? ¿Retrato, plano abierto, o mezcla?
- Restricciones de legibilidad (qué NO se debe tapar)

## 4. Audio
- Banda dominante esperada (low / mid / high) y por qué
- Carácter de la reactividad: ¿pulso de beat, o respiración lenta?

## 5. Qué crear

### Visuales (0 a 16)
Por cada uno: Nombre | mood en una línea | ¿generativo puro o mezcla con input de video?

### Efectos de cámara (los que propongas)
Por cada efecto entrega EXACTAMENTE 5 parámetros expresivos, en este ORDEN DE ROL:
  1. Intensidad / cantidad del efecto
  2. Velocidad / tiempo
  3. Distorsión / deformación espacial
  4. Color / cromática
  5. Firma (lo más característico de ESE efecto)
Formato por efecto:
  - Nombre | esencia en 2 líneas | ¿usa feedback? sí/no
  - Los 5 params: nombre del parámetro + rango real (ej. Feedbackamt 0.0–0.99)
  - Mapeo de audio sugerido: a cuál de los 5 lo empuja la banda (low/mid/high)
  - ¿Seguro para retrato? ¿mejor en plano abierto?

### Layouts de cámara (los que propongas)
Por cada uno: Nombre | nº de cámaras | concepto de la vista en una línea

## 6. Prioridad de uso
- Cuáles son "look base" continuos y cuáles son "acentos" puntuales
- Orden sugerido durante el show (intro / verso / pre-coro / coro / balada / transición)

REGLAS:
- Máximo 5 parámetros por efecto, siempre en el orden de rol de arriba. Si un efecto
  no tiene parámetro de color, usa en el slot 4 el siguiente más expresivo y anótalo.
- Da rangos reales, no normalizados 0-1 (eso lo maneja mi sistema).
- No escribas código GLSL ni nodos de TouchDesigner. Solo dirección + parámetros.
- Español, conciso, sin relleno.
```

---

## Cómo lee el skill este brief

- **§1–§4** fijan mood/paleta/cámara/audio → guían el estilo del shader y los defaults
  de la página Audio (qué banda viene activa por defecto).
- **§5 Visuales** → cuántos crear (1→16) y, por cada uno, si el builder usa input
  (`GENERATIVE_ONLY = False`) o no.
- **§5 Efectos** → cada efecto ya trae sus 5 params en orden de rol con rangos reales:
  van directo a `FIVE_SLOTS` del `effect_builder.py`. El mapeo de audio sugiere el
  default de `Audiotarget` y qué bandas encender.
- **§5 Layouts** → nombre + nº de cámaras → `layout_builder.py`.
- **§6** → se archiva en `projects/` como guía de uso en vivo.

Si el brief no respeta el formato (p. ej. da 8 params a un efecto), el skill recorta a
los 5 más expresivos en orden de rol y lo anota en `LEARNINGS.md`.
