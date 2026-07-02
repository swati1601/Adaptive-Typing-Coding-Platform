let level = "easy";
let currentText = "";

let startTime = null;
let timerInterval;
let timeLeft = 45;

// Timer according to level
function getTimeForLevel(level) {
    if (level === "easy") return 45;
    if (level === "medium") return 60;
    return 90;
}

// Load typing paragraph
function loadText() {

    fetch(`/get_text?level=${level}`)
        .then(res => res.json())
        .then(data => {

            currentText = data.text;

            document.getElementById("level").innerText = data.level;

            document.getElementById("input").value = "";
            document.getElementById("result").innerHTML = "";

            // reset timer
            clearInterval(timerInterval);
            timeLeft = getTimeForLevel(data.level);

            document.getElementById("timer").innerText = timeLeft;
            document.getElementById("wpm").innerText = 0;
            document.getElementById("accuracy").innerText = 100;

            startTime = null;

            renderText("");

        });

}

// Display colored text
function renderText(userInput) {

    const textDiv = document.getElementById("text");

    let html = "";

    for (let i = 0; i < currentText.length; i++) {

        let cls = "";

        if (i < userInput.length) {

            if (userInput[i] === currentText[i])
                cls = "correct";
            else
                cls = "wrong";

        }
        else if (i === userInput.length) {

            cls = "current";

        }

        html += `<span class="${cls}">${currentText[i]}</span>`;

    }

    textDiv.innerHTML = html;

}

// Start timer
function startTimer() {

    if (startTime !== null)
        return;

    startTime = new Date();

    timerInterval = setInterval(() => {

        timeLeft--;

        document.getElementById("timer").innerText = timeLeft;

        if (timeLeft <= 0) {

            clearInterval(timerInterval);

            document.getElementById("result").innerHTML =
                "<span style='color:red'>⏰ Time Over!</span>";

        }

    },1000);

}

// Live typing
document.addEventListener("DOMContentLoaded",()=>{

    loadText();

    const input = document.getElementById("input");

    input.addEventListener("input",function(){

        if(startTime===null)
            startTimer();

        let typed=this.value;

        renderText(typed);

        // Accuracy
        let correct=0;

        for(let i=0;i<typed.length;i++){

            if(typed[i]===currentText[i])
                correct++;

        }

        let accuracy=typed.length===0
            ?100
            :Math.round((correct/typed.length)*100);

        document.getElementById("accuracy").innerText=accuracy;

        // WPM
        if(startTime){

            let elapsed=(new Date()-startTime)/1000/60;

            if(elapsed>0){

                let words=typed.trim().split(/\s+/).length;

                if(typed.trim()==="")
                    words=0;

                let wpm=Math.round(words/elapsed);

                document.getElementById("wpm").innerText=wpm;

            }

        }

    });

});

// Submit
function checkTyping(){

    clearInterval(timerInterval);

    let userText=document.getElementById("input").value;

    if(userText.trim()===currentText.trim()){

        document.getElementById("result").innerHTML=
        "<span style='color:green;font-size:22px;'>✔ Correct!</span>";

        if(level==="easy")
            level="medium";

        else if(level==="medium")
            level="hard";

    }
    else{

        document.getElementById("result").innerHTML=
        "<span style='color:red;font-size:22px;'>✖ Wrong!</span>";

    }

    // Wait before next question
    setTimeout(loadText,2000);

}
