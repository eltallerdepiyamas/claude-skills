# led_salida

Saca el mapeo a la pantalla del procesador por la ventana `/salida_led`, aparte de la UI (`/perform`).

- **Lienzo** (ancho × alto = resolución del monitor del procesador) con el mapeo pegado 1:1 en **X / Y**.
- **Abrir ventana LED** la arma; **Cerrar** la desarma. Armada, el vigía (cada 2 s y al arrancar) la abre o la pasa al monitor externo, y si se pierde la pantalla la cierra y espera. Log: `control/led_log.txt`.
- Con monitor externo: pantalla completa, sin barra ni cursor, Esc no la cierra. Sin externo: ventana de prueba en la lap.
- **Patrón de prueba**: pone el pixel map (`Pixelmap`) en lugar del visual. MODO SHOW lo apaga.
- **UI** (`ui.py`): pestaña SALIDA LED en SHOW (vista FILAS × COLUMNAS / EN LÍNEA + todas las páginas de `/project1/led`) y chip LED arriba (gris apagada · verde al aire · ámbar prueba · rojo sin pantalla).
- `led_cadena.encadenar()`: conecta los efectos `ledfx_*` en orden entre la fuente y el lienzo.

En sitio: la resolución del procesador va en Windows (o resolución personalizada en NVIDIA), escala 100 %, y la misma en Lienzo.
