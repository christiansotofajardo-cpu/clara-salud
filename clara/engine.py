
"""CLARA Salud — motor educativo en español, versión 0.3.

Repositorio abierto e independiente de tecnologías propietarias.
Respuestas acotadas a contenido documentado; evaluación heurística,
no validada clínicamente. No realiza recomendaciones médicas individuales.
Compatible con clara/main.py: catalog(), answer_question(), assess().
"""

from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data" / "es.json"
SOURCE_ALLOWLIST = (
    "https://www.who.int/",
    "https://www.cdc.gov/",
    "https://www.minsal.cl/",
)

STOPWORDS = {
    "que", "como", "para", "por", "con", "los", "las", "una", "uno",
    "del", "en", "de", "la", "el", "mi", "me", "es", "un", "y", "se",
    "puedo", "puede", "sirve", "tengo", "sobre", "hace", "hacer", "hay",
    "si", "al", "cuanto", "cuando", "cual", "cuales", "despues", "antes",
}


@lru_cache(maxsize=1)
def get_data():
    """Carga las preguntas y rúbricas desde el JSON público del proyecto."""
    data = json.loads(DATA.read_text(encoding="utf-8"))
    for source in data["sources"]:
        if not source["url"].startswith(SOURCE_ALLOWLIST):
            raise ValueError("Dominio de fuente no permitido")
    return data


def normalize(value):
    value = unicodedata.normalize("NFKD", value.lower())
    return "".join(c for c in value if not unicodedata.combining(c))


def tokens(value):
    return set(re.findall(r"[a-z0-9]+", normalize(value))) - STOPWORDS


def matches(value, *patterns):
    return any(re.search(pattern, value) for pattern in patterns)


def _sources(ids):
    source_map = {item["id"]: item for item in get_data()["sources"]}
    return [source_map[x] for x in ids if x in source_map]


def _faq(faq_id):
    return next(item for item in get_data()["faqs"] if item["id"] == faq_id)


def _format_answer(entry, warning=False):
    return {
        "matched": True,
        "warning": warning,
        "topic_id": entry["id"],
        "title": entry["label"],
        "answer": entry["answer"],
        "next": entry["next"],
        "sources": _sources(entry["source_ids"]),
    }


def _uncertain():
    return {
        "matched": False,
        "warning": False,
        "topic_id": None,
        "title": "Todavía no tengo una respuesta revisada para esa duda",
        "answer": (
            "Por ahora, CLARA ofrece información educativa sobre anticoncepción "
            "de emergencia y una orientación general sobre métodos anticonceptivos. "
            "No sería seguro inventar una respuesta fuera de esa biblioteca. "
            "Puedes elegir una pregunta sugerida o consultar con una matrona "
            "u otro profesional sanitario. Si hay una urgencia, busca atención inmediata."
        ),
        "next": (
            "Prueba con: «¿Qué métodos anticonceptivos existen?», "
            "«¿Cuánto tiempo tengo para utilizar anticoncepción de emergencia?» "
            "o «¿Produce un aborto?»."
        ),
        "sources": [],
    }


def _general_contraception():
    """Respuesta general, no una elección personalizada de anticonceptivo."""
    return {
        "matched": True,
        "warning": False,
        "topic_id": "anticoncepcion-general",
        "title": "¿Qué método anticonceptivo es mejor?",
        "answer": (
            "No existe un método anticonceptivo que sea el mejor para todas "
            "las personas. Los implantes y los dispositivos intrauterinos (DIU) "
            "están entre los métodos reversibles más eficaces para prevenir "
            "embarazos. También hay píldoras, inyecciones, parches, anillos "
            "vaginales y preservativos. Los preservativos ayudan además a "
            "reducir el riesgo de infecciones de transmisión sexual. "
            "Para elegir conviene considerar la eficacia, los efectos "
            "secundarios, la disponibilidad, las preferencias y las "
            "circunstancias de salud. Una matrona u otro profesional "
            "sanitario puede ayudarte a comparar opciones y tomar una "
            "decisión informada."
        ),
        "next": (
            "¿Te interesa conocer los métodos de larga duración, los "
            "hormonales o la diferencia con la anticoncepción de emergencia? "
            "CLARA aún no ofrece recomendaciones personalizadas."
        ),
        "sources": [
            {
                "id": "who-general",
                "name": "OMS · Métodos anticonceptivos",
                "url": "https://www.who.int/news-room/fact-sheets/detail/family-planning-contraception",
            },
            {
                "id": "cdc-general",
                "name": "CDC · Contraception and Birth Control Methods",
                "url": "https://www.cdc.gov/contraception/about/index.html",
            },
        ],
    }


def _similarity(question, entry):
    """Coincidencia conservadora de expresiones, sin fingir entender semántica."""
    qn = normalize(question)
    qt = tokens(question)
    expressions = entry["keywords"] + [entry["label"]]
    phrase_length = max(
        (
            len(normalize(expr).split())
            for expr in expressions
            if len(normalize(expr)) >= 3 and normalize(expr) in qn
        ),
        default=0,
    )
    overlap = max(
        (
            len(qt & tokens(expr)) / max(len(tokens(expr)), 1)
            for expr in expressions
        ),
        default=0,
    )
    return phrase_length * 1.2 + overlap * 2


def answer_question(question):
    """Responde solo mediante entradas identificadas o textos de alcance fijo."""
    q = question.strip()
    if not 1 <= len(q) <= 900:
        raise ValueError("La pregunta debe contener entre 1 y 900 caracteres.")

    n = normalize(q)

    # Seguridad: estas señales siempre preceden a la búsqueda por similitud.
    if matches(
        n,
        r"\b(agresion sexual|violacion|violaron|abuso sexual|abusaron|"
        r"me obligaron|sin consentimiento|violencia sexual|me forzaron)\b",
    ):
        return _format_answer(_faq("violencia"), warning=True)

    if matches(
        n,
        r"\b(dolor (abdominal |de vientre )?(muy )?intenso|"
        r"desmayo|sangrado (muy )?abundante|hemorragia)\b",
    ):
        return _format_answer(_faq("efectos"), warning=True)

    # Preguntas personales de riesgo/contraindicaciones requieren atención individual.
    if matches(
        n,
        r"\b(cancer|trombosis|coagulos|anticoagulantes|"
        r"contraindicaciones|interacciones medicamentosas|"
        r"alergia|lactancia|amamantar)\b",
    ):
        return _uncertain()

    emergency = matches(
        n,
        r"\b(emergencia|urgencia|postcoital|dia despues|"
        r"pastilla del dia siguiente|pildora del dia siguiente)\b",
    )
    general = matches(
        n,
        r"\b(anticonceptiv\w*|anticoncepcion regular|"
        r"planificacion familiar|control de natalidad)\b",
    ) or (
        matches(n, r"\b(metodos?|opciones)\b")
        and matches(n, r"\b(embaraz\w*|no embarazarme|evitar embarazo)\b")
    )

    # La anticoncepción general no debe redirigirse a la de emergencia.
    if general and not emergency:
        return _general_contraception()

    # Rutas explícitas del módulo de anticoncepción de emergencia.
    routes = [
        ("efectos", r"\b(vomit\w*|nausea\w*|efectos secundarios)\b"),
        ("fertilidad", r"\b(fertilidad|infertilidad|esterilidad)\b"),
        ("its", r"\b(its|ets|vih|sida|infecciones? de transmision|"
         r"enfermedades? de transmision)\b"),
        ("aborto", r"\b(aborto|abortiva|embarazo establecido|"
         r"interrumpe (?:un |el )?embarazo)\b"),
        ("periodo", r"\b(menstruacion|regla atrasada|retraso menstrual|"
         r"prueba de embarazo|test de embarazo)\b"),
        ("cuando", r"\b(\d|dos|tres|cuatro|cinco)\s+dias\b|"
         r"\b(\d+|\d{2,3})\s+horas\b"),
        ("acceso", r"\b(cesfam|farmacia|consultorio|donde conseguir|"
         r"donde comprar)\b"),
    ]

    for faq_id, pattern in routes:
        if re.search(pattern, n):
            return _format_answer(_faq(faq_id))

    if re.search(
        r"\b(rompio|fallo|roto|rompe)\b.{0,30}\b(condon|preservativo)\b|"
        r"\b(condon|preservativo)\b.{0,30}\b(rompio|fallo|roto|rompe)\b",
        n,
    ):
        return _format_answer(_faq("que-es"))

    ranked = sorted(
        ((_similarity(q, faq), faq) for faq in get_data()["faqs"]),
        key=lambda pair: pair[0],
        reverse=True,
    )
    if not ranked or ranked[0][0] < 1.45:
        return _uncertain()
    return _format_answer(ranked[0][1])


def _near_negation(text, match, distance=40):
    """Busca negación cercana previa; aproximación, no análisis sintáctico."""
    preceding = text[max(0, match.start() - distance):match.start()]
    return bool(re.search(
        r"\b(no|nunca|tampoco|ni|sin)\b(?:\W+\w+){0,4}\W*$",
        preceding,
    ))


def misconception_codes(text):
    n = normalize(text)
    errors = []
    for match in re.finditer(
        r"\b(provoca|produce|causa|genera|es|equivale a|"
        r"interrumpe|termina|elimina)\s+"
        r"(?:un\s+|el\s+|al\s+)?"
        r"(?:aborto|embarazo (?:ya )?establecido)\b",
        n,
    ):
        if not _near_negation(n, match):
            errors.append("abortion")
            break

    if matches(
        n,
        r"\b(solo|solamente|unicamente)\b.{0,30}"
        r"\b(24 horas|un dia|72 horas|tres dias)\b",
        r"\b(ya no sirve|no funciona)\b.{0,25}\b(3 dias|72 horas)\b",
        r"\b(desde|despues de)\s+(?:los\s+)?"
        r"(?:6|7|8|10|seis|siete|ocho|diez)\s+dias\s+"
        r"(?:si\s+|todavia\s+)?(?:sirve|funciona|efectiva)",
    ):
        errors.append("wrong_window")

    for match in re.finditer(
        r"\b(protege|previene|evita)\b.{0,40}"
        r"\b(its|ets|vih|sida|infecciones|enfermedades sexuales|"
        r"enfermedades de transmision)\b",
        n,
    ):
        if not _near_negation(n, match):
            errors.append("sti_protection")
            break
    return list(dict.fromkeys(errors))


def detected_concepts(text):
    n = normalize(text)
    found = {
        "prevent": matches(
            n,
            r"\b(previen|prevenir|evit|impid|preven)\w*\b.{0,50}"
            r"\b(embarazo|quedar embarazada)",
            r"\b(no quedar embarazada|no embarazarse)",
            r"\b(embarazo|embarazada)\b.{0,40}"
            r"\b(previen|evit|impid)\w*",
        ),
        "no_abortion": matches(
            n,
            r"\b(no|nunca|tampoco)\b.{0,35}"
            r"\b(aborto|abortiva|interrumpe|interrumpir embarazo)",
            r"\b(no es abortiva|no provoca aborto|no causa un aborto|"
            r"no termina un embarazo)",
        ),
        "five_days": matches(n, r"\b(5|cinco)\s+dias\b", r"\b120\s+horas\b"),
        "earlier": matches(
            n,
            r"\b(lo antes posible|cuanto antes|mas pronto|"
            r"lo mas rapido|a tiempo|apenas posible)\b",
            r"\b(antes|pronto|rapido)\b.{0,40}"
            r"\b(mejor|eficaz|efectiv)\w*",
        ),
        "not_sti": matches(
            n,
            r"\b(no|nunca|tampoco)\b.{0,32}"
            r"\b(proteg|previen|evit)\w*.{0,36}"
            r"\b(its|ets|vih|infecciones|enfermedades)",
            r"\b(its|ets|vih|infecciones)\b.{0,30}"
            r"\b(no protege|no previene)",
        ),
        "condom": matches(
            n, r"\b(condon|condones|preservativo|preservativos)\b"
        ),
    }
    return found


MISCONCEPTION_FEEDBACK = {
    "abortion": (
        "Cuidado: la anticoncepción de emergencia no provoca abortos "
        "ni interrumpe embarazos establecidos."
    ),
    "wrong_window": (
        "Revisa los plazos: hay opciones de anticoncepción de emergencia "
        "hasta cinco días (120 horas), según el método. Conviene actuar cuanto antes."
    ),
    "sti_protection": (
        "La anticoncepción de emergencia no protege contra infecciones "
        "de transmisión sexual."
    ),
}


def assess(lesson_id, response, phase="pre"):
    lessons = {entry["id"]: entry for entry in get_data()["lessons"]}
    if lesson_id not in lessons:
        raise ValueError("Lección no disponible")
    if phase not in ("pre", "post"):
        raise ValueError("La fase debe ser pre o post")
    answer = response.strip()
    if not 1 <= len(answer) <= 1200:
        raise ValueError("La explicación debe contener entre 1 y 1200 caracteres")

    lesson = lessons[lesson_id]
    identified = detected_concepts(answer)
    errors = [
        code for code in misconception_codes(answer)
        if code in lesson["misconceptions"]
    ]
    covered = [c for c in lesson["concepts"] if identified.get(c["id"], False)]
    missing = [c for c in lesson["concepts"] if not identified.get(c["id"], False)]
    coverage = round(100 * len(covered) / max(1, len(lesson["concepts"])))
    score = min(coverage, 25) if errors else coverage
    status = (
        "misconception" if errors else
        "complete" if not missing else "partial"
    )
    summaries = {
        "complete": "Identificaste los conceptos centrales de esta explicación.",
        "partial": "Hay elementos importantes que aún podemos aclarar.",
        "misconception": "Detecté una posible idea incorrecta que conviene revisar.",
    }
    feedback = [MISCONCEPTION_FEEDBACK[x] for x in errors]
    feedback += [concept["hint"] for concept in missing]
    if not feedback:
        feedback = [
            "Buen trabajo. Para una situación personal, consulta con "
            "un profesional sanitario cuando corresponda."
        ]

    return {
        "lesson_id": lesson_id,
        "phase": phase,
        "status": status,
        "score": score,
        "concept_coverage": coverage,
        "summary": summaries[status],
        "covered": [c["name"] for c in covered],
        "missing": [c["name"] for c in missing],
        "misconceptions": errors,
        "feedback": feedback,
        "rubric_version": "heuristic-es-v0.3",
        "interpretation": (
            "Índice exploratorio basado en reglas lingüísticas. "
            "No es una evaluación clínica validada."
        ),
    }


def catalog():
    data = get_data()
    return {
        "locale": data["locale"],
        "module": data["module"],
        "version": data["version"],
        "review_status": data["review_status"],
        "faqs": [
            {"id": x["id"], "label": x["label"]} for x in data["faqs"]
        ],
        "lessons": [
            {
                "id": x["id"],
                "title": x["title"],
                "intro": x["intro"],
                "question": x["question"],
            }
            for x in data["lessons"]
        ],
        "sources": data["sources"],
    }
