# ledfx_eq

**EQ de bocinas**: cada slice (o tablero) es una banda del espectro y se prende con ella. Con 12 bocinas = un ecualizador de 12 bandas a lo largo de la pantalla. Segunda capa, encima del visual.

Página **EQ**:
- **EQ DE BOCINAS**: prendido · Cómo se ve: **Brillo** (la bocina se prende con su banda; lo apagado queda en Fondo) · **Anillo** (aro de luz que crece desde el centro de la bocina) · **Nivel** (se llena de abajo hacia arriba, como un VU) · Bandas: graves → agudos en el orden del XML, al revés, o graves al centro.
- **CÓMO SE VE**: Fondo · Intensidad de la luz · Tinta (Color A / B de la paleta o blanco).
- **AUDIO**: Ganancia · Piso (debajo no prende) · Caída (s) · Audio (mono; default `/project2/audio/audio_gain`).

Cómo: Audio Spectrum logarítmico (128 puntos) → `eq_bandas` (Script CHOP) los junta en una banda por bocina, con **autonivel por banda** (los agudos también se mueven) y caída suave (sin parpadeo) → textura → `eq_led`. Orden en la cadena 30. Va en `led_slices` (o `led_salida`). Apagado por default. Entra solo a `auto_capa`.
