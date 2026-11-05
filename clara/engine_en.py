
"""CLARA Salud — Independent English comprehension engine.

Rule-based educational prototype.
Not a clinical decision system or validated AI model.
"""

import json
import re
from functools import lru_cache
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "en.json"

ALLOWED_SOURCES = (
    "https://www.who.int/",
    "https://www.cdc.gov/",
    "https://www.minsal.cl/",
)


@lru_cache(maxsize=1)
def load_english():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    for source in data["sources"]:
        if not source["url"].startswith(ALLOWED_SOURCES):
            raise ValueError("Unexpected reference domain")

    return data


def norm(value):
    text = value.lower().replace("’", "'")

    contractions = {
        "doesn't": "does not",
        "don't": "do not",
        "isn't": "is not",
        "can't": "cannot",
        "won't": "will not",
    }

    for original, replacement in contractions.items():
        text = text.replace(original, replacement)

    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def has(text, *patterns):
    return any(re.search(pattern, text) for pattern in patterns)


def faq_by_id(faq_id):
    return next(
        x for x in load_english()["faqs"]
        if x["id"] == faq_id
    )


def format_faq(entry, warning=False):
    refs = {
        x["id"]: x
        for x in load_english()["sources"]
    }

    return {
        "matched": True,
        "warning": warning,
        "topic_id": entry["id"],
        "title": entry["label"],
        "answer": entry["answer"],
        "next": entry["next"],
        "sources": [
            refs[s] for s in entry["source_ids"]
        ],
    }


def answer_question_en(question):
    q = question.strip()

    if not 1 <= len(q) <= 900:
        raise ValueError(
            "Question must contain 1 to 900 characters."
        )

    n = norm(q)

    # Safety-related questions take priority.
    if has(
        n,
        r"\b(rape|raped|sexual assault|sexual abuse|forced sex|sexual violence)\b"
    ):
        return format_faq(
            faq_by_id("violencia"), warning=True
        )

    if has(
        n,
        r"\b(severe abdominal pain|fainting|heavy bleeding|hemorrhage)\b"
    ):
        return format_faq(
            faq_by_id("efectos"), warning=True
        )

    special_routes = [
        ("efectos", r"\b(vomit|vomited|vomiting|nausea)\b"),
        ("aborto", r"\b(abortion|abortifacient|terminate pregnancy|end an existing pregnancy)\b"),
        ("its", r"\b(stis?|stds?|hiv|aids|sexually transmitted)\b"),
        ("fertilidad", r"\b(infertility|fertility|sterility)\b"),
        ("acceso", r"\b(where|access|obtain|buy|pharmacy|cesfam|clinic)\b"),
    ]

    for faq_id, pattern in special_routes:
        if has(n, pattern):
            return format_faq(faq_by_id(faq_id))

    stopwords = {
        "the", "a", "an", "is", "it", "in",
        "to", "of", "do", "i", "how", "what",
        "can", "does", "my", "for", "and",
    }

    words = set(n.split()) - stopwords
    ranked = []

    for item in load_english()["faqs"]:
        score = 0.0

        for expression in [
            item["label"], *item["keywords"]
        ]:
            phrase = norm(expression)

            if not phrase:
                continue

            exact = re.search(
                r"(?<!\w)" + re.escape(phrase) + r"(?!\w)",
                n,
            )

            if exact:
                candidate = (
                    3 + min(len(phrase.split()), 4) / 4
                )
            else:
                exp_words = set(phrase.split())
                candidate = (
                    2 * len(words & exp_words)
                    / max(1, len(exp_words))
                )

            score = max(score, candidate)

        ranked.append((score, item))

    best_score, best = max(
        ranked, key=lambda pair: pair[0]
    )

    if best_score < 1.45:
        return {
            "matched": False,
            "warning": False,
            "topic_id": None,
            "title": "Let's clarify your question",
            "answer": (
                "I do not have enough reviewed information "
                "to answer that safely. Please choose a "
                "listed question or contact a healthcare "
                "professional. Seek urgent care for "
                "an emergency."
            ),
            "next": (
                "Try: How much time do I have? "
                "or Does it cause abortion?"
            ),
            "sources": [],
        }

    return format_faq(best)


def concepts_en(text):
    n = norm(text)

    prevent = has(
        n,
        r"\b(prevents?|avoids?|stops?)\b.{0,28}\bpregnancy\b",
        r"\bpregnancy prevention\b",
    )

    if has(
        n,
        r"\b(does not|cannot|will not)\s+"
        r"(prevent|avoid|stop)\b.{0,28}\bpregnancy\b",
    ):
        prevent = False

    return {
        "prevent": prevent,

        "no_abortion": has(
            n,
            r"\b(not|never|cannot|does not|will not)\b"
            r".{0,35}\b(abortion|abortifacient|end|"
            r"terminate|interrupt)\b",
            r"\bdoes not cause\b.{0,12}\babortion\b",
            r"\bnot an abortion pill\b",
        ),

        "five_days": has(
            n,
            r"\b(five|5) days\b",
            r"\b120 hours\b",
        ),

        "earlier": has(
            n,
            r"\bas soon as possible\b",
            r"\bthe sooner the better\b",
            r"\b(act|take|use)\b.{0,22}"
            r"\b(early|quickly|promptly|soon)\b",
        ),

        "not_sti": has(
            n,
            r"\b(does not|cannot|will not|never)\b"
            r".{0,30}\b(protect|prevent)\b"
            r".{0,35}\b(stis?|stds?|hiv|infections?)\b",
            r"\bno protection\b.{0,25}"
            r"\b(stis?|stds?|hiv|infections?)\b",
        ),

        "condom": has(
            n,
            r"\b(condom|condoms|preservative|preservatives)\b",
        ),
    }


def misconception_codes_en(text):
    n = norm(text)
    result = []

    abortion_claim = has(
        n,
        r"\b(causes|cause|produces|is)\s+"
        r"(an?\s+)?abortion\b",
        r"\b(ends|terminates|interrupts)\s+"
        r"(an?\s+)?(existing|established)?"
        r"\s*pregnancy\b",
        r"\bis an? abortion pill\b",
    )

    abortion_negated = has(
        n,
        r"\b(does not|cannot|will not|never|not)\b"
        r".{0,22}\b(cause|causes|is|end|ends|"
        r"terminate|terminates)\b"
        r".{0,20}\babortion\b",
        r"\bnot an? abortion pill\b",
    )

    if abortion_claim and not abortion_negated:
        result.append("abortion")

    if has(
        n,
        r"\b(only|just)\b.{0,20}\b(24|72) hours\b",
        r"\b(only|just)\b.{0,20}"
        r"\b(one|three|1|3) days\b",
        r"\b(no longer works|does not work)\b"
        r".{0,24}\b(after three days|after 72 hours)\b",
    ):
        result.append("wrong_window")

    sti_claim = has(
        n,
        r"\b(protects|prevents)\b.{0,35}"
        r"\b(stis?|stds?|hiv|infections?)\b",
    )

    sti_negated = has(
        n,
        r"\b(does not|cannot|will not|never)\b"
        r".{0,18}\b(protect|protects|"
        r"prevent|prevents)\b",
    )

    if sti_claim and not sti_negated:
        result.append("sti_protection")

    return result


MESSAGES = {
    "abortion": (
        "Emergency contraception does not cause "
        "abortion or interrupt an established pregnancy."
    ),
    "wrong_window": (
        "There are generally options up to five days, "
        "depending on the method. Seek advice as soon "
        "as possible."
    ),
    "sti_protection": (
        "Emergency contraception does not protect "
        "against sexually transmitted infections."
    ),
}


def assess_en(lesson_id, response, phase="pre"):
    lessons = {
        x["id"]: x
        for x in load_english()["lessons"]
    }

    if lesson_id not in lessons:
        raise ValueError("Lesson not found.")

    if phase not in ("pre", "post"):
        raise ValueError("Phase must be pre or post.")

    answer = response.strip()

    if not 1 <= len(answer) <= 1200:
        raise ValueError(
            "Response must contain 1 to 1200 characters."
        )

    lesson = lessons[lesson_id]
    found = concepts_en(answer)

    hits = [
        c for c in lesson["concepts"]
        if found.get(c["id"], False)
    ]

    missing = [
        c for c in lesson["concepts"]
        if not found.get(c["id"], False)
    ]

    errors = [
        x for x in misconception_codes_en(answer)
        if x in lesson["misconceptions"]
    ]

    coverage = round(
        100 * len(hits)
        / max(1, len(lesson["concepts"]))
    )

    score = min(25, coverage) if errors else coverage

    if errors:
        status = "misconception"
    elif not missing:
        status = "complete"
    else:
        status = "partial"

    summaries = {
        "misconception": (
            "A possible misunderstanding needs clarification."
        ),
        "complete": (
            "You included the central ideas in this explanation."
        ),
        "partial": (
            "There are important ideas we can clarify together."
        ),
    }

    feedback = (
        [MESSAGES[x] for x in errors]
        + [c["hint"] for c in missing]
    )

    if not feedback:
        feedback = [
            "Good work. For personal medical advice, "
            "contact a healthcare professional."
        ]

    return {
        "lesson_id": lesson_id,
        "phase": phase,
        "status": status,
        "score": score,
        "concept_coverage": coverage,
        "summary": summaries[status],
        "covered": [c["name"] for c in hits],
        "missing": [c["name"] for c in missing],
        "misconceptions": errors,
        "feedback": feedback,
        "rubric_version": "heuristic-en-v0.1",
        "interpretation": (
            "Exploratory rule-based estimate; "
            "not a clinically validated assessment."
        ),
    }


def catalog_en():
    data = load_english()

    return {
        "locale": data["locale"],
        "module": data["module"],
        "version": data["version"],
        "review_status": data["review_status"],
        "faqs": [
            {
                "id": x["id"],
                "label": x["label"],
            }
            for x in data["faqs"]
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
