from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():

    response = client.get(
        "/api/health"
    )

    assert response.status_code == 200

    assert (
        response.json()["status"]
        == "ok"
    )


def test_ask():

    response = client.post(
        "/api/ask",
        json={
            "question":
                "What is Python?"
        },
    )

    assert response.status_code == 200

    assert "result" in response.json()


def test_explain():

    response = client.post(
        "/api/explain",
        json={
            "topic":
                "Photosynthesis",

            "level":
                "beginner",
        },
    )

    assert response.status_code == 200


def test_summary():

    response = client.post(
        "/api/summarize",
        json={
            "text":
                "Photosynthesis is the process "
                "by which plants convert light "
                "energy into chemical energy."
        },
    )

    assert response.status_code == 200


def test_quiz():

    response = client.post(
        "/api/quiz",
        json={
            "text":
                "Python is a programming language "
                "used for web development, "
                "data science and automation."
        },
    )

    assert response.status_code == 200

    questions = response.json()[
        "questions"
    ]

    assert len(questions) == 3

    assert all(
        len(question["options"]) == 4
        for question in questions
    )


def test_learning_path():

    response = client.post(
        "/api/learn/recommendations",
        json={
            "topic": "Python",
            "level": "beginner",
            "goal":
                "learn programming",
        },
    )

    assert response.status_code == 200