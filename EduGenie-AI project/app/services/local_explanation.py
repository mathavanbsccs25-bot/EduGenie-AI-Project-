from app.config import settings


_pipeline = None
_load_attempted = False


def local_explain(
    topic: str,
    level: str,
) -> str | None:

    global _pipeline
    global _load_attempted

    if not settings.use_local_explanation:
        return None

    if not _load_attempted:

        _load_attempted = True

        try:

            from transformers import pipeline

            _pipeline = pipeline(
                "text2text-generation",
                model="MBZUAI/LaMini-Flan-T5-783M",
            )

        except Exception:

            _pipeline = None

    if _pipeline is None:
        return None

    prompt = (
        f"Explain {topic} for a {level} "
        "student simply with a definition "
        "and example."
    )

    try:

        result = _pipeline(
            prompt,
            max_new_tokens=220,
            do_sample=False,
        )

        return result[0][
            "generated_text"
        ].strip()

    except Exception:

        return None