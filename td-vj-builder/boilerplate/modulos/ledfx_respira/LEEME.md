# ledfx_respira

**Respiración**: la luz de las bocinas sube y baja con el compás (BPM detectado). Pulso sin strobe. Segunda capa, al final de la cadena (orden 50).

Página **Respira**:
- **RESPIRACIÓN**: prendida · Forma: **Suave** (sube y baja en curva) · **Latido** (sube en el 1 con un ataque del 5 % y se va apagando) · **Ola** (la respiración corre de bocina en bocina: un ciclo cruza todas).
- **RITMO Y NIVEL**: un ciclo cada N tiempos (4 = un compás) · Fondo (lo más bajo que llega).

Sin `audio_tempo` usa 120 BPM. En SOLO EFECTOS el color de fondo respira. Apagado por default. Entra solo a `auto_capa`.
