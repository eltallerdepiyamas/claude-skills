# ledfx_chaser

Idea del Chaser de Resolume: cada tablero tiene una luz que prende y se apaga encima del visual, en secuencia.

Página **Chaser**: Patrón (corrida · ida y vuelta · centro → afuera · afuera → centro · pares / impares · aleatorio · acumular · todos) · Avanza con (BPM detectado · kick · BPM fijo) · Cada N · Umbral del kick · Ancho · Decaimiento · Ataque (mínimo contra strobe) · Fondo (nivel de lo apagado).

Sirve para cualquier cuadrícula de `led_mapeo`. Con `audio_tempo` sigue el ritmo también en los breaks.
