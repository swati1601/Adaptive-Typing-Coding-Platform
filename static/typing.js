let level = "easy";
let currentText = "";
let startTime = null;
let timerInterval;

function loadText() {
    fetch(`/get_text?level=${level}`)
        .then(res => res.json())
        .then(data => {
            currentText = data.text;

            document.getElementById("text").innerText =
                data.text;

            document.getElementById("level").innerText =
                data.level;

            document.getElementById("input").value = "";
            document.getElementById("result").innerHTML = "";

            document.getElementById("wpm").innerText = "0";
            document.getElementById("accuracy").innerText = "0";
            document.getElementById("timer").innerText = "60";

            startTimer();
        });
}

function startTimer() {
    clearInterval(timerInterval);

    let timeLeft = 60;

    if (level === "easy")
        timeLeft = 45;
    else if (level === "medium")
        timeLeft = 60;
    else if (level === "hard")
        timeLeft = 90;

    document.getElementById("timer").innerText =
        timeLeft;

    startTime = Date.now();

    timerInterval = setInterval(() => {

        timeLeft--;

        document.getElementById("timer").innerText =
            timeLeft;

        if (timeLeft <= 0) {

            clearInterval(timerInterval);

            document.getElementById("result").innerHTML =
                "⏰ Time Up!";

            document.getElementById("input").disabled = true;
        }

    }, 1000);
}
document.getElementById("input").addEventListener(
    "input",
    function () {
        let typed = this.value;

        let correct = 0;

        for (let i = 0; i < typed.length; i++) {
            if (typed[i] === currentText[i]) {
                correct++;
            }
        }

        let accuracy = 0;

        if (typed.length > 0) {
            accuracy =
                (correct / typed.length) * 100;
        }

        document.getElementById("accuracy")
            .innerText = accuracy.toFixed(0);

        let minutes =
            (Date.now() - startTime) / 60000;

        let words =
            typed.trim().split(" ").length;

        let wpm = 0;

        if (minutes > 0) {
            wpm = words / minutes;
        }

        document.getElementById("wpm")
            .innerText = Math.round(wpm);
    }
);

function checkTyping() {

    clearInterval(timerInterval);

    let userText =
        document.getElementById("input").value;

    if (userText.trim() === currentText.trim()) {

        document.getElementById("result").innerHTML =
            "✅ Correct";

        if (level === "easy")
            level = "medium";

        else if (level === "medium")
            level = "hard";

    } else {

        document.getElementById("result").innerHTML =
            "❌ Wrong";
    }

   <button onclick="nextQuestion()">
    Next Question
   </button> 
function nextQuestion() {

    document.getElementById("input").disabled = false;

    loadText();
}
}

window.onload = loadText;
