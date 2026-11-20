# led_slices

El **Advanced Output de Resolume rehecho en TouchDesigner** desde su XML. Sirve de **alternativa / respaldo de Resolume**: si Resolume o el Spout fallan, TD saca los slices directo a la pantalla. Además aloja la **segunda capa de efectos** (`ledfx_chaser`, `ledfx_barrido`) slice por slice, encima del visual.

## El proceso (cómo se usa en un show)

1. **En la oficina: se arma todo en TD.** Visuales, UI, piloto. La salida a Resolume es el Spout / NDI (`setup_salida.py`).
2. **En sitio: se mapea en Resolume.** Resolume recibe el Spout / NDI de TD y en **Advanced Output** se acomodan los slices sobre la pantalla real (con el patrón de prueba de TD, el Test Card de Resolume o la guía).
3. **Se prueba que lo que manda TD llega bien a Resolume** (patrón de prueba, cada slice en su lugar, orientación).
4. **Se saca el XML final de Resolume:** Advanced Output → guardar el preset. Vive en `Documentos\Resolume Arena\Presets\Screensetup\<nombre>.xml`. Copiarlo a `assets/` del show.
5. **Se carga en TD:** `proyecto.json` → `"slices": {"xml": "assets/<nombre>.xml"}` y correr `armar.py` (o instalar el módulo), o en `/project1/slices` → XML de Advanced Output → **Leer XML otra vez**.
6. **Se revisa en TD:** pestaña **SLICES** de la UI → Prueba **Bordes** (marco de cada slice sobre el visual) y **Guía** (pixel map con el nombre de cada slice). Comparar con la captura del Advanced Output de Resolume. Leer **No reproduce**: si dice algo, ese slice no va a salir igual.
7. **Guía para los dos lados:** `python modulos/led_slices/gen_guia.py "assets/<nombre>.xml"` hace el PNG (junto al XML). Ponerlo en `proyecto.json → slices → guia` y, si se quiere, como **Output Guide** en Resolume. Si una guía vieja no coincide con los slices, manda el XML (es lo que Resolume realmente saca).
8. **Para salir por TD:** quitar antes la salida de Resolume a ese monitor (en Advanced Output) y en TD **Abrir ventana (arma)** (pestaña SLICES, o en el cel). Para regresar a Resolume: **Cerrar ventana (desarma)** y volver a prender la de Resolume.

## Qué hace

- `/project1/slices`: `entrada` (lo que va a Resolume) → `mapa` (GLSL) → efectos `ledfx_*` → `out_slices`. Tabla `slices` (nombre, x, y, w, h, on, entrada) en px de salida, origen **arriba-izquierda** como Resolume: editarla regenera el shader.
- `indice`: por píxel de salida, qué slice es y dónde cae adentro; con eso el chaser va slice por slice (en el orden del XML) y el barrido los recorre en línea.
- Reproduce: rectángulo de entrada (recorte de la composición) y de salida, encendido / apagado. **Avisa y no reproduce**: warp (perspectiva o bezier), slices girados, flip, color / brillo por slice, máscaras, soft edge.
- **Ventana `/salida_slices`**: se instala **cerrada y sin armar**. Abrir = arma y va al monitor externo a pantalla completa (sin barra, encima, sin cursor, Esc no la cierra); sin externo, ventana de prueba en la lap. Armada: vigía cada 2 s y al arrancar; si se pierde el externo la cierra y espera. No se arma si `led_salida` está armada (un solo monitor externo). Log: `control/slices_log.txt`.
- **UI** (`ui.py`): pestaña SLICES en SHOW (preview = lo que sale por TD; páginas Salida · Chaser · Barrido · Slices) y chip **TD · …** en la barra (gris apagada · verde al aire · ámbar abriendo / prueba en la lap · rojo sin pantalla); toca = la pestaña.
- **Cel** (`ctl_celular`): bloque SALIDA DESDE TD (SLICES) con estado, prueba y ABRIR (con confirmación) / CERRAR.

## Qué sale (segunda capa)

Página **Efectos** → **QUÉ SALE**: **Visual + efectos** (los `ledfx_*` encima del visual) o **Solo efectos**: el visual se cambia por un **color sólido** de la paleta (Color A / B / blanco, con nivel) y los efectos trabajan sobre él (chaser, EQ y respiración quedan como patrones de color por bocina; barrido y onda suman luz encima; cascada y giro necesitan visual). `auto_capa` lo puede alternar solo. Cadena: `mapa → base (visual o color) → efectos → out_slices`.

## Panorámico (una imagen en todas las bocinas)

Página **Efectos** → **PANORÁMICO**: en vez de que cada bocina enseñe el visual completo, **una sola imagen cruza todas** como si fueran una pantalla de bocinas pegadas (lienzo de columnas × filas; cada slice tiene su **celda** en la tabla, sacada del nombre: `A-1` = columna 1 fila 1, `C-4` = columna 4 fila 3; editable). Fuente: el cuadro completo del visual (`/project1/color_final`, 16:9), **recortado al centro** a la proporción del lienzo (o **estirado**). Modos: **Solo canal PANORÁMICOS** (default: solo los pads del grupo `PANORAMICOS` de `GRUPOS`) · **Automático** (además los que no son redondos: los generativos) · Siempre · Nunca. Fundido de 0.4 s. Los efectos siguen en el espacio de salida (pendiente: que el barrido y la onda usen el lienzo pegado, sin el tiempo muerto entre filas del pixel map).

## Máscara redonda (bocinas circulares)

Página **Efectos** → **MÁSCARA REDONDA**: **Automática** (default: solo se aplica cuando está al aire un visual que no es redondo; los grupos `CIRCULARES` y `LOGOS` de `GRUPOS` en `ui_bancos.py` ya lo son. En Corona Capital = los generativos de CH9) · Siempre · Nunca · Tamaño del círculo (1 = toca los bordes del slice; para igualarlo al círculo físico) · Borde suave · Ahora (lectura). Entra y sale con un fundido de 0.4 s al cambiar de visual. Va al final de la cadena (visual y efectos siguen el círculo); con Prueba (bordes / guía) no actúa. Sin `ui_bancos.py`, Automática = siempre.

## proyecto.json

```json
"slices": {"xml": "assets/<nombre>.xml", "entrada": "/project1/salida_patron", "guia": "assets/<nombre>_guia.png"}
```
`entrada` vacío = la entrada del Spout / NDI cuadrado (o 16:9). Rutas relativas a la carpeta del show.

## Ojo

- Medir la salida con `numpyArray` / `ver_salida` de algo que no está al aire da cuadros viejos: dejar pasar cuadros (`run(..., delayFrames=...)`).
- Cada slice puede tomar la composición completa (como en Corona Capital: 12 slices de 320×320 con la composición 1080×1080 entera) o un recorte; las dos se reproducen.
