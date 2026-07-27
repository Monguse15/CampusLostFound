from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/report-lost")
def report_lost():
    return render_template("report_lost.html")


@app.route("/report-found")
def report_found():
    return render_template("report_found.html")


@app.route("/login")
def login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)