# Cinematic Pipeline Orchestrator

Plantilla para producir series de video con personajes consistentes en Higgsfield.

Separa en tres capas:
- **qué se ve:** el personaje;
- **cómo se ve:** el estilo;
- **en qué orden ocurre:** el storyboard.

Un compilador determinista combina las tres capas en los parámetros de cada toma.

```
character.md + style-guide.md + storyboard.json
                     │
             scripts/compile_shot.py
                     │
   params por toma (prompt + ajustes) + manifiesto
                     │
          Higgsfield · generación de video
                     │
       assets/clips/<id>.mp4  →  montaje
```

## Estructura

```
cinematic-pipeline-orchestrator/
├── assets/
│   ├── clips/            # un clip por toma: <id>.mp4
│   └── references/       # imágenes de referencia aprobadas del personaje
├── build/                # salida del compilador (se regenera)
├── config/
│   ├── character.md      # identidad: rostro, vestuario, estados, poses
│   └── style-guide.md    # render: medio, paleta, luz, movimiento
├── scripts/
│   └── compile_shot.py   # compilador de prompts
├── sequence/
│   └── storyboard.json   # la secuencia: una toma por entrada, en orden de montaje
└── README.md
```

## Requisitos

- Python 3.8 o superior. Solo usa la biblioteca estándar, sin dependencias.
- Una cuenta de Higgsfield.

## Inicio rápido

Desde la raíz del repositorio:

```bash
mkdir build
python scripts/compile_shot.py sequence/storyboard.json --model seedance_2_5 --out build/storyboard.compiled.json
```

`mkdir build` solo hace falta la primera vez.

La salida es una lista con un objeto por toma. Cada objeto tiene dos partes:

- **`params`:** lo que se envía a Higgsfield. Incluye modelo, prompt, duración, relación de aspecto, audio y referencias.
- **`manifest`:** la trazabilidad de la toma. Registra la versión del compilador, la versión y el hash de cada archivo de `config/`, los bloques usados, el número de palabras y los avisos.

Después:

1. Envía cada `params` a Higgsfield como una generación de video. Puedes hacerlo desde un agente con el conector de Higgsfield o copiando el prompt y los ajustes en la interfaz.
2. Guarda cada clip como `assets/clips/<id>.mp4`.
3. Monta los clips en el orden de `storyboard.json`.

## Cómo está organizado

| Capa | Archivo | Responde a | Cambia cuando |
|---|---|---|---|
| Identidad | `config/character.md` | ¿Quién es y cómo luce? | Cambias de personaje |
| Estilo | `config/style-guide.md` | ¿Cómo se pinta? | Cambias de estética |
| Secuencia | `sequence/storyboard.json` | ¿Qué pasa y en qué orden? | En cada video nuevo |

Ningún archivo invade el terreno de otro:
- El personaje no menciona técnica, luz ni paleta.
- El estilo no describe a ningún personaje.
- El storyboard solo usa los bloques que exportan los otros dos.

Gracias a esa separación, puedes usar el mismo personaje con otro estilo, o el mismo estilo con otro personaje, sin reescribir nada.

### Bloques

Los archivos de `config/` contienen bloques de texto en inglés delimitados con marcadores:

~~~markdown
<!-- BEGIN CORE_IDENTITY -->
```text
A tall East Asian man in his late twenties with a calm, regal bearing...
```
<!-- END CORE_IDENTITY -->
~~~

- El compilador copia cada bloque literalmente. No edites un bloque de una toma a otra: cambiar una sola palabra basta para que el personaje derive.
- Todo bloque debe figurar en la lista `exports` del front matter, y viceversa. Si no coinciden, el compilador se detiene.

## El storyboard

`storyboard.json` es una lista JSON. Cada objeto es una toma, y el orden de la lista es el orden del montaje.

| Campo | Obligatorio | Valores | Notas |
|---|---|---|---|
| `id` | Sí | Texto único | También da nombre al clip |
| `scale` | Sí | `wide`, `full`, `medium`, `close-up`, `insert` | Decide qué detalles entran |
| `camera_motion` | En close-up e insert | `static`, `slow`, `fast` | |
| `camera_directive` | No | Texto en inglés | Encuadre y movimiento de cámara |
| `state` | No | `STATE_*` | Por defecto, `STATE_CALM` |
| `pose` | Si no hay `action` | `POSE_*` | `POSE_MUDRA` solo en medium o más cerrado |
| `action` | Si no hay `pose` | Texto en inglés | Lo que ocurre en la toma |
| `setting` | Recomendado | Texto en inglés | Si falta, el compilador avisa |
| `details` | No | Lista de `TIER3_*` | Solo en close-up o insert con cámara `static` o `slow` |
| `duration` | No | Entero | Seedance 2.5: 4–30 s · Seedance 2.0: 4–15 s · Kling 3.0: 3–15 s |
| `aspect_ratio` | No | P. ej., `16:9` | Se valida según el modelo |
| `include_composition` | No | `true` / `false` | Por defecto, solo cuando no hay `setting` |

Cualquier otro campo hace fallar la compilación. Así se detectan los errores tipográficos.

Qué detalles del personaje entran según el plano:

| Plano | Bloques |
|---|---|
| wide / full | Identidad base |
| medium | Identidad base + Tier 2 |
| close-up | Identidad base + Tier 2 + los `TIER3_*` de `details` |
| insert | Identidad base + los `TIER3_*` de `details` |

Para mantener la continuidad entre tomas:

- Repite `setting` palabra por palabra en las tomas que ocurren en el mismo lugar.
- Escribe `camera_directive`, `action` y `setting` en inglés, igual que los bloques.

## Modelos

| Modelo | Prompt negativo | Referencias de identidad | Duración | Audio |
|---|---|---|---|---|
| `seedance_2_5` | No; usa los bloques `*_NEGATIVE_FALLBACK` | Sí | 4–30 s | Apagado |
| `seedance_2_0` | No; usa los bloques `*_NEGATIVE_FALLBACK` | Sí | 4–15 s | Apagado |
| `kling3_0` | No; usa los bloques `*_NEGATIVE_FALLBACK` | No | 3–15 s | Apagado |

Los perfiles de cada modelo están en `MODEL_PROFILES`, dentro de `scripts/compile_shot.py`. Fijan explícitamente la resolución o el modo y el audio, para no depender de los valores por defecto de la plataforma.

Antes de añadir un modelo nuevo, consulta en el catálogo de Higgsfield si tiene campo de prompt negativo y qué roles de imagen acepta.

## Imágenes de referencia

La referencia de identidad es lo que más ayuda a mantener el mismo rostro entre clips. El compilador funciona sin ella, pero muestra un aviso en cada toma.

1. Genera y aprueba dos imágenes del personaje: un retrato frontal con expresión neutra y un cuerpo completo. Usa fondo liso y luz uniforme.
2. Guárdalas en `assets/references/`.
3. Súbelas a Higgsfield y copia sus IDs de media en `config/character.md`:
   `reference_images: [id-retrato, id-cuerpo]`

Ten en cuenta:

- **Los IDs están ligados a la cuenta que subió las imágenes.** Quien clone el repositorio tiene que subirlas desde su propia cuenta y poner sus propios IDs.
- **Una referencia también transmite estilo.** Si cambias de `style-guide.md`, genera referencias nuevas en ese estilo.
- **Solo los modelos Seedance las reciben.** Con Kling 3.0, el compilador las omite y muestra un aviso.

## Crear un personaje o cambiar de estilo

**Personaje nuevo.**
1. Copia `config/character.md` y reescribe sus bloques.
2. Incluye como mínimo `CORE_IDENTITY`, `STATE_CALM` y `CHARACTER_NEGATIVES`.
3. Para modelos sin prompt negativo, añade también `NEGATIVE_FALLBACK`.
4. Mantén `CORE_IDENTITY` en torno a 100 palabras.

**Estilo nuevo.** Crea otro archivo, por ejemplo `config/style-guide.anime-retro.md`, que cumpla el *Swap Contract* descrito en `style-guide.md`. Después pásalo con `--style`:

```bash
python scripts/compile_shot.py sequence/storyboard.json --model seedance_2_5 \
  --style config/style-guide.anime-retro.md --out build/storyboard.anime.json
```

## Reproducibilidad

- **El prompt es determinista.** La misma entrada produce la misma salida, byte a byte y en cualquier sistema operativo, siempre que uses `--out`.
- **El manifiesto identifica el origen de cada clip.** Registra con qué versión de cada archivo y de qué bloques salió el prompt.
- **El video no es determinista.** Los modelos de Higgsfield no exponen semilla, así que el mismo prompt da clips distintos en cada generación. Guarda el clip aprobado junto con su manifiesto.

## Errores frecuentes

| Mensaje | Causa |
|---|---|
| `'exports' no coincide con los bloques` | Un bloque declarado en `exports` no existe, o un bloque existe sin estar declarado |
| `N marcadores BEGIN pero M bloques válidos` | Hay un `END` mal escrito o falta la línea `` ```text `` |
| `claves desconocidas` | Hay un campo mal escrito en el storyboard |
| `estado inexistente` / `pose inexistente` | Ese ID no existe en `character.md` |
| `'details' solo se permite en close-up/insert…` | Se pidieron detalles en un plano abierto o con cámara rápida |
| `duration inválida` | La duración está fuera del rango del modelo |
| `falta el front matter` | El archivo no empieza con el bloque `--- … ---` |

## Licencia

[MIT](LICENSE)
