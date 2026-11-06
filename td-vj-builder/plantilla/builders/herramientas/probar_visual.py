# probar_visual.py — prueba el router OSC (setVisual) y la deteccion del visual activo; deja todo como estaba.
cb = op('/project2/base17/escena_modular/oscin1_callbacks').module
s2 = op('/project2/switch2')
antes = s2.par.index.eval()
for n in (1, 9, 16):
    cb.setVisual(n)
    b = op('/project2/vis_knobs_lib').module.active_base()
    print('setVisual(%d) -> switch2.index=%d -> %s' % (n, s2.par.index.eval(), b.path if b else None))
s2.par.index = antes
print('regresado a index', antes)
