# =============================================================
# diag_mix.py  —  SOLO LECTURA: por que la pagina MIX del Stream Deck no muestra los parametros
# Revisa: que exista y corra mix_feedback, que exista companion_out (a donde manda) y que manda ahorita.
# Uso (Textport):
#   exec(open(project.folder + '/control/diag_mix.py', encoding='utf-8').read())
# =============================================================

m = op('/project2/base17/escena_modular')
ex = m.op('mix_feedback')
out = m.op('companion_out')

print('mix_feedback:', 'FALTA (corre actualizar_companion.py)' if ex is None else
      'ok · active=%s frameend=%s · errores: %s' % (ex.par.active.eval(), ex.par.frameend.eval(),
                                                     (ex.scriptErrors() or 'ninguno').strip()))
if out is None:
    print('companion_out: FALTA (corre actualizar_companion.py)')
else:
    addr = next((p for p in out.pars() if 'address' in p.label.lower() and not p.isMenu), None)
    port = next((p for p in out.pars() if p.label.lower() in ('network port', 'port')), None)
    print('companion_out: manda a %s:%s · active=%s' % (addr.eval() if addr else '?', port.eval() if port else '?',
                                                       out.par.active.eval() if hasattr(out.par, 'active') else '?'))

if ex is not None:
    print('foco:', ex.fetch('mix_foco', '-', storeDefault=False))
    sent = ex.fetch('mix_sent', {}, storeDefault=False)
    if not sent:
        print('[!] todavia no ha mandado nada: mix_feedback no esta corriendo (revisa errores arriba)')
    for k in ['foco', 'foconombre'] + ['p%dn' % i for i in range(1, 6)] + ['p%dv' % i for i in range(1, 6)]:
        print('   mix_%-12s = %s' % (k, sent.get(k, '-')))
print('Si aqui salen valores pero el Stream Deck no los muestra: en Companion -> Variables -> Custom,')
print('revisa que existan mix_p1n... (si no, importa el streamdeck.companionconfig nuevo) y que el')
print('servicio OSC de Companion este activo en el puerto 12321 (el de fabrica).')
