document.addEventListener("DOMContentLoaded", () => {

    const quizForm = document.getElementById("quizForm");

    quizForm.addEventListener("submit", async (e) => {

        e.preventDefault();

        const selected = document.querySelector(
            'input[name="answer"]:checked'
        );

        if (!selected) {
            alert("Please select an answer.");
            return;
        }

        const response = await fetch("/submit_answer", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question_id: document.getElementById("question-id").value,
                answer: selected.value
            })
        });

        const result = await response.json();

        // Small delay for better UX
        setTimeout(() => {
            loadNextQuestion();
        }, 300);

    });

});


async function loadNextQuestion() {

    const response = await fetch("/next_question");

    const data = await response.json();

    // -------------------------------------
    // Assessment Finished
    // -------------------------------------
    if (data.completed) {

        window.location.href = data.redirect;

        return;
    }

    // -------------------------------------
    // Skill Changed
    // -------------------------------------
    if (data.new_skill) {

        document.getElementById("skill-name").textContent =
            data.skill_name;

    }

    // -------------------------------------
    // Update Question
    // -------------------------------------

    document.getElementById("question-id").value =
        data.question_id;

    document.getElementById("question-number").textContent =
        data.question_number;

    document.getElementById("question-text").textContent =
        data.question_text;

    document.getElementById("option-a").textContent =
        data.option_a;

    document.getElementById("option-b").textContent =
        data.option_b;

    document.getElementById("option-c").textContent =
        data.option_c;

    document.getElementById("option-d").textContent =
        data.option_d;

    // -------------------------------------
    // Clear Selection
    // -------------------------------------

    document
        .querySelectorAll('input[name="answer"]')
        .forEach(radio => radio.checked = false);

}