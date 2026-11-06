# fix_audio_chop.py — todo lo que aun apunte a /project1/null4 (audio viejo) -> /project2/audio/null4. Recarga rig.
import sys, importlib
sys.path.insert(0, project.folder + '/_lib') if project.folder + '/_lib' not in sys.path else None
import rig, tdvj_core
importlib.reload(rig); importlib.reload(tdvj_core)
n = 0
for o in op('/project2').findChildren():
    if '/_respaldo' in o.path:
        continue
    for p in o.pars():
        try:
            if p.mode == ParMode.EXPRESSION and '/project1/null4' in p.expr:
                p.expr = p.expr.replace('/project1/null4', '/project2/audio/null4'); n += 1
            elif p.mode == ParMode.CONSTANT and isinstance(p.val, str) and '/project1/null4' in p.val:
                p.val = p.val.replace('/project1/null4', '/project2/audio/null4'); n += 1
        except Exception:
            pass
for o in list(op('/project1').findChildren()) + list(op('/project2').findChildren()):
    try:
        o.cook(force=True)
    except Exception:
        pass
bad = [o.path for r in (op('/project1'), op('/project2')) for o in [r] + list(r.findChildren())
       if '/_respaldo' not in o.path and '/audioAnalysis/' not in o.path and (o.errors(recurse=False) or o.scriptErrors(recurse=False))]
print('[ok] referencias de audio corregidas:', n, '· rig.AUDIO_SOURCE =', rig.AUDIO_SOURCE)
print('errores vivos:', len(bad), bad[:5])
