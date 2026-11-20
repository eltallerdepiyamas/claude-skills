# ledfx_giro

**Giro por bocina**: cada bocina gira su contenido sobre su centro, como 12 discos. Segunda capa (gira el visual: va después de la cascada y antes del chaser, orden 7).

Página **Giro**:
- **GIRO POR BOCINA**: prendido · Cómo giran: **Todas igual** · **Alternado** (una a la derecha, la siguiente a la izquierda) · **Ola** (desfasadas: el giro corre por las bocinas) · **Un paso por kick** (cada kick las gira un paso con un movimiento suave de 0.3 s) · **Recorte circular** (lo de fuera del círculo de la bocina va a negro: no se ven esquinas girando; ideal para el sello).
- **RITMO**: Velocidad (vueltas por compás, con el BPM detectado; sin tempo 120 BPM) · Paso por kick (0.125 = 45°) · Umbral del kick.

El tamaño de cada bocina lo saca del índice de `led_slices` (no hace falta saber las medidas). En SOLO EFECTOS no hace nada (gira imágenes). Apagado por default. Entra solo a `auto_capa`.
