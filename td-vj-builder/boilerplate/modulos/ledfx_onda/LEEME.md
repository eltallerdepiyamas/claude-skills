# ledfx_onda

**Onda de kick**: cada kick lanza un pulso de luz que corre de bocina en bocina y se apaga; se ve como el sonido viajando por las bocinas. Hasta 4 ondas a la vez. Segunda capa.

Página **Onda**:
- **ONDA DE KICK**: prendida · Recorre: en orden (A-1 → último) · del centro a los extremos · de los extremos al centro · ida y vuelta · **Lanzar una onda (prueba)**.
- **CÓMO SE VE**: **Luz** (halo en la tinta) o **Brillo** (solo aviva el visual donde pasa; lo demás en Fondo) · Tinta · Intensidad · Fondo.
- **RITMO Y FORMA**: una onda cada N kicks · Umbral del kick · Velocidad (bocinas / s) · Ancho (bocinas) · Se apaga en (s).

Kick = canal `kick` de `/project2/audio/master_audio`. Orden en la cadena 40. Va en `led_slices` (o `led_salida`). Apagado por default. Entra solo a `auto_capa`.
