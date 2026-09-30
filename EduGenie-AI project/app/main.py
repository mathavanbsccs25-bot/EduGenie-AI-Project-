from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from app.config import settings

from app.schemas.models import (
    AskRequest,
    ExplainRequest,
    LearnRequest,
    QuizResponse,
    TextRequest,
    TextResponse,
    HealthResponse,
)

from app.services.gemini_service import gemini_service
from app.services.local_explanation import local_explain


BASE_DIR = Path(__file__).resolve().parent.parent


app = FastAPI(
    title="EduGenie API",
    version="1.0.0",
    description="AI-powered educational assistant",
)


origins = [
    x.strip()
    for x in settings.cors_origins.split(",")
    if x.strip()
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=(
        origins
        if origins != ["*"]
        else ["*"]
    ),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount(
    "/static",
    StaticFiles(
        directory=BASE_DIR / "static"
    ),
    name="static",
)


templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)


# -----------------------------
# DEMO RESPONSES
# -----------------------------

def demo_answer(question: str) -> str:

    return (
        "Demo response:\n\n"
        f"EduGenie received your question:\n"
        f"\"{question}\"\n\n"
        "For real Gemini-generated answers, "
        "add your Gemini API key and set "
        "DEMO_MODE=false."
    )


def demo_explanation(
    topic: str,
    level: str,
) -> str:

    return (
        f"{topic} is being explained for a "
        f"{level} learner.\n\n"
        "This is a demo explanation.\n"
        "Enable Gemini or the optional local "
        "LaMini model for generated explanations."
    )


def demo_summary(text: str) -> str:

    words = text.split()

    short = " ".join(words[:45])

    suffix = (
        "..."
        if len(words) > 45
        else ""
    )

    return (
        "Demo summary:\n\n"
        f"{short}{suffix}"
    )


def demo_learning(
    topic: str,
    level: str,
    goal: str,
) -> str:

    return (
        f"Learning Path: {topic}\n\n"
        f"Level: {level}\n"
        f"Goal: {goal}\n\n"
        "1. Basics\n"
        f"   Learn the core ideas of {topic}.\n\n"
        "2. Practice\n"
        "   Solve beginner exercises.\n\n"
        "3. Intermediate\n"
        "   Build a small project.\n\n"
        "4. Advanced\n"
        "   Study real-world applications."
    )


def demo_quiz(text: str) -> QuizResponse:

    return QuizResponse(
        questions=[

            {
                "question":
                    "What is the main purpose "
                    "of the passage?",

                "options": [
                    "Explain a topic",
                    "Sell a product",
                    "Tell a joke",
                    "Give directions",
                ],

                "answer":
                    "Explain a topic",

                "explanation":
                    "The demo quiz assumes "
                    "the passage is educational.",
            },

            {
                "question":
                    "Which approach is useful "
                    "for learning?",

                "options": [
                    "Practice",
                    "Ignore the material",
                    "Avoid examples",
                    "Skip revision",
                ],

                "answer":
                    "Practice",

                "explanation":
                    "Practice helps reinforce concepts.",
            },

            {
                "question":
                    "What can a summary help with?",

                "options": [
                    "Quick revision",
                    "Deleting knowledge",
                    "Changing the topic",
                    "Removing all context",
                ],

                "answer":
                    "Quick revision",

                "explanation":
                    "A concise summary supports revision.",
            },
        ]
    )


# -----------------------------
# FRONTEND
# -----------------------------

@app.get(
    "/",
    response_class=HTMLResponse,
)
async def home(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
    )


# -----------------------------
# HEALTH
# -----------------------------

@app.get(
    "/api/health",
    response_model=HealthResponse,
)
async def health():

    return HealthResponse(
        status="ok",
        demo_mode=settings.demo_mode,
        model=settings.gemini_model,
        local_explanation=(
            settings.use_local_explanation
        ),
    )


# -----------------------------
# ASK
# -----------------------------

@app.post(
    "/api/ask",
    response_model=TextResponse,
)
async def ask(
    payload: AskRequest,
):

    try:

        if settings.demo_mode:

            result = demo_answer(
                payload.question
            )

        else:

            result = gemini_service.ask(
                payload.question
            )

        return TextResponse(
            result=result
        )

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )


# -----------------------------
# EXPLAIN
# -----------------------------

@app.post(
    "/api/explain",
    response_model=TextResponse,
)
async def explain(
    payload: ExplainRequest,
):

    try:

        local_result = local_explain(
            payload.topic,
            payload.level,
        )

        if local_result:

            return TextResponse(
                result=local_result
            )

        if settings.demo_mode:

            result = demo_explanation(
                payload.topic,
                payload.level,
            )

        else:

            result = gemini_service.explain(
                payload.topic,
                payload.level,
            )

        return TextResponse(
            result=result
        )

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )


# -----------------------------
# SUMMARIZE
# -----------------------------

@app.post(
    "/api/summarize",
    response_model=TextResponse,
)
async def summarize(
    payload: TextRequest,
):

    try:

        if settings.demo_mode:

            result = demo_summary(
                payload.text
            )

        else:

            result = gemini_service.summarize(
                payload.text
            )

        return TextResponse(
            result=result
        )

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )


# -----------------------------
# QUIZ
# -----------------------------

@app.post(
    "/api/quiz",
    response_model=QuizResponse,
)
async def quiz(
    payload: TextRequest,
):

    try:

        if settings.demo_mode:

            result = demo_quiz(
                payload.text
            )

        else:

            result = gemini_service.quiz(
                payload.text
            )

        return result

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )


# -----------------------------
# LEARNING PATH
# -----------------------------

@app.post(
    "/api/learn/recommendations",
    response_model=TextResponse,
)
async def learning_path(
    payload: LearnRequest,
):

    try:

        if settings.demo_mode:

            result = demo_learning(
                payload.topic,
                payload.level,
                payload.goal,
            )

        else:

            result = gemini_service.learning_path(
                payload.topic,
                payload.level,
                payload.goal,
            )

        return TextResponse(
            result=result
        )

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )