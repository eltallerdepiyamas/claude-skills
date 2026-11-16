# =============================================================
# diag_todo.py — revisa TODO el rig en una pasada y dice que esta bien y que falla (con el arreglo).
# Solo lee: no cambia nada. Correrlo despues de build_all / actualizar_companion, antes de ensayar.
#   Textport:  exec(open(project.folder + '/control/diag_todo.py', encoding='utf-8').read())
# =============================================================
import json, os, sys

SCENE_PATH = '/project2/base17/escena_modular'
TD_PORT, COMPANION_PORT = 7010, 12321

_res = {'ok': 0, 'falla': 0, 'aviso': 0}


def ok(msg):
    _res['ok'] += 1
    print('  OK     ' + msg)


def falla(msg, arreglo=''):
    _res['falla'] += 1
    print('  FALLA  ' + msg + (('\n         -> ' + arreglo) if arreglo else ''))


def aviso(msg, arreglo=''):
    _res['aviso'] += 1
    print('  AVISO  ' + msg + (('\n         -> ' + arreglo) if arreglo else ''))


def seccion(t):
    print('\n== %s ==' % t)


def par_por_label(o, *labels):
    return next((p for p in o.pars() if p.label.lower() in labels and not p.isMenu), None)


def run():
    print('==== diag_todo: %s ====' % project.name)
    S = op(SCENE_PATH)
    if S is None:
        falla('no existe ' + SCENE_PATH)
        return

    # ── resolucion
    seccion('Resolucion')
    if project.folder + '/_lib' not in sys.path:
        sys.path.insert(0, project.folder + '/_lib')
    try:
        import importlib, tdvj_core
        importlib.reload(tdvj_core)
        m = tdvj_core.master_res_pars()
    except Exception as e:
        m = None
        falla('no pude leer la resolucion maestra (%s)' % e)
    if m:
        rw, rh = m
        ok('maestra %d x %d (%s.%s / %s)' % (rw.eval(), rh.eval(), S.name, rw.name, rh.name))
        sueltas = []
        for c in op('/project2').children:
            if c.isCOMP and c.name.startswith('base') and getattr(c.par, 'Resw', None) is not None:
                if rw.name not in (c.par.Resw.expr or ''):
                    sueltas.append('%s (%dx%d)' % (c.name, c.par.Resw.eval(), c.par.Resh.eval()))
        if sueltas:
            aviso('bases con resolucion propia: ' + ', '.join(sueltas),
                  'si deben seguir a la maestra: builders/herramientas/aplicar_resolucion.py')
        else:
            ok('visuales / FX siguen a la maestra')
        fits = [t for t in op('/project2').children if t.name.startswith('fit') and t.OPType == 'fitTOP']
        malas = [t.name for t in fits if rw.name not in (t.par.resolutionw.expr or '')]
        if malas:
            aviso('salidas que no siguen a la maestra: ' + ', '.join(malas), 'aplicar_resolucion.py')
        elif fits:
            ok('salidas %s siguen a la maestra' % ', '.join(t.name for t in fits))

    # ── escenas
    seccion('Escenas (layouts)')
    p = getattr(S.par, 'Modoescena', None)
    lays = [c for c in S.children if c.isCOMP and c.name.startswith('layout_')]
    if p is None:
        falla('no existe el menu Modoescena', 'builders/herramientas/registrar_layouts.py')
    else:
        fuera = [c.name for c in lays if c.name not in p.menuNames]
        if fuera:
            falla('layouts que no estan en el menu: ' + ', '.join(fuera), 'registrar_layouts.py')
        fam = {'multiview': 0, 'singlecam': 0}
        for c in lays:
            fam['singlecam' if 'tdvj_fam_singlecam' in c.tags else 'multiview'] += 1
        ok('%d escenas en el menu (%d multiview · %d single cam)' % (len(p.menuNames), fam['multiview'], fam['singlecam']))
        bs = S.op('blend_switch')
        if bs is not None and len(bs.inputs) < len(p.menuNames):
            falla('blend_switch tiene %d entradas para %d escenas' % (len(bs.inputs), len(p.menuNames)),
                  'registrar_layouts.py')
    for c in lays:
        g = c.op('glsl_layout')
        if g is None:
            falla('%s sin glsl_layout' % c.name, 'vuelve a correr su builder')
            continue
        e = (g.errors() or '').strip()
        if e:
            falla('%s: %s' % (c.name, e.splitlines()[0][:160]), 'revisa el shader (pegame el error)')
        if c.op('out1') is None:
            falla('%s sin out1' % c.name)
        cols = [getattr(c.par, 'Color%dr' % i, None) for i in range(1, 6)]
        if None in cols:
            aviso('%s sin los 5 colores del album' % c.name, 'vuelve a correr build_all.py')
    if lays:
        ok('%d layouts revisados (los que fallan salen arriba)' % len(lays))

    # ── Companion / OSC
    seccion('Stream Deck (Companion) y OSC')
    oin = S.op('oscin1')
    if oin is None:
        falla('no existe oscin1 (Companion -> TD)')
    else:
        port = par_por_label(oin, 'network port', 'port')
        if port is not None and int(port.eval()) != TD_PORT:
            falla('oscin1 escucha en %s (debe ser %d)' % (port.eval(), TD_PORT))
        else:
            ok('oscin1 escucha en %d' % TD_PORT)
        cb = oin.par.callbacks.eval() if hasattr(oin.par, 'callbacks') else None
        if cb is None or 'deck_t' not in cb.text:
            falla('el router OSC es una version vieja', 'control/actualizar_companion.py')
        else:
            ok('router OSC al dia')
    out = S.op('companion_out')
    if out is None:
        falla('no existe companion_out (TD -> Companion)', 'control/actualizar_companion.py')
    else:
        port = par_por_label(out, 'network port', 'port')
        if port is not None and int(port.eval()) != COMPANION_PORT:
            falla('companion_out manda a %s (Companion escucha en %d)' % (port.eval(), COMPANION_PORT),
                  'control/actualizar_companion.py')
        else:
            ok('TD -> Companion en %d' % COMPANION_PORT)
    for n, txt in (('companion_feedback', 'feedback de escena / camaras'), ('mix_feedback', 'pagina AJUSTES / MENU')):
        if S.op(n) is None:
            falla('falta %s (%s)' % (n, txt), 'control/actualizar_companion.py')
        else:
            ok('%s activo' % n)
    try:
        with open(project.folder + '/control/show.json', encoding='utf-8') as f:
            sj = json.load(f)
        if p is not None and len(sj.get('layouts', [])) != len(p.menuNames):
            aviso('el Stream Deck tiene %d escenas y TD %d' % (len(sj.get('layouts', [])), len(p.menuNames)),
                  'actualizar_companion.py en TD -> python control/gen_companion.py -> importar en Companion')
        else:
            ok('show.json al dia con las escenas')
    except Exception:
        aviso('no hay control/show.json', 'control/actualizar_companion.py')

    # ── demo / rec
    seccion('ENSAYO: DEMO y REC')
    rec, ex = S.op('demo_rec'), S.op('demo_exec')
    if rec is None or ex is None:
        falla('faltan demo_rec / demo_exec', 'control/setup_demo.py')
    else:
        ok('demo y grabador listos (graba %s)' % (S.par.Recsel.menuLabels[S.par.Recsel.menuIndex]
                                                if hasattr(S.par, 'Recsel') else '?'))
        if 'audio_chop' not in ex.text:
            falla('el grabador es una version vieja (sin audio)', 'control/setup_demo.py')
        ac = S.par.Recaudiochop.eval() if hasattr(S.par, 'Recaudiochop') else None
        if not (hasattr(S.par, 'Recaudio') and S.par.Recaudio.eval()):
            aviso('grabar con audio esta apagado (pestana Demo)')
        elif ac is None:
            falla('no hay CHOP de audio para grabar', 'pestana Demo -> "Audio que se graba"')
        else:
            real = ac.inputs[0] if ac.OPType == 'audiodeviceoutCHOP' and ac.inputs else ac
            if real.rate < 8000:
                falla('%s corre a %g/s: no es sonido' % (real.path, real.rate),
                      'usa el Audio Device In / lo que entra a audiodevout, no el analisis (null4)')
            else:
                ok('audio para grabar: %s (%d canales, %g Hz)' % (real.path, real.numChans, real.rate))
        cod = getattr(rec.par, 'audiocodec', None)
        if cod is not None and 'pcm' not in cod.eval() and 'alac' not in cod.eval():
            aviso('codec de audio %s (en .mov conviene PCM)' % cod.eval(), 'control/setup_demo.py')
        folder = project.folder + '/renders'
        movs = sorted(f for f in os.listdir(folder) if f.endswith('.mov')) if os.path.isdir(folder) else []
        if movs:
            ok('ultima grabacion: renders/%s' % movs[-1])

    # ── beatstep
    seccion('Beatstep (canal 9 = escenas)')
    if not [c for c in S.children if c.name.startswith('bs_escenas')]:
        aviso('no estan los nodos bs_escenas_*', 'control/setup_beatstep_escenas.py')
    else:
        ok('pads del canal 9 -> escenas 1-16')

    print('\n==== %d OK · %d avisos · %d fallas ====' % (_res['ok'], _res['aviso'], _res['falla']))
    if _res['falla'] == 0 and _res['aviso'] == 0:
        print('Todo listo para ensayar.')


run()
