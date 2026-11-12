#!/usr/bin/env python3
"""
Compilador determinista de prompts para Higgsfield.

Entrada:  config/character.md + config/style-guide.md + shots.json
Salida:   JSON con, por toma, los `params` para generate_video y un manifiesto.

Misma entrada -> misma salida, byte a byte, en cualquier sistema operativo
(usa --out para escribir el archivo). Toda entrada inválida aborta con un
mensaje claro; nunca degrada el prompt en silencio.
Solo biblioteca estándar, Python 3.8+.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

COMPILER_VERSION = "1.1.0"

BLOCK_RE = re.compile(
    r"<!-- BEGIN (\w+) -->\s*```text[ \t]*\n(.*?)\n[ \t]*```\s*<!-- END \1 -->",
    re.DOTALL,
)
MARKER_RE = re.compile(r"<!-- BEGIN \w+ -->")
FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)

SCALES = ("wide", "full", "medium", "close-up", "insert")
MEDIUM_OR_CLOSER = {"medium", "close-up", "insert"}
TIER2_SCALES = {"medium", "close-up"}  # un insert solo lleva los TIER3_* que pida
CLOSE = {"close-up", "insert"}
CAMERA_MOTIONS = {"static", "slow", "fast"}
TEXT_KEYS = ("id", "scale", "camera_directive", "camera_motion", "state",
             "pose", "action", "setting", "aspect_ratio")
SHOT_KEYS = set(TEXT_KEYS) | {"include_composition", "duration", "details"}

# Capacidades verificadas en el catálogo de Higgsfield (models_explore).
# Antes de añadir un modelo: ¿tiene campo negativo? ¿qué roles de media acepta?
# base_params fija de forma explícita los valores que cambian el resultado, para
# no depender de los defaults de la plataforma. El audio va apagado porque en una
# serie el sonido se monta en postproducción; cámbialo aquí si lo quieres generado.
MODEL_PROFILES = {
    "seedance_2_5": {
        "output": "video",
        "negative_field": None,
        "reference_role": "image_references",
        "reference_params": {"mode": "omni_reference"},
        "base_params": {"resolution": "720p", "generate_audio": False},
        "duration": (4, 30),
        "aspect_ratios": {"auto", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"},
        "max_words": None,  # fija tu presupuesto tras las primeras pruebas
    },
    "kling3_0": {
        "output": "video",
        "negative_field": None,
        "reference_role": None,  # solo start_image / end_image
        "reference_params": {},
        "base_params": {"mode": "std", "sound": "off"},
        "duration": (3, 15),
        "aspect_ratios": {"16:9", "9:16", "1:1"},
        "max_words": None,
    },
    "seedance_2_0": {
        "output": "video",
        "negative_field": None,
        "reference_role": "image_references",
        "reference_params": {},
        # 720p + std + high bitrate entran en la prueba ilimitada.
        # genre es una decisión de proyecto: "epic" para esta serie.
        "base_params": {"resolution": "720p", "mode": "std", "bitrate_mode": "high",
                        "genre": "epic", "generate_audio": False},
        "duration": (4, 15),
        "aspect_ratios": {"auto", "16:9", "9:16", "4:3", "3:4", "1:1", "21:9"},
        "max_words": None,
    },
}



class CompileError(Exception):
    pass


def read_text(path: Path) -> str:
    # utf-8-sig descarta el BOM que añaden algunos editores de Windows.
    return path.read_text(encoding="utf-8-sig")


def parse_front_matter(raw: str) -> dict:
    """Subconjunto de YAML: escalares, listas en línea [a, b] y listas con guion.
    Cualquier otra sintaxis (bloques | o >, mapas anidados) aborta con error."""
    meta: dict = {}
    key = None
    for line in raw.splitlines():
        line = line.split(" #", 1)[0].rstrip()
        if not line.strip():
            continue
        item = re.match(r"\s+-\s+(.+)", line)
        if item and isinstance(meta.get(key), list):
            meta[key].append(item.group(1).strip().strip("'\""))
            continue
        kv = re.match(r"([\w-]+):\s*(.*)", line)
        if not kv:
            raise CompileError(f"front matter: línea no reconocida: {line!r}")
        key, value = kv.group(1), kv.group(2).strip()
        if value == "":
            meta[key] = []
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            meta[key] = [v.strip().strip("'\"") for v in inner.split(",")] if inner else []
        else:
            meta[key] = value.strip("'\"")
    return meta


def load_config(path: Path, required: set[str]) -> dict:
    text = read_text(path)
    fm = FRONT_MATTER_RE.match(text)
    if not fm:
        raise CompileError(f"{path}: falta el front matter (--- ... ---) al inicio")
    meta = parse_front_matter(fm.group(1))

    matches = list(BLOCK_RE.finditer(text))
    n_markers = len(MARKER_RE.findall(text))
    if n_markers != len(matches):
        raise CompileError(f"{path}: {n_markers} marcadores BEGIN pero {len(matches)} "
                           "bloques válidos; revisa los END y las líneas ```text")
    blocks: dict[str, str] = {}
    for m in matches:
        if m.group(1) in blocks:
            raise CompileError(f"{path}: bloque duplicado {m.group(1)}")
        blocks[m.group(1)] = " ".join(m.group(2).split())

    exports = meta.get("exports")
    if not isinstance(exports, list):
        raise CompileError(f"{path}: falta la lista 'exports' en el front matter")
    if set(exports) != set(blocks):
        raise CompileError(
            f"{path}: 'exports' no coincide con los bloques. "
            f"Declarados sin bloque: {sorted(set(exports) - set(blocks))}. "
            f"Bloques sin declarar: {sorted(set(blocks) - set(exports))}")
    missing = required - set(blocks)
    if missing:
        raise CompileError(f"{path}: faltan bloques obligatorios {sorted(missing)}")

    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return {"meta": meta, "blocks": blocks,
            "ref": f"{meta.get('id', path.stem)}@{meta.get('version', '?')}#{digest}"}


def sentence(text: str) -> str:
    text = " ".join(text.split())
    return text if not text or text[-1] in ".!?" else text + "."


def merge_negatives(*chunks: str) -> list[str]:
    seen, out = set(), []
    for chunk in chunks:
        for term in chunk.split(","):
            term = " ".join(term.split())
            if term and term.lower() not in seen:
                seen.add(term.lower())
                out.append(term)
    return out


def compile_shot(char: dict, style: dict, shot: dict, model: str) -> dict:
    profile = MODEL_PROFILES[model]
    cb, sb = char["blocks"], style["blocks"]
    sid = shot.get("id")

    def fail(msg: str):
        raise CompileError(f"toma {sid!r}: {msg}")

    # --- Validación ---
    unknown = set(shot) - SHOT_KEYS
    if unknown:
        fail(f"claves desconocidas {sorted(unknown)}")
    for k in TEXT_KEYS:
        if k in shot and not isinstance(shot[k], str):
            fail(f"'{k}' debe ser texto")
    if "include_composition" in shot and not isinstance(shot["include_composition"], bool):
        fail("'include_composition' debe ser true o false")

    scale = shot.get("scale")
    if scale not in SCALES:
        fail(f"scale debe ser uno de {list(SCALES)}, recibido {scale!r}")
    motion = shot.get("camera_motion")
    if motion is not None and motion not in CAMERA_MOTIONS:
        fail(f"camera_motion debe ser uno de {sorted(CAMERA_MOTIONS)}")
    if scale in CLOSE and motion is None:
        fail("los planos close-up/insert requieren camera_motion")

    state = shot.get("state", "STATE_CALM")
    if not state.startswith("STATE_") or state not in cb:
        fail(f"estado inexistente {state!r}")
    pose = shot.get("pose")
    if pose is not None:
        if not pose.startswith("POSE_") or pose not in cb:
            fail(f"pose inexistente {pose!r}")
        if pose in char["meta"].get("min_scale_medium", []) and scale not in MEDIUM_OR_CLOSER:
            fail(f"{pose} solo se permite en planos medium o más cerrados")
    if not pose and not shot.get("action"):
        fail("indica 'pose', 'action' o ambos")

    details = shot.get("details", [])
    if not isinstance(details, list) or not all(isinstance(d, str) for d in details):
        fail("'details' debe ser una lista de IDs TIER3_*")
    if len(set(details)) != len(details):
        fail("'details' tiene IDs repetidos")
    for d in details:
        if not d.startswith("TIER3_") or d not in cb:
            fail(f"detalle inexistente {d!r}")
    if details and not (scale in CLOSE and motion in {"static", "slow"}):
        fail("'details' solo se permite en close-up/insert con camera_motion static o slow")

    warnings: list[str] = []
    is_video = profile["output"] == "video"
    parts: list[tuple[str, str]] = []

    def add(label: str, text: str):
        parts.append((label, sentence(text)))

    # --- Ensamblado (orden del contrato) ---
    if shot.get("camera_directive"):
        add("shot.camera_directive", shot["camera_directive"])
    add("CORE_IDENTITY", cb["CORE_IDENTITY"])
    if scale in TIER2_SCALES and "DETAIL_TIER_2" in cb:
        add("DETAIL_TIER_2", cb["DETAIL_TIER_2"])
    for d in details:
        add(d, cb[d])
    add(state, cb[state])
    if pose:
        add(pose, cb[pose])
    if shot.get("action"):
        add("shot.action", shot["action"])
    if shot.get("setting"):
        add("shot.setting", shot["setting"])
    else:
        warnings.append("sin setting: el modelo decidirá el entorno")
    if is_video and "MOTION_BEHAVIOR" in cb:
        add("MOTION_BEHAVIOR", cb["MOTION_BEHAVIOR"])
    add("STYLE_ANCHORS", sb["STYLE_ANCHORS"])
    if is_video:
        if "STYLE_MOTION" not in sb:
            fail("el modelo es de video y el estilo no exporta STYLE_MOTION")
        add("STYLE_MOTION", sb["STYLE_MOTION"])
    # La composición del estilo solo entra por defecto si la toma no define entorno.
    if shot.get("include_composition", not shot.get("setting")) and "STYLE_COMPOSITION" in sb:
        add("STYLE_COMPOSITION", sb["STYLE_COMPOSITION"])

    # --- Negativos según el modelo ---
    if profile["negative_field"] is None:
        if "NEGATIVE_FALLBACK" not in cb:
            fail(f"{model} no tiene campo negativo y el personaje no exporta NEGATIVE_FALLBACK")
        add("NEGATIVE_FALLBACK", cb["NEGATIVE_FALLBACK"])
        if "STYLE_NEGATIVE_FALLBACK" in sb:
            add("STYLE_NEGATIVE_FALLBACK", sb["STYLE_NEGATIVE_FALLBACK"])

    prompt = " ".join(text for _, text in parts)
    words = len(prompt.split())
    if profile["max_words"] and words > profile["max_words"]:
        fail(f"{words} palabras; el presupuesto de {model} es {profile['max_words']}")

    params: dict = {"model": model, "prompt": prompt}
    params.update(profile["base_params"])
    if profile["negative_field"]:
        params[profile["negative_field"]] = ", ".join(
            merge_negatives(cb["CHARACTER_NEGATIVES"], sb["STYLE_NEGATIVES"]))

    duration = shot.get("duration")
    if duration is not None:
        rng = profile.get("duration")
        if type(duration) is not int or (rng and not rng[0] <= duration <= rng[1]):
            fail(f"duration inválida para {model}: {duration!r} (rango {rng})")
        params["duration"] = duration
    ratio = shot.get("aspect_ratio")
    if ratio is not None:
        allowed = profile.get("aspect_ratios")
        if allowed and ratio not in allowed:
            fail(f"aspect_ratio {ratio!r} no soportado por {model}: {sorted(allowed)}")
        params["aspect_ratio"] = ratio

    refs = char["meta"].get("reference_images", [])
    if refs and profile["reference_role"]:
        params.update(profile["reference_params"])
        params["medias"] = [{"role": profile["reference_role"], "value": r} for r in refs]
    elif refs:
        warnings.append(f"{model} no acepta referencias de identidad; se omitieron {len(refs)}")
    else:
        warnings.append("sin reference_images: la consistencia depende solo del texto")

    return {
        "shot_id": sid,
        "params": params,
        "manifest": {
            "compiler": COMPILER_VERSION,
            "character": char["ref"],
            "style": style["ref"],
            "blocks": [label for label, _ in parts],
            "negatives": "field" if profile["negative_field"] else "fallback",
            "word_count": words,
            "warnings": warnings,
        },
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Compila tomas a params de Higgsfield.")
    ap.add_argument("storyboard", type=Path, help="JSON con una lista de tomas, en orden de montaje")
    ap.add_argument("--model", required=True, choices=sorted(MODEL_PROFILES))
    ap.add_argument("--character", type=Path, default=Path("config/character.md"))
    ap.add_argument("--style", type=Path, default=Path("config/style-guide.md"))
    ap.add_argument("--out", type=Path, help="archivo de salida; por defecto, stdout")
    args = ap.parse_args(argv)

    try:
        char = load_config(args.character, {"CORE_IDENTITY", "STATE_CALM", "CHARACTER_NEGATIVES"})
        style = load_config(args.style, {"STYLE_ANCHORS", "STYLE_NEGATIVES"})
        for key in ("reference_images", "min_scale_medium"):
            if not isinstance(char["meta"].get(key, []), list):
                raise CompileError(f"{args.character}: '{key}' debe ser una lista")
        shots = json.loads(read_text(args.storyboard))
        if not isinstance(shots, list) or not shots:
            raise CompileError("storyboard.json debe ser una lista no vacía")
        ids = [s.get("id") if isinstance(s, dict) else None for s in shots]
        if None in ids or len(set(map(str, ids))) != len(ids):
            raise CompileError("cada toma necesita un 'id' único")
        result = [compile_shot(char, style, s, args.model) for s in shots]

        output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.out:
            with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(output)
        else:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8", newline="\n")
            sys.stdout.write(output)
    except (CompileError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())