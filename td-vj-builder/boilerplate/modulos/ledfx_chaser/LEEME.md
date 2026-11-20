# ledfx_chaser

Idea del Chaser de Resolume: cada tablero tiene una luz que prende y se apaga encima del visual, en secuencia.

Página **Chaser**: Patrón (corrida · ida y vuelta · centro → afuera · afuera → centro · pares / impares · aleatorio · acumular · todos) · Avanza con (BPM detectado · kick · BPM fijo) · Cada N · Umbral del kick · Ancho · Decaimiento · Ataque (mínimo contra strobe) · Fondo (nivel de lo apagado).

Sirve para cualquier cuadrícula de `led_mapeo`. Con `audio_tempo` sigue el ritmo también en los breaks.

## v2 (2026-11-20): segunda capa sobre los slices

Se instala donde haya salida: en **`led_slices`** si existe (va slice por slice, en el orden del XML de Resolume: A-1, A-2, …; el "Ancho" cuenta slices) y si no, en la LED de `led_salida` (tableros). `proyecto.json → "ledfx": {"en": "led"}` lo fuerza a la LED. Al pasar de la LED a slices trae los valores que tenía. La página Chaser queda en `/project1/slices` (pestaña SLICES de la UI).
