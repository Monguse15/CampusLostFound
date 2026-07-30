from flask import Flask, render_template, request

app = Flask(__name__)

# Store reports temporarily
lost_reports = []
found_reports = []


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/report-lost", methods=["GET", "POST"])
def report_lost():

    if request.method == "POST":

        report = {
            "item_name": request.form["item_name"],
            "category": request.form["category"],
            "location": request.form["location"],
            "description": request.form["description"],
            "phone": request.form["phone"],
            "email": request.form["email"]
        }

        lost_reports.append(report)

        return render_template("report_lost.html", success=True)

    return render_template("report_lost.html", success=False)


@app.route("/report-found", methods=["GET", "POST"])
def report_found():

    if request.method == "POST":

        report = {
            "item_name": request.form["item_name"],
            "category": request.form["category"],
            "location": request.form["location"],
            "description": request.form["description"],
            "phone": request.form["phone"],
            "email": request.form["email"]
        }

        found_reports.append(report)

        return render_template("report_found.html", success=True)

    return render_template("report_found.html", success=False)


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/search")
def search():

    all_reports = []

    for report in lost_reports:
        report["status"] = "Lost"
        all_reports.append(report)

    for report in found_reports:
        report["status"] = "Found"
        all_reports.append(report)

    return render_template("search.html", reports=all_reports)


if __name__ == "__main__":
    app.run(debug=True)