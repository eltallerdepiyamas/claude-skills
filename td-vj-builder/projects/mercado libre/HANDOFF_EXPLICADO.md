# Handoff a Mich — cómo funciona y cómo verificarlo

Documento para ti (no para Mich). Explica qué se le manda, cómo viajan sus datos hasta tus bases,
cómo comprobar que todo funciona **antes** de enviarlo y qué hay que preguntarle.

---

## 1. Qué recibe Mich

`handoff.py` genera todo en `exports/handoff/`:

| Archivo | Qué es | ¿Lo necesita? |
|---|---|---|
| **`ML_floor_pack.tox`** | Todo en uno: el hub de tracking + todas las bases + un menú para elegir visual. Una sola salida. | **Sí, es lo principal** |
| `LEEME_MICH.md` | Instrucciones cortas para Mich (pasos, formatos, calibración) | Sí |
| `tracking_input.tox` + `baseN_nombre.tox` | Las mismas piezas sueltas, por si quiere montarlas en su propio rig | Opcional |

Todo va **congelado**: los shaders y scripts viajan dentro del `.tox`, sin rutas a tu carpeta ni a tu
`escena_modular`. Mich no necesita `_lib/`, ni `builders/`, ni `shaders/`.

Los builders (`builders/…`) **no** se le mandan: son tu herramienta de trabajo y dependen de esta carpeta.

---

## 2. Cómo viajan los datos

```
 Hokuyo ──► CHOP de Mich ──► tracking_input (hub) ──► out1 ──┬──► base1  ─┐
            (su formato)     · elige la fuente              ├──► base2   │
                             · convierte su formato          ├──► base3   ├──► menú "Visual" ──► out1 del pack
                             · metros → 0..1                 ├──► …       │
                             · origen / swap / flip / clip   └──► base6  ─┘
```

**La idea clave:** todas las bases hablan un solo "idioma" (el *contrato*), y el hub es el traductor.
Mich solo toca el hub; las bases no se enteran de dónde vienen los datos.

### El contrato (lo que las bases entienden)

Un CHOP de 1 sample con hasta **8 personas** (`i = 0..7`):

| Canal | Significado |
|---|---|
| `p{i}x`, `p{i}y` | posición en el piso, **0..1** (0,0 = esquina abajo-izquierda) |
| `p{i}a` | 1 = hay persona en ese slot, 0 = vacío |
| `p{i}id` | ID estable de la persona (define su color/fase en los visuales) |

Dentro de cada base, `tracking_in` lee `tracking_input/out1` y lo pasa al shader como `u_p0 … u_p7`
(xy = posición, z = activa, w = id).

### Qué hace el hub con los datos de Mich

`tracking_input` → página **Input**:

- **Source**: `Simulate` (caminantes falsos) · `Webcam` (tu demo) · `Externo` (Hokuyo).
- **Formato** — acepta dos formas de CHOP:
  - **A · contrato**: Mich ya manda `p0x p0y p0a p0id…` → pasa directo.
  - **B · canales X/Y**: un canal X y uno Y con **un sample por persona** (típico de trackers de blobs).
    Se escriben los nombres de sus canales (y el de ID si tiene; si no, usa el índice).
- **Unidades**: `Normalizado 0..1` o `Metros`. En metros: `(valor − Origen) ÷ Floor W/H`.
- **Origen X/Y**: dónde queda el (0,0) del sensor respecto a la esquina abajo-izquierda del piso.
- **Swap XY / Flip X / Flip Y**: alinear los ejes del sensor con el piso.
- **Descartar fuera del piso**: ignora puntos fuera del área (reflejos, gente de paso).
- **Status**: te dice qué está leyendo (`external · 3 persona(s)` o `falta el CHOP del Hokuyo`).

---

## 3. Qué está probado y qué no

| Parte | Estado |
|---|---|
| Lógica de conversión del hub (formatos A y B, metros, origen, flip, clip) | ✅ Probada fuera de TD con datos simulados |
| Shaders de las bases | ✅ Compilan y renderizan (OpenGL real, fuera de TD) |
| Bases 1–6 dentro de TD | 🟡 Las ves funcionando; el hub nuevo aún no confirmado |
| Hub dentro de TD (Simulate / Webcam / Externo) | ⬜ Sin probar |
| `handoff.py` (armar y guardar el pack) | ⬜ Sin correr nunca |
| Abrir el pack en un proyecto **limpio** | ⬜ Sin probar — **es la prueba que importa** |

---

## 4. Checklist antes de mandarlo

Haz esto en orden. Si algo falla, pega el Textport.

**A · El hub en tu proyecto**
1. Corre `builders/build_all.py`.
2. `tracking_input` → Source = **Simulate**. Status = `simulate · 3 persona(s)`. Las bases muestran 3 caminantes.
3. Source = **Webcam** → las bases te siguen a ti.

**B · Simular el CHOP de Mich (sin Hokuyo)**

*Formato A (contrato):*
1. En `/project2` crea un **Constant CHOP** con canales `p0x = 0.3`, `p0y = 0.5`, `p0a = 1`, `p0id = 7`.
   (Para que se mueva: en `p0x` pon la expresión `0.5 + 0.3*math.sin(absTime.seconds)`.)
2. Hub: Source = **Externo**, arrastra ese CHOP a **CHOP externo**, Formato = `p0x p0y p0a p0id…`.
3. Status = `external · 1 persona(s)` y en las bases aparece una persona moviéndose.

*Formato B (canales X/Y en metros):*
1. Crea un **Table DAT** con columnas `x` y `y` y 2–3 filas en metros (p. ej. `1 1`, `3.5 2.5`, `6 4`),
   y conviértelo con un **DAT to CHOP** (una columna = un canal, una fila = un sample).
2. Hub: arrastra ese CHOP, Formato = `Canales X/Y`, Canal X = `x`, Canal Y = `y`, Unidades = `Metros`.
3. Aparecen 2–3 personas en posiciones proporcionales a 7 x 5 m. Prueba Flip / Swap / Origen y confirma
   que se mueven como esperas. Pon una fila en `20 1` → debe desaparecer (fuera del piso).

**C · El paquete**
1. Corre `builders/herramientas/handoff.py` → revisa que aparezcan los `.tox` en `exports/handoff/`.
2. **Abre un proyecto de TouchDesigner nuevo y vacío** (File → New).
3. Arrastra `ML_floor_pack.tox`. Debe verse un visual con 3 caminantes (Simulate) sin errores.
4. Cambia el menú **Visual** del pack → cambian los looks.
5. Repite la prueba B dentro de ese proyecto vacío (Constant CHOP → hub del pack → Externo).

Si **C** pasa, lo que le mandas funciona sin tu carpeta. Eso es lo que hay que garantizar.

---

## 5. Qué preguntarle a Mich (antes de cerrar)

Los formatos que soporta el hub cubren los casos más comunes, pero conviene confirmarlo. Mensaje listo para mandar:

> Oye Mich, para dejarte los visuales plug & play necesito saber cómo sale tu tracking:
> 1. ¿Qué **versión de TouchDesigner** usas? (Yo estoy en 2025.33230; un .tox nuevo puede no abrir en una versión vieja.)
> 2. Tu CHOP del Hokuyo: ¿qué **canales** tiene y cómo se llaman? ¿Es **un sample por persona** (canales x/y) o **canales por persona** (p0x, p1x…)? Si puedes, mándame un screenshot del CHOP o un .tox con datos grabados.
> 3. ¿En qué **unidades** salen las posiciones: metros, milímetros o normalizado?
> 4. ¿Dónde queda el **(0,0) del sensor** respecto al piso y hacia dónde apuntan X y Y?
> 5. ¿Tu tracking ya **agrupa las dos piernas** de una persona en un solo punto? (El Hokuyo escanea a la altura de los tobillos.)
> 6. ¿Da **IDs estables** por persona? ¿Cuántas personas máximo esperas a la vez?
> 7. ¿Cuál es la **resolución final** del piso LED y cómo mapeas la salida?

### Qué haría yo con cada respuesta

- **Milímetros** → agrego un factor de escala al hub (hoy solo hay normalizado y metros).
- **Canales con otros nombres o estructura** → basta con escribir los nombres en el hub. Si es un formato
  distinto a A/B, agrego un tercer formato.
- **Piernas sin agrupar** → agrego al hub un agrupado de puntos cercanos (dos piernas → una persona).
- **Más de 8 personas** → hay que subir el límite en el hub y en los shaders.
- **Sin IDs estables** → los colores/fases pueden saltar; se puede agregar seguimiento de IDs al hub
  (como el que ya tiene `webcam_tracker`).
- **Resolución del LED** → Mich la pone él mismo en `tracking_input` → Salida (Resolución W/H y Piso ancho/alto). No hace falta re-exportar.
- **Versión de TD más vieja** → hay que exportar desde esa versión o evitar features nuevas.

Con un .tox o una grabación de su CHOP puedo probar el hub con sus datos reales antes de mandárselo.
