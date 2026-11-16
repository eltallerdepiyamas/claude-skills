# setup_salida_led.py — separa "abrir la ventana del LED" de "test pattern" (2026-11-14).
#
# Antes: /project1/perform_test (Window COMP que muestra test_switch = show final o test) se abria
# y cerraba con show.Pantallas, o sea solo existia mientras el test pattern estaba prendido.
# Ahora:
#   show.Salidaled  (pestaña Pantallas, "Salida al LED")  -> abre / cierra perform_test
#   show.Pantallas  (igual que antes)                     -> SOLO cambia lo que se ve: 0 = show · 1 = test
# Con Salidaled prendido la ventana va sin bordes (aunque Pantallacompleta este apagado).
# Si el proyecto se abre con Salidaled prendido, la ventana se abre sola (perform_test_start).
# Re-correr setup_test_pantallas.py regresa el comportamiento viejo: correr este despues.
#
# QUITAR = True: borra Salidaled y perform_test_start y regresa el watcher a Pantallas.
QUITAR = False

s = op('/project2/show')
p1 = op('/project1')
pw = p1.op('perform_test')
watch = p1.op('perform_test_watch')
if s is None or pw is None or watch is None:
    print('[falla] falta /project2/show, perform_test o perform_test_watch: correr antes setup_test_pantallas.py')
else:
    pg = next((p for p in s.customPages if p.name == 'Pantallas'), None)
    BORDES_VIEJO = "0 if op('/project2/show').par.Pantallacompleta.eval() else 1"
    if QUITAR:
        if hasattr(s.par, 'Salidaled'):
            s.par.Salidaled.destroy()
        st = p1.op('perform_test_start')
        if st is not None:
            st.destroy()
        watch.par.pars = 'Pantallas'
        watch.text = watch.text.replace("par.name == 'Salidaled'", "True")
        pw.par.borders.expr = BORDES_VIEJO
        print('[ok] quitado: la ventana vuelve a abrirse con Pantallas')
    else:
        if not hasattr(s.par, 'Salidaled'):
            t = pg.appendToggle('Salidaled', label='Salida al LED')[0]
            t.default = False
            nombres = [p.name for p in pg.pars]
            pg.sort(*(['Salidaled'] + [n for n in nombres if n != 'Salidaled']))
        watch.par.pars = 'Salidaled'
        watch.text = '''# abre / cierra /project1/perform_test (salida al LED) segun /project2/show.Salidaled
# (lo instala builders/herramientas/setup_salida_led.py). Pantallas solo cambia show <-> test.
def onValueChange(par, prev):
    pw = op('/project1/perform_test')
    if pw is None:
        return
    if par.eval():
        pw.par.winopen.pulse()
    else:
        pw.par.winclose.pulse()
'''
        pw.par.borders.expr = ("0 if (op('/project2/show').par.Pantallacompleta.eval() "
                               "or op('/project2/show').par.Salidaled.eval()) else 1")
        st = p1.op('perform_test_start') or p1.create(executeDAT, 'perform_test_start')
        st.nodeX, st.nodeY = watch.nodeX, watch.nodeY - 150
        st.tags.add('tdvj_test_pantallas')
        st.par.start = True
        st.text = '''# al abrir el proyecto: si Salida al LED quedo prendida, abre la ventana del LED
def onStart():
    s = op('/project2/show')
    if s is not None and s.par.Salidaled.eval():
        run("op('/project1/perform_test').par.winopen.pulse()", delayFrames=30)
    return
'''
        print('[ok] Salida al LED separada del test pattern')
