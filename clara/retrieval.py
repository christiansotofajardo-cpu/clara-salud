
"""CLARA Salud v0.5 - Bilingual knowledge retrieval engine.

Independent open-source educational prototype.
No proprietary models or generative AI.
Clinical review pending. No personal diagnosis.
"""

from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

VERSION = "0.5.0"
DATA_DIR = Path(__file__).resolve().parent / "data"

ALLOWED_HOSTS = {
    "www.who.int",
    "www.cdc.gov",
    "www.minsal.cl",
}

STOP = {
    "es": set(
        "a al algo ante antes asi como con cual cuales "
        "cuando de del desde donde el ella ellas ellos "
        "en entre es esta este esto hay la las le les "
        "lo los mas me mi mis muy o para pero por "
        "porque que quien se ser si sin sobre son su "
        "sus te tengo tu un una uno unas unos y ya".split()
    ),
    "en": set(
        "a about after all an and are as at be can "
        "could did do does for from had has have how "
        "i in is it its me my of on or our should so "
        "than that the their them there these this "
        "those to was were what when where which who "
        "why will with would you your".split()
    ),
}

EQUIV = {
    "es": {
        "anticonceptivo": "anticoncepcion",
        "anticonceptiva": "anticoncepcion",
        "anticonceptivos": "anticoncepcion",
        "anticonceptivas": "anticoncepcion",
        "hormonas": "hormona",
        "hormonales": "hormona",
        "hormonal": "hormona",
        "pastillas": "pastilla",
        "pildora": "pastilla",
        "pildoras": "pastilla",
        "condon": "preservativo",
        "condones": "preservativo",
        "preservativos": "preservativo",
        "metodos": "metodo",
        "buenos": "mejor",
        "buenas": "mejor",
        "eficaces": "eficaz",
        "efectivos": "eficaz",
        "efectivas": "eficaz",
        "ets": "its",
        "sida": "vih",
        "cuatro": "4",
        "cinco": "5",
    },
    "en": {
        "contraceptives": "contraception",
        "contraceptive": "contraception",
        "contraception": "contraception",
        "pills": "pill",
        "methods": "method",
        "condoms": "condom",
        "stis": "sti",
        "stds": "sti",
        "std": "sti",
        "best": "effective",
        "better": "effective",
        "good": "effective",
        "hours": "hour",
        "days": "day",
        "implants": "implant",
    },
}


def normalized(text: str) -> str:
    value = unicodedata.normalize(
        "NFKD", text.lower()
    )
    value = "".join(
        char for char in value
        if not unicodedata.combining(char)
    )
    return " ".join(
        re.findall(r"[a-z0-9]+", value)
    )


def words(text: str, lang: str) -> set[str]:
    return {
        EQUIV[lang].get(word, word)
        for word in normalized(text).split()
        if word not in STOP[lang]
        and len(word) > 1
    }


@lru_cache(maxsize=2)
def library(lang: str) -> dict:
    if lang not in {"es", "en"}:
        raise ValueError("Unsupported language")

    file = DATA_DIR / f"knowledge_{lang}.json"
    doc = json.loads(
        file.read_text(encoding="utf-8")
    )

    refs = {
        source["id"]: source
        for source in doc["sources"]
    }

    ids = {
        card["id"]
        for card in doc["cards"]
    }

    if (
        len(ids) != len(doc["cards"])
        or len(refs) != len(doc["sources"])
    ):
        raise ValueError(
            "Duplicate knowledge identifiers"
        )

    for source in refs.values():
        url = urlparse(source["url"])
        if (
            url.scheme != "https"
            or url.hostname not in ALLOWED_HOSTS
        ):
            raise ValueError(
                "Unapproved medical source"
            )

    for card in doc["cards"]:
        if not set(card["source_ids"]) <= refs.keys():
            raise ValueError(
                "Unknown source identifier"
            )
        if not set(card["related"]) <= ids:
            raise ValueError(
                "Unknown related identifier"
            )

    return doc


def _card(lang: str, identifier: str) -> dict:
    return next(
        c for c in library(lang)["cards"]
        if c["id"] == identifier
    )


def _result(
    lang: str,
    card: dict,
    mode: str = "direct"
) -> dict:

    refs = {
        s["id"]: s
        for s in library(lang)["sources"]
    }

    partial = mode == "related"

    if partial:
        prefix = (
            "No tengo una respuesta exacta y revisada "
            "para esa pregunta. Como información "
            "complementaria, no como respuesta específica: "
            if lang == "es"
            else
            "I do not have a reviewed answer to that "
            "exact question. As related background, "
            "not a specific answer: "
        )
        title = (
            "Información relacionada: "
            if lang == "es"
            else "Related information: "
        ) + card["title"]
    else:
        prefix = ""
        title = card["title"]

    return {
        "matched": not partial,
        "warning": card["risk"] == "urgent",
        "topic_id": card["id"],
        "title": title,
        "answer": prefix + card["answer"],
        "next": card["follow_up"],
        "sources": [
            refs[x] for x in card["source_ids"]
        ],
        "evidence_level": mode,
        "knowledge_version": VERSION,
    }


def _unknown(
    lang: str,
    detail: str = ""
) -> dict:

    if lang == "es":
        answer = detail or (
            "Aún no dispongo de una respuesta "
            "suficientemente revisada para esta duda. "
            "Puedo explicar información general sobre "
            "anticoncepción, salud sexual e ITS, pero "
            "no sería seguro adivinar una indicación "
            "clínica. Puedes revisar las preguntas "
            "disponibles o consultar con una matrona "
            "u otro profesional de salud."
        )

        title = (
            "Todavía no tengo una respuesta específica"
        )

        follow = (
            "Prueba con métodos anticonceptivos, "
            "anticoncepción de emergencia o "
            "prevención de ITS."
        )

    else:
        answer = detail or (
            "I do not yet have sufficiently reviewed "
            "information to answer this question. "
            "I can share general information about "
            "contraception, sexual health, and STIs, "
            "but I cannot safely guess a clinical "
            "recommendation. Consider the available "
            "topics or ask a qualified healthcare "
            "professional."
        )

        title = (
            "I do not yet have a specific answer"
        )

        follow = (
            "Try contraception methods, emergency "
            "contraception, or STI prevention."
        )

    return {
        "matched": False,
        "warning": False,
        "topic_id": None,
        "title": title,
        "answer": answer,
        "next": follow,
        "sources": [],
        "evidence_level": "unavailable",
        "knowledge_version": VERSION,
    }


def _start_of_protection(
    lang: str,
    emergency: bool
) -> dict:
    """Bounded guidance pending clinical review."""

    if emergency:
        card = _card(lang, "ec_plazo")
        result = _result(lang, card)

        result["title"] = (
            "¿Cuándo puede utilizarse la "
            "anticoncepción de emergencia?"
            if lang == "es"
            else
            "When can emergency contraception be used?"
        )

        introduction = (
            "La anticoncepción de emergencia se "
            "utiliza después de una relación sin "
            "protección; no ofrece protección continua "
            "frente a relaciones posteriores. "
            if lang == "es"
            else
            "Emergency contraception is used after "
            "unprotected sex; it does not provide "
            "ongoing protection for later sexual "
            "encounters. "
        )

        result["answer"] = (
            introduction + card["answer"]
        )

        return result

    if lang == "es":
        title = (
            "¿Cuándo empiezan a proteger "
            "los anticonceptivos?"
        )

        answer = (
            "Depende del método y del momento en que "
            "se inicia. No todos ofrecen protección "
            "inmediata. Como orientación general, "
            "para varios métodos hormonales puede "
            "ser necesario usar preservativo u otro "
            "respaldo durante los primeros siete días, "
            "según el método y el día del ciclo. "
            "El DIU de cobre no requiere ese respaldo "
            "después de su colocación correcta. "
            "Estos plazos no son idénticos para todas "
            "las píldoras y situaciones; para saber "
            "cuándo estarás protegida hay que "
            "identificar el método y consultar "
            "sus indicaciones específicas."
        )

        follow = (
            "¿Utilizas píldora, implante, inyección "
            "o DIU? Una matrona puede confirmar "
            "el plazo preciso."
        )

        source_name = (
            "CDC · Cuándo iniciar métodos "
            "anticonceptivos (guía 2024)"
        )

    else:
        title = (
            "When do contraceptives start "
            "protecting against pregnancy?"
        )

        answer = (
            "It depends on the method and when it "
            "is started. Protection is not always "
            "immediate. For several hormonal methods, "
            "condoms or another backup method may be "
            "needed for the first seven days, "
            "depending on the method and the day "
            "of the menstrual cycle. A correctly "
            "inserted copper IUD does not require "
            "backup contraception. Rules differ "
            "across pill formulations and individual "
            "circumstances, so check the specific "
            "method instructions with a healthcare "
            "professional."
        )

        follow = (
            "Which method are you asking about: "
            "pill, implant, injection, or IUD?"
        )

        source_name = (
            "CDC · When to start contraceptive "
            "methods (2024 guidance)"
        )

    return {
        "matched": True,
        "warning": False,
        "topic_id": "start_of_protection",
        "title": title,
        "answer": answer,
        "next": follow,
        "sources": [
            {
                "id": "cdc_start",
                "name": source_name,
                "url": (
                    "https://www.cdc.gov/mmwr/volumes/"
                    "73/rr/rr7303a1_appendix.htm"
                ),
            }
        ],
        "evidence_level": "direct",
        "knowledge_version": VERSION,
    }


def _score(
    question: str,
    card: dict,
    lang: str,
    emergency: bool,
    sti: bool
) -> float:

    q = normalized(question)
    qt = words(question, lang)
    highest = 0.0

    for phrase in [
        card["title"],
        *card["aliases"]
    ]:
        pt = words(phrase, lang)

        if not pt:
            continue

        common = len(pt & qt)

        if not common:
            continue

        score = (
            2.0 * common / len(qt or {"x"})
            + 2.2 * common / len(pt)
        )

        p = normalized(phrase)

        if (
            len(p) >= 5
            and re.search(
                r"(?<!\w)"
                + re.escape(p)
                + r"(?!\w)",
                q,
            )
        ):
            score += 3.3

        highest = max(highest, score)

    emergency_topic = card["id"].startswith(
        "ec_"
    )

    if emergency and emergency_topic:
        highest += 0.9

    if (
        emergency
        and card["id"].startswith("regular_")
    ):
        highest -= 1.5

    if not emergency and emergency_topic:
        highest -= 0.6

    if sti and card["id"].startswith("its_"):
        highest += 0.7

    return highest


def search(
    question: str,
    lang: str = "es"
) -> dict:
    """Retrieve bounded educational information."""

    if lang not in {"es", "en"}:
        raise ValueError("Use 'es' or 'en'")

    if not 1 <= len(question.strip()) <= 900:
        raise ValueError(
            "Question must contain 1 to 900 characters"
        )

    q = normalized(question)

    emergency = bool(
        re.search(
            r"\b(emergencia|urgencia|postcoital|"
            r"dia despues|dia siguiente|emergency|"
            r"morning after|postcoital)\b",
            q,
        )
    )

    sti = bool(
        re.search(
            r"\b(its|ets|vih|sida|vph|sti|"
            r"std|hiv|aids|hpv)\b",
            q,
        )
    )

    # Safety checks always precede retrieval.
    if re.search(
        r"\b(violacion|violaron|agresion sexual|"
        r"abuso sexual|me obligaron|sin consentimiento|"
        r"me agredieron|agredieron sexualmente|"
        r"abusaron de mi|sexual assault|rape|raped|"
        r"sexual abuse|forced sex|without consent)\b",
        q,
    ):
        return _result(
            lang,
            _card(lang, "seg_violencia"),
        )

    if re.search(
        r"\b(desmayo|hemorragia|"
        r"sangrado (muy )?abundante|"
        r"dolor (abdominal |de vientre )?"
        r"(muy )?intenso|fainting|heavy bleeding|"
        r"severe abdominal pain|hemorrhage)\b",
        q,
    ):
        return _result(
            lang,
            _card(lang, "seg_sintomas"),
        )

    if re.search(
        r"\b(posible exposicion al vih|"
        r"exposicion al vih|profilaxis postexposicion|"
        r"profilaxis posexposicion|"
        r"possible hiv exposure|exposed to hiv|"
        r"hiv exposure|pep)\b",
        q,
    ):
        return _result(
            lang,
            _card(lang, "its_pep"),
        )

    # Personal contraindications need a clinician.
    if re.search(
        r"\b(trombosis|coagulos|anticoagulantes|"
        r"cancer de mama|contraindicaciones|"
        r"dosis exacta|infeccion urinaria|cistitis|"
        r"antibioticos|thrombosis|blood clots|"
        r"blood thinners|breast cancer|"
        r"contraindications|urinary tract infection|"
        r"antibiotics)\b",
        q,
    ):
        return _unknown(lang)

    # Detect questions about start of protection.
    onset = bool(
        re.search(
            r"\b(cuanto (tiempo|tarda|demora)|"
            r"cuando|desde cuando|a partir de cuando|"
            r"how long|when|how soon)\b",
            q,
        )
        and re.search(
            r"\b(hacen? efecto|"
            r"empiezan? a (hacer efecto|proteger|funcionar)|"
            r"comienzan? a (proteger|funcionar)|"
            r"surten? efecto|start working|"
            r"starts working|take effect|"
            r"become effective|start protecting|"
            r"protection begins|kick in|effective after)\b",
            q,
        )
    )

    if onset and re.search(
        r"\b(anticoncepcion|anticonceptiv\w*|"
        r"pastilla|pildora|diu|implante|"
        r"birth control|contraception|"
        r"contraceptiv\w*|pill|iud|implant)\b",
        q,
    ):
        return _start_of_protection(
            lang, emergency
        )

    # Recognize requests for hormone-free methods.
    if re.search(
        r"\b(sin hormonas?|no usa hormonas?|"
        r"no contiene hormonas?|libre de hormonas?|"
        r"no hormonal|without hormones?|"
        r"no hormones?|hormone free|non hormonal)\b",
        q,
    ):
        return _result(
            lang,
            _card(lang, "regular_sin_hormonas"),
        )

    # Specific health intents override generic routing.
    if emergency and re.search(
        r"\b(aborto|abortiva|abortivo|"
        r"abortion|abortifacient)\b",
        q,
    ):
        return _result(
            lang,
            _card(lang, "ec_no_aborto"),
        )

    if emergency and sti:
        return _result(
            lang,
            _card(lang, "its_general"),
        )

    # Method comparison for emergency contraception.
    if emergency and re.search(
        r"\b(metodo\w*|opciones|mejor\w*|"
        r"buen\w*|cual\w*|tipos|comparar|"
        r"method\w*|options|best|better|"
        r"good|which|compare)\b",
        q,
    ):
        if not re.search(
            r"\b(aborto|abortion|vomito|"
            r"vomiting|efectos|side effects)\b",
            q,
        ):
            return _result(
                lang,
                _card(lang, "ec_metodos"),
            )

    # General contraceptive method comparison.
    if not emergency and re.search(
        r"\b(mejor\w*|buen\w*|eficaz|"
        r"efectivo\w*|best|good|most effective)\b",
        q,
    ) and re.search(
        r"\b(anticonceptiv\w*|anticoncepcion|"
        r"birth control|contraception|"
        r"contraceptiv\w*)\b",
        q,
    ):
        return _result(
            lang,
            _card(lang, "regular_comparar"),
        )

    # Search the complete knowledge library.
    ranking = sorted(
        (
            (
                _score(
                    q,
                    card,
                    lang,
                    emergency,
                    sti,
                ),
                card,
            )
            for card in library(lang)["cards"]
        ),
        key=lambda pair: pair[0],
        reverse=True,
    )

    score, best = ranking[0]

    if score < 2.3:
        return _unknown(lang)

    if score < 3.45:
        if best["risk"] == "urgent":
            return _unknown(lang)

        return _result(
            lang,
            best,
            mode="related",
        )

    return _result(lang, best)
