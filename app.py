from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "campus_lost_found_secret_key"

# ----------------------------
# Database Configuration
# ----------------------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///campuslostfound.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ----------------------------
# Database Models
# ----------------------------

class LostItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)


class FoundItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


# ----------------------------
# Home
# ----------------------------

@app.route("/")
def home():
    return render_template("home.html")


# ----------------------------
# Register
# ----------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        existing_user = User.query.filter_by(
            email=request.form["email"]
        ).first()

        if existing_user:
            return render_template(
                "register.html",
                error="Email already registered."
            )

        new_user = User(
            fullname=request.form["fullname"],
            email=request.form["email"],
            password=generate_password_hash(
                request.form["password"]
            )
        )

        db.session.add(new_user)
        db.session.commit()

        return render_template(
            "register.html",
            success=True
        )

    return render_template("register.html")


# ----------------------------
# Login
# ----------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            session["user_id"] = user.id
            session["user_name"] = user.fullname

            return redirect(url_for("home"))

        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    return render_template("login.html")


# ----------------------------
# Logout
# ----------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ----------------------------
# Dashboard
# ----------------------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    my_lost_items = LostItem.query.filter_by(
        user_id=session["user_id"]
    ).all()

    my_found_items = FoundItem.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "dashboard.html",
        lost_items=my_lost_items,
        found_items=my_found_items
    )

# ----------------------------
# Report Lost
# ----------------------------

@app.route("/report-lost", methods=["GET", "POST"])
def report_lost():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        new_report = LostItem(
            user_id=session["user_id"],
            item_name=request.form["item_name"],
            category=request.form["category"],
            location=request.form["location"],
            description=request.form["description"],
            phone=request.form["phone"],
            email=request.form["email"]
        )

        db.session.add(new_report)
        db.session.commit()

        return render_template(
            "report_lost.html",
            success=True
        )

    return render_template("report_lost.html")


# ----------------------------
# Report Found
# ----------------------------

@app.route("/report-found", methods=["GET", "POST"])
def report_found():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        new_report = FoundItem(
            user_id=session["user_id"],
            item_name=request.form["item_name"],
            category=request.form["category"],
            location=request.form["location"],
            description=request.form["description"],
            phone=request.form["phone"],
            email=request.form["email"]
        )

        db.session.add(new_report)
        db.session.commit()

        return render_template(
            "report_found.html",
            success=True
        )

    return render_template("report_found.html")


# ----------------------------
# Search
# ----------------------------

@app.route("/search")
def search():

    all_reports = []

    lost_items = LostItem.query.all()

    for item in lost_items:
        all_reports.append({
            "status": "Lost",
            "item_name": item.item_name,
            "category": item.category,
            "location": item.location,
            "description": item.description,
            "phone": item.phone,
            "email": item.email
        })

    found_items = FoundItem.query.all()

    for item in found_items:
        all_reports.append({
            "status": "Found",
            "item_name": item.item_name,
            "category": item.category,
            "location": item.location,
            "description": item.description,
            "phone": item.phone,
            "email": item.email
        })

    return render_template(
        "search.html",
        reports=all_reports
    )
@app.route("/test")
def test():
    return str(session)


# ----------------------------
# Run Application
# ----------------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)