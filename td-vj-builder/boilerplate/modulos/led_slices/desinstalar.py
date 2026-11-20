# led_slices/desinstalar.py — cierra y quita la ventana /salida_slices y /project1/slices (con sus efectos ledfx_*
# de la segunda capa). No toca Resolume ni el Spout / NDI. Despues: rehacer la UI (setup_ui.py) para quitar la pestana.
hecho = []
w = op('/salida_slices')
if w is not None:
    if w.isOpen:
        w.par.winclose.pulse()
    w.destroy()
    hecho.append('fuera /salida_slices')
C = op('/project1/slices')
if C is not None:
    C.destroy()
    hecho.append('fuera /project1/slices')
print('[ok] led_slices desinstalado:', hecho or 'no habia nada')
