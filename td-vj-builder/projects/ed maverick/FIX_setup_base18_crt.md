# Parche para `setup_base18_crt.py`

Dos cambios. No toques nada más del archivo (shader, presets, páginas y contrato
de 5 macros se quedan igual).

---

## 1. Arreglar `AttributeError: module 'td' has no attribute 'ParMode'`

En esta build de TouchDesigner `ParMode` no es atributo del módulo `td`. Además,
asignar `.expr` ya pone el parámetro en modo expresión por sí solo, así que la
línea `p.mode = ...` es redundante en todos los casos.

**Agrega este helper** junto a los demás helpers (después de `_set_par_any`):

```python
def _set_expr(p, e):
    """Asigna una expresion de forma tolerante a la version de TD.
    Asignar .expr ya cambia el modo a EXPRESSION; el set explicito de modo
    solo se intenta si ParMode existe en esta build."""
    if p is None:
        return False
    try:
        p.expr = e
    except Exception:
        return False
    PM = getattr(td, 'ParMode', None) or globals().get('ParMode', None)
    if PM is not None:
        try:
            p.mode = PM.EXPRESSION
        except Exception:
            pass
    return True
```

**Reemplaza TODAS las ocurrencias de `p.mode = td.ParMode.EXPRESSION` (y
variantes `gp.mode`, `vp.mode`, `sw.par.index.mode`) usando `_set_expr`.**
Son cuatro sitios:

1. En `_set_par_any`, la rama `if mode == 'expr':`
   ```python
   if mode == 'expr':
       if not _set_expr(p, value):
           continue
   ```
   (quita el `p.mode = td.ParMode.EXPRESSION` de ahí)

2. En `_bind_uniform`, el bloque que hace `vp.expr = e` → cámbialo por
   `_set_expr(vp, e)` y borra la línea de `.mode`.

3. En `build`, el binding de resolución:
   ```python
   if rp:
       _set_expr(gp, f"op('{sm.path}').par.{rp}")
   else:
       gp.val = fb
   ```

4. En `build`, el switch de bypass:
   ```python
   _set_expr(sw.par.index, 'parent().par.Bypass')
   ```

Después no debe quedar **ninguna** referencia a `td.ParMode` en el archivo.
Verifícalo con una búsqueda antes de terminar.

---

## 2. Meter un Null entre el Movie File In y el resto (incluido el feedback)

El `feedbackTOP` necesita una textura de entrada válida para inicializarse y
tomar resolución; sin input puede quedar negro o tronar. La fuente pasa a ir por
un Null que alimenta todo.

**Cambios en `build`:**

- Agrega `'null_src'` a la lista `managed` (para que la limpieza siga siendo
  idempotente).

- Justo después de crear y configurar `moviefilein1`, crea el null:

  ```python
  src = _create(base, nullTOP, 'null_src', -700, 0)
  _connect(mov, src)
  ```

- **Recablea todo lo que hoy sale de `mov` para que salga de `src`:**
  - `_connect(mov, glsl, 0)`      → `_connect(src, glsl, 0)`
  - `_connect(mov, cross, 0)`     → `_connect(src, cross, 0)`
  - `_connect(mov, sw, 1)`        → `_connect(src, sw, 1)`

- **Conecta el null a la entrada del feedback**, además de dejar su `Target TOP`
  apuntando al GLSL (el target es lo que captura; la entrada es lo que lo
  inicializa). El bloque del feedback queda así:

  ```python
  fb = _create(base, feedbackTOP, 'feedback1', -300, -200)
  _set_par_any(fb, (('top', glsl.name, 'val'), ('targetop', glsl.name, 'val'),
                    ('target', glsl.name, 'val')))
  _connect(src, fb, 0)      # inicializa el buffer con la fuente
  _connect(fb, glsl, 1)     # feedback -> input 1 del shader (persistencia)
  ```

- La expresión de `SRC_ASPECT` dentro de `UNIFORM_PACK` sigue leyendo
  `op('moviefilein1')` — **déjala así**, el aspecto viene del archivo original,
  no del null.

---

## Criterio de aceptación

Correr el script en un Text DAT dentro de `base18` no debe tirar excepción, y en
la red deben quedar: `moviefilein1 → null_src`, y de `null_src` salen tres
cables (a `glsl_crt` input 0, a `cross_intensity` input 0, a `switch1` input 1) más
uno a `feedback1` input 0. `feedback1` sale al input 1 de `glsl_crt`.
Los parámetros con expresión (resolución, uniforms, bypass, file/play/speed del
movie) deben verse en modo expresión (fondo azul) en la UI.
