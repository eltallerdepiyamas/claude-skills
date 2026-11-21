# audio_auto — micro <-> canción solo

El micro (`/project2/audio/audio_vivo`) escucha **siempre**. Con **Cambio automático** prendido (página Audio de `show`, sección CAMBIO AUTOMÁTICO MICRO / CANCIÓN, o pestaña AUDIO del cel):

| Fuente ahora | Condición | Cambia a |
|---|---|---|
| CANCIÓN (archivo) | nivel del micro **arriba** de *Pasa a MICRO arriba de* (0.05) durante *durante (s)* (1.5) | EN VIVO |
| MICRO (en vivo) | nivel del micro **abajo** de *Regresa a CANCIÓN abajo de* (0.015) durante *durante (s)* (10) | ARCHIVO |

- Dos umbrales (histéresis; el de bajar siempre queda bajo el de subir) y dos tiempos: un golpe suelto o un hueco de la rola no lo hacen brincar.
- Nivel del micro = pico de la entrada **cruda** (antes del Gain), sube al instante y cae suave (0.35 s). Se lee en `Audioautonivel` y en el cel (barra con las dos marcas: ámbar = pasa a micro, azul = regresa a canción). Calibrar en sitio: ver el nivel con el lugar en silencio y con música, y poner los umbrales entre los dos.
- **CALIBRAR CON EL AMBIENTE** (pulso `Audioautocalibrar`, botón en el cel): mide 10 s lo que suena *cuando el escenario de enfrente NO toca* (lo que llega de lejos) y pone *Regresa a CANCIÓN* = ambiente (p90) × 1.15 y *Pasa a MICRO* = ambiente × 1.6. En festival el ambiente no es silencio: en Corona Capital marcó p90 0.238 → canción < 0.274, micro > 0.381.
- Festival (casi siempre micro, la canción solo de respaldo): *durante* corto para subir (1 s) y largo para bajar (20 s).
- Cada minuto el log anota min / mediana / p90 del micro y la fuente: sirve para afinar después del show.
- Elegir la fuente a mano (hub, UI o cel) **apaga** el automático.
- Cada cambio sale en AVISOS del cel (y por ntfy si Avisos está prendido) y en `control/audio_auto_log.txt`.
- Apagado por default. Prueba sin tocar la fuente real: `control/probar_audio_auto.py` (simulacro con niveles falsos).

Instalar: `instalar.py` (requiere la cadena de `setup_show.py`: `audio_vivo`, `audio_fuente`). Desinstalar: `desinstalar.py`.
