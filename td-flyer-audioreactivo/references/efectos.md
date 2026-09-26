# Catálogo de efectos — flyer audioreactivo

Elige según lo que el flyer ya pide; no metas todos. Para cada efecto: qué hace,
cuándo encaja, cómo se arma en TD y a qué banda de audio conviene amarrarlo.
Los tres primeros vienen ya armados en `templates/flyer_builder.py`.

## boil (incluido)
Anima un dibujo fijo haciéndolo "respirar" cuadro a cuadro: un ruido suave que
evoluciona lento deforma la imagen. Es el efecto de mayor impacto / menor esfuerzo
para ilustración hecha a mano.
- **Cuándo:** casi siempre como base, sobre todo en flyers con linework / estética dibujada.
- **TD:** Noise TOP (monochrome, animado en círculo con `math.cos/sin` para que loopee)
  → Displace TOP (input0 = imagen, input1 = ruido).
- **Audio:** medios (el cuerpo de la música) empujando el peso del displace. Sutil.

## feedback / estela (incluido)
Deja rastros del frame anterior, acumulando eco. Extiende trazos de movimiento que
el flyer ya insinúe (líneas de trayectoria, giros).
- **Cuándo:** hay movimiento implícito (deportes, baile, discos girando, trails dibujados).
- **TD:** Feedback TOP (Target TOP = el composite del loop, input vacío) → Transform
  (zoom/giro) → Level (decay <1) → Composite (Over) de vuelta. 16-bit float.
- **Audio:** graves (kick) pulsando el zoom de la estela. `Trailzoom` >1 = eco afuera, <1 = túnel.
- **Cuidado:** decay alto + zoom alto se quema a blanco. No cierra loop perfecto (ver loop-vs-vivo).

## chroma split / aberración RGB (incluido)
Separa los canales R/B unos pixeles a lo largo de un ángulo que bambolea. Hereda el
lenguaje de un logo con tratamiento CRT/desplazado.
- **Cuándo:** el logo o tipografía ya trae rojo/eco desplazado; estética punk/glitch/print.
- **TD:** GLSL TOP (`library/shaders/chroma_split.glsl`). Loop-safe vía seno del tiempo.
- **Audio:** agudos (hats/crash) abriendo el split. Puede ir agresivo.

## halftone / dither (no incluido — añadir si aplica)
Trama de puntos / medios tonos animada. Mantiene el look de impresión cutre/fanzine en movimiento.
- **Cuándo:** flyers a 1–2 tintas, estética risográfica o fotocopia.
- **TD:** GLSL TOP (patrón de puntos por luminancia) o composición con un Circle/Ramp + Multiply.
- **Audio:** medios o el master controlando el tamaño del punto.

## threshold wobble (no incluido — añadir si aplica)
Recorta a alto contraste (dos tintas duras) y hace temblar el umbral. Conserva el contraste
del flyer mientras se mueve.
- **Cuándo:** piezas de alto contraste donde quieres movimiento sin perder la dureza gráfica.
- **TD:** Threshold TOP (o Level con curva dura) con el umbral animado por ruido/audio.
- **Audio:** cualquier banda moviendo el umbral; bonito con graves.

## slit-scan / time displacement (avanzado — no incluido)
Deforma según el movimiento acumulado; look líquido/derretido sin glitch barato.
- **Cuándo:** quieres algo más orgánico que el boil, piezas más "art".
- **TD:** combinación de Feedback + Displace usando el frame previo como mapa.
- **Audio:** graves para la cantidad de derretido.

---

## Mapa de bandas (punto de partida)
- **Low (graves/kick):** pulsos grandes — zoom de estela, escala global, derretido.
- **Mid (cuerpo):** deformación del boil, tamaño de halftone.
- **High (hats/aire):** chroma split, detalle fino, parpadeos breves.

Mantén la respuesta suave (el lag del audio ayuda): "respiración", no trigger 1:1 con el beat.
