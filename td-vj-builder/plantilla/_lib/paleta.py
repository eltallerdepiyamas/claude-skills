"""
paleta.py — paleta del álbum (Río Salvaje): la ÚNICA fuente de color de los layouts.

Estándar del show (2026-11-04): el slider 4 (color) de cada layout tiñe la cámara con estos colores,
como los discos de Playeras (albumTint en el shader). Nada de hue / chroma / RGB delay.
Todos los layouts reciben Color1..5 = ALBUM, en este orden, y layout_core los vuelve a poner en cada
build (no se editan a mano en TD: para cambiar la paleta se cambia aquí y se corre build_all.py).
Los fondos / halos que usan un color de aquí (CREMA, NEGRO...) también se reponen en cada build.
"""

AMARILLO = (0.96, 0.76, 0.06)
VERDE    = (0.09, 0.53, 0.36)
AZUL     = (0.10, 0.33, 0.78)
NEGRO    = (0.06, 0.06, 0.07)
ROJO     = (0.87, 0.12, 0.13)
CREMA    = (0.93, 0.91, 0.86)

ALBUM = [AMARILLO, VERDE, AZUL, NEGRO, ROJO]          # uColor1..5 (el orden importa: albumColor(i))
# proyecto.json manda: 5 colores (en orden) + fondo. Si falta, quedan los de arriba.
import json as _json, os as _os
_cfg = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'proyecto.json')
if _os.path.exists(_cfg):
    _p = _json.load(open(_cfg, encoding='utf-8')).get('paleta', {})
    if len(_p.get('colores', [])) == 5:
        ALBUM = [tuple(c['rgb']) for c in _p['colores']]
    if _p.get('fondo'):
        CREMA = tuple(_p['fondo']['rgb'])
TODOS = ALBUM + [CREMA]


def con_album(colors):
    """colors del builder + Color1..5 del álbum (los del builder con esos nombres se reemplazan)."""
    propios = [c for c in colors if c[0] not in ('Color1', 'Color2', 'Color3', 'Color4', 'Color5')]
    return [('Color%d' % (i + 1), 'uColor%d' % (i + 1), c) for i, c in enumerate(ALBUM)] + propios


def es_del_album(rgb):
    return any(all(abs(a - b) < 1e-4 for a, b in zip(rgb, c)) for c in TODOS)
