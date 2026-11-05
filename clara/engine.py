
"""Independent, auditable Spanish-language retrieval and teach-back engine.
This is a rule-based NLP baseline; no proprietary models, no LLM calls.
Automated assessments are exploratory and must not be interpreted as clinical advice.
"""
from __future__ import annotations
import json
import math
import re
import unicodedata
from collections import Counter
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).parent / "data" / "es.json"
SOURCE_ALLOWLIST = ("https://www.who.int/", "https://www.cdc.gov/", "https://www.minsal.cl/")

@lru_cache(maxsize=1)
def get_data():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    for source in data["sources"]:
        if not source["url"].startswith(SOURCE_ALLOWLIST):
            raise ValueError("Unrecognized reference domain")
    return data

def normalize(text):
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(ch for ch in text if not unicodedata.combining(ch))

def tokens(text):
    return set(re.findall(r"[a-z0-9]+", normalize(text))) - {
        "que", "como", "para", "por", "con", "los", "las", "una", "uno", "del", "en", "de", "la", "el", "mi", "me", "es", "un", "y", "se", "puedo", "puede", "sirve", "tengo", "sobre", "hace", "hacer", "hay", "si", "al", "cuanto", "cuando", "cual", "cuales", "despues", "antes"
    }

def _sources(ids):
    sources = {entry["id"]: entry for entry in get_data()["sources"]}
    return [sources[source_id] for source_id in ids]

# Guardrails are checked before FAQ routing. They return no personal diagnosis.
URGENT_PATTERNS = [
    r"\b(agresion|violacion|violaron|abusaron|abuso sexual|forzar|forzaron|me obligaron|sin consentimiento)\b",
    r"\b(dolor (abdominal |de vientre )?(muy )?intenso|desmayo|sangrado (muy )?abundante|hemorragia)\b",
]

def _urgent(text):
    n = normalize(text)
    return any(re.search(p, n) for p in URGENT_PATTERNS)

def _similarity(q, entry):
    qn = normalize(q)
    qt = tokens(q)
    expressions = entry["keywords"] + [entry["label"]]
    exact_phrase = max((len(normalize(k).split()) for k in expressions if len(normalize(k)) >= 3 and normalize(k) in qn), default=0)
    overlap = max((len(qt & tokens(k)) / max(len(tokens(k)), 1) for k in expressions), default=0)
    return round(exact_phrase * 1.2 + overlap * 2, 4)

def answer_question(question):
    q = question.strip()
    if not q or len(q) > 900:
        raise ValueError("La pregunta debe contener entre 1 y 900 caracteres.")
    data = get_data()
    if _urgent(q):
        category = "violencia" if re.search(URGENT_PATTERNS[0], normalize(q)) else "efectos"
        entry = next(item for item in data["faqs"] if item["id"] == category)
        return _format_answer(entry, warning=True)
    # User-facing safety and intent routing: strong signals override generic vocabulary.
    qn = normalize(q)
    if re.search(r"\b(vomit|vomito|vomite|nausea|nauseas)\w*\b", qn):
        return _format_answer(next(e for e in data["faqs"] if e["id"] == "efectos"))
    if re.search(r"\b(fertilidad|infertilidad|esterilidad)\b", qn):
        return _format_answer(next(e for e in data["faqs"] if e["id"] == "fertilidad"))
    if re.search(r"\b(its|ets|vih|sida|infecciones de transmision|enfermedades de transmision)\b", qn):
        return _format_answer(next(e for e in data["faqs"] if e["id"] == "its"))
    if re.search(r"\b(rompio|fallo|roto|rompe)\b.{0,30}\b(condon|preservativo)\b|\b(condon|preservativo)\b.{0,30}\b(rompio|fallo|roto|rompe)\b", qn):
        return _format_answer(next(e for e in data["faqs"] if e["id"] == "que-es"))
    if re.search(r"\b([2345]|dos|tres|cuatro|cinco)\s+dias\b|\b(cuanto tarda|hace [2345] dias)\b", qn):
        return _format_answer(next(e for e in data["faqs"] if e["id"] == "cuando"))
    # Specific clinically important misconception queries take priority over generic terms.
    if re.search(r"\b(aborto|abortiva|interrumpe (?:un |el )?embarazo|embarazo establecido)\b", normalize(q)):
        return _format_answer(next(e for e in data["faqs"] if e["id"] == "aborto"))
    ranked = sorted(((_similarity(q, e), e) for e in data["faqs"]), key=lambda x:x[0], reverse=True)
    best_score, best = ranked[0]
    # No fabrication: do not answer if routing confidence is weak.
    if best_score < 1.45:
        return {
            "matched": False, "warning": False, "topic_id": None,
            "title": "Necesito una pregunta más concreta",
            "answer": "Todavía no tengo una respuesta suficientemente revisada para esa pregunta. Puedes elegir una de las dudas disponibles o consultar con un profesional sanitario. Si hay una urgencia médica, busca atención inmediata.",
            "next": "Prueba con: ¿cuánto tiempo tengo? o ¿produce un aborto?",
            "sources": []
        }
    return _format_answer(best)

def _format_answer(entry, warning=False):
    return {
        "matched": True, "warning": warning, "topic_id": entry["id"],
        "title": entry["label"], "answer": entry["answer"],
        "next": entry["next"], "sources": _sources(entry["source_ids"])
    }

def _contains(text, patterns):
    return any(re.search(pattern, text) for pattern in patterns)

def _near_no(text, match, distance=28):
    preceding = text[max(0, match.start()-distance):match.start()]
    return bool(re.search(r"\b(no|nunca|tampoco|ni|sin)\b(?:\W+\w+){0,3}\W*$", preceding))

def misconception_codes(text):
    n = normalize(text)
    result = []
    for match in re.finditer(r"\b(provoca|produce|causa|genera|es|equivale a|interrumpe|termina|elimina)\s+(?:un\s+|el\s+|al\s+)?(?:aborto|embarazo (?:ya )?establecido)\b", n):
        if not _near_no(n, match):
            result.append("abortion")
            break
    if _contains(n, [r"\b(solo|solamente|unicamente)\b.{0,30}\b(24 horas|un dia|72 horas|tres dias)\b",r"\b(ya no sirve|no funciona)\b.{0,25}\b(3 dias|72 horas)\b", r"\b(desde|despues de)\s+(?:los\s+)?(?:6|7|8|10|seis|siete|ocho|diez)\s+dias\s+(?:si|todavia)?\s*(?:sirve|funciona|efectiva)"]):
        result.append("wrong_window")
    for match in re.finditer(r"\b(protege|previene|evita)\b.{0,40}\b(its|ets|vih|sida|infecciones|enfermedades sexuales|enfermedades de transmision)\b", n):
        if not _near_no(n, match):
            result.append("sti_protection")
            break
    return list(dict.fromkeys(result))

def detected_concepts(text):
    n = normalize(text)
    concept = {}
    concept["prevent"] = _contains(n, [r"\b(previen|prevenir|evit|impid|preven)\w*\b.{0,50}\b(embarazo|quedar embarazada)",r"\b(no quedar embarazada|no embarazarse)",r"\b(embarazo|embarazada)\b.{0,40}\b(previen|evit|impid)\w*"])
    concept["no_abortion"] = _contains(n, [r"\b(no|nunca|tampoco)\b.{0,35}\b(aborto|abortiva|interrumpe|interrumpir embarazo)", r"\b(no es abortiva|no provoca aborto|no causa un aborto|no termina un embarazo)"])
    concept["five_days"] = _contains(n, [r"\b(5|cinco)\s+dias\b", r"\b120\s+horas\b"])
    concept["earlier"] = _contains(n, [r"\b(lo antes posible|cuanto antes|mas pronto|lo mas rapido|a tiempo|apenas posible)\b",r"\b(antes|pronto|rapido)\b.{0,40}\b(mejor|eficaz|efectiv)\w*"])
    concept["not_sti"] = _contains(n, [r"\b(no|nunca|tampoco)\b.{0,32}\b(proteg|previen|evit)\w*.{0,36}\b(its|ets|vih|infecciones|enfermedades)", r"\b(its|ets|vih|infecciones)\b.{0,30}\b(no protege|no previene)"])
    concept["condom"] = _contains(n, [r"\b(condon|condones|preservativo|preservativos)\b"])
    return concept

MISCONCEPTION_FEEDBACK = {
    "abortion":"Cuidado: la anticoncepción de emergencia no provoca abortos ni interrumpe embarazos establecidos.",
    "wrong_window":"Cuidado con los plazos: en general existen opciones hasta cinco días (120 horas), pero conviene actuar cuanto antes.",
    "sti_protection":"Importante: la anticoncepción de emergencia no protege contra infecciones de transmisión sexual."
}

def assess(lesson_id, response, phase="pre"):
    lessons = {x["id"]: x for x in get_data()["lessons"]}
    if lesson_id not in lessons:
        raise ValueError("Lección no disponible")
    if phase not in ("pre", "post"):
        raise ValueError("La fase debe ser pre o post")
    response = response.strip()
    if not response or len(response) > 1200:
        raise ValueError("La explicación debe contener entre 1 y 1200 caracteres")
    lesson = lessons[lesson_id]
    matches = detected_concepts(response)
    misconceptions = [m for m in misconception_codes(response) if m in lesson["misconceptions"]]
    hits = [c for c in lesson["concepts"] if matches[c["id"]]]
    missing = [c for c in lesson["concepts"] if not matches[c["id"]]]
    concept_coverage = round(100 * len(hits) / len(lesson["concepts"]))
    # A critical misconception must not produce an apparently reassuring high score.
    score = min(concept_coverage, 25) if misconceptions else concept_coverage
    if misconceptions:
        status = "misconception"
    elif not missing:
        status = "complete"
    else:
        status = "partial"
    summary = {
        "complete":"Identificaste los conceptos centrales de esta explicación.",
        "partial":"Hay elementos importantes que aún podemos aclarar.",
        "misconception":"Detecté una posible idea incorrecta que conviene revisar."
    }[status]
    feedback = [MISCONCEPTION_FEEDBACK[m] for m in misconceptions] + [c["hint"] for c in missing]
    if not feedback:
        feedback = ["Buen trabajo. Recuerda que cada situación personal debe evaluarse con apoyo sanitario cuando corresponda."]
    return {
        "lesson_id":lesson_id,"phase":phase, "status":status,
        "score":score,"concept_coverage":concept_coverage,"summary":summary, "covered":[c["name"] for c in hits],
        "missing":[c["name"] for c in missing], "misconceptions":misconceptions,
        "feedback":feedback, "rubric_version":"heuristic-es-v0.1",
        "interpretation":"Índice exploratorio basado en conceptos detectados, penalizado ante posibles errores críticos. No es una evaluación clínica validada."
    }

def catalog():
    data = get_data()
    return {"locale":data["locale"],"module":data["module"],"version":data["version"],
            "review_status":data["review_status"],
            "faqs":[{"id":f["id"],"label":f["label"]} for f in data["faqs"]],
            "lessons":[{"id":l["id"],"title":l["title"],"intro":l["intro"],"question":l["question"]} for l in data["lessons"]],
            "sources":data["sources"]}
