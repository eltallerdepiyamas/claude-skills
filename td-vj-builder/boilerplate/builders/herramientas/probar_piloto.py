# probar_piloto.py: estado del piloto (MODO = 'prender' prueba corta, 'ver' solo lee, 'apagar' regresa defaults)
MODO = 'ver'
S = op('/project2/show')
P = S.op('piloto')
lib = P.op('piloto_lib')
if MODO == 'prender':
    S.par.Pilotoduracion = 6
    S.par.Pilotominimo = 3
    S.par.Pilotoauto = True
    S.par.Pilotosiguiente.pulse()
elif MODO == 'apagar':
    S.par.Pilotoauto = False
    S.par.Pilotoduracion = S.par.Pilotoduracion.default
    S.par.Pilotominimo = S.par.Pilotominimo.default
d = P.fetch('pil', {}, search=False)
print('AUTO', S.par.Pilotoauto.eval(), '| chip:', lib.module.estado_txt(), '| ahora:', P.fetch('ahora_txt', '-', search=False),
      '| vigia:', P.fetch('vigia_txt', '-', search=False))
print('cambios', d.get('cambios'), '| trans', bool(d.get('trans')), '| cross', op('/project2/piloto_cross').par.cross.eval(),
      '| switch2', op('/project2/switch2').par.index.eval(), '| piloto_b', op('/project2/piloto_b').par.index.eval(),
      '| deriva', (d.get('deriva') or {}).get('base'))
print('errores:', [ (o.path, o.errors()) for o in (lib, P.op('piloto_exec'), P.op('piloto_pulsos')) if o.errors()])
import os
f = project.folder + '/control/piloto_log.txt'
print(open(f, encoding='utf-8').read()[-600:] if os.path.exists(f) else 'sin log')
