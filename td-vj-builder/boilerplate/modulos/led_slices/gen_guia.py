# gen_guia.py — guia PIXEL MAP hecha desde el XML de Advanced Output de Resolume (cada slice con su nombre, cruz,
# borde, coordenadas y un triangulo hacia ARRIBA). Sirve de Prueba > Guia en TD y de Output Guide en Resolume.
# Correr con Python normal (necesita Pillow), fuera de TD:
#   python modulos/led_slices/gen_guia.py "<ruta del XML>" ["<PNG de salida>"]
# Sin PNG de salida: junto al XML, "<nombre del XML>_guia.png". Poner esa ruta en proyecto.json -> slices -> guia
# (o en el parametro Guia de /project1/slices).
import os
import sys
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

if len(sys.argv) < 2:
    sys.exit('uso: python gen_guia.py "<XML de Advanced Output>" ["<PNG de salida>"]')
XML = sys.argv[1]
SAL = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(XML)[0] + '_guia.png'

r = ET.parse(XML).getroot()
d = r.find('.//OutputDeviceDisplay')
W, H = (int(d.get('width')), int(d.get('height'))) if d is not None and d.get('width') else (1920, 1080)
TINTAS = [(200, 40, 55), (40, 150, 110), (60, 80, 200), (200, 150, 40), (150, 60, 190), (40, 150, 190)]
img = Image.new('RGB', (W, H), (0, 0, 0))
dr = ImageDraw.Draw(img)


def fuente(n, negrita=True):
    for f in (('arialbd' if negrita else 'arial') + '.ttf', 'DejaVuSans-Bold.ttf' if negrita else 'DejaVuSans.ttf'):
        for base in ('C:/Windows/Fonts/', '/Library/Fonts/', '/usr/share/fonts/truetype/dejavu/', ''):
            try:
                return ImageFont.truetype(base + f, n)
            except Exception:
                pass
    return ImageFont.load_default()


slices = []
for sl in r.iter('Slice'):
    nom = next((p.get('value') for p in sl.iter('Param') if p.get('name') == 'Name'), '?')
    o = [(float(v.get('x')), float(v.get('y'))) for v in sl.find('OutputRect').findall('v')]
    slices.append((nom, min(p[0] for p in o), min(p[1] for p in o), max(p[0] for p in o), max(p[1] for p in o)))
filas = sorted({s[0].split('-')[0] for s in slices})          # una tinta por prefijo (A-, B-, ...)
for nom, x0, y0, x1, y1 in slices:
    c = TINTAS[filas.index(nom.split('-')[0]) % len(TINTAS)]
    dr.rectangle([x0, y0, x1 - 1, y1 - 1], fill=tuple(int(v * 0.25) for v in c))
    cx, cy, rr = (x0 + x1) / 2, (y0 + y1) / 2, min(x1 - x0, y1 - y0) * 0.42
    dr.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=c, outline=(255, 255, 255), width=3)
    dr.line([cx, y0, cx, y1], fill=(255, 255, 255), width=2)
    dr.line([x0, cy, x1, cy], fill=(255, 255, 255), width=2)
    dr.text((cx, cy), nom, font=fuente(int(min(x1 - x0, y1 - y0) * 0.3)), fill=(255, 255, 255), anchor='mm',
            stroke_width=5, stroke_fill=(0, 0, 0))
    dr.text((x0 + 8, y1 - 8), '%d,%d  %dx%d' % (round(x0), round(y0), round(x1 - x0), round(y1 - y0)), font=fuente(18),
            fill=(255, 255, 255), anchor='ld', stroke_width=2, stroke_fill=(0, 0, 0))
    dr.polygon([(cx, y0 + 10), (cx - 14, y0 + 34), (cx + 14, y0 + 34)], fill=(255, 255, 255))     # ARRIBA
    dr.rectangle([x0, y0, x1 - 1, y1 - 1], outline=(255, 230, 0), width=3)
# texto: en la esquina con menos slices
libre = min(((10, 10), (W - 560, 10), (10, H - 190), (W - 560, H - 190)),
            key=lambda q: sum(1 for s in slices if s[1] < q[0] + 550 and s[3] > q[0] and s[2] < q[1] + 180 and s[4] > q[1]))
tx, ty = libre[0] + 20, libre[1] + 20
titulo, tam = 'PIXEL MAP · ' + os.path.splitext(os.path.basename(XML))[0], 26
while tam > 12 and dr.textlength(titulo, font=fuente(tam)) > 500:      # que quepa en su esquina sin pisar slices
    tam -= 1
dr.text((tx, ty), titulo, font=fuente(tam), fill=(255, 255, 255))
dr.text((tx, ty + 40), '%d slices · salida %dx%d · desde el XML de Advanced Output' % (len(slices), W, H),
        font=fuente(18, False), fill=(190, 190, 190))
dr.text((tx, ty + 68), 'triangulo = ARRIBA del slice', font=fuente(18, False), fill=(190, 190, 190))
img.save(SAL)
print('[ok]', SAL, '·', len(slices), 'slices:', ', '.join(s[0] for s in slices))
