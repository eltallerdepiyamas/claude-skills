# Módulos

Piezas que se agregan a un show **solo si se usan**. Viven en el boilerplate (`BOILERPLATE_TD/modulos/`) y cada show nuevo las trae, pero no se instalan hasta que se piden.

## Usar

1. En `proyecto.json` → `"modulos"`, poner en `true` los que quieras (por ejemplo `"ledfx_chaser": true`). Las dependencias se instalan solas.
2. Correr `armar.py`, o solo `modulos/instalar_proyecto.py`.
3. `modulos/lista.py` muestra qué hay, la versión y qué está instalado en el `.toe`.

Para instalar o actualizar uno a mano:
`exec(open(project.folder + '/modulos/modulos.py', encoding='utf-8').read(), dict(globals(), ACCION='instalar', NOMBRES=['ledfx_chaser']))`

Reinstalar es actualizar: todos los instaladores son idempotentes y conservan los valores.

## Nombres

**Familia + una palabra en español que diga qué hace (no cómo se ve).** Si el término de la industria se entiende mejor, va en inglés (chaser). Si el nombre pide tres palabras, probablemente son dos módulos.

| Prefijo | Qué es |
|---|---|
| `led_` | Infraestructura de pantallas LED: siempre va si hay LED, no se toca en show |
| `ledfx_` | Efectos sobre los tableros LED: opcionales, se prenden y apagan |
| `fx_` | FX global sobre la salida principal (NDI) |
| `audio_` | Análisis del audio en vivo |
| `vig_` | Vigilancia y protección |
| `auto_` | Lo que corre solo |
| `ctl_` | Control externo (Stream Deck, MIDI) |
| `ui_` | Agregados a la UI |
| `test_` | Pruebas de pantalla y ensayo |
| `rec_` | Grabar y renderizar |

## Reglas de un módulo

1. **Apagado por default.** Instalarlo nunca cambia lo que se ve.
2. **Su propia página de parámetros** y nodos con su nombre; nada se mezcla.
3. **Se conecta en una cadena con orden, no a mano.** Los efectos LED llevan tag `ledfx` y `store('orden', n)`; `led_cadena.encadenar()` los conecta (chaser 10, barrido 20).
4. **Sale solo en la UI**: si trae `ui` en `modulo.json`, `setup_ui.py` lo corre al final.
5. **Lo propio de cada show va en parámetros o en `proyecto.json`, no en el código** (por ejemplo la cuadrícula LED: `"led": {"columnas", "filas", "tablero", ...}`).
6. **Legible y fácil de navegar** (regla del usuario): cada página se parte en secciones con título en MAYÚSCULAS (Header = separador con nombre) con `modulos/secciones.py`, en orden de uso: lo que se toca en show arriba, ajustes después, lecturas al final. Etiquetas claras con unidades ("Decaimiento (s)", "X (px desde la izquierda)"). Nada amontonado: si una página no cabe sin scroll, se parte en dos.
7. Carpeta = `modulo.json` (nombre, versión, familia, requiere, opcional, detecta, ui, origen) + `instalar.py` + `LEEME.md` (+ `ui.py` si toca la UI).

## Cómo crece

Se hace en un show; si sirve, se sube aquí como módulo (y a su espejo `td-vj-builder/boilerplate/modulos/` del repo `claude-skills`), con el show de origen en `modulo.json`. Al mejorarlo, se sube la versión.

## Catálogo

| Módulo | Qué hace | Requiere |
|---|---|---|
| `led_mapeo` | Visual → tableros (Columnas × Filas × Tablero) en el orden del procesador. Modos cuadros / franja / bloque del centro | — |
| `led_salida` | Ventana al procesador (lienzo + X/Y), armada con vigía, pixel map de prueba, MODO SHOW apaga la prueba, chip y pestaña SALIDA LED | `led_mapeo` |
| `ledfx_chaser` | Luz por tablero en secuencia, 8 patrones, con BPM detectado, kick o BPM fijo | `led_salida` (`audio_tempo` opcional) |
| `ledfx_barrido` | Rampa con halo que barre la pantalla, en tinta de la paleta o blanco | `led_salida` |
| `audio_tempo` | BPM y fase de tiempos desde el kick; sigue en los breaks | — |

Pendientes para convertir en módulo: `fx_circuit_bending`, `fx_feedback_hsv`, `auto_piloto`, `vig_audio`, `vig_video`, `test_pantallas` (Little Jesus), `rec_reel`, `ctl_streamdeck_xl`.
