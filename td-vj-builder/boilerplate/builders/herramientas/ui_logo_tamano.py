# ui_logo_tamano.py: muestra la pagina Logo (Tamano logo) en el panel CONTROLES de la UI sin rehacer toda la UI.
# (setup_ui.py ya la incluye; esto es para un show ya armado)
hechos = []
for pc in op('/').findChildren(name='par_show_hub', type=parameterCOMP):
    s = pc.par.pagescope.eval()
    if 'Logo' not in s.split():
        pc.par.pagescope = s.replace('Paleta', 'Paleta Logo') if 'Paleta' in s else s + ' Logo'
    hechos.append('%s -> %s' % (pc.path, pc.par.pagescope.eval()))
print(hechos or 'no encontre par_show_hub')
