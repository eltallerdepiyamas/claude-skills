# ledfx_barrido

Rampa con halo que barre la pantalla LED (venía del test de pantallas de Little Jesus como "glow").

Página **Barrido**: Forma (línea diagonal · círculo · barra horizontal · barra vertical) · Velocidad · Intensidad · Tinta (Color A / Color B de la paleta, o Blanco) · Recorre (tableros en línea, como cuelgan / imagen del mapeo).

Sirve como efecto y como prueba de movimiento: si la rampa brinca entre dos tableros, están en orden cambiado. Para medir píxeles, apagarlo.

## v2 (2026-11-20): segunda capa sobre los slices

Se instala en **`led_slices`** si existe y si no en la LED de `led_salida` (`proyecto.json → "ledfx": {"en": "led"}` la fuerza a la LED). En slices, **Recorre**: *Tableros / slices en línea* = la rampa pasa de un slice al siguiente en el orden del XML (si una fila del XML va de derecha a izquierda, ahí la rampa también); *Imagen completa* = cruza la pantalla como se ve. Al pasar de la LED a slices trae los valores que tenía.

## v2.1 (2026-11-20): al beat

Sección **Ritmo**: **Libre** (usa Velocidad) · **Al tiempo** (una pasada exacta por beat, BPM detectado) · **Al compás** (una por compás) · **Disparado por el kick** (cada kick, o cada N, lanza una pasada que dura dos tiempos) · Una pasada cada N · Umbral del kick · **Brillo sigue la energía** (graves + kick).
