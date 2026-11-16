# quitar_cc63_resolume.py — CC63 deja de mandar composition/master a Resolume; capas 1-3 siguen. Idempotente.
s = op('/project2/control_p1/select1')
s.par.channames = ' '.join(x for x in s.par.channames.eval().split() if x != 'ch1ctrl63')
o = op('/project2/control_p1/oscout1')
print('select1:', s.par.channames.eval(), '| oscout1 manda:', [c.name for c in o.chans()])
m = op('/project2/base17/escena_modular/oscin1_callbacks').module
print('pad reset listo:', op('/project2/show/pad_reset_in').numChans, 'canal ·', len(m.resetActivo(aplicar=False, escena=True)), 'sliders')
print('color map:', op('/project2/show/color_midi').par.channames.eval())
