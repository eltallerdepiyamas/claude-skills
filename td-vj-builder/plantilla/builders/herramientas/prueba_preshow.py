# prueba_preshow.py — PRUEBA GENERAL UN DIA ANTES DEL SHOW (sirve para cualquier .toe del rig)
#
# Se corre DOS veces:
#   1a vez: revisa el proyecto (errores, archivos que faltan, dispositivos, tipografias, memoria de video) y
#           arranca la prueba de rendimiento: mide como esta y luego pone al aire CADA escena un par de segundos
#           (y un titulo, si hay). OJO: cambia lo que sale por la salida durante ~1-2 minutos. No usar al aire.
#   2a vez (cuando termine): imprime el reporte. Tambien queda en exports/preshow_<fecha>.txt
#
# No arregla ni borra nada: solo lee, mide y deja todo como estaba.
import os
import time

ESCENAS = True        # recorrer todas las escenas
TITULO = True         # probar un titulo al aire
ASIENTO = 20          # cuadros que se dejan pasar al cambiar de escena (compila el shader)
MEDIR = 45            # cuadros que se miden por escena
CANCELAR = False      # True = detiene una prueba a medias y regresa todo
SOLO_FRIO = False     # True = solo la revision en frio (no toca la salida)

R = op('/')
FUERA = ('/_respaldo', '/_descartados')
SISTEMA = ('local', 'sys', 'ui', 'perform')

TICK = r'''# preshow_tick — temporal: lo crea y lo borra builders/herramientas/prueba_preshow.py
import time
_OPS = None


def _ops():
    global _OPS
    if _OPS is None:
        _OPS = [o for r in op('/').children if r.isCOMP and r.name not in %(SISTEMA)r
                for o in r.findChildren() if not o.isCOMP and not any(x in o.path for x in %(FUERA)r)]
    return _OPS


def _nodos():
    """Lo que cocino en este cuadro: (ms por contenedor, los nodos mas caros, ms de GPU en total)."""
    f = absTime.frame
    cont, caros, gpu = {}, [], 0.0
    for o in _ops():
        try:
            if f - o.cookAbsFrame > 1:
                continue
            c, g = o.cpuCookTime, (o.gpuCookTime if o.isTOP else 0.0)
        except Exception:
            continue
        gpu += g
        k = '/'.join(o.path.split('/')[:3])
        cont[k] = cont.get(k, 0.0) + c + g
        if c + g > 0.3:
            caros.append((round(c + g, 2), o.path))
    caros.sort(reverse=True)
    top = sorted(cont.items(), key=lambda kv: -kv[1])[:6]
    return [(k, round(v, 1)) for k, v in top], caros[:6], round(gpu, 1)


def _aplicar(s, paso):
    tipo, cual = paso
    if tipo == 'escena':
        op(s['escena']).par.Modoescena = cual
    elif tipo == 'titulo':
        op(s['show']).par.Tituloaire = True


def _cerrar(s, paso):
    tipo, cual = paso
    d = s['dts']
    med = sum(d) / len(d) if d else 0.0
    r = {'tipo': tipo, 'cual': cual, 'fps': round(1.0 / med, 1) if med > 0 else 0.0,
         'peor': round(max(d) * 1000, 1) if d else 0.0}
    r['cont'], r['caros'], r['gpu'] = _nodos()
    if tipo == 'escena':
        E = op(s['escena'])
        f = absTime.frame
        coc = []
        for l in E.children:
            if l.isCOMP and l.name.startswith('layout_'):
                g = l.op('glsl_layout')
                if g is not None and f - g.cookAbsFrame <= 2:
                    coc.append(l.name)
                    if g.errors() or g.warnings():
                        r['err'] = (g.errors() or g.warnings())[:120]
        r['cocinan'] = coc
    elif tipo == 'titulo':
        S = op(s['show'])
        t = S.op('titulos')
        r['activo'] = float(t.op('estado')['activo']) if t is not None and t.op('estado') is not None else -1
        S.par.Tituloaire = False
    s['res'].append(r)


def _terminar(s):
    try:
        if s.get('escena') and s.get('escena0') is not None:
            op(s['escena']).par.Modoescena = s['escena0']
        if s.get('show') and s.get('tit'):
            op(s['show']).par.Tituloaire = False
    except Exception as x:
        s['log'].append('no pude regresar todo: ' + repr(x))
    s['fase'] = 'listo'
    me.par.active = False


def onFrameEnd(frame):
    s = op('/').fetch('preshow', None, search=False, storeDefault=False)
    if not s or s.get('fase') != 'corriendo':
        return
    try:
        ahora = time.perf_counter()
        dt = ahora - s['t'] if s['t'] else None
        s['t'] = ahora
        paso = s['pasos'][s['i']]
        n = s['n']
        if n == 0:
            _aplicar(s, paso)
        elif n > s['asiento'] and dt is not None:
            s['dts'].append(dt)
        if n >= s['asiento'] + s['medir']:
            _cerrar(s, paso)
            s['i'] += 1
            s['n'] = 0
            s['dts'] = []
            if s['i'] >= len(s['pasos']):
                _terminar(s)
            return
        s['n'] = n + 1
    except Exception as x:
        s['log'].append('la prueba se detuvo: ' + repr(x))
        _terminar(s)
    return
''' % {'SISTEMA': SISTEMA, 'FUERA': FUERA}


def vivos():
    return [o for r in R.children if r.isCOMP and r.name not in SISTEMA
            for o in [r] + list(r.findChildren()) if o.OPType != 'annotateCOMP' and not any(x in o.path for x in FUERA)]


def corto(l, n=6):
    l = list(l)
    return ' · '.join(str(x) for x in l[:n]) + ('  (+%d)' % (len(l) - n) if len(l) > n else '')


def revisar():
    """Revision en frio. Devuelve los renglones del reporte."""
    L = []
    t0 = time.perf_counter()
    ops = vivos()
    reloj = R.time
    L.append('PROYECTO  %s · TD %s · %d nodos · meta %.0f fps · linea de tiempo %s · tiempo real %s · perform %s'
             % (project.name, app.build, len(ops), project.cookRate, 'CORRIENDO' if reloj.play else 'EN PAUSA  <<<',
                'si' if project.realTime else 'NO  <<<', 'si' if ui.performMode else 'no'))
    # errores y avisos
    err = [o for o in ops if o.errors(recurse=False) or o.scriptErrors(recurse=False)]
    avi = [o for o in ops if '/audioAnalysis/' not in o.path and o.warnings(recurse=False) and o not in err]
    L.append('ERRORES   %d%s' % (len(err), '' if not err else ': ' + corto(o.path for o in err)))
    L.append('AVISOS    %d%s' % (len(avi), '' if not avi else ': ' + corto(o.path for o in avi)))
    # archivos, dispositivos, tipografias
    base = project.folder.replace('\\', '/').rstrip('/').lower()
    faltan, lejos, disp, letras = [], [], [], []
    for o in ops:
        if o.OPType in ('moviefileoutTOP', 'annotateCOMP'):      # los recuadros imprimen AttributeError al leerlos
            continue
        try:
            for p in o.pars():
                if p.style not in ('File', 'Folder'):
                    continue
                v = p.eval()
                v = '' if v is None else str(v).strip()
                if not v or v == 'None' or '://' in v:
                    continue
                ruta = v if os.path.isabs(v) else project.folder + '/' + v
                if not os.path.exists(ruta):
                    faltan.append('%s.%s = %s' % (o.path, p.name, v[-50:]))
                elif os.path.isabs(v) and not ruta.replace('\\', '/').lower().startswith(base):
                    lejos.append('%s.%s = %s' % (o.path, p.name, v[-50:]))
        except Exception:
            pass
        if o.OPType in ('videodeviceinTOP', 'audiodeviceinCHOP', 'audiodeviceoutCHOP'):
            p = getattr(o.par, 'device', None)
            act = getattr(o.par, 'active', None)
            if p is not None and (act is None or act.eval()) and p.eval() not in p.menuNames:
                disp.append('%s (%s)' % (o.path, str(p.eval())[-30:] or 'sin elegir'))
        if o.OPType == 'textTOP':
            if not o.par.fontfile.eval() and o.par.font.eval() not in o.par.font.menuNames:
                letras.append('%s (%s)' % (o.path, o.par.font.eval()))
    L.append('ARCHIVOS QUE FALTAN        %d%s' % (len(faltan), '' if not faltan else ': ' + corto(faltan, 20)))
    L.append('ARCHIVOS FUERA DE LA CARPETA DEL SHOW (se pierden al cambiar de computadora)  %d%s'
             % (len(lejos), '' if not lejos else ': ' + corto(lejos, 8)))
    L.append('DISPOSITIVOS PRENDIDOS QUE NO APARECEN  %d%s' % (len(disp), '' if not disp else ': ' + corto(disp, 8)))
    L.append('TIPOGRAFIAS QUE NO ESTAN EN ESTA COMPUTADORA  %d%s' % (len(letras), '' if not letras else ': ' + corto(letras)))
    # memoria de video
    show = op('/project2/show')
    W = H = None
    if show is not None and getattr(show.par, 'W', None) is not None:
        W, H = int(show.par.W), int(show.par.H)
    tops = [o for o in ops if o.isTOP]
    f = absTime.frame
    usados = [o for o in tops if f - o.cookAbsFrame < 120]      # OJO: pedir .width a un TOP dormido lo cocina y le reserva memoria
    mem = sorted(((getattr(o, 'gpuMemory', 0) or 0, o) for o in tops), key=lambda x: -x[0])
    total = sum(m for m, _ in mem) / 1e6
    L.append('MEMORIA DE VIDEO  %.0f MB en %d TOP (%d en uso)%s · los mas pesados: %s'
             % (total, len(tops), len(usados), '' if W is None else ' · show %dx%d' % (W, H),
                corto(('%s %.0f MB' % (o.path, m / 1e6) for m, o in mem[:5]), 5)))
    if W:
        gr = [o for o in usados if o.width * o.height > W * H * 1.01]
        L.append('TOP MAS GRANDES QUE LA SALIDA  %d%s' % (len(gr), '' if not gr else ': ' + corto(('%s %dx%d' % (o.path, o.width, o.height) for o in gr))))
    # peso muerto
    muertos = [c for r in R.children if r.isCOMP and r.name not in SISTEMA
               for c in r.findChildren(type=COMP) if c.name in ('_respaldo', '_descartados')]
    for c in muertos:
        n = len(c.findChildren())
        L.append('GUARDADO SIN USAR  %s: %d nodos · %s' % (c.path, n, 'no cocina' if not c.allowCooking else 'COCINA  <<<'))
    # como esta puesto el rig (solo lo que exista)
    E = op('/project2/base17/escena_modular')
    lista = []
    for o, n, quiero in ((show, 'Master', 1.0), (show, 'Tituloaire', False), (show, 'Pantallas', False),
                         (show, 'Modoshow', None), (show, 'Demo', False), (show, 'Rec', False),
                         (show, 'Envivo', None), (E, 'Bypass', False), (E, 'Modoescena', None)):
        p = getattr(o.par, n, None) if o is not None else None
        if p is None:
            continue
        v = p.eval()
        mal = quiero is not None and (abs(v - quiero) > 0.001 if isinstance(quiero, float) else bool(v) != quiero)
        lista.append('%s=%s%s' % (n, round(v, 2) if isinstance(v, float) else v, '  <<<' if mal else ''))
    if lista:
        L.append('COMO ESTA PUESTO  ' + ' · '.join(lista))
    L.append('(revision en frio: %.1f s)' % (time.perf_counter() - t0))
    return L


def arrancar():
    L = revisar()
    show = op('/project2/show')
    E = op('/project2/base17/escena_modular')
    pasos = [('base', 'como estaba')]
    s = {'fase': 'corriendo', 'frio': L, 'res': [], 'log': [], 'i': 0, 'n': 0, 'dts': [], 't': None,
         'asiento': ASIENTO, 'medir': MEDIR, 'meta': project.cookRate, 'cuando': time.strftime('%Y%m%d_%H%M')}
    if ESCENAS and E is not None and getattr(E.par, 'Modoescena', None) is not None:
        s['escena'], s['escena0'] = E.path, E.par.Modoescena.eval()
        pasos += [('escena', n) for n in E.par.Modoescena.menuNames]
        pasos.append(('escena', s['escena0']))          # regresa a la que estaba antes del titulo
    if TITULO and show is not None and getattr(show.par, 'Tituloaire', None) is not None:
        s['show'], s['tit'] = show.path, True
        pasos.append(('titulo', 'titulo al aire'))
    s['pasos'] = pasos
    if not R.time.play:
        R.time.play = True
    R.store('preshow', s)
    d = R.op('preshow_tick') or R.create(executeDAT, 'preshow_tick')
    d.text = TICK
    d.par.frameend = True
    d.par.active = True
    seg = len(pasos) * (ASIENTO + MEDIR + 1) / max(project.cookRate, 1)
    print('[ok] revision hecha y prueba corriendo: %d pasos, ~%.0f s. Volver a correr este script para ver el reporte.' % (len(pasos), seg))


def reporte(s):
    meta = s['meta']
    L = ['PRUEBA PRE-SHOW  ' + s['cuando'], ''] + s['frio'] + ['']
    res = s['res']
    b = next((r for r in res if r['tipo'] == 'base'), None)
    if b:
        L.append('RENDIMIENTO COMO ESTABA  %.1f de %.0f fps · peor cuadro %.0f ms · GPU de los nodos %.1f ms'
                 % (b['fps'], meta, b['peor'], b['gpu']))
        L.append('  donde se va el tiempo (ms): ' + corto(('%s %.1f' % kv for kv in b['cont']), 6))
        L.append('  nodos mas caros (ms): ' + corto(('%s %.1f' % (p, v) for v, p in b['caros']), 6))
    esc = [r for r in res if r['tipo'] == 'escena'][:-1]     # el ultimo solo regresa a la escena que estaba
    if esc:
        esc.sort(key=lambda r: r['fps'])
        bien = [r for r in esc if r['fps'] >= meta * 0.95]
        L.append('')
        L.append('ESCENAS  %d probadas · %d a 95 %% o mas de la meta · la mas lenta %s (%.1f fps) · la mas rapida %s (%.1f fps)'
                 % (len(esc), len(bien), esc[0]['cual'], esc[0]['fps'], esc[-1]['cual'], esc[-1]['fps']))
        for r in esc:
            extra = ''
            if len(r.get('cocinan', [])) != 1:
                extra += ' · cocinan %d: %s' % (len(r['cocinan']), corto(r['cocinan'], 4))
            if r.get('err'):
                extra += ' · SHADER: ' + r['err'].replace(chr(10), ' ')
            L.append('  %-28s %5.1f fps · peor %4.0f ms · GPU %5.1f ms%s' % (r['cual'], r['fps'], r['peor'], r['gpu'], extra))
        L.append('  la mas lenta, nodos mas caros (ms): ' + corto(('%s %.1f' % (p, v) for v, p in esc[0]['caros']), 6))
    t = next((r for r in res if r['tipo'] == 'titulo'), None)
    if t:
        L.append('')
        L.append('TITULO AL AIRE  %.1f fps · peor %.0f ms · %s' % (t['fps'], t['peor'], 'SALIO' if t['activo'] > 0 else 'NO SALIO  <<<'))
    for x in s['log']:
        L.append('OJO: ' + x)
    return L


s = R.fetch('preshow', None, search=False, storeDefault=False)
if CANCELAR:
    if s:
        s['fase'] = 'cancelado'
        try:
            if s.get('escena'):
                op(s['escena']).par.Modoescena = s['escena0']
            if s.get('tit'):
                op(s['show']).par.Tituloaire = False
        except Exception as x:
            print('no pude regresar todo:', x)
        R.unstore('preshow')
    if R.op('preshow_tick'):
        R.op('preshow_tick').destroy()
    print('[ok] prueba cancelada')
elif s and s.get('fase') == 'corriendo':
    print('corriendo: paso %d de %d (%s)' % (s['i'] + 1, len(s['pasos']), s['pasos'][min(s['i'], len(s['pasos']) - 1)][1]))
elif s and s.get('fase') == 'listo':
    L = reporte(s)
    carpeta = project.folder + '/exports'
    if not os.path.isdir(carpeta):
        carpeta = project.folder
    with open('%s/preshow_%s.txt' % (carpeta, s['cuando']), 'w', encoding='utf-8') as f:
        f.write(chr(10).join(L))
    print(chr(10).join(L))
    R.unstore('preshow')
    if R.op('preshow_tick'):
        R.op('preshow_tick').destroy()
elif SOLO_FRIO:
    print(chr(10).join(revisar()))
else:
    arrancar()
