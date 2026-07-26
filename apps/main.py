import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from apps.db import init_db
from apps.logic.items import STYLE_DESCRIPTIONS, STYLE_NAMES, TETRADS
from apps.logic.scoring import STYLES
from apps.logic.validation import ValidationError, validate_answer
from apps.repo import first_unanswered_tetrad, get_answers, get_or_create_results, save_answer
from apps.session import get_current_respondent, get_or_create_respondent


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=os.environ["SESSION_SECRET"])

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

TOTAL_TETRADS = len(TETRADS)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def index(request: Request):
    respondent = get_current_respondent(request)
    if respondent is None:
        return RedirectResponse("/q/0", status_code=303)

    resume_index = first_unanswered_tetrad(respondent["id"], TOTAL_TETRADS)
    if resume_index is None:
        return RedirectResponse("/results", status_code=303)
    return RedirectResponse(f"/q/{resume_index}", status_code=303)


@app.get("/results")
def show_results(request: Request):
    respondent = get_current_respondent(request)
    if respondent is None:
        return RedirectResponse("/q/0", status_code=303)

    resume_index = first_unanswered_tetrad(respondent["id"], TOTAL_TETRADS)
    if resume_index is not None:
        return RedirectResponse(f"/q/{resume_index}", status_code=303)

    results = get_or_create_results(respondent["id"], TOTAL_TETRADS)

    return templates.TemplateResponse(
        request,
        "results.html",
        {
            "diff": {style: results[f"diff_{style.lower()}"] for style in STYLES},
            "top_styles": results["top_styles"].split(","),
            "bottom_styles": results["bottom_styles"].split(","),
            "style_names": STYLE_NAMES,
            "style_descriptions": STYLE_DESCRIPTIONS,
        },
    )


@app.get("/q/{tetrad_index}")
def show_tetrad(request: Request, tetrad_index: int):
    if not (0 <= tetrad_index < TOTAL_TETRADS):
        return templates.TemplateResponse(
            request, "error.html", {"message": "That question doesn't exist."}, status_code=404
        )

    respondent = get_or_create_respondent(request)
    resume_index = first_unanswered_tetrad(respondent["id"], TOTAL_TETRADS)
    if resume_index is None:
        return RedirectResponse("/results", status_code=303)
    if tetrad_index > resume_index:
        return RedirectResponse(f"/q/{resume_index}", status_code=303)

    existing = get_answers(respondent["id"]).get(tetrad_index)

    return templates.TemplateResponse(
        request,
        "tetrad.html",
        {
            "tetrad_index": tetrad_index,
            "total_tetrads": TOTAL_TETRADS,
            "statements": TETRADS[tetrad_index],
            "most_style": existing["most_style"] if existing else None,
            "least_style": existing["least_style"] if existing else None,
            "error": None,
        },
    )


@app.post("/q/{tetrad_index}")
def submit_tetrad(
    request: Request,
    tetrad_index: int,
    most_style: str = Form(...),
    least_style: str = Form(...),
):
    if not (0 <= tetrad_index < TOTAL_TETRADS):
        return templates.TemplateResponse(
            request, "error.html", {"message": "That question doesn't exist."}, status_code=404
        )

    respondent = get_current_respondent(request)
    if respondent is None:
        return RedirectResponse(f"/q/{tetrad_index}", status_code=303)

    # Match GET /q/<index>: never let a submission jump ahead of the
    # respondent's true resume point (e.g. POST /q/23 right after /q/0).
    resume_index = first_unanswered_tetrad(respondent["id"], TOTAL_TETRADS)
    if resume_index is not None and tetrad_index > resume_index:
        return RedirectResponse(f"/q/{resume_index}", status_code=303)

    try:
        validate_answer(tetrad_index, TOTAL_TETRADS, most_style, least_style)
    except ValidationError as exc:
        return templates.TemplateResponse(
            request,
            "tetrad.html",
            {
                "tetrad_index": tetrad_index,
                "total_tetrads": TOTAL_TETRADS,
                "statements": TETRADS[tetrad_index],
                "most_style": most_style,
                "least_style": least_style,
                "error": str(exc),
            },
            status_code=400,
        )

    save_answer(respondent["id"], tetrad_index, most_style, least_style)

    next_index = first_unanswered_tetrad(respondent["id"], TOTAL_TETRADS)
    if next_index is None:
        return RedirectResponse("/results", status_code=303)
    return RedirectResponse(f"/q/{next_index}", status_code=303)
