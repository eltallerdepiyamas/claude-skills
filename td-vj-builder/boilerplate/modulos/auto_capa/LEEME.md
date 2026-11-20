# auto_capa

**Alterna sola la segunda capa** (los efectos que van encima del visual: chaser, barrido y los `ledfx_*` que se agreguen), como el piloto alterna los visuales.

Página **Capa** (en `/project1/slices`, pestaña SLICES de la UI; sin slices, en `/project1/led`):

- **ALTERNAR EFECTOS**: prendido (apagado por default) · Siguiente ya.
- **RITMO**: cada **N compases** con el BPM detectado (`audio_tempo`: el cambio cae en el 1 del compás) o cada **N segundos** (esperando el kick, máximo 1 s). Sin `audio_tempo`, usa segundos.
- **QUÉ ALTERNA**: incluir cada efecto instalado (chaser, barrido, EQ, onda, cascada) · combinaciones de dos · solo el visual · **variar** (cada vez que entra un efecto le cambia el patrón del chaser o la forma del barrido). Nunca repite la opción anterior.
- **Solo efectos** (con `led_slices`): incluir · qué tan seguido (0-1, default 0.3). En esos cambios QUÉ SALE pasa a solo efectos (sobre color); nunca con cascada o giro, que necesitan visual. Los demás cambios regresan a visual + efectos.
- **LECTURA**: lo que está ahora.

Log: `control/capa_log.txt`. Requiere al menos un efecto (`ledfx_chaser` o `ledfx_barrido`). Un efecto nuevo entra solo si su TOP lleva tag `ledfx` y `store('on_par', ...)` (opcional `store('var_par', ...)` para variarlo).
