
"""CLARA Salud — Bilingual API v0.5.1.

Open-source educational prototype.
No generative clinical advice.
Technical correction following bilingual API testing.
Medical content requires qualified clinical review.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .engine import catalog as catalog_es, assess as assess_es
from .engine_en import catalog_en, assess_en
from .retrieval import (
    search as original_search,
    library,
    VERSION as KNOWLEDGE_VERSION,
)

VERSION = "0.5.1"
Language = Literal["es", "en"]

app = FastAPI(
    title="CLARA Salud",
    description=(
        "Bilingual educational health information "
        "and teach-back prototype."
    ),
    version=VERSION,
    docs_url="/api/docs",
    redoc_url=None,
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

if STATIC_DIR.is_dir():
    app.mount(
        "/static",
        StaticFiles(directory=str(STATIC_DIR)),
        name="static",
    )


class QuestionPayload(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=900,
    )
    lang: Language = "es"


class AssessmentPayload(BaseModel):
    lesson_id: str = Field(
        min_length=1,
        max_length=30,
    )
    response: str = Field(
        min_length=1,
        max_length=1200,
    )
    phase: Literal["pre", "post"] = "pre"
    lang: Language = "es"


@app.middleware("http")
async def privacy_headers(request, call_next):
    response = await call_next(request)

    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self'; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "frame-ancestors 'none'; "
        "form-action 'self'"
    )
    return response


@app.get("/", include_in_schema=False)
def home():
    index = STATIC_DIR / "index.html"

    if index.is_file():
        return FileResponse(index)

    return JSONResponse({
        "application": "CLARA Salud",
        "version": VERSION,
        "status": "API ready",
        "languages": ["es", "en"],
    })


@app.get("/api/status")
def status():
    return {
        "status": "ok",
        "app": "CLARA Salud",
        "version": VERSION,
        "knowledge_engine": KNOWLEDGE_VERSION,
        "languages": ["es", "en"],
        "knowledge_cards": {
            "es": len(library("es")["cards"]),
            "en": len(library("en")["cards"]),
        },
        "clinical_review": "pending",
        "mode": "educational_prototype",
        "application_database": "none",
        "assessment": "heuristic",
        "routing_revision": "2026-11-06",
    }


@app.get("/api/catalog")
def get_catalog(lang: Language = "es"):
    try:
        result = (
            catalog_en()
            if lang == "en"
            else catalog_es()
        )
        return {
            **result,
            "lang": lang,
            "knowledge_engine": KNOWLEDGE_VERSION,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


def _norm(value: str) -> str:
    value = unicodedata.normalize(
        "NFKD",
        value.lower(),
    )
    value = "".join(
        c for c in value
        if not unicodedata.combining(c)
    )
    return " ".join(
        re.findall(r"[a-z0-9]+", value)
    )


def _has(text: str, pattern: str) -> bool:
    return re.search(pattern, text) is not None


def _knowledge_answer(
    lang: str,
    topic_id: str,
) -> dict:
    doc = library(lang)
    cards = {
        c["id"]: c
        for c in doc["cards"]
    }
    sources = {
        s["id"]: s
        for s in doc["sources"]
    }
    card = cards[topic_id]

    return {
        "matched": True,
        "warning": card["risk"] == "urgent",
        "topic_id": topic_id,
        "title": card["title"],
        "answer": card["answer"],
        "next": card["follow_up"],
        "sources": [
            sources[s]
            for s in card["source_ids"]
        ],
        "evidence_level": "direct",
        "knowledge_version": KNOWLEDGE_VERSION,
    }


def _start_protection(
    lang: str,
    emergency: bool = False,
) -> dict:
    if not emergency:
        canonical = (
            "¿Después de cuánto tiempo hacen efecto "
            "los anticonceptivos?"
            if lang == "es"
            else
            "When does birth control start working?"
        )

        result = original_search(canonical, lang)

        if result.get("topic_id") == "start_of_protection":
            return result

        return {
            "matched": False,
            "warning": False,
            "topic_id": None,
            "title": (
                "Inicio de protección"
                if lang == "es"
                else "Start of protection"
            ),
            "answer": (
                "La protección no comienza al mismo "
                "tiempo para todos los métodos. Consulta "
                "las indicaciones específicas del método "
                "con personal sanitario."
                if lang == "es"
                else
                "Protection does not begin at the same "
                "time for all methods. Check your specific "
                "method with a healthcare professional."
            ),
            "next": (
                "¿Qué método utilizas?"
                if lang == "es"
                else "Which method do you use?"
            ),
            "sources": [],
            "evidence_level": "unavailable",
            "knowledge_version": KNOWLEDGE_VERSION,
        }

    base = _knowledge_answer(lang, "ec_plazo")
    base["topic_id"] = "start_of_protection"

    if lang == "es":
        base["title"] = (
            "¿Cuándo actúa la anticoncepción "
            "de emergencia?"
        )
        base["answer"] = (
            "No existe un plazo universal en horas "
            "que permita asegurar que una píldora de "
            "emergencia ya ha 'hecho efecto'. Estos "
            "métodos se utilizan después de una relación "
            "sin protección para reducir la posibilidad "
            "de embarazo; su eficacia depende del método "
            "y de cuándo se utilice. No proporcionan "
            "protección continua para relaciones "
            "posteriores. Lo importante es buscar "
            "orientación y utilizar el método indicado "
            "cuanto antes dentro de la ventana apropiada."
        )
        base["next"] = (
            "¿Quieres conocer los plazos para usar "
            "cada método de emergencia?"
        )
    else:
        base["title"] = (
            "When does emergency contraception "
            "take effect?"
        )
        base["answer"] = (
            "There is no universal number of hours "
            "that guarantees an emergency contraceptive "
            "pill has 'started working'. These methods "
            "are used after unprotected sex to reduce "
            "the chance of pregnancy; effectiveness "
            "depends on the method and when it is used. "
            "They do not provide ongoing protection "
            "for later sexual encounters. Seek timely "
            "guidance about the appropriate method and "
            "its recommended time window."
        )
        base["next"] = (
            "Would you like to compare the "
            "recommended time windows?"
        )

    return base


def _specific_intent(
    question: str,
    lang: str,
    baseline: dict,
) -> dict | None:
    """Apply conservative bilingual intent precedence.

    Keep urgent routing and personalized medical
    contraindication refusals.
    """

    if baseline.get("warning"):
        return None

    q = _norm(question)

    if (
        baseline.get("evidence_level") == "unavailable"
        and _has(
            q,
            r"\b(trombosis|coagulos|anticoagulantes|"
            r"cancer de mama|thrombosis|blood clots|"
            r"blood thinners|breast cancer|"
            r"recetarias|prescribe|"
            r"which pill should i personally take)\b",
        )
    ):
        return None

    ec = _has(
        q,
        r"\b(emergencia|urgencia|dia despues|"
        r"dia siguiente|morning after|"
        r"emergency contraception|ulipristal|"
        r"levonorgestrel)\b",
    )

    contraception = _has(
        q,
        r"\b(anticonceptiv\w*|anticoncepcion|"
        r"birth control|contraceptiv\w*|"
        r"contraception|pastilla|pildora|pill|"
        r"iud|diu|implante|implant)\b",
    )

    # Broken or slipped condom.
    if (
        _has(q, r"\b(condon|preservativo|condom)\b")
        and _has(
            q,
            r"\b(rompio|roto|rompido|fallo|"
            r"salio|broke|broken|slipped|failed)\b",
        )
    ):
        return _knowledge_answer(
            lang,
            "ec_condon_roto",
        )

    # Adolescent contraception.
    if (
        contraception
        and _has(
            q,
            r"\b(adolescent\w*|teenager\w*|"
            r"teen\w*|menor de edad|"
            r"16 anos|17 anos|under 18)\b",
        )
    ):
        return _knowledge_answer(
            lang,
            "regular_adolescentes",
        )

    # STI tests.
    if (
        _has(q, r"\b(its|ets|sti|std|hiv|vih)\b")
        and _has(
            q,
            r"\b(test|tests|prueba\w*|"
            r"examen\w*|testing|screening)\b",
        )
    ):
        return _knowledge_answer(
            lang,
            "its_pruebas",
        )

    # Fertility concerns.
    if (
        contraception
        and _has(
            q,
            r"\b(infertilidad|infertility|"
            r"fertilidad|fertility|esteril|sterile)\b",
        )
    ):
        return _knowledge_answer(
            lang,
            "regular_fertilidad",
        )

    # Copper versus hormonal IUD.
    if (
        _has(q, r"\b(diu|iud|coil)\b")
        and _has(q, r"\b(cobre|copper)\b")
        and _has(
            q,
            r"\b(hormonal|hormone|hormon\w*)\b",
        )
    ):
        return _knowledge_answer(
            lang,
            "regular_diu",
        )

    # Hormonal contraception after ulipristal.
    if (
        _has(q, r"\b(ulipristal)\b")
        and _has(
            q,
            r"\b(retomo|retomar|reiniciar|"
            r"reanudar|continuar|restart|resume|"
            r"start|restarting|resuming|"
            r"vuelvo|volver)\b",
        )
    ):
        return _knowledge_answer(
            lang,
            "ec_continuar",
        )

    # Vomiting after emergency contraception.
    if (
        ec
        and _has(
            q,
            r"\b(vomit\w*|throw up|threw up|"
            r"puked|vomited)\b",
        )
    ):
        return _knowledge_answer(
            lang,
            "ec_vomitos",
        )

    # Side effects.
    if (
        ec
        and _has(
            q,
            r"\b(efectos secundarios|"
            r"efectos adversos|side effects|"
            r"adverse effects)\b",
        )
    ):
        return _knowledge_answer(
            lang,
            "ec_efectos",
        )

    # Residual pregnancy risk.
    if (
        ec
        and _has(
            q,
            r"\b(embarazada|embarazo|"
            r"pregnant|pregnancy)\b",
        )
        and _has(
            q,
            r"\b(puedo|puede|quedar|still|"
            r"can|could|after|despues)\b",
        )
        and not _has(
            q,
            r"\b(prueba|test|period|regla|"
            r"menstruacion|aborto|abortion|"
            r"abortiva|abortifacient)\b",
        )
    ):
        return _knowledge_answer(
            lang,
            "ec_eficacia",
        )

    # Start of protection versus time window.
    onset = _has(
        q,
        r"\b(hace efecto|hacen efecto|"
        r"empieza a funcionar|"
        r"empiezan a funcionar|"
        r"cuando empieza|cuando empiezan|"
        r"start working|starts working|"
        r"take to work|take effect|"
        r"take to become effective|kick in)\b",
    )

    if contraception and onset:
        return _start_protection(
            lang,
            emergency=ec,
        )

    if (
        ec
        and _has(
            q,
            r"\b(cuanto tiempo|cuantos dias|"
            r"hasta cuando|plazo|how long after|"
            r"how many days|time limit|"
            r"how soon after)\b",
        )
    ):
        return _knowledge_answer(
            lang,
            "ec_plazo",
        )

    return None


@app.post("/api/ask")
def ask(payload: QuestionPayload):
    try:
        baseline = original_search(
            payload.question,
            payload.lang,
        )

        specific = _specific_intent(
            payload.question,
            payload.lang,
            baseline,
        )

        result = (
            specific
            if specific is not None
            else baseline
        )

        return {
            **result,
            "lang": payload.lang,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


def _spanish_abortion_misconception(
    text: str,
) -> bool:
    """Detect explicit affirmative misconception."""

    q = _norm(text)

    if "?" in text or "¿" in text:
        return False

    if not _has(
        q,
        r"\b(pastilla|pildora|anticoncepcion|"
        r"anticonceptivo|emergencia)\b",
    ):
        return False

    tokens = q.split()

    verbs = {
        "interrumpe",
        "interrumpen",
        "termina",
        "terminan",
        "provoca",
        "provocan",
        "causa",
        "causan",
        "produce",
        "producen",
    }

    for i, word in enumerate(tokens):
        if word not in verbs:
            continue

        if any(
            w in {"no", "nunca", "jamas", "tampoco", "ni"}
            for w in tokens[max(0, i - 3):i]
        ):
            continue

        if any(
            w in {"embarazo", "aborto"}
            for w in tokens[i + 1:i + 7]
        ):
            return True

    return _has(
        q,
        r"\b(?:sirve|usada|utilizada) "
        r"para abortar\b",
    )


@app.post("/api/assess")
def evaluate(payload: AssessmentPayload):
    try:
        if payload.lang == "en":
            result = assess_en(
                payload.lesson_id,
                payload.response,
                payload.phase,
            )
        else:
            result = assess_es(
                payload.lesson_id,
                payload.response,
                payload.phase,
            )

        if (
            payload.lang == "es"
            and payload.lesson_id == "objetivo"
            and _spanish_abortion_misconception(
                payload.response
            )
        ):
            result = dict(result)

            existing = list(
                result.get("misconceptions") or []
            )

            if "abortion" not in existing:
                existing.append("abortion")

            result["misconceptions"] = existing
            result["status"] = "misconception"
            result["score"] = min(
                result.get("score", 0),
                25,
            )

            result["summary"] = (
                "Hay un posible malentendido "
                "que conviene aclarar."
            )

            feedback = list(
                result.get("feedback") or []
            )

            clarification = (
                "La anticoncepción de emergencia "
                "no interrumpe un embarazo establecido."
            )

            if clarification not in feedback:
                feedback.insert(0, clarification)

            result["feedback"] = feedback

        return {
            **result,
            "lang": payload.lang,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
