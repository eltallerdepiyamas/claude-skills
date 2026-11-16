# ─────────────────────────────────────────────────────────────
# setup_lut_camaras.py — LUT por camara (1 archivo compartido, 6 toggles).
#
# TD 2023 no tiene LUT TOP (.cube) nativo; lookupTOP solo hace 1D por canal. Para un 3D
# LUT real usamos un glslTOP con shader de Hald lookup (shaders/master/hald_lookup.frag),
# que samplea una imagen Hald CLUT.
#
# Para convertir un .cube a Hald:
#   ffmpeg -y -f lavfi -i "haldclutsrc=8,lut3d=<file.cube>" -frames:v 1 hald_<nombre>.png
#   (level 8 → 512x512, 64 colores/dim, 64^3 muestras. Default ffmpeg = 6 → 216x216.)
#
# Inserta en /project2/base17/escena_modular, por cada N:
#   cam_lut_file         (moviefileinTOP) - carga show.Lutarchivo, compartido por los 6
#   cam_lut_pixel        (textDAT)        - hald_lookup.frag (compartido por los 6)
#   camN_lut             (glslTOP)        - aplica Hald: input 0 = camN_fuente, 1 = cam_lut_file
#   camN_lut_sw          (switchTOP)      - 0 = camN_fuente (sin LUT), 1 = camN_lut (con LUT)
#                                           index = int(Luton{N})  → toggle por camara
#
# Cadena final por cámara: camN_fuente -> camN_lut_sw -> CAM_N (correccion_camara)
# El LUT se aplica a lo que sea que esa cámara muestre: sólido, stock o vivo.
# (Antes: solo a camN_vivo. Reconectamos camN_fuente entrada vivo directo a camN_vivo
# si quedó colgado de una versión anterior.)
#
# En /project2/show, pestana LUT (separada de Camaras):
#   Lutarchivo      File   (Hald .png)  — un solo archivo para los 6
#   Lutlevel        Int    (auto-detect del ancho del PNG, readOnly)
#   Luton1..Luton6  Toggle (default OFF — prender la camara que lo necesite)
#   Luttodas        Pulse  — prende los 6
#   Lutninguna      Pulse  — apaga los 6
#
# Idempotente: nodos con tag 'tdvj_lut_cam' se reusan.
#
# Uso (Textport):
#   exec(open(project.folder + '/builders/herramientas/setup_lut_camaras.py', encoding='utf-8').read())
# ─────────────────────────────────────────────────────────────

TAG = 'tdvj_lut_cam'
N_CAMS = 6
SCENE_PATH = '/project2/base17/escena_modular'
SHADER = 'shaders/master/hald_lookup.frag'

scene = op(SCENE_PATH)
show = op('/project2/show')
if scene is None:
    raise SystemExit('[err] No existe %s' % SCENE_PATH)
if show is None:
    raise SystemExit('[err] No existe /project2/show')
print('[run] setup_lut_camaras: scene=%s' % scene.path)

# ---------- 1. pestana LUT: parametros ----------
pg = next((g for g in show.customPages if g.name == 'LUT'), None) or show.appendCustomPage('LUT')

# si quedaron params viejos en la pestana Camaras (version anterior), los migramos a LUT
# preservando valor + expresion. Algunos nombres (Seplut) los dejamos atras y no re-creamos.
_VIEJOS = {'Seplut', 'Lutarchivo', 'Lutlevel',
           'Luton1', 'Luton2', 'Luton3', 'Luton4', 'Luton5', 'Luton6',
           'Luttodas', 'Lutninguna'}
_MIGRAR = {}  # name -> {val, expr, mode}
for pg_otra in list(show.customPages):
    if pg_otra is pg:
        continue
    for p in list(pg_otra.pars):
        if p.name in _VIEJOS and p.name != 'Seplut':
            _MIGRAR[p.name] = {
                'val': p.eval() if p.mode != ParMode.EXPRESSION else None,
                'expr': p.expr if p.mode == ParMode.EXPRESSION else '',
                'mode': p.mode,
            }
        if p.name in _VIEJOS:
            try: p.destroy()
            except Exception as e: print('[warn] no pude borrar %s de %s:', p.name, pg_otra.name, e)

def _ensure(name, label, append, **kw):
    for p in pg.pars:
        if p.name == name:
            p.label = label
            for k, v in kw.items():
                setattr(p, k, v)
            return p
    tup = append(name, label=label)
    p = tup[0] if isinstance(tup, (list, tuple)) else tup
    for k, v in kw.items():
        setattr(p, k, v)
    # restaurar valor migrado si venía de la pestaña vieja
    mig = _MIGRAR.get(name)
    if mig:
        if mig['mode'] == ParMode.EXPRESSION and mig['expr']:
            p.expr = mig['expr']
        elif mig['val'] is not None:
            try: p.val = mig['val']
            except Exception: pass
    return p

_LUTMEZCLA_NUEVO = getattr(show.par, 'Lutmezcla', None) is None
_ensure('Lutarchivo', 'LUT archivo (Hald .png)', pg.appendFile)
p_lv = _ensure('Lutlevel', 'LUT level (auto del tamano del PNG)', pg.appendInt)
p_lv.min, p_lv.max = 2, 16
p_lv.normMin, p_lv.normMax = 2, 16
p_lv.clampMin = p_lv.clampMax = True
p_lv.default = 8
# raiz cubica del ancho del Hald: 512 → 8, 216 → 6, 64 → 4. Usuario no tiene que tocarlo.
p_lv.expr = ("max(2, int(round(op('%s/cam_lut_file').width ** (1/3)))) "
             "if op('%s/cam_lut_file').width > 0 else 8") % (SCENE_PATH, SCENE_PATH)
p_lv.readOnly = True
# intensidad del LUT: 0 = camara tal cual · 1 = LUT completo (uMezcla del shader). Este si se mueve en vivo.
p_mz = _ensure('Lutmezcla', 'LUT intensidad', pg.appendFloat)
p_mz.min, p_mz.max, p_mz.normMin, p_mz.normMax = 0.0, 1.0, 0.0, 1.0
p_mz.clampMin = p_mz.clampMax = True
p_mz.default = 1.0
if _LUTMEZCLA_NUEVO:
    p_mz.val = 1.0
for i in range(1, N_CAMS + 1):
    _ensure('Luton%d' % i, 'LUT Cam %d' % i, pg.appendToggle)
_ensure('Luttodas', 'LUT prender todas', pg.appendPulse)
_ensure('Lutninguna', 'LUT apagar todas', pg.appendPulse)

# orden de la pagina LUT
try:
    pg.sort('Lutarchivo', 'Lutmezcla', 'Lutlevel',
            *['Luton%d' % i for i in range(1, N_CAMS + 1)],
            'Luttodas', 'Lutninguna')
except Exception as e:
    print('[warn] no pude ordenar pestana LUT:', e)

# ---------- 2. nodos compartidos (archivo LUT + shader) ----------
lut_file = scene.op('cam_lut_file')
if lut_file is None:
    lut_file = scene.create(moviefileinTOP, 'cam_lut_file')
    lut_file.tags.add(TAG)
    ref = scene.op('CAM_1')
    lut_file.nodeX = (ref.nodeX - 400) if ref is not None else -800
    lut_file.nodeY = (ref.nodeY + 400) if ref is not None else 400
lut_file.par.file.expr = "op('/project2/show').par.Lutarchivo.eval()"
# nearest: el shader samplea centros de pixel; con linear los vecinos no son colores vecinos
if hasattr(lut_file.par, 'inputfiltertype'):
    lut_file.par.inputfiltertype = 'nearest'

pix = scene.op('cam_lut_pixel')
if pix is None:
    pix = scene.create(textDAT, 'cam_lut_pixel')
    pix.tags.add(TAG)
    pix.nodeX, pix.nodeY = lut_file.nodeX, lut_file.nodeY + 150
pix.par.file = SHADER
pix.par.syncfile = True

# ---------- 3. glslTOP por camara (Hald lookup) ----------
# si quedaron lookupTOPs de una version anterior, los reemplazamos
for i in range(1, N_CAMS + 1):
    viejo = scene.op('cam%d_lut' % i)
    if viejo is not None and viejo.OPType != 'glslTOP':
        print('[info] cam%d_lut era %s, lo rehacemos como glslTOP' % (i, viejo.OPType))
        try: viejo.destroy()
        except Exception as e: print('  no pude destruirlo:', e)
insertados, saltadas = [], []
for i in range(1, N_CAMS + 1):
    vivo = scene.op('cam%d_vivo' % i)
    fuente = scene.op('cam%d_fuente' % i)
    cam_n = scene.op('CAM_%d' % i)  # glslTOP correccion_camara
    if vivo is None or fuente is None or cam_n is None:
        saltadas.append('cam%d (vivo=%s, fuente=%s, CAM_%d=%s)' % (
            i, bool(vivo), bool(fuente), i, bool(cam_n)))
        continue

    lut_prev = scene.op('cam%d_lut' % i)
    sw_prev = scene.op('cam%d_lut_sw' % i)

    # --- limpieza de la versión vieja (LUT entre vivo y fuente) ---
    # si camN_fuente tiene su entrada "vivo" (idx 2 por convención) apuntando al sw/lut
    # viejo, la reconectamos directo a camN_vivo.
    IDX_VIVO = 2
    if IDX_VIVO < len(fuente.inputConnectors):
        c = fuente.inputConnectors[IDX_VIVO].connections
        owner = c[0].owner if c else None
        if owner is not None and owner is not vivo and owner in (lut_prev, sw_prev):
            try: fuente.inputConnectors[IDX_VIVO].disconnect()
            except Exception: pass
            fuente.inputConnectors[IDX_VIVO].connect(vivo)

    # --- crear/ajustar el glslTOP camN_lut ---
    lut = scene.op('cam%d_lut' % i)  # podria haber sido destruido arriba si era lookupTOP
    es_nuevo = lut is None
    if es_nuevo:
        lut = scene.create(glslTOP, 'cam%d_lut' % i)
        lut.tags.add(TAG)
        lut.nodeX, lut.nodeY = fuente.nodeX + 200, fuente.nodeY

    lut.par.pixeldat = pix
    lut.par.outputresolution = 'useinput'
    if hasattr(lut.par, 'vec0name'):
        lut.par.vec0name = 'uLevel'
        lut.par.vec0valuex.expr = "op('/project2/show').par.Lutlevel.eval()"
        lut.par.vec1name = 'uMezcla'
        lut.par.vec1valuex.expr = "op('/project2/show').par.Lutmezcla.eval()"

    # input 0 = SALIDA del switch de fuente (sol / stock / vivo, lo que elija)
    c0 = lut.inputConnectors[0].connections
    if not c0 or c0[0].owner is not fuente:
        try: lut.inputConnectors[0].disconnect()
        except Exception: pass
        lut.inputConnectors[0].connect(fuente)

    # input 1 = archivo LUT compartido
    c1 = lut.inputConnectors[1].connections
    if not c1 or c1[0].owner is not lut_file:
        try: lut.inputConnectors[1].disconnect()
        except Exception: pass
        lut.inputConnectors[1].connect(lut_file)

    # --- switch de bypass por camara: 0 = fuente directa, 1 = fuente con LUT ---
    sw = scene.op('cam%d_lut_sw' % i)
    if sw is None:
        sw = scene.create(switchTOP, 'cam%d_lut_sw' % i)
        sw.tags.add(TAG)
        sw.nodeX, sw.nodeY = lut.nodeX + 200, lut.nodeY
    for conn in sw.inputConnectors:
        try: conn.disconnect()
        except Exception: pass
    sw.inputConnectors[0].connect(fuente)
    sw.inputConnectors[1].connect(lut)
    sw.par.index.expr = "int(op('/project2/show').par.Luton%d.eval())" % i

    # --- insertar el switch antes de CAM_N (correccion_camara) ---
    c_cam = cam_n.inputConnectors[0].connections
    if not c_cam or c_cam[0].owner is not sw:
        try: cam_n.inputConnectors[0].disconnect()
        except Exception: pass
        cam_n.inputConnectors[0].connect(sw)

    if es_nuevo:
        insertados.append('cam%d' % i)

# ---------- 4. DAT para pulsos Luttodas / Lutninguna ----------
watch = show.op('lut_camaras_watch')
if watch is None:
    watch = show.create(parameterexecuteDAT, 'lut_camaras_watch')
    watch.tags.add(TAG)
    watch.nodeX, watch.nodeY = 400, -400
watch.par.ops = '/project2/show'
watch.par.pars = 'Luttodas Lutninguna'
watch.par.valuechange = False
watch.par.onpulse = True
watch.text = '''# LUT camaras: pulsos globales (prender/apagar los 6 toggles)
def onPulse(par):
    show = op('/project2/show')
    on = (par.name == 'Luttodas')
    for i in range(1, 7):
        p = getattr(show.par, 'Luton%d' % i, None)
        if p is not None:
            p.val = on
'''

print('[ok] LUT camaras listo')
print('     nuevos: %s' % (', '.join(insertados) if insertados else 'ninguno'))
if saltadas:
    print('     saltadas: %s' % ', '.join(saltadas))
print('     pestana LUT en /project2/show: Lutarchivo + Lutlevel + Luton1..6 + Luttodas / Lutninguna')
