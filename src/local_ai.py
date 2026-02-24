import os
import re
import wave
import math
import struct
from uuid import uuid4
from typing import List
from importlib import import_module
from importlib.util import find_spec

from PIL import Image, ImageDraw, ImageFont

from config import (
    ROOT_DIR,
    get_font,
    get_fonts_dir,
    get_local_ai_provider,
    get_local_hf_model_dir,
    get_local_hf_model_id,
)

_HF_PIPELINE = None
_HF_DISABLED = False


def _load_hf_pipeline():
    global _HF_PIPELINE, _HF_DISABLED

    if _HF_PIPELINE is not None or _HF_DISABLED:
        return _HF_PIPELINE

    if get_local_ai_provider() != "hf_transformers":
        return None

    if find_spec("transformers") is None or find_spec("torch") is None:
        _HF_DISABLED = True
        return None

    transformers = import_module("transformers")

    model_dir = get_local_hf_model_dir()
    model_id = get_local_hf_model_id()
    selected_model = model_dir if os.path.isdir(model_dir) else model_id

    try:
        _HF_PIPELINE = transformers.pipeline(
            "text-generation",
            model=selected_model,
            tokenizer=selected_model,
            device=-1,
        )
    except Exception:
        _HF_DISABLED = True
        return None

    return _HF_PIPELINE


def _hf_generate(prompt: str, max_new_tokens: int = 90) -> str:
    pipe = _load_hf_pipeline()
    if pipe is None:
        return ""

    try:
        out = pipe(
            prompt,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            num_return_sequences=1,
            pad_token_id=pipe.tokenizer.eos_token_id,
        )
    except Exception:
        return ""

    if not out:
        return ""

    raw = out[0].get("generated_text", "")
    return raw[len(prompt):].strip() if raw.startswith(prompt) else raw.strip()


def local_text_response(prompt: str, niche: str = "", language: str = "fr") -> str:
    """Retourne une réponse locale simple (sans API)."""
    hf_response = _hf_generate(prompt, max_new_tokens=80)
    if hf_response:
        return hf_response

    low = prompt.lower()

    if "youtube video title" in low:
        return f"{niche.title()} : astuces rapides #{language} #shorts"[:95]
    if "video description" in low:
        return f"Vidéo générée localement sur {niche}. Donne ton avis en commentaire."
    if "twitter post" in low:
        return f"Astuce rapide sur {niche}: commence petit, reste régulier, mesure tes progrès."
    if "specific video idea" in low or "topic" in low:
        return f"3 erreurs fréquentes en {niche} et comment les éviter facilement."
    if "image prompts" in low:
        prompts = [
            f"Illustration cinématique de {niche}, lumière naturelle, plan détaillé",
            f"Scène pédagogique sur {niche}, ambiance chaleureuse, style réaliste",
            f"Visuel vertical créatif lié à {niche}, couleurs contrastées",
            f"Infographie visuelle de {niche}, composition claire",
            f"Mise en situation moderne autour de {niche}, rendu propre",
        ]
        return str(prompts).replace("'", '"')

    clean = re.sub(r"\s+", " ", prompt).strip()
    return clean[:240]


def local_script(subject: str, sentence_count: int = 8, language: str = "fr") -> str:
    hf_prompt = (
        f"Écris un script vidéo court en {language} sur: {subject}. "
        f"Donne exactement {sentence_count} phrases courtes."
    )
    hf_script = _hf_generate(hf_prompt, max_new_tokens=140)
    if hf_script:
        return hf_script

    base = [
        f"Aujourd'hui on parle de {subject}.",
        "Commence par définir un objectif simple et mesurable.",
        "Ensuite, applique une méthode répétable chaque jour.",
        "Évite de compliquer les premières étapes.",
        "Teste rapidement puis corrige ce qui bloque.",
        "Observe les résultats et note ce qui fonctionne.",
        "Automatise les actions utiles dès que possible.",
        "Avec de la constance, les progrès deviennent visibles.",
        "Reste patient et améliore un détail à la fois.",
        "Tu peux démarrer maintenant avec les ressources locales."
    ]
    return " ".join(base[:max(3, min(sentence_count, len(base)))])


def generate_local_image(prompt: str) -> str:
    """Crée une image locale simple avec texte."""
    image_path = os.path.join(ROOT_DIR, ".mp", f"{uuid4()}.png")
    img = Image.new("RGB", (1080, 1920), color=(20, 24, 28))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(os.path.join(get_fonts_dir(), get_font()), 42)
    except Exception:
        font = ImageFont.load_default()

    text = prompt[:220]
    wrapped = []
    words = text.split()
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        if len(test) > 32:
            wrapped.append(line)
            line = w
        else:
            line = test
    if line:
        wrapped.append(line)

    y = 200
    for l in wrapped[:18]:
        draw.text((80, y), l, fill=(245, 245, 245), font=font)
        y += 72

    draw.rectangle((50, 50, 1030, 1870), outline=(255, 208, 0), width=5)
    img.save(image_path)
    return image_path


def generate_local_subtitles(script: str, output_path: str) -> str:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", script) if s.strip()]
    cur = 0
    lines: List[str] = []
    for idx, sentence in enumerate(sentences, start=1):
        start = cur
        dur = max(2, min(6, len(sentence) // 20 + 1))
        end = cur + dur
        cur = end

        def fmt(sec: int) -> str:
            h = sec // 3600
            m = (sec % 3600) // 60
            s = sec % 60
            return f"{h:02}:{m:02}:{s:02},000"

        lines.append(f"{idx}\n{fmt(start)} --> {fmt(end)}\n{sentence}\n")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return output_path


def synthesize_beep_speech(text: str, output_file: str, sample_rate: int = 22050) -> str:
    """Fallback TTS local: génère une onde (sans dépendance premium)."""
    duration = max(2, min(30, len(text) // 18))
    freq = 220.0
    with wave.open(output_file, "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for i in range(int(duration * sample_rate)):
            value = int(12000.0 * math.sin(2 * math.pi * freq * (i / sample_rate)))
            wav_file.writeframesraw(struct.pack("<h", value))
    return output_file
