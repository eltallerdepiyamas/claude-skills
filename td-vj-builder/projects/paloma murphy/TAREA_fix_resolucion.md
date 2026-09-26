# TAREA — Fix de resolución en los 7 builders

> Instrucciones para Claude Code. Lee `CLAUDE.md` primero, luego ejecuta esta tarea.
> **No toques TouchDesigner** — los builders los corre Sebas desde el TextPort.

## Contexto (errores reales del TextPort)

Al correr `setup_base1_marquee_frame.py` en TD salieron dos errores en `glsl_marquee_frame`:

1. `td.tdAttributeError: 'td.ParCollection' object has no attribute 'ResW'` (y `ResH`).
   La fuente de resolución **no** son parámetros de `escena_modular`.
2. `Cook dependency loop detected` entre `glsl_marquee_frame_info` y `glsl_marquee_frame`
   (Parameter: Value). Causa: el uniform `u_res` usa `me.width` / `me.height`, lo que hace
   que un parámetro del nodo dependa del output cocinado del mismo nodo (vía su `_info`).

## Fuente de resolución REAL del rig

La resolución viene de un **Constant CHOP** llamado `constant45`, canales `resX` / `resY`.
Referencia canónica desde el GLSL TOP (que vive dentro de `/project2/baseN`):

```python
parent(2).op('constant45')['resX']
parent(2).op('constant45')['resY']
```

## Cambios a aplicar en LOS 7 builders de `scripts\`

### 1. Expresiones de resolución del GLSL TOP

- `resolutionw` → expresión: `parent(2).op('constant45')['resX']`
- `resolutionh` → expresión: `parent(2).op('constant45')['resY']`
- **Eliminar por completo** toda referencia a `escena_modular.par.ResW/ResH`
  (y cualquier variante `Resw`/`Resh`).

### 2. Uniform `u_res` (página Vectors)

- Debe usar `me.par.resolutionw` / `me.par.resolutionh`
  (referencia a **parámetro**, no a propiedad cocinada).
- **Nunca** `me.width` / `me.height` — eso crea el cook dependency loop.

## Actualizar `CLAUDE.md`

### En "Rig (recordatorio)"

Reemplazar la línea de resolución por:

> Resolución de salida: canales `resX`/`resY` del Constant CHOP `constant45`;
> referencia canónica desde un nodo dentro de baseN:
> `parent(2).op('constant45')['resX']` / `['resY']`

### En "Notas del show"

Registrar estos tres hallazgos:

1. Fuente de resolución real del rig = `constant45` (CHOP), **no** parámetros de `escena_modular`.
2. Nunca usar `me.width`/`me.height` en expresiones de parámetros del propio GLSL TOP —
   crea cook dependency loop con el nodo `_info`. Usar `me.par.resolutionw/h`.
3. Parámetros custom en TD: solo primera letra mayúscula (`Resw`, no `ResW`).

---

# PARTE 2 — Página Layout: Scale + Rows/Columns (repeticiones)

Sebas necesita: llenar el canvas con el visual, poder hacerlo más grande o más pequeño,
y repetirlo en retícula (rows × columns). Aplica esto a **los 7 builders** y a sus shaders
embebidos.

## Nueva página custom `Layout` (en cada base)

Va **después** de `Visual` y **antes** de `Audio`. No forma parte del contrato de 5 sliders
(no es audio-targeteable). Parámetros:

| Par | Tipo | Default | Min | Max | Uniform |
|-----|------|---------|-----|-----|---------|
| `Scale` | Float | 1.0 | 0.25 | 4.0 | `u_scale` |
| `Rows` | Int | 1 | 1 | 12 | `u_tiles` (componente y) |
| `Columns` | Int | 1 | 1 | 12 | `u_tiles` (componente x) |

Binding en la página Vectors del GLSL TOP (mismo patrón `_bind` existente, valores directos
sin audio):

- `u_scale` → `parent().par.Scale`
- `u_tiles` → x: `parent().par.Columns`, y: `parent().par.Rows`

## Cambios en el shader (HEADER compartido)

1. Declarar los uniforms nuevos:

```glsl
uniform float u_scale;   // 0.25..4  (1 = normal; >1 = mas grande / llena canvas)
uniform vec2  u_tiles;   // columns, rows (1,1 = sin repeticion)
```

2. Agregar helper de tiling (el `fract` repite el visual completo en cada celda):

```glsl
vec2 layoutUV(vec2 uv){
    uv = fract(uv * u_tiles);   // reticula rows x columns
    return uv;
}
```

3. Ajustar `aspect()` para que cada celda conserve proporción y aplicar `Scale`:

```glsl
vec2 aspect(vec2 uv){
    vec2 p = uv * 2.0 - 1.0;
    vec2 cellRes = u_res / max(u_tiles, vec2(1.0));
    p.x *= cellRes.x / max(cellRes.y, 1.0);
    p /= max(u_scale, 0.05);    // Scale: >1 acerca/agranda, <1 aleja/encoge
    return p;
}
```

4. En el `main()` de **cada pieza**, reemplazar `vUV.st` por `layoutUV(vUV.st)`.
   - Ojo con `dot_matrix_field`: usa `vUV.st` directo en espacio uv (no `aspect`);
     ahí aplicar `layoutUV` primero y dividir la densidad efectiva **no** es necesario —
     basta con el reemplazo de uv. Para el Scale en esa pieza, multiplicar
     `cells` por `1.0/u_scale` (clampeado) para que Scale también la afecte.

## Reglas

- Mantener **sin indexado dinámico de arrays** y todos los uniforms asignados en la
  página **Vectors**.
- Los builders siguen siendo idempotentes: la página `Layout` entra al snapshot/restore
  y al `_clear_pages` (agregar `'Layout'` a las tuplas de nombres de página en
  `_snapshot` y `_clear_pages`).
- Actualizar también los `.frag` de referencia en `shaders\` para que queden en sync
  con el código embebido en los builders.

## Actualizar `CLAUDE.md`

- En "Contrato por base (invariante)" agregar:
  > **Página Layout** (no audio-targeteable): `Scale` (0.25–4, u_scale),
  > `Rows`/`Columns` (1–12, u_tiles) para repetir el visual en retícula.
- En "Estructura de nodos por base" no cambia nada (mismos nodos).

---

# PARTE 3 — Dirección del chase (sentido de encendido de las bombillas)

Sebas necesita seleccionar **hacia dónde corre el encendido secuencial** de las bombillas.
Aplica a **los 7 builders** y sus shaders embebidos.

## Nuevo parámetro (en la página `Layout`)

| Par | Tipo | Menú | Default | Uniform |
|-----|------|------|---------|---------|
| `Chasedir` | Menu | `Normal` / `Invertido` | `Normal` | `u_dir` (+1.0 / -1.0) |

Binding en Vectors (expresión):

```python
-1.0 if str(parent().par.Chasedir) == 'Invertido' else 1.0
```

## Cambios en el shader

1. Declarar en el HEADER: `uniform float u_dir;   // +1 normal, -1 invertido`
2. Multiplicar por `u_dir` **todos los términos de fase animada** (todo lugar donde
   `u_time * u_speed` empuja el patrón). Pieza por pieza:

| Pieza | Dónde aplica |
|-------|--------------|
| `marquee_frame` | en `chase()`: `fract(s - u_time * u_speed * 0.15 * u_dir)` → invierte horario/antihorario del perímetro |
| `atomic_starburst` | fase del chase radial: `fract(idx * 0.14 - u_time * u_speed * 0.35 * u_dir)` → hacia afuera / hacia adentro |
| `bulb_arrow` | fase del blink secuencial: `- u_time * u_speed * 0.40 * u_dir` → hacia la punta / desde la punta |
| `dot_matrix_field` | fase de la ola: `- u_time * u_speed * 1.2 * u_dir` → invierte la dirección de la ola |
| `spin_ring` | rotación: `u_time * u_speed * 0.30 * dir * u_dir` (se combina con la alternancia por anillo existente) |
| `chevron_march` | scroll: `scroll = u_time * u_speed * 0.25 * u_dir` → los galones marchan hacia arriba o abajo |
| `circulos` | ripple: `- u_time * u_speed * 1.4 * u_dir` → pulso hacia afuera / hacia adentro |

Como `chase()` vive en el HEADER compartido, con multiplicar ahí ya cubre a las piezas
que la usan; las demás fases (olas, scroll, spin, ripple) se multiplican en el cuerpo
de cada pieza.

## Reglas

- Mismo estándar: uniform asignado en la página **Vectors**, builders idempotentes
  (`Chasedir` entra al snapshot/restore por estar en la página `Layout`).
- Actualizar los `.frag` de referencia en `shaders\` en sync.
- En `CLAUDE.md`, en la línea de la página Layout, agregar `Chasedir` (Normal/Invertido,
  `u_dir`) a la lista de parámetros.

---

# PARTE 4 — Rampas de color en el chase (cola degradada que "ilumina")

Sebas quiere que el encendido pueda verse como una **rampa**: una cabeza brillante con
una **cola que se desvanece en degradado** (y que recorre la paleta), como si la luz
viajara iluminando el letrero — en vez del on/off duro actual. Ambos modos deben coexistir.
Aplica a **los 7 builders** y sus shaders embebidos.

## Nuevos parámetros (en la página `Visual`, después de los 5 sliders)

| Par | Tipo | Menú/Rango | Default | Uniform |
|-----|------|-----------|---------|---------|
| `Chasemode` | Menu | `Duro` / `Rampa` | `Duro` | `u_ramp` (0.0 / 1.0) |
| `Tail` | Float | 0.1 – 1.0 | 0.5 | `u_tail` (largo de la cola en modo Rampa) |

Binding en Vectors:

```python
# u_ramp
1.0 if str(parent().par.Chasemode) == 'Rampa' else 0.0
# u_tail
parent().par.Tail
```

## Cambios en el shader (HEADER)

1. Declarar: `uniform float u_ramp;` y `uniform float u_tail;`
2. Reescribir `chase()` para soportar ambos modos y **exponer la fase** (para poder
   teñir la cola con la paleta):

```glsl
// devuelve brillo y deja la fase en outPh (0 = cabeza del chase)
float chase2(float s, float win, out float outPh){
    float ph = fract(s - u_time * u_speed * 0.15 * u_dir);
    outPh = ph;
    // modo duro: ventana on/off (comportamiento actual)
    float hard = 1.0 - smoothstep(win, win + 0.03, ph);
    // modo rampa: cabeza caliente + cola que decae suave segun u_tail
    float soft = pow(clamp(1.0 - ph / max(u_tail, 0.05), 0.0, 1.0), 1.6);
    float on = mix(hard, soft, u_ramp);
    return mix(0.16, 1.0, on);
}
// wrapper compatible con las llamadas existentes
float chase(float s, float win){ float _p; return chase2(s, win, _p); }
```

3. **Tinte de la cola** (esto es lo que hace que "se vea que ilumina"): en las piezas
   que usan chase, cuando `u_ramp > 0.5`, desplazar la paleta con la fase:

```glsl
float ph; float ch = chase2(idx / n, 0.35, ph);
vec3 tint = palette(u_colormix + ph * 0.25 * u_ramp);  // la cola recorre la paleta
col += tint * bmask * ch * u_intensity;
```

   La cabeza además puede llevar un boost caliente: `+ vec3(1.0) * bmask * u_ramp * pow(max(1.0 - ph/0.06, 0.0), 2.0) * 0.6 * u_intensity;` (destello blanco en la punta, opcional pero recomendado).

## Piezas que NO usan `chase()` (equivalente por fase propia)

| Pieza | Cómo aplicar la rampa |
|-------|----------------------|
| `atomic_starburst` | ya calcula `ph` radial propio: usar la misma fórmula `soft` con `u_tail`, mezclar con el `on` duro vía `u_ramp`, y teñir con `palette(u_colormix + r*0.15 + ph*0.25*u_ramp)` |
| `bulb_arrow` | idem con su `ph` secuencial |
| `dot_matrix_field` | su ola `w` ya es suave: en modo Rampa ensanchar el smoothstep (`smoothstep(0.1, 0.9, w)`) y teñir con `palette(... + (1.0-w)*0.25*u_ramp)` |
| `spin_ring` | el blink por anillo pasa a rampa: `pow(0.5+0.5*sin(...), mix(1.0, 3.0, u_ramp))` y teñir por anillo con fase |
| `circulos` | su `pulse` es la fase: mismo tratamiento que la matriz (ensanchar + teñir) |

## Reglas

- `Chasemode` y `Tail` viven en la página `Visual` pero **no** entran al contrato de los
  5 sliders audio-targeteables (el menú `Audiotarget` sigue listando solo los 5).
- Uniforms en la página **Vectors**, builders idempotentes, `.frag` de `shaders\` en sync.
- En `CLAUDE.md`, sección "Contrato por base", agregar:
  > Extras de Visual (no audio-targeteables): `Chasemode` (Duro/Rampa, `u_ramp`) y
  > `Tail` (0.1–1, `u_tail`) — chase con cola degradada que recorre la paleta.

---

# PARTE 5 — CORRECCIÓN A LA PARTE 2 (anula el tiling; solo base1 por ahora)

**La Parte 2 quedó mal interpretada.** Sebas NO quiere repetir el visual completo en
retícula (tiling con `fract`). Lo que quiere es que **los focos abarquen toda la
pantalla**: la forma se repite **hacia adentro** — marcos concéntricos anidados.

## Qué hacer

1. **Revertir el tiling** (`layoutUV` / `u_tiles` / `Rows` / `Columns`) en todos los
   builders donde se haya aplicado. El helper `layoutUV` y el uniform `u_tiles`
   desaparecen.
2. Implementar el nuevo diseño **SOLO en `setup_base1_marquee_frame.py`** (y su `.frag`).
   Los otros 6 se quedan como están; su layout se decidirá después pieza por pieza.

## Nuevo diseño de la página `Layout` (solo base1)

| Par | Tipo | Rango | Default | Uniform |
|-----|------|-------|---------|---------|
| `Scale` | Float | 0.25 – 1.2 | 1.0 | `u_scale` (1.0 = el marco exterior pegado al borde de pantalla) |
| `Repeat` | Int | 1 – 10 | 1 | `u_repeat` (cuántos marcos concéntricos hacia adentro) |
| `Gap` | Float | 0.06 – 0.40 | 0.16 | `u_gap` (separación entre marcos) |

(`Chasedir` de la Parte 3 se mantiene en esta página.)

## Implementación en el shader de base1

1. El marco **exterior** debe poder llenar el canvas: derivar la caja del aspect real,
   con un margen pequeño, escalada por `u_scale`:

```glsl
float aspX = u_res.x / max(u_res.y, 1.0);
vec2 bOuter = vec2(aspX, 1.0) * 0.94 * u_scale;   // 1.0 => pegado al borde
```

2. Marcos concéntricos: loop de tope fijo (sin indexado dinámico de arrays, esto es
   solo un loop de acumulación) donde cada iteración dibuja un marco más chico:

```glsl
float m = 0.0;
for (int i = 0; i < 10; i++){
    if (float(i) >= u_repeat) break;
    vec2 b = bOuter - vec2(u_gap) * float(i);
    if (b.x < 0.08 || b.y < 0.08) break;          // ya no cabe otro marco
    float per = 4.0 * (b.x + b.y);
    float nn  = max(8.0, floor(u_sig * per / (4.0 * (bOuter.x + bOuter.y)))); // densidad pareja
    m = max(m, frameBulbs(p, b, nn, float(i)));
}
```

3. `frameBulbs` recibe además el índice del anillo y **desfasa el chase por anillo**
   (cascada hacia adentro, respetando `u_dir` y el modo Rampa de la Parte 4):

```glsl
// dentro de frameBulbs: al llamar chase/chase2 usar
//   s = idx / n + ringIdx * 0.13
```

4. La densidad (`u_sig`, slider `Density`) se refiere al marco exterior; los interiores
   escalan proporcionalmente a su perímetro para que la separación entre focos se vea
   igual en todos los anillos (por eso el cálculo de `nn` de arriba).

## Reglas

- Uniforms nuevos (`u_scale`, `u_repeat`, `u_gap`) en la página **Vectors**.
- Builder idempotente: página `Layout` en snapshot/restore y `_clear_pages`.
- `.frag` de referencia de `shaders\marquee_frame.frag` en sync.
- `CLAUDE.md`: en la fila de base1 de la tabla, anotar que tiene Layout de marcos
  concéntricos (`Scale`/`Repeat`/`Gap`); y en "Notas del show" registrar:
  > Layout ≠ tiling: la repetición es de la forma hacia adentro (concéntrica),
  > los focos deben poder abarcar toda la pantalla. Decidir layout pieza por pieza.

## Al terminar

Reporta qué archivos tocaste. Sebas re-corre `setup_base1` desde TextPort para validar.
