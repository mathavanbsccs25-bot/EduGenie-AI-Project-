from typing import Any, Type
import time

from pydantic import BaseModel

from app.config import settings
from app.schemas.models import QuizResponse


class GeminiService:

    def __init__(self):
        self.client = None

        if settings.gemini_api_key:
            from google import genai

            self.client = genai.Client(
    api_key=settings.gemini_api_key,
    enterprise=False,
)

    @property
    def available(self) -> bool:
        return (
            self.client is not None
            and not settings.demo_mode
        )

    def _generate(
        self,
        prompt: str,
        schema: Type[BaseModel] | None = None,
    ) -> Any:

        if not self.available:
            raise RuntimeError(
                "Gemini is not configured. "
                "Set GEMINI_API_KEY and DEMO_MODE=false."
            )

        from google.genai import types

        config = types.GenerateContentConfig(
            temperature=0.4,
            max_output_tokens=1800,
        )

        if schema is not None:
            config.response_mime_type = "application/json"
            config.response_schema = schema

        last_error = None

        for attempt in range(3):

            try:
                response = self.client.models.generate_content(
                    model=settings.gemini_model,
                    contents=prompt,
                    config=config,
                )

                text = response.text

                if not text:
                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                if schema is not None:

                    if getattr(response, "parsed", None) is not None:
                        return response.parsed

                    return schema.model_validate_json(text)

                return text.strip()

            except Exception as exc:

                last_error = exc
                error_text = str(exc).upper()

                temporary_error = (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "HIGH DEMAND" in error_text
                    or "SERVICE UNAVAILABLE" in error_text
                )

                quota_error = (
                    "429" in error_text
                    or "RESOURCE_EXHAUSTED" in error_text
                    or "QUOTA" in error_text
                )

                # Do not retry quota errors.
                if quota_error:
                    raise RuntimeError(
                        "Gemini API quota has been exceeded. "
                        "Please wait for the quota to reset or "
                        "check your Gemini API usage and billing plan."
                    ) from exc

                # Do not retry other permanent errors.
                if not temporary_error:
                    raise

                # Retry temporary Gemini service errors.
                if attempt < 2:
                    time.sleep(2 ** (attempt + 1))

        raise RuntimeError(
            "Gemini is temporarily unavailable after "
            "multiple attempts. Please try again shortly."
        ) from last_error

    def ask(self, question: str) -> str:

        prompt = f"""
You are EduGenie, an educational assistant.

Answer the student's question clearly and accurately.

Rules:
- Use simple language.
- Use short sections.
- Give examples when useful.
- Do not invent uncertain facts.
- Make the answer educational.

Student question:
{question}
"""

        return self._generate(prompt)

    def explain(
        self,
        topic: str,
        level: str,
    ) -> str:

        prompt = f"""
Explain the following topic for a {level} learner.

Topic:
{topic}

Use this structure:

1. Simple definition
2. How it works
3. Example
4. Key points

Keep the explanation beginner-friendly.
Avoid unnecessary technical jargon.
"""

        return self._generate(prompt)

    def summarize(self, text: str) -> str:

        prompt = f"""
Summarize the following educational text.

Requirements:
- Preserve important facts.
- Preserve important concepts.
- Remove unnecessary repetition.
- Make it useful for quick revision.
- Give a short summary followed by bullet points.

Text:
{text}
"""

        return self._generate(prompt)

    def quiz(self, text: str) -> QuizResponse:

        prompt = f"""
Create exactly 3 multiple-choice questions
from the educational passage below.

Requirements:

- Exactly 3 questions.
- Exactly 4 options per question.
- Options must be distinct.
- The answer must exactly match one option.
- Include a short explanation.
- Questions must be based only on the passage.
- Do not introduce unrelated facts.

Passage:
{text}
"""

        return self._generate(
            prompt,
            QuizResponse,
        )

    def learning_path(
        self,
        topic: str,
        level: str,
        goal: str,
    ) -> str:

        prompt = f"""
Create a personalized learning path.

Topic:
{topic}

Learner level:
{level}

Learning goal:
{goal}

Organize the learning path from beginner
to advanced.

Include:

1. Core concepts
2. Practice ideas
3. Intermediate concepts
4. Advanced concepts
5. Project ideas
6. Suggested resource types

Resource types can include:
- Videos
- Articles
- Books
- Documentation

Do not invent specific URLs.
"""

        return self._generate(prompt)


gemini_service = GeminiService()