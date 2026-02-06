from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = "exam_secret_key"

# Dummy user (later database use kar sakte ho)
USER = {
    "student1": "1234"
}

QUESTIONS = {
    "q1": {"question": "Python is ___ language?", "options": ["Low level", "High level", "Machine", "Assembly"], "answer": "High level"},
    "q2": {"question": "HTML stands for?", "options": ["Hyper Text Markup Language", "High Text Machine Language", "Hyperlinks Text Mark", "None"], "answer": "Hyper Text Markup Language"},
    "q3": {"question": "Which is backend language?", "options": ["HTML", "CSS", "Python", "Bootstrap"], "answer": "Python"}
}

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in USER and USER[username] == password:
            session["user"] = username
            return redirect(url_for("exam"))
        else:
            return "Invalid Login"

    return render_template("login.html")

@app.route("/exam", methods=["GET","POST"])
def exam():
    threading.Thread(target=start_camera).start()

    os.system("start cmd /k python camera_monitor.py")
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        score = 0
        for q in QUESTIONS:
            if request.form.get(q) == QUESTIONS[q]["answer"]:
                score += 1
        return render_template("result.html", score=score, total=len(QUESTIONS))

    return render_template("exam.html", questions=QUESTIONS)

@app.route("/submit")
def submit():
    return redirect(url_for("result"))

@app.route("/result")
def result():
    return "Exam Submitted"

if __name__ == "__main__":
    app.run(debug=True)
