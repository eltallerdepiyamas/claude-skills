# estado_revision.py: en que va revisar_visuales (y errores del modulo si se detuvo)
lib = op('/project2/show/revisar_visuales_lib')
st = lib.fetch('rv', None, search=False) if lib else None
if not st:
    print('no hay revision')
else:
    print('van %d/%d | fin: %s' % (st['i'], len(st['lista']), st.get('fin', False)))
    if not st.get('fin') and st['i'] < len(st['lista']):
        v = st['lista'][st['i']]
        print('en:', v['canal'], v['pad'], v['nombre'], '| muestras', len(v.get('muestras', [])))
print('errores lib:', lib.errors() if lib else '-')
