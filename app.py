from flask import Flask, render_template, request, jsonify
import random
import json

app = Flask(__name__)

# -------------------------
# LEVELS
# -------------------------

levels = ["easy", "medium", "hard"]

typing_level_index = 0
coding_level_index = 0

# -------------------------
# LOAD JSON FILES
# -------------------------

with open("typing_questions.json") as f:
    typing_data = json.load(f)

with open("coding_questions.json") as f:
    coding_questions = json.load(f)

# -------------------------
# TRACK USED QUESTIONS
# -------------------------

used_texts = {
    "easy": set(),
    "medium": set(),
    "hard": set()
}

used_questions = {
    "easy": set(),
    "medium": set(),
    "hard": set()
}

# -------------------------
# HOME
# -------------------------

@app.route('/')
def index():
    return render_template('index.html')

# -------------------------
# TYPING PAGE
# -------------------------

@app.route('/typing')
def typing():
    return render_template('typing.html')

# -------------------------
# GET TYPING TEXT
# -------------------------

@app.route('/get_text')
def get_text():

    global typing_level_index

    level = levels[typing_level_index]

    texts = typing_data[level]

    available = [
        t for t in texts
        if t not in used_texts[level]
    ]

    if not available:
        used_texts[level].clear()
        available = texts

    text = random.choice(available)

    used_texts[level].add(text)

    return jsonify({
        "text": text,
        "level": level
    })

# -------------------------
# UPDATE TYPING LEVEL
# -------------------------

@app.route('/update_typing', methods=['POST'])
def update_typing():

    global typing_level_index

    data = request.json

    accuracy = data.get("accuracy", 0)

    if accuracy >= 70:

        if typing_level_index < 2:
            typing_level_index += 1

    elif accuracy < 40:

        if typing_level_index > 0:
            typing_level_index -= 1

    return jsonify({
        "level": levels[typing_level_index]
    })

# -------------------------
# CODING PAGE
# -------------------------

@app.route('/coding')
def coding():
    return render_template('coding.html')

# -------------------------
# LOAD QUESTIONS
# -------------------------

@app.route('/all_questions')
def all_questions():

    global coding_level_index

    lang = request.args.get('lang', 'python')

    level = levels[coding_level_index]

    data = coding_questions[lang][level]

    return jsonify({
        "questions": data,
        "level": level
    })

# -------------------------
# CHECK CODE
# -------------------------
@app.route('/check_code', methods=['POST'])
def check_code():
    global coding_level_index

    data = request.json

    user_code = data.get('code', '')
    answer = data.get('answer', '')

    # DEBUG PRINTS
    print("USER CODE:", user_code)
    print("ANSWER:", answer)
    print("LEVEL INDEX:", coding_level_index)
    print("CURRENT LEVEL:", levels[coding_level_index])

    if user_code.strip() == answer.strip():

        result = "Correct"

        if coding_level_index < len(levels) - 1:
            coding_level_index += 1

    else:
        result = "Wrong"

    return jsonify({
        "result": result,
        "level": levels[coding_level_index]
    })
# -------------------------

if __name__ == '__main__':
    app.run(debug=True)