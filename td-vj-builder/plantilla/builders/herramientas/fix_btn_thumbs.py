# fix_btn_thumbs.py — agrega ACTUALIZAR THUMBS y RESET FEEDBACK a la UI ya construida, sin reconstruirla (idempotente).
# Lo mismo que hace setup_ui.py desde cero, pero respetando los ajustes a mano de /project2/ui_perform.
ESC = '/project2/base17/escena_modular'
W, H, TOP_H = 1920, 1080, 56
ui = op('/project2/ui_perform')

# ui_lib: el mismo texto de setup_ui.py
src = open(project.folder + '/builders/herramientas/setup_ui.py', encoding='utf-8').read()
a = src.index("UI_LIB = '''") + len("UI_LIB = '''")
b = src.index("''' % ((ESC,)*6)")
ui.op('ui_lib').text = src[a:b] % ((ESC,) * 6)

# Cada thumb guarda de donde se captura y a donde se guarda
n = 0
for c in ui.children:
    if not (c.isCOMP and c.name.startswith('th_')):
        continue
    img = c.op('img_p/img')
    if img is None:          # th_cam_N son en vivo: no tienen imagen capturada
        continue
    ruta = img.par.file.eval()
    fid = ruta.rsplit('/', 1)[1].rsplit('.', 1)[0]
    if fid == 'fx_off':
        top = op(ESC + '/master_video')
    elif fid.startswith('layout_'):
        top = op(ESC + '/' + fid + '/out1')
    else:
        top = op('/project2/' + fid + '/out1')
    if top is None:
        print('[aviso] sin fuente:', c.name, fid)
        continue
    c.store('fuente', top.path)
    c.store('ruta', ruta)
    n += 1


def boton(nombre, x, txt, rgb, tipo):
    t = ui.op(nombre) or ui.create(textCOMP, nombre)
    t.par.x, t.par.y, t.par.w, t.par.h = x, H - TOP_H + 4, 220, TOP_H - 8
    t.par.text = txt
    t.par.fontsize = 15
    for nb in ('fontbold', 'bold'):
        if hasattr(t.par, nb):
            setattr(t.par, nb, True)
    t.par.bgcolorr, t.par.bgcolorg, t.par.bgcolorb, t.par.bgalpha = rgb[0], rgb[1], rgb[2], 1.0
    t.store('tipo', tipo)
    t.store('dato', '')
    return t


# Botones: a la derecha de la barra superior
ui.op('titulo').par.w = W - 470
b1 = boton('btn_thumbs', W - 460, 'ACTUALIZAR THUMBS', (0.25, 0.25, 0.27), 'THUMBS')
b2 = boton('btn_resetfb', W - 230, 'RESET FEEDBACK', (0.55, 0.12, 0.12), 'RESETFB')

paneles = ui.op('th_click').par.panels.eval()
print('[ok] thumbs con fuente:', n, '| en th_click:', b1 in paneles, b2 in paneles)
