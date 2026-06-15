
import json
import random



typing_easy = []
typing_medium = []
typing_hard = []

words_easy = [
    "cat", "dog", "sun", "book", "pen",
    "apple", "ball", "tree", "milk", "road"
]

words_medium = [
    "computer", "keyboard", "science",
    "python", "coding", "database",
    "network", "monitor", "programming"
]

words_hard = [
    "artificial intelligence",
    "machine learning",
    "data structures",
    "software engineering",
    "cloud computing",
    "cyber security"
]

for i in range(300):
    typing_easy.append(
        " ".join(random.choices(words_easy, k=15))
    )

for i in range(300):
    typing_medium.append(
        " ".join(random.choices(words_medium, k=20))
    )

for i in range(400):
    typing_hard.append(
        " ".join(random.choices(words_hard, k=25))
    )

typing_data = {
    "easy": typing_easy,
    "medium": typing_medium,
    "hard": typing_hard
}

#coding questions

coding_data = {

    "python": {

        "easy": [
            {"question": "Add two numbers", "answer": "a+b", "hint": "Use + operator"},
            {"question": "Subtract two numbers", "answer": "a-b", "hint": "Use - operator"},
            {"question": "Multiply two numbers", "answer": "a*b", "hint": "Use * operator"},
            {"question": "Divide two numbers", "answer": "a/b", "hint": "Use / operator"},
            {"question": "Check even number", "answer": "n%2==0", "hint": "Use modulo operator"},
            {"question": "Find square of a number", "answer": "n*n", "hint": "Multiply number by itself"},
            {"question": "Find cube of a number", "answer": "n*n*n", "hint": "Multiply three times"},
            {"question": "Find maximum of two numbers", "answer": "max(a,b)", "hint": "Use max()"},
            {"question": "Find minimum of two numbers", "answer": "min(a,b)", "hint": "Use min()"},
            {"question": "Find length of string", "answer": "len(s)", "hint": "Use len()"}
        ],

        "medium": [
            {"question": "Reverse a string", "answer": "s[::-1]", "hint": "Use slicing"},
            {"question": "Sort a list", "answer": "sorted(l)", "hint": "Use sorted()"},
            {"question": "Convert string to uppercase", "answer": "s.upper()", "hint": "Use upper()"},
            {"question": "Convert string to lowercase", "answer": "s.lower()", "hint": "Use lower()"},
            {"question": "Count character occurrences", "answer": "s.count('a')", "hint": "Use count()"},
            {"question": "Remove spaces from string", "answer": "s.replace(' ','')", "hint": "Use replace()"},
            {"question": "Find list length", "answer": "len(l)", "hint": "Use len()"}
        ],

        "hard": [
            {"question": "Remove duplicates from list", "answer": "list(set(l))", "hint": "Use set()"},
            {"question": "Find second largest element", "answer": "sorted(l)[-2]", "hint": "Sort list"},
            {"question": "Merge two lists", "answer": "l1+l2", "hint": "Use + operator"},
            {"question": "Check palindrome", "answer": "s==s[::-1]", "hint": "Reverse string"},
            {"question": "Find factorial", "answer": "math.factorial(n)", "hint": "Use math module"}
        ]
    },

    "c": {

        "easy": [
            {"question": "Add two numbers", "answer": "a+b;", "hint": "Use +"},
            {"question": "Subtract two numbers", "answer": "a-b;", "hint": "Use -"},
            {"question": "Multiply two numbers", "answer": "a*b;", "hint": "Use *"},
            {"question": "Divide two numbers", "answer": "a/b;", "hint": "Use /"}
        ],

        "medium": [
            {"question": "Find maximum of two numbers", "answer": "(a>b)?a:b;", "hint": "Use ternary operator"},
            {"question": "Check even number", "answer": "n%2==0;", "hint": "Use modulo"}
        ],

        "hard": [
            {"question": "Logical AND operation", "answer": "a&&b;", "hint": "Use &&"},
            {"question": "Logical OR operation", "answer": "a||b;", "hint": "Use ||"}
        ]
    },

    "java": {

        "easy": [
            {"question": "Add two numbers", "answer": "a+b;", "hint": "Use +"},
            {"question": "Subtract two numbers", "answer": "a-b;", "hint": "Use -"},
            {"question": "Multiply two numbers", "answer": "a*b;", "hint": "Use *"}
        ],

        "medium": [
            {"question": "Find maximum of two numbers", "answer": "Math.max(a,b);", "hint": "Use Math.max()"},
            {"question": "Find minimum of two numbers", "answer": "Math.min(a,b);", "hint": "Use Math.min()"}
        ],

        "hard": [
            {"question": "Compare two numbers", "answer": "Integer.compare(a,b);", "hint": "Use Integer.compare()"},
            {"question": "Convert string to uppercase", "answer": "s.toUpperCase();", "hint": "Use toUpperCase()"}
        ]
    }
}
#save file

with open("typing_questions.json", "w") as f:
    json.dump(typing_data, f, indent=4)

with open("coding_questions.json", "w") as f:
    json.dump(coding_data, f, indent=4)

print("Questions generated successfully!")

