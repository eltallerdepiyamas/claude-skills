# audio_tempo

BPM del audio en vivo a partir del canal `kick` de `/project2/audio/master_audio`. Crea `/project2/audio/tempo`.

- Vota el tempo con todos los intervalos entre kicks (y sus múltiplos) de los últimos 12 s, dentro de BPM mínimo – máximo.
- Un cambio grande solo entra si se repite (cambio de rola), no por un golpe raro.
- Lleva una **fase de tiempos** que sigue corriendo en los breaks y se engancha al kick.

Página **Tempo** de `/project2/show`: Usar BPM detectado · BPM detectado · Confianza · BPM manual · mínimo · máximo.
Uso desde otros: `op('/project2/audio/tempo/tempo_lib').module.bpm()` y `.fase()`.
