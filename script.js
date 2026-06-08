let currentAnswer = "";

// ========================
// LOAD QUESTIONS
// ========================

function loadQuestions() {
  let lang = document.getElementById("languageSelect").value;

  let level = document.getElementById("level").innerText.trim();

  fetch(`/all_questions?lang=${lang}&level=${level}`)
    .then((res) => res.json())

    .then((response) => {
      let data = response.questions;

      document.getElementById("level").innerText = response.level;

      let list = document.getElementById("questionsList");

      list.innerHTML = "";

      data.forEach((q, index) => {
        let item = document.createElement("div");

        item.className = "question-item";

        item.innerHTML = `
                <strong>Q${index + 1}</strong><br>
                ${q.question}
            `;

        item.onclick = function () {
          document.getElementById("questionTitle").innerText = q.question;

          currentAnswer = q.answer;
        };

        list.appendChild(item);
      });

      if (data.length > 0) {
        document.getElementById("questionTitle").innerText = data[0].question;

        currentAnswer = data[0].answer;
      }
    })

    .catch((err) => {
      console.log("Error:", err);
    });
}

// ========================
// CHECK CODE
// ========================

function checkCode() {
  let code = document.getElementById("code").value.trim();

  fetch("/check_code", {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      code: code,
      answer: currentAnswer,
    }),
  })
    .then((res) => res.json())

    .then((data) => {
      document.getElementById("result").innerHTML = data.result;

      document.getElementById("level").innerText = data.level;

      document.getElementById("code").value = "";

      loadQuestions();
    })

    .catch((err) => {
      console.log("Error:", err);
    });
}

// ========================
// LANGUAGE CHANGE
// ========================

document
  .getElementById("languageSelect")
  .addEventListener("change", function () {
    loadQuestions();
  });

// ========================
// PAGE LOAD
// ========================

window.onload = function () {
  loadQuestions();
};
