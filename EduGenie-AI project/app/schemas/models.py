from typing import List

from pydantic import BaseModel, Field


class TextRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=30000,
    )


class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=10000,
    )


class ExplainRequest(BaseModel):
    topic: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

    level: str = Field(
        default="beginner",
        max_length=50,
    )


class LearnRequest(BaseModel):
    topic: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

    level: str = Field(
        default="beginner",
        max_length=50,
    )

    goal: str = Field(
        default="understand the topic",
        max_length=2000,
    )


class QuizQuestion(BaseModel):
    question: str
    options: List[str] = Field(
        min_length=4,
        max_length=4,
    )
    answer: str
    explanation: str


class QuizResponse(BaseModel):
    questions: List[QuizQuestion] = Field(
        min_length=3,
        max_length=3,
    )


class TextResponse(BaseModel):
    result: str


class HealthResponse(BaseModel):
    status: str
    demo_mode: bool
    model: str
    local_explanation: bool