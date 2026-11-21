# ctl_celular

Una página web que sirve TouchDesigner para **operar y vigilar el show desde el celular**, sin regresar a la compu. Pensado para mapear en sitio y para shows sin operador (el usuario se da sus vueltas).

## Usar

1. `proyecto.json` → `"modulos": {"ctl_celular": true}` (opcional `"celular": {"puerto": 9990}`) y correr `armar.py`, o instalarlo a mano con `modulos.py`.
2. Al instalar imprime la dirección: en el cel, **en la misma red Wi-Fi que la lap**, abrir `http://<ip de la lap>:9990`.
3. Si la lap cambia de red, cambia la IP: volver a instalar (o ver la IP en la red de Windows). El puerto 9980 es del MCP; no usarlo.
4. Si no carga: misma red, que la red no aísle dispositivos (redes de invitados), y que el firewall de Windows deje pasar a TouchDesigner en ese perfil de red.

## Qué trae

Sale solo lo que el show tenga (si no hay piloto, slices o patrón, ese bloque no aparece):

| Bloque | Qué hace | Necesita |
|---|---|---|
| ESTADO | Salida · Vigía · FPS · Audio, con semáforo | — |
| AVISOS (ntfy) | Avisa al cel al fallar y al arreglarse: salida, vigía, FPS, sin audio, TD arrancó, resumen. Página **Avisos** del hub; en el cel, app ntfy suscrita a `Avisostema` | internet en la lap |
| PATRÓN DE PRUEBA | Manda el patrón de alineación en vez del visual | `show.Patronprueba` |
| SALIDA DESDE TD (SLICES) | Estado, modo de prueba y ABRIR (con confirmación) / CERRAR | `led_slices` |
| ◀ ANTERIOR / SIGUIENTE ▶ + CANAL | Recorre `BANCOS` de `ui_bancos.py` (o las entradas de `switch2`). **CANAL**: TODOS o un canal (CH9 … CH13); con uno elegido, anterior / siguiente da la vuelta solo en ese canal y abajo sale la **rejilla de sus pads** para tocar uno directo (el al aire en verde; el piloto se pausa solo, como con un thumb) | — |
| Tamaño | LOGOS → `Logotamano` + `base.Tamano`; CIRCULARES → `Circulotamano` + `base.Tamano` (según `GRUPOS`) | esos parámetros |
| MANUAL / AUTO + AJUSTES DEL PILOTO | Todas las páginas Piloto · Repertorio · Vigía con sus secciones; un parámetro nuevo ahí sale solo en el cel | `auto_piloto` |
| PAUSA / PLAY | Congela la imagen | — |
| EFECTOS (botones rápidos) | Siempre visible: AUTO · CHASER · BARRIDO · EQ · ONDA · CASCADA · GIRO · RESPIRA · SOLO EFECTOS; un toque prende / apaga (verde = prendido) y arriba dice cuántos hay | `led_slices` + `ledfx_*` |
| EFECTOS Y MÁSCARA | Una sub-página por página de `/project1/slices` (qué sale y máscara · capa automática · chaser · barrido · EQ · onda · cascada · giro · respiración), con sus secciones; el encabezado dice si el efecto está ON. Un parámetro nuevo en esas páginas sale solo | `led_slices` + `ledfx_*` |
| GUARDAR | El GUARDAR de la UI (siguiente versión) | `ui_guardar` |
| FUENTE DE AUDIO | Archivo / en vivo y dispositivo · GAIN de entrada (−/+) · Autonivel · **VER ONDA DE AUDIO** (v1.2): pico de entrada que corre, barras graves · medios · agudos · kick y espectro tenue; dice NO LLEGA AUDIO / SATURA. Solo lee (`/audio_nivel`, ~7 por s) mientras está prendida; el cel recuerda si la dejaste prendida | `show.Audiofuente`, `Audiogain`, `Autonivel` |
| BLACKOUT · RESET FEEDBACK | Bajo PAUSA (v1.2). BLACKOUT = el de la UI (fundido; pide confirmar, regresar no); RESET FEEDBACK reinicia las estelas. Los dos con confirmación | `ui_lib.elegir('BLACKOUT')`, `ui_lib.resetear_feedbacks()` |

## Pestañas (v1.3)

Arriba, fijo: conexión, canal y visual al aire con marcas (EN NEGRO · EN PAUSA · PATRÓN AL AIRE · AUTO / MANUAL) y las pestañas:
**VISUAL** (anterior / siguiente, pausa, blackout, reset feedback, tamaños) · **PADS** (canal y sus pads) · **PILOTO** (manual / auto y ajustes) · **EFECTOS** (botones rápidos y páginas de efectos y máscara) · **AUDIO** (fuente, gain, autonivel, onda) · **ESTADO** (semáforo, guardar, patrón, salida de slices, avisos).
Una pestaña sin contenido en el show no sale. AUDIO y ESTADO llevan un punto ámbar / rojo si algo falla. El cel recuerda la última pestaña. La onda solo lee con AUDIO a la vista.

## MODO SHOW del cel (v1.4)

Botón 🔓 / 🔒 **MODO SHOW** arriba a la derecha. Puesto: el cel **solo mira** (se navega entre pestañas, se ve el estado, la onda y los pads de cada canal) y **el servidor ignora** cualquier cambio (`/set`, `/ir`, `/pad`, `/par`, `/audio`, `/blackout`, …): aunque un toque se cuele, no pasa nada (queda en el log). Quitarlo pide confirmación. Es solo del cel: la UI de la lap y su `Modoshow` no cambian. Se guarda en el COMP (`C.store('candado')`).

## PAUSA / PLAY (cómo funciona)

`<lo que entra a level1> → pausa_sw → level1`, con `pausa_cache` guardando el último cuadro. La base **sigue corriendo detrás**: apagarle el cook a la base la manda a **negro** (así falló la primera versión). Mientras está en pausa: el piloto no cambia (`Pilotoquedarse`) y el **vigía se apaga** (leía la imagen quieta como falla y saltaba el visual); al dar PLAY regresan como estaban. PLAY solo si el visual al aire cambia por otro lado o TD arranca. Master / BLACKOUT siguen funcionando. Si otro script reconecta `level1`, la cadena se rehace sola.

## Reglas

- No agregar botones que no se pidan: la página es para lo que se necesita en sitio.
- Todo control nuevo del show va primero en la UI de perform; al cel solo lo que haga falta lejos de la lap.
- Medir una base fuera del aire con `numpyArray` / `ver_salida` da cuadros viejos: dejar pasar cuadros (`run(..., delayFrames=...)`).

Desinstalar: `desinstalar.py` (PLAY, level1 como estaba, fuera pausa y `show/celular`; la página Avisos se queda).
