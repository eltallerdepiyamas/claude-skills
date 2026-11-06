"""
nuevo_proyecto.py — arranca un show nuevo desde el boilerplate de td-vj-builder.

    python nuevo_proyecto.py "<carpeta del proyecto>/01. EDITABLES" "NOMBRE DEL SHOW"

Copia plantilla/ (con BOILERPLATE.toe, renombrado al show) sin pisar archivos que ya existan,
llena CLAUDE.md y proyecto.json con el nombre, y deja en _lib/BOILERPLATE_VERSION el commit del repo de skills que se usó.
El proyecto queda con SU copia del núcleo: actualizar la skill no cambia un show ya armado.
Para traer un núcleo nuevo a un show: copia a mano boilerplate/_lib/tdvj_core.py.
"""
import datetime
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'plantilla')


def _version():
    try:
        return subprocess.check_output(['git', '-C', HERE, 'rev-parse', '--short', 'HEAD'],
                                       text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return 'sin-git'


def main(dst, name):
    os.makedirs(dst, exist_ok=True)
    copied, skipped = 0, 0
    for folder, _dirs, files in os.walk(SRC):
        rel = os.path.relpath(folder, SRC)
        os.makedirs(os.path.join(dst, rel), exist_ok=True)
        for f in files:
            destino = name + '.toe' if f == 'BOILERPLATE.toe' else f
            target = os.path.join(dst, rel, destino)
            if os.path.exists(target):
                skipped += 1
                continue
            shutil.copy2(os.path.join(folder, f), target)
            copied += 1

    version = _version()
    claude = os.path.join(dst, 'CLAUDE.md')
    with open(claude, encoding='utf-8') as fh:
        text = fh.read()
    text = (text.replace('{{PROYECTO}}', name).replace('{{VERSION}}', version)
                .replace('{{FECHA}}', datetime.date.today().isoformat()))
    with open(claude, 'w', encoding='utf-8') as fh:
        fh.write(text)
    cfg_path = os.path.join(dst, 'proyecto.json')
    with open(cfg_path, encoding='utf-8') as fh:
        cfg = json.load(fh)
    if not cfg.get('nombre'):
        cfg['nombre'] = name
        with open(cfg_path, 'w', encoding='utf-8') as fh:
            json.dump(cfg, fh, ensure_ascii=False, indent=2)
    with open(os.path.join(dst, '_lib', 'BOILERPLATE_VERSION'), 'w', encoding='utf-8') as fh:
        fh.write(version + '\n')
    print('[ok] %s: %d archivos copiados, %d ya existían (no se tocaron). Boilerplate %s'
          % (dst, copied, skipped, version))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
