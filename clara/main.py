
"""CLARA Salud — Bilingual API.
Open-source health communication and comprehension prototype.
IDE SpA | Version 0.2.0
"""

from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .engine import (
    catalog as catalog_es,
    answer_question as answer_es,
    assess as assess_es,
)

from .engine_en import (
    catalog_en,
    answer_question_en,
    assess_en,
)


VERSION = "0.2.0"

app = FastAPI(
    title="CLARA Salud",
    description=(
        "Open-source bilingual health communication "
        "and comprehension platform."
    ),
    version=VERSION,
    docs_url="/api/docs",
    redoc_url=None,
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

# Static resources will be added in the next steps.
if STATIC_DIR.is_dir():
    app.mount(
        "/static",
        StaticFiles(directory=str(STATIC_DIR)),
        name="static",
    )


Language = Literal["es", "en"]


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
        "message": (
            "Bilingual interface under construction."
        ),
        "languages": ["es", "en"],
    })


@app.get("/api/status")
def status():
    return {
        "status": "ok",
        "app": "CLARA Salud",
        "version": VERSION,
        "languages": ["es", "en"],
        "clinical_review": "pending",
        "persistence": "none",
        "mode": "educational_prototype",
    }


@app.get("/api/catalog")
def get_catalog(lang: Language = "es"):
    if lang == "en":
        result = catalog_en()
    else:
        result = catalog_es()

    return {
        **result,
        "lang": lang,
    }


@app.post("/api/ask")
def ask(payload: QuestionPayload):
    try:
        if payload.lang == "en":
            result = answer_question_en(
                payload.question
            )
        else:
            result = answer_es(
                payload.question
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
