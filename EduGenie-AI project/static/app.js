async function api(path, body) {

    const response = await fetch(
        path,
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body: JSON.stringify(body)
        }
    );

    const data =
        await response.json();

    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Request failed"
        );
    }

    return data;
}


function show(id, text) {

    document.getElementById(id)
        .textContent = text;
}


/* -------------------------
   ASK
------------------------- */

async function askQuestion() {

    try {

        show(
            "askResult",
            "Thinking..."
        );

        const data =
            await api(
                "/api/ask",
                {
                    question:
                        document.getElementById(
                            "askInput"
                        ).value
                }
            );

        show(
            "askResult",
            data.result
        );

    } catch (error) {

        show(
            "askResult",
            error.message
        );
    }
}


/* -------------------------
   EXPLAIN
------------------------- */

async function explainTopic() {

    try {

        show(
            "explainResult",
            "Generating explanation..."
        );

        const data =
            await api(
                "/api/explain",
                {
                    topic:
                        document.getElementById(
                            "topicInput"
                        ).value,

                    level:
                        document.getElementById(
                            "levelInput"
                        ).value
                }
            );

        show(
            "explainResult",
            data.result
        );

    } catch (error) {

        show(
            "explainResult",
            error.message
        );
    }
}


/* -------------------------
   SUMMARY
------------------------- */

async function summarizeText() {

    try {

        show(
            "summaryResult",
            "Summarizing..."
        );

        const data =
            await api(
                "/api/summarize",
                {
                    text:
                        document.getElementById(
                            "summaryInput"
                        ).value
                }
            );

        show(
            "summaryResult",
            data.result
        );

    } catch (error) {

        show(
            "summaryResult",
            error.message
        );
    }
}


/* -------------------------
   QUIZ
------------------------- */

async function generateQuiz() {

    const box =
        document.getElementById(
            "quizResult"
        );

    box.textContent =
        "Generating quiz...";

    try {

        const data =
            await api(
                "/api/quiz",
                {
                    text:
                        document.getElementById(
                            "quizInput"
                        ).value
                }
            );


        box.innerHTML =
            data.questions
                .map(
                    (question, index) => {

                        return `
                        <div class="quiz-question">

                            <strong>
                                ${index + 1}.
                                ${escapeHtml(
                                    question.question
                                )}
                            </strong>

                            ${question.options
                                .map(
                                    option => `
                                    <div class="option">
                                        ${escapeHtml(
                                            option
                                        )}
                                    </div>
                                    `
                                )
                                .join("")
                            }

                            <small>

                                <b>
                                    Answer:
                                </b>

                                ${escapeHtml(
                                    question.answer
                                )}

                                <br>

                                ${escapeHtml(
                                    question.explanation
                                )}

                            </small>

                        </div>
                        `;
                    }
                )
                .join("");

    } catch (error) {

        box.textContent =
            error.message;
    }
}


/* -------------------------
   LEARNING PATH
------------------------- */

async function learningPath() {

    try {

        show(
            "learnResult",
            "Building learning path..."
        );

        const data =
            await api(
                "/api/learn/recommendations",
                {
                    topic:
                        document.getElementById(
                            "learnTopic"
                        ).value,

                    level:
                        document.getElementById(
                            "learnLevel"
                        ).value,

                    goal:
                        document.getElementById(
                            "learnGoal"
                        ).value
                }
            );

        show(
            "learnResult",
            data.result
        );

    } catch (error) {

        show(
            "learnResult",
            error.message
        );
    }
}


/* -------------------------
   SECURITY HELPER
------------------------- */

function escapeHtml(value) {

    return String(value).replace(
        /[&<>'"]/g,

        character => ({

            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            "'": "&#39;",
            '"': "&quot;"

        }[character])
    );
}


/* -------------------------
   HEALTH CHECK
------------------------- */

async function checkHealth() {

    try {

        const response =
            await fetch(
                "/api/health"
            );

        const data =
            await response.json();

        const status =
            document.getElementById(
                "status"
            );


        if (data.demo_mode) {

            status.textContent =
                `Backend online • Demo mode • ${data.model}`;

        } else {

            status.textContent =
                `Backend online • Gemini ${data.model}`;

        }

    } catch (error) {

        document.getElementById(
            "status"
        ).textContent =
            "Backend unavailable";
    }
}


checkHealth();