# Prompt para Claude Code — base07: asset sobre rostro (face tracking)

/td-vj-builder

Nuevo efecto para **base07** (proyecto Casa Bacardí, TouchDesigner 2023.11600, `/project1`).

## Referencia

Usa la **misma arquitectura de face tracking** que ya construiste en `base03` y `base04`
(la que usa YOLO para detectar el rostro). **Lee esos builders primero** y reusa el
pipeline de detección tal cual.

## Diferencia con base03

En base03 el rostro se pixelea. En base07 **NO quiero pixelado** — quiero que sobre el
rostro detectado se dibuje una **imagen (asset)** que yo cargo:

- Agrega un **Movie File In TOP** llamado `asset_face` dentro de `base07`,
  donde yo arrastro mi PNG (con alpha) o imagen.
- Ese asset entra al GLSL Multi como un `sTD2DInputs` adicional.
- El shader **compone el asset encima del rostro**: centrado en la bounding box
  del face tracking, escalado al tamaño del rostro, respetando el alpha del PNG.
- El resto del frame se ve normal (cámara limpia).

## Los 5 sliders (contrato del skill)

1. **Intensity** → opacidad del asset sobre el rostro (0–1)
2. **Speed** → si aplica animación (ej. wobble/pulso del asset), rate
3. **Distortion** → escala del asset relativa a la cara (0.5–3)
4. **Color** → tinte/mezcla de color del asset
5. **Signature** → offset vertical del asset (para ajustar posición sobre la cara)

Más **Bypass** y página **Audio** como siempre.

## Reglas ya aprendidas (no repetir errores)

- Vertex shader **vacío** (usar el default de TD, no generar DAT de vertex).
- **Nunca** redeclarar `vUV` ni `sTD2DInputs` en el pixel shader — TD los inyecta.

## Entregables

- El shader GLSL del efecto.
- `setup_base07.py` (builder idempotente, estilo de los anteriores).
