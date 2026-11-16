# probar_pads_bancos.py - recorre cada pad de BANCOS como si llegara su nota y confirma que visual sale
import re
R = op('/project2')
sw, fx = R.op('switch2'), R.op('switch23')
t = R.op('table1')
mod = R.op('ui_perform/ui_lib').module
if not getattr(mod, '_BANCOS', None):
    raise SystemExit('[alto] BANCOS vacio en builders/herramientas/ui_bancos.py: nada que probar')
vk = R.op('vis_knobs_lib').module
print('switch23 entradas', [i.name for i in fx.inputs])
print('notas repetidas', [n for n in {t[r, 0].val for r in range(t.numRows)} if n and sum(t[r, 0].val == n for r in range(t.numRows)) > 1])
antes = int(sw.par.index.eval()), int(fx.par.index.eval())
bad = 0
for canal, slots in mod._BANCOS.items():
    for pad, slot in enumerate(slots):
        note = 'ch%dn%d' % (canal, 45 + pad if pad < 8 else 29 + pad)
        filas = [r for r in range(t.numRows) if t[r, 0].val == note]
        if slot is None:
            print(canal, pad + 1, note, 'libre', 'OK' if not filas else 'SOBRA %s' % filas)
            bad += bool(filas)
            continue
        r = filas[0] if filas else None
        cons = next((c for c in R.children if c.OPType == 'constantCHOP' and c.par.const0value.expr == "op('MIDI')[op('table1')[%s,0]]" % r), None)
        log = cons.outputs[0] if cons and cons.outputs else None
        ex = next((x for x in R.children if x.OPType == 'chopexecuteDAT' and x.par.chop.eval() == log), None) if log else None
        if ex is None:
            print(canal, pad + 1, note, 'SIN CADENA', slot); bad += 1; continue
        sw.par.index = (slot[1] + 1) % 22
        ex.module.onOffToOn(None, 0, 1, 0)
        b = vk.active_base()
        ok = len(filas) == 1 and int(sw.par.index.eval()) == slot[1]
        bad += not ok
        print(canal, pad + 1, note, ex.name, '->', int(sw.par.index.eval()), b.name if b else None, b.fetch('nombre', '') if b else '', 'OK' if ok else 'MAL')
sw.par.index, fx.par.index = antes
print('fallas', bad, '· switch2 restaurado', sw.par.index.eval())
print('luces', R.op('bs_luces_exec').module.deseados(), t[antes[0], 0].val)
print('errores', [o.path for o in R.findChildren(maxDepth=1) if o.errors(recurse=False) or o.scriptErrors(recurse=False)][:10])
