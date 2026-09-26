# claude-skills

Colección de skills de Claude Code para producción audiovisual y VJ.

## Skills incluidas

### TouchDesigner
- **td-vj-builder** — Generative visuals, camera effects y layouts para shows en vivo
- **td-flyer-audioreactivo** — Anima flyers/pósters como loops audio-reactivos
- **td-glsl** — Shaders GLSL para GLSL TOP, MAT y COMP
- **td-glsl-vertex** — Vertex shaders para GLSL MAT (displacement, deformation, instancing)
- **td-pops** — Compute shaders para el sistema POP (partículas, point clouds)

### Otros
- **hou-vex** — VEX code para Houdini SOPs, DOPs, COPs y shaders
- **sc-designer** — SuperCollider: síntesis, sound design, composición algorítmica
- **find-skills** — Descubre e instala nuevas skills
- **remotion-*** — Skills para video con Remotion (React)

## Estructura de cada skill

```
skill-name/
├── SKILL.md          # Definición principal, trigger conditions
├── LEARNINGS.md      # Aprendizajes acumulados (si existe)
├── README.md         # Descripción técnica
├── templates/        # Plantillas de código reutilizables
├── references/       # Documentación y convenciones
├── library/          # Componentes y helpers
└── examples/         # Ejemplos completos
```

## Uso

Las skills están disponibles en `~/.claude/skills/` (enlazada a esta carpeta).
Se activan automáticamente según el contexto del proyecto en Claude Code.
