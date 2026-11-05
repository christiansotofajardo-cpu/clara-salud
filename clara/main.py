
"""CLARA Salud API: independent, privacy-conscious educational prototype."""

from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .engine import catalog, answer_question, assess


VERSION = "0.1.0"

app = FastAPI(
    title="CLARA Salud",
    version=VERSION,
    docs_url=None,
    redoc_url=None,
)

STATIC = Path(__file__).parent / "static"

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC)),
    name="static",
)


class QuestionPayload(BaseModel):
    question: str = Field(min_length=1, max_length=900)


class AssessmentPayload(BaseModel):
    lesson_id: str = Field(min_length=1, max_length=30)
    response: str = Field(min_length=1, max_length=1200)
    phase: Literal["pre", "post"] = "pre"


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
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/status")
def status():
    return {
        "status": "ok",
        "app": "CLARA Salud",
        "version": VERSION,
        "clinical_review": "pending",
        "persistence": "none",
        "mode": "educational_prototype",
    }


@app.get("/api/catalog")
def get_catalog():
    return catalog()


@app.post("/api/ask")
def ask(payload: QuestionPayload):
    try:
        return answer_question(payload.question)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@app.post("/api/assess")
def evaluate(payload: AssessmentPayload):
    try:
        return assess(
            payload.lesson_id,
            payload.response,
            payload.phase,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
