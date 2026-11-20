# ledfx_cascada

**Cascada de tiempo**: cada bocina enseña el visual unos cuadros después que la anterior, así el movimiento corre de bocina en bocina como un eco (time glitch ordenado). Segunda capa.

Página **Cascada**:
- **CASCADA DE TIEMPO**: prendida · El retraso va: en orden (A-1 sin retraso, la última la más atrasada) · del centro a los extremos · de los extremos al centro · al azar (fijo).
- **CÓMO SE VE**: Cuadros entre bocinas (1-4) · Mezcla (0 vivo, 1 todo eco).

Cómo: `cascada_hist` (Texture 3D con los últimos cuadros de la salida de slices) → `cascada_tiempo` (Time Machine con `cascada_mapa`: cuánto atrás mira cada bocina) → `cascada_led`. **Va primero en la cadena** (orden 5): el eco es del visual limpio y los demás efectos van encima sin retraso. Memoria: (bocinas − 1) × cuadros + 2 cuadros de la salida; con 12 bocinas y 2 cuadros, 24 cuadros de 1920×1080 (~200 MB de GPU). Apagado guarda solo 2 cuadros. Probado: A-1 = el vivo, el retraso crece hasta la última.
