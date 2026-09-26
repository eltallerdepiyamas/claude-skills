# Along TD FX

Toolkit modular para TouchDesigner + GLSL TOP inspirado en el universo visual de Along para un show en vivo con camara/video.

La direccion es intima, romantica, nocturna, vulnerable, surreal y pop emocional. Evita el glitch EDM agresivo: los efectos priorizan glow suave, degradacion digital delicada, halos, reflejos, feedback lento y distorsiones con intencion emocional.

## Estructura

- `builders/`: scripts que construyen redes TouchDesigner automaticamente.
- `lib/`: helpers reutilizables para crear nodos, cargar shaders, configurar uniforms y aplicar presets.
- `shaders/`: shaders GLSL TOP. Cada archivo es un efecto autocontenido.
- `tools/`: utilidades de validacion, exportacion y recarga.
- `config.py`: registro central de efectos, rutas y uniforms.
- `NEW_SHADERS_2026.md`: dossier tecnico-creativo de los efectos.

## Naming

Los shaders usan prefijo numerico para mantener orden de show:

`NN_nombre_emocional.frag`

Ejemplo: `01_cobalto_fantasma.frag`.

Cada shader declara el mismo contrato de uniforms:

```glsl
uniform float time;
uniform float intensity;
uniform float speed;
uniform float distortion;
uniform float audioReactive;
uniform float feedbackAmount;
```

Esto permite mapear control MIDI, CHOPs, audio analysis o presets sin reconfigurar cada efecto.

## Carga automatica

Los builders crean un `textDAT` por shader, leen el archivo `.frag` y lo asignan al parametro Pixel Shader DAT del `glslTOP`. La lista de efectos vive en `config.py`, asi que para agregar un shader nuevo basta con:

1. Crear `shaders/09_nombre.frag`.
2. Agregar una entrada en `config.py`.
3. Ejecutar `builders/build_master_comp.py` o `builders/build_all_fx.py` desde TouchDesigner.

## Builders

- `build_all_fx.py`: crea un `baseCOMP` independiente por efecto.
- `build_master_comp.py`: crea un master `baseCOMP` con todos los GLSL TOP conectados a un `switchTOP`.
- `build_test_network.py`: crea entrada de camara, level, master FX y preview.
- `build_into_existing_bases.py`: instala shaders dentro de `baseCOMP`s ya existentes, exponiendo parametros en cada base.

Uso recomendado en TouchDesigner:

```python
run("E:/tiani/Documents/Touch Designer Projects/01. EDITABLES/along_td_fx/builders/build_test_network.py")
```

Para usar tus bases existentes de `/project2/base18` a `/project2/base24`:

```python
run("E:/tiani/Documents/Touch Designer Projects/01. EDITABLES/along_td_fx/builders/build_into_existing_bases.py")
```

Mapeo por defecto:

- `/project2/base18`: `01_cobalto_fantasma`
- `/project2/base19`: `02_girasol_cenital`
- `/project2/base20`: `03_cuarto_inclinado`
- `/project2/base21`: `04_corazon_mascota`
- `/project2/base22`: `05_parabrisas_ambar`
- `/project2/base23`: `06_rayo_pop_posterizado`
- `/project2/base24`: `07_eco_confesional`

Hay 8 shaders y ese rango solo contiene 7 bases. Para incluir `08_vertical_c100t`, agrega `/project2/base25` o cambia el mapeo `TARGETS` en `build_into_existing_bases.py`.

## Extension

Para crear nuevos efectos, conserva:

- `out vec4 fragColor;`
- lectura con `texture(sTD2DInputs[0], vUV.st)`
- salida con `fragColor = TDOutputSwizzle(vec4(color, 1.0));`
- uniforms compartidos
- comentarios cortos de intencion visual

Si el efecto requiere feedback, usa input 1 del GLSL TOP y construye la red con `feedbackTOP` + `levelTOP` + `compositeTOP`. Mantener el feedback bajo es importante para concierto: valores entre `0.18` y `0.55` suelen ser estables.

## Performance

Los shaders usan pocas muestras de textura, operaciones simples y no dependen de loops largos. Para show:

- Trabajar a 1280x720 o 1920x1080 segun GPU.
- Usar `nullTOP` despues del master para ruteo estable.
- Mantener `blurTOP` previo en tamano bajo.
- Controlar `intensity`, `distortion` y `feedbackAmount` desde un `constantCHOP` o MIDI.
