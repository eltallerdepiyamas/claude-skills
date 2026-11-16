"""
verificar_layouts.py — comprueba, FUERA de TouchDesigner, que cada layout sea un par sincronizado
shader + CONFIG antes de correr el builder en TD.

    python builders/herramientas/verificar_layouts.py            (desde la carpeta 01. EDITABLES)
    o en el Textport de TD:
    exec(open(project.folder + '/builders/herramientas/verificar_layouts.py', encoding='utf-8').read())

Por cada builders/layouts/setup_layout_*.py lee su CONFIG (solo literales, sin ejecutar nada) y revisa:
  - exactamente 5 slots en orden de rol; nombres de parámetro con solo la primera letra en mayúscula
  - default dentro de [min, max]; audio_target es uno de los 5 slots
  - el shader existe y no usa `uniform sampler2D` ni redeclara `vUV` / `sTD2DInputs`
  - cada uniform declarado en el shader está enlazado (los 5 comunes + slots + extras + colores
    + uHeroIndex si hero=True) y cada uniform enlazado está declarado
  - cada uniform va en su propia línea (el regex de tdvj_core.check_uniforms solo ve uno por línea)
Sale con código 1 si algo falla.
"""
import ast
import glob
import os
import re
import sys

try:
    ROOT = project.folder                      # dentro de TD (Textport)
except NameError:
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
COMMON = {'uTime', 'uResolution', 'uCamCount', 'uCamfit', 'uCamAspect'}
# paleta del album: layout_core agrega Color1..5 a TODOS los layouts (_lib/paleta.py)
ALBUM = {'uColor1', 'uColor2', 'uColor3', 'uColor4', 'uColor5'}
OPTIONAL = {'uPhase'}     # reloj acumulado de la velocidad (slot 2): layout_core lo crea si el shader lo declara
UNIFORM_RE = re.compile(r'^\s*uniform\s+(?:float|int|vec2|vec3|vec4)\s+(\w+)\s*;', re.M)
PARNAME_RE = re.compile(r'^[A-Z][a-z0-9]*$')


def load_config(path):
    with open(path, encoding='utf-8') as f:
        tree = ast.parse(f.read(), path)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, 'id', '') == 'CONFIG' for t in node.targets):
            call = node.value
            if isinstance(call, ast.Call):
                return {kw.arg: ast.literal_eval(kw.value) for kw in call.keywords}
    raise ValueError('no encuentro CONFIG = dict(...)')


def check(path):
    errs = []
    cfg = load_config(path)
    slots, extras, colors = cfg['five_slots'], cfg.get('extras', []), cfg.get('colors', [])
    if len(slots) != 5:
        errs.append('five_slots tiene %d entradas (deben ser 5)' % len(slots))
    pars = [s[0] for s in slots] + [e[0] for e in extras] + [c[0] for c in colors]
    for p in pars:
        if not PARNAME_RE.match(p):
            errs.append('parámetro %r: TD solo acepta primera letra en mayúscula y el resto en minúscula' % p)
    if len(set(pars)) != len(pars):
        errs.append('nombres de parámetro repetidos')
    for (name, uni, mn, mx, d) in list(slots) + list(extras):
        if not (mn <= d <= mx):
            errs.append('%s: default %s fuera de [%s, %s]' % (name, d, mn, mx))
    at = cfg.get('audio_target')
    if at is not None and at not in [s[0] for s in slots]:
        errs.append('audio_target %r no es uno de los 5 slots' % at)

    bound = set(COMMON) | ALBUM
    if cfg.get('hero'):
        bound.add('uHeroIndex')
    bound |= {s[1] for s in slots} | {e[1] for e in extras} | {c[1] for c in colors}

    shader = os.path.join(ROOT, cfg['shader'])
    if not os.path.isfile(shader):
        errs.append('no existe el shader %s' % cfg['shader'])
        return cfg['name'], errs
    with open(shader, encoding='utf-8') as f:
        src = f.read()
    declared = set(UNIFORM_RE.findall(src))
    bound |= declared & OPTIONAL                     # opcionales: se enlazan solo si el shader los declara
    for u in sorted(declared - bound):
        errs.append('uniform %s declarado en el shader pero SIN enlazar (render negro/plano)' % u)
    for u in sorted(bound - declared):
        errs.append('uniform %s enlazado pero NO declarado en el shader' % u)
    n_decl = len(re.findall(r'\buniform\b', src))
    if n_decl != len(declared):
        errs.append('hay %d "uniform" pero check_uniforms solo ve %d (¿varios por línea o tipo raro?)'
                    % (n_decl, len(declared)))
    if re.search(r'uniform\s+sampler2D', src):
        errs.append('usa `uniform sampler2D`: las cámaras son sTD2DInputs[0..4]')
    if re.search(r'^\s*(in|varying)\s+vec[23]\s+vUV\s*;', src, re.M):
        errs.append('redeclara vUV (TD ya lo inyecta → "redefinition")')
    if re.search(r'uniform\s+sampler2D\s+sTD2DInputs', src):
        errs.append('redeclara sTD2DInputs (TD ya lo inyecta)')
    return cfg['name'], errs


def main():
    files = sorted(glob.glob(os.path.join(ROOT, 'builders', 'layouts', 'setup_layout_*.py')))
    if not files:
        print('No hay builders en builders/layouts/')
        return 1
    bad = 0
    for f in files:
        try:
            name, errs = check(f)
        except Exception as e:
            name, errs = os.path.basename(f), ['no pude leer el CONFIG: %s' % e]
        print('%s %s' % ('OK  ' if not errs else 'FAIL', name))
        for e in errs:
            print('       - ' + e)
        bad += bool(errs)
    print('\n%d layout(s) · %d con problemas' % (len(files), bad))
    return 1 if bad else 0


if 'project' in globals():
    main()                                     # en TD: solo imprime (sin sys.exit)
elif __name__ == '__main__':
    sys.exit(main())
