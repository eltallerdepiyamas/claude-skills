# Loop autónomo vs reactivo en vivo

Es la primera pregunta del flujo porque cambia cómo se piensa el feedback y el audio.

## Reactivo en vivo (default del template)
Corre dentro de TD reaccionando a audio en tiempo real (mic / loopback / interfaz).
- El "loop" es solo la animación base (el boil) que cicla sola; el audio añade encima.
- El feedback NO necesita cerrar loop perfecto: es una pieza viva.
- La cadena de audio (`audio_devicein → bandas → null 'audio'`) va tal cual.
- Salida: el viewer de `out_null`, o un Out TOP para mandarlo a una salida/proyector.

## Loop autónomo (para exportar MP4/GIF y subir como story)
Una pieza finita que loopea perfecto al reproducirse.
- **El boil y el chroma SÍ loopean** porque van sobre fases senoidales (`math.cos/sin`
  del tiempo): periodo = cada cuánto vuelven al inicio.
- **El feedback NO loopea solo** (es recursivo, acumula memoria). Opciones:
  1. Mantener la estela sutil y dejar que llegue a estado estable; aceptar costura mínima.
  2. Renderizar unos segundos de más y trimear (descartar el arranque "frío" del feedback).
  3. Quitar el feedback duro y fingir la estela con un par de composites pre-desplazados
     (eso sí loopea perfecto).
- El audio en vivo no aplica para un export determinista. Para que el export "siga la
  música" de un track fijo, alimenta la cadena de audio con un Audio File In (en vez de
  Audio Device In) y renderiza a esa duración.
- **Exportar en TD:** Movie File Out TOP, o el render/export del proyecto, a la duración
  del loop y al fps deseado. Resolución = la del flyer (vertical 1080×1920 para story).

## Regla práctica
Si el usuario dice "story", "subir", "exportar", "MP4" → loop autónomo (cuida el feedback).
Si dice "en vivo", "proyectar", "set", "que reaccione al micro" → reactivo (template tal cual).
