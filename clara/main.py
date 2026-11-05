
"""CLARA Salud — Bilingual API v0.5.0

Open-source health communication and comprehension prototype.
IDE SpA.

Features:
- Spanish and English health information.
- Structured knowledge retrieval.
- Direct, related, and unavailable responses.
- Original teach-back assessment engines.
- No proprietary EVALIA or MetaSistema dependencies.

Educational prototype. Clinical review pending.
"""

from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Original comprehension assessment engines
from .engine import (
    catalog as catalog_es,
    assess as assess_es,
)

from .engine_en import (
    catalog_en,
    assess_en,
)

# New bilingual knowledge retrieval engine
from .retrieval import (
    search,
    library,
    VERSION as KNOWLEDGE_VERSION,
)


VERSION = "0.5.0"

Language = Literal["es", "en"]


# =========================================
# APPLICATION
# =========================================

app = FastAPI(
    title="CLARA Salud",
    description=(
        "Open-source bilingual health information, "
        "comprehension assessment and feedback platform."
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


# =========================================
# REQUEST MODELS
# =========================================

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


# =========================================
# SECURITY AND PRIVACY HEADERS
# =========================================

@app.middleware("http")
async def privacy_headers(request, call_next):

    response = await call_next(request)

    response.headers["Cache-Control"] = "no-store"

    response.headers["X-Content-Type-Options"] = (
        "nosniff"
    )

    response.headers["Referrer-Policy"] = (
        "no-referrer"
    )

    response.headers["X-Frame-Options"] = (
        "DENY"
    )

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


# =========================================
# HOME PAGE
# =========================================

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


# =========================================
# SYSTEM STATUS
# =========================================

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
    }


# =========================================
# EDUCATIONAL CATALOG
# =========================================

@app.get("/api/catalog")
def get_catalog(lang: Language = "es"):

    try:
        if lang == "en":
            result = catalog_en()
        else:
            result = catalog_es()

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


# =========================================
# HEALTH INFORMATION QUERY
# =========================================

@app.post("/api/ask")
def ask(payload: QuestionPayload):

    try:
        result = search(
            question=payload.question,
            lang=payload.lang,
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


# =========================================
# TEACH-BACK ASSESSMENT
# =========================================

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

        return {
            **result,
            "lang": payload.lang,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
