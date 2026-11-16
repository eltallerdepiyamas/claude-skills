# inspeccionar_feedback.py — SOLO LEE: estado del feedback TD -> Companion.
S = op('/project2/base17/escena_modular')
for o in S.children:
    if o.OPType in ('parameterexecuteDAT', 'oscoutDAT'):
        print(o.name, o.OPType, (o.errors() or o.scriptErrors() or 'ok').strip()[:120], 'pars', getattr(o.par, 'pars', None) and o.par.pars.eval(), 'op', getattr(o.par, 'op', None) and o.par.op.eval(), 'act', o.par.active.eval() if hasattr(o.par, 'active') else '', 'port', o.par.port.eval() if hasattr(o.par, 'port') else '')
print(S.par.Modoescena.eval(), S.par.Modoescena.menuLabels[S.par.Modoescena.menuIndex])
