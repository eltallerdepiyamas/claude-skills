# fix_contrato.py — fx_knobs_lib era una version vieja: solo conocia el contrato de LJ. Le agrega la lectura
# de la pagina del FX (igual que vis_knobs_lib) y revisa Trama. Idempotente.
d = op('/project2/fx_knobs_lib')
a = "    names = [t[r, 0].val for r in range(t.numRows)] if t is not None and t.isDAT else CONTRACT\n"
b = a + """    if (t is None or not t.isDAT) and not all(getattr(base.par, n, None) is not None for n in CONTRACT):
        pg = next((g for g in base.customPages if g.name in ('Visual', 'Filter', 'Layout')), None)
        if pg is not None:
            names = [p.name for p in pg.pars if (p.isFloat or p.isInt) and p.style not in ('RGB', 'RGBA')]
"""
if 'not all(getattr(base.par' not in d.text:
    d.text = d.text.replace(a, b)
print('listo; revisar con leer_fx_sd.py')
