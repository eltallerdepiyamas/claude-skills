# FIX: limpiar base1–base8 (restos de Paloma Murphy) y dejarlas para Petite Amie

Task para Claude Code. Ejecutar **antes** de correr los builders de visuales de `PETITE_AMIE_build.md`.

---

## Diagnóstico

`base1` y `base2` de `/project2` contienen shaders de **Paloma Murphy** (`glsl_marquee_frame`, `glsl_atomic_starburst`), no de Petite Amie. En algún momento se corrió `destroyCustomPars()` sobre esas bases: borró los Custom Parameters (`Intensity`, `Speed`, `Distort`, `Colormix`, `Density`/`Rays`, los `Color*`, y los propios del marquee: `Scale`, `Chasedir`, `Repeat`, `Gap`, `Chasemode`, `Tail`, `Rampstyle`) pero **dejó vivos los nodos** `glsl_marquee_frame` y `audio_util`.

Resultado: esos nodos huérfanos siguen referenciando en su página Vectors y en `audio_util` (línea 15) parámetros que ya no existen → cascada de `td.tdAttributeError: 'td.ParCollection' object has no attribute 'X'`.

**Causa raíz:** el `visual_builder.py` sólo destruye los nodos de su lista `managed` (`select_input`, `audio_in`, `glsl_gen`, `shader_pixel`, `switch1`, `null1`, `out1`). Los nodos de otro proyecto con nombres distintos sobreviven al rebuild. Media sobrescritura = red rota.

**Decisión de Sebas:** este `.toe` partió del proyecto de Paloma Murphy como plantilla, pero es un proyecto distinto (Petite Amie). Borrar por completo base1–base8 y reconstruir desde cero. Paloma Murphy tiene su propio `.toe`, así que no se pierde nada; este borrado es intencional.

---

## Parte 1 — script de limpieza a fondo

Crear `clean_bases.py` en la carpeta del proyecto. Vacía por completo cada base destino: destruye **todos** los children (no sólo los managed) y todos los Custom Parameters, protegiendo el propio baseX (nunca lo renombra ni lo destruye).

```python
"""
clean_bases.py — vacia por completo un rango de bases antes de reconstruir.
Destruye TODOS los children y TODOS los custom pars del baseX, sin tocar el
baseX en si (no renombrar, no destruir). Idempotente.

Uso (Text DAT dentro de /project2 o Textport):
  exec(open('clean_bases.py').read())
"""

import td

# Bases a limpiar para Petite Amie (visuales). Ajustar si el mapeo cambia.
TARGET_BASES = ['base1', 'base2', 'base3', 'base4',
                'base5', 'base6', 'base7', 'base8']

# Borrado TOTAL de cada base: nada protegido. Las paginas Audio/Visual de cada
# base son del contrato (las crea el builder), no de sistema, asi que se borran
# tambien para que el rebuild las recree limpias.
PROTECTED_PAGES = set()


def _clean_base(base):
    destroyed = []
    # 1) destruir TODOS los children del base (nodos huerfanos incluidos)
    for child in list(base.children):
        nm = child.name
        try:
            child.destroy()
            destroyed.append(nm)
        except Exception as e:
            print(f'  [warn] no pude destruir {nm}: {e}')

    # 2) borrar Custom Parameters. Si el rig usa paginas de sistema en el base,
    #    borrar pagina por pagina y respetar las protegidas; si no, nuclear.
    pages = list(getattr(base, 'customPages', []))
    if pages:
        for pg in pages:
            if pg.name in PROTECTED_PAGES:
                continue
            try:
                pg.destroy()
            except Exception as e:
                print(f'  [warn] no pude borrar pagina {pg.name}: {e}')
    else:
        try:
            base.destroyCustomPars()
        except Exception as e:
            print(f'  [warn] destroyCustomPars: {e}')

    print(f'[ok] {base.path} limpio — destruidos {len(destroyed)} nodos'
          + (f': {", ".join(destroyed)}' if destroyed else ''))


def run():
    for name in TARGET_BASES:
        base = td.op(f'/project2/{name}') or td.op(f'/{name}')
        if base is None:
            print(f'[skip] no existe {name}')
            continue
        _clean_base(base)
    print('--- limpieza terminada. Ahora corre los builders de visuales. ---')


run()
```

**Sebas lo corre desde un Text DAT en `/project2` o el TextPort.** Después de correrlo, base1–base8 quedan vacías (sólo el contenedor, sin children ni custom pars).

---

## Parte 2 — parche al `visual_builder.py` (para que no vuelva a pasar)

Modificar el template para que, cuando construya en una base que pudo tener otro proyecto, haga limpieza a fondo en vez de sólo la lista `managed`. Agregar una constante y usarla en `build()`:

```python
# --- CONFIG ---
FULL_CLEAN = True   # True: destruye TODOS los children antes de construir
                    #       (usar cuando la base pudo tener otro proyecto).
                    # False: comportamiento original (solo lista managed).
```

En `build(base)`, reemplazar el bloque de limpieza inicial:

```python
    # --- limpieza ---
    if FULL_CLEAN:
        for child in list(base.children):
            try: child.destroy()
            except Exception: pass
    else:
        managed = ['select_input', 'audio_in', GLSL_NAME, 'shader_pixel',
                   'switch1', 'null1', 'out1']
        for nm in managed:
            ch = base.op(nm)
            if ch is not None:
                try: ch.destroy()
                except Exception: pass
    try:
        base.destroyCustomPars()
    except Exception:
        pass
```

Aplicar el mismo patrón al `effect_builder.py` si algún efecto (base18–24, 38) va a construirse sobre una base que pudo tener otro contenido. Para las bases de efectos de Petite Amie, que están vacías o intactas, `FULL_CLEAN = False` es suficiente y más seguro.

---

## Parte 3 — orden de ejecución

1. Correr `clean_bases.py` → base1–base8 vacías.
2. Verificar en TD: base1 y base2 ya no tiran errores (están vacías, sin GLSL que cocine).
3. Con `FULL_CLEAN = True` en `visual_builder.py`, correr los builders de visuales en el orden de tandas de `PETITE_AMIE_build.md` (§10): base1 `grano_degradado`, base2 `liquid_light`, etc.
4. Después de cada build, pasar el checklist de la §12 del brief principal.

---

## Verificación

Por cada base limpiada y reconstruida:

- [ ] `base.children` sólo contiene los nodos del builder de Petite Amie (no queda `glsl_marquee_frame`, `glsl_atomic_starburst`, `audio_util`, ni ningún nombre ajeno)
- [ ] Cero `ParCollection has no attribute` en el TextPort
- [ ] El GLSL nuevo compila y muestra imagen
- [ ] Las páginas custom son las del contrato (Visual con 5 sliders + Bypass, y Audio)

Si al limpiar aparecen nodos con nombres que no reconoces de Paloma Murphy ni de Petite Amie, pausar y avisar a Sebas antes de destruir — podría ser algo compartido del rig.
